#!/usr/bin/env python3
"""Crushing Thorn (Worlds 2024) vs the household 60s.

Fernando Cifuentes, 1st Worlds 2024, Limitless 12238. Row is player A.
Who goes first is random inside run_simulation. Standard 60 rules.
"""

from __future__ import annotations

import json
import os
import sys
import time
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
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("THORNS_GAMES", "300"))
SEED = int(os.environ.get("THORNS_SEED", "20260930"))
OUT = ROOT / "data" / "lab" / "iron_thorns_matrix.json"

OPPONENTS = (
    ("c60", SET_C60_NAMES, "party"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "carnival"),
)


def _cell(opponent: str, games: int, thorns_is_a: bool) -> dict:
    names, strat = next((n, s) for key, n, s in OPPONENTS if key == opponent)
    thorns = build_fallback_deck(list(IRON_THORNS_NAMES))
    other = build_fallback_deck(list(names))
    if thorns_is_a:
        cards_a, cards_b = thorns, other
        strat_a, strat_b = "thorns", strat
        left, right = "thorns", opponent
    else:
        cards_a, cards_b = other, thorns
        strat_a, strat_b = strat, "thorns"
        left, right = opponent, "thorns"
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=games,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": left, "name": left},
        deck_b_meta={"id": right, "name": right},
    )
    results = rec["results"]
    return {
        "a": left,
        "b": right,
        "games": games,
        "seed": SEED,
        "win_rate_a": results["win_rate_a"],
        "win_rate_b": results["win_rate_b"],
        "tie_rate": results["tie_rate"],
        "win_rate_a_going_first": results["win_rate_a_going_first"],
        "win_rate_a_going_second": results["win_rate_a_going_second"],
    }


def main() -> None:
    started = time.perf_counter()
    jobs = [(key, True) for key, *_ in OPPONENTS] + [(key, False) for key, *_ in OPPONENTS]
    cells: list[dict] = []
    workers = min(4, os.cpu_count() or 2)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_cell, key, GAMES, thorns_is_a) for key, thorns_is_a in jobs]
        for fut in as_completed(futures):
            cell = fut.result()
            cells.append(cell)
            print(
                f"{cell['a']} vs {cell['b']}: {cell['win_rate_a']:.1%} "
                f"(first {cell['win_rate_a_going_first']:.1%}, second {cell['win_rate_a_going_second']:.1%})",
                flush=True,
            )
    cells.sort(key=lambda row: (row["a"] != "thorns", row["b"], row["a"]))
    payload = {
        "list": "Fernando Cifuentes Worlds 2024 Crushing Thorn, Limitless 12238",
        "games": GAMES,
        "seed": SEED,
        "rules": "standard_60",
        "seconds": round(time.perf_counter() - started, 1),
        "cells": cells,
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {OUT} in {payload['seconds']}s")


if __name__ == "__main__":
    main()
