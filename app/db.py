from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, DB_PATH
from app.engine.models import (
    FamilyRules,
    default_family_rules,
    default_rule_presets_for,
    legacy_rule_presets_for,
    normalize_rule_presets,
    rule_preset_summary,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sessions (
    token TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT,
    cards_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    owner_id TEXT,
    rules_json TEXT
);
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    title TEXT,
    messages_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    agent_id TEXT,
    owner_id TEXT
);
CREATE TABLE IF NOT EXISTS simulations (
    id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL,
    question TEXT,
    record_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value_json TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS lab_experiments (
    id TEXT PRIMARY KEY,
    owner_id TEXT NOT NULL,
    question TEXT,
    cells_json TEXT NOT NULL,
    queries_json TEXT NOT NULL,
    games INTEGER,
    seed INTEGER,
    results_json TEXT,
    locked_cell_id TEXT,
    lock_reason TEXT,
    script_text TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

LAB_SCRIPT_MAX_CHARS = 65_536


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)
        row = conn.execute("SELECT value_json FROM settings WHERE key='rules'").fetchone()
        if not row:
            conn.execute(
                "INSERT INTO settings(key, value_json) VALUES (?, ?)",
                ("rules", json.dumps(default_family_rules().to_dict())),
            )
        else:
            stored = json.loads(row["value_json"])
            fresh = default_family_rules()
            changed = False
            if stored.get("deck_size") == 28:
                stored["deck_size"] = fresh.deck_size
                changed = True
            if stored.get("extra_prize_for_ex") is not True:
                stored["extra_prize_for_ex"] = True
                changed = True
            if stored.get("max_copies_except_basic_energy") != 4:
                stored["max_copies_except_basic_energy"] = 4
                changed = True
            if stored.get("name") == "Family Cup (Rule B)":
                stored["name"] = fresh.name
                changed = True
            if "one card per mulligan" not in (stored.get("notes") or ""):
                stored["notes"] = fresh.notes
                changed = True
            if changed:
                stored["notes"] = fresh.notes
                conn.execute(
                    "UPDATE settings SET value_json=? WHERE key='rules'",
                    (json.dumps(stored),),
                )
        _ensure_chat_agent_id(conn)
        _ensure_owner_columns(conn)
        _ensure_deck_rules_column(conn)
        _ensure_lab_experiments(conn)
        admin_id = _ensure_admin(conn)
        _upsert_seed_decks(conn, owner_id=admin_id)
        conn.execute(
            "UPDATE decks SET owner_id=? WHERE owner_id IS NULL OR owner_id=''",
            (admin_id,),
        )
        conn.execute(
            "UPDATE chats SET owner_id=? WHERE owner_id IS NULL OR owner_id=''",
            (admin_id,),
        )


def _ensure_chat_agent_id(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(chats)")}
    if "agent_id" not in cols:
        conn.execute("ALTER TABLE chats ADD COLUMN agent_id TEXT")


def _ensure_owner_columns(conn: sqlite3.Connection) -> None:
    deck_cols = {row[1] for row in conn.execute("PRAGMA table_info(decks)")}
    if "owner_id" not in deck_cols:
        conn.execute("ALTER TABLE decks ADD COLUMN owner_id TEXT")
    chat_cols = {row[1] for row in conn.execute("PRAGMA table_info(chats)")}
    if "owner_id" not in chat_cols:
        conn.execute("ALTER TABLE chats ADD COLUMN owner_id TEXT")


def _ensure_deck_rules_column(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(decks)")}
    if "rules_json" not in cols:
        conn.execute("ALTER TABLE decks ADD COLUMN rules_json TEXT")
    rows = conn.execute("SELECT id, rules_json FROM decks").fetchall()
    for row in rows:
        if row["rules_json"]:
            continue
        presets = legacy_rule_presets_for(row["id"])
        conn.execute("UPDATE decks SET rules_json=? WHERE id=?", (json.dumps(presets), row["id"]))


def _ensure_lab_experiments(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS lab_experiments (
            id TEXT PRIMARY KEY,
            owner_id TEXT NOT NULL,
            question TEXT,
            cells_json TEXT NOT NULL,
            queries_json TEXT NOT NULL,
            games INTEGER,
            seed INTEGER,
            results_json TEXT,
            locked_cell_id TEXT,
            lock_reason TEXT,
            script_text TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )


def _ensure_admin(conn: sqlite3.Connection) -> str:
    from app.auth import hash_password, normalize_email

    email = normalize_email(ADMIN_EMAIL)
    row = conn.execute("SELECT id, role FROM users WHERE email=?", (email,)).fetchone()
    if row:
        if row["role"] != "admin":
            conn.execute("UPDATE users SET role='admin' WHERE id=?", (row["id"],))
        return row["id"]
    user_id = str(uuid.uuid4())
    conn.execute(
        "INSERT INTO users(id, email, password_hash, role, created_at) VALUES (?,?,?,?,?)",
        (user_id, email, hash_password(ADMIN_PASSWORD), "admin", _now()),
    )
    return user_id


def _upsert_seed_decks(conn: sqlite3.Connection, owner_id: str | None = None) -> None:
    from app.seed import load_seed_payload

    payload = load_seed_payload()
    now = _now()
    from app.seed import SEED_KEYS

    for key in SEED_KEYS:
        if key not in payload:
            continue
        deck = payload[key]
        existing = conn.execute("SELECT id, rules_json FROM decks WHERE id=?", (deck["id"],)).fetchone()
        presets_json = json.dumps(default_rule_presets_for(deck["id"]))
        if existing:
            conn.execute(
                "UPDATE decks SET name=?, source=?, owner_id=COALESCE(owner_id, ?), "
                "rules_json=COALESCE(rules_json, ?) WHERE id=?",
                (deck["name"], deck.get("sample"), owner_id, presets_json, deck["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO decks(id, name, source, cards_json, created_at, owner_id, rules_json) "
                "VALUES (?,?,?,?,?,?,?)",
                (deck["id"], deck["name"], deck.get("sample"), json.dumps(deck["cards"]), now, owner_id, presets_json),
            )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_rules() -> FamilyRules:
    with connect() as conn:
        row = conn.execute("SELECT value_json FROM settings WHERE key='rules'").fetchone()
    return FamilyRules.from_dict(json.loads(row["value_json"]) if row else {})


def save_rules(rules: FamilyRules) -> FamilyRules:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings(key, value_json) VALUES (?, ?)",
            ("rules", json.dumps(rules.to_dict())),
        )
    return rules


def list_decks(owner_id: str | None = None) -> list[dict]:
    with connect() as conn:
        if owner_id:
            rows = conn.execute(
                "SELECT id, name, source, cards_json, created_at, owner_id, rules_json FROM decks "
                "WHERE owner_id=? ORDER BY created_at",
                (owner_id,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, name, source, cards_json, created_at, owner_id, rules_json FROM decks ORDER BY created_at"
            ).fetchall()
    decks = []
    for row in rows:
        cards = json.loads(row["cards_json"])
        decks.append(_deck_dict(row, cards))
    return decks


def get_deck(deck_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM decks WHERE id=?", (deck_id,)).fetchone()
    if not row:
        return None
    cards = json.loads(row["cards_json"])
    return _deck_dict(row, cards)


def _deck_dict(row: sqlite3.Row, cards: list) -> dict:
    keys = row.keys()
    presets = _rule_presets_from_row(row)
    return {
        "id": row["id"],
        "name": row["name"],
        "source": row["source"],
        "created_at": row["created_at"],
        "owner_id": row["owner_id"] if "owner_id" in keys else None,
        "count": len(cards),
        "kind": _deck_kind(row["id"]),
        "rule_preset": rule_preset_summary(presets),
        "rule_presets": presets,
        "cards": cards,
    }


def _rule_presets_from_row(row: sqlite3.Row) -> list[str]:
    raw = None
    if "rules_json" in row.keys() and row["rules_json"]:
        try:
            raw = json.loads(row["rules_json"])
        except (TypeError, json.JSONDecodeError):
            raw = None
    presets = normalize_rule_presets(raw, fallback=legacy_rule_presets_for(row["id"]))
    return presets or legacy_rule_presets_for(row["id"])


def _deck_kind(deck_id: str) -> str:
    return "spare" if deck_id == "seed-spare" else "list"


def _deck_rule_preset(deck_id: str) -> str:
    """Carpet E/F are the no-Pokémon-energy lists; other seeds are Pokémon-as-energy."""
    return rule_preset_summary(legacy_rule_presets_for(deck_id))


def save_deck(
    name: str,
    cards: list[dict],
    source: str | None = None,
    deck_id: str | None = None,
    owner_id: str | None = None,
    rule_presets: list[str] | None = None,
) -> dict:
    deck_id = deck_id or str(uuid.uuid4())
    now = _now()
    with connect() as conn:
        existing = conn.execute("SELECT id, rules_json FROM decks WHERE id=?", (deck_id,)).fetchone()
        if rule_presets is not None:
            presets = normalize_rule_presets(rule_presets)
            if not presets:
                raise ValueError("Keep at least one rule.")
        elif not existing:
            presets = default_rule_presets_for(deck_id)
        elif existing["rules_json"]:
            presets = None
        else:
            presets = legacy_rule_presets_for(deck_id)
        if existing:
            if presets is None:
                conn.execute(
                    "UPDATE decks SET name=?, source=?, cards_json=?, owner_id=COALESCE(owner_id, ?) WHERE id=?",
                    (name, source, json.dumps(cards), owner_id, deck_id),
                )
            else:
                conn.execute(
                    "UPDATE decks SET name=?, source=?, cards_json=?, owner_id=COALESCE(owner_id, ?), rules_json=? WHERE id=?",
                    (name, source, json.dumps(cards), owner_id, json.dumps(presets), deck_id),
                )
        else:
            conn.execute(
                "INSERT INTO decks(id, name, source, cards_json, created_at, owner_id, rules_json) VALUES (?,?,?,?,?,?,?)",
                (
                    deck_id,
                    name,
                    source,
                    json.dumps(cards),
                    now,
                    owner_id,
                    json.dumps(presets or default_rule_presets_for(deck_id)),
                ),
            )
    return get_deck(deck_id)


def delete_deck(deck_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM decks WHERE id=?", (deck_id,))


def save_simulation(record: dict) -> dict:
    with connect() as conn:
        conn.execute(
            "INSERT INTO simulations(id, created_at, question, record_json) VALUES (?,?,?,?)",
            (record["id"], record["created_at"], record.get("question"), json.dumps(record)),
        )
    return record


def list_simulations(limit: int = 30) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, created_at, question, record_json FROM simulations ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    out = []
    for row in rows:
        record = json.loads(row["record_json"])
        out.append(
            {
                "id": row["id"],
                "created_at": row["created_at"],
                "question": row["question"],
                "win_rate_a": record.get("results", {}).get("win_rate_a"),
                "games": record.get("method", {}).get("games"),
                "learning": record.get("learning", {}).get("insights", [])[:3],
            }
        )
    return out


def get_simulation(sim_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT record_json FROM simulations WHERE id=?", (sim_id,)).fetchone()
    return json.loads(row["record_json"]) if row else None


def validate_lab_script_text(script_text: object) -> str | None:
    if script_text is None:
        return None
    if not isinstance(script_text, str):
        raise ValueError("script_text must be text")
    if "\x00" in script_text:
        raise ValueError("script_text must be text")
    if len(script_text) > LAB_SCRIPT_MAX_CHARS:
        raise ValueError(f"script_text must be at most {LAB_SCRIPT_MAX_CHARS} characters")
    return script_text or None


def _lab_experiment_from_row(row: sqlite3.Row, *, include_script: bool) -> dict:
    blob = {
        "id": row["id"],
        "owner_id": row["owner_id"],
        "question": row["question"],
        "cells": json.loads(row["cells_json"] or "[]"),
        "queries": json.loads(row["queries_json"] or "[]"),
        "games": row["games"],
        "seed": row["seed"],
        "results": json.loads(row["results_json"]) if row["results_json"] else None,
        "locked_cell_id": row["locked_cell_id"],
        "lock_reason": row["lock_reason"],
        "script_present": bool(row["script_text"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }
    if include_script:
        blob["script_text"] = row["script_text"]
    return blob


def get_lab_experiment(exp_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM lab_experiments WHERE id=?", (exp_id,)).fetchone()
    if not row:
        return None
    return _lab_experiment_from_row(row, include_script=True)


def list_lab_experiments(owner_id: str | None = None, limit: int = 50) -> list[dict]:
    with connect() as conn:
        if owner_id:
            rows = conn.execute(
                "SELECT * FROM lab_experiments WHERE owner_id=? ORDER BY updated_at DESC LIMIT ?",
                (owner_id, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM lab_experiments ORDER BY updated_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [_lab_experiment_from_row(row, include_script=False) for row in rows]


def save_lab_experiment(
    *,
    owner_id: str,
    question: str | None = None,
    cells: list | dict | None = None,
    queries: list | dict | None = None,
    games: int | None = None,
    seed: int | None = None,
    results: dict | list | None = None,
    locked_cell_id: str | None = None,
    lock_reason: str | None = None,
    script_text: str | None = None,
    exp_id: str | None = None,
) -> dict:
    if not owner_id:
        raise ValueError("owner_id is required")
    script = validate_lab_script_text(script_text)
    cells_json = json.dumps(cells if cells is not None else [])
    queries_json = json.dumps(queries if queries is not None else [])
    results_json = json.dumps(results) if results is not None else None
    exp_id = exp_id or str(uuid.uuid4())
    now = _now()
    with connect() as conn:
        existing = conn.execute("SELECT id FROM lab_experiments WHERE id=?", (exp_id,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE lab_experiments SET question=?, cells_json=?, queries_json=?, games=?, seed=?,
                    results_json=?, locked_cell_id=?, lock_reason=?, script_text=?, updated_at=?
                WHERE id=?
                """,
                (
                    question,
                    cells_json,
                    queries_json,
                    games,
                    seed,
                    results_json,
                    locked_cell_id,
                    lock_reason,
                    script,
                    now,
                    exp_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO lab_experiments(
                    id, owner_id, question, cells_json, queries_json, games, seed,
                    results_json, locked_cell_id, lock_reason, script_text, created_at, updated_at
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    exp_id,
                    owner_id,
                    question,
                    cells_json,
                    queries_json,
                    games,
                    seed,
                    results_json,
                    locked_cell_id,
                    lock_reason,
                    script,
                    now,
                    now,
                ),
            )
    saved = get_lab_experiment(exp_id)
    if not saved:
        raise RuntimeError("lab experiment was not saved")
    return saved


def get_chat(chat_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
    if not row:
        return None
    keys = row.keys()
    return {
        "id": row["id"],
        "title": row["title"],
        "messages": json.loads(row["messages_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "agent_id": row["agent_id"] if "agent_id" in keys else None,
        "owner_id": row["owner_id"] if "owner_id" in keys else None,
    }


def _escape_like(text: str) -> str:
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _chat_preview(messages: list[dict]) -> str:
    for msg in reversed(messages):
        content = (msg.get("content") or "").strip()
        if content:
            return content.replace("\n", " ")[:140]
    return ""


def list_chats(query: str | None = None, limit: int = 80, owner_id: str | None = None) -> list[dict]:
    q = (query or "").strip()
    with connect() as conn:
        params: list = []
        where = []
        if owner_id:
            where.append("owner_id=?")
            params.append(owner_id)
        if q:
            like = f"%{_escape_like(q)}%"
            where.append("(title LIKE ? ESCAPE '\\' OR messages_json LIKE ? ESCAPE '\\')")
            params.extend([like, like])
        clause = f"WHERE {' AND '.join(where)}" if where else ""
        params.append(limit)
        rows = conn.execute(
            f"SELECT id, title, messages_json, created_at, updated_at, owner_id FROM chats {clause} "
            "ORDER BY updated_at DESC LIMIT ?",
            params,
        ).fetchall()
    out = []
    for row in rows:
        messages = json.loads(row["messages_json"] or "[]")
        out.append(
            {
                "id": row["id"],
                "title": row["title"] or "Family cup chat",
                "preview": _chat_preview(messages),
                "turns": sum(1 for msg in messages if msg.get("role") == "user"),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
            }
        )
    return out


def delete_chat(chat_id: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM chats WHERE id=?", (chat_id,))


def save_chat(
    messages: list[dict],
    chat_id: str | None = None,
    title: str | None = None,
    agent_id: str | None = None,
    owner_id: str | None = None,
) -> dict:
    chat_id = chat_id or str(uuid.uuid4())
    now = _now()
    if not title:
        title = next((m["content"][:48] for m in messages if m.get("role") == "user"), "Family cup chat")
    with connect() as conn:
        existing = conn.execute("SELECT id, agent_id FROM chats WHERE id=?", (chat_id,)).fetchone()
        if existing:
            stored_agent = agent_id if agent_id is not None else existing["agent_id"]
            conn.execute(
                "UPDATE chats SET title=?, messages_json=?, updated_at=?, agent_id=?, owner_id=COALESCE(owner_id, ?) WHERE id=?",
                (title, json.dumps(messages), now, stored_agent, owner_id, chat_id),
            )
        else:
            conn.execute(
                "INSERT INTO chats(id, title, messages_json, created_at, updated_at, agent_id, owner_id) VALUES (?,?,?,?,?,?,?)",
                (chat_id, title, json.dumps(messages), now, now, agent_id, owner_id),
            )
    return get_chat(chat_id)


def get_user_by_email(email: str) -> dict | None:
    from app.auth import public_user

    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not row:
        return None
    user = public_user(row)
    user["password_hash"] = row["password_hash"]
    return user


def get_user_by_id(user_id: str) -> dict | None:
    from app.auth import public_user

    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return public_user(row) if row else None


def create_user(email: str, password_hash: str, role: str = "member") -> dict:
    from app.auth import public_user

    user_id = str(uuid.uuid4())
    now = _now()
    with connect() as conn:
        conn.execute(
            "INSERT INTO users(id, email, password_hash, role, created_at) VALUES (?,?,?,?,?)",
            (user_id, email, password_hash, role, now),
        )
        row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    return public_user(row)


def list_users() -> list[dict]:
    from app.auth import public_user

    with connect() as conn:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at").fetchall()
    return [public_user(row) for row in rows]


def create_session(user_id: str) -> str:
    from app.auth import new_session_token
    from app.config import SESSION_DAYS

    token = new_session_token()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(days=SESSION_DAYS)
    with connect() as conn:
        conn.execute(
            "INSERT INTO sessions(token, user_id, created_at, expires_at) VALUES (?,?,?,?)",
            (token, user_id, now.isoformat(), expires.isoformat()),
        )
    return token


def delete_session(token: str) -> None:
    with connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))


def user_from_session(token: str | None) -> dict | None:
    from app.auth import public_user

    if not token:
        return None
    with connect() as conn:
        row = conn.execute(
            "SELECT users.*, sessions.expires_at AS session_expires FROM sessions "
            "JOIN users ON users.id = sessions.user_id WHERE sessions.token=?",
            (token,),
        ).fetchone()
        if not row:
            return None
        expires = datetime.fromisoformat(row["session_expires"])
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires < datetime.now(timezone.utc):
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            return None
        return public_user(row)
