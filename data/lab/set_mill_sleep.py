#!/usr/bin/env python3
"""Compare the Sisters 60 with the thin sleep-wall Mill 60.

The live list is the Sisters shell plus one Playground Pichu, one Call of
Legends Mime Jr., one Slumbering Forest, and one Switch. Fighting Energy is
the cut. The Sisters list is frozen here. SET_MILL_NAMES is the live list.
C60 is one of the measured foes.

Each list plays both seats against the household foes, including C60. The cell is the
mean of those two win rates. A head-to-head row plays the two Mill lists
against each other. Loss weights are frozen from the Sisters 60.

Seed 20261022. Games per seat from MILL_SLEEP_GAMES (default 250).
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
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_C60_NAMES,
    SET_MILL_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    build_mill_deck,
)

# Loss-weighted greedy seed 20261009. Frozen so the comparison does not
# follow SET_MILL_NAMES after the sleep wall replaced it.
SISTERS_60 = (
    ["Wiglett"] * 4
    + ["Wugtrio"] * 4
    + ["Victini"]
    + ["Level Ball"] * 3
    + ["Nest Ball"] * 3
    + ["Buddy-Buddy Poffin"] * 4
    + ["Rescue Carrier"] * 4
    + ["Crushing Hammer"] * 4
    + ["Counter Catcher"] * 2
    + ["Miss Fortune Sisters"] * 2
    + ["Crispin"] * 3
    + ["Boss's Orders"]
    + ["Team Rocket's Handiwork"] * 2
    + ["Colress's Tenacity"] * 4
    + ["Neutralization Zone"]
    + ["Double Turbo Energy"] * 4
    + ["Water Energy"] * 4
    + ["Fighting Energy"] * 2
    + ["Ignition Energy"] * 4
    + ["Reversal Energy"] * 4
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

DECKS = ("sisters", "sleep")
LIST_ID = "spark"
GAMES = int(os.environ.get("MILL_SLEEP_GAMES", "250"))
SEED = int(os.environ.get("MILL_SLEEP_SEED", "20261022"))
WORKERS = int(os.environ.get("MILL_SLEEP_WORKERS", str(min(4, os.cpu_count() or 2))))
QUERIES = [
    {"type": "event_sum", "prefix": "playground", "key": "playground"},
    {"type": "event_sum", "prefix": "sweet_sleeping_face", "key": "face"},
    {"type": "event_sum", "prefix": "mill_attack", "key": "mill_attack"},
    {"type": "event_sum", "prefix": "attack:Wugtrio:Undersea Tunnel", "key": "undersea"},
    {"type": "event_sum", "prefix": "sleepy_lost_miss", "key": "sleepy_miss"},
    {"type": "event_sum", "prefix": "sleepy_lost", "key": "sleepy_lost_all"},
    {"type": "event_sum", "prefix": "energy_antics_fail", "key": "antics_fail"},
    {"type": "event_sum", "prefix": "energy_antics", "key": "energy_antics_all"},
    {"type": "event_sum", "prefix": "slumbering_forest", "key": "forest"},
    {"type": "event_prefix", "prefix": "saw_play:Pichu", "key": "pichu"},
    {"type": "event_prefix", "prefix": "saw_play:Mime Jr.", "key": "mime"},
    {"type": "event_prefix", "prefix": "saw_play:Smoochum", "key": "smoochum"},
    {"type": "event_prefix", "prefix": "saw_play:Manaphy", "key": "manaphy"},
    {"type": "event_prefix", "prefix": "stadium:Slumbering Forest", "key": "forest_play"},
]
PARTIAL = Path(os.environ.get("MILL_SLEEP_PARTIAL", ROOT / "data/lab/set-mill-sleep-partial.jsonl"))
DEST = Path(os.environ.get("MILL_SLEEP_DEST", ROOT / "data/lab/set-mill-sleep.json"))
MD_DEST = Path(os.environ.get("MILL_SLEEP_MD", ROOT / "data/lab/set-mill-sleep.md"))
USAGE_KEYS = (
    "playground",
    "face",
    "mill_attack",
    "undersea",
    "sleepy_lost",
    "energy_antics",
    "forest",
    "pichu",
    "mime",
    "smoochum",
    "manaphy",
    "forest_play",
)


def _subject_deck(key: str):
    if key == "sleep":
        return build_mill_deck()
    if key == "sisters":
        return build_fallback_deck(list(SISTERS_60))
    raise KeyError(key)


def _foe_deck(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _blank_usage() -> dict[str, float]:
    return {key: 0.0 for key in USAGE_KEYS}


def _usage_from(queries: dict) -> dict[str, float]:
    out = _blank_usage()
    for key in USAGE_KEYS:
        out[key] = float(queries.get(key, 0.0))
    # event_sum matches by prefix, so the success key also counts the miss/fail bump.
    out["sleepy_lost"] = float(queries.get("sleepy_lost_all", 0.0)) - float(queries.get("sleepy_miss", 0.0))
    out["energy_antics"] = float(queries.get("energy_antics_all", 0.0)) - float(queries.get("antics_fail", 0.0))
    return out


def _run(subject: str, foe_key: str, seat: str) -> tuple[str, str, str, dict]:
    if foe_key == "h2h":
        foe_cards = _subject_deck("sisters" if subject == "sleep" else "sleep")
        foe_strat = "mill"
    else:
        _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
        foe_cards = _foe_deck(foe_names, g30)
    subject_cards = _subject_deck(subject)
    if seat == "a":
        cards_a, cards_b = subject_cards, foe_cards
        strat_a, strat_b = "mill", foe_strat
    else:
        cards_a, cards_b = foe_cards, subject_cards
        strat_a, strat_b = foe_strat, "mill"
    rec = run_simulation(
        cards_a,
        cards_b,
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": subject, "name": subject},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    r = rec["results"]
    wr = r["win_rate_a"] if seat == "a" else r["win_rate_b"]
    cell = {"wr": wr, "tie": r["tie_rate"]}
    cell.update(_usage_from(r["queries"]))
    return subject, foe_key, seat, cell


def _load_partial() -> dict[tuple[str, str, str], dict]:
    found: dict[tuple[str, str, str], dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("games") != GAMES or row.get("seed") != SEED or row.get("list_id") != LIST_ID:
            continue
        found[(row["subject"], row["foe"], row["seat"])] = row["cell"]
    return found


def _append(subject: str, foe: str, seat: str, cell: dict) -> None:
    PARTIAL.parent.mkdir(parents=True, exist_ok=True)
    with PARTIAL.open("a") as fh:
        fh.write(
            json.dumps(
                {
                    "games": GAMES,
                    "seed": SEED,
                    "list_id": LIST_ID,
                    "subject": subject,
                    "foe": foe,
                    "seat": seat,
                    "cell": cell,
                }
            )
            + "\n"
        )


def _mean_usage(cells: list[dict]) -> dict[str, float]:
    if not cells:
        return _blank_usage()
    return {key: sum(cell[key] for cell in cells) / len(cells) for key in USAGE_KEYS}


def _combine(seat_cells: dict[str, dict[str, dict]]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for foe, *_ in FOES:
        a = seat_cells["a"][foe]
        b = seat_cells["b"][foe]
        merged = {
            "wr": (a["wr"] + b["wr"]) / 2,
            "a": a["wr"],
            "b": b["wr"],
            "tie": (a["tie"] + b["tie"]) / 2,
        }
        usage = _mean_usage([a, b])
        merged.update(usage)
        out[foe] = merged
    return out


def _eval(done: dict[tuple[str, str, str], dict]) -> dict[str, dict[str, dict]]:
    seats = {key: {"a": {}, "b": {}} for key in DECKS}
    jobs: list[tuple[str, str, str]] = []
    for subject in DECKS:
        for foe, *_ in FOES:
            for seat in ("a", "b"):
                cached = done.get((subject, foe, seat))
                if cached is not None:
                    seats[subject][seat][foe] = cached
                    continue
                jobs.append((subject, foe, seat))
    for seat in ("a", "b"):
        cached = done.get(("sleep", "h2h", seat))
        if cached is None:
            jobs.append(("sleep", "h2h", seat))
    print(f"{len(jobs)} cells to run", flush=True)
    h2h: dict[str, dict] = {}
    if jobs:
        with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
            futs = [pool.submit(_run, *job) for job in jobs]
            finished = 0
            started = time.perf_counter()
            for fut in as_completed(futs):
                subject, foe, seat, cell = fut.result()
                done[(subject, foe, seat)] = cell
                _append(subject, foe, seat, cell)
                if foe == "h2h":
                    h2h[seat] = cell
                else:
                    seats[subject][seat][foe] = cell
                finished += 1
                if finished == 1 or finished % 8 == 0 or finished == len(jobs):
                    elapsed = time.perf_counter() - started
                    rate = finished / elapsed if elapsed else 0
                    left = (len(jobs) - finished) / rate if rate else 0
                    print(
                        f"  {subject} seat {seat} vs {foe}: {cell['wr']:.1%}  "
                        f"({finished}/{len(jobs)}, {left:.0f}s left)",
                        flush=True,
                    )
    for seat in ("a", "b"):
        if seat not in h2h:
            cached = done.get(("sleep", "h2h", seat))
            if cached is None:
                raise RuntimeError(f"missing head-to-head seat {seat}")
            h2h[seat] = cached
    combined = {}
    for subject in DECKS:
        for seat in ("a", "b"):
            for foe, *_ in FOES:
                if foe not in seats[subject][seat]:
                    raise RuntimeError(f"missing cell {subject} seat {seat} vs {foe}")
        combined[subject] = _combine(seats[subject])
    combined["h2h"] = h2h
    return combined


def _score(cells: dict[str, dict]) -> dict[str, float]:
    rates = [cells[key]["wr"] for key, *_ in FOES]
    return {
        "mean": sum(rates) / len(rates),
        "worst": min(rates),
        "best": max(rates),
    }


def _weights(cells: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - cells[key]["wr"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key, *_ in FOES}


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["wr"] * weights[key] for key, *_ in FOES)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _counts(names: list[str]) -> dict[str, int]:
    return dict(Counter(names))


def _markdown(report: dict) -> str:
    weights = report["weights"]
    sisters = report["decks"]["sisters"]
    sleep = report["decks"]["sleep"]
    h2h = report["head_to_head"]
    lines = [
        "# Mill sleep wall vs Sisters 60",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each Mill list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: loss-weighted from the Sisters 60, frozen. Harder Sisters matchups count more.",
        f"- **Weights**: {', '.join(f'{key} {weights[key]:.1%}' for key, *_ in FOES)}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Printed Playground lets each player bench as many Basic Pokémon as they like, user first, then Pichu is Asleep. "
        "Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. "
        "Sleepy Lost puts the top card of the opponent's deck into the Lost Zone, then Mime Jr. is Asleep. "
        "Energy Antics moves an Energy from one of the opponent's Pokémon to another of theirs, then Smoochum is Asleep. "
        "Slumbering Forest makes an Asleep Pokémon flip 2 coins between turns and stay Asleep unless both are heads. "
        "Manaphy Wave Veil prevents damage done to the bench by attacks.",
        "",
        "## Win-rate array",
        "",
        "| Foe | Sisters A | Sisters B | Sisters | Sleep A | Sleep B | Sleep | Delta |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, label, *_ in FOES:
        old = sisters["cells"][key]
        new = sleep["cells"][key]
        lines.append(
            f"| {label} | {_pct(old['a'])} | {_pct(old['b'])} | {_pct(old['wr'])} | "
            f"{_pct(new['a'])} | {_pct(new['b'])} | {_pct(new['wr'])} | {_signed(new['wr'] - old['wr'])} |"
        )
    lines.append(
        f"| Mean |  |  | {_pct(sisters['mean'])} |  |  | {_pct(sleep['mean'])} | {_signed(sleep['mean'] - sisters['mean'])} |"
    )
    lines.append(
        f"| Weighted |  |  | {_pct(sisters['weighted'])} |  |  | {_pct(sleep['weighted'])} | "
        f"{_signed(sleep['weighted'] - sisters['weighted'])} |"
    )
    lines.append(
        f"| Worst |  |  | {_pct(sisters['worst'])} |  |  | {_pct(sleep['worst'])} | {_signed(sleep['worst'] - sisters['worst'])} |"
    )
    lines.extend(
        [
            "",
            "## Head to head",
            "",
            f"Sleep wall win rate vs Sisters 60: {_pct(h2h['wr'])} "
            f"(as A {_pct(h2h['a'])}, as B {_pct(h2h['b'])}).",
            "",
            "## Package use on the sleep wall",
            "",
            "Means are per game across the measured foes and both seats. "
            "Pichu, Mime Jr., Smoochum, Manaphy, and Slumbering Forest rows are the share of games in which that card entered play. "
            "Manaphy is not in this Mill list; a hit there is the opponent's Manaphy.",
            "",
            "| Event | Per game |",
            "| :--- | ---: |",
        ]
    )
    labels = {
        "playground": "Playground",
        "face": "Sweet Sleeping Face blocks",
        "mill_attack": "Cards milled by an attack or Handiwork",
        "undersea": "Undersea Tunnel attacks",
        "sleepy_lost": "Sleepy Lost",
        "energy_antics": "Energy Antics",
        "forest": "Slumbering Forest sleep checks",
        "pichu": "Pichu saw play",
        "mime": "Mime Jr. saw play",
        "smoochum": "Smoochum saw play",
        "manaphy": "Manaphy saw play",
        "forest_play": "Slumbering Forest entered play",
    }
    usage = sleep["usage"]
    for key, label in labels.items():
        value = usage[key]
        shown = _pct(value) if key in {"pichu", "mime", "smoochum", "manaphy", "forest_play"} else f"{value:.2f}"
        lines.append(f"| {label} | {shown} |")
    lines.extend(
        [
            "",
            "## Lists",
            "",
            "Sisters 60 is frozen in `SISTERS_60`. Sleep wall is `build_mill_deck()`.",
            "",
            "| Card | Sisters | Sleep |",
            "| :--- | ---: | ---: |",
        ]
    )
    names = sorted(set(report["sisters_counts"]) | set(report["sleep_counts"]))
    for name in names:
        lines.append(f"| {name} | {report['sisters_counts'].get(name, 0)} | {report['sleep_counts'].get(name, 0)} |")
    lines.extend(["", "## Decision", "", report["decision"], ""])
    return "\n".join(lines)


def _check_lists() -> None:
    sisters = list(SISTERS_60)
    sleep = list(SET_MILL_NAMES)
    if len(sisters) != 60 or len(sleep) != 60:
        raise SystemExit(f"list length sisters {len(sisters)} sleep {len(sleep)}")
    if sisters == sleep:
        raise SystemExit("the two lists are identical")
    for label, cards in (
        ("sisters", build_fallback_deck(sisters)),
        ("sleep", build_mill_deck()),
    ):
        bad = copy_violations(cards, standard_60_rules())
        if bad:
            raise SystemExit(f"{label} is illegal: {bad}")
    mime = [card for card in build_mill_deck() if card.name == "Mime Jr."]
    if len(mime) != list(SET_MILL_NAMES).count("Mime Jr.") or any(card.catalog_id != "col1-47" for card in mime):
        raise SystemExit("sleep wall Mime Jr. is not Call of Legends 47")


def main() -> None:
    started = time.perf_counter()
    _check_lists()
    done = _load_partial()
    scored = _eval(done)
    sisters_cells = scored["sisters"]
    sleep_cells = scored["sleep"]
    weights = _weights(sisters_cells)
    sisters_score = _score(sisters_cells)
    sleep_score = _score(sleep_cells)
    sisters_w = _weighted(sisters_cells, weights)
    sleep_w = _weighted(sleep_cells, weights)
    h2h_seats = scored["h2h"]
    h2h = {
        "a": h2h_seats["a"]["wr"],
        "b": h2h_seats["b"]["wr"],
        "wr": (h2h_seats["a"]["wr"] + h2h_seats["b"]["wr"]) / 2,
        "tie": (h2h_seats["a"]["tie"] + h2h_seats["b"]["tie"]) / 2,
    }
    usage_cells = [sleep_cells[key] for key, *_ in FOES]
    decision = (
        f"Sleep wall mean {_pct(sleep_score['mean'])} vs Sisters {_pct(sisters_score['mean'])} "
        f"({_signed(sleep_score['mean'] - sisters_score['mean'])}). "
        f"Weighted {_pct(sisters_w)} → {_pct(sleep_w)} "
        f"({_signed(sleep_w - sisters_w)}). "
        f"Head to head sleep wall {_pct(h2h['wr'])}."
    )
    report = {
        "seed": SEED,
        "games": GAMES,
        "list_id": LIST_ID,
        "weights": weights,
        "elapsed": time.perf_counter() - started,
        "sisters_counts": _counts(list(SISTERS_60)),
        "sleep_counts": _counts(list(SET_MILL_NAMES)),
        "decks": {
            "sisters": {**sisters_score, "weighted": sisters_w, "cells": sisters_cells},
            "sleep": {
                **sleep_score,
                "weighted": sleep_w,
                "cells": sleep_cells,
                "usage": _mean_usage(usage_cells),
            },
        },
        "head_to_head": h2h,
        "decision": decision,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_markdown(report))
    print(decision, flush=True)
    print(f"wrote {DEST}", flush=True)


if __name__ == "__main__":
    main()
