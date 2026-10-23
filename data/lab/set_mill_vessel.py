#!/usr/bin/env python3
"""Greedy Nincada + Shedinja pairs on the locked sleep-wall Mill.

A pair is one Dragons Exalted Nincada (Dig) and one Lost Thunder Shedinja
(Vessel of Life). Neither card does anything alone, so each greedy step adds
one pair and cuts two cards. The list stays at 60.

Shedinja is searched into hand only after a Wugtrio is in play. Nincada is
benched only once that Shedinja is in hand, because the Basic cannot evolve
on the turn it is played and a 40 HP body is a gust Prize. Spread matchups
leave Nincada in the deck. The Tool goes on a Wugtrio that is not already
preventing damage. Rescue Carrier takes the discarded Nincada ahead of a
spare Wiglett, then the Shedinja.

The cell is the mean of the two seat win rates against every household foe.
Weights are frozen from the sleep wall's losses on the confirm seed. A step
is taken only when the confirmed weighted rate clears the current list by
more than the combined standard error. The finalist is held out on a fresh
seed. This script does not edit SET_MILL_NAMES.
"""

from __future__ import annotations

import importlib.util
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

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import SET_MILL_NAMES, build_fallback_deck, build_g30_deck, fallback_named

_SPEC = importlib.util.spec_from_file_location("set_mill_sleep", ROOT / "data/lab/set_mill_sleep.py")
_SLEEP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_SLEEP)
FOES = _SLEEP.FOES

NINCADA = "Nincada"
SHEDINJA = "Shedinja"
FLOORS = {
    "Pichu": 1,
    "Mime Jr.": 1,
    "Slumbering Forest": 1,
    "Neutralization Zone": 1,
    "Wiglett": 2,
    "Wugtrio": 2,
}
VERSION = 1
GAMES = int(os.environ.get("MILL_VESSEL_GAMES", "80"))
SCREEN_GAMES = int(os.environ.get("MILL_VESSEL_SCREEN_GAMES", "32"))
SCREEN_TOP = int(os.environ.get("MILL_VESSEL_SCREEN_TOP", "4"))
HOLDOUT_GAMES = int(os.environ.get("MILL_VESSEL_HOLDOUT_GAMES", "120"))
SEED = int(os.environ.get("MILL_VESSEL_SEED", "20261023"))
HOLDOUT_SEED = int(os.environ.get("MILL_VESSEL_HOLDOUT_SEED", "20261024"))
WORKERS = int(os.environ.get("MILL_VESSEL_WORKERS", "4"))
MAX_PAIRS = int(os.environ.get("MILL_VESSEL_MAX_PAIRS", "4"))
DEST = Path(os.environ.get("MILL_VESSEL_DEST", ROOT / "data/lab/set-mill-vessel.json"))
MD_DEST = Path(os.environ.get("MILL_VESSEL_MD", ROOT / "data/lab/set-mill-vessel.md"))
CACHE_PATH = Path(os.environ.get("MILL_VESSEL_CACHE", ROOT / "data/cache/set-mill-vessel-cells.json"))
USAGE = ("vessel", "vessel_prize", "ko_nincada", "nincada", "shedinja", "mill_attack", "undersea")
QUERIES = [
    {"type": "event_sum", "prefix": "vessel_of_life", "key": "vessel"},
    {"type": "event_sum", "prefix": "vessel_prize", "key": "vessel_prize"},
    {"type": "event_sum", "prefix": "ko:Nincada", "key": "ko_nincada"},
    {"type": "event_prefix", "prefix": "saw_play:Nincada", "key": "nincada"},
    {"type": "event_prefix", "prefix": "saw_play:Shedinja", "key": "shedinja"},
    {"type": "event_sum", "prefix": "mill_attack", "key": "mill_attack"},
    {"type": "event_sum", "prefix": "attack:Wugtrio:Undersea Tunnel", "key": "undersea"},
]


def build_subject(names: list[str]):
    out = []
    for name in names:
        card = fallback_named("mime jr. col" if name == "Mime Jr." else name)
        out.append(card)
    return out


