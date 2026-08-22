#!/usr/bin/env python3
"""Rank one-card swaps for Carpet Set B vs A / C / D. Same method as Set A."""

from __future__ import annotations

import json
import time
from pathlib import Path

from app.catalog import fetch_full, normalize_card
from app.engine.models import Card, default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "lab" / "set-b-buy-rank.json"
SEED = 20260818
GAMES = 2000
CUT = "Ivysaur"

CATALOG = {
    "iron-hands-ex": "sv04-070",
    "pikachu-ex": "sv08-057",
    "bulbasaur": "sv03.5-001",
    "raichu": "sv03.5-026",
    "salandit": "swsh12.5-027",
    "fuecoco": "sv04-023",
    "lickitung": "swsh11-138",
    "great-tusk-ex": "sv01-123",
    "miraidon-ex": "sv01-081",
    "wo-chien-ex": "sv02-027",
}


def load_seed_cards() -> dict[str, list[Card]]:
    data = json.loads((ROOT / "data" / "seed_decks.json").read_text())
    return {key: [Card.from_dict(c) for c in data[key]["cards"]] for key in ("a", "b", "c", "d")}


def from_deck(cards: list[Card], name: str) -> Card:
    return Card.from_dict(next(c.to_dict() for c in cards if c.name == name))


def from_id(card_id: str) -> Card:
    return normalize_card(fetch_full(card_id))


def replace(cards: list[Card], old: str, new: Card) -> list[Card]:
    out, done = [], False
    for c in cards:
        if not done and c.name == old:
            out.append(Card.from_dict(new.to_dict()))
            done = True
        else:
            out.append(Card.from_dict(c.to_dict()))
    if not done:
        raise ValueError(f"cut card {old!r} not found")
    if len(out) != len(cards):
        raise AssertionError(f"expected {len(cards)} cards after swap, got {len(out)}")
    return out


def shock_mod(**overrides) -> StrategySpec:
    base = StrategySpec.from_dict("shock").to_dict()
    protect = list(overrides.pop("protect", base["protect"]))
    search_aces = list(overrides.pop("search_aces", base["search_aces"]))
    backups = list(overrides.pop("backups", base["backups"]))
    insurance = list(overrides.pop("insurance", base["insurance"]))
    closers = list(overrides.pop("closers", base["closers"]))
    extra_protect = overrides.pop("extra_protect", [])
    extra_aces = overrides.pop("extra_aces", [])
    extra_insurance = overrides.pop("extra_insurance", [])
    extra_backups = overrides.pop("extra_backups", [])
    protect = list(dict.fromkeys(extra_protect + protect))
    search_aces = list(dict.fromkeys(extra_aces + search_aces))
    insurance = list(dict.fromkeys(extra_insurance + insurance))
    backups = list(dict.fromkeys(extra_backups + backups))
    base.update(overrides)
    base.update(
        {
            "name": "shock",
            "protect": protect,
            "search_aces": search_aces,
            "backups": backups,
            "insurance": insurance,
            "closers": closers,
        }
    )
    return StrategySpec.from_dict(base)


def pack(result: dict) -> dict:
    r = result["results"]
    return {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "b_first": 1.0 - r["win_rate_a_going_second"] if r["games_a_second"] else 0.0,
        "b_second": 1.0 - r["win_rate_a_going_first"] if r["games_a_first"] else 0.0,
    }


def run_b(b_cards: list[Card], strat_b: StrategySpec, opponents: dict, games: int, seed: int = SEED) -> dict:
    rules = default_family_rules()
    detail = {}
    rates = {}
    for tag, (opp, strat_opp) in opponents.items():
        rec = run_simulation(
            opp,
            b_cards,
            rules,
            strat_opp,
            strat_b,
            games=games,
            seed=seed,
            queries=[],
        )
        detail[tag] = pack(rec)
        rates[tag] = rec["results"]["win_rate_b"]
    avg = sum(rates.values()) / len(rates)
    return {"avg": avg, **rates, "detail": detail}


