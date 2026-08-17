from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx

from app.config import CACHE_DIR, TCGDEX_BASE
from app.engine.effects import parse_attack
from app.engine.models import Ability, Card

CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CLIENT = httpx.Client(timeout=20.0, headers={"User-Agent": "PokemonFamilySimulator/1.0"})

ENERGY_NAME_TO_TYPE = {
    "grass energy": "Grass",
    "fire energy": "Fire",
    "water energy": "Water",
    "lightning energy": "Lightning",
    "psychic energy": "Psychic",
    "fighting energy": "Fighting",
    "darkness energy": "Darkness",
    "metal energy": "Metal",
    "fairy energy": "Fairy",
    "basic grass energy": "Grass",
    "basic fire energy": "Fire",
    "basic water energy": "Water",
    "basic lightning energy": "Lightning",
    "basic psychic energy": "Psychic",
    "basic fighting energy": "Fighting",
    "basic darkness energy": "Darkness",
    "basic metal energy": "Metal",
}

TRAINER_KIND_HINTS = {
    "rare candy": "item",
    "quick ball": "item",
    "great ball": "item",
    "nest ball": "item",
    "nesting ball": "item",
    "picnic basket": "item",
    "energy search": "item",
    "energy retrieval": "item",
    "energy switch": "item",
    "ultra ball": "item",
    "poké ball": "item",
    "poke ball": "item",
    "tool box": "item",
    "trekking shoes": "item",
    "lake acuity": "stadium",
    "hop": "supporter",
    "youngster": "supporter",
    "shauna": "supporter",
    "jacq": "supporter",
    "tulip": "supporter",
}

# Carpet-photo printings confirmed via attack OCR phrases / user correction.
PREFERRED_IDS = {
    "Dondozo": "sv04-055",  # Supplemental Swallow-Up / Hydro Splash 180 (Paradox Rift)
    "Orthworm": "sv04-138",  # Punch and Draw / Crunch-Time Rush
    "Flutter Mane": "sv05-078",  # Hex Hurl
    "Pikachu": "sm3-40",  # Tail Whap / Thunder Shock
    "Tulip": "sv04-181",
    "Plusle": "sv04-060",
    "Crocalor": "sv04-024",
    "Salazzle": "swsh12.5-028",
    "Roselia": "swsh11-014",
    "Relicanth": "swsh11-101",
    "Carbink": "swsh11-108",
    "Hisuian Sliggoo": "swsh11-133",
    "Lickilicky": "swsh11-139",
    "Emolga": "sv10.5b-029",
    "Oddish": "swsh12.5-001",
    "Clefairy": "swsh11-062",
    "Dusclops": "swsh9-061",
    "Spinarak": "swsh10.5-006",
}

# When resolving by name, prefer candidates whose attacks/text match these phrases.
PRINT_PREFER = {
    "Dondozo": ["supplemental swallow", "hydro splash"],
    "Orthworm": ["crunch-time", "punch and draw"],
    "Flutter Mane": ["hex hurl"],
    "Pikachu": ["thunder shock", "tail whap", "paralyze"],
    "Roselia": ["soothing scent"],
    "Salazzle": ["tail trickery", "super singe"],
    "Carbink": ["lucky find", "power gem"],
    "Relicanth": ["into the deep"],
    "Plusle": ["plus damage"],
    "Emolga": ["static shock"],
    "Hisuian Sliggoo": ["rigidify", "gentle slap"],
    "Dusclops": ["fade to black"],
    "Oddish": ["leaf boomerang"],
    "Clefairy": ["wonder storm"],
    "Lickilicky": ["tongue slap", "heavy impact"],
    "Spinarak": ["poison sting"],
    "Corphish": ["crabhammer"],
    "Bronzor": ["spinning attack"],
    "Metang": ["bullet punch"],
    "Crocalor": ["rolling fireball"],
    "Tulip": ["psychic"],
}


