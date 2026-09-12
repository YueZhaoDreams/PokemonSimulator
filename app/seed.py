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
    SET_C60_NAMES,
    SET_D_NAMES,
    SET_D60_NAMES,
    SET_E_NAMES,
    SET_F_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_S_NAMES,
    SET_S60_NAMES,
    SET_T_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    SET_SPARE_NAMES,
    build_fallback_deck,
)

LIST_KEYS = ("a", "b", "c", "d", "e", "f", "g", "h", "s", "t", "c60", "d60", "s60", "t60", "t-meta", "t-unl")
SEED_KEYS = (*LIST_KEYS, "spare")

SEED_PATH = DATA_DIR / "seed_decks.json"
SAMPLE_HASHES: dict[str, int] = {}


def _is_basic_energy_name(name: str) -> bool:
    key = name.lower()
    return key.endswith(" energy") and "double" not in key and "boomerang" not in key


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
    key = {
        "1": "a",
        "2": "b",
        "3": "c",
        "4": "d",
        "5": "s",
        "6": "spare",
        "7": "t",
        "8": "e",
        "9": "f",
        "10": "g",
        "11": "c60",
        "12": "d60",
        "13": "s60",
        "14": "t60",
        "15": "t-meta",
        "16": "t-unl",
        "17": "h",
        "hedrick": "t-meta",
        "tmeta": "t-meta",
        "unl": "t-unl",
        "tunl": "t-unl",
        "spare-cards": "spare",
        "p": "spare",
    }.get(key, key)
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
            elif blob.get("name") and data[key].get("name") != blob["name"]:
                data[key]["name"] = blob["name"]
                if blob.get("sample"):
                    data[key]["sample"] = blob["sample"]
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
            ("e", SET_E_NAMES),
            ("f", SET_F_NAMES),
            ("g", SET_G_NAMES),
            ("h", SET_H_NAMES),
            ("s", SET_S_NAMES),
            ("t", SET_T_NAMES),
            ("c60", SET_C60_NAMES),
            ("d60", SET_D60_NAMES),
            ("s60", SET_S60_NAMES),
            ("t60", SET_T60_NAMES),
            ("t-meta", SET_T_META_NAMES),
            ("t-unl", SET_T_UNL_NAMES),
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
        from app.seed_data import fallback_named as _fallback_named

        nuzzle = _fallback_named("pikachu-nuzzle")
        shock = _fallback_named("Pikachu")
        want_ids = ["sm12-66", "sm3-40"]
        for key in ("b", "e"):
            if key not in data:
                continue
            have_ids = [c.get("catalog_id") for c in data[key]["cards"] if c.get("name") == "Pikachu"]
            if have_ids[:2] == want_ids:
                continue
            assigned = _assign_named_prints(data[key]["cards"], "Pikachu", [nuzzle, shock])
            as_dicts = [c.to_dict() if isinstance(c, Card) else c for c in assigned]
            if as_dicts != data[key]["cards"]:
                data[key]["cards"] = as_dicts
                dirty = True
        if "g" in data:
            claw = _fallback_named("starly-claw")
            staravia_90 = _fallback_named("staravia-brilliant")
            staravia_80 = _fallback_named("Staravia")
            want_starly = ["swsh9-117", "swsh9-117"]
            want_staravia = ["swsh9-118", "sv01-149"]
            have_starly = [c.get("catalog_id") for c in data["g"]["cards"] if c.get("name") == "Starly"]
            have_staravia = [c.get("catalog_id") for c in data["g"]["cards"] if c.get("name") == "Staravia"]
            cards_g = data["g"]["cards"]
            if have_starly[:2] != want_starly:
                cards_g = _assign_named_prints(cards_g, "Starly", [claw, claw])
            if have_staravia[:2] != want_staravia:
                cards_g = _assign_named_prints(cards_g, "Staravia", [staravia_90, staravia_80])
            ib = _fallback_named("Iron Boulder")
            refresh = {
                "Iron Boulder": ib,
                "Drifloon": _fallback_named("Drifloon"),
                "Drifblim": _fallback_named("Drifblim"),
                "Dedenne": _fallback_named("Dedenne"),
                "Misdreavus": _fallback_named("Misdreavus"),
                "Mismagius": _fallback_named("Mismagius"),
            }
            cards_g = [
                refresh.get((c.name if isinstance(c, Card) else c.get("name")), c)
                for c in cards_g
            ]
            as_dicts = [c.to_dict() if isinstance(c, Card) else c for c in cards_g]
            if as_dicts != data["g"]["cards"]:
                data["g"]["cards"] = as_dicts
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
        elif name.lower() == "boomerang energy":
            out.append(fallback_named(name).to_dict())
        elif _is_basic_energy_name(name):
            out.append(energy_card(name.split()[0]).to_dict())
        else:
            out.append(fallback_named(name).to_dict())
    return out


