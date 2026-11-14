#!/usr/bin/env python3
"""Build the Kecleon / Ditto ◇ research tables from the local physical-card dump.

The dump is the Pokémon TCG JSON snapshot under /tmp/tcg (sets_en.json plus raw/<set>.json).
It is the physical card game only. Pokémon TCG Pocket is not in that snapshot and is not
included here. Run this once while the snapshot is available; the CSVs are the deliverable.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from itertools import combinations
from pathlib import Path

from kecleon_ditto_rainbow import DECKS, WEAK_TO, deck_size, energy_symbols, pays

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "lab" / "kecleon-ditto-rainbow"
DUMP = Path("/tmp/tcg")
EXPANDED_FROM = "2011/04/25"  # Black & White
TYPES = (
    "Grass", "Fire", "Water", "Lightning", "Psychic", "Fighting",
    "Darkness", "Metal", "Fairy", "Dragon", "Colorless",
)
NINE = tuple(t for t in TYPES if t not in {"Dragon", "Colorless"})


def load_sets() -> dict:
    return {s["id"]: s for s in json.loads((DUMP / "sets_en.json").read_text())}


def stage_of(subtypes: list[str]) -> str:
    if "LEGEND" in subtypes:
        return "LEGEND"
    if "MEGA" in subtypes:
        return "MEGA"
    if "Stage 2" in subtypes:
        return "Stage 2"
    if "Stage 1" in subtypes:
        return "Stage 1"
    if "Basic" in subtypes:
        return "Basic"
    return " ".join(subtypes)


def has_rule_box(subtypes: list[str], series: str) -> str:
    """Compendium ruling of 18 March 2021, updated by later mechanics.

    Original EX-era Pokémon-ex do not have a Rule Box. Pokémon-EX, Pokémon V,
    VMAX, VSTAR, GX, Prism Star, BREAK, Radiant, and Mega Evolution do.
    """
    if any(s in subtypes for s in ("EX", "V", "VMAX", "VSTAR", "GX", "BREAK", "Radiant", "Prism Star")):
        return "yes"
    if "MEGA" in subtypes:
        return "yes"
    if "ex" in subtypes and series in {"Scarlet & Violet", "Mega Evolution", "Sword & Shield"}:
        return "yes"
    return "no"


def legality(card: dict, setinfo: dict) -> str:
    formats = ["Unlimited"]
    if (setinfo.get("releaseDate") or "0000/00/00") >= EXPANDED_FROM:
        formats.insert(0, "Expanded")
    if card.get("regulationMark") in {"H", "I", "J"}:
        formats.insert(0, "Standard")
    return "; ".join(formats)


def attack_fields(card: dict, index: int) -> dict:
    attacks = card.get("attacks") or []
    if index >= len(attacks):
        return {"name": "", "cost": "", "damage": "", "text": ""}
    attack = attacks[index]
    return {
        "name": attack.get("name") or "",
        "cost": " ".join(attack.get("cost") or []),
        "damage": attack.get("damage") or "",
        "text": (attack.get("text") or "").replace("\n", " "),
    }


def ability_text(card: dict) -> str:
    parts = []
    for ability in card.get("abilities") or []:
        parts.append(f"{ability.get('name')}: {(ability.get('text') or '').replace(chr(10), ' ')}")
    return " | ".join(parts)


def weakness_text(card: dict) -> str:
    return ", ".join(f"{w.get('type')} {w.get('value')}" for w in card.get("weaknesses") or [])


def dual_rows(sets: dict) -> list[dict]:
    rows = []
    for path in sorted((DUMP / "raw").glob("*.json")):
        info = sets.get(path.stem)
        if info is None:
            continue
        for card in json.loads(path.read_text()):
            if card.get("supertype") != "Pokémon":
                continue
            types = card.get("types") or []
            if len(types) < 2:
                continue
            subtypes = card.get("subtypes") or []
            first = attack_fields(card, 0)
            second = attack_fields(card, 1)
            number = str(card.get("number"))
            printed = info.get("printedTotal")
            rows.append({
                "pokemon": card.get("name"),
                "set": info["name"],
                "series": info.get("series"),
                "release_date": info.get("releaseDate"),
                "card_id": card.get("id"),
                "card_number": number,
                "printed_as": f"{number}/{printed}" if printed and number.isdigit() else number,
                "type_1": types[0],
                "type_2": types[1] if len(types) > 1 else "",
                "extra_types": " ".join(types[2:]),
                "stage": stage_of(subtypes),
                "subtypes": " ".join(subtypes),
                "hp": card.get("hp") or "",
                "evolves_from": card.get("evolvesFrom") or "",
                "ability": ability_text(card),
                "attack_1": first["name"],
                "attack_1_cost": first["cost"],
                "attack_1_damage": first["damage"],
                "attack_1_text": first["text"],
                "attack_2": second["name"],
                "attack_2_cost": second["cost"],
                "attack_2_damage": second["damage"],
                "attack_2_text": second["text"],
                "weakness": weakness_text(card),
                "retreat": " ".join(card.get("retreatCost") or []),
                "regulation_mark": card.get("regulationMark") or "",
                "rule_box": has_rule_box(subtypes, info.get("series") or ""),
                "legend_pair": "half" if "LEGEND" in subtypes else "",
                "legality": legality(card, info),
            })
    rows.sort(key=lambda r: (r["release_date"] or "", r["set"], r["card_number"]))
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        raise SystemExit(f"no rows for {path}")
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def exemplar_key(row: dict) -> tuple:
    rule = 1 if row["rule_box"] == "yes" else 0
    stage_rank = {"Stage 1": 0, "Basic": 1, "Stage 2": 2, "LEGEND": 3, "MEGA": 4}.get(row["stage"], 5)
    return (rule, stage_rank, row["release_date"] or "")


def playable(row: dict) -> bool:
    return row["stage"] in {"Basic", "Stage 1"} and row["rule_box"] == "no" and row["legend_pair"] == ""


def minimum_cover(rows: list[dict], needed: tuple[str, ...], expanded_only: bool = False, only_playable: bool = False) -> dict:
    pool = {}
    for row in rows:
        if expanded_only and "Expanded" not in row["legality"]:
            continue
        if only_playable and not playable(row):
            continue
        pair = frozenset((row["type_1"], row["type_2"]))
        if not pair <= set(needed):
            # A pair that includes Dragon or Colorless still helps those, but this search is the nine.
            if not (pair & set(needed)):
                continue
        current = pool.get(pair)
        if current is None or exemplar_key(row) < exemplar_key(current):
            pool[pair] = row
    pairs = list(pool.items())
    target = set(needed)

    def search(size: int):
        best = None
        for chosen in combinations(pairs, size):
            covered = set()
            for pair, _row in chosen:
                covered |= set(pair) & target
            if covered != target:
                continue
            names = tuple(sorted(row["pokemon"] for _pair, row in chosen))
            if best is None or names < best[0]:
                best = (names, chosen)
        return best

    for size in range(1, 6):
        found = search(size)
        if found:
            names, chosen = found
            return {
                "cards": size,
                "pokemon": [
                    {
                        "pokemon": row["pokemon"],
                        "set": row["set"],
                        "printed_as": row["printed_as"],
                        "types": sorted(pair),
                        "stage": row["stage"],
                        "legality": row["legality"],
                    }
                    for pair, row in chosen
                ],
            }
    return {"cards": None, "pokemon": []}


def toolbox_rows(duals: list[dict]) -> list[dict]:
    """Dual-type Stage 1 cards, plus the Stage 1 cards the three decks actually play."""
    deck_names = set()
    for cards in DECKS.values():
        for card in cards:
            if card.get("stage") == "stage1":
                deck_names.add(card["name"])
    rows = []
    seen = set()
    for row in duals:
        if row["stage"] not in {"Stage 1", "MEGA"}:
            continue
        reason = "dual-type Stage 1"
        if row["stage"] == "MEGA":
            reason = "dual-type Mega Evolution; evolving into an older Mega Evolution Pokémon-EX ends the turn"
        if row["pokemon"] in deck_names:
            reason = "in a researched deck; " + reason
        key = row["card_id"]
        if key in seen:
            continue
        seen.add(key)
        rows.append({
            "name": row["pokemon"],
            "set": row["set"],
            "card_number": row["printed_as"],
            "type": f"{row['type_1']} {row['type_2']}".strip(),
            "stage": row["stage"],
            "hp": row["hp"],
            "attack": row["attack_1"],
            "attack_text": row["attack_1_text"],
            "energy_cost": row["attack_1_cost"],
            "second_attack": row["attack_2"],
            "second_cost": row["attack_2_cost"],
            "weakness": row["weakness"],
            "ability": row["ability"],
            "role": reason,
            "legality": row["legality"],
            "rule_box": row["rule_box"],
            "evolves_from": row["evolves_from"],
        })
    # Single-type Stage 1 cards used by the decks that are not already listed.
    present = {row["name"] for row in rows}
    for cards in DECKS.values():
        for card in cards:
            if card.get("stage") != "stage1" or card["name"] in present:
                continue
            present.add(card["name"])
            attack = card["attacks"][0] if card["attacks"] else ("", (), 0)
            rows.append({
                "name": card["name"],
                "set": card.get("set"),
                "card_number": card.get("number"),
                "type": " ".join(card["types"]),
                "stage": "Stage 1",
                "hp": card.get("hp"),
                "attack": attack[0],
                "attack_text": "See the deck note. Damage used by the goldfish is the printed base.",
                "energy_cost": " ".join(attack[1]),
                "second_attack": "",
                "second_cost": "",
                "weakness": "",
                "ability": "",
                "role": "single-type Stage 1 in a researched deck",
                "legality": "",
                "rule_box": "yes" if card.get("rule_box") or card.get("gx_ex") else "no",
                "evolves_from": "",
            })
    return rows


def coverage_rows(packages: list[tuple[str, dict]]) -> list[dict]:
    rows = []
    for label, found in packages:
        if not found["pokemon"]:
            rows.append({
                "package": label,
                "package_size": "none in five cards",
                "pokemon": "",
                "set": "",
                "printed_as": "",
                "types": "",
                "stage": "",
                "legality": "",
                "still_needed_after_these_cards": "No five playable dual-type cards in this pool cover Grass, Fire, Water, Lightning, Psychic, Fighting, Darkness, Metal, and Fairy.",
            })
            continue
        for card in found["pokemon"]:
            rows.append({
                "package": label,
                "package_size": found["cards"],
                "pokemon": card["pokemon"],
                "set": card["set"],
                "printed_as": card["printed_as"],
                "types": " ".join(card["types"]),
                "stage": card["stage"],
                "legality": card["legality"],
                "still_needed_after_these_cards": "Dragon and Colorless are not on any dual-type card",
            })
    return rows


def weakness_rows() -> list[dict]:
    """Common Sword & Shield-onward weakness, applied to the deck's attackers.

    This is a comparison chart, not a rule. A dual-type attacker hits weakness if the
    defender is weak to either printed type.
    """
    attackers = []
    seen = set()
    for cards in DECKS.values():
        for card in cards:
            if card["kind"] != "pokemon" or card["name"] in seen:
                continue
            seen.add(card["name"])
            attackers.append(card)
    rows = []
    for card in attackers:
        attack = card["attacks"][0] if card["attacks"] else None
        base = attack[2] if attack else 0
        for defender, attacking_type in WEAK_TO.items():
            hits = attacking_type in card["types"] and base > 0 and card.get("idx_name") != "kecleon"
            rows.append({
                "attacker": card["name"],
                "attacker_types": " ".join(card["types"]),
                "defender_type": defender,
                "defender_weak_to": attacking_type,
                "printed_base_damage": base if attack else "",
                "weakness_applies": "yes" if hits else "no",
                "damage_after_weakness": base * 2 if hits else base,
            })
    return rows


def energy_rows() -> list[dict]:
    profiles = [
        ("Double Colorless Energy", "dce", False, False, False, False),
        ("Counter Energy, behind, not GX/EX", "counter", True, False, False, True),
        ("Counter Energy, not behind", "counter", True, False, False, False),
        ("Reversal Energy, behind, no Rule Box", "reversal", True, False, False, True),
        ("Reversal Energy, behind, Rule Box", "reversal", True, True, False, True),
        ("Triple Acceleration Energy on an Evolution", "triple", True, False, False, False),
        ("Ignition Energy on an Evolution", "ignition", True, False, False, False),
        ("Ignition Energy on a Basic", "ignition", False, False, False, False),
    ]
    rows = []
    seen = set()
    for cards in DECKS.values():
        for card in cards:
            if card["kind"] != "pokemon" or not card["attacks"] or card["name"] in seen:
                continue
            seen.add(card["name"])
            for tag, cost, damage in card["attacks"]:
                for label, kind, evolution, rule_box, gx_ex, behind in profiles:
                    symbols = energy_symbols(
                        kind, "Psychic", evolution=evolution, rule_box=rule_box, gx_ex=gx_ex, behind=behind,
                    )
                    rows.append({
                        "pokemon": card["name"],
                        "attack": tag,
                        "cost": " ".join(cost),
                        "printed_base": damage,
                        "energy": label,
                        "provides": "" if symbols is None else " ".join(symbols),
                        "pays_cost": "no" if symbols is None else ("yes" if pays(cost, symbols) else "no"),
                    })
    return rows


def deck_rows() -> list[dict]:
    rows = []
    for name, cards in DECKS.items():
        if deck_size(cards) != 60:
            raise SystemExit(f"{name} is {deck_size(cards)}")
        for card in cards:
            rows.append({
                "deck": name,
                "count": card["count"],
                "name": card["name"],
                "set": card.get("set"),
                "number": card.get("number"),
                "kind": card["kind"],
                "types": " ".join(card.get("types") or []),
                "stage": card.get("stage") or "",
            })
    return rows


def main() -> None:
    if not DUMP.exists():
        raise SystemExit(f"card dump not found at {DUMP}")
    sets = load_sets()
    duals = dual_rows(sets)
    dragons = [row for row in duals if "Dragon" in (row["type_1"], row["type_2"], row["extra_types"])]
    if dragons:
        raise SystemExit(f"unexpected dual-type Dragon cards: {dragons[:3]}")
    basics = [row for row in duals if row["stage"] == "Basic"]
    unlimited = minimum_cover(duals, NINE, expanded_only=False)
    expanded = minimum_cover(duals, NINE, expanded_only=True)
    unlimited_playable = minimum_cover(duals, NINE, expanded_only=False, only_playable=True)
    expanded_playable = minimum_cover(duals, NINE, expanded_only=True, only_playable=True)
    deck_ids = ("xy11-15", "xy11-77", "ex11-10", "ex7-39", "ex7-6")
    by_id = {row["card_id"]: row for row in duals}
    deck_cover = {
        "cards": 5,
        "pokemon": [
            {
                "pokemon": by_id[i]["pokemon"],
                "set": by_id[i]["set"],
                "printed_as": by_id[i]["printed_as"],
                "types": sorted((by_id[i]["type_1"], by_id[i]["type_2"])),
                "stage": by_id[i]["stage"],
                "legality": by_id[i]["legality"],
            }
            for i in deck_ids
        ],
    }
    write_csv(OUT / "dual_type_pokemon.csv", duals)
    write_csv(OUT / "basic_dual_type_pokemon.csv", basics)
    write_csv(OUT / "stage1_toolbox.csv", toolbox_rows(duals))
    write_csv(OUT / "type_coverage_matrix.csv", coverage_rows([
        ("unlimited absolute minimum, any dual-type card", unlimited),
        ("unlimited playable Basics and Stage 1s, no Rule Box", unlimited_playable),
        ("expanded absolute minimum, any dual-type card", expanded),
        ("expanded playable Basics and Stage 1s, no Rule Box", expanded_playable),
        ("Deck A hand package, five Stage 1 cards, one repeated Darkness", deck_cover),
    ]))
    write_csv(OUT / "weakness_coverage_matrix.csv", weakness_rows())
    write_csv(OUT / "energy_compatibility_matrix.csv", energy_rows())
    write_csv(OUT / "decklists.csv", deck_rows())
    summary = {
        "dual_type_cards": len(duals),
        "dual_type_names": len({row["pokemon"] for row in duals}),
        "basic_dual_type_cards": len(basics),
        "dragon_dual_type_cards": 0,
        "sets": dict(Counter(row["set"] for row in duals)),
        "stages": dict(Counter(row["stage"] for row in duals)),
        "unlimited_cover": unlimited,
        "expanded_cover": expanded,
        "unlimited_playable_cover": unlimited_playable,
        "expanded_playable_cover": expanded_playable,
        "deck_a_cover": deck_cover,
        "source": "Physical-card JSON snapshot at /tmp/tcg. Pocket cards are not included.",
    }
    (OUT / "coverage_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({
        "duals": len(duals),
        "basics": len(basics),
        "unlimited": unlimited["cards"],
        "unlimited_playable": unlimited_playable["cards"],
        "expanded": expanded["cards"],
        "expanded_playable": expanded_playable["cards"],
        "expanded_playable_names": [card["pokemon"] for card in expanded_playable["pokemon"]],
        "unlimited_playable_names": [card["pokemon"] for card in unlimited_playable["pokemon"]],
    }, indent=2))


if __name__ == "__main__":
    main()
