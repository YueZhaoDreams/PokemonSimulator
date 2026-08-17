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
    coin = "flip a coin" in t or ("flip" in t and "heads" in t)

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

    if "draw" in t and "search your deck" not in t:
        n = re.search(r"draw (\d+)", t)
        effects.append({"kind": "draw", "amount": int(n.group(1)) if n else 1})

    # Call for Family / bench a Basic from deck
    if (
        "call for family" in t
        or ("basic" in t and "bench" in t and "search your deck" in t)
        or "search your deck for a basic" in t
        or "search your deck for up to" in t and "basic" in t and "bench" in t
    ):
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "call_family", "count": int(up_to.group(1)) if up_to else 1})

    # Carbink Lucky Find / item search attacks
    if "search your deck" in t and "item" in t:
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "search_item", "count": int(up_to.group(1)) if up_to else 1})

    if "this attack does nothing" in t:
        effects.append({"kind": "coin_whiff"})

    if "×" in damage_raw or "x" in damage_raw.lower() or "for each" in t:
        # Clefairy Wonder Storm style: scale by Psychic Energy in play.
        if "psychic energy" in t and "attached" in t:
            effects.append({"kind": "psychic_energy_times", "per": parse_damage(damage_raw) or 20})
        else:
            effects.append({"kind": "times", "note": damage_raw or text})

    # Dondozo (Paradox Rift): Supplemental Swallow-Up
    if "attach any number of basic energy" in t and "top" in t:
        top = re.search(r"top (\d+)", t)
        effects.append({"kind": "swallow_energy", "look": int(top.group(1)) if top else 5})

    # Orthworm Crunch-Time Rush style: more damage when deck is thin
    more = re.search(r"(\d+) or fewer cards in your deck.*?(\d+) more damage", t)
    if more:
        effects.append(
            {
                "kind": "deck_count_bonus",
                "max_deck": int(more.group(1)),
                "bonus": int(more.group(2)),
            }
        )

    # Flutter Mane Hex Hurl: damage counters on benched Pokémon
    bench = re.search(r"put (\d+) damage counters? on your opponent'?s? benched", t)
    if bench:
        effects.append({"kind": "bench_damage_counters", "counters": int(bench.group(1))})

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
