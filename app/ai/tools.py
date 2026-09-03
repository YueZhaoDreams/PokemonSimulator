from __future__ import annotations

import json
from contextvars import ContextVar, Token
from typing import Any

from app.catalog import fetch_full, lookup_seed_card, normalize_card, resolve_name, search_local
from app.db import (
    get_deck,
    get_lab_experiment,
    get_rules,
    list_decks,
    list_lab_experiments,
    list_simulations,
    save_deck,
    save_lab_experiment,
    save_simulation,
)
from app.engine.models import CANONICAL_RULE_PRESETS, Card, resolve_simulation_rules, rule_preset_label
from app.engine.montecarlo import run_simulation
from app.engine.overlay import OverlayError
from app.engine.probability import draw_probability
from app.engine.strategies import StrategySpec, list_strategies
from app.engine.trades import suggest_trades
from app.lab.report import payload_cells, payload_conclusion, payload_results
from app.lab.runner import run_lab_experiment
from app.lab.sandbox import run_lab_script

_VIEWER: ContextVar[dict | None] = ContextVar("deck_viewer", default=None)

TOOL_SCHEMAS = [
    {
        "name": "list_decks",
        "description": "List saved card sets and a short summary of each.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_deck",
        "description": "Get cards in a set with catalog id, HP, set name, and attack names/text. Use this before explaining why a move was missing.",
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
        "description": "Run a Monte Carlo match between two decks. Use 1000-10000 games. Pass rule_preset b (30 cards 4 of a name, Pokémon = energy), c (30 cards 4 of a name), s30 (Standard 30, 2 of a name), or s60 (Standard 60). Does not change the Fight tab or git.",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_a_id": {"type": "string"},
                "deck_b_id": {"type": "string"},
                "games": {"type": "integer", "default": 2000},
                "strategy_a": {
                    "type": ["string", "object"],
                    "description": "Preset name (thrifty|shock|nuzzle|party|demolish|slash|phantom|aggressive|setup|control|balanced) or a StrategySpec overlay (weights, when-clauses). Not printed look-N."
                },
                "strategy_b": {
                    "type": ["string", "object"],
                    "description": "Preset name or StrategySpec overlay.",
                },
                "question": {"type": "string"},
                "queries": {"type": "array"},
                "rule_preset": {
                    "type": "string",
                    "description": "b, c, s30, or s60. Omit to infer from the two decks (E/F → c) or use household rules.",
                },
                "card_overlay": {
                    "type": "object",
                    "description": (
                        "Catalog-id keyed overlay for this match only (both decks). "
                        "Each value may include params, effects or program, attack, decisions. "
                        "Published effect kinds only. Cannot raise a parsed look above print. Does not write git."
                    ),
                },
                "card_overlay_a": {"type": "object", "description": "Same overlay shape, deck A only."},
                "card_overlay_b": {"type": "object", "description": "Same overlay shape, deck B only."},
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
                "rule_preset": {"type": "string"},
            },
            "required": ["deck_a_id", "deck_b_id"],
        },
    },
    {
        "name": "get_rules",
        "description": "Show the household default Family Cup rules plus selectable presets b, c, s30, and s60. Simulations may override with rule_preset; this does not change git.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "list_lab",
        "description": "List recent Fight simulation records (one matchup each).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "list_lab_experiments",
        "description": "List this trainer's lab questions (question, attempts, conclusion). Not git files.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "get_lab_experiment",
        "description": "Get one lab question this trainer owns, including attempts, conclusion, and script_text if stored.",
        "parameters": {
            "type": "object",
            "properties": {"experiment_id": {"type": "string"}},
            "required": ["experiment_id"],
        },
    },
    {
        "name": "save_lab_experiment",
        "description": (
            "Create a lab question or update one this trainer owns. "
            "Pass experiment_id to add another run on the same question (send the full attempts list). "
            "attempts is the customer shape; cells still works. Do not write data/lab/ or app/."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "experiment_id": {
                    "type": "string",
                    "description": "Existing question to update. Omit to create a new row.",
                },
                "question": {"type": "string"},
                "conclusion": {"type": ["string", "null"], "description": "Current written conclusion for this question."},
                "attempts": {
                    "type": "array",
                    "description": "Runs to try (id, title, input with decks/strategies/patch/overlay). Replaces cells when sent.",
                },
                "cells": {"type": "array", "description": "Compatibility alias for attempts input. Ignored if attempts is sent."},
                "queries": {"type": "array"},
                "games": {"type": "integer"},
                "seed": {"type": "integer"},
                "script_text": {"type": ["string", "null"]},
                "results": {"type": ["object", "array", "null"]},
                "locked_cell_id": {"type": ["string", "null"]},
                "lock_reason": {"type": ["string", "null"]},
            },
        },
    },
    {
        "name": "run_lab",
        "description": "Run this trainer's lab question (every attempt) at the shared seed and games. Persists the report. Do not write data/lab/ or app/.",
        "parameters": {
            "type": "object",
            "properties": {
                "experiment_id": {"type": "string"},
                "games": {"type": "integer"},
                "seed": {"type": "integer"},
                "rule_preset": {"type": "string", "description": "b, c, s30, or s60; omit to infer from the runs' decks."},
            },
            "required": ["experiment_id"],
        },
    },
    {
        "name": "run_lab_script",
        "description": (
            "Run this trainer's stored lab Python in the game sandbox. "
            "The script must already be a Family Cup bakeoff (run_simulation / StrategySpec / Card). "
            "Hostile imports are not executable. Results stay in the database, never in git."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "experiment_id": {"type": "string"},
                "games": {"type": "integer"},
                "seed": {"type": "integer"},
                "rule_preset": {"type": "string", "description": "b or c; omit to infer from saved decks."},
            },
            "required": ["experiment_id"],
        },
    },
    {
        "name": "list_strategies",
        "description": "List named Family Cup strategies the engine can run (thrifty, shock, party, demolish, slash, …).",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "name": "search_cards",
        "description": "Search the local card catalog by name, HP, collector number, or attack hint.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "replace_deck_card",
        "description": "Replace a printing in this trainer's set (database, not git). Use when the name is right but attacks are wrong (e.g. Raichu Electro Ball vs Ambushing Spark). Photo rescan is the Cards tab; this tool takes catalog_id, query, or attack phrases.",
        "parameters": {
            "type": "object",
            "properties": {
                "deck_id": {"type": "string"},
                "index": {"type": "integer", "description": "0-based slot. If omitted, replace every card matching name."},
                "name": {"type": "string"},
                "catalog_id": {"type": "string"},
                "query": {"type": "string", "description": "e.g. Raichu Electro Ball or Paldea Evolved"},
                "prefer": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["deck_id"],
        },
    },
]


