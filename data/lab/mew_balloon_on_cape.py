#!/usr/bin/env python3
"""Greedy Bursting Balloon swaps for the current Set M.

Start from M60_BEFORE (Hero's Cape, four Max Potion, two Budew, three Ultra Ball). Each step
replaces exactly one copy of one other card with one Bursting Balloon. The
decision score is the loss-weighted win rate. Weights are frozen from that
starting list. Stop when the next swap does not raise that score, or at 4 copies.

Foes and the weight formula match data/lab/set_m_max_potion.py:
T60, Hedrick, C60, D60. Seed 20260929. 1000 games per cell.
"""

from __future__ import annotations

import importlib.util
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
from app.seed_data import build_fallback_deck

# Cape / four Max Potion Set M, before this balloon search. SET_M60_NAMES is the locked 1-balloon list.
M60_BEFORE = (
    ["Mew ex"] * 4
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Budew"] * 2
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 3
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 4
    + ["Hero's Cape"]
    + ["Max Potion"] * 4
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Professor's Research"] * 2
    + ["Boss's Orders"] * 3
    + ["Crushing Hammer"] * 4
    + ["Switch"]
    + ["Counter Catcher"] * 2
)

_potion_path = Path(__file__).with_name("set_m_max_potion.py")
_spec = importlib.util.spec_from_file_location("set_m_max_potion", _potion_path)
_potion = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_potion)
FOES = _potion.FOES
loss_weights = _potion.loss_weights

GAMES = int(os.environ.get("M_BALLOON_GAMES", os.environ.get("M_POTION_GAMES", "1000")))
SEED = int(os.environ.get("M_BALLOON_SEED", os.environ.get("M_POTION_SEED", "20260929")))
WORKERS = int(os.environ.get("M_BALLOON_WORKERS", os.environ.get("M_POTION_WORKERS", "4")))
IN_NAME = "Bursting Balloon"

QUERIES = [{"type": "event_prefix", "prefix": "bursting_balloon", "key": "bursting_balloon"}]
DEST = ROOT / "data/lab/mew_balloon_on_cape.json"


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Bursting Balloon would exceed 4")
    if out.count("Hero's Cape") > 1:
        raise ValueError("a second Hero's Cape is not legal")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


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
        "bursting_balloon": r["queries"].get("bursting_balloon", 0.0),
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
                f"  {key} vs {foe_key}: {detail['a']:.1%}  balloon {detail['bursting_balloon']:.1%}  ({done}/{len(jobs)})",
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
        "bursting_balloon": sum(ordered[key]["bursting_balloon"] for key, *_ in FOES) / len(FOES),
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


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2))
    print(f"wrote {DEST}", flush=True)


def main() -> None:
    started = time.perf_counter()
    current = list(M60_BEFORE)
    if len(current) != 60:
        raise SystemExit(f"M60_BEFORE has {len(current)} cards")
    if current.count(IN_NAME):
        raise SystemExit("baseline already contains Bursting Balloon")
    if current.count("Hero's Cape") != 1 or current.count("Max Potion") != 4:
        raise SystemExit("baseline is not the cape / four Max Potion list")
    if current.count("Maximum Belt"):
        raise SystemExit("baseline still contains Maximum Belt")

    print(f"baseline {GAMES} games x {len(FOES)} foes, seed {SEED}", flush=True)
    base_cells = _eval_lists([("baseline", current)])["baseline"]
    weights = loss_weights(base_cells)
    base_weighted = _weighted(base_cells, weights)
    array = [
        {
            "copies": 0,
            "cut": None,
            "cuts": [],
            "list": current,
            "weighted": base_weighted,
            "mean": _mean(base_cells),
            "worst": _worst(base_cells),
            "cells": {key: base_cells[key] for key, *_ in FOES},
        }
    ]
    print(
        f"baseline weighted {base_weighted:.1%}  mean {array[0]['mean']:.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )
    steps: list[dict] = []
    rejected = None
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": 0.0,
        "rule_preset": "s60",
        "method": (
            "greedy one-card Bursting Balloon swap from the Hero's Cape / four Max Potion Set M; "
            "score is the loss-weighted win rate with weights frozen from that list; "
            "stop when that score does not rise, or at 4 copies"
        ),
        "foes": {key: strat for key, _label, _names, strat in FOES},
        "weights": weights,
        "copies": 0,
        "cuts": [],
        "win_rate_array": [base_weighted],
        "array": array,
        "steps": steps,
        "rejected": None,
        "list": current,
        "done": False,
    }
    _write(report)

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
        step = {
            "copies_after": current.count(IN_NAME) + 1,
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
        report["steps"] = steps
        report["elapsed"] = time.perf_counter() - started
        if not accepted:
            rejected = {
                "cut": best["cut"],
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "cells": best["cells"],
                "candidates": rows,
            }
            report["rejected"] = rejected
            report["done"] = True
            _write(report)
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
                "bursting_balloon": best["bursting_balloon"],
                "cells": best["cells"],
            }
        )
        report["copies"] = current.count(IN_NAME)
        report["cuts"] = [row["cut"] for row in array[1:]]
        report["win_rate_array"] = [row["weighted"] for row in array]
        report["array"] = array
        report["list"] = current
        report["elapsed"] = time.perf_counter() - started
        report["done"] = current.count(IN_NAME) >= 4
        _write(report)

    if rejected is None and current.count(IN_NAME) >= 4:
        report["done"] = True
        report["note"] = "The weighted score was still rising at 4 copies. A fifth Bursting Balloon is not legal."
        report["elapsed"] = time.perf_counter() - started
        _write(report)

    print(f"\narray {[round(x, 4) for x in report['win_rate_array']]}")
    print(f"copies {report['copies']} cuts {report['cuts']}")
    print(f"elapsed {report['elapsed']:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
