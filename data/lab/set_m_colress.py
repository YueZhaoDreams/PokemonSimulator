#!/usr/bin/env python3
"""Greedy Colress swaps on the locked Set M list.

Start from SET_M60_NAMES. Each step replaces exactly one copy of one other card
with one Colress. The decision score is the loss-weighted win rate. Weights are
frozen from that 0-Colress list. Stop when the next copy does not raise the
score, or at 4.

Plasma Storm 118 shuffles your hand into your deck, then draws a number of cards
equal to the number of Benched Pokémon (both yours and your opponent's).
Professor's Research discards the hand and draws 7. Sky Field lets each Bench
reach 8, and this list already fills its own Bench, so the draw is often near
that 7 without discarding the hand.

Every cut is screened on SCREEN_GAMES games per foe. The best SCREEN_TOP cuts
are confirmed on GAMES games per foe. The accepted lists are run again on a
fresh seed.

The locked 60 is the Elekid list plus one Colress: one Elekid, three Battle Cage,
one Colress, and two Crushing Hammer. data/lab/set-m-colress.json is the
pre-Elekid measurement and its list_start still has zero Colress. A fresh run
with no saved list puts that locked Colress back as Crushing Hammer, so the
search still starts from zero Colress. A later 6000-game retest on the Elekid
list was stopped during step 1 and did not choose this lock.
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

IN_NAME = "Colress"
GAMES = int(os.environ.get("M_COLRESS_GAMES", "1000"))
SCREEN_GAMES = int(os.environ.get("M_COLRESS_SCREEN_GAMES", "300"))
SCREEN_TOP = int(os.environ.get("M_COLRESS_SCREEN_TOP", "6"))
SEED = int(os.environ.get("M_COLRESS_SEED", "20261007"))
HOLDOUT_SEED = int(os.environ.get("M_COLRESS_HOLDOUT_SEED", "20261015"))
HOLDOUT_GAMES = int(os.environ.get("M_COLRESS_HOLDOUT_GAMES", "1000"))
WORKERS = int(os.environ.get("M_COLRESS_WORKERS", "4"))
MAX_COPIES = int(os.environ.get("M_COLRESS_MAX", "4"))
DEST = Path(os.environ.get("M_COLRESS_DEST", ROOT / "data/lab/set-m-colress.json"))
MD_DEST = DEST.with_suffix(".md")
CACHE_PATH = Path(os.environ.get("M_COLRESS_CACHE", ROOT / "data/cache/set-m-colress-cells.json"))

QUERIES = [
    {"type": "event_sum", "prefix": "shuffle_hand_draw_per_bench_a", "key": "plays"},
    {"type": "event_sum", "prefix": "colress_drawn_a", "key": "drawn"},
]


def loss_weights(rates: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - rates[key]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def list_key(names: list[str]) -> str:
    return ",".join(f"{name}x{count}" for name, count in sorted(Counter(names).items()))


def cell_key(names: list[str], games: int, foe_key: str, seed: int) -> str:
    return f"v1|seed{seed}|{games}|{foe_key}|{list_key(names)}"


def zero_colress_start() -> list[str]:
    """The 60 a fresh search adds Colress to.

    The live lock already has one Colress in place of one Crushing Hammer.
    Put that copy back so the search still starts at zero Colress.
    """
    names = list(SET_M60_NAMES)
    if names.count(IN_NAME) == 1 and names.count("Crushing Hammer") == 2:
        names[names.index(IN_NAME)] = "Crushing Hammer"
    if len(names) != 60 or names.count(IN_NAME) != 0 or names.count("Crushing Hammer") != 3:
        raise SystemExit("start list is not the 60-card list with zero Colress")
    return names


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Colress would exceed 4")
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
        deck_a_meta={"id": "m-colress", "name": "m-colress"},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    return foe_key, {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "games": games,
        "plays": result["queries"].get("plays", 0.0),
        "drawn": result["queries"].get("drawn", 0.0),
    }


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
    DEST.write_text(json.dumps({"report": report, "cells": cache.cells}, indent=1) + "\n")
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
                print(f"  [{label}] {done}/{total} {key} vs {foe_key} {detail['a']:.3f}", flush=True)
                if done % len(FOES) == 0 or done == total:
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


def per_play(cells: dict[str, dict]) -> float:
    plays = avg(cells, "plays")
    if plays <= 0:
        return 0.0
    return avg(cells, "drawn") / plays


def row_for(cut: str, names: list[str], cells: dict[str, dict], weights: dict[str, float], copies: Counter) -> dict:
    return {
        "cut": cut,
        "copies_before": copies[cut] if cut in copies else 0,
        "colress": names.count(IN_NAME),
        "list": names,
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "plays": avg(cells, "plays"),
        "drawn": per_play(cells),
        "cells": {
            key: {"a": cell["a"], "games": cell["games"], "plays": cell.get("plays", 0.0), "drawn": cell.get("drawn", 0.0)}
            for key, cell in cells.items()
        },
    }


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


def cell_pct(cells: dict, key: str) -> str:
    return pct(cells[key]["a"])


def result_lines(report: dict) -> list[str]:
    holdout = report.get("holdout") or []
    array = report.get("array") or []
    weights = report.get("weights") or {}
    if not report.get("done") or len(holdout) < 1 or len(array) < 1 or not weights:
        return []
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
    if len(holdout) >= 2:
        zero = holdout[0]
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
    kept = int(report.get("copies") or 0)
    by_copies = {row["copies"]: row for row in holdout}
    lines.extend(["", f"The selection seed kept {kept}."])
    if not kept:
        lines.append("No copy raised the score, so `SET_M60_NAMES` stays the starting 60.")
    else:
        cuts = [row["cut"] for row in array[1:]]
        lines.append("That path cuts " + ", then ".join(cuts) + ".")
        neighbor = []
        for left, right in ((2, 1), (3, 2), (3, 1), (4, 3), (4, 2), (4, 1)):
            if left in by_copies and right in by_copies and left <= kept:
                delta, _se, z = _pair(by_copies[left], by_copies[right], weights)
                neighbor.append(f"{left} against {right} is {delta:+.2%} ({z:.2f} standard errors)")
        if neighbor:
            lines.extend(["", "On the holdout, " + "; ".join(neighbor) + "."])
        first = ((report.get("steps") or [{}])[0]).get("screen") or []
        screen_bits = []
        for rank, row in enumerate(first, start=1):
            if row.get("cut") in ("Professor's Research", "Iono"):
                screen_bits.append(f"{row['cut']} is rank {rank} at {pct(row['weighted'])}")
        if screen_bits:
            lines.append("On the first screen, " + "; ".join(screen_bits) + ".")
        kept_row = next(row for row in array if row["copies"] == kept)
        lines.append(
            f"At {_copies(kept)} on the selection seed, Colress is played {kept_row['plays']:.2f} times a game "
            f"and draws {kept_row['drawn']:.1f} cards when it is played. "
            "The rest of the hand is shuffled into the deck. "
            "Professor's Research discards the hand and draws 7."
        )
        zero = holdout[0]
        hold_z = {row["copies"]: _pair(row, zero, weights) for row in holdout[1:]}
        above = [str(n) for n, (_delta, _se, z) in hold_z.items() if z >= 2]
        if above:
            lines.append(
                "Holdout counts at or above 2 standard errors against zero: " + ", ".join(above) + ". "
                "This note leaves `SET_M60_NAMES` unchanged."
            )
        else:
            kept_delta, _kept_se, kept_z = hold_z[kept]
            bits = [
                "No holdout count is 2 standard errors above zero copies.",
                f"{_copies(kept)} against zero is {kept_delta:+.2%} ({kept_z:.2f} standard errors).",
            ]
            one = hold_z.get(1)
            one_z = None
            if one is not None:
                one_delta, _one_se, one_z = one
                if one_z < 0:
                    bits.append(
                        f"{_copies(1)} is {one_delta:+.2%} ({one_z:.2f} standard errors), below the starting 60."
                    )
                else:
                    bits.append(
                        f"{_copies(1)} against zero is {one_delta:+.2%} ({one_z:.2f} standard errors)."
                    )
            bits.append("`SET_M60_NAMES` stays the starting 60.")
            lines.append(" ".join(bits))
            versus_one = []
            if one_z is not None and one_z < 0 and 1 in by_copies:
                for left in range(2, kept + 1):
                    if left in by_copies and _pair(by_copies[left], by_copies[1], weights)[2] >= 2:
                        versus_one.append(str(left))
            if versus_one:
                joined = " and ".join(versus_one)
                verb = "clears" if len(versus_one) == 1 else "clear"
                lines.append(
                    f"{joined} against 1 {verb} 2 standard errors. "
                    "That 1-copy list is below zero copies."
                )
    names = report.get("list") or []
    if names:
        lines.extend(["", "The list at the end of the search:", "", "```"])
        for name, count in sorted(Counter(names).items()):
            lines.append(f"{count} {name}")
        lines.extend(["```", ""])
    return lines


def render_md(report: dict) -> str:
    if not report:
        return "# Set M greedy Colress\n\nRunning.\n"
    weights = report.get("weights") or {}
    lines = [
        "# Set M greedy Colress",
        "",
        "Plasma Storm Colress shuffles your hand into your deck, then draws a number of cards equal to",
        "the number of Benched Pokémon (both yours and your opponent's).",
        "Professor's Research discards the hand and draws 7. The shuffled cards are not discarded.",
        "Sky Field lets each Bench reach 8, and this list already fills its Bench, so the draw is often",
        "near that 7 once both boards are out.",
        "",
        "Starting 60 is the locked Set M list (`SET_M60_NAMES`): three Sky Field, four Budew, one Junk Arm,",
        "two Professor's Research, four Iono, and zero Colress.",
        "Each step cuts exactly one copy of one other card. Weights are frozen from the 0-Colress list.",
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
        "| Colress | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    start_counts = Counter(report.get("list_start") or [])
    if start_counts.get("Elekid"):
        path_at = lines.index("## Path")
        lines[path_at:path_at] = [
            f"This pass starts from the Elekid lock: {start_counts['Elekid']} Elekid and {start_counts['Battle Cage']} Battle Cage.",
            "",
        ]
    games_n = int(report.get("games") or 0)
    screen_n = int(report.get("screen_games") or 0)
    if games_n >= 6000 and screen_n >= games_n:
        se_points = 0.59 * math.sqrt(1000 / games_n)
        path_at = lines.index("## Path")
        lines[path_at:path_at] = [
            "Every cut is scored on this same game count. "
            "The 1000-game difference had a standard error near 0.59 percentage points. "
            f"At {games_n} games that standard error is about {se_points:.2f} percentage points, "
            f"so a half-point gap sits at about {0.50 / se_points:.1f} standard errors.",
            "",
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
            f"{pct(row['mean'])} | {pct(row['worst'])} | {row.get('plays', 0):.2f} | {row.get('drawn', 0):.1f} | "
            + " | ".join(cell_pct(cells, key) for key, *_ in FOES)
            + " |"
        )
    for step in report.get("steps") or []:
        lines.extend(["", f"## Step {step['copies_after']}", ""])
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
                "| Rank | Cut | Weighted | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step.get("confirm") or [], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {pct(row['weighted'])} | {pct(row['mean'])} | {pct(row['worst'])} | "
                f"{row.get('plays', 0):.2f} | {row.get('drawn', 0):.1f} | "
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
                "| Colress | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
                "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        hold_base = holdout[0]
        for row in holdout:
            cells = row["cells"]
            delta = row["weighted"] - hold_base["weighted"]
            diff = "—" if row is hold_base else pct(diff_se(cells, hold_base["cells"], weights))
            lines.append(
                f"| {row['copies']} | {pct(row['weighted'])} | {pct(row['se'])} | {delta:+.2%} | {diff} | "
                f"{pct(row['mean'])} | {pct(row['worst'])} | {row.get('plays', 0):.2f} | {row.get('drawn', 0):.1f} | "
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
    out["cells"] = {
        key: {"a": cell["a"], "games": cell["games"], "plays": cell.get("plays", 0.0), "drawn": cell.get("drawn", 0.0)}
        for key, cell in row["cells"].items()
    }
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
    print(
        f"colress greedy games={GAMES} screen={SCREEN_GAMES} top={SCREEN_TOP} "
        f"holdout={HOLDOUT_GAMES} seed={SEED} holdout_seed={HOLDOUT_SEED} "
        f"workers={WORKERS} dest={DEST}",
        flush=True,
    )
    started = time.perf_counter()
    saved = json.loads(DEST.read_text()) if DEST.exists() else None
    report = (saved or {}).get("report") or {}
    if report.get("seed") not in (None, SEED) or report.get("games") not in (None, GAMES):
        report = {}
        saved = None
    start = list(report.get("list_start") or zero_colress_start())
    if report.get("list_start") not in (None, start):
        report = {}
        saved = None
        start = zero_colress_start()
    if len(start) != 60 or start.count(IN_NAME) != 0:
        raise SystemExit("start list is not the 60-card list with zero Colress")
    print(
        f"start elekid={start.count('Elekid')} "
        f"battle_cage={start.count('Battle Cage')} "
        f"colress={start.count(IN_NAME)} "
        f"hammer={start.count('Crushing Hammer')}",
        flush=True,
    )

    cache = Cache(saved if report else None)
    prior = float(report.get("elapsed") or 0) if report else 0.0

    def save() -> None:
        report["elapsed"] = prior + (time.perf_counter() - started)
        _save(cache, report)

    report.setdefault("list_start", start)
    report["seed"] = SEED
    report["games"] = GAMES
    report["screen_games"] = SCREEN_GAMES
    report["screen_top"] = SCREEN_TOP
    report["holdout_seed"] = HOLDOUT_SEED
    report["holdout_games"] = HOLDOUT_GAMES
    report["in"] = IN_NAME
    report["rule_preset"] = "s60"

    if not report.get("array"):
        print("baseline: locked Set M, zero Colress", flush=True)
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
                "plays": base_row["plays"],
                "drawn": base_row["drawn"],
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
    print(f"resume colress={current.count(IN_NAME)} steps={len(report.get('steps') or [])}", flush=True)

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
                    "plays": row["plays"],
                    "drawn": row["drawn"],
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
    if not report.get("holdout") and os.environ.get("M_COLRESS_SKIP_HOLDOUT") != "1":
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
                    "plays": packed["plays"],
                    "drawn": packed["drawn"],
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
