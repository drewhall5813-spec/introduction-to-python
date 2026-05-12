"""
zones.the_planes.rooms
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
            "name": "The Withered-Rose Tavern ",
            "description": "An average &yroadside tavern&N, it sits at the edge of a &gconiferous forest&N.\nThe interior is warmed by a large &rfireplace&N on the left wall and the scents of &mvarious&N &Yalcohols&N waft about the room.&N",
            "indoors": True,
            "terrain": "wooden floor",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
            #],
            #"objects": [
            #    O.spawn("silken_sack"),
            #    O.spawn("windsong"),
            #],
            #"mobs": [M.spawn("escbaalion")],  # two independent students
        }
    ),
}
