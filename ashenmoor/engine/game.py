"""
ashenmoor.engine.game
─────────────────────
Game state container and core engine functions.

Command resolution order
────────────────────────
1. Player powers  — keywords defined in the player's character.powers list
2. System commands — look, go, who, stats, examine, quit, ...
3. "Pardon?"       — nothing matched
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room      import Room
    from ..core.character  import Character

from .targeting import find_target, find_all_targets, target_name

DIRECTIONS = frozenset({
    "north", "south", "east", "west", "up", "down",
    "n", "s", "e", "w", "u", "d",
})

_DIR_EXPAND = {
    "n": "north", "s": "south", "e": "east", "w": "west",
    "u": "up",    "d": "down",
}

def _expand_direction(d: str) -> str:
    return _DIR_EXPAND.get(d.lower(), d.lower())


def go(character, locations, rooms, direction):
    direction = _expand_direction(direction)
    room      = rooms[locations[character]]
    dest_id   = room.exit_room_id(direction)
    if dest_id is not None and dest_id in rooms:
        locations[character] = dest_id
        return rooms[dest_id]
    return "&NAlas, you cannot go that way. . . ."


class GameState:

    def __init__(self):
        self.rooms            = {}
        self.characters       = {}
        self.locations        = {}
        self.player           = ""
        self.object_templates = {}
        self.mob_templates    = {}

    def load_world(self, rooms, characters, locations, player=""):
        self.rooms      = rooms
        self.characters = characters
        self.locations  = locations
        self.player     = player or (next(iter(characters)) if characters else "")

    def load_zone(self, zone):
        collisions = set(zone.rooms) & set(self.rooms)
        if collisions:
            import warnings
            warnings.warn(
                f"Zone '{zone.name}' overwrites existing room numbers: {sorted(collisions)}",
                stacklevel=2,
            )
        self.rooms.update(zone.rooms)
        self.object_templates.update(zone.object_templates)
        self.mob_templates.update(zone.mob_templates)

    @property
    def current_room(self):
        room_id = self.locations.get(self.player)
        return self.rooms.get(room_id) if room_id is not None else None

    def _target(self, target_str):
        room = self.current_room
        if room is None:
            return None
        return find_target(target_str, room, self.locations, self.characters)

    # ── Command handler ───────────────────────────────────────────────────────

    def handle(self, raw: str):
        tokens = raw.strip().lower().split()
        if not tokens:
            return None
        verb, *args = tokens

        # 1. Player powers first
        power_result = self._try_power(verb, args)
        if power_result is not None:
            return power_result

        # 2. System commands
        if verb in ("quit", "exit", "leave", "q", "camp"):
            return "quit"

        if verb in DIRECTIONS or verb == "go":
            direction = args[0] if verb == "go" and args else verb
            return go(self.player, self.locations, self.rooms, direction)

        if verb in ("look", "l"):
            return self._cmd_look(args)

        if verb in ("examine", "ex", "x"):
            return self._cmd_examine(args)

        if verb == "who":
            return self._who()

        if verb in ("score", "stats", "stat"):
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"

        if verb in ("powers", "spells", "skills", "abilities"):
            return self._cmd_powers()

        # 3. Unknown
        return "&NPardon?"

    # ── Powers ────────────────────────────────────────────────────────────────

    def _try_power(self, verb: str, args: list):
        """
        Return output string if verb matches a player power keyword, else None.
        Returning None tells handle() to keep checking system commands.
        """
        char = self.characters.get(self.player)
        if not char or not char.powers:
            return None

        for power in char.powers:
            keywords = power.get("keywords", ())
            if isinstance(keywords, str):
                keywords = (keywords,)
            if verb in (k.lower() for k in keywords):
                return self._execute_power(power)

        return None

    def _execute_power(self, power: dict) -> str:
        """
        Build the output for a triggered power.

        user_msg  — shown to the player
        room_msg  — shown to everyone else in the room
                    {name} is replaced with the player's name.

        For now both appear in the same output.  When multiplayer is added,
        room_msg will be broadcast separately to other connections.
        """
        char = self.characters.get(self.player)
        name = char.name if char else "Someone"

        user_msg = power.get("user_msg", "")
        room_msg = power.get("room_msg", "").format(name=name)

        parts = []
        if user_msg:
            parts.append(user_msg)
        if room_msg:
            parts.append(f"&w(others see)&N {room_msg}")
        return "\n".join(parts)

    def _cmd_powers(self) -> str:
        """List the player's known powers."""
        char = self.characters.get(self.player)
        if not char:
            return "&RNo character found.&N"
        if not char.powers:
            return "&wYou have no powers.&N"
        lines = [f"&+W{'Power':<20} {'Keywords'}&N",
                 "&w" + "─" * 46 + "&N"]
        for p in char.powers:
            kws  = ", ".join(p.get("keywords", ()))
            name = p.get("name", "?")
            lines.append(f"{name:<20} &c{kws}&N")
        return "\n".join(lines)

    # ── look ─────────────────────────────────────────────────────────────────

    _ALL_DIRS = frozenset({
        "north","south","east","west","up","down",
        "northeast","northwest","southeast","southwest",
        "n","s","e","w","u","d","ne","nw","se","sw",
    })

    def _cmd_look(self, args):
        room = self.current_room
        if room is None:
            return "&RYou are nowhere.&N"
        if not args:
            return room.render(self.locations, self.characters)
        token = args[0].lower()
        if token in self._ALL_DIRS:
            direction = _expand_direction(token)
            dest, blocked, msg = room.peek(direction, self.rooms)
            if msg:
                return msg
            return dest.render(self.locations, self.characters)
        target_str = " ".join(args)
        instance   = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance)

    def _cmd_examine(self, args):
        if not args:
            return "&wExamine what?  e.g.  &Wexamine 2.marker&N"
        room = self.current_room
        if room is None:
            return "&RYou are nowhere.&N"
        target_str = " ".join(args)
        instance   = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance)

    def _describe(self, instance):
        from ..world.mob import Mob
        from ..core.character import Character
        from ..world.objects import Object
        if isinstance(instance, Mob):
            return instance.description or f"You see nothing special about {instance.name}."
        if isinstance(instance, Character):
            return instance.character_sheet()
        if isinstance(instance, Object):
            desc = getattr(instance, "description", "")
            name = target_name(instance)
            return desc if desc else f"You see nothing special about {name}."
        return str(instance)

    def _who(self):
        if not self.characters:
            return "&wNobody is here.&N"
        lines = [f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5}&N"]
        lines.append("&w" + "─" * 46 + "&N")
        for char in self.characters.values():
            lines.append(f"{char.name:<15} {char.race:<12} {char.cclass:<10} {char.level:>5}")
        return "\n".join(lines)

    def character_list(self):
        return self._who()
