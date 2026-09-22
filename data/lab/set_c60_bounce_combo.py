#!/usr/bin/env python3
"""C60 bounce-slot swap matrix.

The live lock spends five indexes on 2 Penny, Professor Turo's Scenario,
Mr. Briney's Compassion, and Seeker. Those indexes used to be a second Hop,
a second Lillie, a second Lillie's Determination, the last Iono, and a second
Energy Switch. Every variant writes only those five indexes, so the other 55
cards stay in the same places.

Seed 20260922. 3,000 games / cell. The C60 variant is always player A; who
goes first is random.

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
    c60_names_before_bounce,
)

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEED = 20260922
WORKERS = min(4, os.cpu_count() or 1)

# Live lock order of the five swapped indexes.
BOUNCE_IN_LOCK = (
    "Penny",
    "Penny",
    "Professor Turo's Scenario",
    "Mr. Briney's Compassion",
    "Seeker",
)
# Cards those indexes held on the cage lock, same order.
CAGE_IN_SLOTS = (
    "Hop",
    "Lillie",
    "Lillie's Determination",
    "Iono",
    "Energy Switch",
)

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "g"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

# Side-scoped keys. UNL also plays Turo, so an unscoped bounce:Turo count
# mixes the opponent's copies into C60's column.
QUERIES = [
    {"type": "event_prefix", "prefix": "bounce_a:Penny", "key": "bounce_penny"},
    {"type": "event_prefix", "prefix": "bounce_a:Professor Turo's Scenario", "key": "bounce_turo"},
    {"type": "event_prefix", "prefix": "bounce_a:Mr. Briney's Compassion", "key": "bounce_briney"},
    {"type": "event_prefix", "prefix": "bounce_a:Seeker", "key": "bounce_seeker"},
    {"type": "event_prefix", "prefix": "bounce_a:AZ", "key": "bounce_az"},
    {"type": "event_prefix", "prefix": "bounce_a:Cheren's Care", "key": "bounce_cheren"},
    {"type": "event_prefix", "prefix": "bounce_heal_a", "key": "bounce_heal"},
    {"type": "event_prefix", "prefix": "bounce_fail_a", "key": "bounce_fail"},
]


def slot_indexes() -> tuple[int, ...]:
    left = list(BOUNCE_IN_LOCK)
    found: list[int] = []
    for i, name in enumerate(SET_C60_NAMES):
        if left and name == left[0]:
            found.append(i)
            left.pop(0)
    if left or len(found) != 5:
        raise RuntimeError(f"bounce slots not found, still missing {left}")
    return tuple(found)


def _cage_with(slot: int, card: str) -> tuple[str, ...]:
    cards = list(CAGE_IN_SLOTS)
    cards[slot] = card
    return tuple(cards)


# key -> the five cards written into the bounce indexes.
VARIANT_SLOTS: dict[str, tuple[str, ...]] = {
    "cage": CAGE_IN_SLOTS,
    "iono-penny": _cage_with(3, "Penny"),
    "iono-turo": _cage_with(3, "Professor Turo's Scenario"),
    "iono-briney": _cage_with(3, "Mr. Briney's Compassion"),
    "iono-seeker": _cage_with(3, "Seeker"),
    "iono-az": _cage_with(3, "AZ"),
    "iono-cheren": _cage_with(3, "Cheren's Care"),
    "penny2": ("Penny", "Penny", "Lillie's Determination", "Iono", "Energy Switch"),
    "penny4": ("Penny", "Penny", "Penny", "Penny", "Energy Switch"),
    "live": BOUNCE_IN_LOCK,
    "no-penny": ("Hop", "Lillie", "Professor Turo's Scenario", "Mr. Briney's Compassion", "Seeker"),
    "no-turo": ("Penny", "Penny", "Lillie's Determination", "Mr. Briney's Compassion", "Seeker"),
    "no-briney": ("Penny", "Penny", "Professor Turo's Scenario", "Iono", "Seeker"),
    "no-seeker": ("Penny", "Penny", "Professor Turo's Scenario", "Mr. Briney's Compassion", "Energy Switch"),
    "az-for-turo": ("Penny", "Penny", "AZ", "Mr. Briney's Compassion", "Seeker"),
    "cheren-for-turo": ("Penny", "Penny", "Cheren's Care", "Mr. Briney's Compassion", "Seeker"),
    "turo-for-briney": (
        "Penny",
        "Penny",
        "Professor Turo's Scenario",
        "Professor Turo's Scenario",
        "Seeker",
    ),
    "briney-for-turo": (
        "Penny",
        "Penny",
        "Mr. Briney's Compassion",
        "Mr. Briney's Compassion",
        "Seeker",
    ),
}


def fill(slot_cards: tuple[str, ...]) -> list[str]:
    if len(slot_cards) != 5:
        raise ValueError(f"need 5 slot cards, got {len(slot_cards)}")
    names = list(SET_C60_NAMES)
    for idx, card in zip(slot_indexes(), slot_cards, strict=True):
        names[idx] = card
    if len(names) != 60:
        raise ValueError(f"list is {len(names)} cards")
    bad = copy_violations(build_fallback_deck(names), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return names


VARIANTS: dict[str, list[str]] = {key: fill(cards) for key, cards in VARIANT_SLOTS.items()}


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
        return ROOT / "data/lab/set-c60-bounce-combo.json"
    return Path(f"/tmp/set-c60-bounce-combo-{GAMES}.json")


def main() -> None:
    from collections import Counter

    if Counter(VARIANTS["cage"]) != Counter(c60_names_before_bounce()):
        raise SystemExit("cage variant drifted from c60_names_before_bounce()")
    if VARIANTS["live"] != list(SET_C60_NAMES):
        raise SystemExit("live variant is not SET_C60_NAMES")
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
                f"(1st {detail['first']:.1%} / 2nd {detail['second']:.1%}) "
                f"penny {detail['bounce_penny']} turo {detail['bounce_turo']} "
                f"briney {detail['bounce_briney']} seeker {detail['bounce_seeker']} "
                f"heal {detail['bounce_heal']}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {var: {foe: cells[var][foe] for foe, _n, _s in FOES} for var in VARIANTS}
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "foes": [foe for foe, _n, _s in FOES],
        "slot_indexes": list(slot_indexes()),
        "variant_slots": {key: list(cards) for key, cards in VARIANT_SLOTS.items()},
        "lists": {key: list(names) for key, names in VARIANTS.items()},
        "cells": ordered,
        "weighted_competitive": _weighted(ordered, ordered["cage"], COMPETITIVE),
        "weighted_all": _weighted(ordered, ordered["cage"], tuple(foe for foe, _n, _s in FOES)),
    }
    dest = _dest()
    dest.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}", flush=True)
    header = "variant".ljust(18) + "".join(foe.rjust(10) for foe, _n, _s in FOES) + "   wComp".rjust(10)
    print(header, flush=True)
    for key in VARIANTS:
        row = "".join(f"{ordered[key][foe]['a']:9.1%}" for foe, _n, _s in FOES)
        w = payload["weighted_competitive"][key]
        print(f"{key.ljust(18)}{row}  {w:7.1%}", flush=True)


if __name__ == "__main__":
    main()