def list_key(names: list[str]) -> str:
    return ",".join(f"{name}x{count}" for name, count in sorted(Counter(names).items()))


def cell_key(names: list[str], games: int, foe_key: str, seed: int) -> str:
    return f"v{VERSION}|{seed}|{games}|{foe_key}|{list_key(names)}"


def cut_pairs(names: list[str]) -> list[tuple[str, str]]:
    counts = Counter(names)
    cuttable: list[tuple[str, int]] = []
    for name in sorted(counts):
        if name in {NINCADA, SHEDINJA}:
            continue
        spare = counts[name] - FLOORS.get(name, 0)
        if spare >= 1:
            cuttable.append((name, spare))
    pairs: list[tuple[str, str]] = []
    for i, (left, spare_left) in enumerate(cuttable):
        for right, _spare_right in cuttable[i:]:
            if left == right:
                if spare_left >= 2:
                    pairs.append((left, right))
            else:
                pairs.append((left, right))
    return pairs


def apply_pair(names: list[str], cuts: tuple[str, str]) -> list[str]:
    out = list(names)
    for cut in cuts:
        out.remove(cut)
    counts = Counter(out)
    for name, floor in FLOORS.items():
        if counts[name] < floor:
            raise ValueError(f"cut {cuts} drops {name} below {floor}")
    if counts[NINCADA] >= 4 or counts[SHEDINJA] >= 4:
        raise ValueError(f"cut {cuts} would exceed 4 copies")
    out.extend([NINCADA, SHEDINJA])
    if len(out) != 60:
        raise ValueError(f"cut {cuts} left {len(out)} cards")
    return out


def cut_label(cuts: tuple[str, str]) -> str:
    if cuts[0] == cuts[1]:
        return f"{cuts[0]} x2"
    return f"{cuts[0]} + {cuts[1]}"


def _usage(queries: dict) -> dict[str, float]:
    return {key: float(queries.get(key, 0.0)) for key in USAGE}


def _run(payload: tuple) -> tuple[str, dict]:
    names, games, foe_key, foe_names, foe_strat, g30, seed = payload
    subject = build_subject(names)
    foe = build_g30_deck() if g30 else build_fallback_deck(list(foe_names))
    seats = {}
    for seat in ("a", "b"):
        if seat == "a":
            cards_a, cards_b = subject, foe
            strat_a, strat_b = "mill", foe_strat
        else:
            cards_a, cards_b = foe, subject
            strat_a, strat_b = foe_strat, "mill"
        rec = run_simulation(
            cards_a,
            cards_b,
            standard_60_rules(),
            StrategySpec.from_dict(strat_a),
            StrategySpec.from_dict(strat_b),
            games=games,
            seed=seed,
            queries=QUERIES,
            deck_a_meta={"id": "mill", "name": "mill"},
            deck_b_meta={"id": foe_key, "name": foe_key},
        )
        result = rec["results"]
        wr = result["win_rate_a"] if seat == "a" else result["win_rate_b"]
        seats[seat] = {"wr": wr, "tie": result["tie_rate"], **_usage(result["queries"])}
    cell = {
        "a": seats["a"]["wr"],
        "b": seats["b"]["wr"],
        "wr": (seats["a"]["wr"] + seats["b"]["wr"]) / 2,
        "tie": (seats["a"]["tie"] + seats["b"]["tie"]) / 2,
        "games": games,
    }
    for key in USAGE:
        cell[key] = (seats["a"][key] + seats["b"][key]) / 2
    return foe_key, cell


class Cache:
    def __init__(self) -> None:
        self.cells: dict[str, dict] = {}
        if CACHE_PATH.exists():
            self.cells.update(json.loads(CACHE_PATH.read_text()))

    def get(self, names: list[str], games: int, foe_key: str, seed: int) -> dict | None:
        return self.cells.get(cell_key(names, games, foe_key, seed))

    def put(self, names: list[str], games: int, foe_key: str, detail: dict, seed: int) -> None:
        self.cells[cell_key(names, games, foe_key, seed)] = detail


