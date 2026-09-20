#!/usr/bin/env python3
"""G plus + 1 Mega Clefable ex vs household 60s.

Swap one live seed-g card for Mega from live seed-c60. Rule: s60. Seed 20260912.
G is always player A. Do not compare vs Set H. Do not write seed-g.
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

ROOT = Path(__file__).resolve().parents[2]
GAMES = 2000
SEED = 20260912
# Every live 1-of, plus one Psychic Energy and one Munkidori. Leave Clefairy / Ledyba-Ledian /
# Starly line / the other Darkness Energy in place.
CUTS = (
    "Mewtwo",
    "Energy Search",
    "Hop's Cramorant",
    "Flutter Mane",
    "Indeedee",
    "Relicanth",
    "Emolga",
    "Plusle",
    "Kecleon",
    "Tulip",
    "Surfer",
    "Drayton",
    "Iris's Fighting Spirit",
    "Energy Retrieval",
    "Trekking Shoes",
    "Potion",
    "Energy Switch",
    "Poké Ball",
    "Ultra Ball",
    "Boomerang Energy",
    "Psychic Energy",
    "Munkidori",
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
    {"type": "event_prefix", "prefix": "mega_in_play", "key": "mega"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable", "key": "moons"},
    {"type": "event_prefix", "prefix": "attack:Plusle", "key": "plusle"},
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
    raise SystemExit(f"{name} not in pool")


def _swap(g_cards: list[Card], cut: str, mega: Card) -> tuple[list[Card], dict]:
    leftover = list(g_cards)
    removed = _take_named(leftover, cut)
    plus = leftover + [mega]
    rules = standard_60_rules()
    if len(plus) != 60:
        raise SystemExit(f"{cut} swap is {len(plus)} cards")
    bad = copy_violations(plus, rules)
    if bad:
        raise SystemExit(f"{cut} copy cap: {bad}")
    return plus, {
        "cut": f"{removed.name} {removed.catalog_id}",
        "add": f"{mega.name} {mega.catalog_id}",
        "counts": Counter(c.name for c in plus).most_common(),
    }


def _run(label: str, foe_key: str, foe_id: str, foe_strat: str, plus_dicts: list[dict], foe_dicts: list[dict]) -> tuple[str, str, dict]:
    rec = run_simulation(
        [Card.from_dict(c) for c in plus_dicts],
        [Card.from_dict(c) for c in foe_dicts],
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "g-mega", "name": label},
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
        "mega_games": q.get("mega", 0),
        "moons_games": q.get("moons", 0),
        "plusle_games": q.get("plusle", 0),
    }


def _simulate(label: str, plus_dicts: list[dict], foes: dict[str, list[dict]]) -> tuple[float, dict]:
    cells: dict[str, dict] = {}
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(6, len(FOES))) as pool:
        futs = [
            pool.submit(_run, label, key, deck_id, strat, plus_dicts, foes[key])
            for key, deck_id, strat in FOES
        ]
        for fut in as_completed(futs):
            _lab, key, detail = fut.result()
            cells[key] = detail
            print(
                f"{label} vs {key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"party {detail['party_games']} mega {detail['mega_games']} moons {detail['moons_games']}",
                flush=True,
            )
    ordered = {key: cells[key] for key, *_ in FOES}
    return time.perf_counter() - started, ordered


def main() -> None:
    g_cards = _hydrate("seed-g")
    mega = _take_named(_hydrate("seed-c60"), "Mega Clefable ex")
    foes: dict[str, list[dict]] = {}
    for key, deck_id, _strat in FOES:
        foes[key] = [c.to_dict() for c in _hydrate(deck_id)]
        if len(foes[key]) != 60:
            raise SystemExit(f"{deck_id} is {len(foes[key])} cards")
    dest = ROOT / "data/lab/set-g-mega-s60.json"
    out: dict = {
        "games": GAMES,
        "seed": SEED,
        "rule_preset": "s60",
        "g_strategy": "g",
        "source": "live data/app.db",
        "foes": [key for key, *_ in FOES],
        "variants": {},
    }
    elapsed = 0.0
    if dest.exists():
        prev = json.loads(dest.read_text())
        if prev.get("games") == GAMES and prev.get("seed") == SEED:
            out["variants"] = prev.get("variants") or {}
            elapsed = float(prev.get("elapsed") or 0)
            print(f"resume {len(out['variants'])} variants from {dest}", flush=True)

    def _save() -> None:
        out["elapsed"] = elapsed
        dest.write_text(json.dumps(out, indent=2))

    if "baseline" not in out["variants"]:
        base_elapsed, base_cells = _simulate("G+", [c.to_dict() for c in g_cards], foes)
        elapsed += base_elapsed
        out["variants"]["baseline"] = {
            "elapsed": base_elapsed,
            "win_rate_a": [base_cells[key]["a"] for key, *_ in FOES],
            "cells": base_cells,
        }
        _save()
    for cut in CUTS:
        if cut in out["variants"]:
            print(f"skip {cut}", flush=True)
            continue
        plus, meta = _swap(g_cards, cut, mega)
        label = f"Mega-{cut}"
        took, cells = _simulate(label, [c.to_dict() for c in plus], foes)
        elapsed += took
        out["variants"][cut] = {
            "elapsed": took,
            "swap": meta,
            "win_rate_a": [cells[key]["a"] for key, *_ in FOES],
            "cells": cells,
        }
        _save()
    _save()
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("baseline", out["variants"]["baseline"]["win_rate_a"])
    for cut in CUTS:
        print(cut, out["variants"][cut]["win_rate_a"])


if __name__ == "__main__":
    main()
