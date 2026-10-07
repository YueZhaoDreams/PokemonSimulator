#!/usr/bin/env python3
"""Greedy Eco Arm swaps on the locked two Rescue Carrier Set M.

Start from SET_M60_NAMES: one Manaphy, two Rescue Carrier, two Spiky Energy,
three Max Potion, one Boss's Orders, no Eco Arm. Each step replaces exactly
one copy of one other card with one Eco Arm. The decision score is the
loss-weighted win rate. Weights are frozen from that starting list, including
Kudo's Mega Starmie. Stop when the next copy does not raise the score, or at 4.

Ancient Origins Eco Arm: shuffle 3 Pokémon Tool cards from the discard pile
into the deck. The sentence does not say "up to", so fewer than 3 Tools cannot
play it. Set M recovers Hero's Cape first, then Bursting Balloon, then Bravery
Charm. Battle Cage is a Stadium and is not a Tool.

The 0-copy cells are the locked two-carrier list from seed 20261007, 1000 games:
data/lab/set-m-rescue-carrier.json, copies 2. An earlier search used the
pre-carrier Manaphy 60 and is kept in data/lab/set-m-eco-arm.json.
"""

from __future__ import annotations

import json
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

CARRIER_REPORT = ROOT / "data/lab/set-m-rescue-carrier.json"

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom"),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom"),
    ("c60", "Clefable/Mewtwo ex (C60)", SET_C60_NAMES, "party"),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish"),
    ("thorns", "Iron Thorns ex (Crushing Thorn)", IRON_THORNS_NAMES, "thorns"),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie"),
)

GAMES = int(os.environ.get("M_ECO_GAMES", "1000"))
SEED = int(os.environ.get("M_ECO_SEED", "20261007"))
WORKERS = int(os.environ.get("M_ECO_WORKERS", "4"))
IN_NAME = "Eco Arm"
DEST = ROOT / "data/lab/set-m-eco-arm-on-carrier.json"
MD_DEST = ROOT / "data/lab/set-m-eco-arm-on-carrier.md"

QUERIES = [
    {"type": "event_prefix", "prefix": "eco_arm_a", "key": "eco_arm"},
    {"type": "event_prefix", "prefix": "eco_arm_cape", "key": "cape"},
    {"type": "event_prefix", "prefix": "eco_arm_balloon", "key": "balloon"},
    {"type": "event_prefix", "prefix": "eco_arm_charm", "key": "charm"},
]


def loss_weights(rates: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - rates[key]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def _starting_list() -> list[str]:
    names = list(SET_M60_NAMES)
    counts = Counter(names)
    if len(names) != 60:
        raise SystemExit(f"SET_M60_NAMES has {len(names)} cards")
    expected = {
        "Manaphy": 1,
        "Budew": 0,
        "Eco Arm": 0,
        "Rescue Carrier": 2,
        "Spiky Energy": 2,
        "Max Potion": 3,
        "Boss's Orders": 1,
    }
    for name, count in expected.items():
        if counts[name] != count:
            raise SystemExit(f"SET_M60_NAMES has {counts[name]} {name}, expected {count}")
    return names


def _baseline_rates() -> dict[str, float]:
    data = json.loads(CARRIER_REPORT.read_text())
    if data.get("games") != 1000 or data.get("seed") != 20261007:
        raise SystemExit("Rescue Carrier report is not the seed 20261007, 1000-game table")
    row = next(item for item in data["array"] if item.get("copies") == 2)
    if Counter(row["list"]) != Counter(SET_M60_NAMES):
        raise SystemExit("SET_M60_NAMES does not match the published two-carrier list")
    return {key: row["cells"][key]["a"] for key, *_ in FOES}


def swap_one(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    if len(out) != 60:
        raise ValueError(f"{cut} swap is {len(out)} cards")
    if out.count(IN_NAME) > 4:
        raise ValueError("Eco Arm would exceed 4")
    if out.count("Hero's Cape") > 1:
        raise ValueError("a second Hero's Cape is not legal")
    return out


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["a"] for key, *_ in FOES) / len(FOES)


def _weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["a"] * weights[key] for key, *_ in FOES)


