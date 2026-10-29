#!/usr/bin/env python3
"""Add one Sleepy Voice Igglybuff to the current Doll 60.

Each step adds one copy and replaces one other card. Every cut is screened,
then the cuts that can still beat that step's baseline are confirmed at 400
games per seat. A confirm higher than its baseline becomes the next list, and
the next copy is measured. Four is the maximum. This script records the
sample; it does not edit SET_DOLL_NAMES.

Printed text (Cosmic Eclipse 168): once during your turn, before your attack,
you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep.
If you use this Ability, your turn ends. A Benched copy can use it. Doll uses
it when that Active is not already Asleep. The turn then has no attack.
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

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_DOLL_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    fallback_named,
)

ADD = "Igglybuff"
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

SCREEN_GAMES = int(os.environ.get("DOLL_IGGLYBUFF_SCREEN", "40"))
GAMES = int(os.environ.get("DOLL_IGGLYBUFF_GAMES", "400"))
SEED = int(os.environ.get("DOLL_IGGLYBUFF_SEED", "20261029"))
WORKERS = int(os.environ.get("DOLL_IGGLYBUFF_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("DOLL_IGGLYBUFF_PARTIAL", HERE / "set-doll-igglybuff-partial.jsonl"))
DEST = Path(os.environ.get("DOLL_IGGLYBUFF_DEST", HERE / "set-doll-igglybuff.json"))
MD_DEST = Path(os.environ.get("DOLL_IGGLYBUFF_MD", HERE / "set-doll-igglybuff.md"))

QUERIES = [
    {"type": "event_sum", "prefix": "doll_sleepy_flip", "key": "sleepy_flip"},
    {"type": "event_sum", "prefix": "doll_sleepy_heads", "key": "sleepy_heads"},
    {"type": "event_sum", "prefix": "doll_arven", "key": "arven"},
    {"type": "event_sum", "prefix": "doll_petrel", "key": "petrel"},
    {"type": "event_sum", "prefix": "proxy_play", "key": "proxy"},
    {"type": "event_sum", "prefix": "junk_hunt", "key": "junk_hunt"},
]
COUNT_KEYS = ("sleepy_flip", "sleepy_heads", "arven", "petrel", "proxy", "junk_hunt")


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        elif name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
        elif name == "Igglybuff":
            out.append(fallback_named("igglybuff sleepy"))
        else:
            out.append(fallback_named(name))
    return out


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(list(names))
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "doll", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "doll"
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=games,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": "doll-igglybuff", "name": "doll-igglybuff"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
    cell = {"wr": wr, "tie": result["tie_rate"]}
    for key in COUNT_KEYS:
        cell[key] = float(result["queries"].get(key, 0.0))
    return cell


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}"


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
            elapsed = time.perf_counter() - started
            left = elapsed / done * (len(futures) - done)
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
        for key in COUNT_KEYS:
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_count(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] * WEIGHTS[foe] for foe, *_ in FOES)


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]["wr"]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["wr"] for key, *_ in FOES)


def _avg(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] for foe, *_ in FOES) / len(FOES)


def _swap(names: list[str], cut: str, add: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(add)
    if len(out) != 60 or out.count(add) != names.count(add) + 1:
        raise ValueError(cut)
    return out


def _row(label: str, names: list[str], raw: dict[str, dict], games: int, cut: str | None) -> dict:
    cells = _combine(raw)
    return {
        "label": label,
        "cut": cut,
        "copies_before": 0 if cut is None else names.count(cut) + 1,
        "list": list(names),
        "weighted": _weighted(cells),
        "se": _weighted_se(raw, games),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "sleepy_flip": _avg(cells, "sleepy_flip"),
        "sleepy_flip_weighted": _weighted_count(cells, "sleepy_flip"),
        "sleepy_heads": _avg(cells, "sleepy_heads"),
        "sleepy_heads_weighted": _weighted_count(cells, "sleepy_heads"),
        "arven": _avg(cells, "arven"),
        "petrel": _avg(cells, "petrel"),
        "proxy": _avg(cells, "proxy"),
        "junk_hunt": _avg(cells, "junk_hunt"),
        "cells": cells,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _step(base_names: list[str], cache: dict[str, dict]) -> dict:
    have = base_names.count(ADD)
    if have >= 4:
        raise SystemExit(f"{ADD} is already at four")
    cuts = sorted(name for name in Counter(base_names) if name != ADD)
    screen_lists = [("baseline", base_names)] + [(cut, _swap(base_names, cut, ADD)) for cut in cuts]
    print(f"screen copy {have + 1}: {len(screen_lists)} lists", flush=True)
    screened = _evaluate(screen_lists, SCREEN_GAMES, cache)
    screen_rows = [
        _row(label, names, screened[label], SCREEN_GAMES, None if label == "baseline" else label)
        for label, names in screen_lists
    ]
    screen_rows.sort(key=lambda row: (-row["weighted"], row["cut"] or ""))
    base_screen = next(row for row in screen_rows if row["cut"] is None)
    band = max(base_screen["se"], screen_rows[0]["se"]) * 2
    floor = screen_rows[0]["weighted"] - band
    confirm_labels = ["baseline"]
    for row in screen_rows:
        if row["cut"] is None:
            continue
        if row["weighted"] + 1e-12 >= floor or len(confirm_labels) == 1:
            confirm_labels.append(row["cut"])
        if len(confirm_labels) >= 8:
            break
    if screen_rows[0]["cut"] and screen_rows[0]["cut"] not in confirm_labels:
        confirm_labels.append(screen_rows[0]["cut"])
    confirm_lists = [("baseline", base_names)] + [
        (cut, _swap(base_names, cut, ADD)) for cut in confirm_labels if cut != "baseline"
    ]
    print(f"confirm copy {have + 1}: " + ", ".join(label for label, _names in confirm_lists), flush=True)
    confirmed = _evaluate(confirm_lists, GAMES, cache)
    confirm_rows = [
        _row(label, names, confirmed[label], GAMES, None if label == "baseline" else label)
        for label, names in confirm_lists
    ]
    base = next(row for row in confirm_rows if row["cut"] is None)
    swaps = [row for row in confirm_rows if row["cut"]]
    best_swap = max(swaps, key=lambda row: (row["weighted"], row["worst"], -ord(row["cut"][0])))
    gap = best_swap["weighted"] - base["weighted"]
    gap_se = (best_swap["se"] ** 2 + base["se"] ** 2) ** 0.5
    kept = gap > 0
    locked = kept
    best = best_swap if locked else base
    return {
        "add": ADD,
        "starting_copies": have,
        "screen_band": band,
        "screen": [{key: value for key, value in row.items() if key != "list"} for row in screen_rows],
        "confirm": [
            {key: value for key, value in row.items() if key != "list"}
            for row in sorted(confirm_rows, key=lambda row: (row["cut"] is not None, -row["weighted"]))
        ],
        "baseline": {key: value for key, value in base.items() if key != "list"},
        "best_swap": {key: value for key, value in best_swap.items() if key != "list"},
        "best": {key: value for key, value in best.items() if key != "list"},
        "best_list": list(best["list"]),
        "gap": gap,
        "gap_se": gap_se,
        "kept": kept,
        "locked": locked,
    }


def _table(rows: list[dict], base_weighted: float) -> list[str]:
    lines = [
        "| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    ordered = sorted(rows, key=lambda row: (row["cut"] is not None, -row["weighted"]))
    for row in ordered:
        lines.append(
            "| {cut} | {weighted} | {se:.2%} | {delta} | {mean} | {worst} | {flip:.2f} | {heads:.2f} | {proxy:.2f} |".format(
                cut=row["cut"] or "— baseline —",
                weighted=_pct(row["weighted"]),
                se=row["se"],
                delta=_signed(row["weighted"] - base_weighted),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                flip=row["sleepy_flip"],
                heads=row["sleepy_heads"],
                proxy=row["proxy"],
            )
        )
    return lines


def _markdown(report: dict) -> str:
    lines = [
        "# Doll, Sleepy Voice Igglybuff",
        "",
        "Printed text: once during your turn (before your attack), you may flip a coin. "
        "If heads, your opponent's Active Pokémon is now Asleep. "
        "If you use this Ability, your turn ends. "
        "The sentence does not say the Active Spot, so a Benched Igglybuff can use it. "
        "Doll uses it when that Active is not already Asleep. The turn then has no attack. "
        "Slumbering Forest is the wake check that is already in the list.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Screen games per seat**: {report['screen_games']}",
        f"- **Confirm games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.",
        "- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Each step adds one Sleepy Voice Igglybuff. The confirm is 400 games per seat. "
        "A cut higher than that step's baseline is the next list. Four is the maximum. "
        "This sample is not the 1000-game holdout.",
        "",
    ]
    for index, step in enumerate(report["steps"], start=1):
        base = step["baseline"]
        swap = step["best_swap"]
        have = step.get("starting_copies", index - 1)
        lines.extend(
            [
                f"## Copy {have + 1}",
                "",
                "### Screen",
                "",
                *_table(step["screen"], next(row["weighted"] for row in step["screen"] if row["cut"] is None)),
                "",
                "### Confirm",
                "",
                *_table(step["confirm"], base["weighted"]),
                "",
            ]
        )
        if step["locked"]:
            lines.append(
                f"The confirm cuts one {swap['cut']} for copy {have + 1}. "
                f"Weighted {_pct(swap['weighted'])} vs {_pct(base['weighted'])} "
                f"({_signed(step['gap'])}; SE {swap['se']:.2%} on the swap and {base['se']:.2%} on the baseline, "
                f"so the gap's SE is about {step['gap_se']:.2%}, {step['gap'] / step['gap_se']:.1f} SE). "
                f"Sleepy Voice flips {swap['sleepy_flip_weighted']:.2f} times a game "
                f"and lands heads {swap['sleepy_heads_weighted']:.2f} times, on the Sisters weights."
            )
        else:
            lines.append(
                f"No confirm beat this baseline. Best confirm is {swap['cut']}: "
                f"weighted {_pct(swap['weighted'])} vs {_pct(base['weighted'])} "
                f"({_signed(step['gap'])}; the gap's SE is about {step['gap_se']:.2%}). "
                f"The list stays at {have} copies."
            )
        lines.append("")
        lines.append("| Foe | Baseline | " + " | ".join(row["cut"] for row in step["confirm"] if row["cut"]) + " |")
        lines.append("| :--- | ---: | " + " | ".join("---:" for row in step["confirm"] if row["cut"]) + " |")
        for key, label, *_rest in FOES:
            bits = [f"| {label} | {_pct(base['cells'][key]['wr'])}"]
            for row in step["confirm"]:
                if not row["cut"]:
                    continue
                bits.append(_pct(row["cells"][key]["wr"]))
            lines.append(" | ".join(bits) + " |")
        lines.append("")
    return "\n".join(lines)


def _load_prior() -> list[dict]:
    if not DEST.exists():
        return []
    old = json.loads(DEST.read_text())
    if old.get("steps"):
        return list(old["steps"])
    if old.get("step"):
        return [old["step"]]
    return []


def _resume(prior: list[dict], start: list[str]) -> tuple[list[dict], list[str] | None]:
    """Keep finished steps and continue from the last list that was kept."""
    kept: list[dict] = []
    base = list(start)
    for step in prior:
        have = step.get("starting_copies")
        if have is None and step.get("locked") and step.get("best_list", []).count(ADD) == 1:
            have = 0
        if have is None or have > base.count(ADD):
            break
        if have < base.count(ADD):
            kept.append(step)
            continue
        kept.append(step)
        if step.get("locked") and step.get("best_list"):
            base = list(step["best_list"])
            continue
        return kept, None
    return kept, base


def main() -> None:
    start = list(SET_DOLL_NAMES)
    if (
        len(start) != 60
        or start.count("Arven") != 1
        or start.count("Team Rocket's Petrel") != 1
        or start.count("Lillie's Determination") != 4
        or start.count("Igglybuff") != 0
    ):
        raise SystemExit("Doll lock is not the current 60")
    prior, base = _resume(_load_prior(), start)
    if base is None:
        print("the greedy already stopped", flush=True)
        return
    if base.count(ADD) >= 4:
        print("already at four copies", flush=True)
        return
    started = time.perf_counter()
    cache = _load_cache()
    steps = list(prior)
    while base and base.count(ADD) < 4:
        step = _step(base, cache)
        steps.append(step)
        report = {
            "seed": SEED,
            "screen_games": SCREEN_GAMES,
            "games": GAMES,
            "weights": WEIGHTS,
            "elapsed": time.perf_counter() - started,
            "steps": steps,
            "step": step,
        }
        DEST.write_text(json.dumps(report, indent=2) + "\n")
        MD_DEST.write_text(_markdown(report))
        print(
            f"copy {step['starting_copies'] + 1} locked={step['locked']} cut={step['best_swap']['cut']} "
            f"{_pct(step['best_swap']['weighted'])} baseline {_pct(step['baseline']['weighted'])} "
            f"gap {_signed(step['gap'])} gap_se {step['gap_se']:.2%}",
            flush=True,
        )
        if not step["locked"]:
            break
        base = list(step["best_list"])
    print(MD_DEST, flush=True)


if __name__ == "__main__":
    main()
