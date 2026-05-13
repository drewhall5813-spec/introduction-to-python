"""
zones.the_void.mobs
───────────────────
Mob templates for The Void zone.

Add an entry to TEMPLATES for every NPC type that can appear in this zone.
Call spawn(key) to get a fresh independent Mob instance — place as many
copies in rooms as you like, each is independent.
"""

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "escbaalion": {
        "name": "Escbaalion",  # The c is silent
        "key_words": ("Escbaalion"),
        "room_description": "&gEscbaalion&N &wlicks his eyeball.&N",
        "description": (
            "A humanoid lizard. He is &gdark-green&N, and has a short\n"
            "&Ccyan sail&N that runs from the top of his head to the end of his tail.\n"
            "He wears an almost &Xblack cloak&N, but wears &Rno&N pants.\n"
            "A &ybrown leather satchel&N is slung over his shoulder.\n"
            "Only &ghe&N knows what is inside his &ybag&N. . . ."
        ),
        "race": "Lizaroid",
        "class": "Sorcerer",
        "level": 10,
        "stats": [80, 50, 200, 90, 90, 70],
        "aggro": True,
        "wander": True,
    }
}

spawn = make_spawner(TEMPLATES, lambda: Mob)
