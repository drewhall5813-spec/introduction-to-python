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
3001: Room(
        {
            "number": 1,
            "name": "&GGarden&N of &gEden&N",
            "description": "&GThere&N &gis&N &Ga huge garden&N streching for miles.There is a &Gtree&N in the &gmiddle of the Garden&N.\n &YGod is watching over his creation&N.",
            "indoors": False,
            "terrain": "rolling grass hills",
            "exits": [
                {"direction": "north", "roomId": 3002},
                {"direction": "north", "roomId": 2999},
            "objects": [
                O.spawn("Banana"),
                O.spawn("green leaf"),
                O.spawn("The Fruit"),
            ],
            "mobs": [
                M.spawn("Adam") ,
                M.spawn("Eve"),
                M.spawn("Slippery Serpant")],  # two independent students

        }
    ),
3002: Room(
        {
            "number": 2,
            "name": "Jericho",
            "description": "This is a city with a huge wall going around it to protect it.",
            "indoors": False,
            "terrain": "grass plane",
            "exits": [
                {"direction": "north", "roomId": 3003},
                {"direction": "north", "roomId": 3002},
            ],
            "objects": [
                O.spawn("The Horn"),
                O.spawn("Tunic")
            ],
            "mobs": [  
                M.spawn("Joshua") ,
                M.spawn("Israelite"),
                M.spawn("Trumpet Player")
            ],  # two independent students
        }
    ),
3003: Room(
        {
            "number": 3,
            "name": "Upper Room",
            "description": "This is the very room that Jesus and his disciples ate in during the last supper.",
            "indoors": True,
            "terrain": "Clay floor",
            "exits": [
                {"direction": "north", "roomId": 3004},
                {"direction": "north", "roomId": 3003},
            ],
            "objects": [
                O.spawn("The Holy Grail"),
                O.spawn("Bread"),
                O.spawn("Wine")
            ],
            "mobs": [  
                M.spawn("Jesus") ,
                M.spawn("Peter"),
                M.spawn("Matthew"),
                M.spawn("Judas"),
                M.spawn("John 1"),
                M.spawn("John 2"),
                M.spawn("Andrew"),
                M.spawn("James"),
                M.spawn("Philip"),
                M.spawn("Bartholomew"),
                M.spawn(""),
                M.spawn(""),
            ],
        }
    ),
}