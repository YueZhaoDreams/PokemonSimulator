"""Physical dual-type cards for Card search.

The search category is 双属性. It lists every physical printing whose type
line has two types: Basic, Stage 1, Stage 2, MEGA, and both halves of each
LEGEND pair. Attack sort uses the printed damage number (30× and 150+ sort
as 30 and 150). The printed damage string stays on the search hit.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.catalog import normalize_card

CATEGORY = "双属性"
_DATA = Path(__file__).resolve().parents[1] / "data" / "catalog" / "dual_type_cards.json"
_NUMBER = re.compile(r"\d+")
_ENERGIES = (
    "Colorless",
    "Darkness",
    "Lightning",
    "Fighting",
    "Psychic",
    "Grass",
    "Water",
    "Fire",
    "Metal",
    "Fairy",
    "Dragon",
)
_STAGE_QUERIES = {
    "basic": frozenset({"Basic"}),
    "基础": frozenset({"Basic"}),
    "evolution": frozenset({"Stage 1", "Stage 2", "MEGA"}),
    "进化": frozenset({"Stage 1", "Stage 2", "MEGA"}),
    "stage 1": frozenset({"Stage 1"}),
    "stage1": frozenset({"Stage 1"}),
    "一阶": frozenset({"Stage 1"}),
    "stage 2": frozenset({"Stage 2"}),
    "stage2": frozenset({"Stage 2"}),
    "二阶": frozenset({"Stage 2"}),
    "legend": frozenset({"LEGEND"}),
    "传说": frozenset({"LEGEND"}),
    "mega": frozenset({"MEGA"}),
    "超级": frozenset({"MEGA"}),
}
_CATEGORY_ALIASES = frozenset({"dual", "dual type", "dual-type", "dualtype", "双属性"})


def is_dual_category(value: str) -> bool:
    return (value or "").strip().casefold() in _CATEGORY_ALIASES


@lru_cache(maxsize=1)
def load_dual_type_cards() -> tuple[dict, ...]:
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    return tuple(raw)


def attack_value(damage: str) -> int:
    match = _NUMBER.search(str(damage or ""))
    return int(match.group()) if match else 0


def leading_attack(card: dict) -> tuple[int, str, str]:
    """Highest printed attack number, plus that attack's printed damage and name."""
    best_n = -1
    best_damage = ""
    best_name = ""
    for attack in card.get("attacks") or []:
        damage = str(attack.get("damage") or "")
        number = attack_value(damage)
        if number > best_n:
            best_n = number
            best_damage = damage
            best_name = attack.get("name") or ""
    if best_n < 0:
        return 0, "", ""
    return best_n, best_damage, best_name


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").casefold()


def _split_energy(text: str) -> list[str]:
    rest = text or ""
    found: list[str] = []
    while rest:
        rest = rest.lstrip()
        if not rest:
            break
        for name in _ENERGIES:
            if rest.startswith(name):
                found.append(name)
                rest = rest[len(name) :]
                break
        else:
            break
    return found


def _retreat_count(text: str) -> int:
    raw = (text or "").strip()
    if raw.isdigit():
        return int(raw)
    return len(_split_energy(raw))


def _typed_mods(text: str, mark: str) -> list[dict[str, str]]:
    mods: list[dict[str, str]] = []
    for part in (text or "").split(","):
        part = " ".join(part.split())
        if not part:
            continue
        if mark in part:
            typ, val = part.split(mark, 1)
            mods.append({"type": typ.strip(), "value": f"{mark}{val.strip()}"})
        else:
            mods.append({"type": part, "value": ""})
    return mods


def _matches(card: dict, folded: str) -> bool:
    bits = [
        card.get("name") or "",
        card.get("id") or "",
        card.get("set") or "",
        card.get("number") or "",
        card.get("stage") or "",
        " ".join(card.get("types") or []),
    ]
    for attack in card.get("attacks") or []:
        bits.append(attack.get("name") or "")
        bits.append(attack.get("damage") or "")
        bits.append(attack.get("text") or "")
    return folded in _fold(" ".join(bits))


def _hit(card: dict) -> dict:
    number = str(card.get("number") or "")
    local_id = number.split("/")[0] if number else str(card.get("id") or "").split("-", 1)[-1]
    value, damage, attack_name = leading_attack(card)
    return {
        "id": card.get("id") or "",
        "name": card.get("name") or "",
        "image": card.get("image") or "",
        "local_id": local_id,
        "code": number,
        "hp": str(card.get("hp") or ""),
        "types": list(card.get("types") or []),
        "stage": card.get("stage") or "",
        "search_category": CATEGORY,
        "attack": damage,
        "attack_name": attack_name,
        "attack_value": value,
        "set_name": card.get("set") or "",
    }


def search_dual_type(query: str = "", sort: str = "attack") -> list[dict]:
    text = (query or "").strip()
    if is_dual_category(text):
        text = ""
    folded = _fold(text)
    stage_filter = _STAGE_QUERIES.get(folded)
    rows = []
    for card in load_dual_type_cards():
        if stage_filter and card.get("stage") not in stage_filter:
            continue
        if text and not stage_filter and not _matches(card, folded):
            continue
        rows.append(_hit(card))
    if (sort or "").strip().casefold() == "name":
        rows.sort(key=lambda hit: (_fold(hit["name"]), hit["id"]))
    else:
        rows.sort(key=lambda hit: (-int(hit["attack_value"]), _fold(hit["name"]), hit["id"]))
    return rows


def _normalize_raw(card: dict) -> dict:
    attacks = []
    for attack in card.get("attacks") or []:
        attacks.append(
            {
                "name": attack.get("name") or "Attack",
                "cost": _split_energy(attack.get("cost") or ""),
                "damage": attack.get("damage") or "",
                "effect": attack.get("text") or "",
                "printed_damage": attack.get("damage") or "",
            }
        )
    abilities = [
        {"name": ability.get("name") or "Ability", "effect": ability.get("text") or ""}
        for ability in card.get("abilities") or []
    ]
    return {
        "id": card.get("id") or "",
        "name": card.get("name") or "",
        "category": "Pokemon",
        "stage": card.get("stage") or "",
        "types": list(card.get("types") or []),
        "hp": card.get("hp") or 0,
        "attacks": attacks,
        "abilities": abilities,
        "weaknesses": _typed_mods(card.get("weak") or "", "×"),
        "resistances": _typed_mods(card.get("resist") or "", "-"),
        "retreat": _retreat_count(card.get("retreat") or ""),
        "evolveFrom": card.get("evolves") or None,
        "image": card.get("image") or "",
        "set": {"name": card.get("set") or ""},
        "effect": card.get("rules") or "",
        "dexId": card.get("dex") or [],
    }


def dual_type_record(catalog_id: str) -> dict | None:
    cid = (catalog_id or "").strip()
    if not cid:
        return None
    for card in load_dual_type_cards():
        if card.get("id") != cid:
            continue
        printed = [attack.get("damage") or "" for attack in card.get("attacks") or []]
        data = normalize_card(_normalize_raw(card)).to_dict()
        for attack, damage in zip(data.get("attacks") or [], printed):
            attack["printed_damage"] = damage
        data["search_category"] = CATEGORY
        return data
    return None
