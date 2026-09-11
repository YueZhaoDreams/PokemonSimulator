#!/usr/bin/env python3
"""Set C constructed Standard 60 vs household 60-card lists.

Rule: s60 (60 cards, 4 of a name, 6 prizes, Pokémon are not energy).
Seed 20260911. 3,000 games / ordered pair (C60 is always player A).
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
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    build_fallback_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260911
FOES = (
    ("g", SET_G_NAMES, "carnival"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("s60", SET_S60_NAMES, "slash"),
)


def _run(foe_key: str, foe_names: tuple | list, foe_strat: str) -> tuple[str, dict]:
    a = build_fallback_deck(list(SET_C60_NAMES))
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
        deck_a_meta={"id": "c60", "name": "Set C Standard 60 (Clefairy / Mewtwo)"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
        "pokemon_as_energy": rec["method"]["rules"]["pokemon_as_energy"],
        "deck_size": rec["method"]["rules"]["deck_size"],
        "prize_count": rec["method"]["rules"]["prize_count"],
    }


def main() -> None:
    started = time.perf_counter()
    cells: dict[str, dict] = {}
    with ProcessPoolExecutor(max_workers=min(4, len(FOES))) as pool:
        futs = [pool.submit(_run, key, names, strat) for key, names, strat in FOES]
        for fut in as_completed(futs):
            key, detail = fut.result()
            cells[key] = detail
            print(
                f"C60 vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "c60": list(SET_C60_NAMES),
        "cells": cells,
    }
    dest = ROOT / "data/lab/set-c60-standard.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
