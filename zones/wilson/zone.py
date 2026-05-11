number = 13

from ashenmoor.world import Mob
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "George_Washington": {
        "name": "George_Washington",
        "key_words": ("Washington", "George"),
        "room_description": "&wA He stands forever in the position he was in crossing the Deleware.&N",
        "description": (
            "A man lost in the past.\n"
        ),
        "race": "Human",
        "class": "President",
        "level": 1,
        "stats": [100, 100, 100, 100, 100, 100],
        "aggro": False,
        "wander": False,
# Module-level spawn — rooms.py calls  M.spawn("void_guardian")
spawn = make_spawner(TEMPLATES, lambda: Mob)