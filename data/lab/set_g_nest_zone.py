#!/usr/bin/env python3
"""Carpet Set G: Nest Ball / Clefable ex / Energy Switch / Switch arrive, stay at 60.

Base is the frozen Poffin lock (SET_G_POFFIN_NAMES). Ten cards in, ten cards out.
Rule: s60. Seed 20260921. G is always player A; first player is random.
G uses dedicated `g` (one Lunar Zone, Nest fetches Munkidori / Flutter Mane,
Switch only when a bench attacker should be Active).

Stage 1: named 10-for-10 packages, full field, 2000 games.
Stage 2: confirm baseline + top competitive + top all-field at 3000 games.
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
    SET_G_POFFIN_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES_FINAL = 2000
GAMES_CONFIRM = 3000
SEED = 20260921
WORKERS = 4

ADDS = (
    ["Nest Ball"] * 4
    + ["Clefable ex"] * 3
    + ["Energy Switch"]
    + ["Switch"] * 2
)

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

# 10 cuts for the 10 arrivals. Do not cut Clefairy, Mega, Ultra Ball, Poffin,
# Boss, or the Energy Switch already in the list (the arrival is the second copy).
PACKAGES = (
    (
        "flex_out",
        (
            "Surfer",
            "Tulip",
            "Drayton",
            "Iris's Fighting Spirit",
            "Energy Retrieval",
            "Trekking Shoes",
            "Energy Search",
            "Kecleon",
            "Flutter Mane",
            "Boomerang Energy",
        ),
    ),
    (
        "keep_draw",
        (
            "Surfer",
            "Tulip",
            "Energy Retrieval",
            "Trekking Shoes",
            "Energy Search",
            "Kecleon",
            "Flutter Mane",
            "Boomerang Energy",
            "Psychic Energy",
            "Psychic Energy",
        ),
    ),
    (
        "keep_flutter",
        (
            "Surfer",
            "Tulip",
            "Drayton",
            "Iris's Fighting Spirit",
            "Energy Retrieval",
            "Trekking Shoes",
            "Energy Search",
            "Kecleon",
            "Boomerang Energy",
            "Psychic Energy",
        ),
    ),
    (
        "keep_search",
        (
            "Surfer",
            "Tulip",
            "Drayton",
            "Iris's Fighting Spirit",
            "Energy Retrieval",
            "Kecleon",
            "Flutter Mane",
            "Boomerang Energy",
            "Psychic Energy",
            "Psychic Energy",
        ),
    ),
    (
        "bird_thin",
        (
            "Starly",
            "Staravia",
            "Staraptor",
            "Surfer",
            "Kecleon",
            "Boomerang Energy",
            "Flutter Mane",
            "Energy Search",
            "Trekking Shoes",
            "Tulip",
        ),
    ),
    (
        "ledian_thin",
        (
            "Ledian",
            "Ledian",
            "Ledyba",
            "Ledyba",
            "Surfer",
            "Kecleon",
            "Boomerang Energy",
            "Flutter Mane",
            "Energy Search",
            "Trekking Shoes",
        ),
    ),
    (
        "psychic3",
        (
            "Psychic Energy",
            "Psychic Energy",
            "Psychic Energy",
            "Surfer",
            "Energy Search",
            "Trekking Shoes",
            "Energy Retrieval",
            "Kecleon",
            "Boomerang Energy",
            "Tulip",
        ),
    ),
    (
        "dark_out",
        (
            "Munkidori",
            "Munkidori",
            "Darkness Energy",
            "Darkness Energy",
            "Darkness Energy",
            "Surfer",
            "Kecleon",
            "Flutter Mane",
            "Boomerang Energy",
            "Energy Search",
        ),
    ),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "lunar_zone_play", "key": "zone"},
    {"type": "event_prefix", "prefix": "attack:Clefable ex", "key": "moon"},
    {"type": "event_prefix", "prefix": "tutor:Munkidori:nest ball", "key": "nest_munk"},
    {"type": "event_prefix", "prefix": "tutor:Clefairy:nest ball", "key": "nest_clef"},
    {"type": "event_prefix", "prefix": "switch", "key": "rotate"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex", "key": "mega"},
]


def apply_cuts_adds(names: list[str], cuts: tuple[str, ...] | list[str], adds: tuple[str, ...] | list[str]) -> list[str]:
    out = list(names)
    for name in cuts:
        out.remove(name)
    out.extend(list(adds))
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards, want 60 (cuts={cuts})")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return out


def arrive(cuts: tuple[str, ...] | list[str]) -> list[str]:
    if len(cuts) != len(ADDS):
        raise ValueError(f"need {len(ADDS)} cuts, got {len(cuts)}")
    return apply_cuts_adds(list(SET_G_POFFIN_NAMES), cuts, ADDS)


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
        "zone_games": q.get("zone", 0),
        "moon_games": q.get("moon", 0),
        "nest_munk": q.get("nest_munk", 0),
        "nest_clef": q.get("nest_clef", 0),
        "rotate_games": q.get("rotate", 0),
        "adrena_games": q.get("adrena", 0),
        "mega_games": q.get("mega", 0),
    }


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str, games: int) -> tuple[str, str, dict]:
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


def _jobs(variants: list[tuple[str, list[str]]], foes: tuple, games: int):
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
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"zone {detail['zone_games']} moon {detail['moon_games']} "
                f"nest_munk {detail['nest_munk']} party {detail['party_games']} "
                f"rotate {detail['rotate_games']}",
                flush=True,
            )
    return {variant: {key: cells[variant][key] for key, *_ in foes} for variant, _ in variants}


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    out: dict[str, float] = {}
    for variant, row in cells.items():
        out[variant] = sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
    return out


def main() -> None:
    started = time.perf_counter()
    base = list(SET_G_POFFIN_NAMES)
    assert len(base) == 60
    assert base.count("Buddy-Buddy Poffin") == 4
    assert base.count("Nest Ball") == 0
    assert base.count("Clefable ex") == 0
    assert base.count("Switch") == 0
    assert base.count("Energy Switch") == 1
    for key, cuts in PACKAGES:
        names = arrive(cuts)
        assert names.count("Nest Ball") == 4, key
        assert names.count("Clefable ex") == 3, key
        assert names.count("Switch") == 2, key
        assert names.count("Energy Switch") == 2, key

    variants: list[tuple[str, list[str]]] = [("baseline", base)]
    for key, cuts in PACKAGES:
        variants.append((key, arrive(cuts)))

    print(f"=== packages {GAMES_FINAL} games, {len(variants)} lists ===", flush=True)
    final = _jobs(variants, FOES, GAMES_FINAL)
    foe_keys = tuple(k for k, *_ in FOES)
    final_w = _weighted(final, final["baseline"], foe_keys)
    comp_w = _weighted(final, final["baseline"], COMPETITIVE)
    ranked_all = sorted(final_w.items(), key=lambda kv: -kv[1])
    ranked_comp = sorted(comp_w.items(), key=lambda kv: -kv[1])
    top_all = next(k for k, _ in ranked_all if k != "baseline")
    top_comp = next(k for k, _ in ranked_comp if k != "baseline")
    confirm_keys = list(dict.fromkeys(["baseline", top_comp, top_all]))
    confirm_variants = [(k, names) for k, names in variants if k in confirm_keys]

    print(f"=== confirm {GAMES_CONFIRM} games, {confirm_keys} ===", flush=True)
    confirm_foes = FOES
    confirm = _jobs(confirm_variants, confirm_foes, GAMES_CONFIRM)
    confirm_w = _weighted(confirm, confirm["baseline"], foe_keys)
    confirm_comp = _weighted(confirm, confirm["baseline"], COMPETITIVE)

    elapsed = time.perf_counter() - started
    out = {
        "games_final": GAMES_FINAL,
        "games_confirm": GAMES_CONFIRM,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "source": "SET_G_POFFIN_NAMES + 4 Nest Ball + 3 Clefable ex + 1 Energy Switch + 2 Switch",
        "adds": ADDS,
        "poffin_g": base,
        "poffin_g_counts": Counter(base).most_common(),
        "packages": {key: list(cuts) for key, cuts in PACKAGES},
        "lists": {k: names for k, names in variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "cells": final,
        "weighted_all": final_w,
        "weighted_competitive": comp_w,
        "confirm_keys": confirm_keys,
        "confirm": confirm,
        "confirm_weighted": confirm_w,
        "confirm_weighted_competitive": confirm_comp,
    }
    dest = ROOT / "data/lab/set-g-nest-zone.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("weighted_all", {k: round(v, 4) for k, v in ranked_all})
    print("weighted_competitive", {k: round(v, 4) for k, v in ranked_comp})
    print("confirm_all", {k: round(v, 4) for k, v in sorted(confirm_w.items(), key=lambda kv: -kv[1])})
    print("confirm_competitive", {k: round(v, 4) for k, v in sorted(confirm_comp.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
