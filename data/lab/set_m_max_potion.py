#!/usr/bin/env python3
"""Greedy Max Potion swaps for Set M (zero-energy Mew ex).

Start from M60_BEFORE (Set M before this bakeoff). Each step replaces exactly one copy of one card
with one Max Potion. The decision score is the loss-weighted win rate: a foe's
weight is how often the 0-potion list loses that matchup, frozen for the whole
search. Stop when the next swap does not raise that score, or at 4 copies.

Foes match the Mew baby matrix: T60, Hedrick, C60, D60.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
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

# Set M before this bakeoff. SET_M60_NAMES is the locked 4-Max-Potion list.
M60_BEFORE = (
    ["Mew ex"] * 4
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Budew"] * 3
    + ["Cleffa"] * 2
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 4
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 4
    + ["Maximum Belt"]
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Professor's Research"] * 2
    + ["Boss's Orders"] * 3
    + ["Crushing Hammer"] * 4
    + ["Switch"]
    + ["Counter Catcher"] * 2
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("M_POTION_GAMES", "1000"))
SEED = int(os.environ.get("M_POTION_SEED", "20260929"))
WORKERS = int(os.environ.get("M_POTION_WORKERS", "4"))

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
)

QUERIES = [{"type": "event_prefix", "prefix": "max_potion", "key": "max_potion"}]


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append("Max Potion")
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count("Max Potion") > 4:
        raise ValueError("Max Potion would exceed 4")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def loss_weights(baseline: dict[str, dict]) -> dict[str, float]:
    """Household weight: matchups the baseline loses more often count more."""
    raw = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def _run(cut: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": cut, "name": cut},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return cut, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "max_potion": r["queries"].get("max_potion", 0.0),
    }


def _eval_lists(lists: list[tuple[str, list[str]]]) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in lists}
    jobs = [
        (key, names, foe_key, foe_names, foe_strat)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
    ]
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        done = 0
        for fut in as_completed(futs):
            key, foe_key, detail = fut.result()
            cells[key][foe_key] = detail
            done += 1
            print(
                f"  {key} vs {foe_key}: {detail['a']:.1%}  potion {detail['max_potion']:.1%}  ({done}/{len(jobs)})",
                flush=True,
            )
    for key, _ in lists:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _candidate_row(cut: str, cells: dict[str, dict], copies: Counter, weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    return {
        "cut": cut,
        "copies_before": copies[cut],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "max_potion": sum(ordered[key]["max_potion"] for key, *_ in FOES) / len(FOES),
        "cells": ordered,
    }


def _better(a: dict, b: dict) -> bool:
    """True when a should replace b as the committed cut."""
    if a["weighted"] != b["weighted"]:
        return a["weighted"] > b["weighted"]
    if a["worst"] != b["worst"]:
        return a["worst"] > b["worst"]
    if a["copies_before"] != b["copies_before"]:
        return a["copies_before"] > b["copies_before"]
    return a["cut"] < b["cut"]


def _markdown(report: dict) -> str:
    lines = [
        "# Set M greedy Max Potion",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        f"- **Score**: loss-weighted win rate. Weights are frozen from the 0-potion list.",
        f"- **Weights**: {', '.join(f'{key} {report['weights'][key]:.1%}' for key, *_ in FOES)}",
        f"- **Copies**: {report['copies']}",
        f"- **Cuts**: {', '.join(report['cuts']) if report['cuts'] else '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "## Weighted win-rate array",
        "",
        "Index is the number of Max Potion copies. Each step after 0 swaps exactly one card.",
        "The weighted column is the decision score. Mean is the equal-weight average of the same four foes.",
        "",
        "| Max Potion | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 |",
        "| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |",
    ]
    for row in report["array"]:
        cells = row["cells"]
        cut = row["cut"] or "—"
        lines.append(
            f"| {row['copies']} | {row['weighted']:.1%} | {row['mean']:.1%} | {cut} | "
            f"{cells['t60']['a']:.1%} | {cells['hedrick']['a']:.1%} | "
            f"{cells['c60']['a']:.1%} | {cells['d60']['a']:.1%} |"
        )
    if report["rejected"]:
        rej = report["rejected"]
        lines.extend(
            [
                "",
                "## Next swap, not taken",
                "",
                f"Best cut `{rej['cut']}` weighted {rej['weighted']:.1%} does not beat "
                f"{report['array'][-1]['weighted']:.1%} at {report['copies']} copies.",
            ]
        )
    elif report["copies"] == 4:
        lines.extend(
            [
                "",
                "The weighted score was still rising at 4 copies. A fifth Max Potion is not legal.",
            ]
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    current = list(M60_BEFORE)
    if len(current) != 60:
        raise SystemExit(f"M60_BEFORE has {len(current)} cards")
    if current.count("Max Potion"):
        raise SystemExit("baseline already contains Max Potion; greedy expects zero")

    print(f"baseline {GAMES} games x {len(FOES)} foes, seed {SEED}", flush=True)
    base_cells = _eval_lists([("baseline", current)])["baseline"]
    weights = loss_weights(base_cells)
    base_mean = _mean(base_cells)
    base_weighted = _weighted(base_cells, weights)
    array = [
        {
            "copies": 0,
            "cut": None,
            "cuts": [],
            "list": current,
            "weighted": base_weighted,
            "mean": base_mean,
            "worst": _worst(base_cells),
            "cells": {key: base_cells[key] for key, *_ in FOES},
        }
    ]
    print(
        f"baseline weighted {base_weighted:.1%}  mean {base_mean:.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )
    steps = []
    rejected = None

    while current.count("Max Potion") < 4:
        copies = Counter(current)
        cuts = sorted(name for name in copies if name != "Max Potion")
        lists = [(cut, swap_one(current, cut)) for cut in cuts]
        print(f"\nstep {current.count('Max Potion') + 1}: {len(lists)} cuts", flush=True)
        cells = _eval_lists(lists)
        rows = [_candidate_row(cut, cells[cut], copies, weights) for cut, _ in lists]
        best = rows[0]
        for row in rows[1:]:
            if _better(row, best):
                best = row
        rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"]))
        accepted = best["weighted"] > array[-1]["weighted"]
        step = {
            "copies_after": current.count("Max Potion") + 1,
            "current_weighted": array[-1]["weighted"],
            "current_mean": array[-1]["mean"],
            "accepted": accepted,
            "chosen": best["cut"],
            "chosen_weighted": best["weighted"],
            "chosen_mean": best["mean"],
            "candidates": rows,
        }
        steps.append(step)
        print(
            f"best cut {best['cut']} -> weighted {best['weighted']:.1%} "
            f"(mean {best['mean']:.1%}) ({'keep' if accepted else 'stop'})",
            flush=True,
        )
        if not accepted:
            rejected = {
                "cut": best["cut"],
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "cells": best["cells"],
            }
            break
        current = swap_one(current, best["cut"])
        array.append(
            {
                "copies": current.count("Max Potion"),
                "cut": best["cut"],
                "cuts": [row["cut"] for row in array[1:]] + [best["cut"]],
                "list": current,
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "max_potion": best["max_potion"],
                "cells": best["cells"],
            }
        )

    elapsed = time.perf_counter() - started
    final = array[-1]
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "method": (
            "greedy one-card Max Potion swap; score is the loss-weighted win rate "
            "with weights frozen from the 0-potion list; stop when that score does not rise"
        ),
        "foes": {key: strat for key, _label, _names, strat in FOES},
        "weights": weights,
        "copies": final["copies"],
        "cuts": [row["cut"] for row in array[1:]],
        "win_rate_array": [row["weighted"] for row in array],
        "equal_weight_array": [row["mean"] for row in array],
        "array": array,
        "steps": steps,
        "rejected": rejected,
        "list": final["list"],
    }
    dest = ROOT / "data/lab/set-m-max-potion.json"
    dest.write_text(json.dumps(report, indent=2))
    md = ROOT / "data/lab/set-m-max-potion.md"
    md.write_text(_markdown(report))
    print(f"\narray {[round(x, 4) for x in report['win_rate_array']]}")
    print(f"copies {report['copies']} cuts {report['cuts']}")
    print(f"elapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
