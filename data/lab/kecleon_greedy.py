#!/usr/bin/env python3
"""One-copy search on the two-Latias Kecleon list.

The locked SET_KECLEON_NAMES list is not edited. The sample starts from that
lock with Battle Compressor and Boss's Orders removed and two Latias ex added.
Three named cards come in, one copy each: Counter Catcher, then Penny, then
Jirachi-EX. The cut is not named, so every other name still in the list is
tried. The best cut is kept, including when the rate falls, and the next card
is tried on that list. A second copy of the same card is not tried.

Seed 20261116. 400 games a seat. Both seats. Each cell starts at
random.Random(20261116). Weights are the 0-copy loss rates. Later games use
the foes whose weights reach 90%. Parked foes stay at the stored 0-copy rate.
"""

from __future__ import annotations

import json
import math
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.game import GameResult, play_game
from app.engine.legality import copy_violations
from app.engine.models import deck_archived_for_presets, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import LIST_KEYS, load_seed_payload
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_A_NAMES,
    SET_B_NAMES,
    SET_C60_NAMES,
    SET_C_NAMES,
    SET_D60_NAMES,
    SET_D_NAMES,
    SET_E_NAMES,
    SET_F_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_KECLEON_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_DOLL_NAMES,
    SET_ROAST_NAMES,
    SET_ROAST_TWO_FOREST_NAMES,
    SET_S60_NAMES,
    SET_S_NAMES,
    SET_SPARE_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_NAMES,
    SET_T_UNL_NAMES,
    build_doll_deck,
    build_fallback_deck,
    build_g30_deck,
    build_kecleon_deck,
    build_mill_deck,
    build_roast_deck,
    build_roast_two_forest_deck,
    fallback_named,
)

SEED = 20261116
GAMES = 400
WORKERS = int(os.environ.get("KECLEON_GREEDY_WORKERS", str(os.cpu_count() or 2)))
INCOMING = ("Counter Catcher", "Penny", "Jirachi-EX", "Prism Energy")
SUBJECT = "kecleon"

HERE = Path(__file__).resolve().parent
PARTIAL = HERE / "kecleon-greedy-partial.jsonl"
DEST = HERE / "kecleon-greedy.json"
MD_DEST = HERE / "kecleon-greedy.md"

# The strategy that already plays each live 60. A key missing from this map
# stops the run when that deck is a live 60.
STRATS = {
    "g": "g",
    "h": "nuzzle",
    "c60": "party",
    "d60": "demolish",
    "s60": "slash",
    "t60": "phantom",
    "t-meta": "phantom",
    "t-unl": "phantom",
    "g30": "celebration",
    "m60": "mew_baby",
    "l60": "aura",
    "mill": "mill",
    "doll": "doll",
    "celebi": "roast",
    "two-forest": "roast",
    "kecleon": "kecleon",
    "starmie": "starmie",
    "thorns": "thorns",
}

_NAMES = {
    "a": ("fallback", SET_A_NAMES),
    "b": ("fallback", SET_B_NAMES),
    "c": ("fallback", SET_C_NAMES),
    "d": ("fallback", SET_D_NAMES),
    "e": ("fallback", SET_E_NAMES),
    "f": ("fallback", SET_F_NAMES),
    "g": ("fallback", SET_G_NAMES),
    "h": ("fallback", SET_H_NAMES),
    "s": ("fallback", SET_S_NAMES),
    "t": ("fallback", SET_T_NAMES),
    "c60": ("fallback", SET_C60_NAMES),
    "d60": ("fallback", SET_D60_NAMES),
    "m60": ("fallback", SET_M60_NAMES),
    "s60": ("fallback", SET_S60_NAMES),
    "t60": ("fallback", SET_T60_NAMES),
    "t-meta": ("fallback", SET_T_META_NAMES),
    "t-unl": ("fallback", SET_T_UNL_NAMES),
    "g30": ("g30", SET_G30_NAMES),
    "l60": ("fallback", SET_L60_NAMES),
    "mill": ("mill", SET_MILL_NAMES),
    "doll": ("doll", SET_DOLL_NAMES),
    "celebi": ("celebi", SET_ROAST_NAMES),
    "two-forest": ("two-forest", SET_ROAST_TWO_FOREST_NAMES),
    "kecleon": ("kecleon", SET_KECLEON_NAMES),
    "spare": ("fallback", SET_SPARE_NAMES),
}

EVENT_KEYS = (
    "counter_catcher",
    "bounce_penny",
    "bounce_heal",
    "stellar_guidance",
    "scoundrel_ring",
    "colorful_whip",
    "colorful_whip_types",
    "prism_any",
)

# Same buckets as data/lab/set_doll_losses.py _kind.
_KNOWN_KINDS = (
    "prizes",
    "empty",
    "foe_empty",
    "decked",
    "foe_decked",
    "no_basic",
    "foe_no_basic",
    "turn_prizes",
    "turn_hp",
    "tie",
)


def _kind(result: GameResult, seat: str) -> tuple[str, str]:
    """(outcome, kind). outcome is win, loss, or tie from the subject's seat."""
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


