#!/usr/bin/env python3
"""Greedy Jacq swaps on the locked roast 60.

Start from the locked list: one Hisuian Heavy Ball, one Switch, four Dawn.
Each step replaces exactly one copy of one other card with one Jacq. Every
name still in the list is a cut. The step keeps the cut with the higher
loss-weighted win rate, then the next copy is tried the same way. Stop when
the next copy does not raise the score, or at 4.

The score is the Sisters 60 loss weight, both seats, seed 20261027. Same
measurement as data/lab/set_mill_roast.py. A foe cell is the mean of the two
seats.

Jacq (SV 175) searches the deck for up to 2 Evolution Pokémon. Roast uses it
for Lampent and Chandelure after Playground has taken the Basics.
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
)

IN_NAME = "Jacq"
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

GAMES = int(os.environ.get("ROAST_JACQ_GAMES", "40"))
SEED = int(os.environ.get("ROAST_JACQ_SEED", "20261027"))
WORKERS = int(os.environ.get("ROAST_JACQ_WORKERS", str(os.cpu_count() or 2)))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("ROAST_JACQ_PARTIAL", "/tmp/mill-roast-jacq-partial.jsonl"))
DEST = Path(os.environ.get("ROAST_JACQ_DEST", HERE / "set-mill-roast-jacq.json"))
MD_DEST = Path(os.environ.get("ROAST_JACQ_MD", HERE / "set-mill-roast-jacq.md"))

_STATS = ("jacq", "roast_mill_cards", "dawn", "hisuian_heavy_ball", "playground", "fired")


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        else:
            out.append(fallback_named(name))
    return out


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
        totals["jacq"] += result.events.get("jacq", 0)
        totals["roast_mill_cards"] += result.events.get("roast_mill_cards", 0)
        totals["dawn"] += result.events.get("dawn", 0)
        totals["hisuian_heavy_ball"] += result.events.get("hisuian_heavy_ball", 0)
        totals["playground"] += result.events.get(f"used_playground_{seat}", 0)
    cell = {"wr": wins / games, "fired": fired / games}
    for key in ("jacq", "roast_mill_cards", "dawn", "hisuian_heavy_ball", "playground"):
        cell[key] = totals[key] / games
    return cell


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}|roast-jacq-v1"


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
        "jacq": _avg(cells, "jacq"),
        "roast_mill_cards": _avg(cells, "roast_mill_cards"),
        "dawn": _avg(cells, "dawn"),
        "hisuian_heavy_ball": _avg(cells, "hisuian_heavy_ball"),
        "playground": _avg(cells, "playground"),
        "fired": _avg(cells, "fired"),
        "cells": {key: {"wr": cell["wr"], "a": cell["a"], "b": cell["b"]} for key, cell in cells.items()},
    }


def _markdown(report: dict) -> str:
    base = report["path"][0]
    lines = [
        "# Roast Jacq greedy",
        "",
        "Each step tries every other card as the one copy to replace with one Jacq. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.",
        "",
        "The starting 60 is the locked list: one Hisuian Heavy Ball in place of one Switch. Jacq searches the deck for up to 2 Evolution Pokémon. Roast takes Lampent while uncovered Litwick remain, counting Litwick that Playground will bench, then Chandelure once a Lampent is in hand or in play.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "## Path",
        "",
        "| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Jacq | Mill cards | Dawn | Heavy Ball | Playground |",
        "| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {copies} | {cut} | {weighted} | {se} | {mean} | {worst} | {delta} | {jacq:.2f} | {mill:.2f} | {dawn:.2f} | {heavy:.2f} | {play:.2f} |".format(
                label=row["label"],
                copies=row["copies"],
                cut=row.get("cut") or "—",
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                jacq=row["jacq"],
                mill=row["roast_mill_cards"],
                dawn=row["dawn"],
                heavy=row["hisuian_heavy_ball"],
                play=row["playground"],
            )
        )
    best = report["best"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                f"Kept list is {best['label']}: {best['copies']} Jacq, "
                f"weighted {_pct(best['weighted'])} against the locked list at {_pct(base['weighted'])} "
                f"({_signed(best['weighted'] - base['weighted'])})."
            ),
            "",
            "Counts:",
            "",
        ]
    )
    for name, count in best["counts"].items():
        lines.append(f"- {name} ×{count}")
    previous = base
    for rnd in report["rounds"]:
        lines.extend(
            [
                "",
                f"## Step {rnd['step']}",
                "",
                (
                    f"List entering this step: weighted {_pct(previous['weighted'])} ± {_pct(previous['se'])}. "
                    "Each row replaces one copy of that card with one Jacq."
                ),
                "",
                "| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Mill cards |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["rows"]:
            lines.append(
                "| {cut} | {before} | {weighted} | {se} | {mean} | {worst} | {delta} | {jacq:.2f} | {mill:.2f} |".format(
                    cut=row["cut"],
                    before=row["copies_before"],
                    weighted=_pct(row["weighted"]),
                    se=_pct(row["se"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous["weighted"]),
                    jacq=row["jacq"],
                    mill=row["roast_mill_cards"],
                )
            )
        kept = rnd.get("kept")
        lines.append("")
        if kept:
            lines.append(
                f"Kept −{kept['cut']} at {_pct(kept['weighted'])} ({_signed(kept['weighted'] - previous['weighted'])})."
            )
            previous = kept
        else:
            lines.append("No cut in this step was higher than the list already kept. The search stopped.")
    lines.extend(["", "## Foes at the kept list", "", "| Foe | A | B | Mean | Delta vs locked |", "| :--- | ---: | ---: | ---: | ---: |"])
    for key, label, *_rest in FOES:
        cell = best["cells"][key]
        base_cell = base["cells"][key]
        lines.append(
            f"| {label} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base_cell['wr'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    current = list(SET_ROAST_NAMES)
    if current.count("Jacq") != 0 or current.count("Hisuian Heavy Ball") != 1:
        raise SystemExit("baseline must be the locked Heavy Ball list with no Jacq")
    _check_list(current)
    cache = _load_cache()
    print(f"baseline locked, {GAMES} games, seed {SEED}", flush=True)
    base_seats = _evaluate([("locked", current)], GAMES, cache)["locked"]
    base = _row("locked", current, base_seats, None)
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
            kept["label"] = f"{winner['copies']} Jacq"
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
            "greedy one-card Jacq swaps from the locked roast 60; "
            "every other card name is tried as the cut; a step is kept only when its "
            "Sisters-weighted win rate is higher than the list already kept"
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
