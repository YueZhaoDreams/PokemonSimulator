#!/usr/bin/env python3
"""Carpet G staged run: comparable win rates from none of the three to all three.

Re-runs every optimization stage on the SAME seed and SAME bake so the
deltas are comparable: seed 20260915, rule s60, G always player A, the same
7 household foes + strategies as the Boss-Friday and Poffin labs, 3000
games/cell (confirm level).

Stages (each 60 cards, copy-legal):
  s0_none   - no Mega, no Boss, no Poffin (Friday minus Mega/Boss, Emolga +
              Potion / Poke Ball / Plusle back in the printed slots)
  s1_mega   - s0 minus Emolga plus Mega Clefable ex (= Boss-Friday live G)
  s2_boss   - s1 minus Potion / Poke Ball / Plusle plus 3 Boss's Orders
              (= SET_G_FRIDAY_NAMES)
  s3_poffin - s2 minus Tornadus / Hop's Cramorant / Relicanth / Indeedee
              plus 4 Buddy-Buddy Poffin (= SET_G_NAMES lock)
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
try:
    import app  # noqa: F401
except ImportError:
    sys.path.insert(0, str(ROOT))

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_FRIDAY_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES = 3000
SEED = 20260915
WORKERS = 4

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
FOE_KEYS = tuple(k for k, _, _ in FOES)
COMPETITIVE = ("t60", "hedrick", "d60")

STAGE_ORDER = ("s0_none", "s1_mega", "s2_boss", "s3_poffin")

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "boss_orders", "key": "boss"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex", "key": "mega"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
    {"type": "event_prefix", "prefix": "tutor:Clefairy:poffin", "key": "poffin_clef"},
    {"type": "event_prefix", "prefix": "tutor:Ledyba:poffin", "key": "poffin_ledyba"},
    {"type": "event_prefix", "prefix": "tutor:Starly:poffin", "key": "poffin_starly"},
    {"type": "event_prefix", "prefix": "tutor:Kecleon:poffin", "key": "poffin_kecleon"},
]


def apply_cuts_adds(names: list[str], cuts, adds) -> list[str]:
    out = list(names)
    for name in cuts:
        out.remove(name)
    out.extend(adds)
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards, want 60 (cuts={cuts} adds={adds})")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return out


def stage_lists() -> dict[str, list[str]]:
    friday = list(SET_G_FRIDAY_NAMES)
    assert len(friday) == 60
    assert friday.count("Mega Clefable ex") == 1
    assert friday.count("Boss's Orders") == 3
    assert friday.count("Buddy-Buddy Poffin") == 0

    s1_mega = apply_cuts_adds(
        friday, ["Boss's Orders"] * 3, ["Potion", "Poké Ball", "Plusle"]
    )
    s0_none = apply_cuts_adds(s1_mega, ["Mega Clefable ex"], ["Emolga"])
    s2_boss = friday
    s3_poffin = list(SET_G_NAMES)
    assert len(s3_poffin) == 60
    assert Counter(s3_poffin) - Counter(s2_boss) == Counter({"Buddy-Buddy Poffin": 4})
    assert Counter(s2_boss) - Counter(s3_poffin) == Counter(
        {"Tornadus": 1, "Hop's Cramorant": 1, "Relicanth": 1, "Indeedee": 1}
    )
    return {
        "s0_none": s0_none,
        "s1_mega": s1_mega,
        "s2_boss": s2_boss,
        "s3_poffin": s3_poffin,
    }


def _detail(rec: dict) -> dict:
    r = rec["results"]
    q = r.get("query_counts") or {}
    return {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "party_games": q.get("party", 0),
        "gust_games": q.get("gust", 0),
        "boss_games": q.get("boss", 0),
        "adrena_games": q.get("adrena", 0),
        "mega_games": q.get("mega", 0),
        "tornadus_games": q.get("tornadus", 0),
        "poffin_games": sum(q.get(k, 0) for k in ("poffin_clef", "poffin_ledyba", "poffin_starly", "poffin_kecleon")),
    }


def _run(stage: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": stage, "name": stage},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return stage, foe_key, _detail(rec)


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        stage: sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
        for stage, row in cells.items()
    }


def main() -> None:
    started = time.perf_counter()
    lists = stage_lists()
    variants = [(stage, lists[stage]) for stage in STAGE_ORDER]

    cells: dict[str, dict[str, dict]] = {stage: {} for stage in STAGE_ORDER}
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [
            pool.submit(_run, stage, names, foe_key, foe_names, foe_strat)
            for stage, names in variants
            for foe_key, foe_names, foe_strat in FOES
        ]
        for fut in as_completed(futs):
            stage, foe_key, detail = fut.result()
            cells[stage][foe_key] = detail
            print(
                f"{stage} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"party {detail['party_games']} boss {detail['boss_games']} "
                f"mega {detail['mega_games']} poffin {detail['poffin_games']}",
                flush=True,
            )
    cells = {stage: {key: cells[stage][key] for key in FOE_KEYS} for stage in STAGE_ORDER}

    base = cells["s0_none"]
    weighted_all = _weighted(cells, base, FOE_KEYS)
    weighted_comp = _weighted(cells, base, COMPETITIVE)
    deltas = {
        stage: {key: round(cells[stage][key]["a"] - cells[prev][key]["a"], 4) for key in FOE_KEYS}
        for stage, prev in zip(STAGE_ORDER[1:], STAGE_ORDER)
    }

    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "stages": list(STAGE_ORDER),
        "lists": lists,
        "counts": {s: Counter(n).most_common() for s, n in lists.items()},
        "foes": {key: strat for key, _names, strat in FOES},
        "cells": cells,
        "deltas_vs_prev": deltas,
        "weighted_all_vs_s0": weighted_all,
        "weighted_competitive_vs_s0": weighted_comp,
    }
    dest = ROOT / "data/lab/set-g-stages.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("win% by stage:")
    for stage in STAGE_ORDER:
        row = " ".join(f"{k}={cells[stage][k]['a']:.1%}" for k in FOE_KEYS)
        print(f"  {stage}: {row}")
    print("weighted_all", {k: round(v, 4) for k, v in weighted_all.items()})
    print("weighted_competitive", {k: round(v, 4) for k, v in weighted_comp.items()})


if __name__ == "__main__":
    main()
