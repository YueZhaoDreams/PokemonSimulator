#!/usr/bin/env python3
"""Locked household 60s against the new C60 and the list it replaced.

C60's own greedy table played the new 60 as player A. M, Kudo's Mega Starmie,
the Wugtrio mill, Lucario, Iron Thorns, Carpet G, Carpet H, and the Ambipom
list were still scored against the previous C60 (one Prankish Clefable, zero
Mega). This run puts each of those lists in seat A and plays both C60s in
seat B. Seed and game count match, so the delta is the Mega swap.

Seed 20261011. Games per cell from C60_FIELD_GAMES (default 1000).
"""

from __future__ import annotations

import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_STARMIE60_NAMES,
    build_fallback_deck,
    build_g30_deck,
    c60_names_before_mega,
)

# key, label, names, strategy, use the G30 print builder
DECKS = (
    ("m", "Set M (Mew ex)", SET_M60_NAMES, "mew_baby", False),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie", False),
    ("mill", "Wugtrio mill", SET_MILL_NAMES, "mill", False),
    ("lucario", "Lucario Hariyama", SET_L60_NAMES, "aura", False),
    ("thorns", "Iron Thorns ex", IRON_THORNS_NAMES, "thorns", False),
    ("g", "Carpet Set G", SET_G_NAMES, "g", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)

GAMES = int(os.environ.get("C60_FIELD_GAMES", "1000"))
SEED = int(os.environ.get("C60_FIELD_SEED", "20261011"))
WORKERS = int(os.environ.get("C60_FIELD_WORKERS", str(min(4, os.cpu_count() or 2))))
QUERIES = [
    {"type": "event_prefix", "prefix": "seeker_moons_fuel", "key": "moons"},
    {"type": "event_prefix", "prefix": "attack:Mega Clefable ex:Shooting Moons", "key": "shooting"},
]
DEST = ROOT / "data/lab/set-c60-mega-field.json"
MD_DEST = ROOT / "data/lab/set-c60-mega-field.md"


def _deck(names: list[str], g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _run(deck_key: str, c60_key: str, names: list[str], strat: str, g30: bool, c60_names: list[str]) -> tuple[str, str, dict]:
    rec = run_simulation(
        _deck(names, g30),
        build_fallback_deck(list(c60_names)),
        standard_60_rules(),
        StrategySpec.from_dict(strat),
        StrategySpec.from_dict("party"),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": deck_key, "name": deck_key},
        deck_b_meta={"id": c60_key, "name": c60_key},
    )
    r = rec["results"]
    return deck_key, c60_key, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "moons": r["queries"].get("moons", 0.0),
        "shooting": r["queries"].get("shooting", 0.0),
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _markdown(report: dict) -> str:
    lines = [
        "# Household 60s vs the Mega C60",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per cell**: {report['games']}",
        "- **Seat**: the named deck is player A. C60 is player B. Who goes first is random.",
        "- **Old C60**: one Rebel Clash Prankish Clefable, zero Mega Clefable ex (`c60_names_before_mega`).",
        "- **New C60**: that Prankish Clefable is one Mega Clefable ex. Seeker stays.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "Shooting Moons is recorded for either player. Carpet Set G also attacks with Mega Clefable ex, so that cell's shooting rate includes both.",
        "",
        "| Deck | Strategy | vs old C60 | vs new C60 | Delta | New, A first | New, A second | Moons | Shooting |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["rows"]:
        old = row["old"]
        new = row["new"]
        lines.append(
            f"| {row['label']} | {row['strategy']} | {_pct(old['a'])} | {_pct(new['a'])} | "
            f"{new['a'] - old['a']:+.1%} | {_pct(new['first'])} | {_pct(new['second'])} | "
            f"{new['moons']:.3f} | {new['shooting']:.3f} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    rules = standard_60_rules()
    old_names = c60_names_before_mega()
    new_names = list(SET_C60_NAMES)
    if len(old_names) != 60 or len(new_names) != 60:
        raise SystemExit("C60 lists are not 60")
    if old_names.count("Mega Clefable ex") or new_names.count("Mega Clefable ex") != 1:
        raise SystemExit("expected zero Mega on the old list and one on the new list")
    for label, names in (("old", old_names), ("new", new_names)):
        bad = copy_violations(build_fallback_deck(names), rules)
        if bad:
            raise SystemExit(f"{label} C60 is illegal: {bad}")
    for key, _label, names, _strat, g30 in DECKS:
        pile = _deck(list(names), g30)
        if len(pile) != 60:
            raise SystemExit(f"{key} has {len(pile)} cards")
        bad = copy_violations(pile, rules)
        if bad:
            raise SystemExit(f"{key} is illegal: {bad}")

    c60s = (("old", old_names), ("new", new_names))
    jobs = [
        (key, c60_key, list(names), strat, g30, c60_names)
        for key, _label, names, strat, g30 in DECKS
        for c60_key, c60_names in c60s
    ]
    print(f"{len(jobs)} cells, {GAMES} games, seed {SEED}", flush=True)
    cells: dict[str, dict[str, dict]] = {key: {} for key, *_ in DECKS}
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        done = 0
        for fut in as_completed(futs):
            deck_key, c60_key, detail = fut.result()
            cells[deck_key][c60_key] = detail
            done += 1
            print(
                f"  {deck_key} vs {c60_key}: {detail['a']:.1%}  "
                f"moons {detail['moons']:.3f} shooting {detail['shooting']:.3f}  "
                f"({done}/{len(jobs)})",
                flush=True,
            )

    rows = []
    for key, label, names, strat, g30 in DECKS:
        rows.append(
            {
                "key": key,
                "label": label,
                "strategy": strat,
                "g30": g30,
                "old": cells[key]["old"],
                "new": cells[key]["new"],
            }
        )
    elapsed = time.perf_counter() - started
    report = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rule_preset": "s60",
        "seat": "named deck is player A, C60 is player B",
        "old_c60": "c60_names_before_mega",
        "new_c60": "SET_C60_NAMES",
        "rows": rows,
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(f"elapsed {elapsed:.1f}s -> {DEST}", flush=True)


if __name__ == "__main__":
    main()