def _worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["a"] for key, *_ in FOES)


def _run(cut: str, names: list[str], foe_key: str, foe_names, foe_strat: str) -> tuple[str, str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(foe_strat),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": cut, "name": cut},
        deck_b_meta={"id": foe_key, "name": foe_key},
    )
    result = rec["results"]
    return cut, foe_key, {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "eco_arm": result["queries"].get("eco_arm", 0.0),
        "cape": result["queries"].get("cape", 0.0),
        "balloon": result["queries"].get("balloon", 0.0),
        "charm": result["queries"].get("charm", 0.0),
    }


def _eval_lists(lists: list[tuple[str, list[str]]], done: dict[str, dict[str, dict]], save) -> dict[str, dict[str, dict]]:
    cells: dict[str, dict[str, dict]] = {key: dict(done.get(key, {})) for key, _ in lists}
    jobs = [
        (key, names, foe_key, foe_names, foe_strat)
        for key, names in lists
        for foe_key, _label, foe_names, foe_strat in FOES
        if foe_key not in cells[key]
    ]
    if not jobs:
        return cells
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        finished = len(lists) * len(FOES) - len(jobs)
        for fut in as_completed(futs):
            key, foe_key, detail = fut.result()
            cells[key][foe_key] = detail
            finished += 1
            save(cells)
            print(
                f"  {key} vs {foe_key}: {detail['a']:.1%}  "
                f"arm {detail['eco_arm']:.1%} cape {detail['cape']:.1%} "
                f"balloon {detail['balloon']:.1%} charm {detail['charm']:.1%}  "
                f"({finished}/{len(lists) * len(FOES)})",
                flush=True,
            )
    for key, _ in lists:
        for foe_key, *_ in FOES:
            if foe_key not in cells[key]:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
    return cells


def _avg(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] for foe, *_ in FOES) / len(FOES)


def _candidate_row(cut: str, cells: dict[str, dict], copies: Counter, weights: dict[str, float]) -> dict:
    ordered = {key: cells[key] for key, *_ in FOES}
    return {
        "cut": cut,
        "copies_before": copies[cut],
        "weighted": _weighted(ordered, weights),
        "mean": _mean(ordered),
        "worst": _worst(ordered),
        "eco_arm": _avg(ordered, "eco_arm"),
        "cape": _avg(ordered, "cape"),
        "balloon": _avg(ordered, "balloon"),
        "charm": _avg(ordered, "charm"),
        "cells": ordered,
    }


def _better(a: dict, b: dict) -> bool:
    if a["weighted"] != b["weighted"]:
        return a["weighted"] > b["weighted"]
    if a["worst"] != b["worst"]:
        return a["worst"] > b["worst"]
    if a["copies_before"] != b["copies_before"]:
        return a["copies_before"] > b["copies_before"]
    return a["cut"] < b["cut"]


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _cell(cells: dict, key: str) -> str:
    return _pct(cells[key]["a"])


