"""Fast ecology score and 1-for-1 swap ranking.

S is a weighted sum of print-derived metrics. A swap row is the change in S
after removing one copy and adding one card. It is a fast estimate that prunes
Monte Carlo candidates. It is not a win rate, and the match kernel never reads it.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from app.engine.fate.kg import build_catalog_kg, induce
from app.engine.fate.metrics import compute_metrics
from app.engine.legality import copy_violations
from app.engine.models import Card, FamilyRules, infer_rule_preset_from_rules

ECOLOGIES = (
    "early_equal_hands",
    "main_line",
    "secondary_closers",
    "energy_budget",
    "control",
    "prize_race",
    "consistency",
)

_WEIGHT_NUMBERS = (
    "conditional_kept_live",
    "stranded_penalty",
    "body_slack",
    "widow_penalty",
    "prize_leak",
)
_BOSS_NUMBERS = ("supporter", "hp_gate", "supporter_free")
_CURVE_NAMES = ("fate", "line_2", "engine_4", "party", "charges")

_WEIGHTS_DIR = Path(__file__).resolve().parents[3] / "data" / "fate" / "weights"


def load_preset(preset: str) -> dict[str, Any]:
    """Shipped defaults for s30 or s60. Unknown ecology keys are rejected."""
    path = _WEIGHTS_DIR / f"{preset}.json"
    if not path.is_file():
        raise ValueError(f"unknown weight preset: {preset}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"weight preset {preset} is not an object")
    return _validate_weights(data)


def apply_overlay(base: dict[str, Any], overlay: dict[str, Any] | None) -> dict[str, Any]:
    """Override numbers only. An unknown ecology key is an error."""
    if not overlay:
        return json.loads(json.dumps(base))
    if not isinstance(overlay, dict):
        raise ValueError("weights must be an object")
    merged = json.loads(json.dumps(base))
    for key, value in overlay.items():
        if key in ECOLOGIES:
            merged["ecologies"][key] = _number(value, key)
        elif key == "ecologies":
            if not isinstance(value, dict):
                raise ValueError("ecologies must be an object")
            for eco, eco_value in value.items():
                if eco not in ECOLOGIES:
                    raise ValueError(f"unknown ecology: {eco}")
                merged["ecologies"][eco] = _number(eco_value, eco)
        elif key in _WEIGHT_NUMBERS:
            merged[key] = _number(value, key)
        elif key == "preset":
            # The response echoes this label. It is not a weight, so sending the
            # echoed object back must not fail.
            continue
        elif key == "boss_equivalent":
            _merge_boss(merged, value)
        elif key == "copy_curves":
            _merge_curves(merged, value)
        else:
            raise ValueError(f"unknown weight: {key}")
    return _validate_weights(merged)


def score(metrics: dict[str, Any], weights: dict[str, Any]) -> dict[str, Any]:
    """S = sum of ecology weight times that ecology's print-derived value."""
    weights = _validate_weights(weights)
    ecologies = {
        "early_equal_hands": _early(metrics, weights),
        "main_line": _main_line(metrics, weights),
        "secondary_closers": _secondary(metrics, weights),
        "energy_budget": _energy_budget(metrics),
        "control": _control(metrics),
        "prize_race": _prize_race(metrics, weights),
        "consistency": _consistency(metrics, weights),
    }
    total = sum(float(weights["ecologies"][name]) * value for name, value in ecologies.items())
    return {"total": total, "ecologies": ecologies}


def boss_equivalent(
    deck_kg,
    metrics: dict[str, Any],
    cards: list[Card],
    weights: dict[str, Any],
) -> dict[str, Any]:
    """Boss-equivalent from parsed force-opponent-active hooks.

    A supporter is ``supporter`` per copy. An on-evolve ability is
    ``hp_gate × supporter_free × charge_curve(min(evolution, body))``.
    All three factors and the curve come from the weights data.
    """
    factors = weights["boss_equivalent"]
    by_id = {node.id: node for node in deck_kg.nodes}
    counts = Counter(card.name for card in cards)
    supporters: list[dict[str, Any]] = []
    evolve: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for edge in deck_kg.edges:
        if edge.kind != "force_opponent_active":
            continue
        src = by_id.get(edge.src)
        if src is None or src.kind != "printing":
            continue
        trigger = str((edge.effect or {}).get("trigger") or "")
        key = (src.name, trigger)
        if key in seen:
            continue
        seen.add(key)
        copies = int(counts[src.name])
        if copies <= 0:
            continue
        if trigger == "play" and str(src.attributes.get("trainer_kind") or "").lower() == "supporter":
            per_copy = float(factors["supporter"])
            supporters.append(
                {
                    "name": src.name,
                    "copies": copies,
                    "per_copy": per_copy,
                    "total": per_copy * copies,
                }
            )
        elif trigger == "on_evolve":
            line = next((row for row in metrics["lines"] if row["evolution"] == src.name), None)
            charges = int(line["charges"]) if line else 0
            value = (
                float(factors["hp_gate"])
                * float(factors["supporter_free"])
                * _curve(factors["charge_curve"], charges)
            )
            evolve.append({"name": src.name, "charges": charges, "value": value})
    supporters.sort(key=lambda row: row["name"])
    evolve.sort(key=lambda row: row["name"])
    total = sum(row["total"] for row in supporters) + sum(row["value"] for row in evolve)
    return {"supporters": supporters, "evolve": evolve, "total": total}


