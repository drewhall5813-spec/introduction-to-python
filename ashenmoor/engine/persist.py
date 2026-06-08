"""
ashenmoor.engine.persist
─────────────────────────
SQLite persistence for player character state.
"""

import json
import time
import sqlite3


_SCHEMA = """
PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS world_state (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS characters (
    name              TEXT    PRIMARY KEY,
    race              TEXT    NOT NULL,
    class             TEXT    NOT NULL,
    level             INTEGER NOT NULL DEFAULT 1,
    xp                INTEGER NOT NULL DEFAULT 0,
    stats             TEXT    NOT NULL,
    max_hp            INTEGER NOT NULL,
    hp                INTEGER NOT NULL,
    location          INTEGER NOT NULL,
    updated_at        REAL    NOT NULL,
    status_effects    TEXT    NOT NULL DEFAULT '[]',
    toggles           TEXT    NOT NULL DEFAULT '{}',
    potion_log        TEXT    NOT NULL DEFAULT '[]',
    sex               TEXT    NOT NULL DEFAULT 'male',
    coins             TEXT    NOT NULL DEFAULT '{}',
    bank_coins        TEXT    NOT NULL DEFAULT '{}',
    moves             INTEGER NOT NULL DEFAULT 100,
    max_moves         INTEGER NOT NULL DEFAULT 100,
    position          TEXT    NOT NULL DEFAULT 'standing',
    alignment         TEXT    NOT NULL DEFAULT 'True Neutral',
    title             TEXT    NOT NULL DEFAULT '',
    wimpy             INTEGER,
    detect_flags      TEXT    NOT NULL DEFAULT '[]',
    protect_flags     TEXT    NOT NULL DEFAULT '[]',
    enchant_flags     TEXT    NOT NULL DEFAULT '[]',
    play_time_seconds INTEGER NOT NULL DEFAULT 0,
    dnd               TEXT    NOT NULL DEFAULT 'null',
    powers            TEXT    NOT NULL DEFAULT '[]'
);

CREATE TABLE IF NOT EXISTS inventory (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    position        INTEGER NOT NULL,
    item_data       TEXT    NOT NULL,
    PRIMARY KEY (character_name, position)
);

CREATE TABLE IF NOT EXISTS equipment (
    character_name  TEXT    NOT NULL
        REFERENCES characters(name) ON DELETE CASCADE,
    slot            TEXT    NOT NULL,
    item_index      INTEGER NOT NULL DEFAULT 0,
    item_data       TEXT    NOT NULL,
    PRIMARY KEY (character_name, slot, item_index)
);
"""

# Migrations — run once at open_db time, ignored if column already exists
_MIGRATIONS = [
    "ALTER TABLE characters ADD COLUMN status_effects    TEXT    NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN toggles           TEXT    NOT NULL DEFAULT '{}'",
    "ALTER TABLE characters ADD COLUMN potion_log        TEXT    NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN sex               TEXT    NOT NULL DEFAULT 'male'",
    "ALTER TABLE characters ADD COLUMN coins             TEXT    NOT NULL DEFAULT '{}'",
    "ALTER TABLE characters ADD COLUMN bank_coins        TEXT    NOT NULL DEFAULT '{}'",
    "ALTER TABLE characters ADD COLUMN moves             INTEGER NOT NULL DEFAULT 100",
    "ALTER TABLE characters ADD COLUMN max_moves         INTEGER NOT NULL DEFAULT 100",
    "ALTER TABLE characters ADD COLUMN position          TEXT    NOT NULL DEFAULT 'standing'",
    "ALTER TABLE characters ADD COLUMN alignment         TEXT    NOT NULL DEFAULT 'True Neutral'",
    "ALTER TABLE characters ADD COLUMN title             TEXT    NOT NULL DEFAULT ''",
    "ALTER TABLE characters ADD COLUMN wimpy             INTEGER",
    "ALTER TABLE characters ADD COLUMN detect_flags      TEXT    NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN protect_flags     TEXT    NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN enchant_flags     TEXT    NOT NULL DEFAULT '[]'",
    "ALTER TABLE characters ADD COLUMN play_time_seconds INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE characters ADD COLUMN dnd               TEXT    NOT NULL DEFAULT 'null'",
    "ALTER TABLE characters ADD COLUMN powers            TEXT    NOT NULL DEFAULT '[]'",
]


