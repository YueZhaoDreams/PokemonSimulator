#!/usr/bin/env python3
"""Greedy Sky Field copies on the locked Set M, one to four.

Same method as set_m_sky_field.py, but every step adds another Sky Field and no
Budew. Step 1 is the same swap that script took first, so its cells come from the
same cache. Each step cuts exactly one copy of one other card for one more Sky
Field. A step tries every card name still in the list as the cut, screens each on
SCREEN_GAMES games per foe, and confirms the best SCREEN_TOP on GAMES games per foe.

One Sky Field is in play in only a fraction of games, so this asks whether more
copies get the 8-slot Bench up often enough to pay for the card each copy replaces.
The score is the loss-weighted win rate with weights frozen from the zero-Sky-Field
baseline. Every step is taken, up to the 4-of-a-name limit, and the report names the
best prefix. Every list on the path is then run again on a fresh seed.
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import set_m_sky_field as base  # noqa: E402
from set_m_sky_field import (  # noqa: E402
    FOES,
    GAMES,
    HOLDOUT_GAMES,
    HOLDOUT_SEED,
    SCREEN_GAMES,
    SCREEN_TOP,
    SEED,
    SKY,
    Cache,
    avg,
    babies,
    cell,
    evaluate,
    greedy_step,
    loss_weights,
    mean,
    pct,
    row_for,
    weighted,
    weighted_se,
    worst,
)
from app.seed_data import SET_M60_NAMES  # noqa: E402

MAX_SKY = 4
DEST = Path(os.environ.get("M_SKY_COPIES_DEST", HERE / "set-m-sky-copies.json"))
MD_DEST = DEST.with_suffix(".md")
base.DEST = DEST
base.MD_DEST = MD_DEST


def main() -> None:
    started = time.perf_counter()
    start = list(SET_M60_NAMES)
    counts = Counter(start)
    if len(start) != 60:
        raise SystemExit(f"SET_M60_NAMES has {len(start)} cards")
    if counts[SKY] != 0 or counts["Budew"] != 0:
        raise SystemExit("SET_M60_NAMES already has Sky Field or Budew")

    saved = json.loads(DEST.read_text()) if DEST.exists() else None
    cache = Cache(saved)
    prior_elapsed = float((saved or {}).get("report", {}).get("elapsed") or 0)
    state: dict = {"report": {}}

    def save() -> None:
        base._save(cache, state["report"])

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

    array = [
        {"label": "Set M", "sky": 0, **{k: base_row[k] for k in base_row if k != "cut"}, "cut": None, "list": start}
    ]
    steps: list[dict] = []
    current = list(start)

    def report(done: bool) -> dict:
        return {
            "games": GAMES,
            "screen_games": SCREEN_GAMES,
            "screen_top": SCREEN_TOP,
            "seed": SEED,
            "holdout_seed": HOLDOUT_SEED,
            "holdout_games": HOLDOUT_GAMES,
            "rule_preset": "s60",
            "elapsed": time.perf_counter() - started + prior_elapsed,
            "method": (
                "greedy one-card swaps from the locked Set M; every step adds one more Sky Field, up to 4; "
                "every distinct card is tried as the cut; the score is the loss-weighted win rate with weights "
                "frozen from the zero-Sky-Field baseline; cuts are screened on a short run and the best few "
                "are confirmed on the full run; every list on the path is rerun on a fresh seed"
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

    for copies in range(1, MAX_SKY + 1):
        label = f"Sky Field {copies}"
        print(f"step: add {label}", flush=True)
        state["report"] = report(False)
        step = greedy_step(current, SKY, weights, cache, save, label, limit=MAX_SKY)
        current = step["list"]
        steps.append(step)
        row = step["row"]
        array.append(
            {
                "label": label,
                "sky": current.count(SKY),
                **{k: row[k] for k in row if k != "cut"},
                "cut": step["chosen"],
                "list": list(current),
            }
        )
        print(
            f"  chose cut {step['chosen']}: weighted {row['weighted']:.2%} (±{row['se']:.2%}) "
            f"mean {row['mean']:.2%} babies {row['babies']:.2f} sky in play {row['sky_games']:.1%}",
            flush=True,
        )
        state["report"] = report(False)
        save()

    print("holdout: every list on a fresh seed", flush=True)
    held = evaluate(
        [(row["label"], row["list"]) for row in array],
        HOLDOUT_GAMES,
        cache,
        save,
        "holdout",
        seed=HOLDOUT_SEED,
    )
    for row in array:
        cells = held[row["label"]]
        row["holdout"] = {
            "weighted": weighted(cells, weights),
            "se": weighted_se(cells, weights),
            "mean": mean(cells),
            "worst": worst(cells),
            "babies": babies(cells),
            "sky_games": avg(cells, "sky_games"),
            "attack6": avg(cells, "attack6"),
            "attack7": avg(cells, "attack7"),
            "attack8": avg(cells, "attack8"),
            "cells": cells,
        }
        print(
            f"  holdout {row['label']}: weighted {row['holdout']['weighted']:.2%} "
            f"(±{row['holdout']['se']:.2%}) mean {row['holdout']['mean']:.2%}",
            flush=True,
        )

    state["report"] = report(True)
    best = max(range(len(array)), key=lambda i: (array[i]["weighted"], -i))
    state["report"]["best_index"] = best
    save()
    MD_DEST.write_text(render_md(state["report"]))
    print(f"wrote {MD_DEST}", flush=True)


def _diff_se(a: dict, b: dict) -> float:
    return (a["se"] ** 2 + b["se"] ** 2) ** 0.5


def result_lines(rep: dict) -> list[str]:
    array = rep["array"]
    base_row = array[0]
    base_hold = base_row["holdout"]
    best_row = array[rep["best_index"]]
    lines = [
        f"- Set M, re-measured on the current engine: {pct(base_row['weighted'])} weighted "
        f"(±{pct(base_row['se'])}); {pct(base_hold['weighted'])} on the fresh seed.",
    ]
    for index, row in enumerate(array[1:], start=1):
        hold = row["holdout"]
        prev = array[index - 1]
        lines.append(
            f"- {row['label']} (cut {row['cut']}): {pct(row['weighted'])}, {row['weighted'] - prev['weighted']:+.1%} "
            f"against {prev['label']} and {row['weighted'] - base_row['weighted']:+.1%} against Set M; "
            f"fresh seed {pct(hold['weighted'])}, {hold['weighted'] - prev['holdout']['weighted']:+.1%} against "
            f"{prev['label']} and {hold['weighted'] - base_hold['weighted']:+.1%} against Set M "
            f"(±{pct(_diff_se(hold, base_hold))} of the Set M difference)."
        )
    sky_rows = array[1:]
    higher_sel = all(
        array[i + 1]["weighted"] > array[i]["weighted"] for i in range(1, len(array) - 1)
    )
    higher_hold = all(
        array[i + 1]["holdout"]["weighted"] > array[i]["holdout"]["weighted"] for i in range(1, len(array) - 1)
    )
    if rep["best_index"] == 0:
        verdict = "No Sky Field count beats Set M."
    elif len(sky_rows) > 1 and higher_sel and higher_hold:
        verdict = "Each extra Sky Field raised the weighted win rate on both seeds."
    elif rep["best_index"] == 1:
        verdict = "One Sky Field is the best count. Extra copies did not raise the weighted win rate."
    else:
        verdict = (
            f"The best count on the selection seed is {best_row['label']}. "
            "The steps are not monotone, so read the fresh-seed column before trusting the order."
        )
    lines.extend(["", verdict, "", f"Best list on the selection seed ({best_row['label']}):", "", "```"])
    lines.extend(f"{count} {name}" for name, count in sorted(Counter(best_row["list"]).items()))
    lines.extend(["```", ""])
    return lines


def render_md(rep: dict) -> str:
    weights = rep["weights"]
    array = rep["array"]
    best = rep["best_index"]
    base_row = array[0]
    lines = [
        "# Set M with more Sky Field, greedy",
        "",
        "Starting 60 is the locked Set M list (`SET_M60_NAMES`). Every step adds one more Sky Field, up to 4, and no Budew.",
        "Each step cuts exactly one copy of one other card, and every distinct card is tried as the cut.",
        "Sky Field: each player can have 8 Pokémon on the Bench. Set M has 6 Pokémon with a maximum HP of 30,",
        "so Bouncy Circle tops out at 180 here. The question is whether a second, third, or fourth copy",
        "puts the 8-slot Bench up often enough to pay for the card it replaces.",
        "Mew ex plays a Bench-raising Stadium before Buddy-Buddy Poffin when more 30 HP Basics are waiting than there are",
        "open slots, and Battle Cage does not replace it while the Bench is past 5 (see `tests/test_mew_sky_field.py`).",
        "A second Sky Field is held while one is in play, so extra copies are replacements after the opponent's Stadium removes it.",
        "Step 1 is the same swap as in `set-m-sky-field.md`, and its cells are the same.",
        "",
        f"- **Seed**: `{rep['seed']}`",
        f"- **Games**: cuts screened on {rep['screen_games']} per foe, best {rep['screen_top']} confirmed on {rep['games']} per foe",
        "- **Score**: loss-weighted win rate. Weights are frozen from the zero-Sky-Field baseline.",
        "- **Weights**: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "## Path",
        "",
        "| Step | Sky Field | Cut | Weighted | ±1 SE | vs Set M | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for i, row in enumerate(array):
        cells = row["cells"]
        mark = " (best)" if i == best else ""
        lines.append(
            f"| {row['label']}{mark} | {row['sky']} | {row['cut'] or '—'} | {pct(row['weighted'])} | "
            f"{pct(row['se'])} | {row['weighted'] - base_row['weighted']:+.1%} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(
        [
            "",
            "## Holdout",
            "",
            f"The same lists on a fresh seed, `{rep['holdout_seed']}`, {rep['holdout_games']} games per foe. "
            "No list was chosen on this seed. Weights are the same. "
            "The difference column uses the unpaired standard error of the two lists.",
            "",
            "| Step | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    base_hold = base_row["holdout"]
    for row in array:
        hold = row["holdout"]
        cells = hold["cells"]
        lines.append(
            f"| {row['label']} | {pct(hold['weighted'])} | {pct(hold['se'])} | "
            f"{hold['weighted'] - base_hold['weighted']:+.1%} | {pct(_diff_se(hold, base_hold))} | "
            f"{pct(hold['mean'])} | {pct(hold['worst'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(
        [
            "",
            "## Bench of 30 HP Pokémon",
            "",
            "Babies is the mean number of Benched 30 HP Pokémon at the moment side A attacks.",
            "The attack columns are the share of games with at least one attack at that many (5 is the old limit, 6 is 180, 7 is 210, 8 is 240).",
            "Sky Field is the share of games where one was played. The table is the selection seed.",
            "",
            "| Step | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies |",
            "| :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in array:
        lines.append(
            f"| {row['label']} | {row['babies']:.2f} | {pct(row['sky_games'])} | {pct(row['attack6'])} | "
            f"{pct(row['attack7'])} | {pct(row['attack8'])} |"
        )
    for index, step in enumerate(rep["steps"], start=1):
        lines.extend(
            [
                "",
                f"## Step {index}: add {array[index]['label']}, every cut",
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
    lines.extend(["", "## Result", ""] + result_lines(rep))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
