#!/usr/bin/env python3
"""Replay the locked Kecleon 60 with the stall line.

Dual Ball stays at 0. SET_KECLEON_NAMES is not edited. The stored 0-copy
cells in kecleon-dual-ball.json are the old line. Seed 20261120, 400 games
a seat, both seats, every current 60. Mill, Doll, and roast keep the old
Kecleon-first line; every other foe gets the high-HP wall.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from app.engine.game import play_game
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_KECLEON_NAMES
from kecleon_dual_ball import (
    SEED,
    _cards_for,
    _gap_se,
    _kind,
    _mean,
    _pct,
    _pp,
    _rate,
    _se,
    _subject_cards,
    _unweighted,
    discover,
)

GAMES = 400
WORKERS = int(os.environ.get("KECLEON_STALL_WORKERS", str(os.cpu_count() or 2)))
MILL = {"mill", "doll", "roast"}
PARTIAL = HERE / "kecleon-stall-partial.jsonl"
DEST = HERE / "kecleon-stall.json"
MD_DEST = HERE / "kecleon-stall.md"
BASELINE = HERE / "kecleon-dual-ball.json"


def _run(foe: dict, seat: str) -> dict:
    names = tuple(SET_KECLEON_NAMES)
    subject = _subject_cards(names)
    other = _cards_for(foe["builder"], foe["names"])
    if seat == "a":
        cards_a, cards_b = subject, other
        strat_a, strat_b = "kecleon", foe["strategy"]
    else:
        cards_a, cards_b = other, subject
        strat_a, strat_b = foe["strategy"], "kecleon"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(SEED)
    wins = 0
    events: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for _ in range(GAMES):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        if result.winner == seat:
            wins += 1
        ev = result.events or {}
        events["stall_pass"] += int(ev.get(f"stall_pass_{seat}", 0))
        events["stall_ko"] += int(ev.get(f"stall_ko_{seat}", 0))
        events["stall_wall"] += int(ev.get(f"stall_wall_{seat}", 0))
        events["colorful_whip"] += int(ev.get("colorful_whip", 0))
        events["skyliner_retreat"] += int(ev.get("skyliner_retreat", 0))
        _outcome, kind = _kind(result, seat)
        reasons[kind] += 1
    return {
        "wins": wins,
        "games": GAMES,
        "wr": wins / GAMES,
        "events": dict(events),
        "reasons": dict(reasons),
    }


def _load() -> dict[str, dict]:
    found: dict[str, dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found[row["key"]] = row["cell"]
    return found


def _append(key: str, cell: dict) -> None:
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")
        handle.flush()


def _per(cell: dict, name: str) -> float:
    return cell["events"].get(name, 0) / cell["games"]


def _note(payload: dict) -> str:
    weights = payload["weights"]
    active = payload["active"]
    old = payload["old_cells"]
    new = payload["cells"]
    lines = [
        "# Kecleon stall line, Dual Ball at 0",
        "",
        "The locked `SET_KECLEON_NAMES` list is not edited. Dual Ball is 0. "
        "Latias ex stays at 2. Against Mill, Doll, and the roast mills the old "
        "line still leads Kecleon and swings a short Colorful Whip. Against every "
        "other current 60, a higher-HP Basic stays Active. Energy goes to the "
        "benched Kecleon. Retreat, including a free Skyliner retreat, happens "
        "when Colorful Whip, Cruel Arrow, or Hyperspace Fury Knocks Out. A short "
        "Whip passes.",
        "",
        "The old cells are `start_cells` in `kecleon-dual-ball.json`. "
        f"Seed {payload['seed']}. {payload['games']} games per seat. Both seats. "
        "Each cell starts a new `random.Random` at that seed. The two lines diverge "
        "after the first choice that consumes a different number of draws. "
        "Mill matchups share the old choices, so their win counts should match.",
        "",
        f"Elapsed {payload['elapsed_s']:.0f}s.",
        "",
        "## Rates",
        "",
        f"Full field, 0-copy weights: old {_pct(payload['old_weighted'])}, "
        f"new {_pct(payload['new_weighted'])}, {_pp(payload['delta_weighted'])}. "
        f"Old SE {_pct(payload['old_se'])}, new SE {_pct(payload['new_se'])}, "
        f"gap SE {_pct(payload['gap_se'])}.",
        "",
        f"Same weights on the old active set only: old {_pct(payload['old_active'])}, "
        f"new {_pct(payload['new_active'])}, {_pp(payload['delta_active'])}.",
        "",
        f"Unweighted, all {len(payload['foes'])} foes: old {_pct(payload['old_flat'])}, "
        f"new {_pct(payload['new_flat'])}, {_pp(payload['delta_flat'])}.",
        "",
        "A positive step is the stall line winning more often. The weight vector "
        "is the old loss rates, so a foe the old line already beat has a small weight.",
        "",
        "| Foe | Strategy | Line | Old | New | Change | Whip / game | Stall pass | Stall KO | Stall wall |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    ranked = sorted(payload["foes"], key=lambda foe: _mean(new[foe["key"]]) - _mean(old[foe["key"]]))
    for foe in ranked:
        key = foe["key"]
        left = _mean(old[key])
        right = _mean(new[key])
        pair = new[key]
        whip = (_per(pair["a"], "colorful_whip") + _per(pair["b"], "colorful_whip")) / 2
        old_whip = (
            old[key]["a"]["events"].get("colorful_whip", 0) / old[key]["a"]["games"]
            + old[key]["b"]["events"].get("colorful_whip", 0) / old[key]["b"]["games"]
        ) / 2
        passed = (_per(pair["a"], "stall_pass") + _per(pair["b"], "stall_pass")) / 2
        ko = (_per(pair["a"], "stall_ko") + _per(pair["b"], "stall_ko")) / 2
        wall = (_per(pair["a"], "stall_wall") + _per(pair["b"], "stall_wall")) / 2
        line = "old" if foe["strategy"] in MILL else "stall"
        lines.append(
            f"| {foe['label']} | {foe['strategy']} | {line} | {_pct(left)} | {_pct(right)} | "
            f"{_pp(right - left)} | {old_whip:.2f} → {whip:.2f} | {passed:.2f} | {ko:.2f} | {wall:.2f} |"
        )
    lines.extend(
        [
            "",
            "Stall pass, stall KO, and stall wall are per subject seat per game. "
            "Colorful Whip has no seat, so a Kecleon mirror counts both players. "
            "Mill, Doll, Celebi Mill, and 二森林 stay on the old line; a stall "
            "counter above zero there is a bug.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    names = list(SET_KECLEON_NAMES)
    if names.count("Dual Ball") != 0 or names.count("Latias ex") != 2 or len(names) != 60:
        raise SystemExit(f"lock changed: dual {names.count('Dual Ball')} latias {names.count('Latias ex')} n {len(names)}")
    previous = json.loads(BASELINE.read_text())
    old_cells = previous["start_cells"]
    weights = previous["weights"]
    active = previous["active"]
    foes = discover()["foes"]
    missing = [foe["key"] for foe in foes if foe["key"] not in old_cells or foe["key"] not in weights]
    if missing:
        raise SystemExit(f"baseline is missing {missing}")
    cache = _load()
    jobs = []
    cells: dict[str, dict] = {}
    for foe in foes:
        for seat in ("a", "b"):
            key = f"{SEED}|{GAMES}|{seat}|{foe['key']}"
            cached = cache.get(key)
            if cached is not None:
                cells.setdefault(foe["key"], {})[seat] = cached
                continue
            jobs.append((foe, seat, key))
    print(f"stall: {len(jobs)} cells to play, {GAMES} games", flush=True)
    started = time.perf_counter()
    if jobs:
        workers = max(1, min(WORKERS, len(jobs)))
        with ProcessPoolExecutor(max_workers=workers) as pool:
            future = {pool.submit(_run, foe, seat): (foe, seat, key) for foe, seat, key in jobs}
            done = 0
            for item in as_completed(future):
                foe, seat, key = future[item]
                cell = item.result()
                _append(key, cell)
                cells.setdefault(foe["key"], {})[seat] = cell
                done += 1
                print(
                    f"  {done}/{len(jobs)} {foe['key']} seat {seat} {cell['wins']}/{GAMES}",
                    flush=True,
                )
    elapsed = time.perf_counter() - started
    old_view = {foe["key"]: old_cells[foe["key"]] for foe in foes}
    new_view = cells
    old_weighted = _rate(old_view, weights)
    new_weighted = _rate(new_view, weights)
    payload = {
        "seed": SEED,
        "games": GAMES,
        "list": names,
        "dual_ball": 0,
        "elapsed_s": elapsed,
        "weights": weights,
        "active": active,
        "foes": [{"key": foe["key"], "label": foe["label"], "strategy": foe["strategy"]} for foe in foes],
        "old_cells": old_view,
        "cells": new_view,
        "old_weighted": old_weighted,
        "new_weighted": new_weighted,
        "delta_weighted": new_weighted - old_weighted,
        "old_se": _se(old_view, weights),
        "new_se": _se(new_view, weights),
        "gap_se": _gap_se(old_view, new_view, weights, list(weights)),
        "old_active": _rate({key: old_view[key] for key in active}, {key: weights[key] for key in active}),
        "new_active": _rate({key: new_view[key] for key in active}, {key: weights[key] for key in active}),
        "old_flat": _unweighted(old_view, [foe["key"] for foe in foes]),
        "new_flat": _unweighted(new_view, [foe["key"] for foe in foes]),
    }
    payload["delta_active"] = payload["new_active"] - payload["old_active"]
    payload["delta_flat"] = payload["new_flat"] - payload["old_flat"]
    DEST.write_text(json.dumps(payload, indent=2) + "\n")
    MD_DEST.write_text(_note(payload))
    print(
        f"weighted {_pct(old_weighted)} -> {_pct(new_weighted)} {_pp(new_weighted - old_weighted)}",
        flush=True,
    )
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
