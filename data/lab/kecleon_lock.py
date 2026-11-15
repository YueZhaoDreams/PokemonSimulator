#!/usr/bin/env python3
"""Locked Kecleon vs every household set.

Both seats. A 60-card list uses Standard 60. A 30-card list uses that set's own
rules: Family Cup when the list is built on Pokémon-as-energy, otherwise the
30-card rules that set is registered with. The printed Colorful Whip, Scoundrel
Ring, Poké Radar, and Teammates sentences are what the games use.
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

from app.engine.models import (
    default_family_rules,
    no_pokemon_energy_family_rules,
    standard_30_rules,
    standard_60_rules,
)
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_A_NAMES,
    SET_B_NAMES,
    SET_C_NAMES,
    SET_C60_NAMES,
    SET_D_NAMES,
    SET_D60_NAMES,
    SET_DOLL_NAMES,
    SET_E_NAMES,
    SET_F_NAMES,
    SET_G_NAMES,
    SET_G30_NAMES,
    SET_H_NAMES,
    SET_KECLEON_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_ROAST_NAMES,
    SET_ROAST_TWO_FOREST_NAMES,
    SET_S_NAMES,
    SET_S60_NAMES,
    SET_T_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_kecleon_deck,
)

# key, label, names, rules, foe strategy
FOES = (
    ("c60", "Set C Standard 60 (Clefairy / Mewtwo)", SET_C60_NAMES, "s60", "party"),
    ("h", "Carpet Set H (Team Rocket's Zapdos)", SET_H_NAMES, "s60", "nuzzle"),
    ("m60", "Set M (Mew ex)", SET_M60_NAMES, "s60", "mew_baby"),
    ("l60", "Lucario / Hariyama", SET_L60_NAMES, "s60", "aura"),
    ("g30", "Ambipom Hand Fling", SET_G30_NAMES, "s60", "celebration"),
    ("mill", "Mill", SET_MILL_NAMES, "s60", "mill"),
    ("doll", "Doll", SET_DOLL_NAMES, "s60", "doll"),
    ("celebi", "Celebi Mill", SET_ROAST_NAMES, "s60", "roast"),
    ("two-forest", "二森林", SET_ROAST_TWO_FOREST_NAMES, "s60", "roast"),
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "s60", "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "s60", "phantom"),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "s60", "phantom"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "s60", "demolish"),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "s60", "slash"),
    ("g", "Carpet Set G", SET_G_NAMES, "s60", "g"),
    ("a", "Carpet Set A (Dondozo / Staraptor)", SET_A_NAMES, "family", "thrifty"),
    ("b", "Carpet Set B (Walrein / Pikachu)", SET_B_NAMES, "family", "shock"),
    ("c", "Set C (Clefairy / Mewtwo)", SET_C_NAMES, "family", "party"),
    ("d", "Set D (Charm Ogerpon)", SET_D_NAMES, "family", "demolish"),
    ("s", "Set S (Floragato)", SET_S_NAMES, "family", "slash"),
    ("e", "Carpet Set E (Walrein / Iris)", SET_E_NAMES, "family-energy", "shock"),
    ("f", "Carpet Set F (Staraptor / Gengar)", SET_F_NAMES, "family-energy", "carnival"),
    ("t", "Set T (Dragapult ex)", SET_T_NAMES, "s30", "phantom"),
)

RULES = {
    "s60": standard_60_rules,
    "s30": standard_30_rules,
    "family": default_family_rules,
    "family-energy": no_pokemon_energy_family_rules,
}

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


def _cell(seat: str, foe_key: str, foe_names, rules_key: str, foe_strat: str) -> tuple[str, str, dict]:
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
        RULES[rules_key](),
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
    jobs = [(seat, key, names, rules_key, strat) for key, _label, names, rules_key, strat in FOES for seat in ("a", "b")]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(_cell, seat, key, names, rules_key, strat) for seat, key, names, rules_key, strat in jobs]
        for fut in as_completed(futures):
            seat, key, row = fut.result()
            cells.setdefault(key, {})[seat] = row
            print(f"{key} seat {seat}: {row['win_rate']:.3f}", flush=True)
    report = []
    for key, label, names, rules_key, strat in FOES:
        a = cells[key]["a"]["win_rate"]
        b = cells[key]["b"]["win_rate"]
        rules = RULES[rules_key]()
        report.append(
            {
                "key": key,
                "name": label,
                "cards": len(list(names)),
                "rules": rules_key,
                "rules_name": rules.name,
                "prize_count": rules.prize_count,
                "pokemon_as_energy": rules.pokemon_as_energy,
                "foe_strategy": strat,
                "kecleon_as_a": a,
                "kecleon_as_b": b,
                "mean": (a + b) / 2,
                "a": cells[key]["a"],
                "b": cells[key]["b"],
            }
        )
    s60_rows = [row for row in report if row["rules"] == "s60"]
    short_rows = [row for row in report if row["rules"] != "s60"]
    payload = {
        "deck": "Kecleon",
        "cards": list(SET_KECLEON_NAMES),
        "games_per_seat": GAMES,
        "seed": SEED,
        "seconds": round(time.perf_counter() - started, 1),
        "mean_s60": sum(row["mean"] for row in s60_rows) / len(s60_rows),
        "mean_30": sum(row["mean"] for row in short_rows) / len(short_rows),
        "field": report,
    }
    DEST.write_text(json.dumps(payload, indent=2))
    print(json.dumps({
        "mean_s60": payload["mean_s60"],
        "mean_30": payload["mean_30"],
        "seconds": payload["seconds"],
        "field": [{"key": row["key"], "rules": row["rules"], "mean": row["mean"]} for row in report],
    }, indent=2))


if __name__ == "__main__":
    main()
