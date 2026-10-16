#!/usr/bin/env python3
"""Keep searching from the best Sky Field and Budew list on Set M, with every 30 HP Basic as a candidate.

The start list is the last row of set-m-budew-policy.json: Set M with one Sky Field and
four Budew, played with the fixed Baby order. Each step tries to add one more copy of
each card name that is still under the 4-of-a-name limit and is on the candidate list
(Sky Field, Budew, Igglybuff, Mime Jr., Cleffa). For each candidate, every card name in the
list except the candidate is tried as the cut. Cuts are screened on SCREEN_GAMES games per foe,
the best SCREEN_TOP are confirmed on GAMES games per foe, and the candidate whose best cut scores
highest is the step. A step is taken only if it beats the current list on the selection seed,
so the search stops at the first plateau. The score is the loss-weighted win rate with the
weights frozen from the zero-Sky-Field baseline.

The selection seed picks the best of many cuts, so its gains are biased upward. Every list on the
path is therefore run again on two fresh seeds, pooled, and the start list, Set M and the final
list are run once more on a third seed that nothing was chosen on.
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
    Cache,
    cell,
    evaluate,
    greedy_step,
    mean,
    pct,
    row_for,
    weighted,
    weighted_se,
    worst,
)

START = HERE / "set-m-budew-policy.json"
DEST = Path(os.environ.get("M_BEST_DEST", HERE / "set-m-best-search.json"))
MD_DEST = DEST.with_suffix(".md")
CACHE = Path(os.environ.get("M_BEST_CACHE", base.ROOT / "data/cache/set-m-best-search-cells.json"))
ADDS = ("Sky Field", "Budew", "Igglybuff", "Mime Jr.", "Cleffa")
COPY_LIMIT = 4
MAX_STEPS = int(os.environ.get("M_BEST_MAX_STEPS", "5"))
HOLDOUT2_SEED = int(os.environ.get("M_SKY_HOLDOUT2_SEED", "20261022"))
HOLDOUT2_GAMES = int(os.environ.get("M_SKY_HOLDOUT2_GAMES", "3000"))
CLEAN_SEED = int(os.environ.get("M_BEST_CLEAN_SEED", "20261029"))
CLEAN_GAMES = int(os.environ.get("M_BEST_CLEAN_GAMES", "8000"))

base.DEST = DEST
base.MD_DEST = MD_DEST
base.CACHE_PATH = CACHE


def trim(row: dict) -> dict:
    out = {k: v for k, v in row.items() if k != "cells"}
    out["cells"] = {key: {"a": c["a"]} for key, c in row["cells"].items()}
    return out


def summarize(cells: dict[str, dict], weights: dict[str, float]) -> dict:
    return {
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "cells": {key: {"a": cells[key]["a"], "games": cells[key]["games"]} for key, *_ in FOES},
    }


def pool_cells(parts: list[dict[str, dict]]) -> dict[str, dict]:
    out = {}
    for key, *_ in FOES:
        games = sum(part[key]["games"] for part in parts)
        out[key] = {"a": sum(part[key]["a"] * part[key]["games"] for part in parts) / games, "games": games}
    return out


def diff_se(a: dict, b: dict) -> float:
    return (a["se"] ** 2 + b["se"] ** 2) ** 0.5


def candidates(current: list[str]) -> list[str]:
    counts = Counter(current)
    return [name for name in ADDS if counts[name] < COPY_LIMIT]


def main() -> None:
    started = time.perf_counter()
    seed_report = json.loads(START.read_text())["report"]
    set_m = list(seed_report["list_start"])
    sky_row = seed_report["array"][1]
    start_row = seed_report["array"][-1]
    if (start_row["sky"], start_row["budew"]) != (1, 4):
        raise SystemExit("start row is not one Sky Field and four Budew")
    weights = seed_report["weights"]
    start = list(start_row["list"])
    if len(start) != 60:
        raise SystemExit("start list is not 60 cards")

    cache = Cache(None)
    state: dict = {"report": {}}

    def save() -> None:
        base._save(cache, state["report"])

    prior = float(json.loads(DEST.read_text())["report"].get("elapsed") or 0) if DEST.exists() else 0.0

    print("start: Set M with one Sky Field and four Budew", flush=True)
    start_cells = evaluate([("start", start)], GAMES, cache, save, "start")["start"]
    current_row = row_for("—", start, start_cells, weights, Counter())
    print(f"start weighted {current_row['weighted']:.2%} mean {current_row['mean']:.2%}", flush=True)

    path = [
        {
            "label": "Budew 4 (start)",
            "add": None,
            "cut": None,
            "list": start,
            **{k: v for k, v in trim(current_row).items() if k != "cut"},
        }
    ]
    steps: list[dict] = []
    current = list(start)
    stopped = f"reached {MAX_STEPS} steps"

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
            "clean_seed": CLEAN_SEED,
            "clean_games": CLEAN_GAMES,
            "rule_preset": "s60",
            "elapsed": time.perf_counter() - started + prior,
            "method": (
                "greedy one-card swaps from the best Sky Field and Budew list; every card name under the 4-of-a-name "
                "limit on the candidate list is tried as the card to add; every card name except the added one is "
                "tried as the cut; a step is taken only if it beats the current list on the selection seed"
            ),
            "adds": list(ADDS),
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "list_set_m": set_m,
            "list_start": start,
            "list": current,
            "path": path,
            "steps": steps,
            "stopped": stopped,
            "done": done,
        }

    for step_no in range(1, MAX_STEPS + 1):
        tried = []
        for add in candidates(current):
            print(f"step {step_no}: add {add}", flush=True)
            state["report"] = report(False)
            res = greedy_step(current, add, weights, cache, save, f"step {step_no} +{add}", limit=COPY_LIMIT, protect={add})
            row = res["row"]
            print(
                f"  best cut {res['chosen']}: weighted {row['weighted']:.2%} (±{row['se']:.2%}) "
                f"mean {row['mean']:.2%} babies {row['babies']:.2f}",
                flush=True,
            )
            tried.append(res)
        if not tried:
            stopped = "every card on the candidate list is at the copy limit"
            break
        best = max(tried, key=lambda r: (r["row"]["weighted"], r["row"]["worst"]))
        gain = best["row"]["weighted"] - path[-1]["weighted"]
        step = {
            "step": step_no,
            "accepted": gain > 0,
            "gain": gain,
            "add": best["add"],
            "cut": best["chosen"],
            "candidates": [
                {
                    "add": r["add"],
                    "cut": r["chosen"],
                    "row": trim(r["row"]),
                    "confirm": [trim(c) for c in r["confirm"]],
                }
                for r in tried
            ],
            "screen": [trim(s) for s in best["screen"]],
        }
        steps.append(step)
        if gain <= 0:
            stopped = f"step {step_no}: no candidate beats the current list on the selection seed"
            print(f"  stop: best candidate {best['add']} is {gain:+.2%} against the current list", flush=True)
            state["report"] = report(False)
            save()
            break
        current = best["list"]
        counts = Counter(current)
        path.append(
            {
                "label": f"Step {step_no}: +{best['add']}",
                "add": best["add"],
                "cut": best["chosen"],
                "list": list(current),
                **{k: v for k, v in trim(best["row"]).items() if k != "cut"},
            }
        )
        print(f"  take +{best['add']} cut {best['chosen']}: {path[-1]['weighted']:.2%} ({gain:+.2%})", flush=True)
        state["report"] = report(False)
        save()

    lists = [("Set M", set_m), ("Sky Field", list(sky_row["list"]))] + [(row["label"], row["list"]) for row in path]
    print("fresh seed 1", flush=True)
    held1 = evaluate(lists, HOLDOUT_GAMES, cache, save, "fresh 1", seed=HOLDOUT_SEED)
    print("fresh seed 2", flush=True)
    held2 = evaluate(lists, HOLDOUT2_GAMES, cache, save, "fresh 2", seed=HOLDOUT2_SEED)
    fresh = []
    for label, names in lists:
        pooled = pool_cells([held1[label], held2[label]])
        fresh.append(
            {
                "label": label,
                "list": names,
                "seed1": summarize(held1[label], weights),
                "seed2": summarize(held2[label], weights),
                "pooled": summarize(pooled, weights),
            }
        )
        print(
            f"  {label}: {fresh[-1]['seed1']['weighted']:.2%} / {fresh[-1]['seed2']['weighted']:.2%} "
            f"pooled {fresh[-1]['pooled']['weighted']:.2%}",
            flush=True,
        )

    final_label = path[-1]["label"]
    fresh_by_label = {row["label"]: row for row in fresh}
    best_fresh_label = max(
        (row["label"] for row in path), key=lambda label: fresh_by_label[label]["pooled"]["weighted"]
    )
    wanted = {path[0]["label"], final_label, best_fresh_label}
    clean_lists = [("Set M", set_m)] + [(row["label"], row["list"]) for row in path if row["label"] in wanted]
    print(f"clean seed {CLEAN_SEED}: {', '.join(label for label, _ in clean_lists)}", flush=True)
    clean = evaluate(clean_lists, CLEAN_GAMES, cache, save, "clean", seed=CLEAN_SEED)
    clean_rows = []
    for label, names in clean_lists:
        three = pool_cells([held1[label], held2[label], clean[label]])
        clean_rows.append(
            {
                "label": label,
                "list": names,
                "clean": summarize(clean[label], weights),
                "all_fresh": summarize(three, weights),
            }
        )
        print(
            f"  {label}: clean {clean_rows[-1]['clean']['weighted']:.2%} "
            f"(±{clean_rows[-1]['clean']['se']:.2%}) three fresh seeds {clean_rows[-1]['all_fresh']['weighted']:.2%}",
            flush=True,
        )

    final = report(True)
    final["fresh"] = fresh
    final["clean_rows"] = clean_rows
    final["best_selection_index"] = max(range(len(path)), key=lambda i: (path[i]["weighted"], -i))
    final["best_fresh_label"] = best_fresh_label
    state["report"] = final
    save()
    MD_DEST.write_text(render_md(final))
    print(f"wrote {MD_DEST}", flush=True)


def result_lines(rep: dict) -> list[str]:
    fresh = {row["label"]: row for row in rep["fresh"]}
    clean = {row["label"]: row for row in rep["clean_rows"]}
    path = rep["path"]
    start = path[0]["label"]
    final_label = path[-1]["label"]
    set_m = clean["Set M"]
    lines = [
        f"- Start list ({start}): {pct(path[0]['weighted'])} on the selection seed, "
        f"{pct(fresh[start]['pooled']['weighted'])} on the two fresh seeds pooled, "
        f"{pct(clean[start]['clean']['weighted'])} on the clean seed."
    ]
    if len(path) == 1:
        lines.append(f"- The search took no step: {rep['stopped']}.")
    for row in path[1:]:
        label = row["label"]
        pooled = fresh[label]["pooled"]
        z_start = (pooled["weighted"] - fresh[start]["pooled"]["weighted"]) / diff_se(pooled, fresh[start]["pooled"])
        lines.append(
            f"- {label} (cut {row['cut']}): {pct(row['weighted'])} on the selection seed "
            f"({row['weighted'] - path[0]['weighted']:+.1%} against the start list); two fresh seeds pooled "
            f"{pct(pooled['weighted'])} ({pooled['weighted'] - fresh[start]['pooled']['weighted']:+.1%}, {z_start:+.1f} standard errors)."
        )
    lines.append(f"- The search stopped: {rep['stopped']}.")
    final = clean[final_label]
    for label in [name for name in clean if name != "Set M"]:
        other = clean[label]
        d_clean = other["clean"]["weighted"] - set_m["clean"]["weighted"]
        z_clean = d_clean / diff_se(other["clean"], set_m["clean"])
        d_all = other["all_fresh"]["weighted"] - set_m["all_fresh"]["weighted"]
        z_all = d_all / diff_se(other["all_fresh"], set_m["all_fresh"])
        lines.append(
            f"- {label} against Set M: clean seed {d_clean:+.2%} ({z_clean:+.1f} standard errors); "
            f"all three fresh seeds {d_all:+.2%} ({z_all:+.1f})."
        )
    if final_label != start:
        d = final["all_fresh"]["weighted"] - clean[start]["all_fresh"]["weighted"]
        z = d / diff_se(final["all_fresh"], clean[start]["all_fresh"])
        d_clean = final["clean"]["weighted"] - clean[start]["clean"]["weighted"]
        z_clean = d_clean / diff_se(final["clean"], clean[start]["clean"])
        lines.append(
            f"- {final_label} against the start list: clean seed {d_clean:+.2%} ({z_clean:+.1f} standard errors); "
            f"all three fresh seeds {d:+.2%} ({z:+.1f})."
        )
        if z >= 2.0:
            relation = "better than"
        elif z <= -2.0:
            relation = "worse than"
        else:
            relation = "not clearly different from"
        verdict = (
            f"The final list is {relation} the start list on the three fresh seeds. "
            "The selection seed keeps the best of many cuts at every step, so its gain is biased upward and the fresh seeds decide."
        )
    else:
        verdict = "No step beats the start list on the selection seed, so the start list stays the best found."
    best_label = rep["best_fresh_label"]
    if best_label != final_label:
        other = clean[best_label]
        d_clean = final["clean"]["weighted"] - other["clean"]["weighted"]
        z_clean = d_clean / diff_se(final["clean"], other["clean"])
        lines.append(
            f"- {final_label} against {best_label}, the best list on the two fresh seeds: clean seed {d_clean:+.2%} "
            f"({z_clean:+.1f} standard errors)."
        )
    best_row = next(row for row in path if row["label"] == best_label)
    lines.extend(
        [
            "",
            verdict,
            "",
            f"Best list on the two fresh seeds ({best_label}); the clean seed above was not used to pick it:",
            "",
            "```",
        ]
    )
    lines.extend(f"{count} {name}" for name, count in sorted(Counter(best_row["list"]).items()))
    lines.extend(["```", ""])
    return lines


def render_md(rep: dict) -> str:
    weights = rep["weights"]
    path = rep["path"]
    start_row = path[0]
    lines = [
        "# Set M, more search from one Sky Field and four Budew",
        "",
        "Start list is the last row of `set-m-budew-policy.md`: the locked Set M (`SET_M60_NAMES`) with one Sky Field and four Budew,",
        "played with the fixed Baby order (`tests/test_mew_baby_attacker.py`).",
        "Each step may add one more copy of Sky Field, Budew, Igglybuff, Mime Jr. or Cleffa (4-of-a-name limit), and every card name",
        "in the list except the added one is tried as the cut. A step is taken only if it beats the current list on the selection seed.",
        "Every list on the path is then run on two fresh seeds and pooled, and Set M, the start list and the final list on a third.",
        "",
        f"- **Selection seed**: `{rep['seed']}`; cuts screened on {rep['screen_games']} games per foe, best {rep['screen_top']} confirmed on {rep['games']}",
        f"- **Fresh seeds**: `{rep['holdout_seed']}` with {rep['holdout_games']} per foe, `{rep['holdout2_seed']}` with {rep['holdout2_games']}",
        f"- **Clean seed**: `{rep['clean_seed']}` with {rep['clean_games']} per foe",
        "- **Score**: loss-weighted win rate. Weights: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "## Path (selection seed)",
        "",
        "| Step | Add | Cut | Weighted | ±1 SE | vs start | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in path:
        cells = row["cells"]
        lines.append(
            f"| {row['label']} | {row['add'] or '—'} | {row['cut'] or '—'} | {pct(row['weighted'])} | {pct(row['se'])} | "
            f"{row['weighted'] - start_row['weighted']:+.1%} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    for step in rep["steps"]:
        lines.extend(
            [
                "",
                f"## Step {step['step']}: {'take ' + step['add'] if step['accepted'] else 'stop'}",
                "",
                f"Best candidate is {step['add']} cutting {step['cut']}, {step['gain']:+.2%} against the current list on the selection seed"
                + ("." if step["accepted"] else ", so the search stops."),
                "",
                "| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Babies | 8 Babies |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for cand in sorted(step["candidates"], key=lambda c: -c["row"]["weighted"]):
            row = cand["row"]
            lines.append(
                f"| {cand['add']} | {cand['cut']} | {pct(row['weighted'])} | {pct(row['se'])} | {pct(row['mean'])} | "
                f"{pct(row['worst'])} | {row['babies']:.2f} | {pct(row['attack8'])} |"
            )
        lines.extend(
            [
                "",
                f"Confirmed cuts for {step['add']}:",
                "",
                "| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        best = next(c for c in step["candidates"] if c["add"] == step["add"])
        for rank, row in enumerate(best["confirm"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | {row['babies']:.2f} | "
                f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
                f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
            )
    fresh = rep["fresh"]
    base_pool = fresh[0]["pooled"]
    lines.extend(
        [
            "",
            "## Fresh seeds",
            "",
            "No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.",
            "",
            "| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in fresh:
        pooled = row["pooled"]
        cells = pooled["cells"]
        lines.append(
            f"| {row['label']} | {pct(row['seed1']['weighted'])} | {pct(row['seed2']['weighted'])} | {pct(pooled['weighted'])} | "
            f"{pct(pooled['se'])} | {pooled['weighted'] - base_pool['weighted']:+.1%} | {pct(diff_se(pooled, base_pool))} | "
            f"{pct(pooled['mean'])} | {pct(pooled['worst'])} | {cell(cells, 't60')} | {cell(cells, 'hedrick')} | "
            f"{cell(cells, 'c60')} | {cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    set_m = rep["clean_rows"][0]
    lines.extend(
        [
            "",
            f"## Clean seed `{rep['clean_seed']}`",
            "",
            f"{rep['clean_games']} games per foe per list. The last two columns merge this seed with both fresh seeds.",
            "",
            "| List | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs Set M |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rep["clean_rows"]:
        c = row["clean"]
        cells = c["cells"]
        lines.append(
            f"| {row['label']} | {pct(c['weighted'])} | {pct(c['se'])} | {c['weighted'] - set_m['clean']['weighted']:+.2%} | "
            f"{pct(diff_se(c, set_m['clean']))} | {pct(c['mean'])} | {pct(c['worst'])} | {cell(cells, 't60')} | "
            f"{cell(cells, 'hedrick')} | {cell(cells, 'c60')} | {cell(cells, 'd60')} | {cell(cells, 'thorns')} | "
            f"{cell(cells, 'starmie')} | {pct(row['all_fresh']['weighted'])} | "
            f"{row['all_fresh']['weighted'] - set_m['all_fresh']['weighted']:+.2%} |"
        )
    lines.extend(
        [
            "",
            "## Bench of 30 HP Pokémon (selection seed)",
            "",
            "| List | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies | Itchy Pollen |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in path:
        lines.append(
            f"| {row['label']} | {row['babies']:.2f} | {pct(row['sky_games'])} | {pct(row['attack6'])} | "
            f"{pct(row['attack7'])} | {pct(row['attack8'])} | {pct(row['itchy'])} |"
        )
    lines.extend(["", "## Result", ""] + result_lines(rep))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
