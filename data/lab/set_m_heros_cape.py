#!/usr/bin/env python3
"""One Hero's Cape in the locked 4-Max-Potion Set M.

Hero's Cape is an ACE SPEC, so the search adds exactly one copy. Each trial
replaces one card. The decision score is the loss-weighted win rate, with
weights frozen from this list before the cape (how often that list loses
each matchup).

Foes: T60, Hedrick, C60, D60. Same seed and game count as the potion search.
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
from data.lab.set_m_max_potion import FOES, loss_weights

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("M_CAPE_GAMES", "1000"))
SEED = int(os.environ.get("M_CAPE_SEED", "20260929"))
WORKERS = int(os.environ.get("M_CAPE_WORKERS", "4"))

# Locked 4 Max Potion list, in the order the potion search actually shuffled.
# Max Potion was appended by each swap, so those four copies sit at the end.
M60_POTION = (
    ["Mew ex"] * 4
    + ["Mime Jr."] * 2
    + ["Igglybuff"] * 4
    + ["Budew"] * 3
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 4
    + ["Ultra Ball"] * 3
    + ["Night Stretcher"] * 4
    + ["Battle Cage"] * 4
    + ["Bravery Charm"] * 4
    + ["Arven"] * 4
    + ["Iono"] * 4
    + ["Professor's Research"] * 2
    + ["Boss's Orders"] * 3
    + ["Crushing Hammer"] * 4
    + ["Switch"]
    + ["Counter Catcher"] * 2
    + ["Max Potion"] * 4
)

QUERIES = [
    {"type": "event_prefix", "prefix": "tool:Hero's Cape", "key": "cape"},
    {"type": "event_prefix", "prefix": "max_potion", "key": "max_potion"},
]


def swap_cape(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append("Hero's Cape")
    if len(out) != 60 or out.count("Hero's Cape") != 1:
        raise ValueError(f"{cut} swap is not one Hero's Cape in 60 cards")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


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
        "cape": r["queries"].get("cape", 0.0),
        "max_potion": r["queries"].get("max_potion", 0.0),
    }


def _eval(lists: list[tuple[str, list[str]]]) -> dict[str, dict[str, dict]]:
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
                f"  {key} vs {foe_key}: {detail['a']:.1%}  cape {detail['cape']:.1%}  ({done}/{len(jobs)})",
                flush=True,
            )
    return cells


def _markdown(report: dict) -> str:
    lines = [
        "# Set M: one Hero's Cape",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 4-Max-Potion list, before the cape.",
        f"- **Weights**: {', '.join(f'{key} {report['weights'][key]:.1%}' for key, *_ in FOES)}",
        f"- **Cut**: {report['cut'] or '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Hero's Cape is an ACE SPEC, so every row is exactly one copy. The lock is the 4 Max Potion list.",
        "",
        "| Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | Cape played |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["ranking"]:
        cells = row["cells"]
        name = "lock" if row["cut"] is None else row["cut"]
        lines.append(
            f"| {name} | {row['weighted']:.1%} | {row['mean']:.1%} | "
            f"{cells['t60']['a']:.1%} | {cells['hedrick']['a']:.1%} | "
            f"{cells['c60']['a']:.1%} | {cells['d60']['a']:.1%} | {row['cape']:.0%} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    base = list(M60_POTION)
    if len(base) != 60 or base.count("Hero's Cape") or base.count("Max Potion") != 4:
        raise SystemExit("M60_POTION is not the locked 4-potion list")
    print(f"baseline {GAMES} games, seed {SEED}", flush=True)
    base_cells = _eval([("lock", base)])["lock"]
    weights = loss_weights(base_cells)
    print(
        "weights " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        flush=True,
    )
    cuts = sorted(Counter(base))
    print(f"\n{len(cuts)} one-card cuts", flush=True)
    cells = _eval([(cut, swap_cape(base, cut)) for cut in cuts])
    rows = []
    for cut in cuts:
        ordered = {key: cells[cut][key] for key, *_ in FOES}
        rows.append(
            {
                "cut": cut,
                "copies_before": base.count(cut),
                "weighted": _weighted(ordered, weights),
                "mean": _mean(ordered),
                "cape": sum(ordered[key]["cape"] for key, *_ in FOES) / len(FOES),
                "cells": ordered,
            }
        )
    rows.sort(key=lambda row: (-row["weighted"], -row["mean"], -row["copies_before"], row["cut"]))
    lock = {
        "cut": None,
        "weighted": _weighted(base_cells, weights),
        "mean": _mean(base_cells),
        "cape": 0.0,
        "cells": {key: base_cells[key] for key, *_ in FOES},
    }
    best = rows[0]
    chosen = best["cut"] if best["weighted"] > lock["weighted"] else None
    ranking = [lock, *rows]
    ranking.sort(key=lambda row: (-row["weighted"], -row["mean"], row["cut"] or ""))
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": time.perf_counter() - started,
        "method": "one Hero's Cape; loss-weighted win rate frozen on the 4-Max-Potion list",
        "weights": weights,
        "cut": chosen,
        "lock_weighted": lock["weighted"],
        "best_cut": best["cut"],
        "best_weighted": best["weighted"],
        "ranking": ranking,
        "list": swap_cape(base, chosen) if chosen else base,
    }
    dest = ROOT / "data/lab/set-m-heros-cape.json"
    dest.write_text(json.dumps(report, indent=2) + "\n")
    md = ROOT / "data/lab/set-m-heros-cape.md"
    md.write_text(_markdown(report))
    print(f"\nlock {lock['weighted']:.1%}  best {best['cut']} {best['weighted']:.1%}")
    print(f"cut {chosen}")
    print(f"elapsed {report['elapsed']:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
