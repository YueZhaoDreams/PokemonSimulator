#!/usr/bin/env python3
"""C60: one Seeker in Iono's slot, after the five Seeker lines are scripted.

Lines the party plan plays from the printed Seeker sentence:
1. Return a damaged benched ex Boss (or a bench snipe) can knock out. It stays
   in hand, so the ex is not gusted.
2. Bench is full, a Prankish is sitting on the only Clefairy, and Clefable ex
   or Mega Clefable ex is in hand. Seeker returns that stack and replays Clefairy.
3. Two Clefairies on the Bench: evolve one (Prankish), Seeker, evolve the other.
4. Opponent has exactly one Benched Pokémon and the Active attack still KOs.
5. Shooting Moons is short of Energy in hand, and a Benched Pokémon has the
   Energy that makes the knockout.

The other 59 cards are the live lock. Seed 20260926. 3,000 games / cell.
C60 is always player A. LAB_GAMES / LAB_OUT override.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.engine.legality import copy_violations
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

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEED = 20260926
WORKERS = min(4, os.cpu_count() or 1)

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "g"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

QUERIES = [
    {"type": "event_prefix", "prefix": "bounce_a:Seeker", "key": "bounce_seeker"},
    {"type": "event_prefix", "prefix": "seeker_board_wipe", "key": "wipe"},
    {"type": "event_prefix", "prefix": "seeker_save_ex", "key": "save_ex"},
    {"type": "event_prefix", "prefix": "seeker_reline", "key": "reline"},
    {"type": "event_prefix", "prefix": "seeker_double_prankish", "key": "double_prankish"},
    {"type": "event_prefix", "prefix": "seeker_moons_fuel", "key": "moons"},
    {"type": "event_prefix", "prefix": "seeker_moons_blocked", "key": "moons_blocked"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex:Shooting Moons", "key": "moons_attack"},
    {"type": "event_prefix", "prefix": "moons_window", "key": "moons_window"},
    {"type": "event_prefix", "prefix": "moons_already_ko", "key": "moons_already"},
    {"type": "event_prefix", "prefix": "moons_no_fuel", "key": "moons_no_fuel"},
    {"type": "event_prefix", "prefix": "prankish_a", "key": "prankish"},
]


def iono_to_seeker() -> list[str]:
    names = list(SET_C60_NAMES)
    if names.count("Iono") != 1 or names.count("Seeker") != 0:
        raise RuntimeError("live lock no longer has exactly one Iono and zero Seeker")
    names.remove("Iono")
    names.append("Seeker")
    if len(names) != 60:
        raise RuntimeError(f"list is {len(names)} cards")
    bad = copy_violations(build_fallback_deck(names), standard_60_rules())
    if bad:
        raise RuntimeError(f"copy cap: {bad}")
    return names


VARIANTS = {
    "lock": list(SET_C60_NAMES),
    "iono-seeker": iono_to_seeker(),
}


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    total = sum(weights.values())
    out: dict[str, float] = {}
    for variant, row in cells.items():
        out[variant] = sum(row[key]["a"] * weights[key] for key in foe_keys) / total
    return out


def _detail(rec: dict, foe_strat: str) -> dict:
    r = rec["results"]
    q = r.get("query_counts") or {}
    detail = {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
    }
    for query in QUERIES:
        detail[query["key"]] = q.get(query["key"], 0)
    return detail


def _run(var_key: str, var_names: list[str], foe_key: str, foe_names, foe_strat: str):
    rec = run_simulation(
        build_fallback_deck(list(var_names)),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": var_key, "name": var_key},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return var_key, foe_key, _detail(rec, foe_strat)


def _dest() -> Path:
    override = os.environ.get("LAB_OUT")
    if override:
        return Path(override)
    if GAMES == 3000:
        return ROOT / "data/lab/set-c60-seeker-lines.json"
    return Path(f"/tmp/set-c60-seeker-lines-{GAMES}.json")


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict[str, dict]] = {key: {} for key in VARIANTS}
    jobs = [
        (var_key, names, foe_key, foe_names, foe_strat)
        for var_key, names in VARIANTS.items()
        for foe_key, foe_names, foe_strat in FOES
    ]
    print(f"{len(jobs)} cells × {GAMES} games, {WORKERS} workers", flush=True)
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        for fut in as_completed(futs):
            var_key, foe_key, detail = fut.result()
            cells[var_key][foe_key] = detail
            done += 1
            print(
                f"[{done}/{len(jobs)}] {var_key} vs {foe_key}: {detail['a']:.1%} "
                f"seeker {detail['bounce_seeker']} wipe {detail['wipe']} "
                f"save {detail['save_ex']} reline {detail['reline']} "
                f"prank {detail['double_prankish']} moons {detail['moons']} "
                f"blocked {detail['moons_blocked']} swing {detail['moons_attack']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {var: {foe: cells[var][foe] for foe, _n, _s in FOES} for var in VARIANTS}
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "cut": "Iono",
        "add": "Seeker",
        "foes": [foe for foe, _n, _s in FOES],
        "lists": {key: list(names) for key, names in VARIANTS.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, ordered["lock"], COMPETITIVE),
        "weighted_all": _weighted(ordered, ordered["lock"], tuple(foe for foe, _n, _s in FOES)),
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "variant".ljust(16) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp".rjust(10)
    print(header, flush=True)
    for key in VARIANTS:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{key.ljust(16)}{row}  {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
