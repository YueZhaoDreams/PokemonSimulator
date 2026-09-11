#!/usr/bin/env python3
"""C60 + 1 Lillie's Clefairy ex (cut 1 Psychic Energy) vs Dragon / Ogerpon 60s.

Fairy Zone: opponent Dragon Weakness is Psychic ×2. Full Moon Rondo is [P][C]
20 + 20 per benched Pokémon (both sides). 190 HP Basic, 2 prizes.

Seed 20260911. 3,000 games / cell. C60 always A.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260911
FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
)


def _lillie_list() -> list[str]:
    names = list(SET_C60_NAMES)
    names[names.index("Psychic Energy")] = "Lillie's Clefairy ex"
    return names


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": variant, "name": variant},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return variant, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
    }


def main() -> None:
    started = time.perf_counter()
    variants = (
        ("energy", list(SET_C60_NAMES)),
        ("lillie", _lillie_list()),
    )
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    jobs = []
    with ProcessPoolExecutor(max_workers=6) as pool:
        for variant, names in variants:
            for foe_key, foe_names, foe_strat in FOES:
                jobs.append(pool.submit(_run, variant, names, foe_key, foe_names, foe_strat))
        for fut in as_completed(jobs):
            variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    ordered = {
        variant: {key: cells[variant][key] for key, *_ in FOES}
        for variant, _ in variants
    }
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "swap": "1 Lillie's Clefairy ex for 1 Psychic Energy",
        "lillie_list": _lillie_list(),
        "cells": ordered,
    }
    dest = ROOT / "data/lab/set-c60-lillie-clefairy-ex.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
