#!/usr/bin/env python3
"""C60: 1 Prankish + 1 Pad, add CLC by cutting something other than Hop.

Pad-only (second Clefable → Poké Pad) was the only row above the lock.
Paying for CLC with a Hop lost. This matrix keeps 1 Prankish + 1 Pad and
slots CLC 014 by cutting Clefable ex, a Psychic Energy, or another 1-of /
2-of / 3-of that is not Hop — plus the Hop cut as the known floor.

Seed 20260922. 3,000 games / cell. C60 always player A. Do not lock.

LAB_GAMES / LAB_OUT / LAB_ONLY as in the other C60 labs.
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

# pad + CLC paid by cutting this card. hop is the previous combined list.
CUTS = (
    ("hop", "Hop"),
    ("ex", "Clefable ex"),
    ("energy", "Psychic Energy"),
    ("tele", "Telepathic Psychic Energy"),
    ("eswitch", "Energy Switch"),
    ("switch", "Switch"),
    ("iono", "Iono"),
    ("lillie", "Lillie"),
    ("det", "Lillie's Determination"),
    ("stretcher", "Night Stretcher"),
    ("cage", "Battle Cage"),
    ("ultra", "Ultra Ball"),
    ("nest", "Nest Ball"),
    ("poffin", "Buddy-Buddy Poffin"),
    ("mega", "Mega Clefable ex"),
    ("arven", "Arven"),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "poke_pad_hit_a", "key": "pad_hit"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefairy:poke pad", "key": "pad_clefairy"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefable:poke pad", "key": "pad_clefable"},
    {"type": "event_prefix", "prefix": "pad_metro_a", "key": "pad_metro"},
    {"type": "event_prefix", "prefix": "pad_prankish_a", "key": "pad_prankish"},
    {"type": "event_prefix", "prefix": "metronome:Phantom Dive", "key": "copy_dive"},
    {"type": "event_prefix", "prefix": "metronome:", "key": "metronome_copy"},
    {"type": "event_prefix", "prefix": "metronome_evolve", "key": "metronome_evolve"},
    {"type": "event_prefix", "prefix": "prankish", "key": "prankish"},
    {"type": "event_prefix", "prefix": "boss_orders_a", "key": "boss_a"},
]


def _legal(names: list[str], label: str) -> list[str]:
    if len(names) != 60:
        raise ValueError(f"{label} is {len(names)} cards")
    cards = build_fallback_deck(names)
    bad = copy_violations(cards, standard_60_rules())
    if bad:
        raise ValueError(f"{label} copy cap: {bad}")
    return names


def locked_list() -> list[str]:
    return _legal(list(SET_C60_NAMES), "lock")


def pad_list() -> list[str]:
    names = locked_list()
    names.remove("Clefable")
    names.append("Poké Pad")
    return _legal(names, "pad")


def pad_plus_clc(cut: str) -> list[str]:
    names = pad_list()
    names.remove(cut)
    names.append("Clefable CLC")
    return _legal(names, f"pad_clc_cut_{cut}")


def variant_lists() -> list[tuple[str, list[str]]]:
    rows = [
        ("prankish2", locked_list()),
        ("pad", pad_list()),
    ]
    for key, card in CUTS:
        rows.append((key, pad_plus_clc(card)))
    return rows


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
        return ROOT / "data/lab/set-c60-pad-clc-cuts.json"
    return Path(f"/tmp/set-c60-pad-clc-cuts-{GAMES}.json")


def main() -> None:
    variants = dict(variant_lists())
    if variants["prankish2"] != list(SET_C60_NAMES):
        raise SystemExit("prankish2 drifted from SET_C60_NAMES")
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
                f"pad {detail['pad_hit']} metro {detail['pad_metro']} "
                f"prank {detail['pad_prankish']} dive {detail['copy_dive']}",
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
        "swap": "1 Prankish + 1 Pad + 1 CLC by cutting X (not only Hop)",
        "cuts": {key: card for key, card in CUTS},
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
    header = "variant".ljust(12) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp"
    print(header, flush=True)
    for key in selected:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{key.ljust(12)}{row}  {w:7.1%}", flush=True)
    print("\nwComp rank:", flush=True)
    for i, (key, w) in enumerate(
        sorted(payload["weighted_competitive"].items(), key=lambda kv: -kv[1]),
        1,
    ):
        print(f"  {i:2}. {key.ljust(12)} {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
