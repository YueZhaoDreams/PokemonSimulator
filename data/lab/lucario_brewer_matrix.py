#!/usr/bin/env python3
"""Chris Brewer Lucario Hariyama vs every household 60.

s60, random seat, Lucario is always player A. 30-card Family Cup lists stay
out: they are a different deck size and rule preset.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260925

FOES = (
    ("c60", "C60 Clefairy / Mewtwo", SET_C60_NAMES, "party", False),
    ("m60", "M Mew ex baby box", SET_M60_NAMES, "mew_baby", False),
    ("d60", "D60 Charm Ogerpon", SET_D60_NAMES, "demolish", False),
    ("s60", "S60 Floragato", SET_S60_NAMES, "slash", False),
    ("t60", "T60 Dragapult", SET_T60_NAMES, "phantom", False),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom", False),
    ("unl", "UNL Pidgeot Dragapult", SET_T_UNL_NAMES, "phantom", False),
    ("g", "Carpet Set G", SET_G_NAMES, "g", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "G30 Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)


def _eval(foe_key: str) -> dict:
    label, names, strat, g30 = next(
        (label, names, strat, g30) for key, label, names, strat, g30 in FOES if key == foe_key
    )
    deck_a = build_fallback_deck(list(SET_L60_NAMES))
    deck_b = build_g30_deck() if g30 else build_fallback_deck(list(names))
    stats = run_simulation(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("aura"),
        StrategySpec.from_dict(strat),
        games=GAMES,
        seed=SEED,
    )
    res = stats["results"]
    return {
        "foe": foe_key,
        "label": label,
        "strategy": strat,
        "win_rate": res["win_rate_a"],
        "wins_a": res["wins_a"],
        "wins_b": res["wins_b"],
        "ties": res["ties"],
        "first": res["win_rate_a_going_first"],
        "second": res["win_rate_a_going_second"],
        "attacks": {
            k: v
            for k, v in res.get("query_counts", {}).items()
            if str(k).startswith("attack:") or str(k) in {"aura_jab_attach", "lunar_cycle", "premium_power_pro", "fighting_gong"}
        },
    }


def main() -> None:
    started = time.time()
    rows = []
    with ProcessPoolExecutor(max_workers=5) as pool:
        futs = {pool.submit(_eval, key): key for key, *_ in FOES}
        for fut in as_completed(futs):
            row = fut.result()
            rows.append(row)
            print(f"{row['foe']}: {row['win_rate']:.1%}", flush=True)
    order = {key: i for i, (key, *_) in enumerate(FOES)}
    rows.sort(key=lambda r: order[r["foe"]])
    out = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": round(time.time() - started, 1),
        "rows": rows,
    }
    path = ROOT / "data/lab/lucario-brewer-matrix.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path} in {out['elapsed']}s")


if __name__ == "__main__":
    main()
