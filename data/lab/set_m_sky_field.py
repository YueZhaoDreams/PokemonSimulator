#!/usr/bin/env python3
"""Greedy Sky Field, then greedy Budew, on the locked Set M.

Start from SET_M60_NAMES. Step 1 puts one Sky Field in by cutting exactly one
copy of one other card. Each later step puts one Budew in the same way. A step
tries every card name still in the list as the cut, so one card leaves and one
card arrives and the list stays at 60.

Sky Field (Roaring Skies): each player can have 8 Pokémon on the Bench. Igglybuff's
Bouncy Circle is 30 damage for each Benched Pokémon with a maximum HP of 30, so
8 such Pokémon on the Bench is 240. Set M plays 6 of them (4 Igglybuff, 2 Mime Jr.),
so the stadium alone cannot fill 8 slots. Budew is the other 30 HP Basic.

The decision score is the loss-weighted win rate, with weights frozen from the
fresh zero-Sky-Field baseline. The Sky Field step is taken even when it lowers the
score. The Budew steps run to 4 copies, the 4-of-a-name limit, and the report
names the best prefix of that path.

Every cut is screened on SCREEN_GAMES games per foe. The best SCREEN_TOP cuts
are then confirmed on GAMES games per foe. Games with the same seed share their
shuffles up to the first card that differs between the two lists.
"""

from __future__ import annotations

import json
import math
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
    SET_M60_NAMES,
    SET_STARMIE60_NAMES,
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
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie"),
)

GAMES = int(os.environ.get("M_SKY_GAMES", "1000"))
SCREEN_GAMES = int(os.environ.get("M_SKY_SCREEN_GAMES", "300"))
SCREEN_TOP = int(os.environ.get("M_SKY_SCREEN_TOP", "6"))
SEED = int(os.environ.get("M_SKY_SEED", "20261007"))
WORKERS = int(os.environ.get("M_SKY_WORKERS", "4"))
MAX_BUDEW = int(os.environ.get("M_SKY_MAX_BUDEW", "4"))
SKY = "Sky Field"
BUDEW = "Budew"
DEST = Path(os.environ.get("M_SKY_DEST", ROOT / "data/lab/set-m-sky-field.json"))
MD_DEST = DEST.with_suffix(".md")

QUERIES = [
    {"type": "event_prefix", "prefix": "stadium:Sky Field", "key": "sky_games"},
    {"type": "event_sum", "prefix": "sky_field_turns", "key": "sky_turns"},
    {"type": "event_sum", "prefix": "sky_field_with_cage", "key": "sky_cage_turns"},
    {"type": "event_sum", "prefix": "bench30_sum_a", "key": "bench_sum"},
    {"type": "event_sum", "prefix": "bench30_n_a", "key": "bench_n"},
    {"type": "event_prefix", "prefix": "bench30_attack_a:6", "key": "attack6"},
    {"type": "event_prefix", "prefix": "bench30_attack_a:7", "key": "attack7"},
    {"type": "event_prefix", "prefix": "bench30_attack_a:8", "key": "attack8"},
    {"type": "event_prefix", "prefix": "itchy_pollen_lock_a", "key": "itchy"},
]
QUERY_KEYS = ("sky_games", "attack6", "attack7", "attack8", "itchy")


