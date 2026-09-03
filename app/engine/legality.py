from __future__ import annotations

from collections import Counter
from typing import Any

from app.engine.effects import is_special_energy
from app.engine.models import Card, FamilyRules, default_family_rules


def copy_limit_for(card: Card, rules: FamilyRules | None = None) -> int | None:
    """Copy cap from the selected rules: Family Cup 4 of a name, Standard 30 is 2 of a name.

    Basic Energy is unlimited. Special Energy (Double Colorless, Boomerang) is not unlimited.
    Pokémon of the same printed name share the cap even across printings
    (Rebel Clash / TWM / CLC Clefable are all \"Clefable\").
    Clefable, Clefable ex, and Mega Clefable ex are different names.
    """
    rules = rules or default_family_rules()
    if card.is_energy and not is_special_energy(card):
        return None
    return rules.max_copies_except_basic_energy


def copy_violations(cards: list[Card], rules: FamilyRules | None = None) -> list[dict[str, Any]]:
    rules = rules or default_family_rules()
    counts = Counter(card.name for card in cards)
    seen: dict[str, Card] = {}
    for card in cards:
        seen.setdefault(card.name, card)
    out: list[dict[str, Any]] = []
    for name, n in counts.items():
        cap = copy_limit_for(seen[name], rules)
        if cap is not None and n > cap:
            out.append({"name": name, "count": n, "max": cap})
    return out
