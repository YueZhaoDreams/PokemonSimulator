#!/usr/bin/env python3
"""Carpet Set G: 4 Buddy-Buddy Poffin arrive, stay at 60.

Base is frozen Friday-lock SET_G_FRIDAY_NAMES (3 Boss, Mega, Tornadus,
0 Poffin, 0 Mewtwo). SET_G_NAMES is now the Poffin lock.
Poffin is printed "Search your deck for up to 2 Basic Pokemon with 70 HP or
less and put them onto your Bench" -- engine already plays exactly that
(count=2, max_hp=70). G targets: Clefairy / Ledyba / Starly / Kecleon (11).

Rule: s60. Seed 20260915. G is always player A; first player is random.
G uses dedicated `g`.

Stage 1: 1-for-1 screen (1 Poffin in) on t60 / Hedrick / D60 / UNL.
Stage 2: named 4-for-4 packages + auto top4 from the screen, full field.
Stage 3: confirm baseline + top-competitive + top-all at 3000 games.
"""

from __future__ import annotations

import json
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
    SET_G_FRIDAY_NAMES,
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)

GAMES_SCREEN = 1500
GAMES_FINAL = 2000
GAMES_CONFIRM = 3000
SEED = 20260915
WORKERS = 8

FOES = (
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("c60", SET_C60_NAMES, "party"),
    ("s60", SET_S60_NAMES, "slash"),
    ("h", SET_H_NAMES, "nuzzle"),
)
SCREEN_FOES = ("t60", "hedrick", "d60", "unl")
COMPETITIVE = ("t60", "hedrick", "d60")

# 1-for-1 screen. Keep Clefairy (Party engine). Include C60-overlap cards so
# the numbers can show they are not the cut.
CUT_ONE = (
    "Hop's Cramorant",
    "Relicanth",
    "Kecleon",
    "Indeedee",
    "Flutter Mane",
    "Tornadus",
    "Trekking Shoes",
    "Energy Search",
    "Drayton",
    "Tulip",
    "Iris's Fighting Spirit",
    "Surfer",
    "Ledian",
    "Ledyba",
    "Staraptor",
    "Starly",
    "Staravia",
    "Munkidori",
    "Darkness Energy",
    "Boomerang Energy",
    "Psychic Energy",
    "Mega Clefable ex",
    "Energy Retrieval",
    "Energy Switch",
    "Ultra Ball",
)

# Named 4-for-4 packages (4 Poffin in). Auto top4 from the screen is added.
PACKAGES = (
    ("junk4", ("Tornadus", "Hop's Cramorant", "Kecleon", "Relicanth")),
    ("tech_keep_kec", ("Tornadus", "Hop's Cramorant", "Relicanth", "Indeedee")),
    ("search_swap", ("Energy Search", "Trekking Shoes", "Tornadus", "Hop's Cramorant")),
    ("supporters", ("Tulip", "Drayton", "Iris's Fighting Spirit", "Trekking Shoes")),
    ("energy", ("Psychic Energy", "Psychic Energy", "Psychic Energy", "Hop's Cramorant")),
    ("dark3cram", ("Darkness Energy", "Darkness Energy", "Darkness Energy", "Hop's Cramorant")),
    ("ledian_thin", ("Ledian", "Ledian", "Ledyba", "Hop's Cramorant")),
    ("bird_thin", ("Staraptor", "Staravia", "Starly", "Hop's Cramorant")),
    ("flutter_junk", ("Flutter Mane", "Tornadus", "Hop's Cramorant", "Kecleon")),
    ("boom_search", ("Boomerang Energy", "Energy Search", "Tornadus", "Hop's Cramorant")),
)

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "glittering_star", "key": "gust"},
    {"type": "event_prefix", "prefix": "boss_orders", "key": "boss"},
    {"type": "event_prefix", "prefix": "adrena_brain", "key": "adrena"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex", "key": "mega"},
    {"type": "event_prefix", "prefix": "attack:Tornadus", "key": "tornadus"},
    {"type": "event_prefix", "prefix": "tutor:Clefairy:poffin", "key": "poffin_clef"},
    {"type": "event_prefix", "prefix": "tutor:Ledyba:poffin", "key": "poffin_ledyba"},
    {"type": "event_prefix", "prefix": "tutor:Starly:poffin", "key": "poffin_starly"},
    {"type": "event_prefix", "prefix": "tutor:Kecleon:poffin", "key": "poffin_kecleon"},
]


