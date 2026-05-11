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
    "fanciful_bard": {
        "name": "Marloe the Bard",
        "key_words": ("Bard", "Marloe", "Siren"),
        "room_description": "A bard sits here, plucking at her &ylyre&N and wearing a mildly board expression",
        "description": (
            "&bMarloe&N sits here with a &ylyre&N in hand, she wears somewhat &gfanciful clothing&N as well as what looks like a large &xcaptans hat&N.\n"
            "she looks...human."
        ),
        "race": "Siren",
        "class": "bard",
        "level": 5,
        "stats": [50, 75, 10, 80, 70, 100],
        "aggro": False,
        "wander": True,
    },
    "Red kobold": {
        "name": "Jremblen",
        "key_words": ("kobold", "Red"),
        "room_description": "a &rkobold&N stands here, looking through a &ybag&N full of &gm&Go&gs&Gs.&N",
        "description": (
            "A small &rkobold&n stands here looking through a &ybag&N, it seems to be filled with various different types of &gm&Go&gs&Gs&N.\n"
            "His scales are &rgarnet red&N."
        ),
        "race": "Kobold",
        "class": "rouge",
        "level": 1,
        "stats": [40, 50, 40, 30, 20, 40],
        "aggro": False,
        "wander": False,
    },

    "blank_templet": {
        "name": "name",
        "key_words": ("1", "2"),
        "room_description": "",
        "description": (
            "this is just so i can ctrl c  ctrl v".\n"
            "hi"
        ),
        "race": "race",
        "class": "class",
        "level": 5,
        "stats": [60, 75, 65, 80, 70, 75],
        "aggro": False,
        "wander": True,
    },
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)