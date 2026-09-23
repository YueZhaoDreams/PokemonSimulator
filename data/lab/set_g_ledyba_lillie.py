#!/usr/bin/env python3
"""Ledyba → Psychic and Iris's Fighting Spirit → Lillie, alone and together.

The matrix base is the four-Psychic list (Telepathic lock, then 2 Ledian,
1 Ledyba, and 1 Munkidori paid as Psychic). Live SET_G_NAMES is the
ledyba_energy row. The two swaps were previously measured on separate lists.
This run puts them in one 60.

- lillie_iris: Iris's Fighting Spirit → Lillie
- ledyba_energy: one Ledyba → Psychic Energy
- both: those two swaps in the same list
- both_energy: the same Ledyba cut, with Iris paid as Psychic Energy

Seeds 20260928 and 20260929. Games per seed from LAB_GAMES (default 3,000).
Side A is strategy g. This engine scores Lillie at 17+(cards drawn-3) for g.
"""

from __future__ import annotations

import json
import math
import os
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
    SET_G_NEST_ZONE_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    fallback_named,
)

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEEDS = (20260928, 20260929)
WORKERS = int(os.environ.get("LAB_WORKERS", "4"))

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
COMPETITIVE = ("t60", "hedrick", "d60")

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "lillie_a", "key": "lillie"},
]


def _replace(names: list[str], pairs: list[tuple[str, str]]) -> list[str]:
    out = list(names)
    for old, new in pairs:
        out[out.index(old)] = new
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(bad)
    return out


def _four_psychic_base() -> list[str]:
    """Matrix base. Live SET_G_NAMES is this list with one more Ledyba → Psychic."""
    names = list(SET_G_NEST_ZONE_NAMES)
    for old, new, n in (
        ("Psychic Energy", "Telepathic Psychic Energy", 2),
        ("Ledian", "Psychic Energy", 2),
        ("Ledyba", "Psychic Energy", 1),
        ("Munkidori", "Psychic Energy", 1),
    ):
        for _ in range(n):
            names[names.index(old)] = new
    return names


def g_lists() -> list[tuple[str, list[str]]]:
    base = _four_psychic_base()
    ledyba = ("Ledyba", "Psychic Energy")
    lillie = ("Iris's Fighting Spirit", "Lillie")
    iris_energy = ("Iris's Fighting Spirit", "Psychic Energy")
    return [
        ("base", base),
        ("lillie_iris", _replace(base, [lillie])),
        ("ledyba_energy", _replace(base, [ledyba])),
        ("both", _replace(base, [ledyba, lillie])),
        ("both_energy", _replace(base, [ledyba, iris_energy])),
    ]


def _check_lists() -> None:
    lists = dict(g_lists())
    base = Counter(lists["base"])
    assert base["Psychic Energy"] == 19
    assert base["Ledyba"] == 3
    assert base["Iris's Fighting Spirit"] == 1
    assert base["Lillie"] == 0
    lillie = Counter(lists["lillie_iris"])
    assert lillie["Lillie"] == 1 and lillie["Iris's Fighting Spirit"] == 0
    assert lillie["Ledyba"] == 3 and lillie["Psychic Energy"] == 19
    energy = Counter(lists["ledyba_energy"])
    assert energy["Ledyba"] == 2 and energy["Psychic Energy"] == 20
    assert energy["Iris's Fighting Spirit"] == 1 and energy["Lillie"] == 0
    both = Counter(lists["both"])
    assert both["Ledyba"] == 2 and both["Psychic Energy"] == 20
    assert both["Lillie"] == 1 and both["Iris's Fighting Spirit"] == 0
    both_e = Counter(lists["both_energy"])
    assert both_e["Ledyba"] == 2 and both_e["Psychic Energy"] == 21
    assert both_e["Lillie"] == 0 and both_e["Iris's Fighting Spirit"] == 0
    assert list(SET_G_NAMES) == lists["ledyba_energy"]
    text = (fallback_named("Lillie").text or "").lower()
    assert "until you have 6" in text and "until you have 8" in text
    iris = (fallback_named("Iris's Fighting Spirit").text or "").lower()
    assert "discard another card" in iris and "until you have 6" in iris


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str, seed: int):
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": f"g-{variant}", "name": f"g-{variant}"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    q = r.get("query_counts") or {}
    wins = int(r["wins_a"])
    return variant, foe_key, seed, {
        "wins": wins,
        "games": GAMES,
        "party": q.get("party", 0),
        "lillie": q.get("lillie", 0),
    }


