#!/usr/bin/env python3
"""Why the locked Doll 60 loses.

The list is SET_DOLL_NAMES: one Switch, one Black Market. Both seats, the same
13 foes and Sisters loss weights as the Doll lock. Each cell starts from
DOLL_LOSS_SEED (default 20261028), which is the Black Market confirm seed.
Games per seat from DOLL_LOSS_GAMES (default 200).

A loss reason is the engine's GameResult.reason, read from Doll's seat.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.game import play_game
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_DOLL_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    fallback_named,
)

FOES = (
    ("t60", "Dragapult ex (T60)", SET_T60_NAMES, "phantom", False),
    ("hedrick", "Hedrick Worlds Dragapult", SET_T_META_NAMES, "phantom", False),
    ("unl", "Unlimited Dragapult", SET_T_UNL_NAMES, "phantom", False),
    ("d60", "Cornerstone Ogerpon (D60)", SET_D60_NAMES, "demolish", False),
    ("s60", "Wo-Chien / Floragato (S60)", SET_S60_NAMES, "slash", False),
    ("g", "Gholdengo (G)", SET_G_NAMES, "g", False),
    ("c60", "Clefairy / Mewtwo (C60)", SET_C60_NAMES, "party", False),
    ("m", "Set M (Mew ex)", SET_M60_NAMES, "mew_baby", False),
    ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES, "starmie", False),
    ("lucario", "Lucario Hariyama", SET_L60_NAMES, "aura", False),
    ("thorns", "Iron Thorns ex", IRON_THORNS_NAMES, "thorns", False),
    ("h", "Carpet Set H", SET_H_NAMES, "nuzzle", False),
    ("g30", "Ambipom Hand Fling", SET_G30_NAMES, "celebration", True),
)

WEIGHTS = {
    "t60": 0.040,
    "hedrick": 0.051,
    "unl": 0.022,
    "d60": 0.145,
    "s60": 0.070,
    "g": 0.117,
    "c60": 0.124,
    "m": 0.145,
    "starmie": 0.106,
    "lucario": 0.051,
    "thorns": 0.041,
    "h": 0.076,
    "g30": 0.011,
}
_WEIGHT_TOTAL = sum(WEIGHTS.values())
WEIGHTS = {key: value / _WEIGHT_TOTAL for key, value in WEIGHTS.items()}

# Bodies that award a Prize when Knocked Out as a Pokémon. Shedinja's Vessel
# cuts a Prize only after it has become a Tool on another Pokémon.
PRIZE_BODIES = ("Cleffa", "Smoochum", "Mime Jr.", "Manaphy", "Sableye", "Nincada", "Shedinja")
DOLL_BODIES = ("Lillie's Poké Doll", "Robo Substitute Team Flare Gear", "Snorlax Doll")

GAMES = int(os.environ.get("DOLL_LOSS_GAMES", "200"))
SEED = int(os.environ.get("DOLL_LOSS_SEED", "20261028"))
WORKERS = int(os.environ.get("DOLL_LOSS_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("DOLL_LOSS_PARTIAL", HERE / "set-doll-losses-partial.jsonl"))
DEST = Path(os.environ.get("DOLL_LOSS_DEST", HERE / "set-doll-losses.json"))
MD_DEST = Path(os.environ.get("DOLL_LOSS_MD", HERE / "set-doll-losses.md"))

LOSS_KINDS = ("prizes", "empty", "decked", "no_basic", "turn_prizes", "turn_hp")
WIN_KINDS = ("foe_decked", "foe_empty", "foe_no_basic", "prizes", "turn_prizes", "turn_hp")


def _cards(names: list[str]):
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        elif name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
        else:
            out.append(fallback_named(name))
    return out


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _bucket() -> dict:
    return {
        "n": 0,
        "foe_prizes": [0] * 7,
        "turns": 0,
        "turn_hist": [0] * 5,
        "market": 0,
        "cut": 0,
        "kos": {},
        "prize_ko_hist": [0] * 16,
        "doll_ko_hist": [0] * 16,
    }


def _kind(result, seat: str) -> tuple[str, str]:
    """(outcome, kind). outcome is win, loss, or tie from Doll's seat."""
    reason = result.reason or ""
    if result.winner == "tie":
        return "tie", "tie"
    won = result.winner == seat
    outcome = "win" if won else "loss"
    if reason.endswith("had no Basic Pokémon") or reason.endswith("had no playable Pokémon"):
        who = reason.split()[0]
        if who == seat:
            return "loss", "no_basic"
        return "win", "foe_no_basic"
    if reason == "took all prize cards":
        return outcome, "prizes"
    if reason == "opponent has no Pokémon in play":
        return outcome, "empty" if outcome == "loss" else "foe_empty"
    if reason.endswith("decked out"):
        who = reason.split()[0]
        if who == seat:
            return "loss", "decked"
        return "win", "foe_decked"
    if reason == "more prizes at turn limit":
        return outcome, "turn_prizes"
    if reason == "more remaining HP at turn limit":
        return outcome, "turn_hp"
    if reason == "turn limit":
        return "tie", "tie"
    return outcome, reason or "other"


