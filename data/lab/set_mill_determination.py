#!/usr/bin/env python3
"""Greedy Lillie's Determination on the locked Wiglett Mill.

The recorded search started from the zero-Determination Wiglett Mill. Each step
replaces one copy of one other card with one Lillie's Determination and runs
through four copies. The point estimate with the largest gain over that start
is four copies. The fourth step is inside one combined standard error, and the
lock keeps three: one Ignition Energy, Pichu, and Counter Catcher. Wugtrio
stays at four. This file does not assign SET_MILL_NAMES.
"""

from __future__ import annotations

import json
import os
import random
import sys
import time
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.game import play_game
from app.engine.legality import copy_violations
from app.engine.models import deck_archived_for_presets, default_rule_presets_for, standard_60_rules
from app.engine.strategies import STRATEGY_LIBRARY, StrategySpec
from app.seed import load_seed_payload
from app.seed_data import (
    IRON_THORNS_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_G_NAMES,
    SET_H_NAMES,
    SET_L60_NAMES,
    SET_M60_NAMES,
    SET_MILL_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_doll_deck,
    build_fallback_deck,
    build_g30_deck,
    build_mill_deck,
    build_roast_deck,
    build_roast_two_forest_deck,
    fallback_named,
)

IN_NAME = "Lillie's Determination"
PRINTED = (
    "Shuffle your hand into your deck. Then, draw 6 cards. "
    "If you have exactly 6 Prize cards remaining, draw 8 cards instead."
)
MAX_COPIES = 4
GAMES = 400
SEED = 20261116
WORKERS = int(os.environ.get("MILL_DETERMINATION_WORKERS", str(os.cpu_count() or 2)))

HERE = Path(__file__).resolve().parent
PARTIAL = Path(
    os.environ.get(
        "MILL_DETERMINATION_PARTIAL",
        str(HERE / "set-mill-determination-partial.jsonl"),
    )
)
DEST = Path(os.environ.get("MILL_DETERMINATION_DEST", str(HERE / "set-mill-determination.json")))
MD_DEST = Path(os.environ.get("MILL_DETERMINATION_MD", str(HERE / "set-mill-determination.md")))

# Strategies that already play these locked 60s. A key missing here stops the run.
STRAT = {
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
    "starmie": "starmie",
    "thorns": "thorns",
}

NAMES = {
    "g": SET_G_NAMES,
    "h": SET_H_NAMES,
    "c60": SET_C60_NAMES,
    "d60": SET_D60_NAMES,
    "s60": SET_S60_NAMES,
    "t60": SET_T60_NAMES,
    "t-meta": SET_T_META_NAMES,
    "t-unl": SET_T_UNL_NAMES,
    "g30": SET_G30_NAMES,
    "m60": SET_M60_NAMES,
    "l60": SET_L60_NAMES,
    "starmie": SET_STARMIE60_NAMES,
    "thorns": IRON_THORNS_NAMES,
}

# Event keys the engine already bumps for a printed sentence. An empty tuple
# means this sample has no counter for that card.
CARD_EVENTS = {
    "Lillie's Determination": (),
    "Hilda": ("hilda", "evo_from_hilda", "energy_from_hilda"),
    "Wally": ("wally",),
    "Miss Fortune Sisters": ("sisters_item", "sisters_miss"),
    "Team Rocket's Handiwork": ("handiwork", "handiwork_tails"),
    "Colress's Tenacity": ("colress",),
    "Crushing Hammer": ("crushing_hammer_heads", "crushing_hammer_tails"),
    "Counter Catcher": ("counter_catcher", "counter_catcher_fail"),
    "Level Ball": ("level_ball",),
    "Rescue Carrier": ("rescue_carrier",),
    "Cleffa": ("eeeeeeek_shuffle",),
    "Igglybuff": ("sleepy_flip", "sleepy_heads"),
    "Mime Jr.": ("sleepy_lost", "sleepy_lost_miss"),
    "Pichu": ("playground",),
    "Neutralization Zone": ("neutralization_zone",),
    "Slumbering Forest": ("slumbering_forest",),
    "Victini": ("victory_star_reflip",),
    "Lillie's Poké Doll": (),
    "Buddy-Buddy Poffin": (),
    "Double Turbo Energy": (),
    "Water Energy": (),
    "Ignition Energy": (),
    "Reversal Energy": (),
    "Wiglett": (),
    "Wugtrio": (),
}
LINE_EVENTS = ("mill_opponent", "mill_attack", "hilda", "wally", "eeeeeeek_shuffle")

