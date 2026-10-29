#!/usr/bin/env python3
"""1000-game check of every legal Luvdisc cut on the locked Mill 60.

One Luvdisc replaces one copy of each cuttable card. The other 58 cards stay.
Same seed as the 400-game screen and the Wally pair. The lock and the Wally
list are reused from that pair's partial when the cache key matches.

SET_MILL_NAMES is not edited here. A cut is ahead only when its weighted gain
is larger than one standard error of the difference.
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
    str(Path(__file__).resolve().parent / "set-mill-luvdisc-cuts-1000-partial.jsonl"),
)

import data.lab.set_mill_luvdisc as lab

GAMES = int(os.environ.get("MILL_LUVDISC_CUTS_GAMES", "1000"))
SEED = int(os.environ.get("MILL_LUVDISC_CUTS_SEED", "20261031"))
DEST = Path(os.environ.get("MILL_LUVDISC_CUTS_DEST", lab.HERE / "set-mill-luvdisc-cuts-1000.json"))
MD_DEST = Path(os.environ.get("MILL_LUVDISC_CUTS_MD", lab.HERE / "set-mill-luvdisc-cuts-1000.md"))
WALLY_PARTIAL = lab.HERE / "set-mill-luvdisc-wally-1000-partial.jsonl"


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _signed(value: float) -> str:
    return f"{value:+.2%}"


def _load_many(paths: list[Path]) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in paths:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            found[row["key"]] = row["cell"]
    return found


def _summary(label: str, cut: str | None, names: list[str], cells: dict) -> dict:
    return {
        "label": label,
        "cut": cut,
        "remaining": None if cut is None else names.count(cut),
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


def _markdown(report: dict) -> str:
    lock = report["lock"]
    rows = report["cuts"]
    lines = [
        "# Luvdisc vs every legal cut, 1000 games",
        "",
        "One Luvdisc replaces one copy of a cuttable card on the locked Mill 60. "
        "The other 58 cards stay. Protected cards stay in the list: the babies, "
        "Manaphy, Wiglett, Wugtrio, Victini, Slumbering Forest, and Neutralization Zone. "
        "Paldea Evolved Luvdisc uses Matching and Water Pulse.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: Mill is player A and player B. A matchup cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60.",
        "- **Weights**: " + ", ".join(f"{key} {lab.WEIGHTS[key]:.1%}" for key, *_rest in lab.FOES),
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate. "
        "Δ/SE is the gap divided by one standard error of the difference against the lock.",
        "",
        "## Lists",
        "",
        "| List | Left | Weighted | ± | Mean | Worst | Delta | Δ/SE | Matching | Supporters taken | Opponent Asleep | Luvdisc saw play | Undersea Tunnel |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    ordered = [lock] + rows
    for row in ordered:
        gap = row["weighted"] - lock["weighted"]
        gap_se = (lock["se"] ** 2 + row["se"] ** 2) ** 0.5
        ratio = gap / gap_se if gap_se else 0.0
        left = "—" if row["cut"] is None else str(row["remaining"])
        lines.append(
            "| {label} | {left} | {weighted} | {se} | {mean} | {worst} | {delta} | {ratio:.2f} | {matching:.3f} | {cards:.3f} | {asleep:.3f} | {saw:.1%} | {mill:.3f} |".format(
                label=row["label"],
                left=left,
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(gap),
                ratio=ratio,
                matching=row["matching"],
                cards=row["matching_cards"],
                asleep=row["opponent_asleep"],
                saw=row["luvdisc"],
                mill=row["mill_attack"],
            )
        )
    def _gap(row: dict) -> tuple[float, float]:
        gap = row["weighted"] - lock["weighted"]
        gap_se = (lock["se"] ** 2 + row["se"] ** 2) ** 0.5
        return gap, gap_se

    beaters = [row for row in rows if _gap(row)[0] > _gap(row)[1]]
    best = beaters[0] if beaters else rows[0]
    gap, gap_se = _gap(best)
    if beaters:
        decision = (
            f"−{best['cut']} is {_pct(best['weighted'])} versus the lock at {_pct(lock['weighted'])} "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            "The gain is larger than one standard error of the difference."
        )
    else:
        decision = (
            f"No cut beat the lock by more than one standard error. "
            f"The closest is −{best['cut']} at {_pct(best['weighted'])} "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            "SET_MILL_NAMES stays the current 60. Luvdisc stays at zero copies."
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
    for row in rows:
        lines.extend(
            [
                "",
                f"## {row['label']}, both seats",
                "",
                "Delta is the two-seat mean against the lock.",
                "",
                "| Matchup | Weight | A | B | Mean | Delta |",
                "| :--- | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for key, label, *_rest in lab.FOES:
            cell = row["cells"][key]
            base = lock["cells"][key]
            lines.append(
                f"| {label} | {lab.WEIGHTS[key]:.1%} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base['wr'])} |"
            )
    lines.append("")
    return "\n".join(lines)


def _lists() -> list[tuple[str, str | None, list[str]]]:
    lock_names = list(lab.SET_MILL_NAMES)
    if len(lock_names) != 60:
        raise SystemExit("lock is not 60")
    built = [("lock", None, lock_names)]
    for cut in lab._cuts(lock_names):
        swapped = lab._swap(lock_names, cut)
        if swapped is None or len(swapped) != 60 or swapped.count("Luvdisc") != 1:
            raise SystemExit(f"swap failed for {cut}")
        if swapped.count(cut) != lock_names.count(cut) - 1:
            raise SystemExit(f"cut count failed for {cut}")
        built.append((f"-{cut}", cut, swapped))
    return built


def main() -> None:
    lab.SEED = SEED
    started = time.perf_counter()
    lists = _lists()
    cache = _load_many([WALLY_PARTIAL, lab.PARTIAL])
    print(
        f"cuts-1000 games={GAMES} seed={SEED} lists={len(lists)} cached={len(cache)}",
        flush=True,
    )
    raw = lab._evaluate([(label, names) for label, _cut, names in lists], GAMES, cache)
    lock = _summary("lock", None, lists[0][2], lab._combine(raw["lock"]))
    cuts = []
    for label, cut, names in lists[1:]:
        cuts.append(_summary(f"−{cut}", cut, names, lab._combine(raw[label])))
    cuts.sort(key=lambda row: row["weighted"], reverse=True)
    best = cuts[0]
    gap_se = (lock["se"] ** 2 + best["se"] ** 2) ** 0.5
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": lab.WEIGHTS,
        "gap": best["weighted"] - lock["weighted"],
        "gap_se": gap_se,
        "lock": lock,
        "cuts": cuts,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(f"lock {lock['weighted'] * 100:.3f} ± {lock['se'] * 100:.3f}", flush=True)
    for row in cuts:
        gap = row["weighted"] - lock["weighted"]
        se = (lock["se"] ** 2 + row["se"] ** 2) ** 0.5
        ratio = gap / se if se else 0.0
        print(
            f"{row['label']} {row['weighted'] * 100:.3f} ± {row['se'] * 100:.3f} "
            f"gap {gap * 100:+.3f} se {se * 100:.3f} ratio {ratio:+.2f}",
            flush=True,
        )
    print(MD_DEST, flush=True)


if __name__ == "__main__":
    main()
