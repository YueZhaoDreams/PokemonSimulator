from __future__ import annotations

from typing import Any

from app.engine.models import Card, FamilyRules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec


def _role(card: Card) -> str:
    if card.is_energy:
        return "energy"
    if card.is_supporter:
        return "supporter"
    if card.is_item:
        name = card.name.lower()
        if "ball" in name or "search" in name or "candy" in name:
            return "search"
        return "item"
    if (card.stage or "").lower() in {"stage2", "stage 2"}:
        return "stage2"
    if (card.stage or "").lower() in {"stage1", "stage 1"}:
        return "stage1"
    if card.hp >= 140:
        return "wall"
    if any("paralyze" in (a.text or "").lower() for a in card.attacks):
        return "status"
    return "basic"


def _counts(cards: list[Card]) -> dict[str, int]:
    bag: dict[str, int] = {}
    for card in cards:
        bag[_role(card)] = bag.get(_role(card), 0) + 1
    bag["pokemon"] = sum(1 for c in cards if c.is_pokemon)
    bag["energy_cards"] = sum(1 for c in cards if c.is_energy)
    bag["search"] = bag.get("search", 0)
    return bag


def _needs(cards: list[Card]) -> list[str]:
    c = _counts(cards)
    needs = []
    if c.get("energy_cards", 0) == 0:
        needs.append("energy")
    if c.get("search", 0) == 0:
        needs.append("search")
    if c.get("stage2", 0) and c.get("stage1", 0) == 0:
        needs.append("stage1")
    if c.get("supporter", 0) == 0:
        needs.append("supporter")
    if c.get("status", 0) == 0:
        needs.append("status")
    if c.get("wall", 0) == 0 and max((x.hp for x in cards if x.is_pokemon), default=0) < 120:
        needs.append("wall")
    names = {x.name.lower() for x in cards}
    if any(x.evolves_from and x.evolves_from.lower() not in names for x in cards if x.is_pokemon):
        needs.append("evolution_basic")
    return needs


def suggest_trades(
    cards_a: list[Card],
    cards_b: list[Card],
    rules: FamilyRules,
    strat_a: StrategySpec,
    strat_b: StrategySpec,
    games: int = 400,
    seed: int = 7,
    baseline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    baseline = baseline or run_simulation(cards_a, cards_b, rules, strat_a, strat_b, games=games, seed=seed)
    base_a = baseline["results"]["win_rate_a"]
    needs_a = _needs(cards_a)
    needs_b = _needs(cards_b)
    candidates = []

    for i, ca in enumerate(cards_a):
        for j, cb in enumerate(cards_b):
            if ca.name.lower() == cb.name.lower():
                continue
            role_a, role_b = _role(ca), _role(cb)
            # Skip swapping two of the same role unless it fills a need.
            helpful_a = role_b in needs_a or (role_b == "energy" and needs_a)
            helpful_b = role_a in needs_b or (role_a == "energy" and needs_b)
            if not (helpful_a or helpful_b):
                continue
            if role_a == role_b and not (helpful_a and helpful_b):
                continue
            candidates.append((i, j, ca, cb, helpful_a, helpful_b))

    # Rank by heuristic, simulate top few.
    def heuristic(item) -> float:
        _, _, ca, cb, ha, hb = item
        score = 0.0
        if ha:
            score += 2
        if hb:
            score += 2
        if _role(cb) in needs_a and _role(ca) in needs_b:
            score += 3
        # Prefer trading a duplicate.
        if sum(1 for c in cards_a if c.name == ca.name) > 1:
            score += 1
        if sum(1 for c in cards_b if c.name == cb.name) > 1:
            score += 1
        return score

    candidates.sort(key=heuristic, reverse=True)
    evaluated = []
    seen = set()
    for i, j, ca, cb, ha, hb in candidates[:18]:
        key = (ca.name, cb.name)
        if key in seen:
            continue
        seen.add(key)
        new_a = list(cards_a)
        new_b = list(cards_b)
        new_a[i], new_b[j] = cb, ca
        sim = run_simulation(new_a, new_b, rules, strat_a, strat_b, games=max(80, games // 2), seed=seed + i + j)
        wr = sim["results"]["win_rate_a"]
        consist_a = 1 - sim["learning"]["status"].get("pokemon_as_energy_per_game", 0) * 0  # placeholder
        # Strength: closer matchup + both decks get a missing role.
        fairness = 1 - abs(wr - 0.5) * 2
        both_helped = ha and hb
        evaluated.append(
            {
                "give_a": ca.name,
                "give_b": cb.name,
                "why_a": f"A receives {cb.name} ({_role(cb)})" + (" — fills a gap" if ha else ""),
                "why_b": f"B receives {ca.name} ({_role(ca)})" + (" — fills a gap" if hb else ""),
                "win_rate_a_after": wr,
                "win_rate_b_after": sim["results"]["win_rate_b"],
                "fairness": fairness,
                "both_helped": both_helped,
                "delta_from_baseline_a": wr - base_a,
                "insights": sim["learning"]["insights"][:2],
                "score": fairness + (1.5 if both_helped else 0) + (0.3 if ha else 0) + (0.3 if hb else 0),
            }
        )

    evaluated.sort(key=lambda r: r["score"], reverse=True)
    top = evaluated[:5]
    return {
        "baseline_win_rate_a": base_a,
        "needs_a": needs_a,
        "needs_b": needs_b,
        "recommendations": top,
        "method": (
            f"Enumerated one-for-one trades that fill missing roles (energy, search, status, walls), "
            f"then re-simulated the matchup for the best candidates ({max(80, games // 2)} games each). "
            "Win-win means both decks fill a hole and the matchup stays close to 50/50."
        ),
    }
