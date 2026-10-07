#!/usr/bin/env python3
"""Greedy Rescue Carrier swaps on the locked Manaphy Set M.

Start from the Manaphy snapshot below: one Manaphy, no Budew. Each step replaces exactly one
copy of one other card with one Rescue Carrier. The decision score is the
loss-weighted win rate. Weights are frozen from that starting list, including
Kudo's Mega Starmie. Stop when the next copy does not raise the score, or at 4.

Rescue Carrier (Evolving Skies 154): put up to 2 Pokémon, each with 90 HP or
less, from the discard pile into the hand. Mew ex is 160 and does not qualify.
A 30 HP baby does. Manaphy is 70 and does.

The 0-copy cells are the locked list from seed 20261007, 1000 games:
data/lab/set-m-manaphy-starmie.json, cut Budew.
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
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

# The study started here. SET_M60_NAMES now has the two copies this run kept.
BASELINE_NAMES = (
    ["Mew ex"] * 3
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Manaphy"]
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 2
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 3
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

# Published locked-list win rates. Seed 20261007, 1000 games.
BASELINE_RATES = {
    "t60": 0.897,
    "hedrick": 0.866,
    "c60": 0.868,
    "d60": 0.989,
    "thorns": 0.988,
    "starmie": 0.825,
}

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("thorns", "Iron Thorns ex (Crushing Thorn)", IRON_THORNS_NAMES, "thorns"),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie"),
)

GAMES = int(os.environ.get("M_CARRIER_GAMES", "1000"))
SEED = int(os.environ.get("M_CARRIER_SEED", "20261007"))
WORKERS = int(os.environ.get("M_CARRIER_WORKERS", "4"))
IN_NAME = "Rescue Carrier"
DEST = ROOT / "data/lab/set-m-rescue-carrier.json"
MD_DEST = ROOT / "data/lab/set-m-rescue-carrier.md"

QUERIES = [
    {"type": "event_prefix", "prefix": "rescue_carrier_a", "key": "carrier"},
]


def loss_weights(rates: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - rates[key]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Rescue Carrier would exceed 4")
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
    result = rec["results"]
    return cut, foe_key, {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "carrier": result["queries"].get("carrier", 0.0),
    }


def _eval_lists(lists: list[tuple[str, list[str]]], done: dict[str, dict[str, dict]], save) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {key: dict(done.get(key, {})) for key, _ in lists}
    jobs = [
        (key, names, foe_key, foe_names, foe_strat)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
        if foe_key not in cells[key]
    ]
    if not jobs:
        return cells
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        finished = len(lists) * len(FOES) - len(jobs)
        for fut in as_completed(futs):
            key, foe_key, detail = fut.result()
            cells[key][foe_key] = detail
            finished += 1
            save(cells)
            print(
                f"  {key} vs {foe_key}: {detail['a']:.1%}  carrier {detail['carrier']:.1%}  ({finished}/{len(lists) * len(FOES)})",
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
        "carrier": sum(ordered[key]["carrier"] for key, *_ in FOES) / len(FOES),
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


def _render_md(report: dict) -> str:
    weights = report["weights"]
    lines = [
        "# Set M greedy Rescue Carrier",
        "",
        "Starting 60 is the locked Manaphy list: one Manaphy, no Budew.",
        "Evolving Skies Rescue Carrier puts up to 2 Pokémon with 90 HP or less from the discard pile into the hand.",
        "Mew ex is 160 HP, so it stays in the discard. A 30 HP baby qualifies. Manaphy is 70 HP and qualifies.",
        "Night Stretcher remains the card that can take Mew ex.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per new cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 0-copy list.",
        "- **0-copy cells**: reused from the locked list, seed 20261007, 1000 games.",
        "- **Weights**: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Copies**: {report['copies']}",
        f"- **Cuts**: {', '.join(report['cuts']) or '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "| Carrier | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["array"]:
        cut = row["cut"] or "—"
        cells = row["cells"]
        lines.append(
            f"| {row['copies']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | {cut} | "
            f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | "
            f"{_cell(cells, 'd60')} | {_cell(cells, 'thorns')} | {_cell(cells, 'starmie')} |"
        )
    for step in report["steps"]:
        lines.extend(
            [
                "",
                f"## Step {step['copies_after']}, every cut",
                "",
                f"Current weighted rate {_pct(step['current_weighted'])}. "
                + (
                    f"Accepted cut is {step['chosen']}."
                    if step["accepted"]
                    else f"Best cut is not taken: {step['chosen']}."
                ),
                "",
                "| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Carrier played |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step["candidates"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | "
                f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | "
                f"{_cell(cells, 'd60')} | {_cell(cells, 'thorns')} | {_cell(cells, 'starmie')} | "
                f"{_pct(row['carrier'])} |"
            )
    if report.get("note"):
        lines.extend(["", report["note"]])
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_render_md(report))


def _baseline_cells() -> dict[str, dict]:
    return {key: {"a": BASELINE_RATES[key], "carrier": 0.0} for key, *_ in FOES}


def _load() -> dict | None:
    if not DEST.exists():
        return None
    data = json.loads(DEST.read_text())
    if data.get("games") != GAMES or data.get("seed") != SEED:
        return None
    return data


def main() -> None:
    started = time.perf_counter()
    current = list(BASELINE_NAMES)
    if len(current) != 60:
        raise SystemExit(f"baseline has {len(current)} cards")
    if current.count("Manaphy") != 1 or current.count("Budew") or current.count(IN_NAME):
        raise SystemExit("baseline is not the locked one-Manaphy list")

    weights = loss_weights(BASELINE_RATES)
    base_cells = _baseline_cells()
    base_weighted = _weighted(base_cells, weights)
    saved = _load()
    if saved and saved.get("list_start") == current:
        array = saved["array"]
        steps = saved["steps"]
        pending = saved.get("pending") or {}
        current = list(saved["list"])
        print(f"resume copies={current.count(IN_NAME)} steps={len(steps)}", flush=True)
    else:
        array = [
            {
                "copies": 0,
                "cut": None,
                "cuts": [],
                "list": current,
                "weighted": base_weighted,
                "mean": _mean(base_cells),
                "worst": _worst(base_cells),
                "cells": base_cells,
            }
        ]
        steps = []
        pending = {}
    print(
        f"baseline weighted {base_weighted:.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )

    def report_from(done: bool, rejected, pending_cells) -> dict:
        return {
            "games": GAMES,
            "seed": SEED,
            "elapsed": time.perf_counter() - started + float((saved or {}).get("elapsed") or 0),
            "rule_preset": "s60",
            "method": (
                "greedy one-card Rescue Carrier swap from the locked Manaphy Set M; "
                "printed effect returns up to 2 Pokémon with 90 HP or less; "
                "foes are T60, Hedrick, C60, D60, Crushing Thorn, and Kudo Mega Starmie; "
                "score is the loss-weighted win rate with weights frozen from the 0-copy list; "
                "stop when that score does not rise, or at 4 copies"
            ),
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "copies": current.count(IN_NAME),
            "cuts": [row["cut"] for row in array[1:]],
            "win_rate_array": [row["weighted"] for row in array],
            "array": array,
            "steps": steps,
            "rejected": rejected,
            "list_start": list(BASELINE_NAMES),
            "list": current,
            "pending": pending_cells,
            "done": done,
            "note": None,
        }

    rejected = (saved or {}).get("rejected")
    if (saved or {}).get("done"):
        print("already done")
        print(f"copies {(saved or {})['copies']} cuts {(saved or {})['cuts']}")
        return

    while current.count(IN_NAME) < 4:
        copies = Counter(current)
        cuts = sorted(name for name in copies if name != IN_NAME)
        lists = [(cut, swap_one(current, cut)) for cut in cuts]
        step_key = f"{current.count(IN_NAME) + 1}:" + ",".join(cuts)
        done_cells = pending.get("cells") or {} if pending.get("key") == step_key else {}
        print(f"\nstep {current.count(IN_NAME) + 1}: {len(lists)} cuts, {len(done_cells)} already stored", flush=True)

        def save(cells: dict) -> None:
            pending_now = {"key": step_key, "cells": cells}
            _write(report_from(False, rejected, pending_now))

        cells = _eval_lists(lists, done_cells, save)
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
        pending = {}
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
                "candidates": rows,
            }
            report = report_from(True, rejected, {})
            report["note"] = (
                f"Stopped at {current.count(IN_NAME)} Rescue Carrier. "
                f"The next copy, cutting {best['cut']}, is {best['weighted']:.2%} "
                f"against the current {array[-1]['weighted']:.2%}."
            )
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
                "carrier": best["carrier"],
                "cells": best["cells"],
            }
        )
        report = report_from(current.count(IN_NAME) >= 4, None, {})
        if current.count(IN_NAME) >= 4:
            report["note"] = "The weighted score was still rising at 4 copies. A fifth Rescue Carrier is not legal."
        _write(report)

    final = _load()
    print(f"\narray {[round(x, 4) for x in final['win_rate_array']]}")
    print(f"copies {final['copies']} cuts {final['cuts']}")
    print(f"elapsed {final['elapsed']:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