def open_db(path: str = "ashenmoor.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)
    conn.commit()
    for stmt in _MIGRATIONS:
        try:
            conn.execute(stmt)
            conn.commit()
        except sqlite3.OperationalError:
            pass   # column already exists
    return conn


# ── Item serialisation ────────────────────────────────────────────────────────

def _item_to_dict(item) -> dict:
    from ..world.objects import Weapon, Container, Item, Scroll, Potion

    base = {
        "type":             type(item).__name__,
        "name":             item.name,
        "key_words":        list(item.key_words),
        "room_description": item.room_description,
        "description":      item.description,
    }

    if isinstance(item, Weapon):
        base.update({
            "weight":     item.weight,
            "mod":        item.mod,
            "wear_on":    item.wear_on,
            "dice":       item.dice,
            "hitroll":    item.hitroll,
            "damroll":    item.damroll,
            "two_handed": item.two_handed,
            "proc":       item.proc,
            "powers":     item.powers,
            "stat_mods":  getattr(item, "stat_mods", {}),
            "save_mods":  getattr(item, "save_mods", {}),
            "ac_bonus":   getattr(item, "ac_bonus",  0),
            "armor_type": getattr(item, "armor_type", None),
        })

    elif isinstance(item, Scroll):
        base.update({
            "weight":    item.weight,
            "mod":       item.mod,
            "wear_on":   item.wear_on,
            "effect":    item.effect,
            "apply_msg": item.apply_msg,
            "room_msg":  item.room_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name", "key_words", "room_description", "description", "type")},
        })

    elif isinstance(item, Potion):
        base.update({
            "weight":    item.weight,
            "mod":       item.mod,
            "wear_on":   item.wear_on,
            "effect":    item.effect,
            "apply_msg": item.apply_msg,
            **{k: v for k, v in item._data.items()
               if k not in ("name", "key_words", "room_description", "description", "type")},
        })

    elif isinstance(item, Container):
        base.update({
            "weight":              item.weight,
            "mod":                 item.mod,
            "wear_on":             item.wear_on,
            "capacity":            item.capacity,
            "weightless_capacity": item.weightless_capacity,
            "is_open":             item.is_open,
            "contents":            [_item_to_dict(c) for c in item.contents],
        })

    elif isinstance(item, Item):
        base.update({
            "weight":     item.weight,
            "mod":        item.mod,
            "wear_on":    item.wear_on,
            "stat_mods":  getattr(item, "stat_mods", {}),
            "save_mods":  getattr(item, "save_mods", {}),
            "ac_bonus":   getattr(item, "ac_bonus",  0),
            "armor_type": getattr(item, "armor_type", None),
            "is_key":     getattr(item, "is_key",    False),
            "key_name":   getattr(item, "key_name",  None),
        })

    return base


def _dict_to_item(data: dict):
    from ..world.objects import Weapon, Container, Item, Object, Scroll, Potion

    t = data.get("type", "Object")

    if t == "Weapon":
        return Weapon(data)

    if t == "Container":
        d        = dict(data)
        contents = d.pop("contents", [])
        obj      = Container(d)
        obj.contents = [_dict_to_item(c) for c in contents]
        return obj

    if t == "Scroll":
        return Scroll(data)

    if t == "Potion":
        return Potion(data)

    if t == "Item":
        return Item(data)

    return Object(data)


# ── World time ────────────────────────────────────────────────────────────────

def save_world_time(conn: sqlite3.Connection, total_minutes: int) -> None:
    with conn:
        conn.execute(
            "INSERT OR REPLACE INTO world_state (key, value) VALUES ('total_minutes', ?)",
            (str(total_minutes),),
        )


def load_world_time(conn: sqlite3.Connection) -> int:
    row = conn.execute(
        "SELECT value FROM world_state WHERE key = 'total_minutes'"
    ).fetchone()
    return int(row["value"]) if row else 0


# ── Powers serialisation helper ───────────────────────────────────────────────

def _powers_to_json(powers: list) -> str:
    """
    Serialise the powers list.  Each power dict may contain callables
    (e.g. "effect" functions) — those are skipped; only JSON-safe keys
    are stored.  The powers list is typically reconstructed from the
    class template on load anyway (warrior powers are re-attached in
    the shell-char builder), so this is a belt-and-suspenders fallback.
    """
    safe = []
    for p in powers:
        entry = {}
        for k, v in p.items():
            try:
                json.dumps(v)
                entry[k] = v
            except (TypeError, ValueError):
                pass   # skip non-serialisable values (callables, etc.)
        safe.append(entry)
    return json.dumps(safe)


# ── Save ──────────────────────────────────────────────────────────────────────

def save_character(
    conn:       sqlite3.Connection,
    char,
    location:   int,
    include_hp: bool = False,
) -> None:
    now = time.time()
    hp  = getattr(char, "hp", char.max_hp)

    # Accumulate total play time including current session
    # (caller is responsible for passing updated play_time_seconds if needed)
    play_time = getattr(char, "play_time_seconds", 0)

    coins      = getattr(char, "coins",      {"gold": 0, "silver": 0, "copper": 0})
    bank_coins = getattr(char, "bank_coins", {"gold": 0, "silver": 0, "copper": 0})

    with conn:
        conn.execute("""
            INSERT INTO characters
                (name, race, class, level, xp, stats, max_hp, hp, location, updated_at,
                 coins, bank_coins, moves, max_moves, position, alignment, title, wimpy,
                 detect_flags, protect_flags, enchant_flags, play_time_seconds, dnd, powers)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                race              = excluded.race,
                class             = excluded.class,
                level             = excluded.level,
                xp                = excluded.xp,
                stats             = excluded.stats,
                max_hp            = excluded.max_hp,
                hp                = CASE WHEN ? THEN excluded.hp ELSE hp END,
                location          = excluded.location,
                updated_at        = excluded.updated_at,
                coins             = excluded.coins,
                bank_coins        = excluded.bank_coins,
                moves             = excluded.moves,
                max_moves         = excluded.max_moves,
                position          = excluded.position,
                alignment         = excluded.alignment,
                title             = excluded.title,
                wimpy             = excluded.wimpy,
                detect_flags      = excluded.detect_flags,
                protect_flags     = excluded.protect_flags,
                enchant_flags     = excluded.enchant_flags,
                play_time_seconds = excluded.play_time_seconds,
                dnd               = excluded.dnd,
                powers            = excluded.powers
        """, (
            char.name, char.race, char.cclass,
            char.level, getattr(char, "xp", 0),
            json.dumps(char.stats),
            char.max_hp, hp, location, now,
            # extra fields
            json.dumps(coins),
            json.dumps(bank_coins),
            getattr(char, "moves",     100),
            getattr(char, "max_moves", 100),
            getattr(char, "position",  "standing"),
            getattr(char, "alignment", "True Neutral"),
            getattr(char, "title",     ""),
            getattr(char, "wimpy",     None),
            json.dumps(getattr(char, "detect_flags",  [])),
            json.dumps(getattr(char, "protect_flags", [])),
            json.dumps(getattr(char, "enchant_flags", [])),
            play_time,
            json.dumps(getattr(char, "dnd", None)),
            _powers_to_json(getattr(char, "powers", [])),
            # UPSERT conditional
            1 if include_hp else 0,
        ))

        # Inventory
        conn.execute("DELETE FROM inventory WHERE character_name = ?", (char.name,))
        for pos, item in enumerate(char.inventory):
            conn.execute(
                "INSERT INTO inventory (character_name, position, item_data) VALUES (?, ?, ?)",
                (char.name, pos, json.dumps(_item_to_dict(item))),
            )

        # Equipment
        conn.execute("DELETE FROM equipment WHERE character_name = ?", (char.name,))
        from ..world.equipment import DUAL_SLOTS
        for slot, equipped in char.equipment.items():
            items = equipped if isinstance(equipped, list) else [equipped]
            for idx, item in enumerate(items):
                conn.execute(
                    "INSERT INTO equipment (character_name, slot, item_index, item_data) VALUES (?, ?, ?, ?)",
                    (char.name, slot, idx, json.dumps(_item_to_dict(item))),
                )

        # Status effects (flags set → list for JSON)
        status_effects = getattr(char, "status_effects", [])
        serializable   = []
        for eff in status_effects:
            e          = dict(eff)
            e["flags"] = list(e.get("flags", set()))
            serializable.append(e)
        conn.execute(
            "UPDATE characters SET status_effects = ? WHERE name = ?",
            (json.dumps(serializable), char.name),
        )
        conn.execute(
            "UPDATE characters SET toggles = ? WHERE name = ?",
            (json.dumps(getattr(char, "toggles", {})), char.name),
        )
        conn.execute(
            "UPDATE characters SET potion_log = ? WHERE name = ?",
            (json.dumps(getattr(char, "potion_log", [])), char.name),
        )
        conn.execute(
            "UPDATE characters SET sex = ? WHERE name = ?",
            (getattr(char, "sex", "male"), char.name),
        )


# ── Load ──────────────────────────────────────────────────────────────────────

def load_character(
    conn: sqlite3.Connection,
    name: str,
    char,
) -> int | None:
    row = conn.execute(
        "SELECT * FROM characters WHERE name = ?", (name,)
    ).fetchone()

    if row is None:
        return None

    # Core stats
    char.level  = row["level"]
    char.xp     = row["xp"]
    char.stats  = json.loads(row["stats"])
    char.max_hp = row["max_hp"]
    char.hp     = row["hp"]

    # Currency
    char.coins      = json.loads(row["coins"]      or "{}")
    char.bank_coins = json.loads(row["bank_coins"] or "{}")
    # Ensure all keys present
    for purse in (char.coins, char.bank_coins):
        purse.setdefault("gold",   0)
        purse.setdefault("silver", 0)
        purse.setdefault("copper", 0)

    # Movement
    char.moves     = row["moves"]     if row["moves"]     is not None else 100
    char.max_moves = row["max_moves"] if row["max_moves"] is not None else 100

    # Character state
    char.position          = row["position"]  or "standing"
    char.alignment         = row["alignment"] or "True Neutral"
    char.title             = row["title"]     or ""
    char.wimpy             = row["wimpy"]     # None = disabled
    char.play_time_seconds = row["play_time_seconds"] or 0

    # Flags
    char.detect_flags  = json.loads(row["detect_flags"]  or "[]")
    char.protect_flags = json.loads(row["protect_flags"] or "[]")
    char.enchant_flags = json.loads(row["enchant_flags"] or "[]")

    # D&D state — only restore if the char doesn't already have a populated dnd dict
    # (the shell-char builder sets up the correct warrior dnd dict; we merge into it)
    saved_dnd = json.loads(row["dnd"] or "null")
    if saved_dnd and isinstance(saved_dnd, dict):
        existing_dnd = getattr(char, "dnd", None) or {}
        # Merge saved values into the existing dnd structure so class features
        # (hit_die, saving_throw_proficiencies, etc.) from the template survive
        existing_dnd.update(saved_dnd)
        char.dnd = existing_dnd

    # Powers — warrior powers are already set by the shell-char builder;
    # only restore if the char has none (non-warrior classes, future classes)
    if not getattr(char, "powers", None):
        saved_powers = json.loads(row["powers"] or "[]")
        if saved_powers:
            char.powers = saved_powers

    # Status effects (flags list → set)
    raw_effects = json.loads(row["status_effects"] or "[]")
    for eff in raw_effects:
        eff["flags"] = set(eff.get("flags", []))
    char.status_effects = raw_effects
    from ..world.effects import recalc_status
    recalc_status(char)

    # Misc
    char.toggles    = json.loads(row["toggles"]    or "{}")
    char.potion_log = json.loads(row["potion_log"] or "[]")
    char.sex        = row["sex"] if row["sex"] else "male"

    # Inventory
    inv_rows = conn.execute(
        "SELECT item_data FROM inventory WHERE character_name = ? ORDER BY position",
        (name,),
    ).fetchall()
    char.inventory = [_dict_to_item(json.loads(r["item_data"])) for r in inv_rows]

    # Equipment
    eq_rows = conn.execute(
        "SELECT slot, item_index, item_data FROM equipment "
        "WHERE character_name = ? ORDER BY slot, item_index",
        (name,),
    ).fetchall()

    from ..world.equipment import DUAL_SLOTS
    char.equipment = {}
    for r in eq_rows:
        slot = r["slot"]
        item = _dict_to_item(json.loads(r["item_data"]))
        if slot in DUAL_SLOTS:
            char.equipment.setdefault(slot, []).append(item)
        else:
            char.equipment[slot] = item

    return row["location"]
