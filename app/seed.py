from __future__ import annotations

import json
from pathlib import Path

from app.config import DATA_DIR, SAMPLES_DIR
from app.engine.models import Card
from app.recognition.images import dhash, load_image
from app.seed_data import SET_A_NAMES, SET_B_NAMES, build_fallback_deck

SEED_PATH = DATA_DIR / "seed_decks.json"
SAMPLE_HASHES: dict[str, int] = {}


def _try_enrich(names: list[str], prefer: dict[str, list[str]] | None = None) -> list[Card]:
    prefer = prefer or {}
    try:
        from app.catalog import resolve_name

        cards = []
        for name in names:
            card = resolve_name(name, prefer.get(name))
            # Keep the Thunder Shock Pikachu for family tests if API returns a dull print.
            if name.lower() == "pikachu" and not any("paralyze" in (a.text or "").lower() for a in card.attacks):
                from app.seed_data import fallback_named

                card = fallback_named("Pikachu")
            cards.append(card)
        return cards
    except Exception:
        return build_fallback_deck(names)


def load_seed_deck(which: str) -> dict:
    decks = load_seed_payload()
    key = "a" if which.lower() in {"a", "set-a", "1"} else "b"
    return decks[key]


def load_seed_payload() -> dict:
    if SEED_PATH.exists():
        data = json.loads(SEED_PATH.read_text())
        _refresh_hashes(data)
        return data
    payload = build_seed_payload(enrich=False)
    SEED_PATH.write_text(json.dumps(payload, indent=2))
    _refresh_hashes(payload)
    return payload


def build_seed_payload(enrich: bool = True) -> dict:
    builder = _try_enrich if enrich else lambda names, prefer=None: build_fallback_deck(names)
    cards_a = builder(SET_A_NAMES, {})
    cards_b = builder(SET_B_NAMES, {"Pikachu": ["paralyze", "Thunder Shock"]})
    payload = {
        "a": {
            "id": "seed-a",
            "name": "Carpet Set A (Dondozo)",
            "sample": "set-a-web.jpg",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_a],
        },
        "b": {
            "id": "seed-b",
            "name": "Carpet Set B (Pikachu shock)",
            "sample": "set-b-web.jpg",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_b],
        },
        "hashes": {},
    }
    _refresh_hashes(payload)
    payload["hashes"] = dict(SAMPLE_HASHES)
    return payload


def _refresh_hashes(payload: dict) -> None:
    SAMPLE_HASHES.clear()
    stored = payload.get("hashes") or {}
    for key, val in stored.items():
        SAMPLE_HASHES[key] = int(val)
    for key, filename in (("a", "set-a-web.jpg"), ("b", "set-b-web.jpg")):
        path = SAMPLES_DIR / filename
        if path.exists():
            try:
                SAMPLE_HASHES[key] = dhash(load_image(path))
            except Exception:
                pass


def cards_from_seed(which: str) -> list[Card]:
    deck = load_seed_deck(which)
    return [Card.from_dict(c) for c in deck["cards"]]
