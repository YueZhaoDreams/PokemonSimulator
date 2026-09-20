#!/usr/bin/env python3
"""Live seed-g swaps: Tornadus / Oranguru vs Mewtwo, household 60s.

Rule: s60. Multiple seeds. G is always player A. Do not write seed-g.
Adds use printed Stellar Crown Tornadus 120 and Surging Sparks Oranguru.
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
from app.seed_data import fallback_named

ROOT = Path(__file__).resolve().parents[2]
GAMES = 2000
SEEDS = (20260912, 20260913, 20260914)
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
    {"type": "event_prefix", "prefix": "now_youre_in_my_power", "key": "power"},
    {"type": "event_prefix", "prefix": "storm_barrier", "key": "barrier"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
    {"type": "event_prefix", "prefix": "attack:Oranguru", "key": "oranguru"},
    {"type": "event_prefix", "prefix": "attack:Mewtwo", "key": "mewtwo"},
    {"type": "event_prefix", "prefix": "attack:", "key": "attacked"},
]
VARIANTS = (
    ("baseline", (), ()),
    ("tornadus", ("Mewtwo",), ("Tornadus",)),
    ("oranguru", ("Mewtwo",), ("Oranguru",)),
    ("both-flutter", ("Mewtwo", "Flutter Mane"), ("Tornadus", "Oranguru")),
    ("both-kecleon", ("Mewtwo", "Kecleon"), ("Tornadus", "Oranguru")),
    ("both-cramorant", ("Mewtwo", "Hop's Cramorant"), ("Tornadus", "Oranguru")),
)


def _hydrate(deck_id: str) -> list[Card]:
    deck = get_deck(deck_id)
    if deck is None:
        raise SystemExit(f"missing live deck {deck_id}")
    return [Card.from_dict(c) for c in deck["cards"]]


def _take_named(pool: list[Card], name: str) -> Card:
    for i, card in enumerate(pool):
        if card.name == name:
            return pool.pop(i)
    raise SystemExit(f"{name} not in pool")


def _swap(g_cards: list[Card], cuts: tuple[str, ...], adds: tuple[str, ...]) -> tuple[list[Card], dict]:
    leftover = list(g_cards)
    removed = [_take_named(leftover, name) for name in cuts]
    added = [fallback_named(name) for name in adds]
    plus = leftover + added
    rules = standard_60_rules()
    if len(plus) != 60:
        raise SystemExit(f"{cuts}->{adds} is {len(plus)} cards")
    bad = copy_violations(plus, rules)
    if bad:
        raise SystemExit(f"{cuts} copy cap: {bad}")
    return plus, {
        "cut": [f"{c.name} {c.catalog_id}" for c in removed],
        "add": [f"{c.name} {c.catalog_id}" for c in added],
        "counts": Counter(c.name for c in plus).most_common(),
    }


def _run(
    label: str,
    foe_key: str,
    foe_id: str,
    foe_strat: str,
    plus_dicts: list[dict],
    foe_dicts: list[dict],
    seed: int,
) -> tuple[str, str, dict]:
    rec = run_simulation(
        [Card.from_dict(c) for c in plus_dicts],
        [Card.from_dict(c) for c in foe_dicts],
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": "g-to", "name": label},
        deck_b_meta={"id": foe_id, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    return label, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "party_games": q.get("party", 0),
        "gust_games": q.get("gust", 0),
        "power_games": q.get("power", 0),
        "barrier_games": q.get("barrier", 0),
        "tornadus_games": q.get("tornadus", 0),
        "oranguru_games": q.get("oranguru", 0),
        "mewtwo_games": q.get("mewtwo", 0),
    }


def _simulate(label: str, plus_dicts: list[dict], foes: dict[str, list[dict]], seed: int) -> tuple[float, dict]:
    cells: dict[str, dict] = {}
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(6, len(FOES))) as pool:
        futs = [
            pool.submit(_run, label, key, deck_id, strat, plus_dicts, foes[key], seed)
            for key, deck_id, strat in FOES
        ]
        for fut in as_completed(futs):
            _lab, key, detail = fut.result()
            cells[key] = detail
            print(
                f"{label} seed {seed} vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"power {detail['power_games']} barrier {detail['barrier_games']} "
                f"tornadus {detail['tornadus_games']} oranguru {detail['oranguru_games']}",
                flush=True,
            )
    ordered = {key: cells[key] for key, *_ in FOES}
    return time.perf_counter() - started, ordered


def _mean(rows: list[list[float]]) -> list[float]:
    n = len(rows)
    width = len(rows[0])
    return [sum(row[i] for row in rows) / n for i in range(width)]


def main() -> None:
    g_cards = _hydrate("seed-g")
    if len(g_cards) != 60:
        raise SystemExit(f"seed-g is {len(g_cards)} cards")
    foes: dict[str, list[dict]] = {}
    for key, deck_id, _strat in FOES:
        foes[key] = [c.to_dict() for c in _hydrate(deck_id)]
        if len(foes[key]) != 60:
            raise SystemExit(f"{deck_id} is {len(foes[key])} cards")
    dest = ROOT / "data/lab/set-g-tornadus-oranguru-s60.json"
    out: dict = {
        "games": GAMES,
        "seeds": list(SEEDS),
        "rule_preset": "s60",
        "g_strategy": "g",
        "source": "live data/app.db seed-g + fallback Tornadus/Oranguru",
        "foes": [key for key, *_ in FOES],
        "variants": {},
        "elapsed": 0.0,
    }
    if dest.exists():
        prev = json.loads(dest.read_text())
        if prev.get("games") == GAMES and prev.get("seeds") == list(SEEDS):
            out["variants"] = prev.get("variants") or {}
            out["elapsed"] = float(prev.get("elapsed") or 0)
            print(f"resume {len(out['variants'])} variants from {dest}", flush=True)

    def _save() -> None:
        dest.write_text(json.dumps(out, indent=2))

    for label, cuts, adds in VARIANTS:
        row = out["variants"].setdefault(label, {"seeds": {}, "swap": None})
        if cuts or adds:
            plus, meta = _swap(g_cards, cuts, adds)
            row["swap"] = meta
        else:
            plus = list(g_cards)
            row["swap"] = {"cut": [], "add": [], "counts": Counter(c.name for c in plus).most_common()}
        plus_dicts = [c.to_dict() for c in plus]
        for seed in SEEDS:
            key = str(seed)
            if key in row["seeds"]:
                print(f"skip {label} {seed}", flush=True)
                continue
            took, cells = _simulate(label, plus_dicts, foes, seed)
            out["elapsed"] += took
            row["seeds"][key] = {
                "elapsed": took,
                "win_rate_a": [cells[foe]["a"] for foe, *_ in FOES],
                "cells": cells,
            }
            rates = [row["seeds"][str(s)]["win_rate_a"] for s in SEEDS if str(s) in row["seeds"]]
            row["mean_win_rate_a"] = _mean(rates)
            _save()
        row["mean_win_rate_a"] = _mean([row["seeds"][str(s)]["win_rate_a"] for s in SEEDS])
        _save()

    _save()
    print(f"\nelapsed {out['elapsed']:.1f}s -> {dest}")
    print("foes", out["foes"])
    for label, *_ in VARIANTS:
        print(label, out["variants"][label]["mean_win_rate_a"])


if __name__ == "__main__":
    main()
