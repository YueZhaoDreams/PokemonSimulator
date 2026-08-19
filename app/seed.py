from __future__ import annotations

import json
from pathlib import Path

from app.config import DATA_DIR, SAMPLES_DIR
from app.engine.models import Card
from app.recognition.images import dhash, load_image
from app.seed_data import SET_A_NAMES, SET_B_NAMES, SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, build_fallback_deck

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
    key = which.lower().replace("set-", "").replace("seed-", "")
    key = {"1": "a", "2": "b", "3": "c", "4": "d", "5": "s"}.get(key, key)
    if key not in decks:
        raise KeyError(f"unknown seed deck {which}")
    return decks[key]


def load_seed_payload() -> dict:
    if SEED_PATH.exists():
        data = json.loads(SEED_PATH.read_text())
        dirty = False
        if "c" not in data or "d" not in data or "s" not in data:
            extra = _cd_payload(enrich=True)
            data["c"] = extra["c"]
            data["d"] = extra["d"]
            data["s"] = extra["s"]
            dirty = True
        # Set E was folded into Set C — drop any leftover seed.
        if "e" in data:
            del data["e"]
            dirty = True
        # Refresh Set C whenever the locked list changes (Tool Box / Hop counts).
        expected_c = [c.name for c in _repeat_named_cards(list(SET_C_NAMES), enrich=False)]
        have_c = [c.get("name") for c in (data.get("c") or {}).get("cards") or []]
        if have_c != expected_c:
            data["c"] = _cd_payload(enrich=False)["c"]
            dirty = True
        expected_s = [c.name for c in _repeat_named_cards(list(SET_S_NAMES), enrich=False)]
        have_s = [c.get("name") for c in (data.get("s") or {}).get("cards") or []]
        if have_s != expected_s:
            data["s"] = _cd_payload(enrich=False)["s"]
            dirty = True
        if dirty:
            SEED_PATH.write_text(json.dumps(data, indent=2))
        _refresh_hashes(data)
        return data
    payload = build_seed_payload(enrich=False)
    SEED_PATH.write_text(json.dumps(payload, indent=2))
    _refresh_hashes(payload)
    return payload


def _repeat_named_cards(names: list[str], enrich: bool) -> list[Card]:
    from app.catalog import PREFERRED_IDS, energy_card, fetch_full, normalize_card
    from app.seed_data import fallback_named

    cache: dict[str, Card] = {}
    out: list[Card] = []
    for name in names:
        if name not in cache:
            if name.lower().endswith(" energy") and "double" not in name.lower():
                cache[name] = energy_card(name.split()[0])
            elif enrich:
                try:
                    cid = PREFERRED_IDS.get(name)
                    card = normalize_card(fetch_full(cid)) if cid else fallback_named(name)
                    if card.name.lower() != name.lower():
                        card = fallback_named(name)
                    cache[name] = card
                except Exception:
                    cache[name] = fallback_named(name)
            else:
                cache[name] = fallback_named(name)
        out.append(cache[name])
    return out


def _cd_payload(enrich: bool = True) -> dict:
    cards_c = _repeat_named_cards(list(SET_C_NAMES), enrich)
    cards_d = _repeat_named_cards(list(SET_D_NAMES), enrich)
    cards_s = _repeat_named_cards(list(SET_S_NAMES), enrich)
    return {
        "c": {
            "id": "seed-c",
            "name": "Set C (Clefairy / Mewtwo)",
            "sample": None,
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_c],
        },
        "d": {
            "id": "seed-d",
            "name": "Set D (Charm Ogerpon)",
            "sample": None,
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_d],
        },
        "s": {
            "id": "seed-s",
            "name": "Set S (Floragato hunter)",
            "sample": None,
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_s],
        },
    }


def _assign_named_prints(cards: list, name: str, prints: list) -> list:
    """Replace successive copies of `name` with the given printings, in order."""
    idx = 0
    out = []
    for card in cards:
        card_name = card.name if isinstance(card, Card) else card.get("name")
        if card_name == name and idx < len(prints):
            out.append(prints[idx])
            idx += 1
        else:
            out.append(card)
    return out


def build_seed_payload(enrich: bool = True) -> dict:
    from app.catalog import PRINT_PREFER
    from app.seed_data import fallback_named

    prefer_a = {
        **PRINT_PREFER,
        "Rockruff": ["invite out", "smash kick"],
    }
    prefer_b = {
        **PRINT_PREFER,
        "Pikachu": ["paralyze", "Thunder Shock", "Tail Whap"],
        "Rockruff": ["double draw", "rear kick"],
    }
    builder = _try_enrich if enrich else lambda names, prefer=None: build_fallback_deck(names)
    cards_a = builder(SET_A_NAMES, prefer_a)
    cards_b = builder(SET_B_NAMES, prefer_b)
    # After A traded Cosmic Eclipse Pikachu for B's Tulip, B holds both carpet prints:
    # first copy = original Burning Shadows Thunder Shock, second = Nuzzle / Volt Tackle.
    nuzzle = fallback_named("pikachu-nuzzle")
    shock = fallback_named("Pikachu")
    if enrich:
        try:
            from app.catalog import fetch_full, normalize_card

            nuzzle = normalize_card(fetch_full("sm12-66"))  # Cosmic Eclipse, moved A → B
            shock = normalize_card(fetch_full("sm3-40"))  # Burning Shadows, original Set B
            # Distinct Rockruff prints: A howls at the moon (CZ), B rolls in grass (Lost Origin).
            a_ruff = normalize_card(fetch_full("swsh12.5-073"))
            b_ruff = normalize_card(fetch_full("swsh11-109"))
            cards_a = [a_ruff if c.name == "Rockruff" else c for c in cards_a]
            cards_b = [b_ruff if c.name == "Rockruff" else c for c in cards_b]
        except Exception:
            pass
    cards_b = _assign_named_prints(cards_b, "Pikachu", [shock, nuzzle])
    cd = _cd_payload(enrich=enrich)
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
        "c": cd["c"],
        "d": cd["d"],
        "s": cd["s"],
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