def _cards_for(builder: str, names: tuple[str, ...] | list[str]):
    if builder == "g30":
        return build_g30_deck()
    if builder == "mill":
        return build_mill_deck()
    if builder == "doll":
        return build_doll_deck()
    if builder == "celebi":
        return build_roast_deck()
    if builder == "two-forest":
        return build_roast_two_forest_deck()
    if builder == "kecleon":
        return build_kecleon_deck()
    return build_fallback_deck(list(names))


def _subject_cards(names: tuple[str, ...] | list[str]):
    return [fallback_named(name) for name in names]


def starting_list() -> list[str]:
    """Locked Kecleon, minus Battle Compressor and Boss's Orders, plus two Latias ex."""
    names = list(SET_KECLEON_NAMES)
    if names.count("Battle Compressor") != 1 or names.count("Boss's Orders") != 1:
        raise SystemExit("the lock no longer has one Battle Compressor and one Boss's Orders")
    names.remove("Battle Compressor")
    names.remove("Boss's Orders")
    names.extend(["Latias ex", "Latias ex"])
    if names.count("Latias ex") != 2 or len(names) != 60:
        raise SystemExit(f"start list is {len(names)} cards with {names.count('Latias ex')} Latias ex")
    return names


def _check_list(names: list[str]) -> list[str]:
    pile = _subject_cards(names)
    if len(pile) != 60:
        raise SystemExit(f"list has {len(pile)} cards")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"list is illegal: {bad}")
    return [item for item in bad]


def printed(name: str) -> str:
    card = fallback_named(name)
    bits: list[str] = []
    text = " ".join((card.text or "").split())
    if text:
        bits.append(text)
    for abi in card.abilities:
        line = " ".join((abi.text or "").split())
        if line and line not in text:
            bits.append(f"{abi.name}: {line}")
    for atk in card.attacks:
        line = " ".join((atk.text or "").split())
        if line and line not in text:
            bits.append(f"{atk.name}: {line}")
    if not bits and card.is_energy:
        return f"Basic {card.energy_type or ''} Energy.".replace("  ", " ")
    return " ".join(bits) if bits else card.name


def discover() -> dict:
    payload = load_seed_payload()
    foes = []
    archived = []
    short = []
    not_list = []
    for key in LIST_KEYS:
        blob = payload.get(key) or {}
        builder, names = _NAMES[key]
        deck_id = blob.get("id") or f"seed-{key}"
        label = blob.get("name") or key
        kind = blob.get("kind")
        presets = default_rule_presets_for(deck_id)
        if blob.get("archived") is None:
            is_archived = deck_archived_for_presets(presets)
        else:
            is_archived = bool(blob.get("archived"))
        try:
            built = _cards_for(builder, names)
            count = len(built)
            err = None
        except Exception as exc:  # a skipped pile may name a card the builder rejects
            built = None
            count = len(blob.get("cards") or [])
            err = str(exc)
        row = {
            "key": key,
            "label": label,
            "id": deck_id,
            "kind": kind,
            "cards": count,
            "presets": list(presets),
            "archived": is_archived,
            "error": err,
        }
        if kind != "list":
            not_list.append(row)
            continue
        if is_archived:
            archived.append(row)
            continue
        if built is None:
            raise SystemExit(f"{key} did not build: {err}")
        if count != 60:
            short.append(row)
            continue
        strat = STRATS.get(key)
        if not strat:
            raise SystemExit(f"no strategy plays live 60 {key} ({label})")
        bad = copy_violations(built, standard_60_rules())
        if bad:
            raise SystemExit(f"{key} is illegal under standard 60: {bad}")
        foes.append(
            {
                "key": key,
                "label": label,
                "id": deck_id,
                "strategy": strat,
                "builder": builder,
                "names": tuple(names),
                "cards": count,
            }
        )
    have = {tuple(sorted(card.name for card in _cards_for(foe["builder"], foe["names"]))) for foe in foes}
    for key, label, names, strat in (
        ("starmie", "Mega Starmie", SET_STARMIE60_NAMES, "starmie"),
        ("thorns", "Iron Thorns", IRON_THORNS_NAMES, "thorns"),
    ):
        built = _cards_for("fallback", names)
        sig = tuple(sorted(card.name for card in built))
        if sig in have:
            continue
        if len(built) != 60:
            raise SystemExit(f"{key} has {len(built)} cards")
        bad = copy_violations(built, standard_60_rules())
        if bad:
            raise SystemExit(f"{key} is illegal under standard 60: {bad}")
        foes.append(
            {
                "key": key,
                "label": label,
                "id": key,
                "strategy": strat,
                "builder": "fallback",
                "names": tuple(names),
                "cards": 60,
            }
        )
        have.add(sig)
    spare = payload.get("spare") or {}
    if spare:
        presets = default_rule_presets_for(spare.get("id") or "seed-spare")
        not_list.append(
            {
                "key": "spare",
                "label": spare.get("name") or "Spare Cards",
                "id": spare.get("id") or "seed-spare",
                "kind": spare.get("kind") or "spare",
                "cards": len(spare.get("cards") or []),
                "presets": list(presets),
                "archived": deck_archived_for_presets(presets) if spare.get("archived") is None else bool(spare.get("archived")),
                "error": None,
            }
        )
    return {"foes": foes, "archived": archived, "short": short, "not_list": not_list}


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str) -> str:
    return f"{SEED}|{GAMES}|{seat}|{foe_key}|{'/'.join(names)}"


