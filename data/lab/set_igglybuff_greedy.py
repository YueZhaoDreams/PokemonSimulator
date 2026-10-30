#!/usr/bin/env python3
"""Greedy Sleepy Voice Igglybuff for Mill and Celebi Mill.

Each step adds one Cosmic Eclipse 168 Igglybuff and tries every other card as
the cut. The confirm is 400 games per seat. A cut is kept only when its
Sisters-weighted win rate is higher than the list already kept. Four is the
maximum. This script records the sample. It does not edit the locked lists.

The recorded Mill search used the pre-lock 60: one Boss's Orders and no Igglybuff.
Re-running it after the lock stops, because that list already contains Igglybuff.

The coin is the Doll benefit rule. Demolish spends the turn on it. Undersea
Tunnel, Sleepy Lost, Eeeeeeek, and the first Playground stay ahead on Mill.
Time Distortion, Kindling Panic, Playground, and Eeeeeeek stay ahead on
Celebi Mill. A turn with none of those still flips when the hit would land.
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

from app.engine.legality import copy_violations
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

ADD = "Igglybuff"
POLICY = "benefit"
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

GAMES = int(os.environ.get("IGGLY_GAMES", "400"))
SEED = int(os.environ.get("IGGLY_SEED", "20261029"))
WORKERS = int(os.environ.get("IGGLY_WORKERS", str(os.cpu_count() or 2)))
HERE = Path(__file__).resolve().parent
QUERIES = [
    {"type": "event_sum", "prefix": "sleepy_flip", "key": "sleepy_flip"},
    {"type": "event_sum", "prefix": "sleepy_heads", "key": "sleepy_heads"},
    {"type": "event_sum", "prefix": "mill_opponent", "key": "mill_cards"},
    {"type": "event_sum", "prefix": "roast_mill_cards", "key": "roast_mill_cards"},
    {"type": "event_sum", "prefix": "saw_play:Igglybuff", "key": "plays"},
]
COUNT_KEYS = ("sleepy_flip", "sleepy_heads", "mill_cards", "roast_mill_cards", "plays")

SPECS = {
    "mill": {
        "title": "Mill, Sleepy Voice Igglybuff",
        "strat": "mill",
        "names": list(SET_MILL_NAMES),
        "progress": "mill_cards",
        "progress_label": "Mill cards",
        "partial": HERE / "set-mill-igglybuff-partial.jsonl",
        "dest": HERE / "set-mill-igglybuff.json",
        "md": HERE / "set-mill-igglybuff.md",
        "plan": (
            "Undersea Tunnel, Sleepy Lost, Eeeeeeek, and the first Playground stay ahead of the coin. "
            "The coin replaces those attacks only when the hit ignores effects on the Active, as Demolish does. "
            "A turn with none of those attacks still flips when their hit would land. "
            "One Igglybuff is benched once a Wiglett is already in play or in hand. "
            "Poffin takes it after the wall and the first Wiglett. Level Ball still finds Wugtrio. "
            "Slumbering Forest is already in this list, so the wake check is two coins."
        ),
    },
    "roast": {
        "title": "Celebi Mill, Sleepy Voice Igglybuff",
        "strat": "roast",
        "names": list(SET_ROAST_NAMES),
        "progress": "roast_mill_cards",
        "progress_label": "Roast mill",
        "partial": HERE / "set-mill-roast-igglybuff-partial.jsonl",
        "dest": HERE / "set-mill-roast-igglybuff.json",
        "md": HERE / "set-mill-roast-igglybuff.md",
        "plan": (
            "Time Distortion, Kindling Panic, Playground, and Eeeeeeek stay ahead of the coin. "
            "The coin replaces those attacks only when the hit ignores effects on the Active, as Demolish does. "
            "A turn that cannot mill or Playground still flips when their hit would land. "
            "One copy is benched once three Litwick lines are out, in the slot a fourth line would have used. "
            "Celebi ◇ keeps its Bench spot. This list has no Slumbering Forest, so the wake check is one coin."
        ),
    },
}


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


def _check(names: list[str]) -> None:
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


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int, strat: str) -> dict:
    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(list(names))
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = strat, foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, strat
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=games,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": f"{strat}-igglybuff", "name": f"{strat}-igglybuff"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
    cell = {"wr": wr}
    for key in COUNT_KEYS:
        cell[key] = float(result["queries"].get(key, 0.0))
    return cell


def _cache_key(kind: str, names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{POLICY}|{kind}|{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}"


def _load_cache(path: Path) -> dict[str, dict]:
    found: dict[str, dict] = {}
    if not path.exists():
        return found
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found[row["key"]] = row["cell"]
    return found


def _append(path: Path, key: str, cell: dict) -> None:
    with path.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")


def _evaluate(kind: str, strat: str, lists: list[tuple[str, list[str]]], cache: dict[str, dict], partial: Path):
    jobs = []
    out: dict[str, dict[str, dict]] = {label: {} for label, _names in lists}
    for label, names in lists:
        frozen = tuple(names)
        for foe_key, *_ in FOES:
            for seat in ("a", "b"):
                key = _cache_key(kind, frozen, foe_key, seat, GAMES, SEED)
                cached = cache.get(key)
                if cached is not None:
                    out[label].setdefault(foe_key, {})[seat] = cached
                    continue
                jobs.append((label, frozen, foe_key, seat, key))
    print(f"  {len(jobs)} cells, {GAMES} games, {WORKERS} workers", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, frozen, foe_key, seat, GAMES, SEED, strat): (label, foe_key, seat, key)
            for label, frozen, foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            label, foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(partial, key, cell)
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
        for key in COUNT_KEYS:
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_count(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] * WEIGHTS[foe] for foe, *_ in FOES)


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


def _row(label: str, names: list[str], seats: dict[str, dict], cut: str | None, progress: str) -> dict:
    cells = _combine(seats)
    return {
        "label": label,
        "cut": cut,
        "copies": names.count(ADD),
        "copies_before": None if cut is None else names.count(cut) + (0 if cut == ADD else 1),
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, GAMES),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "sleepy_flip": _weighted_count(cells, "sleepy_flip"),
        "sleepy_heads": _weighted_count(cells, "sleepy_heads"),
        "plays": _weighted_count(cells, "plays"),
        "progress": _weighted_count(cells, progress),
        "cells": {key: {"wr": cell["wr"], "a": cell["a"], "b": cell["b"]} for key, cell in cells.items()},
    }


def _swap(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(ADD)
    if len(out) != 60 or out.count(ADD) != names.count(ADD) + 1:
        raise ValueError(cut)
    return out


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _public(row: dict) -> dict:
    return {key: value for key, value in row.items() if key != "list"}


def _markdown(spec: dict, report: dict) -> str:
    base = report["path"][0]
    progress = spec["progress_label"]
    lines = [
        f"# {spec['title']}",
        "",
        "Printed text: once during your turn (before your attack), you may flip a coin. "
        "If heads, your opponent's Active Pokémon is now Asleep. "
        "If you use this Ability, your turn ends. "
        "The sentence does not say the Active Spot, so a Benched Igglybuff can use it.",
        "",
        spec["plan"],
        "",
        "Each step tries every other card as the one copy to replace with one Sleepy Voice Igglybuff. "
        "The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "This sample is not the 1000-game holdout.",
        "",
        "## Path",
        "",
        f"| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Flips | Heads | Plays | {progress} |",
        "| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {copies} | {cut} | {weighted} | {se} | {mean} | {worst} | {delta} | {flip:.2f} | {heads:.2f} | {plays:.2f} | {progress:.2f} |".format(
                label=row["label"],
                copies=row["copies"],
                cut=row.get("cut") or "—",
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                flip=row["sleepy_flip"],
                heads=row["sleepy_heads"],
                plays=row["plays"],
                progress=row["progress"],
            )
        )
    best = report["best"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                f"Kept list is {best['label']}: {best['copies']} {ADD}, "
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
                    f"Each row replaces one copy of that card with one {ADD}."
                ),
                "",
                f"| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flips | Heads | Plays | {progress} |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        ordered = sorted(rnd["rows"], key=lambda item: item["weighted"], reverse=True)
        for row in ordered:
            lines.append(
                "| {cut} | {before} | {weighted} | {se} | {mean} | {worst} | {delta} | {flip:.2f} | {heads:.2f} | {plays:.2f} | {progress:.2f} |".format(
                    cut=row["cut"],
                    before=row["copies_before"],
                    weighted=_pct(row["weighted"]),
                    se=_pct(row["se"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous["weighted"]),
                    flip=row["sleepy_flip"],
                    heads=row["sleepy_heads"],
                    plays=row["plays"],
                    progress=row["progress"],
                )
            )
        kept = rnd.get("kept")
        lines.append("")
        if kept:
            gap_se = kept.get("gap_se") or 0.0
            se_text = f", {kept['gap'] / gap_se:.1f} SE" if gap_se else ""
            lines.append(
                f"Kept −{kept['cut']} at {_pct(kept['weighted'])} "
                f"({_signed(kept['weighted'] - previous['weighted'])}{se_text}). "
                f"Sleepy Voice flips {kept['sleepy_flip']:.2f} times a game and lands heads {kept['sleepy_heads']:.2f} times."
            )
            lines.append("")
            lines.append("| Foe | Baseline | Kept | Delta |")
            lines.append("| :--- | ---: | ---: | ---: |")
            for key, label, *_rest in FOES:
                before = previous["cells"][key]["wr"]
                after = kept["cells"][key]["wr"]
                lines.append(f"| {label} | {_pct(before)} | {_pct(after)} | {_signed(after - before)} |")
            previous = kept
        else:
            winner = ordered[0]
            lines.append(
                f"No cut beat this list. Best cut is {winner['cut']}: "
                f"weighted {_pct(winner['weighted'])} vs {_pct(previous['weighted'])} "
                f"({_signed(winner['weighted'] - previous['weighted'])})."
            )
    lines.append("")
    return "\n".join(lines)


def _save(spec: dict, report: dict) -> None:
    spec["dest"].write_text(json.dumps(report, indent=2) + "\n")
    spec["md"].write_text(_markdown(spec, report))


def _check_start(kind: str, names: list[str]) -> None:
    _check(names)
    if names.count(ADD) != 0:
        raise SystemExit(f"{kind} already contains {ADD}")
    if kind == "mill":
        if (
            names.count("Wiglett") != 4
            or names.count("Wugtrio") != 4
            or names.count("Level Ball") != 4
            or names.count("Manaphy") != 1
            or names.count("Cleffa") != 1
            or names.count("Slumbering Forest") != 1
        ):
            raise SystemExit("Mill lock is not the current 60")
    if kind == "roast":
        if (
            names.count("Hop") != 4
            or names.count("Jacq") != 2
            or names.count("Hyper Aroma") != 1
            or names.count("Evolution Incense") != 3
            or names.count("Celebi ◇") != 1
            or names.count("Litwick") != 4
        ):
            raise SystemExit("Celebi Mill lock is not the current 60")


def run(kind: str) -> dict:
    spec = SPECS[kind]
    partial = Path(os.environ.get("IGGLY_PARTIAL", spec["partial"]))
    spec = dict(spec)
    spec["partial"] = partial
    spec["dest"] = Path(os.environ.get("IGGLY_DEST", spec["dest"]))
    spec["md"] = Path(os.environ.get("IGGLY_MD", spec["md"]))
    current = list(spec["names"])
    _check_start(kind, current)
    started = time.perf_counter()
    carried = 0.0
    path: list[dict] = []
    rounds: list[dict] = []
    if spec["dest"].exists():
        old = json.loads(spec["dest"].read_text())
        if old.get("policy") == POLICY and old.get("seed") == SEED and old.get("games") == GAMES and old.get("deck") == kind:
            path = list(old.get("path") or [])
            rounds = list(old.get("rounds") or [])
            carried = float(old.get("elapsed") or 0.0)
            if path:
                current = list(path[-1]["list"])
            if rounds and rounds[-1].get("kept") is None:
                print(f"{kind}: the greedy already stopped", flush=True)
                return old
            if current.count(ADD) >= MAX_COPIES:
                print(f"{kind}: already at four copies", flush=True)
                return old
    cache = _load_cache(partial)
    progress = spec["progress"]
    if not path:
        print(f"{kind} baseline, {GAMES} games, seed {SEED}", flush=True)
        seats = _evaluate(kind, spec["strat"], [("locked", current)], cache, partial)["locked"]
        base = _row("locked", current, seats, None, progress)
        print(f"  weighted {base['weighted']:.2%} ± {base['se']:.2%}", flush=True)
        path = [base]
    while current.count(ADD) < MAX_COPIES:
        cuts = sorted(name for name in Counter(current) if name != ADD)
        options = [(cut, _swap(current, cut)) for cut in cuts]
        for _cut, names in options:
            _check(names)
        print(f"{kind} step {len(rounds) + 1}: {len(options)} cuts", flush=True)
        evaluated = _evaluate(kind, spec["strat"], options, cache, partial)
        rows = [_row(cut, names, evaluated[cut], cut, progress) for cut, names in options]
        rows.sort(key=lambda item: (item["weighted"], item["worst"], item["cut"]), reverse=True)
        winner = rows[0]
        previous = path[-1]
        gap = winner["weighted"] - previous["weighted"]
        gap_se = (winner["se"] ** 2 + previous["se"] ** 2) ** 0.5
        print(
            f"  best -{winner['cut']} {winner['weighted']:.2%} ± {winner['se']:.2%} "
            f"vs {previous['weighted']:.2%} gap {gap:+.2%} gap_se {gap_se:.2%}",
            flush=True,
        )
        kept = None
        if gap > 0:
            kept = _public(winner)
            kept["label"] = f"{winner['copies']} {ADD}"
            kept["gap"] = gap
            kept["gap_se"] = gap_se
            kept["list"] = list(winner["list"])
            current = list(winner["list"])
            path.append(kept)
        rounds.append(
            {
                "step": len(rounds) + 1,
                "rows": [_public(row) for row in rows],
                "kept": kept,
            }
        )
        best = max(path, key=lambda item: (item["weighted"], -path.index(item)))
        report = {
            "deck": kind,
            "policy": POLICY,
            "seed": SEED,
            "games": GAMES,
            "weights": WEIGHTS,
            "elapsed": carried + (time.perf_counter() - started),
            "method": (
                f"greedy one-card {ADD} swap from the locked {kind} 60; "
                "every other card name is tried as the cut; a step is kept only when its "
                "Sisters-weighted win rate is higher than the list already kept"
            ),
            "path": [_public(row) | {"list": row["list"]} for row in path],
            "best": _public(best) | {"list": best["list"]},
            "rounds": rounds,
        }
        _save(spec, report)
        if kept is None:
            print(f"{kind}: did not improve; stop", flush=True)
            return report
    print(f"{kind}: stopped at {current.count(ADD)} -> {spec['md']}", flush=True)
    return json.loads(spec["dest"].read_text())


def main() -> None:
    kinds = sys.argv[1:] or ["mill", "roast"]
    for kind in kinds:
        if kind not in SPECS:
            raise SystemExit(f"unknown deck {kind}")
        run(kind)


if __name__ == "__main__":
    main()