def _weighted(rates: dict[str, dict[str, float]], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - rates["base"][key]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        variant: sum(row[key] * weights[key] for key in foe_keys) / wsum for variant, row in rates.items()
    }


def _z(
    rates: dict[str, dict[str, float]],
    games: dict[str, dict[str, int]],
    left: str,
    right: str,
) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - rates["base"][key]) for key in COMPETITIVE}
    wsum = sum(weights.values())

    def score(variant: str) -> float:
        return sum(rates[variant][key] * weights[key] for key in COMPETITIVE) / wsum

    def variance(variant: str) -> float:
        total = 0.0
        for key in COMPETITIVE:
            p = rates[variant][key]
            n = games[variant][key]
            total += (weights[key] / wsum) ** 2 * p * (1.0 - p) / n
        return total

    delta = score(left) - score(right)
    se = math.sqrt(variance(left) + variance(right))
    return {"delta": delta, "se": se, "z": delta / se if se else 0.0}


def main() -> None:
    _check_lists()
    started = time.perf_counter()
    variants = g_lists()
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in variants}
    jobs = [
        (variant, names, foe_key, foe_names, foe_strat, seed)
        for seed in SEEDS
        for variant, names in variants
        for foe_key, foe_names, foe_strat in FOES
    ]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        done = 0
        for fut in as_completed(futs):
            variant, foe_key, seed, detail = fut.result()
            cell = cells[variant].setdefault(foe_key, {"wins": 0, "games": 0, "by_seed": {}})
            cell["wins"] += detail["wins"]
            cell["games"] += detail["games"]
            cell["by_seed"][str(seed)] = detail
            done += 1
            print(
                f"[{done}/{len(jobs)}] {variant} vs {foe_key} seed {seed}: {detail['wins'] / GAMES:.1%}",
                flush=True,
            )
    foe_keys = tuple(key for key, *_ in FOES)
    ordered = {variant: {key: cells[variant][key] for key in foe_keys} for variant, _ in variants}
    for row in ordered.values():
        for cell in row.values():
            cell["a"] = cell["wins"] / cell["games"]
    rates = {variant: {key: row[key]["a"] for key in foe_keys} for variant, row in ordered.items()}
    games = {variant: {key: row[key]["games"] for key in foe_keys} for variant, row in ordered.items()}
    contrasts = {
        "both_minus_base": _z(rates, games, "both", "base"),
        "both_minus_lillie_iris": _z(rates, games, "both", "lillie_iris"),
        "both_minus_ledyba_energy": _z(rates, games, "both", "ledyba_energy"),
        "both_minus_both_energy": _z(rates, games, "both", "both_energy"),
        "lillie_iris_minus_base": _z(rates, games, "lillie_iris", "base"),
        "ledyba_energy_minus_base": _z(rates, games, "ledyba_energy", "base"),
    }
    payload = {
        "games_per_seed": GAMES,
        "seeds": list(SEEDS),
        "base": "SET_G_NAMES four Psychic, play corrections on",
        "engine": "Lillie scores 17+(n-3) for strategy g",
        "elapsed": round(time.perf_counter() - started, 1),
        "lists": {variant: names for variant, names in variants},
        "cells": ordered,
        "weighted_all": _weighted(rates, foe_keys),
        "weighted_competitive": _weighted(rates, COMPETITIVE),
        "contrasts": contrasts,
    }
    out = ROOT / "data" / "lab" / "set-g-ledyba-lillie.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed']}s", flush=True)
    header = "variant".ljust(16) + "".join(key.rjust(9) for key in foe_keys) + "   wComp    wAll"
    print(header, flush=True)
    for variant, _ in variants:
        line = variant.ljust(16) + "".join(f"{rates[variant][key]:9.1%}" for key in foe_keys)
        line += f" {payload['weighted_competitive'][variant]:7.1%} {payload['weighted_all'][variant]:7.1%}"
        print(line, flush=True)
    for name, row in contrasts.items():
        print(f"{name}: {row['delta']:+.4%} z {row['z']:+.2f}", flush=True)


if __name__ == "__main__":
    main()
