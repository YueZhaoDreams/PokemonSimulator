#!/usr/bin/env python3
"""Greedy search with Boss's Orders and Counter Catcher as candidates, after the gust fix.

Before the fix Set M played Boss's Orders and Counter Catcher whenever the opponent had a Bench
(Counter Catcher also needed more Prize cards remaining than the opponent, as printed) and pulled the
lowest-HP Benched Pokémon. A third of those plays took no prize that turn, and in 15% to 23% the Active
Pokémon could already have been Knocked Out for the same prizes or more. The engine now plays a gust only
when the pulled Pokémon's Knock Out takes more prizes this turn than the Active Spot already would, and
pulls the Knock Out that takes the most prizes (`tests/test_mew_gust.py`).

The start list is the best list of `set-m-best-search.md`: four Sky Field and four Budew, with no Boss's
Orders and one Counter Catcher. Each step tries to add one more copy of Boss's Orders or of Counter
Catcher (4-of-a-name limit); every other card name is tried as the cut. Cuts are screened on SCREEN_GAMES
games per foe, the best SCREEN_TOP are confirmed on GAMES games per foe, and a step is taken only if it
beats the current list on the selection seed. The score is the loss-weighted win rate with the weights
frozen from the zero-Sky-Field Set M baseline, the same weights as every earlier Set M report.

The selection seed keeps the best of many cuts, so its gains are biased upward. Every list on the path is
run again on two fresh seeds, pooled, and Set M, the start list, the final list and the best list on the
fresh seeds are run once more on the clean seed of `set-m-best-search.md`. That seed and game count are
unchanged, so the same list can be set against its result before the gust fix.
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

import set_m_best_search as best  # noqa: E402
import set_m_sky_field as base  # noqa: E402
from set_m_sky_field import (  # noqa: E402
    FOES,
    GAMES,
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

START = HERE / "set-m-best-search.json"
DEST = Path(os.environ.get("M_GUST_DEST", HERE / "set-m-gust-search.json"))
MD_DEST = DEST.with_suffix(".md")
CACHE = Path(os.environ.get("M_GUST_CACHE", base.ROOT / "data/cache/set-m-gust-search-cells.json"))
ADDS = ("Boss's Orders", "Counter Catcher")
COPY_LIMIT = 4
MAX_STEPS = int(os.environ.get("M_GUST_MAX_STEPS", "4"))
FRESH1_SEED = int(os.environ.get("M_GUST_FRESH1_SEED", "20261105"))
FRESH1_GAMES = int(os.environ.get("M_GUST_FRESH1_GAMES", "2000"))
FRESH2_SEED = int(os.environ.get("M_GUST_FRESH2_SEED", "20261112"))
FRESH2_GAMES = int(os.environ.get("M_GUST_FRESH2_GAMES", "3000"))
CLEAN_SEED = int(os.environ.get("M_GUST_CLEAN_SEED", "20261029"))
CLEAN_GAMES = int(os.environ.get("M_GUST_CLEAN_GAMES", "8000"))

base.DEST = DEST
base.MD_DEST = MD_DEST
base.CACHE_PATH = CACHE

pool_cells = best.pool_cells
diff_se = best.diff_se


def usage(cells: dict[str, dict]) -> dict[str, float]:
    """Average Boss's Orders and Counter Catcher plays per game across the six foes."""
    return {
        "boss": sum(cells[key].get("boss_plays", 0) / cells[key]["games"] for key, *_ in FOES) / len(FOES),
        "catcher": sum(cells[key].get("catcher_plays", 0) / cells[key]["games"] for key, *_ in FOES) / len(FOES),
    }


def trim(row: dict) -> dict:
    out = {k: v for k, v in row.items() if k != "cells"}
    out["usage"] = usage(row["cells"])
    out["cells"] = {key: {"a": c["a"], "games": c["games"]} for key, c in row["cells"].items()}
    return out