def _save_cache(cache: Cache) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache.cells) + "\n")


def evaluate(
    lists: list[tuple[str, list[str]]],
    games: int,
    cache: Cache,
    seed: int,
    label: str,
) -> dict[str, dict[str, dict]]:
    jobs = []
    for key, names in lists:
        for foe_key, _title, foe_names, foe_strat, g30 in FOES:
            if cache.get(names, games, foe_key, seed) is None:
                jobs.append((key, names, foe_key, foe_names, foe_strat, g30))
    total = len(lists) * len(FOES)
    done = total - len(jobs)
    if jobs:
        workers = min(WORKERS, len(jobs))
        started = time.perf_counter()
        with ProcessPoolExecutor(max_workers=workers) as pool:
            futs = {
                pool.submit(_run, (names, games, foe_key, foe_names, foe_strat, g30, seed)): (key, names, foe_key)
                for key, names, foe_key, foe_names, foe_strat, g30 in jobs
            }
            for fut in as_completed(futs):
                key, names, foe_key = futs[fut]
                got_foe, detail = fut.result()
                if got_foe != foe_key:
                    raise RuntimeError(f"foe mismatch {got_foe} != {foe_key}")
                cache.put(names, games, foe_key, detail, seed)
                done += 1
                if done == 1 or done % 12 == 0 or done == total:
                    elapsed = time.perf_counter() - started
                    rate = (done - (total - len(jobs))) / elapsed if elapsed else 0
                    left = (total - done) / rate if rate else 0
                    print(f"  [{label}] {done}/{total} cells, {left:.0f}s left", flush=True)
                    _save_cache(cache)
        _save_cache(cache)
    out: dict[str, dict[str, dict]] = {}
    for key, names in lists:
        out[key] = {}
        for foe_key, *_ in FOES:
            cell = cache.get(names, games, foe_key, seed)
            if cell is None:
                raise RuntimeError(f"missing cell {key} vs {foe_key}")
            out[key][foe_key] = cell
    return out


def loss_weights(cells: dict[str, dict]) -> dict[str, float]:
    raw = {key: max(1e-6, 1.0 - cells[key]["wr"]) for key, *_ in FOES}
    total = sum(raw.values())
    return {key: raw[key] / total for key, *_ in FOES}


