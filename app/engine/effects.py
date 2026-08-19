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


def parse_ability_effects(text: str) -> list[dict[str, Any]]:
    """Parse Pokémon ability text. The printed sentence is the only source of truth.

    Lab notes, strategy names, and hardcoded look-N values must not invent an effect
    that is not in this text. Attacks already go through parse_effects; abilities
    must go through this function before the engine attaches, searches, or looks.
    """
    t = (text or "").lower().replace("pokémon", "pokemon").replace("poké", "poke")
    effects: list[dict[str, Any]] = []
    if not t:
        return effects

    energy = re.search(
        r"(grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|colorless) energy",
        t,
    )
    energy_type = (energy.group(1) if energy else "psychic").title()
    benched = re.search(r"benched (\w+)", t)
    benched_name = benched.group(1) if benched else ""
    top = re.search(r"look at the top (\d+)", t)
    each = re.search(r"for each of your benched (\w+)", t)
    search_attach = "search your deck" in t and "attach" in t and "energy" in t

    # LOR 62 Moon-Watching Party: full-deck search, one energy per benched copy.
    if each and search_attach:
        effects.append(
            {
                "kind": "attach_energy_from_deck_per_benched",
                "benched_name": each.group(1),
                "energy_type": energy_type,
                "require_active": "active" in t,
            }
        )
        return effects

    # Only if the printed text actually says to look at the top N.
    if top and "attach" in t and "energy" in t:
        effects.append(
            {
                "kind": "attach_energy_from_top",
                "look": int(top.group(1)),
                "energy_type": energy_type,
                "benched_name": benched_name,
                "any_number": "any number" in t,
            }
        )
    return effects


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

    # Litwick Kindling Panic / opponent deck mill
    if "discard the top" in t and "opponent" in t and "deck" in t:
        top = re.search(r"top (\d+)", t)
        effects.append({"kind": "mill_opponent", "count": int(top.group(1)) if top else 1})

    if "this attack does nothing" in t:
        effects.append({"kind": "coin_whiff"})

    # Mewtwo Transfer Charge: attach Basic Psychic Energy from discard.
    if "discard pile" in t and "attach" in t and "energy" in t and "up to" in t:
        up = re.search(r"up to (\d+)", t)
        effects.append({"kind": "transfer_charge", "count": int(up.group(1)) if up else 2})

    if "isn't affected by weakness" in t or "not affected by weakness" in t:
        effects.append({"kind": "ignore_wr"})

    # Plusle Plus Damage: 10 more for each damage counter on the opponent's Active.
    counter_bonus = re.search(r"(\d+) more damage for each damage counter", t)
    psychic_ref = "psychic energy" in t or "{p} energy" in t or "{p}" in t
    if counter_bonus and "opponent" in t:
        effects.append({"kind": "damage_counter_bonus", "per": int(counter_bonus.group(1))})
    elif psychic_ref and "more damage" in t and "for each" in t:
        n = re.search(r"(\d+) more damage for each", t)
        effects.append({"kind": "psychic_energy_bonus", "per": int(n.group(1)) if n else 30})
    elif "×" in damage_raw or "x" in damage_raw.lower() or "for each" in t:
        # Clefairy Wonder Storm style: scale by Psychic Energy in play.
        if psychic_ref and "attached" in t and "discarded" not in t:
            effects.append({"kind": "psychic_energy_times", "per": parse_damage(damage_raw) or 20})
        elif "discarded" not in t:
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


def is_double_colorless(card: Any) -> bool:
    return "double colorless" in (getattr(card, "name", "") or "").lower()


def energy_provided(card: Any) -> list[str]:
    """Energy units one attached card pays. DCE pays two Colorless."""
    if is_double_colorless(card):
        return ["Colorless", "Colorless"]
    et = getattr(card, "as_energy_type", None)
    if callable(et):
        et = card.as_energy_type
    if not et and getattr(card, "is_energy", False):
        et = getattr(card, "energy_type", None) or (card.types[0] if getattr(card, "types", None) else None)
    return [et] if et else []


def is_basic_energy(card: Any, pokemon_as_energy: bool = False) -> bool:
    if is_double_colorless(card):
        return False
    if getattr(card, "is_energy", False):
        return True
    if pokemon_as_energy and getattr(card, "is_pokemon", False) and getattr(card, "as_energy_type", None):
        return True
    return False


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
