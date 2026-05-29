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
    "purple beanbag": {
        "name": " purple beanbag",
        "key_words": ("purple", "beanbag"),
        "room_description": "&wa &Pbeanbag&N sits in a corner.&N",
        "description": (
            "behold it is actually a monster.\n"
        ),
        "race": "Human",
        "class": "Student",
        "level": 19,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "killable": True,
        "wander": False
    },
    " grey beanbag": {
        "name": "grey beanbag",
        "key_words": ("grey", "beanbag"),
        "room_description": "&wa &Xbeanbag&N sits in a corner.&N",
        "description": (
            "you have been fooled, tis a monster!\n"
        ),
        "race": "Human",
        "class": "Student",
        "level": 19,
        "stats": [10, 10, 10, 10, 10, 10],
        "aggro": False,
        "killable": True,
        "wander": False
    },
    "Mr. Carlson": {
        "name": "Mr. Carlson",
        "key_words": ("student", "wandering"),
        "room_description": "&wA wandering student meanders about aimlessly.&N",
        "description": (
            "A student with a faraway look, clearly lost in thought.\n"
            "Or possibly just lost."
        ),
        "race": "Human",
        "class": "Student",
        "level": 1,
        "stats": [60, 65, 60, 80, 70, 75],
        "aggro": False,
        "killable": False,
        "wander": True
    },
    "Enemy": {
        "name": "Enemy",
        "key_words": ("Enemy"),
        "room_description": "&wa &Xdark&N figure stands with &rhate&N in his posture.&N",
        "description": (
            "this being is the schools strongest nemesis, he has fought with the attendants for centuries."
        ),
        "race": "Celestial",
        "class": "Enemy",
        "level": 50,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": True,
        "killable": True,
        "wander": True,
    }
}
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)