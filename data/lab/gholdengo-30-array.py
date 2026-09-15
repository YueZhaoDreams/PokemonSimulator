#!/usr/bin/env python3
"""Ambipom PAR Hand Fling 60 vs household 60s. Directed array, not a full NxN remake.

Row is G30 (strategy celebration) as player A. Columns are the household 60s from
data/lab/set_c60_unl_matrix.py. First player is random. Seed 20260911.
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
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("GAMES", "3000"))
SEED = 20260911
OPPONENTS = (
    ("c60", SET_C60_NAMES, "party"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "carnival"),
)
QUERIES = [
    {"type": "event_prefix", "prefix": "hand_fling", "key": "hand_fling"},
    {"type": "event_prefix", "prefix": "speed_l_draw", "key": "speed_l_draw"},
    {"type": "event_prefix", "prefix": "return_self_to_hand", "key": "return_self_to_hand"},
    {"type": "event_prefix", "prefix": "big_jump", "key": "big_jump"},
    {"type": "event_prefix", "prefix": "celebration", "key": "celebration"},
    {"type": "event_prefix", "prefix": "hand_thirty", "key": "hand_thirty"},
    {"type": "event_prefix", "prefix": "junk_hunt", "key": "junk_hunt"},
    {"type": "event_prefix", "prefix": "puzzle_pair", "key": "puzzle_pair"},
    {"type": "event_prefix", "prefix": "crazy_code", "key": "crazy_code"},
    {"type": "event_prefix", "prefix": "draw_energy_draw", "key": "draw_energy_draw"},
    {"type": "event_prefix", "prefix": "rare_candy", "key": "rare_candy"},
    {"type": "event_prefix", "prefix": "fleet_footed", "key": "fleet_footed"},
    {"type": "event_prefix", "prefix": "star_alchemy", "key": "star_alchemy"},
]


def _run(opp: str) -> tuple[str, dict]:
    names, strat = next((n, s) for k, n, s in OPPONENTS if k == opp)
    rec = run_simulation(
        build_g30_deck(),
        build_fallback_deck(list(names)),
        standard_60_rules(),
        StrategySpec.from_dict("celebration"),
        StrategySpec.from_dict(strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "g30", "name": "g30"},
        deck_b_meta={"id": opp, "name": opp},
    )
    r = rec["results"]
    return opp, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "hand_fling": r["queries"].get("hand_fling", 0.0),
        "speed_l_draw": r["queries"].get("speed_l_draw", 0.0),
        "return_self_to_hand": r["queries"].get("return_self_to_hand", 0.0),
        "big_jump": r["queries"].get("big_jump", 0.0),
        "celebration": r["queries"].get("celebration", 0.0),
        "hand_thirty": r["queries"].get("hand_thirty", 0.0),
        "junk_hunt": r["queries"].get("junk_hunt", 0.0),
        "puzzle_pair": r["queries"].get("puzzle_pair", 0.0),
        "crazy_code": r["queries"].get("crazy_code", 0.0),
        "draw_energy_draw": r["queries"].get("draw_energy_draw", 0.0),
        "rare_candy": r["queries"].get("rare_candy", 0.0),
        "fleet_footed": r["queries"].get("fleet_footed", 0.0),
        "star_alchemy": r["queries"].get("star_alchemy", 0.0),
    }


def main() -> None:
    started = time.perf_counter()
    keys = [k for k, *_ in OPPONENTS]
    cells: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=min(7, len(keys))) as pool:
        futs = [pool.submit(_run, key) for key in keys]
        for fut in as_completed(futs):
            opp, detail = fut.result()
            cells[opp] = detail
            print(
                f"g30 vs {opp}: {detail['a']:.1%} "
                f"(first {detail['first']:.1%} second {detail['second']:.1%} "
                f"hand_fling {detail['hand_fling']:.1%} speed_l {detail['speed_l_draw']:.1%} "
                f"jump {detail['big_jump']:.1%})",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "row": "g30 player A win rate; first player random",
        "strategy_a": "celebration",
        "opponents": keys,
        "cells": cells,
    }
    dest = ROOT / "data/lab/gholdengo-30-array.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    header = ["A \\\\ B", *keys]
    print("| " + " | ".join(header) + " |")
    print("| " + " | ".join(["---"] * len(header)) + " |")
    print("| " + " | ".join(["g30"] + [f"{cells[k]['a']:.1%}" for k in keys]) + " |")
    print("| first | " + " | ".join(f"{cells[k]['first']:.1%}" for k in keys) + " |")
    print("| second | " + " | ".join(f"{cells[k]['second']:.1%}" for k in keys) + " |")
    print("| Hand Fling | " + " | ".join(f"{cells[k]['hand_fling']:.1%}" for k in keys) + " |")
    print("| Speed L draw | " + " | ".join(f"{cells[k]['speed_l_draw']:.1%}" for k in keys) + " |")
    print("| Big Jump | " + " | ".join(f"{cells[k]['big_jump']:.1%}" for k in keys) + " |")


if __name__ == "__main__":
    main()