def apply_cuts_adds(names: list[str], cuts: tuple[str, ...] | list[str], adds: tuple[str, ...] | list[str]) -> list[str]:
    out = list(names)
    for name in cuts:
        out.remove(name)
    out.extend(adds)
    if len(out) != 60:
        raise ValueError(f"list is {len(out)} cards, want 60 (cuts={cuts} adds={adds})")
    bad = copy_violations(build_fallback_deck(out), standard_60_rules())
    if bad:
        raise ValueError(f"copy cap: {bad}")
    return out


def add_poffin(names: list[str] | None, n: int, cuts: tuple[str, ...] | list[str]) -> list[str]:
    if n != len(cuts):
        raise ValueError(f"need {n} cuts for {n} Poffin, got {cuts}")
    return apply_cuts_adds(
        list(names if names is not None else SET_G_FRIDAY_NAMES),
        cuts,
        ["Buddy-Buddy Poffin"] * n,
    )


def _detail(rec: dict) -> dict:
    r = rec["results"]
    q = r.get("query_counts") or {}
    return {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "party_games": q.get("party", 0),
        "gust_games": q.get("gust", 0),
        "boss_games": q.get("boss", 0),
        "adrena_games": q.get("adrena", 0),
        "mega_games": q.get("mega", 0),
        "tornadus_games": q.get("tornadus", 0),
        "poffin_clef": q.get("poffin_clef", 0),
        "poffin_ledyba": q.get("poffin_ledyba", 0),
        "poffin_starly": q.get("poffin_starly", 0),
        "poffin_kecleon": q.get("poffin_kecleon", 0),
    }


def _run(variant: str, names: list[str], foe_key: str, foe_names, foe_strat: str, games: int) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": variant, "name": variant},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    return variant, foe_key, _detail(rec)


def _jobs(variants: list[tuple[str, list[str]]], foes: tuple, games: int):
    workers = min(WORKERS, max(1, len(variants) * len(foes)))
    cells: dict[str, dict[str, dict]] = {k: {} for k, _ in variants}
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = [
            pool.submit(_run, variant, names, foe_key, foe_names, foe_strat, games)
            for variant, names in variants
            for foe_key, foe_names, foe_strat in foes
        ]
        for fut in as_completed(futs):
            variant, foe_key, detail = fut.result()
            cells[variant][foe_key] = detail
            poffin = detail["poffin_clef"] + detail["poffin_ledyba"] + detail["poffin_starly"] + detail["poffin_kecleon"]
            print(
                f"{variant} vs {foe_key}: {detail['a']:.1%}  "
                f"(first {detail['first']:.1%} / second {detail['second']:.1%})  "
                f"poffin {poffin} gust {detail['gust_games']} party {detail['party_games']}",
                flush=True,
            )
    return {variant: {key: cells[variant][key] for key, *_ in foes} for variant, _ in variants}


def _weighted(cells: dict[str, dict], baseline: dict[str, dict], foe_keys: tuple[str, ...]) -> dict[str, float]:
    weights = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key in foe_keys}
    wsum = sum(weights.values())
    out: dict[str, float] = {}
    for variant, row in cells.items():
        out[variant] = sum(row[key]["a"] * weights[key] for key in foe_keys) / wsum
    return out


