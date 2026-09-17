#!/usr/bin/env python3
"""Carpet Set G: 4 Buddy-Buddy Poffin arrive, 3 Boss stay out for now.

Baseline is pre-Friday live G (combocub.com seed-g 2026-09-15: Mega Clefable ex
+ Tornadus, Potion / Poke Ball / Plusle, 0 Boss, 0 Poffin), frozen in
data/lab/set-g-boss-friday.json as "live_g" so this bakeoff does not drift with
SET_G_NAMES.

Printed Poffin (sv05-144): search the deck for up to 2 Basic Pokemon with 70 HP
or less and bench them. G targets: Clefairy 60, Ledyba 60, Starly 60, Kecleon 70.

Rule: s60. Seed 20260917. G is always player A; first player is random.
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

GAMES = 2000
SEED = 20260917
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

# Locked Poffin 4-for-4 after the bakeoff: Potion / Poké Ball / Plusle /
# Hop's Cramorant out, 4 Buddy-Buddy Poffin in. Boss stays out until in hand.
POFFIN_CUTS = ("Potion", "Poké Ball", "Plusle", "Hop's Cramorant")

# 4 Poffin in (poffin2 is the 2-Poffin fallback). Potion + Poke Ball + Plusle
# was the Friday Boss 3-cut; the 4th slot is the open question.
PACKAGES = (
    ("junk4", POFFIN_CUTS),
    ("relicanth4", ("Potion", "Poké Ball", "Plusle", "Relicanth")),
    ("kecleon4", ("Potion", "Poké Ball", "Plusle", "Kecleon")),
    ("indeedee4", ("Potion", "Poké Ball", "Plusle", "Indeedee")),
    ("tornadus4", ("Potion", "Poké Ball", "Plusle", "Tornadus")),
    ("shoes4", ("Potion", "Poké Ball", "Plusle", "Trekking Shoes")),
    ("drayton4", ("Potion", "Poké Ball", "Plusle", "Drayton")),
    ("search4", ("Potion", "Poké Ball", "Plusle", "Energy Search")),
    ("tulip4", ("Potion", "Poké Ball", "Plusle", "Tulip")),
    ("iris4", ("Potion", "Poké Ball", "Plusle", "Iris's Fighting Spirit")),
    ("surfer4", ("Potion", "Poké Ball", "Plusle", "Surfer")),
    ("supporters4", ("Tulip", "Drayton", "Iris's Fighting Spirit", "Surfer")),
    ("line_thin4", ("Ledian", "Ledyba", "Potion", "Poké Ball")),
    ("energy4", ("Psychic Energy", "Potion", "Poké Ball", "Plusle")),
    ("keep_plusle4", ("Potion", "Poké Ball", "Relicanth", "Kecleon")),
    ("poffin2", ("Potion", "Poké Ball")),
    ("poffin3", ("Potion", "Poké Ball", "Plusle")),
    ("rel_cram4", ("Potion", "Poké Ball", "Hop's Cramorant", "Relicanth")),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex", "key": "mega"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
    {"type": "event_prefix", "prefix": "tutor:", "key": "tutor"},
]


def baseline_g_names() -> list[str]:
    blob = json.loads((ROOT / "data/lab/set-g-boss-friday.json").read_text())
    names = list(blob["live_g"])
    counts = Counter(names)
    assert len(names) == 60
    assert counts["Boss's Orders"] == 0
    assert counts["Buddy-Buddy Poffin"] == 0
    assert counts["Potion"] == 1
    assert counts["Poké Ball"] == 1
    assert counts["Plusle"] == 1
    assert counts["Mega Clefable ex"] == 1
    assert counts["Tornadus"] == 1
    return names


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


def poffin_g_names() -> list[str]:
    return list(SET_G_NAMES)


def add_poffin(names: list[str] | None, cuts: tuple[str, ...] | list[str]) -> list[str]:
    return apply_cuts_adds(
        list(names if names is not None else baseline_g_names()),
        cuts,
        ["Buddy-Buddy Poffin"] * len(cuts),
    )


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
        "adrena_games": q.get("adrena", 0),
        "mega_games": q.get("mega", 0),
        "tornadus_games": q.get("tornadus", 0),
        "tutor_games": q.get("tutor", 0),
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


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    out: dict[str, float] = {}
    for variant, row in cells.items():
        out[variant] = sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
    return out


def main() -> None:
    started = time.perf_counter()
    base = baseline_g_names()
    variants: list[tuple[str, list[str]]] = [("baseline", base)]
    for key, cuts in PACKAGES:
        variants.append((key, add_poffin(base, cuts)))

    print(f"=== poffin packages {GAMES} games, {len(variants)} lists ===", flush=True)
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    workers = min(WORKERS, max(1, len(variants) * len(FOES)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run, variant, names, foe_key, foe_names, foe_strat, GAMES)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in FOES
        ]
        for fut in as_completed(futs):
            variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"tutor {detail['tutor_games']} party {detail['party_games']} gust {detail['gust_games']}",
                flush=True,
            )
    foe_keys = tuple(k for k, *_ in FOES)
    ordered = {variant: {key: cells[variant][key] for key in foe_keys} for variant, _ in variants}
    final_w = _weighted(ordered, ordered["baseline"], foe_keys)
    comp_w = _weighted(ordered, ordered["baseline"], ("t60", "hedrick", "d60"))

    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "source": "combocub.com seed-g 2026-09-15 pre-Friday live_g",
        "baseline": base,
        "baseline_counts": Counter(base).most_common(),
        "packages": {key: list(cuts) for key, cuts in PACKAGES},
        "lists": {k: names for k, names in variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "cells": ordered,
        "weighted_all": final_w,
        "weighted_competitive": comp_w,
    }
    dest = ROOT / "data/lab/set-g-poffin-swap.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("weighted_all", {k: round(v, 4) for k, v in sorted(final_w.items(), key=lambda kv: -kv[1])})
    print("weighted_competitive", {k: round(v, 4) for k, v in sorted(comp_w.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
