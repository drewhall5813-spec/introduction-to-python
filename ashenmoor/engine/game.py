"""
ashenmoor.engine.game
─────────────────────
Game state container and core engine functions.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..world.room      import Room
    from ..core.character  import Character

from .targeting import find_target, find_all_targets, target_name


# ── Movement directions ───────────────────────────────────────────────────────

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


# ── go() ─────────────────────────────────────────────────────────────────────

def go(character: str,
       locations: dict[str, int],
       rooms:     dict[int, "Room"],
       direction: str) -> object:
    """
    Move *character* in *direction*. Updates locations in place.
    Returns the destination Room on success, or an error string.
    """
    direction = _expand_direction(direction)
    room      = rooms[locations[character]]
    dest_id   = room.exit_room_id(direction)
    if dest_id is not None and dest_id in rooms:
        locations[character] = dest_id
        return rooms[dest_id]
    return "&NAlas, you cannot go that way. . . ."


# ── GameState ─────────────────────────────────────────────────────────────────

class GameState:
    """
    Owns all runtime world state and exposes handle() for crepl().
    """

    def __init__(self):
        self.rooms:            dict[int, "Room"]      = {}
        self.characters:       dict[str, "Character"] = {}
        self.locations:        dict[str, int]         = {}
        self.player:           str                    = ""
        self.object_templates: dict[str, dict]        = {}
        self.mob_templates:    dict[str, dict]        = {}

    def load_world(self, rooms, characters, locations, player=""):
        self.rooms      = rooms
        self.characters = characters
        self.locations  = locations
        self.player     = player or (next(iter(characters)) if characters else "")

    def load_zone(self, zone) -> None:
        """Merge a Zone's rooms and templates into the live world."""
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

    # ── Convenience ───────────────────────────────────────────────────────────

    @property
    def current_room(self):
        room_id = self.locations.get(self.player)
        return self.rooms.get(room_id) if room_id is not None else None

    def _target(self, target_str: str):
        """
        Resolve a target string in the player's current room.

        Convenience wrapper around find_target() that supplies the current
        room, locations, and characters automatically.  Any command handler
        can call self._target("2.marker") and get back the instance or None.
        """
        room = self.current_room
        if room is None:
            return None
        return find_target(target_str, room, self.locations, self.characters)

    # ── Command handler ───────────────────────────────────────────────────────

    def handle(self, raw: str) -> object:
        tokens      = raw.strip().lower().split()
        if not tokens:
            return None
        verb, *args = tokens

        # quit
        if verb in ("quit", "exit", "leave", "q", "camp"):
            return "quit"

        # movement
        if verb in DIRECTIONS or verb == "go":
            direction = args[0] if verb == "go" and args else verb
            return go(self.player, self.locations, self.rooms, direction)

        # look / look <target>
        if verb in ("look", "l"):
            return self._cmd_look(args)

        # examine / ex / x
        if verb in ("examine", "ex", "x"):
            return self._cmd_examine(args)

        # who
        if verb == "who":
            return self._who()

        # score / stats
        if verb in ("score", "stats", "stat"):
            char = self.characters.get(self.player)
            return char.character_sheet() if char else "&RNo character found.&N"

        return "&NPardon?"

    # ── look ─────────────────────────────────────────────────────────────────

    # All words that count as a direction for 'look <direction>'
    _ALL_DIRS = frozenset({
        "north","south","east","west","up","down",
        "northeast","northwest","southeast","southwest",
        "n","s","e","w","u","d","ne","nw","se","sw",
    })

    def _cmd_look(self, args: list) -> str:
        room = self.current_room
        if room is None:
            return "&RYou are nowhere.&N"

        # bare 'look' — describe the room
        if not args:
            return room.render(self.locations, self.characters)

        token = args[0].lower()

        # 'look <direction>' — peek into the next room
        if token in self._ALL_DIRS:
            direction = _expand_direction(token)
            dest, blocked, msg = room.peek(direction, self.rooms)
            if msg:
                return msg
            return dest.render(self.locations, self.characters)

        # 'look <target>' — describe a specific thing in this room
        target_str = " ".join(args)
        instance   = find_target(target_str, room, self.locations, self.characters)
        if instance is None:
            return f"&wYou don't see any '&W{target_str}&w' here.&N"
        return self._describe(instance)

    # ── examine ───────────────────────────────────────────────────────────────

    def _cmd_examine(self, args: list) -> str:
        """
        examine <target>   — show the full description of a target.

        Uses the same targeting system as look:
            examine marker       first marker in the room
            examine 2.marker     second marker
            examine guardian     the void guardian mob
            examine moted        a character named moted
        """
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

    # ── describe — shared by look and examine ─────────────────────────────────

    def _describe(self, instance) -> str:
        """
        Return the appropriate description string for any target type.

        Mob / Character   → character_sheet() + examine() if present
        Object            → description field
        """
        from ..world.mob import Mob
        from ..core.character import Character
        from ..world.objects import Object

        if isinstance(instance, Mob):
            # Mobs have both a character sheet and an examine description
            parts = []
            if instance.description:
                parts.append(instance.description)
            else:
                parts.append(f"You see nothing special about {instance.name}.")
            return "\n".join(parts)

        if isinstance(instance, Character):
            return instance.character_sheet()

        if isinstance(instance, Object):
            desc = getattr(instance, "description", "")
            name = target_name(instance)
            return desc if desc else f"You see nothing special about {name}."

        return str(instance)

    # ── who ───────────────────────────────────────────────────────────────────

    def _who(self) -> str:
        if not self.characters:
            return "&wNobody is here.&N"
        lines = [f"&+W{'Name':<15} {'Race':<12} {'Class':<10} {'Level':>5}&N"]
        lines.append("&w" + "─" * 46 + "&N")
        for char in self.characters.values():
            lines.append(
                f"{char.name:<15} {char.race:<12} {char.cclass:<10} {char.level:>5}"
            )
        return "\n".join(lines)

    def character_list(self) -> str:
        return self._who()
