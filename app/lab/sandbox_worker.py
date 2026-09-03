"""Child process: restricted exec of an already-classified lab script."""

from __future__ import annotations

import builtins
import json
import sys
from io import StringIO
from typing import Any

from app.engine.models import Card, FamilyRules
from app.engine.montecarlo import query_key, run_simulation
from app.engine.strategies import StrategySpec
from app.lab.patches import apply_deck_patch
from app.lab.sandbox import LAB_SCRIPT_MAX_GAMES, classify_lab_script


def _safe_builtins() -> dict[str, Any]:
    allowed = (
        "abs",
        "bool",
        "dict",
        "enumerate",
        "float",
        "int",
        "isinstance",
        "len",
        "list",
        "max",
        "min",
        "print",
        "range",
        "reversed",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
    )
    return {name: getattr(builtins, name) for name in allowed}


def _capped_run_simulation(*args: Any, **kwargs: Any) -> dict:
    max_games = int(kwargs.pop("_max_games", LAB_SCRIPT_MAX_GAMES))
    games = int(kwargs.get("games") or 200)
    kwargs["games"] = max(1, min(games, max_games))
    cards_a = args[0] if args else kwargs.get("cards_a")
    cards_b = args[1] if len(args) > 1 else kwargs.get("cards_b")
    rules = args[2] if len(args) > 2 else kwargs.get("rules")
    strat_a = args[3] if len(args) > 3 else kwargs.get("strat_a")
    strat_b = args[4] if len(args) > 4 else kwargs.get("strat_b")
    rest = args[5:]
    kwargs.pop("cards_a", None)
    kwargs.pop("cards_b", None)
    kwargs.pop("rules", None)
    kwargs.pop("strat_a", None)
    kwargs.pop("strat_b", None)
    return run_simulation(
        _as_cards(cards_a),
        _as_cards(cards_b),
        rules,
        _as_strategy(strat_a),
        _as_strategy(strat_b),
        *rest,
        **kwargs,
    )


def _as_cards(value: Any) -> list[Card]:
    if not value:
        return []
    out: list[Card] = []
    for item in value:
        if isinstance(item, Card):
            out.append(item)
        elif isinstance(item, dict):
            out.append(Card.from_dict(item))
        else:
            raise ValueError("cards must be Card objects or card dicts")
    return out


def _as_strategy(value: Any) -> StrategySpec:
    if isinstance(value, StrategySpec):
        return value
    return StrategySpec.from_dict(value)


def main() -> int:
    payload = json.loads(sys.stdin.read())
    script = payload.get("script") or ""
    verdict = classify_lab_script(script)
    if not verdict.executable:
        json.dump({"ok": False, "error": verdict.reason}, sys.stdout)
        return 0
    reported: dict[str, Any] = {}

    def report(value: object) -> None:
        if not isinstance(value, dict):
            raise ValueError("report() needs a dict")
        reported.clear()
        reported.update(value)

    max_games = int(payload.get("max_games") or LAB_SCRIPT_MAX_GAMES)
    rules = FamilyRules.from_dict(payload.get("rules") or {})
    env: dict[str, Any] = {
        "__builtins__": _safe_builtins(),
        "run_simulation": lambda *a, **k: _capped_run_simulation(*a, **k, _max_games=max_games),
        "StrategySpec": StrategySpec,
        "Card": Card,
        "FamilyRules": FamilyRules,
        "apply_deck_patch": apply_deck_patch,
        "query_key": query_key,
        "decks": payload.get("decks") or {},
        "rules": rules,
        "games": int(payload.get("games") or 200),
        "seed": int(payload.get("seed") or 20260831),
        "queries": payload.get("queries") or [],
        "question": payload.get("question"),
        "cells": payload.get("cells") or [],
        "report": report,
    }
    captured = StringIO()
    old_stdout = sys.stdout
    sys.stdout = captured
    try:
        exec(compile(script, "<lab-script>", "exec"), env, env)  # noqa: S102 — AST-gated bakeoff only
    finally:
        sys.stdout = old_stdout
    # Prints are discarded on purpose: stdout is the JSON protocol to the parent.
    result = reported or env.get("RESULT")
    if not isinstance(result, dict):
        json.dump({"ok": False, "error": "script must call report({...}) or set RESULT"}, sys.stdout)
        return 0
    json.dump({"ok": True, "results": result}, sys.stdout)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 — surface any child failure as JSON
        json.dump({"ok": False, "error": str(exc)}, sys.stdout)
        raise SystemExit(0) from exc