REASON_ORDER = (
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


def _kind(result, seat: str) -> str:
    """Same buckets as data/lab/set_doll_losses.py _kind, from the subject's seat."""
    reason = result.reason or ""
    if result.winner == "tie" or reason == "turn limit":
        return "tie"
    if reason.endswith("had no Basic Pokémon") or reason.endswith("had no playable Pokémon"):
        who = reason.split()[0]
        return "no_basic" if who == seat else "foe_no_basic"
    if reason == "took all prize cards":
        return "prizes"
    if reason == "opponent has no Pokémon in play":
        return "empty" if result.winner != seat else "foe_empty"
    if reason.endswith("decked out"):
        who = reason.split()[0]
        return "decked" if who == seat else "foe_decked"
    if reason == "more prizes at turn limit":
        return "turn_prizes"
    if reason == "more remaining HP at turn limit":
        return "turn_hp"
    return "other"


def mill_cards(names: list[str]):
    out = []
    for name in names:
        if name == "Mime Jr.":
            out.append(fallback_named("mime jr. col"))
        elif name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        elif name == "Igglybuff":
            out.append(fallback_named("igglybuff sleepy"))
        else:
            out.append(fallback_named(name))
    return out


def card_text(name: str) -> str:
    """Printed sentences the engine parses: the card text, then abilities and attacks."""
    card = mill_cards([name])[0]
    parts = []
    if card.text:
        parts.append(card.text.strip())
    for ability in card.abilities or []:
        if ability.text:
            parts.append(f"{ability.name}: {ability.text.strip()}")
    for attack in card.attacks or []:
        if attack.text:
            parts.append(f"{attack.name}: {attack.text.strip()}")
    return " ".join(parts)


def build_foe(key: str):
    if key == "g30":
        return build_g30_deck()
    if key == "mill":
        return build_mill_deck()
    if key == "doll":
        return build_doll_deck()
    if key == "celebi":
        return build_roast_deck()
    if key == "two-forest":
        return build_roast_two_forest_deck()
    if key not in NAMES:
        raise SystemExit(f"no builder for foe {key}")
    return build_fallback_deck(list(NAMES[key]))


def _strategy(name: str) -> StrategySpec:
    spec = STRATEGY_LIBRARY.get(name)
    if spec is None:
        raise SystemExit(f"strategy {name} is not in the library")
    return spec


def _check_list(names: list[str]) -> None:
    pile = mill_cards(names)
    if len(pile) != 60:
        raise SystemExit(f"subject has {len(pile)} cards")
    bad = copy_violations(pile, standard_60_rules())
    if bad:
        raise SystemExit(f"subject is illegal: {bad}")


def discover() -> dict:
    payload = load_seed_payload()
    foes = []
    archived = []
    not_60 = []
    other = []
    seen = set()
    for key, record in payload.items():
        if not isinstance(record, dict):
            continue
        deck_id = record.get("id") or f"seed-{key}"
        if "archived" in record and record.get("archived") is not None:
            is_arch = bool(record["archived"])
        else:
            is_arch = deck_archived_for_presets(default_rule_presets_for(deck_id))
        if record.get("kind") is None and "cards" not in record and "name" not in record:
            # Sample hashes live beside the decks. They are not a deck.
            continue
        info = {
            "key": key,
            "name": record.get("name") or key,
            "id": deck_id,
            "cards": len(record.get("cards") or []),
            "kind": record.get("kind"),
        }
        if is_arch:
            archived.append(info)
            continue
        if record.get("kind") != "list":
            other.append(info)
            continue
        if info["cards"] != 60:
            not_60.append(info)
            continue
        if key not in STRAT:
            raise SystemExit(
                f"No strategy plays {info['name']} ({key}). This search stops before the first game."
            )
        built = build_foe(key)
        if len(built) != 60:
            raise SystemExit(f"{info['name']} builder has {len(built)} cards")
        if len(built) != info["cards"]:
            raise SystemExit(
                f"{info['name']} registry has {info['cards']} cards and the builder has {len(built)}"
            )
        bad = copy_violations(built, standard_60_rules())
        if bad:
            raise SystemExit(f"{info['name']} is illegal: {bad}")
        foes.append({**info, "strategy": STRAT[key], "extra": False})
        seen.add(key)
    extras = (
        ("starmie", "Mega Starmie ex (Kudo)", SET_STARMIE60_NAMES),
        ("thorns", "Iron Thorns ex", IRON_THORNS_NAMES),
    )
    for key, label, names in extras:
        if key in seen:
            continue
        if deck_archived_for_presets(default_rule_presets_for(None)):
            archived.append({"key": key, "name": label, "id": None, "cards": len(list(names)), "kind": "list"})
            continue
        built = build_foe(key)
        if len(built) != 60:
            raise SystemExit(f"{label} has {len(built)} cards")
        bad = copy_violations(built, standard_60_rules())
        if bad:
            raise SystemExit(f"{label} is illegal: {bad}")
        foes.append(
            {
                "key": key,
                "name": label,
                "id": None,
                "cards": 60,
                "kind": "list",
                "strategy": STRAT[key],
                "extra": True,
            }
        )
    foes.sort(key=lambda row: row["key"])
    archived.sort(key=lambda row: row["key"])
    not_60.sort(key=lambda row: row["key"])
    return {"foes": foes, "archived": archived, "not_60": not_60, "other": other}


def _cache_key(names: tuple[str, ...], foe_key: str, seat: str) -> str:
    return f"{SEED}|{GAMES}|{seat}|{foe_key}|{'/'.join(names)}"


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
        handle.flush()
        os.fsync(handle.fileno())


def _run(names: tuple[str, ...], foe_key: str, seat: str, games: int, seed: int) -> dict:
    subject = mill_cards(list(names))
    foe = build_foe(foe_key)
    foe_strat = STRAT[foe_key]
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "mill", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "mill"
    rules = standard_60_rules()
    spec_a = _strategy(strat_a)
    spec_b = _strategy(strat_b)
    rng = random.Random(seed)
    wins = 0
    events: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        if result.winner == seat:
            wins += 1
        events.update(result.events or {})
        reasons[_kind(result, seat)] += 1
    return {"wins": wins, "n": games, "events": dict(events), "reasons": dict(reasons)}


def _evaluate_many(
    lists: list[tuple[str, list[str]]],
    foe_keys: list[str],
    cache: dict[str, dict],
) -> dict[str, dict[str, dict]]:
    """Play every list against foe_keys, both seats. One pool for the whole batch."""
    out: dict[str, dict[str, dict]] = {}
    jobs = []
    cached_n = 0
    for label, names in lists:
        frozen = tuple(names)
        out[label] = {}
        for foe_key in foe_keys:
            out[label][foe_key] = {}
            for seat in ("a", "b"):
                key = _cache_key(frozen, foe_key, seat)
                cached = cache.get(key)
                if cached is not None:
                    if cached.get("n") != GAMES:
                        raise SystemExit(f"cached cell {key} has {cached.get('n')} games")
                    out[label][foe_key][seat] = cached
                    cached_n += 1
                    continue
                jobs.append((label, frozen, foe_key, seat, key))
    print(f"  {len(lists)} lists: {len(jobs)} cells to play, {cached_n} cached", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    with ProcessPoolExecutor(max_workers=min(WORKERS, len(jobs))) as pool:
        futures = {
            pool.submit(_run, frozen, foe_key, seat, GAMES, SEED): (label, foe_key, seat, key)
            for label, frozen, foe_key, seat, key in jobs
        }
        done = 0
        for fut in as_completed(futures):
            label, foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out[label][foe_key][seat] = cell
            done += 1
            if done == 1 or done % 10 == 0 or done == len(futures):
                elapsed = time.perf_counter() - started
                rate = done / elapsed if elapsed else 0
                left = (len(futures) - done) / rate if rate else 0
                wr = cell["wins"] / cell["n"]
                print(
                    f"    {done}/{len(futures)} {label} {seat} vs {foe_key} {wr:.1%} ({left:.0f}s left)",
                    flush=True,
                )
    return out


def _seat_wr(cell: dict) -> float:
    return cell["wins"] / cell["n"]


def _pair(seats: dict, key: str) -> dict:
    a = _seat_wr(seats[key]["a"])
    b = _seat_wr(seats[key]["b"])
    return {"a": a, "b": b, "wr": (a + b) / 2}


def _view(seats: dict, zero: dict, weights: dict[str, float], active: list[str]) -> dict[str, dict]:
    view = {}
    for key in weights:
        src = seats if key in active else zero
        view[key] = _pair(src, key)
    return view


def _weighted(view: dict[str, dict], weights: dict[str, float]) -> float:
    return sum(view[key]["wr"] * weights[key] for key in weights)


def _mean(view: dict[str, dict]) -> float:
    return sum(view[key]["wr"] for key in view) / len(view)


def _worst(view: dict[str, dict]) -> tuple[str, float]:
    key = min(view, key=lambda item: (view[item]["wr"], item))
    return key, view[key]["wr"]


def _list_se(seats: dict, zero: dict, weights: dict[str, float], active: list[str]) -> float:
    variance = 0.0
    for key, weight in weights.items():
        src = seats if key in active else zero
        seat_var = 0.0
        for seat in ("a", "b"):
            cell = src[key][seat]
            p = _seat_wr(cell)
            seat_var += p * (1.0 - p) / cell["n"]
        variance += weight ** 2 * seat_var / 4.0
    return variance ** 0.5


def _gap_se(before: dict, after: dict, weights: dict[str, float], active: list[str]) -> float:
    """Parked foes cancel. Sum the gap variance over the active set only."""
    variance = 0.0
    for key in active:
        weight = weights[key]
        both = 0.0
        for block in (before, after):
            for seat in ("a", "b"):
                cell = block[key][seat]
                p = _seat_wr(cell)
                both += p * (1.0 - p) / cell["n"]
        variance += weight ** 2 * both / 4.0
    return variance ** 0.5


def _weights_from(seats: dict, foe_keys: list[str]) -> dict[str, float]:
    raw = {}
    for key in foe_keys:
        wr = _pair(seats, key)["wr"]
        raw[key] = max(1e-6, 1.0 - wr)
    total = sum(raw.values())
    return {key: raw[key] / total for key in foe_keys}


def _active_set(weights: dict[str, float]) -> tuple[list[str], float]:
    ranked = sorted(weights, key=lambda key: (-weights[key], key))
    active = []
    taken = 0.0
    for key in ranked:
        if taken >= 0.90 - 1e-15:
            break
        active.append(key)
        taken += weights[key]
    return active, taken


def _blend_counter(seats: dict, zero: dict, weights: dict[str, float], active: list[str], event: str) -> float:
    total = 0.0
    for key, weight in weights.items():
        src = seats if key in active else zero
        rates = []
        for seat in ("a", "b"):
            cell = src[key][seat]
            rates.append(cell["events"].get(event, 0) / cell["n"])
        total += weight * sum(rates) / 2.0
    return total


def _blend_reasons(seats: dict, zero: dict, weights: dict[str, float], active: list[str]) -> dict[str, float]:
    names = set(REASON_ORDER)
    for key in weights:
        src = seats if key in active else zero
        for seat in ("a", "b"):
            names.update(src[key][seat]["reasons"])
    out = {}
    for name in names:
        total = 0.0
        for key, weight in weights.items():
            src = seats if key in active else zero
            rates = []
            for seat in ("a", "b"):
                cell = src[key][seat]
                rates.append(cell["reasons"].get(name, 0) / cell["n"])
            total += weight * sum(rates) / 2.0
        out[name] = total
    return out


def _contributions(new: dict[str, dict], old: dict[str, dict], weights: dict[str, float]) -> list[dict]:
    rows = []
    for key, weight in weights.items():
        delta = new[key]["wr"] - old[key]["wr"]
        rows.append(
            {
                "key": key,
                "weight": weight,
                "delta_wr": delta,
                "contribution": weight * delta,
            }
        )
    rows.sort(key=lambda row: (-abs(row["contribution"]), row["key"]))
    return rows


def _events_of(seats: dict, zero: dict, weights: dict[str, float], active: list[str]) -> dict[str, float]:
    wanted = set(LINE_EVENTS)
    for keys in CARD_EVENTS.values():
        wanted.update(keys)
    wanted.add("doll_determination")
    return {key: _blend_counter(seats, zero, weights, active, key) for key in sorted(wanted)}


def _summarize(
    copies: int,
    cut: str | None,
    copies_before: int,
    names: list[str],
    seats: dict,
    zero: dict,
    weights: dict[str, float],
    active: list[str],
    start_view: dict[str, dict],
    prev_view: dict[str, dict],
    prev_seats: dict,
    start_seats: dict,
) -> dict:
    view = _view(seats, zero, weights, active)
    weighted = _weighted(view, weights)
    start_w = _weighted(start_view, weights)
    prev_w = _weighted(prev_view, weights)
    worst_key, worst = _worst(view)
    return {
        "copies": copies,
        "cut": cut,
        "copies_before": copies_before,
        "names": list(names),
        "list_id": "/".join(names),
        "weighted": weighted,
        "se": _list_se(seats, zero, weights, active),
        "mean": _mean(view),
        "worst": worst,
        "worst_key": worst_key,
        "delta_start": weighted - start_w,
        "gap_se_start": 0.0 if copies == 0 else _gap_se(start_seats, seats, weights, active),
        "delta_prev": weighted - prev_w,
        "gap_se_prev": 0.0 if seats is prev_seats else _gap_se(prev_seats, seats, weights, active),
        "events": _events_of(seats, zero, weights, active),
        "reasons": _blend_reasons(seats, zero, weights, active),
        "contributions_start": _contributions(view, start_view, weights),
        "contributions_prev": _contributions(view, prev_view, weights),
        "by_foe": view,
    }


def _ratio(delta: float, se: float) -> float | None:
    if se <= 0:
        return None
    return delta / se


def _swap(names: list[str], cut: str) -> list[str]:
    out = list(names)
    out.remove(cut)
    out.append(IN_NAME)
    return out


def _rank(row: dict) -> tuple:
    return (-row["weighted"], -row["worst"], -row["copies_before"], row["cut"] or "")


def _pct(value: float) -> str:
    return f"{value:.2%}"


def _signed(value: float) -> str:
    return f"{value:+.2%}"


def _se_text(delta: float, se: float) -> str:
    ratio = _ratio(delta, se)
    if ratio is None:
        return f"{_signed(delta)} (gap SE undefined)"
    return f"{_signed(delta)}, gap SE {_pct(se)}, {ratio:.2f} combined standard errors"


def _counts(names: list[str]) -> list[tuple[str, int]]:
    order = []
    seen = set()
    for name in names:
        if name not in seen:
            order.append(name)
            seen.add(name)
    return [(name, names.count(name)) for name in order]


def _top_contrib(rows: list[dict], sign: int, n: int = 3) -> list[dict]:
    picked = [row for row in rows if row["contribution"] * sign > 1e-12]
    picked.sort(key=lambda row: (-abs(row["contribution"]), row["key"]))
    return picked[:n]


def _reason_bits(before: dict, after: dict) -> list[str]:
    extra = sorted((set(before) | set(after)) - set(REASON_ORDER))
    names = list(dict.fromkeys(list(REASON_ORDER) + extra))
    shown = []
    for name in names:
        old = before.get(name, 0.0)
        new = after.get(name, 0.0)
        if abs(new - old) < 0.002:
            continue
        shown.append((name, old, new, new - old))
    shown.sort(key=lambda item: -abs(item[3]))
    return [
        f"{name} {_pct(old)} → {_pct(new)} ({_signed(delta)})"
        for name, old, new, delta in shown[:4]
    ]


def _counter_sentence(name: str, before: dict[str, float], after: dict[str, float]) -> str:
    keys = CARD_EVENTS.get(name, ())
    if name == IN_NAME:
        return (
            "The sample has no counter for Lillie's Determination on Mill. "
            "The engine bumps doll_determination only when the strategy is doll."
        )
    if not keys:
        return f"The sample has no counter for {name}."
    parts = []
    moved = False
    for key in keys:
        old = before.get(key, 0.0)
        new = after.get(key, 0.0)
        parts.append(f"{key} {old:.2f} → {new:.2f}")
        if abs(new - old) >= 0.05:
            moved = True
    text = f"{name} counters: " + ", ".join(parts) + "."
    if not moved:
        text += " The sample does not show that sentence firing more or less often."
    return text


def _one_sentence(row: dict, entering: dict, foes: dict[str, str]) -> str:
    gain = row["delta_prev"]
    direction = "higher" if gain > 0 else "lower" if gain < 0 else "flat"
    # The piece that carries the move is the largest contribution in that direction.
    sign = -1 if gain < 0 else 1
    picked = _top_contrib(row["contributions_prev"], sign, 1)
    if not picked:
        picked = _top_contrib(row["contributions_prev"], -sign, 1)
    key = picked[0]["key"] if picked else ""
    foe = foes.get(key, key) or "no foe"
    reasons = _reason_bits(entering["reasons"], row["reasons"])
    end = reasons[0].split()[0] if reasons else "the end mix"
    cut = row["cut"] or "nothing"
    return (
        f"Replacing one {cut} with Lillie's Determination leaves the weighted rate {direction} "
        f"({_signed(gain)}), with the largest piece on {foe}, and the end-reason mix moves at {end}. "
        "Lillie's Determination itself has no Mill counter in this sample."
    )


def _paragraph(row: dict, entering: dict, start: dict, path: list[dict], foes: dict[str, str]) -> list[str]:
    cut = row["cut"]
    lines = [
        f"### {row['copies']} {IN_NAME}, cut {cut}",
        "",
        (
            f"{IN_NAME}: \"{PRINTED}\" "
            f"{cut}: \"{card_text(cut)}\""
        ),
        "",
    ]
    lines.append(
        "The score uses the 0-copy loss weights. "
        f"Against the start, {_se_text(row['delta_start'], row['gap_se_start'])}. "
        f"Against the previous count, {_se_text(row['delta_prev'], row['gap_se_prev'])}."
    )
    earlier = [item for item in path if 0 < item["copies"] < row["copies"]]
    for item in earlier:
        if row["delta_start"] > item["delta_start"] + 1e-12:
            lines.append(
                f"Copy {row['copies']} gains {_signed(row['delta_start'])} over the start. "
                f"Copy {item['copies']} gains {_signed(item['delta_start'])}. "
                "The higher count gained more."
            )
            break
    for item in earlier:
        if row["delta_prev"] > item["delta_prev"] + 1e-12:
            lines.append(
                f"The step gain at copy {row['copies']} is {_signed(row['delta_prev'])}. "
                f"The step gain at copy {item['copies']} is {_signed(item['delta_prev'])}. "
                "The later step gained more."
            )
            break
    lines.append("")
    up = _top_contrib(row["contributions_prev"], 1)
    down = _top_contrib(row["contributions_prev"], -1)
    bits = []
    for item in up:
        bits.append(f"{foes.get(item['key'], item['key'])} {item['contribution']:+.2%} of the weighted rate")
    for item in down:
        bits.append(f"{foes.get(item['key'], item['key'])} {item['contribution']:+.2%} of the weighted rate")
    if bits:
        lines.append("Against the previous count, the weighted move is " + "; ".join(bits) + ".")
    else:
        lines.append("No foe moves the weighted rate against the previous count.")
    lines.append("")
    lines.append(
        f"The unweighted mean is {_pct(row['mean'])} against {_pct(entering['mean'])} on the previous count "
        f"and {_pct(start['mean'])} on the start. The keeper is the 0-copy loss weights."
    )
    lines.append("")
    lines.append(_counter_sentence(IN_NAME, entering["events"], row["events"]))
    lines.append(_counter_sentence(cut, entering["events"], row["events"]))
    line_bits = []
    for key in LINE_EVENTS:
        line_bits.append(f"{key} {entering['events'].get(key, 0):.2f} → {row['events'].get(key, 0):.2f}")
    lines.append("Line counters, on the same weights: " + ", ".join(line_bits) + ".")
    rate_moved = abs(row["delta_prev"]) >= row["gap_se_prev"]
    counters_moved = False
    for key in CARD_EVENTS.get(cut, ()):
        if abs(row["events"].get(key, 0) - entering["events"].get(key, 0)) >= 0.05:
            counters_moved = True
    for key in ("mill_opponent", "mill_attack"):
        if abs(row["events"].get(key, 0) - entering["events"].get(key, 0)) >= 0.05:
            counters_moved = True
    if counters_moved and not rate_moved:
        lines.append("Those counters moved, and the weighted win rate did not clear one combined standard error.")
    lines.append("")
    lines.append("End reasons, weighted with the 0-copy vector, from Mill's seat: " + "; ".join(_reason_bits(entering["reasons"], row["reasons"])) + ".")
    lines.append("")
    lines.append(_one_sentence(row, entering, foes))
    lines.append("")
    return lines


def _cut_paragraph(row: dict, entering: dict, foes: dict[str, str]) -> list[str]:
    """A cut in the same step that moved at least one combined standard error and was not kept."""
    lines = [
        f"#### Also {row['cut']} ({_signed(row['delta_prev'])})",
        "",
        f"{IN_NAME}: \"{PRINTED}\" {row['cut']}: \"{card_text(row['cut'])}\"",
        "",
        (
            "The score uses the 0-copy loss weights. "
            f"Against the list entering the step, {_se_text(row['delta_prev'], row['gap_se_prev'])}."
        ),
        "",
    ]
    up = _top_contrib(row["contributions_prev"], 1, 2)
    down = _top_contrib(row["contributions_prev"], -1, 2)
    bits = [
        f"{foes.get(item['key'], item['key'])} {item['contribution']:+.2%}"
        for item in up + down
    ]
    lines.append("Weighted contributions: " + (", ".join(bits) if bits else "none") + ".")
    lines.append(f"Unweighted mean {_pct(row['mean'])} against the entering list at {_pct(entering['mean'])}.")
    lines.append(_counter_sentence(row["cut"], entering["events"], row["events"]))
    lines.append(
        "End reasons: " + "; ".join(_reason_bits(entering["reasons"], row["reasons"])) + "."
    )
    lines.append(_one_sentence(row, entering, foes))
    lines.append("")
    return lines


def _mean_flip(kept: dict, rival: dict, foes: dict[str, str]) -> str:
    if rival["cut"] == kept["cut"]:
        return "The unweighted mean keeps the same cut."
    ahead = []
    for key, cell in rival["by_foe"].items():
        delta = cell["wr"] - kept["by_foe"][key]["wr"]
        if delta > 0:
            ahead.append((delta, key))
    ahead.sort(reverse=True)
    named = ", ".join(f"{foes.get(key, key)} {delta:+.2%}" for delta, key in ahead[:4]) or "no foe"
    return (
        f"The unweighted mean would keep {rival['cut']} at {_pct(rival['mean'])} "
        f"instead of {kept['cut']} at {_pct(kept['mean'])}. "
        f"The foes ahead on that cut are {named}."
    )


def _markdown(report: dict) -> str:
    foes = {row["key"]: row["name"] for row in report["foes"]}
    weights = report["weights"]
    lines = [
        "# Mill, Lillie's Determination",
        "",
        "Each step replaces one copy of one other card with one Lillie's Determination. "
        "The cut with the higher win rate under the 0-copy loss weights is kept. "
        "The next copy is measured on that list, through four copies, including when a copy lowers the rate. "
        "The kept count is the one whose gain over the starting list is the largest.",
        "",
        f"Printed sentence: \"{PRINTED}\"",
        "",
        "The starting 60 is the Wiglett Mill before this card, four Hilda and zero Lillie's Determination. "
        "Mill's strategy already plays a Supporter the picker selects. "
        "This search does not add a strategy branch. The lock written after the sample is the three-copy list.",
        "",
        f"- **Seed**: `{SEED}`",
        f"- **Games per seat**: {GAMES}",
        "- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from this starting list's own losses. A foe it loses more often counts more.",
        f"- **Elapsed**: {report['elapsed_seconds']:.1f}s",
        "- **Streams**: each cell starts with `random.Random(20261116)`. "
        "Two lists diverge after the first choice that consumes a different number of draws.",
        "",
        "The weight of a foe is `max(1e-6, 1 - win rate)` divided by the sum of those values. "
        "The script divides. The Sisters weights in `data/lab/set-mill-sleep.md` are not this vector.",
        "",
        f"The active set is the weight prefix that first reaches 90%. "
        f"Its cumulative weight is {report['active_weight']:.2%}. "
        "Later cells are played only against that set. "
        "A parked foe keeps its 0-copy win rate and its weight. It is not played again.",
        "",
        "## 0-copy pass",
        "",
        "Every live 60-card deck that is not archived. Card count is the registry length. "
        "Mega Starmie and Iron Thorns are included while they are not seed keys.",
        "",
        "| Key | Deck | Cards | Strategy | A | B | Mean | Weight |",
        "| :--- | :--- | ---: | :--- | ---: | ---: | ---: | ---: |",
    ]
    zero = report["zero"]
    order = sorted(weights, key=lambda key: (-weights[key], key))
    for key in order:
        foe = next(row for row in report["foes"] if row["key"] == key)
        cell = zero["by_foe"][key]
        mark = "active" if key in report["active"] else "parked"
        lines.append(
            f"| {key} | {foe['name']} | {foe['cards']} | {foe['strategy']} | "
            f"{_pct(cell['a'])} | {_pct(cell['b'])} | {_pct(cell['wr'])} | {weights[key]:.4%} ({mark}) |"
        )
    lines += [
        "",
        f"Active set ({report['active_weight']:.2%}): " + ", ".join(report["active"]) + ".",
        "",
        "Parked foes stay at the 0-copy rates below.",
        "",
        "| Key | Deck | Weight | A | B | Mean |",
        "| :--- | :--- | ---: | ---: | ---: | ---: |",
    ]
    for row in report["parked"]:
        lines.append(
            f"| {row['key']} | {foes.get(row['key'], row['key'])} | {row['weight']:.4%} | "
            f"{_pct(row['a'])} | {_pct(row['b'])} | {_pct(row['wr'])} |"
        )
    lines += ["", "## Archived, no row", ""]
    if report["archived"]:
        for row in report["archived"]:
            lines.append(f"- {row['name']} (`{row['key']}`, {row['cards']} cards)")
    else:
        lines.append("None.")
    lines += ["", "## Not 60 cards, no row", ""]
    if report["not_60"]:
        for row in report["not_60"]:
            lines.append(f"- {row['name']} (`{row['key']}`, {row['cards']} cards)")
    else:
        lines.append("None.")
    if report["other"]:
        lines += ["", "## Not a list, no row", ""]
        for row in report["other"]:
            lines.append(f"- {row['name']} (`{row['key']}`, kind {row['kind']})")
    lines += [
        "",
        "## Path",
        "",
        "Delta start is against the 0-copy list. Delta step is against the previous count. "
        "Mill cards is `mill_opponent`. Mill has no counter for Lillie's Determination, so that sentence is not a column. "
        "The counters are weighted over every foe in the score, including a foe that mills or plays Hilda.",
        "",
        "| Copies | Cut | Weighted | ± | Mean | Worst | Delta start | Delta step | Mill cards | Mill attacks | Hilda | Wally | Eeeeeeek |",
        "| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in report["path"]:
        cut = row["cut"] or "—"
        events = row["events"]
        lines.append(
            f"| {row['copies']} | {cut} | {_pct(row['weighted'])} | {_pct(row['se'])} | {_pct(row['mean'])} | "
            f"{_pct(row['worst'])} | {_signed(row['delta_start'])} | {_signed(row['delta_prev'])} | "
            f"{events.get('mill_opponent', 0):.2f} | {events.get('mill_attack', 0):.2f} | "
            f"{events.get('hilda', 0):.2f} | {events.get('wally', 0):.2f} | {events.get('eeeeeeek_shuffle', 0):.2f} |"
        )
    best = report.get("best")
    lines += ["", "## Decision", ""]
    if not report["complete"] or best is None:
        lines.append("The search has not reached four copies. `complete` is false. The lock is unchanged.")
    else:
        lines.append(
            f"Kept count is {best['copies']} {IN_NAME}: weighted {_pct(best['weighted'])} "
            f"against the start at {_pct(report['zero']['weighted'])} "
            f"({_se_text(best['delta_start'], best['gap_se_start'])})."
        )
        lines.append("")
        gains = [(row["copies"], row["delta_start"]) for row in report["path"]]
        for copies, gain in gains:
            if copies == 0 or copies == best["copies"]:
                continue
            if best["delta_start"] > gain + 1e-12 and best["copies"] > copies:
                lines.append(
                    f"Copy {best['copies']} gains {_signed(best['delta_start'])} over the start. "
                    f"Copy {copies} gains {_signed(gain)}. The higher count gained more."
                )
        lines.append("")
        if best["copies"] > 0 and best["gap_se_prev"] > 0 and abs(best["delta_prev"]) < best["gap_se_prev"]:
            lines.append(
                f"The step from {best['copies'] - 1} to {best['copies']} is "
                f"{_se_text(best['delta_prev'], best['gap_se_prev'])}. "
                "That step does not clear one combined standard error. "
                "The kept count is still the one with the largest gain over the start."
            )
            lines.append("")
        lines.append(
            "Each step took the best cut on this seed, so that path sits a little high. "
            "Continuing through a dip does not remove that."
        )
        lines.append("")
        lines.append("This file records the sample. It does not assign `SET_MILL_NAMES`.")
        lines.append("")
        locked = next(row for row in report["path"] if row["copies"] == 3)
        lines.append(
            "The lock is that three-copy list: one Ignition Energy, Pichu, and Counter Catcher. "
            "Wugtrio stays at four. The fourth copy stays out of the lock."
        )
        lines.append("")
        lines.append("Counts on the locked list:")
        lines.append("")
        for name, count in _counts(locked["names"]):
            lines.append(f"- {name} ×{count}")
        lines.append("")
        lines.append("Counts on the four-copy sample list:")
        lines.append("")
        for name, count in _counts(best["names"]):
            lines.append(f"- {name} ×{count}")
    lines.append("")
    path = report["path"]
    start = path[0]
    for index, row in enumerate(path):
        if row["copies"] == 0:
            continue
        entering = path[index - 1]
        lines.extend(_paragraph(row, entering, start, path[: index + 1], foes))
        rnd = next(item for item in report["rounds"] if item["copies"] == row["copies"])
        for other in rnd["cuts"]:
            if other["cut"] == row["cut"]:
                continue
            se = other["gap_se_prev"]
            if se > 0 and abs(other["delta_prev"]) >= se:
                lines.extend(_cut_paragraph(other, entering, foes))
    for rnd in report["rounds"]:
        lines += [
            f"## Step {rnd['copies']}",
            "",
            f"List entering this step: weighted {_pct(rnd['entering_weighted'])}. "
            "Each row replaces one copy of that card with one Lillie's Determination. "
            "Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.",
            "",
            "| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for row in sorted(rnd["cuts"], key=_rank):
            lines.append(
                f"| {row['cut']} | {row['copies_before']} | {_pct(row['weighted'])} | {_pct(row['se'])} | "
                f"{_pct(row['mean'])} | {_pct(row['worst'])} | {_signed(row['delta_prev'])} | "
                f"{_signed(row['delta_start'])} | {row['events'].get('mill_opponent', 0):.2f} |"
            )
        kept = next(row for row in rnd["cuts"] if row["kept"])
        rival = max(rnd["cuts"], key=lambda item: (item["mean"], item["cut"]))
        lines += [
            "",
            f"Kept −{kept['cut']} at {_pct(kept['weighted'])} ({_se_text(kept['delta_prev'], kept['gap_se_prev'])}).",
            "",
            _mean_flip(kept, rival, foes),
            "",
        ]
    if report["complete"] and best is not None:
        # Unweighted mean across counts.
        mean_best = max(path, key=lambda row: (row["mean"], -row["copies"]))
        lines += ["## Unweighted mean across counts", ""]
        if mean_best["copies"] == best["copies"]:
            lines.append(
                f"The unweighted mean also keeps {best['copies']} copies at {_pct(best['mean'])}. "
                "The keeper stays the 0-copy loss weights."
            )
        else:
            lines.append(
                f"The unweighted mean would keep {mean_best['copies']} copies at {_pct(mean_best['mean'])} "
                f"instead of {best['copies']} copies at {_pct(best['mean'])}. "
                "The keeper stays the 0-copy loss weights."
            )
            ahead = []
            for key in best["by_foe"]:
                delta = mean_best["by_foe"][key]["wr"] - best["by_foe"][key]["wr"]
                if delta > 0:
                    ahead.append((delta, key))
            ahead.sort(reverse=True)
            if ahead:
                named = ", ".join(f"{foes.get(key, key)} {delta:+.2%}" for delta, key in ahead[:5])
                lines.append(f"The foes ahead on the mean's count are {named}.")
        lines += [
            "",
            "## Foes at the kept list",
            "",
            "A parked foe repeats its 0-copy rate. Delta is against the start.",
            "",
            "| Foe | Weight | A | B | Mean | Delta |",
            "| :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
        for key in order:
            cell = best["by_foe"][key]
            base = start["by_foe"][key]
            lines.append(
                f"| {foes.get(key, key)} | {weights[key]:.4%} | {_pct(cell['a'])} | {_pct(cell['b'])} | "
                f"{_pct(cell['wr'])} | {_signed(cell['wr'] - base['wr'])} |"
            )
        lines.append("")
    if not report["complete"]:
        lines.append("`complete` is false. The cap has not been measured.")
        lines.append("")
    return "\n".join(lines)


def _write(report: dict) -> None:
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(f"wrote {DEST.name} and {MD_DEST.name} complete={report['complete']}", flush=True)


def _base_elapsed() -> float:
    if not DEST.exists():
        return 0.0
    try:
        return float(json.loads(DEST.read_text()).get("elapsed_seconds") or 0.0)
    except (json.JSONDecodeError, OSError, TypeError, ValueError):
        return 0.0


def show_field() -> None:
    found = discover()
    print(f"foes {len(found['foes'])}")
    for row in found["foes"]:
        print(f"  {row['key']}: {row['name']} cards={row['cards']} strat={row['strategy']} extra={row['extra']}")
    print("archived")
    for row in found["archived"]:
        print(f"  {row['key']}: {row['name']} cards={row['cards']}")
    print("not 60")
    for row in found["not_60"]:
        print(f"  {row['key']}: {row['name']} cards={row['cards']}")
    print("other")
    for row in found["other"]:
        print(f"  {row['key']}: {row['name']} kind={row['kind']}")


def main() -> None:
    det = fallback_named(IN_NAME)
    if det.text != PRINTED:
        raise SystemExit("Lillie's Determination text does not match the printed sentence")
    if list(SET_MILL_NAMES).count(IN_NAME) != 0 or len(SET_MILL_NAMES) != 60:
        raise SystemExit("SET_MILL_NAMES is not the zero-Determination Mill 60")
    _check_list(list(SET_MILL_NAMES))
    if [card.catalog_id for card in mill_cards(list(SET_MILL_NAMES))] != [
        card.catalog_id for card in build_mill_deck()
    ]:
        raise SystemExit("mill_cards drifted from build_mill_deck")
    found = discover()
    foe_keys = [row["key"] for row in found["foes"]]
    if "mill" not in foe_keys:
        raise SystemExit("the locked Mill is not in the foe field")
    cache = _load_cache()
    started = time.perf_counter()
    base = _base_elapsed()
    start_names = list(SET_MILL_NAMES)
    print("0-copy pass", flush=True)
    zero_seats = _evaluate_many([("0", start_names)], foe_keys, cache)["0"]
    weights = _weights_from(zero_seats, foe_keys)
    active, active_weight = _active_set(weights)
    print(f"active {active} weight {active_weight:.4%}", flush=True)
    zero_view = _view(zero_seats, zero_seats, weights, active)
    zero_row = _summarize(
        0, None, 0, start_names, zero_seats, zero_seats, weights, active, zero_view, zero_view, zero_seats, zero_seats
    )
    parked = []
    for key, weight in weights.items():
        if key in active:
            continue
        cell = zero_view[key]
        parked.append({"key": key, "weight": weight, "wr": cell["wr"], "a": cell["a"], "b": cell["b"]})
    path = [zero_row]
    rounds = []
    cells = {"/".join(start_names): zero_seats}

    def elapsed() -> float:
        return base + (time.perf_counter() - started)

    def pack(complete: bool, best: dict | None) -> dict:
        return {
            "seed": SEED,
            "games": GAMES,
            "complete": complete,
            "incoming": IN_NAME,
            "printed": PRINTED,
            "subject": "SET_MILL_NAMES",
            "strategy": "mill",
            "lock_unchanged": True,
            "elapsed_seconds": elapsed(),
            "foes": found["foes"],
            "archived": found["archived"],
            "not_60": found["not_60"],
            "other": found["other"],
            "weights": weights,
            "active": active,
            "active_weight": active_weight,
            "parked": parked,
            "zero": zero_row,
            "path": path,
            "rounds": rounds,
            "best": best,
            "cells": {
                list_id: {
                    foe_key: {"a": block["a"], "b": block["b"]}
                    for foe_key, block in foe_cells.items()
                }
                for list_id, foe_cells in cells.items()
            },
        }

    _write(pack(False, None))
    current = start_names
    current_seats = zero_seats
    current_view = zero_view
    for copies in range(1, MAX_COPIES + 1):
        cut_names = sorted({name for name in current if name != IN_NAME})
        measured = []
        print(f"copy {copies}, {len(cut_names)} cuts, active {len(active)}", flush=True)
        batch = []
        built = {}
        for cut in cut_names:
            nxt = _swap(current, cut)
            _check_list(nxt)
            built[cut] = nxt
            batch.append((f"{copies}:{cut}", nxt))
        played = _evaluate_many(batch, active, cache)
        for cut in cut_names:
            nxt = built[cut]
            seats = played[f"{copies}:{cut}"]
            cells["/".join(nxt)] = seats
            row = _summarize(
                copies,
                cut,
                current.count(cut),
                nxt,
                seats,
                zero_seats,
                weights,
                active,
                zero_view,
                current_view,
                current_seats,
                zero_seats,
            )
            measured.append((row, nxt, seats))
        measured.sort(key=lambda item: _rank(item[0]))
        kept_row, kept_names, kept_seats = measured[0]
        for row, _names, _seats in measured:
            row["kept"] = row["cut"] == kept_row["cut"]
        rounds.append(
            {
                "copies": copies,
                "entering_weighted": current_view and _weighted(current_view, weights),
                "cuts": [row for row, _names, _seats in measured],
            }
        )
        path.append(kept_row)
        current = kept_names
        current_seats = kept_seats
        current_view = _view(kept_seats, zero_seats, weights, active)
        print(
            f"kept copy {copies} -{kept_row['cut']} {_pct(kept_row['weighted'])} "
            f"start {_signed(kept_row['delta_start'])}",
            flush=True,
        )
        _write(pack(False, None))
    best = max(path, key=lambda row: (row["weighted"], -row["copies"]))
    _write(pack(True, best))
    print(
        f"done kept {best['copies']} {_pct(best['weighted'])} vs start {_pct(zero_row['weighted'])}",
        flush=True,
    )


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--field":
        show_field()
    else:
        main()