def _cache_path(kind: str, key: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", key)[:180]
    folder = CACHE_DIR / kind
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{safe}.json"


def _get_json(url: str, cache_key: str) -> Any:
    path = _cache_path("http", cache_key)
    if path.exists():
        return json.loads(path.read_text())
    response = _CLIENT.get(url)
    response.raise_for_status()
    data = response.json()
    path.write_text(json.dumps(data))
    return data


def search_briefs(name: str) -> list[dict[str, Any]]:
    url = f"{TCGDEX_BASE}/cards?name={quote(name)}"
    data = _get_json(url, f"search-{name.lower()}")
    if isinstance(data, list):
        return data
    return data.get("data") or []


def fetch_full(card_id: str) -> dict[str, Any]:
    url = f"{TCGDEX_BASE}/cards/{quote(card_id)}"
    return _get_json(url, f"card-{card_id}")


def _image_url(raw: dict[str, Any]) -> str | None:
    image = raw.get("image")
    if not image:
        return None
    if image.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return image
    return f"{image}/low.webp"


def _trainer_kind(name: str, stage: str, category: str, trainer_type: str | None = None) -> str | None:
    if category.lower() != "trainer":
        return None
    hinted = TRAINER_KIND_HINTS.get(name.lower())
    if hinted:
        return hinted
    for blob in (trainer_type or "", stage or ""):
        stage_l = blob.lower()
        if "support" in stage_l:
            return "supporter"
        if "stadium" in stage_l:
            return "stadium"
        if "item" in stage_l or "tool" in stage_l:
            return "item"
    return "item"


def normalize_card(raw: dict[str, Any]) -> Card:
    category = raw.get("category") or "Pokemon"
    name = raw.get("name") or "Unknown"
    types = list(raw.get("types") or [])
    energy_type = None
    if category.lower() == "energy":
        energy_type = ENERGY_NAME_TO_TYPE.get(name.lower())
        if not energy_type and types:
            energy_type = types[0]
        if not energy_type:
            for energy_name, etype in ENERGY_NAME_TO_TYPE.items():
                if etype.lower() in name.lower():
                    energy_type = etype
                    break
            energy_type = energy_type or "Colorless"
        types = types or [energy_type]
        category = "Energy"

    attacks = [parse_attack(a) for a in raw.get("attacks") or []]
    abilities = [
        Ability(name=a.get("name") or "Ability", text=a.get("effect") or a.get("text") or "")
        for a in raw.get("abilities") or []
    ]
    set_info = raw.get("set") or {}
    trainer_type = raw.get("trainerType") or raw.get("trainer_type")
    stage = raw.get("stage") or ""
    trainer_kind = _trainer_kind(name, stage, category, trainer_type)
    if category.lower() == "trainer" and not stage:
        stage = (trainer_kind or "item").title()

    evolves = raw.get("evolveFrom") or raw.get("evolvesFrom") or raw.get("evolves_from")
    return Card(
        catalog_id=str(raw.get("id") or name),
        name=name,
        category=category,
        stage=stage,
        types=types,
        hp=int(raw.get("hp") or 0),
        attacks=attacks,
        abilities=abilities,
        weaknesses=list(raw.get("weaknesses") or []),
        resistances=list(raw.get("resistances") or []),
        retreat=int(raw.get("retreat") or 0),
        evolves_from=evolves,
        trainer_kind=trainer_kind,
        energy_type=energy_type,
        image=_image_url(raw),
        set_name=set_info.get("name") if isinstance(set_info, dict) else None,
        text=raw.get("effect") or raw.get("description") or "",
        dex_id=(raw.get("dexId") or [None])[0] if isinstance(raw.get("dexId"), list) else raw.get("dexId"),
    )


def _score_candidate(brief: dict[str, Any], name: str, prefer: list[str]) -> float:
    score = 0.0
    cid = str(brief.get("id") or "")
    cname = brief.get("name") or ""
    if cname.lower() == name.lower():
        score += 50
    elif name.lower() in cname.lower():
        score += 10
    else:
        score -= 20
    if "tcgp" in cid or cid.startswith("A") and "-" in cid:
        score -= 15
    if any(cid.startswith(prefix) for prefix in ("sv", "swsh", "sm", "xy")):
        score += 8
    if prefer:
        blob = json.dumps(brief).lower()
        score += 5 * sum(1 for p in prefer if p.lower() in blob)
    return score


def resolve_name(name: str, prefer: list[str] | None = None) -> Card:
    name = name.strip()
    energy = ENERGY_NAME_TO_TYPE.get(name.lower())
    if energy:
        return energy_card(energy)

    prefer = list(prefer or []) or list(PRINT_PREFER.get(name) or [])
    preferred_id = PREFERRED_IDS.get(name)
    if preferred_id:
        try:
            card = normalize_card(fetch_full(preferred_id))
            if not prefer:
                return card
            blob = json.dumps(card.to_dict()).lower()
            if any(p.lower() in blob for p in prefer):
                return card
            # Preferred id exists but does not match attack hints — keep searching.
        except Exception:
            pass

    briefs = search_briefs(name)
    exact = [b for b in briefs if (b.get("name") or "").lower() == name.lower()]
    pool = exact or briefs
    if not pool:
        return fallback_card(name)

    ranked = sorted(pool, key=lambda b: _score_candidate(b, name, prefer), reverse=True)
    for brief in ranked[:12]:
        try:
            full = fetch_full(brief["id"])
            card = normalize_card(full)
            if prefer:
                blob = json.dumps(card.to_dict()).lower()
                if any(p.lower() in blob for p in prefer):
                    return card
                continue
            return card
        except Exception:
            continue
    # Fall back to preferred id even without phrase match, then any ranked card.
    if preferred_id:
        try:
            return normalize_card(fetch_full(preferred_id))
        except Exception:
            pass
    for brief in ranked[:8]:
        try:
            return normalize_card(fetch_full(brief["id"]))
        except Exception:
            continue
    return fallback_card(name)


def energy_card(energy_type: str) -> Card:
    return Card(
        catalog_id=f"energy-{energy_type.lower()}",
        name=f"{energy_type} Energy",
        category="Energy",
        stage="Basic",
        types=[energy_type],
        energy_type=energy_type,
        image=None,
        retreat=0,
    )


def fallback_card(name: str) -> Card:
    lower = name.lower()
    if lower in TRAINER_KIND_HINTS:
        kind = TRAINER_KIND_HINTS[lower]
        return Card(
            catalog_id=f"fallback-{lower.replace(' ', '-')}",
            name=name,
            category="Trainer",
            stage=kind.title(),
            trainer_kind=kind,
            text=f"Family-rules approximation of {name}.",
        )
    if "energy" in lower:
        etype = ENERGY_NAME_TO_TYPE.get(lower, "Colorless")
        return energy_card(etype)
    return Card(
        catalog_id=f"fallback-{lower.replace(' ', '-')}",
        name=name,
        category="Pokemon",
        stage="Basic",
        types=["Colorless"],
        hp=70,
        attacks=[parse_attack({"name": "Tackle", "cost": ["Colorless"], "damage": 20})],
        retreat=1,
    )


def resolve_many(names: list[str], prefer_map: dict[str, list[str]] | None = None) -> list[Card]:
    prefer_map = prefer_map or {}
    return [resolve_name(n, prefer_map.get(n)) for n in names]


@lru_cache(maxsize=1)
def popular_names() -> list[str]:
    path = CACHE_DIR / "popular_names.json"
    if path.exists():
        return json.loads(path.read_text())
    return []


def search_local(query: str, limit: int = 12) -> list[dict[str, str]]:
    q = query.strip()
    if len(q) < 2:
        return []
    try:
        briefs = search_briefs(q)[:limit]
        return [
            {
                "id": b.get("id") or "",
                "name": b.get("name") or q,
                "image": _image_url(b) or "",
            }
            for b in briefs
        ]
    except Exception:
        return [{"id": "", "name": q, "image": ""}]
