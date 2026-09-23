#!/usr/bin/env python3
"""Review: each of Pad / Ultra Ball / Prankish against the card it replaces, on fresh seeds.

Base is live SET_G_NAMES. Each card has its own slot control: the same cut
paid with a Psychic Energy. Pad vs ledyba_energy is the Pad question.
Ultra vs ledian_energy is the Ultra Ball question. Prank vs munk_energy is
the Prankish question.

Ultra Ball is only played with 2 other cards to discard, and G discards a
spare Basic Energy before Boss's Orders, Poffin, or Nest Ball.

Seeds 20260924 and 20260925 (the policy was tuned on 20260923). Games per
seed from LAB_GAMES (default 3,000). Side A is strategy g.
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
SEEDS = (20260924, 20260925)
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
    pad = ("Ledyba", "Poké Pad")
    ultra = ("Ledian", "Ultra Ball")
    prank = ("Munkidori", "Clefable")
    return [
        ("base", base),
        ("pad", _replace(base, [pad])),
        ("ledyba_energy", _replace(base, [("Ledyba", "Psychic Energy")])),
        ("ultra", _replace(base, [ultra])),
        ("ledian_energy", _replace(base, [("Ledian", "Psychic Energy")])),
        ("prank", _replace(base, [prank])),
        ("munk_energy", _replace(base, [("Munkidori", "Psychic Energy")])),
        ("full", _replace(base, [pad, ultra, prank])),
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
    ]


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str, seed: int):
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": f"g-{variant}", "name": f"g-{variant}"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    wins = round(r["win_rate_a"] * GAMES)
    detail = {"wins": wins, "games": GAMES}
    for key in ("party", "prankish", "pad", "ultra"):
        detail[key] = q.get(key, 0)
    return variant, foe_key, seed, detail


def _weighted(rates: dict[str, dict[str, float]], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - rates["base"][key]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        variant: sum(row[key] * weights[key] for key in foe_keys) / wsum for variant, row in rates.items()
    }


def main() -> None:
    started = time.perf_counter()
    variants = g_lists()
    assert variants[0][1] == list(SET_G_NAMES)
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in variants}
    jobs = [
        (variant, names, foe_key, foe_names, foe_strat, seed)
        for seed in SEEDS
        for variant, names in variants
        for foe_key, foe_names, foe_strat in FOES
    ]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        for fut in as_completed(futs):
            variant, foe_key, seed, detail = fut.result()
            cell = cells[variant].setdefault(foe_key, {"wins": 0, "games": 0, "by_seed": {}})
            cell["wins"] += detail["wins"]
            cell["games"] += detail["games"]
            cell["by_seed"][str(seed)] = detail
            print(f"{variant} vs {foe_key} seed {seed}: {detail['wins'] / GAMES:.1%}", flush=True)
    foe_keys = tuple(key for key, *_ in FOES)
    ordered = {variant: {key: cells[variant][key] for key in foe_keys} for variant, _ in variants}
    for row in ordered.values():
        for cell in row.values():
            cell["a"] = cell["wins"] / cell["games"]
    rates = {variant: {key: row[key]["a"] for key in foe_keys} for variant, row in ordered.items()}
    payload = {
        "games_per_seed": GAMES,
        "seeds": list(SEEDS),
        "elapsed": round(time.perf_counter() - started, 1),
        "lists": {variant: names for variant, names in variants},
        "cells": ordered,
        "weighted_all": _weighted(rates, foe_keys),
        "weighted_competitive": _weighted(rates, COMPETITIVE),
    }
    out = ROOT / "data" / "lab" / "set-g-pad-ultra-review.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed']}s", flush=True)
    header = "variant".ljust(15) + "".join(key.rjust(9) for key in foe_keys) + "   wComp    wAll"
    print(header, flush=True)
    for variant, _ in variants:
        line = variant.ljust(15) + "".join(f"{rates[variant][key]:9.1%}" for key in foe_keys)
        line += f" {payload['weighted_competitive'][variant]:7.1%} {payload['weighted_all'][variant]:7.1%}"
        print(line, flush=True)


if __name__ == "__main__":
    main()
