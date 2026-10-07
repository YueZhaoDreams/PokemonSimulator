#!/usr/bin/env python3
"""One Manaphy swap for the locked Set M.

Start from SET_M60_NAMES. Each candidate replaces exactly one copy of one
other card with one Manaphy. The decision score is the loss-weighted win
rate. Weights are frozen from the current list, which has no Manaphy.

Manaphy Wave Veil prevents attack damage to the Bench. The baby strategy
benches it only when an opposing attack can do that damage (Fezandipiti ex
Cruel Arrow on the Dragapult lists). Battle Cage still stops damage counters.
Penny or one Energy gets Manaphy off the Active Spot.

Foes: T60, Hedrick, C60, D60, and the Worlds 2024 Crushing Thorn list.
Seed 20261007. 1000 games per cell.
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
    SET_M60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("thorns", "Iron Thorns ex (Crushing Thorn)", IRON_THORNS_NAMES, "thorns"),
)

# Cruel Arrow is the bench-damage attack on these two lists. The others are not.
DAMAGE_FOES = {"t60", "hedrick"}

GAMES = int(os.environ.get("M_MANAPHY_GAMES", "1000"))
SEED = int(os.environ.get("M_MANAPHY_SEED", "20261007"))
WORKERS = int(os.environ.get("M_MANAPHY_WORKERS", "4"))
IN_NAME = "Manaphy"

QUERIES = [
    {"type": "event_prefix", "prefix": "saw_play:Manaphy", "key": "manaphy"},
    {"type": "event_prefix", "prefix": "wave_veil", "key": "wave_veil"},
]
DEST = ROOT / "data/lab/set-m-manaphy.json"
MD_DEST = ROOT / "data/lab/set-m-manaphy.md"


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
        raise ValueError("Manaphy would exceed 4")
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
        "manaphy": r["queries"].get("manaphy", 0.0),
        "wave_veil": r["queries"].get("wave_veil", 0.0),
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
                f"manaphy {detail['manaphy']:.2f}  veil {detail['wave_veil']:.2f}  "
                f"({done}/{len(jobs)})",
                flush=True,
            )
    for key, _ in lists:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _candidate_row(cut: str, cells: dict[str, dict], copies: Counter, weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    damage = [ordered[key] for key in DAMAGE_FOES]
    return {
        "cut": cut,
        "copies_before": copies[cut],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "manaphy": sum(ordered[key]["manaphy"] for key, *_ in FOES) / len(FOES),
        "wave_veil": sum(row["wave_veil"] for row in damage) / len(damage),
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
    base = report["baseline"]
    lines = [
        "# Set M one Manaphy",
        "",
        "Starting 60 is the locked Set M list (`SET_M60_NAMES`), which has no Manaphy.",
        "Each row replaces one copy of that card with one Manaphy.",
        "Wave Veil prevents attack damage done to the Bench. On these foes that attack is "
        "Fezandipiti ex Cruel Arrow, on T60 and Hedrick. C60, D60, and Crushing Thorn have none, "
        "so Manaphy stays in hand there. Battle Cage still stops damage counters.",
        "If Manaphy is Active, Penny puts that Basic and all attached cards into the hand, "
        "or one Energy retreats it onto the Bench.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the current list.",
        "- **Weights**: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Baseline weighted**: {_pct(base['weighted'])}",
        f"- **Best cut**: {report['best_cut']}",
        f"- **Worth swapping**: {report['worth_swapping']}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "| Rank | Cut | Weighted | Delta | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | Manaphy in play | Veil vs Dive lists |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    lines.append(
        f"| 0 | (none) | {_pct(base['weighted'])} | — | {_pct(base['mean'])} | "
        f"{_cell(base['cells'], 't60')} | {_cell(base['cells'], 'hedrick')} | "
        f"{_cell(base['cells'], 'c60')} | {_cell(base['cells'], 'd60')} | "
        f"{_cell(base['cells'], 'thorns')} | — | — |"
    )
    for rank, row in enumerate(report["candidates"], start=1):
        cells = row["cells"]
        delta = row["weighted"] - base["weighted"]
        lines.append(
            f"| {rank} | {row['cut']} | {_pct(row['weighted'])} | {delta:+.1%} | {_pct(row['mean'])} | "
            f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | "
            f"{_cell(cells, 'd60')} | {_cell(cells, 'thorns')} | {row['manaphy']:.2f} | {row['wave_veil']:.2f} |"
        )
    if report.get("note"):
        lines.extend(["", report["note"]])
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_render_md(report))
    print(f"wrote {DEST}", flush=True)


def main() -> None:
    started = time.perf_counter()
    current = list(SET_M60_NAMES)
    if len(current) != 60:
        raise SystemExit(f"SET_M60_NAMES has {len(current)} cards")
    if current.count(IN_NAME):
        raise SystemExit("baseline already contains Manaphy")
    copies = Counter(current)
    cuts = sorted(copies)
    print(f"baseline {GAMES} games x {len(FOES)} foes, seed {SEED}, {len(cuts)} cuts", flush=True)
    base_cells = _eval_lists([("baseline", current)])["baseline"]
    weights = loss_weights(base_cells)
    base_weighted = _weighted(base_cells, weights)
    baseline = {
        "weighted": base_weighted,
        "mean": _mean(base_cells),
        "worst": _worst(base_cells),
        "cells": {key: base_cells[key] for key, *_ in FOES},
    }
    print(
        f"baseline weighted {base_weighted:.1%}  mean {baseline['mean']:.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": time.perf_counter() - started,
        "rule_preset": "s60",
        "method": (
            "one-card Manaphy swap from locked SET_M60_NAMES; "
            "Wave Veil benches only against attack damage to the Bench; "
            "foes are T60, Hedrick, C60, D60, and Crushing Thorn; "
            "score is the loss-weighted win rate with weights frozen from that list"
        ),
        "foes": {key: strat for key, _label, _names, strat in FOES},
        "damage_foes": sorted(DAMAGE_FOES),
        "weights": weights,
        "baseline": baseline,
        "best_cut": None,
        "worth_swapping": False,
        "candidates": [],
        "list": current,
        "done": False,
    }
    _write(report)

    lists = [(cut, swap_one(current, cut)) for cut in cuts]
    print(f"\n{len(lists)} cuts", flush=True)
    cells = _eval_lists(lists)
    rows = [_candidate_row(cut, cells[cut], copies, weights) for cut, _ in lists]
    rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"]))
    best = rows[0]
    worth = best["weighted"] > baseline["weighted"]
    report["candidates"] = rows
    report["best_cut"] = best["cut"]
    report["worth_swapping"] = worth
    report["best"] = {
        "cut": best["cut"],
        "weighted": best["weighted"],
        "mean": best["mean"],
        "worst": best["worst"],
        "delta": best["weighted"] - baseline["weighted"],
        "cells": best["cells"],
    }
    report["elapsed"] = time.perf_counter() - started
    report["done"] = True
    if worth:
        report["note"] = (
            f"Cut one {best['cut']} for Manaphy. "
            f"Weighted {baseline['weighted']:.1%} → {best['weighted']:.1%}."
        )
    else:
        report["note"] = (
            f"No cut raises the weighted score. Best is {best['cut']} at "
            f"{best['weighted']:.1%} against the baseline {baseline['weighted']:.1%}."
        )
    _write(report)
    print(report["note"])
    print(f"elapsed {report['elapsed']:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