def fetch_catalog() -> dict[str, Card]:
    fetched: dict[str, Card] = {}
    for key, cid in CATALOG.items():
        try:
            fetched[key] = from_id(cid)
            print(
                f"fetched {key} {cid} hp={fetched[key].hp} "
                f"atk={[(a.name, a.damage) for a in fetched[key].attacks]}",
                flush=True,
            )
        except Exception as exc:
            print(f"SKIP {key} {cid}: {exc}", flush=True)
    return fetched


def build_candidates(decks: dict[str, list[Card]], fetched: dict[str, Card]) -> list[dict]:
    b, c, d = decks["b"], decks["c"], decks["d"]
    plusle = from_deck(b, "Plusle")
    electrike = from_deck(b, "Electrike")
    shock_pika = next(card for card in b if card.name == "Pikachu" and any(a.name == "Thunder Shock" for a in card.attacks))
    mewtwo = from_deck(c, "Mewtwo ex")
    nest = from_deck(c, "Nest Ball")
    hop = from_deck(c, "Hop")
    belt = from_deck(c, "Maximum Belt")
    charm = from_deck(d, "Bravery Charm")
    energy_search = from_deck(b, "Energy Search")
    shock = StrategySpec.from_dict("shock")

    candidates: list[dict] = [
        {"label": "baseline", "cut": None, "card": None, "strat": shock},
        {"label": "Lightning Energy", "cut": CUT, "card": fallback_named("Lightning Energy"), "strat": shock},
        {"label": "Nest Ball", "cut": CUT, "card": nest, "strat": shock},
        {"label": "Poké Ball", "cut": CUT, "card": fallback_named("Poké Ball"), "strat": shock},
        {"label": "Ultra Ball", "cut": CUT, "card": fallback_named("Ultra Ball"), "strat": shock},
        {"label": "Hop", "cut": CUT, "card": hop, "strat": shock},
        {"label": "Bravery Charm", "cut": CUT, "card": charm, "strat": shock},
        {"label": "Maximum Belt", "cut": CUT, "card": belt, "strat": shock},
        {"label": "Switch", "cut": CUT, "card": fallback_named("Switch"), "strat": shock},
        {"label": "2nd Plusle", "cut": CUT, "card": plusle, "strat": shock},
        {"label": "2nd Electrike", "cut": CUT, "card": electrike, "strat": shock},
        {"label": "3rd Pikachu (Thunder Shock)", "cut": CUT, "card": shock_pika, "strat": shock},
        {"label": "2nd Energy Search", "cut": CUT, "card": energy_search, "strat": shock},
        {
            "label": "Professor's Research",
            "cut": CUT,
            "card": fallback_named("Professor's Research"),
            "strat": shock,
        },
        {
            "label": "Mewtwo ex (tank, don't attach)",
            "cut": CUT,
            "card": mewtwo,
            "strat": shock_mod(extra_protect=["Mewtwo ex"], extra_insurance=["Mewtwo ex"], extra_backups=["Mewtwo ex"]),
        },
        {
            "label": "Mewtwo ex (vanilla shock)",
            "cut": CUT,
            "card": mewtwo,
            "strat": shock,
        },
        {
            "label": "Lightning Energy (cut Grass Energy)",
            "cut": "Grass Energy",
            "card": fallback_named("Lightning Energy"),
            "strat": shock,
        },
        {
            "label": "Nest Ball (cut Grass Energy)",
            "cut": "Grass Energy",
            "card": nest,
            "strat": shock,
        },
    ]
    if "iron-hands-ex" in fetched:
        hands = fetched["iron-hands-ex"]
        candidates.append(
            {
                "label": "Iron Hands ex (new ace)",
                "cut": CUT,
                "card": hands,
                "strat": shock_mod(
                    extra_protect=["Iron Hands ex"],
                    extra_aces=["Iron Hands ex"],
                    extra_backups=["Iron Hands ex"],
                    extra_insurance=["Iron Hands ex"],
                ),
            }
        )
        candidates.append({"label": "Iron Hands ex (vanilla shock)", "cut": CUT, "card": hands, "strat": shock})
    if "pikachu-ex" in fetched:
        pex = fetched["pikachu-ex"]
        candidates.append(
            {
                "label": "Pikachu ex (new ace)",
                "cut": CUT,
                "card": pex,
                "strat": shock_mod(
                    extra_protect=["Pikachu ex"],
                    extra_aces=["Pikachu ex"],
                    extra_backups=["Pikachu ex"],
                ),
            }
        )
    if "bulbasaur" in fetched:
        candidates.append({"label": "Bulbasaur", "cut": CUT, "card": fetched["bulbasaur"], "strat": shock})
        candidates.append(
            {
                "label": "Bulbasaur (grass ace)",
                "cut": CUT,
                "card": fetched["bulbasaur"],
                "strat": shock_mod(
                    extra_protect=["Bulbasaur", "Ivysaur", "Tangela"],
                    extra_aces=["Bulbasaur", "Tangela", "Ivysaur"],
                ),
            }
        )
    if "raichu" in fetched:
        candidates.append({"label": "Raichu", "cut": CUT, "card": fetched["raichu"], "strat": shock})
    if "salandit" in fetched:
        candidates.append({"label": "Salandit", "cut": CUT, "card": fetched["salandit"], "strat": shock})
    if "fuecoco" in fetched:
        candidates.append({"label": "Fuecoco", "cut": CUT, "card": fetched["fuecoco"], "strat": shock})
    if "lickitung" in fetched:
        candidates.append({"label": "Lickitung", "cut": CUT, "card": fetched["lickitung"], "strat": shock})
    if "wo-chien-ex" in fetched:
        wo = fetched["wo-chien-ex"]
        candidates.append(
            {
                "label": "Wo-Chien ex (grass ace)",
                "cut": CUT,
                "card": wo,
                "strat": shock_mod(
                    extra_protect=["Wo-Chien ex"],
                    extra_aces=["Wo-Chien ex"],
                    extra_backups=["Wo-Chien ex"],
                    extra_insurance=["Wo-Chien ex"],
                ),
            }
        )
    if "great-tusk-ex" in fetched:
        candidates.append(
            {
                "label": "Great Tusk ex (fighting ace)",
                "cut": CUT,
                "card": fetched["great-tusk-ex"],
                "strat": shock_mod(
                    extra_protect=["Great Tusk ex"],
                    extra_aces=["Great Tusk ex"],
                    extra_insurance=["Great Tusk ex"],
                ),
            }
        )
    if "miraidon-ex" in fetched:
        candidates.append(
            {
                "label": "Miraidon ex (new ace)",
                "cut": CUT,
                "card": fetched["miraidon-ex"],
                "strat": shock_mod(
                    extra_protect=["Miraidon ex"],
                    extra_aces=["Miraidon ex"],
                    extra_backups=["Miraidon ex"],
                ),
            }
        )
    return candidates


