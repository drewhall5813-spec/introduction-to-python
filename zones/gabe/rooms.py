"""
zones.the_void.rooms
────────────────────
Room definitions for The Void zone.  Vnum range: 1 – 99.

Each room entry calls O.spawn() / M.spawn() to place fresh object and mob
instances.  Calling spawn() twice places two independent copies, so loot
or damage on one never affects the other.

Exit roomIds must match vnums defined here or in another loaded zone.
"""

from ashenmoor.world import Room
from . import objects as O
from . import mobs as M

ROOMS: dict[int, Room] = {
    1: Room(
        {
            "number": 1,
            "name": "The Cheese Layer",
            "description": "&WYou are in the cheese layer of the world.\n &N&yCheese&N is everywhere, in all shapes and sizes. &N",
            "indoors": False,
            "terrain": "cheese",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 3},
                {"direction": "up", "roomId": 1},
                {"direction": "down", "roomId": 1},
            ],
            "objects": [
                O.spawn("cheese wheel"),
                O.spawn("toy cheese"),
            ],
            "mobs": [M.spawn("cheese monster"), M.spawn("cheez sniffer"), M.spawn("the cheese spirit")],
        },
    ),
}
