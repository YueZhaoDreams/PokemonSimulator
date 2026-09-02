from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.db import save_lab_experiment
from app.engine.models import Card, FamilyRules, default_family_rules
from app.engine.overlay import OverlayError
from app.engine.montecarlo import query_key, run_simulation
from app.engine.strategies import StrategySpec
from app.lab.patches import apply_deck_patch

LAB_CELL_MAX = 12


def _as_int(value: object, *, default: int, field: str) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be an integer") from exc


def run_lab_experiment(
    experiment: dict,
    *,
    deck_for: Callable[[str], dict | None],
    rules: FamilyRules | None = None,
    games: int | None = None,
    seed: int | None = None,
) -> dict:
    cells = experiment.get("cells") or []
    if not isinstance(cells, list) or not cells:
        raise ValueError("experiment needs at least one cell")
    if len(cells) > LAB_CELL_MAX:
        raise ValueError(f"at most {LAB_CELL_MAX} cells")
    games_n = _as_int(games if games is not None else experiment.get("games"), default=200, field="games")
    seed_n = _as_int(seed if seed is not None else experiment.get("seed"), default=20260831, field="seed")
    queries = experiment.get("queries")
    if queries is None:
        queries = []
    if not isinstance(queries, list):
        raise ValueError("queries must be a list")
    rules = rules or default_family_rules()
    matrix: list[dict[str, Any]] = []
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            raise ValueError(f"cell {index} must be an object")
        cell_id = str(cell.get("id") or f"cell-{index + 1}")
        deck_a = _require_deck(deck_for, cell.get("deck_a_id"), cell_id, "deck_a_id")
        deck_b = _require_deck(deck_for, cell.get("deck_b_id"), cell_id, "deck_b_id")
        cards_a = apply_deck_patch(deck_a["cards"], cell.get("patch_a"))
        cards_b = apply_deck_patch(deck_b["cards"], cell.get("patch_b"))
        strat_a = StrategySpec.from_dict(cell.get("strategy_a") or "thrifty")
        strat_b = StrategySpec.from_dict(cell.get("strategy_b") or "shock")
        try:
            record = run_simulation(
                [Card.from_dict(c) for c in cards_a],
                [Card.from_dict(c) for c in cards_b],
                rules,
                strat_a,
                strat_b,
                games=games_n,
                seed=seed_n,
                question=experiment.get("question"),
                queries=queries,
                deck_a_meta={"id": deck_a["id"], "name": deck_a["name"]},
                deck_b_meta={"id": deck_b["id"], "name": deck_b["name"]},
                card_overlay=cell.get("card_overlay") if "card_overlay" in cell else None,
                card_overlay_a=cell["card_overlay_a"] if "card_overlay_a" in cell else None,
                card_overlay_b=cell["card_overlay_b"] if "card_overlay_b" in cell else None,
            )
        except OverlayError as exc:
            raise ValueError(str(exc)) from exc
        results = record["results"]
        keyed = results.get("queries") or {}
        query_rates = {}
        for query in queries:
            key = query_key(query)
            if key:
                query_rates[key] = keyed.get(key, 0.0)
        matrix.append(
            {
                "id": cell_id,
                "title": cell.get("title") or cell_id,
                "strategy_a": strat_a.to_dict(),
                "strategy_b": strat_b.to_dict(),
                "win_rate_a": results["win_rate_a"],
                "win_rate_b": results["win_rate_b"],
                "tie_rate": results["tie_rate"],
                "queries": query_rates,
            }
        )
    actual_games = record["method"]["games"]
    blob = {"seed": seed_n, "games": actual_games, "cells": matrix}
    return save_lab_experiment(
        owner_id=experiment["owner_id"],
        question=experiment.get("question"),
        cells=experiment.get("cells"),
        queries=queries,
        games=actual_games,
        seed=seed_n,
        results=blob,
        locked_cell_id=experiment.get("locked_cell_id"),
        lock_reason=experiment.get("lock_reason"),
        script_text=experiment.get("script_text"),
        exp_id=experiment["id"],
    )


def _require_deck(deck_for: Callable[[str], dict | None], deck_id: object, cell_id: str, field: str) -> dict:
    deck = deck_for(str(deck_id or ""))
    if not deck:
        raise ValueError(f"cell {cell_id} {field} is missing or not usable")
    return deck
