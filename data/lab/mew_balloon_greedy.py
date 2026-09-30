#!/usr/bin/env python3
"""Greedy one-card swaps of Bursting Balloon into Set M.

Each step lists every legal cut (one copy of a card already in the 60, Balloon
stays at 4 or fewer). The chosen swap is the one with the highest weighted win
rate. Weights are frozen from the starting list: foe weight is 1 minus that
list's win rate, so a matchup Set M already loses counts more. Stop when no
swap raises the weighted win rate.

Set M is player A. Who goes first is random inside run_simulation.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_M60_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("BALLOON_GAMES", "1000"))
SEED = int(os.environ.get("BALLOON_SEED", "20260930"))
OUT = ROOT / "data" / "lab" / "mew_balloon_greedy.json"
ADD = "Bursting Balloon"

FOES = (
    ("c60", list(SET_C60_NAMES), "party"),
    ("t60", list(SET_T60_NAMES), "phantom"),
    ("hedrick", list(SET_T_META_NAMES), "phantom"),
    ("unl", list(SET_T_UNL_NAMES), "phantom"),
    ("d60", list(SET_D60_NAMES), "demolish"),
    ("s60", list(SET_S60_NAMES), "slash"),
    ("g", list(SET_G_NAMES), "carnival"),
    ("thorns", list(IRON_THORNS_NAMES), "thorns"),
)


def _cell(deck: list[str], foe_key: str, games: int) -> dict:
    foe_names, foe_strat = next((names, strat) for key, names, strat in FOES if key == foe_key)
    rec = run_simulation(
        build_fallback_deck(list(deck)),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": "m-balloon", "name": "m-balloon"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    results = rec["results"]
    return {
        "a": results["win_rate_a"],
        "b": results["win_rate_b"],
        "tie": results["tie_rate"],
        "first": results["win_rate_a_going_first"],
        "second": results["win_rate_a_going_second"],
    }


def _run_rows(jobs: list[tuple[str, list[str]]], games: int) -> dict[str, dict[str, dict]]:
    """jobs are (label, deck). Every foe cell in the batch shares one process pool."""
    workers = min(4, os.cpu_count() or 2, max(1, len(jobs) * len(FOES)))
    cells: dict[str, dict[str, dict]] = {label: {} for label, _deck in jobs}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_cell, deck, foe_key, games): (label, foe_key)
            for label, deck in jobs
            for foe_key, *_rest in FOES
        }
        for fut in as_completed(futures):
            label, foe_key = futures[fut]
            detail = fut.result()
            cells[label][foe_key] = detail
            print(
                f"  {label} vs {foe_key}: {detail['a']:.1%} "
                f"(first {detail['first']:.1%}, second {detail['second']:.1%})",
                flush=True,
            )
    return {
        label: {foe_key: cells[label][foe_key] for foe_key, *_rest in FOES}
        for label, _deck in jobs
    }


def _weights(baseline: dict[str, dict]) -> dict[str, float]:
    return {key: max(1e-6, 1.0 - float(baseline[key]["a"])) for key, *_ in FOES}


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    total = sum(weights.values())
    return sum(float(cells[key]["a"]) * weights[key] for key in weights) / total


def _cuts(deck: list[str]) -> list[str]:
    counts = Counter(deck)
    if counts[ADD] >= 4:
        return []
    return sorted(name for name, count in counts.items() if name != ADD and count > 0)


def _swap(deck: list[str], cut: str) -> list[str]:
    nxt = list(deck)
    nxt.remove(cut)
    nxt.append(ADD)
    if len(nxt) != 60:
        raise RuntimeError(f"swap {cut} produced {len(nxt)} cards")
    if Counter(nxt)[ADD] > 4:
        raise RuntimeError("Bursting Balloon would exceed 4")
    return nxt


def _counts(deck: list[str]) -> list[list]:
    return [[name, count] for name, count in Counter(deck).most_common()]


def main() -> None:
    started = time.perf_counter()
    current = list(SET_M60_NAMES)
    if len(current) != 60:
        raise RuntimeError(f"Set M has {len(current)} cards")
    print(f"=== baseline {GAMES} games, seed {SEED} ===", flush=True)
    baseline_cells = _run_rows([("baseline", current)], GAMES)["baseline"]
    weights = _weights(baseline_cells)
    best = _weighted(baseline_cells, weights)
    print(f"baseline weighted {best:.4f}  weights { {k: round(v, 3) for k, v in weights.items()} }", flush=True)
    steps: list[dict] = [
        {
            "step": 0,
            "cut": None,
            "add": None,
            "weighted": best,
            "counts": _counts(current),
            "cards": current,
            "cells": baseline_cells,
        }
    ]
    accepted: list[str] = []
    step_n = 0
    while True:
        cuts = _cuts(current)
        if not cuts:
            print("stop: Bursting Balloon is already at 4", flush=True)
            break
        step_n += 1
        print(f"=== step {step_n}: {len(cuts)} cuts ===", flush=True)
        jobs = [(cut, _swap(current, cut)) for cut in cuts]
        rows = _run_rows(jobs, GAMES)
        options = []
        for cut, _trial in jobs:
            cells = rows[cut]
            weighted = _weighted(cells, weights)
            options.append(
                {
                    "cut": cut,
                    "add": ADD,
                    "weighted": weighted,
                    "delta": weighted - best,
                    "counts": _counts(_swap(current, cut)),
                    "cells": cells,
                }
            )
            print(f"  cut {cut}: weighted {weighted:.4f}  delta {weighted - best:+.4f}", flush=True)
        options.sort(key=lambda row: (-row["weighted"], row["cut"]))
        chosen = options[0]
        improved = chosen["weighted"] > best
        steps.append(
            {
                "step": step_n,
                "options": options,
                "chosen": chosen["cut"],
                "chosen_weighted": chosen["weighted"],
                "accepted": improved,
            }
        )
        payload = _payload(started, weights, best, current, accepted, steps)
        OUT.write_text(json.dumps(payload, indent=2))
        print(
            "ranked: "
            + ", ".join(f"{row['cut']} {row['weighted']:.3f}" for row in options),
            flush=True,
        )
        if not improved:
            print(
                f"stop: best cut {chosen['cut']} {chosen['weighted']:.4f} "
                f"does not beat {best:.4f}",
                flush=True,
            )
            break
        accepted.append(chosen["cut"])
        current = _swap(current, chosen["cut"])
        best = chosen["weighted"]
        print(f"accept cut {chosen['cut']} -> weighted {best:.4f}", flush=True)
        OUT.write_text(json.dumps(_payload(started, weights, best, current, accepted, steps), indent=2))
    OUT.write_text(json.dumps(_payload(started, weights, best, current, accepted, steps), indent=2))
    print(f"wrote {OUT}", flush=True)


def _payload(started: float, weights: dict, best: float, current: list[str], accepted: list[str], steps: list) -> dict:
    return {
        "games": GAMES,
        "seed": SEED,
        "rule_preset": "s60",
        "seconds": round(time.perf_counter() - started, 1),
        "weight_rule": "frozen from the starting Set M: foe weight = max(1e-6, 1 - baseline win_rate_a)",
        "weights": weights,
        "add": ADD,
        "accepted_cuts": accepted,
        "weighted": best,
        "list": current,
        "counts": _counts(current),
        "steps": steps,
    }


if __name__ == "__main__":
    main()
