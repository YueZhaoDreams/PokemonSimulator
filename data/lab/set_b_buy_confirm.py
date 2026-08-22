#!/usr/bin/env python3
"""Confirm top Set B buys at 5000 vs A/C and 3000 vs D."""

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
OUT = ROOT / "data" / "lab" / "set-b-buy-confirm.json"
SEED = 20260818
CUT = "Crocalor"
GAMES_AC = 5000
GAMES_D = 3000


def load_seed_cards() -> dict[str, list[Card]]:
    data = json.loads((ROOT / "data" / "seed_decks.json").read_text())
    return {key: [Card.from_dict(c) for c in data[key]["cards"]] for key in ("a", "b", "c", "d")}


def from_deck(cards, name):
    return Card.from_dict(next(c.to_dict() for c in cards if c.name == name))


def from_id(cid):
    return normalize_card(fetch_full(cid))


def replace(cards, old, new):
    out, done = [], False
    for c in cards:
        if not done and c.name == old:
            out.append(Card.from_dict(new.to_dict()))
            done = True
        else:
            out.append(Card.from_dict(c.to_dict()))
    if not done or len(out) != len(cards):
        raise AssertionError(f"swap {old!r} failed (len {len(out)} vs {len(cards)})")
    return out


def shock_mod(**overrides) -> StrategySpec:
    base = StrategySpec.from_dict("shock").to_dict()
    protect = list(dict.fromkeys(overrides.pop("extra_protect", []) + base["protect"]))
    search_aces = list(dict.fromkeys(overrides.pop("extra_aces", []) + base["search_aces"]))
    backups = list(dict.fromkeys(overrides.pop("extra_backups", []) + base["backups"]))
    insurance = list(dict.fromkeys(overrides.pop("extra_insurance", []) + base["insurance"]))
    base.update(overrides)
    base.update(
        {
            "name": "shock",
            "protect": protect,
            "search_aces": search_aces,
            "backups": backups,
            "insurance": insurance,
        }
    )
    return StrategySpec.from_dict(base)


def pack(result):
    r = result["results"]
    return {"a": r["win_rate_a"], "b": r["win_rate_b"], "tie": r["tie_rate"]}


def run_b(b_cards, strat_b, opponents, games_ac=GAMES_AC, games_d=GAMES_D):
    rules = default_family_rules()
    detail, rates = {}, {}
    for tag, (opp, strat_opp) in opponents.items():
        games = games_d if tag == "D" else games_ac
        rec = run_simulation(opp, b_cards, rules, strat_opp, strat_b, games=games, seed=SEED, queries=[])
        detail[tag] = pack(rec)
        rates[tag] = rec["results"]["win_rate_b"]
    return {"avg": sum(rates.values()) / 3, **rates, "detail": detail}


def build_candidates(decks: dict[str, list[Card]]) -> list[dict]:
    b, c, d = decks["b"], decks["c"], decks["d"]
    shock = StrategySpec.from_dict("shock")
    hands = from_id("sv04-070")
    miraidon = from_id("sv01-081")
    tusk = from_id("sv01-123")
    pex = from_id("sv08-057")
    wo = from_id("sv02-027")
    belt = from_deck(c, "Maximum Belt")
    charm = from_deck(d, "Bravery Charm")
    nest = from_deck(c, "Nest Ball")
    mewtwo = from_deck(c, "Mewtwo ex")
    return [
        {"label": "baseline", "cut": None, "card": None, "strat": shock},
        {
            "label": "Iron Hands ex",
            "cut": CUT,
            "card": hands,
            "strat": shock_mod(
                extra_protect=["Iron Hands ex"],
                extra_aces=["Iron Hands ex"],
                extra_backups=["Iron Hands ex"],
                extra_insurance=["Iron Hands ex"],
            ),
        },
        {
            "label": "Miraidon ex",
            "cut": CUT,
            "card": miraidon,
            "strat": shock_mod(extra_protect=["Miraidon ex"], extra_aces=["Miraidon ex"], extra_backups=["Miraidon ex"]),
        },
        {
            "label": "Great Tusk ex",
            "cut": CUT,
            "card": tusk,
            "strat": shock_mod(extra_protect=["Great Tusk ex"], extra_aces=["Great Tusk ex"], extra_insurance=["Great Tusk ex"]),
        },
        {
            "label": "Pikachu ex",
            "cut": CUT,
            "card": pex,
            "strat": shock_mod(extra_protect=["Pikachu ex"], extra_aces=["Pikachu ex"], extra_backups=["Pikachu ex"]),
        },
        {"label": "Maximum Belt", "cut": CUT, "card": belt, "strat": shock},
        {"label": "Bravery Charm", "cut": CUT, "card": charm, "strat": shock},
        {
            "label": "Wo-Chien ex",
            "cut": CUT,
            "card": wo,
            "strat": shock_mod(
                extra_protect=["Wo-Chien ex"],
                extra_aces=["Wo-Chien ex"],
                extra_backups=["Wo-Chien ex"],
                extra_insurance=["Wo-Chien ex"],
            ),
        },
        {"label": "Nest Ball", "cut": CUT, "card": nest, "strat": shock},
        {
            "label": "Mewtwo ex (tank)",
            "cut": CUT,
            "card": mewtwo,
            "strat": shock_mod(extra_protect=["Mewtwo ex"], extra_insurance=["Mewtwo ex"], extra_backups=["Mewtwo ex"]),
        },
        {"label": "Lightning Energy", "cut": CUT, "card": fallback_named("Lightning Energy"), "strat": shock},
        {"label": "Poké Ball", "cut": CUT, "card": fallback_named("Poké Ball"), "strat": shock},
    ]


def main():
    decks = load_seed_cards()
    opponents = {
        "A": (decks["a"], StrategySpec.from_dict("thrifty")),
        "C": (decks["c"], StrategySpec.from_dict("party")),
        "D": (decks["d"], StrategySpec.from_dict("demolish")),
    }
    candidates = build_candidates(decks)
    started = time.perf_counter()
    rows = []
    for i, cand in enumerate(candidates, 1):
        t0 = time.perf_counter()
        deck = [Card.from_dict(c.to_dict()) for c in decks["b"]] if cand["cut"] is None else replace(decks["b"], cand["cut"], cand["card"])
        row = run_b(deck, cand["strat"], opponents)
        row["label"] = cand["label"]
        row["cut"] = cand["cut"] or ""
        rows.append(row)
        print(
            f"[{i}/{len(candidates)}] {cand['label']:<22} "
            f"A={row['A']:.3f} C={row['C']:.3f} D={row['D']:.3f} avg={row['avg']:.3f}  {time.perf_counter()-t0:.1f}s",
            flush=True,
        )
    rows.sort(key=lambda r: r["avg"], reverse=True)
    payload = {
        "games_ac": GAMES_AC,
        "games_d": GAMES_D,
        "seed": SEED,
        "elapsed": time.perf_counter() - started,
        "rows": rows,
    }
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"\nWrote {OUT} in {payload['elapsed']:.1f}s")
    for row in rows:
        print(f"  {row['avg']:.3f}  {row['label']:<22}  vsA {row['A']:.3f}  vsC {row['C']:.3f}  vsD {row['D']:.3f}")


if __name__ == "__main__":
    main()
