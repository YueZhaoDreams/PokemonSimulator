from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone

from app.config import DB_PATH
from app.engine.models import FamilyRules, default_family_rules

SCHEMA = """
CREATE TABLE IF NOT EXISTS decks (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    source TEXT,
    cards_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    title TEXT,
    messages_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
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
"""


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
            if stored.get("deck_size") == 28:
                fresh = default_family_rules()
                stored["deck_size"] = fresh.deck_size
                stored["notes"] = fresh.notes
                conn.execute(
                    "UPDATE settings SET value_json=? WHERE key='rules'",
                    (json.dumps(stored),),
                )
        _upsert_seed_decks(conn)


def _upsert_seed_decks(conn: sqlite3.Connection) -> None:
    from app.seed import load_seed_payload

    payload = load_seed_payload()
    now = _now()
    for key in ("a", "b", "c", "d", "s"):
        if key not in payload:
            continue
        deck = payload[key]
        existing = conn.execute("SELECT id FROM decks WHERE id=?", (deck["id"],)).fetchone()
        if existing:
            conn.execute(
                "UPDATE decks SET name=?, source=?, cards_json=? WHERE id=?",
                (deck["name"], deck.get("sample"), json.dumps(deck["cards"]), deck["id"]),
            )
        else:
            conn.execute(
                "INSERT INTO decks(id, name, source, cards_json, created_at) VALUES (?,?,?,?,?)",
                (deck["id"], deck["name"], deck.get("sample"), json.dumps(deck["cards"]), now),
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


def list_decks() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT id, name, source, cards_json, created_at FROM decks ORDER BY created_at").fetchall()
    decks = []
    for row in rows:
        cards = json.loads(row["cards_json"])
        decks.append(
            {
                "id": row["id"],
                "name": row["name"],
                "source": row["source"],
                "created_at": row["created_at"],
                "count": len(cards),
                "cards": cards,
            }
        )
    return decks


def get_deck(deck_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM decks WHERE id=?", (deck_id,)).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "name": row["name"],
        "source": row["source"],
        "created_at": row["created_at"],
        "cards": json.loads(row["cards_json"]),
    }


def save_deck(name: str, cards: list[dict], source: str | None = None, deck_id: str | None = None) -> dict:
    deck_id = deck_id or str(uuid.uuid4())
    now = _now()
    with connect() as conn:
        existing = conn.execute("SELECT id FROM decks WHERE id=?", (deck_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE decks SET name=?, source=?, cards_json=? WHERE id=?",
                (name, source, json.dumps(cards), deck_id),
            )
        else:
            conn.execute(
                "INSERT INTO decks(id, name, source, cards_json, created_at) VALUES (?,?,?,?,?)",
                (deck_id, name, source, json.dumps(cards), now),
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


def get_chat(chat_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM chats WHERE id=?", (chat_id,)).fetchone()
    if not row:
        return None
    return {
        "id": row["id"],
        "title": row["title"],
        "messages": json.loads(row["messages_json"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_chats() -> list[dict]:
    with connect() as conn:
        rows = conn.execute("SELECT id, title, created_at, updated_at FROM chats ORDER BY updated_at DESC").fetchall()
    return [dict(r) for r in rows]


def save_chat(messages: list[dict], chat_id: str | None = None, title: str | None = None) -> dict:
    chat_id = chat_id or str(uuid.uuid4())
    now = _now()
    if not title:
        title = next((m["content"][:48] for m in messages if m.get("role") == "user"), "Family cup chat")
    with connect() as conn:
        existing = conn.execute("SELECT id FROM chats WHERE id=?", (chat_id,)).fetchone()
        if existing:
            conn.execute(
                "UPDATE chats SET title=?, messages_json=?, updated_at=? WHERE id=?",
                (title, json.dumps(messages), now, chat_id),
            )
        else:
            conn.execute(
                "INSERT INTO chats(id, title, messages_json, created_at, updated_at) VALUES (?,?,?,?,?)",
                (chat_id, title, json.dumps(messages), now, now),
            )
    return get_chat(chat_id)
