#!/usr/bin/env python3
"""C60 Dimension Valley vs Battle Cage bakeoff.

Testing whether Dimension Valley can replace Battle Cage (0, 1, 2, 3 copies)
in C60, evaluating across all standard foes: T60, Hedrick, UNL, D60, G, S60.

Seed: 20260911
Games: 3,000 / cell
Rule: s60 (Standard 60, Pokémon are not Basic Energy, 6 prizes)
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

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

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260911

FOES = (
    ("t60", "Dragapult 60 (4 Candy)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds 2026", SET_T_META_NAMES, "phantom"),
    ("unl", "UNL Pidgeot Dragapult", SET_T_UNL_NAMES, "phantom"),
    ("d60", "Cornerstone Ogerpon 60", SET_D60_NAMES, "demolish"),
    ("g", "Carpet Set G", SET_G_NAMES, "carnival"),
    ("s60", "Floragato hunter 60", SET_S60_NAMES, "slash"),
)


def _variant(base: list[str], dv_count: int) -> list[str]:
    names = list(base)
    for _ in range(dv_count):
        names.remove("Battle Cage")
        names.append("Dimension Valley")
    assert len(names) == 60, len(names)
    return names


VARIANTS = {
    "cage3_dv0": ("3 Battle Cage (Locked Baseline)", _variant(SET_C60_NAMES, 0)),
    "cage2_dv1": ("2 Battle Cage + 1 Dimension Valley", _variant(SET_C60_NAMES, 1)),
    "cage1_dv2": ("1 Battle Cage + 2 Dimension Valley", _variant(SET_C60_NAMES, 2)),
    "cage0_dv3": ("0 Battle Cage + 3 Dimension Valley", _variant(SET_C60_NAMES, 3)),
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
    jobs = [
        (v, vdata[1], fk, fn, fs)
        for v, vdata in VARIANTS.items()
        for fk, _flabel, fn, fs in FOES
    ]
    with ProcessPoolExecutor(max_workers=8) as pool:
        futs = [pool.submit(_run, v, vn, fk, fn, fs) for v, vn, fk, fn, fs in jobs]
        for fut in as_completed(futs):
            (var_key, foe_key), detail = fut.result()
            cells[var_key][foe_key] = detail
            print(
                f"{var_key:<10} vs {foe_key:<10}: {detail['a']:.1%} (1st {detail['first']:.1%} / 2nd {detail['second']:.1%})",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {
        var: {foe[0]: cells[var][foe[0]] for foe in FOES} for var in VARIANTS
    }
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "variants": {k: {"label": v[0], "cards": list(v[1])} for k, v in VARIANTS.items()},
        "cells": ordered,
    }
    dest = ROOT / "data/lab/set-c60-dimension-valley.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