def _load_cache() -> dict[str, dict]:
    found: dict[str, dict] = {}
    if not PARTIAL.exists():
        return found
    for line in PARTIAL.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        found[row["key"]] = row["cell"]
    return found


def _append(key: str, cell: dict) -> None:
    with PARTIAL.open("a") as handle:
        handle.write(json.dumps({"key": key, "cell": cell}) + "\n")
        handle.flush()


def _run(names: tuple[str, ...], foe: dict, seat: str, games: int, seed: int) -> dict:
    subject = _subject_cards(names)
    other = _cards_for(foe["builder"], foe["names"])
    if seat == "a":
        cards_a, cards_b = subject, other
        strat_a, strat_b = SUBJECT, foe["strategy"]
    else:
        cards_a, cards_b = other, subject
        strat_a, strat_b = foe["strategy"], SUBJECT
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    events: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        if result.winner == seat:
            wins += 1
        ev = result.events or {}
        events["counter_catcher"] += int(ev.get(f"counter_catcher_{seat}", 0))
        events["bounce_penny"] += int(ev.get(f"bounce_{seat}:Penny", 0))
        events["bounce_heal"] += int(ev.get(f"bounce_heal_{seat}", 0))
        events["stellar_guidance"] += int(ev.get(f"stellar_guidance_{seat}", 0))
        events["scoundrel_ring"] += int(ev.get(f"scoundrel_ring_{seat}", 0))
        events["colorful_whip"] += int(ev.get("colorful_whip", 0))
        events["colorful_whip_types"] += int(ev.get("colorful_whip_types", 0))
        events["prism_any"] += int(ev.get(f"prism_any_{seat}", 0))
        _outcome, kind = _kind(result, seat)
        reasons[kind] += 1
    return {"wins": wins, "games": games, "events": dict(events), "reasons": dict(reasons)}


