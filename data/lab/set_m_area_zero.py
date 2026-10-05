#!/usr/bin/env python3
"""Area Zero Underdepths + Terapagos ex swaps for the current Set M.

Add one Terapagos ex and one Area Zero Underdepths. Replace exactly two trainer
copies. Pokémon and Spiky Energy stay. Buddy-Buddy Poffin, Nest Ball, Max Potion,
and Arven stay: those are the search, heal, and setup core.

The burst is late. Babies fill the bench first. Terapagos ex comes down when
Area Zero is available and either two Colorless can be paid or the board is
already full. Unified Beatdown is 30 for each benched Pokémon, including Mew ex.
Bouncy Circle still counts only printed maximum HP 30.

Foes: T60, Hedrick, C60, D60, and the Worlds 2024 Crushing Thorn list.
Seed 20260929. Weights are frozen from the current list at the confirm game count.
Screen the pairs, then confirm the leaders.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from itertools import combinations
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
    SET_M60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("thorns", "Iron Thorns ex (Crushing Thorn)", IRON_THORNS_NAMES, "thorns"),
)

# Not the setup core, and not a Pokémon or an Energy.
CUT_POOL = (
    "Bravery Charm",
    "Bursting Balloon",
    "Hero's Cape",
    "Ultra Ball",
    "Night Stretcher",
    "Battle Cage",
    "Iono",
    "Professor's Research",
    "Boss's Orders",
    "Penny",
    "Crushing Hammer",
    "Counter Catcher",
)
ADD = ("Terapagos ex", "Area Zero Underdepths")
HELD = {
    "Mew ex",
    "Mime Jr.",
    "Igglybuff",
    "Budew",
    "Buddy-Buddy Poffin",
    "Nest Ball",
    "Max Potion",
    "Arven",
    "Spiky Energy",
}

SCREEN = int(os.environ.get("M_AREA_SCREEN", "150"))
CONFIRM = int(os.environ.get("M_AREA_CONFIRM", "1000"))
SEED = int(os.environ.get("M_AREA_SEED", "20260929"))
WORKERS = int(os.environ.get("M_AREA_WORKERS", "4"))
TOP_N = int(os.environ.get("M_AREA_TOP", "8"))

QUERIES = [
    {"type": "event_prefix", "prefix": "stadium:Area Zero Underdepths", "key": "area_zero"},
    {"type": "event_prefix", "prefix": "saw_play:Terapagos ex", "key": "terapagos"},
    {"type": "event_prefix", "prefix": "attack:Mew ex:Unified Beatdown", "key": "mew_beatdown"},
    {"type": "event_prefix", "prefix": "attack:Terapagos ex:Unified Beatdown", "key": "tera_beatdown"},
]
DEST = ROOT / "data/lab/set-m-area-zero.json"
MD_DEST = ROOT / "data/lab/set-m-area-zero.md"


def loss_weights(baseline: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - baseline[key]["a"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def _label(cuts: tuple[str, str]) -> str:
    if cuts[0] == cuts[1]:
        return f"2 {cuts[0]}"
    return f"{cuts[0]} + {cuts[1]}"


def pairs(names: list[str]) -> list[tuple[str, tuple[str, str]]]:
    counts = Counter(names)
    usable = [name for name in CUT_POOL if counts[name] >= 1]
    found: list[tuple[str, tuple[str, str]]] = []
    for left, right in combinations(usable, 2):
        found.append((_label((left, right)), (left, right)))
    for name in usable:
        if counts[name] >= 2:
            found.append((_label((name, name)), (name, name)))
    return found


def swap_two(names: list[str], cuts: tuple[str, str]) -> list[str]:
    if any(cut in HELD for cut in cuts):
        raise ValueError(f"refusing to cut {cuts}")
    out = list(names)
    for cut in cuts:
        out.remove(cut)
    out.extend(ADD)
    if len(out) != 60:
        raise ValueError(f"{cuts} swap is {len(out)} cards")
    counts = Counter(out)
    if counts["Hero's Cape"] > 1:
        raise ValueError("a second Hero's Cape is not legal")
    for name, count in counts.items():
        if count > 4:
            raise ValueError(f"{name} would exceed 4")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def _run(label: str, names: list[str], foe_key: str, foe_names, foe_strat: str, games: int) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": label, "name": label},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    queries = rec["results"]["queries"]
    r = rec["results"]
    return label, foe_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "area_zero": queries.get("area_zero", 0.0),
        "terapagos": queries.get("terapagos", 0.0),
        "mew_beatdown": queries.get("mew_beatdown", 0.0),
        "tera_beatdown": queries.get("tera_beatdown", 0.0),
    }


def _eval_lists(lists: list[tuple[str, list[str]]], games: int) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {key: {} for key, _ in lists}
    jobs = [
        (key, names, foe_key, foe_names, foe_strat, games)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
    ]
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        done = 0
        for fut in as_completed(futs):
            key, foe_key, detail = fut.result()
            cells[key][foe_key] = detail
            done += 1
            if done % 5 == 0 or done == len(jobs):
                print(
                    f"  {key} vs {foe_key}: {detail['a']:.1%}  area {detail['area_zero']:.1%}  "
                    f"beat {detail['mew_beatdown']:.1%}  ({done}/{len(jobs)})",
                    flush=True,
                )
    for key, _ in lists:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _row(label: str, cuts: tuple[str, str] | None, cells: dict[str, dict], weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    return {
        "label": label,
        "cuts": list(cuts) if cuts else [],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "area_zero": sum(ordered[key]["area_zero"] for key, *_ in FOES) / len(FOES),
        "terapagos": sum(ordered[key]["terapagos"] for key, *_ in FOES) / len(FOES),
        "mew_beatdown": sum(ordered[key]["mew_beatdown"] for key, *_ in FOES) / len(FOES),
        "tera_beatdown": sum(ordered[key]["tera_beatdown"] for key, *_ in FOES) / len(FOES),
        "cells": ordered,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _render_md(report: dict) -> str:
    weights = report["weights"]
    base = report["baseline"]
    lines = [
        "# Set M — Area Zero Underdepths + Terapagos ex",
        "",
        "One Terapagos ex and one Area Zero Underdepths replace two trainer copies.",
        "Pokémon, Spiky Energy, Buddy-Buddy Poffin, Nest Ball, Max Potion, and Arven stay.",
        "Unified Beatdown is 30 damage for each benched Pokémon. Bouncy Circle still counts only maximum HP 30.",
        "",
        f"Seed {report['seed']}. Screen {report['screen_games']} games, confirm {report['confirm_games']}.",
        "Score is the loss-weighted win rate. Weights are frozen from the current list.",
        "",
        "Weights: "
        + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES)
        + ".",
        "",
        f"Current list weighted {_pct(base['weighted'])} (mean {_pct(base['mean'])}, worst {_pct(base['worst'])}).",
        "",
        "## Confirmed",
        "",
        "| Cut | Weighted | vs current | Mean | Worst | Area Zero | Mew Beatdown | "
        + " | ".join(key for key, *_ in FOES)
        + " |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | " + " | ".join("---:" for _ in FOES) + " |",
    ]
    for row in report["confirmed"]:
        delta = row["weighted"] - base["weighted"]
        foe_cells = " | ".join(_pct(row["cells"][key]["a"]) for key, *_ in FOES)
        lines.append(
            f"| {row['label']} | {_pct(row['weighted'])} | {delta:+.1%} | {_pct(row['mean'])} | "
            f"{_pct(row['worst'])} | {_pct(row['area_zero'])} | {_pct(row['mew_beatdown'])} | {foe_cells} |"
        )
    lines.extend(["", "## Screen leaders", ""])
    lines.append("| Cut | Weighted | vs current | Area Zero | Mew Beatdown |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for row in report["screen"][:15]:
        delta = row["weighted"] - base["weighted"]
        lines.append(
            f"| {row['label']} | {_pct(row['weighted'])} | {delta:+.1%} | "
            f"{_pct(row['area_zero'])} | {_pct(row['mew_beatdown'])} |"
        )
    best = report.get("best")
    lines.extend(["", "## Result", ""])
    if not report.get("confirmed"):
        lines.append("Screen is saved. Confirm has not finished.")
    elif best and best["weighted"] > base["weighted"]:
        lines.append(
            f"Best confirm is {best['label']} at {_pct(best['weighted'])}, "
            f"{best['weighted'] - base['weighted']:+.1%} versus the current list."
        )
    else:
        lines.append("No confirmed swap beat the current list.")
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_render_md(report))


def main() -> None:
    started = time.perf_counter()
    base_names = list(SET_M60_NAMES)
    if len(base_names) != 60:
        raise SystemExit(f"current list is {len(base_names)}")
    options = pairs(base_names)
    print(f"{len(options)} swaps, screen {SCREEN}, confirm {CONFIRM}, workers {WORKERS}", flush=True)

    print("\nbaseline", flush=True)
    base_cells = _eval_lists([("current", base_names)], CONFIRM)["current"]
    weights = loss_weights(base_cells)
    baseline = _row("current", None, base_cells, weights)
    print(
        f"current weighted {baseline['weighted']:.1%} mean {baseline['mean']:.1%} worst {baseline['worst']:.1%}",
        flush=True,
    )
    print("weights " + ", ".join(f"{key}={weights[key]:.1%}" for key, *_ in FOES), flush=True)

    print(f"\nscreen {len(options)}", flush=True)
    screened = _eval_lists([(label, swap_two(base_names, cuts)) for label, cuts in options], SCREEN)
    screen_rows = [
        _row(label, cuts, screened[label], weights) for label, cuts in options
    ]
    screen_rows.sort(key=lambda row: (-row["weighted"], -row["worst"], row["label"]))
    print("screen top:", flush=True)
    for row in screen_rows[:TOP_N]:
        print(f"  {row['label']}: {row['weighted']:.1%} area {row['area_zero']:.1%}", flush=True)
    partial = {
        "seed": SEED,
        "screen_games": SCREEN,
        "confirm_games": CONFIRM,
        "workers": WORKERS,
        "elapsed": time.perf_counter() - started,
        "held": sorted(HELD),
        "added": list(ADD),
        "weights": weights,
        "baseline": baseline,
        "screen": screen_rows,
        "confirmed": [],
        "best": None,
        "beats_current": False,
    }
    _write(partial)

    leaders = screen_rows[:TOP_N]
    leader_cuts = {row["label"]: tuple(row["cuts"]) for row in leaders}
    print(f"\nconfirm {len(leaders)}", flush=True)
    confirmed_cells = _eval_lists(
        [(label, swap_two(base_names, leader_cuts[label])) for label in leader_cuts],
        CONFIRM,
    )
    confirmed = [
        _row(label, leader_cuts[label], confirmed_cells[label], weights) for label in leader_cuts
    ]
    confirmed.sort(key=lambda row: (-row["weighted"], -row["worst"], row["label"]))
    best = confirmed[0]
    print(
        f"best {best['label']} {best['weighted']:.1%} vs current {baseline['weighted']:.1%}",
        flush=True,
    )
    report = {
        "seed": SEED,
        "screen_games": SCREEN,
        "confirm_games": CONFIRM,
        "workers": WORKERS,
        "elapsed": time.perf_counter() - started,
        "held": sorted(HELD),
        "added": list(ADD),
        "weights": weights,
        "baseline": baseline,
        "screen": screen_rows,
        "confirmed": confirmed,
        "best": best,
        "beats_current": best["weighted"] > baseline["weighted"],
    }
    _write(report)
    print(f"elapsed {report['elapsed']:.1f}s -> {DEST}", flush=True)


if __name__ == "__main__":
    main()
