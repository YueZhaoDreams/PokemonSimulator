#!/usr/bin/env python3
"""C60 bench-shield bakeoff vs Dragapult (Rabsca / Shaymin / Battle Cage).

Rule: s60 (60 cards, 4 of a name, 6 prizes, Pokémon are not energy).
Seed 20260911. 3,000 games / cell (C60 variant is always player A; first random).
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_D60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    c60_names_before_bounce,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260911
FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
)


def _variant(base: list[str], cut: list[str], add: list[str]) -> list[str]:
    names = list(base)
    for c in cut:
        names.remove(c)
    names.extend(add)
    assert len(names) == 60, len(names)
    return names


def _pre_shield_base() -> list[str]:
    """C60 before this bakeoff locked, in exact original order.

    Order matters: the same seed shuffles indices, so re-insert the cuts where
    they sat (Jacq after Arven, 2nd Iono after the 1st, Retrieval before
    Stretcher) instead of appending, or re-runs diverge from the saved JSON.
    """
    names = c60_names_before_bounce()
    for _ in range(names.count("Battle Cage")):
        names.remove("Battle Cage")
    names.insert(names.index("Arven") + 1, "Jacq")
    names.insert(names.index("Iono") + 1, "Iono")
    names.insert(names.index("Night Stretcher"), "Energy Retrieval")
    assert len(names) == 60
    return names


BASE = _pre_shield_base()
VARIANTS = {
    "base": BASE,
    "cage2-hop-iono": _variant(BASE, ["Hop", "Iono"], ["Battle Cage", "Battle Cage"]),
    "cage2-jacq-retr": _variant(BASE, ["Jacq", "Energy Retrieval"], ["Battle Cage", "Battle Cage"]),
    "cage1-iono": _variant(BASE, ["Iono"], ["Battle Cage"]),
    "rabsca-hop-iono": _variant(BASE, ["Hop", "Iono"], ["Rellor", "Rabsca"]),
    "rabsca-jacq-retr": _variant(BASE, ["Jacq", "Energy Retrieval"], ["Rellor", "Rabsca"]),
    "shaymin-iono": _variant(BASE, ["Iono"], ["Shaymin"]),
}


def _run(var_key: str, var_names: list, foe_key: str, foe_names, foe_strat: str):
    a = build_fallback_deck(list(var_names))
    b = build_fallback_deck(list(foe_names))
    rec = run_simulation(
        a,
        b,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": var_key, "name": var_key},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return (var_key, foe_key), {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
    }


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict[str, dict]] = {v: {} for v in VARIANTS}
    jobs = [(v, vn, fk, fn, fs) for v, vn in VARIANTS.items() for fk, fn, fs in FOES]
    with ProcessPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(_run, v, vn, fk, fn, fs) for v, vn, fk, fn, fs in jobs]
        for fut in as_completed(futs):
            (var_key, foe_key), detail = fut.result()
            cells[var_key][foe_key] = detail
            print(f"{var_key} vs {foe_key}: {detail['a']:.1%} (1st {detail['first']:.1%} / 2nd {detail['second']:.1%})", flush=True)
    elapsed = time.perf_counter() - started
    ordered = {
        var: {foe: cells[var][foe] for foe, _names, _strat in FOES} for var in VARIANTS
    }
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "variants": {k: list(v) for k, v in VARIANTS.items()},
        "cells": ordered,
    }
    dest = ROOT / "data/lab/set-c60-bench-shield.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
