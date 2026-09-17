#!/usr/bin/env python3
"""Diagnostic: how much work do G's 1-ofs do in baseline (Friday lock)?

Measures saw_play + attack rates for each singleton candidate cut, so the
Poffin 4-cut recommendation rests on usage data, not vibes.
Baseline is the frozen Friday list (pre-Poffin lock).
Self-contained. Rule: s60. Seed 20260915. G is always player A.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_D60_NAMES,
    SET_G_FRIDAY_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    SET_C60_NAMES,
    build_fallback_deck,
)

GAMES = 2000
SEED = 20260915

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)

NAMES = [
    "Tornadus",
    "Hop's Cramorant",
    "Relicanth",
    "Indeedee",
    "Kecleon",
    "Flutter Mane",
    "Staraptor",
    "Munkidori",
    "Mega Clefable ex",
]
QUERIES = (
    [{"type": "event_prefix", "prefix": f"saw_play:{n}", "key": f"see_{n}"} for n in NAMES]
    + [{"type": "event_prefix", "prefix": f"attack:{n}", "key": f"atk_{n}"} for n in NAMES]
    + [
        {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
        {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    ]
)


def _run(foe_key, foe_names, foe_strat):
    rec = run_simulation(
        build_fallback_deck(list(SET_G_FRIDAY_NAMES)),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "baseline", "name": "baseline"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    return foe_key, {"a": r["win_rate_a"], **{k: q.get(k, 0) for k in [*[f"see_{n}" for n in NAMES], *[f"atk_{n}" for n in NAMES], "party", "gust"]}}


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=7) as pool:
        futs = [pool.submit(_run, k, n, s) for k, n, s in FOES]
        for fut in as_completed(futs):
            key, detail = fut.result()
            cells[key] = detail
            print(f"baseline vs {key}: {detail['a']:.1%}", flush=True)
    dest = ROOT / "data/lab/set-g-poffin-usage.json"
    dest.write_text(json.dumps({"games": GAMES, "seed": SEED, "cells": cells}, indent=2))
    print(f"elapsed {time.perf_counter()-started:.1f}s -> {dest}")
    for n in NAMES:
        row = " ".join(
            f"{f}:{cells[f][f'see_{n}']}/{cells[f][f'atk_{n}']}" for f, _, _ in FOES
        )
        print(f"{n:<16} see/atk per foe (of {GAMES}): {row}")


if __name__ == "__main__":
    main()
