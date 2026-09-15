#!/usr/bin/env python3
"""C60 + N Telepathic Psychic Energy vs every s60 60-card seed list.

Printed POR 88: attach from hand to a Psychic Pokémon, then search up to 2 Basic
Psychic onto the Bench. Party cannot search it from the deck. G uses dedicated
`g` (not carnival). H has no Zapdos script — nuzzle is the Lightning stand-in.

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
    SET_G_NAMES,
    SET_H_NAMES,
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
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "g"),
    ("h", SET_H_NAMES, "nuzzle"),
)


def _c60_psychic_baseline() -> list[str]:
    return [
        "Psychic Energy" if n == "Telepathic Psychic Energy" else n
        for n in SET_C60_NAMES
    ]


def _tele_list(n: int) -> list[str]:
    names = _c60_psychic_baseline()
    for _ in range(n):
        names[names.index("Psychic Energy")] = "Telepathic Psychic Energy"
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
    variants = [("energy", _c60_psychic_baseline())]
    for n in (1, 2, 3, 4):
        variants.append((f"tele{n}", _tele_list(n)))
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    jobs = []
    with ProcessPoolExecutor(max_workers=8) as pool:
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
        "swap": "N Telepathic Psychic Energy for N Psychic Energy",
        "lists": {variant: names for variant, names in variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "cells": ordered,
    }
    dest = ROOT / "data/lab/set-c60-telepathic-energy.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
