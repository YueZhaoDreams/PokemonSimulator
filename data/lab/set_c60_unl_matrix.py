#!/usr/bin/env python3
"""s60 win-rate matrix: C60 plus household 60s and the three Dragapult 60s.

The three Dragapult lists are household T60 (Candy), printed Hedrick Worlds 2026,
and the Unlimited-shaped Pidgeot / Rotom package. Seed 20260911. 3,000 games /
directed cell. Row is player A; who goes first is random. Diagonal is skipped.

Official opening: mulligan until a Basic, then the opponent always draws one
card per mulligan. This script records that table as `cells`, plus the same
seed without bonus draws as `cells_no_bonus` so the delta is visible.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from random import Random

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.game import Game
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


def _rules(bonus: bool):
    rules = standard_60_rules()
    rules.mulligan_bonus_draws = bonus
    return rules


def _run(left: str, right: str, bonus: bool) -> tuple[str, str, bool, dict]:
    a_names, a_strat = next((n, s) for k, n, s in DECKS if k == left)
    b_names, b_strat = next((n, s) for k, n, s in DECKS if k == right)
    rec = run_simulation(
        build_fallback_deck(list(a_names)),
        build_fallback_deck(list(b_names)),
        _rules(bonus),
        StrategySpec.from_dict(a_strat),
        StrategySpec.from_dict(b_strat),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": left, "name": left},
        deck_b_meta={"id": right, "name": right},
    )
    r = rec["results"]
    return left, right, bonus, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
    }


def _first_hand_miss(games: int = GAMES, seed: int = SEED) -> dict[str, dict[str, float]]:
    """Share of opening 7s with no Basic (at least one mulligan), by list."""
    rng = Random(seed)
    dummy_names = list(SET_C60_NAMES)
    dummy = build_fallback_deck(dummy_names)
    dummy_spec = StrategySpec.from_dict("party")
    rules = _rules(True)
    out: dict[str, dict[str, float]] = {}
    for key, names, strat in DECKS:
        deck = build_fallback_deck(list(names))
        spec = StrategySpec.from_dict(strat)
        misses = 0
        total_mull = 0
        for _ in range(games):
            game = Game(deck, dummy, rules, spec, dummy_spec, rng)
            me = game.players["a"]
            if me.mulligans:
                misses += 1
            total_mull += me.mulligans
        out[key] = {
            "first_hand_miss": misses / games,
            "avg_mulligans": total_mull / games,
        }
    return out


def _print_table(keys: list[str], cells: dict[str, dict[str, dict]], title: str) -> None:
    print(title)
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
    print()


def main() -> None:
    started = time.perf_counter()
    keys = [k for k, *_ in DECKS]
    pairs = [(a, b) for a in keys for b in keys if a != b]
    jobs = [(a, b, bonus) for bonus in (True, False) for a, b in pairs]
    cells: dict[str, dict[str, dict]] = {k: {} for k in keys}
    cells_no_bonus: dict[str, dict[str, dict]] = {k: {} for k in keys}
    workers = min(8, os.cpu_count() or 4, len(jobs))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [pool.submit(_run, a, b, bonus) for a, b, bonus in jobs]
        for fut in as_completed(futs):
            left, right, bonus, detail = fut.result()
            dest = cells if bonus else cells_no_bonus
            dest[left][right] = detail
            tag = "bonus" if bonus else "no-bonus"
            print(f"{left} vs {right} ({tag}): {detail['a']:.1%}", flush=True)
    miss = _first_hand_miss()
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "mulligan_bonus_draws": True,
        "row": "player A win rate; first player random",
        "decks": keys,
        "first_hand_miss": miss,
        "cells": cells,
        "cells_no_bonus": cells_no_bonus,
    }
    dest = ROOT / "data/lab/set-c60-unl-matrix.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("first-hand miss (no Basic in the opening 7):")
    for key in keys:
        row = miss[key]
        print(f"  {key}: {row['first_hand_miss']:.1%}  avg mulligans {row['avg_mulligans']:.2f}")
    print()
    _print_table(keys, cells, "with mulligan bonus draws (official)")
    _print_table(keys, cells_no_bonus, "without mulligan bonus draws")
    print("delta (bonus minus no-bonus, player A pp):")
    header = ["A \\\\ B", *keys]
    print("| " + " | ".join(header) + " |")
    print("| " + " | ".join(["---"] * len(header)) + " |")
    for row in keys:
        bits = [row]
        for col in keys:
            if row == col:
                bits.append("—")
            else:
                delta = (cells[row][col]["a"] - cells_no_bonus[row][col]["a"]) * 100
                bits.append(f"{delta:+.1f}")
        print("| " + " | ".join(bits) + " |")


if __name__ == "__main__":
    main()
