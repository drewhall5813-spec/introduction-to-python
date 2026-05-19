
from __future__ import annotations
from typing import TYPE_CHECKING
from .stats import Stats
if TYPE_CHECKING:
    from .race import Race


class Character:
    """
    Base character (player or NPC).

    Parameters
    ----------
    d : dict
        'name'     str          character name
        'stats'    list[int]    [STR, DEX, CON, INT, WIS, CHA], default 80 each
        'race'     str          key into the races registry, default 'Human'
        'level'    int          default 1
        'position' str          default 'standing'
        'class'    str          class name, default 'Warrior'
        'powers'   list         list of power dicts, default []
                                See ashenmoor.world.powers for the power format.

    races : dict[str, Race] | None
        Race registry to use for computed_stat().
        Defaults to ashenmoor.core.race.RACES if not supplied.
    """

    def __init__(self, d: dict, races: dict | None = None):
        self.name:     str       = d.get("name",     "Unknown")
        self.stats:    list[int] = d.get("stats",    [80, 80, 80, 80, 80, 80])
        self.race:     str       = d.get("race",     "Human")
        self.level:    int       = d.get("level",    1)
        self.position: str       = d.get("position", "standing")
        self.cclass:   str       = d.get("class",    "Warrior")
        self.powers:   list      = d.get("powers",   [])
        # powers is a list of power dicts (see ashenmoor.world.powers).
        # Each dict has at minimum: keywords, name, user_msg, room_msg.
        # The engine checks this list before system commands so players can
        # type any keyword from their powers directly at the prompt.

        if races is None:
            from .race import RACES
            races = RACES
        self._races = races

    # ── Stat access ───────────────────────────────────────────────────────────

    def get_stat(self, stat) -> int:
        if isinstance(stat, int):   return self.stats[stat]
        if isinstance(stat, Stats): return self.stats[stat.value]
        if isinstance(stat, str):
            for s in Stats:
                if stat.lower() == s.abv: return self.stats[s.value]
        raise ValueError(f"Unknown stat: {stat!r}")

    def computed_stat(self, stat) -> int:
        race = self._races.get(self.race)
        if race is None: return self.get_stat(stat)
        return int(self.get_stat(stat) * race.get_mod(stat))

    # ── Display ───────────────────────────────────────────────────────────────

    def character_sheet(self) -> str:
        lines = [
            f"&+WCharacter sheet for &N{self.name}\n",
            f"&wRace:&N  {self.race}",
            f"&wClass:&N {self.cclass}",
            f"&wLevel:&N {self.level}",
            "&wStats:&N",
            (f"  &wStrength:&N     {self.get_stat('str'):>3}    "
             f"&wIntelligence:&N {self.get_stat('int'):>3}"),
            (f"  &wDexterity:&N    {self.get_stat('dex'):>3}    "
             f"&wWisdom:&N       {self.get_stat('wis'):>3}"),
            (f"  &wConstitution:&N {self.get_stat('con'):>3}    "
             f"&wCharisma:&N     {self.get_stat('cha'):>3}"),
        ]
        if self.powers:
            lines.append("&wPowers:&N  " +
                         ", ".join(p.get("name","?") for p in self.powers))
        return "\n".join(lines)

    def pcs(self) -> None:
        from ..color import cprint
        cprint(self.character_sheet())

    def __str__(self):  return self.character_sheet()
    def __repr__(self): return (f"Character(name={self.name!r}, race={self.race!r}, "
                                f"class={self.cclass!r}, level={self.level})")