def rank_swaps(
    deck: list[Card],
    add: str,
    weights: dict[str, Any] | None,
    rules: FamilyRules,
) -> dict[str, Any]:
    """One row per distinct legal cut. Higher delta_s is the better card to remove."""
    cards = list(deck)
    preset = _preset_name(rules)
    merged = apply_overlay(load_preset(preset), weights)
    added = _resolve_add(cards, add)
    before = _bundle(cards, rules, merged)
    before_score = score(before, merged)
    rows: list[dict[str, Any]] = []
    full_deck = len(cards) == int(rules.deck_size)
    for name in sorted({card.name for card in cards}):
        swapped = _swap(cards, name, added)
        if full_deck and len(swapped) != int(rules.deck_size):
            continue
        if copy_violations(swapped, rules):
            continue
        after = _bundle(swapped, rules, merged)
        after_score = score(after, merged)
        deltas = {
            eco: after_score["ecologies"][eco] - before_score["ecologies"][eco]
            for eco in ECOLOGIES
        }
        copies = sum(1 for card in cards if card.name == name)
        rows.append(
            {
                "cut": name,
                "copies": copies,
                "delta_s": after_score["total"] - before_score["total"],
                "ecologies": deltas,
                "reason": _reason(before, after, before_score, after_score, name, added.name),
            }
        )
    rows.sort(key=lambda row: (-row["delta_s"], row["cut"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
        row["delta_s"] = round(row["delta_s"], 4)
        row["ecologies"] = {eco: round(value, 4) for eco, value in row["ecologies"].items()}
    return {
        "estimate": True,
        "label": "fast estimate, not a win rate",
        "add": added.name,
        "weights": merged,
        "boss_equivalent": before["boss_equivalent"],
        "rows": rows,
    }


def _bundle(cards: list[Card], rules: FamilyRules, weights: dict[str, Any]) -> dict[str, Any]:
    graph = induce(build_catalog_kg(cards, rules), Counter(card.name for card in cards))
    metrics = compute_metrics(graph, rules, cards)
    metrics["party_charges"] = _party_charges(graph, cards)
    metrics["boss_equivalent"] = boss_equivalent(graph, metrics, cards, weights)
    return metrics


def _party_charges(graph, cards: list[Card]) -> int:
    """Copies of each Pokémon the printed per-benched attach names."""
    counts = Counter(card.name.lower() for card in cards)
    names: set[str] = set()
    for edge in graph.edges:
        if edge.kind != "attaches_from_deck":
            continue
        name = str((edge.effect or {}).get("benched_name") or "").lower()
        if name:
            names.add(name)
    return sum(int(counts[name]) for name in names)


def _swap(cards: list[Card], cut_name: str, added: Card) -> list[Card]:
    swapped: list[Card] = []
    removed = False
    for card in cards:
        if not removed and card.name == cut_name:
            removed = True
            continue
        swapped.append(card)
    swapped.append(Card.from_dict(added.to_dict()))
    return swapped


def _resolve_add(cards: list[Card], add: str) -> Card:
    key = add.strip()
    if not key:
        raise ValueError("add is required")
    for card in cards:
        if card.name == key or (card.catalog_id and card.catalog_id == key):
            return Card.from_dict(card.to_dict())
    from app.catalog import lookup_seed_card

    found = lookup_seed_card(name=key, catalog_id=key)
    if found:
        return found
    raise ValueError(f"unknown card: {key}")


def _preset_name(rules: FamilyRules) -> str:
    name = infer_rule_preset_from_rules(rules)
    if name in {"s30", "s60"}:
        return name
    return "s60" if int(rules.deck_size) >= 60 else "s30"


def _reason(
    before: dict[str, Any],
    after: dict[str, Any],
    before_score: dict[str, Any],
    after_score: dict[str, Any],
    cut_name: str,
    added_name: str,
) -> str:
    deltas = {
        eco: after_score["ecologies"][eco] - before_score["ecologies"][eco]
        for eco in ECOLOGIES
    }
    movers = sorted((eco for eco in deltas if abs(deltas[eco]) > 1e-9), key=lambda eco: abs(deltas[eco]), reverse=True)
    parts: list[str] = []
    if movers:
        parts.append(", ".join(f"{eco} {deltas[eco]:+.2f}" for eco in movers[:2]))
    interesting = {cut_name, added_name}
    before_lines = {(row["basic"], row["evolution"]): row for row in before["lines"]}
    after_lines = {(row["basic"], row["evolution"]): row for row in after["lines"]}
    for key in sorted(set(before_lines) | set(after_lines)):
        prev = before_lines.get(key)
        nxt = after_lines.get(key)
        left = prev or {"basic": key[0], "evolution": key[1], "bodies": 0, "evolutions": 0}
        right = nxt or {"basic": key[0], "evolution": key[1], "bodies": 0, "evolutions": 0}
        if left["bodies"] == right["bodies"] and left["evolutions"] == right["evolutions"]:
            continue
        if left["evolution"] not in interesting and left["basic"] not in interesting:
            continue
        parts.append(
            f"{right['evolution']} body dependence: bodies {right['bodies']} vs evolutions {right['evolutions']}"
        )
    party_before = int(before.get("party_charges") or 0)
    party_after = int(after.get("party_charges") or 0)
    if party_before != party_after:
        parts.append(f"Party charges {party_before}→{party_after}")
    supply_before = before["energy_budget"]["supply"]
    supply_after = after["energy_budget"]["supply"]
    for energy in sorted(set(supply_before) | set(supply_after)):
        if supply_before.get(energy, 0) != supply_after.get(energy, 0):
            parts.append(f"energy {energy} {supply_before.get(energy, 0)}→{supply_after.get(energy, 0)}")
            break
    before_copies = {row["name"]: int(row["copies"]) for row in before["nodes"]}
    after_copies = {row["name"]: int(row["copies"]) for row in after["nodes"]}
    for row in before["nodes"]:
        prize = int(row.get("prize_weight") or 1)
        if prize < 2:
            continue
        if after_copies.get(row["name"], 0) < before_copies.get(row["name"], 0):
            parts.append(f"closer loss {row['name']}")
    return "; ".join(parts) if parts else "no change"


def _early(metrics: dict[str, Any], weights: dict[str, Any]) -> float:
    """2-energy Basics. A printed "does nothing" attack stays in the sum when kept live."""
    keep = float(weights["conditional_kept_live"])
    total = 0.0
    for node in metrics.get("nodes") or []:
        if str(node.get("category") or "").lower() != "pokemon":
            continue
        if int(node.get("body_ready") or 0) != 0:
            continue
        if node.get("energy_lead") != 2:
            continue
        dpe = node.get("dpe_lead")
        if not dpe:
            continue
        copies = int(node.get("copies") or 0)
        factor = keep if node.get("condition") else 1.0
        total += float(dpe) * copies * factor
    return total


def _main_line(metrics: dict[str, Any], weights: dict[str, Any]) -> float:
    curves = weights["copy_curves"]
    total = 0.0
    by_name = {row["name"]: row for row in metrics.get("nodes") or []}
    for line in metrics.get("lines") or []:
        charges = int(line["charges"])
        total += _curve(curves["charges"], charges)
        total += _curve(curves["line_2"], min(charges, 2))
        slack = int(line["bodies"]) - int(line["evolutions"])
        if slack > 0:
            total += float(weights["body_slack"]) * slack
        evolution = by_name.get(line["evolution"])
        if not evolution:
            continue
        if evolution.get("typed_payable_from_supply"):
            total += float(evolution.get("reach") or 0)
        total += len(evolution.get("searchers") or [])
    total += _curve(curves["party"], int(metrics.get("party_charges") or 0))
    return total


def _secondary(metrics: dict[str, Any], weights: dict[str, Any]) -> float:
    fate = weights["copy_curves"]["fate"]
    total = 0.0
    for node in metrics.get("nodes") or []:
        if int(node.get("prize_weight") or 1) < 2:
            continue
        copies = int(node.get("copies") or 0)
        if copies <= 0:
            continue
        dpe = node.get("dpe_max")
        if dpe is None:
            dpe = node.get("dpe_lead") or 0
        total += float(dpe) * copies * _curve(fate, 1)
    return total


def _energy_budget(metrics: dict[str, Any]) -> float:
    supply = (metrics.get("energy_budget") or {}).get("supply") or {}
    drinkers: Counter[str] = Counter()
    for node in metrics.get("nodes") or []:
        if str(node.get("category") or "").lower() != "pokemon":
            continue
        copies = int(node.get("copies") or 0)
        for energy, count in (node.get("typed_cost") or {}).items():
            drinkers[str(energy).title()] += int(count) * copies
    total = 0.0
    for energy in set(supply) | set(drinkers):
        total += max(0, int(supply.get(energy, 0)) - int(drinkers.get(energy, 0)))
    return total


def _control(metrics: dict[str, Any]) -> float:
    boss = metrics.get("boss_equivalent") or {}
    return float(boss.get("total") or 0)


def _prize_race(metrics: dict[str, Any], weights: dict[str, Any]) -> float:
    leak = float(weights["prize_leak"])
    total = 0.0
    for node in metrics.get("nodes") or []:
        if str(node.get("category") or "").lower() != "pokemon":
            continue
        copies = int(node.get("copies") or 0)
        prize = int(node.get("prize_weight") or 1)
        if prize <= 1:
            total += copies
        else:
            total -= leak * (prize - 1) * copies
    return max(0.0, total)


def _consistency(metrics: dict[str, Any], weights: dict[str, Any]) -> float:
    curves = weights["copy_curves"]
    total = 0.0
    for node in metrics.get("nodes") or []:
        total += float(node.get("reach") or 0)
        total += len(node.get("searchers") or [])
        if str(node.get("category") or "").lower() == "pokemon":
            total += _curve(curves["engine_4"], int(node.get("copies") or 0))
    stranded = sum(1 for line in metrics.get("lines") or [] if line.get("stranded"))
    widows = sum(
        1
        for line in metrics.get("lines") or []
        if int(line.get("bodies") or 0) == 1 and int(line.get("evolutions") or 0) == 1
    )
    total -= float(weights["stranded_penalty"]) * stranded
    total -= float(weights["widow_penalty"]) * widows
    return max(0.0, total)


def _curve(table: dict[str, Any], n: int) -> float:
    if str(n) in table:
        return float(table[str(n)])
    try:
        keys = sorted(int(key) for key in table)
    except (TypeError, ValueError) as exc:
        raise ValueError("curve steps must be integers") from exc
    if not keys:
        return float(n)
    if n >= keys[-1]:
        return float(table[str(keys[-1])])
    eligible = [key for key in keys if key <= n]
    if not eligible:
        return 0.0
    return float(table[str(max(eligible))])


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    return float(value)


def _merge_boss(merged: dict[str, Any], value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("boss_equivalent must be an object")
    for key, item in value.items():
        if key in _BOSS_NUMBERS:
            merged["boss_equivalent"][key] = _number(item, key)
        elif key == "charge_curve":
            merged["boss_equivalent"]["charge_curve"].update(_numeric_table(item, "charge_curve"))
        else:
            raise ValueError(f"unknown boss factor: {key}")


def _merge_curves(merged: dict[str, Any], value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("copy_curves must be an object")
    for key, item in value.items():
        if key not in _CURVE_NAMES:
            raise ValueError(f"unknown copy curve: {key}")
        merged["copy_curves"][key].update(_numeric_table(item, key))


def _numeric_table(value: Any, label: str) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    out: dict[str, float] = {}
    for key, item in value.items():
        step = _step_key(key, label)
        out[step] = _number(item, f"{label}.{key}")
    return out


def _step_key(key: Any, label: str) -> str:
    text = str(key).strip()
    if not text.lstrip("-").isdigit():
        raise ValueError(f"{label} step must be an integer, got {key}")
    return str(int(text))


def _validate_weights(data: dict[str, Any]) -> dict[str, Any]:
    ecologies = data.get("ecologies")
    if not isinstance(ecologies, dict):
        raise ValueError("ecologies must be an object")
    unknown = set(ecologies) - set(ECOLOGIES)
    if unknown:
        raise ValueError(f"unknown ecology: {sorted(unknown)[0]}")
    missing = set(ECOLOGIES) - set(ecologies)
    if missing:
        raise ValueError(f"missing ecology: {sorted(missing)[0]}")
    boss = data.get("boss_equivalent")
    if not isinstance(boss, dict):
        raise ValueError("boss_equivalent must be an object")
    for key in (*_BOSS_NUMBERS, "charge_curve"):
        if key not in boss:
            raise ValueError(f"missing boss factor: {key}")
    curves = data.get("copy_curves")
    if not isinstance(curves, dict):
        raise ValueError("copy_curves must be an object")
    for key in _CURVE_NAMES:
        if key not in curves:
            raise ValueError(f"missing copy curve: {key}")
    for key in _WEIGHT_NUMBERS:
        if key not in data:
            raise ValueError(f"missing weight: {key}")
    return data
