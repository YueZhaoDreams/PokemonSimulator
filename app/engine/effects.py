from __future__ import annotations

import re
from typing import Any

from app.engine.models import Attack


def parse_damage(raw: Any) -> int:
    if raw is None or raw == "":
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    text = str(raw)
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def parse_attack(raw: dict[str, Any]) -> Attack:
    text = raw.get("effect") or raw.get("text") or ""
    damage_raw = raw.get("damage")
    return Attack(
        name=raw.get("name") or "Attack",
        cost=[c for c in (raw.get("cost") or ["Colorless"]) if c],
        damage=parse_damage(damage_raw),
        text=text,
        effects=parse_effects(text, str(damage_raw or "")),
    )


def parse_effects(text: str, damage_raw: str = "") -> list[dict[str, Any]]:
    t = (text or "").lower()
    effects: list[dict[str, Any]] = []
    coin = "flip a coin" in t or "flip" in t

    if "paralyze" in t:
        effects.append({"kind": "status", "status": "paralyzed", "coin": coin})
    if "poison" in t:
        effects.append({"kind": "status", "status": "poisoned", "coin": coin and "poison" in t})
    if "burn" in t:
        effects.append({"kind": "status", "status": "burned", "coin": coin})
    if "asleep" in t or "put to sleep" in t:
        effects.append({"kind": "status", "status": "asleep", "coin": coin})
    if "confus" in t:
        effects.append({"kind": "status", "status": "confused", "coin": coin})

    heal = re.search(r"heal (\d+)", t)
    if heal:
        effects.append({"kind": "heal", "amount": int(heal.group(1))})

    if "draw" in t:
        n = re.search(r"draw (\d+)", t)
        effects.append({"kind": "draw", "amount": int(n.group(1)) if n else 1})

    if "call for family" in t or "search your deck for a basic" in t:
        effects.append({"kind": "call_family"})

    if "this attack does nothing" in t:
        effects.append({"kind": "coin_whiff"})

    if "×" in damage_raw or "x" in damage_raw.lower():
        effects.append({"kind": "times", "note": damage_raw})

    return effects


def can_pay_energy(attached_types: list[str], cost: list[str]) -> bool:
    pool = list(attached_types)
    for need in [c for c in cost if c != "Colorless"]:
        if need in pool:
            pool.remove(need)
        else:
            return False
    colorless = sum(1 for c in cost if c == "Colorless")
    return len(pool) >= colorless


def weakness_multiplier(defender_weaknesses: list[dict[str, str]], attack_types: list[str]) -> int:
    for weak in defender_weaknesses or []:
        if weak.get("type") in attack_types:
            value = weak.get("value") or "×2"
            if "2" in value:
                return 2
    return 1


def resistance_reduce(defender_resistances: list[dict[str, str]], attack_types: list[str]) -> int:
    for resist in defender_resistances or []:
        if resist.get("type") in attack_types:
            value = resist.get("value") or "-30"
            match = re.search(r"(\d+)", value)
            return int(match.group(1)) if match else 30
    return 0
