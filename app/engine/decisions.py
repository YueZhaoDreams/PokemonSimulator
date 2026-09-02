"""Named decision points. Kernel asks; Strategy answers among legal actions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.engine.strategies import StrategySpec

LOOK_THEN_ATTACH = "look_then_attach.how_many"


@dataclass
class DecisionContext:
    id: str
    source: str
    legal: list[Any]
    observe: dict[str, Any] = field(default_factory=dict)
    default: Any = None


def decide(strat: StrategySpec, ctx: DecisionContext) -> Any:
    """Pick a legal action. Illegal or empty answers become the kernel default."""
    if ctx.id == LOOK_THEN_ATTACH:
        chosen = _decide_look_then_attach(strat, ctx)
        legal_set = list(ctx.legal)
        picked = [item for item in chosen if item in legal_set]
        if picked or chosen == []:
            return picked
        return ctx.default if ctx.default is not None else list(ctx.legal)
    return ctx.default


def _decide_look_then_attach(strat: StrategySpec, ctx: DecisionContext) -> list[Any]:
    legal = list(ctx.legal)
    want = len(legal)
    obs = ctx.observe or {}
    conservative = strat.self_preserve >= 0.5 or strat.item_spend < 0.75
    if conservative:
        if obs.get("hand_attachable"):
            want = max(0, want - 1)
        deck_len = int(obs.get("deck_len") or 99)
        if obs.get("can_pay") and deck_len <= 12:
            want = min(want, 1)
        if deck_len <= 8:
            want = min(want, 0 if obs.get("can_pay") else 1)
    for clause in strat.when or []:
        if not isinstance(clause, dict):
            continue
        if not _when_matches(clause.get("if"), obs):
            continue
        if "max_attach" in clause:
            try:
                want = min(want, max(0, int(clause["max_attach"])))
            except (TypeError, ValueError):
                continue
        if "fewer" in clause:
            try:
                want = max(0, want - int(clause["fewer"]))
            except (TypeError, ValueError):
                continue
    return legal[:want]


def _when_matches(pred: Any, obs: dict[str, Any]) -> bool:
    if pred is None:
        return True
    if not isinstance(pred, dict):
        return False
    for key, value in pred.items():
        if key == "deck_len_lte":
            try:
                if int(obs.get("deck_len") or 0) > int(value):
                    return False
            except (TypeError, ValueError):
                return False
        elif key == "hand_attachable":
            if bool(obs.get("hand_attachable")) != bool(value):
                return False
        elif key == "can_pay":
            if bool(obs.get("can_pay")) != bool(value):
                return False
        else:
            return False
    return True
