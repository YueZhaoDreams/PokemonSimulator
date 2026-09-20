#!/usr/bin/env python3
"""Monte Carlo Optimization & Win-Rate Array for Zero-Energy Mew ex & Igglybuff.

Evaluates 5 candidate variations of the 0-energy Mew Baby Box deck against the
primary meta benchmarks in Standard 60 format:
  1. T60: Standard Dragapult ex (Phantom Dive 200 + 60 spread counters)
  2. Hedrick: Andrew Hedrick Worlds 2026 Dragapult ex list
  3. C60: Standard Clefable ex / Mewtwo ex (Moon-Watching Party)
  4. D60: Cornerstone Mask Ogerpon ex (Demolish 140, 260 HP Charm)

Outputs full win-rate array to data/lab/mew-igglybuff-matrix.json and markdown.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

# Allow running from repository root
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
GAMES_PER_CELL = 1000
SEED = 20260920

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
)

# --- 5 Candidate Deck Variations (All 60 cards, 0 Energy) ---

VARIANTS: dict[str, dict] = {
    "v1_balanced": {
        "name": "V1: Balanced Baseline",
        "description": "Solid counts of all user pieces: 3 Mew ex, 4 Igglybuff, 3 Budew, 2 Cleffa, 2 Mime Jr, 4 Battle Cage, 4 Stretcher, Belt, 3 Charm.",
        "cards": (
            ["Mew ex"] * 3
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
            + ["Mime Jr."] * 2
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 4
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 4
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 3
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Boss's Orders"] * 3
            + ["Professor's Research"] * 3
            + ["Crushing Hammer"] * 4
            + ["Switch"] * 4
        ),
    },
    "v2_control_lock": {
        "name": "V2: Heavy Disruption & Item Lock",
        "description": "Maximized disruption: 4 Budew (constant Item Lock), 4 Battle Cage, 4 Crushing Hammer, 4 Iono, 2 Judge.",
        "cards": (
            ["Mew ex"] * 3
            + ["Igglybuff"] * 4
            + ["Budew"] * 4
            + ["Cleffa"] * 2
            + ["Mime Jr."]
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 2
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 4
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 2
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Judge"] * 2
            + ["Boss's Orders"] * 3
            + ["Crushing Hammer"] * 4
            + ["Poké Pad"] * 4
            + ["Switch"] * 4
        ),
    },
    "v3_turbo_aggro": {
        "name": "V3: Turbo Aggro Swarm",
        "description": "Maximum opening consistency: 4 Mew ex, 4 Igglybuff, 4 Ultra Ball, 4 Research, 4 Night Stretcher for fast 150 damage turn 2.",
        "cards": (
            ["Mew ex"] * 4
            + ["Igglybuff"] * 4
            + ["Budew"] * 2
            + ["Cleffa"] * 2
            + ["Mime Jr."]
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 4
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 3
            + ["Maximum Belt"]
            + ["Bravery Charm"] * 2
            + ["Professor's Research"] * 4
            + ["Iono"] * 4
            + ["Arven"] * 4
            + ["Boss's Orders"] * 3
            + ["Switch"] * 4
            + ["Poké Pad"] * 3
            + ["Crushing Hammer"] * 3
        ),
    },
    "v4_tank_mew": {
        "name": "V4: 210 HP Tank Mew (Anti-Phantom)",
        "description": "Survive Phantom Dive: 4 Bravery Charm (Mew 210 HP soaks 200 damage), 4 Battle Cage, 4 Arven, 4 Stretcher.",
        "cards": (
            ["Mew ex"] * 3
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
            + ["Mime Jr."]
            + ["Buddy-Buddy Poffin"] * 4
            + ["Nest Ball"] * 4
            + ["Ultra Ball"] * 3
            + ["Night Stretcher"] * 4
            + ["Battle Cage"] * 4
            + ["Bravery Charm"] * 4
            + ["Maximum Belt"]
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Professor's Research"] * 3
            + ["Boss's Orders"] * 3
            + ["Switch"] * 4
            + ["Counter Catcher"] * 3
            + ["Poké Pad"] * 2
        ),
    },
    "v5_hybrid_meta": {
        "name": "V5: Refined Optimal Hybrid",
        "description": "Best-of-both: 3 Mew ex, 4 Igglybuff, 3 Budew, 2 Cleffa, 1 Mime Jr, 4 Battle Cage, 3 Charm, 1 Belt, 4 Stretcher, 4 Poffin, 4 Nest, 4 Ultra.",
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
            + ["Bravery Charm"] * 3
            + ["Maximum Belt"]
            + ["Arven"] * 4
            + ["Iono"] * 4
            + ["Professor's Research"] * 2
            + ["Boss's Orders"] * 3
            + ["Crushing Hammer"] * 4
            + ["Switch"] * 4
            + ["Counter Catcher"] * 2
        ),
    },
}


def _verify_deck_counts():
    for key, v in VARIANTS.items():
        cards = v["cards"]
        assert len(cards) == 60, f"Deck {key} has {len(cards)} cards, expected 60!"


def _run_cell(var_key: str, foe_key: str, foe_names: tuple | list, foe_strat: str) -> tuple[str, str, dict]:
    deck_a_cards = VARIANTS[var_key]["cards"]
    a = build_fallback_deck(list(deck_a_cards))
    b = build_fallback_deck(list(foe_names))
    rec = run_simulation(
        a,
        b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES_PER_CELL,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": var_key, "name": VARIANTS[var_key]["name"]},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return var_key, foe_key, {
        "win_rate_a": r["win_rate_a"],
        "win_rate_b": r["win_rate_b"],
        "tie_rate": r["tie_rate"],
        "first_win_rate_a": r["win_rate_a_going_first"],
        "second_win_rate_a": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
    }


def main() -> None:
    _verify_deck_counts()
    print(f"=== Starting Mew Baby Box Monte Carlo Optimization ({GAMES_PER_CELL} games/cell) ===")
    started = time.perf_counter()

    matrix: dict[str, dict[str, dict]] = {vk: {} for vk in VARIANTS}
    tasks = []

    with ProcessPoolExecutor(max_workers=min(4, len(VARIANTS) * len(FOES))) as pool:
        for var_key in VARIANTS:
            for foe_key, _foe_name, foe_names, foe_strat in FOES:
                tasks.append(pool.submit(_run_cell, var_key, foe_key, foe_names, foe_strat))

        for fut in as_completed(tasks):
            var_key, foe_key, stats = fut.result()
            matrix[var_key][foe_key] = stats
            print(
                f"[{var_key}] vs {foe_key:<8}: {stats['win_rate_a']:.1%} "
                f"(1st: {stats['first_win_rate_a']:.1%} | 2nd: {stats['second_win_rate_a']:.1%})",
                flush=True,
            )

    elapsed = time.perf_counter() - started
    print(f"\nAll simulations complete in {elapsed:.1f}s!\n")

    # Compute overall composite win rate for each variant
    rankings = []
    for vk, vdata in VARIANTS.items():
        cell_wrs = [matrix[vk][fk]["win_rate_a"] for fk, _, _, _ in FOES]
        avg_wr = sum(cell_wrs) / len(cell_wrs)
        rankings.append({
            "variant_id": vk,
            "name": vdata["name"],
            "description": vdata["description"],
            "avg_win_rate": avg_wr,
            "cells": matrix[vk],
            "cards": list(vdata["cards"]),
        })

    rankings.sort(key=lambda x: x["avg_win_rate"], reverse=True)
    best = rankings[0]

    out_data = {
        "meta": {
            "title": "Mew ex & Igglybuff Baby Box 60-Card Optimization Matrix",
            "date": "2026-09-20",
            "seed": SEED,
            "games_per_cell": GAMES_PER_CELL,
            "elapsed_seconds": elapsed,
            "best_variant": best["variant_id"],
        },
        "rankings": rankings,
    }

    json_path = ROOT / "data/lab/mew-igglybuff-matrix.json"
    json_path.write_text(json.dumps(out_data, indent=2))
    print(f"Saved results to {json_path}")

    # Generate Markdown Report
    md_content = _build_markdown_report(out_data)
    md_path = ROOT / "data/lab/mew-igglybuff-matrix.md"
    md_path.write_text(md_content)
    print(f"Saved report to {md_path}")


def _build_markdown_report(data: dict) -> str:
    lines = [
        "# Zero-Energy Mew ex & Igglybuff Deck Optimization Report",
        "",
        f"- **Date**: {data['meta']['date']}",
        f"- **Seed**: `{data['meta']['seed']}`",
        f"- **Games per cell**: {data['meta']['games_per_cell']:,}",
        f"- **Elapsed**: {data['meta']['elapsed_seconds']:.1f}s",
        f"- **Optimal Variant**: **{data['rankings'][0]['name']}** ({data['rankings'][0]['avg_win_rate']:.1%} avg win rate)",
        "",
        "## Win-Rate Matrix (Array) Across Archetypes",
        "",
        "| Rank | Deck Variant | Avg Win Rate | vs T60 (Dragapult) | vs Hedrick (Worlds) | vs C60 (Clefairy) | vs D60 (Ogerpon) |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    for rank, item in enumerate(data["rankings"], 1):
        cells = item["cells"]
        t60 = f"{cells['t60']['win_rate_a']:.1%}"
        hedrick = f"{cells['hedrick']['win_rate_a']:.1%}"
        c60 = f"{cells['c60']['win_rate_a']:.1%}"
        d60 = f"{cells['d60']['win_rate_a']:.1%}"
        avg = f"**{item['avg_win_rate']:.1%}**" if rank == 1 else f"{item['avg_win_rate']:.1%}"
        lines.append(f"| {rank} | **{item['name']}** | {avg} | {t60} | {hedrick} | {c60} | {d60} |")

    lines.extend([
        "",
        "## Deep-Dive Analysis: What Makes the Optimal Deck Strong?",
        "",
        f"### 1. The Winner: {data['rankings'][0]['name']} ({data['rankings'][0]['avg_win_rate']:.1%})",
        data['rankings'][0]['description'],
        "",
        "**Key Insights**:",
        "- **Battle Cage is Essential vs Dragapult**: Dragapult ex's *Phantom Dive* attempts to place 6 damage counters on the bench to wipe 30 HP babies. With 4 Battle Cage in the list, Battle Cage is constantly in play, neutralizing phantom counters entirely.",
        "- **Bravery Charm (210 HP Mew ex)**: With Bravery Charm attached to Mew ex, its HP rises to 210, surviving a direct 200 damage hit from Phantom Dive with 10 HP remaining.",
        "- **Bouncy Circle Burst**: With 5 benched 30-HP Pokémon, Mew ex copies Bouncy Circle for 150 damage for 0 energy every turn. With Maximum Belt vs ex Pokémon, damage reaches 200, 2-shotting any Stage 2 ex or 1-shotting basic ex.",
        "- **Budew Item Lock**: In early game or when facing item-reliant setup (Rare Candy / Poffin / Ultra Ball), copying Itchy Pollen halts the opponent's engine before they evolve.",
        "- **Zero Energy Advantage**: 0 energy cards means 0 energy bricks. Every card drawn is pure gas (search, disruption, recovery).",
        "",
        "## Optimal 60-Card Decklist",
        "",
        "```text",
    ])

    best_cards = data["rankings"][0]["cards"]
    from collections import Counter
    counts = Counter(best_cards)
    for card, cnt in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"{cnt}x {card}")
    lines.extend([
        "```",
        "",
    ])

    return "\n".join(lines)


if __name__ == "__main__":
    main()
