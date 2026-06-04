"""
zones.new_zone.objects
"""

from ashenmoor.world import Object, Item, Weapon, Container, Scroll
from ashenmoor.world.zone import make_spawner

TEMPLATES: dict[str, dict] = {
    "object_template": {
        "spawn_as":         Object,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
    },

    "item_template": {
        "spawn_as":         Item,
        "name":             "",
        "key_words":        (),
        "room_description": "",
        "description":      "",
        "weight":              0,
    },

    "treasure_chest": {
        "spawn_as":        Container,
        "name":            "&ya treasure chest&N",
        "key_words":       ("chest", "treasure"),
        "room_description":"A sturdy oak chest sits here.",
        "no_take":         True,       # can't pick it up
        "is_open":         False,      # starts closed
        "locked":          True,       # starts locked
        "key_name":        "chest key",
        "capacity":        50.0,
        "weight":          20.0,
        "contents": [                  # template keys — spawned automatically
           "windsong",
           "windsong",
           "dimensional_vault",
           "stoneskin_scroll", 
           "stoneskin_scroll", 
           "stoneskin_scroll", 
           "stoneskin_scroll", 
           "stoneskin_scroll", 
           "stoneskin_scroll", 
           "stoneskin_scroll" 
        ],
    },

    "chest_key": {
        "spawn_as":        Item,
        "name":            "&ya small brass key&N",
        "key_words":       ("key", "brass", "small"),
        "room_description":"A small &ybrass key&N lies here.",
        "is_key":          True,
        "key_name":        "chest key",   # must match chest's key_name exactly
        "weight":          0.1,
    },
    "silken_sack": {
        "spawn_as":         Container,
        "name":             "a &rtattered &csilken sack&N",
        "key_words":        ("tattered", "silken", "sack"),
        "room_description": "A &rtattered &csilken sack&N lies here, discarded.",
        "description":      "This sack seems to be in an awful condition.",
        "capacity":            200.0,
        "weightless_capacity": 100.0,
        "weight":              0,
        "is_open":             True,
    },

    "dimensional_vault": {
        "spawn_as":            Container,
        "name":                "&La dimensional vault&N",
        "key_words":           ("dimensional", "vault"),
        "room_description":    "&LA dimensional vault floats here, humming softly.&N",
        "description":         "A shimmering vault that exists partially outside this dimension.\nIt can hold an extraordinary amount without adding to your burden.",
        "capacity":            1000.0,
        "weightless_capacity": 1000.0,
        "weight":              0,
        "is_open":             True,
    },

    "stoneskin_scroll": {
        "spawn_as": Scroll,
        "name": "&wa &Lstoneskin&N &Yscroll&N",
        "key_words": ("parchment", "rolled", "stoneskin", "scroll"),
        "room_description": "&wa rolled up piece of &Yparchment&N lies here&N",
        "effects": [{"effect": "apply_stoneskin", "duration": 150},]

    },


    "windsong": {
        "spawn_as":         Weapon,
        "name":             "&ga &wg&Wl&N&wi&Wtt&N&wer&Wi&N&wng&N &gelven scimitar&N",
        "key_words":        ("scimitar", "elven", "glittering", "windsong"),
        "room_description": "&gA glittering elven scimitar lies here, humming softly.&N",
        "description": (
            "&gIts blade is encrusted with diamond dust.  This magically light\n"
            "&gelven blade glitters in the sunlight and seems to hum softly\n"
            "&gwhen wielded in battle.  Only a &WRanger&g may truly master it.&N"
        ),
        # Stats matching original: 3d4 base, +4 hit, +3 dam
        "dice":    "3d4",
        "hitroll": 4,
        "damroll": 3,
        "weight":  2,
        # Windsong proc: 1-in-33 chance per hit to fire extra swings.
        # Rangers only — non-rangers take damage and lose the weapon.
        # Grey Elf gets 3 bonus swings; Half Elf gets +2 on the first branch.
        "proc":    "windsong",
        # Active power — type 'windsong' or 'ws' while wielding.
        # Fires a guaranteed burst of extra swings (inner chaining still applies).
        # 4-tick (16 second) cooldown.
        "powers": [
            {
                "keywords":       ("windsong", "ws"),
                "name":           "Windsong",
                "cooldown_ticks": 4,
                "effect":         "windsong_burst",
                "user_msg": (
                    "&cYou channel your will through the scimitar — "
                    "&cw&Ca&N&cv&Ce&N&cs &Co&N&cf &Ce&N&cn&Ce&N&cr&Cg&N&cy&N&c "
                    "surge through the blade!&N"
                ),
                "room_msg": (
                    "&c{name}'s scimitar &Wflares&N&c as waves of "
                    "energy surge through it!&N"
                ),
            },
            {
                "keywords":       ("envenom", "en"),
                "name":           "Envenom",
                "cooldown_ticks": 3,
                "effect":         "apply_poison",
                "duration":       8,
                "dot_dice":       "1d6",
                "user_msg":       "&cYou envenom your strike with deadly poison!&N",
                "room_msg":       "&c{name} envenoms their strike with poison!&N",
            }
        ],
    },
}

spawn = make_spawner(TEMPLATES, lambda: Object)
