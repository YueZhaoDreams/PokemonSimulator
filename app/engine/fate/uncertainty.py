"""Spread and brick rates from a finished Monte Carlo run.

Every number in the returned block belongs to that run's id. A comparison
prefers the higher mean when the means are outside the preset tolerance, and
the lower variance / broken-chain list when they are inside it.
"""

from __future__ import annotations

import json
import random
from collections import Counter
from dataclasses import replace
from pathlib import Path
from typing import Any

from app.engine.fate.kg import build_catalog_kg, induce
from app.engine.fate.metrics import compute_metrics
from app.engine.models import Card, FamilyRules, infer_rule_preset_from_rules
from app.engine.strategies import STRATEGY_LIBRARY

OUTPUTS = (
    "prizes_taken",
    "mulligans",
    "energy_by_turn_3",
    "first_lead_attack_turn",
    "win_rate",
)

GAMES_CAP = 25000

_DATA = Path(__file__).resolve().parents[3] / "data" / "fate" / "uncertainty"


def load_uncertainty_preset(preset: str) -> dict[str, Any]:
    path = _DATA / f"{preset}.json"
    if not path.is_file():
        raise ValueError(f"unknown uncertainty preset: {preset}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"uncertainty preset {preset} is not an object")
    return _validate_preset(data)


def apply_tolerance(base: dict[str, Any], overlay: dict[str, Any] | None) -> dict[str, Any]:
    """Override tolerance numbers only. An unknown output name is an error."""
    if not overlay:
        return json.loads(json.dumps(base))
    if not isinstance(overlay, dict):
        raise ValueError("tolerance must be an object")
    merged = json.loads(json.dumps(base))
    incoming = overlay.get("tolerance", overlay)
    if not isinstance(incoming, dict):
        raise ValueError("tolerance must be an object")
    for key, value in incoming.items():
        if key not in OUTPUTS:
            raise ValueError(f"unknown output: {key}")
        merged["tolerance"][key] = _number(value, key)
    return _validate_preset(merged)


def uncertainty(result: dict[str, Any]) -> dict[str, Any]:
    """The spread block from a simulation record. Refuses a number with no id.

    ``mean`` and ``variance`` are the prizes-taken distribution. The other
    outputs stay under ``outputs``.
    """
    block = result.get("uncertainty") if isinstance(result, dict) else None
    if not isinstance(block, dict) or not block.get("sim_id"):
        raise ValueError("uncertainty requires a simulation id")
    prizes = (block.get("outputs") or {}).get("prizes_taken") or {}
    view = dict(block)
    view["mean"] = prizes.get("mean")
    view["variance"] = prizes.get("variance")
    return view


def summarize_games(
    results: list[Any],
    cards: list[Card],
    rules: FamilyRules,
    sim_id: str,
) -> dict[str, Any]:
    """Aggregate one side of a finished run. Side A is the list being measured."""
    if not sim_id:
        raise ValueError("uncertainty requires a simulation id")
    preset = load_uncertainty_preset(_preset_name(rules))
    brick_turn = int(preset["brick_turn"])
    energy_turn = int(preset["energy_turn"])
    lead = _lead_attack(cards)
    lines = _lines(cards, rules)
    prizes: list[float] = []
    mulligans: list[float] = []
    energy: list[float] = []
    lead_turns: list[float] = []
    wins: list[float] = []
    bricks = 0
    breaks = 0
    for result in results:
        side = (getattr(result, "fate", None) or {}).get("a") or {}
        prizes.append(float(side.get("prizes_taken") or 0))
        mulligans.append(float(side.get("mulligans") or 0))
        wins.append(1.0 if getattr(result, "winner", None) == "a" else 0.0)
        attacks = side.get("first_attack_turn") or {}
        first_any = min(attacks.values()) if attacks else None
        if first_any is None or int(first_any) > brick_turn:
            bricks += 1
        observed = (side.get("energy_in_play_by_turn") or {}).get(str(energy_turn))
        if observed is not None:
            energy.append(float(observed))
        if lead is not None:
            turn = attacks.get(f"{lead['pokemon']}|{lead['attack']}")
            if turn is not None:
                lead_turns.append(float(turn))
        if _chain_broken(
            lines,
            side.get("hand") or [],
            side.get("in_play") or [],
            side.get("ever_in_play"),
        ):
            breaks += 1
    games = len(results)
    outputs = {
        "prizes_taken": _stats(prizes),
        "mulligans": _stats(mulligans),
        "energy_by_turn_3": _stats(energy),
        "first_lead_attack_turn": _stats(lead_turns),
        "win_rate": _stats(wins),
    }
    return {
        "sim_id": sim_id,
        "mean": outputs["prizes_taken"]["mean"],
        "variance": outputs["prizes_taken"]["variance"],
        "games": games,
        "brick_turn": brick_turn,
        "energy_turn": energy_turn,
        "lead_attack": lead,
        "brick_rate": (bricks / games) if games else None,
        "chain_break_rate": (breaks / games) if games else None,
        "outputs": outputs,
    }


def compare_lists(
    cards_a: list[Card],
    cards_b: list[Card],
    rules: FamilyRules,
    games: int,
    seed: int | None,
    output: str,
    tolerance: dict[str, Any] | None,
) -> dict[str, Any]:
    """Two capped runs, then the tolerance rule. Each list is measured as side A."""
    if output not in OUTPUTS:
        raise ValueError(f"unknown output: {output}")
    preset_name = _preset_name(rules)
    merged = apply_tolerance(load_uncertainty_preset(preset_name), tolerance)
    tol = float(merged["tolerance"][output])
    played = max(1, min(int(games), GAMES_CAP))
    shared_seed = int(seed if seed is not None else random.randrange(1, 10**9))
    from app.engine.montecarlo import run_simulation

    base = STRATEGY_LIBRARY["balanced"]
    run_a = run_simulation(
        cards_a,
        cards_b,
        rules,
        replace(base),
        replace(base),
        games=played,
        seed=shared_seed,
        question="fate compare",
        queries=[],
    )
    run_b = run_simulation(
        cards_b,
        cards_a,
        rules,
        replace(base),
        replace(base),
        games=played,
        seed=shared_seed,
        question="fate compare",
        queries=[],
    )
    block_a = uncertainty(run_a)
    block_b = uncertainty(run_b)
    higher = bool(merged["higher_is_better"][output])
    preferred, reason = _prefer(block_a, block_b, output, tol, higher)
    return {
        "output": output,
        "higher_is_better": higher,
        "tolerance": merged["tolerance"],
        "tolerance_used": tol,
        "games": played,
        "seed": shared_seed,
        "preferred": preferred,
        "reason": reason,
        "a": _public(block_a, output),
        "b": _public(block_b, output),
        "runs": {"a": run_a, "b": run_b},
    }


def _prefer(
    block_a: dict[str, Any],
    block_b: dict[str, Any],
    output: str,
    tol: float,
    higher_is_better: bool,
) -> tuple[str, str]:
    stat_a = block_a["outputs"][output]
    stat_b = block_b["outputs"][output]
    mean_a = stat_a["mean"]
    mean_b = stat_b["mean"]
    if mean_a is None or mean_b is None:
        raise ValueError(f"{output} has no observations in one of the runs")
    var_a = stat_a["variance"]
    var_b = stat_b["variance"]
    brick_a = float(block_a["brick_rate"])
    brick_b = float(block_b["brick_rate"])
    chain_a = float(block_a["chain_break_rate"])
    chain_b = float(block_b["chain_break_rate"])
    base = (
        f"{output} means {mean_a:.3f} and {mean_b:.3f}. "
        f"Tolerance {tol:g}. "
        f"Variance {var_a:.3f} and {var_b:.3f}. "
        f"Broken chain {chain_a:.3f} and {chain_b:.3f}. "
        f"Brick {brick_a:.3f} and {brick_b:.3f}. "
        f"Simulation {block_a['sim_id']} and {block_b['sim_id']}."
    )
    if abs(float(mean_a) - float(mean_b)) < tol:
        score_a = (float(var_a or 0), brick_a, chain_a)
        score_b = (float(var_b or 0), brick_b, chain_b)
        if score_a < score_b:
            return "a", base + (
                " Means are within tolerance, so list A is preferred: "
                "lower variance, then lower brick rate, then lower broken chain rate."
            )
        if score_b < score_a:
            return "b", base + (
                " Means are within tolerance, so list B is preferred: "
                "lower variance, then lower brick rate, then lower broken chain rate."
            )
        return "tie", base + " Means are within tolerance, and the variance, brick rate, and broken chain rate match."
    if higher_is_better:
        winner = "a" if float(mean_a) > float(mean_b) else "b"
        direction = "higher"
    else:
        winner = "a" if float(mean_a) < float(mean_b) else "b"
        direction = "lower"
    return winner, base + f" Means are outside tolerance, so the {direction} mean is preferred."


def _public(block: dict[str, Any], output: str) -> dict[str, Any]:
    stat = block["outputs"][output]
    return {
        "sim_id": block["sim_id"],
        "mean": stat["mean"],
        "variance": stat["variance"],
        "n": stat["n"],
        "brick_rate": block["brick_rate"],
        "chain_break_rate": block["chain_break_rate"],
        "lead_attack": block["lead_attack"],
    }


def _stats(values: list[float]) -> dict[str, Any]:
    n = len(values)
    if n == 0:
        return {"mean": None, "variance": None, "n": 0}
    mean = sum(values) / n
    if n == 1:
        variance = 0.0
    else:
        variance = sum((value - mean) ** 2 for value in values) / (n - 1)
    return {"mean": mean, "variance": variance, "n": n}


def _lead_attack(cards: list[Card]) -> dict[str, str] | None:
    best: tuple[tuple[int, int], str, str] | None = None
    for card in cards:
        if (card.category or "").lower() != "pokemon":
            continue
        for attack in card.attacks:
            damage = int(attack.damage or 0)
            rank = (damage, -len(attack.cost or []))
            if best is None or rank > best[0]:
                best = (rank, card.name, attack.name)
    if best is None or best[0][0] <= 0:
        return None
    return {"pokemon": best[1], "attack": best[2]}


def _lines(cards: list[Card], rules: FamilyRules) -> list[dict[str, Any]]:
    graph = induce(build_catalog_kg(cards, rules), Counter(card.name for card in cards))
    return list(compute_metrics(graph, rules, cards)["lines"])


def _chain_broken(
    lines: list[dict[str, Any]],
    hand: list[str],
    in_play: list[str],
    ever_in_play: list[str] | None = None,
) -> bool:
    """An evolution in hand whose line never reached the board.

    The final board can miss a line that already evolved and then left play.
    ``ever_in_play`` is every name that was in play at the end of a turn.
    A spare copy in hand after that is not a broken chain. A body that was
    knocked out before the evolution ever entered play still counts.
    """
    hand_names = {name.lower() for name in hand}
    play_names = {name.lower() for name in in_play}
    reached = {name.lower() for name in (ever_in_play if ever_in_play is not None else in_play)}
    reached |= play_names
    later: dict[str, set[str]] = {}
    pairs: list[tuple[str, str]] = []
    for line in lines:
        evolution = str(line.get("evolution") or "").lower()
        basic = str(line.get("basic") or "").lower()
        if not evolution or not basic:
            continue
        pairs.append((basic, evolution))
        later.setdefault(basic, set()).add(evolution)
    for basic, evolution in pairs:
        if evolution not in hand_names:
            continue
        if basic in play_names or evolution in play_names:
            continue
        if evolution in reached or _later_stage_in_play(evolution, later, reached):
            continue
        return True
    return False


def _later_stage_in_play(name: str, later: dict[str, set[str]], play_names: set[str], seen: set[str] | None = None) -> bool:
    seen = set() if seen is None else seen
    if name in seen:
        return False
    seen.add(name)
    for child in later.get(name, ()):
        if child in play_names or _later_stage_in_play(child, later, play_names, seen):
            return True
    return False


def _preset_name(rules: FamilyRules) -> str:
    name = infer_rule_preset_from_rules(rules)
    if name in {"s30", "s60"}:
        return name
    return "s60" if int(rules.deck_size) >= 60 else "s30"


def _number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    return float(value)


def _validate_preset(data: dict[str, Any]) -> dict[str, Any]:
    if "brick_turn" not in data or "energy_turn" not in data:
        raise ValueError("uncertainty preset is missing a turn")
    tolerance = data.get("tolerance")
    if not isinstance(tolerance, dict):
        raise ValueError("tolerance must be an object")
    missing = set(OUTPUTS) - set(tolerance)
    if missing:
        raise ValueError(f"missing tolerance: {sorted(missing)[0]}")
    unknown = set(tolerance) - set(OUTPUTS)
    if unknown:
        raise ValueError(f"unknown output: {sorted(unknown)[0]}")
    direction = data.get("higher_is_better")
    if not isinstance(direction, dict):
        raise ValueError("higher_is_better must be an object")
    for key in OUTPUTS:
        if not isinstance(direction.get(key), bool):
            raise ValueError(f"higher_is_better.{key} must be true or false")
    return data
