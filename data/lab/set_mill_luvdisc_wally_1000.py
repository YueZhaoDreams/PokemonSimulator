#!/usr/bin/env python3
"""1000-game check of one Luvdisc against one Wally on the locked Mill 60.

The 400-game pass left these two cards inside one standard error. This run
plays only that pair. Same seed, both seats, frozen Sisters weights.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.setdefault(
    "MILL_LUVDISC_PARTIAL",
    str(Path(__file__).resolve().parent / "set-mill-luvdisc-wally-1000-partial.jsonl"),
)

import data.lab.set_mill_luvdisc as lab

GAMES = int(os.environ.get("MILL_LUVDISC_WALLY_GAMES", "1000"))
SEED = int(os.environ.get("MILL_LUVDISC_WALLY_SEED", "20261031"))
DEST = Path(os.environ.get("MILL_LUVDISC_WALLY_DEST", lab.HERE / "set-mill-luvdisc-wally-1000.json"))
MD_DEST = Path(os.environ.get("MILL_LUVDISC_WALLY_MD", lab.HERE / "set-mill-luvdisc-wally-1000.md"))


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _signed(value: float) -> str:
    return f"{value:+.2%}"


def _markdown(report: dict) -> str:
    lock = report["lock"]
    swap = report["swap"]
    gap = swap["weighted"] - lock["weighted"]
    gap_se = report["gap_se"]
    lines = [
        "# Luvdisc vs Wally, 1000 games",
        "",
        "One Luvdisc replaces one Wally on the locked Mill 60. The other 58 cards stay. "
        "Paldea Evolved Luvdisc uses Matching and Water Pulse. "
        "Wally searches the deck for Wugtrio and evolves Wiglett.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: Mill is player A and player B. A matchup cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60.",
        "- **Weights**: " + ", ".join(f"{key} {lab.WEIGHTS[key]:.1%}" for key, *_rest in lab.FOES),
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate. "
        "The difference column is one standard error of the gap.",
        "",
        "## Lists",
        "",
        "| List | Wally | Luvdisc | Weighted | ± | Mean | Worst | Delta | Matching | Supporters taken | Opponent Asleep | Luvdisc saw play | Undersea Tunnel |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in (lock, swap):
        lines.append(
            "| {label} | {wally} | {luvdisc} | {weighted} | {se} | {mean} | {worst} | {delta} | {matching:.3f} | {cards:.3f} | {asleep:.3f} | {saw:.1%} | {mill:.3f} |".format(
                label=row["label"],
                wally=row["wally"],
                luvdisc=row["luvdisc_count"],
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - lock["weighted"]),
                matching=row["matching"],
                cards=row["matching_cards"],
                asleep=row["opponent_asleep"],
                saw=row["luvdisc"],
                mill=row["mill_attack"],
            )
        )
    if gap > gap_se:
        decision = (
            f"−Wally is { _pct(swap['weighted']) } versus the lock at { _pct(lock['weighted']) } "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            "The gain is larger than one standard error of the difference."
        )
    elif gap < -gap_se:
        decision = (
            f"−Wally is { _pct(swap['weighted']) } versus the lock at { _pct(lock['weighted']) } "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            "The lock is ahead by more than one standard error of the difference. "
            "SET_MILL_NAMES stays at Wally ×3."
        )
    else:
        decision = (
            f"−Wally is { _pct(swap['weighted']) } versus the lock at { _pct(lock['weighted']) } "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            "The gap is inside one standard error of the difference. "
            "SET_MILL_NAMES stays at Wally ×3."
        )
    lines.extend(["", "## Decision", "", decision, ""])
    lines.extend(
        [
            "## Lock, both seats",
            "",
            "| Matchup | Weight | A | B | Mean |",
            "| :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_rest in lab.FOES:
        cell = lock["cells"][key]
        lines.append(
            f"| {label} | {lab.WEIGHTS[key]:.1%} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} |"
        )
    lines.extend(
        [
            "",
            "## −Wally, both seats",
            "",
            "Delta is the two-seat mean against the lock.",
            "",
            "| Matchup | Weight | A | B | Mean | Delta |",
            "| :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_rest in lab.FOES:
        cell = swap["cells"][key]
        base = lock["cells"][key]
        lines.append(
            f"| {label} | {lab.WEIGHTS[key]:.1%} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base['wr'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _summary(label: str, names: list[str], cells: dict) -> dict:
    return {
        "label": label,
        "wally": names.count("Wally"),
        "luvdisc_count": names.count("Luvdisc"),
        "weighted": lab._weighted(cells),
        "se": lab._weighted_se(cells, GAMES),
        "mean": lab._mean(cells),
        "worst": lab._worst(cells),
        "matching": lab._avg(cells, "matching"),
        "matching_cards": lab._avg(cells, "matching_cards"),
        "opponent_asleep": lab._avg(cells, "opponent_asleep"),
        "luvdisc": lab._avg(cells, "luvdisc"),
        "mill_attack": lab._avg(cells, "mill_attack"),
        "forest": lab._avg(cells, "forest"),
        "forest_play": lab._avg(cells, "forest_play"),
        "face": lab._avg(cells, "face"),
        "cells": {
            key: {"wr": row["wr"], "a": row["a"], "b": row["b"]}
            for key, row in cells.items()
        },
    }


def main() -> None:
    lab.SEED = SEED
    started = time.perf_counter()
    lock_names = list(lab.SET_MILL_NAMES)
    swap_names = lab._swap(lock_names, "Wally")
    if swap_names is None or swap_names.count("Wally") != lock_names.count("Wally") - 1:
        raise SystemExit("Wally swap failed")
    if len(lock_names) != 60 or len(swap_names) != 60:
        raise SystemExit("list is not 60")
    cache = lab._load_cache()
    print(f"wally-1000 games={GAMES} seed={SEED}", flush=True)
    raw = lab._evaluate([("lock", lock_names), ("-Wally", swap_names)], GAMES, cache)
    lock_cells = lab._combine(raw["lock"])
    swap_cells = lab._combine(raw["-Wally"])
    lock = _summary("lock", lock_names, lock_cells)
    swap = _summary("−Wally", swap_names, swap_cells)
    gap_se = (lock["se"] ** 2 + swap["se"] ** 2) ** 0.5
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": lab.WEIGHTS,
        "gap": swap["weighted"] - lock["weighted"],
        "gap_se": gap_se,
        "lock": lock,
        "swap": swap,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(MD_DEST.read_text())


if __name__ == "__main__":
    main()
