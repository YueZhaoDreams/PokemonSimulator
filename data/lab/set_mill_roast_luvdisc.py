#!/usr/bin/env python3
"""Joint greedy for Luvdisc on the locked Celebi ◇ roast.

Each step changes one card. The choices are one more Luvdisc, one Fire Energy
replaced by Water Energy, one Slumbering Forest, or one Switch. Every legal
cut is screened, the best few are played out at the full game count, and the
step is kept only when that full count beats the list already kept.

Water Pulse cannot be paid with Fire, and Slumbering Forest scores as the
second lock only when Luvdisc is in the deck. A one-card step never holds both
pieces. After that search stops, the package cross confirms the best Luvdisc
cuts at 0, 1, 3, and 7 Water, then continues the same one-card greedy from the
best of those lists. The first package step also confirms Forest and Switch
together. The locked list changes only when a full confirm beats it.

Luvdisc is Paldea Evolved 47. Matching searches the deck for up to 2 Supporter
cards. Water Pulse costs one Water Energy and the opponent's Active Pokémon
is now Asleep. Slumbering Forest makes the between-turns check two coins.
Pichu is the Sweet Sleeping Face wall. The two asleep Pokémon are the dual lock:
the face prevents attack damage, and the opponent's Active cannot attack or retreat.

Seed 20261027, the same seed as the locked roast. Games per seat from
LUVDISC_GAMES (default 400). The screen is LUVDISC_SCREEN (default 40).
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

# The mill engine stays. Everything else, including Fire Energy and Pichu, can be the cut.
KEEP_LAST = {"Celebi ◇", "Litwick", "Lampent", "Chandelure"}

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

GAMES = int(os.environ.get("LUVDISC_GAMES", "400"))
SCREEN = int(os.environ.get("LUVDISC_SCREEN", "40"))
TOP = int(os.environ.get("LUVDISC_TOP", "3"))
MAX_STEPS = int(os.environ.get("LUVDISC_STEPS", "8"))
SEED = int(os.environ.get("LUVDISC_SEED", "20261027"))
WORKERS = int(os.environ.get("LUVDISC_WORKERS", str(os.cpu_count() or 2)))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("LUVDISC_PARTIAL", "/tmp/mill-roast-luvdisc-partial.jsonl"))
DEST = Path(os.environ.get("LUVDISC_DEST", HERE / "set-mill-roast-luvdisc.json"))
MD_DEST = Path(os.environ.get("LUVDISC_MD", HERE / "set-mill-roast-luvdisc.md"))

_STATS = (
    "luvdisc_matching",
    "water_pulse",
    "slumbering_forest",
    "roast_mill_cards",
    "dawn",
    "playground",
)


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
    basics = sum(1 for card in pile if card.is_pokemon and card.is_basic)
    if basics < 1:
        raise SystemExit("list has no Basic Pokémon")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"list is illegal: {bad}")
    luv = next(card for card in pile if card.name == "Luvdisc") if names.count("Luvdisc") else None
    if luv is not None:
        kinds = {eff.get("kind") for atk in luv.attacks for eff in atk.effects}
        if "search_supporter" not in kinds or "status" not in kinds:
            raise SystemExit("Luvdisc is not Matching plus Water Pulse")


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
    totals = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        roast_is_a = seat == "a"
        if (roast_is_a and result.winner == "a") or (not roast_is_a and result.winner == "b"):
            wins += 1
        for key in _STATS:
            totals[key] += result.events.get(key, 0)
    cell = {"wr": wins / games}
    for key in _STATS:
        cell[key] = totals[key] / games
    return cell


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}|roast-luvdisc-v1"


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


def _swap(names: list[str], add: str, cut: str, limit: int | None) -> list[str] | None:
    if cut == add or names.count(cut) <= 0:
        return None
    if limit is not None and names.count(add) >= limit:
        return None
    if cut in KEEP_LAST and names.count(cut) <= 1:
        return None
    out = list(names)
    out.remove(cut)
    out.append(add)
    if len(out) != 60:
        return None
    return out


def _cuts(names: list[str], add: str) -> list[str]:
    counts = Counter(names)
    return sorted(
        name
        for name, count in counts.items()
        if count > 0 and name != add and not (name in KEEP_LAST and count <= 1)
    )


def _actions(names: list[str]) -> list[tuple[str, list[str], str, str]]:
    found: list[tuple[str, list[str], str, str]] = []
    seen: set[tuple[tuple[str, int], ...]] = set()

    def push(add: str, cut: str, new: list[str] | None, limit: int | None) -> None:
        if new is None:
            return
        key = tuple(sorted(Counter(new).items()))
        if key in seen:
            return
        try:
            _check_list(new)
        except SystemExit as exc:
            print(f"  skip +{add}/-{cut}: {exc}", flush=True)
            return
        seen.add(key)
        found.append((f"+{add}/-{cut}", new, add, cut))

    if names.count("Luvdisc") < 4:
        for cut in _cuts(names, "Luvdisc"):
            push("Luvdisc", cut, _swap(names, "Luvdisc", cut, 4), 4)
    if names.count("Fire Energy") > 0:
        push("Water Energy", "Fire Energy", _swap(names, "Water Energy", "Fire Energy", None), None)
    if names.count("Slumbering Forest") < 4:
        for cut in _cuts(names, "Slumbering Forest"):
            push("Slumbering Forest", cut, _swap(names, "Slumbering Forest", cut, 4), 4)
    if names.count("Switch") < 2:
        for cut in _cuts(names, "Switch"):
            push("Switch", cut, _swap(names, "Switch", cut, 2), 2)
    return found


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _row(label: str, names: list[str], seats: dict[str, dict], add: str | None, cut: str | None, games: int) -> dict:
    cells = _combine(seats)
    return {
        "label": label,
        "add": add,
        "cut": cut,
        "luvdisc": names.count("Luvdisc"),
        "water": names.count("Water Energy"),
        "fire": names.count("Fire Energy"),
        "forest": names.count("Slumbering Forest"),
        "switch": names.count("Switch"),
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, games),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "matching": _avg(cells, "luvdisc_matching"),
        "pulse": _avg(cells, "water_pulse"),
        "forest_checks": _avg(cells, "slumbering_forest"),
        "roast_mill_cards": _avg(cells, "roast_mill_cards"),
        "dawn": _avg(cells, "dawn"),
        "playground": _avg(cells, "playground"),
        "cells": {key: {"wr": cell["wr"], "a": cell["a"], "b": cell["b"]} for key, cell in cells.items()},
        "games": games,
    }


def _markdown(report: dict) -> str:
    base = report["path"][0]
    lines = [
        "# Celebi ◇ roast with Luvdisc",
        "",
        "Luvdisc is Paldea Evolved 47. Matching says: search your deck for up to 2 Supporter cards, reveal them, and put them into your hand, then shuffle. Water Pulse costs Water, does 20, and the opponent's Active Pokémon is now Asleep.",
        "",
        "Pichu is the sleep wall. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Slumbering Forest makes the between-turns check two coins, so either tails and the Pokémon is still Asleep. That is the dual lock: the face holds on our side, and the opponent's Active cannot attack or retreat.",
        "",
        "Playground still benches Litwick first. Once Luvdisc is in the deck, that attack leaves a slot for Celebi ◇ and a slot for Luvdisc, so the line stops at three Litwick. Matching takes Petrel when the Asleep wall needs Switch, then Jacq or Dawn, then Hop or Arven. Water Pulse is the attack when none of those Supporters are left to find. Celebi ◇ is paid first on a mill turn. Water goes to Luvdisc otherwise. Fire still pays Matching and Time Distortion. Forest does not replace Broken Time-Space while a same-turn evolution is waiting.",
        "",
        "Each greedy step tries one more Luvdisc, one Fire Energy replaced by Water Energy, one Slumbering Forest, or one Switch. The screen is short. The best few cuts are confirmed at the full game count. A step is kept only when that confirm is higher than the list already kept. The last Celebi ◇, Litwick, Lampent, and Chandelure are not cuts.",
        "",
        "Water Pulse costs Water, so one Luvdisc with seven Fire Energy never puts the opponent to sleep. Forest's second lock turns on only when that Luvdisc is in the deck. The one-card search cannot hold both. After it stops, the three best Luvdisc cuts are confirmed with 0, 1, 3, and 7 Water. The best of those lists is the package seed. The same one-card greedy continues from that seed, and the first of those steps also confirms one Forest and one Switch on the same list.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        f"- **Screen**: {report['screen']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "## Path",
        "",
        "| Step | Add | Cut | Luvdisc | Water | Fire | Forest | Switch | Weighted | ± | Delta | Matching | Pulse | Mill cards |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {add} | {cut} | {luv} | {water} | {fire} | {forest} | {switch} | {weighted} | {se} | {delta} | {matching:.2f} | {pulse:.2f} | {mill:.2f} |".format(
                label=row["label"],
                add=row.get("add") or "—",
                cut=row.get("cut") or "—",
                luv=row["luvdisc"],
                water=row["water"],
                fire=row["fire"],
                forest=row["forest"],
                switch=row["switch"],
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                matching=row["matching"],
                pulse=row["pulse"],
                mill=row["roast_mill_cards"],
            )
        )
    best = report["best"]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            report["decision"],
            "",
            "Counts on the kept list:",
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
                    "Screen rows are the short run. Confirm rows are the full run."
                ),
                "",
                "| Add | Cut | Screen | Confirm | ± | Delta | Luvdisc | Water | Fire | Forest | Switch | Matching | Pulse | Mill |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["rows"]:
            confirm = row.get("confirm")
            lines.append(
                "| {add} | {cut} | {screen} | {confirm} | {se} | {delta} | {luv} | {water} | {fire} | {forest} | {switch} | {matching:.2f} | {pulse:.2f} | {mill:.2f} |".format(
                    add=row["add"],
                    cut=row["cut"],
                    screen=_pct(row["screen"]),
                    confirm=_pct(confirm) if confirm is not None else "—",
                    se=_pct(row["se"]) if confirm is not None else "—",
                    delta=_signed(confirm - previous["weighted"]) if confirm is not None else "—",
                    luv=row["luvdisc"],
                    water=row["water"],
                    fire=row["fire"],
                    forest=row["forest"],
                    switch=row["switch"],
                    matching=row["matching"],
                    pulse=row["pulse"],
                    mill=row["roast_mill_cards"],
                )
            )
        kept = rnd.get("kept")
        lines.append("")
        if kept:
            lines.append(
                f"Kept +{kept['add']} −{kept['cut']} at {_pct(kept['weighted'])} ({_signed(kept['weighted'] - previous['weighted'])})."
            )
            previous = kept
        else:
            lines.append("No confirm in this step was higher than the list already kept. The search stopped.")
    lines.extend(
        [
            "",
            "## Foes at the kept list",
            "",
            "| Foe | A | B | Mean | Delta vs locked |",
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
    package = report.get("package")
    if package and package.get("cross"):
        lines.extend(_package_markdown(report))
    return "\n".join(lines)


def _package_markdown(report: dict) -> list[str]:
    base = report["path"][0]
    package = report["package"]
    lines = [
        "## Package",
        "",
        "These lists start from a Luvdisc cut the one-card screen ranked highly, then replace Fire Energy with Water Energy. Zero Water is Matching only. Seven Water is every Fire turned into Water. The seed is the highest confirm in this table. Later steps may sit below the locked list; a step is kept when it beats the package list, and the lock moves only when the package beats the lock.",
        "",
        "| List | Water | Fire | Weighted | ± | Delta | Matching | Pulse | Mill cards |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in package["cross"]:
        lines.append(
            "| {label} | {water} | {fire} | {weighted} | {se} | {delta} | {matching:.2f} | {pulse:.2f} | {mill:.2f} |".format(
                label=row["label"],
                water=row["water"],
                fire=row["fire"],
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                matching=row["matching"],
                pulse=row["pulse"],
                mill=row["roast_mill_cards"],
            )
        )
    seed = package.get("seed")
    if seed is not None:
        lines.extend(
            [
                "",
                f"Package seed: {seed['label']} at {_pct(seed['weighted'])} ({_signed(seed['weighted'] - base['weighted'])}).",
            ]
        )
    for rnd in package.get("rounds") or []:
        previous = package["path"][rnd["step"] - 1]
        joint = any(row.get("screen") is None and row.get("confirm") is not None for row in rnd["rows"])
        note = (
            " The Forest+Switch row is two cards on this same list. It has no screen."
            if joint
            else ""
        )
        lines.extend(
            [
                "",
                f"## Package step {rnd['step']}",
                "",
                (
                    f"List entering this step: weighted {_pct(previous['weighted'])} ± {_pct(previous['se'])}."
                    + note
                ),
                "",
                "| Add | Cut | Screen | Confirm | ± | Delta | Luvdisc | Water | Fire | Forest | Switch | Matching | Pulse | Mill |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["rows"]:
            confirm = row.get("confirm")
            screen = row.get("screen")
            lines.append(
                "| {add} | {cut} | {screen} | {confirm} | {se} | {delta} | {luv} | {water} | {fire} | {forest} | {switch} | {matching:.2f} | {pulse:.2f} | {mill:.2f} |".format(
                    add=row["add"],
                    cut=row["cut"],
                    screen=_pct(screen) if screen is not None else "—",
                    confirm=_pct(confirm) if confirm is not None else "—",
                    se=_pct(row["se"]) if confirm is not None and row.get("se") is not None else "—",
                    delta=_signed(confirm - previous["weighted"]) if confirm is not None else "—",
                    luv=row["luvdisc"],
                    water=row["water"],
                    fire=row["fire"],
                    forest=row["forest"],
                    switch=row["switch"],
                    matching=row["matching"],
                    pulse=row["pulse"],
                    mill=row["roast_mill_cards"],
                )
            )
        kept = rnd.get("kept")
        lines.append("")
        if kept:
            lines.append(
                f"Kept +{kept['add']} −{kept['cut']} at {_pct(kept['weighted'])} ({_signed(kept['weighted'] - previous['weighted'])})."
            )
        else:
            lines.append("No confirm in this step was higher than the package list. The package search stopped.")
    return lines


def _with_water_count(names: list[str], water: int) -> list[str] | None:
    """Turn Fire into Water, or Water back into Fire, until the Water count is exact."""
    out = list(names)
    have = out.count("Water Energy")
    if have == water:
        return out
    if have < water:
        need = water - have
        if out.count("Fire Energy") < need:
            return None
        for _ in range(need):
            out.remove("Fire Energy")
            out.append("Water Energy")
        return out
    if out.count("Water Energy") < have - water:
        return None
    for _ in range(have - water):
        out.remove("Water Energy")
        out.append("Fire Energy")
    return out


def _joint_forest_switch(names: list[str], screen_rows: list[dict]) -> tuple[str, list[str], str, str] | None:
    """One Forest and one Switch, using the best screen cut for each that are different cards."""
    forests = [row for row in screen_rows if row["add"] == "Slumbering Forest"]
    switches = [row for row in screen_rows if row["add"] == "Switch"]
    if not forests or not switches:
        return None
    forests.sort(key=lambda item: (item["weighted"], item["worst"], item["label"]), reverse=True)
    switches.sort(key=lambda item: (item["weighted"], item["worst"], item["label"]), reverse=True)
    forest = forests[0]
    switch = next((row for row in switches if row["cut"] != forest["cut"]), None)
    if switch is None:
        return None
    first = _swap(names, "Slumbering Forest", forest["cut"], 4)
    if first is None:
        return None
    both = _swap(first, "Switch", switch["cut"], 2)
    if both is None:
        return None
    try:
        _check_list(both)
    except SystemExit as exc:
        print(f"  skip Forest+Switch: {exc}", flush=True)
        return None
    label = f"+Slumbering Forest+Switch/-{forest['cut']}+{switch['cut']}"
    return label, both, "Slumbering Forest+Switch", f"{forest['cut']}+{switch['cut']}"


def _package_cross(step_rows: list[dict], cache: dict[str, dict]) -> list[dict]:
    """Best Luvdisc screens, each with 0, 1, 3, and every remaining Fire turned into Water."""
    luv = [row for row in step_rows if row["add"] == "Luvdisc"]
    luv.sort(key=lambda item: (item["screen"], item["label"]), reverse=True)
    jobs: list[tuple[str, list[str], str, str, int]] = []
    seen: set[tuple[tuple[str, int], ...]] = set()
    for row in luv[:TOP]:
        for water in (0, 1, 3, 7):
            names = _with_water_count(row["list"], water)
            if names is None:
                continue
            key = tuple(sorted(Counter(names).items()))
            if key in seen:
                continue
            try:
                _check_list(names)
            except SystemExit as exc:
                print(f"  skip {row['label']} water {water}: {exc}", flush=True)
                continue
            seen.add(key)
            jobs.append((f"+Luvdisc/-{row['cut']}/w{water}", names, "Luvdisc", row["cut"], water))
    if not jobs:
        return []
    print(f"package cross: {len(jobs)} lists at {GAMES}", flush=True)
    confirmed = _evaluate([(label, names) for label, names, _add, _cut, _water in jobs], GAMES, cache)
    found = []
    for label, names, add, cut, water in jobs:
        full = _row(label, names, confirmed[label], add, cut, GAMES)
        full["water_target"] = water
        print(
            f"  cross {label} {full['weighted']:.2%} ± {full['se']:.2%} "
            f"pulse {full['pulse']:.2f} matching {full['matching']:.2f}",
            flush=True,
        )
        found.append(full)
    return found


def _package_greedy(
    seed: dict,
    cross: list[dict],
    cache: dict[str, dict],
    started: float,
    path: list[dict],
    rounds: list[dict],
) -> dict:
    """One-card greedy from a Luvdisc list that already has its Water count."""
    current = list(seed["list"])
    pkg_path = [seed]
    pkg_rounds: list[dict] = []
    for step_no in range(1, MAX_STEPS + 1):
        options = _actions(current)
        if not options:
            break
        print(f"package step {step_no}: screen {len(options)} lists at {SCREEN}", flush=True)
        screened = _evaluate([(label, names) for label, names, _add, _cut in options], SCREEN, cache)
        screen_rows = []
        for label, names, add, cut in options:
            row = _row(label, names, screened[label], add, cut, SCREEN)
            row["screen"] = row["weighted"]
            row["confirm"] = None
            screen_rows.append(row)
        screen_rows.sort(key=lambda item: (item["weighted"], item["worst"], item["label"]), reverse=True)
        pool = _confirm_pool(screen_rows)
        joint = None
        if step_no == 1:
            joint = _joint_forest_switch(current, screen_rows)
        confirm_jobs = [(row["label"], row["list"], row["add"], row["cut"]) for row in pool]
        if joint is not None and joint[0] not in {label for label, *_rest in confirm_jobs}:
            confirm_jobs.append(joint)
            print(f"  joint {joint[0]}", flush=True)
        print(
            "  screen best " + ", ".join(f"{row['label']} {row['weighted']:.2%}" for row in pool),
            flush=True,
        )
        print(f"  confirm {len(confirm_jobs)} at {GAMES}", flush=True)
        confirmed = _evaluate([(label, names) for label, names, _add, _cut in confirm_jobs], GAMES, cache)
        by_label = {row["label"]: row for row in screen_rows}
        fulls = []
        for label, names, add, cut in confirm_jobs:
            full = _row(label, names, confirmed[label], add, cut, GAMES)
            fulls.append(full)
            if label in by_label:
                by_label[label]["confirm"] = full["weighted"]
                by_label[label]["se"] = full["se"]
                by_label[label]["full"] = full
            print(f"  confirm {label} {full['weighted']:.2%} ± {full['se']:.2%}", flush=True)
        winner = max(fulls, key=lambda item: (item["weighted"], item["worst"], item["label"]))
        kept = None
        if winner["weighted"] > pkg_path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"+{winner['add']} −{winner['cut']}"
            current = list(winner["list"])
            pkg_path.append(kept)
            print(f"  kept {kept['label']} {kept['weighted']:.2%}", flush=True)
        else:
            print(
                f"  {winner['label']} {winner['weighted']:.2%} did not beat {pkg_path[-1]['weighted']:.2%}",
                flush=True,
            )
        shown = []
        for row in screen_rows:
            shown.append(
                {
                    "add": row["add"],
                    "cut": row["cut"],
                    "screen": row["screen"],
                    "confirm": row.get("confirm"),
                    "se": row["se"] if row.get("confirm") is not None else None,
                    "luvdisc": row["luvdisc"],
                    "water": row["water"],
                    "fire": row["fire"],
                    "forest": row["forest"],
                    "switch": row["switch"],
                    "matching": row["matching"],
                    "pulse": row["pulse"],
                    "roast_mill_cards": row["roast_mill_cards"],
                    "label": row["label"],
                }
            )
        if joint is not None:
            joint_full = next(item for item in fulls if item["label"] == joint[0])
            shown.append(
                {
                    "add": joint[2],
                    "cut": joint[3],
                    "screen": None,
                    "confirm": joint_full["weighted"],
                    "se": joint_full["se"],
                    "luvdisc": joint_full["luvdisc"],
                    "water": joint_full["water"],
                    "fire": joint_full["fire"],
                    "forest": joint_full["forest"],
                    "switch": joint_full["switch"],
                    "matching": joint_full["matching"],
                    "pulse": joint_full["pulse"],
                    "roast_mill_cards": joint_full["roast_mill_cards"],
                    "label": joint[0],
                }
            )
        pkg_rounds.append({"step": step_no, "rows": shown, "kept": kept})
        partial = {
            "cross": cross,
            "seed": seed,
            "path": pkg_path,
            "rounds": pkg_rounds,
            "best": max(pkg_path, key=lambda item: (item["weighted"], -pkg_path.index(item))),
        }
        _write(path, rounds, started, partial)
        if kept is None:
            break
    best = max(pkg_path, key=lambda item: (item["weighted"], -pkg_path.index(item)))
    return {"seed": seed, "path": pkg_path, "rounds": pkg_rounds, "best": best}


def _package(path: list[dict], rounds: list[dict], cache: dict[str, dict], started: float) -> dict:
    step_rows = rounds[0]["rows"] if rounds else []
    cross = _package_cross(step_rows, cache)
    if not cross:
        return {"cross": [], "seed": None, "path": [], "rounds": [], "best": None}
    seed = max(cross, key=lambda item: (item["weighted"], item["worst"], item["label"]))
    print(
        f"package seed {seed['label']} {seed['weighted']:.2%} "
        f"(lock {path[0]['weighted']:.2%})",
        flush=True,
    )
    _write(
        path,
        rounds,
        started,
        {"cross": cross, "seed": seed, "path": [seed], "rounds": [], "best": seed},
    )
    greedy = _package_greedy(seed, cross, cache, started, path, rounds)
    greedy["cross"] = cross
    _write(path, rounds, started, greedy)
    return greedy


def _confirm_pool(screen_rows: list[dict]) -> list[dict]:
    ranked = sorted(screen_rows, key=lambda item: (item["weighted"], item["worst"], item["label"]), reverse=True)
    if not ranked:
        return []
    best = ranked[0]["weighted"]
    near = [row for row in ranked if row["weighted"] >= best - 0.02]
    return near[:TOP]


def main() -> None:
    started = time.perf_counter()
    current = list(SET_ROAST_NAMES)
    if (
        current.count("Luvdisc")
        or current.count("Water Energy")
        or current.count("Slumbering Forest")
        or current.count("Switch")
        or current.count("Fire Energy") != 7
        or current.count("Hop") != 4
    ):
        raise SystemExit("Luvdisc search starts from the locked roast: 7 Fire, 4 Hop, no Luvdisc, no Forest, no Switch")
    _check_list(current)
    cache = _load_cache()
    print(f"baseline locked, {GAMES} games, seed {SEED}", flush=True)
    base_seats = _evaluate([("locked", current)], GAMES, cache)["locked"]
    base = _row("locked", current, base_seats, None, None, GAMES)
    print(f"  weighted {base['weighted']:.2%} ± {base['se']:.2%}", flush=True)
    path = [base]
    rounds: list[dict] = []
    for step_no in range(1, MAX_STEPS + 1):
        options = _actions(current)
        if not options:
            break
        print(f"step {step_no}: screen {len(options)} lists at {SCREEN}", flush=True)
        screened = _evaluate([(label, names) for label, names, _add, _cut in options], SCREEN, cache)
        screen_rows = []
        for label, names, add, cut in options:
            row = _row(label, names, screened[label], add, cut, SCREEN)
            row["screen"] = row["weighted"]
            row["confirm"] = None
            screen_rows.append(row)
        screen_rows.sort(key=lambda item: (item["weighted"], item["worst"], item["label"]), reverse=True)
        pool = _confirm_pool(screen_rows)
        print(
            "  screen best "
            + ", ".join(f"{row['label']} {row['weighted']:.2%}" for row in pool),
            flush=True,
        )
        print(f"  confirm {len(pool)} at {GAMES}", flush=True)
        confirmed = _evaluate([(row["label"], row["list"]) for row in pool], GAMES, cache)
        by_label = {row["label"]: row for row in screen_rows}
        for row in pool:
            full = _row(row["label"], row["list"], confirmed[row["label"]], row["add"], row["cut"], GAMES)
            by_label[row["label"]]["confirm"] = full["weighted"]
            by_label[row["label"]]["se"] = full["se"]
            by_label[row["label"]]["weighted_full"] = full["weighted"]
            by_label[row["label"]]["full"] = full
            print(f"  confirm {row['label']} {full['weighted']:.2%} ± {full['se']:.2%}", flush=True)
        ranked_full = sorted(
            (by_label[row["label"]]["full"] for row in pool),
            key=lambda item: (item["weighted"], item["worst"], item["label"]),
            reverse=True,
        )
        winner = ranked_full[0]
        kept = None
        if winner["weighted"] > path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"+{winner['add']} −{winner['cut']}"
            current = list(winner["list"])
            path.append(kept)
            print(f"  kept {kept['label']} {kept['weighted']:.2%}", flush=True)
        else:
            print(
                f"  {winner['label']} {winner['weighted']:.2%} did not beat {path[-1]['weighted']:.2%}",
                flush=True,
            )
        shown = []
        for row in screen_rows:
            shown.append(
                {
                    "add": row["add"],
                    "cut": row["cut"],
                    "screen": row["screen"],
                    "confirm": row.get("confirm"),
                    "se": row["se"] if row.get("confirm") is not None else None,
                    "luvdisc": row["luvdisc"],
                    "water": row["water"],
                    "fire": row["fire"],
                    "forest": row["forest"],
                    "switch": row["switch"],
                    "matching": row["matching"],
                    "pulse": row["pulse"],
                    "roast_mill_cards": row["roast_mill_cards"],
                    "label": row["label"],
                    "list": row["list"],
                    "counts": row["counts"],
                }
            )
        rounds.append({"step": step_no, "rows": shown, "kept": kept})
        _write(path, rounds, started)
        if kept is None:
            break
    package = _package(path, rounds, cache, started)
    _write(path, rounds, started, package)
    best = _overall_best(path, package)
    print(
        f"kept {best['label']} weighted {best['weighted']:.2%} -> {MD_DEST}",
        flush=True,
    )


def _overall_best(path: list[dict], package: dict | None) -> dict:
    best = max(path, key=lambda item: (item["weighted"], -path.index(item)))
    if package and package.get("best") and package["best"]["weighted"] > best["weighted"]:
        return package["best"]
    return best


def _decision(path: list[dict], package: dict | None = None) -> str:
    base = path[0]
    best = _overall_best(path, package)
    delta = best["weighted"] - base["weighted"]
    if best is base or best["weighted"] <= base["weighted"]:
        sentences = [
            f"The locked roast stays. No confirmed list beat {_pct(base['weighted'])} ± {_pct(base['se'])}."
        ]
        if package and package.get("cross"):
            seed = max(package["cross"], key=lambda item: (item["weighted"], item["worst"], item["label"]))
            sentences.append(
                f"The highest Luvdisc confirm is {seed['label']} at {_pct(seed['weighted'])} "
                f"({_signed(seed['weighted'] - base['weighted'])})."
            )
            watered = [row for row in package["cross"] if row["water"] > 0]
            if watered:
                top_water = max(watered, key=lambda item: (item["weighted"], item["pulse"], item["label"]))
                fullest = max(watered, key=lambda item: (item["water"], item["pulse"]))
                sentences.append(
                    f"The highest confirm with Water Energy is {top_water['label']} at {_pct(top_water['weighted'])}. "
                    f"On {fullest['water']} Water, Water Pulse fires {fullest['pulse']:.2f} times per game."
                )
            if package.get("best") and package["best"]["label"] != seed["label"]:
                pb = package["best"]
                gain = pb["weighted"] - seed["weighted"]
                noise = " That step is inside one standard error of the seed." if gain < pb["se"] else ""
                sentences.append(
                    f"Greedy steps from that seed reach {pb['label']} at {_pct(pb['weighted'])} "
                    f"({_signed(pb['weighted'] - base['weighted'])})."
                    + noise
                )
        for rnd in (package or {}).get("rounds") or []:
            for row in rnd["rows"]:
                if row.get("add") == "Slumbering Forest+Switch" and row.get("confirm") is not None:
                    sentences.append(
                        f"Forest and Switch together on the Luvdisc list confirm at {_pct(row['confirm'])}."
                    )
        return " ".join(sentences)
    return (
        f"Kept list is {best['label']}: Luvdisc ×{best['luvdisc']}, Water ×{best['water']}, "
        f"Fire ×{best['fire']}, Slumbering Forest ×{best['forest']}, Switch ×{best['switch']}. "
        f"Weighted {_pct(best['weighted'])} against the locked list at {_pct(base['weighted'])} "
        f"({_signed(delta)}). The screen picks the best of many cuts, so a small confirm can sit a little high."
    )


def _write(path: list[dict], rounds: list[dict], started: float, package: dict | None = None) -> None:
    best = _overall_best(path, package)
    report = {
        "seed": SEED,
        "games": GAMES,
        "screen": SCREEN,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "method": (
            "joint greedy one-card swaps from the locked Celebi roast; each step may add one Luvdisc, "
            "replace one Fire Energy with Water Energy, add one Slumbering Forest, or add one Switch; "
            "every legal cut is screened and the best few are confirmed; a step is kept only when the "
            "full Sisters-weighted win rate is higher than the list already kept; after that search stops, "
            "the best Luvdisc cuts are confirmed at 0, 1, 3, and 7 Water and the same greedy continues "
            "from the best of those lists, with Forest and Switch also confirmed together on the first package step"
        ),
        "decision": _decision(path, package),
        "path": path,
        "best": best,
        "rounds": rounds,
        "package": package,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))


if __name__ == "__main__":
    main()
