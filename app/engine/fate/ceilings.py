"""Whole-list copy ceilings.

A name capped at k copies has a hypergeometric ceiling on showing up in the cards a
player actually sees. Printed draw operators ("Draw 3 cards.") raise the number of
cards seen; they do not add a flat 3/60 to every name. Deck size, opening hand, and
the copy cap all come from the active rules, never from literals here.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.engine.effects import _normalize_card_text, parse_draw_until_hand, parse_effects
from app.engine.legality import copy_limit_for
from app.engine.models import Card, FamilyRules
from app.engine.probability import hypergeometric_at_least_one

_FIXED_DRAW = re.compile(r"\bdraw (a|\d+) cards?\b")
_CONDITIONAL_MARKERS = ("for each", "until", "instead", "if ", "that many")


def printed_draw_operators(cards: list[Card]) -> list[dict[str, Any]]:
    """Trainer cards whose printed text is a draw operator.

    Only an unconditional "Draw N cards" is counted toward effective seen cards. A
    draw-until-hand-size or a per-prize draw is listed with ``counted: false`` so the
    reader sees it, but no amount is invented for it.
    """
    by_name: dict[str, dict[str, Any]] = {}
    for card in cards:
        if not card.is_trainer:
            continue
        text = card.text or ""
        if not text:
            continue
        entry = by_name.get(card.name)
        if entry is not None:
            entry["copies"] += 1
            continue
        operator = _draw_operator(card.name, text)
        if operator is not None:
            by_name[card.name] = operator
    return sorted(by_name.values(), key=lambda op: (not op["counted"], op["name"]))


def _draw_operator(name: str, text: str) -> dict[str, Any] | None:
    normalized = _normalize_card_text(text)
    until = parse_draw_until_hand(text)
    if until:
        return {
            "name": name,
            "copies": 1,
            "kind": until["kind"],
            "amount": None,
            "counted": False,
            "note": f"draws until {until['count']} in hand; depends on hand size",
            "source": text,
        }
    draw = next((e for e in parse_effects(text) if e.get("kind") == "draw"), None)
    if draw is None:
        return None
    fixed = _FIXED_DRAW.search(normalized)
    conditional = any(marker in normalized for marker in _CONDITIONAL_MARKERS)
    if fixed and not conditional:
        amount = 1 if fixed.group(1) == "a" else int(fixed.group(1))
        return {
            "name": name,
            "copies": 1,
            "kind": "draw",
            "amount": amount,
            "counted": True,
            "note": f"+{amount} seen cards per copy",
            "source": text,
        }
    return {
        "name": name,
        "copies": 1,
        "kind": "draw",
        "amount": None,
        "counted": False,
        "note": "draw amount depends on game state; not added to seen cards",
        "source": text,
    }


def effective_seen_cards(cards: list[Card], rules: FamilyRules) -> tuple[int, list[dict[str, Any]]]:
    operators = printed_draw_operators(cards)
    extra = sum(int(op["amount"]) * int(op["copies"]) for op in operators if op["counted"])
    return int(rules.opening_hand) + extra, operators


def compute_ceilings(
    cards: list[Card],
    rules: FamilyRules,
    *,
    preset: str | None = None,
) -> dict[str, Any]:
    """Per-name copies, legal cap, and P(at least one) at opening hand and at seen cards."""
    population = len(cards)
    opening = int(rules.opening_hand)
    seen, operators = effective_seen_cards(cards, rules)
    counts = Counter(card.name for card in cards)
    first_print: dict[str, Card] = {}
    for card in cards:
        first_print.setdefault(card.name, card)

    names: list[dict[str, Any]] = []
    for name, copies in counts.items():
        card = first_print[name]
        cap = copy_limit_for(card, rules)
        p_opening = hypergeometric_at_least_one(copies, population, opening)
        p_seen = hypergeometric_at_least_one(copies, population, seen)
        names.append(
            {
                "name": name,
                "category": card.category,
                "copies": copies,
                "copy_cap": cap,
                "at_cap": cap is not None and copies >= cap,
                "over_cap": cap is not None and copies > cap,
                "p_opening": p_opening,
                "p_seen": p_seen,
                "p_gain": p_seen - p_opening,
            }
        )
    names.sort(key=lambda row: (-row["copies"], row["name"]))

    return {
        "rules": {
            "preset": preset,
            "name": rules.name,
            "deck_size": int(rules.deck_size),
            "opening_hand": opening,
            "copy_cap": int(rules.max_copies_except_basic_energy),
        },
        "deck_size": population,
        "size_matches_rules": population == int(rules.deck_size),
        "opening_hand": opening,
        "effective_seen": seen,
        "draw_operators": operators,
        "names": names,
        "method": (
            f"Hypergeometric P(at least one) = 1 - C({population}-k, n) / C({population}, n) for k copies, "
            f"n = {opening} (opening hand) and n = {seen} (opening hand plus printed draw operators present "
            f"in the list). Pre-mulligan. Copy cap {int(rules.max_copies_except_basic_energy)} from "
            f"{rules.name}; basic Energy uncapped."
        ),
        "estimate": True,
    }