def weighted(cells: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(cells[key]["wr"] * weights[key] for key, *_ in FOES)


def mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def worst(cells: dict[str, dict]) -> float:
    return min(cells[key]["wr"] for key, *_ in FOES)


def weighted_se(cells: dict[str, dict], weights: dict[str, float]) -> float:
    var = 0.0
    for key, *_ in FOES:
        pa = cells[key]["a"]
        pb = cells[key]["b"]
        n = cells[key]["games"]
        var += (weights[key] ** 2) * (pa * (1.0 - pa) + pb * (1.0 - pb)) / (4 * n)
    return math.sqrt(var)


def avg(cells: dict[str, dict], field: str) -> float:
    return sum(cells[key][field] for key, *_ in FOES) / len(FOES)


def summarize(label: str, names: list[str], cells: dict[str, dict], weights: dict[str, float]) -> dict:
    row = {
        "label": label,
        "pairs": names.count(NINCADA),
        "weighted": weighted(cells, weights),
        "se": weighted_se(cells, weights),
        "mean": mean(cells),
        "worst": worst(cells),
        "counts": dict(Counter(names)),
        "foes": {key: cells[key]["wr"] for key, *_ in FOES},
    }
    for field in USAGE:
        row[field] = avg(cells, field)
    return row


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _markdown(report: dict) -> str:
    weights = report["weights"]
    base = report["baseline"]
    lines = [
        "# Mill Vessel of Life pairs",
        "",
        f"- **Confirm seed**: `{report['seed']}`",
        f"- **Holdout seed**: `{report['holdout_seed']}`",
        f"- **Screen**: {report['screen_games']} games per seat, both seats, top {report['screen_top']} confirmed",
        f"- **Confirm**: {report['games']} games per seat",
        f"- **Holdout**: {report['holdout_games']} games per seat",
        "- **Score**: mean of the two seat win rates, then loss-weighted. Weights are frozen from the sleep wall on the confirm seed.",
        "- **Step**: one Nincada and one Shedinja replace two cards. A step is kept only when the confirmed weighted rate beats the current list by more than the combined standard error.",
        f"- **Weights**: {', '.join(f'{key} {weights[key]:.1%}' for key, *_ in FOES)}",
        f"- **Elapsed**: {report['elapsed']:.0f}s",
        "",
        "Dig prevents effects of attacks, including damage, on heads during the opponent's next turn. "
        "Vessel of Life discards the cards attached to Shedinja, including the Nincada under it, and attaches Shedinja as a Tool. "
        "The Tool makes that Knock Out worth 1 fewer Prize. On a 1-Prize Wugtrio that is 0 Prizes. "
        "The line is worth about one extra Undersea Tunnel only when the Tool is actually knocked out. "
        "Handiwork and Miss Fortune Sisters still mill on the same turn as the attack, so the slots have to win the match, not the card-count comparison.",
        "",
        "## Baseline",
        "",
        f"Sleep wall weighted {_pct(base['weighted'])} (SE {_pct(base['se'])}), "
        f"mean {_pct(base['mean'])}, worst {_pct(base['worst'])}.",
        "",
        "| Foe | Win rate |",
        "| :--- | ---: |",
    ]
    for key, title, *_ in FOES:
        lines.append(f"| {title} | {_pct(base['foes'][key])} |")
    lines.extend(["", "## Path", ""])
    if not report["steps"]:
        lines.append("No pair cleared the confirm bar.")
    for step in report["steps"]:
        lines.append(f"### {step['pairs']} pair, cut {step['label']}")
        lines.append("")
        lines.append(
            f"Weighted {_pct(step['before'])} → {_pct(step['after'])} "
            f"({_signed(step['delta'])}, combined SE {_pct(step['combined_se'])}). "
            f"Mean {_pct(step['mean'])}, worst {_pct(step['worst'])}. "
            f"Vessel {step['vessel']:.2f}/game, prizes denied {step['vessel_prize']:.2f}, "
            f"Nincada KO {step['ko_nincada']:.2f}."
        )
        lines.append("")
        lines.append("| Confirm rank | Cut | Weighted | Mean | Worst | Vessel | Nincada KO |")
        lines.append("| ---: | :--- | ---: | ---: | ---: | ---: | ---: |")
        for rank, row in enumerate(step["confirm"], start=1):
            lines.append(
                f"| {rank} | {row['label']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | "
                f"{_pct(row['worst'])} | {row['vessel']:.2f} | {row['ko_nincada']:.2f} |"
            )
        lines.append("")
        lines.append("| Screen rank | Cut | Weighted | Mean | Worst |")
        lines.append("| ---: | :--- | ---: | ---: | ---: |")
        for rank, row in enumerate(step["screen"][:8], start=1):
            lines.append(
                f"| {rank} | {row['label']} | {_pct(row['weighted'])} | {_pct(row['mean'])} | {_pct(row['worst'])} |"
            )
        lines.append("")
    hold = report.get("holdout")
    lines.extend(["## Holdout", ""])
    if not hold:
        lines.append("No finalist. The sleep wall stays the lock.")
    else:
        lines.append(
            f"Fresh seed `{report['holdout_seed']}`, {report['holdout_games']} games per seat. "
            f"Sleep wall {_pct(hold['baseline']['weighted'])}, "
            f"finalist {_pct(hold['final']['weighted'])} "
            f"({_signed(hold['final']['weighted'] - hold['baseline']['weighted'])}). "
            f"Mean {_pct(hold['baseline']['mean'])} → {_pct(hold['final']['mean'])}."
        )
        lines.append("")
        lines.append("| Foe | Sleep | Finalist | Delta |")
        lines.append("| :--- | ---: | ---: | ---: |")
        for key, title, *_ in FOES:
            old = hold["baseline"]["foes"][key]
            new = hold["final"]["foes"][key]
            lines.append(f"| {title} | {_pct(old)} | {_pct(new)} | {_signed(new - old)} |")
        lines.append("")
    lines.extend(["## Counts", ""])
    final_counts = report["final_counts"]
    base_counts = report["baseline"]["counts"]
    lines.append("| Card | Sleep | Finalist |")
    lines.append("| :--- | ---: | ---: |")
    for name in sorted(set(base_counts) | set(final_counts)):
        if base_counts.get(name, 0) == final_counts.get(name, 0):
            continue
        lines.append(f"| {name} | {base_counts.get(name, 0)} | {final_counts.get(name, 0)} |")
    if final_counts == base_counts:
        lines.append("| — | same list | |")
    lines.extend(["", "## Decision", "", report["decision"], ""])
    return "\n".join(lines)


def _check_subject(names: list[str]) -> None:
    cards = build_subject(names)
    if len(cards) != 60:
        raise SystemExit(f"{len(cards)} cards")
    bad = copy_violations(cards, standard_60_rules())
    if bad:
        raise SystemExit(f"illegal list: {bad}")
    nincada = [card for card in cards if card.name == NINCADA]
    shedinja = [card for card in cards if card.name == SHEDINJA]
    if any(card.catalog_id != "bw6-10" for card in nincada):
        raise SystemExit("Nincada is not Dragons Exalted 10")
    if any(card.catalog_id != "sm8-95" for card in shedinja):
        raise SystemExit("Shedinja is not Lost Thunder 95")
    mime = [card for card in cards if card.name == "Mime Jr."]
    if any(card.catalog_id != "col1-47" for card in mime):
        raise SystemExit("Mime Jr. is not Call of Legends 47")


def main() -> None:
    started = time.perf_counter()
    current = list(SET_MILL_NAMES)
    if len(current) != 60:
        raise SystemExit(f"SET_MILL_NAMES has {len(current)} cards")
    if current.count(NINCADA) or current.count(SHEDINJA):
        raise SystemExit("SET_MILL_NAMES already has the vessel line")
    _check_subject(current)
    cache = Cache()
    print(f"{len(cut_pairs(current))} cut pairs at the first step", flush=True)

    print("baseline", flush=True)
    base_cells = evaluate([("base", current)], GAMES, cache, SEED, "baseline")["base"]
    weights = loss_weights(base_cells)
    base_row = summarize("sleep wall", current, base_cells, weights)
    print(
        f"baseline weighted {base_row['weighted']:.2%} mean {base_row['mean']:.2%} worst {base_row['worst']:.2%}",
        flush=True,
    )
    print("weights " + ", ".join(f"{key} {weights[key]:.1%}" for key, *_ in FOES), flush=True)

    steps: list[dict] = []
    path = [base_row]
    for pair_n in range(1, MAX_PAIRS + 1):
        pairs = cut_pairs(current)
        if not pairs:
            print(f"no legal cuts at pair {pair_n}", flush=True)
            break
        screen_lists = [(cut_label(cuts), apply_pair(current, cuts)) for cuts in pairs]
        screened = evaluate(screen_lists, SCREEN_GAMES, cache, SEED, f"pair {pair_n} screen")
        screen_rows = sorted(
            (summarize(label, names, screened[label], weights) for label, names in screen_lists),
            key=lambda row: (-row["weighted"], -row["worst"], row["label"]),
        )
        for row in screen_rows:
            row.pop("counts", None)
        finalists = screen_rows[:SCREEN_TOP]
        confirm_lists = [(row["label"], apply_pair(current, _cuts_of(row["label"]))) for row in finalists]
        confirmed = evaluate(confirm_lists, GAMES, cache, SEED, f"pair {pair_n} confirm")
        confirm_rows = sorted(
            (summarize(label, names, confirmed[label], weights) for label, names in confirm_lists),
            key=lambda row: (-row["weighted"], -row["worst"], row["label"]),
        )
        chosen = confirm_rows[0]
        current_w = path[-1]["weighted"]
        current_se = path[-1]["se"]
        combined = math.sqrt(chosen["se"] ** 2 + current_se ** 2)
        delta = chosen["weighted"] - current_w
        kept = delta > combined
        step = {
            "pairs": pair_n,
            "label": chosen["label"],
            "kept": kept,
            "before": current_w,
            "after": chosen["weighted"],
            "delta": delta,
            "combined_se": combined,
            "mean": chosen["mean"],
            "worst": chosen["worst"],
            "vessel": chosen["vessel"],
            "vessel_prize": chosen["vessel_prize"],
            "ko_nincada": chosen["ko_nincada"],
            "confirm": [
                {k: row[k] for k in ("label", "weighted", "se", "mean", "worst", "vessel", "ko_nincada", "foes")}
                for row in confirm_rows
            ],
            "screen": [
                {k: row[k] for k in ("label", "weighted", "mean", "worst", "vessel", "ko_nincada")}
                for row in screen_rows
            ],
        }
        steps.append(step)
        print(
            f"pair {pair_n} best {chosen['label']}: {current_w:.2%} → {chosen['weighted']:.2%} "
            f"({delta:+.2%}, bar {combined:.2%}) {'KEEP' if kept else 'STOP'}",
            flush=True,
        )
        if not kept:
            break
        current = apply_pair(current, _cuts_of(chosen["label"]))
        path.append(chosen)

    holdout = None
    if current != list(SET_MILL_NAMES):
        print("holdout", flush=True)
        held = evaluate(
            [("base", list(SET_MILL_NAMES)), ("final", current)],
            HOLDOUT_GAMES,
            cache,
            HOLDOUT_SEED,
            "holdout",
        )
        holdout = {
            "baseline": summarize("sleep wall", list(SET_MILL_NAMES), held["base"], weights),
            "final": summarize(f"{current.count(NINCADA)} pairs", current, held["final"], weights),
        }
        for row in holdout.values():
            row.pop("counts", None)

    final_counts = dict(Counter(current))
    if holdout and holdout["final"]["weighted"] > holdout["baseline"]["weighted"] and current != list(SET_MILL_NAMES):
        decision = (
            f"Holdout weighted {_pct(holdout['baseline']['weighted'])} → {_pct(holdout['final']['weighted'])} "
            f"({_signed(holdout['final']['weighted'] - holdout['baseline']['weighted'])}). "
            f"The {current.count(NINCADA)}-pair list cleared both the confirm bar and the fresh seed. "
            "SET_MILL_NAMES can move to this list."
        )
        verdict = "move"
    elif current != list(SET_MILL_NAMES) and holdout:
        decision = (
            f"Confirm kept a list, but the fresh seed did not. "
            f"Holdout {_pct(holdout['baseline']['weighted'])} → {_pct(holdout['final']['weighted'])} "
            f"({_signed(holdout['final']['weighted'] - holdout['baseline']['weighted'])}). "
            "SET_MILL_NAMES stays the sleep wall."
        )
        verdict = "keep"
    else:
        decision = (
            "No Nincada + Shedinja pair beat the sleep wall by more than the confirm noise. "
            "SET_MILL_NAMES stays the sleep wall."
        )
        verdict = "keep"
    report = {
        "seed": SEED,
        "holdout_seed": HOLDOUT_SEED,
        "games": GAMES,
        "screen_games": SCREEN_GAMES,
        "screen_top": SCREEN_TOP,
        "holdout_games": HOLDOUT_GAMES,
        "version": VERSION,
        "elapsed": time.perf_counter() - started,
        "weights": weights,
        "baseline": base_row,
        "steps": steps,
        "holdout": holdout,
        "final_counts": final_counts,
        "final_names": current,
        "verdict": verdict,
        "decision": decision,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(decision, flush=True)
    print(f"verdict {verdict}", flush=True)
    print(f"wrote {DEST}", flush=True)


def _cuts_of(label: str) -> tuple[str, str]:
    if label.endswith(" x2"):
        name = label[: -len(" x2")]
        return (name, name)
    left, right = label.split(" + ", 1)
    return (left, right)


if __name__ == "__main__":
    main()
