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
            "name": "The Void",
            "description": "There is a weird feeling in the air, almost a feeling of doom. The ground moves slightly when you walk, as if it is floating.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 2},
                {"direction": "south", "roomId": 3},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 4},
                {"direction": "down", "roomId": 99002, "external": True}
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
                O.spawn("sword_that_seals_the_darkness"),
                O.spawn('hanging_tree'),
                O.spawn('pile_of_goo'),
                O.spawn('falcon_feather'),      
            ],
            "mobs": [
                M.spawn("void_dragon"),
                M.spawn("shadow_gremlin"),
                M.spawn("dark_mage"),
                M.spawn("dark_glob"),
                M.spawn("falcon_spy"),
            ],
        }
    ),
    2: Room(
        {
            "number": 2,
            "name": "A Destroyed House",
            "description": "You look around you at the devastated home. The roof is caved in, and there is dirty furniture and trinkets littered around the ground. There is a trapdoor in the floor in the back",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 5},
                {"direction": "down", "roomId": 7},
            ],
            "mobs": [
                M.spawn("shadow_gremlin"),
            ],
        }
    ),
    3: Room(
        {
            "number": 3,
            "name": "A Large Crater",
            "description": "You see a giant round hole in the ground. There is purple rocks scattered around.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 6},
            ],
            "objects": [
                O.spawn("sack_of_darkness"),
            ],
            "mobs": [
                M.spawn("dark_mage"),
            ],
        }
    ),
    4: Room(
        {
            "number": 4,
            "name": "Gooey Plains",
            "description": "It appears that this area used to be covered in grass, but now an &godd&N &mpurple&N &gslime&N covers the ground",
            "indoors": False,
            "terrain": "slime",
            "exits": [
                {"direction": "north", "roomId": 5},
                {"direction": "south", "roomId": 6},
                {"direction": "east", "roomId": 1},
                {"direction": "west", "roomId": 1},
            ],
            "mobs": [
                M.spawn("dark_glob"),
            ],            
        }
    ),
    5: Room(
        {
            "number": 5,
            "name": "Dead Fields",
            "description": "The field is flat and covered with dead, brownish grass",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "north", "roomId": 1},
                {"direction": "south", "roomId": 4},
                {"direction": "east", "roomId": 2},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
    6: Room(
        {
            "number": 6,
            "name": "Dead Fields",
            "description": "The field is flat and covered with dead, brownish grass",
            "indoors": False,
            "terrain": "grass",
            "exits": [
                {"direction": "north", "roomId": 4},
                {"direction": "south", "roomId": 1},
                {"direction": "east", "roomId": 3},
                {"direction": "west", "roomId": 1},
            ],
        }
    ),
    7: Room(
        {
            "number": 7,
            "name": "Mage's Dungeon",
            "description": "You climb down the ladder into a small, stone room. There is a workbench with various contraptions, and many shelves with &Mw&Ge&Yi&Cr&Md&Gl&Yy &Cc&Mo&Gl&Yo&Cr&Me&Gd &Yl&Ci&Mq&Gu&Yi&Cd&Ms.",
            "indoors": False,
            "terrain": "stone",
            "exits": [
                {"direction": "up", "roomId": 2},
            ],
            "mobs": [
                M.spawn("dark_mage"),
            ],
        }
    ),

}
