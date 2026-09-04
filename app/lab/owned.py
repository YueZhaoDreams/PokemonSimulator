"""Per-owner StrategySpec overlays saved from Lab locks."""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

from app.db import (
    get_deck,
    get_user_strategy,
    list_user_strategies,
    save_deck,
    save_lab_experiment,
    save_user_strategy,
)
from app.engine.strategies import StrategySpec, list_strategies
from app.lab.patches import apply_deck_patch
from app.lab.report import cells_from_attempts

USER_STRATEGY_PREFIX = "user:"


def user_strategy_option_id(strategy_id: str) -> str:
    raw = str(strategy_id or "")
    if raw.startswith(USER_STRATEGY_PREFIX):
        return raw
    return f"{USER_STRATEGY_PREFIX}{raw}"


def lock_strategy_id(owner_id: str, experiment_id: str, cell_id: str) -> str:
    digest = hashlib.sha256(f"{owner_id}:{experiment_id}:{cell_id}".encode()).hexdigest()
    return str(uuid.UUID(digest[:32]))


def listed_strategies_for(viewer: dict | None) -> list[dict[str, Any]]:
    out = []
    for spec in list_strategies():
        item = dict(spec)
        item["id"] = spec["name"]
        item["source"] = "library"
        out.append(item)
    owner_id = (viewer or {}).get("id")
    if not owner_id:
        return out
    for row in list_user_strategies(owner_id):
        spec = row["spec"] if isinstance(row.get("spec"), dict) else {}
        out.append(
            {
                "id": user_strategy_option_id(row["id"]),
                "name": row["name"],
                "description": spec.get("description") or "Saved from Lab",
                "source": "user",
                "spec": spec,
            }
        )
    return out


def _can_use_strategy(viewer: dict | None, row: dict | None) -> bool:
    if not row:
        return False
    if not viewer:
        return False
    if viewer.get("role") == "admin":
        return True
    return row.get("owner_id") == viewer.get("id")


def resolve_strategy_spec(value: object, viewer: dict | None = None) -> StrategySpec:
    if isinstance(value, dict):
        return StrategySpec.from_dict(value)
    raw = str(value or "").strip()
    if not raw:
        return StrategySpec.from_dict("balanced")
    if raw.startswith(USER_STRATEGY_PREFIX):
        row = get_user_strategy(raw)
        if not _can_use_strategy(viewer, row):
            raise ValueError("strategy not found")
        return StrategySpec.from_dict(row["spec"])
    return StrategySpec.from_dict(raw)


def _cell_for_lock(experiment: dict, cell_id: str) -> dict:
    cells = experiment.get("cells") or []
    if not cells:
        cells = cells_from_attempts(experiment.get("attempts") or [])
    for cell in cells:
        if isinstance(cell, dict) and str(cell.get("id")) == str(cell_id):
            return cell
    raise ValueError("that run is not on this question")


def lock_lab_cell(
    experiment: dict,
    *,
    viewer: dict,
    cell_id: str,
    reason: str | None = None,
    side: str = "b",
    apply_deck_id: str | None = None,
) -> dict:
    if not viewer or not viewer.get("id"):
        raise ValueError("sign in required")
    if experiment.get("owner_id") != viewer.get("id") and viewer.get("role") != "admin":
        raise ValueError("experiment not found")
    cell = _cell_for_lock(experiment, cell_id)
    side_key = "a" if str(side).lower() == "a" else "b"
    if side_key == "a":
        spec_src = cell.get("strategy_a") or "thrifty"
    else:
        spec_src = cell.get("strategy_b") or "shock"
    spec = resolve_strategy_spec(spec_src, viewer).to_dict()
    title = str(cell.get("title") or cell_id)
    saved = save_user_strategy(
        owner_id=viewer["id"],
        name=title,
        spec=spec,
        strategy_id=lock_strategy_id(viewer["id"], experiment["id"], cell_id),
    )
    deck_out = None
    if apply_deck_id:
        deck = get_deck(apply_deck_id)
        if not deck or (viewer.get("role") != "admin" and deck.get("owner_id") != viewer.get("id")):
            raise ValueError("deck not found")
        patch = cell.get("patch_a") if side_key == "a" else cell.get("patch_b")
        cards = apply_deck_patch(deck["cards"], patch)
        deck_out = save_deck(
            deck["name"],
            cards,
            source=deck.get("source"),
            deck_id=deck["id"],
            owner_id=deck.get("owner_id") or viewer["id"],
        )
    locked = save_lab_experiment(
        owner_id=experiment["owner_id"],
        question=experiment.get("question"),
        cells=experiment.get("cells"),
        queries=experiment.get("queries"),
        games=experiment.get("games"),
        seed=experiment.get("seed"),
        results=experiment.get("results"),
        locked_cell_id=str(cell_id),
        lock_reason=reason or f"locked {title}",
        script_text=experiment.get("script_text"),
        conclusion=experiment.get("conclusion"),
        exp_id=experiment["id"],
    )
    return {
        "experiment": locked,
        "strategy": {
            "id": user_strategy_option_id(saved["id"]),
            "name": saved["name"],
            "spec": saved["spec"],
            "source": "user",
        },
        "deck": deck_out,
    }
