#!/usr/bin/env python3
"""C60: cut 1 Tool Box (keep Maximum Belt + Arven) for 1 other card.

Arven is still the full-deck Tool + Item search for Belt. Tool Box is only
printed top 7. Seed 20260911. 3,000 games / cell. C60 always A.
G uses dedicated `g`. H has no Zapdos script — nuzzle is the Lightning stand-in.
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
    c60_names_before_bounce,
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


def c60_at_toolbox_bakeoff() -> list[str]:
    """C60 when this bakeoff ran: 13 Psychic + Tool Box.

    Locked C60 later cut Tool Box for a 14th Psychic, then -Jacq -Retrieval
    -1 Iono +3 Battle Cage (bench shields). Re-runs undo that drift so the
    JSON stays comparable.
    """
    names = c60_names_before_bounce()
    for _ in range(names.count("Battle Cage")):
        names.remove("Battle Cage")
    names.extend(["Jacq", "Energy Retrieval", "Iono"])
    if "Tool Box" not in names:
        names[names.index("Psychic Energy")] = "Tool Box"
    return names


FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "g"),
    ("h", SET_H_NAMES, "nuzzle"),
)
REPLACEMENTS = (
    ("energy", "Psychic Energy"),
    ("tele", "Telepathic Psychic Energy"),
    ("stretcher", "Night Stretcher"),
    ("boss", "Boss's Orders"),
    ("retrieval", "Energy Retrieval"),
    ("eswitch", "Energy Switch"),
    ("iono", "Iono"),
    ("hop", "Hop"),
)


def cut_toolbox(names: list[str] | None = None) -> list[str]:
    out = list(names if names is not None else c60_at_toolbox_bakeoff())
    out.remove("Tool Box")
    return out


def swap_toolbox(card: str, names: list[str] | None = None) -> list[str]:
    out = cut_toolbox(names)
    out.append(card)
    if len(out) != 60:
        raise ValueError(f"trial list is {len(out)} cards, not 60")
    return out


def variant_lists() -> list[tuple[str, list[str]]]:
    variants = [("toolbox", c60_at_toolbox_bakeoff())]
    for key, card in REPLACEMENTS:
        variants.append((key, swap_toolbox(card)))
    return variants


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
    variants = variant_lists()
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    workers = min(4, max(1, len(variants) * len(FOES)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        jobs = [
            pool.submit(_run, variant, names, foe_key, foe_names, foe_strat)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in FOES
        ]
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
        "swap": "1 Tool Box -> 1 other (keep Maximum Belt + Arven)",
        "lists": {variant: names for variant, names in variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "cells": ordered,
    }
    dest = ROOT / "data/lab/set-c60-toolbox-swap.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