def use_viewer(user: dict | None) -> Token:
    return _VIEWER.set(user)


def reset_viewer(token: Token) -> None:
    _VIEWER.reset(token)


def current_viewer() -> dict | None:
    return _VIEWER.get()


def chat_visible(chat: dict | None) -> bool:
    if not chat:
        return False
    user = _VIEWER.get()
    if not user or user.get("role") == "admin":
        return True
    return chat.get("owner_id") == user["id"]


def _experiment_visible(experiment: dict | None) -> bool:
    if not experiment:
        return False
    user = _VIEWER.get()
    if not user:
        return False
    if user.get("role") == "admin":
        return True
    return experiment.get("owner_id") == user["id"]


def _visible_decks() -> list[dict]:
    user = _VIEWER.get()
    if user and user.get("role") != "admin":
        return list_decks(owner_id=user["id"])
    return list_decks()


def _usable_deck(deck_id: str) -> dict | None:
    deck = get_deck(deck_id)
    if not deck:
        return None
    user = _VIEWER.get()
    if user and user.get("role") != "admin" and deck.get("owner_id") != user["id"]:
        return None
    return deck


def _cards(deck: dict) -> list[Card]:
    return [Card.from_dict(c) for c in deck["cards"]]


def _card_tool_view(raw: dict, index: int) -> dict[str, Any]:
    attacks = [a for a in (raw.get("attacks") or []) if isinstance(a, dict)]
    category = str(raw.get("category") or raw.get("supertype") or "Pokemon")
    unresolved = category.lower() == "pokemon" and not attacks
    return {
        "index": index,
        "name": raw.get("name"),
        "catalog_id": raw.get("catalog_id") or raw.get("id"),
        "set_name": raw.get("set_name"),
        "hp": raw.get("hp") or 0,
        "print_unresolved": unresolved,
        "attacks": [
            {"name": a.get("name"), "damage": a.get("damage") or 0, "text": (a.get("text") or a.get("effect") or "")[:180]}
            for a in attacks
        ],
    }


