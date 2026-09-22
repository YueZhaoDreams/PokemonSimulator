#!/usr/bin/env python3
"""G → C60: sleeve 2–4 Telepathic Psychic Energy, pick the count by win rate.

Base G is the frozen Nest/Zone lock (SET_G_NEST_ZONE_NAMES): 17 Psychic, 0 Telepathic.
Destination C60 (SET_C60_NAMES) is already 14 Psychic + 2 Telepathic; 3 and 4
are legal. Swap is N Telepathic for N Psychic Energy on each list.

Printed POR 88 / ME03 88: attach from hand to a Psychic Pokémon, then search
up to 2 Basic Psychic onto the Bench. Party cannot search it from the deck.
g attaches it before Party the same way party does.

Seed 20260922. 3,000 games / cell. Side A is the trial list; first player random.
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
    SET_G_NEST_ZONE_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEED = 20260922
WORKERS = 4
TELE_COUNTS = (0, 2, 3, 4)

C60_FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NEST_ZONE_NAMES, "g"),
    ("h", SET_H_NAMES, "nuzzle"),
)
G_FOES = (
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
    {"type": "event_prefix", "prefix": "telepathic_bench", "key": "tele_bench"},
    {"type": "event_prefix", "prefix": "telepathic_attach", "key": "tele_attach"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "lunar_zone_play", "key": "zone"},
]


def psychic_baseline(names: list[str] | tuple[str, ...]) -> list[str]:
    return [
        "Psychic Energy" if n == "Telepathic Psychic Energy" else n
        for n in names
    ]


def with_telepathic(names: list[str] | tuple[str, ...], n: int) -> list[str]:
    out = psychic_baseline(names)
    psychic = out.count("Psychic Energy")
    if n > psychic:
        raise ValueError(f"need {n} Psychic Energy to swap, have {psychic}")
    for _ in range(n):
        out[out.index("Psychic Energy")] = "Telepathic Psychic Energy"
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards, want 60")
    return out


def c60_lists() -> list[tuple[str, list[str]]]:
    return [(f"tele{n}", with_telepathic(SET_C60_NAMES, n)) for n in TELE_COUNTS]


def g_lists() -> list[tuple[str, list[str]]]:
    return [(f"tele{n}", with_telepathic(SET_G_NEST_ZONE_NAMES, n)) for n in TELE_COUNTS]


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
        "tele_bench_games": q.get("tele_bench", 0),
        "tele_attach_games": q.get("tele_attach", 0),
        "gust_games": q.get("gust", 0),
        "zone_games": q.get("zone", 0),
    }


def _run(
    family: str,
    variant: str,
    names: list[str],
    foe_key: str,
    foe_names,
    foe_strat: str,
    strat_a: str,
) -> tuple[str, str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": f"{family}-{variant}", "name": f"{family}-{variant}"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return family, variant, foe_key, _detail(rec)


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    out: dict[str, float] = {}
    for variant, row in cells.items():
        out[variant] = sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
    return out


def _jobs(
    family: str,
    variants: list[tuple[str, list[str]]],
    foes: tuple,
    strat_a: str,
) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    workers = min(WORKERS, max(1, len(variants) * len(foes)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run, family, variant, names, foe_key, foe_names, foe_strat, strat_a)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in foes
        ]
        for fut in as_completed(futs):
            fam, variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            print(
                f"{fam} {variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"tele_attach {detail['tele_attach_games']} tele_bench {detail['tele_bench_games']} "
                f"party {detail['party_games']}",
                flush=True,
            )
    return {variant: {key: cells[variant][key] for key, *_ in foes} for variant, _ in variants}


def main() -> None:
    started = time.perf_counter()
    c60_variants = c60_lists()
    g_variants = g_lists()
    assert c60_variants[0][0] == "tele0"
    assert c60_variants[1][1] == list(SET_C60_NAMES)
    assert g_variants[0][1] == list(SET_G_NEST_ZONE_NAMES)
    assert g_variants[0][1].count("Telepathic Psychic Energy") == 0
    assert g_variants[0][1].count("Psychic Energy") == 17

    print(f"=== C60 destination {GAMES} games ===", flush=True)
    c60_cells = _jobs("c60", c60_variants, C60_FOES, "party")
    c60_keys = tuple(k for k, *_ in C60_FOES)
    c60_w = _weighted(c60_cells, c60_cells["tele2"], c60_keys)
    c60_comp = _weighted(c60_cells, c60_cells["tele2"], COMPETITIVE)

    print(f"=== G nest/zone {GAMES} games ===", flush=True)
    g_cells = _jobs("g", g_variants, G_FOES, "g")
    g_keys = tuple(k for k, *_ in G_FOES)
    g_w = _weighted(g_cells, g_cells["tele0"], g_keys)
    g_comp = _weighted(g_cells, g_cells["tele0"], COMPETITIVE)

    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "swap": "N Telepathic Psychic Energy for N Psychic Energy",
        "c60": {
            "source": "SET_C60_NAMES",
            "strat": "party",
            "lists": {k: names for k, names in c60_variants},
            "foes": {key: strat for key, _names, strat in C60_FOES},
            "cells": c60_cells,
            "weighted_all": c60_w,
            "weighted_competitive": c60_comp,
        },
        "g": {
            "source": "SET_G_NEST_ZONE_NAMES",
            "strat": "g",
            "lists": {k: names for k, names in g_variants},
            "foes": {key: strat for key, _names, strat in G_FOES},
            "cells": g_cells,
            "weighted_all": g_w,
            "weighted_competitive": g_comp,
        },
    }
    dest = ROOT / "data/lab/set-g-c60-telepathic.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("c60 weighted_all", {k: round(v, 4) for k, v in sorted(c60_w.items(), key=lambda kv: -kv[1])})
    print("c60 weighted_competitive", {k: round(v, 4) for k, v in sorted(c60_comp.items(), key=lambda kv: -kv[1])})
    print("g weighted_all", {k: round(v, 4) for k, v in sorted(g_w.items(), key=lambda kv: -kv[1])})
    print("g weighted_competitive", {k: round(v, 4) for k, v in sorted(g_comp.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