def _add(bucket: dict, result, seat: str, prize_names: tuple[str, ...], doll_names: tuple[str, ...]) -> None:
    foe_prizes = result.prizes_taken_b if seat == "a" else result.prizes_taken_a
    bucket["n"] += 1
    if 0 <= foe_prizes <= 6:
        bucket["foe_prizes"][foe_prizes] += 1
    bucket["turns"] += result.turns
    bucket["turn_hist"][min(4, result.turns // 8)] += 1
    events = result.events or {}
    if events.get("stadium:Black Market", 0):
        bucket["market"] += 1
    if events.get("market_prize_cut", 0):
        bucket["cut"] += 1
    prize_ko = 0
    doll_ko = 0
    for name in prize_names:
        n = int(events.get(f"ko:{name}", 0))
        if n:
            bucket["kos"][name] = bucket["kos"].get(name, 0) + n
            prize_ko += n
    for name in doll_names:
        n = int(events.get(f"ko:{name}", 0))
        if n:
            bucket["kos"][name] = bucket["kos"].get(name, 0) + n
            doll_ko += n
    bucket["prize_ko_hist"][min(15, prize_ko)] += 1
    bucket["doll_ko_hist"][min(15, doll_ko)] += 1


def _run(foe_key: str, seat: str, games: int, seed: int) -> dict:
    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(list(SET_DOLL_NAMES))
    foe = _foe_cards(foe_names, g30)
    foe_name_set = {card.name for card in foe}
    prize_names = tuple(name for name in PRIZE_BODIES if name not in foe_name_set)
    doll_names = tuple(name for name in DOLL_BODIES if name not in foe_name_set)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "doll", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "doll"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    kinds: dict[str, dict] = {}
    wins = 0
    ties = 0
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        outcome, kind = _kind(result, seat)
        label = f"{outcome}:{kind}"
        bucket = kinds.get(label)
        if bucket is None:
            bucket = _bucket()
            kinds[label] = bucket
        _add(bucket, result, seat, prize_names, doll_names)
        if outcome == "win":
            wins += 1
        elif outcome == "tie":
            ties += 1
    return {
        "games": games,
        "wins": wins,
        "ties": ties,
        "wr": wins / games if games else 0.0,
        "prize_names": list(prize_names),
        "doll_names": list(doll_names),
        "kinds": kinds,
    }


def _cache_key(foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(SET_DOLL_NAMES)}"


def _load_cache() -> dict[str, dict]:
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


def _merge_bucket(dst: dict, src: dict) -> None:
    dst["n"] += src["n"]
    dst["turns"] += src["turns"]
    dst["market"] += src["market"]
    dst["cut"] += src["cut"]
    for i, n in enumerate(src["foe_prizes"]):
        dst["foe_prizes"][i] += n
    for i, n in enumerate(src["turn_hist"]):
        dst["turn_hist"][i] += n
    for i, n in enumerate(src["prize_ko_hist"]):
        dst["prize_ko_hist"][i] += n
    for i, n in enumerate(src["doll_ko_hist"]):
        dst["doll_ko_hist"][i] += n
    for name, n in src["kos"].items():
        dst["kos"][name] = dst["kos"].get(name, 0) + n


def _evaluate(cache: dict[str, dict]) -> dict[str, dict]:
    jobs = []
    out: dict[str, dict] = {}
    for foe_key, *_ in FOES:
        for seat in ("a", "b"):
            key = _cache_key(foe_key, seat, GAMES, SEED)
            cached = cache.get(key)
            if cached is not None:
                out.setdefault(foe_key, {})[seat] = cached
                continue
            jobs.append((foe_key, seat, key))
    print(f"  {len(jobs)} cells, {GAMES} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, foe_key, seat, GAMES, SEED): (foe_key, seat, key)
            for foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out.setdefault(foe_key, {})[seat] = cell
            done += 1
            elapsed = time.perf_counter() - started
            left = elapsed / done * (len(futures) - done)
            print(
                f"    {done}/{len(futures)} {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)",
                flush=True,
            )
    return out


def _pct(rate: float) -> str:
    return f"{rate:.1%}"


def _mean_prizes(bucket: dict) -> float:
    if not bucket["n"]:
        return 0.0
    return sum(i * n for i, n in enumerate(bucket["foe_prizes"])) / bucket["n"]


def _hist(counts: list[int]) -> str:
    parts = [f"{i}:{n}" for i, n in enumerate(counts) if n]
    return " ".join(parts) if parts else "—"


def _combine_kind(cells: dict[str, dict], label: str) -> dict:
    merged = _bucket()
    for seat in ("a", "b"):
        src = cells[seat]["kinds"].get(label)
        if src:
            _merge_bucket(merged, src)
    return merged


def _write(report: dict) -> None:
    cells = report["cells"]
    games = report["games"]
    pair = games * 2
    loss_weights = {kind: 0.0 for kind in LOSS_KINDS}
    loss_weights["other"] = 0.0
    weighted_losses = 0.0
    raw_losses = {kind: 0 for kind in LOSS_KINDS}
    raw_losses["other"] = 0
    raw_games = 0
    lines = [
        "# Doll losses",
        "",
        "Locked 60: one Switch, one Black Market. Strategy `doll`. Product engine. "
        "Both seats. Doll goes first in either seat. "
        "The win rates are the Switch confirm in `set-doll-black-market.md`: same seed, same list, same games.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {games}",
        "- **Weights**: frozen Sisters loss weights, the same weights as the Doll lock.",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "A reason is `GameResult.reason` from Doll's seat. "
        "`prizes` means the opponent took all 6 Prize cards. "
        "`empty` means Doll's Active was Knocked Out with an empty Bench, before the opponent had 6 Prizes. "
        "`decked` means Doll's deck ran out. "
        "`no_basic` means Doll still had no Basic after the mulligan cap. "
        "Knock Out counts use names that are not in that foe's deck. The counter itself is not side-specific.",
        "",
        "## By foe",
        "",
        "| Foe | Win | Prizes | Empty | Decked | No basic | Turn | Foe prizes when the board is empty |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    foe_rows = []
    for key, label, *_ in FOES:
        pair_cell = cells[key]
        wins = pair_cell["a"]["wins"] + pair_cell["b"]["wins"]
        ties = pair_cell["a"]["ties"] + pair_cell["b"]["ties"]
        wr = wins / pair
        prizes = _combine_kind(pair_cell, "loss:prizes")
        empty = _combine_kind(pair_cell, "loss:empty")
        decked = _combine_kind(pair_cell, "loss:decked")
        no_basic = _combine_kind(pair_cell, "loss:no_basic")
        turn = _combine_kind(pair_cell, "loss:turn_prizes")
        turn_hp = _combine_kind(pair_cell, "loss:turn_hp")
        turn_n = turn["n"] + turn_hp["n"]
        known = prizes["n"] + empty["n"] + decked["n"] + no_basic["n"] + turn_n
        losses = pair - wins - ties
        other = losses - known
        weight = WEIGHTS[key]
        weighted_losses += weight * losses / pair
        for kind, bucket in (
            ("prizes", prizes),
            ("empty", empty),
            ("decked", decked),
            ("no_basic", no_basic),
            ("turn_prizes", turn),
            ("turn_hp", turn_hp),
        ):
            loss_weights[kind] += weight * bucket["n"] / pair
            raw_losses[kind] += bucket["n"]
        loss_weights["other"] += weight * other / pair
        raw_losses["other"] += other
        raw_games += pair
        empty_prizes = _mean_prizes(empty)
        lines.append(
            "| {label} | {wr} | {prizes} | {empty} | {decked} | {basic} | {turn} | {empty_prizes} |".format(
                label=label,
                wr=_pct(wr),
                prizes=_pct(prizes["n"] / pair),
                empty=_pct(empty["n"] / pair),
                decked=_pct(decked["n"] / pair),
                basic=_pct(no_basic["n"] / pair),
                turn=_pct(turn_n / pair),
                empty_prizes=f"{empty_prizes:.2f}" if empty["n"] else "—",
            )
        )
        foe_rows.append(
            {
                "key": key,
                "label": label,
                "wr": wr,
                "wins": wins,
                "ties": ties,
                "losses": losses,
                "prizes": prizes,
                "empty": empty,
                "decked": decked,
                "no_basic": no_basic,
                "turn_prizes": turn,
                "turn_hp": turn_hp,
                "other": other,
                "cell": pair_cell,
            }
        )
    lines.extend(
        [
            "",
            "## Share of the weighted losses",
            "",
            f"Sisters-weighted loss rate: {_pct(weighted_losses)} of games.",
            "",
            "| Reason | Weighted share of games | Share of weighted losses | Raw games |",
            "| :--- | ---: | ---: | ---: |",
        ]
    )
    labels = {
        "prizes": "Opponent took 6 Prizes",
        "empty": "Doll's board emptied",
        "decked": "Doll decked out",
        "no_basic": "Doll had no Basic",
        "turn_prizes": "Turn limit, fewer Prizes",
        "turn_hp": "Turn limit, less HP",
        "other": "Other",
    }
    for kind in ("prizes", "empty", "decked", "no_basic", "turn_prizes", "turn_hp", "other"):
        share = loss_weights[kind]
        of_losses = share / weighted_losses if weighted_losses else 0.0
        lines.append(
            f"| {labels[kind]} | {_pct(share)} | {_pct(of_losses)} | {raw_losses[kind]} / {raw_games} |"
        )
    lines.extend(["", "## Knock Outs when the opponent takes 6 Prizes", ""])
    lines.append("Mean Knock Outs of Doll-only names in those losses. A foe that shares the name is omitted.")
    lines.append("")
    lines.append(
        "| Foe | Games | Cleffa | Smoochum | Mime Jr. | Manaphy | Sableye | Nincada | Shedinja | Dolls | Turns | Market | Prize cut |"
    )
    lines.append("| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in foe_rows:
        bucket = row["prizes"]
        if not bucket["n"]:
            continue
        n = bucket["n"]
        tracked = set(row["cell"]["a"].get("prize_names") or PRIZE_BODIES)
        tracked |= set(row["cell"]["b"].get("prize_names") or PRIZE_BODIES)

        def ko(name: str, bucket=bucket, n=n, tracked=tracked) -> str:
            if name not in tracked:
                return "—"
            return f"{bucket['kos'].get(name, 0) / n:.2f}"

        doll_ko = sum(bucket["kos"].get(name, 0) for name in DOLL_BODIES) / n
        lines.append(
            "| {label} | {n} | {cleffa} | {smoochum} | {mime} | {manaphy} | {sableye} | {nincada} | {shed} | {dolls} | {turns:.1f} | {market:.0%} | {cut:.0%} |".format(
                label=row["label"],
                n=n,
                cleffa=ko("Cleffa"),
                smoochum=ko("Smoochum"),
                mime=ko("Mime Jr."),
                manaphy=ko("Manaphy"),
                sableye=ko("Sableye"),
                nincada=ko("Nincada"),
                shed=ko("Shedinja"),
                dolls=f"{doll_ko:.2f}",
                turns=bucket["turns"] / n,
                market=bucket["market"] / n,
                cut=bucket["cut"] / n,
            )
        )
    lines.extend(
        [
            "",
            "## Empty board",
            "",
            "Foe Prize cards already taken when Doll's Bench was empty. "
            "The count is games, both seats.",
            "",
            "| Foe | Games | Prize cards | Doll Knock Outs | Prize-body Knock Outs | Turns | Market played |",
            "| :--- | ---: | :--- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in foe_rows:
        bucket = row["empty"]
        if not bucket["n"]:
            continue
        n = bucket["n"]
        doll_ko = sum(bucket["kos"].get(name, 0) for name in DOLL_BODIES) / n
        prize_ko = sum(bucket["kos"].get(name, 0) for name in PRIZE_BODIES) / n
        lines.append(
            "| {label} | {n} | {hist} | {dolls:.2f} | {bodies:.2f} | {turns:.1f} | {market:.0%} |".format(
                label=row["label"],
                n=n,
                hist=_hist(bucket["foe_prizes"]),
                dolls=doll_ko,
                bodies=prize_ko,
                turns=bucket["turns"] / n,
                market=bucket["market"] / n,
            )
        )
    lines.extend(
        [
            "",
            "## Turn limit",
            "",
            "The game stops after 40 turns. Doll loses this way when the opponent has more Prize cards, or the same number and more remaining HP. "
            "The Prize column is how many the opponent had already taken.",
            "",
            "| Foe | Fewer Prizes | Their Prizes | Less HP |",
            "| :--- | ---: | :--- | ---: |",
        ]
    )
    for row in foe_rows:
        prizes = row["turn_prizes"]
        hp = row["turn_hp"]
        if prizes["n"] + hp["n"] < pair * 0.05:
            continue
        lines.append(
            f"| {row['label']} | {prizes['n']} | {_hist(prizes['foe_prizes'])} | {hp['n']} |"
        )
    omitted = []
    for row in foe_rows:
        have = set(row["cell"]["a"].get("prize_names") or []) | set(row["cell"]["b"].get("prize_names") or [])
        missing = [name for name in PRIZE_BODIES if name not in have]
        if missing:
            omitted.append(f"{row['label']} shares {', '.join(missing)}")
    if omitted:
        lines.extend(["", "Shared names are left out of the Knock Out columns: " + "; ".join(omitted) + "."])
    lines.extend(["", "## How the wins happen", ""])
    lines.append("| Foe | Foe decked | Foe board empty | Foe had no Basic | Doll took 6 |")
    lines.append("| :--- | ---: | ---: | ---: | ---: |")
    for row in foe_rows:
        pair_cell = cells[row["key"]]
        decked = _combine_kind(pair_cell, "win:foe_decked")["n"] / pair
        empty = _combine_kind(pair_cell, "win:foe_empty")["n"] / pair
        basic = _combine_kind(pair_cell, "win:foe_no_basic")["n"] / pair
        prizes = _combine_kind(pair_cell, "win:prizes")["n"] / pair
        lines.append(
            f"| {row['label']} | {_pct(decked)} | {_pct(empty)} | {_pct(basic)} | {_pct(prizes)} |"
        )
    lines.append("")
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text("\n".join(lines) + "\n")
    print(f"wrote {DEST}", flush=True)
    print(f"wrote {MD_DEST}", flush=True)


def main() -> None:
    if len(SET_DOLL_NAMES) != 60 or SET_DOLL_NAMES.count("Black Market") != 1 or SET_DOLL_NAMES.count("Switch") != 1:
        raise SystemExit("SET_DOLL_NAMES is not the one-Switch, one-Black-Market lock")
    started = time.perf_counter()
    cache = _load_cache()
    cells = _evaluate(cache)
    elapsed = time.perf_counter() - started
    if elapsed < 1.0 and DEST.exists():
        previous = json.loads(DEST.read_text()).get("elapsed") or 0
        if previous > elapsed:
            elapsed = previous
    report = {
        "seed": SEED,
        "games": GAMES,
        "weights": WEIGHTS,
        "elapsed": elapsed,
        "list": list(SET_DOLL_NAMES),
        "cells": cells,
    }
    _write(report)


if __name__ == "__main__":
    main()
