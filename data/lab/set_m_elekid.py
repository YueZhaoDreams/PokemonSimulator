#!/usr/bin/env python3
"""Greedy Elekid search on the locked Set M, forced to four copies so the report can say how many are best.

Elekid (Paradox Rift 59) is a 30 HP Basic Lightning Pokémon with Retreat Cost 0. Crackling Shot costs no Energy:
"This attack does 30 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched
Pokémon.)" It is one more Benched body for Igglybuff's Bouncy Circle. The attack is a finisher only. It is used when
the Knock Out wins the game, or when it takes at least 2 prizes the Active attack cannot take this turn. Mew ex copies
it and stays Active. Elekid itself goes Active only when Mew ex cannot use the attack and that Knock Out is extreme.
The play is written in `set-m-elekid-strategy.md` before the search.

The measured start is that report's `list_start`, the lock when the search ran: four Team Rocket's Petrel, one Junk Arm,
three Sky Field, four Budew, four Battle Cage, no Elekid, no Ultra Ball, no Penny, no Boss's Orders. A later lock of
`SET_M60_NAMES` does not move it. Each step adds one more Elekid and tries every other card name as the cut.
Cuts are screened on SCREEN_GAMES games per foe, the best SCREEN_TOP are confirmed on GAMES games per foe, and the best
confirmed cut is taken even when the list gets worse, up to MAX_COPIES (the 4-of-a-name limit). The score is the
loss-weighted win rate. Weights are frozen from this locked list on the selection seed.

The selection seed keeps the best of many cuts, so its gains are biased upward. Every list on the path is run again on two
fresh seeds and pooled, and the start list, the final list and the best list on the fresh seeds are run once more on the
clean seed used by the earlier Set M reports.
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
    SCREEN_GAMES,
    SCREEN_TOP,
    SEED,
    Cache,
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

DEST = Path(os.environ.get("M_ELEKID_DEST", HERE / "set-m-elekid.json"))
MD_DEST = DEST.with_suffix(".md")
CACHE = Path(os.environ.get("M_ELEKID_CACHE", base.ROOT / "data/cache/set-m-elekid-finisher-cells.json"))
ADD = "Elekid"
COPY_LIMIT = 4
MAX_COPIES = int(os.environ.get("M_ELEKID_MAX_COPIES", "4"))
FRESH1_SEED = int(os.environ.get("M_ELEKID_FRESH1_SEED", "20261105"))
FRESH1_GAMES = int(os.environ.get("M_ELEKID_FRESH1_GAMES", "2000"))
FRESH2_SEED = int(os.environ.get("M_ELEKID_FRESH2_SEED", "20261112"))
FRESH2_GAMES = int(os.environ.get("M_ELEKID_FRESH2_GAMES", "3000"))
CLEAN_SEED = int(os.environ.get("M_ELEKID_CLEAN_SEED", "20261029"))
CLEAN_GAMES = int(os.environ.get("M_ELEKID_CLEAN_GAMES", "8000"))

# Counts per cell. The prefixes are the events the engine bumps, and every one is a sum over games.
EXTRA_QUERIES = [
    {"type": "event_sum", "prefix": "attack:Elekid:Crackling Shot", "key": "elekid_own"},
    {"type": "event_sum", "prefix": "attack:Mew ex:Crackling Shot", "key": "elekid_mew"},
    {"type": "event_sum", "prefix": "snipe_ko_a", "key": "snipe_ko"},
    {"type": "event_sum", "prefix": "snipe_ko_bench_a", "key": "snipe_ko_bench"},
    {"type": "event_sum", "prefix": "ko:Elekid", "key": "elekid_ko"},
    {"type": "event_prefix", "prefix": "attack:Elekid:Crackling Shot", "key": "elekid_games"},
]
USAGE_KEYS = (
    "boss_plays",
    "catcher_plays",
    "elekid_own",
    "elekid_mew",
    "snipe_ko",
    "snipe_ko_bench",
    "elekid_ko",
    "elekid_games",
)
for query in EXTRA_QUERIES:
    if query not in base.QUERIES:
        base.QUERIES.append(query)
base.EXTRA_COUNT_KEYS = tuple(q["key"] for q in EXTRA_QUERIES)

base.DEST = DEST
base.MD_DEST = MD_DEST
base.CACHE_PATH = CACHE


def pool_cells(parts: list[dict[str, dict]]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for key, *_ in FOES:
        games = sum(part[key]["games"] for part in parts)
        out[key] = {"a": sum(part[key]["a"] * part[key]["games"] for part in parts) / games, "games": games}
        for field in USAGE_KEYS:
            out[key][field] = sum(part[key].get(field, 0) for part in parts)
    return out


def diff_se(a: dict, b: dict) -> float:
    return (a["se"] ** 2 + b["se"] ** 2) ** 0.5


def usage(cells: dict[str, dict]) -> dict[str, float]:
    """Average per game across the six foes. Elekid games is the share of games with a Crackling Shot."""
    out = {}
    for field in USAGE_KEYS:
        out[field] = sum(cells[key].get(field, 0) / cells[key]["games"] for key, *_ in FOES) / len(FOES)
    return out


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


def copies_label(count: int) -> str:
    return "Start (no Elekid)" if count == 0 else f"{count} Elekid"


def starting_list() -> list[str]:
    """The Set M this search measured. Four Battle Cage, zero Elekid.

    The card order is the report's list_start. Later locks of SET_M60_NAMES
    do not move it. The lock after this search is one Elekid for one Battle Cage.
    """
    if not DEST.exists():
        raise SystemExit("measured start is the report's list_start, and that report is missing")
    names = list(json.loads(DEST.read_text())["report"]["list_start"])
    if len(names) != 60 or names.count(ADD) or names.count("Battle Cage") != 4:
        raise SystemExit("measured start is not the four Battle Cage list without Elekid")
    if names.count("Team Rocket's Petrel") != 4 or names.count("Junk Arm") != 1 or names.count("Manaphy") != 1:
        raise SystemExit("measured start is not the Junk Arm lock")
    return names


def main() -> None:
    started = time.perf_counter()
    start = starting_list()
    start_label = copies_label(0)

    cache = Cache(None)
    state: dict = {"report": {}}

    def save() -> None:
        base._save(cache, state["report"])

    prior = 0.0
    if DEST.exists():
        old = json.loads(DEST.read_text()).get("report") or {}
        if old.get("list_start") == start and not old.get("done"):
            prior = float(old.get("elapsed") or 0)

    print(f"start: locked Set M ({start_label})", flush=True)
    start_cells = evaluate([("start", start)], GAMES, cache, save, "start")["start"]
    weights = loss_weights({key: start_cells[key]["a"] for key, *_ in FOES})
    print("weights " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES), flush=True)
    current_row = row_for("—", start, start_cells, weights, Counter())
    print(f"start weighted {current_row['weighted']:.2%} mean {current_row['mean']:.2%}", flush=True)

    path = [{"label": copies_label(0), "copies": 0, **trim(current_row), "cut": None, "list": start}]
    steps: list[dict] = []
    current = list(start)

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
                "greedy one-card swaps from the locked Set M (four Petrel, one Junk Arm, three Sky Field, four Budew); "
                "one more Elekid per step, forced up to "
                f"{MAX_COPIES} copies (the 4-of-a-name limit); every other card name is tried as the cut; the best "
                "confirmed cut is taken even when the list gets worse, so the fresh seeds can name the best number of copies; "
                "Crackling Shot is used only for an extreme Knock Out, and Mew ex stays Active when it can copy it"
            ),
            "add": ADD,
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "weights_from": "locked Set M on the selection seed",
            "start_label": start_label,
            "list_set_m": list(start),
            "list_start": list(start),
            "list": current,
            "path": path,
            "steps": steps,
            "done": done,
        }

    for step_no in range(1, MAX_COPIES + 1):
        print(f"step {step_no}: add {ADD}", flush=True)
        state["report"] = report(False)
        res = greedy_step(current, ADD, weights, cache, save, f"step {step_no} +{ADD}", limit=COPY_LIMIT, protect={ADD})
        row = res["row"]
        gain = row["weighted"] - path[-1]["weighted"]
        print(
            f"  best cut {res['chosen']}: weighted {row['weighted']:.2%} (±{row['se']:.2%}) "
            f"mean {row['mean']:.2%} ({gain:+.2%} against the list before)",
            flush=True,
        )
        steps.append(
            {
                "step": step_no,
                "gain": gain,
                "cut": res["chosen"],
                "row": trim(row),
                "confirm": [trim(c) for c in res["confirm"]],
                "screen": [{k: v for k, v in s.items() if k != "cells"} for s in res["screen"]],
            }
        )
        current = res["list"]
        path.append(
            {
                **trim(row),
                "label": copies_label(step_no),
                "copies": step_no,
                "cut": res["chosen"],
                "list": list(current),
            }
        )
        state["report"] = report(False)
        save()

    lists = [(row["label"], row["list"]) for row in path]
    print(f"fresh seed 1 ({FRESH1_SEED})", flush=True)
    held1 = evaluate(lists, FRESH1_GAMES, cache, save, "fresh 1", seed=FRESH1_SEED)
    print(f"fresh seed 2 ({FRESH2_SEED})", flush=True)
    held2 = evaluate(lists, FRESH2_GAMES, cache, save, "fresh 2", seed=FRESH2_SEED)
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
    clean_lists = [(row["label"], row["list"]) for row in path if row["label"] in wanted]
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
            f"(±{clean_rows[-1]['clean']['se']:.2%}) three seeds {clean_rows[-1]['all_fresh']['weighted']:.2%}",
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
    best_label = rep["best_fresh_label"]
    lines = [
        f"- Locked Set M, no Elekid: {pct(path[0]['weighted'])} on the selection seed, "
        f"{pct(fresh[start]['pooled']['weighted'])} on the two fresh seeds pooled, "
        f"{pct(clean[start]['clean']['weighted'])} on the clean seed."
    ]
    for row in path[1:]:
        label = row["label"]
        pooled = fresh[label]["pooled"]
        base_pool = fresh[start]["pooled"]
        z = (pooled["weighted"] - base_pool["weighted"]) / diff_se(pooled, base_pool)
        lines.append(
            f"- {label} (cut {row['cut']}): {pct(row['weighted'])} on the selection seed "
            f"({row['weighted'] - path[0]['weighted']:+.1%} against the start list); two fresh seeds pooled "
            f"{pct(pooled['weighted'])} ({pooled['weighted'] - base_pool['weighted']:+.1%}, {z:+.1f} standard errors)."
        )
    for prev, row in zip(path, path[1:]):
        later = fresh[row["label"]]["pooled"]
        earlier = fresh[prev["label"]]["pooled"]
        gap = later["weighted"] - earlier["weighted"]
        z_step = gap / diff_se(later, earlier)
        lines.append(
            f"- {row['label']} against {prev['label']} on the two fresh seeds: {gap:+.2%} ({z_step:+.1f} standard errors)."
        )
    fresh_gap = fresh[best_label]["pooled"]["weighted"] - fresh[start]["pooled"]["weighted"]
    fresh_z = fresh_gap / diff_se(fresh[best_label]["pooled"], fresh[start]["pooled"])
    if best_label != start:
        d_clean = clean[best_label]["clean"]["weighted"] - clean[start]["clean"]["weighted"]
        z_clean = d_clean / diff_se(clean[best_label]["clean"], clean[start]["clean"])
        d_all = clean[best_label]["all_fresh"]["weighted"] - clean[start]["all_fresh"]["weighted"]
        z_all = d_all / diff_se(clean[best_label]["all_fresh"], clean[start]["all_fresh"])
        lines.append(
            f"- {best_label} against the start list: clean seed {d_clean:+.2%} ({z_clean:+.1f} standard errors); "
            f"all three seeds {d_all:+.2%} ({z_all:+.1f} standard errors)."
        )
        if abs(fresh_z) < 2.0 and z_all < 2.0:
            verdict = (
                f"No Elekid count separates from the start list. On the two fresh seeds the highest is {best_label} "
                f"at {fresh_gap:+.2%} ({fresh_z:+.1f} standard errors). On the clean seed it is {d_clean:+.2%} "
                f"({z_clean:+.1f} standard errors), and on all three seeds {d_all:+.2%} ({z_all:+.1f}). "
                "The selection seed keeps the best of many cuts at every step, so its climb is biased upward. "
                "The start list, with no Elekid, stays the one to play."
            )
        else:
            verdict = (
                f"{best_label} is the best list on the two fresh seeds, and it is {relation(z_all)} the start list on all three seeds. "
                "The selection seed keeps the best of many cuts at every step, so its gains are biased upward and the fresh seeds decide."
            )
    else:
        verdict = "No Elekid count beats the start list on the two fresh seeds, so the start list stays the best found."
    if best_label != final_label:
        d_clean = clean[final_label]["clean"]["weighted"] - clean[best_label]["clean"]["weighted"]
        z_clean = d_clean / diff_se(clean[final_label]["clean"], clean[best_label]["clean"])
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
            (
                f"Highest list on the two fresh seeds ({best_label}). The clean seed was not used to pick it, "
                "and the paragraph above is what decides whether to play it:"
                if best_label != start and abs(fresh_z) < 2.0
                else f"Best list on the two fresh seeds ({best_label}); the clean seed above was not used to pick it:"
            ),
            "",
            "```",
        ]
    )
    lines.extend(f"{count} {name}" for name, count in sorted(Counter(best_row["list"]).items()))
    lines.extend(["```", ""])
    return lines


def usage_cells(use: dict[str, float]) -> str:
    return (
        f"{use['elekid_games']:.2f} | {use['elekid_own']:.2f} | {use['elekid_mew']:.2f} | "
        f"{use['snipe_ko']:.2f} | {use['snipe_ko_bench']:.2f} | {use['elekid_ko']:.2f} | "
        f"{use['boss_plays'] + use['catcher_plays']:.2f}"
    )


def render_md(rep: dict) -> str:
    weights = rep["weights"]
    path = rep["path"]
    start_row = path[0]
    lines = [
        "# Set M with Elekid",
        "",
        "Elekid (Paradox Rift 59) is a 30 HP Basic with Retreat Cost 0. Crackling Shot costs no Energy and does 30 damage to 1 of the "
        "opponent's Pokémon, with no Weakness or Resistance on the Bench. It is one more Benched body for Bouncy Circle. "
        "The attack is a finisher: it is used only when the Knock Out wins the game, or it takes at least 2 prizes the Active attack "
        "cannot take this turn. Mew ex copies it and stays Active. Elekid itself goes Active only when Mew ex cannot use the attack "
        "and that Knock Out is extreme. The play, written before the search, is in "
        "`set-m-elekid-strategy.md`; the engine paths are in `tests/test_mew_elekid.py`.",
        "",
        "Start list is the locked Set M: four Team Rocket's Petrel, one Junk Arm, three Sky Field, four Budew, "
        "no Ultra Ball, no Penny, no Boss's Orders. "
        f"Each step adds one more Elekid, forced up to {len(path) - 1} copies, and every other card name is tried as the cut. "
        "Every list on the path is then run on two fresh seeds and pooled, and the start list, the final list and the best "
        "fresh-seed list go to the clean seed.",
        "",
        f"- **Selection seed**: `{rep['seed']}`; cuts screened on {rep['screen_games']} games per foe, best {rep['screen_top']} confirmed on {rep['games']}",
        f"- **Fresh seeds**: `{rep['fresh1_seed']}` with {rep['fresh1_games']} per foe, `{rep['fresh2_seed']}` with {rep['fresh2_games']}",
        f"- **Clean seed**: `{rep['clean_seed']}` with {rep['clean_games']} per foe",
        "- **Score**: loss-weighted win rate, weights frozen from the locked list on the selection seed. Weights: "
        + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Elapsed**: {rep['elapsed']:.0f}s",
        "",
        "## Path (selection seed)",
        "",
        "| List | Cut | Weighted | ±1 SE | vs start | Mean | Worst | Elekid games | Elekid shots | Mew shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in path:
        cells = row["cells"]
        lines.append(
            f"| {row['label']} | {row['cut'] or '—'} | {pct(row['weighted'])} | {pct(row['se'])} | "
            f"{row['weighted'] - start_row['weighted']:+.1%} | {pct(row['mean'])} | {pct(row['worst'])} | "
            f"{usage_cells(row['usage'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
            f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    lines.extend(
        [
            "",
            "Elekid games is the share of games in which an Elekid itself used Crackling Shot. Elekid shots and Mew shots are "
            "per game, averaged over the six foes. Mew ex is the one that copies the shot when it can. Snipe KOs count every "
            "Crackling Shot that Knocked something Out; Bench KOs are the ones on a Benched Pokémon. Boss + Catcher is per game.",
        ]
    )
    for step in rep["steps"]:
        lines.extend(
            [
                "",
                f"## Step {step['step']}: {copies_label(step['step'])}, cut {step['cut']}",
                "",
                f"{step['gain']:+.2%} against the list before on the selection seed.",
                "",
                "Confirmed cuts:",
                "",
                "| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step["confirm"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | "
                f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | {cell(cells, 'c60')} | "
                f"{cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
            )
    fresh = rep["fresh"]
    base_pool = next(row for row in fresh if row["label"] == start_row["label"])["pooled"]
    lines.extend(
        [
            "",
            "## Fresh seeds",
            "",
            "No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.",
            "",
            "| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs start | ±1 SE of diff | Mean | Worst | Elekid games | Elekid shots | Mew shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in fresh:
        pooled = row["pooled"]
        cells = pooled["cells"]
        lines.append(
            f"| {row['label']} | {pct(row['seed1']['weighted'])} | {pct(row['seed2']['weighted'])} | {pct(pooled['weighted'])} | "
            f"{pct(pooled['se'])} | {pooled['weighted'] - base_pool['weighted']:+.1%} | {pct(diff_se(pooled, base_pool))} | "
            f"{pct(pooled['mean'])} | {pct(pooled['worst'])} | {usage_cells(pooled['usage'])} | "
            f"{cell(cells, 't60')} | {cell(cells, 'hedrick')} | "
            f"{cell(cells, 'c60')} | {cell(cells, 'd60')} | {cell(cells, 'thorns')} | {cell(cells, 'starmie')} |"
        )
    locked = rep["clean_rows"][0]
    lines.extend(
        [
            "",
            f"## Clean seed `{rep['clean_seed']}`",
            "",
            f"{rep['clean_games']} games per foe per list. The first row is the locked list. "
            "The last two columns merge this seed with both fresh seeds.",
            "",
            "| List | Weighted | ±1 SE | vs locked | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs locked |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rep["clean_rows"]:
        c = row["clean"]
        cells = c["cells"]
        lines.append(
            f"| {row['label']} | {pct(c['weighted'])} | {pct(c['se'])} | {c['weighted'] - locked['clean']['weighted']:+.2%} | "
            f"{pct(diff_se(c, locked['clean']))} | {pct(c['mean'])} | {pct(c['worst'])} | {cell(cells, 't60')} | "
            f"{cell(cells, 'hedrick')} | {cell(cells, 'c60')} | {cell(cells, 'd60')} | {cell(cells, 'thorns')} | "
            f"{cell(cells, 'starmie')} | {pct(row['all_fresh']['weighted'])} | "
            f"{row['all_fresh']['weighted'] - locked['all_fresh']['weighted']:+.2%} |"
        )
    lines.extend(["", "## Result", ""] + result_lines(rep))
    return "\n".join(lines)


if __name__ == "__main__":
    main()