def main() -> None:
    started = time.perf_counter()
    base = list(SET_G_FRIDAY_NAMES)
    assert len(base) == 60
    assert base.count("Buddy-Buddy Poffin") == 0
    assert base.count("Boss's Orders") == 3
    assert base.count("Mega Clefable ex") == 1
    assert base.count("Mewtwo ex") == 0

    screen_foes = tuple(f for f in FOES if f[0] in SCREEN_FOES)
    screen_variants: list[tuple[str, list[str]]] = [("baseline", base)]
    for cut in CUT_ONE:
        screen_variants.append((f"cut:{cut}", add_poffin(base, 1, (cut,))))

    print(f"=== screen {GAMES_SCREEN} games, {len(screen_variants)} lists ===", flush=True)
    screen = _jobs(screen_variants, screen_foes, GAMES_SCREEN)
    screen_w = _weighted(screen, screen["baseline"], SCREEN_FOES)
    ranked = sorted(
        ((k, screen_w[k], screen[k]) for k in screen if k != "baseline"),
        key=lambda x: -x[1],
    )
    top4 = tuple(k.split(":", 1)[1] for k, *_ in ranked[:4])
    print("top 1-for-1 weighted:", [(k, f"{w:.3f}") for k, w, _ in ranked[:8]], flush=True)
    print("auto top4 cuts:", top4, flush=True)

    packages = list(PACKAGES)
    if top4 not in {cuts for _, cuts in packages}:
        packages.append(("auto_top4", top4))
    top2 = tuple(k.split(":", 1)[1] for k, *_ in ranked[:2])
    final_variants: list[tuple[str, list[str]]] = [("baseline", base)]
    final_variants.append(("poffin2", add_poffin(base, 2, top2)))
    for key, cuts in packages:
        final_variants.append((key, add_poffin(base, 4, cuts)))

    print(f"=== packages {GAMES_FINAL} games, {len(final_variants)} lists ===", flush=True)
    final = _jobs(final_variants, FOES, GAMES_FINAL)
    foe_keys = tuple(k for k, *_ in FOES)
    final_w = _weighted(final, final["baseline"], foe_keys)
    comp_w = _weighted(final, final["baseline"], COMPETITIVE)

    ranked_all = sorted(final_w.items(), key=lambda kv: -kv[1])
    ranked_comp = sorted(comp_w.items(), key=lambda kv: -kv[1])
    top_all = next(k for k, _ in ranked_all if k != "baseline")
    top_comp = next(k for k, _ in ranked_comp if k != "baseline")
    confirm_keys = list(dict.fromkeys(["baseline", top_comp, top_all]))
    confirm_variants = [(k, names) for k, names in final_variants if k in confirm_keys]

    print(f"=== confirm {GAMES_CONFIRM} games, {confirm_keys} ===", flush=True)
    confirm = _jobs(confirm_variants, screen_foes, GAMES_CONFIRM)
    confirm_w = _weighted(confirm, confirm["baseline"], SCREEN_FOES)
    confirm_comp = _weighted(confirm, confirm["baseline"], COMPETITIVE)

    elapsed = time.perf_counter() - started
    out = {
        "games_screen": GAMES_SCREEN,
        "games_final": GAMES_FINAL,
        "games_confirm": GAMES_CONFIRM,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "source": "SET_G_FRIDAY_NAMES + 4 Buddy-Buddy Poffin",
        "friday_g": base,
        "friday_g_counts": Counter(base).most_common(),
        "screen_ranked": [
            {"cut": k.split(":", 1)[1], "weighted": w, "cells": row}
            for k, w, row in ranked
        ],
        "auto_top4": list(top4),
        "packages": {key: list(cuts) for key, cuts in packages},
        "poffin2_cuts": list(top2),
        "lists": {k: names for k, names in final_variants},
        "foes": {key: strat for key, _names, strat in FOES},
        "screen": screen,
        "cells": final,
        "weighted_all": final_w,
        "weighted_competitive": comp_w,
        "confirm_keys": confirm_keys,
        "confirm": confirm,
        "confirm_weighted": confirm_w,
        "confirm_weighted_competitive": confirm_comp,
    }
    dest = ROOT / "data/lab/set-g-poffin-c60.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    print("weighted_all", {k: round(v, 4) for k, v in ranked_all})
    print("weighted_competitive", {k: round(v, 4) for k, v in ranked_comp})
    print("confirm", {k: round(v, 4) for k, v in sorted(confirm_w.items(), key=lambda kv: -kv[1])})


if __name__ == "__main__":
    main()
