#!/usr/bin/env python3
"""C60 + 1 Budew (cut 1 Psychic Energy) vs Item-heavy 60s.

Budew Itchy Pollen locks Item cards only. Historical 1500-game json used a
temporary party sit-and-Pollen path (Switch after Party). That path is not in
locked party; re-running this script on current party will understate Budew.
Seed 20260911. 1,500 games / cell. Result: do not lock Budew into C60.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Allow `python data/lab/set_c60_budew_item_lock.py` from the repo root.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 1500
SEED = 20260911
FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
)


def _c60_plus_budew() -> list[str]:
    names = list(SET_C60_NAMES)
    names[names.index("Psychic Energy")] = "Budew"
    return names


def _run(foe_key: str, foe_names: tuple | list, foe_strat: str) -> tuple[str, dict]:
    a = build_fallback_deck(_c60_plus_budew())
    b = build_fallback_deck(list(foe_names))
    rec = run_simulation(
        a,
        b,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": "c60_budew", "name": "C60 + 1 Budew − 1 Psychic"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
    }


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=min(3, len(FOES))) as pool:
        futs = [pool.submit(_run, key, names, strat) for key, names, strat in FOES]
        for fut in as_completed(futs):
            key, detail = fut.result()
            cells[key] = detail
            print(
                f"C60+Budew vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {key: cells[key] for key, _names, _strat in FOES}
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "swap": "1 Budew for 1 Psychic Energy",
        "c60_plus_budew": _c60_plus_budew(),
        "cells": ordered,
        "baseline_3000_seed_20260911": {
            "t60": 0.543,
            "hedrick": 0.629,
            "d60": 0.753,
        },
        "notes": (
            "Cells used a temporary party sit-and-Pollen path. "
            "Do not lock Budew into SET_C60_NAMES."
        ),
    }
    dest = ROOT / "data/lab/set-c60-budew-item-lock.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
