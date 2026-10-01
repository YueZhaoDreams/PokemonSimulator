#!/usr/bin/env python3
"""C60: Latias ex in place of the two Moonlight Stadium.

``SET_C60_NAMES`` is the locked row: one Surging Sparks 76 Latias ex and one
Ultra Ball. This script rebuilds the previous two-stadium list as ``lock``,
``latias2`` as both stadiums replaced by Latias ex, and ``latias_ultra`` as
the live list. Seed 20260926 matches the stadium matrices. 3,000 games / cell.
C60 is always player A.

Nest Ball takes Latias ex once a Clefairy is in play. Poffin keeps taking
Clefairy, and Clefairy in hand are played before Mewtwo, so the Demolish 4+1
line still gets its chumps. Telepathic's two Basic Psychic slots are both
Clefairy until the play cap. Mewtwo ex is Lightning, so Telepathic never
takes it, and Latias ex stays for Nest Ball.
LAB_GAMES / LAB_OUT / LAB_ONLY.
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

PRINTED = "Your Basic Pokémon in play have no Retreat Cost."

QUERIES = [
    {"type": "event_prefix", "prefix": "moonlight_party_pivot", "key": "pivot"},
    {"type": "event_prefix", "prefix": "skyliner_party_pivot", "key": "skyliner"},
    {"type": "event_prefix", "prefix": "stadium:Moonlight Stadium", "key": "stadium"},
    {"type": "event_prefix", "prefix": "tutor:Latias ex:nest ball", "key": "nest_latias"},
    {"type": "event_prefix", "prefix": "saw_play:Latias ex", "key": "latias_play"},
    {"type": "event_prefix", "prefix": "attack:Latias ex:Eon Blade", "key": "eon"},
]


def build_variants() -> dict[str, list[str]]:
    live = list(SET_C60_NAMES)
    if (
        live.count("Latias ex") != 1
        or live.count("Ultra Ball") != 1
        or live.count("Moonlight Stadium") != 0
    ):
        raise RuntimeError(
            "live list must be one Latias ex and one Ultra Ball, found "
            f"{live.count('Latias ex')} Latias ex and {live.count('Ultra Ball')} Ultra Ball"
        )
    lock = list(live)
    lock[lock.index("Latias ex")] = "Moonlight Stadium"
    lock[lock.index("Ultra Ball")] = "Moonlight Stadium"
    latias2 = list(live)
    latias2[latias2.index("Ultra Ball")] = "Latias ex"
    mixed = list(live)
    variants = {"lock": lock, "latias2": latias2, "latias_ultra": mixed}
    for key, names in variants.items():
        if len(names) != 60:
            raise RuntimeError(f"{key} is {len(names)} cards")
        bad = copy_violations(build_fallback_deck(names), standard_60_rules())
        if bad:
            raise RuntimeError(f"{key} copy cap: {bad}")
    if latias2.count("Latias ex") != 2 or latias2.count("Moonlight Stadium") != 0:
        raise RuntimeError("latias2 did not replace both stadiums")
    if mixed.count("Latias ex") != 1 or mixed.count("Ultra Ball") != 1 or mixed.count("Moonlight Stadium") != 0:
        raise RuntimeError("latias_ultra did not land on one Latias ex and one Ultra Ball")
    return variants


VARIANTS = build_variants()
LABELS = {
    "lock": "lock",
    "latias2": "2 Latias ex",
    "latias_ultra": "1 Latias ex + Ultra Ball",
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
        return ROOT / "data/lab/set-c60-latias-ex.json"
    return Path(f"/tmp/set-c60-latias-ex-{GAMES}.json")


def main() -> None:
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
                f"skyliner {detail['skyliner']} nest {detail['nest_latias']} "
                f"play {detail['latias_play']} eon {detail['eon']} pivot {detail['pivot']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    if "lock" not in cells:
        raise SystemExit("weighted scores need the lock row in this run")
    ordered = {var: {foe: cells[var][foe] for foe, _n, _s in FOES} for var in selected}
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "add": "Latias ex",
        "catalog_id": "sv08-076",
        "printed": PRINTED,
        "attack": "Eon Blade",
        "attack_text": "During your next turn, this Pokémon can't attack.",
        "foes": [foe for foe, _n, _s in FOES],
        "lists": {key: list(names) for key, names in selected.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, ordered["lock"], COMPETITIVE),
        "weighted_all": _weighted(ordered, ordered["lock"], tuple(foe for foe, _n, _s in FOES)),
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "list".ljust(24) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp    wAll"
    print(header, flush=True)
    ranking = sorted(selected, key=lambda key: payload["weighted_competitive"][key], reverse=True)
    for key in ranking:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        wall = payload["weighted_all"][key]
        print(f"{LABELS[key].ljust(24)}{row}  {w:7.1%}  {wall:7.1%}", flush=True)


if __name__ == "__main__":
    main()
