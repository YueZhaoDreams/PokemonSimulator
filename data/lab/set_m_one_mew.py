#!/usr/bin/env python3
"""Compare one-Mew benching with the current Set M board, then one Budew.

The current mew_baby board plays every Mew ex in hand. one_mew keeps a second
Mew ex in hand. Bouncy Circle does 30 damage for each benched Pokémon whose
printed maximum HP is 30, and Mew ex retreats for 0.

Both arms use the locked Penny list. The score is the loss-weighted win rate.
Weights for the comparison are frozen from the old board. If one_mew raises
that score, one Budew is tried by cutting exactly one copy of one other card.
Those weights are frozen from the one_mew list with zero Budew.

Foes: T60, Hedrick, C60, D60, and the Worlds 2024 Crushing Thorn list.
Seed 20260929. 1000 games per cell.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

# Locked Penny list before this search. Do not rewrite it to the locked one-Mew list.
M60_BEFORE = (
    ["Mew ex"] * 3
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 2
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 4
    + ["Bursting Balloon"] * 2
    + ["Hero's Cape"]
    + ["Max Potion"] * 4
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Professor's Research"] * 2
    + ["Boss's Orders"] * 2
    + ["Penny"] * 2
    + ["Crushing Hammer"] * 4
    + ["Counter Catcher"] * 2
    + ["Spiky Energy"] * 2
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("thorns", "Iron Thorns ex (Crushing Thorn)", IRON_THORNS_NAMES, "thorns"),
)

GAMES = int(os.environ.get("M_ONE_MEW_GAMES", "1000"))
SEED = int(os.environ.get("M_ONE_MEW_SEED", "20260929"))
WORKERS = int(os.environ.get("M_ONE_MEW_WORKERS", "4"))
IN_NAME = "Budew"
QUERIES = [
    {"type": "event_sum", "prefix": "bench30_sum_a", "key": "bench_sum"},
    {"type": "event_sum", "prefix": "bench30_n_a", "key": "bench_n"},
    {"type": "event_prefix", "prefix": "two_mew_a", "key": "two_mew"},
    {"type": "event_prefix", "prefix": "itchy_pollen_lock_a", "key": "itchy"},
]
DEST = ROOT / "data/lab/set-m-one-mew.json"
MD_DEST = ROOT / "data/lab/set-m-one-mew.md"


def loss_weights(baseline: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def mew_strat(one_mew: bool) -> StrategySpec:
    data = StrategySpec.from_dict("mew_baby").to_dict()
    data["one_mew"] = one_mew
    return StrategySpec.from_dict(data)


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count("Hero's Cape") > 1:
        raise ValueError("a second Hero's Cape is not legal")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def _babies(cells: dict[str, dict]) -> float:
    total_sum = sum(cells[key]["bench_sum"] for key, *_ in FOES)
    total_n = sum(cells[key]["bench_n"] for key, *_ in FOES)
    return total_sum / total_n if total_n else 0.0


def _run(key: str, names: list[str], one_mew: bool, foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        mew_strat(one_mew),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": key, "name": key},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    counts = r["query_counts"]
    return key, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "bench_sum": counts.get("bench_sum", 0),
        "bench_n": counts.get("bench_n", 0),
        "two_mew": r["queries"].get("two_mew", 0.0),
        "itchy": r["queries"].get("itchy", 0.0),
    }


def _eval(jobs: list[tuple[str, list[str], bool]]) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {key: {} for key, _, _ in jobs}
    work = [
        (key, names, one_mew, foe_key, foe_names, foe_strat)
        for key, names, one_mew in jobs
        for foe_key, _label, foe_names, foe_strat in FOES
    ]
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(work))) as pool:
        futs = [pool.submit(_run, *job) for job in work]
        done = 0
        for fut in as_completed(futs):
            key, foe_key, detail = fut.result()
            cells[key][foe_key] = detail
            done += 1
            babies = detail["bench_sum"] / detail["bench_n"] if detail["bench_n"] else 0.0
            print(
                f"  {key} vs {foe_key}: {detail['a']:.1%}  babies {babies:.2f}  two-mew {detail['two_mew']:.1%}  ({done}/{len(work)})",
                flush=True,
            )
    for key, _, _ in jobs:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _row(cut: str, cells: dict[str, dict], copies: Counter, weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    return {
        "cut": cut,
        "copies_before": copies[cut],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "babies": _babies(ordered),
        "two_mew": sum(ordered[key]["two_mew"] for key, *_ in FOES) / len(FOES),
        "itchy": sum(ordered[key]["itchy"] for key, *_ in FOES) / len(FOES),
        "cells": ordered,
    }


def _better(a: dict, b: dict) -> bool:
    if a["weighted"] != b["weighted"]:
        return a["weighted"] > b["weighted"]
    if a["worst"] != b["worst"]:
        return a["worst"] > b["worst"]
    if a["copies_before"] != b["copies_before"]:
        return a["copies_before"] > b["copies_before"]
    return a["cut"] < b["cut"]


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _cell(cells: dict, key: str) -> str:
    return _pct(cells[key]["a"])


def _board_line(label: str, row: dict) -> str:
    cells = row["cells"]
    return (
        f"| {label} | {_pct(row['weighted'])} | {_pct(row['mean'])} | {row['babies']:.2f} | {_pct(row['two_mew'])} | "
        f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | {_cell(cells, 'd60')} | {_cell(cells, 'thorns')} |"
    )


def _render_md(report: dict) -> str:
    weights = report["weights_old"]
    lines = [
        "# Set M one-Mew bench",
        "",
        "Same locked Penny list. Old board plays every Mew ex in hand.",
        "one_mew leaves a second Mew ex in hand. Bouncy Circle does 30 damage for each",
        "benched Pokémon with a printed maximum HP of 30. Mew ex retreats for 0.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Comparison weights are frozen from the old board.",
        "- **Weights**: "
        + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **one_mew better**: {report['one_mew_better']}",
        f"- **Elapsed**: {report['elapsed_seconds']}s",
        "",
        "| Board | Weighted | Mean | Babies on bench | Games with 2 Mew | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        _board_line("old", report["old"]),
        _board_line("one_mew", report["one_mew"]),
        "",
    ]
    budew = report.get("budew")
    if budew is None:
        lines.append("one_mew did not raise the weighted win rate, so no Budew swap was run.")
        lines.append("")
        return "\n".join(lines)
    lines.extend(
        [
            "## One Budew",
            "",
            "Weights for this step are frozen from the one_mew list with zero Budew.",
            "A swap is better only when the weighted win rate rises.",
            "",
            "- **Budew weights**: "
            + ", ".join(f"{key} {budew['weights'][key]:.1%}" for key, *_ in FOES),
            f"- **Accepted**: {budew['accepted'] or 'none'}",
            "",
            f"| Budew | Weighted | Mean | Babies | Itchy Pollen | Cut | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |",
            f"| ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    base = budew["baseline"]
    lines.append(
        f"| 0 | {_pct(base['weighted'])} | {_pct(base['mean'])} | {base['babies']:.2f} | {_pct(base['itchy'])} | — | "
        f"{_cell(base['cells'], 't60')} | {_cell(base['cells'], 'hedrick')} | {_cell(base['cells'], 'c60')} | "
        f"{_cell(base['cells'], 'd60')} | {_cell(base['cells'], 'thorns')} |"
    )
    if budew["accepted"]:
        best = budew["best"]
        lines.append(
            f"| 1 | {_pct(best['weighted'])} | {_pct(best['mean'])} | {best['babies']:.2f} | {_pct(best['itchy'])} | {best['cut']} | "
            f"{_cell(best['cells'], 't60')} | {_cell(best['cells'], 'hedrick')} | {_cell(best['cells'], 'c60')} | "
            f"{_cell(best['cells'], 'd60')} | {_cell(best['cells'], 'thorns')} |"
        )
    lines.extend(
        [
            "",
            "### Every cut for one Budew",
            "",
            "| Rank | Cut | Weighted | Mean | Babies | Itchy Pollen | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |",
            "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for i, row in enumerate(budew["ranked"], start=1):
        cells = row["cells"]
        lines.append(
            f"| {i} | {row['cut']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | {row['babies']:.2f} | {_pct(row['itchy'])} | "
            f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | {_cell(cells, 'd60')} | {_cell(cells, 'thorns')} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    base_names = list(M60_BEFORE)
    if len(base_names) != 60:
        raise SystemExit(f"Set M is {len(base_names)} cards")
    if base_names.count(IN_NAME) != 0:
        raise SystemExit("Set M already contains Budew")

    print("phase 1: old board vs one_mew", flush=True)
    compared = _eval(
        [
            ("old", base_names, False),
            ("one_mew", base_names, True),
        ]
    )
    old_weights = loss_weights(compared["old"])
    old_row = _row("—", compared["old"], Counter(), old_weights)
    new_row = _row("—", compared["one_mew"], Counter(), old_weights)
    better = new_row["weighted"] > old_row["weighted"]
    print(
        f"old {old_row['weighted']:.4%}  one_mew {new_row['weighted']:.4%}  babies {old_row['babies']:.2f} -> {new_row['babies']:.2f}",
        flush=True,
    )

    budew_report = None
    if better:
        print("phase 2: one Budew under one_mew", flush=True)
        new_weights = loss_weights(compared["one_mew"])
        copies = Counter(base_names)
        cuts = sorted(copies)
        jobs = [(cut, swap_one(base_names, cut), True) for cut in cuts]
        found = _eval(jobs)
        ranked = sorted(
            (_row(cut, found[cut], copies, new_weights) for cut in cuts),
            key=lambda row: (
                -row["weighted"],
                -row["worst"],
                -row["copies_before"],
                row["cut"],
            ),
        )
        baseline = _row("—", compared["one_mew"], copies, new_weights)
        accepted = ranked[0]["cut"] if ranked and ranked[0]["weighted"] > baseline["weighted"] else None
        budew_report = {
            "weights": new_weights,
            "baseline": baseline,
            "ranked": ranked,
            "best": ranked[0] if ranked else None,
            "accepted": accepted,
        }
        print(f"budew accepted: {accepted}", flush=True)

    report = {
        "seed": SEED,
        "games": GAMES,
        "list": base_names,
        "weights_old": old_weights,
        "one_mew_better": better,
        "old": old_row,
        "one_mew": new_row,
        "budew": budew_report,
        "elapsed_seconds": round(time.perf_counter() - started, 1),
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_render_md(report))
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
