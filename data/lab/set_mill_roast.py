#!/usr/bin/env python3
"""Celebi ◇ / Chandelure roast mill. One list, both seats, loss-weighted.

Mountain Roasting discards the top 3 only when Chandelure is played from the
hand. Dawn searches the deck for a Basic Pokémon, a Stage 1 Pokémon, and a
Stage 2 Pokémon and puts them into the hand.
Broken Time-Space lets a Pokémon that was just played or just evolved this
turn evolve again. Pichu Playground benches Litwick
and then Celebi ◇. A Chandelure in the hand evolves onto any Lampent that can
evolve this turn. Team Rocket's Petrel
searches a Trainer card. Rescue Scarf returns Celebi ◇ to the hand.

Seed 20261027 unless ROAST_SEED is set. Games per seat from ROAST_GAMES
(default 20).
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
    SET_ROAST_NAMES,
    SET_S60_NAMES,
    SET_STARMIE60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
    build_roast_deck,
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

GAMES = int(os.environ.get("ROAST_GAMES", "20"))
SEED = int(os.environ.get("ROAST_SEED", "20261027"))
WORKERS = int(os.environ.get("ROAST_WORKERS", str(min(4, os.cpu_count() or 2))))
HERE = Path(__file__).resolve().parent
PARTIAL = Path(os.environ.get("ROAST_PARTIAL", "/tmp/mill-roast-partial.jsonl"))
DEST = Path(os.environ.get("ROAST_DEST", HERE / "set-mill-roast.json"))
MD_DEST = Path(os.environ.get("ROAST_MD", HERE / "set-mill-roast.md"))

_COUNT_KEYS = (
    "mill_attack",
    "mountain_roasting",
    "roast_mill_cards",
    "roast_mill_turns",
    "grand_tree",
    "dawn",
    "evolution_incense",
    "hisuian_heavy_ball",
    "roast_bts",
    "time_distortion",
    "rescue_scarf",
    "prism_lost_zone",
    "eeeeeeek",
    "cleffa_play",
    "playground",
    "pichu_play",
    "turns",
    "opp_prizes",
)


def _check() -> None:
    rules = standard_60_rules()
    pile = build_roast_deck()
    if len(pile) != 60:
        raise SystemExit(f"roast has {len(pile)} cards")
    bad = copy_violations(pile, rules)
    if bad:
        raise SystemExit(f"roast is illegal: {bad}")
    names = [card.name for card in pile]
    pichu = [card for card in pile if card.name == "Pichu"]
    if len(pichu) < 2:
        raise SystemExit(f"roast has {len(pichu)} Pichu")
    for card in pichu:
        kinds = {effect.get("kind") for attack in card.attacks for effect in attack.effects}
        if "playground" not in kinds:
            raise SystemExit("Pichu is not Playground")
    cleffa = [card for card in pile if card.name == "Cleffa"]
    if len(cleffa) < 1:
        raise SystemExit("roast has no Cleffa")
    for card in cleffa:
        kinds = {effect.get("kind") for attack in card.attacks for effect in attack.effects}
        if "shuffle_hand_then_draw" not in kinds:
            raise SystemExit("Cleffa is not Eeeeeeek")
    if names.count("Level Ball") != 3 or names.count("Nest Ball"):
        raise SystemExit("roast Level Ball count")
    if names.count("Slumbering Forest") < 1:
        raise SystemExit("roast has no Slumbering Forest")
    if names.count("Dawn") != 4 or names.count("Evolution Incense") or names.count("Grand Tree"):
        raise SystemExit("roast Dawn list")
    if names.count("Broken Time-Space") != 3:
        raise SystemExit("roast Broken Time-Space count")
    if (
        names.count("Hisuian Heavy Ball") != 1
        or names.count("Ultra Ball") != 1
        or names.count("Energy Search") != 4
        or names.count("Switch") != 1
    ):
        raise SystemExit("roast Hisuian Heavy Ball count")
    heavy = fallback_named("Hisuian Heavy Ball")
    heavy_text = heavy.text.lower().replace("é", "e")
    if "basic pokemon" not in heavy_text or "face-down prize" not in heavy_text:
        raise SystemExit("Hisuian Heavy Ball text")
    bts = fallback_named("Broken Time-Space")
    if "just played or evolved" not in bts.text.lower():
        raise SystemExit("Broken Time-Space text")
    dawn = fallback_named("Dawn")
    if "a basic pokemon, a stage 1 pokemon, and a stage 2 pokemon" not in dawn.text.lower().replace("é", "e"):
        raise SystemExit("Dawn text")
    if fallback_named("Team Rocket's Petrel").text.lower().count("trainer") < 1:
        raise SystemExit("Petrel text missing")


def _foe_cards(names, g30: bool):
    if g30:
        return build_g30_deck()
    return build_fallback_deck(list(names))


def _bucket(seat: str, winner: str, reason: str) -> str:
    if winner == "tie":
        return f"tie|{reason}"
    won = (seat == "a" and winner == "a") or (seat == "b" and winner == "b")
    return f"{'roast' if won else 'foe'}|{reason}"


def _run(foe_key: str, seat: str, games: int, seed: int) -> dict:
    import random

    _key, _label, foe_names, foe_strat, g30 = next(row for row in FOES if row[0] == foe_key)
    subject = build_roast_deck()
    foe = _foe_cards(foe_names, g30)
    if seat == "a":
        cards_a, cards_b = subject, foe
        strat_a, strat_b = "roast", foe_strat
    else:
        cards_a, cards_b = foe, subject
        strat_a, strat_b = foe_strat, "roast"
    rules = standard_60_rules()
    spec_a = StrategySpec.from_dict(strat_a)
    spec_b = StrategySpec.from_dict(strat_b)
    rng = random.Random(seed)
    wins = 0
    ties = 0
    fired = 0
    totals = Counter()
    waves: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    for _ in range(games):
        result = play_game(cards_a, cards_b, rules, spec_a, spec_b, rng)
        roast_is_a = seat == "a"
        if (roast_is_a and result.winner == "a") or (not roast_is_a and result.winner == "b"):
            wins += 1
        elif result.winner == "tie":
            ties += 1
        if result.events.get("mountain_roasting", 0):
            fired += 1
        totals["mill_attack"] += result.events.get("mill_attack", 0)
        totals["mountain_roasting"] += result.events.get("mountain_roasting", 0)
        totals["roast_mill_cards"] += result.events.get("roast_mill_cards", 0)
        totals["roast_mill_turns"] += result.events.get("roast_mill_turns", 0)
        totals["grand_tree"] += result.events.get("grand_tree", 0)
        totals["dawn"] += result.events.get("dawn", 0)
        totals["evolution_incense"] += result.events.get("evolution_incense", 0)
        totals["hisuian_heavy_ball"] += result.events.get("hisuian_heavy_ball", 0)
        totals["roast_bts"] += result.events.get(f"roast_bts_{seat}", 0)
        totals["time_distortion"] += result.events.get("time_distortion", 0)
        totals["rescue_scarf"] += result.events.get("rescue_scarf", 0)
        totals["prism_lost_zone"] += result.events.get("prism_lost_zone", 0)
        totals["eeeeeeek"] += result.events.get("eeeeeeek_shuffle", 0)
        totals["cleffa_play"] += result.events.get("saw_play:Cleffa", 0)
        totals["playground"] += result.events.get(f"used_playground_{seat}", 0)
        totals["pichu_play"] += result.events.get("saw_play:Pichu", 0)
        totals["turns"] += result.turns
        totals["opp_prizes"] += result.prizes_taken_b if roast_is_a else result.prizes_taken_a
        for key, count in result.events.items():
            if key.startswith("roast_mill_wave:"):
                waves[key.split(":", 1)[1]] += count
        reasons[_bucket(seat, result.winner, result.reason)] += 1
    row = {
        "wr": wins / games,
        "tie": ties / games,
        "fired": fired / games,
        "waves": {key: waves[key] / games for key in waves},
        "reasons": dict(reasons),
    }
    for key in _COUNT_KEYS:
        row[key] = totals[key] / games
    return row


def _cache_key(foe_key: str, seat: str, games: int, seed: int) -> str:
    return f"{seed}|{games}|{seat}|{foe_key}|roast-heavy-one"


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


def _evaluate(games: int, cache: dict[str, dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    jobs = []
    for foe_key, *_ in FOES:
        for seat in ("a", "b"):
            key = _cache_key(foe_key, seat, games, SEED)
            cached = cache.get(key)
            if cached is not None:
                out.setdefault(foe_key, {})[seat] = cached
                continue
            jobs.append((foe_key, seat, key))
    print(f"{len(jobs)} cells, {games} games, seed {SEED}", flush=True)
    if not jobs:
        return out
    started = time.perf_counter()
    done = 0
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futures = {
            pool.submit(_run, foe_key, seat, games, SEED): (foe_key, seat, key)
            for foe_key, seat, key in jobs
        }
        for fut in as_completed(futures):
            foe_key, seat, key = futures[fut]
            cell = fut.result()
            cache[key] = cell
            _append(key, cell)
            out.setdefault(foe_key, {})[seat] = cell
            done += 1
            elapsed = time.perf_counter() - started
            rate = done / elapsed if elapsed else 0
            left = (len(futures) - done) / rate if rate else 0
            print(
                f"  {done}/{len(futures)} seat {seat} vs {foe_key} {cell['wr']:.1%} "
                f"fired {cell['fired']:.0%} ({left:.0f}s left)",
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
            "fired": (a["fired"] + b["fired"]) / 2,
        }
        for key in _COUNT_KEYS:
            row[key] = (a.get(key, 0) + b.get(key, 0)) / 2
        waves: Counter[str] = Counter()
        for seat in (a, b):
            for size, count in (seat.get("waves") or {}).items():
                waves[size] += count / 2
        row["waves"] = dict(waves)
        reasons: Counter[str] = Counter()
        for seat in (a, b):
            reasons.update(seat.get("reasons") or {})
        row["reasons"] = dict(reasons)
        combined[foe_key] = row
    return combined


def _weighted(cells: dict[str, dict]) -> float:
    return sum(cells[key]["wr"] * WEIGHTS[key] for key, *_ in FOES)


def _weighted_stat(cells: dict[str, dict], key: str) -> float:
    return sum(cells[foe][key] * WEIGHTS[foe] for foe, *_ in FOES)


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _markdown(report: dict) -> str:
    counts = dict(Counter(SET_ROAST_NAMES))
    lines = [
        "# Celebi ◇ Chandelure roast",
        "",
        "Celebi ◇ uses Time Distortion: devolve any number of benched Pokémon as many times as you like, and put each Evolution card removed this way into the hand. The measured line devolves each benched Chandelure once, leaving Lampent.",
        "",
        "Chandelure's Mountain Roasting says the top 3 cards are discarded when you play that Pokémon from your hand to evolve. One evolution mills 3. Three mill 9. Four mill 12. Dawn puts one Basic, one Stage 1, and one Stage 2 into the hand. Playing Chandelure from that hand mills.",
        "",
        "Broken Time-Space says each player may evolve a Pokémon that he or she just played or evolved during that turn. With it in play, a Litwick played this turn can evolve into Lampent and then into Chandelure before the attack. Both players may use that stadium.",
        "",
        "Pichu is HeartGold & SoulSilver Playground. Each player may bench as many Basic Pokémon as they like, this player first. Roast benches Litwick until four lines are in play, then Celebi ◇. Dawn searches the deck for a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon. It takes Pichu, Litwick, or Celebi ◇ for the Basic, Lampent for the Stage 1, and Chandelure for the Stage 2. Under Broken Time-Space a Litwick played this turn can evolve twice before the attack. Celebi ◇ uses Time Distortion and puts that Chandelure back into the hand. Level Ball finds a Pokémon with 90 HP or less and does not find Chandelure. When this turn will play Playground, Level Ball searches a Stage 1, so Litwick stays in the deck for that attack.",
        "",
        "Hisuian Heavy Ball looks at the face-down Prize cards. It may reveal a Basic Pokémon, put that Pokémon into the hand, and put this card in its place as a face-down Prize card. If it does not reveal a Basic, this card goes to the discard pile. Then the face-down prizes are shuffled. When more than one Basic is there, roast reveals Celebi ◇ before Litwick, then a Pichu or Cleffa the deck no longer has. The roast list has one copy. That copy replaced one Switch: every other card was measured as the cut, this swap had the higher weighted win rate, and a second copy did not raise it. See data/lab/set-mill-roast-heavy.md.",
        "",
        "Lampent is Plasma Storm Freefloating. With no Energy attached, its retreat cost is 0. Fire Energy stays on Celebi ◇.",
        "",
        "Rescue Scarf puts the Pokémon into the hand when an attack Knocks it Out, and discards the cards attached to it. Celebi ◇ therefore does not go to the discard pile, and the Prism Star rule does not put it in the Lost Zone. Energy Retrieval takes that Fire Energy back. Arven can find an Item and the scarf. When Celebi ◇ or a needed Litwick or Pichu is in the prizes and Hisuian Heavy Ball is still in the deck, Arven takes that ball. Team Rocket's Petrel searches the deck for a Trainer card. It takes Hisuian Heavy Ball before Broken Time-Space when that prize is Celebi ◇, a stuck Pichu, or a Litwick with almost none of the line outside the prizes. A spare Litwick waits until after Dawn. Petrel does not search a Pokémon or an Energy card.",
        "",
        "Cleffa is HeartGold & SoulSilver Eeeeeeek: shuffle the hand into the deck, draw 6, then Cleffa is Asleep. Pichu is the Playground attacker. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Slumbering Forest makes the between-turns sleep check two coins, and the Pokémon stays Asleep unless both are heads. Asleep blocks retreat, so Switch brings Celebi ◇ Active.",
        "",
        "A Litwick played on the turn Dawn finds Lampent stays unevolved until Broken Time-Space is in play. The stadium also lets that Lampent take Chandelure the same turn.",
        "",
        f"- **List**: {', '.join(f'{name} ×{counts[name]}' for name in dict.fromkeys(SET_ROAST_NAMES))}",
        f"- **Seed**: `{report['seed']}`",
        f"- **Games per seat**: {report['games']}",
        "- **Seats**: roast is player A and player B. A foe cell is the mean of those two win rates.",
        "- **Weights**: frozen from the Sisters 60.",
        f"- **Weights**: {', '.join(f'{key} {WEIGHTS[key]:.1%}' for key, *_ in FOES)}",
        f"- **Elapsed**: {report['elapsed']:.1f}s",
        "",
        f"Weighted win rate **{_pct(report['weighted'])}** (± {_pct(report['se'])}). "
        f"Games in which Mountain Roasting fired: **{_pct(report['fired'])}**. "
        f"Hand-evolve turns per game: {report['roast_mill_turns']:.2f}. "
        f"Cards milled by those turns per game: {report['roast_mill_cards']:.2f}. "
        f"Dawn plays per game: {report['dawn']:.2f}. "
        f"Hisuian Heavy Ball swaps per game: {report['hisuian_heavy_ball']:.2f}. "
        f"Broken Time-Space plays per game: {report['roast_bts']:.2f}. "
        f"Time Distortion devolves per game: {report['time_distortion']:.2f}. "
        f"Rescue Scarf returns per game: {report['rescue_scarf']:.2f}. "
        f"Celebi ◇ sent to the Lost Zone per game: {report['prism_lost_zone']:.2f}. "
        f"Playground attacks per game: {report['playground']:.2f}. "
        f"Pichu entered play per game: {report['pichu_play']:.2f}. "
        f"Eeeeeeek per game: {report['eeeeeeek']:.2f}. "
        f"Cleffa entered play per game: {report['cleffa_play']:.2f}. "
        f"Mill turns of 9 or more: {report['wave_ge9']:.1%}. "
        "A shorter row can be one Lampent taking one Chandelure from the hand, or the opponent's deck running out.",
        "",
        "## Wave",
        "",
        "Each row is how often a turn's from-hand Chandelure evolutions milled that many cards. One Chandelure mills 3. Dawn itself is not in this histogram. A short last row can be the opponent's deck running out.",
        "",
        "| Cards milled that turn | Turns per game |",
        "| ---: | ---: |",
    ]
    waves = report["waves"]
    if not waves:
        lines.append("| — | 0 |")
    else:
        for size in sorted(waves, key=lambda item: int(item)):
            lines.append(f"| {size} | {waves[size]:.3f} |")
    lines.extend(
        [
            "",
            "## Foes",
            "",
            "| Foe | Win rate | A | B | Fired | Mill turns | Mill cards | Scarf | Lost Zone |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, label, *_ in FOES:
        row = report["cells"][key]
        lines.append(
            f"| {label} | {_pct(row['wr'])} | {_pct(row['a'])} | {_pct(row['b'])} | "
            f"{_pct(row['fired'])} | {row['roast_mill_turns']:.2f} | {row['roast_mill_cards']:.2f} | "
            f"{row['rescue_scarf']:.2f} | {row['prism_lost_zone']:.2f} |"
        )
    lines.append("")
    return "\n".join(lines)


def _wave_share(waves: Counter[str], pred) -> float:
    total = sum(waves.values())
    if not total:
        return 0.0
    return sum(count for size, count in waves.items() if pred(int(size))) / total


def _weighted_se(cells: dict[str, dict], games: int) -> float:
    variance = 0.0
    for key, *_rest in FOES:
        seat_var = 0.0
        for seat in ("a", "b"):
            p = cells[key][seat]["wr"]
            seat_var += p * (1.0 - p) / games
        variance += WEIGHTS[key] ** 2 * seat_var / 4.0
    return variance ** 0.5


def main() -> None:
    started = time.perf_counter()
    _check()
    cache = _load_cache()
    seats = _evaluate(GAMES, cache)
    cells = _combine(seats)
    waves: Counter[str] = Counter()
    for foe_key, *_ in FOES:
        for size, count in cells[foe_key]["waves"].items():
            waves[size] += count * WEIGHTS[foe_key]
    report = {
        "seed": SEED,
        "games": GAMES,
        "elapsed": time.perf_counter() - started,
        "weighted": _weighted(cells),
        "se": _weighted_se(seats, GAMES),
        "fired": _weighted_stat(cells, "fired"),
        "playground": _weighted_stat(cells, "playground"),
        "pichu_play": _weighted_stat(cells, "pichu_play"),
        "roast_mill_turns": _weighted_stat(cells, "roast_mill_turns"),
        "roast_mill_cards": _weighted_stat(cells, "roast_mill_cards"),
        "grand_tree": _weighted_stat(cells, "grand_tree"),
        "dawn": _weighted_stat(cells, "dawn"),
        "evolution_incense": _weighted_stat(cells, "evolution_incense"),
        "hisuian_heavy_ball": _weighted_stat(cells, "hisuian_heavy_ball"),
        "roast_bts": _weighted_stat(cells, "roast_bts"),
        "time_distortion": _weighted_stat(cells, "time_distortion"),
        "rescue_scarf": _weighted_stat(cells, "rescue_scarf"),
        "prism_lost_zone": _weighted_stat(cells, "prism_lost_zone"),
        "eeeeeeek": _weighted_stat(cells, "eeeeeeek"),
        "cleffa_play": _weighted_stat(cells, "cleffa_play"),
        "waves": dict(waves),
        "wave_ge9": _wave_share(waves, lambda size: size >= 9),
        "cells": cells,
        "counts": dict(Counter(SET_ROAST_NAMES)),
    }
    DEST.write_text(json.dumps(report, indent=2) + "\n")
    MD_DEST.write_text(_markdown(report))
    print(
        f"weighted {report['weighted']:.1%} fired {report['fired']:.1%} "
        f"mill/turn {report['roast_mill_cards']:.2f} ge9 {report['wave_ge9']:.1%} -> {MD_DEST}",
        flush=True,
    )


if __name__ == "__main__":
    main()
