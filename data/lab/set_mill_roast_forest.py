#!/usr/bin/env python3
"""Greedy Slumbering Forest swaps on the Flickering Flames Celebi Mill 60.

The four Litwick are already Guardians Rising Flickering Flames. This search
does not change that print. Start from SET_ROAST_NAMES, which has zero
Slumbering Forest. Each step replaces exactly one copy of one other card with
one Slumbering Forest. Every name still in the list is a cut. The step keeps
the cut with the higher Sisters-weighted win rate, then the next copy is tried
the same way. Stop when the next copy does not raise the score, or at 4.

The printed stadium sentence flips 2 coins between turns. Either tails and
that Pokémon is still Asleep. Roast plays it when this turn does not need
Broken Time-Space. Flickering Flames is the attack that puts the opponent's
Active Pokémon to sleep.

400 games per seat. A foe cell is the mean of the two seats. This script
records the sample. It does not edit the locked list.
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
    roast_card,
)

IN_NAME = "Slumbering Forest"
MAX_COPIES = 4

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

GAMES = int(os.environ.get("ROAST_FOREST_GAMES", "400"))
SEED = int(os.environ.get("ROAST_FOREST_SEED", "20261101"))
WORKERS = int(os.environ.get("ROAST_FOREST_WORKERS", str(os.cpu_count() or 2)))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("ROAST_FOREST_PARTIAL", "/tmp/mill-roast-forest-partial.jsonl"))
DEST = Path(os.environ.get("ROAST_FOREST_DEST", HERE / "set-mill-roast-forest.json"))
MD_DEST = Path(os.environ.get("ROAST_FOREST_MD", HERE / "set-mill-roast-forest.md"))

_STATS = ("flickering", "slumbering_forest", "forest_play", "roast_mill_cards", "time_distortion", "fired")


def _cards(names: list[str]):
    return [roast_card(name) for name in names]


def _check_list(names: list[str]) -> None:
    pile = _cards(names)
    if len(pile) != 60:
        raise SystemExit(f"list has {len(pile)} cards")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"list is illegal: {bad}")


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(list(names))
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
    fired = 0
    totals = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        roast_is_a = seat == "a"
        if (roast_is_a and result.winner == "a") or (not roast_is_a and result.winner == "b"):
            wins += 1
        if result.events.get("mountain_roasting", 0):
            fired += 1
        totals["flickering"] += result.events.get("attack:Litwick:Flickering Flames", 0)
        totals["slumbering_forest"] += result.events.get("slumbering_forest", 0)
        totals["forest_play"] += result.events.get("stadium:Slumbering Forest", 0)
        totals["roast_mill_cards"] += result.events.get("roast_mill_cards", 0)
        totals["time_distortion"] += result.events.get("time_distortion", 0)
        totals["fired"] += 1 if result.events.get("mountain_roasting", 0) else 0
    cell = {"wr": wins / games}
    for key in _STATS:
        if key == "fired":
            cell[key] = fired / games
        else:
            cell[key] = totals[key] / games
    return cell


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}|roast-forest-v1"


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


def _evaluate(lists: list[tuple[str, list[str]]], games: int, cache: dict[str, dict]) -> dict[str, dict[str, dict]]:
    jobs = []
    out: dict[str, dict[str, dict]] = {label: {} for label, _names in lists}
    for label, names in lists:
        frozen = tuple(names)
        for foe_key, *_ in FOES:
            for seat in ("a", "b"):
                key = _cache_key(frozen, foe_key, seat, games, SEED)
                cached = cache.get(key)
                if cached is not None:
                    out[label].setdefault(foe_key, {})[seat] = cached
                    continue
                jobs.append((label, frozen, foe_key, seat, key))
    print(f"  {len(jobs)} cells, {games} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, frozen, foe_key, seat, games, SEED): (label, foe_key, seat, key)
            for label, frozen, foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            label, foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out[label].setdefault(foe_key, {})[seat] = cell
            done += 1
            if done == 1 or done % 26 == 0 or done == len(futures):
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                print(
                    f"    {done}/{len(futures)} {label} {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)",
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


def _swap(names: list[str], cut: str) -> list[str] | None:
    if names.count(IN_NAME) >= MAX_COPIES:
        return None
    if cut == IN_NAME or names.count(cut) <= 0:
        return None
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        return None
    return out


def _cuts(names: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(names).items() if count > 0 and name != IN_NAME)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _row(label: str, names: list[str], seats: dict[str, dict], cut: str | None) -> dict:
    cells = _combine(seats)
    return {
        "label": label,
        "cut": cut,
        "copies": names.count(IN_NAME),
        "copies_before": 0 if cut is None else names.count(cut) + 1,
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, GAMES),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "flickering": _avg(cells, "flickering"),
        "slumbering_forest": _avg(cells, "slumbering_forest"),
        "forest_play": _avg(cells, "forest_play"),
        "roast_mill_cards": _avg(cells, "roast_mill_cards"),
        "time_distortion": _avg(cells, "time_distortion"),
        "fired": _avg(cells, "fired"),
        "cells": {key: {"wr": cell["wr"], "a": cell["a"], "b": cell["b"]} for key, cell in cells.items()},
    }


def _metric_cells(row: dict) -> str:
    return (
        "| {flick:.2f} | {checks:.2f} | {play:.2f} | {mill:.2f} | {td:.2f} | {fired:.1%} |".format(
            flick=row["flickering"],
            checks=row["slumbering_forest"],
            play=row["forest_play"],
            mill=row["roast_mill_cards"],
            td=row["time_distortion"],
            fired=row["fired"],
        )
    )


def _markdown(report: dict) -> str:
    base = report["path"][0]
    lines = [
        "# Celebi Mill, Slumbering Forest",
        "",
        "The four Litwick are Guardians Rising Flickering Flames. The printed sentence is: Your opponent's Active Pokémon is now Asleep. Roast uses that attack when the opponent's Active Pokémon is not Asleep and a Litwick can pay it. Time Distortion waits until that Active is Asleep, or until Flickering Flames cannot be paid.",
        "",
        "Printed stadium sentence: If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep.",
        "",
        "Roast plays Slumbering Forest when this turn does not need Broken Time-Space. Broken Time-Space is played when a Pokémon played this turn still has to evolve. One stadium replaces the other.",
        "",
        "Each step tries every other card as the one copy to replace with one Slumbering Forest. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way. The Litwick print is not one of the swaps.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen Sisters loss weights. The same weights as the Celebi Mill lock.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "This sample is not the 1000-game holdout. This script does not edit the locked list.",
        "",
        "## Path",
        "",
        "| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |",
        "| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {copies} | {cut} | {weighted} | {se} | {mean} | {worst} | {delta} {metrics}".format(
                label=row["label"],
                copies=row["copies"],
                cut=row.get("cut") or "—",
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                metrics=_metric_cells(row),
            )
        )
    best = report["best"]
    kept_copies = best["copies"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                f"The search kept {kept_copies} Slumbering Forest. "
                f"Weighted win rate {_pct(best['weighted'])} against the zero-Forest list at {_pct(base['weighted'])} "
                f"({_signed(best['weighted'] - base['weighted'])}, ± {_pct(best['se'])})."
                if kept_copies
                else (
                    f"No copy raised the Sisters-weighted win rate. "
                    f"The list stays at zero Slumbering Forest, at {_pct(base['weighted'])} ± {_pct(base['se'])}."
                )
            ),
            "",
            "The locked Celebi Mill list is not changed by this search.",
            "",
        ]
    )
    if kept_copies:
        counts = best["counts"]
        lines.append("Counts on the kept list:")
        lines.append("")
        for name, count in counts.items():
            lines.append(f"- {name} ×{count}")
        lines.append("")
    previous = base
    for rnd in report["rounds"]:
        lines.extend(
            [
                f"## Step {rnd['step']}",
                "",
                f"List entering this step: weighted {_pct(previous['weighted'])} ± {_pct(previous['se'])}. "
                "Each row replaces one copy of that card with one Slumbering Forest.",
                "",
                "| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["rows"]:
            lines.append(
                "| {cut} | {before} | {weighted} | {se} | {mean} | {worst} | {delta} {metrics}".format(
                    cut=row["cut"],
                    before=row["copies_before"],
                    weighted=_pct(row["weighted"]),
                    se=_pct(row["se"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous["weighted"]),
                    metrics=_metric_cells(row),
                )
            )
        kept = rnd.get("kept")
        lines.append("")
        if kept:
            lines.append(
                f"Kept −{kept['cut']} at {_pct(kept['weighted'])} "
                f"({_signed(kept['weighted'] - previous['weighted'])})."
            )
            previous = kept
        else:
            lines.append("No cut in this step was higher than the list already kept. The search stopped.")
        lines.append("")
    lines.extend(
        [
            "## Foes at the kept list",
            "",
            "| Foe | A | B | Mean | Delta vs zero Forest |",
            "| :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_rest in FOES:
        cell = best["cells"][key]
        base_cell = base["cells"][key]
        lines.append(
            f"| {label} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base_cell['wr'])} |"
        )
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    started = time.perf_counter()
    current = list(SET_ROAST_NAMES)
    if current.count(IN_NAME) != 0:
        raise SystemExit("Slumbering Forest is already in the Celebi Mill lock. This script must not overwrite that report.")
    if len(current) != 60:
        raise SystemExit(f"Celebi Mill lock has {len(current)} cards")
    pile = _cards(current)
    if any(card.name == "Litwick" and card.attacks[0].name != "Flickering Flames" for card in pile):
        raise SystemExit("roast Litwick is not Flickering Flames")
    _check_list(current)
    cache = _load_cache()
    print(f"baseline flicker, 0 forest, {GAMES} games, seed {SEED}, workers {WORKERS}", flush=True)
    base_seats = _evaluate([("locked", current)], GAMES, cache)["locked"]
    base = _row("0 Forest", current, base_seats, None)
    print(f"  weighted {base['weighted']:.2%} ± {base['se']:.2%}", flush=True)
    path = [base]
    rounds: list[dict] = []
    while current.count(IN_NAME) < MAX_COPIES:
        options = []
        for cut in _cuts(current):
            swapped = _swap(current, cut)
            if swapped is None:
                continue
            _check_list(swapped)
            options.append((cut, swapped))
        if not options:
            break
        print(f"step {len(rounds) + 1}: {len(options)} cuts", flush=True)
        evaluated = _evaluate([(cut, names) for cut, names in options], GAMES, cache)
        rows = []
        for cut, names in options:
            row = _row(cut, names, evaluated[cut], cut)
            rows.append(row)
        rows.sort(key=lambda item: (item["weighted"], item["worst"], item["copies_before"], item["cut"]), reverse=True)
        winner = rows[0]
        print(
            f"  best -{winner['cut']} {winner['weighted']:.2%} ± {winner['se']:.2%} vs {path[-1]['weighted']:.2%}",
            flush=True,
        )
        kept = None
        if winner["weighted"] > path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"{winner['copies']} Forest"
            current = list(winner["list"])
            path.append(kept)
        rounds.append({"step": len(rounds) + 1, "rows": rows, "kept": kept})
        if kept is None:
            print("  did not improve; stop", flush=True)
            break
    best = max(path, key=lambda item: (item["weighted"], -path.index(item)))
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "method": (
            "greedy one-card Slumbering Forest swaps from the Flickering Flames Celebi Mill 60; "
            "every other card name is tried as the cut; a step is kept only when its "
            "Sisters-weighted win rate is higher than the list already kept; "
            "400 games per seat"
        ),
        "path": path,
        "best": best,
        "rounds": rounds,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(
        f"kept {best['copies']} by cutting {best.get('cut')} "
        f"weighted {best['weighted']:.2%} -> {MD_DEST}",
        flush=True,
    )


if __name__ == "__main__":
    main()
