#!/usr/bin/env python3
"""Greedy one-card Mega Clefable ex swap for the locked C60 list.

The live lock has Seeker and zero Mega Clefable ex. This search adds exactly
one Mega Clefable ex, cutting one copy of one other card. The decision score
is the loss-weighted win rate. Weights are frozen from that 0-Mega list.

Party line this card is scored with: Mega Clefable ex is Active and can use
Shooting Moons. Energy in hand is short of the knockout and short of the
printed "discard up to 4 Energy cards". Seeker returns a Benched Pokémon and
the Energy attached to it, and those cards are discarded for 40 more damage
each. One attached Energy is returned when that fills a knockout or the 4.
Two or more are returned when they add at least two discards.

Foes: T60, Hedrick, Unlimited Dragapult, D60, S60, and G.
Seed 20261011. Games per cell from C60_MEGA_GAMES (default 1000).
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
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "phantom"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "slash"),
    ("g", "Carpet Set G", SET_G_NAMES, "g"),
)

IN_NAME = "Mega Clefable ex"
GAMES = int(os.environ.get("C60_MEGA_GAMES", "1000"))
SEED = int(os.environ.get("C60_MEGA_SEED", "20261011"))
WORKERS = int(os.environ.get("C60_MEGA_WORKERS", str(min(4, os.cpu_count() or 2))))
QUERIES = [
    {"type": "event_prefix", "prefix": "seeker_moons_fuel", "key": "moons"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex:Shooting Moons", "key": "shooting"},
    {"type": "event_sum", "prefix": "shooting_moons_discard", "key": "discarded"},
]
DEST = ROOT / "data/lab/set-c60-mega-seeker.json"
MD_DEST = ROOT / "data/lab/set-c60-mega-seeker.md"

PRINTED = (
    "You may discard up to 4 Energy cards from your hand, and this attack does "
    "40 more damage for each card you discarded in this way."
)
SEEKER = (
    "Each player returns 1 of his or her Benched Pokémon and all cards attached "
    "to it to his or her hand. (You return your Pokémon first.)"
)


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
        raise ValueError("Mega Clefable ex would exceed 4")
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
        "moons": r["queries"].get("moons", 0.0),
        "shooting": r["queries"].get("shooting", 0.0),
        "discarded": r["queries"].get("discarded", 0.0),
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
                f"  {key or 'baseline'} vs {foe_key}: {detail['a']:.1%}  "
                f"moons {detail['moons']:.3f} shooting {detail['shooting']:.3f}  "
                f"({done}/{len(jobs)})",
                flush=True,
            )
    for key, _ in lists:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _avg(cells: dict[str, dict], field: str) -> float:
    return sum(cells[key][field] for key, *_ in FOES) / len(FOES)


def _candidate_row(cut: str, cells: dict[str, dict], copies: Counter, weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    return {
        "cut": cut,
        "copies_before": copies[cut],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "moons": _avg(ordered, "moons"),
        "shooting": _avg(ordered, "shooting"),
        "discarded": _avg(ordered, "discarded"),
        "cells": ordered,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _markdown(report: dict) -> str:
    weights = report["weights"]
    lines = [
        "# C60 greedy one Mega Clefable ex",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 0-Mega list.",
        f"- **Weights**: {', '.join(f'{key} {weights[key]:.1%}' for key, *_ in FOES)}",
        f"- **Chosen cut**: {report['cut'] or '(none — no swap beat the lock)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Printed Shooting Moons: " + PRINTED,
        "",
        "Printed Seeker: " + SEEKER,
        "",
        "Mega Clefable ex is Active and can pay Shooting Moons. Energy already in "
        "hand does not knock the Defending Pokémon out and does not fill the 4 "
        "discards. Seeker returns one Benched Pokémon and every card attached to "
        "it. Those Energy cards are in hand for the discard, 40 more damage each. "
        "The attack's printed base is 120, so four discards are 280.",
        "",
        "## Ranking",
        "",
        "The lock is zero Mega Clefable ex. Every other row cuts one copy and adds one Mega.",
        "",
        "| Rank | Cut | Copies | Weighted | Mean | Worst | Moons | Shooting | vs T60 | vs Hedrick | vs UNL | vs D60 | vs S60 | vs G |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["ranking"]:
        cells = row["cells"]
        cut = row["cut"] or "lock"
        copies = "—" if row["cut"] is None else str(row["copies_before"])
        lines.append(
            f"| {row['rank']} | {cut} | {copies} | {_pct(row['weighted'])} | {_pct(row['mean'])} | "
            f"{_pct(row['worst'])} | {row['moons']:.3f} | {row['shooting']:.3f} | "
            f"{_pct(cells['t60']['a'])} | {_pct(cells['hedrick']['a'])} | {_pct(cells['unl']['a'])} | "
            f"{_pct(cells['d60']['a'])} | {_pct(cells['s60']['a'])} | {_pct(cells['g']['a'])} |"
        )
    chosen = report["cut"]
    lock = next(row for row in report["ranking"] if row["cut"] is None)
    top = next(row for row in report["ranking"] if row["cut"])
    lines.extend(["", "## Decision", ""])
    if chosen:
        lines.append(
            f"Cut one {chosen} for one Mega Clefable ex. Weighted win rate "
            f"{_pct(top['weighted'])} versus the lock's {_pct(lock['weighted'])}."
        )
    else:
        lines.append(
            f"No cut beat the lock ({_pct(lock['weighted'])}). "
            f"Closest is {top['cut']} at {_pct(top['weighted'])}."
        )
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))


def main() -> None:
    started = time.perf_counter()
    current = list(SET_C60_NAMES)
    if len(current) != 60:
        raise SystemExit(f"C60 has {len(current)} cards")
    if current.count(IN_NAME):
        raise SystemExit("baseline already contains Mega Clefable ex; greedy expects zero")
    if current.count("Seeker") != 1:
        raise SystemExit("baseline should keep the one Seeker this combo uses")

    print(f"baseline {GAMES} games x {len(FOES)} foes, seed {SEED}", flush=True)
    base_cells = _eval_lists([("baseline", current)])["baseline"]
    weights = loss_weights(base_cells)
    base_weighted = _weighted(base_cells, weights)
    print(
        f"baseline weighted {base_weighted:.1%}  mean {_mean(base_cells):.1%}  "
        f"weights {', '.join(f'{k} {weights[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )

    copies = Counter(current)
    cuts = sorted(name for name in copies if name != IN_NAME)
    lists = [(cut, swap_one(current, cut)) for cut in cuts]
    print(f"\none Mega: {len(lists)} cuts", flush=True)
    cells = _eval_lists(lists)
    rows = [_candidate_row(cut, cells[cut], copies, weights) for cut, _ in lists]
    rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"]))
    best = rows[0]
    accepted = best["weighted"] > base_weighted
    ranking = [
        {
            "rank": 0,
            "cut": None,
            "copies_before": 0,
            "weighted": base_weighted,
            "mean": _mean(base_cells),
            "worst": _worst(base_cells),
            "moons": _avg(base_cells, "moons"),
            "shooting": _avg(base_cells, "shooting"),
            "discarded": _avg(base_cells, "discarded"),
            "cells": {key: base_cells[key] for key, *_ in FOES},
        }
    ]
    ranking.extend(rows)
    ranking.sort(
        key=lambda row: (
            -row["weighted"],
            -row["worst"],
            -(row["copies_before"] or 0),
            row["cut"] or "",
        )
    )
    for index, row in enumerate(ranking, start=1):
        row["rank"] = index

    elapsed = time.perf_counter() - started
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "method": (
            "greedy one-card Mega Clefable ex swap from locked C60; "
            "score is the loss-weighted win rate with weights frozen from the 0-Mega list; "
            "exactly one copy"
        ),
        "printed_attack": PRINTED,
        "printed_seeker": SEEKER,
        "catalog_id": "me03-031",
        "foes": {key: strat for key, _label, _names, strat in FOES},
        "weights": weights,
        "accepted": accepted,
        "cut": best["cut"] if accepted else None,
        "baseline_weighted": base_weighted,
        "baseline_mean": _mean(base_cells),
        "chosen_weighted": best["weighted"],
        "chosen_mean": best["mean"],
        "list": swap_one(current, best["cut"]) if accepted else current,
        "ranking": ranking,
        "partial": False,
    }
    _write(report)
    print(
        f"\nbest cut {best['cut']} -> weighted {best['weighted']:.1%} "
        f"(lock {base_weighted:.1%}, moons {best['moons']:.3f}) "
        f"({'keep' if accepted else 'stop'})",
        flush=True,
    )
    print(f"elapsed {elapsed:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
