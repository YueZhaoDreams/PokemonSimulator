#!/usr/bin/env python3
"""Add one Mega Starmie foe to the Set M Manaphy swap, without replaying the old five.

The old cells stay in data/lab/set-m-manaphy.json (seed 20261007, 1000 games).
This run is baseline, each one-card Manaphy cut, and the three Budew replacements
against Riku Kudo's Mega Starmie list only. Weights are recomputed from the
no-Manaphy loss rates, now including that foe.

Jetting Blow is one Water Energy for 120, plus 50 damage to one Benched Pokémon.
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
from app.seed_data import SET_M60_NAMES, SET_STARMIE60_NAMES, build_fallback_deck

OLD = ROOT / "data/lab/set-m-manaphy.json"
DEST = ROOT / "data/lab/set-m-manaphy-starmie.json"
MD_DEST = ROOT / "data/lab/set-m-manaphy-starmie.md"

OLD_FOES = ("t60", "hedrick", "c60", "d60", "thorns")
FOE_KEY = "starmie"
FOE_LABELS = {
    "t60": "T60",
    "hedrick": "Hedrick",
    "c60": "C60",
    "d60": "D60",
    "thorns": "Thorns",
    "starmie": "Starmie",
}

GAMES = int(os.environ.get("M_MANAPHY_GAMES", "1000"))
SEED = int(os.environ.get("M_MANAPHY_SEED", "20261007"))
WORKERS = int(os.environ.get("M_MANAPHY_WORKERS", "4"))

QUERIES = [
    {"type": "event_prefix", "prefix": "saw_play:Manaphy", "key": "manaphy"},
    {"type": "event_prefix", "prefix": "wave_veil", "key": "wave_veil"},
    {"type": "event_prefix", "prefix": "attack:Mega Starmie ex:Jetting Blow", "key": "jetting"},
    {"type": "event_prefix", "prefix": "freezing_shroud", "key": "shroud"},
    {"type": "event_prefix", "prefix": "surfing_beach", "key": "beach"},
]

CONTROLS = (
    ("Bravery Charm", "Bravery Charm"),
    ("Ultra Ball", "Ultra Ball"),
    ("Professor's Research", "Professor's Research"),
)


def _swap(names: list[str], cut: str, add: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(add)
    if len(out) != 60:
        raise ValueError(f"{cut} -> {add} is {len(out)} cards")
    return out


def _run(key: str, names: list[str]) -> tuple[str, dict]:
    rec = run_simulation(
        build_fallback_deck(names),
        build_fallback_deck(list(SET_STARMIE60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("starmie"),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": key, "name": key},
        deck_b_meta={"id": FOE_KEY, "name": "kudo-starmie"},
    )
    result = rec["results"]
    return key, {
        "a": result["win_rate_a"],
        "b": result["win_rate_b"],
        "tie": result["tie_rate"],
        "first": result["win_rate_a_going_first"],
        "second": result["win_rate_a_going_second"],
        "manaphy": result["queries"].get("manaphy", 0.0),
        "wave_veil": result["queries"].get("wave_veil", 0.0),
        "jetting": result["queries"].get("jetting", 0.0),
        "shroud": result["queries"].get("shroud", 0.0),
        "beach": result["queries"].get("beach", 0.0),
    }


def _load_partial() -> dict:
    if not DEST.exists():
        return {}
    data = json.loads(DEST.read_text())
    cells = data.get("starmie_cells") or {}
    if data.get("games") != GAMES or data.get("seed") != SEED:
        return {}
    return cells


def _save_partial(cells: dict, started: float) -> None:
    DEST.write_text(
        json.dumps(
            {
                "games": GAMES,
                "seed": SEED,
                "done": False,
                "elapsed": time.perf_counter() - started,
                "starmie_cells": cells,
            },
            indent=2,
        )
    )


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _weights(base_cells: dict[str, float]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - base_cells[key]) for key in base_cells}
    total = sum(raw.values())
    return {key: raw[key] / total for key in raw}


def _weighted(cells: dict[str, float], weights: dict[str, float]) -> float:
    return sum(cells[key] * weights[key] for key in weights)


def _merge(starmie_cells: dict[str, dict], elapsed: float) -> dict:
    old = json.loads(OLD.read_text())
    if old.get("seed") != SEED or old.get("games") != GAMES:
        raise SystemExit("old Manaphy lab seed/games do not match this run")
    base_old = {key: old["baseline"]["cells"][key]["a"] for key in OLD_FOES}
    base_all = {**base_old, FOE_KEY: starmie_cells["baseline"]["a"]}
    weights = _weights(base_all)
    order = list(OLD_FOES) + [FOE_KEY]

    def row_cells(cut: str, old_cells: dict) -> dict[str, float]:
        found = {key: old_cells[key]["a"] for key in OLD_FOES}
        found[FOE_KEY] = starmie_cells[cut]["a"]
        return found

    baseline_cells = row_cells("baseline", old["baseline"]["cells"])
    baseline = {
        "weighted": _weighted(baseline_cells, weights),
        "cells": baseline_cells,
        "starmie": starmie_cells["baseline"],
    }
    rows = []
    for candidate in old["candidates"]:
        cut = candidate["cut"]
        cells = row_cells(cut, candidate["cells"])
        rows.append(
            {
                "cut": cut,
                "copies_before": candidate["copies_before"],
                "weighted": _weighted(cells, weights),
                "cells": cells,
                "starmie": starmie_cells[cut],
            }
        )
    rows.sort(key=lambda row: (-row["weighted"], -row["copies_before"], row["cut"]))
    controls = []
    manaphy_budew = next(row for row in rows if row["cut"] == "Budew")
    controls.append(
        {
            "replacement": "Manaphy",
            "weighted": manaphy_budew["weighted"],
            "cells": manaphy_budew["cells"],
            "starmie": manaphy_budew["starmie"],
        }
    )
    for label, _add in CONTROLS:
        key = f"control:{label}"
        old_row = next(row for row in old["budew_controls"]["rows"] if row["replacement"] == label)
        cells = {key_name: old_row["cells"][key_name] for key_name in OLD_FOES}
        cells[FOE_KEY] = starmie_cells[key]["a"]
        controls.append(
            {
                "replacement": label,
                "weighted": _weighted(cells, weights),
                "cells": cells,
                "starmie": starmie_cells[key],
            }
        )
    best = rows[0]
    best_control = max(controls, key=lambda row: row["weighted"])
    manaphy_beats_baseline = manaphy_budew["weighted"] > baseline["weighted"]
    manaphy_is_best_budew = best_control["replacement"] == "Manaphy"
    any_cut_beats = best["weighted"] > baseline["weighted"]
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "done": True,
        "foe": "Riku Kudo 19th Champions League Yokohama, Limitless 29462",
        "weights": weights,
        "baseline": baseline,
        "candidates": rows,
        "controls": controls,
        "best_cut": best["cut"],
        "best_weighted": best["weighted"],
        "worth_swapping": bool(any_cut_beats and (best["cut"] != "Budew" or manaphy_is_best_budew)),
        "lock_list": False,
        "manaphy_beats_baseline": manaphy_beats_baseline,
        "best_budew_replacement": best_control["replacement"],
        "starmie_cells": starmie_cells,
        "note": "",
    }
    report["note"] = _note(report)
    return report


def _note(report: dict) -> str:
    base = report["baseline"]["weighted"]
    best = report["best_cut"]
    best_w = report["best_weighted"]
    replacement = report["best_budew_replacement"]
    if report["worth_swapping"]:
        return (
            f"Best Manaphy cut is {best} at {best_w:.1%} against the baseline {base:.1%}, "
            f"with Mega Starmie included. Best Budew replacement is {replacement}."
        )
    return (
        f"With Mega Starmie included, no Manaphy cut is worth locking. "
        f"Best cut is {best} at {best_w:.1%} against the baseline {base:.1%}. "
        f"Best Budew replacement is {replacement}. SET_M60_NAMES stays unchanged."
    )


def _render(report: dict) -> str:
    weights = report["weights"]
    base = report["baseline"]
    lines = [
        "# Set M one Manaphy, plus Mega Starmie",
        "",
        "Old foes are reused from `set-m-manaphy.json`. Only the Mega Starmie foe is new.",
        "That list is Riku Kudo, 19th Champions League Yokohama (Limitless 29462).",
        "Jetting Blow costs one Water Energy, does 120, and does 50 damage to one Benched Pokémon.",
        "Weights are the no-Manaphy loss rates across T60, Hedrick, C60, D60, Crushing Thorn, and this Starmie list.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per new cell**: {report['games']}",
        "- **Weights**: " + ", ".join(f"{FOE_LABELS[key]} {weights[key]:.1%}" for key in list(OLD_FOES) + [FOE_KEY]),
        f"- **Baseline weighted**: {_pct(base['weighted'])}",
        f"- **Best cut**: {report['best_cut']}",
        f"- **Worth swapping**: {report['worth_swapping']}",
        f"- **Lock the list**: {report['lock_list']}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "| Rank | Cut | Weighted | Delta | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Manaphy | Veil | Jetting |",
        "| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| 0 | (none) | {_pct(base['weighted'])} | — | "
            + " | ".join(_pct(base["cells"][key]) for key in list(OLD_FOES) + [FOE_KEY])
            + " | — | — | "
            f"{base['starmie']['jetting']:.2f} |"
        ),
    ]
    for rank, row in enumerate(report["candidates"], start=1):
        delta = row["weighted"] - base["weighted"]
        lines.append(
            f"| {rank} | {row['cut']} | {_pct(row['weighted'])} | {delta:+.1%} | "
            + " | ".join(_pct(row["cells"][key]) for key in list(OLD_FOES) + [FOE_KEY])
            + f" | {row['starmie']['manaphy']:.2f} | {row['starmie']['wave_veil']:.2f} | {row['starmie']['jetting']:.2f} |"
        )
    lines.extend(
        [
            "",
            "## Replacing Budew",
            "",
            "| Replacement | Weighted | Delta | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Veil |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in report["controls"]:
        delta = row["weighted"] - base["weighted"]
        lines.append(
            f"| {row['replacement']} | {_pct(row['weighted'])} | {delta:+.1%} | "
            + " | ".join(_pct(row["cells"][key]) for key in list(OLD_FOES) + [FOE_KEY])
            + f" | {row['starmie']['wave_veil']:.2f} |"
        )
    lines.extend(["", report["note"], ""])
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    current = list(SET_M60_NAMES)
    if len(current) != 60 or current.count("Manaphy"):
        raise SystemExit("baseline must be the locked 60 with no Manaphy")
    cuts = sorted(Counter(current))
    jobs: list[tuple[str, list[str]]] = [("baseline", current)]
    jobs.extend((cut, _swap(current, cut, "Manaphy")) for cut in cuts)
    jobs.extend((f"control:{label}", _swap(current, "Budew", add)) for label, add in CONTROLS)
    cells = _load_partial()
    pending = [(key, names) for key, names in jobs if key not in cells]
    print(f"{len(jobs)} starmie cells, {len(pending)} pending, seed {SEED}, games {GAMES}", flush=True)
    if pending:
        with ProcessPoolExecutor(max_workers=min(WORKERS, len(pending))) as pool:
            futs = [pool.submit(_run, key, names) for key, names in pending]
            done = len(cells)
            for fut in as_completed(futs):
                key, detail = fut.result()
                cells[key] = detail
                done += 1
                print(
                    f"  {key} vs starmie: {detail['a']:.1%}  "
                    f"manaphy {detail['manaphy']:.2f}  veil {detail['wave_veil']:.2f}  "
                    f"jetting {detail['jetting']:.2f}  ({done}/{len(jobs)})",
                    flush=True,
                )
                _save_partial(cells, started)
    missing = [key for key, _ in jobs if key not in cells]
    if missing:
        raise SystemExit(f"missing cells: {missing}")
    report = _merge(cells, time.perf_counter() - started)
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_render(report))
    print(report["note"], flush=True)
    print(f"elapsed {report['elapsed']:.1f}s -> {DEST}", flush=True)


if __name__ == "__main__":
    main()
