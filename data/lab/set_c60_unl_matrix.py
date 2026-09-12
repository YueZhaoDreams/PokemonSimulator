#!/usr/bin/env python3
"""s60 win-rate matrix: C60 plus household 60s and the three Dragapult 60s.

The three Dragapult lists are household T60 (Candy), printed Hedrick Worlds 2026,
and the Unlimited-shaped Pidgeot / Rotom package. Seed 20260911. 3,000 games /
directed cell. Row is player A; who goes first is random. Diagonal is skipped.
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
GAMES = 3000
SEED = 20260911
DECKS = (
    ("c60", SET_C60_NAMES, "party"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "carnival"),
)


def _run(left: str, right: str) -> tuple[str, str, dict]:
    a_names, a_strat = next((n, s) for k, n, s in DECKS if k == left)
    b_names, b_strat = next((n, s) for k, n, s in DECKS if k == right)
    rec = run_simulation(
        build_fallback_deck(list(a_names)),
        build_fallback_deck(list(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict(a_strat),
        StrategySpec.from_dict(b_strat),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": left, "name": left},
        deck_b_meta={"id": right, "name": right},
    )
    r = rec["results"]
    return left, right, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
    }


def main() -> None:
    started = time.perf_counter()
    keys = [k for k, *_ in DECKS]
    jobs = [(a, b) for a in keys for b in keys if a != b]
    cells: dict[str, dict[str, dict]] = {k: {} for k in keys}
    with ProcessPoolExecutor(max_workers=min(8, len(jobs))) as pool:
        futs = [pool.submit(_run, a, b) for a, b in jobs]
        for fut in as_completed(futs):
            left, right, detail = fut.result()
            cells[left][right] = detail
            print(f"{left} vs {right}: {detail['a']:.1%}", flush=True)
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "row": "player A win rate; first player random",
        "decks": keys,
        "cells": cells,
    }
    dest = ROOT / "data/lab/set-c60-unl-matrix.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    header = ["A \\\\ B", *keys]
    print("| " + " | ".join(header) + " |")
    print("| " + " | ".join(["---"] * len(header)) + " |")
    for row in keys:
        bits = [row]
        for col in keys:
            if row == col:
                bits.append("—")
            else:
                bits.append(f"{cells[row][col]['a']:.1%}")
        print("| " + " | ".join(bits) + " |")


if __name__ == "__main__":
    main()
