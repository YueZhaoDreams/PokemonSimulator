#!/usr/bin/env python3
"""Locked Kecleon vs the household 60-card field.

Both seats. Standard 60, six prizes. The printed Colorful Whip, Scoundrel Ring,
Poké Radar, and Teammates sentences are what the games use.
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_KECLEON_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_kecleon_deck,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "phantom"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "slash"),
    ("g", "Carpet Set G", SET_G_NAMES, "g"),
)

GAMES = int(os.environ.get("KECLEON_GAMES", "200"))
SEED = int(os.environ.get("KECLEON_SEED", "20261115"))
WORKERS = int(os.environ.get("KECLEON_WORKERS", str(min(6, os.cpu_count() or 2))))
QUERIES = [
    {"type": "event_prefix", "prefix": "colorful_whip", "key": "whip"},
    {"type": "event_sum", "prefix": "colorful_whip_types", "key": "whip_types"},
    {"type": "event_sum", "prefix": "scoundrel_ring", "key": "ring"},
    {"type": "event_prefix", "prefix": "teammates", "key": "teammates"},
    {"type": "event_prefix", "prefix": "flip_the_script", "key": "fez"},
    {"type": "event_prefix", "prefix": "poke_radar", "key": "radar"},
]
DEST = ROOT / "data/lab/kecleon-lock.json"


def _cell(seat: str, foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    kecleon = build_kecleon_deck()
    foe = build_fallback_deck(list(foe_names))
    if seat == "a":
        cards_a, cards_b = kecleon, foe
        strat_a, strat_b = "kecleon", foe_strat
    else:
        cards_a, cards_b = foe, kecleon
        strat_a, strat_b = foe_strat, "kecleon"
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=GAMES,
        seed=SEED + (0 if seat == "a" else 17),
        queries=QUERIES,
        deck_a_meta={"id": "kecleon" if seat == "a" else foe_key, "name": "Kecleon" if seat == "a" else foe_key},
        deck_b_meta={"id": foe_key if seat == "a" else "kecleon", "name": foe_key if seat == "a" else "Kecleon"},
    )
    results = rec["results"]
    rate = results["win_rate_a"] if seat == "a" else results["win_rate_b"]
    return seat, foe_key, {
        "win_rate": rate,
        "games": results.get("games") or GAMES,
        "queries": results.get("queries") or {},
        "query_counts": results.get("query_counts") or {},
    }


def main() -> None:
    if len(SET_KECLEON_NAMES) != 60:
        raise SystemExit(f"Kecleon is {len(SET_KECLEON_NAMES)} cards")
    started = time.perf_counter()
    cells: dict[str, dict] = {}
    jobs = [(seat, key, names, strat) for key, _label, names, strat in FOES for seat in ("a", "b")]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(_cell, seat, key, names, strat) for seat, key, names, strat in jobs]
        for fut in as_completed(futures):
            seat, key, row = fut.result()
            cells.setdefault(key, {})[seat] = row
            print(f"{key} seat {seat}: {row['win_rate']:.3f}", flush=True)
    report = []
    for key, label, _names, strat in FOES:
        a = cells[key]["a"]["win_rate"]
        b = cells[key]["b"]["win_rate"]
        report.append(
            {
                "key": key,
                "name": label,
                "foe_strategy": strat,
                "kecleon_as_a": a,
                "kecleon_as_b": b,
                "mean": (a + b) / 2,
                "a": cells[key]["a"],
                "b": cells[key]["b"],
            }
        )
    payload = {
        "deck": "Kecleon",
        "cards": list(SET_KECLEON_NAMES),
        "games_per_seat": GAMES,
        "seed": SEED,
        "rules": "standard_60",
        "seconds": round(time.perf_counter() - started, 1),
        "mean": sum(row["mean"] for row in report) / len(report),
        "field": report,
    }
    DEST.write_text(json.dumps(payload, indent=2))
    print(json.dumps({"mean": payload["mean"], "seconds": payload["seconds"], "field": [
        {"key": row["key"], "mean": row["mean"]} for row in report
    ]}, indent=2))


if __name__ == "__main__":
    main()
