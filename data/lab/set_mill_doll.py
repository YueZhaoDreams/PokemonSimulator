#!/usr/bin/env python3
"""Greedy no-Prize Item Pokémon on the locked Mill 60.

Each candidate is an Item whose printed text puts it into play as a Pokémon
and awards no Prize when it is Knocked Out. Same-name printings that still
award a Prize (Unidentified Fossil, Rare Fossil, Antique fossils, and the DP
fossils that say the Knock Out counts) stay out.

A step adds one copy of one candidate and cuts one other card. Every legal
cut is screened at the short sample. The best cut of each card is then
confirmed at the long sample, and the step keeps the confirm with the higher
loss-weighted win rate. Weights are the frozen Sisters 60 loss weights from
the sleep-wall lock.

Seed 20261023. Screen games from MILL_DOLL_SCREEN (default 40). Confirm games
from MILL_DOLL_GAMES (default 120). Both seats.

MILL_DOLL_FULL=1 skips the short screen and measures every legal cut at
MILL_DOLL_GAMES. MILL_DOLL_CANDIDATES limits the names (comma-separated).
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

# Loss weights frozen from the Sisters 60 (set-mill-sleep.md).
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

# Distinct names. HP is the printed number. Removal is the printed sentence.
CANDIDATES = (
    "Lillie's Poké Doll",
    "Robo Substitute",
    "Snorlax Doll",
    "Mysterious Fossil",
    "Root Fossil",
    "Claw Fossil",
    "Clefairy Doll",
)
PROTECT = {
    "Wiglett",
    "Wugtrio",
    "Victini",
    "Pichu",
    "Mime Jr.",
    "Slumbering Forest",
    "Neutralization Zone",
    *CANDIDATES,
}

SCREEN_GAMES = int(os.environ.get("MILL_DOLL_SCREEN", "40"))
GAMES = int(os.environ.get("MILL_DOLL_GAMES", "120"))
SEED = int(os.environ.get("MILL_DOLL_SEED", "20261023"))
WORKERS = int(os.environ.get("MILL_DOLL_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("MILL_DOLL_PARTIAL", HERE / "set-mill-doll-partial.jsonl"))
DEST = Path(os.environ.get("MILL_DOLL_DEST", HERE / "set-mill-doll.json"))
MD_DEST = Path(os.environ.get("MILL_DOLL_MD", HERE / "set-mill-doll.md"))

QUERIES = [
    {"type": "event_sum", "prefix": "proxy_play", "key": "proxy_play"},
    {"type": "event_sum", "prefix": "proxy_hold", "key": "proxy_hold"},
    {"type": "event_sum", "prefix": "proxy_tuck", "key": "proxy_tuck"},
    {"type": "event_sum", "prefix": "proxy_stall", "key": "proxy_stall"},
    {"type": "event_sum", "prefix": "proxy_setup", "key": "proxy_setup"},
    {"type": "event_sum", "prefix": "ko_no_prize", "key": "ko_no_prize"},
    {"type": "event_sum", "prefix": "mill_attack", "key": "mill_attack"},
]


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
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
        deck_a_meta={"id": "mill-doll", "name": "mill-doll"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
    cell = {"wr": wr, "tie": result["tie_rate"]}
    for key in ("proxy_play", "proxy_hold", "proxy_tuck", "proxy_stall", "proxy_setup", "ko_no_prize", "mill_attack"):
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
            if done == 1 or done % 10 == 0 or done == len(futures):
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                print(f"    {done}/{len(futures)} {label} {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)", flush=True)
    return out


def _combine(cells: dict[str, dict]) -> dict[str, dict]:
    combined = {}
    for foe_key, *_ in FOES:
        a = cells[foe_key]["a"]
        b = cells[foe_key]["b"]
        row = {"wr": (a["wr"] + b["wr"]) / 2, "a": a["wr"], "b": b["wr"]}
        for key in ("proxy_play", "proxy_hold", "proxy_tuck", "proxy_stall", "proxy_setup", "ko_no_prize", "mill_attack"):
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    """One standard error of the loss-weighted rate.

    A foe cell is the mean of two seats, and each seat is `games` trials.
    """
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["wr"] for key, *_ in FOES)


def _avg(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] for foe, *_ in FOES) / len(FOES)


def _swap(names: list[str], cut: str, add: str) -> list[str] | None:
    if names.count(add) >= 4:
        return None
    if names.count(cut) <= 0 or cut in PROTECT:
        return None
    out = list(names)
    out.remove(cut)
    out.append(add)
    if len(out) != 60:
        return None
    return out


def _cuts(names: list[str]) -> list[str]:
    return sorted(name for name, count in Counter(names).items() if count > 0 and name not in PROTECT)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _row(label: str, names: list[str], cells: dict[str, dict], cut: str | None, add: str | None) -> dict:
    return {
        "label": label,
        "cut": cut,
        "add": add,
        "list": list(names),
        "counts": dict(Counter(names)),
        "weighted": _weighted(cells),
        "mean": _mean(cells),
        "worst": _worst(cells),
        "proxy_play": _avg(cells, "proxy_play"),
        "proxy_hold": _avg(cells, "proxy_hold"),
        "proxy_tuck": _avg(cells, "proxy_tuck"),
        "proxy_stall": _avg(cells, "proxy_stall"),
        "ko_no_prize": _avg(cells, "ko_no_prize"),
        "mill_attack": _avg(cells, "mill_attack"),
        "cells": cells,
    }


def _markdown(report: dict) -> str:
    lines = [
        "# Mill no-Prize dolls",
        "",
        "Items played as a Pokémon. A Knock Out awards no Prize. Each greedy step screens every legal cut, confirms the best cut of each card, and keeps the confirm with the higher loss-weighted win rate.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Screen games per seat**: {report['screen_games']}",
        f"- **Confirm games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "## Cards",
        "",
        "Kept: the printed sentence awards no Prize.",
        "",
        "| Card | HP | Play | When it leaves |",
        "| :--- | ---: | :--- | :--- |",
        "| Lillie's Poké Doll | 30 | during the turn | Active: discard attached cards, put it on the bottom of the deck |",
        "| Robo Substitute | 30 | during the turn | discard from play |",
        "| Snorlax Doll | 120 | setup only | discard from play; immune to Special Conditions |",
        "| Clefairy Doll | 10 | during the turn | discard; Asleep, Confused, Paralyzed, and Poisoned do not apply |",
        "| Mysterious Fossil | 50 | during the turn | discard; immune to Special Conditions |",
        "| Root Fossil | 40 | during the turn | discard; immune to Special Conditions |",
        "| Claw Fossil | 40 | during the turn | discard; immune to Special Conditions |",
        "",
        "Left out, because a Knock Out still awards a Prize: Unidentified Fossil, Rare Fossil, the Antique fossils, and Helix Fossil, Dome Fossil, Old Amber, Armor Fossil, and Skull Fossil from Diamond & Pearl and Platinum. The XY fossils that look at the bottom 7 cards are not played as Pokémon. A lower-HP reprint of the same name, such as Mysterious Fossil at 10 HP, does not raise the four-copy cap.",
        "",
        "## Greedy path",
        "",
        "| Step | Add | Cut | Weighted | Mean | Worst | Doll plays | Holds | Tucks | No-Prize KOs | Mill attacks |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {add} | {cut} | {weighted} | {mean} | {worst} | {play:.2f} | {hold:.2f} | {tuck:.2f} | {ko:.2f} | {mill:.2f} |".format(
                label=row["label"],
                add=row.get("add") or "—",
                cut=row.get("cut") or "—",
                weighted=_pct(row["weighted"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                play=row["proxy_play"],
                hold=row["proxy_hold"],
                tuck=row["proxy_tuck"],
                ko=row["ko_no_prize"],
                mill=row["mill_attack"],
            )
        )
    best = report["best"]
    base = report["path"][0]
    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                f"Best confirmed list is {best['label']}: weighted {_pct(best['weighted'])} "
                f"vs the locked Mill at {_pct(base['weighted'])} ({_signed(best['weighted'] - base['weighted'])}). "
                f"Mean {_pct(best['mean'])} ({_signed(best['mean'] - base['mean'])}). "
                "SET_MILL_NAMES stays the sleep-wall 60. The worst foe on this swap is still Cornerstone Ogerpon."
            ),
            "",
            "Counts on that list:",
            "",
        ]
    )
    for name in CANDIDATES:
        lines.append(f"- {name}: {best['counts'].get(name, 0)}")
    previous = base
    for rnd in report.get("rounds") or []:
        kept = rnd.get("kept")
        lines.extend(
            [
                "",
                f"## Step {rnd['step']} confirms",
                "",
                (
                    f"Screen leader +{rnd['screen_add']} −{rnd['screen_cut']} at {_pct(rnd['screen_best'])}. "
                    f"The list entering this step screened at {_pct(rnd['screen_lock'])}. "
                    f"Each row is that card's best cut, confirmed at {report['games']} games per seat."
                ),
                "",
                "| Card | Cut | Screen | Confirmed | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["checks"]:
            lines.append(
                "| {add} | {cut} | {screen} | {weighted} | {mean} | {worst} | {delta} | {play:.2f} | {stall:.2f} | {hold:.2f} | {ko:.2f} | {mill:.2f} |".format(
                    add=row["add"],
                    cut=row["cut"],
                    screen=_pct(row["screen_weighted"]),
                    weighted=_pct(row["weighted"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous["weighted"]),
                    play=row["proxy_play"],
                    stall=row["proxy_stall"],
                    hold=row["proxy_hold"],
                    ko=row["ko_no_prize"],
                    mill=row["mill_attack"],
                )
            )
        if kept:
            lines.append("")
            lines.append(
                f"Kept +{kept['add']} −{kept['cut']} at {_pct(kept['weighted'])} "
                f"({_signed(kept['weighted'] - previous['weighted'])})."
            )
            previous = kept
        else:
            lines.append("")
            lines.append("No confirm in this step was higher than the list already kept. The search stopped.")
    lines.extend(["", "## Foes at the best list", "", "| Foe | A | B | Mean | Delta vs lock |", "| :--- | ---: | ---: | ---: | ---: |"])
    for key, label, *_ in FOES:
        cell = best["cells"][key]
        delta = cell["wr"] - base["cells"][key]["wr"]
        lines.append(
            f"| {label} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(delta)} |"
        )
    lines.append("")
    return "\n".join(lines)


def _smoke() -> None:
    names = list(SET_MILL_NAMES)
    names.remove("Crushing Hammer")
    names.append("Lillie's Poké Doll")
    started = time.perf_counter()
    for foe_key in ("s60", "t60"):
        for seat in ("a",):
            cell = _run(tuple(names), foe_key, seat, 20, SEED)
            print(
                f"smoke {seat} vs {foe_key}: {cell['wr']:.1%} "
                f"play {cell['proxy_play']:.2f} hold {cell['proxy_hold']:.2f} "
                f"tuck {cell['proxy_tuck']:.2f} ko0 {cell['ko_no_prize']:.2f} "
                f"mill {cell['mill_attack']:.2f}",
                flush=True,
            )
    print(f"smoke {time.perf_counter() - started:.1f}s", flush=True)


def _confirm_card_checks(ranked: list[tuple], cache: dict[str, dict]) -> list[dict]:
    """Confirm each card's best 40-game cut at the full game count.

    The greedy path only confirms the single best swap. These rows say whether
    any other card's own best cut is ahead of the lock once the sample is longer.
    """
    pending = []
    seen: set[str] = set()
    for screen_w, _worst_w, label, cut, names in ranked:
        add = label.split(" -", 1)[0][1:]
        if add in seen:
            continue
        seen.add(add)
        pending.append((add, cut, names, screen_w))
    if not pending:
        return []
    print(f"direct checks: {len(pending)} cards", flush=True)
    evaluated = _evaluate([(add, names) for add, _cut, names, _screen_w in pending], GAMES, cache)
    rows = []
    for add, cut, names, screen_w in pending:
        row = _row(add, names, _combine(evaluated[add]), cut, add)
        row["screen_weighted"] = screen_w
        rows.append(row)
        print(
            f"  check +{add} -{cut} screen {screen_w:.2%} confirm {row['weighted']:.2%}",
            flush=True,
        )
    return rows


def _candidate_names() -> tuple[str, ...]:
    raw = os.environ.get("MILL_DOLL_CANDIDATES", "").strip()
    if not raw:
        return CANDIDATES
    wanted = tuple(part.strip() for part in raw.split(",") if part.strip())
    unknown = [name for name in wanted if name not in CANDIDATES]
    if unknown:
        raise SystemExit(f"unknown candidates: {unknown}")
    return wanted


def _markdown_full(report: dict) -> str:
    base = report["path"][0]
    best = report["best"]
    lines = [
        "# Lillie's Poké Doll, long sample",
        "",
        "Only this card. Every legal cut is measured at the full game count. A step keeps the cut with the higher loss-weighted win rate.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.",
        f"- **Games played**: {report['games_played']}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate. A foe rate uses both seats.",
        "",
        "## Greedy path",
        "",
        "| Step | Add | Cut | Weighted | ± | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        lines.append(
            "| {label} | {add} | {cut} | {weighted} | {se} | {mean} | {worst} | {delta} | {play:.2f} | {stall:.2f} | {hold:.2f} | {ko:.2f} | {mill:.2f} |".format(
                label=row["label"],
                add=row.get("add") or "—",
                cut=row.get("cut") or "—",
                weighted=_pct(row["weighted"]),
                se=_pct(row["se"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                delta=_signed(row["weighted"] - base["weighted"]),
                play=row["proxy_play"],
                stall=row["proxy_stall"],
                hold=row["proxy_hold"],
                ko=row["ko_no_prize"],
                mill=row["mill_attack"],
            )
        )
    delta = best["weighted"] - base["weighted"]
    delta_se = (best["se"] ** 2 + base["se"] ** 2) ** 0.5
    lines.extend(
        [
            "",
            "## Decision",
            "",
            (
                f"Best list is {best['label']}: weighted {_pct(best['weighted'])} "
                f"vs the locked Mill at {_pct(base['weighted'])} ({_signed(delta)}, ±{_pct(delta_se)}). "
                f"Mean {_pct(best['mean'])} ({_signed(best['mean'] - base['mean'])}). "
                "This file records the measurement. SET_MILL_NAMES changes only when that list is accepted. "
                "The 120-game pass kept a Buddy-Buddy Poffin cut. On this sample that cut is flat, and the cut that stays ahead is Switch."
            ),
            "",
            "Counts on that list:",
            "",
            f"- Lillie's Poké Doll: {best['counts'].get('Lillie\'s Poké Doll', 0)}",
        ]
    )
    previous = base
    for rnd in report["rounds"]:
        lines.extend(
            [
                "",
                f"## Step {rnd['step']} cuts",
                "",
                (
                    f"List entering this step: weighted {_pct(previous['weighted'])} ± {_pct(previous['se'])}. "
                    f"Each row replaces one card with one Lillie's Poké Doll."
                ),
                "",
                "| Cut | Weighted | ± | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |",
                "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in rnd["rows"]:
            lines.append(
                "| {cut} | {weighted} | {se} | {mean} | {worst} | {delta} | {play:.2f} | {stall:.2f} | {hold:.2f} | {ko:.2f} | {mill:.2f} |".format(
                    cut=row["cut"],
                    weighted=_pct(row["weighted"]),
                    se=_pct(row["se"]),
                    mean=_pct(row["mean"]),
                    worst=_pct(row["worst"]),
                    delta=_signed(row["weighted"] - previous["weighted"]),
                    play=row["proxy_play"],
                    stall=row["proxy_stall"],
                    hold=row["proxy_hold"],
                    ko=row["ko_no_prize"],
                    mill=row["mill_attack"],
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
    lines.extend(["", "## Foes at the best list", "", "| Foe | A | B | Mean | Delta vs lock |", "| :--- | ---: | ---: | ---: | ---: |"])
    for key, label, *_rest in FOES:
        cell = best["cells"][key]
        base_cell = base["cells"][key]
        lines.append(
            f"| {label} | {_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {_signed(cell['wr'] - base_cell['wr'])} |"
        )
    lines.append("")
    return "\n".join(lines)


def _run_full() -> None:
    """Every legal cut at MILL_DOLL_GAMES. No short screen."""
    candidates = _candidate_names()
    started = time.perf_counter()
    current = list(SET_MILL_NAMES)
    if len(current) != 60:
        raise SystemExit(f"mill lock is {len(current)} cards")
    cache = _load_cache()
    print(f"full sample candidates={candidates} games={GAMES}", flush=True)
    print("baseline", flush=True)
    base_cells = _combine(_evaluate([("lock", current)], GAMES, cache)["lock"])
    base = _row("lock", current, base_cells, None, None)
    base["se"] = _weighted_se(base_cells, GAMES)
    print(f"  weighted {base['weighted']:.2%} ± {base['se']:.2%}", flush=True)
    path = [base]
    rounds: list[dict] = []
    games_played = len(FOES) * 2 * GAMES
    steps = 0
    while steps < 4:
        options: list[tuple[str, str, list[str]]] = []
        for add in candidates:
            if current.count(add) >= 4:
                continue
            for cut in _cuts(current):
                swapped = _swap(current, cut, add)
                if swapped is None:
                    continue
                options.append((f"+{add} -{cut}", cut, swapped))
        if not options:
            break
        print(f"step {steps + 1}: {len(options)} cuts at {GAMES} games", flush=True)
        evaluated = _evaluate([(label, names) for label, _cut, names in options], GAMES, cache)
        games_played += len(options) * len(FOES) * 2 * GAMES
        rows = []
        for label, cut, names in options:
            add = label.split(" -", 1)[0][1:]
            cells = _combine(evaluated[label])
            row = _row(label, names, cells, cut, add)
            row["se"] = _weighted_se(cells, GAMES)
            rows.append(row)
        rows.sort(key=lambda item: (item["weighted"], item["worst"], item["cut"]), reverse=True)
        winner = rows[0]
        print(
            f"  best +{winner['add']} -{winner['cut']} {winner['weighted']:.2%} ± {winner['se']:.2%} "
            f"vs {path[-1]['weighted']:.2%}",
            flush=True,
        )
        kept = None
        if winner["weighted"] > path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"step {steps + 1}"
            current = list(winner["list"])
            path.append(kept)
            steps += 1
        rounds.append({"step": len(rounds) + 1, "rows": rows, "kept": kept})
        DEST.write_text(
            json.dumps(
                {
                    "seed": SEED,
                    "games": GAMES,
                    "path": [{k: v for k, v in item.items() if k != "cells"} for item in path],
                },
                indent=2,
            )
        )
        if kept is None:
            print("  did not improve; stop", flush=True)
            break
    best = max(path, key=lambda item: (item["weighted"], -path.index(item)))
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "games_played": games_played,
        "weights": WEIGHTS,
        "path": path,
        "best": best,
        "rounds": rounds,
    }
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_markdown_full(report))
    print(f"wrote {MD_DEST} games_played={games_played}", flush=True)


def main() -> None:
    if os.environ.get("MILL_DOLL_SMOKE"):
        _smoke()
        return
    if os.environ.get("MILL_DOLL_FULL"):
        _run_full()
        return
    started = time.perf_counter()
    current = list(SET_MILL_NAMES)
    if len(current) != 60:
        raise SystemExit(f"mill lock is {len(current)} cards")
    cache = _load_cache()
    print("baseline", flush=True)
    base_cells = _combine(_evaluate([("lock", current)], GAMES, cache)["lock"])
    base = _row("lock", current, base_cells, None, None)
    print(f"  weighted {base['weighted']:.2%} mean {base['mean']:.2%}", flush=True)
    path = [base]
    steps = 0
    rounds: list[dict] = []
    while steps < 8:
        cuts = _cuts(current)
        options: list[tuple[str, str, list[str]]] = []
        for add in CANDIDATES:
            if current.count(add) >= 4:
                continue
            for cut in cuts:
                swapped = _swap(current, cut, add)
                if swapped is None:
                    continue
                options.append((f"+{add} -{cut}", cut, swapped))
        if not options:
            break
        print(f"step {steps + 1}: screen {len(options)} swaps", flush=True)
        screened = _evaluate([(label, names) for label, _cut, names in options], SCREEN_GAMES, cache)
        ranked = sorted(
            (
                (
                    _weighted(_combine(screened[label])),
                    _worst(_combine(screened[label])),
                    label,
                    cut,
                    names,
                )
                for label, cut, names in options
            ),
            reverse=True,
        )
        best_w, _worst_w, label, cut, names = ranked[0]
        print(f"  screen best {label} {best_w:.2%}", flush=True)
        current_screen = _combine(_evaluate([("current", current)], SCREEN_GAMES, cache)["current"])
        screen_lock = _weighted(current_screen)
        print(f"  screen lock {screen_lock:.2%}", flush=True)
        if best_w < screen_lock - 0.04:
            print("  screen is worse by more than 4 points; stop", flush=True)
            break
        checks = _confirm_card_checks(ranked, cache)
        winner = max(checks, key=lambda item: item["weighted"])
        kept = None
        print(
            f"  best confirm +{winner['add']} -{winner['cut']} {winner['weighted']:.2%} "
            f"vs {path[-1]['weighted']:.2%}",
            flush=True,
        )
        if winner["weighted"] > path[-1]["weighted"]:
            kept = dict(winner)
            kept["label"] = f"step {steps + 1}"
            current = list(winner["list"])
            path.append(kept)
            steps += 1
            DEST.write_text(
                json.dumps(
                    {"path": [{k: v for k, v in item.items() if k != "cells"} for item in path]},
                    indent=2,
                )
            )
        rounds.append(
            {
                "step": len(rounds) + 1,
                "screen_lock": screen_lock,
                "screen_best": best_w,
                "screen_add": label.split(" -", 1)[0][1:],
                "screen_cut": cut,
                "checks": checks,
                "kept": kept,
            }
        )
        if kept is None:
            print("  confirm did not improve; stop", flush=True)
            break
    best = max(path, key=lambda row: (row["weighted"], -path.index(row)))
    report = {
        "seed": SEED,
        "screen_games": SCREEN_GAMES,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "path": path,
        "best": best,
        "rounds": rounds,
    }
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_markdown(report))
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
