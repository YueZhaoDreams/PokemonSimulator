#!/usr/bin/env python3
"""C60: one more Moonlight Stadium in place of one copy of every other card.

The lock is the live list (``SET_C60_NAMES``). Each other row removes exactly
one copy of one other printed name and adds one Moonlight Stadium. Seed
20260926 matches the earlier stadium matrices. 3,000 games / cell. C60 is
always player A. LAB_GAMES / LAB_OUT / LAB_ONLY.

Re-run after locking a copy. The output file is numbered by the row's stadium
count, so a third-copy matrix does not overwrite the second.
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
COPY_CAP = 4

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "g"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

# Stable keys for the printed names this matrix has cut. A new live name needs a key.
CUT_KEYS = {
    "Clefairy": "clefairy",
    "Mewtwo ex": "mewtwo",
    "Clefable": "prankish",
    "Clefable CLC": "clc",
    "Clefable ex": "ex",
    "Seeker": "seeker",
    "Nest Ball": "nest",
    "Buddy-Buddy Poffin": "poffin",
    "Ultra Ball": "ultra",
    "Hop": "hop",
    "Lillie": "lillie",
    "Lillie's Determination": "det",
    "Arven": "arven",
    "Boss's Orders": "boss",
    "Iono": "iono",
    "Switch": "switch",
    "Energy Switch": "eswitch",
    "Night Stretcher": "stretcher",
    "Maximum Belt": "belt",
    "Battle Cage": "cage",
    "Telepathic Psychic Energy": "tele",
    "Psychic Energy": "energy",
    "Poké Pad": "pad",
}

QUERIES = [
    {"type": "event_prefix", "prefix": "moonlight_party_pivot", "key": "pivot"},
    {"type": "event_prefix", "prefix": "stadium:Moonlight Stadium", "key": "stadium"},
    {"type": "event_prefix", "prefix": "party_energy", "key": "party_energy"},
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
]


def lock_copies() -> int:
    return list(SET_C60_NAMES).count("Moonlight Stadium")


def target_copies() -> int:
    return lock_copies() + 1


def cuts() -> tuple[tuple[str, str], ...]:
    names = []
    seen: set[str] = set()
    for name in SET_C60_NAMES:
        if name == "Moonlight Stadium" or name in seen:
            continue
        seen.add(name)
        names.append(name)
    missing = [name for name in names if name not in CUT_KEYS]
    if missing:
        raise RuntimeError(f"no cut key for {missing}")
    return tuple((CUT_KEYS[name], name) for name in names)


def swap_one(cut: str) -> list[str]:
    names = list(SET_C60_NAMES)
    have = names.count("Moonlight Stadium")
    if have < 1 or have >= COPY_CAP:
        raise RuntimeError(f"live lock has {have} Moonlight Stadium; next copy must stay within {COPY_CAP}")
    if names.count(cut) < 1:
        raise RuntimeError(f"live lock has no {cut}")
    names.remove(cut)
    names.append("Moonlight Stadium")
    if names.count("Moonlight Stadium") != have + 1:
        raise RuntimeError(f"{cut} did not land on {have + 1} Moonlight Stadium")
    if len(names) != 60:
        raise RuntimeError(f"list is {len(names)} cards")
    bad = copy_violations(build_fallback_deck(names), standard_60_rules())
    if bad:
        raise RuntimeError(f"{cut} copy cap: {bad}")
    return names


def build_variants() -> dict[str, list[str]]:
    listed = cuts()
    covered = {name for _key, name in listed}
    live = set(SET_C60_NAMES)
    if covered | {"Moonlight Stadium"} != live:
        missing = sorted(live - covered - {"Moonlight Stadium"})
        extra = sorted(covered - live)
        raise RuntimeError(f"cut list drifted. missing {missing} extra {extra}")
    variants = {"lock": list(SET_C60_NAMES)}
    for key, name in listed:
        variants[key] = swap_one(name)
    return variants


VARIANTS = build_variants()
CUT_NAME = {key: name for key, name in cuts()}


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
    copies = target_copies()
    if GAMES == 3000:
        return ROOT / f"data/lab/set-c60-moonlight-{copies}.json"
    return Path(f"/tmp/set-c60-moonlight-{copies}-{GAMES}.json")


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
    print(
        f"{len(jobs)} cells × {GAMES} games, {WORKERS} workers, "
        f"{lock_copies()} -> {target_copies()} Moonlight Stadium",
        flush=True,
    )
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        for fut in as_completed(futs):
            var_key, foe_key, detail = fut.result()
            cells[var_key][foe_key] = detail
            done += 1
            print(
                f"[{done}/{len(jobs)}] {var_key} vs {foe_key}: {detail['a']:.1%} "
                f"pivot {detail['pivot']} stadium {detail['stadium']}",
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
        "add": "Moonlight Stadium",
        "lock_copies": lock_copies(),
        "stadium_copies": target_copies(),
        "catalog_id": "dp4-100",
        "printed": (
            "The Retreat Cost for each Psychic and Darkness Pokémon "
            "(both yours and your opponent's) is 0."
        ),
        "cuts": {key: CUT_NAME[key] for key in selected if key != "lock"},
        "counts": {name: list(SET_C60_NAMES).count(name) for name in dict.fromkeys(SET_C60_NAMES)},
        "foes": [foe for foe, _n, _s in FOES],
        "lists": {key: list(names) for key, names in selected.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, ordered["lock"], COMPETITIVE),
        "weighted_all": _weighted(ordered, ordered["lock"], tuple(foe for foe, _n, _s in FOES)),
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "cut".ljust(22) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp"
    print(header, flush=True)
    ranking = sorted(selected, key=lambda key: payload["weighted_competitive"][key], reverse=True)
    for key in ranking:
        label = "lock" if key == "lock" else CUT_NAME[key]
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{label.ljust(22)}{row}  {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
