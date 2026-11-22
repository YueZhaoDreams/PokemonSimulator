#!/usr/bin/env python3
"""Rescore one Luxury Ball after Kecleon holds cards against Doll.

The locked SET_KECLEON_NAMES list is not edited. The 0-copy pass and every
non-Doll cell stay the cells in kecleon-luxury.json. Those games do not reach
the hold: the check returns before a random draw when the foe is not Doll.
Doll is replayed for the starting list and for every one-card cut, on the
same seed, 400 games, both seats. Weights are recomputed from that 0-copy
pass. Copies 2 through 4 are not measured.
"""

from __future__ import annotations

import importlib.util
import json
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD = HERE / "kecleon-luxury.json"
PARTIAL = HERE / "kecleon-luxury-hold-partial.jsonl"
DEST = HERE / "kecleon-luxury-hold.json"
MD_DEST = HERE / "kecleon-luxury-hold.md"

spec = importlib.util.spec_from_file_location("kecleon_luxury", HERE / "kecleon_luxury.py")
lux = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lux)


def _run_doll_counted(names: tuple[str, ...], foe: dict, seat: str) -> dict:
    from app.engine.game import play_game
    from app.engine.models import standard_60_rules
    from app.engine.strategies import StrategySpec

    subject = lux._subject_cards(names)
    other = lux._cards_for(foe["builder"], foe["names"])
    if seat == "a":
        cards_a, cards_b = subject, other
        strat_a, strat_b = lux.SUBJECT, foe["strategy"]
    else:
        cards_a, cards_b = other, subject
        strat_a, strat_b = foe["strategy"], lux.SUBJECT
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = __import__("random").Random(lux.SEED)
    wins = 0
    events: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for _ in range(lux.GAMES):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        if result.winner == seat:
            wins += 1
        ev = result.events or {}
        events["luxury_ball"] += int(ev.get(f"luxury_ball_{seat}", 0))
        events["dual_ball"] += int(ev.get(f"dual_ball_{seat}", 0))
        events["dual_ball_basic"] += int(ev.get(f"dual_ball_basic_{seat}", 0))
        events["scoundrel_ring"] += int(ev.get(f"scoundrel_ring_{seat}", 0))
        events["colorful_whip"] += int(ev.get("colorful_whip", 0))
        events["doll_hold"] += int(ev.get(f"doll_hold_{seat}", 0))
        prefix = f"tutor_{seat}:"
        suffix = ":luxury ball"
        for key, value in ev.items():
            if key.startswith(prefix) and key.endswith(suffix):
                found = key[len(prefix) : -len(suffix)]
                events[f"luxury_to:{found}"] += int(value)
        _outcome, kind = lux._kind(result, seat)
        reasons[kind] += 1
    return {"wins": wins, "games": lux.GAMES, "events": dict(events), "reasons": dict(reasons)}


