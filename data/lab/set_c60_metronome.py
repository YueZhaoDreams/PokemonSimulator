#!/usr/bin/env python3
"""C60: 1 Prankish + 1 Metronome Clefable vs 2 Prankish.

Printed Metronome: choose 1 of the opponent's Active Pokémon's attacks and use
it as this attack. We pick the copy (KO prizes + Active damage + bench
counters). Mime Jr. Mimed Games is the opponent's choice (min). CLC 014 is
Colorless 70 HP Metronome [C]; TWM is Psychic 120 HP Metronome [CC]. Same
printed name as Rebel Clash Prankish, so this is the 2-of Clefable slot, not a
fifth copy. Keep one Prankish for Demolish bounce.

Seed 20260922. 3,000 games / cell. The C60 variant is always player A; who
goes first is random. Do not lock SET_C60_NAMES from this run.

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
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    c60_names_before_bounce,
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

QUERIES = [
    {"type": "event_prefix", "prefix": "metronome:Phantom Dive", "key": "copy_dive"},
    {"type": "event_prefix", "prefix": "metronome:", "key": "metronome_copy"},
    {"type": "event_prefix", "prefix": "metronome_evolve", "key": "metronome_evolve"},
    {"type": "event_prefix", "prefix": "prankish", "key": "prankish"},
    {"type": "event_prefix", "prefix": "boss_orders_a", "key": "boss_a"},
]


def _replace_second_clefable(alias: str) -> list[str]:
    names = c60_names_before_bounce()
    seen = 0
    for i, name in enumerate(names):
        if name != "Clefable":
            continue
        seen += 1
        if seen == 2:
            names[i] = alias
            break
    else:
        raise RuntimeError("expected two Clefable on the cage-lock C60 list")
    return names


def fill(metro_alias: str | None) -> list[str]:
    names = c60_names_before_bounce() if metro_alias is None else _replace_second_clefable(metro_alias)
    if len(names) != 60:
        raise ValueError(f"list is {len(names)} cards")
    cards = build_fallback_deck(names)
    if sum(1 for c in cards if c.name == "Clefable") != 2:
        raise ValueError("need two printed Clefable")
    bad = copy_violations(cards, standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return names


VARIANTS: dict[str, list[str]] = {
    "prankish2": fill(None),
    "clc1": fill("Clefable CLC"),
    "twm1": fill("Clefable TWM"),
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
        return ROOT / "data/lab/set-c60-metronome.json"
    return Path(f"/tmp/set-c60-metronome-{GAMES}.json")


def main() -> None:
    if VARIANTS["prankish2"] != c60_names_before_bounce():
        raise SystemExit("prankish2 drifted from C60_CAGE_LOCK_NAMES")
    only = [part for part in os.environ.get("LAB_ONLY", "").split(",") if part]
    unknown = [key for key in only if key not in VARIANTS]
    if unknown:
        raise SystemExit(f"unknown LAB_ONLY variants: {unknown}")
    selected = {key: VARIANTS[key] for key in (only or VARIANTS)}
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
                f"dive {detail['copy_dive']} copy {detail['metronome_copy']} "
                f"evo {detail['metronome_evolve']} prankish {detail['prankish']} "
                f"boss {detail['boss_a']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {var: {foe: cells[var][foe] for foe, _n, _s in FOES} for var in selected}
    baseline_key = "prankish2" if "prankish2" in ordered else next(iter(ordered))
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "foes": [foe for foe, _n, _s in FOES],
        "lists": {key: list(names) for key, names in selected.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, ordered[baseline_key], COMPETITIVE),
        "weighted_all": _weighted(
            ordered, ordered[baseline_key], tuple(foe for foe, _n, _s in FOES)
        ),
        "lock": "none — trial; SET_C60_NAMES stays 2 Rebel Clash Prankish",
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "variant".ljust(12) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp".rjust(10)
    print(header, flush=True)
    for key in selected:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{key.ljust(12)}{row}  {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
