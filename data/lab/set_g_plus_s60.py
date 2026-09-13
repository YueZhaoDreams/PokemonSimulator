#!/usr/bin/env python3
"""G plus vs household 60s. After the 10-for-10, live seed-g IS G plus.

Rule: s60. Seed 20260912. G plus is always player A; who goes first is random.
Do not compare vs Set H.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.db import get_deck
from app.engine.legality import copy_violations
from app.engine.models import Card, standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import SET_G_NAMES

ROOT = Path(__file__).resolve().parents[2]
GAMES = 2000
SEED = 20260912

# Live seed-g cuts: no Party, no Psychic storm, redundant 1-ofs, Boulder (Kecleon is the Stance passenger).
CUT = (
    "Scatterbug",
    "Scatterbug",
    "Misdreavus",
    "Misdreavus",
    "Mismagius",
    "Mismagius",
    "Drifloon",
    "Drifblim",
    "Iron Boulder",
    "Dedenne",
)
# Live seed-h adds. Skip H's Clefairy (swsh2-74, no Party), Lightning attackers, extra Ledyba/Ledian.
# Locked G plus: Kecleon + Trapinch. Plusle tech: swap Trapinch for Plusle (Emolga still Call-2).
LOCKED_ADD = (
    "Indeedee",
    "Relicanth",
    "Emolga",
    "Trapinch",
    "Hop's Cramorant",
    "Kecleon",
    "Iris's Fighting Spirit",
    "Energy Retrieval",
    "Trekking Shoes",
    "Potion",
)
PLUSLE_ADD = (
    "Indeedee",
    "Relicanth",
    "Emolga",
    "Plusle",
    "Hop's Cramorant",
    "Kecleon",
    "Iris's Fighting Spirit",
    "Energy Retrieval",
    "Trekking Shoes",
    "Potion",
)
FOES = (
    ("c60", "seed-c60", "party"),
    ("d60", "seed-d60", "demolish"),
    ("t60", "seed-t60", "phantom"),
    ("hedrick", "seed-t-meta", "phantom"),
    ("unl", "seed-t-unl", "phantom"),
    ("s60", "seed-s60", "slash"),
)
QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "expert_nurturer", "key": "nurturer"},
    {"type": "event_prefix", "prefix": "into_the_deep", "key": "deep"},
    {"type": "event_prefix", "prefix": "attack:Hop's Cramorant", "key": "cramorant"},
    {"type": "event_prefix", "prefix": "attack:Plusle", "key": "plusle"},
    {"type": "event_prefix", "prefix": "attack:Kecleon", "key": "kecleon"},
    {"type": "event_prefix", "prefix": "attack:", "key": "attacked"},
]


def _hydrate(deck_id: str) -> list[Card]:
    deck = get_deck(deck_id)
    if deck is None:
        raise SystemExit(f"missing live deck {deck_id}")
    return [Card.from_dict(c) for c in deck["cards"]]


def _take_named(pool: list[Card], name: str) -> Card:
    for i, card in enumerate(pool):
        if card.name == name:
            return pool.pop(i)
    raise SystemExit(f"{name} not in live pool")


def assemble_g_plus(g_cards: list[Card], h_cards: list[Card], add: tuple[str, ...]) -> tuple[list[Card], dict]:
    leftover = list(g_cards)
    cut_cards: list[Card] = []
    for name in CUT:
        cut_cards.append(_take_named(leftover, name))
    h_pool = list(h_cards)
    added: list[Card] = []
    for name in add:
        added.append(_take_named(h_pool, name))
    plus = leftover + added
    rules = standard_60_rules()
    if len(plus) != 60:
        raise SystemExit(f"G plus is {len(plus)} cards, want 60")
    bad = copy_violations(plus, rules)
    if bad:
        raise SystemExit(f"G plus copy cap: {bad}")
    meta = {
        "cut": [f"{c.name} {c.catalog_id}" for c in cut_cards],
        "add": [f"{c.name} {c.catalog_id}" for c in added],
        "counts": Counter(c.name for c in plus).most_common(),
        "g_count": len(g_cards),
        "h_count": len(h_cards),
    }
    return plus, meta


def _run(foe_key: str, foe_id: str, foe_strat: str, plus_dicts: list[dict], foe_dicts: list[dict]) -> tuple[str, dict]:
    rec = run_simulation(
        [Card.from_dict(c) for c in plus_dicts],
        [Card.from_dict(c) for c in foe_dicts],
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "g-plus", "name": "Carpet G plus"},
        deck_b_meta={"id": foe_id, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    return foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "foe_strat": foe_strat,
        "party_games": q.get("party", 0),
        "gust_games": q.get("gust", 0),
        "adrena_games": q.get("adrena", 0),
        "nurturer_games": q.get("nurturer", 0),
        "deep_games": q.get("deep", 0),
        "cramorant_games": q.get("cramorant", 0),
        "plusle_games": q.get("plusle", 0),
        "kecleon_games": q.get("kecleon", 0),
    }


def _simulate(label: str, plus_dicts: list[dict], foes: dict[str, list[dict]]) -> tuple[float, dict]:
    cells: dict[str, dict] = {}
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(6, len(FOES))) as pool:
        futs = [
            pool.submit(_run, key, deck_id, strat, plus_dicts, foes[key])
            for key, deck_id, strat in FOES
        ]
        for fut in as_completed(futs):
            key, detail = fut.result()
            cells[key] = detail
            print(
                f"{label} vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"party {detail['party_games']} gust {detail['gust_games']} "
                f"nurturer {detail['nurturer_games']} cramorant {detail['cramorant_games']} "
                f"plusle {detail.get('plusle_games', 0)} kecleon {detail.get('kecleon_games', 0)}",
                flush=True,
            )
    ordered = {key: cells[key] for key, *_ in FOES}
    return time.perf_counter() - started, ordered


def main() -> None:
    g_cards = _hydrate("seed-g")
    have = Counter(c.name for c in g_cards)
    want = Counter(SET_G_NAMES)
    if have != want:
        raise SystemExit(f"seed-g is not the locked G plus 10-10: {have - want} extra, {want - have} missing")
    plus_dicts = [c.to_dict() for c in g_cards]
    foes: dict[str, list[dict]] = {}
    for key, deck_id, _strat in FOES:
        foes[key] = [c.to_dict() for c in _hydrate(deck_id)]
        if len(foes[key]) != 60:
            raise SystemExit(f"{deck_id} is {len(foes[key])} cards")
    dest = ROOT / "data/lab/set-g-plus-s60.json"
    elapsed, cells = _simulate("G+", plus_dicts, foes)
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "g_strategy": "g",
        "source": "live data/app.db seed-g",
        "foes": [key for key, *_ in FOES],
        "cells": cells,
        "win_rate_a": [cells[key]["a"] for key, *_ in FOES],
        "counts": have.most_common(),
    }
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("win_rate_a", out["win_rate_a"])


if __name__ == "__main__":
    main()
