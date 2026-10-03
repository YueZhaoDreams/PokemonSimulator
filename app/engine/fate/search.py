"""One-step neighbors of a list, pruned by the ecology score, then confirmed.

The budget in ``data/fate/search.json`` is the limit. A larger pool is not
walked past that many legal swaps, and only the top slice is simulated.
The result is a relative improvement.
"""

from __future__ import annotations

import json
import random
from dataclasses import replace
from pathlib import Path
from typing import Any

from app.engine.fate.score import _bundle, _preset_name, _reason, _swap, apply_overlay, load_preset, score
from app.engine.fate.uncertainty import GAMES_CAP, load_uncertainty_preset, uncertainty
from app.engine.legality import copy_violations
from app.engine.models import Card, FamilyRules
from app.engine.strategies import STRATEGY_LIBRARY

_DATA = Path(__file__).resolve().parents[3] / "data" / "fate" / "search.json"
_BUDGET_KEYS = ("max_candidates", "top_k", "games_per_candidate", "depth")

LABEL = "relative improvement, not the best deck"


def load_budget() -> dict[str, int]:
    data = json.loads(_DATA.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("search budget is not an object")
    return _validate_budget(data)


def apply_budget(base: dict[str, int], overlay: dict[str, Any] | None) -> dict[str, int]:
    """Lower a documented limit. A larger request is rejected."""
    merged = dict(base)
    if not overlay:
        return _clamp(merged)
    if not isinstance(overlay, dict):
        raise ValueError("budget must be an object")
    for key, value in overlay.items():
        if key not in _BUDGET_KEYS:
            raise ValueError(f"unknown budget: {key}")
        number = _whole(value, key)
        if number > int(base[key]):
            raise ValueError(f"{key} is above the documented budget")
        if number < 1:
            raise ValueError(f"{key} must be at least 1")
        merged[key] = number
    if merged["depth"] != int(base["depth"]):
        raise ValueError("depth is 1")
    return _clamp(merged)


def resolve_pool(names: list[str] | None, seed: list[Card], owned: list[Card]) -> list[Card]:
    """Named cards, or the seed plus the trainer's own cards when names are omitted."""
    have: dict[str, Card] = {}
    for card in list(seed) + list(owned):
        have.setdefault(card.name, card)
    if names is None:
        return list(have.values())
    if not isinstance(names, list) or not names:
        raise ValueError("pool must be card names")
    from app.catalog import lookup_seed_card

    chosen: list[Card] = []
    for name in names:
        if not isinstance(name, str) or not name.strip():
            raise ValueError("pool must be card names")
        key = name.strip()
        if key in have:
            chosen.append(have[key])
            continue
        found = lookup_seed_card(name=key, catalog_id=key)
        if not found:
            raise ValueError(f"unknown card: {key}")
        chosen.append(found)
    return chosen


def search(
    seed: list[Card],
    pool: list[Card],
    rules: FamilyRules,
    weights: dict[str, Any] | None,
    budget: dict[str, Any] | None = None,
    locks: list[str] | None = None,
    opponent: list[Card] | None = None,
    seed_int: int | None = None,
) -> dict[str, Any]:
    """Score a bounded set of 1-for-1 neighbors and simulate the best slice."""
    if not seed:
        raise ValueError("seed is empty")
    if not pool:
        raise ValueError("pool is empty")
    limits = apply_budget(load_budget(), budget)
    locked = _locks(locks)
    preset_name = _preset_name(rules)
    merged = apply_overlay(load_preset(preset_name), weights)
    before = _bundle(list(seed), rules, merged)
    before_score = score(before, merged)
    neighbors = _neighbors(seed, pool, rules, locked, int(limits["max_candidates"]))
    scored: list[dict[str, Any]] = []
    for cut, added, swapped in neighbors:
        after = _bundle(swapped, rules, merged)
        after_score = score(after, merged)
        text = _speak(before, after, before_score, after_score, cut, added.name)
        scored.append(
            {
                "cut": cut,
                "add": added.name,
                "delta_s": round(after_score["total"] - before_score["total"], 4),
                "reason": text,
                "_cards": swapped,
            }
        )
    scored.sort(key=lambda row: (-row["delta_s"], row["cut"], row["add"]))
    keep = int(limits["top_k"])
    chosen = scored[:keep]
    held = scored[keep:]
    games_each = min(int(limits["games_per_candidate"]), GAMES_CAP)
    shared = int(seed_int if seed_int is not None else random.randrange(1, 10**9))
    foe = list(opponent) if opponent is not None else list(seed)
    runs: list[dict[str, Any]] = []
    if chosen:
        runs = _confirm(chosen, foe, rules, games_each, shared)
        tol = float(load_uncertainty_preset(preset_name)["tolerance"]["win_rate"])
        chosen = _by_uncertainty(chosen, tol)
    else:
        tol = float(load_uncertainty_preset(preset_name)["tolerance"]["win_rate"])
    for index, row in enumerate(chosen, start=1):
        row["rank"] = index
        row.pop("_cards", None)
    pruned = [{"cut": row["cut"], "add": row["add"], "delta_s": row["delta_s"]} for row in held]
    games_run = games_each * len(chosen)
    return {
        "label": LABEL,
        "relative": True,
        "deck_size": len(seed),
        "depth": int(limits["depth"]),
        "budget": {
            "max_candidates": int(limits["max_candidates"]),
            "top_k": keep,
            "games_per_candidate": games_each,
            "depth": int(limits["depth"]),
            "candidates_scored": len(scored),
            "games_run": games_run,
            "budget_games": int(limits["max_candidates"]) * int(limits["games_per_candidate"]),
        },
        "tolerance_used": tol,
        "seed": shared,
        "weights": merged,
        "survivors": chosen,
        "pruned": pruned,
        "runs": runs,
    }


def _neighbors(
    seed: list[Card],
    pool: list[Card],
    rules: FamilyRules,
    locked: set[str],
    limit: int,
) -> list[tuple[str, Card, list[Card]]]:
    cuts = sorted({card.name for card in seed if card.name not in locked})
    adds: dict[str, Card] = {}
    for card in pool:
        adds.setdefault(card.name, card)
    found: list[tuple[str, Card, list[Card]]] = []
    for cut in cuts:
        for name in sorted(adds):
            if name == cut:
                continue
            added = adds[name]
            swapped = _swap(seed, cut, added)
            if len(swapped) != len(seed):
                continue
            if len(seed) == int(rules.deck_size) and len(swapped) != int(rules.deck_size):
                continue
            if copy_violations(swapped, rules):
                continue
            found.append((cut, added, swapped))
            if len(found) >= limit:
                return found
    return found


def _confirm(
    rows: list[dict[str, Any]],
    foe: list[Card],
    rules: FamilyRules,
    games: int,
    shared: int,
) -> list[dict[str, Any]]:
    from app.engine.montecarlo import run_simulation

    base = STRATEGY_LIBRARY["balanced"]
    runs: list[dict[str, Any]] = []
    for row in rows:
        record = run_simulation(
            row["_cards"],
            foe,
            rules,
            replace(base),
            replace(base),
            games=games,
            seed=shared,
            question="fate search",
            queries=[],
        )
        block = uncertainty(record)
        stat = block["outputs"]["win_rate"]
        if stat["mean"] is None:
            raise ValueError("win rate has no observations")
        row["win_rate"] = stat["mean"]
        row["variance"] = stat["variance"]
        row["brick_rate"] = block["brick_rate"]
        row["chain_break_rate"] = block["chain_break_rate"]
        row["sim_id"] = block["sim_id"]
        row["games"] = block["games"]
        runs.append(record)
    return runs


def _by_uncertainty(rows: list[dict[str, Any]], tol: float) -> list[dict[str, Any]]:
    """Higher win rate, unless the rates sit inside tolerance: then the steadier list."""

    def cmp(left: dict[str, Any], right: dict[str, Any]) -> int:
        gap = abs(float(left["win_rate"]) - float(right["win_rate"]))
        if gap < tol:
            score_left = (float(left["variance"] or 0), float(left["brick_rate"]), float(left["chain_break_rate"]))
            score_right = (float(right["variance"] or 0), float(right["brick_rate"]), float(right["chain_break_rate"]))
            if score_left < score_right:
                return -1
            if score_right < score_left:
                return 1
            return 0
        if float(left["win_rate"]) > float(right["win_rate"]):
            return -1
        if float(right["win_rate"]) > float(left["win_rate"]):
            return 1
        return 0

    from functools import cmp_to_key

    return sorted(rows, key=cmp_to_key(cmp))


def _speak(before, after, before_score, after_score, cut: str, added: str) -> str:
    text = _reason(before, after, before_score, after_score, cut, added)
    cut_row = next((row for row in before["nodes"] if row["name"] == cut), None)
    add_row = next((row for row in after["nodes"] if row["name"] == added), None)
    extra: list[str] = []
    if cut_row and cut_row.get("isolated"):
        extra.append(f"{cut} is isolated")
    if (
        cut_row
        and add_row
        and cut_row.get("dpe_lead") is not None
        and add_row.get("dpe_lead") is not None
    ):
        extra.append(f"{added} damage per energy {add_row['dpe_lead']} vs {cut} {cut_row['dpe_lead']}")
    if add_row and add_row.get("searchers"):
        extra.append("linked to " + ", ".join(add_row["searchers"]))
    elif add_row and not add_row.get("isolated"):
        extra.append(f"{added} is linked")
    if extra:
        return "; ".join(extra + ([text] if text and text != "no change" else []))
    return text


def _locks(names: list[str] | None) -> set[str]:
    if not names:
        return set()
    if not isinstance(names, list) or not all(isinstance(name, str) and name.strip() for name in names):
        raise ValueError("locks must be card names")
    return {name.strip() for name in names}


def _whole(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label} must be an integer")
    return value


def _validate_budget(data: dict[str, Any]) -> dict[str, int]:
    for key in _BUDGET_KEYS:
        if key not in data:
            raise ValueError(f"missing budget: {key}")
    out = {key: _whole(data[key], key) for key in _BUDGET_KEYS}
    if out["depth"] != 1:
        raise ValueError("depth is 1")
    if any(out[key] < 1 for key in _BUDGET_KEYS):
        raise ValueError("budget must be at least 1")
    return out


def _clamp(budget: dict[str, int]) -> dict[str, int]:
    merged = dict(budget)
    if merged["top_k"] > merged["max_candidates"]:
        merged["top_k"] = merged["max_candidates"]
    return merged
