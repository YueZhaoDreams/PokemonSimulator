#!/usr/bin/env python3
"""Measure the looser Eeeeeeek on the locked Doll 60.

Same 13 foes, both seats, seed 20261029, 200 games per seat, Sisters weights.
The baseline is the Petrel confirm in set-doll-arven-petrel.json (weighted
0.33789289289289287). This does not cut a card. It only changes when Cleffa
uses the printed shuffle-and-draw.

Writes set-doll-eeeeeeek.md and set-doll-eeeeeeek.json. Partial rows go to a
gitignored jsonl.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.game import play_game
from app.engine.models import standard_60_rules
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

GAMES = int(os.environ.get("DOLL_EEEK_GAMES", "200"))
SEED = int(os.environ.get("DOLL_EEEK_SEED", "20261029"))
WORKERS = int(os.environ.get("DOLL_EEEK_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("DOLL_EEEK_PARTIAL", HERE / "set-doll-eeeeeeek-partial.jsonl"))
DEST = Path(os.environ.get("DOLL_EEEK_DEST", HERE / "set-doll-eeeeeeek.json"))
MD_DEST = Path(os.environ.get("DOLL_EEEK_MD", HERE / "set-doll-eeeeeeek.md"))
BASELINE_JSON = HERE / "set-doll-arven-petrel.json"
BASELINE_LOSSES = HERE / "set-doll-arven-petrel-losses.json"
POLICY = "sacrifice-when-dolls-run-out"


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


def _run(foe_key: str, seat: str, games: int, seed: int) -> dict:
    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(list(SET_DOLL_NAMES))
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "doll", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "doll"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    eeeeek = 0
    empty = 0
    dew = 0
    cleffa_ko = 0
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        events = result.events or {}
        eeeeek += int(events.get("eeeeeeek_shuffle", 0))
        dew += int(events.get("tool:Life Dew", 0))
        cleffa_ko += int(events.get("ko:Cleffa", 0))
        if result.winner == seat:
            wins += 1
        elif result.reason == "opponent has no Pokémon in play":
            empty += 1
    return {
        "games": games,
        "wins": wins,
        "wr": wins / games if games else 0.0,
        "empty": empty,
        "empty_rate": empty / games if games else 0.0,
        "eeeeeeek": eeeeek / games if games else 0.0,
        "life_dew": dew / games if games else 0.0,
        "cleffa_ko": cleffa_ko / games if games else 0.0,
    }


def _cache_key(foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{POLICY}|{seed}|{games}|{seat}|{foe_key}|{'/'.join(SET_DOLL_NAMES)}"


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


def _evaluate(cache: dict[str, dict]) -> dict[str, dict]:
    jobs = []
    out: dict[str, dict] = {}
    for foe_key, *_ in FOES:
        for seat in ("a", "b"):
            key = _cache_key(foe_key, seat, GAMES, SEED)
            cached = cache.get(key)
            if cached is not None:
                out.setdefault(foe_key, {})[seat] = cached
                continue
            jobs.append((foe_key, seat, key))
    print(f"  {len(jobs)} cells, {GAMES} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, foe_key, seat, GAMES, SEED): (foe_key, seat, key)
            for foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out.setdefault(foe_key, {})[seat] = cell
            done += 1
            elapsed = time.perf_counter() - started
            left = elapsed / done * (len(futures) - done)
            print(
                f"    {done}/{len(futures)} {seat} vs {foe_key} {cell['wr']:.1%} "
                f"eeeeek {cell['eeeeeeek']:.2f} ({left:.0f}s left)",
                flush=True,
            )
    return out


def _pair(cells: dict[str, dict], foe_key: str, field: str) -> float:
    return (cells[foe_key]["a"][field] + cells[foe_key]["b"][field]) / 2


def _weighted(cells: dict[str, dict], field: str = "wr") -> float:
    return sum(_pair(cells, key, field) * WEIGHTS[key] for key, *_ in FOES)


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]["wr"]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _baseline() -> dict:
    data = json.loads(BASELINE_JSON.read_text())
    best = data["steps"][-1]["best"]
    if abs(float(best["weighted"]) - 0.33789289289289287) > 1e-12:
        raise SystemExit("Petrel confirm baseline is not the locked Cleffa cut")
    losses = json.loads(BASELINE_LOSSES.read_text())
    empty = {}
    for key, *_ in FOES:
        games = 0
        n = 0
        for seat in ("a", "b"):
            cell = losses["cells"][key][seat]
            games += cell["games"]
            n += cell["kinds"].get("loss:empty", {}).get("n", 0)
        empty[key] = n / games if games else 0.0
    return {
        "weighted": best["weighted"],
        "se": best["se"],
        "cells": {key: best["cells"][key]["wr"] for key, *_ in FOES},
        "empty": empty,
    }


def _pct(rate: float) -> str:
    return f"{rate:.1%}"


def _write(report: dict) -> None:
    cells = report["cells"]
    base = report["baseline"]
    gap = report["weighted"] - base["weighted"]
    gap_se = math.sqrt(report["se"] ** 2 + base["se"] ** 2)
    lines = [
        "# Doll Eeeeeeek when dolls run out",
        "",
        "Same locked 60 as the Petrel confirm. Cleffa still shuffles the hand into the deck and draws 6. "
        "The pilot sends an awake Cleffa Active when the hand has fewer than two replayable dolls, "
        "at most two are already in play, and the deck still has one. Life Dew prefers that Cleffa. "
        "The Bench must not be empty. Junk Hunt stays ahead of the switch.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Weights**: frozen Sisters loss weights, the same weights as the Doll lock.",
        f"- **Baseline**: Petrel confirm weighted {base['weighted']:.6f} (SE {base['se']:.6f}).",
        f"- **This pilot**: weighted {report['weighted']:.6f} (SE {report['se']:.6f}).",
        f"- **Gap**: {gap:+.5f} (gap SE {gap_se:.5f}, {gap / gap_se if gap_se else 0:.2f} SE).",
        f"- **Eeeeeeek per game**: {report['eeeeeeek']:.3f}. Life Dew attached per game: {report['life_dew']:.3f}.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Empty is a loss where Doll's board was gone before the opponent took 6 Prizes. "
        "The Petrel empty rate is the 200-game loss report on the same seed.",
        "",
        "| Foe | Petrel win | This win | Petrel empty | This empty | Eeeeeeek | Life Dew | Cleffa KO |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, label, *_rest in FOES:
        lines.append(
            "| {label} | {base} | {now} | {base_empty} | {empty} | {eeeeek:.2f} | {dew:.2f} | {ko:.2f} |".format(
                label=label,
                base=_pct(base["cells"][key]),
                now=_pct(_pair(cells, key, "wr")),
                base_empty=_pct(base["empty"][key]),
                empty=_pct(_pair(cells, key, "empty_rate")),
                eeeeek=_pair(cells, key, "eeeeeeek"),
                dew=_pair(cells, key, "life_dew"),
                ko=_pair(cells, key, "cleffa_ko"),
            )
        )
    lines.append("")
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text("\n".join(lines) + "\n")
    print(f"wrote {DEST}", flush=True)
    print(f"wrote {MD_DEST}", flush=True)
    print(
        f"weighted {report['weighted']:.6f} gap {gap:+.5f} gap_se {gap_se:.5f}",
        flush=True,
    )


def main() -> None:
    if (
        len(SET_DOLL_NAMES) != 60
        or SET_DOLL_NAMES.count("Cleffa") != 2
        or SET_DOLL_NAMES.count("Arven") != 1
        or SET_DOLL_NAMES.count("Team Rocket's Petrel") != 1
    ):
        raise SystemExit("SET_DOLL_NAMES is not the Arven and Petrel lock")
    started = time.perf_counter()
    cache = _load_cache()
    cells = _evaluate(cache)
    elapsed = time.perf_counter() - started
    report = {
        "seed": SEED,
        "games": GAMES,
        "policy": POLICY,
        "weights": WEIGHTS,
        "elapsed": elapsed,
        "weighted": _weighted(cells),
        "se": _weighted_se(cells, GAMES),
        "eeeeeeek": _weighted(cells, "eeeeeeek"),
        "life_dew": _weighted(cells, "life_dew"),
        "empty": _weighted(cells, "empty_rate"),
        "baseline": _baseline(),
        "cells": cells,
    }
    _write(report)


if __name__ == "__main__":
    main()
