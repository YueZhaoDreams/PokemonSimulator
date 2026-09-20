#!/usr/bin/env python3
"""Monte Carlo Optimization & Win-Rate Array for Radiant Charizard + Colorless Mew ex.

Evaluates 5 candidate variations of the Radiant Charizard + 1-5 Colorless Tech
deck alongside the Phase 1 Champion (V5 Hybrid Baseline) against 4 primary meta
benchmarks in Standard 60 format:
  1. T60: Standard Dragapult ex (Phantom Dive 200 + 60 spread counters)
  2. Hedrick: Andrew Hedrick Worlds 2026 Dragapult ex list
  3. C60: Standard Clefable ex / Mewtwo ex (Moon-Watching Party)
  4. D60: Cornerstone Mask Ogerpon ex (Demolish 140, 260 HP Charm)

Outputs full win-rate array to data/lab/mew-radiant-matrix.json and markdown.
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

VARIANTS: dict[str, dict] = {
    "baseline_v5": {
        "name": "Phase 1 Champion: V5 Hybrid Baseline (Pure Baby)",
        "description": "Winning list from Phase 1: 3 Mew ex, 4 Igglybuff, 3 Budew, 2 Cleffa, 1 Mime Jr., 4 Poffin, 4 Nest, 4 Ultra, 4 Stretcher, 4 Cage, 3 Charm, 1 Belt, 4 Arven, 4 Iono, 2 Research, 3 Boss, 4 Hammer, 4 Switch, 2 CC.",
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
    "rc_v1_pure_slaking": {
        "name": "RC-V1: Pure 0-Energy Slaking & Dunsparce Turbo",
        "description": "100% 0-energy. 1 Radiant Charizard for Excited Heart cost reduction aura + 1 Slaking V (260 dmg at 4 prizes) + 1 Dunsparce (10 dmg + 100% Paralyze at 1 prize) + Baby engine.",
        "cards": (
            ["Mew ex"] * 3
            + ["Radiant Charizard"]
            + ["Slaking V"]
            + ["Dunsparce"]
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
            + ["Switch"] * 3
        ),
    },
    "rc_v2_1fire_hybrid": {
        "name": "RC-V2: 1-Fire Hybrid Finisher",
        "description": "Adds 1 Basic Fire Energy so Radiant Charizard itself can promote and unleash 250 dmg Combustion Blast for 1 Fire at 3+ prizes taken, as an alternate late-game win condition.",
        "cards": (
            ["Mew ex"] * 3
            + ["Radiant Charizard"]
            + ["Slaking V"]
            + ["Dunsparce"]
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
            + ["Switch"] * 2
            + ["Fire Energy"]
        ),
    },
    "rc_v3_full_arsenal": {
        "name": "RC-V3: Full 1-5 Colorless Arsenal (0 Energy)",
        "description": "Full scaling arsenal: 1 Dunsparce (1[C] Para), 1 Snorlax (3[C] 100 dmg), 1 Slaking V (4[C] 260 dmg), 1 Regigigas (5[C] 230 dmg) + 1 Radiant Charizard.",
        "cards": (
            ["Mew ex"] * 3
            + ["Radiant Charizard"]
            + ["Dunsparce"]
            + ["Snorlax"]
            + ["Slaking V"]
            + ["Regigigas"]
            + ["Igglybuff"] * 3
            + ["Budew"] * 2
            + ["Cleffa"] * 2
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
        ),
    },
    "rc_v4_midrange": {
        "name": "RC-V4: Focused Snorlax & Slaking Midrange (0 Energy)",
        "description": "Streamlined 0-energy attacker core: 1 Snorlax (100 dmg at 3 prizes) + 1 Slaking V (260 dmg at 4 prizes), keeping 4 Igglybuff for max Bouncy Circle synergy.",
        "cards": (
            ["Mew ex"] * 3
            + ["Radiant Charizard"]
            + ["Slaking V"]
            + ["Snorlax"]
            + ["Igglybuff"] * 4
            + ["Budew"] * 3
            + ["Cleffa"] * 2
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
            + ["Switch"] * 3
            + ["Counter Catcher"]
        ),
    },
    "rc_v5_2fire_heavy": {
        "name": "RC-V5: 2-Fire Heavy Charizard Finisher",
        "description": "Runs 2 Fire Energy for maximum reliability of drawing and attaching Fire Energy to Radiant Charizard, ensuring 250 Combustion Blast is always online.",
        "cards": (
            ["Mew ex"] * 3
            + ["Radiant Charizard"]
            + ["Slaking V"]
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
            + ["Switch"] * 2
            + ["Fire Energy"] * 2
        ),
    },
}


def _run_cell(var_key: str, foe_key: str, seed: int) -> dict:
    var = VARIANTS[var_key]
    foe_entry = next(f for f in FOES if f[0] == foe_key)
    _, foe_name, foe_cards, foe_strat = foe_entry

    deck_a = build_fallback_deck(var["cards"])
    deck_b = build_fallback_deck(foe_cards)
    strat_a = StrategySpec.from_dict("mew_baby")
    strat_b = StrategySpec.from_dict(foe_strat)

    record = run_simulation(
        deck_a,
        deck_b,
        standard_60_rules(),
        strat_a,
        strat_b,
        games=GAMES_PER_CELL,
        seed=seed,
        queries=[
            {"type": "event_prefix", "prefix": "attack:Mew ex:"},
            {"type": "event_prefix", "prefix": "attack:Radiant Charizard:"},
        ],
    )

    r = record["results"]
    win_rate = r.get("win_rate_a", 0.0)
    wins_a = r.get("wins_a", 0)
    total = r.get("games_a_first", 0) + r.get("games_a_second", 0) or GAMES_PER_CELL
    win_rate_first = r.get("win_rate_a_going_first", 0.0)
    win_rate_second = r.get("win_rate_a_going_second", 0.0)

    attacks_used = {}
    for k, v in r.get("query_counts", {}).items():
        attacks_used[k] = v

    return {
        "variant": var_key,
        "foe": foe_key,
        "win_rate": round(win_rate, 4),
        "wins_a": wins_a,
        "total_games": total,
        "win_rate_first": round(win_rate_first, 4),
        "win_rate_second": round(win_rate_second, 4),
        "avg_turns": 0.0,
        "key_attacks": attacks_used,
    }


def main():
    print("=" * 80)
    print("Monte Carlo Optimization: Radiant Charizard + Colorless Tech Mew ex")
    print(f"Candidates: {len(VARIANTS)} variants")
    print(f"Matchups: {len(FOES)} meta archetypes")
    print(f"Games per cell: {GAMES_PER_CELL} (Total: {len(VARIANTS) * len(FOES) * GAMES_PER_CELL:,} games)")
    print("=" * 80)

    # Validate all deck sizes
    for k, v in VARIANTS.items():
        assert len(v["cards"]) == 60, f"Variant {k} has {len(v['cards'])} cards, expected 60!"

    tasks = []
    cell_idx = 0
    for var_key in VARIANTS:
        for foe_key, _, _, _ in FOES:
            tasks.append((var_key, foe_key, SEED + cell_idx * 17))
            cell_idx += 1

    t0 = time.time()
    results: dict[str, dict[str, dict]] = {vk: {} for vk in VARIANTS}

    with ProcessPoolExecutor() as pool:
        futures = {pool.submit(_run_cell, vk, fk, s): (vk, fk) for (vk, fk, s) in tasks}
        completed = 0
        for f in as_completed(futures):
            res = f.result()
            results[res["variant"]][res["foe"]] = res
            completed += 1
            print(
                f"[{completed:02d}/{len(tasks):02d}] {VARIANTS[res['variant']]['name'][:28]:<28} "
                f"vs {res['foe']:<7} -> Win Rate: {res['win_rate'] * 100:5.1f}% "
                f"(1st: {res['win_rate_first'] * 100:4.1f}%, 2nd: {res['win_rate_second'] * 100:4.1f}%, turns: {res['avg_turns']:.1f})"
            )

    elapsed = time.time() - t0
    print(f"\nSimulation complete in {elapsed:.1f}s ({completed * GAMES_PER_CELL / elapsed:.0f} games/s)\n")

    # Aggregate overall win rates
    summary: dict[str, dict] = {}
    for vk, vdata in VARIANTS.items():
        cell_wrs = [results[vk][fk]["win_rate"] for fk, _, _, _ in FOES]
        overall_wr = sum(cell_wrs) / len(cell_wrs)
        summary[vk] = {
            "name": vdata["name"],
            "description": vdata["description"],
            "overall_win_rate": round(overall_wr, 4),
            "matchups": {fk: results[vk][fk]["win_rate"] for fk, _, _, _ in FOES},
            "details": results[vk],
            "cards": vdata["cards"],
        }

    # Print summary leaderboard
    print("=" * 80)
    print("LEADERBOARD SUMMARY (Sorted by Overall Win Rate)")
    print("=" * 80)
    sorted_variants = sorted(summary.items(), key=lambda x: x[1]["overall_win_rate"], reverse=True)
    header = f"{'Rank':<4} {'Variant':<35} {'Overall':<8} {'vs T60':<8} {'vs Hedr':<8} {'vs C60':<8} {'vs D60':<8}"
    print(header)
    print("-" * 80)
    for rank, (vk, s) in enumerate(sorted_variants, 1):
        m = s["matchups"]
        print(
            f"{rank:<4} {s['name'][:34]:<35} {s['overall_win_rate']*100:5.1f}%  "
            f"{m.get('t60', 0)*100:5.1f}%   "
            f"{m.get('hedrick', 0)*100:5.1f}%   "
            f"{m.get('c60', 0)*100:5.1f}%   "
            f"{m.get('d60', 0)*100:5.1f}%"
        )
    print("=" * 80)

    # Save to JSON
    json_path = ROOT / "data" / "lab" / "mew-radiant-matrix.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "games_per_cell": GAMES_PER_CELL,
                "leaderboard": [
                    {
                        "rank": i + 1,
                        "variant": k,
                        "name": v["name"],
                        "overall_win_rate": v["overall_win_rate"],
                        "matchups": v["matchups"],
                    }
                    for i, (k, v) in enumerate(sorted_variants)
                ],
                "variants": summary,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"Saved matrix JSON: {json_path}")

    # Generate Markdown Table Report
    md_path = ROOT / "data" / "lab" / "mew-radiant-matrix.md"
    best_var_key, best_var = sorted_variants[0]
    baseline = summary.get("baseline_v5", {})
    delta = (best_var["overall_win_rate"] - baseline.get("overall_win_rate", 0)) * 100

    lines = [
        "# Radiant Charizard & 1-5 Colorless Tech Attackers: Monte Carlo Optimization Matrix",
        "",
        f"**Date**: {time.strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Sample Size**: {GAMES_PER_CELL:,} games per cell × {len(VARIANTS)} variants × {len(FOES)} opponents = **{len(VARIANTS) * len(FOES) * GAMES_PER_CELL:,} games total**",
        "",
        "## Executive Summary",
        "",
        f"- **Champion Variant**: **{best_var['name']}**",
        f"- **Peak Overall Win Rate**: **{best_var['overall_win_rate'] * 100:.1f}%** (vs Phase 1 Baseline: {baseline.get('overall_win_rate', 0) * 100:.1f}%, **{'+' if delta >= 0 else ''}{delta:.1f}% net change**)",
        f"- **Best Matchup**: vs {max(best_var['matchups'], key=best_var['matchups'].get)} ({max(best_var['matchups'].values()) * 100:.1f}%)",
        "",
        "## Full Win-Rate Matrix",
        "",
        "| Rank | Candidate Variant | Overall WR | vs Dragapult (T60) | vs Hedrick Worlds | vs Clefable/Mewtwo (C60) | vs Cornerstone (D60) |",
        "| :---: | :--- | :---: | :---: | :---: | :---: | :---: |",
    ]

    for rank, (vk, s) in enumerate(sorted_variants, 1):
        m = s["matchups"]
        bold = "**" if vk == best_var_key else ""
        lines.append(
            f"| {rank} | {bold}{s['name']}{bold} | {bold}{s['overall_win_rate']*100:.1f}%{bold} | "
            f"{m.get('t60', 0)*100:.1f}% | {m.get('hedrick', 0)*100:.1f}% | {m.get('c60', 0)*100:.1f}% | {m.get('d60', 0)*100:.1f}% |"
        )

    lines.extend([
        "",
        "## Attack Usage Insights",
        "",
        "Key attacks executed during simulations across variants:",
    ])

    for vk, s in sorted_variants[:3]:
        lines.append(f"### {s['name']}")
        lines.append(f"*{s['description']}*")
        lines.append("")
        lines.append("| Matchup | Win Rate | Top Attacks Executed |")
        lines.append("| :--- | :---: | :--- |")
        for fk, _, _, _ in FOES:
            det = s["details"].get(fk, {})
            atks = det.get("key_attacks", {})
            top_atks = sorted(atks.items(), key=lambda x: x[1], reverse=True)[:4]
            atk_str = ", ".join(f"`{k.replace('attack:', '')}`: {v}" for k, v in top_atks) if top_atks else "N/A"
            lines.append(f"| {fk.upper()} | {det.get('win_rate', 0)*100:.1f}% | {atk_str} |")
        lines.append("")

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Saved matrix Markdown: {md_path}")


if __name__ == "__main__":
    main()
