#!/usr/bin/env python3
"""Poffin follow-up: dose check (2 Poffin, sane cuts) and Tornadus-keep 4-cut.

Main run showed every 1-for-1 Poffin swap loses t60 vs baseline, and cutting
Tornadus screened worst on t60 (18.9%). Two questions:
1. Is the t60 drop dose-dependent? 2 Poffin for Tornadus + Cramorant.
2. Does keeping Tornadus fix t60? 4 Poffin for Cramorant + Relicanth +
   Indeedee + Kecleon (no Tornadus cut).

Self-contained (no import of the main lab module: spawn pickling).
Rule: s60. Seed 20260915. G is always player A.
"""

from __future__ import annotations

import json
import sys
import time
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
    SET_G_FRIDAY_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES = 2000
GAMES_CONFIRM = 3000
SEED = 20260915
WORKERS = 8

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
SCREEN_FOES = ("t60", "hedrick", "d60", "unl")
COMPETITIVE = ("t60", "hedrick", "d60")

VARIANTS = (
    ("baseline", (), ()),
    ("poffin2_sane", ("Tornadus", "Hop's Cramorant"), ("Buddy-Buddy Poffin",) * 2),
    (
        "keep_torn4",
        ("Hop's Cramorant", "Relicanth", "Indeedee", "Kecleon"),
        ("Buddy-Buddy Poffin",) * 4,
    ),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
    {"type": "event_prefix", "prefix": "tutor:Clefairy:poffin", "key": "poffin_clef"},
    {"type": "event_prefix", "prefix": "tutor:Ledyba:poffin", "key": "poffin_ledyba"},
    {"type": "event_prefix", "prefix": "tutor:Starly:poffin", "key": "poffin_starly"},
    {"type": "event_prefix", "prefix": "tutor:Kecleon:poffin", "key": "poffin_kecleon"},
]


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
        "tornadus_games": q.get("tornadus", 0),
        "poffin_clef": q.get("poffin_clef", 0),
        "poffin_ledyba": q.get("poffin_ledyba", 0),
        "poffin_starly": q.get("poffin_starly", 0),
        "poffin_kecleon": q.get("poffin_kecleon", 0),
    }


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str, games: int):
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": variant, "name": variant},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return variant, foe_key, _detail(rec)


def _jobs(variants, foes, games):
    workers = min(WORKERS, max(1, len(variants) * len(foes)))
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run, variant, names, foe_key, foe_names, foe_strat, games)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in foes
        ]
        for fut in as_completed(futs):
            variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            poffin = detail["poffin_clef"] + detail["poffin_ledyba"] + detail["poffin_starly"] + detail["poffin_kecleon"]
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  poffin {poffin} party {detail['party_games']} gust {detail['gust_games']}",
                flush=True,
            )
    return {variant: {key: cells[variant][key] for key, *_ in foes} for variant, _ in variants}


def _weighted(cells, baseline, foe_keys):
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        variant: sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
        for variant, row in cells.items()
    }


def main() -> None:
    started = time.perf_counter()
    base = list(SET_G_FRIDAY_NAMES)
    variants: list[tuple[str, list[str]]] = []
    for key, cuts, adds in VARIANTS:
        out = list(base)
        for name in cuts:
            out.remove(name)
        out.extend(adds)
        assert len(out) == 60, (key, len(out))
        bad = copy_violations(build_fallback_deck(out), standard_60_rules())
        assert not bad, (key, bad)
        variants.append((key, out))

    print(f"=== followup {GAMES} games ===", flush=True)
    cells = _jobs(variants, FOES, GAMES)
    foe_keys = tuple(k for k, *_ in FOES)
    w_all = _weighted(cells, cells["baseline"], foe_keys)
    w_comp = _weighted(cells, cells["baseline"], COMPETITIVE)

    screen_foes = tuple(f for f in FOES if f[0] in SCREEN_FOES)
    print(f"=== confirm {GAMES_CONFIRM} games ===", flush=True)
    confirm = _jobs(variants, screen_foes, GAMES_CONFIRM)
    c_all = _weighted(confirm, confirm["baseline"], SCREEN_FOES)
    c_comp = _weighted(confirm, confirm["baseline"], COMPETITIVE)

    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "games_confirm": GAMES_CONFIRM,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "variants": {k: {"cuts": list(c), "adds": list(a)} for k, c, a in VARIANTS},
        "lists": {k: names for k, names in variants},
        "cells": cells,
        "weighted_all": w_all,
        "weighted_competitive": w_comp,
        "confirm": confirm,
        "confirm_weighted": c_all,
        "confirm_weighted_competitive": c_comp,
    }
    dest = ROOT / "data/lab/set-g-poffin-followup.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("weighted_all", {k: round(v, 4) for k, v in sorted(w_all.items(), key=lambda kv: -kv[1])})
    print("weighted_comp", {k: round(v, 4) for k, v in sorted(w_comp.items(), key=lambda kv: -kv[1])})
    print("confirm", {k: round(v, 4) for k, v in sorted(c_all.items(), key=lambda kv: -kv[1])})
    print("confirm_comp", {k: round(v, 4) for k, v in sorted(c_comp.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