def _prefer_phrases(args: dict[str, Any], name: str) -> list[str]:
    raw = args.get("prefer")
    if isinstance(raw, str):
        phrases = [raw]
    elif isinstance(raw, list):
        phrases = [str(p) for p in raw if str(p).strip()]
    else:
        phrases = []
    query = str(args.get("query") or "").strip()
    if query:
        leftover = query
        if name and leftover.lower().startswith(name.lower()):
            leftover = leftover[len(name) :].strip(" ,/-")
        if leftover and leftover.lower() not in {p.lower() for p in phrases}:
            phrases.append(leftover)
    return phrases


def _load_catalog_card(catalog_id: str) -> dict[str, Any] | None:
    cid = str(catalog_id or "").strip()
    if not cid:
        return None
    seed = lookup_seed_card(catalog_id=cid)
    if seed:
        return seed.to_dict()
    try:
        return normalize_card(fetch_full(cid)).to_dict()
    except Exception:
        return None


def _resolve_replacement(args: dict[str, Any], current_name: str) -> dict[str, Any]:
    catalog_id = str(args.get("catalog_id") or "").strip()
    name = str(args.get("name") or current_name or "").strip()
    query = str(args.get("query") or "").strip()
    if query and not name:
        name = query.split()[0]
    if catalog_id:
        loaded = _load_catalog_card(catalog_id)
        if not loaded:
            return {"error": f"could not load printing {catalog_id}"}
        return loaded
    if not name:
        return {"error": "name, query, or catalog_id required"}
    prefer = _prefer_phrases(args, name)
    try:
        return resolve_name(name, prefer or None).to_dict()
    except Exception as exc:
        return {"error": str(exc)}


def _replace_deck_card(args: dict[str, Any]) -> dict[str, Any]:
    deck = _usable_deck(str(args.get("deck_id") or ""))
    if not deck:
        return {"error": "deck not found"}
    cards = list(deck.get("cards") or [])
    if not cards:
        return {"error": "that set has no cards"}
    index = args.get("index")
    name = str(args.get("name") or "").strip()
    slots: list[int] = []
    if index is not None and str(index) != "":
        try:
            idx = int(index)
        except (TypeError, ValueError):
            return {"error": "index must be an integer"}
        if idx < 0 or idx >= len(cards):
            return {"error": "index out of range"}
        slots = [idx]
        name = name or str(cards[idx].get("name") or "")
    elif name:
        slots = [i for i, card in enumerate(cards) if str(card.get("name") or "").lower() == name.lower()]
        if not slots:
            return {"error": f"{name} is not in that set"}
    else:
        query = str(args.get("query") or "").strip()
        guess = query.split()[0] if query else ""
        if guess:
            slots = [i for i, card in enumerate(cards) if str(card.get("name") or "").lower() == guess.lower()]
            name = guess
        if not slots:
            return {"error": "pass index or the card name to replace"}
    replacement = _resolve_replacement(args, name)
    if replacement.get("error"):
        return replacement
    for slot in slots:
        cards[slot] = replacement
    saved = save_deck(
        deck["name"],
        cards,
        source=deck.get("source"),
        deck_id=deck["id"],
        owner_id=deck.get("owner_id"),
    )
    return {
        "id": saved["id"],
        "name": saved["name"],
        "replaced": slots,
        "card": _card_tool_view(replacement, slots[0]),
        "cards": [_card_tool_view(card, i) for i, card in enumerate(saved.get("cards") or [])],
    }


def _match_rules(*, rule_preset: object = None, decks: list[dict | None] | None = None):
    try:
        return resolve_simulation_rules(
            rule_preset=None if rule_preset in (None, "") else str(rule_preset),
            decks=decks or [],
            fallback=get_rules(),
        )
    except ValueError as exc:
        return {"error": str(exc)}