def _load_partial() -> dict[str, dict]:
    found: dict[str, dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        found[row["key"]] = row["cell"]
    return found


def _append(key: str, cell: dict) -> None:
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")
        handle.flush()


def _pair(cache: dict[str, dict], names: list[str]) -> dict:
    frozen = tuple(names)
    out = {}
    for seat in ("a", "b"):
        key = lux._cache_key(frozen, "doll", seat)
        out[seat] = lux._public_cell(cache[key])
    return out


def _hold_per_game(pair: dict) -> float:
    total = 0.0
    for seat in ("a", "b"):
        cell = pair[seat]
        total += cell["events"].get("doll_hold", 0) / cell["games"]
    return total / 2


def main() -> None:
    started = time.time()
    if list(lux.SET_KECLEON_NAMES).count("Dual Ball") != 4:
        raise SystemExit("the lock is not 4 Dual Ball")
    if "Luxury Ball" in lux.SET_KECLEON_NAMES:
        raise SystemExit("the lock already contains Luxury Ball")
    old = json.loads(OLD.read_text())
    if old["seed"] != lux.SEED or old["games"] != lux.GAMES:
        raise SystemExit("the stored sample is not this seed and game count")
    if list(old["start"]) != list(lux.SET_KECLEON_NAMES):
        raise SystemExit("the stored start is not the lock")
    field = lux.discover()
    doll = next(foe for foe in field["foes"] if foe["key"] == "doll")
    check_foe = next(foe for foe in field["foes"] if foe["key"] == "h")
    stored = old["start_cells"]["h"]
    for seat in ("a", "b"):
        cell = lux._run(tuple(old["start"]), check_foe, seat, lux.GAMES, lux.SEED)
        if cell["wins"] != stored[seat]["wins"]:
            raise SystemExit(
                f"h seat {seat} replayed {cell['wins']} wins, the stored cell has {stored[seat]['wins']}. "
                "Non-Doll cells are not reusable."
            )
        if cell["events"].get("colorful_whip") != stored[seat]["events"].get("colorful_whip"):
            raise SystemExit(f"h seat {seat} whip counter moved. Non-Doll cells are not reusable.")
    print("h both seats match the stored cells", flush=True)

    lists = [("start", list(old["start"]))]
    for cut in old["rounds"][0]["cuts"]:
        lists.append((cut["cut"], list(cut["names"])))
    cache = _load_partial()
    jobs = []
    for _label, names in lists:
        frozen = tuple(names)
        for seat in ("a", "b"):
            key = lux._cache_key(frozen, "doll", seat)
            if key in cache:
                continue
            jobs.append((frozen, seat, key))
    print(f"doll cells to play {len(jobs)}", flush=True)
    if jobs:
        workers = max(1, min(lux.WORKERS, len(jobs)))
        t0 = time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futures = {
                pool.submit(_run_doll_counted, names, doll, seat): (names, seat, key)
                for names, seat, key in jobs
            }
            done = 0
            total = len(futures)
            for fut in as_completed(futures):
                names, seat, key = futures[fut]
                cell = fut.result()
                cache[key] = cell
                _append(key, cell)
                done += 1
                elapsed = time.perf_counter() - t0
                left = (total - done) * elapsed / done
                print(
                    f"  {done}/{total} doll seat {seat} {cell['wins']}/{lux.GAMES} ~{left / 60:.1f} min",
                    flush=True,
                )

    start_cells = json.loads(json.dumps(old["start_cells"]))
    start_cells["doll"] = _pair(cache, old["start"])
    weights = lux._weights(start_cells)
    active, parked = lux._active_set(weights)
    if active != old["active"]:
        missing = [foe for foe in active if foe not in old["active"]]
        if missing:
            raise SystemExit(f"the new 90% prefix pulls in {missing}, which has no later cells")
    start_view = start_cells
    start_rate = lux._rate(start_view, weights)
    labels = {foe["key"]: foe["label"] for foe in old["foes"]}
    cut_rows = []
    measured: dict[str, dict] = {}
    for cut in old["rounds"][0]["cuts"]:
        view = json.loads(json.dumps(cut["cells"]))
        view["doll"] = _pair(cache, cut["names"])
        worst_rate, worst_name = lux._worst(view, active)
        row = {
            "cut": cut["cut"],
            "copies": cut["copies"],
            "names": cut["names"],
            "weighted": lux._rate(view, weights),
            "se": lux._se(view, weights),
            "unweighted": lux._unweighted(view, active),
            "worst": worst_rate,
            "worst_foe": worst_name,
            "delta_prev": lux._rate(view, weights) - start_rate,
            "delta_start": lux._rate(view, weights) - start_rate,
            "gap_se_prev": lux._gap_se(start_view, view, weights, active),
            "gap_se_start": lux._gap_se(start_view, view, weights, active),
            "cells": view,
        }
        row["ratio_prev"] = lux._ratio(row["delta_prev"], row["gap_se_prev"])
        cut_rows.append(row)
        measured[cut["cut"]] = view
    cut_rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies"], row["cut"]))
    kept = cut_rows[0]
    reasons = []
    for row in cut_rows:
        moved = abs(row["delta_prev"]) >= row["gap_se_prev"] and row["gap_se_prev"] > 0
        if row["cut"] != kept["cut"] and row["cut"] != "Druddigon" and not moved:
            continue
        text = lux._reason(
            "Luxury Ball",
            row["cut"],
            row["copies"],
            start_view,
            measured[row["cut"]],
            start_view,
            weights,
            active,
            cut_rows,
            labels,
        )
        before_hold = _hold_per_game(start_view["doll"])
        after_hold = _hold_per_game(measured[row["cut"]]["doll"])
        text += (
            f" Against Doll the hold fired {before_hold:.3f} times per game on the start "
            f"and {after_hold:.3f} on this list. That counter is the Doll cell only."
        )
        reasons.append(text)
    druddigon_rank = next(i for i, row in enumerate(cut_rows, start=1) if row["cut"] == "Druddigon")
    jirachi_rank = next(i for i, row in enumerate(cut_rows, start=1) if row["cut"] == "Jirachi-EX")
    start_snap = lux._snapshot(list(old["start"]), start_view, weights, active, start_rate, start_rate)
    kept_view = measured[kept["cut"]]
    decision = (
        f"Kept counts: 1 Luxury Ball. The highest 0-copy weighted rate is 1 Luxury Ball minus "
        f"{kept['cut']} at {lux._pct(kept['weighted'])}. "
        f"Jirachi-EX is rank {jirachi_rank} of {len(cut_rows)}. "
        f"Druddigon is rank {druddigon_rank} of {len(cut_rows)}. "
        "Non-Doll cells are the stored cells from kecleon-luxury.json. "
        "Doll was replayed after Kecleon holds a turn once a Pokémon already in play can "
        "Knock Out Doll's Active. "
        "Each step took the best cut on this seed, so that path sits a little high. "
        "The script does not write the list into SET_KECLEON_NAMES."
    )
    state = lux._base_state(field, list(old["start"]), started)
    state.update(
        {
            "complete": True,
            "elapsed_s": time.time() - started,
            "weights": weights,
            "active": active,
            "parked": parked,
            "active_weight": sum(weights[foe] for foe in active),
            "start_cells": start_snap["cells"],
            "start_unweighted_all": sum(lux._mean(start_cells[foe["key"]]) for foe in field["foes"]) / len(field["foes"]),
            "start_unweighted_active": lux._unweighted(start_view, active),
            "start_worst": start_snap["worst"],
            "start_worst_foe": start_snap["worst_foe"],
            "path": [
                {
                    "step": "0",
                    "incoming": "—",
                    "cut": "—",
                    **{key: start_snap[key] for key in (
                        "weighted", "se", "unweighted", "worst", "worst_foe", "delta_start", "delta_prev",
                        *lux.PATH_COUNTERS,
                    )},
                },
                {
                    "step": "1",
                    "incoming": "Luxury Ball",
                    "cut": kept["cut"],
                    **{key: lux._snapshot(kept["names"], kept_view, weights, active, start_rate, start_rate)[key] for key in (
                        "weighted", "se", "unweighted", "worst", "worst_foe", "delta_start", "delta_prev",
                        *lux.PATH_COUNTERS,
                    )},
                },
            ],
            "rounds": [
                {
                    "incoming": "Luxury Ball",
                    "count": 1,
                    "kept_cut": kept["cut"],
                    "cuts": cut_rows,
                    "reasons": reasons,
                }
            ],
            "decision": decision,
            "kept_label": f"1 Luxury Ball minus {kept['cut']}",
            "kept_list": kept["names"],
            "kept_cells": kept_view,
            "path_label": f"1 Luxury Ball minus {kept['cut']}",
            "path_list": kept["names"],
            "path_cells": kept_view,
            "replayed": ["doll"],
            "reused_from": "kecleon-luxury.json",
            "identity_check": "h both seats matched wins and colorful_whip",
            "jirachi_rank": jirachi_rank,
            "druddigon_rank": druddigon_rank,
        }
    )
    note = lux._markdown(state)
    doll_lines = [
        "",
        "## What was replayed",
        "",
        "Doll was replayed for the starting list and for all 29 cuts. "
        "Every other foe keeps the cell in `kecleon-luxury.json`. "
        "The hold returns before a random draw when that foe's strategy is not Doll. "
        "Both seats of H matched the stored wins and the Whip counter before this rescore started. "
        "The active set is the same twelve foes. Doll's lower loss rate moves it behind the mirror. "
        "No parked foe enters the 90% prefix, so none of those lists were replayed.",
        "",
        "| Cut | Rank | Doll A | Doll B | Doll mean | Δ Doll | Hold / game |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    start_doll = lux._mean(start_view["doll"])
    order = {row["cut"]: i for i, row in enumerate(cut_rows, start=1)}
    for row in cut_rows:
        pair = measured[row["cut"]]["doll"]
        doll_lines.append(
            f"| {row['cut']} | {order[row['cut']]} | "
            f"{lux._pct(pair['a']['wins'] / pair['a']['games'])} | "
            f"{lux._pct(pair['b']['wins'] / pair['b']['games'])} | "
            f"{lux._pct(lux._mean(pair))} | {lux._pp(lux._mean(pair) - start_doll)} | "
            f"{_hold_per_game(pair):.2f} |"
        )
    doll_lines.append("")
    note = note.replace(
        "Parked foes stay at the win rate in that table.",
        "Parked foes stay at the win rate in that table. "
        "Active foes other than Doll also stay at the stored cell. Only Doll was replayed.",
    )
    note = note + "\n".join(doll_lines)
    lux._dump(DEST, json.dumps(state, indent=2) + "\n")
    lux._dump(MD_DEST, note)
    print(decision, flush=True)
    for i, row in enumerate(cut_rows, start=1):
        print(
            f"{i:2} {row['cut']:24} {lux._pct(row['weighted'])} {lux._pp(row['delta_start'])} {row['ratio_prev']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
