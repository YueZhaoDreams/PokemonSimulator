#!/usr/bin/env python3
"""One Poké Vital A on the 4-Max-Potion Set M, before Hero's Cape.

Poké Vital A is an ACE SPEC, so the search adds exactly one copy. Each trial
replaces one card. The decision score is the loss-weighted win rate, with the
same weights as the cape search: frozen from this list before either ACE SPEC.

Foes: T60, Hedrick, C60, D60. Same seed and game count as the cape search.
This script does not change SET_M60_NAMES.
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
from app.seed_data import build_fallback_deck
from data.lab.set_m_heros_cape import M60_POTION
from data.lab.set_m_max_potion import FOES, loss_weights

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("M_VITAL_GAMES", "1000"))
SEED = int(os.environ.get("M_VITAL_SEED", "20260929"))
WORKERS = int(os.environ.get("M_VITAL_WORKERS", "4"))

# The 4-potion lock cell from the potion report. A miss means this engine change
# moved games that do not contain Poké Vital A.
LOCK_WIN = {"t60": 0.888, "hedrick": 0.831, "c60": 0.863, "d60": 0.978}

QUERIES = [
    {"type": "event_prefix", "prefix": "poke_vital_a", "key": "vital"},
    {"type": "event_prefix", "prefix": "max_potion", "key": "max_potion"},
]


def swap_vital(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append("Poké Vital A")
    if (
        len(out) != 60
        or out.count("Poké Vital A") != 1
        or out.count("Hero's Cape")
        or out.count("Survival Brace")
    ):
        raise ValueError(f"{cut} swap is not one Poké Vital A in the no-cape 60")
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
        "vital": r["queries"].get("vital", 0.0),
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
                f"  {key} vs {foe_key}: {detail['a']:.1%}  vital {detail['vital']:.1%}  "
                f"potion {detail['max_potion']:.1%}  ({done}/{len(jobs)})",
                flush=True,
            )
    return cells


def _markdown(report: dict) -> str:
    cape = report.get("cape") or {}
    lines = [
        "# Set M: one Poké Vital A",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 4-Max-Potion list, before either ACE SPEC.",
        f"- **Weights**: {', '.join(f'{key} {report['weights'][key]:.1%}' for key, *_ in FOES)}",
        f"- **Cut**: {report['cut'] or '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Poké Vital A is an ACE SPEC, so every row is exactly one copy. The list is the 4 Max Potion deck, with no Hero's Cape.",
        "The lock cell matches the potion report at this seed: T60 88.8%, Hedrick 83.1%, C60 86.3%, D60 97.8%.",
        "SET_M60_NAMES is unchanged. This search only reports the rate.",
        "",
    ]
    if cape:
        lines.append(
            f"Hero's Cape on this same list, best cut {cape.get('best_cut')} at {cape.get('best_weighted', 0):.1%} weighted."
        )
        lines.append("")
    lines.extend(
        [
            "| Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | Vital played | Max Potion |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["ranking"]:
        cells = row["cells"]
        name = "lock" if row["cut"] is None else row["cut"]
        lines.append(
            f"| {name} | {row['weighted']:.1%} | {row['mean']:.1%} | "
            f"{cells['t60']['a']:.1%} | {cells['hedrick']['a']:.1%} | "
            f"{cells['c60']['a']:.1%} | {cells['d60']['a']:.1%} | "
            f"{row['vital']:.0%} | {row['max_potion']:.0%} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    base = list(M60_POTION)
    if (
        len(base) != 60
        or base.count("Hero's Cape")
        or base.count("Survival Brace")
        or base.count("Poké Vital A")
        or base.count("Max Potion") != 4
        or base.count("Budew") != 3
    ):
        raise SystemExit("M60_POTION is not the no-cape 4-potion list")
    print(f"baseline {GAMES} games, seed {SEED}", flush=True)
    base_cells = _eval([("lock", base)])["lock"]
    for key, wr in LOCK_WIN.items():
        got = base_cells[key]["a"]
        if abs(got - wr) > 1e-9:
            raise SystemExit(f"lock vs {key} is {got:.3f}, expected {wr:.3f}")
    weights = loss_weights(base_cells)
    print(
        "weights " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        flush=True,
    )
    cuts = sorted(Counter(base))
    print(f"\n{len(cuts)} one-card cuts", flush=True)
    cells = _eval([(cut, swap_vital(base, cut)) for cut in cuts])
    rows = []
    for cut in cuts:
        ordered = {key: cells[cut][key] for key, *_ in FOES}
        rows.append(
            {
                "cut": cut,
                "copies_before": base.count(cut),
                "weighted": _weighted(ordered, weights),
                "mean": _mean(ordered),
                "vital": sum(ordered[key]["vital"] for key, *_ in FOES) / len(FOES),
                "max_potion": sum(ordered[key]["max_potion"] for key, *_ in FOES) / len(FOES),
                "cells": ordered,
            }
        )
    rows.sort(key=lambda row: (-row["weighted"], -row["mean"], -row["copies_before"], row["cut"]))
    lock = {
        "cut": None,
        "weighted": _weighted(base_cells, weights),
        "mean": _mean(base_cells),
        "vital": 0.0,
        "max_potion": sum(base_cells[key]["max_potion"] for key, *_ in FOES) / len(FOES),
        "cells": {key: base_cells[key] for key, *_ in FOES},
    }
    best = rows[0]
    chosen = best["cut"] if best["weighted"] > lock["weighted"] else None
    ranking = [lock, *rows]
    ranking.sort(key=lambda row: (-row["weighted"], -row["mean"], row["cut"] or ""))
    cape_path = ROOT / "data/lab/set-m-heros-cape.json"
    cape = json.loads(cape_path.read_text()) if cape_path.exists() else {}
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": time.perf_counter() - started,
        "method": "one Poké Vital A on the no-cape list; loss-weighted win rate frozen on the 4-Max-Potion list",
        "weights": weights,
        "cut": chosen,
        "lock_weighted": lock["weighted"],
        "best_cut": best["cut"],
        "best_weighted": best["weighted"],
        "cape": {
            "best_cut": cape.get("best_cut"),
            "best_weighted": cape.get("best_weighted"),
            "lock_weighted": cape.get("lock_weighted"),
        },
        "ranking": ranking,
        "list": swap_vital(base, chosen) if chosen else base,
    }
    dest = ROOT / "data/lab/set-m-poke-vital-a.json"
    dest.write_text(json.dumps(report, indent=2) + "\n")
    md = ROOT / "data/lab/set-m-poke-vital-a.md"
    md.write_text(_markdown(report))
    print(f"\nlock {lock['weighted']:.1%}  best {best['cut']} {best['weighted']:.1%}")
    print(f"cape {cape.get('best_cut')} {cape.get('best_weighted')}")
    print(f"cut {chosen}")
    print(f"elapsed {report['elapsed']:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
