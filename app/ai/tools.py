from __future__ import annotations

import json
from typing import Any

from app.catalog import search_local
from app.db import get_deck, get_rules, list_decks, list_simulations, save_simulation
from app.engine.models import Card
from app.engine.montecarlo import run_simulation
from app.engine.probability import draw_probability
from app.engine.strategies import StrategySpec
from app.engine.trades import suggest_trades

TOOL_SCHEMAS = [
    {
        "name": "list_decks",
        "description": "List saved card sets and a short summary of each.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_deck",
        "description": "Get the full card list for a deck id (seed-a, seed-b, or a scanned deck).",
        "parameters": {
            "type": "object",
            "properties": {"deck_id": {"type": "string"}},
            "required": ["deck_id"],
        },
    },
    {
        "name": "draw_odds",
        "description": "Exact hypergeometric probability that a named card appears in the opening hand (or any draw of N cards).",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_id": {"type": "string"},
                "card_name": {"type": "string"},
                "draw": {"type": "integer", "default": 7},
            },
            "required": ["deck_id", "card_name"],
        },
    },
    {
        "name": "simulate_match",
        "description": "Run a Monte Carlo match between two decks. Use 1000-10000 games. Records strategy, results, and what was learned.",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_a_id": {"type": "string"},
                "deck_b_id": {"type": "string"},
                "games": {"type": "integer", "default": 2000},
                "strategy_a": {"type": "string", "description": "aggressive|setup|control|balanced"},
                "strategy_b": {"type": "string"},
                "question": {"type": "string"},
            },
            "required": ["deck_a_id", "deck_b_id"],
        },
    },
    {
        "name": "suggest_trades",
        "description": "Find win-win one-for-one trades so both family decks get stronger while the matchup stays fair.",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_a_id": {"type": "string"},
                "deck_b_id": {"type": "string"},
                "games": {"type": "integer", "default": 300},
            },
            "required": ["deck_a_id", "deck_b_id"],
        },
    },
    {
        "name": "get_rules",
        "description": "Show the current family ruleset.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "list_lab",
        "description": "List recent simulation lab records.",
        "parameters": {"type": "object", "properties": {}},
    },
]


def _cards(deck: dict) -> list[Card]:
    return [Card.from_dict(c) for c in deck["cards"]]


def _default_ids() -> tuple[str, str]:
    decks = list_decks()
    if len(decks) >= 2:
        return decks[0]["id"], decks[1]["id"]
    return "seed-a", "seed-b"


def run_tool(name: str, args: dict[str, Any]) -> Any:
    if name == "list_decks":
        return [
            {"id": d["id"], "name": d["name"], "count": d["count"], "cards": [c["name"] for c in d["cards"]]}
            for d in list_decks()
        ]
    if name == "get_deck":
        deck = get_deck(args["deck_id"])
        if not deck:
            return {"error": "deck not found"}
        return {"id": deck["id"], "name": deck["name"], "cards": [c["name"] for c in deck["cards"]]}
    if name == "get_rules":
        return get_rules().to_dict()
    if name == "list_lab":
        return list_simulations()
    if name == "draw_odds":
        deck = get_deck(args["deck_id"])
        if not deck:
            return {"error": "deck not found"}
        names = [c["name"] for c in deck["cards"]]
        return draw_probability(args["card_name"], names, int(args.get("draw") or 7))
    if name == "simulate_match":
        deck_a = get_deck(args["deck_a_id"])
        deck_b = get_deck(args["deck_b_id"])
        if not deck_a or not deck_b:
            return {"error": "need two saved decks"}
        rules = get_rules()
        games = int(args.get("games") or 2000)
        record = run_simulation(
            _cards(deck_a),
            _cards(deck_b),
            rules,
            StrategySpec.from_dict(args.get("strategy_a") or "balanced"),
            StrategySpec.from_dict(args.get("strategy_b") or "control"),
            games=games,
            question=args.get("question"),
            queries=[
                {"type": "opening_hand_contains", "side": "a", "card": "Dondozo", "key": "dondozo_opening_a"},
                {
                    "type": "status",
                    "attacker": "Pikachu",
                    "defender": "Dondozo",
                    "status": "paralyzed",
                    "key": "pikachu_paralyze_dondozo",
                },
            ],
            deck_a_meta={"id": deck_a["id"], "name": deck_a["name"]},
            deck_b_meta={"id": deck_b["id"], "name": deck_b["name"]},
        )
        save_simulation(record)
        return {
            "simulation_id": record["id"],
            "method": record["method"],
            "strategies": record["strategies"],
            "results": record["results"],
            "learning": record["learning"],
        }
    if name == "suggest_trades":
        deck_a = get_deck(args["deck_a_id"])
        deck_b = get_deck(args["deck_b_id"])
        if not deck_a or not deck_b:
            return {"error": "need two saved decks"}
        rules = get_rules()
        rec = suggest_trades(
            _cards(deck_a),
            _cards(deck_b),
            rules,
            StrategySpec.from_dict("balanced"),
            StrategySpec.from_dict("control"),
            games=int(args.get("games") or 240),
        )
        return rec
    if name == "search_cards":
        return search_local(args.get("query") or "")
    return {"error": f"unknown tool {name}"}
