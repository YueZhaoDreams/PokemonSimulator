#!/usr/bin/env python3
"""Simulation study comparing Dimension Valley variants vs V5 Champion."""

import sys
import time
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

FOES = (
    ("t60", "Dragapult ex", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon", SET_D60_NAMES, "demolish"),
)

VARIANTS = {
    "v5_baseline": {
        "name": "V5 Baseline (Pure Baby + 4 Battle Cage)",
        "cards": (
            ["Mew ex"] * 3
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
            + ["Mime Jr."]
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 4
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 4
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 3
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Professor's Research"] * 2
            + ["Boss's Orders"] * 3
            + ["Crushing Hammer"] * 4
            + ["Switch"] * 4
            + ["Counter Catcher"] * 2
        ),
    },
    "dv1_dunsparce_paralyze": {
        "name": "DV-1: Dimension Valley + Dunsparce (Turn 1 Free Paralyze)",
        "cards": (
            ["Mew ex"] * 3
            + ["Dunsparce"] * 2
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 4
            + ["Night Stretcher"] * 4
            + ["Dimension Valley"] * 4
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 3
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Professor's Research"] * 2
            + ["Boss's Orders"] * 3
            + ["Crushing Hammer"] * 4
            + ["Switch"] * 4
            + ["Counter Catcher"]
        ),
    },
    "dv2_hybrid_cage_valley": {
        "name": "DV-2: Hybrid 2 Battle Cage + 2 Dimension Valley + Dunsparce",
        "cards": (
            ["Mew ex"] * 3
            + ["Dunsparce"]
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
            + ["Mime Jr."]
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 4
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 2
            + ["Dimension Valley"] * 2
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 3
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Professor's Research"] * 2
            + ["Boss's Orders"] * 3
            + ["Crushing Hammer"] * 4
            + ["Switch"] * 3
            + ["Counter Catcher"] * 2
        ),
    },
}

for k, v in VARIANTS.items():
    assert len(v["cards"]) == 60, f"{k} has {len(v['cards'])} cards"

print("=" * 75)
print("DIMENSION VALLEY EVALUATION MATRIX (500 games/cell)")
print("=" * 75)

for vk, vdata in VARIANTS.items():
    print(f"\n--- {vdata['name']} ---")
    wrs = []
    for fk, fname, fcards, fstrat in FOES:
        a = build_fallback_deck(vdata["cards"])
        b = build_fallback_deck(fcards)
        rec = run_simulation(
            a,
            b,
            standard_60_rules(),
            StrategySpec.from_dict("mew_baby"),
            StrategySpec.from_dict(fstrat),
            games=500,
            seed=20260920,
        )
        wr = rec["results"]["win_rate_a"]
        wrs.append(wr)
        print(f"  vs {fname:<20}: {wr*100:5.1f}%")
    avg_wr = sum(wrs) / len(wrs)
    print(f"  >> OVERALL WIN RATE: {avg_wr*100:5.1f}%")
