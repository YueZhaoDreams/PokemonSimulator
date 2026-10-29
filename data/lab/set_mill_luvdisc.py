#!/usr/bin/env python3
"""Greedy Paldea Evolved Luvdisc on the locked Mill 60.

Matching searches for up to 2 Supporter cards. Water Pulse does 20 and puts the
opponent's Active to sleep. Slumbering Forest makes that check two coins.
Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep.
Those two layers are the double protection.

Each step adds one Luvdisc and cuts one other card. Every legal cut is screened
on the short sample. The three best cuts are confirmed on the long sample.
A step keeps a confirm only when its loss-weighted win rate is higher.
Weights are the frozen Sisters 60 loss weights.

Seed 20261030. Screen games from MILL_LUVDISC_SCREEN (default 30). Confirm
games from MILL_LUVDISC_GAMES (default 80). Both seats.

MILL_LUVDISC_SMOKE=1 plays two foes for 8 games and exits.
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
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
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

ADD = "Luvdisc"
PROTECT = {
    "Wiglett",
    "Wugtrio",
    "Victini",
    "Pichu",
    "Mime Jr.",
    "Cleffa",
    "Manaphy",
    "Luvdisc",
    "Slumbering Forest",
    "Neutralization Zone",
}

SCREEN_GAMES = int(os.environ.get("MILL_LUVDISC_SCREEN", "30"))
GAMES = int(os.environ.get("MILL_LUVDISC_GAMES", "80"))
SEED = int(os.environ.get("MILL_LUVDISC_SEED", "20261030"))
WORKERS = int(os.environ.get("MILL_LUVDISC_WORKERS", str(os.cpu_count() or 2)))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("MILL_LUVDISC_PARTIAL", HERE / "set-mill-luvdisc-partial.jsonl"))
DEST = Path(os.environ.get("MILL_LUVDISC_DEST", HERE / "set-mill-luvdisc.json"))
MD_DEST = Path(os.environ.get("MILL_LUVDISC_MD", HERE / "set-mill-luvdisc.md"))
CONFIRM_N = int(os.environ.get("MILL_LUVDISC_CONFIRM", "3"))

QUERIES = [
    {"type": "event_sum", "prefix": "match_use", "key": "matching"},
    {"type": "event_sum", "prefix": "match_take", "key": "matching_cards"},
    {"type": "event_sum", "prefix": "opponent_asleep", "key": "opponent_asleep"},
    {"type": "event_sum", "prefix": "slumbering_forest", "key": "forest"},
    {"type": "event_sum", "prefix": "sweet_sleeping_face", "key": "face"},
    {"type": "event_sum", "prefix": "mill_attack", "key": "mill_attack"},
    {"type": "event_prefix", "prefix": "saw_play:Luvdisc", "key": "luvdisc"},
    {"type": "event_prefix", "prefix": "stadium:Slumbering Forest", "key": "forest_play"},
]
STAT_KEYS = (
    "matching",
    "matching_cards",
    "opponent_asleep",
    "forest",
    "face",
    "mill_attack",
    "luvdisc",
    "forest_play",
)


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
        elif name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
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
        strat_a, strat_b = "mill", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "mill"
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=games,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": "mill-luvdisc", "name": "mill-luvdisc"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
    cell = {"wr": wr, "tie": result["tie_rate"]}
    for key in STAT_KEYS:
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
        for foe_key, *_rest in FOES:
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
            if done == 1 or done % 8 == 0 or done == len(futures):
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
    for foe_key, *_rest in FOES:
        a = cells[foe_key]["a"]
        b = cells[foe_key]["b"]
        row = {"wr": (a["wr"] + b["wr"]) / 2, "a": a["wr"], "b": b["wr"]}
        for key in STAT_KEYS:
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_rest in FOES)


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_rest in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["wr"] for key, *_rest in FOES)


def _avg(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] for foe, *_rest in FOES) / len(FOES)


def _swap(names: list[str], cut: str) -> list[str] | None:
    if names.count(ADD) >= 4:
        return None
    if names.count(cut) <= 0 or cut in PROTECT:
        return None
    out = list(names)
    out.remove(cut)
    out.append(ADD)
    if len(out) != 60:
        return None
    return out


def _cuts(names: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(names).items() if count > 0 and name not in PROTECT)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _row(label: str, names: list[str], cells: dict[str, dict], cut: str | None, games: int) -> dict:
    return {
        "label": label,
        "cut": cut,
        "add": None if cut is None else ADD,
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "se": _weighted_se(cells, games),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "matching": _avg(cells, "matching"),
        "matching_cards": _avg(cells, "matching_cards"),
        "opponent_asleep": _avg(cells, "opponent_asleep"),
        "forest": _avg(cells, "forest"),
        "face": _avg(cells, "face"),
        "mill_attack": _avg(cells, "mill_attack"),
        "luvdisc": _avg(cells, "luvdisc"),
        "forest_play": _avg(cells, "forest_play"),
        "cells": {
            key: {"wr": row["wr"], "a": row["a"], "b": row["b"]}
            for key, row in cells.items()
        },
    }


def _screen_row(cut: str, cells: dict[str, dict], score: float) -> dict:
    return {
        "cut": cut,
        "weighted": score,
        "mean": _mean(cells),
        "worst": _worst(cells),
        "matching": _avg(cells, "matching"),
        "opponent_asleep": _avg(cells, "opponent_asleep"),
        "mill_attack": _avg(cells, "mill_attack"),
        "luvdisc": _avg(cells, "luvdisc"),
    }


def _markdown(report: dict) -> str:
    base = report["path"][0]
    best = report["best"]
    lines = [
        "# Mill greedy Luvdisc",
        "",
        "Paldea Evolved Luvdisc. Matching searches the deck for up to 2 Supporter cards. "
        "Water Pulse does 20 and the opponent's Active is Asleep. "
        "Slumbering Forest flips 2 coins between turns and the Pokémon stays Asleep unless both are heads. "
        "Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. "
        "Forest and Sweet Sleeping Face are the two protections.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Screen games per seat**: {report['screen_games']}",
        f"- **Confirm games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.",
        "- **Weights**: "
        + ", ".join(f"{key} {WEIGHTS[key]:.1%}" for key, *_rest in FOES),
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate, measured on the confirm sample. "
        "A step keeps the confirm only when the weighted rate rises.",
        "",
        "## Greedy path",
        "",
        "| Step | Add | Cut | Luvdisc | Weighted | ± | Mean | Worst | Delta | Matching | Asleep | Forest checks | Face blocks | Mill attacks |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {add} | {cut} | {count} | {weighted} | {se} | {mean} | {worst} | {delta} | {matching:.2f} | {asleep:.2f} | {forest:.2f} | {face:.2f} | {mill:.2f} |".format(
                label=row["label"],
                add=row.get("add") or "—",
                cut=row.get("cut") or "—",
                count=row["counts"].get(ADD, 0),
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                matching=row["matching"],
                asleep=row["opponent_asleep"],
                forest=row["forest"],
                face=row["face"],
                mill=row["mill_attack"],
            )
        )
    delta = best["weighted"] - base["weighted"]
    delta_se = (best["se"] ** 2 + base["se"] ** 2) ** 0.5
    kept = best["label"] != base["label"] and delta > delta_se
    closest = None
    for rnd in report["rounds"]:
        for row in rnd["confirms"]:
            if closest is None or row["weighted"] > closest["weighted"]:
                closest = row
    if kept:
        decision = (
            f"Best confirm is {best['label']}: weighted {_pct(best['weighted'])} "
            f"vs the lock at {_pct(base['weighted'])} ({_signed(delta)}, difference ±{_pct(delta_se)}). "
            f"Mean {_pct(best['mean'])} ({_signed(best['mean'] - base['mean'])}). "
            "The gain is larger than one standard error of the difference. "
            f"That list cuts {best.get('cut')} for Luvdisc ×{best['counts'].get(ADD, 0)}."
        )
    elif closest is not None:
        gap = closest["weighted"] - base["weighted"]
        gap_se = (closest["se"] ** 2 + base["se"] ** 2) ** 0.5
        decision = (
            f"No confirm beat the lock. The closest is −{closest['cut']} at {_pct(closest['weighted'])} "
            f"({_signed(gap)}, difference ±{_pct(gap_se)}). "
            f"Matching averaged {closest['matching']:.2f} per game and the opponent fell Asleep "
            f"{closest['opponent_asleep']:.2f} times per game. Luvdisc saw play in {closest['luvdisc']:.0%} of games. "
            "The gap is not a gain, so SET_MILL_NAMES stays the current 60."
        )
    else:
        decision = (
            f"No confirm beat the lock by more than one standard error. "
            f"Best sample is {best['label']} at {_pct(best['weighted'])} "
            f"vs the lock at {_pct(base['weighted'])} ({_signed(delta)}, difference ±{_pct(delta_se)}). "
            "SET_MILL_NAMES stays the current 60."
        )
    lines.extend(["", "## Decision", "", decision, "", "Counts on the best sample:", ""])
    for name, count in sorted(best["counts"].items(), key=lambda item: (-item[1], item[0])):
        if name == ADD or count != base["counts"].get(name, 0):
            lines.append(f"- {name}: {count}")
    lines.append(f"- Luvdisc saw play: {best['luvdisc']:.2f} per game")
    lines.append(f"- Slumbering Forest entered play: {best['forest_play']:.2f} per game")
    for rnd in report["rounds"]:
        lines.extend(
            [
                "",
                f"## Step {rnd['step']}",
                "",
                (
                    f"Screen leader −{rnd['screen_cut']} at {_pct(rnd['screen_best'])}. "
                    f"The list entering this step screened at {_pct(rnd['screen_lock'])}. "
                    f"The top {len(rnd['confirms'])} cuts were confirmed at {report['games']} games per seat."
                ),
                "",
            ]
        )
        screened = rnd.get("screened") or []
        if screened:
            lines.extend(
                [
                    "Every legal cut, on the short sample:",
                    "",
                    "| Cut | Screen | Mean | Worst | Delta | Matching | Asleep | Luvdisc | Mill attacks |",
                    "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
                ]
            )
            for row in screened:
                lines.append(
                    "| {cut} | {weighted} | {mean} | {worst} | {delta} | {matching:.2f} | {asleep:.2f} | {luvdisc:.2f} | {mill:.2f} |".format(
                        cut=row["cut"],
                        weighted=_pct(row["weighted"]),
                        mean=_pct(row["mean"]),
                        worst=_pct(row["worst"]),
                        delta=_signed(row["weighted"] - rnd["screen_lock"]),
                        matching=row["matching"],
                        asleep=row["opponent_asleep"],
                        luvdisc=row["luvdisc"],
                        mill=row["mill_attack"],
                    )
                )
            lines.append("")
        lines.extend(
            [
                "| Cut | Screen | Confirmed | ± | Mean | Worst | Delta | Matching | Asleep | Mill attacks |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        previous = rnd["entering"]
        for row in rnd["confirms"]:
            lines.append(
                "| {cut} | {screen} | {weighted} | {se} | {mean} | {worst} | {delta} | {matching:.2f} | {asleep:.2f} | {mill:.2f} |".format(
                    cut=row["cut"],
                    screen=_pct(row["screen_weighted"]),
                    weighted=_pct(row["weighted"]),
                    se=_pct(row["se"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous),
                    matching=row["matching"],
                    asleep=row["opponent_asleep"],
                    mill=row["mill_attack"],
                )
            )
        kept_row = rnd.get("kept")
        lines.append("")
        if kept_row:
            lines.append(
                f"Kept −{kept_row['cut']} at {_pct(kept_row['weighted'])} "
                f"({_signed(kept_row['weighted'] - previous)})."
            )
        else:
            lines.append("No confirm in this step was higher than the list already kept. The search stopped.")
        if rnd["confirms"] and best["label"] == base["label"]:
            lines.extend(
                [
                    "",
                    "Confirmed matchups. Each cell is the mean of the two seats, then the delta against the lock.",
                    "",
                    "| Foe | Lock | "
                    + " | ".join(f"−{row['cut']}" for row in rnd["confirms"])
                    + " |",
                    "| :--- | ---: | " + " | ".join("---:" for _ in rnd["confirms"]) + " |",
                ]
            )
            for key, label, *_rest in FOES:
                bits = [_pct(base["cells"][key]["wr"])]
                for row in rnd["confirms"]:
                    wr = row["cells"][key]["wr"]
                    bits.append(f"{_pct(wr)} ({_signed(wr - base['cells'][key]['wr'])})")
                lines.append("| " + " | ".join([label, *bits]) + " |")
    lines.extend(
        ["", "## Foes at the best sample", "", "| Foe | A | B | Mean | Delta vs lock |", "| :--- | ---: | ---: | ---: | ---: |"]
    )
    for key, label, *_rest in FOES:
        cell = best["cells"][key]
        base_cell = base["cells"][key]
        lines.append(
            f"| {label} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base_cell['wr'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _smoke() -> None:
    names = list(SET_MILL_NAMES)
    names.remove("Crushing Hammer")
    names.append(ADD)
    started = time.perf_counter()
    for foe_key in ("s60", "c60"):
        cell = _run(tuple(names), foe_key, "a", 8, SEED)
        print(
            f"smoke vs {foe_key}: {cell['wr']:.1%} matching {cell['matching']:.2f} "
            f"asleep {cell['opponent_asleep']:.2f} luvdisc {cell['luvdisc']:.2f} "
            f"mill {cell['mill_attack']:.2f}",
            flush=True,
        )
    print(f"smoke {time.perf_counter() - started:.1f}s", flush=True)


def _public(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "cells"} | {"cells": row["cells"]}


def main() -> None:
    if os.environ.get("MILL_LUVDISC_SMOKE") == "1":
        _smoke()
        return
    started = time.perf_counter()
    current = list(SET_MILL_NAMES)
    if len(current) != 60:
        raise SystemExit(f"mill lock is {len(current)} cards")
    cache = _load_cache()
    print(f"baseline games={GAMES} screen={SCREEN_GAMES}", flush=True)
    base_cells = _combine(_evaluate([("lock", current)], GAMES, cache)["lock"])
    base = _row("lock", current, base_cells, None, GAMES)
    print(f"  weighted {base['weighted']:.2%} ± {base['se']:.2%}", flush=True)
    path = [base]
    rounds: list[dict] = []
    while current.count(ADD) < 4:
        screened: list[tuple[float, str, list[str]]] = []
        options = []
        for cut in _cuts(current):
            swapped = _swap(current, cut)
            if swapped is None:
                continue
            options.append((f"screen -{cut}", cut, swapped))
        if not options:
            break
        print(f"step {len(rounds) + 1}: screen {len(options)} cuts", flush=True)
        screen_eval = _evaluate([(label, names) for label, _cut, names in options], SCREEN_GAMES, cache)
        lock_screen = _combine(_evaluate([("screen-lock", current)], SCREEN_GAMES, cache)["screen-lock"])
        for label, cut, names in options:
            cells = _combine(screen_eval[label])
            screened.append((_weighted(cells), cut, names))
        screened.sort(key=lambda item: (item[0], item[1]), reverse=True)
        screen_rows = []
        for score, cut, names in screened:
            cells = _combine(screen_eval[f"screen -{cut}"])
            screen_rows.append(_screen_row(cut, cells, score))
        pending = screened[:CONFIRM_N]
        print(
            f"  screen best -{pending[0][1]} {pending[0][0]:.2%} vs lock screen {_weighted(lock_screen):.2%}",
            flush=True,
        )
        confirm_lists = [(f"confirm -{cut}", names) for _score, cut, names in pending]
        confirm_eval = _evaluate(confirm_lists, GAMES, cache)
        confirms = []
        for score, cut, names in pending:
            cells = _combine(confirm_eval[f"confirm -{cut}"])
            row = _row(f"-{cut}", names, cells, cut, GAMES)
            row["screen_weighted"] = score
            confirms.append(row)
            print(f"  confirm -{cut} {row['weighted']:.2%} ± {row['se']:.2%}", flush=True)
        confirms.sort(key=lambda item: (item["weighted"], item["worst"]), reverse=True)
        winner = confirms[0]
        kept = None
        if winner["weighted"] > path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"step {len(rounds) + 1}"
            current = list(winner["list"])
            path.append(kept)
        rounds.append(
            {
                "step": len(rounds) + 1,
                "entering": path[-2]["weighted"] if kept else path[-1]["weighted"],
                "screen_cut": pending[0][1],
                "screen_best": pending[0][0],
                "screen_lock": _weighted(lock_screen),
                "screened": screen_rows,
                "confirms": [_public(row) for row in confirms],
                "kept": None if kept is None else _public(kept),
            }
        )
        if kept is None:
            print("  did not improve; stop", flush=True)
            break
    best = max(path, key=lambda item: item["weighted"])
    report = {
        "seed": SEED,
        "screen_games": SCREEN_GAMES,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "path": [_public(row) for row in path],
        "rounds": rounds,
        "best": _public(best),
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(MD_DEST.read_text())


if __name__ == "__main__":
    main()
