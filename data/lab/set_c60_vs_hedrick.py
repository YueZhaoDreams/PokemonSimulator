#!/usr/bin/env python3
"""C60 vs Worlds-2026-shaped Dragapult (engine-playable Hedrick list)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T_META_NAMES, build_fallback_deck

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260911


def main() -> None:
    started = time.perf_counter()
    a = build_fallback_deck(list(SET_C60_NAMES))
    b = build_fallback_deck(list(SET_T_META_NAMES))
    rec = run_simulation(
        a,
        b,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        games=GAMES,
        seed=SEED,
        queries=[],
        deck_a_meta={"id": "c60", "name": "Set C Standard 60 (Clefairy / Mewtwo)"},
        deck_b_meta={"id": "t_meta", "name": "Hedrick-shaped Dragapult 60"},
    )
    r = rec["results"]
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "c60": list(SET_C60_NAMES),
        "t_meta": list(SET_T_META_NAMES),
        "cell": {
            "a": r["win_rate_a"],
            "b": r["win_rate_b"],
            "tie": r["tie_rate"],
            "first": r["win_rate_a_going_first"],
            "second": r["win_rate_a_going_second"],
            "foe_strat": "phantom",
        },
    }
    dest = ROOT / "data/lab/set-c60-vs-hedrick.json"
    dest.write_text(json.dumps(out, indent=2))
    print(
        f"C60 vs Hedrick-shaped T: {r['win_rate_a']:.1%}  "
        f"(first {r['win_rate_a_going_first']:.1%} / second {r['win_rate_a_going_second']:.1%})",
        flush=True,
    )
    print(f"elapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
