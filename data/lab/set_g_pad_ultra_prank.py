#!/usr/bin/env python3
"""Energy-lock G: 1 Pad + 1 Ultra Ball + 1 Prankish for Ledyba, Ledian, Munkidori.

Base is live SET_G_NAMES (one Ledian already traded for a Psychic Energy).
Poké Pad and Ultra Ball are held until a hole is in the deck, then they take
that one card. Clefairy while fewer than three are in hand or play, Prankish
when two Clefairy are out and the opponent's Active has an Energy, Clefable ex
for Ultra Ball while Lunar Zone is missing, then Ledyba / Ledian / Munkidori.
Mega only after Clefable ex is in play. Nest Ball and Poffin keep the old list.
Pad cannot take a Rule Box.

The thin_energy row pays the same three cuts with Psychic Energy, so a win
that is only the cuts does not get credited to the tutors.

Earlier matrices: set-g-pad-ultra-prank.json (fixed prefer, items always
played) and set-g-pad-ultra-prank-ondemand.json (hole list that fetched Mega
and stopped Party at two Clefairy). This file is the hold-until-hole run.

Seed 20260923. Games from LAB_GAMES (default 3,000). Side A is strategy g.
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
    {"type": "event_prefix", "prefix": "prankish_a", "key": "prankish"},
    {"type": "event_prefix", "prefix": "poke_pad_hit_a", "key": "pad"},
    {"type": "event_prefix", "prefix": "ultra_ball_hit_a", "key": "ultra"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefable:poke pad", "key": "pad_prank"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefairy:poke pad", "key": "pad_fairy"},
    {"type": "event_prefix", "prefix": "tutor_a:Ledyba:poke pad", "key": "pad_ledyba"},
    {"type": "event_prefix", "prefix": "tutor_a:Ledian:poke pad", "key": "pad_ledian"},
    {"type": "event_prefix", "prefix": "tutor_a:Munkidori:poke pad", "key": "pad_munk"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefable:ultra ball", "key": "ultra_prank"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefable ex:ultra ball", "key": "ultra_ex"},
    {"type": "event_prefix", "prefix": "tutor_a:Mega Clefable ex:ultra ball", "key": "ultra_mega"},
    {"type": "event_prefix", "prefix": "tutor_a:Ledian:ultra ball", "key": "ultra_ledian"},
    {"type": "event_prefix", "prefix": "tutor_a:Ledyba:ultra ball", "key": "ultra_ledyba"},
    {"type": "event_prefix", "prefix": "tutor_a:Munkidori:ultra ball", "key": "ultra_munk"},
    {"type": "event_prefix", "prefix": "tutor_a:Clefairy:ultra ball", "key": "ultra_fairy"},
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
]


def _replace(names: list[str], pairs: list[tuple[str, str]]) -> list[str]:
    out = list(names)
    for old, new in pairs:
        out[out.index(old)] = new
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(bad)
    return out


def g_lists() -> list[tuple[str, list[str]]]:
    base = list(SET_G_NAMES)
    cuts = [
        ("Ledyba", "Poké Pad"),
        ("Ledian", "Ultra Ball"),
        ("Munkidori", "Clefable"),
    ]
    return [
        ("base", base),
        (
            "thin_energy",
            _replace(
                base,
                [
                    ("Ledyba", "Psychic Energy"),
                    ("Ledian", "Psychic Energy"),
                    ("Munkidori", "Psychic Energy"),
                ],
            ),
        ),
        ("pad", _replace(base, [("Ledyba", "Poké Pad")])),
        ("ultra", _replace(base, [("Ledian", "Ultra Ball")])),
        ("prank", _replace(base, [("Munkidori", "Clefable")])),
        ("pad_ultra", _replace(base, cuts[:2])),
        ("pad_prank", _replace(base, [cuts[0], cuts[2]])),
        ("ultra_prank", _replace(base, cuts[1:])),
        ("full", _replace(base, cuts)),
    ]


def _detail(rec: dict) -> dict:
    r = rec["results"]
    q = r.get("query_counts") or {}
    keys = (
        "party",
        "prankish",
        "pad",
        "ultra",
        "pad_prank",
        "pad_fairy",
        "pad_ledyba",
        "pad_ledian",
        "pad_munk",
        "ultra_prank",
        "ultra_ex",
        "ultra_mega",
        "ultra_ledian",
        "ultra_ledyba",
        "ultra_munk",
        "ultra_fairy",
    )
    out = {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
    }
    for key in keys:
        out[key] = q.get(key, 0)
    return out


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
    assert variants[0][1].count("Ledian") == 3
    assert variants[0][1].count("Psychic Energy") == 16
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in variants}
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(variants) * len(FOES))) as pool:
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
                f"pad {detail['pad']} prankish {detail['prankish']} "
                f"pad→prank {detail['pad_prank']} pad→fairy {detail['pad_fairy']} "
                f"ultra→ex {detail['ultra_ex']}",
                flush=True,
            )
    foe_keys = tuple(key for key, *_ in FOES)
    ordered = {variant: {key: cells[variant][key] for key in foe_keys} for variant, _ in variants}
    payload = {
        "games": GAMES,
        "seed": SEED,
        "policy": "hole_ex",
        "elapsed": round(time.perf_counter() - started, 1),
        "lists": {variant: names for variant, names in variants},
        "cells": ordered,
        "weighted_all": _weighted(ordered, ordered["base"], foe_keys),
        "weighted_competitive": _weighted(ordered, ordered["base"], COMPETITIVE),
    }
    out = ROOT / "data" / "lab" / "set-g-pad-ultra-prank-hole.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed']}s", flush=True)
    header = "variant".ljust(14) + "".join(key.rjust(10) for key in foe_keys) + "    wComp     wAll"
    print(header, flush=True)
    for variant, _ in variants:
        row = ordered[variant]
        line = variant.ljust(14) + "".join(f"{row[key]['a']:10.1%}" for key in foe_keys)
        line += f"  {payload['weighted_competitive'][variant]:8.1%}  {payload['weighted_all'][variant]:8.1%}"
        print(line, flush=True)


if __name__ == "__main__":
    main()
