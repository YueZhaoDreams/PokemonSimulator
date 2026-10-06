#!/usr/bin/env python3
"""Mill stall 60 vs every household Standard 60.

s60, random seat, mill is always player A. 30-card Family Cup lists stay
out: they are a different deck size and rule preset. G30 is the 60-card
Ambipom list already in the household bakeoff.
"""

from __future__ import annotations

import json
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.game import play_game
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL60_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20261006

FOES = (
    ("c60", "C60 Clefairy / Mewtwo", SET_C60_NAMES, "party", False),
    ("m60", "M60 Mew ex baby box", SET_M60_NAMES, "mew_baby", False),
    ("d60", "D60 Charm Ogerpon", SET_D60_NAMES, "demolish", False),
    ("s60", "S60 Floragato", SET_S60_NAMES, "slash", False),
    ("t60", "T60 Dragapult", SET_T60_NAMES, "phantom", False),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom", False),
    ("unl", "UNL Pidgeot Dragapult", SET_T_UNL_NAMES, "phantom", False),
    ("l60", "L60 Lucario Hariyama", SET_L60_NAMES, "aura", False),
    ("g", "Carpet Set G", SET_G_NAMES, "g", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "G30 Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)

SUM_KEYS = (
    "mill_opponent",
    "attack:Great Tusk:Land Collapse",
    "attack:Great Tusk:Giant Tusk",
    "ancient_supporter",
    "heal_each_own",
    "max_potion",
    "tool:Hero's Cape",
    "ko:Great Tusk",
    "ko:Latias ex",
    "ko:Meowth ex",
    "ko:Radiant Tsareena",
)
GAME_KEYS = (
    "mill_opponent",
    "attack:Great Tusk:Land Collapse",
    "ancient_supporter",
    "heal_each_own",
    "max_potion",
    "saw_play:Radiant Tsareena",
    "tool:Hero's Cape",
    "saw_play:Lively Stadium",
)


def _eval(foe_key: str, games: int, seed: int) -> dict:
    label, names, strat, g30 = next(
        (label, names, strat, g30) for key, label, names, strat, g30 in FOES if key == foe_key
    )
    deck_a = build_fallback_deck(list(SET_MILL60_NAMES))
    deck_b = build_g30_deck() if g30 else build_fallback_deck(list(names))
    rules = standard_60_rules()
    strat_a = StrategySpec.from_dict("mill")
    strat_b = StrategySpec.from_dict(strat)
    rng = random.Random(seed)
    wins = ties = 0
    first_games = first_wins = 0
    second_games = second_wins = 0
    deckouts = self_deckouts = 0
    turns = prizes_a = prizes_b = 0
    mill_sum = mill_max = mill_games = 0
    reasons: Counter[str] = Counter()
    sums: Counter[str] = Counter()
    games_with: Counter[str] = Counter()
    for i in range(games):
        result = play_game(deck_a, deck_b, rules, strat_a, strat_b, rng)
        if result.winner == "a":
            wins += 1
        elif result.winner == "tie":
            ties += 1
        if result.first_player == "a":
            first_games += 1
            if result.winner == "a":
                first_wins += 1
        else:
            second_games += 1
            if result.winner == "a":
                second_wins += 1
        reasons[f"{result.winner}|{result.reason}"] += 1
        if result.reason == "b decked out":
            deckouts += 1
        elif result.reason == "a decked out":
            self_deckouts += 1
        turns += result.turns
        prizes_a += result.prizes_taken_a
        prizes_b += result.prizes_taken_b
        milled = int(result.events.get("mill_opponent") or 0)
        mill_sum += milled
        if milled:
            mill_games += 1
            if milled > mill_max:
                mill_max = milled
        for key in SUM_KEYS:
            sums[key] += int(result.events.get(key) or 0)
        for key in GAME_KEYS:
            if result.events.get(key):
                games_with[key] += 1
        if (i + 1) % 1000 == 0:
            print(f"{foe_key} {i + 1}/{games} wins {wins}", flush=True)
    return {
        "foe": foe_key,
        "label": label,
        "strategy": strat,
        "games": games,
        "wins": wins,
        "losses": games - wins - ties,
        "ties": ties,
        "first_games": first_games,
        "first_wins": first_wins,
        "second_games": second_games,
        "second_wins": second_wins,
        "deckouts": deckouts,
        "self_deckouts": self_deckouts,
        "turns": turns,
        "prizes_a": prizes_a,
        "prizes_b": prizes_b,
        "mill_sum": mill_sum,
        "mill_max": mill_max,
        "mill_games": mill_games,
        "reasons": dict(reasons),
        "sums": dict(sums),
        "games_with": dict(games_with),
    }


def main() -> None:
    games = GAMES
    seed = SEED
    if len(sys.argv) > 1:
        games = int(sys.argv[1])
    started = time.time()
    rows = []
    workers = min(4, len(FOES))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(_eval, key, games, seed): key for key, *_ in FOES}
        for fut in as_completed(futs):
            row = fut.result()
            rows.append(row)
            rate = row["wins"] / row["games"] if row["games"] else 0
            print(
                f"{row['foe']}: {row['wins']}/{row['games']} ({rate:.1%}) "
                f"deckouts {row['deckouts']} mill_avg {row['mill_sum'] / row['games']:.1f}",
                flush=True,
            )
    order = {key: i for i, (key, *_) in enumerate(FOES)}
    rows.sort(key=lambda r: order[r["foe"]])
    out = {
        "seed": seed,
        "games": games,
        "subject": "mill",
        "seat": "a",
        "elapsed": round(time.time() - started, 1),
        "rows": rows,
    }
    path = ROOT / "data/lab/mill-stall-matrix.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {path} in {out['elapsed']}s")


if __name__ == "__main__":
    main()
