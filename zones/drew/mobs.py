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
    "sand_puma": {
        "name": "sand puma",
        "key_words":       ("puma"),
        "room_description": "&wA sand puma aimlesly being taken under the quick sand.&N",
        "description": (
            "rockyish sand color with yellow.\n"
            "Or possibly just lo."
        ),
        "race": "pumaish",
        "class": "sandy",
        "level": 1,
        "stats": [99, 68, 71, 87, 81, 100],
        "aggro": False,
        "wander": True,
    }
}

# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)