def summarize(cells: dict[str, dict], weights: dict[str, float]) -> dict:
    return {
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "usage": usage(cells),
        "cells": {key: {"a": cells[key]["a"], "games": cells[key]["games"]} for key, *_ in FOES},
    }


def pool_with_usage(parts: list[dict[str, dict]]) -> dict[str, dict]:
    out = pool_cells(parts)
    for key, *_ in FOES:
        for field in ("boss_plays", "catcher_plays"):
            out[key][field] = sum(part[key].get(field, 0) for part in parts)
    return out


def candidates(current: list[str]) -> list[str]:
    counts = Counter(current)
    return [name for name in ADDS if counts[name] < COPY_LIMIT]


def old_engine(prev: dict) -> dict:
    """Clean-seed rows of the report before the gust fix, for the lists that are run again here."""
    if (prev["clean_seed"], prev["clean_games"]) != (CLEAN_SEED, CLEAN_GAMES):
        return {}
    return {row["label"]: row["clean"] for row in prev["clean_rows"]}


def main() -> None:
    started = time.perf_counter()
    prev = json.loads(START.read_text())["report"]
    set_m = list(prev["list_set_m"])
    weights = prev["weights"]
    start_label = prev["best_fresh_label"]
    start = list(next(row["list"] for row in prev["path"] if row["label"] == start_label))
    if len(start) != 60:
        raise SystemExit("start list is not 60 cards")
    before = old_engine(prev)
    before_start = before.get(start_label)
    before_set_m = before.get("Set M")

    cache = Cache(None)
    state: dict = {"report": {}}

    def save() -> None:
        base._save(cache, state["report"])

    prior = float(json.loads(DEST.read_text())["report"].get("elapsed") or 0) if DEST.exists() else 0.0

    print(f"start: {start_label}", flush=True)
    start_cells = evaluate([("start", start)], GAMES, cache, save, "start")["start"]
    current_row = row_for("—", start, start_cells, weights, Counter())
    print(f"start weighted {current_row['weighted']:.2%} mean {current_row['mean']:.2%}", flush=True)

    start_path_label = "Start (4 Sky Field, 4 Budew)"
    path = [
        {
            "label": start_path_label,
            "add": None,
            "cut": None,
            **trim(current_row),
            "cut": None,
            "list": start,
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
            "fresh1_seed": FRESH1_SEED,
            "fresh1_games": FRESH1_GAMES,
            "fresh2_seed": FRESH2_SEED,
            "fresh2_games": FRESH2_GAMES,
            "clean_seed": CLEAN_SEED,
            "clean_games": CLEAN_GAMES,
            "rule_preset": "s60",
            "elapsed": time.perf_counter() - started + prior,
            "method": (
                "greedy one-card swaps from the best Sky Field and Budew list; Boss's Orders and Counter Catcher "
                "(under the 4-of-a-name limit) are the cards to add; every card name except the added one is tried "
                "as the cut; a step is taken only if it beats the current list on the selection seed"
            ),
            "adds": list(ADDS),
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "start_label": start_label,
            "list_set_m": set_m,
            "list_start": start,
            "list": current,
            "path": path,
            "steps": steps,
            "stopped": stopped,
            "before_fix": {"Set M": before_set_m, "start": before_start},
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
        top = max(tried, key=lambda r: (r["row"]["weighted"], r["row"]["worst"]))
        gain = top["row"]["weighted"] - path[-1]["weighted"]
        step = {
            "step": step_no,
            "accepted": gain > 0,
            "gain": gain,
            "add": top["add"],
            "cut": top["chosen"],
            "candidates": [
                {
                    "add": r["add"],
                    "cut": r["chosen"],
                    "row": trim(r["row"]),
                    "confirm": [trim(c) for c in r["confirm"]],
                }
                for r in tried
            ],
            "screen": [{k: v for k, v in s.items() if k != "cells"} for s in top["screen"]],
        }
        steps.append(step)
        if gain <= 0:
            stopped = f"step {step_no}: no candidate beats the current list on the selection seed"
            print(f"  stop: best candidate {top['add']} is {gain:+.2%} against the current list", flush=True)
            state["report"] = report(False)
            save()
            break
        current = top["list"]
        path.append(
            {
                **trim(top["row"]),
                "label": f"Step {step_no}: +{top['add']}",
                "add": top["add"],
                "cut": top["chosen"],
                "list": list(current),
            }
        )
        print(f"  take +{top['add']} cut {top['chosen']}: {path[-1]['weighted']:.2%} ({gain:+.2%})", flush=True)
        state["report"] = report(False)
        save()

    lists = [("Set M", set_m)] + [(row["label"], row["list"]) for row in path]
    print(f"fresh seed 1 ({FRESH1_SEED})", flush=True)
    held1 = evaluate(lists, FRESH1_GAMES, cache, save, "fresh 1", seed=FRESH1_SEED)
    print(f"fresh seed 2 ({FRESH2_SEED})", flush=True)
    held2 = evaluate(lists, FRESH2_GAMES, cache, save, "fresh 2", seed=FRESH2_SEED)
    fresh = []
    for label, names in lists:
        pooled = pool_with_usage([held1[label], held2[label]])
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
        three = pool_with_usage([held1[label], held2[label], clean[label]])
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


def relation(z: float) -> str:
    if z >= 2.0:
        return "better than"
    if z <= -2.0:
        return "worse than"
    return "not clearly different from"


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
    verdict = "No step beats the start list on the selection seed, so the start list stays the best found."
    if final_label != start:
        d = clean[final_label]["all_fresh"]["weighted"] - clean[start]["all_fresh"]["weighted"]
        z = d / diff_se(clean[final_label]["all_fresh"], clean[start]["all_fresh"])
        d_clean = clean[final_label]["clean"]["weighted"] - clean[start]["clean"]["weighted"]
        z_clean = d_clean / diff_se(clean[final_label]["clean"], clean[start]["clean"])
        lines.append(
            f"- {final_label} against the start list: clean seed {d_clean:+.2%} ({z_clean:+.1f} standard errors); "
            f"all three fresh seeds {d:+.2%} ({z:+.1f})."
        )
        verdict = (
            f"The final list is {relation(z)} the start list on the three fresh seeds. "
            "The selection seed keeps the best of many cuts at every step, so its gain is biased upward and the fresh seeds decide."
        )
    best_label = rep["best_fresh_label"]
    if best_label != final_label:
        other = clean[best_label]
        d_clean = clean[final_label]["clean"]["weighted"] - other["clean"]["weighted"]
        z_clean = d_clean / diff_se(clean[final_label]["clean"], other["clean"])
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


def before_fix_lines(rep: dict) -> list[str]:
    before = rep.get("before_fix") or {}
    if not before.get("Set M") or not before.get("start"):
        return []
    clean = {row["label"]: row for row in rep["clean_rows"]}
    start = rep["path"][0]["label"]
    lines = [
        "",
        f"## The gust fix alone, clean seed `{rep['clean_seed']}`",
        "",
        "The same two lists, the same seed and game count, before and after the gust fix. The foes' decks and play are unchanged.",
        "",
        "| List | Before | After | Change | ±1 SE of diff | Boss's Orders per game | Counter Catcher per game |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for label, old in (("Set M", before["Set M"]), (start, before["start"])):
        new = clean[label]["clean"]
        lines.append(
            f"| {label} | {pct(old['weighted'])} | {pct(new['weighted'])} | {new['weighted'] - old['weighted']:+.2%} | "
            f"{pct(diff_se(old, new))} | {new['usage']['boss']:.2f} | {new['usage']['catcher']:.2f} |"
        )
    return lines


def render_md(rep: dict) -> str:
    weights = rep["weights"]
    path = rep["path"]
    start_row = path[0]
    lines = [
        "# Set M, Boss's Orders and Counter Catcher after the gust fix",
        "",
        "Set M used to play Boss's Orders and Counter Catcher whenever the opponent had a Bench, and pulled the lowest-HP Benched Pokémon.",
        "Counter Catcher also needs more Prize cards remaining than the opponent, as printed. In 300 games per foe on the locked Set M,",
        "36% of Boss's Orders plays took no prize that turn, and in 15% (Counter Catcher 23%) the Active Pokémon could already have been",
        "Knocked Out for the same prizes or more. A gust is now played only when the pulled Pokémon's Knock Out takes more prizes this turn than",
        "the Active Spot already would, and the pull is the Knock Out that takes the most prizes (`tests/test_mew_gust.py`).",
        "",
        "Start list is the best list of `set-m-best-search.md` (four Sky Field, four Budew, no Boss's Orders, one Counter Catcher).",
        "Each step may add one more copy of Boss's Orders or Counter Catcher (4-of-a-name limit), and every other card name is tried as the cut.",
        "A step is taken only if it beats the current list on the selection seed. Every list on the path is then run on two fresh seeds and pooled,",
        "and Set M, the start list, the final list and the best fresh-seed list on the clean seed.",
        "",
        f"- **Selection seed**: `{rep['seed']}`; cuts screened on {rep['screen_games']} games per foe, best {rep['screen_top']} confirmed on {rep['games']}",
        f"- **Fresh seeds**: `{rep['fresh1_seed']}` with {rep['fresh1_games']} per foe, `{rep['fresh2_seed']}` with {rep['fresh2_games']}",
        f"- **Clean seed**: `{rep['clean_seed']}` with {rep['clean_games']} per foe (the clean seed of `set-m-best-search.md`)",
        "- **Score**: loss-weighted win rate. Weights: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "## Path (selection seed)",
        "",
        "| Step | Add | Cut | Weighted | ±1 SE | vs start | Mean | Worst | Boss | Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in path:
        cells = row["cells"]
        lines.append(
            f"| {row['label']} | {row['add'] or '—'} | {row['cut'] or '—'} | {pct(row['weighted'])} | {pct(row['se'])} | "
            f"{row['weighted'] - start_row['weighted']:+.1%} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{row['usage']['boss']:.2f} | {row['usage']['catcher']:.2f} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(["", "Boss and Catcher are plays per game, averaged over the six foes."])
    for step in rep["steps"]:
        lines.extend(
            [
                "",
                f"## Step {step['step']}: {'take +' + step['add'] if step['accepted'] else 'stop'}",
                "",
                f"Best candidate is {step['add']} cutting {step['cut']}, {step['gain']:+.2%} against the current list on the selection seed"
                + ("." if step["accepted"] else ", so the search stops."),
                "",
                "| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Boss | Catcher |",
                "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for cand in sorted(step["candidates"], key=lambda c: -c["row"]["weighted"]):
            row = cand["row"]
            lines.append(
                f"| {cand['add']} | {cand['cut']} | {pct(row['weighted'])} | {pct(row['se'])} | {pct(row['mean'])} | "
                f"{pct(row['worst'])} | {row['usage']['boss']:.2f} | {row['usage']['catcher']:.2f} |"
            )
        lines.extend(
            [
                "",
                f"Confirmed cuts for {step['add']}:",
                "",
                "| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        top = next(c for c in step["candidates"] if c["add"] == step["add"])
        for rank, row in enumerate(top["confirm"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | "
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
            "| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | Boss | Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in fresh:
        pooled = row["pooled"]
        cells = pooled["cells"]
        lines.append(
            f"| {row['label']} | {pct(row['seed1']['weighted'])} | {pct(row['seed2']['weighted'])} | {pct(pooled['weighted'])} | "
            f"{pct(pooled['se'])} | {pooled['weighted'] - base_pool['weighted']:+.1%} | {pct(diff_se(pooled, base_pool))} | "
            f"{pct(pooled['mean'])} | {pct(pooled['worst'])} | {pooled['usage']['boss']:.2f} | {pooled['usage']['catcher']:.2f} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | "
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
    lines.extend(before_fix_lines(rep))
    lines.extend(["", "## Result", ""] + result_lines(rep))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
