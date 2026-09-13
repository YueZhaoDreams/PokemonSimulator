#!/usr/bin/env python3
"""Carpet Set G vs household 60s, with the g strategy (Party / Ledian / Flutter Mane).

Rule: s60. Seed 20260912. G is always player A; who goes first is random.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
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
GAMES = 2000
SEED = 20260912
FOES = (
    ("c60", SET_C60_NAMES, "party"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("s60", SET_S60_NAMES, "slash"),
)
QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:", "key": "attacked"},
]


def _run(foe_key: str, foe_names: tuple | list, foe_strat: str) -> tuple[str, dict]:
    rec = run_simulation(
        build_fallback_deck(list(SET_G_NAMES)),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "g", "name": "Carpet Set G"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    return foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
        "party_games": q.get("party", 0),
        "gust_games": q.get("gust", 0),
        "adrena_games": q.get("adrena", 0),
    }


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=min(6, len(FOES))) as pool:
        futs = [pool.submit(_run, key, names, strat) for key, names, strat in FOES]
        for fut in as_completed(futs):
            key, detail = fut.result()
            cells[key] = detail
            print(
                f"G vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"party {detail['party_games']} gust {detail['gust_games']} adrena {detail['adrena_games']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {key: cells[key] for key, _names, _strat in FOES}
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "g_strategy": "g",
        "cells": ordered,
        "win_rate_a": [ordered[key]["a"] for key, *_ in FOES],
        "foes": [key for key, *_ in FOES],
    }
    dest = ROOT / "data/lab/set-g-s60.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("win_rate_a", out["win_rate_a"])


if __name__ == "__main__":
    main()
