#!/usr/bin/env python3
"""One Black Market on the locked Doll 60.

Dark Market is Black Market ◇ (Team Up 134). The step adds that one Stadium and
cuts one other card. Every cut is screened, then the cuts that can still beat
the locked list are confirmed. The score is the frozen Sisters loss-weighted
win rate. Both seats. Doll goes first in either seat.

Seed from DOLL_MARKET_SEED (default 20261028). Screen games per seat from
DOLL_MARKET_SCREEN (default 40). Confirm games per seat from DOLL_MARKET_GAMES
(default 120). SET_DOLL_NAMES is not changed here.
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

ADD = "Black Market"

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

# Loss weights frozen from the Sisters 60, the same weights as the Doll lock.
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

SCREEN_GAMES = int(os.environ.get("DOLL_MARKET_SCREEN", "40"))
GAMES = int(os.environ.get("DOLL_MARKET_GAMES", "120"))
SEED = int(os.environ.get("DOLL_MARKET_SEED", "20261028"))
WORKERS = int(os.environ.get("DOLL_MARKET_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("DOLL_MARKET_PARTIAL", HERE / "set-doll-black-market-partial.jsonl"))
DEST = Path(os.environ.get("DOLL_MARKET_DEST", HERE / "set-doll-black-market.json"))
MD_DEST = Path(os.environ.get("DOLL_MARKET_MD", HERE / "set-doll-black-market.md"))

QUERIES = [
    {"type": "event_sum", "prefix": "stadium:Black Market", "key": "market"},
    {"type": "event_sum", "prefix": "market_prize_cut", "key": "market_cut"},
    {"type": "event_sum", "prefix": "junk_hunt", "key": "junk_hunt"},
    {"type": "event_sum", "prefix": "ko_no_prize", "key": "ko_no_prize"},
]


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        elif name == "Mime Jr.":
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
        deck_a_meta={"id": "doll-market", "name": "doll-market"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
    cell = {"wr": wr, "tie": result["tie_rate"]}
    for key in ("market", "market_cut", "junk_hunt", "ko_no_prize"):
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
            if done == 1 or done % 20 == 0 or done == len(futures):
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
        for key in ("market", "market_cut", "junk_hunt", "ko_no_prize"):
            row[key] = (a.get(key, 0.0) + b.get(key, 0.0)) / 2
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


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


def _swap(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(ADD)
    if len(out) != 60 or out.count(ADD) != 1:
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
        "market": _avg(cells, "market"),
        "market_cut": _avg(cells, "market_cut"),
        "junk_hunt": _avg(cells, "junk_hunt"),
        "ko_no_prize": _avg(cells, "ko_no_prize"),
        "cells": cells,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _markdown(report: dict) -> str:
    base = report["baseline"]
    best = report["best"]
    lines = [
        "# Doll, one Black Market",
        "",
        "Dark Market is Black Market ◇, Team Up 134. One copy. The Prism Star rule puts it in the Lost Zone instead of the discard pile. When a Darkness Pokémon with any Darkness Energy attached to it is Knocked Out by damage from an opponent's attack, that player takes 1 fewer Prize card. An Item or a Supporter cannot affect this Stadium. Another Stadium still replaces it.",
        "",
        "The pilot plays it for Sableye once that Sableye has Darkness Energy, or can attach one this turn. Junk Hunt still costs Darkness, and the prize line does too, so the Energy stays. Life Dew stays off that Sableye. Battle Cage stays up against spread. Slumbering Forest stays up while a face is Asleep.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Screen games per seat**: {report['screen_games']}",
        f"- **Confirm games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.",
        "- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "## Screen",
        "",
        "| Cut | Copies | Weighted | Mean | Worst | Stadium plays | Prize cuts |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["screen"]:
        lines.append(
            "| {cut} | {copies} | {weighted} | {mean} | {worst} | {market:.2f} | {cut_n:.2f} |".format(
                cut=row["cut"] or "— locked —",
                copies=row["copies_before"],
                weighted=_pct(row["weighted"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                market=row["market"],
                cut_n=row["market_cut"],
            )
        )
    lines.extend(
        [
            "",
            "## Confirm",
            "",
            "| Cut | Weighted | SE | vs locked | Mean | Worst | Stadium plays | Prize cuts | Junk Hunt |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["confirm"]:
        lines.append(
            "| {cut} | {weighted} | {se:.2%} | {delta} | {mean} | {worst} | {market:.2f} | {cut_n:.2f} | {hunt:.2f} |".format(
                cut=row["cut"] or "— locked —",
                weighted=_pct(row["weighted"]),
                se=row["se"],
                delta=_signed(row["weighted"] - base["weighted"]),
                mean=_pct(row["mean"]),
                worst=_pct(row["worst"]),
                market=row["market"],
                cut_n=row["market_cut"],
                hunt=row["junk_hunt"],
            )
        )
    delta = best["weighted"] - base["weighted"]
    gap_se = (best["se"] ** 2 + base["se"] ** 2) ** 0.5
    if report["kept"]:
        decision = (
            f"The highest confirm cuts one {best['cut']} for one Black Market. "
            f"Weighted {_pct(best['weighted'])} vs the locked Doll at {_pct(base['weighted'])} "
            f"({_signed(delta)}; SE {best['se']:.2%} on the swap and {base['se']:.2%} on the lock, "
            f"so the gap's SE is about {gap_se:.2%}). "
            "The Stadium comes down about once every ten games, and the prize line fires less often than that, "
            "because Battle Cage stays up against spread. "
            "SET_DOLL_NAMES stays the locked 60. This sample is not the 1000-game holdout."
        )
    else:
        decision = (
            f"No confirm beat the locked Doll. Best confirm is {best['cut'] or 'the lock'}: "
            f"weighted {_pct(best['weighted'])} vs {_pct(base['weighted'])} ({_signed(delta)}; "
            f"the gap's SE is about {gap_se:.2%}). "
            "SET_DOLL_NAMES stays the locked 60."
        )
    lines.extend(["", "## Decision", "", decision, ""])
    lines.append("## Foes on the confirm")
    lines.append("")
    header = "| Foe | Locked | " + " | ".join(row["cut"] or "locked" for row in report["confirm"] if row["cut"]) + " |"
    align = "| :--- | ---: | " + " | ".join("---:" for row in report["confirm"] if row["cut"]) + " |"
    lines.extend([header, align])
    for key, label, *_rest in FOES:
        bits = [f"| {label} | {_pct(base['cells'][key]['wr'])}"]
        for row in report["confirm"]:
            if not row["cut"]:
                continue
            bits.append(_pct(row["cells"][key]["wr"]))
        lines.append(" | ".join(bits) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    cache = _load_cache()
    base_names = list(SET_DOLL_NAMES)
    if len(base_names) != 60 or base_names.count(ADD):
        raise SystemExit("locked Doll is not a 60 without Black Market")
    cuts = sorted(Counter(base_names))
    screen_lists = [("locked", base_names)] + [(cut, _swap(base_names, cut)) for cut in cuts]
    print(f"screen {len(screen_lists)} lists", flush=True)
    screened = _evaluate(screen_lists, SCREEN_GAMES, cache)
    screen_rows = [
        _row(label, names, screened[label], SCREEN_GAMES, None if label == "locked" else label)
        for label, names in screen_lists
    ]
    screen_rows.sort(key=lambda row: (-row["weighted"], row["cut"] or ""))
    base_screen = next(row for row in screen_rows if row["cut"] is None)
    # Confirm the lock and every cut within two screen standard errors of the best.
    band = max(base_screen["se"], screen_rows[0]["se"]) * 2
    floor = screen_rows[0]["weighted"] - band
    confirm_labels = ["locked"]
    for row in screen_rows:
        if row["cut"] is None:
            continue
        if row["weighted"] + 1e-12 >= floor or len(confirm_labels) == 1:
            confirm_labels.append(row["cut"])
        if len(confirm_labels) >= 8:
            break
    # The best screen cut is always confirmed, even when the band is empty.
    if screen_rows[0]["cut"] and screen_rows[0]["cut"] not in confirm_labels:
        confirm_labels.append(screen_rows[0]["cut"])
    confirm_lists = [("locked", base_names)] + [
        (cut, _swap(base_names, cut)) for cut in confirm_labels if cut != "locked"
    ]
    print("confirm " + ", ".join(label for label, _names in confirm_lists), flush=True)
    confirmed = _evaluate(confirm_lists, GAMES, cache)
    confirm_rows = [
        _row(label, names, confirmed[label], GAMES, None if label == "locked" else label)
        for label, names in confirm_lists
    ]
    base = next(row for row in confirm_rows if row["cut"] is None)
    swaps = [row for row in confirm_rows if row["cut"]]
    best_swap = max(swaps, key=lambda row: (row["weighted"], row["worst"], -ord(row["cut"][0])))
    kept = best_swap["weighted"] > base["weighted"]
    best = best_swap if kept else base
    report = {
        "seed": SEED,
        "screen_games": SCREEN_GAMES,
        "games": GAMES,
        "weights": WEIGHTS,
        "elapsed": time.perf_counter() - started,
        "screen": [
            {key: value for key, value in row.items() if key != "list"}
            for row in screen_rows
        ],
        "confirm": [
            {key: value for key, value in row.items() if key != "list"}
            for row in sorted(confirm_rows, key=lambda row: (row["cut"] is not None, -row["weighted"]))
        ],
        "baseline": {key: value for key, value in base.items() if key != "list"},
        "best": {key: value for key, value in best.items() if key != "list"},
        "kept": kept,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(MD_DEST)
    print(
        f"kept={kept} best={best['cut']} {_pct(best['weighted'])} locked {_pct(base['weighted'])}",
        flush=True,
    )


if __name__ == "__main__":
    main()
