#!/usr/bin/env python3
"""C60: 1 Prankish Clefable → 1 Poké Pad.

Printed ME02.5 198: search the deck for a Pokémon without a Rule Box.
In this list that is Clefairy or Rebel Clash Clefable — never Clefable ex,
Mega, or Mewtwo. Party treats the Item as that superposition: fetch the
Party engine when short, or the Prankish evo when a Clefairy is already
in play. Locked C60 stays 2 Clefable / 0 Pad; this script only measures.

Seed 20260922. 3,000 games / cell. The C60 variant is always player A;
who goes first is random.

LAB_GAMES overrides the game count (smoke runs). LAB_OUT overrides the JSON
path. A non-3000 run writes under /tmp unless LAB_OUT is set.
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
SEED = 20260922
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

# Hedrick also plays Poké Pad, so tutor / hit counts are side-scoped.
QUERIES = [
    {"type": "event_prefix", "prefix": "poke_pad_hit_a", "key": "pad_hit"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefairy:poke pad", "key": "pad_clefairy"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefable:poke pad", "key": "pad_clefable"},
    {"type": "event_prefix", "prefix": "prankish", "key": "prankish"},
]


def locked_list() -> list[str]:
    names = list(SET_C60_NAMES)
    if len(names) != 60:
        raise ValueError(f"locked C60 is {len(names)} cards")
    return names


def pad_list() -> list[str]:
    names = locked_list()
    names.remove("Clefable")
    names.append("Poké Pad")
    bad = copy_violations(build_fallback_deck(names), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    if names.count("Clefable") != 1 or names.count("Poké Pad") != 1:
        raise ValueError("pad trial is not 1 Clefable + 1 Poké Pad")
    return names


def variant_lists() -> list[tuple[str, list[str]]]:
    return [("clefable2", locked_list()), ("pad", pad_list())]


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
        return ROOT / "data/lab/set-c60-poke-pad.json"
    return Path(f"/tmp/set-c60-poke-pad-{GAMES}.json")


def main() -> None:
    variants = dict(variant_lists())
    only = [part for part in os.environ.get("LAB_ONLY", "").split(",") if part]
    unknown = [key for key in only if key not in variants]
    if unknown:
        raise SystemExit(f"unknown LAB_ONLY variants: {unknown}")
    selected = {key: variants[key] for key in (only or variants)}
    started = time.perf_counter()
    cells: dict[str, dict[str, dict]] = {key: {} for key in selected}
    jobs = [
        (var_key, names, foe_key, foe_names, foe_strat)
        for var_key, names in selected.items()
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
                f"(1st {detail['first']:.1%} / 2nd {detail['second']:.1%}) "
                f"pad {detail['pad_hit']} fairy {detail['pad_clefairy']} "
                f"fable {detail['pad_clefable']} prankish {detail['prankish']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {var: {foe: cells[var][foe] for foe, _n, _s in FOES} for var in selected}
    baseline = ordered.get("clefable2") or next(iter(ordered.values()))
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "swap": "1 Prankish Clefable -> 1 Poké Pad",
        "foes": [foe for foe, _n, _s in FOES],
        "lists": {key: list(names) for key, names in selected.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, baseline, COMPETITIVE),
        "weighted_all": _weighted(ordered, baseline, tuple(foe for foe, _n, _s in FOES)),
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "variant".ljust(14) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp"
    print(header, flush=True)
    for key in selected:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{key.ljust(14)}{row}  {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
