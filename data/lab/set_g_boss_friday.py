#!/usr/bin/env python3
"""Carpet Set G Friday lock: 3 Boss's Orders for Potion, Poké Ball, Plusle.

Live combocub seed-g on 2026-09-15 already had Mega Clefable ex and Tornadus
(Mewtwo / Emolga out) and 0 Boss. The bakeoff locked −Potion −Poké Ball
−Plusle +3 Boss. Repo SET_G_NAMES is that Friday list so seed-g upserts.

Rule: s60. Seed 20260915. G is always player A; first player is random.
G uses dedicated `g`. Foe `c60` uses locked SET_C60_NAMES.
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
    SET_G_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES_SCREEN = 1500
GAMES_FINAL = 2000
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
SCREEN_FOES = ("t60", "hedrick", "d60", "unl")

# Rank 1-for-1 cuts. Keep Clefairy (Party). Include C60-overlap cards so the
# numbers can show they are not the Friday cut.
CUT_ONE = (
    "Potion",
    "Poké Ball",
    "Hop's Cramorant",
    "Relicanth",
    "Kecleon",
    "Plusle",
    "Indeedee",
    "Flutter Mane",
    "Tornadus",
    "Trekking Shoes",
    "Energy Search",
    "Drayton",
    "Tulip",
    "Iris's Fighting Spirit",
    "Surfer",
    "Ledian",
    "Ledyba",
    "Staraptor",
    "Starly",
    "Staravia",
    "Munkidori",
    "Darkness Energy",
    "Boomerang Energy",
    "Psychic Energy",
    "Mega Clefable ex",
    "Energy Retrieval",
    "Energy Switch",
    "Ultra Ball",
)

# Locked Friday 3-for-3 after the bakeoff: 3 Boss for Potion / Poké Ball / Plusle.
# Confirmed 3,000 games on t60 / Hedrick / D60 / UNL (seed 20260915).
FRIDAY_CUTS = ("Potion", "Poké Ball", "Plusle")

# Named 3-for-3 packages (3 Boss in). Auto top-3 from the screen is added at run.
PACKAGES = (
    ("junk", ("Potion", "Poké Ball", "Hop's Cramorant")),
    ("plusle", FRIDAY_CUTS),
    ("relicanth", ("Potion", "Poké Ball", "Relicanth")),
    ("kecleon", ("Potion", "Poké Ball", "Kecleon")),
    ("ledian3", ("Ledian", "Ledian", "Ledian")),
    ("dark3", ("Darkness Energy", "Darkness Energy", "Darkness Energy")),
    ("ledian_junk", ("Ledian", "Potion", "Poké Ball")),
    ("supporters", ("Tulip", "Drayton", "Iris's Fighting Spirit")),
    ("search", ("Energy Search", "Poké Ball", "Potion")),
    ("line_thin", ("Ledian", "Ledyba", "Potion")),
    ("energy", ("Psychic Energy", "Potion", "Poké Ball")),
    ("tornadus", ("Tornadus", "Potion", "Poké Ball")),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "boss_orders", "key": "boss"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex", "key": "mega"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
]


def apply_cuts_adds(names: list[str], cuts: tuple[str, ...] | list[str], adds: tuple[str, ...] | list[str]) -> list[str]:
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


def friday_g_names() -> list[str]:
    return list(SET_G_NAMES)


def live_g_names() -> list[str]:
    """Pre-Friday live G: Mega + Tornadus, Potion / Poké Ball / Plusle, 0 Boss."""
    return apply_cuts_adds(list(SET_G_NAMES), ["Boss's Orders"] * 3, list(FRIDAY_CUTS))


def add_boss(names: list[str] | None, n: int, cuts: tuple[str, ...] | list[str]) -> list[str]:
    if n != len(cuts):
        raise ValueError(f"need {n} cuts for {n} Boss, got {cuts}")
    return apply_cuts_adds(list(names if names is not None else live_g_names()), cuts, ["Boss's Orders"] * n)


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
                f"boss {detail['boss_games']} gust {detail['gust_games']} party {detail['party_games']}",
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
    base = live_g_names()
    assert len(base) == 60
    assert base.count("Boss's Orders") == 0
    assert base.count("Mega Clefable ex") == 1
    assert base.count("Tornadus") == 1
    assert base.count("Mewtwo") == 0
    assert base.count("Emolga") == 0

    screen_foes = tuple(f for f in FOES if f[0] in SCREEN_FOES)
    screen_variants: list[tuple[str, list[str]]] = [("baseline", base)]
    for cut in CUT_ONE:
        screen_variants.append((f"cut:{cut}", add_boss(base, 1, (cut,))))

    print(f"=== screen {GAMES_SCREEN} games, {len(screen_variants)} lists ===", flush=True)
    screen = _jobs(screen_variants, screen_foes, GAMES_SCREEN)
    screen_w = _weighted(screen, screen["baseline"], SCREEN_FOES)
    ranked = sorted(
        ((k, screen_w[k], screen[k]) for k in screen if k != "baseline"),
        key=lambda x: -x[1],
    )
    top3 = tuple(k.split(":", 1)[1] for k, *_ in ranked[:3])
    print("top 1-for-1 weighted:", [(k, f"{w:.3f}") for k, w, _ in ranked[:8]], flush=True)
    print("auto top3 cuts:", top3, flush=True)

    packages = list(PACKAGES)
    if top3 not in {cuts for _, cuts in packages}:
        packages.append(("auto_top3", top3))
    # 2 Boss of the two best singleton cuts — in case 3 supporters brick.
    top2 = tuple(k.split(":", 1)[1] for k, *_ in ranked[:2])
    final_variants: list[tuple[str, list[str]]] = [("baseline", base)]
    final_variants.append(("boss2", add_boss(base, 2, top2)))
    for key, cuts in packages:
        final_variants.append((key, add_boss(base, 3, cuts)))

    print(f"=== packages {GAMES_FINAL} games, {len(final_variants)} lists ===", flush=True)
    final = _jobs(final_variants, FOES, GAMES_FINAL)
    foe_keys = tuple(k for k, *_ in FOES)
    final_w = _weighted(final, final["baseline"], foe_keys)
    competitive = ("t60", "hedrick", "d60")
    comp_w = _weighted(final, final["baseline"], competitive)

    elapsed = time.perf_counter() - started
    out = {
        "games_screen": GAMES_SCREEN,
        "games_final": GAMES_FINAL,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "source": "combocub.com seed-g 2026-09-15 household admin",
        "live_g": base,
        "live_g_counts": Counter(base).most_common(),
        "friday_vs_live": {"add": ["Boss's Orders"] * 3, "cut": list(FRIDAY_CUTS)},
        "screen_ranked": [
            {
                "cut": k.split(":", 1)[1],
                "weighted": w,
                "cells": row,
            }
            for k, w, row in ranked
        ],
        "auto_top3": list(top3),
        "packages": {key: list(cuts) for key, cuts in packages},
        "boss2_cuts": list(top2),
        "lists": {k: names for k, names in final_variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "screen": screen,
        "cells": final,
        "weighted_all": final_w,
        "weighted_competitive": comp_w,
    }
    dest = ROOT / "data/lab/set-g-boss-friday.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("weighted_all", {k: round(v, 4) for k, v in sorted(final_w.items(), key=lambda kv: -kv[1])})
    print("weighted_competitive", {k: round(v, 4) for k, v in sorted(comp_w.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
