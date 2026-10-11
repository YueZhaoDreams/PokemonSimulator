#!/usr/bin/env python3
"""Re-rank the one-Mega cuts with the household foes included.

The first greedy table scored C60 only against T60, Hedrick, Unlimited
Dragapult, D60, S60, and G. Those cells are reused. This run adds M, Kudo's
Mega Starmie, the Wugtrio mill, Lucario, Iron Thorns, Carpet H, and Ambipom.
C60 is player A in every cell, matching the first table. Weights are frozen
from the 0-Mega list across all 13 foes.

Seed 20261011. Games per new cell from C60_ALL_GAMES (default 1000).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_G30_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_STARMIE60_NAMES,
    build_fallback_deck,
    build_g30_deck,
    c60_names_before_mega,
)

_SEEKER_PATH = Path(__file__).with_name("set_c60_mega_seeker.py")
_spec = importlib.util.spec_from_file_location("set_c60_mega_seeker", _SEEKER_PATH)
_seeker = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_seeker)
IN_NAME = _seeker.IN_NAME
swap_one = _seeker.swap_one

PRIOR = ROOT / "data/lab/set-c60-mega-seeker.json"
PARTIAL = ROOT / "data/lab/set-c60-mega-allfoes-partial.jsonl"
DEST = ROOT / "data/lab/set-c60-mega-allfoes.json"
MD_DEST = ROOT / "data/lab/set-c60-mega-allfoes.md"

OLD_FOES = ("t60", "hedrick", "unl", "d60", "s60", "g")
NEW_FOES = (
    ("m", "Set M (Mew ex)", SET_M60_NAMES, "mew_baby", False),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie", False),
    ("mill", "Wugtrio mill", SET_MILL_NAMES, "mill", False),
    ("lucario", "Lucario Hariyama", SET_L60_NAMES, "aura", False),
    ("thorns", "Iron Thorns ex", IRON_THORNS_NAMES, "thorns", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)
FOE_ORDER = OLD_FOES + tuple(key for key, *_ in NEW_FOES)

GAMES = int(os.environ.get("C60_ALL_GAMES", "1000"))
SEED = int(os.environ.get("C60_ALL_SEED", "20261011"))
WORKERS = int(os.environ.get("C60_ALL_WORKERS", str(min(4, os.cpu_count() or 2))))
QUERIES = [
    {"type": "event_prefix", "prefix": "seeker_moons_fuel", "key": "moons"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex:Shooting Moons", "key": "shooting"},
]


def _foe_deck(names: list[str], g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _load_prior() -> dict[str, dict]:
    data = json.loads(PRIOR.read_text())
    if data.get("seed") != SEED or data.get("games") != GAMES:
        raise SystemExit(f"prior table is seed {data.get('seed')} games {data.get('games')}")
    rows = {}
    for row in data["ranking"]:
        key = row["cut"] or "lock"
        cells = row["cells"]
        missing = [foe for foe in OLD_FOES if foe not in cells]
        if missing:
            raise SystemExit(f"{key} is missing {missing}")
        rows[key] = {"copies": row["copies_before"], "old": cells}
    if "lock" not in rows:
        raise SystemExit("prior table has no lock row")
    return rows


def _load_partial() -> dict[tuple[str, str], dict]:
    found: dict[tuple[str, str], dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found[(row["cut"], row["foe"])] = row["cell"]
    return found


def _run(cut: str, names: list[str], foe_key: str, foe_names, foe_strat: str, g30: bool) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(list(names)),
        _foe_deck(list(foe_names), g30),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
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
        "moons": r["queries"].get("moons", 0.0),
        "shooting": r["queries"].get("shooting", 0.0),
    }


def _weights(lock_cells: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - lock_cells[key]["a"]) for key in FOE_ORDER}
    total = sum(raw.values())
    return {key: raw[key] / total for key in FOE_ORDER}


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key in FOE_ORDER)


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key in FOE_ORDER) / len(FOE_ORDER)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key in FOE_ORDER)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _markdown(report: dict) -> str:
    weights = report["weights"]
    lines = [
        "# One Mega, all measured foes",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Seat**: C60 is player A.",
        "- **Old cells**: T60, Hedrick, UNL, D60, S60, and G, reused from `set-c60-mega-seeker.json`.",
        "- **New cells**: M, Starmie, mill, Lucario, Iron Thorns, Carpet H, and Ambipom.",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 0-Mega list over all 13 foes.",
        f"- **Weights**: {', '.join(f'{key} {weights[key]:.1%}' for key in FOE_ORDER)}",
        f"- **Best cut**: {report['best']}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "| Rank | Cut | 6-foe weighted | All-foe weighted | Mean | Worst | vs M | vs Starmie | vs Mill | vs Lucario | vs Thorns | vs H | vs G30 |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["ranking"]:
        cells = row["cells"]
        cut = row["cut"] or "lock"
        lines.append(
            f"| {row['rank']} | {cut} | {_pct(row['old_weighted'])} | {_pct(row['weighted'])} | "
            f"{_pct(row['mean'])} | {_pct(row['worst'])} | {_pct(cells['m']['a'])} | "
            f"{_pct(cells['starmie']['a'])} | {_pct(cells['mill']['a'])} | {_pct(cells['lucario']['a'])} | "
            f"{_pct(cells['thorns']['a'])} | {_pct(cells['h']['a'])} | {_pct(cells['g30']['a'])} |"
        )
    lines.extend(
        [
            "",
            "## Decision",
            "",
            report["decision"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    prior = _load_prior()
    base = c60_names_before_mega()
    lists = {"lock": list(base)}
    for cut in prior:
        if cut == "lock":
            continue
        built = swap_one(base, cut)
        if built.count(IN_NAME) != 1:
            raise SystemExit(f"{cut} did not add one Mega")
        lists[cut] = built
    if set(lists) != set(prior):
        raise SystemExit("cut names drifted from the first greedy table")

    done = _load_partial()
    jobs = []
    for cut, names in lists.items():
        for foe_key, _label, foe_names, foe_strat, g30 in NEW_FOES:
            if (cut, foe_key) in done:
                continue
            jobs.append((cut, names, foe_key, foe_names, foe_strat, g30))
    print(f"{len(jobs)} new cells, {len(done)} already stored, seed {SEED}", flush=True)
    if jobs:
        with PARTIAL.open("a") as handle:
            with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
                futs = [pool.submit(_run, *job) for job in jobs]
                finished = 0
                for fut in as_completed(futs):
                    cut, foe_key, cell = fut.result()
                    done[(cut, foe_key)] = cell
                    handle.write(json.dumps({"cut": cut, "foe": foe_key, "cell": cell}) + "\n")
                    handle.flush()
                    finished += 1
                    print(
                        f"  {cut} vs {foe_key}: {cell['a']:.1%}  "
                        f"moons {cell['moons']:.3f} shooting {cell['shooting']:.3f}  "
                        f"({finished}/{len(jobs)})",
                        flush=True,
                    )

    combined: dict[str, dict[str, dict]] = {}
    for cut, row in prior.items():
        cells = {foe: row["old"][foe] for foe in OLD_FOES}
        for foe_key, *_ in NEW_FOES:
            cells[foe_key] = done[(cut, foe_key)]
        combined[cut] = cells

    weights = _weights(combined["lock"])
    # Six-foe weighted score, weights frozen on the lock's six original foes only.
    six_raw = {foe: max(1e-6, 1.0 - combined["lock"][foe]["a"]) for foe in OLD_FOES}
    six_total = sum(six_raw.values())
    six_weights = {foe: six_raw[foe] / six_total for foe in OLD_FOES}

    def six_weighted(cut: str) -> float:
        return sum(combined[cut][foe]["a"] * six_weights[foe] for foe in OLD_FOES)

    rows = []
    for cut, cells in combined.items():
        rows.append(
            {
                "cut": None if cut == "lock" else cut,
                "copies_before": prior[cut]["copies"],
                "weighted": _weighted(cells, weights),
                "old_weighted": six_weighted(cut),
                "mean": _mean(cells),
                "worst": _worst(cells),
                "cells": cells,
            }
        )
    rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -(row["copies_before"] or 0), row["cut"] or ""))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    lock = next(row for row in rows if row["cut"] is None)
    best = next(row for row in rows if row["cut"])
    accepted = best["weighted"] > lock["weighted"]
    if accepted and best["cut"] == "Clefable":
        decision = (
            f"Cutting one Prankish Clefable is still the best one-Mega swap. "
            f"All-foe weighted win rate {_pct(best['weighted'])} versus the lock's {_pct(lock['weighted'])}."
        )
    elif accepted:
        decision = (
            f"The best one-Mega swap on all 13 foes is one {best['cut']}. "
            f"All-foe weighted win rate {_pct(best['weighted'])} versus the lock's {_pct(lock['weighted'])}. "
            f"Prankish Clefable is {_pct(next(row['weighted'] for row in rows if row['cut'] == 'Clefable'))}."
        )
    else:
        decision = (
            f"No cut beats the lock on all 13 foes ({_pct(lock['weighted'])}). "
            f"Closest is {best['cut']} at {_pct(best['weighted'])}."
        )
    elapsed = time.perf_counter() - started
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "seat": "C60 is player A",
        "reused": list(OLD_FOES),
        "added": [key for key, *_ in NEW_FOES],
        "weights": weights,
        "six_weights": six_weights,
        "best": best["cut"] if accepted else None,
        "lock_weighted": lock["weighted"],
        "best_weighted": best["weighted"],
        "decision": decision,
        "ranking": rows,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(decision, flush=True)
    print(f"elapsed {elapsed:.1f}s -> {DEST}", flush=True)


if __name__ == "__main__":
    main()