def main() -> None:
    decks = load_seed_cards()
    opponents = {
        "A": (decks["a"], StrategySpec.from_dict("thrifty")),
        "C": (decks["c"], StrategySpec.from_dict("party")),
        "D": (decks["d"], StrategySpec.from_dict("demolish")),
    }
    fetched = fetch_catalog()
    candidates = build_candidates(decks, fetched)
    started = time.perf_counter()
    rows = []
    for i, cand in enumerate(candidates, 1):
        t0 = time.perf_counter()
        if cand["cut"] is None:
            deck = [Card.from_dict(c.to_dict()) for c in decks["b"]]
        else:
            deck = replace(decks["b"], cand["cut"], cand["card"])
        row = run_b(deck, cand["strat"], opponents, games=GAMES)
        row["label"] = cand["label"]
        row["cut"] = cand["cut"] or ""
        rows.append(row)
        elapsed = time.perf_counter() - t0
        print(
            f"[{i}/{len(candidates)}] {cand['label']:<36} "
            f"A={row['A']:.3f} C={row['C']:.3f} D={row['D']:.3f} avg={row['avg']:.3f}  {elapsed:.1f}s",
            flush=True,
        )
    rows.sort(key=lambda r: r["avg"], reverse=True)
    payload = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": time.perf_counter() - started,
        "cut_default": CUT,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"\nWrote {OUT} in {payload['elapsed']:.1f}s")
    print("\nRank by B win-rate average vs A/C/D:")
    for row in rows:
        print(f"  {row['avg']:.3f}  {row['label']:<36}  vsA {row['A']:.3f}  vsC {row['C']:.3f}  vsD {row['D']:.3f}")


if __name__ == "__main__":
    main()