def _default_ids() -> tuple[str, str]:
    decks = _visible_decks()
    if len(decks) >= 2:
        return decks[0]["id"], decks[1]["id"]
    if len(decks) == 1:
        return decks[0]["id"], decks[0]["id"]
    user = _VIEWER.get()
    if user and user.get("role") != "admin":
        return "", ""
    return "seed-a", "seed-b"


def fill_default_args(args: dict[str, Any] | None, question: str | None = None) -> dict[str, Any]:
    filled = dict(args or {})
    a_id, b_id = _default_ids()
    filled.setdefault("deck_a_id", a_id)
    filled.setdefault("deck_b_id", b_id)
    if "deck_id" in filled and not filled["deck_id"]:
        filled["deck_id"] = a_id
    if question and not filled.get("question"):
        filled["question"] = question
    return filled


def run_tool(name: str, args: dict[str, Any]) -> Any:
    if name == "list_decks":
        return [
            {"id": d["id"], "name": d["name"], "count": d["count"], "cards": [c["name"] for c in d["cards"]]}
            for d in _visible_decks()
        ]
    if name == "get_deck":
        deck = _usable_deck(args["deck_id"])
        if not deck:
            return {"error": "deck not found"}
        return {
            "id": deck["id"],
            "name": deck["name"],
            "cards": [_card_tool_view(card, i) for i, card in enumerate(deck.get("cards") or [])],
        }
    if name == "get_rules":
        body = get_rules().to_dict()
        body["selectable_presets"] = [
            {"id": key, "label": rule_preset_label(key)} for key in CANONICAL_RULE_PRESETS
        ]
        body["note"] = (
            "Pass rule_preset b, c, s30, or s60 on simulate_match or run_lab. "
            "That runs in the chat sandbox and does not change the Fight tab or git."
        )
        return body
    if name == "list_lab":
        return list_simulations()
    if name == "list_lab_experiments":
        user = _VIEWER.get()
        if not user:
            return {"error": "sign in required"}
        if user.get("role") != "admin":
            return list_lab_experiments(owner_id=user["id"])
        return list_lab_experiments()
    if name == "get_lab_experiment":
        experiment = get_lab_experiment(args.get("experiment_id") or "")
        if not _experiment_visible(experiment):
            return {"error": "experiment not found"}
        return experiment
    if name == "save_lab_experiment":
        user = _VIEWER.get()
        if not user:
            return {"error": "sign in required"}
        existing = None
        exp_id = args.get("experiment_id")
        if exp_id:
            existing = get_lab_experiment(exp_id)
            if existing and not _experiment_visible(existing):
                return {"error": "experiment not found"}
            if existing is None:
                return {"error": "experiment not found"}
        try:
            return save_lab_experiment(
                owner_id=existing["owner_id"] if existing else user["id"],
                question=args.get("question") if "question" in args or not existing else existing.get("question"),
                cells=payload_cells(args, existing),
                queries=args["queries"] if "queries" in args else (existing or {}).get("queries"),
                games=args["games"] if "games" in args else (existing or {}).get("games"),
                seed=args["seed"] if "seed" in args else (existing or {}).get("seed"),
                results=payload_results(args, existing),
                locked_cell_id=args["locked_cell_id"] if "locked_cell_id" in args else (existing or {}).get("locked_cell_id"),
                lock_reason=args["lock_reason"] if "lock_reason" in args else (existing or {}).get("lock_reason"),
                script_text=args["script_text"] if "script_text" in args else (existing or {}).get("script_text"),
                conclusion=payload_conclusion(args, existing),
                exp_id=existing["id"] if existing else None,
            )
        except ValueError as exc:
            return {"error": str(exc)}
    if name == "run_lab":
        user = _VIEWER.get()
        if not user:
            return {"error": "sign in required"}
        experiment = get_lab_experiment(args.get("experiment_id") or "")
        if not _experiment_visible(experiment):
            return {"error": "experiment not found"}
        try:
            cell_decks: list[dict | None] = []
            for cell in experiment.get("cells") or []:
                if not isinstance(cell, dict):
                    continue
                cell_decks.append(_usable_deck(str(cell.get("deck_a_id") or "")))
                cell_decks.append(_usable_deck(str(cell.get("deck_b_id") or "")))
            rules = _match_rules(rule_preset=args.get("rule_preset"), decks=cell_decks)
            if isinstance(rules, dict) and rules.get("error"):
                return rules
            return run_lab_experiment(
                experiment,
                deck_for=_usable_deck,
                rules=rules,
                games=args.get("games"),
                seed=args.get("seed"),
            )
        except ValueError as exc:
            return {"error": str(exc)}
    if name == "run_lab_script":
        user = _VIEWER.get()
        if not user:
            return {"error": "sign in required"}
        experiment = get_lab_experiment(args.get("experiment_id") or "")
        if not _experiment_visible(experiment):
            return {"error": "experiment not found"}
        try:
            cell_decks: list[dict | None] = []
            for cell in experiment.get("cells") or []:
                if not isinstance(cell, dict):
                    continue
                cell_decks.append(_usable_deck(str(cell.get("deck_a_id") or "")))
                cell_decks.append(_usable_deck(str(cell.get("deck_b_id") or "")))
            rules = _match_rules(rule_preset=args.get("rule_preset"), decks=cell_decks or _visible_decks())
            if isinstance(rules, dict) and rules.get("error"):
                return rules
            return run_lab_script(
                experiment,
                decks=_visible_decks(),
                rules=rules,
                games=args.get("games"),
                seed=args.get("seed"),
            )
        except ValueError as exc:
            return {"error": str(exc)}
    if name == "list_strategies":
        return list_strategies()
    if name == "draw_odds":
        deck = _usable_deck(args["deck_id"])
        if not deck:
            return {"error": "deck not found"}
        names = [c["name"] for c in deck["cards"]]
        return draw_probability(args["card_name"], names, int(args.get("draw") or 7))
    if name == "simulate_match":
        deck_a = _usable_deck(args["deck_a_id"])
        deck_b = _usable_deck(args["deck_b_id"])
        if not deck_a or not deck_b:
            return {"error": "need two saved decks"}
        rules = _match_rules(rule_preset=args.get("rule_preset"), decks=[deck_a, deck_b])
        if isinstance(rules, dict) and rules.get("error"):
            return rules
        games = int(args.get("games") or 2000)
        sim_kw: dict = {
            "games": games,
            "question": args.get("question"),
            "deck_a_meta": {"id": deck_a["id"], "name": deck_a["name"]},
            "deck_b_meta": {"id": deck_b["id"], "name": deck_b["name"]},
        }
        if "queries" in args:
            sim_kw["queries"] = args.get("queries") or []
        overlay = args.get("card_overlay")
        overlay_a = args.get("card_overlay_a")
        overlay_b = args.get("card_overlay_b")
        for field, blob in (("card_overlay", overlay), ("card_overlay_a", overlay_a), ("card_overlay_b", overlay_b)):
            if blob is not None and not isinstance(blob, dict):
                return {"error": f"{field} must be an object keyed by catalog_id"}
        try:
            record = run_simulation(
                _cards(deck_a),
                _cards(deck_b),
                rules,
                StrategySpec.from_dict(args.get("strategy_a") or "thrifty"),
                StrategySpec.from_dict(args.get("strategy_b") or "shock"),
                card_overlay=overlay,
                card_overlay_a=overlay_a,
                card_overlay_b=overlay_b,
                **sim_kw,
            )
        except OverlayError as exc:
            return {"error": str(exc)}
        save_simulation(record)
        return {
            "simulation_id": record["id"],
            "method": record["method"],
            "strategies": record["strategies"],
            "results": record["results"],
            "learning": record["learning"],
        }
    if name == "suggest_trades":
        deck_a = _usable_deck(args["deck_a_id"])
        deck_b = _usable_deck(args["deck_b_id"])
        if not deck_a or not deck_b:
            return {"error": "need two saved decks"}
        rules = _match_rules(rule_preset=args.get("rule_preset"), decks=[deck_a, deck_b])
        if isinstance(rules, dict) and rules.get("error"):
            return rules
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
    if name == "replace_deck_card":
        return _replace_deck_card(args)
    return {"error": f"unknown tool {name}"}