def loss_weights(rates: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - rates[key]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def list_key(names: list[str]) -> str:
    return ",".join(f"{name}x{count}" for name, count in sorted(Counter(names).items()))


def cell_key(names: list[str], games: int, foe_key: str) -> str:
    return f"{games}|{foe_key}|{list_key(names)}"


def swap_one(names: list[str], cut: str, add: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(add)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(add) > (1 if add == SKY else 4):
        raise ValueError(f"{add} would exceed its copy limit")
    return out


def _run(names: list[str], games: int, foe_key: str, foe_names, foe_strat: str) -> tuple[str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "m", "name": "m"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    counts = result["query_counts"]
    detail = {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "games": games,
        "bench_sum": counts.get("bench_sum", 0),
        "bench_n": counts.get("bench_n", 0),
        "sky_turns": counts.get("sky_turns", 0),
        "sky_cage_turns": counts.get("sky_cage_turns", 0),
    }
    for key in QUERY_KEYS:
        detail[key] = result["queries"].get(key, 0.0)
    return foe_key, detail


class Cache:
    def __init__(self, saved: dict | None):
        self.cells: dict[str, dict] = dict((saved or {}).get("cells", {}))

    def get(self, names: list[str], games: int, foe_key: str) -> dict | None:
        return self.cells.get(cell_key(names, games, foe_key))

    def put(self, names: list[str], games: int, foe_key: str, detail: dict) -> None:
        self.cells[cell_key(names, games, foe_key)] = detail


def _save(cache: Cache, report: dict) -> None:
    DEST.write_text(json.dumps({"cells": cache.cells, "report": report}, indent=1) + "\n")


def evaluate(
    lists: list[tuple[str, list[str]]],
    games: int,
    cache: Cache,
    save,
    label: str,
) -> dict[str, dict[str, dict]]:
    """Cells for every (label, list, foe). Missing cells run in a process pool."""
    jobs = [
        (key, names, foe_key, foe_names, foe_strat)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
        if cache.get(names, games, foe_key) is None
    ]
    total = len(lists) * len(FOES)
    if jobs:
        with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
            futs = {
                pool.submit(_run, names, games, foe_key, foe_names, foe_strat): (key, names)
                for key, names, foe_key, foe_names, foe_strat in jobs
            }
            done = total - len(jobs)
            for fut in as_completed(futs):
                key, names = futs[fut]
                foe_key, detail = fut.result()
                cache.put(names, games, foe_key, detail)
                done += 1
                if done % 6 == 0 or done == total:
                    print(f"  [{label}] {done}/{total} cells", flush=True)
                    save()
    out: dict[str, dict[str, dict]] = {}
    for key, names in lists:
        out[key] = {}
        for foe_key, *_ in FOES:
            cell = cache.get(names, games, foe_key)
            if cell is None:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
            out[key][foe_key] = cell
    return out


def weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def weighted_se(cells: dict[str, dict], weights: dict[str, float]) -> float:
    var = 0.0
    for key, *_ in FOES:
        p = cells[key]["a"]
        n = cells[key]["games"]
        var += (weights[key] ** 2) * p * (1.0 - p) / n
    return math.sqrt(var)


def babies(cells: dict[str, dict]) -> float:
    total_sum = sum(cells[key]["bench_sum"] for key, *_ in FOES)
    total_n = sum(cells[key]["bench_n"] for key, *_ in FOES)
    return total_sum / total_n if total_n else 0.0


def avg(cells: dict[str, dict], field: str) -> float:
    return sum(cells[key][field] for key, *_ in FOES) / len(FOES)


def row_for(label: str, names: list[str], cells: dict[str, dict], weights: dict[str, float], copies: Counter) -> dict:
    return {
        "cut": label,
        "copies_before": copies[label] if label in copies else 0,
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "babies": babies(cells),
        "sky_games": avg(cells, "sky_games"),
        "attack6": avg(cells, "attack6"),
        "attack7": avg(cells, "attack7"),
        "attack8": avg(cells, "attack8"),
        "itchy": avg(cells, "itchy"),
        "cells": cells,
    }


def rank_key(row: dict):
    return (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"])


def greedy_step(
    current: list[str],
    add: str,
    weights: dict[str, float],
    cache: Cache,
    save,
    step_label: str,
) -> dict:
    copies = Counter(current)
    cuts = sorted(name for name in copies if name not in {SKY, BUDEW})
    screen_lists = [(cut, swap_one(current, cut, add)) for cut in cuts]
    screened = evaluate(screen_lists, SCREEN_GAMES, cache, save, f"{step_label} screen")
    screen_rows = sorted(
        (row_for(cut, dict(screen_lists)[cut], screened[cut], weights, copies) for cut in cuts),
        key=rank_key,
    )
    finalists = [row["cut"] for row in screen_rows[:SCREEN_TOP]]
    confirm_lists = [(cut, dict(screen_lists)[cut]) for cut in finalists]
    confirmed = evaluate(confirm_lists, GAMES, cache, save, f"{step_label} confirm")
    confirm_rows = sorted(
        (row_for(cut, dict(screen_lists)[cut], confirmed[cut], weights, copies) for cut in finalists),
        key=rank_key,
    )
    chosen = confirm_rows[0]
    return {
        "add": add,
        "screen": screen_rows,
        "confirm": confirm_rows,
        "chosen": chosen["cut"],
        "list": dict(screen_lists)[chosen["cut"]],
        "row": chosen,
    }


def main() -> None:
    started = time.perf_counter()
    start = list(SET_M60_NAMES)
    counts = Counter(start)
    if len(start) != 60:
        raise SystemExit(f"SET_M60_NAMES has {len(start)} cards")
    if counts[SKY] != 0 or counts[BUDEW] != 0:
        raise SystemExit("SET_M60_NAMES already has Sky Field or Budew")

    saved = json.loads(DEST.read_text()) if DEST.exists() else None
    if saved and saved.get("report", {}).get("seed") not in (None, SEED):
        saved = None
    cache = Cache(saved)
    state: dict = {"report": {}}

    def save() -> None:
        _save(cache, state["report"])

    print("baseline: locked Set M", flush=True)
    base_cells = evaluate([("base", start)], GAMES, cache, save, "baseline")["base"]
    rates = {key: base_cells[key]["a"] for key, *_ in FOES}
    weights = loss_weights(rates)
    base_row = row_for("—", start, base_cells, weights, Counter())
    print(
        f"baseline weighted {base_row['weighted']:.2%} mean {base_row['mean']:.2%}  "
        + ", ".join(f"{k} {rates[k]:.1%}" for k, *_ in FOES),
        flush=True,
    )
    print("weights " + ", ".join(f"{k} {weights[k]:.1%}" for k, *_ in FOES), flush=True)

    array = [{"label": "Set M", "sky": 0, "budew": 0, **{k: base_row[k] for k in base_row if k != "cut"}, "cut": None, "list": start}]
    steps: list[dict] = []
    current = list(start)

    def report(done: bool) -> dict:
        return {
            "games": GAMES,
            "screen_games": SCREEN_GAMES,
            "screen_top": SCREEN_TOP,
            "seed": SEED,
            "rule_preset": "s60",
            "elapsed": time.perf_counter() - started,
            "method": (
                "greedy one-card swaps from the locked Set M; step 1 adds one Sky Field (forced), "
                "later steps add Budew up to 4 copies; every distinct card is tried as the cut; "
                "the score is the loss-weighted win rate with weights frozen from the zero-Sky-Field baseline; "
                "cuts are screened on a short run and the best few are confirmed on the full run"
            ),
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "baseline_rates": rates,
            "list_start": start,
            "list": current,
            "array": array,
            "steps": steps,
            "done": done,
        }

    plan = [(SKY, "Sky Field")] + [(BUDEW, f"Budew {i}") for i in range(1, MAX_BUDEW + 1)]
    for add, label in plan:
        print(f"step: add {label}", flush=True)
        state["report"] = report(False)
        step = greedy_step(current, add, weights, cache, save, label)
        current = step["list"]
        steps.append(step)
        sky = current.count(SKY)
        budew = current.count(BUDEW)
        row = step["row"]
        array.append(
            {
                "label": label,
                "sky": sky,
                "budew": budew,
                **{k: row[k] for k in row if k != "cut"},
                "cut": step["chosen"],
                "list": list(current),
            }
        )
        print(
            f"  chose cut {step['chosen']}: weighted {row['weighted']:.2%} (±{row['se']:.2%}) "
            f"mean {row['mean']:.2%} babies {row['babies']:.2f} attack8 {row['attack8']:.1%}",
            flush=True,
        )
        state["report"] = report(False)
        save()

    state["report"] = report(True)
    best = max(range(len(array)), key=lambda i: (array[i]["weighted"], -i))
    state["report"]["best_index"] = best
    save()
    MD_DEST.write_text(render_md(state["report"]))
    print(f"wrote {MD_DEST}", flush=True)


def pct(value: float) -> str:
    return f"{value:.1%}"


def cell(cells: dict, key: str) -> str:
    return pct(cells[key]["a"])


def render_md(rep: dict) -> str:
    weights = rep["weights"]
    array = rep["array"]
    best = rep.get("best_index", 0)
    base = array[0]
    lines = [
        "# Set M with Sky Field and Budew, greedy",
        "",
        "Starting 60 is the locked Set M list (`SET_M60_NAMES`). Step 1 adds one Sky Field and the Budew steps follow.",
        "Each step cuts exactly one copy of one other card for the new card, and every distinct card is tried as the cut.",
        "Sky Field: each player can have 8 Pokémon on the Bench. Bouncy Circle is 30 damage for each Benched Pokémon",
        "with a maximum HP of 30, so 8 of them is 240. Set M has 6 such Pokémon (4 Igglybuff, 2 Mime Jr.).",
        "Budew is a third 30 HP Basic, and each copy is one more body for the wider Bench.",
        "The Sky Field step is taken even when it lowers the score. Budew runs to 4 copies, the 4-of-a-name limit.",
        "",
        f"- **Seed**: `{rep['seed']}`",
        f"- **Games**: cuts screened on {rep['screen_games']} per foe, best {rep['screen_top']} confirmed on {rep['games']} per foe",
        "- **Score**: loss-weighted win rate. Weights are frozen from the zero-Sky-Field baseline.",
        "- **Weights**: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "## Path",
        "",
        "| Step | Sky Field | Budew | Cut | Weighted | ±1 SE | vs Set M | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for i, row in enumerate(array):
        cells = row["cells"]
        mark = " (best)" if i == best else ""
        delta = row["weighted"] - base["weighted"]
        lines.append(
            f"| {row['label']}{mark} | {row['sky']} | {row['budew']} | {row['cut'] or '—'} | {pct(row['weighted'])} | "
            f"{pct(row['se'])} | {delta:+.1%} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(
        [
            "",
            "## Bench of 30 HP Pokémon",
            "",
            "Babies is the mean number of Benched 30 HP Pokémon at the moment side A attacks.",
            "The last three columns are the share of games with at least one attack at that many (6 Babies is 180, 7 is 210, 8 is 240).",
            "",
            "| Step | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies | Itchy Pollen |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in array:
        lines.append(
            f"| {row['label']} | {row['babies']:.2f} | {pct(row['sky_games'])} | {pct(row['attack6'])} | "
            f"{pct(row['attack7'])} | {pct(row['attack8'])} | {pct(row['itchy'])} |"
        )
    for step in rep["steps"]:
        lines.extend(
            [
                "",
                f"## Step: add {step['add']}, every cut",
                "",
                f"Chosen cut is {step['chosen']}. Screen is {rep['screen_games']} games per foe; "
                f"the confirmed table is {rep['games']} games per foe.",
                "",
                "### Confirmed",
                "",
                "| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step["confirm"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | {row['babies']:.2f} | "
                f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
                f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
            )
        lines.extend(
            [
                "",
                "### Screen",
                "",
                "| Rank | Cut | Weighted | Mean |",
                "| ---: | :--- | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step["screen"], start=1):
            lines.append(f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} |")
    best_row = array[best]
    lines.extend(
        [
            "",
            "## Result",
            "",
            f"Best on the path: {best_row['label']} at {pct(best_row['weighted'])} weighted "
            f"(±{pct(best_row['se'])}), Set M is {pct(base['weighted'])} (±{pct(base['se'])}).",
            "",
            "Best list:",
            "",
            "```",
            *[f"{count} {name}" for name, count in sorted(Counter(best_row["list"]).items())],
            "```",
            "",
        ]
    )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
