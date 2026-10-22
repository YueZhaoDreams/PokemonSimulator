#!/usr/bin/env python3
"""Greedy Team Rocket's Petrel swaps on the latest Set M.

Start from the fresh-seed best in set-m-gust-search: four Sky Field and four
Budew. Each step replaces exactly one copy of one other card with one Petrel.
The decision score is the loss-weighted win rate. Weights are frozen from that
0-Petrel list. Stop when the next copy does not raise the score, or at 4.

Petrel prints: search the deck for a Trainer, reveal it, put it into the hand,
then shuffle. On the Mew list that Trainer is played the same turn when it is
an Item, a Tool, or a Stadium, and held for the next turn when it is a Supporter.
The collapse follows the scores those cards already use: a Bench-raising Stadium
before Buddy-Buddy Poffin when its printed sentence adds a waiting 30 HP Basic,
Area Zero Underdepths when the burst is ready, Battle Cage on its own score,
Max Potion for a hurt Mew ex, Hero's Cape on an open Mew ex, Counter Catcher
for a bigger Knock Out, then the rest of the item line. Arven keeps an Item or
Tool it can fetch. Arven cannot fetch a Stadium. Boss's Orders keeps a gust
already in hand.

Every cut is screened on SCREEN_GAMES games per foe. The best SCREEN_TOP cuts
are confirmed on GAMES games per foe. The accepted lists are run again on a
fresh seed.
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

IN_NAME = "Team Rocket's Petrel"
GUST_REPORT = ROOT / "data/lab/set-m-gust-search.json"
GAMES = int(os.environ.get("M_PETREL_GAMES", "1000"))
SCREEN_GAMES = int(os.environ.get("M_PETREL_SCREEN_GAMES", "300"))
SCREEN_TOP = int(os.environ.get("M_PETREL_SCREEN_TOP", "6"))
SEED = int(os.environ.get("M_PETREL_SEED", "20261007"))
HOLDOUT_SEED = int(os.environ.get("M_PETREL_HOLDOUT_SEED", "20261015"))
HOLDOUT_GAMES = int(os.environ.get("M_PETREL_HOLDOUT_GAMES", "1000"))
WORKERS = int(os.environ.get("M_PETREL_WORKERS", "4"))
MAX_COPIES = int(os.environ.get("M_PETREL_MAX", "4"))
DEST = Path(os.environ.get("M_PETREL_DEST", ROOT / "data/lab/set-m-petrel.json"))
MD_DEST = DEST.with_suffix(".md")
CACHE_PATH = Path(os.environ.get("M_PETREL_CACHE", ROOT / "data/cache/set-m-petrel-cells.json"))

COLLAPSES = (
    ("poffin", "Buddy-Buddy Poffin"),
    ("potion", "Max Potion"),
    ("catcher", "Counter Catcher"),
    ("cape", "Hero's Cape"),
    ("charm", "Bravery Charm"),
    ("sky", "Sky Field"),
    ("area", "Area Zero Underdepths"),
    ("cage", "Battle Cage"),
    ("balloon", "Bursting Balloon"),
    ("carrier", "Rescue Carrier"),
    ("stretcher", "Night Stretcher"),
    ("nest", "Nest Ball"),
    ("boss", "Boss's Orders"),
    ("penny", "Penny"),
    ("arven", "Arven"),
    ("iono", "Iono"),
    ("research", "Professor's Research"),
)
QUERIES = [{"type": "event_prefix", "prefix": "petrel_into:", "key": "petrel"}]
QUERIES += [
    {"type": "event_prefix", "prefix": f"petrel_into:{name}", "key": key} for key, name in COLLAPSES
]
COLLAPSE_KEYS = ("petrel",) + tuple(key for key, _name in COLLAPSES)


def starting_list() -> tuple[str, list[str]]:
    """Fresh-seed best Set M. That list has four Sky Field and four Budew."""
    report = json.loads(GUST_REPORT.read_text())["report"]
    label = str(report["best_fresh_label"])
    names = next(list(row["list"]) for row in report["path"] if row.get("label") == label)
    if names != list(report["list_start"]):
        raise SystemExit("gust-search best fresh list is not list_start")
    if len(names) != 60:
        raise SystemExit(f"latest Set M has {len(names)} cards")
    if names.count("Sky Field") != 4 or names.count("Budew") != 4:
        raise SystemExit("latest Set M is not four Sky Field and four Budew")
    if names.count(IN_NAME):
        raise SystemExit("latest Set M already contains Petrel")
    return label, names


def loss_weights(rates: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - rates[key]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def list_key(names: list[str]) -> str:
    return ",".join(f"{name}x{count}" for name, count in sorted(Counter(names).items()))


def cell_key(names: list[str], games: int, foe_key: str, seed: int) -> str:
    return f"seed{seed}|{games}|{foe_key}|{list_key(names)}"


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Petrel would exceed 4")
    if out.count("Hero's Cape") > 1:
        raise ValueError("a second Hero's Cape is not legal")
    return out


def _run(names: list[str], games: int, foe_key: str, foe_names, foe_strat: str, seed: int) -> tuple[str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=seed,
        queries=QUERIES,
        deck_a_meta={"id": "m-petrel", "name": "m-petrel"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    detail = {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "games": games,
    }
    for key in COLLAPSE_KEYS:
        detail[key] = result["queries"].get(key, 0.0)
    return foe_key, detail


class Cache:
    def __init__(self, saved: dict | None):
        self.cells: dict[str, dict] = {}
        if CACHE_PATH.exists():
            self.cells.update(json.loads(CACHE_PATH.read_text()))
        self.cells.update((saved or {}).get("cells", {}))

    def get(self, names: list[str], games: int, foe_key: str, seed: int) -> dict | None:
        return self.cells.get(cell_key(names, games, foe_key, seed))

    def put(self, names: list[str], games: int, foe_key: str, detail: dict, seed: int) -> None:
        self.cells[cell_key(names, games, foe_key, seed)] = detail


def _save(cache: Cache, report: dict) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache.cells) + "\n")
    DEST.write_text(json.dumps({"report": report, "cells": {}}, indent=1) + "\n")
    MD_DEST.write_text(render_md(report))


def evaluate(
    lists: list[tuple[str, list[str]]],
    games: int,
    cache: Cache,
    save,
    label: str,
    seed: int,
) -> dict[str, dict[str, dict]]:
    jobs = [
        (key, names, foe_key, foe_names, foe_strat)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
        if cache.get(names, games, foe_key, seed) is None
    ]
    total = len(lists) * len(FOES)
    if jobs:
        with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
            futs = {
                pool.submit(_run, names, games, foe_key, foe_names, foe_strat, seed): (key, names)
                for key, names, foe_key, foe_names, foe_strat in jobs
            }
            done = total - len(jobs)
            for fut in as_completed(futs):
                key, names = futs[fut]
                foe_key, detail = fut.result()
                cache.put(names, games, foe_key, detail, seed)
                done += 1
                if done % len(FOES) == 0 or done == total:
                    print(f"  [{label}] {done}/{total} cells", flush=True)
                    save()
    out: dict[str, dict[str, dict]] = {}
    for key, names in lists:
        out[key] = {}
        for foe_key, *_ in FOES:
            cell = cache.get(names, games, foe_key, seed)
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


def diff_se(a: dict[str, dict], b: dict[str, dict], weights: dict[str, float]) -> float:
    var = 0.0
    for key, *_ in FOES:
        pa, na = a[key]["a"], a[key]["games"]
        pb, nb = b[key]["a"], b[key]["games"]
        var += (weights[key] ** 2) * (pa * (1.0 - pa) / na + pb * (1.0 - pb) / nb)
    return math.sqrt(var)


def avg(cells: dict[str, dict], field: str) -> float:
    return sum(cells[key][field] for key, *_ in FOES) / len(FOES)


def row_for(cut: str, names: list[str], cells: dict[str, dict], weights: dict[str, float], copies: Counter) -> dict:
    row = {
        "cut": cut,
        "copies_before": copies[cut] if cut in copies else 0,
        "petrel": names.count(IN_NAME),
        "list": names,
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "petrel_rate": avg(cells, "petrel"),
        "cells": {key: {"a": cell["a"], "games": cell["games"], **{k: cell.get(k, 0.0) for k in COLLAPSE_KEYS}} for key, cell in cells.items()},
    }
    for key, _name in COLLAPSES:
        row[key] = avg(cells, key)
    return row


def rank_key(row: dict):
    return (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"])


def pct(value: float) -> str:
    return f"{value:.1%}"


def _copies(n: int) -> str:
    return f"{n} copy" if n == 1 else f"{n} copies"


def _pair(later: dict, earlier: dict, weights: dict[str, float]) -> tuple[float, float, float]:
    delta = later["weighted"] - earlier["weighted"]
    se = diff_se(later["cells"], earlier["cells"], weights)
    return delta, se, (delta / se if se else 0.0)


def _hold_avg(holdout: list[dict], copies: int, field: str) -> float:
    row = next(item for item in holdout if item["copies"] == copies)
    cells = row["cells"].values()
    return sum(cell.get(field, 0.0) for cell in cells) / len(row["cells"])


def result_lines(report: dict) -> list[str]:
    """Holdout standard errors for the finished search. Under 2 does not separate two lists."""
    holdout = report.get("holdout") or []
    array = report.get("array") or []
    weights = report.get("weights") or {}
    if not report.get("done") or len(holdout) < 2 or len(array) < 2 or not weights:
        return []
    by_copies = {row["copies"]: row for row in holdout}
    zero = holdout[0]
    lines = [
        "",
        "## Result",
        "",
        "The selection seed keeps a copy when the loss-weighted rate rises. It picks the best of many cuts, "
        "so that gain is biased upward. The holdout seed is the one no list was chosen on. "
        "A difference under 2 standard errors does not separate two lists.",
        "",
    ]
    for prev, row in zip(array, array[1:]):
        delta, _se, z = _pair(row, prev, weights)
        lines.append(
            f"- {_copies(row['copies'])}, cut {row['cut']}: {pct(row['weighted'])} "
            f"({delta:+.2%} against the previous list, {z:.2f} standard errors)."
        )
    steps = report.get("steps") or []
    if steps and steps[-1].get("screen") and steps[-1].get("confirm"):
        screen = steps[-1]["screen"][0]
        confirm = steps[-1]["confirm"]
        second = f" and {confirm[1]['cut']} second at {pct(confirm[1]['weighted'])}" if len(confirm) > 1 else ""
        lines.extend(
            [
                "",
                f"The last copy's {report.get('screen_games')}-game screen ranks {screen['cut']} first "
                f"at {pct(screen['weighted'])}. The {report.get('games')}-game confirm ranks "
                f"{confirm[0]['cut']} first at {pct(confirm[0]['weighted'])}{second}.",
            ]
        )
    lines.extend(
        [
            "",
            f"Holdout seed `{report.get('holdout_seed')}`, {report.get('holdout_games')} games per foe, "
            "same weights. Unpaired difference against zero copies:",
            "",
        ]
    )
    for row in holdout[1:]:
        delta, se, z = _pair(row, zero, weights)
        lines.append(
            f"- {_copies(row['copies'])}: {delta:+.2%} ({z:.2f} standard errors, "
            f"±1 SE of the difference {pct(se)})."
        )
    neighbor = []
    kept = int(report.get("copies") or 0)
    for left, right in ((2, 1), (3, 2), (4, 3), (4, 2)):
        if left in by_copies and right in by_copies and left <= kept:
            delta, _se, z = _pair(by_copies[left], by_copies[right], weights)
            neighbor.append(f"{left} against {right} is {delta:+.2%} ({z:.2f} standard errors)")
    if neighbor:
        lines.extend(["", "On the same seed, " + "; ".join(neighbor) + "."])
    one = by_copies.get(1)
    four = by_copies.get(kept)
    if one is not None and four is not None and 1 in {row["copies"] for row in array}:
        sel_one = next(row for row in array if row["copies"] == 1)
        sel_kept = next(row for row in array if row["copies"] == kept)
        lines.extend(
            [
                "",
                "Sky Field is fetched. On the selection seed it is "
                f"{sel_one['sky']:.3f} finds per game at {_copies(1)}, with four Sky Field still in the deck, "
                f"and {sel_kept['sky']:.3f} finds per game at {_copies(kept)}"
                + (f", with {sel_kept['list'].count('Sky Field')} Sky Field left" if sel_kept.get("list") else "")
                + ". On the holdout those rates are "
                f"{_hold_avg(holdout, 1, 'sky'):.3f} and {_hold_avg(holdout, kept, 'sky'):.3f}. "
                f"At {_copies(kept)} on the selection seed the other finds per game are "
                f"Buddy-Buddy Poffin {sel_kept['poffin']:.3f}, Hero's Cape {sel_kept['cape']:.3f}, "
                f"Battle Cage {sel_kept['cage']:.3f}, Max Potion {sel_kept['potion']:.3f}. "
                f"Area Zero Underdepths is {sel_kept['area']:.3f}.",
            ]
        )
    above = [str(row["copies"]) for row in holdout[1:] if _pair(row, zero, weights)[2] >= 2]
    under = [str(row["copies"]) for row in holdout[1:] if _pair(row, zero, weights)[2] < 2]
    lines.extend(
        [
            "",
            "`SET_M60_NAMES` stays the earlier lock. This report's starting 60 is the fresh-seed best "
            "of `set-m-gust-search`, four Sky Field and four Budew.",
            "",
            "Copies at or above 2 standard errors against zero: "
            + (", ".join(above) if above else "none")
            + ". Copies under 2 standard errors against zero: "
            + (", ".join(under) if under else "none")
            + f". The search kept {kept}.",
        ]
    )
    if kept in by_copies and kept - 1 in by_copies:
        _delta, _se, z_step = _pair(by_copies[kept], by_copies[kept - 1], weights)
        cut = next(row["cut"] for row in array if row["copies"] == kept)
        lines.append(
            f"{_copies(kept)} against {_copies(kept - 1)} is {z_step:.2f} standard errors, "
            f"and that step cuts {cut}."
        )
    names = report.get("list") or []
    if names:
        lines.extend(["", "The list the search kept:", "", "```"])
        for name, count in sorted(Counter(names).items()):
            lines.append(f"{count} {name}")
        lines.extend(["```", ""])
    return lines


def cell_pct(cells: dict, key: str) -> str:
    return pct(cells[key]["a"])


def render_md(report: dict) -> str:
    if not report:
        return "# Set M greedy Petrel\n\nRunning.\n"
    weights = report.get("weights") or {}
    lines = [
        "# Set M greedy Team Rocket's Petrel",
        "",
        "Petrel searches the deck for any Trainer. On this list the found Item, Tool, or Stadium",
        "is played the same turn, and a Supporter is held for the next turn. The collapse uses",
        "the scores those cards already have. Sky Field, and any Stadium whose printed sentence",
        "raises the Bench, is taken before Buddy-Buddy Poffin when that sentence adds a waiting",
        "30 HP Basic. Area Zero Underdepths is taken when a Tera Pokémon is in play and the burst",
        "is ready. Battle Cage uses its own score. Then Max Potion, Hero's Cape, Counter Catcher,",
        "Buddy-Buddy Poffin, Rescue Carrier, Bursting Balloon, Night Stretcher, and Nest Ball.",
        "Boss's Orders is the next-turn Supporter when Catcher cannot be played. Penny is next",
        "when Manaphy is Active. Arven is played instead when it can fetch that Item or Tool",
        "and a second card. Arven cannot fetch a Stadium, so Petrel still takes that Stadium.",
        "Boss's Orders is played instead when the gust is already in hand.",
        "",
        f"Starting 60 is the fresh-seed best from `set-m-gust-search`: {report.get('start_label')}.",
        f"That list has four Sky Field, four Budew, and zero {IN_NAME}.",
        "An earlier pass measured `SET_M60_NAMES`, which has zero Sky Field. Those numbers are withdrawn.",
        "Each step cuts exactly one copy of one other card. Weights are frozen from the",
        "0-Petrel measurement of this list on this engine.",
        "",
        f"- **Seed**: `{report.get('seed')}`",
        f"- **Games**: cuts screened on {report.get('screen_games')} per foe, best {report.get('screen_top')} confirmed on {report.get('games')} per foe",
        "- **Score**: loss-weighted win rate. A copy is kept only when that score rises.",
        "- **Weights**: " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES if key in weights),
        f"- **Copies kept**: {report.get('copies')}",
        f"- **Elapsed**: {report.get('elapsed', 0):.0f}s",
        "",
        "## Path",
        "",
        "| Petrel | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Poffin | Potion | Catcher | Cape | Boss | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    base = (report.get("array") or [{}])[0]
    base_w = base.get("weighted", 0.0)
    base_cells = base.get("cells") or {}
    for row in report.get("array") or []:
        cells = row.get("cells") or {}
        delta = row["weighted"] - base_w
        if row["copies"] == 0 or not base_cells or not cells:
            diff = "—"
        else:
            diff = pct(diff_se(cells, base_cells, weights))
        cut = row.get("cut") or "—"
        lines.append(
            f"| {row['copies']} | {cut} | {pct(row['weighted'])} | {pct(row['se'])} | {delta:+.2%} | {diff} | "
            f"{pct(row['mean'])} | {pct(row['worst'])} | {pct(row.get('poffin', 0))} | {pct(row.get('potion', 0))} | "
            f"{pct(row.get('catcher', 0))} | {pct(row.get('cape', 0))} | {pct(row.get('boss', 0))} | "
            + " | ".join(cell_pct(cells, key) for key, *_ in FOES)
            + " |"
        )
    for step in report.get("steps") or []:
        title = f"Step {step['copies_after']}"
        lines.extend(["", f"## {title}", ""])
        if step["accepted"]:
            lines.append(
                f"Current weighted rate {pct(step['current_weighted'])}. Accepted cut is {step['chosen']} "
                f"at {pct(step['chosen_weighted'])}."
            )
        else:
            lines.append(
                f"Current weighted rate {pct(step['current_weighted'])}. Best cut {step['chosen']} "
                f"at {pct(step['chosen_weighted'])} does not rise. Stop."
            )
        lines.extend(
            [
                "",
                "### Confirmed",
                "",
                "| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step.get("confirm") or [], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | {pct(row['worst'])} | "
                f"{pct(row.get('petrel_rate', 0))} | "
                + " | ".join(cell_pct(cells, key) for key, *_ in FOES)
                + " |"
            )
        lines.extend(
            [
                "",
                "### Screen",
                "",
                "| Rank | Cut | Weighted | Mean | Worst |",
                "| ---: | :--- | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step.get("screen") or [], start=1):
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | {pct(row['worst'])} |"
            )
    holdout = report.get("holdout") or []
    if holdout:
        lines.extend(
            [
                "",
                "## Holdout",
                "",
                f"The same lists on seed `{report.get('holdout_seed')}`, {report.get('holdout_games')} games per foe. "
                "Nothing was chosen on this seed. Weights are unchanged.",
                "",
                "| Petrel | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        hold_base = holdout[0]
        for row in holdout:
            cells = row["cells"]
            delta = row["weighted"] - hold_base["weighted"]
            diff = "—" if row is hold_base else pct(diff_se(cells, hold_base["cells"], weights))
            lines.append(
                f"| {row['copies']} | {pct(row['weighted'])} | {pct(row['se'])} | {delta:+.2%} | {diff} | "
                f"{pct(row['mean'])} | {pct(row['worst'])} | "
                + " | ".join(cell_pct(cells, key) for key, *_ in FOES)
                + " |"
            )
    if report.get("stopped"):
        lines.extend(["", report["stopped"], ""])
    lines.extend(result_lines(report))
    lines.append("")
    return "\n".join(lines)


def slim(row: dict) -> dict:
    out = dict(row)
    out["cells"] = {key: {"a": cell["a"]} for key, cell in row["cells"].items()}
    out.pop("list", None)
    return out


def greedy_step(current: list[str], weights: dict[str, float], cache: Cache, save, step_no: int) -> dict:
    copies = Counter(current)
    cuts = sorted(name for name in copies if name != IN_NAME)
    screen_lists = [(cut, swap_one(current, cut)) for cut in cuts]
    screened = evaluate(screen_lists, SCREEN_GAMES, cache, save, f"step {step_no} screen", SEED)
    screen_rows = sorted(
        (row_for(cut, dict(screen_lists)[cut], screened[cut], weights, copies) for cut in cuts),
        key=rank_key,
    )
    finalists = [row["cut"] for row in screen_rows[:SCREEN_TOP]]
    confirm_lists = [(cut, dict(screen_lists)[cut]) for cut in finalists]
    confirmed = evaluate(confirm_lists, GAMES, cache, save, f"step {step_no} confirm", SEED)
    confirm_rows = sorted(
        (row_for(cut, dict(screen_lists)[cut], confirmed[cut], weights, copies) for cut in finalists),
        key=rank_key,
    )
    chosen = confirm_rows[0]
    return {
        "copies_after": current.count(IN_NAME) + 1,
        "current_weighted": None,
        "chosen": chosen["cut"],
        "chosen_weighted": chosen["weighted"],
        "list": chosen["list"],
        "row": chosen,
        "accepted": False,
        "screen": [slim(row) for row in screen_rows],
        "confirm": [slim(row) for row in confirm_rows],
    }


def main() -> None:
    started = time.perf_counter()
    start_label, start = starting_list()

    saved = json.loads(DEST.read_text()) if DEST.exists() else None
    report = (saved or {}).get("report") or {}
    if report.get("seed") not in (None, SEED) or report.get("games") not in (None, GAMES):
        report = {}
        saved = None
    if report.get("list_start") not in (None, start):
        report = {}
    cache = Cache(saved)
    prior = float(report.get("elapsed") or 0)

    def save() -> None:
        report["elapsed"] = prior + (time.perf_counter() - started)
        _save(cache, report)

    report.setdefault("list_start", start)
    report["start_label"] = start_label
    report["seed"] = SEED
    report["games"] = GAMES
    report["screen_games"] = SCREEN_GAMES
    report["screen_top"] = SCREEN_TOP
    report["holdout_seed"] = HOLDOUT_SEED
    report["holdout_games"] = HOLDOUT_GAMES
    report["in"] = IN_NAME

    if not report.get("array"):
        print(f"baseline: {start_label}", flush=True)
        base_cells = evaluate([("base", start)], GAMES, cache, save, "baseline", SEED)["base"]
        rates = {key: base_cells[key]["a"] for key, *_ in FOES}
        weights = loss_weights(rates)
        base_row = row_for("—", start, base_cells, weights, Counter())
        report["weights"] = weights
        report["rates"] = rates
        report["array"] = [
            {
                "copies": 0,
                "cut": None,
                "cuts": [],
                "weighted": base_row["weighted"],
                "se": base_row["se"],
                "mean": base_row["mean"],
                "worst": base_row["worst"],
                "petrel_rate": base_row["petrel_rate"],
                **{key: base_row[key] for key, _name in COLLAPSES},
                "cells": base_row["cells"],
                "list": start,
            }
        ]
        report["steps"] = []
        report["current"] = start
        save()
        print(
            f"baseline weighted {base_row['weighted']:.2%} mean {base_row['mean']:.2%}  "
            + ", ".join(f"{key} {rates[key]:.1%}" for key, *_ in FOES),
            flush=True,
        )
    weights = report["weights"]
    current = list(report.get("current") or start)
    print(
        f"resume petrel={current.count(IN_NAME)} steps={len(report.get('steps') or [])}",
        flush=True,
    )

    while current.count(IN_NAME) < MAX_COPIES:
        done_steps = report.get("steps") or []
        if done_steps and not done_steps[-1]["accepted"]:
            break
        step_no = current.count(IN_NAME) + 1
        if len(done_steps) >= step_no and done_steps[step_no - 1].get("list"):
            current = list(done_steps[step_no - 1]["list"])
            continue
        print(f"step {step_no}: add {IN_NAME}", flush=True)
        step = greedy_step(current, weights, cache, save, step_no)
        current_weighted = report["array"][-1]["weighted"]
        step["current_weighted"] = current_weighted
        step["accepted"] = step["chosen_weighted"] > current_weighted
        report.setdefault("steps", []).append({k: v for k, v in step.items() if k != "row"})
        if step["accepted"]:
            current = list(step["list"])
            row = step["row"]
            report["array"].append(
                {
                    "copies": current.count(IN_NAME),
                    "cut": step["chosen"],
                    "cuts": report["array"][-1]["cuts"] + [step["chosen"]],
                    "weighted": row["weighted"],
                    "se": row["se"],
                    "mean": row["mean"],
                    "worst": row["worst"],
                    "petrel_rate": row["petrel_rate"],
                    **{key: row[key] for key, _name in COLLAPSES},
                    "cells": row["cells"],
                    "list": current,
                }
            )
            report["current"] = current
            print(
                f"  keep {current.count(IN_NAME)} by cutting {step['chosen']}: "
                f"{current_weighted:.2%} -> {row['weighted']:.2%}",
                flush=True,
            )
        else:
            report["stopped"] = (
                f"Stopped at {current.count(IN_NAME)}. "
                f"The next copy, cutting {step['chosen']}, is {step['chosen_weighted']:.2%} "
                f"against {current_weighted:.2%}."
            )
            report["current"] = current
            print(report["stopped"], flush=True)
        save()

    report["copies"] = current.count(IN_NAME)
    report["list"] = current
    if not report.get("holdout") and os.environ.get("M_PETREL_SKIP_HOLDOUT") != "1":
        print("holdout", flush=True)
        labels = [(f"{row['copies']}", row["list"]) for row in report["array"]]
        held = evaluate(labels, HOLDOUT_GAMES, cache, save, "holdout", HOLDOUT_SEED)
        holdout = []
        for row, (label, names) in zip(report["array"], labels):
            packed = row_for(label, names, held[label], weights, Counter(names))
            holdout.append(
                {
                    "copies": row["copies"],
                    "cut": row.get("cut"),
                    "weighted": packed["weighted"],
                    "se": packed["se"],
                    "mean": packed["mean"],
                    "worst": packed["worst"],
                    "cells": packed["cells"],
                }
            )
        report["holdout"] = holdout
    report["done"] = True
    report["copies"] = current.count(IN_NAME)
    save()
    print(render_md(report), flush=True)


if __name__ == "__main__":
    main()
