#!/usr/bin/env python3
"""Mill draw package: Level Ball, Cleffa, Survival Brace, Junk Arm, Manaphy.

The live lock is SET_MILL_NAMES: one Manaphy, one HGSS Cleffa, Nest Ball ×1.
Lists here swap the previous Wally 60, frozen as _WALLY_60. Cleffa is the
HeartGold & SoulSilver Eeeeeeek print. Survival Brace replaces the ACE SPEC.
Junk Arm discards two cards that no longer extend Undersea and takes a Trainer
from the discard.

Both seats. Loss-weighted win rate. Weights frozen from the Sisters 60.
Seed 20261027 unless MILL_DRAW_SEED is set. Games per seat from MILL_DRAW_GAMES
(default 160). MILL_DRAW_LISTS limits the names (comma-separated).
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

from app.engine.game import play_game
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
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

GAMES = int(os.environ.get("MILL_DRAW_GAMES", "160"))
SEED = int(os.environ.get("MILL_DRAW_SEED", "20261027"))
WORKERS = int(os.environ.get("MILL_DRAW_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("MILL_DRAW_PARTIAL", "/tmp/mill-draw-partial.jsonl"))
DEST = Path(os.environ.get("MILL_DRAW_DEST", HERE / "set-mill-draw.json"))
MD_DEST = Path(os.environ.get("MILL_DRAW_MD", HERE / "set-mill-draw.md"))


# Previous Wally lock, before Manaphy and Cleffa. The live 60 is SET_MILL_NAMES.
_WALLY_60 = (
    ["Pichu"]
    + ["Mime Jr."]
    + ["Wiglett"] * 4
    + ["Wugtrio"] * 4
    + ["Victini"]
    + ["Slumbering Forest"]
    + ["Neutralization Zone"]
    + ["Buddy-Buddy Poffin"] * 4
    + ["Nest Ball"] * 3
    + ["Level Ball"] * 3
    + ["Rescue Carrier"] * 3
    + ["Lillie's Poké Doll"]
    + ["Crushing Hammer"] * 4
    + ["Counter Catcher"] * 2
    + ["Miss Fortune Sisters"] * 2
    + ["Wally"] * 3
    + ["Boss's Orders"]
    + ["Team Rocket's Handiwork"] * 2
    + ["Colress's Tenacity"] * 4
    + ["Double Turbo Energy"] * 4
    + ["Water Energy"] * 3
    + ["Ignition Energy"] * 4
    + ["Reversal Energy"] * 4
)


def _swap(cuts: list[str], adds: list[str]) -> tuple[str, ...]:
    names = list(_WALLY_60)
    for card in cuts:
        names.remove(card)
    names.extend(adds)
    if len(names) != 60:
        raise SystemExit(f"swap {cuts} -> {adds} has {len(names)} cards")
    return tuple(names)


NOTES = {
    "lock": "Wally lock. Level Ball ×3, Nest Ball ×3, Neutralization Zone",
    "level4": "Level Ball ×4, Nest Ball ×2",
    "brace": "Survival Brace replaces Neutralization Zone",
    "cleffa": "One HGSS Cleffa replaces one Nest Ball",
    "junk2": "Junk Arm ×2 replaces two Nest Ball",
    "pack": "Level ×4, Cleffa, Brace, Junk ×2. Cut three Nest, one Hammer, Zone",
    "wake": "Same package, Forest out and one Nest back, so sleep is one coin",
    "veil": "Manaphy and HGSS Cleffa replace two Nest Ball. Level Ball stays ×3. Poffin stays ×4.",
}

LISTS = {
    "lock": tuple(_WALLY_60),
    "level4": _swap(["Nest Ball"], ["Level Ball"]),
    "brace": _swap(["Neutralization Zone"], ["Survival Brace"]),
    "cleffa": _swap(["Nest Ball"], ["Cleffa"]),
    "junk2": _swap(["Nest Ball", "Nest Ball"], ["Junk Arm", "Junk Arm"]),
    "pack": _swap(
        ["Nest Ball", "Nest Ball", "Nest Ball", "Crushing Hammer", "Neutralization Zone"],
        ["Level Ball", "Cleffa", "Survival Brace", "Junk Arm", "Junk Arm"],
    ),
    "wake": _swap(
        [
            "Nest Ball",
            "Nest Ball",
            "Crushing Hammer",
            "Neutralization Zone",
            "Slumbering Forest",
        ],
        ["Level Ball", "Cleffa", "Survival Brace", "Junk Arm", "Junk Arm"],
    ),
    "veil": _swap(["Nest Ball", "Nest Ball"], ["Manaphy", "Cleffa"]),
}


def _selected() -> list[str]:
    raw = os.environ.get("MILL_DRAW_LISTS", "")
    if not raw.strip():
        return list(LISTS)
    labels = [part.strip() for part in raw.split(",") if part.strip()]
    missing = [label for label in labels if label not in LISTS]
    if missing:
        raise SystemExit(f"unknown lists: {missing}")
    return labels


def _cards(names: tuple[str, ...]):
    out = []
    for name in names:
        if name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
        elif name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        else:
            out.append(fallback_named(name))
    return out


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _check_lists(names: list[str]) -> None:
    rules = standard_60_rules()
    for label in names:
        pile = _cards(LISTS[label])
        if len(pile) != 60:
            raise SystemExit(f"{label} has {len(pile)} cards")
        bad = copy_violations(pile, rules)
        if bad:
            raise SystemExit(f"{label} is illegal: {bad}")
        cleffa = [card for card in pile if card.name == "Cleffa"]
        for card in cleffa:
            kinds = {effect.get("kind") for attack in card.attacks for effect in attack.effects}
            if "shuffle_hand_then_draw" not in kinds:
                raise SystemExit(f"{label} Cleffa is not Eeeeeeek")


def _bucket(seat: str, winner: str, reason: str) -> str:
    if winner == "tie":
        return f"tie|{reason}"
    mill_won = (seat == "a" and winner == "a") or (seat == "b" and winner == "b")
    side = "mill" if mill_won else "foe"
    return f"{side}|{reason}"


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = _cards(names)
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "mill", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "mill"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    ties = 0
    mill_attack = 0
    eeeeeeek = 0
    junk = 0
    brace = 0
    cleffa_play = 0
    manaphy_play = 0
    turns = 0
    opp_prizes = 0
    reasons: Counter[str] = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        mill_is_a = seat == "a"
        if (mill_is_a and result.winner == "a") or (not mill_is_a and result.winner == "b"):
            wins += 1
        elif result.winner == "tie":
            ties += 1
        mill_attack += result.events.get("mill_attack", 0)
        eeeeeeek += result.events.get("eeeeeeek_shuffle", 0)
        junk += result.events.get("junk_arm", 0)
        brace += result.events.get("survival_brace", 0)
        cleffa_play += result.events.get("saw_play:Cleffa", 0)
        manaphy_play += result.events.get("saw_play:Manaphy", 0)
        turns += result.turns
        opp_prizes += result.prizes_taken_b if mill_is_a else result.prizes_taken_a
        reasons[_bucket(seat, result.winner, result.reason)] += 1
    return {
        "wr": wins / games,
        "tie": ties / games,
        "mill_attack": mill_attack / games,
        "eeeeeeek": eeeeeeek / games,
        "junk_arm": junk / games,
        "survival_brace": brace / games,
        "cleffa_play": cleffa_play / games,
        "manaphy_play": manaphy_play / games,
        "turns": turns / games,
        "opp_prizes": opp_prizes / games,
        "reasons": dict(reasons),
    }


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|{'/'.join(names)}"


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
    PARTIAL.parent.mkdir(parents=True, exist_ok=True)
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")


def _evaluate(labels: list[str], games: int, cache: dict[str, dict]) -> dict[str, dict[str, dict]]:
    jobs = []
    out: dict[str, dict[str, dict]] = {label: {} for label in labels}
    for label in labels:
        frozen = LISTS[label]
        for foe_key, *_ in FOES:
            for seat in ("a", "b"):
                key = _cache_key(frozen, foe_key, seat, games, SEED)
                cached = cache.get(key)
                if cached is not None:
                    out[label].setdefault(foe_key, {})[seat] = cached
                    continue
                jobs.append((label, frozen, foe_key, seat, key))
    print(f"{len(jobs)} cells, {games} games, seed {SEED}", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(_run, frozen, foe_key, seat, games, SEED): (label, foe_key, seat, key)
            for label, frozen, foe_key, seat, key in jobs
        }
        for fut in as_completed(futures):
            label, foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out[label].setdefault(foe_key, {})[seat] = cell
            done += 1
            if done == 1 or done % 8 == 0 or done == len(futures):
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                print(
                    f"  {done}/{len(futures)} {label} seat {seat} vs {foe_key} {cell['wr']:.1%} ({left:.0f}s left)",
                    flush=True,
                )
    return out


def _combine(cells: dict[str, dict]) -> dict[str, dict]:
    combined = {}
    for foe_key, *_ in FOES:
        a = cells[foe_key]["a"]
        b = cells[foe_key]["b"]
        row = {
            "wr": (a["wr"] + b["wr"]) / 2,
            "a": a["wr"],
            "b": b["wr"],
            "tie": (a["tie"] + b["tie"]) / 2,
            "mill_attack": (a["mill_attack"] + b["mill_attack"]) / 2,
            "eeeeeeek": (a.get("eeeeeeek", 0) + b.get("eeeeeeek", 0)) / 2,
            "junk_arm": (a.get("junk_arm", 0) + b.get("junk_arm", 0)) / 2,
            "survival_brace": (a.get("survival_brace", 0) + b.get("survival_brace", 0)) / 2,
            "cleffa_play": (a.get("cleffa_play", 0) + b.get("cleffa_play", 0)) / 2,
            "manaphy_play": (a.get("manaphy_play", 0) + b.get("manaphy_play", 0)) / 2,
            "turns": (a["turns"] + b["turns"]) / 2,
            "opp_prizes": (a["opp_prizes"] + b["opp_prizes"]) / 2,
        }
        reasons: Counter[str] = Counter()
        for seat in (a, b):
            reasons.update(seat.get("reasons") or {})
        row["reasons"] = dict(reasons)
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def _mean(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] for key, *_ in FOES) / len(FOES)


def _worst(cells: dict[str, dict]) -> tuple[str, float]:
    key = min(FOES, key=lambda row: cells[row[0]]["wr"])[0]
    return key, cells[key]["wr"]


def _score(label: str, cells: dict[str, dict], games: int) -> dict:
    worst_key, worst = _worst(cells)
    played = {
        "eeeeeeek": sum(cells[key]["eeeeeeek"] for key, *_ in FOES) / len(FOES),
        "junk_arm": sum(cells[key]["junk_arm"] for key, *_ in FOES) / len(FOES),
        "survival_brace": sum(cells[key]["survival_brace"] for key, *_ in FOES) / len(FOES),
        "cleffa_play": sum(cells[key].get("cleffa_play", 0) for key, *_ in FOES) / len(FOES),
        "manaphy_play": sum(cells[key].get("manaphy_play", 0) for key, *_ in FOES) / len(FOES),
        "mill_attack": sum(cells[key]["mill_attack"] for key, *_ in FOES) / len(FOES),
    }
    return {
        "label": label,
        "note": NOTES[label],
        "counts": dict(Counter(LISTS[label])),
        "weighted": _weighted(cells),
        "se": _weighted_se(cells, games),
        "mean": _mean(cells),
        "worst": worst,
        "worst_foe": worst_key,
        "played": played,
        "cells": cells,
    }


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _signed(value: float) -> str:
    return f"{value:+.1%}"


def _markdown_final(report: dict) -> str:
    base = next((row for row in report["lists"] if row["label"] == "lock"), None)
    lines = [
        "# Mill draw package",
        "",
        "Level Ball finds any Pokémon with 90 HP or less, including Wugtrio. Nest Ball finds a Basic and benches it. "
        "HeartGold & SoulSilver Cleffa uses Eeeeeeek: shuffle the hand into the deck, draw 6, then Cleffa is Asleep. "
        "Sweet Sleeping Face prevents attack damage while it is Asleep. "
        "Survival Brace is the Twilight Masquerade ACE SPEC. A full-HP Pokémon that would be Knocked Out by attack damage is left at 10 HP, then the tool is discarded. "
        "Demolish ignores effects on the defending Pokémon, so Brace does not stop that attack. "
        "Junk Arm discards 2 cards from the hand and takes a Trainer from the discard, never another Junk Arm.",
        "",
        "The machine needs an evolution and an Energy after the basics are out. "
        "Eeeeeeek is used when the hand has neither. Brace attaches only to a full-HP Wugtrio. "
        "Junk Arm discards Nest Ball and Poffin once a Wiglett and a Sweet Sleeping Face are in play.",
        "",
        "Manaphy Wave Veil prevents damage done to benched Pokémon by attacks. "
        "Phantom Dive and Spooky Balloon place damage counters, and Wave Veil does not stop those, so Cleffa stays in the deck in those matches. "
        "Against bench damage, Poffin benches Manaphy and then Cleffa. Level Ball still searches for Wugtrio.",
        "",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.",
        f"- **Weights**: {', '.join(f'{key} {WEIGHTS[key]:.1%}' for key, *_ in FOES)}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        "The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in this same run.",
        "",
        "## Lists",
        "",
        "| List | Swap | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Cleffa | Manaphy | Attacks |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    ordered = report["lists"]
    for row in ordered:
        delta = "—" if base is None or row["label"] == "lock" else _signed(row["weighted"] - base["weighted"])
        played = row["played"]
        lines.append(
            f"| {row['label']} | {row['note']} | {_pct(row['weighted'])} | {_pct(row['se'])} | "
            f"{_pct(row['mean'])} | {_pct(row['worst'])} | {delta} | "
            f"{played['eeeeeeek']:.2f} | {played['cleffa_play']:.2f} | {played['manaphy_play']:.2f} | "
            f"{played['mill_attack']:.2f} |"
        )
    best = ordered[0]
    lines.extend(["", f"Highest weighted list in this run: `{best['label']}` at {_pct(best['weighted'])}.", ""])
    if base is None:
        return "\n".join(lines)
    lines.extend(
        [
            "## Foes",
            "",
            "| Foe | Lock | "
            + " | ".join(row["label"] for row in ordered if row["label"] != "lock")
            + " |",
            "| :--- | ---: | "
            + " | ".join("---:" for row in ordered if row["label"] != "lock")
            + " |",
        ]
    )
    for key, label, *_ in FOES:
        bits = [_pct(base["cells"][key]["wr"])]
        for row in ordered:
            if row["label"] == "lock":
                continue
            bits.append(_signed(row["cells"][key]["wr"] - base["cells"][key]["wr"]))
        lines.append(f"| {label} | " + " | ".join(bits) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    started = time.perf_counter()
    labels = _selected()
    _check_lists(labels)
    cache = _load_cache()
    scored = _evaluate(labels, GAMES, cache)
    rows = [_score(label, _combine(scored[label]), GAMES) for label in labels]
    rows.sort(key=lambda row: row["weighted"], reverse=True)
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weights": WEIGHTS,
        "lists": rows,
    }
    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(report, indent=2))
    MD_DEST.write_text(_markdown_final(report))
    best = rows[0]
    lock = next((row for row in rows if row["label"] == "lock"), None)
    if lock is None:
        print(f"best {best['label']} {_pct(best['weighted'])} ± {_pct(best['se'])}", flush=True)
    else:
        gap = best["weighted"] - lock["weighted"]
        se = (best["se"] ** 2 + lock["se"] ** 2) ** 0.5
        z = gap / se if se else 0.0
        print(
            f"best {best['label']} {_pct(best['weighted'])} vs lock {_pct(lock['weighted'])} "
            f"({_signed(gap)}, {z:.2f} SE)",
            flush=True,
        )
    print(f"wrote {DEST}", flush=True)


if __name__ == "__main__":
    main()
