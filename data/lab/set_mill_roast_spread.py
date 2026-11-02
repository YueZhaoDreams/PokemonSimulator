#!/usr/bin/env python3
"""400-game sample of the Spreading Light Celebi Mill 60.

The list is 二森林 with Pitch Black Lampent, no Pichu, no Hyper Aroma, and four
Psychic Energy. Seed 20261102 is the holdout already used for 二森林, so this
file can sit next to that row. The script records the sample. It does not edit
the locked list and it does not search cuts.
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
sys.path.insert(0, str(ROOT))

from app.engine.game import play_game
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_ROAST_SPREADING_NAMES,
    SET_ROAST_TWO_FOREST_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    build_roast_spreading_deck,
    fallback_named,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom", False),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom", False),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "phantom", False),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish", False),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "slash", False),
    ("g", "Gholdengo (G)", SET_G_NAMES, "g", False),
    ("c60", "Clefairy / Mewtwo (C60)", SET_C60_NAMES, "party", False),
    ("m", "Set M (Mew ex)", SET_M60_NAMES, "mew_baby", False),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie", False),
    ("lucario", "Lucario Hariyama", SET_L60_NAMES, "aura", False),
    ("thorns", "Iron Thorns ex", IRON_THORNS_NAMES, "thorns", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)

WEIGHTS = {
    "t60": 0.040,
    "hedrick": 0.051,
    "unl": 0.022,
    "d60": 0.145,
    "s60": 0.070,
    "g": 0.117,
    "c60": 0.124,
    "m": 0.145,
    "starmie": 0.106,
    "lucario": 0.051,
    "thorns": 0.041,
    "h": 0.076,
    "g30": 0.011,
}
_WEIGHT_TOTAL = sum(WEIGHTS.values())
WEIGHTS = {key: value / _WEIGHT_TOTAL for key, value in WEIGHTS.items()}

GAMES = int(os.environ.get("ROAST_SPREAD_GAMES", "400"))
WORKERS = int(os.environ.get("ROAST_SPREAD_WORKERS", str(os.cpu_count() or 2)))
SEED = int(os.environ.get("ROAST_SPREAD_SEED", "20261102"))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("ROAST_SPREAD_PARTIAL", "/tmp/mill-roast-spread-partial.jsonl"))
DEST = Path(os.environ.get("ROAST_SPREAD_DEST", HERE / "set-mill-roast-spread.json"))
MD_DEST = Path(os.environ.get("ROAST_SPREAD_MD", HERE / "set-mill-roast-spread.md"))
COMPARE_JSON = HERE / "set-mill-roast-compare.json"
SPREADING = (
    "Search your deck for up to 3 Lampent and put them onto your Bench. Then, shuffle your deck."
)

_STATS = (
    "spreading",
    "spreading_benched",
    "flickering",
    "slumbering_forest",
    "forest_play",
    "roast_mill_cards",
    "time_distortion",
    "devolution_spray",
    "fired",
)


def _check() -> None:
    pile = build_roast_spreading_deck()
    if [card.name for card in pile] != list(SET_ROAST_SPREADING_NAMES):
        raise SystemExit("spreading deck names drifted from SET_ROAST_SPREADING_NAMES")
    if len(pile) != 60:
        raise SystemExit(f"spreading list has {len(pile)} cards")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"spreading list is illegal: {bad}")
    if fallback_named("Lampent").catalog_id != "bw8-22":
        raise SystemExit("fallback Lampent is no longer Plasma Storm Freefloating")
    lampent = [card for card in pile if card.name == "Lampent"]
    if len(lampent) != 4:
        raise SystemExit(f"spreading list has {len(lampent)} Lampent")
    for card in lampent:
        attack = card.attacks[0]
        if card.catalog_id != "me05-037" or attack.name != "Spreading Light" or attack.text != SPREADING:
            raise SystemExit(f"Lampent is {card.catalog_id} {attack.name!r} {attack.text!r}")
        if attack.cost != ["Psychic"] or card.hp != 90:
            raise SystemExit(f"Lampent cost {attack.cost} HP {card.hp}")
    counts = Counter(card.name for card in pile)
    if counts["Pichu"] or counts["Hyper Aroma"] or counts["Psychic Energy"] != 4:
        raise SystemExit(f"unexpected counts {counts}")
    if counts["Slumbering Forest"] != 2 or counts["Devolution Spray"] != 4 or counts["Fire Energy"] != 7:
        raise SystemExit(f"forest/spray/fire drifted {counts}")
    removed = [name for name in SET_ROAST_TWO_FOREST_NAMES if name not in {"Pichu", "Hyper Aroma"}]
    removed.extend(["Psychic Energy"] * 4)
    if removed != list(SET_ROAST_SPREADING_NAMES):
        raise SystemExit("spreading 60 is not 二森林 minus Pichu and Hyper Aroma plus four Psychic Energy")


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = build_roast_spreading_deck()
    if [card.name for card in subject] != list(names):
        raise SystemExit("worker deck does not match the job list")
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "roast", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "roast"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    totals = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        roast_is_a = seat == "a"
        if (roast_is_a and result.winner == "a") or (not roast_is_a and result.winner == "b"):
            wins += 1
        totals["spreading"] += result.events.get("attack:Lampent:Spreading Light", 0)
        totals["spreading_benched"] += result.events.get("call_family:lampent", 0)
        totals["flickering"] += result.events.get("attack:Litwick:Flickering Flames", 0)
        totals["slumbering_forest"] += result.events.get("slumbering_forest", 0)
        totals["forest_play"] += result.events.get("stadium:Slumbering Forest", 0)
        totals["roast_mill_cards"] += result.events.get("roast_mill_cards", 0)
        totals["time_distortion"] += result.events.get("time_distortion", 0)
        totals["devolution_spray"] += result.events.get("devolution_spray", 0)
        totals["fired"] += 1 if result.events.get("mountain_roasting", 0) else 0
    cell = {"wr": wins / games}
    for key in _STATS:
        cell[key] = totals[key] / games
    return cell


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}|roast-spread-v1"


def _load_cache() -> dict[str, dict]:
    found: dict[str, dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found[row["key"]] = row["cell"]
    return found


def _append(key: str, cell: dict) -> None:
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")


def _evaluate(names: list[str], games: int, seed: int, cache: dict[str, dict]) -> dict[str, dict]:
    frozen = tuple(names)
    jobs = []
    out: dict[str, dict] = {}
    for foe_key, *_ in FOES:
        for seat in ("a", "b"):
            key = _cache_key(frozen, foe_key, seat, games, seed)
            cached = cache.get(key)
            if cached is not None:
                out.setdefault(foe_key, {})[seat] = cached
                continue
            jobs.append((foe_key, seat, key))
    print(f"seed {seed}: {len(jobs)} cells, {games} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, frozen, foe_key, seat, games, seed): (foe_key, seat, key)
            for foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out.setdefault(foe_key, {})[seat] = cell
            done += 1
            if done == 1 or done == len(futures) or done % 4 == 0:
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                print(
                    f"  {done}/{len(futures)} {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)",
                    flush=True,
                )
    return out


def _combine(cells: dict[str, dict]) -> dict[str, dict]:
    combined = {}
    for foe_key, *_ in FOES:
        a = cells[foe_key]["a"]
        b = cells[foe_key]["b"]
        row = {"wr": (a["wr"] + b["wr"]) / 2, "a": a["wr"], "b": b["wr"]}
        for key in _STATS:
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_se(seats: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = seats[key][seat]["wr"]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _two_forest_holdout() -> dict:
    report = json.loads(COMPARE_JSON.read_text())
    for seed_row in report["seeds"]:
        if seed_row.get("seed") == SEED:
            return seed_row["flicker"]
    raise SystemExit(f"compare JSON has no flicker row for seed {SEED}")


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _signed(value: float) -> str:
    return f"{value:+.2%}"


def _num(value: float) -> str:
    return f"{value:.2f}"


def _markdown(report: dict) -> str:
    row = report["spread"]
    base = report["two_forest"]
    lines = [
        "# Celebi Mill, Spreading Light",
        "",
        "二森林 is the recorded 2-Forest intermediate. This 60 keeps that list and changes four things: Lampent is Pitch Black Spreading Light, the three Pichu come out, Hyper Aroma comes out, and four Psychic Energy go in.",
        "",
        "The printed attack is: Search your deck for up to 3 Lampent and put them onto your Bench. Then, shuffle your deck. It costs one Psychic Energy. Roast keeps one Lampent to use that attack and leaves the other Lampent in the deck.",
        "",
        f"Seed `{report['seed']}`, {report['games']} games per seat, both seats. A foe cell is the mean of the two seats. Weights are the frozen Sisters loss weights. 二森林 on this seed is the holdout row in `set-mill-roast-compare.md`.",
        "",
        "This script records the sample. It does not edit the locked list.",
        "",
        "## Weighted win rate",
        "",
        "| List | Weighted | ± | Mean | Worst | Spreading Light | Lampent benched | Flicker | Forest plays | Mill cards | Time Distortion | Fired |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 二森林 | {_pct(base['weighted'])} | {_pct(base['se'])} | {_pct(base['mean'])} | {_pct(base['worst'])} "
            f"| 0 | 0 | {_num(base['flickering'])} | {_num(base['forest_play'])} "
            f"| {_num(base['roast_mill_cards'])} | {_num(base['time_distortion'])} | {_pct(base['fired'])} |"
        ),
        (
            f"| Spreading Light | {_pct(row['weighted'])} | {_pct(row['se'])} | {_pct(row['mean'])} | {_pct(row['worst'])} "
            f"| {_num(row['spreading'])} | {_num(row['spreading_benched'])} | {_num(row['flickering'])} | {_num(row['forest_play'])} "
            f"| {_num(row['roast_mill_cards'])} | {_num(row['time_distortion'])} | {_pct(row['fired'])} |"
        ),
        "",
        f"Spreading Light minus 二森林: {_signed(row['weighted'] - base['weighted'])}.",
        "",
        "## Per foe",
        "",
        "| Foe | Weight | 二森林 | Spreading Light | Delta |",
        "| :--- | ---: | ---: | ---: | ---: |",
    ]
    for key, label, *_rest in FOES:
        before = base["cells"][key]["wr"]
        after = row["cells"][key]["wr"]
        lines.append(
            f"| {label} | {WEIGHTS[key]:.3f} | {_pct(before)} | {_pct(after)} | {_signed(after - before)} |"
        )
    lines.extend(
        [
            "",
            "## List",
            "",
            "| Card | Count |",
            "| :--- | ---: |",
        ]
    )
    for name, count in row["counts"].items():
        lines.append(f"| {name} | {count} |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    _check()
    started = time.perf_counter()
    cache = _load_cache()
    seats = _evaluate(list(SET_ROAST_SPREADING_NAMES), GAMES, SEED, cache)
    cells = _combine(seats)
    row = {
        "label": "Spreading Light",
        "list": list(SET_ROAST_SPREADING_NAMES),
        "counts": dict(Counter(SET_ROAST_SPREADING_NAMES)),
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, GAMES),
        "mean": sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES),
        "worst": min(cells[key]["wr"] for key, *_ in FOES),
        "cells": {
            key: {
                "wr": cell["wr"],
                "a": cell["a"],
                "b": cell["b"],
                **{stat: cell[stat] for stat in _STATS},
            }
            for key, cell in cells.items()
        },
    }
    for stat in _STATS:
        row[stat] = sum(cells[key][stat] for key, *_ in FOES) / len(FOES)
    base = _two_forest_holdout()
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed_sec": round(time.perf_counter() - started, 1),
        "two_forest": {
            "weighted": base["weighted"],
            "se": base["se"],
            "mean": base["mean"],
            "worst": base["worst"],
            "flickering": base["flickering"],
            "forest_play": base["forest_play"],
            "roast_mill_cards": base["roast_mill_cards"],
            "time_distortion": base["time_distortion"],
            "fired": base["fired"],
            "cells": base["cells"],
        },
        "spread": row,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(
        f"wrote {MD_DEST} weighted {row['weighted']:.2%} vs two-forest {base['weighted']:.2%}",
        flush=True,
    )


if __name__ == "__main__":
    main()
