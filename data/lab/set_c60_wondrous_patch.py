#!/usr/bin/env python3
"""Greedy Wondrous Patch swaps for the locked C60 list.

The live lock is one Wondrous Patch, cutting one Boss's Orders. Clefable CLC
stays. This search starts from the previous list (``c60_names_before_patch``:
zero Wondrous Patch). Each step replaces
exactly one copy of one other card with one Wondrous Patch. The decision
score is the loss-weighted win rate. Weights are frozen from that starting
list. Stop when the next swap does not raise that score, or at 4 copies.

The party line this card is scored with: on a later turn the Active Clefairy
already has one Energy, attaches one more, and retreats, discarding those two.
A Benched Clefairy with two Psychic Energy comes up, uses Moon-Watching Party,
and Wonder Storm hits for 20 per Psychic Energy in play (at least 80 when one
other Clefairy is there). Printed Wondrous Patch attaches one Basic Psychic
Energy from the discard to a Benched Psychic Pokémon, which is how the third
Energy lands when the attacker still needs it, and how a later copy fuels
Clefable ex or Mega Clefable ex.

Foes: T60, Hedrick, Unlimited Dragapult, D60, S60, and G.
Seed 20261002. Games per cell from C60_PATCH_GAMES (default 1000).
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

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    c60_names_before_patch,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "phantom"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "slash"),
    ("g", "Gholdengo (G)", SET_G_NAMES, "g"),
)

IN_NAME = "Wondrous Patch"
GAMES = int(os.environ.get("C60_PATCH_GAMES", "1000"))
SEED = int(os.environ.get("C60_PATCH_SEED", "20261002"))
WORKERS = int(os.environ.get("C60_PATCH_WORKERS", str(min(8, os.cpu_count() or 4))))
QUERIES = [
    {"type": "event_prefix", "prefix": "wondrous_patch", "key": "patch"},
    {"type": "event_prefix", "prefix": "patch_storm", "key": "storm"},
]
DEST = ROOT / "data/lab/set-c60-wondrous-patch.json"
MD_DEST = ROOT / "data/lab/set-c60-wondrous-patch.md"


def loss_weights(baseline: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Wondrous Patch would exceed 4")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"{cut} swap is illegal: {bad}")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def _run(cut: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(list(names)),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": cut or "baseline", "name": cut or "baseline"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    return cut, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "patch": r["queries"].get("patch", 0.0),
        "storm": r["queries"].get("storm", 0.0),
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
                f"  {key} vs {foe_key}: {detail['a']:.1%}  "
                f"patch {detail['patch']:.2f} storm {detail['storm']:.2f}  ({done}/{len(jobs)})",
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
        "patch": sum(ordered[key]["patch"] for key, *_ in FOES) / len(FOES),
        "storm": sum(ordered[key]["storm"] for key, *_ in FOES) / len(FOES),
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


def _markdown(report: dict) -> str:
    lines = [
        "# C60 greedy Wondrous Patch",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 0-Patch list.",
        f"- **Weights**: {', '.join(f'{key} {report['weights'][key]:.1%}' for key, *_ in FOES)}",
        f"- **Copies**: {report['copies']}",
        f"- **Cuts**: {', '.join(report['cuts']) if report['cuts'] else '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Printed text: Attach a Basic Psychic Energy card from your discard pile to 1 of "
        "your Benched Psychic Pokémon.",
        "",
        "Turn 2, when the Active Clefairy already has one Energy: attach one more, retreat, "
        "and discard those two. The Benched Clefairy that has two Psychic Energy comes up "
        "and uses Moon-Watching Party. Wonder Storm is 20 for each Psychic Energy on your "
        "Pokémon, so one other Clefairy is 80 and more Clefairies add more. The Patch is "
        "played while its target is still Benched. If the discard is empty, those two "
        "discarded Energy are the fuel: retreat into a different Bench Pokémon, Patch, "
        "then Switch the fueled Clefairy Active. Later copies can fuel Clefable ex or "
        "Mega Clefable ex.",
        "",
        "## Weighted win-rate array",
        "",
        "| Patch | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs UNL | vs D60 | vs S60 | vs G |",
        "| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["array"]:
        cells = row["cells"]
        cut = row["cut"] or "—"
        lines.append(
            f"| {row['copies']} | {row['weighted']:.1%} | {row['mean']:.1%} | {cut} | "
            f"{cells['t60']['a']:.1%} | {cells['hedrick']['a']:.1%} | {cells['unl']['a']:.1%} | "
            f"{cells['d60']['a']:.1%} | {cells['s60']['a']:.1%} | {cells['g']['a']:.1%} |"
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
        lines.extend(["", "The weighted score was still rising at 4 copies. A fifth Patch is not legal.", ""])
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))


def main() -> None:
    started = time.perf_counter()
    current = c60_names_before_patch()
    if len(current) != 60:
        raise SystemExit(f"pre-Patch C60 has {len(current)} cards")
    if current.count(IN_NAME):
        raise SystemExit("baseline already contains Wondrous Patch; greedy expects zero")

    print(f"baseline {GAMES} games x {len(FOES)} foes, seed {SEED}", flush=True)
    base_cells = _eval_lists([("baseline", current)])["baseline"]
    weights = loss_weights(base_cells)
    array = [
        {
            "copies": 0,
            "cut": None,
            "cuts": [],
            "list": current,
            "weighted": _weighted(base_cells, weights),
            "mean": _mean(base_cells),
            "worst": _worst(base_cells),
            "cells": {key: base_cells[key] for key, *_ in FOES},
        }
    ]
    print(
        f"baseline weighted {array[-1]['weighted']:.1%}  mean {array[-1]['mean']:.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )
    steps = []
    rejected = None
    while current.count(IN_NAME) < 4:
        copies = Counter(current)
        cuts = sorted(name for name in copies if name != IN_NAME)
        lists = [(cut, swap_one(current, cut)) for cut in cuts]
        print(f"\nstep {current.count(IN_NAME) + 1}: {len(lists)} cuts", flush=True)
        cells = _eval_lists(lists)
        rows = [_candidate_row(cut, cells[cut], copies, weights) for cut, _ in lists]
        best = rows[0]
        for row in rows[1:]:
            if _better(row, best):
                best = row
        rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"]))
        accepted = best["weighted"] > array[-1]["weighted"]
        steps.append(
            {
                "copies_after": current.count(IN_NAME) + 1,
                "current_weighted": array[-1]["weighted"],
                "current_mean": array[-1]["mean"],
                "accepted": accepted,
                "chosen": best["cut"],
                "chosen_weighted": best["weighted"],
                "chosen_mean": best["mean"],
                "candidates": rows,
            }
        )
        print(
            f"best cut {best['cut']} -> weighted {best['weighted']:.1%} "
            f"(mean {best['mean']:.1%}, storm {best['storm']:.2f}) "
            f"({'keep' if accepted else 'stop'})",
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
                "copies": current.count(IN_NAME),
                "cut": best["cut"],
                "cuts": [row["cut"] for row in array[1:]] + [best["cut"]],
                "list": current,
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "patch": best["patch"],
                "storm": best["storm"],
                "cells": best["cells"],
            }
        )
        elapsed = time.perf_counter() - started
        _write(
            {
                "games": GAMES,
                "seed": SEED,
                "elapsed": elapsed,
                "rule_preset": "s60",
                "method": (
                    "greedy one-card Wondrous Patch swap from locked C60; "
                    "score is the loss-weighted win rate with weights frozen from the 0-Patch list; "
                    "stop when that score does not rise, or at 4 copies"
                ),
                "printed": (
                    "Attach a Basic Psychic Energy card from your discard pile to 1 of your "
                    "Benched Psychic Pokémon."
                ),
                "catalog_id": "me02-094",
                "foes": {key: strat for key, _label, _names, strat in FOES},
                "weights": weights,
                "copies": array[-1]["copies"],
                "cuts": [row["cut"] for row in array[1:]],
                "win_rate_array": [row["weighted"] for row in array],
                "equal_weight_array": [row["mean"] for row in array],
                "array": array,
                "steps": steps,
                "rejected": rejected,
                "list": array[-1]["list"],
                "partial": True,
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
            "greedy one-card Wondrous Patch swap from locked C60; "
            "score is the loss-weighted win rate with weights frozen from the 0-Patch list; "
            "stop when that score does not rise, or at 4 copies"
        ),
        "printed": (
            "Attach a Basic Psychic Energy card from your discard pile to 1 of your "
            "Benched Psychic Pokémon."
        ),
        "catalog_id": "me02-094",
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
        "partial": False,
    }
    _write(report)
    print(f"\narray {[round(x, 4) for x in report['win_rate_array']]}")
    print(f"copies {report['copies']} cuts {report['cuts']}")
    print(f"elapsed {elapsed:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
