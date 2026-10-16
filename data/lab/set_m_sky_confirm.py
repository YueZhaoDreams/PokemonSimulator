#!/usr/bin/env python3
"""One pre-set comparison on a seed nothing was chosen on: locked Set M against the
two-Sky-Field list the copies search ended on (cut one Night Stretcher and the one
Boss's Orders for two Sky Field).

The copies search compared four lists on the same fresh games and kept the best, so
its gain is biased upward. This is the single comparison it left open, run once on a
new seed with the same frozen loss weights.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import set_m_sky_field as base  # noqa: E402
from set_m_sky_field import FOES, Cache, cell, evaluate, mean, pct, weighted, weighted_se, worst  # noqa: E402

CONFIRM_SEED = int(os.environ.get("M_SKY_CONFIRM_SEED", "20261029"))
CONFIRM_GAMES = int(os.environ.get("M_SKY_CONFIRM_GAMES", "8000"))
DEST = Path(os.environ.get("M_SKY_CONFIRM_DEST", HERE / "set-m-sky-confirm.json"))
MD_DEST = DEST.with_suffix(".md")
COPIES = HERE / "set-m-sky-copies.json"
TWO_COPIES_INDEX = 2


def inputs() -> tuple[list[str], list[str], dict[str, float], dict]:
    rep = json.loads(COPIES.read_text())["report"]
    set_m = rep["array"][0]["list"]
    two = rep["array"][TWO_COPIES_INDEX]
    if two["sky"] != 2:
        raise SystemExit("copies report row 2 is not the two-Sky-Field list")
    return list(set_m), list(two["list"]), rep["weights"], rep


def summarize(cells: dict[str, dict], weights: dict[str, float]) -> dict:
    return {
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "cells": {key: {"a": cells[key]["a"], "games": cells[key]["games"]} for key, *_ in FOES},
    }


def verdict(set_m: dict, two: dict) -> tuple[float, float, str]:
    diff = two["weighted"] - set_m["weighted"]
    se = (two["se"] ** 2 + set_m["se"] ** 2) ** 0.5
    z = diff / se
    if z >= 2.0:
        text = "The two-Sky-Field list beats Set M by at least 2 standard errors on a seed nothing was chosen on."
    elif z <= -2.0:
        text = "The two-Sky-Field list is worse than Set M by at least 2 standard errors on a seed nothing was chosen on."
    else:
        text = "The difference is under 2 standard errors, so this seed does not separate the two lists."
    return diff, z, text


def render_md(rep: dict) -> str:
    set_m, two = rep["set_m"], rep["two_sky"]
    diff, z, text = verdict(set_m, two)
    lines = [
        "# Set M against Set M with two Sky Field, one fresh seed",
        "",
        "Set M is the locked list (`SET_M60_NAMES`). The other list is the one the copies search ended on at two copies:",
        "one Night Stretcher and the one Boss's Orders cut, two Sky Field added (`set-m-sky-copies.md`).",
        "That search compared four lists on the same fresh games and kept the best, so its +0.7% is biased upward.",
        "This is the one comparison it left open, run once on a seed no list was chosen on.",
        "",
        f"- **Seed**: `{rep['seed']}`",
        f"- **Games**: {rep['games']} per foe per list",
        "- **Weights**: " + ", ".join(f"{key} {rep['weights'][key]:.1%}" for key, *_ in FOES) + " (frozen from the zero-Sky-Field baseline)",
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "| List | Weighted | ±1 SE | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, row in (("Set M", set_m), ("Two Sky Field", two)):
        cells = row["cells"]
        lines.append(
            f"| {label} | {pct(row['weighted'])} | {pct(row['se'])} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(
        [
            "",
            "## Result",
            "",
            f"Two Sky Field minus Set M: {diff:+.2%} weighted ({z:+.1f} standard errors, unpaired). {text}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    set_m, two, weights, copies = inputs()
    cache = Cache(None)

    def save() -> None:
        base.CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        base.CACHE_PATH.write_text(json.dumps(cache.cells) + "\n")

    print(f"confirm: seed {CONFIRM_SEED}, {CONFIRM_GAMES} games per foe per list", flush=True)
    cells = evaluate([("set_m", set_m), ("two_sky", two)], CONFIRM_GAMES, cache, save, "confirm", seed=CONFIRM_SEED)
    save()
    rep = {
        "seed": CONFIRM_SEED,
        "games": CONFIRM_GAMES,
        "rule_preset": "s60",
        "weights": weights,
        "elapsed": time.perf_counter() - started,
        "list_set_m": set_m,
        "list_two_sky": two,
        "set_m": summarize(cells["set_m"], weights),
        "two_sky": summarize(cells["two_sky"], weights),
        "selection_seed": copies["seed"],
        "earlier_fresh_seeds": [copies["holdout_seed"], copies["holdout2_seed"]],
    }
    diff, z, text = verdict(rep["set_m"], rep["two_sky"])
    rep["diff"], rep["z"], rep["verdict"] = diff, z, text
    DEST.write_text(json.dumps({"report": rep}, indent=1) + "\n")
    MD_DEST.write_text(render_md(rep))
    print(f"set M {rep['set_m']['weighted']:.2%} (±{rep['set_m']['se']:.2%})  "
          f"two Sky Field {rep['two_sky']['weighted']:.2%} (±{rep['two_sky']['se']:.2%})  "
          f"diff {diff:+.2%} ({z:+.1f} SE)", flush=True)
    print(text, flush=True)
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
