#!/usr/bin/env python3
"""Which of this C60 shipment belongs in four-Psychic Carpet Set G.

Base is live SET_G_NAMES (Telepathic list plus 2 Ledian, 1 Ledyba, and
1 Munkidori swapped for Psychic Energy). Arrivals:

- 2 Lillie (draw until 6, or 8 on your first turn)
- 1 Night Stretcher
- 1 Ultra Ball (G already has 1)
- 2 Poké Pad
- 2 Rebel Clash Prankish Clefable

Each Pokémon cut has the same slot paid with a Psychic Energy. Lillie
replaces Iris or Drayton. Stretcher replaces Energy Retrieval. The slice
is C60's count of this box: 2 Lillie, 1 Stretcher, a second Ultra Ball,
1 Pad, 1 Prankish.

Seeds 20260926 and 20260927. Games per seed from LAB_GAMES (default 3,000).
Side A is strategy g.
"""

from __future__ import annotations

import json
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
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    fallback_named,
)

GAMES = int(os.environ.get("LAB_GAMES", "3000"))
SEEDS = (20260926, 20260927)
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
    {"type": "event_prefix", "prefix": "prankish", "key": "prankish"},
    {"type": "event_prefix", "prefix": "poke_pad_hit_a", "key": "pad"},
    {"type": "event_prefix", "prefix": "night_stretcher", "key": "stretcher"},
    {"type": "event_prefix", "prefix": "ultra_ball_hit", "key": "ultra"},
    {"type": "event_prefix", "prefix": "drayton", "key": "drayton"},
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


def control_lists() -> list[tuple[str, list[str]]]:
    """Same cuts as the Lillie rows, paid with Psychic Energy instead."""
    base = list(SET_G_NAMES)
    return [
        ("iris_energy", _replace(base, [("Iris's Fighting Spirit", "Psychic Energy")])),
        ("drayton_energy", _replace(base, [("Drayton", "Psychic Energy")])),
    ]


def g_lists() -> list[tuple[str, list[str]]]:
    base = list(SET_G_NAMES)
    draw2 = [
        ("Iris's Fighting Spirit", "Lillie"),
        ("Drayton", "Lillie"),
    ]
    draw_str = draw2 + [("Energy Retrieval", "Night Stretcher")]
    return [
        ("base", base),
        ("lillie_iris", _replace(base, [("Iris's Fighting Spirit", "Lillie")])),
        ("lillie_drayton", _replace(base, [("Drayton", "Lillie")])),
        ("lillie2", _replace(base, draw2)),
        ("stretcher", _replace(base, [("Energy Retrieval", "Night Stretcher")])),
        ("pad", _replace(base, [("Ledyba", "Poké Pad")])),
        ("ledyba_energy", _replace(base, [("Ledyba", "Psychic Energy")])),
        ("ultra", _replace(base, [("Ledian", "Ultra Ball")])),
        ("ledian_energy", _replace(base, [("Ledian", "Psychic Energy")])),
        ("prank", _replace(base, [("Munkidori", "Clefable")])),
        ("munk_energy", _replace(base, [("Munkidori", "Psychic Energy")])),
        (
            "slice",
            _replace(
                base,
                draw_str
                + [
                    ("Darkness Energy", "Ultra Ball"),
                    ("Psychic Energy", "Poké Pad"),
                    ("Ledian", "Clefable"),
                ],
            ),
        ),
    ]


def _check_lists() -> None:
    lists = dict(g_lists())
    base = Counter(lists["base"])
    assert base["Psychic Energy"] == 19
    assert base["Ledian"] == 2 and base["Ledyba"] == 3 and base["Munkidori"] == 1
    assert Counter(lists["lillie_iris"]) - base == Counter({"Lillie": 1})
    assert base - Counter(lists["lillie_iris"]) == Counter({"Iris's Fighting Spirit": 1})
    assert Counter(lists["stretcher"])["Night Stretcher"] == 1
    assert Counter(lists["stretcher"])["Energy Retrieval"] == 0
    assert Counter(lists["pad"])["Poké Pad"] == 1 and Counter(lists["pad"])["Ledyba"] == 2
    assert Counter(lists["ultra"])["Ultra Ball"] == 2 and Counter(lists["ultra"])["Ledian"] == 1
    assert Counter(lists["prank"])["Clefable"] == 1 and Counter(lists["prank"])["Munkidori"] == 0
    sl = Counter(lists["slice"])
    assert sl["Lillie"] == 2 and sl["Night Stretcher"] == 1
    assert sl["Ultra Ball"] == 2 and sl["Poké Pad"] == 1 and sl["Clefable"] == 1
    assert "prankish" in (fallback_named("Clefable").abilities[0].name or "").lower()
    assert "until you have 6" in (fallback_named("Lillie").text or "").lower()
    assert "discard 2" in (fallback_named("Ultra Ball").text or "").lower()
    assert "rule box" in (fallback_named("Poké Pad").text or "").lower()
    assert "discard pile" in (fallback_named("Night Stretcher").text or "").lower()


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
    wins = round(r["win_rate_a"] * GAMES)
    detail = {"wins": wins, "games": GAMES}
    for key in ("party", "prankish", "pad", "stretcher", "ultra", "drayton"):
        detail[key] = q.get(key, 0)
    return variant, foe_key, seed, detail


def _weighted(rates: dict[str, dict[str, float]], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - rates["base"][key]) for key in foe_keys}
    wsum = sum(weights.values())
    return {
        variant: sum(row[key] * weights[key] for key in foe_keys) / wsum for variant, row in rates.items()
    }


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
    payload = {
        "games_per_seed": GAMES,
        "seeds": list(SEEDS),
        "base": "SET_G_NAMES four Psychic",
        "elapsed": round(time.perf_counter() - started, 1),
        "lists": {variant: names for variant, names in variants},
        "cells": ordered,
        "weighted_all": _weighted(rates, foe_keys),
        "weighted_competitive": _weighted(rates, COMPETITIVE),
    }
    out = ROOT / "data" / "lab" / "set-g-four-psychic-arrival.json"
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} in {payload['elapsed']}s", flush=True)
    header = "variant".ljust(16) + "".join(key.rjust(9) for key in foe_keys) + "   wComp    wAll"
    print(header, flush=True)
    for variant, _ in variants:
        line = variant.ljust(16) + "".join(f"{rates[variant][key]:9.1%}" for key in foe_keys)
        line += f" {payload['weighted_competitive'][variant]:7.1%} {payload['weighted_all'][variant]:7.1%}"
        print(line, flush=True)


if __name__ == "__main__":
    main()