def _render_md(report: dict) -> str:
    weights = report["weights"]
    lines = [
        "# Set M greedy Eco Arm on the two Rescue Carrier list",
        "",
        "Starting 60 is the locked Set M list: two Rescue Carrier, two Spiky Energy, three Max Potion, one Boss's Orders.",
        "Ancient Origins Eco Arm shuffles 3 Pokémon Tool cards from the discard pile into the deck.",
        "The sentence does not say \"up to\", so the Item stays in hand when fewer than 3 Tools are in the discard.",
        "Set M recovers Hero's Cape first, then Bursting Balloon, then Bravery Charm.",
        "Battle Cage is a Stadium. It is not a Tool, and Eco Arm leaves it in the discard.",
        "Arven can search the Tools again after they return to the deck.",
        "The earlier table in `data/lab/set-m-eco-arm.md` searched the pre-carrier Manaphy 60.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per new cell**: {report['games']}",
        "- **Score**: loss-weighted win rate. Weights are frozen from the 0-copy list.",
        "- **0-copy cells**: reused from the locked two Rescue Carrier list, seed 20261007, 1000 games.",
        "- **Weights**: "
        + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES),
        f"- **Copies**: {report['copies']}",
        f"- **Cuts**: {', '.join(report['cuts']) or '(none)'}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "| Eco Arm | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |",
        "| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["array"]:
        cut = row["cut"] or "—"
        cells = row["cells"]
        lines.append(
            f"| {row['copies']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | {cut} | "
            f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | "
            f"{_cell(cells, 'd60')} | {_cell(cells, 'thorns')} | {_cell(cells, 'starmie')} |"
        )
    for step in report["steps"]:
        lines.extend(
            [
                "",
                f"## Step {step['copies_after']}, every cut",
                "",
                f"Current weighted rate {_pct(step['current_weighted'])}. "
                + (
                    f"Accepted cut is {step['chosen']}."
                    if step["accepted"]
                    else f"Best cut is not taken: {step['chosen']}."
                ),
                "",
                "| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Eco Arm | Cape | Balloon | Charm |",
                "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(step["candidates"], start=1):
            cells = row["cells"]
            lines.append(
                f"| {rank} | {row['cut']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | "
                f"{_cell(cells, 't60')} | {_cell(cells, 'hedrick')} | {_cell(cells, 'c60')} | "
                f"{_cell(cells, 'd60')} | {_cell(cells, 'thorns')} | {_cell(cells, 'starmie')} | "
                f"{_pct(row['eco_arm'])} | {_pct(row['cape'])} | {_pct(row['balloon'])} | {_pct(row['charm'])} |"
            )
    if report.get("note"):
        lines.extend(["", report["note"]])
    lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_render_md(report))


def _baseline_cells(rates: dict[str, float]) -> dict[str, dict]:
    return {
        key: {"a": rates[key], "eco_arm": 0.0, "cape": 0.0, "balloon": 0.0, "charm": 0.0}
        for key, *_ in FOES
    }


def _load() -> dict | None:
    if not DEST.exists():
        return None
    data = json.loads(DEST.read_text())
    if data.get("games") != GAMES or data.get("seed") != SEED:
        return None
    return data


def main() -> None:
    started = time.perf_counter()
    start = _starting_list()
    current = list(start)
    rates = _baseline_rates()
    weights = loss_weights(rates)
    base_cells = _baseline_cells(rates)
    base_weighted = _weighted(base_cells, weights)
    saved = _load()
    if saved and saved.get("list_start") == start:
        array = saved["array"]
        steps = saved["steps"]
        pending = saved.get("pending") or {}
        current = list(saved["list"])
        print(f"resume copies={current.count(IN_NAME)} steps={len(steps)}", flush=True)
    else:
        array = [
            {
                "copies": 0,
                "cut": None,
                "cuts": [],
                "list": current,
                "weighted": base_weighted,
                "mean": _mean(base_cells),
                "worst": _worst(base_cells),
                "cells": base_cells,
            }
        ]
        steps = []
        pending = {}
    print(
        f"baseline weighted {base_weighted:.2%}  "
        f"rates {', '.join(f'{k} {rates[k]:.1%}' for k, *_ in FOES)}",
        flush=True,
    )
    print(
        "weights " + ", ".join(f"{k} {weights[k]:.1%}" for k, *_ in FOES),
        flush=True,
    )

    def report_from(done: bool, rejected, pending_cells) -> dict:
        return {
            "games": GAMES,
            "seed": SEED,
            "elapsed": time.perf_counter() - started + float((saved or {}).get("elapsed") or 0),
            "rule_preset": "s60",
            "method": (
                "greedy one-card Eco Arm swap from the locked two Rescue Carrier Set M; "
                "printed effect shuffles 3 Pokémon Tools from discard into the deck; "
                "recovery order is Hero's Cape, Bursting Balloon, Bravery Charm; "
                "foes are T60, Hedrick, C60, D60, Crushing Thorn, and Kudo Mega Starmie; "
                "score is the loss-weighted win rate with weights frozen from the 0-copy list; "
                "stop when that score does not rise, or at 4 copies"
            ),
            "foes": {key: strat for key, _label, _names, strat in FOES},
            "weights": weights,
            "baseline_rates": rates,
            "copies": current.count(IN_NAME),
            "cuts": [row["cut"] for row in array[1:]],
            "win_rate_array": [row["weighted"] for row in array],
            "array": array,
            "steps": steps,
            "rejected": rejected,
            "list_start": start,
            "list": current,
            "pending": pending_cells,
            "done": done,
            "note": None,
        }

    rejected = (saved or {}).get("rejected")
    if (saved or {}).get("done"):
        print("already done")
        print(f"copies {(saved or {})['copies']} cuts {(saved or {})['cuts']}")
        return

    while current.count(IN_NAME) < 4:
        copies = Counter(current)
        cuts = sorted(name for name in copies if name != IN_NAME)
        lists = [(cut, swap_one(current, cut)) for cut in cuts]
        step_key = f"{current.count(IN_NAME) + 1}:" + ",".join(cuts)
        done_cells = pending.get("cells") or {} if pending.get("key") == step_key else {}
        print(f"\nstep {current.count(IN_NAME) + 1}: {len(lists)} cuts, {len(done_cells)} already stored", flush=True)

        def save(cells: dict) -> None:
            pending_now = {"key": step_key, "cells": cells}
            _write(report_from(False, rejected, pending_now))

        cells = _eval_lists(lists, done_cells, save)
        rows = [_candidate_row(cut, cells[cut], copies, weights) for cut, _ in lists]
        best = rows[0]
        for row in rows[1:]:
            if _better(row, best):
                best = row
        rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"]))
        accepted = best["weighted"] > array[-1]["weighted"]
        step = {
            "copies_after": current.count(IN_NAME) + 1,
            "current_weighted": array[-1]["weighted"],
            "current_mean": array[-1]["mean"],
            "accepted": accepted,
            "chosen": best["cut"],
            "chosen_weighted": best["weighted"],
            "chosen_mean": best["mean"],
            "candidates": rows,
        }
        steps.append(step)
        pending = {}
        print(
            f"best cut {best['cut']} -> weighted {best['weighted']:.2%} "
            f"(mean {best['mean']:.1%}, arm {best['eco_arm']:.1%}, "
            f"cape {best['cape']:.1%}, balloon {best['balloon']:.1%}, charm {best['charm']:.1%}) "
            f"({'keep' if accepted else 'stop'})",
            flush=True,
        )
        if not accepted:
            rejected = {
                "cut": best["cut"],
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "eco_arm": best["eco_arm"],
                "cape": best["cape"],
                "balloon": best["balloon"],
                "charm": best["charm"],
                "cells": best["cells"],
                "candidates": rows,
            }
            report = report_from(True, rejected, {})
            report["note"] = (
                f"Stopped at {current.count(IN_NAME)} Eco Arm. "
                f"The next copy, cutting {best['cut']}, is {best['weighted']:.2%} "
                f"against the current {array[-1]['weighted']:.2%}."
            )
            _write(report)
            break
        current = swap_one(current, best["cut"])
        array.append(
            {
                "copies": current.count(IN_NAME),
                "cut": best["cut"],
                "cuts": [row["cut"] for row in array[1:]] + [best["cut"]],
                "list": current,
                "weighted": best["weighted"],
                "mean": best["mean"],
                "worst": best["worst"],
                "eco_arm": best["eco_arm"],
                "cape": best["cape"],
                "balloon": best["balloon"],
                "charm": best["charm"],
                "cells": best["cells"],
            }
        )
        report = report_from(current.count(IN_NAME) >= 4, None, {})
        if current.count(IN_NAME) >= 4:
            report["note"] = "The weighted score was still rising at 4 copies. A fifth Eco Arm is not legal."
        _write(report)

    final = _load()
    print(f"\narray {[round(x, 4) for x in final['win_rate_array']]}")
    print(f"copies {final['copies']} cuts {final['cuts']}")
    print(f"elapsed {final['elapsed']:.1f}s -> {DEST}")


if __name__ == "__main__":
    main()
