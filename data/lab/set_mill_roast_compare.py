#!/usr/bin/env python3
"""Same-seed comparison of two Celebi Mill 60s on the current engine.

Kindling is the locked 4-Devolution-Spray list. Its Litwick is Lost Origin
Kindling Panic, the print fallback_named("Litwick") still returns. Flicker is
the 2-Slumbering-Forest list kept by the Flickering Flames search. Its Litwick
is Guardians Rising Flickering Flames. Both lists still contain four
Devolution Spray.

Each seed plays both lists for 400 games per seat, both seats, with the frozen
Sisters weights. A foe cell is the mean of the two seats. Seed 20261101 is the
Forest search seed, so the flicker row on that seed has to match
set-mill-roast-forest.json. Seed 20261102 was not used to choose either list.
Seed 20261031 is the seed recorded in set-mill-roast-spray.md; that file's
46.2% was measured before this engine's Litwick print and Broken Time-Space
policy, so this script replays the seed on the current engine.

This script records the sample. It does not edit the locked list.
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
    SET_ROAST_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    fallback_named,
    roast_card,
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

GAMES = int(os.environ.get("ROAST_COMPARE_GAMES", "400"))
WORKERS = int(os.environ.get("ROAST_COMPARE_WORKERS", str(os.cpu_count() or 2)))
SEEDS = tuple(
    int(part)
    for part in os.environ.get("ROAST_COMPARE_SEEDS", "20261101,20261102,20261031").split(",")
    if part.strip()
)
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("ROAST_COMPARE_PARTIAL", "/tmp/mill-roast-compare-partial.jsonl"))
DEST = Path(os.environ.get("ROAST_COMPARE_DEST", HERE / "set-mill-roast-compare.json"))
MD_DEST = Path(os.environ.get("ROAST_COMPARE_MD", HERE / "set-mill-roast-compare.md"))
FOREST_JSON = HERE / "set-mill-roast-forest.json"
SPRAY_JSON = HERE / "set-mill-roast-spray.json"
HEADLINE_SEED = 20261102
FOREST_SEED = 20261101
SPRAY_SEED = 20261031

_STATS = (
    "flickering",
    "kindling",
    "slumbering_forest",
    "forest_play",
    "roast_mill_cards",
    "time_distortion",
    "devolution_spray",
    "fired",
)
_KINDLING_TEXT = "Discard the top card of your opponent's deck."
_FLICKER_TEXT = "Your opponent's Active Pokémon is now Asleep."


def _kindling_card(name: str):
    if name == "Cleffa":
        return fallback_named("cleffa hgss")
    if name == "Igglybuff":
        return fallback_named("igglybuff sleepy")
    return fallback_named(name)


def _cards(print_id: str, names: list[str]):
    if print_id == "kindling":
        return [_kindling_card(name) for name in names]
    if print_id == "flicker":
        return [roast_card(name) for name in names]
    raise SystemExit(f"unknown print {print_id}")


def _check_list(print_id: str, names: list[str]) -> None:
    pile = _cards(print_id, names)
    if len(pile) != 60:
        raise SystemExit(f"{print_id} list has {len(pile)} cards")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"{print_id} list is illegal: {bad}")
    litwick = [card for card in pile if card.name == "Litwick"]
    if len(litwick) != 4:
        raise SystemExit(f"{print_id} has {len(litwick)} Litwick")
    sprays = sum(card.name == "Devolution Spray" for card in pile)
    forests = sum(card.name == "Slumbering Forest" for card in pile)
    if sprays != 4:
        raise SystemExit(f"{print_id} has {sprays} Devolution Spray")
    if print_id == "kindling":
        for card in litwick:
            attack = card.attacks[0]
            if card.catalog_id != "swsh11-024" or attack.name != "Kindling Panic" or attack.text != _KINDLING_TEXT:
                raise SystemExit(f"kindling Litwick is {card.catalog_id} {attack.name!r} {attack.text!r}")
            if card.hp != 60:
                raise SystemExit(f"kindling Litwick HP is {card.hp}")
        if forests != 0:
            raise SystemExit("kindling list contains Slumbering Forest")
        if names.count("Rescue Scarf") != 4 or names.count("Evolution Incense") != 3:
            raise SystemExit("kindling list is not the locked 4-spray 60")
    if print_id == "flicker":
        for card in litwick:
            attack = card.attacks[0]
            if card.catalog_id != "sm2-11" or attack.name != "Flickering Flames" or attack.text != _FLICKER_TEXT:
                raise SystemExit(f"flicker Litwick is {card.catalog_id} {attack.name!r} {attack.text!r}")
            if card.hp != 50:
                raise SystemExit(f"flicker Litwick HP is {card.hp}")
        if forests != 2:
            raise SystemExit(f"flicker list has {forests} Slumbering Forest")
        if names.count("Rescue Scarf") != 3 or names.count("Evolution Incense") != 2:
            raise SystemExit("flicker list is not the kept 2-forest 60")


def _forest_list() -> tuple[list[str], dict]:
    report = json.loads(FOREST_JSON.read_text())
    names = list(report["best"]["list"])
    built = list(SET_ROAST_NAMES)
    built.remove("Rescue Scarf")
    built.append("Slumbering Forest")
    built.remove("Evolution Incense")
    built.append("Slumbering Forest")
    if built != names:
        raise SystemExit("forest JSON list does not match the two swaps off the locked 60")
    if report["seed"] != FOREST_SEED or report["games"] != 400:
        raise SystemExit("forest JSON is not the 400-game seed 20261101 sample")
    return names, report["best"]


def _historical_spray() -> dict:
    report = json.loads(SPRAY_JSON.read_text())
    return {
        "seed": report["seed"],
        "games": report["games"],
        "weighted": report["best"]["weighted"],
        "se": report["best"]["se"],
    }


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _run(print_id: str, names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(print_id, list(names))
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
        totals["flickering"] += result.events.get("attack:Litwick:Flickering Flames", 0)
        totals["kindling"] += result.events.get("attack:Litwick:Kindling Panic", 0)
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


def _cache_key(print_id: str, names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{print_id}|{'/'.join(names)}|roast-compare-v1"


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


def _evaluate(
    lists: list[tuple[str, str, list[str]]],
    games: int,
    seed: int,
    cache: dict[str, dict],
) -> dict[str, dict[str, dict]]:
    jobs = []
    out: dict[str, dict[str, dict]] = {label: {} for label, _print_id, _names in lists}
    for label, print_id, names in lists:
        frozen = tuple(names)
        for foe_key, *_ in FOES:
            for seat in ("a", "b"):
                key = _cache_key(print_id, frozen, foe_key, seat, games, seed)
                cached = cache.get(key)
                if cached is not None:
                    out[label].setdefault(foe_key, {})[seat] = cached
                    continue
                jobs.append((label, print_id, frozen, foe_key, seat, key))
    print(f"  seed {seed}: {len(jobs)} cells, {games} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, print_id, frozen, foe_key, seat, games, seed): (label, foe_key, seat, key)
            for label, print_id, frozen, foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            label, foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out[label].setdefault(foe_key, {})[seat] = cell
            done += 1
            if done == 1 or done % 13 == 0 or done == len(futures):
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                print(
                    f"    {done}/{len(futures)} seed {seed} {label} {seat} vs {foe_key} "
                    f"{cell['wr']:.1%} ({left:.0f}s left)",
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


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["wr"] for key, *_ in FOES)


def _avg(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] for foe, *_ in FOES) / len(FOES)


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _signed(value: float) -> str:
    return f"{value:+.2%}"


def _row(label: str, print_id: str, names: list[str], seats: dict[str, dict]) -> dict:
    cells = _combine(seats)
    row = {
        "label": label,
        "print": print_id,
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, GAMES),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "cells": {
            key: {"wr": cell["wr"], "a": cell["a"], "b": cell["b"]}
            for key, cell in cells.items()
        },
    }
    for key in _STATS:
        row[key] = _avg(cells, key)
    return row


def _same_rate(got: float, expected: float) -> bool:
    # One seat win is 1/400. Anything smaller is float text from the JSON file.
    return abs(got - expected) < 1e-9


def _match_forest(row: dict, expected: dict) -> None:
    mismatches = []
    if not _same_rate(row["weighted"], expected["weighted"]):
        mismatches.append(f"weighted {row['weighted']!r} vs {expected['weighted']!r}")
    for key, _label, *_rest in FOES:
        got = row["cells"][key]
        exp = expected["cells"][key]
        for field in ("wr", "a", "b"):
            if not _same_rate(got[field], exp[field]):
                mismatches.append(f"{key}.{field} {got[field]!r} vs {exp[field]!r}")
    if mismatches:
        print("seed 20261101 flicker does not reproduce the forest sample:", flush=True)
        for line in mismatches:
            print(f"  {line}", flush=True)
        raise SystemExit(2)


def _markdown(report: dict) -> str:
    historical = report["historical_spray"]
    lines = [
        "# Celebi Mill, same-seed comparison",
        "",
        "Two 60-card lists, both played by the current roast policy, 400 games per seat, both seats. A foe cell is the mean of the two seats. Weights are the frozen Sisters loss weights.",
        "",
        "Kindling is the locked list in `SET_ROAST_NAMES`. Litwick is Lost Origin 24, Kindling Panic, HP 60. The printed sentence is: Discard the top card of your opponent's deck. The list has four Devolution Spray, four Rescue Scarf, three Evolution Incense, and zero Slumbering Forest.",
        "",
        "Flicker is `best.list` in `set-mill-roast-forest.json`. That list is the locked 60 with one Rescue Scarf and one Evolution Incense replaced by Slumbering Forest. Litwick is Guardians Rising 11, Flickering Flames, HP 50. The printed sentence is: Your opponent's Active Pokémon is now Asleep. Four Devolution Spray stay in the list.",
        "",
        (
            f"The 4-spray sample in `set-mill-roast-spray.md` is seed `{historical['seed']}`, "
            f"weighted {_pct(historical['weighted'])} ± {_pct(historical['se'])}. "
            "That sample was recorded before this branch's Litwick print and before Broken Time-Space was limited to a Pokémon that still has to evolve on the turn it was played. "
            f"Seed `{SPRAY_SEED}` in the table below is that same seed, replayed on the current engine."
        ),
        "",
        f"Seed `{FOREST_SEED}` is the Slumbering Forest search seed. The flicker row on that seed matches `set-mill-roast-forest.json`. Seed `{HEADLINE_SEED}` was not used to choose the Forest cuts or the Devolution Spray cuts.",
        "",
        "The locked list is unchanged.",
        "",
        "## Weighted win rate",
        "",
        "| Seed | Role | Kindling | ± | Flicker | ± | Flicker − Kindling | ± of difference |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    by_seed = {block["seed"]: block for block in report["seeds"]}
    order = [HEADLINE_SEED, FOREST_SEED, SPRAY_SEED]
    role = {
        HEADLINE_SEED: "holdout",
        FOREST_SEED: "forest search seed",
        SPRAY_SEED: "spray search seed, current engine",
    }
    for seed in order:
        block = by_seed.get(seed)
        if block is None:
            continue
        kindling = block["kindling"]
        flicker = block["flicker"]
        delta = flicker["weighted"] - kindling["weighted"]
        delta_se = (kindling["se"] ** 2 + flicker["se"] ** 2) ** 0.5
        lines.append(
            f"| `{seed}` | {role[seed]} | {_pct(kindling['weighted'])} | {_pct(kindling['se'])} | "
            f"{_pct(flicker['weighted'])} | {_pct(flicker['se'])} | {_signed(delta)} | {_pct(delta_se)} |"
        )
    lines.extend(
        [
            "",
            "The difference uses independent samples. Its standard error is the square root of the sum of the two squared standard errors.",
            "",
            "## Exact weighted rates",
            "",
            "| Seed | Kindling | Flicker | Flicker − Kindling |",
            "| :--- | ---: | ---: | ---: |",
        ]
    )
    for seed in order:
        block = by_seed.get(seed)
        if block is None:
            continue
        kindling = block["kindling"]["weighted"]
        flicker = block["flicker"]["weighted"]
        lines.append(f"| `{seed}` | {kindling:.16f} | {flicker:.16f} | {flicker - kindling:+.16f} |")
    lines.extend(
        [
            "",
            "## Lists",
            "",
            "| Card | Kindling | Flicker |",
            "| :--- | ---: | ---: |",
        ]
    )
    kindling_counts = Counter(report["kindling_list"])
    flicker_counts = Counter(report["flicker_list"])
    for name in list(dict.fromkeys(report["kindling_list"] + report["flicker_list"])):
        if kindling_counts[name] == flicker_counts[name] and name != "Litwick":
            continue
        note = ""
        if name == "Litwick":
            note = " (print differs)"
        lines.append(f"| {name}{note} | {kindling_counts[name]} | {flicker_counts[name]} |")
    lines.append("")
    lines.append("Litwick count is four in both lists. The prints differ, as described above.")
    lines.append("")
    for seed in order:
        block = by_seed.get(seed)
        if block is None:
            continue
        lines.extend(_seed_section(block))
    lines.append(f"Elapsed {report['elapsed']:.1f}s. Games per seat: {report['games']}. Workers recorded the cells in `set-mill-roast-compare.json`.")
    lines.append("")
    return "\n".join(lines) + "\n"


def _seed_section(block: dict) -> list[str]:
    kindling = block["kindling"]
    flicker = block["flicker"]
    lines = [
        f"## Seed {block['seed']}",
        "",
        "| List | Weighted | ± | Mean | Worst | Flicker | Kindling Panic | Sleep checks | Forest plays | Mill cards | Time Distortion | Spray | Fired |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in (kindling, flicker):
        lines.append(
            "| {label} | {weighted} | {se} | {mean} | {worst} | {flick:.2f} | {kind:.2f} | {checks:.2f} | {play:.2f} | {mill:.2f} | {td:.2f} | {spray:.2f} | {fired} |".format(
                label=row["label"],
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                flick=row["flickering"],
                kind=row["kindling"],
                checks=row["slumbering_forest"],
                play=row["forest_play"],
                mill=row["roast_mill_cards"],
                td=row["time_distortion"],
                spray=row["devolution_spray"],
                fired=_pct(row["fired"]),
            )
        )
    lines.extend(
        [
            "",
            "| Foe | Kindling A | Kindling B | Kindling | Flicker A | Flicker B | Flicker | Delta |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_rest in FOES:
        left = kindling["cells"][key]
        right = flicker["cells"][key]
        lines.append(
            f"| {label} | {_pct(left['a'])} | {_pct(left['b'])} | {_pct(left['wr'])} | "
            f"{_pct(right['a'])} | {_pct(right['b'])} | {_pct(right['wr'])} | {_signed(right['wr'] - left['wr'])} |"
        )
    lines.append("")
    return lines


def main() -> None:
    started = time.perf_counter()
    if list(SET_ROAST_NAMES).count("Slumbering Forest") != 0:
        raise SystemExit("Slumbering Forest is in the locked list. This comparison would no longer be the 4-spray 60.")
    if len(SET_ROAST_NAMES) != 60:
        raise SystemExit(f"locked list has {len(SET_ROAST_NAMES)} cards")
    kindling_names = list(SET_ROAST_NAMES)
    flicker_names, forest_best = _forest_list()
    _check_list("kindling", kindling_names)
    _check_list("flicker", flicker_names)
    if os.environ.get("ROAST_COMPARE_CHECK") == "1":
        print("lists ok", flush=True)
        return
    historical = _historical_spray()
    cache = _load_cache()
    blocks = []
    lists = [
        ("kindling", "kindling", kindling_names),
        ("flicker", "flicker", flicker_names),
    ]
    for seed in SEEDS:
        print(f"seed {seed}, {GAMES} games, workers {WORKERS}", flush=True)
        evaluated = _evaluate(lists, GAMES, seed, cache)
        kindling = _row("4 Spray, Kindling Panic", "kindling", kindling_names, evaluated["kindling"])
        flicker = _row("2 Forest, Flickering Flames", "flicker", flicker_names, evaluated["flicker"])
        print(
            f"  kindling {kindling['weighted']:.4%} ± {kindling['se']:.4%}  "
            f"flicker {flicker['weighted']:.4%} ± {flicker['se']:.4%}  "
            f"delta {flicker['weighted'] - kindling['weighted']:+.4%}",
            flush=True,
        )
        if seed == FOREST_SEED and GAMES == 400:
            _match_forest(flicker, forest_best)
            print("  seed 20261101 flicker matches the forest sample", flush=True)
        blocks.append({"seed": seed, "kindling": kindling, "flicker": flicker})
    report = {
        "games": GAMES,
        "seeds": blocks,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "kindling_list": kindling_names,
        "flicker_list": flicker_names,
        "historical_spray": historical,
        "method": (
            "both 60s on the current roast engine; 400 games per seat; both seats; "
            "frozen Sisters weights; seeds 20261101, 20261102, and 20261031; "
            "kindling Litwick is swsh11-024; flicker Litwick is sm2-11"
        ),
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