def _ensure_card_images(cards: list[dict]) -> list[dict]:
    """Fill missing TCGDex art. Floragato keeps Slashing Claw; only the picture is swapped."""
    from app.catalog import (
        ART_ONLY_IDS,
        EXTRA_PRINT_IDS,
        PREFERRED_IDS,
        allowed_print_ids,
        energy_card,
        fetch_full,
        normalize_card,
        _names_match,
        _looks_like_tcgdex_id,
        _tcgdex_low,
    )
    from app.seed_data import fallback_named

    cache: dict[str, dict] = {}
    out: list[dict] = []
    for card in cards:
        name = card.get("name") or ""
        cid = str(card.get("catalog_id") or "")
        allowed = allowed_print_ids(name)
        mismatched = bool(allowed and cid and not cid.startswith("fallback") and cid not in allowed)
        stale_body = False
        if not mismatched and allowed and cid in allowed and name not in EXTRA_PRINT_IDS:
            fb_card = fallback_named(name)
            if fb_card.catalog_id == cid:
                got_atk = [a.get("name") for a in (card.get("attacks") or [])]
                want_atk = [a.name for a in fb_card.attacks]
                if got_atk != want_atk or int(card.get("hp") or 0) != int(fb_card.hp or 0):
                    stale_body = True
        replace_body = mismatched or stale_body
        if (
            card.get("image")
            and not replace_body
            and (name not in ART_ONLY_IDS or cid == ART_ONLY_IDS.get(name))
        ):
            out.append(card)
            continue
        cache_key = cid if cid in (allowed or set()) else name
        if cache_key not in cache:
            if _is_basic_energy_name(name):
                cache[cache_key] = energy_card(name.split()[0]).to_dict()
            elif name in EXTRA_PRINT_IDS and cid in (allowed or set()):
                patched = dict(card)
                if not patched.get("image") and _looks_like_tcgdex_id(cid):
                    patched["image"] = _tcgdex_low(cid)
                    patched["catalog_id"] = cid
                cache[cache_key] = patched
            elif name in ART_ONLY_IDS:
                base = fallback_named(name)
                try:
                    cache[cache_key] = _overlay_art(base, ART_ONLY_IDS[name]).to_dict()
                except Exception:
                    cache[cache_key] = base.to_dict()
            else:
                fb = fallback_named(name).to_dict()
                if replace_body or fb.get("image"):
                    cache[cache_key] = fb
                else:
                    want = (cid if allowed and cid in allowed else None) or PREFERRED_IDS.get(name) or (cid if "-" in cid else "")
                    try:
                        fetched = normalize_card(fetch_full(want)).to_dict() if want else None
                        if fetched and _names_match(fetched.get("name") or "", name) and fetched.get("image"):
                            cache[cache_key] = fetched
                        else:
                            cache[cache_key] = fb
                    except Exception:
                        cache[cache_key] = fb
                if not cache[cache_key].get("image"):
                    pin = PREFERRED_IDS.get(name)
                    if pin and _looks_like_tcgdex_id(pin):
                        patched = dict(cache[cache_key])
                        patched["image"] = _tcgdex_low(pin)
                        patched["catalog_id"] = pin
                        cache[cache_key] = patched
        src = cache[cache_key]
        if replace_body and src.get("name"):
            out.append(src)
        elif src.get("image"):
            merged = dict(card)
            merged["image"] = src["image"]
            if src.get("catalog_id"):
                merged["catalog_id"] = src["catalog_id"]
            out.append(merged)
        else:
            pin = PREFERRED_IDS.get(name) or card.get("catalog_id")
            if pin and _looks_like_tcgdex_id(str(pin)):
                patched = dict(card)
                patched["image"] = _tcgdex_low(pin)
                patched["catalog_id"] = pin
                out.append(patched)
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
            if _is_basic_energy_name(name):
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
    cards_e = _repeat_named_cards(list(SET_E_NAMES), enrich)
    from app.seed_data import fallback_named

    nuzzle = fallback_named("pikachu-nuzzle")
    shock = fallback_named("Pikachu")
    if enrich:
        try:
            from app.catalog import fetch_full, normalize_card

            nuzzle = normalize_card(fetch_full("sm12-66"))
            shock = normalize_card(fetch_full("sm3-40"))
        except Exception:
            pass
    cards_e = _assign_named_prints(cards_e, "Pikachu", [nuzzle, shock])
    cards_f = _repeat_named_cards(list(SET_F_NAMES), enrich)
    cards_g = _repeat_named_cards(list(SET_G_NAMES), enrich)
    cards_g = _assign_named_prints(cards_g, "Starly", [fallback_named("starly-claw"), fallback_named("starly-claw")])
    cards_g = _assign_named_prints(
        cards_g,
        "Staravia",
        [fallback_named("staravia-brilliant"), fallback_named("Staravia")],
    )
    cards_h = _repeat_named_cards(list(SET_H_NAMES), enrich)
    cards_s = _repeat_named_cards(list(SET_S_NAMES), enrich)
    cards_t = _repeat_named_cards(list(SET_T_NAMES), enrich)
    cards_c60 = _repeat_named_cards(list(SET_C60_NAMES), enrich)
    cards_d60 = _repeat_named_cards(list(SET_D60_NAMES), enrich)
    cards_s60 = _repeat_named_cards(list(SET_S60_NAMES), enrich)
    cards_t60 = _repeat_named_cards(list(SET_T60_NAMES), enrich)
    cards_t_meta = _repeat_named_cards(list(SET_T_META_NAMES), enrich)
    cards_t_unl = _repeat_named_cards(list(SET_T_UNL_NAMES), enrich)
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
        "e": {
            "id": "seed-e",
            "name": "Carpet Set E (Walrein / Iris)",
            "sample": "set-e-carpet.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_e],
        },
        "f": {
            "id": "seed-f",
            "name": "Carpet Set F (Staraptor / Gengar)",
            "sample": "set-f-carpet.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_f],
        },
        "g": {
            "id": "seed-g",
            "name": "Carpet Set G (Clefairy / Ledian 60)",
            "sample": "set-g-carpet.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_g],
        },
        "h": {
            "id": "seed-h",
            "name": "Carpet Set H (Zapdos / Pikachu 60)",
            "sample": "set-h-carpet.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_h],
        },
        "s": {
            "id": "seed-s",
            "name": "Set S (Floragato hunter)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_s],
        },
        "t": {
            "id": "seed-t",
            "name": "Set T (Dragapult ex)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_t],
        },
        "c60": {
            "id": "seed-c60",
            "name": "Set C Standard 60 (Clefairy / Mewtwo)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_c60],
        },
        "d60": {
            "id": "seed-d60",
            "name": "Set D Standard 60 (Charm Ogerpon)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_d60],
        },
        "s60": {
            "id": "seed-s60",
            "name": "Set S Standard 60 (Floragato hunter)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_s60],
        },
        "t60": {
            "id": "seed-t60",
            "name": "Set T Standard 60 (Dragapult ex)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_t60],
        },
        "t-meta": {
            "id": "seed-t-meta",
            "name": "Worlds 2026 Hedrick Dragapult",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_t_meta],
        },
        "t-unl": {
            "id": "seed-t-unl",
            "name": "Unlimited Dragapult (Pidgeot / Rotom V)",
            "sample": None,
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_t_unl],
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
    # After A traded Cosmic Eclipse Pikachu for B's Tulip, B holds both carpet prints.
    # Carpet order is Nuzzle / Volt Tackle first, then Burning Shadows Thunder Shock.
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
    cards_b = _assign_named_prints(cards_b, "Pikachu", [nuzzle, shock])
    cd = _cd_payload(enrich=enrich)
    spare = _spare_payload(enrich=enrich)
    payload = {
        "a": {
            "id": "seed-a",
            "name": "Carpet Set A (Dondozo / Staraptor)",
            "sample": "set-a-web.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_a],
        },
        "b": {
            "id": "seed-b",
            "name": "Carpet Set B (Walrein / Pikachu shock)",
            "sample": "set-b-web.jpg",
            "kind": "list",
            "cards": [c.to_dict() if isinstance(c, Card) else c for c in cards_b],
        },
        "c": cd["c"],
        "d": cd["d"],
        "s": cd["s"],
        "t": cd["t"],
        "c60": cd["c60"],
        "d60": cd["d60"],
        "s60": cd["s60"],
        "t60": cd["t60"],
        "t-meta": cd["t-meta"],
        "t-unl": cd["t-unl"],
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