def _evaluate(names: list[str], foes: list[dict], cache: dict[str, dict], label: str) -> dict[str, dict]:
    frozen = tuple(names)
    out: dict[str, dict] = {}
    jobs = []
    for foe in foes:
        for seat in ("a", "b"):
            key = _cache_key(frozen, foe["key"], seat)
            cached = cache.get(key)
            if cached is not None:
                out.setdefault(foe["key"], {})[seat] = cached
                continue
            jobs.append((foe, seat, key))
    print(f"{label}: {len(jobs)} cells to play, {GAMES} games", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    workers = max(1, min(WORKERS, len(jobs)))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {
            pool.submit(_run, frozen, foe, seat, GAMES, SEED): (foe["key"], seat, key) for foe, seat, key in jobs
        }
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out.setdefault(foe_key, {})[seat] = cell
            done += 1
            elapsed = time.perf_counter() - started
            left = (total - done) * elapsed / done
            print(
                f"  {done}/{total} {foe_key} seat {seat} {cell['wins']}/{GAMES} ~{left / 60:.1f} min",
                flush=True,
            )
    return out


def _mean(pair: dict) -> float:
    return (pair["a"]["wins"] + pair["b"]["wins"]) / (pair["a"]["games"] + pair["b"]["games"])


def _seat_var(cell: dict) -> float:
    p = cell["wins"] / cell["games"]
    return p * (1.0 - p) / cell["games"]


def _weights(cells: dict[str, dict]) -> dict[str, float]:
    raw = {foe: max(1e-6, 1.0 - _mean(pair)) for foe, pair in cells.items()}
    total = sum(raw.values())
    return {foe: value / total for foe, value in raw.items()}


def _active_set(weights: dict[str, float]) -> tuple[list[str], list[str]]:
    ranked = sorted(weights, key=lambda foe: (-weights[foe], foe))
    active: list[str] = []
    cum = 0.0
    for foe in ranked:
        active.append(foe)
        cum += weights[foe]
        if cum + 1e-9 >= 0.90:
            break
    parked = [foe for foe in ranked if foe not in active]
    return active, parked


def _view(active_cells: dict[str, dict], parked_cells: dict[str, dict]) -> dict[str, dict]:
    merged = {foe: pair for foe, pair in parked_cells.items()}
    merged.update(active_cells)
    return merged


def _rate(view: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(weights[foe] * _mean(view[foe]) for foe in weights)


def _se(view: dict[str, dict], weights: dict[str, float]) -> float:
    var = 0.0
    for foe, weight in weights.items():
        pair = view[foe]
        var += (weight**2) * (_seat_var(pair["a"]) + _seat_var(pair["b"])) / 4
    return math.sqrt(var)


def _gap_se(before: dict[str, dict], after: dict[str, dict], weights: dict[str, float], active: list[str]) -> float:
    var = 0.0
    for foe in active:
        weight = weights[foe]
        left = before[foe]
        right = after[foe]
        var += (weight**2) * (
            (_seat_var(left["a"]) + _seat_var(left["b"]) + _seat_var(right["a"]) + _seat_var(right["b"])) / 4
        )
    return math.sqrt(var)


def _unweighted(view: dict[str, dict], active: list[str]) -> float:
    return sum(_mean(view[foe]) for foe in active) / len(active)


def _worst(view: dict[str, dict], active: list[str]) -> tuple[float, str]:
    rows = [(_mean(view[foe]), foe) for foe in active]
    rate, foe = min(rows, key=lambda row: (row[0], row[1]))
    return rate, foe


def _share(view: dict[str, dict], weights: dict[str, float], bucket: str, field: str) -> float:
    total = 0.0
    for foe, weight in weights.items():
        pair = view[foe]
        seats = []
        for seat in ("a", "b"):
            cell = pair[seat]
            seats.append(cell[field].get(bucket, 0) / cell["games"])
        total += weight * sum(seats) / 2
    return total


def _pct(value: float) -> str:
    return f"{100 * value:.2f}%"


def _pp(value: float) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{100 * value:.2f} pp"


def _ratio(gap: float, gap_se: float) -> str:
    if gap_se <= 0:
        return "n/a"
    return f"{gap / gap_se:.2f}"


def _dump(path: Path, text: str) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    tmp.replace(path)


def _public_foe(foe: dict) -> dict:
    return {
        "key": foe["key"],
        "label": foe["label"],
        "id": foe["id"],
        "strategy": foe["strategy"],
        "cards": foe["cards"],
    }


def _public_cell(cell: dict) -> dict:
    return {
        "wins": cell["wins"],
        "games": cell["games"],
        "wr": cell["wins"] / cell["games"],
        "events": cell["events"],
        "reasons": cell["reasons"],
    }


def _reason(
    incoming: str,
    cut: str,
    copies: int,
    before: dict[str, dict],
    after: dict[str, dict],
    start: dict[str, dict],
    weights: dict[str, float],
    active: list[str],
    cuts: list[dict],
    labels: dict[str, str],
) -> str:
    gap_prev = _rate(after, weights) - _rate(before, weights)
    gap_start = _rate(after, weights) - _rate(start, weights)
    se_prev = _gap_se(before, after, weights, active)
    se_start = _gap_se(start, after, weights, active)
    contrib = []
    for foe in active:
        delta = _mean(after[foe]) - _mean(before[foe])
        contrib.append((weights[foe] * delta, foe, delta))
    contrib.sort(key=lambda row: row[0], reverse=True)
    up = [row for row in contrib if row[0] > 0][:3]
    down = [row for row in contrib if row[0] < 0][-3:]
    by_mean = max(cuts, key=lambda row: (row["unweighted"], -row["copies"], row["cut"]))
    parts = [
        f"{incoming} says: \"{printed(incoming)}\" {cut} ({copies} in the list before this cut) says: \"{printed(cut)}\"",
        (
            f"Under the 0-copy weights this list is {_pct(_rate(after, weights))} "
            f"(SE {_pct(_se(after, weights))}). Against the start the gap is {_pp(gap_start)} "
            f"(gap SE {_pct(se_start)}, {_ratio(gap_start, se_start)} combined). "
            f"Against the previous list the gap is {_pp(gap_prev)} "
            f"(gap SE {_pct(se_prev)}, {_ratio(gap_prev, se_prev)} combined)."
        ),
    ]
    if up or down:
        bits = []
        for amount, foe, delta in up:
            bits.append(f"{labels[foe]} {_pp(amount)} of the weighted rate ({_pp(delta)} in the cell)")
        for amount, foe, delta in reversed(down):
            bits.append(f"{labels[foe]} {_pp(amount)} of the weighted rate ({_pp(delta)} in the cell)")
        parts.append("The foes that move the rate: " + "; ".join(bits) + ".")
    else:
        parts.append("No active foe's cell moved, so the foes do not explain a rate change.")
    if by_mean["cut"] == cut:
        parts.append(
            f"The unweighted mean of the active set is {_pct(_unweighted(after, active))} "
            "and it keeps this same cut."
        )
    else:
        parts.append(
            f"The unweighted mean of the active set is {_pct(_unweighted(after, active))}. "
            f"That mean would keep {by_mean['cut']} at {_pct(by_mean['unweighted'])} "
            f"instead of this cut at {_pct(_unweighted(after, active))}. "
            "The keeper is still the 0-copy loss weights."
        )
    counter_bits = []
    for key in EVENT_KEYS:
        after_rate = _share(after, weights, key, "events")
        before_rate = _share(before, weights, key, "events")
        counter_bits.append(f"{key} {before_rate:.3f} to {after_rate:.3f} per game")
    parts.append(
        "Weighted sentence counters, previous list then this list: " + "; ".join(counter_bits) + ". "
        "colorful_whip has no seat on the event, so the Kecleon mirror counts both players. "
        "The leaving card has no separate counter in this sample."
    )
    kinds = set(_KNOWN_KINDS)
    for foe in weights:
        for seat in ("a", "b"):
            kinds.update(before[foe][seat]["reasons"])
            kinds.update(after[foe][seat]["reasons"])
    moved = []
    for kind in sorted(kinds):
        left = _share(before, weights, kind, "reasons")
        right = _share(after, weights, kind, "reasons")
        if abs(right - left) >= 0.002 or kind == "prizes":
            moved.append(f"{kind} {_pct(left)} to {_pct(right)}")
    parts.append("Weighted end reasons from the subject's seat: " + "; ".join(moved) + ".")
    own = {
        "Counter Catcher": "counter_catcher",
        "Penny": "bounce_penny",
        "Jirachi-EX": "stellar_guidance",
    }.get(incoming)
    fired = _share(after, weights, own, "events") if own else 0.0
    before_fired = _share(before, weights, own, "events") if own else 0.0
    if own and fired <= before_fired + 1e-9 and fired < 0.01:
        closing = "The sample does not show that sentence firing."
    elif abs(gap_prev) < se_prev:
        closing = "The counter can move while this cut's win rate stays inside one combined standard error."
    else:
        lead = up[0][1] if gap_prev >= 0 and up else (down[-1][1] if down else active[0])
        closing = (
            f"The printed line is what the {labels[lead]} cell and the end-reason mix above are responding to."
        )
    parts.append(closing)
    return " ".join(parts)


def _markdown(state: dict) -> str:
    foes = state["foes"]
    labels = {foe["key"]: foe["label"] for foe in foes}
    lines = [
        "# Kecleon, one-copy swaps",
        "",
        "One step removes one copy of one other card and adds one copy of the named card. "
        "The list stays 60. The locked `SET_KECLEON_NAMES` list is not assigned and is not changed. "
        "The mirror plays that locked list.",
        "",
        "The starting 60 is the lock with one Battle Compressor and one Boss's Orders removed "
        "and two Latias ex added. Latias ex says: "
        f"\"{state['quotes']['Latias ex']}\"",
        "",
        "The rounds add one copy each, in this order: "
        + ", ".join(state["incoming"])
        + ". "
        "A second copy of the same card is not tried. The request names these rounds, not a walk "
        "to the 4-copy cap. Every other name still in the list is a cut. Nothing is protected. "
        "The step keeps the highest 0-copy weighted rate, then the higher worst active foe, "
        "then the cut that had more copies, then the name. A dip is kept.",
        "",
        f"Seed {state['seed']}. {state['games']} games per seat. Both seats. "
        "Each cell starts a new `random.Random` at that seed and plays its games on that generator. "
        "The foe, the seat, and the step are not mixed into the seed. Two lists diverge after the "
        "first choice that consumes a different number of draws.",
        "",
        "Rules are standard 60. Weights are `max(1e-6, 1 - win rate)` on the starting list, "
        "divided by the sum. A tie is not a win, so it sits on the loss side of that formula. "
        "The same vector scores every later list. Parked foes keep their 0-copy win rate and "
        "are not replayed. Gap standard error is summed on the active set only.",
        "",
        f"Elapsed {state['elapsed_s']:.0f}s.",
        "",
        "## Field",
        "",
        "0-copy foes:",
        "",
    ]
    for foe in foes:
        lines.append(f"- {foe['key']} — {foe['label']} — {foe['strategy']} — {foe['cards']} cards")
    lines.extend(["", "Archived, no row:", ""])
    for row in state["archived"]:
        lines.append(f"- {row['key']} — {row['label']} — {row['cards']} cards — presets {', '.join(row['presets'])}")
    lines.extend(["", "Not 60 cards, no row:", ""])
    for row in state["short"]:
        lines.append(f"- {row['key']} — {row['label']} — {row['cards']} cards — presets {', '.join(row['presets'])}")
    lines.extend(["", "Not a list, no row:", ""])
    for row in state["not_list"]:
        lines.append(
            f"- {row['key']} — {row['label']} — kind {row['kind']} — {row['cards']} cards — "
            f"archived {row.get('archived')}"
        )
    if not state.get("weights"):
        lines.extend(["", "The 0-copy pass has not finished. `complete` is false.", ""])
        return "\n".join(lines)

    weights = state["weights"]
    lines.extend(["", "## 0-copy weights", ""])
    lines.append(f"Active set cumulative weight {_pct(state['active_weight'])}.")
    lines.append("")
    lines.append("| Foe | Weight | Win rate | Seat A | Seat B |")
    lines.append("| :--- | ---: | ---: | ---: | ---: |")
    ranked = sorted(weights, key=lambda foe: (-weights[foe], foe))
    start_cells = state["start_cells"]
    for foe in ranked:
        pair = start_cells[foe]
        mark = "active" if foe in state["active"] else "parked"
        lines.append(
            f"| {labels[foe]} ({mark}) | {_pct(weights[foe])} | {_pct(_mean(pair))} | "
            f"{_pct(pair['a']['wins'] / pair['a']['games'])} | {_pct(pair['b']['wins'] / pair['b']['games'])} |"
        )
    lines.append("")
    lines.append(
        f"Unweighted mean of every live 60: {_pct(state['start_unweighted_all'])}. "
        f"Unweighted mean of the active set: {_pct(state['start_unweighted_active'])}. "
        f"Worst active foe: {labels[state['start_worst_foe']]} {_pct(state['start_worst'])}."
    )
    lines.append("")
    lines.append("Parked foes stay at the win rate in that table.")
    lines.extend(["", "## Path", ""])
    lines.append(
        "| Step | Card in | Cut | Weighted | SE | Unweighted | Worst | Δ start | Δ previous | "
        "Catcher | Penny | Jirachi | Whip | Prism |"
    )
    lines.append("| :--- | :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for row in state["path"]:
        lines.append(
            f"| {row['step']} | {row['incoming']} | {row['cut']} | {_pct(row['weighted'])} | {_pct(row['se'])} | "
            f"{_pct(row['unweighted'])} | {labels[row['worst_foe']]} {_pct(row['worst'])} | "
            f"{_pp(row['delta_start'])} | {_pp(row['delta_prev'])} | {row['counter_catcher']:.3f} | "
            f"{row['bounce_penny']:.3f} | {row['stellar_guidance']:.3f} | {row['colorful_whip']:.3f} | "
            f"{row.get('prism_any', 0):.3f} |"
        )
    lines.extend(["", "## Decision", ""])
    lines.append(state["decision"])
    lines.append("")
    lines.append(
        "Each step took the best cut on this one seed, so the path sits a little high. "
        "There is no second seed."
    )
    for round_row in state["rounds"]:
        lines.extend(["", f"## {round_row['incoming']}", ""])
        lines.append("Quotes: " + round_row["incoming"] + " — " + state["quotes"][round_row["incoming"]])
        lines.append("")
        lines.append(
            "| Cut | Copies | Weighted | SE | Unweighted | Worst | Δ previous | gap/SE | Δ start |"
        )
        lines.append("| :--- | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: |")
        for cut in round_row["cuts"]:
            lines.append(
                f"| {cut['cut']} | {cut['copies']} | {_pct(cut['weighted'])} | {_pct(cut['se'])} | "
                f"{_pct(cut['unweighted'])} | {labels[cut['worst_foe']]} {_pct(cut['worst'])} | "
                f"{_pp(cut['delta_prev'])} | {cut['ratio_prev']} | {_pp(cut['delta_start'])} |"
            )
        lines.append("")
        for paragraph in round_row["reasons"]:
            lines.append(paragraph)
            lines.append("")
    kept = state["kept_cells"]
    lines.extend(["", "## Foe table at the kept list", ""])
    lines.append(state["kept_label"])
    lines.append("")
    lines.append("| Foe | Weight | A | B | Mean | Δ start |")
    lines.append("| :--- | ---: | ---: | ---: | ---: | ---: |")
    for foe in ranked:
        pair = kept[foe]
        start_pair = start_cells[foe]
        lines.append(
            f"| {labels[foe]} | {_pct(weights[foe])} | {_pct(pair['a']['wins'] / pair['a']['games'])} | "
            f"{_pct(pair['b']['wins'] / pair['b']['games'])} | {_pct(_mean(pair))} | "
            f"{_pp(_mean(pair) - _mean(start_pair))} |"
        )
    if state.get("path_cells") and state["path_label"] != state["kept_label"]:
        lines.extend(["", "## Foe table after the rounds", ""])
        lines.append(state["path_label"])
        lines.append("")
        lines.append("| Foe | Weight | A | B | Mean | Δ start |")
        lines.append("| :--- | ---: | ---: | ---: | ---: | ---: |")
        for foe in ranked:
            pair = state["path_cells"][foe]
            start_pair = start_cells[foe]
            lines.append(
                f"| {labels[foe]} | {_pct(weights[foe])} | {_pct(pair['a']['wins'] / pair['a']['games'])} | "
                f"{_pct(pair['b']['wins'] / pair['b']['games'])} | {_pct(_mean(pair))} | "
                f"{_pp(_mean(pair) - _mean(start_pair))} |"
            )
    lines.append("")
    lines.append(f"`complete` is {str(state['complete']).lower()}.")
    lines.append("")
    return "\n".join(lines)


def _snapshot(names: list[str], view: dict[str, dict], weights: dict[str, float], active: list[str], start_rate: float, prev_rate: float) -> dict:
    worst, worst_foe = _worst(view, active)
    return {
        "names": list(names),
        "weighted": _rate(view, weights),
        "se": _se(view, weights),
        "unweighted": _unweighted(view, active),
        "worst": worst,
        "worst_foe": worst_foe,
        "delta_start": _rate(view, weights) - start_rate,
        "delta_prev": _rate(view, weights) - prev_rate,
        "counter_catcher": _share(view, weights, "counter_catcher", "events"),
        "bounce_penny": _share(view, weights, "bounce_penny", "events"),
        "stellar_guidance": _share(view, weights, "stellar_guidance", "events"),
        "colorful_whip": _share(view, weights, "colorful_whip", "events"),
        "prism_any": _share(view, weights, "prism_any", "events"),
        "cells": {foe: {"a": _public_cell(view[foe]["a"]), "b": _public_cell(view[foe]["b"])} for foe in weights},
    }


def _write(state: dict) -> None:
    _dump(DEST, json.dumps(state, indent=2) + "\n")
    _dump(MD_DEST, _markdown(state))


def _base_state(field: dict, start: list[str], started: float) -> dict:
    quotes = {name: printed(name) for name in ("Latias ex", *INCOMING)}
    return {
        "seed": SEED,
        "games": GAMES,
        "complete": False,
        "started": started,
        "elapsed_s": time.time() - started,
        "subject_strategy": SUBJECT,
        "start": list(start),
        "incoming": list(INCOMING),
        "quotes": quotes,
        "foes": [_public_foe(foe) for foe in field["foes"]],
        "archived": field["archived"],
        "short": field["short"],
        "not_list": field["not_list"],
        "weights": None,
        "active": [],
        "parked": [],
        "active_weight": 0.0,
        "start_cells": {},
        "start_unweighted_all": 0.0,
        "start_unweighted_active": 0.0,
        "start_worst": 0.0,
        "start_worst_foe": "",
        "path": [],
        "rounds": [],
        "decision": "The 0-copy pass has not finished.",
        "kept_label": "",
        "kept_list": [],
        "kept_cells": {},
        "path_label": "",
        "path_list": list(start),
        "path_cells": {},
        "note": (
            "The script records the sample. It does not assign SET_KECLEON_NAMES. "
            "Each named card is one copy. The cut search keeps the best cut and continues."
        ),
    }


def main() -> None:
    field = discover()
    start = starting_list()
    _check_list(start)
    print(f"start {len(start)} cards, {len(field['foes'])} foes", flush=True)
    for foe in field["foes"]:
        print(f"  foe {foe['key']} {foe['label']} {foe['strategy']}", flush=True)
    if "--field" in sys.argv:
        print("archived", [row["key"] for row in field["archived"]])
        print("short", [(row["key"], row["cards"]) for row in field["short"]])
        print("not_list", [row["key"] for row in field["not_list"]])
        return
    if "--smoke" in sys.argv:
        foe = next(row for row in field["foes"] if row["key"] == "m60")
        cell = _run(tuple(start), foe, "a", 2, SEED)
        print(json.dumps(cell))
        return
    started = time.time()
    if DEST.exists():
        try:
            previous = json.loads(DEST.read_text())
            if previous.get("seed") == SEED and previous.get("started"):
                started = float(previous["started"])
        except json.JSONDecodeError:
            pass
    state = _base_state(field, start, started)
    state["elapsed_s"] = time.time() - started
    _write(state)
    cache = _load_cache()
    foes = field["foes"]
    by_key = {foe["key"]: foe for foe in foes}
    start_cells = _evaluate(start, foes, cache, "0-copy")
    weights = _weights(start_cells)
    active, parked = _active_set(weights)
    active_foes = [by_key[key] for key in active]
    start_rate = _rate(start_cells, weights)
    worst, worst_foe = _worst(start_cells, active)
    labels = {foe["key"]: foe["label"] for foe in foes}
    state.update(
        {
            "weights": weights,
            "active": active,
            "parked": parked,
            "active_weight": sum(weights[foe] for foe in active),
            "start_cells": {foe: {"a": _public_cell(start_cells[foe]["a"]), "b": _public_cell(start_cells[foe]["b"])} for foe in weights},
            "start_unweighted_all": sum(_mean(start_cells[foe]) for foe in weights) / len(weights),
            "start_unweighted_active": _unweighted(start_cells, active),
            "start_worst": worst,
            "start_worst_foe": worst_foe,
            "elapsed_s": time.time() - started,
            "decision": (
                f"0-copy weighted rate {_pct(start_rate)} (SE {_pct(_se(start_cells, weights))}). "
                f"Active {', '.join(labels[foe] for foe in active)}."
            ),
        }
    )
    state["kept_label"] = "start"
    state["kept_list"] = list(start)
    state["kept_cells"] = state["start_cells"]
    state["path_label"] = "start"
    state["path_list"] = list(start)
    state["path_cells"] = state["start_cells"]
    snap = _snapshot(start, start_cells, weights, active, start_rate, start_rate)
    state["path"] = [
        {
            "step": "0",
            "incoming": "—",
            "cut": "—",
            **{key: snap[key] for key in (
                "weighted", "se", "unweighted", "worst", "worst_foe", "delta_start", "delta_prev",
                "counter_catcher", "bounce_penny", "stellar_guidance", "colorful_whip", "prism_any",
            )},
        }
    ]
    _write(state)
    print(
        f"weights frozen, active {len(active)}/{len(foes)} cum {state['active_weight']:.3f}",
        flush=True,
    )

    current = list(start)
    previous_cells = start_cells
    previous_rate = start_rate
    views = [("start", list(start), start_cells)]
    for step, incoming in enumerate(INCOMING, start=1):
        counts = Counter(current)
        cut_rows = []
        measured: dict[str, dict] = {}
        for cut in sorted(counts):
            trial = list(current)
            trial.remove(cut)
            trial.append(incoming)
            try:
                _check_list(trial)
            except SystemExit as exc:
                print(f"skip {cut}: {exc}", flush=True)
                continue
            cells = _evaluate(trial, active_foes, cache, f"{step} {incoming} minus {cut}")
            view = _view(cells, {foe: start_cells[foe] for foe in parked})
            # Step 1's previous map is the full 0-copy pass. Later steps keep the
            # active cells only, and the parked foes come back from that pass.
            if step == 1:
                full_prev = start_cells
            else:
                full_prev = _view(previous_cells, {foe: start_cells[foe] for foe in parked})
            worst_rate, worst_name = _worst(view, active)
            row = {
                "cut": cut,
                "copies": counts[cut],
                "names": trial,
                "weighted": _rate(view, weights),
                "se": _se(view, weights),
                "unweighted": _unweighted(view, active),
                "worst": worst_rate,
                "worst_foe": worst_name,
                "delta_prev": _rate(view, weights) - previous_rate,
                "delta_start": _rate(view, weights) - start_rate,
                "gap_se_prev": _gap_se(full_prev, view, weights, active),
                "gap_se_start": _gap_se(start_cells, view, weights, active),
            }
            row["ratio_prev"] = _ratio(row["delta_prev"], row["gap_se_prev"])
            cut_rows.append(row)
            measured[cut] = view
        cut_rows.sort(key=lambda row: (-row["weighted"], -row["worst"], -row["copies"], row["cut"]))
        kept = cut_rows[0]
        kept_view = measured[kept["cut"]]
        reasons = []
        for row in cut_rows:
            moved = abs(row["delta_prev"]) >= row["gap_se_prev"] and row["gap_se_prev"] > 0
            if row["cut"] != kept["cut"] and not moved:
                continue
            full_prev = start_cells if step == 1 else _view(previous_cells, {foe: start_cells[foe] for foe in parked})
            reasons.append(
                _reason(
                    incoming,
                    row["cut"],
                    row["copies"],
                    full_prev,
                    measured[row["cut"]],
                    start_cells,
                    weights,
                    active,
                    cut_rows,
                    labels,
                )
            )
        state["rounds"].append(
            {
                "incoming": incoming,
                "kept_cut": kept["cut"],
                "cuts": [
                    {
                        "cut": row["cut"],
                        "copies": row["copies"],
                        "names": row["names"],
                        "weighted": row["weighted"],
                        "se": row["se"],
                        "unweighted": row["unweighted"],
                        "worst": row["worst"],
                        "worst_foe": row["worst_foe"],
                        "delta_prev": row["delta_prev"],
                        "delta_start": row["delta_start"],
                        "gap_se_prev": row["gap_se_prev"],
                        "gap_se_start": row["gap_se_start"],
                        "ratio_prev": row["ratio_prev"],
                        "cells": {
                            foe: {
                                "a": _public_cell(measured[row["cut"]][foe]["a"]),
                                "b": _public_cell(measured[row["cut"]][foe]["b"]),
                            }
                            for foe in weights
                        },
                    }
                    for row in cut_rows
                ],
                "reasons": reasons,
            }
        )
        state["path"].append(
            {
                "step": str(step),
                "incoming": incoming,
                "cut": kept["cut"],
                "weighted": kept["weighted"],
                "se": kept["se"],
                "unweighted": kept["unweighted"],
                "worst": kept["worst"],
                "worst_foe": kept["worst_foe"],
                "delta_start": kept["delta_start"],
                "delta_prev": kept["delta_prev"],
                "counter_catcher": _share(kept_view, weights, "counter_catcher", "events"),
                "bounce_penny": _share(kept_view, weights, "bounce_penny", "events"),
                "stellar_guidance": _share(kept_view, weights, "stellar_guidance", "events"),
                "colorful_whip": _share(kept_view, weights, "colorful_whip", "events"),
            }
        )
        current = list(kept["names"])
        previous_cells = {foe: kept_view[foe] for foe in active}
        previous_rate = kept["weighted"]
        views.append((f"{step} {incoming} minus {kept['cut']}", list(current), kept_view))
        best = max(views, key=lambda item: _rate(item[2], weights))
        state["decision"] = (
            f"After {incoming}, the path cuts {kept['cut']} "
            f"({_pct(kept['weighted'])}, {_pp(kept['delta_start'])} against the start, "
            f"{_pp(kept['delta_prev'])} against the previous list). "
            "The best cut on this seed is a little high."
        )
        state["path_label"] = views[-1][0]
        state["path_list"] = list(current)
        state["path_cells"] = {
            foe: {"a": _public_cell(views[-1][2][foe]["a"]), "b": _public_cell(views[-1][2][foe]["b"])}
            for foe in weights
        }
        state["kept_label"] = best[0]
        state["kept_list"] = list(best[1])
        state["kept_cells"] = {
            foe: {"a": _public_cell(best[2][foe]["a"]), "b": _public_cell(best[2][foe]["b"])} for foe in weights
        }
        state["elapsed_s"] = time.time() - started
        state["complete"] = step == len(INCOMING)
        if state["complete"]:
            rates = [(label, _rate(view, weights)) for label, _names, view in views]
            winner = max(rates, key=lambda item: item[1])
            state["decision"] = (
                f"The rounds are on the path. The highest 0-copy weighted rate is {winner[0]} "
                f"at {_pct(winner[1])}. The path ends at {views[-1][0]} at {_pct(rates[-1][1])}. "
                "Each step took the best cut on this seed, so that path sits a little high. "
                "The script does not write the list into SET_KECLEON_NAMES."
            )
        _write(state)
        print(f"kept {incoming} by cutting {kept['cut']} -> {_pct(kept['weighted'])}", flush=True)


if __name__ == "__main__":
    main()
