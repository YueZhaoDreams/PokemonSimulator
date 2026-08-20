from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from app.config import DATA_DIR, SAMPLES_DIR
from app.engine.models import Card
from app.recognition.images import dhash, load_image
from app.seed_data import (
    SET_A_NAMES,
    SET_B_NAMES,
    SET_C_NAMES,
    SET_D_NAMES,
    SET_S_NAMES,
    SET_SPARE_NAMES,
    build_fallback_deck,
)

LIST_KEYS = ("a", "b", "c", "d", "s")
SEED_KEYS = (*LIST_KEYS, "spare")

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
    key = {"1": "a", "2": "b", "3": "c", "4": "d", "5": "s", "6": "spare", "spare-cards": "spare", "p": "spare"}.get(
        key, key
    )
    if key not in decks:
        raise KeyError(f"unknown seed deck {which}")
    return decks[key]


def load_seed_payload() -> dict:
    if SEED_PATH.exists():
        data = json.loads(SEED_PATH.read_text())
        dirty = False
        extra = {**_cd_payload(enrich=False), **_spare_payload(enrich=False)}
        for key, blob in extra.items():
            if key not in data:
                data[key] = blob
                dirty = True
        # Set E was folded into Set C — drop any leftover seed.
        if "e" in data:
            del data["e"]
            dirty = True
        spare = data.get("spare") or {}
        if spare.get("kind") != "spare" or spare.get("name") != "Spare Cards" or spare.get("id") != "seed-spare":
            spare = {**spare, "id": "seed-spare", "name": "Spare Cards", "kind": "spare", "sample": spare.get("sample")}
            data["spare"] = spare
            dirty = True
        for key, names in (
            ("a", SET_A_NAMES),
            ("b", SET_B_NAMES),
            ("c", SET_C_NAMES),
            ("d", SET_D_NAMES),
            ("s", SET_S_NAMES),
            ("spare", SET_SPARE_NAMES),
        ):
            have = [c.get("name") for c in (data.get(key) or {}).get("cards") or []]
            want = list(names)
            if have != want:
                data[key]["cards"] = _align_named_cards((data.get(key) or {}).get("cards") or [], want)
                dirty = True
            filled = _ensure_card_images(data[key]["cards"])
            if filled != data[key]["cards"]:
                data[key]["cards"] = filled
                dirty = True
        if dirty:
            SEED_PATH.write_text(json.dumps(data, indent=2))
        _refresh_hashes(data)
        return data
    payload = build_seed_payload(enrich=False)
    SEED_PATH.write_text(json.dumps(payload, indent=2))
    _refresh_hashes(payload)
    return payload


def _align_named_cards(existing: list, names: list[str]) -> list[dict]:
    """Keep existing printings, add missing names from fallback / basic energy."""
    from app.catalog import energy_card
    from app.seed_data import fallback_named

    pools: dict[str, deque] = {}
    for card in existing:
        blob = card if isinstance(card, dict) else card.to_dict()
        pools.setdefault(blob.get("name"), deque()).append(blob)
    out: list[dict] = []
    for name in names:
        q = pools.get(name)
        if q:
            out.append(q.popleft())
        elif name.lower().endswith(" energy") and "double" not in name.lower():
            out.append(energy_card(name.split()[0]).to_dict())
        else:
            out.append(fallback_named(name).to_dict())
    return out


def _ensure_card_images(cards: list[dict]) -> list[dict]:
    """Fill missing TCGDex art. Floragato keeps Slashing Claw; only the picture is swapped."""
    from app.catalog import ART_ONLY_IDS, PREFERRED_IDS, energy_card, fetch_full, normalize_card
    from app.seed_data import fallback_named

    cache: dict[str, dict] = {}
    out: list[dict] = []
    for card in cards:
        name = card.get("name") or ""
        if card.get("image") and name not in ART_ONLY_IDS:
            out.append(card)
            continue
        if name not in cache:
            if name.lower().endswith(" energy") and "double" not in name.lower():
                cache[name] = energy_card(name.split()[0]).to_dict()
            elif name in ART_ONLY_IDS:
                base = fallback_named(name)
                try:
                    cache[name] = _overlay_art(base, ART_ONLY_IDS[name]).to_dict()
                except Exception:
                    cache[name] = base.to_dict()
            else:
                cid = PREFERRED_IDS.get(name)
                try:
                    fetched = normalize_card(fetch_full(cid)).to_dict() if cid else None
                    if fetched and (fetched.get("name") or "").lower() == name.lower() and fetched.get("image"):
                        cache[name] = fetched
                    else:
                        cache[name] = card
                except Exception:
                    cache[name] = card
        src = cache[name]
        if src.get("image"):
            out.append(src)
        else:
            out.append(card)
    return out


def _overlay_art(card: Card, card_id: str) -> Card:
    from app.catalog import fetch_full, normalize_card

    art = normalize_card(fetch_full(card_id))
    blob = card.to_dict()
    blob["image"] = art.image
    blob["catalog_id"] = art.catalog_id
    blob["set_name"] = art.set_name
    return Card.from_dict(blob)


def _repeat_named_cards(names: list[str], enrich: bool) -> list[Card]:
    from app.catalog import ART_ONLY_IDS, PREFERRED_IDS, energy_card, fetch_full, normalize_card
    from app.seed_data import fallback_named

    cache: dict[str, Card] = {}
    out: list[Card] = []
    for name in names:
        if name not in cache:
            if name.lower().endswith(" energy") and "double" not in name.lower():
                cache[name] = energy_card(name.split()[0])
            elif name in ART_ONLY_IDS:
                card = fallback_named(name)
                try:
                    cache[name] = _overlay_art(card, ART_ONLY_IDS[name])
                except Exception:
                    cache[name] = card
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
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_c],
        },
        "d": {
            "id": "seed-d",
            "name": "Set D (Charm Ogerpon)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_d],
        },
        "s": {
            "id": "seed-s",
            "name": "Set S (Floragato hunter)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_s],
        },
    }


def _spare_payload(enrich: bool = True) -> dict:
    cards = _repeat_named_cards(list(SET_SPARE_NAMES), enrich)
    return {
        "spare": {
            "id": "seed-spare",
            "name": "Spare Cards",
            "sample": None,
            "kind": "spare",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards],
        }
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
    spare = _spare_payload(enrich=enrich)
    payload = {
        "a": {
            "id": "seed-a",
            "name": "Carpet Set A (Dondozo)",
            "sample": "set-a-web.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_a],
        },
        "b": {
            "id": "seed-b",
            "name": "Carpet Set B (Pikachu shock)",
            "sample": "set-b-web.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_b],
        },
        "c": cd["c"],
        "d": cd["d"],
        "s": cd["s"],
        "spare": spare["spare"],
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
