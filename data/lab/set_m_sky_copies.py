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
HOLDOUT2_SEED = int(os.environ.get("M_SKY_HOLDOUT2_SEED", "20261022"))
HOLDOUT2_GAMES = int(os.environ.get("M_SKY_HOLDOUT2_GAMES", "3000"))
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
            "holdout2_seed": HOLDOUT2_SEED,
            "holdout2_games": HOLDOUT2_GAMES,
            "rule_preset": "s60",
            "elapsed": time.perf_counter() - started + prior_elapsed,
            "method": (
                "greedy one-card swaps from the locked Set M; every step adds one more Sky Field, up to 4; "
                "every distinct card is tried as the cut; the score is the loss-weighted win rate with weights "
                "frozen from the zero-Sky-Field baseline; cuts are screened on a short run and the best few "
                "are confirmed on the full run; every list on the path is rerun on two fresh seeds and pooled"
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
    held2 = evaluate(
        [(row["label"], row["list"]) for row in array],
        HOLDOUT2_GAMES,
        cache,
        save,
        "holdout 2",
        seed=HOLDOUT2_SEED,
    )
    for row in array:
        row["holdout"] = summarize(held[row["label"]], weights)
        row["holdout2"] = summarize(held2[row["label"]], weights)
        row["pooled"] = pool(held[row["label"]], held2[row["label"]], weights)
        print(
            f"  fresh {row['label']}: {row['holdout']['weighted']:.2%} / {row['holdout2']['weighted']:.2%}  "
            f"pooled {row['pooled']['weighted']:.2%} (±{row['pooled']['se']:.2%})",
            flush=True,
        )

    state["report"] = report(True)
    best = max(range(len(array)), key=lambda i: (array[i]["weighted"], -i))
    state["report"]["best_index"] = best
    state["report"]["best_pooled_index"] = max(
        range(len(array)), key=lambda i: (array[i]["pooled"]["weighted"], -i)
    )
    save()
    MD_DEST.write_text(render_md(state["report"]))
    print(f"wrote {MD_DEST}", flush=True)


def summarize(cells: dict[str, dict], weights: dict[str, float]) -> dict:
    return {
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


def pool(first: dict[str, dict], second: dict[str, dict], weights: dict[str, float]) -> dict:
    cells = {}
    for key, *_ in FOES:
        n1, n2 = first[key]["games"], second[key]["games"]
        cells[key] = {
            "a": (first[key]["a"] * n1 + second[key]["a"] * n2) / (n1 + n2),
            "games": n1 + n2,
        }
    return {
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "games": first[FOES[0][0]]["games"] + second[FOES[0][0]]["games"],
        "cells": cells,
    }


def _diff_se(a: dict, b: dict) -> float:
    return (a["se"] ** 2 + b["se"] ** 2) ** 0.5


def result_lines(rep: dict) -> list[str]:
    array = rep["array"]
    base_row = array[0]
    sel = array[rep["best_index"]]
    pooled_best = array[rep["best_pooled_index"]]
    one = array[1]
    lines = [
        f"- Set M, re-measured on the current engine: {pct(base_row['weighted'])} weighted "
        f"(±{pct(base_row['se'])}) on the selection seed; {pct(base_row['pooled']['weighted'])} "
        f"(±{pct(base_row['pooled']['se'])}) on the two fresh seeds pooled.",
    ]
    for index, row in enumerate(array[1:], start=1):
        pooled = row["pooled"]
        z_base = (pooled["weighted"] - base_row["pooled"]["weighted"]) / _diff_se(pooled, base_row["pooled"])
        text = (
            f"- {row['label']} (cut {row['cut']}): selection seed {pct(row['weighted'])} "
            f"({row['weighted'] - base_row['weighted']:+.1%} against Set M); "
            f"fresh seeds pooled {pct(pooled['weighted'])} "
            f"({pooled['weighted'] - base_row['pooled']['weighted']:+.1%} against Set M, {z_base:+.1f} standard errors)"
        )
        if index > 1:
            z_one = (pooled["weighted"] - one["pooled"]["weighted"]) / _diff_se(pooled, one["pooled"])
            text += f"; {pooled['weighted'] - one['pooled']['weighted']:+.1%} against one Sky Field ({z_one:+.1f})"
        lines.append(text + ".")
    extra = array[2:]
    beats_one = [
        row
        for row in extra
        if (row["pooled"]["weighted"] - one["pooled"]["weighted"]) / _diff_se(row["pooled"], one["pooled"]) >= 2.0
    ]
    if rep["best_index"] == rep["best_pooled_index"]:
        verdict = f"The selection seed and the pooled fresh seeds both pick {sel['label']}."
    else:
        verdict = (
            f"The selection seed picks {sel['label']} and the pooled fresh seeds pick {pooled_best['label']}. "
            "The greedy step chooses the best of six confirmed cuts on the selection seed, "
            "so its gains are biased upward, and a gain that the fresh seeds do not repeat is selection noise."
        )
    if extra and not beats_one:
        verdict += " No extra copy beats one Sky Field by 2 standard errors on the pooled fresh seeds."
    elif beats_one:
        verdict += " " + ", ".join(row["label"] for row in beats_one) + " beat one Sky Field by 2 standard errors on the pooled fresh seeds."
    others = array[1:]
    z_best = (pooled_best["pooled"]["weighted"] - base_row["pooled"]["weighted"]) / _diff_se(
        pooled_best["pooled"], base_row["pooled"]
    )
    if pooled_best is not base_row and z_best >= 2.0:
        verdict += (
            f" {pooled_best['label']} is the best of {len(others)} lists compared with Set M on these same games, "
            "so its gain is also biased upward."
        )
    rates = [row["pooled"]["weighted"] for row in array]
    steady = all(b >= a for a, b in zip(rates, rates[1:])) or all(b <= a for a, b in zip(rates, rates[1:]))
    if not steady:
        verdict += " The pooled rates neither rise nor fall steadily with the number of copies."
    lines.extend(["", verdict, "", f"Best list on the pooled fresh seeds ({pooled_best['label']}):", "", "```"])
    lines.extend(f"{count} {name}" for name, count in sorted(Counter(pooled_best["list"]).items()))
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
            "## Fresh seeds",
            "",
            f"The same lists on two seeds that no list was chosen on: `{rep['holdout_seed']}` with {rep['holdout_games']} games per foe "
            f"and `{rep['holdout2_seed']}` with {rep['holdout2_games']}. Weights are the same. "
            "The pooled columns merge both seeds, and the difference uses the unpaired standard error of the two lists.",
            "",
            "| Step | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    base_pool = base_row["pooled"]
    for i, row in enumerate(array):
        pooled = row["pooled"]
        cells = pooled["cells"]
        mark = " (best)" if i == rep["best_pooled_index"] else ""
        lines.append(
            f"| {row['label']}{mark} | {pct(row['holdout']['weighted'])} | {pct(row['holdout2']['weighted'])} | "
            f"{pct(pooled['weighted'])} | {pct(pooled['se'])} | {pooled['weighted'] - base_pool['weighted']:+.1%} | "
            f"{pct(_diff_se(pooled, base_pool))} | {pct(pooled['mean'])} | {pct(pooled['worst'])} | "
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
