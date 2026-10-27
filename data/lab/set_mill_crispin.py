#!/usr/bin/env python3
"""Mill Crispin-era swaps. The 60 in this file still has three Crispin.

The live Mill lock is SET_MILL_NAMES: three Wally replaced these three Crispin.
See data/lab/set-mill-wally.md. Lists below stay on the Crispin-era 60 so this
file can be re-run. The registered Great Ball sentence is "Search your deck for
a Pokémon," which is not the printed coin-flip Basic search, so ball3 is not a
lock candidate.

Printed Crispin searches up to two Basic Energy cards of different types, puts one
into the hand, and attaches the other. With one type the engine puts that single
Water Energy into the hand and does not attach it, and the Supporter is still used.

Each list is the locked Mill with one named swap. Both seats play the household
foes. The score is the loss-weighted win rate. Weights are frozen from the Sisters
60. A higher weighted rate is the list to keep.

Seed 20261026. Games per seat from MILL_CRISPIN_GAMES (default 120).
MILL_CRISPIN_LISTS limits the names (comma-separated).
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

GAMES = int(os.environ.get("MILL_CRISPIN_GAMES", "120"))
SEED = int(os.environ.get("MILL_CRISPIN_SEED", "20261026"))
WORKERS = int(os.environ.get("MILL_CRISPIN_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("MILL_CRISPIN_PARTIAL", HERE / "set-mill-crispin-partial.jsonl"))
DEST = Path(os.environ.get("MILL_CRISPIN_DEST", HERE / "set-mill-crispin.json"))
MD_DEST = Path(os.environ.get("MILL_CRISPIN_MD", HERE / "set-mill-crispin.md"))


# This file measures the Crispin-era 60. The live lock is SET_MILL_NAMES,
# which replaced these three Crispin with Wally. See data/lab/set-mill-wally.md.
CRISPIN_ERA = (
    ["Pichu"]
    + ["Mime Jr."]
    + ["Wiglett"] * 4
    + ["Wugtrio"] * 4
    + ["Victini"]
    + ["Slumbering Forest"]
    + ["Neutralization Zone"]
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 3
    + ["Level Ball"] * 3
    + ["Rescue Carrier"] * 3
    + ["Lillie's Poké Doll"]
    + ["Crushing Hammer"] * 4
    + ["Counter Catcher"] * 2
    + ["Miss Fortune Sisters"] * 2
    + ["Crispin"] * 3
    + ["Boss's Orders"]
    + ["Team Rocket's Handiwork"] * 2
    + ["Colress's Tenacity"] * 4
    + ["Double Turbo Energy"] * 4
    + ["Water Energy"] * 3
    + ["Ignition Energy"] * 4
    + ["Reversal Energy"] * 4
)


def _swap(cuts: list[str], adds: list[str]) -> tuple[str, ...]:
    names = list(CRISPIN_ERA)
    for card in cuts:
        names.remove(card)
    names.extend(adds)
    if len(names) != 60:
        raise SystemExit(f"swap {cuts} -> {adds} has {len(names)} cards")
    return tuple(names)


# The lock is measured in the same run. Every other row is one swap off that 60.
LISTS: dict[str, tuple[str, ...]] = {
    "lock": tuple(CRISPIN_ERA),
    "water3": _swap(["Crispin"] * 3, ["Water Energy"] * 3),
    "water2": _swap(["Crispin"] * 2, ["Water Energy"] * 2),
    "dce3": _swap(["Crispin"] * 3, ["Double Colorless Energy"] * 3),
    "split1": _swap(["Crispin"] * 2, ["Fighting Energy"] * 2),
    "split3": _swap(["Counter Catcher"] * 2, ["Fighting Energy"] * 2),
    "handi": _swap(["Crispin"] * 3, ["Team Rocket's Handiwork"] * 2 + ["Water Energy"]),
    "handi2": _swap(["Crispin"] * 2, ["Team Rocket's Handiwork"] * 2),
    "sisters": _swap(["Crispin"] * 2, ["Miss Fortune Sisters"] * 2),
    "manaphy": _swap(["Crispin"], ["Manaphy"]),
    "types": _swap(["Water Energy"], ["Fighting Energy"]),
    "types2": _swap(["Water Energy"] * 2, ["Fighting Energy"] * 2),
    "carrier": _swap(["Crispin"], ["Rescue Carrier"]),
    "wally3": _swap(["Crispin"] * 3, ["Wally"] * 3),
    "wally2": _swap(["Crispin"] * 2, ["Wally"] * 2),
    "seek": _swap(["Crispin"] * 3, ["Wally"] * 2 + ["VS Seeker"]),
    "ball3": _swap(["Crispin"] * 3, ["Great Ball"] * 3),
    "mix": _swap(["Crispin"] * 3, ["Great Ball"] * 2 + ["Wally"]),
    "bts3": _swap(["Crispin"] * 3, ["Broken Time-Space"] * 3),
    "bts2": _swap(["Crispin"] * 2, ["Broken Time-Space"] * 2),
    "bts1": _swap(["Crispin"], ["Broken Time-Space"]),
}

NOTES = {
    "lock": "Three Crispin, three Water Energy, no second Basic type.",
    "water3": "Cut all three Crispin for Water Energy.",
    "water2": "Cut two Crispin for Water Energy. One Crispin stays.",
    "dce3": "Cut all three Crispin for Double Colorless Energy. Each pays two Colorless.",
    "split1": "Cut two Crispin for Fighting Energy. The remaining Crispin has two Basic types.",
    "split3": "Keep three Crispin. Cut both Counter Catcher for Fighting Energy so Crispin can attach.",
    "handi": "Cut all three Crispin for two Team Rocket's Handiwork and one Water Energy.",
    "handi2": "Cut two Crispin for two Team Rocket's Handiwork. One Crispin stays.",
    "sisters": "Cut two Crispin for two Miss Fortune Sisters. One Crispin stays.",
    "manaphy": "Cut one Crispin for Manaphy. Wave Veil prevents bench damage from attacks.",
    "types": "Turn one Water Energy into Fighting Energy. Three Crispin, and now two Basic types.",
    "types2": "Turn two Water Energy into Fighting Energy. One Water stays for Twisting Strike.",
    "carrier": "Cut one Crispin for a fourth Rescue Carrier.",
    "wally3": "Cut all three Crispin for Wally. Wally fetches Wugtrio from the deck onto Wiglett.",
    "wally2": "Cut two Crispin for Wally. One Crispin stays.",
    "seek": "Cut all three Crispin for two Wally and one VS Seeker.",
    "ball3": "Cut all three Crispin for Great Ball. Great Ball finds Wugtrio once Wiglett is in play.",
    "mix": "Cut all three Crispin for two Great Ball and one Wally.",
    "bts3": "Cut all three Crispin for Broken Time-Space. A Wiglett played this turn can evolve.",
    "bts2": "Cut two Crispin for Broken Time-Space. One Crispin stays.",
    "bts1": "Cut one Crispin for one Broken Time-Space.",
}


def _selected() -> list[str]:
    raw = os.environ.get("MILL_CRISPIN_LISTS", "").strip()
    if not raw:
        return list(LISTS)
    names = [part.strip() for part in raw.split(",") if part.strip()]
    missing = [name for name in names if name not in LISTS]
    if missing:
        raise SystemExit(f"unknown lists: {missing}")
    return names


def _cards(names: tuple[str, ...]):
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


def _check_lists(names: list[str]) -> None:
    rules = standard_60_rules()
    for label in names:
        pile = _cards(LISTS[label])
        if len(pile) != 60:
            raise SystemExit(f"{label} has {len(pile)} cards")
        bad = copy_violations(pile, rules)
        if bad:
            raise SystemExit(f"{label} is illegal: {bad}")
    manaphy = fallback_named("Manaphy")
    text = " ".join(ability.text for ability in manaphy.abilities)
    if "benched" not in text.lower() or "attacks" not in text.lower():
        raise SystemExit(f"Manaphy is not Wave Veil: {text}")


def _bucket(seat: str, winner: str, reason: str) -> str:
    if winner == "tie":
        return f"tie|{reason}"
    mill_won = (seat == "a" and winner == "a") or (seat == "b" and winner == "b")
    side = "mill" if mill_won else "foe"
    return f"{side}|{reason}"


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(names)
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "mill", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "mill"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    ties = 0
    mill_attack = 0
    turns = 0
    opp_prizes = 0
    reasons: Counter[str] = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        mill_is_a = seat == "a"
        if (mill_is_a and result.winner == "a") or (not mill_is_a and result.winner == "b"):
            wins += 1
        elif result.winner == "tie":
            ties += 1
        mill_attack += result.events.get("mill_attack", 0)
        turns += result.turns
        opp_prizes += result.prizes_taken_b if mill_is_a else result.prizes_taken_a
        reasons[_bucket(seat, result.winner, result.reason)] += 1
    return {
        "wr": wins / games,
        "tie": ties / games,
        "mill_attack": mill_attack / games,
        "turns": turns / games,
        "opp_prizes": opp_prizes / games,
        "reasons": dict(reasons),
    }


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
    PARTIAL.parent.mkdir(parents=True, exist_ok=True)
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")


def _evaluate(labels: list[str], games: int, cache: dict[str, dict]) -> dict[str, dict[str, dict]]:
    jobs = []
    out: dict[str, dict[str, dict]] = {label: {} for label in labels}
    for label in labels:
        frozen = LISTS[label]
        for foe_key, *_ in FOES:
            for seat in ("a", "b"):
                key = _cache_key(frozen, foe_key, seat, games, SEED)
                cached = cache.get(key)
                if cached is not None:
                    out[label].setdefault(foe_key, {})[seat] = cached
                    continue
                jobs.append((label, frozen, foe_key, seat, key))
    print(f"{len(jobs)} cells, {games} games, seed {SEED}", flush=True)
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
                    f"  {done}/{len(futures)} {label} seat {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)",
                    flush=True,
                )
    return out


def _combine(cells: dict[str, dict]) -> dict[str, dict]:
    combined = {}
    for foe_key, *_ in FOES:
        a = cells[foe_key]["a"]
        b = cells[foe_key]["b"]
        row = {
            "wr": (a["wr"] + b["wr"]) / 2,
            "a": a["wr"],
            "b": b["wr"],
            "tie": (a["tie"] + b["tie"]) / 2,
            "mill_attack": (a["mill_attack"] + b["mill_attack"]) / 2,
            "turns": (a["turns"] + b["turns"]) / 2,
            "opp_prizes": (a["opp_prizes"] + b["opp_prizes"]) / 2,
        }
        reasons: Counter[str] = Counter()
        for seat in (a, b):
            reasons.update(seat.get("reasons") or {})
        row["reasons"] = dict(reasons)
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


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
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> tuple[str, float]:
    key = min(FOES, key=lambda row: cells[row[0]]["wr"])[0]
    return key, cells[key]["wr"]


def _score(label: str, cells: dict[str, dict], games: int) -> dict:
    worst_key, worst = _worst(cells)
    return {
        "label": label,
        "note": NOTES[label],
        "counts": dict(Counter(LISTS[label])),
        "weighted": _weighted(cells),
        "se": _weighted_se(cells, games),
        "mean": _mean(cells),
        "worst": worst,
        "worst_foe": worst_key,
        "cells": cells,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _markdown_final(report: dict) -> str:
    base = next((row for row in report["lists"] if row["label"] == "lock"), None)
    lines = [
        "# Mill Crispin swaps",
        "",
        "Printed Crispin searches for up to two Basic Energy cards of different types, puts one into the hand, and attaches the other. "
        "The locked Mill has three Crispin and only Water Energy as a Basic Energy. With one type, Crispin puts that Water Energy into the hand and does not attach it. The Supporter is still used.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.",
        f"- **Weights**: {', '.join(f'{key} {WEIGHTS[key]:.1%}' for key, *_ in FOES)}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in this same run.",
        "",
        "## Lists",
        "",
        "| List | Swap | Weighted | ± | Mean | Worst | Delta | D60 | M | G | C60 | Starmie |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    ordered = report["lists"]
    for row in ordered:
        delta = "—" if base is None or row["label"] == "lock" else _signed(row["weighted"] - base["weighted"])
        cells = row["cells"]
        lines.append(
            f"| {row['label']} | {row['note']} | {_pct(row['weighted'])} | {_pct(row['se'])} | "
            f"{_pct(row['mean'])} | {_pct(row['worst'])} | {delta} | "
            f"{_pct(cells['d60']['wr'])} | {_pct(cells['m']['wr'])} | {_pct(cells['g']['wr'])} | "
            f"{_pct(cells['c60']['wr'])} | {_pct(cells['starmie']['wr'])} |"
        )
    best = ordered[0]
    lines.extend(["", f"Highest weighted list in this run: `{best['label']}` at {_pct(best['weighted'])}.", ""])
    if base is None or best["label"] == "lock":
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "## Foes at the highest list",
            "",
            "| Foe | Lock | Best A | Best B | Best | Delta |",
            "| :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_ in FOES:
        old = base["cells"][key]["wr"]
        new = best["cells"][key]
        lines.append(
            f"| {label} | {_pct(old)} | {_pct(new['a'])} | {_pct(new['b'])} | {_pct(new['wr'])} | {_signed(new['wr'] - old)} |"
        )

    def share_reason(row: dict, foe: str, pred) -> float:
        reasons = row["cells"][foe]["reasons"]
        total = sum(reasons.values()) or 1
        return sum(count for key, count in reasons.items() if pred(key)) / total

    lines.extend(
        [
            "",
            "## How the hard games end",
            "",
            "Shares use both seats. Prize losses are the opponent taking all six Prize cards. "
            "Deckout wins are games Mill won because the opponent decked out. "
            "Board losses are games Mill lost with no Pokémon in play.",
            "",
            "| Foe | List | Foe prizes | Mill deckout | Mill board loss | Mill attacks | Turns | Opp prizes |",
            "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for foe in ("d60", "m", "g", "c60", "starmie", "h"):
        for row in (base, best):
            cell = row["cells"][foe]
            prizes = share_reason(row, foe, lambda key: key.startswith("foe|took all prize"))
            deckout = share_reason(row, foe, lambda key: key.startswith("mill|") and "decked out" in key)
            board = share_reason(row, foe, lambda key: key.startswith("foe|opponent has no"))
            lines.append(
                f"| {foe} | {row['label']} | {_pct(prizes)} | {_pct(deckout)} | {_pct(board)} | "
                f"{cell['mill_attack']:.2f} | {cell['turns']:.1f} | {cell['opp_prizes']:.2f} |"
            )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    labels = _selected()
    _check_lists(labels)
    cache = _load_cache()
    scored = _evaluate(labels, GAMES, cache)
    rows = [_score(label, _combine(scored[label]), GAMES) for label in labels]
    rows.sort(key=lambda row: row["weighted"], reverse=True)
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "lists": rows,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_markdown_final(report))
    best = rows[0]
    lock = next((row for row in rows if row["label"] == "lock"), None)
    if lock is None:
        print(f"best {best['label']} {_pct(best['weighted'])} ± {_pct(best['se'])}", flush=True)
    else:
        gap = best["weighted"] - lock["weighted"]
        se = (best["se"] ** 2 + lock["se"] ** 2) ** 0.5
        z = gap / se if se else 0.0
        print(
            f"best {best['label']} {_pct(best['weighted'])} vs lock {_pct(lock['weighted'])} "
            f"({_signed(gap)}, {z:.2f} SE)",
            flush=True,
        )
    print(f"wrote {DEST}", flush=True)
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
