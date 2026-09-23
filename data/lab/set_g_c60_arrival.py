#!/usr/bin/env python3
"""G → C60: which of this arrival actually goes into the live 60.

Arrivals: 2 SM Lillie (until 6 / first turn 8), 1 Night Stretcher, 1 extra
Ultra Ball (G already has 1), 2 Poké Pad, 2 Rebel Clash Prankish Clefable.
C60's lock wants 2 / 1 / 2 / 1 / 1 of those. The second Pad and the second
Prankish are the extras. This matrix swaps them into live SET_G_NAMES.

Result (seed 20260923, 3,000): sleeve none of them. See
data/lab/set-g-c60-arrival.md. The Pad-for-Ledian bump was the Ledian cut;
Ledian → Psychic Energy beats adding the Pad.

Seed 20260923. Games from LAB_GAMES (default 3,000). Side A is the trial
list with strategy g; first player is random.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
try:
    import app  # noqa: F401
except ImportError:
    sys.path.insert(0, str(ROOT))

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEED = 20260923
WORKERS = int(os.environ.get("LAB_WORKERS", "4"))

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "prankish_a", "key": "prankish"},
    {"type": "event_prefix", "prefix": "poke_pad_hit_a", "key": "pad"},
    {"type": "event_prefix", "prefix": "night_stretcher_a", "key": "stretcher"},
    {"type": "event_prefix", "prefix": "ultra_ball_hit_a", "key": "ultra"},
    {"type": "event_prefix", "prefix": "lillie_a", "key": "lillie"},
    {"type": "event_prefix", "prefix": "drayton", "key": "drayton"},
    {"type": "event_prefix", "prefix": "lunar_zone_play", "key": "zone"},
]


def _replace(names: list[str], pairs: list[tuple[str, str]]) -> list[str]:
    out = list(names)
    for old, new in pairs:
        out[out.index(old)] = new
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return out


def g_lists() -> list[tuple[str, list[str]]]:
    base = list(SET_G_NAMES)
    draw2 = [
        ("Iris's Fighting Spirit", "Lillie"),
        ("Drayton", "Lillie"),
    ]
    draw_str = draw2 + [("Energy Retrieval", "Night Stretcher")]
    return [
        ("live", base),
        ("lillie_iris", _replace(base, [("Iris's Fighting Spirit", "Lillie")])),
        ("lillie_drayton", _replace(base, [("Drayton", "Lillie")])),
        ("lillie2", _replace(base, draw2)),
        ("stretcher", _replace(base, [("Energy Retrieval", "Night Stretcher")])),
        (
            "iris_str",
            _replace(
                base,
                [
                    ("Iris's Fighting Spirit", "Lillie"),
                    ("Energy Retrieval", "Night Stretcher"),
                ],
            ),
        ),
        ("lillie2_stretcher", _replace(base, draw_str)),
        ("l2s_ultra", _replace(base, draw_str + [("Darkness Energy", "Ultra Ball")])),
        ("l2s_pad", _replace(base, draw_str + [("Darkness Energy", "Poké Pad")])),
        ("l2s_prank", _replace(base, draw_str + [("Darkness Energy", "Clefable")])),
        (
            "l2s_prank2",
            _replace(
                base,
                draw_str + [("Darkness Energy", "Clefable"), ("Darkness Energy", "Clefable")],
            ),
        ),
        (
            "l2s_pad2",
            _replace(
                base,
                draw_str + [("Darkness Energy", "Poké Pad"), ("Psychic Energy", "Poké Pad")],
            ),
        ),
        (
            "slice",
            _replace(
                base,
                draw_str
                + [
                    ("Darkness Energy", "Ultra Ball"),
                    ("Psychic Energy", "Poké Pad"),
                    ("Ledian", "Clefable"),
                ],
            ),
        ),
        ("pad_ledian", _replace(base, [("Ledian", "Poké Pad")])),
        # Controls: pad_ledian mixes "cut a Ledian" with "add a Pad".
        ("ledian_energy", _replace(base, [("Ledian", "Psychic Energy")])),
        ("iris_pad", _replace(base, [("Iris's Fighting Spirit", "Poké Pad")])),
        ("psychic_pad", _replace(base, [("Psychic Energy", "Poké Pad")])),
    ]


def _detail(rec: dict) -> dict:
    r = rec["results"]
    q = r.get("query_counts") or {}
    return {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "party_games": q.get("party", 0),
        "prankish_games": q.get("prankish", 0),
        "pad_games": q.get("pad", 0),
        "stretcher_games": q.get("stretcher", 0),
        "ultra_games": q.get("ultra", 0),
        "lillie_games": q.get("lillie", 0),
        "drayton_games": q.get("drayton", 0),
        "zone_games": q.get("zone", 0),
    }


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": f"g-{variant}", "name": f"g-{variant}"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return variant, foe_key, _detail(rec)


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        variant: sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
        for variant, row in cells.items()
    }


def main() -> None:
    started = time.perf_counter()
    variants = g_lists()
    assert variants[0][1] == list(SET_G_NAMES)
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in variants}
    workers = min(WORKERS, max(1, len(variants) * len(FOES)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run, variant, names, foe_key, foe_names, foe_strat)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in FOES
        ]
        for fut in as_completed(futs):
            variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"lillie {detail['lillie_games']} prank {detail['prankish_games']} "
                f"pad {detail['pad_games']} stretcher {detail['stretcher_games']}",
                flush=True,
            )
    foe_keys = tuple(key for key, *_ in FOES)
    ordered = {variant: {key: cells[variant][key] for key in foe_keys} for variant, _ in variants}
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": round(time.perf_counter() - started, 1),
        "lists": {variant: names for variant, names in variants},
        "cells": ordered,
        "weighted_all": _weighted(ordered, ordered["live"], foe_keys),
        "weighted_competitive": _weighted(ordered, ordered["live"], COMPETITIVE),
    }
    out = ROOT / "data" / "lab" / "set-g-c60-arrival.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed']}s", flush=True)
    header = "variant".ljust(18) + "".join(key.rjust(10) for key in foe_keys) + "    wComp     wAll"
    print(header, flush=True)
    for variant, _ in variants:
        row = ordered[variant]
        line = variant.ljust(18) + "".join(f"{row[key]['a']:10.1%}" for key in foe_keys)
        line += f"  {payload['weighted_competitive'][variant]:8.1%}  {payload['weighted_all'][variant]:8.1%}"
        print(line, flush=True)


if __name__ == "__main__":
    main()
