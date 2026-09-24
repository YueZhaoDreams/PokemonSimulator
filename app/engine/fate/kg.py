"""Catalog knowledge graph. Edges come from parsed print and evolves_from only."""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from app.engine.effects import (
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)
from app.engine.models import Card, FamilyRules

ROLE_BASIC = "role:basic-pokemon"
ROLE_OPPONENT_BENCH = "role:opponent-bench"
ROLE_DECK = "role:deck"


@dataclass
class KGNode:
    id: str
    kind: str
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KGEdge:
    src: str
    dst: str
    kind: str
    source: str
    effect: dict[str, Any] = field(default_factory=dict)
    generic: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KG:
    nodes: list[KGNode]
    edges: list[KGEdge]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }


def prize_weight(card: Card, rules: FamilyRules | None) -> int:
    name = card.name.lower()
    if not rules or not rules.extra_prize_for_ex or not name.endswith(" ex"):
        return 1
    if name.startswith("mega "):
        return 3
    return 2


def _effects(card: Card) -> list[tuple[str, dict[str, Any]]]:
    out: list[tuple[str, dict[str, Any]]] = []
    text = card.text or ""
    if card.category == "Trainer" and text:
        out += [(text, e) for e in parse_trainer_effects(text)]
    if card.category == "Energy" and text:
        out += [(text, e) for e in parse_energy_effects(text)]
    for ability in card.abilities:
        sentence = ability.text or ""
        out += [(sentence, e) for e in parse_ability_effects(sentence)]
    for attack in card.attacks:
        sentence = attack.text or ""
        if sentence:
            out += [(sentence, e) for e in parse_effects(sentence)]
    return out


def _role(role_id: str, name: str) -> KGNode:
    return KGNode(id=role_id, kind="role", name=name)


def _node(card: Card, rules: FamilyRules | None) -> KGNode:
    return KGNode(
        id=card.catalog_id or card.name,
        kind="printing",
        name=card.name,
        attributes={
            "catalog_id": card.catalog_id,
            "category": card.category,
            "stage": card.stage,
            "types": list(card.types),
            "hp": card.hp,
            "trainer_kind": card.trainer_kind,
            "energy_type": card.energy_type,
            "evolves_from": card.evolves_from,
            "retreat": card.retreat,
            "prize_weight": prize_weight(card, rules),
            "attacks": [
                {"name": a.name, "cost": list(a.cost), "damage": a.damage, "text": a.text or ""}
                for a in card.attacks
            ],
            "abilities": [{"name": a.name, "text": a.text} for a in card.abilities],
        },
    )


def _energy_role(energy_type: str) -> str:
    return f"role:energy:{energy_type.lower()}"


def build_catalog_kg(cards: list[Card], rules: FamilyRules | None = None) -> KG:
    """One node per distinct printing. Edges only from evolves_from and parsed effects."""
    by_id: dict[str, Card] = {}
    for card in cards:
        by_id.setdefault(card.catalog_id or card.name, card)
    unique = list(by_id.values())
    by_name: dict[str, list[Card]] = {}
    for card in unique:
        by_name.setdefault(card.name.lower(), []).append(card)

    nodes: dict[str, KGNode] = {c.catalog_id or c.name: _node(c, rules) for c in unique}
    edges: list[KGEdge] = []

    def add_role(role_id: str, label: str) -> None:
        nodes.setdefault(role_id, _role(role_id, label))

    def add(src: str, dst: str, kind: str, source: str, effect: dict | None = None, generic: bool = False) -> None:
        edges.append(KGEdge(src=src, dst=dst, kind=kind, source=source, effect=effect or {}, generic=generic))

    for card in unique:
        src = card.catalog_id or card.name
        if card.evolves_from:
            for base in by_name.get(card.evolves_from.lower(), []):
                if base is card:
                    continue
                add(base.catalog_id or base.name, src, "evolves_into", f"Evolves from {card.evolves_from}")
        for attack in card.attacks:
            for cost in attack.cost:
                role = _energy_role(cost)
                add_role(role, f"{cost} Energy")
                generic = cost.lower() == "colorless"
                add(
                    role,
                    src,
                    "pays_energy",
                    f"{attack.name}: {' '.join(attack.cost)}",
                    {"attack": attack.name, "energy_type": cost},
                    generic=generic,
                )
        for sentence, effect in _effects(card):
            kind = effect.get("kind")
            if kind == "call_family":
                add_role(ROLE_BASIC, "Basic Pokémon")
                add(src, ROLE_BASIC, "searches_role", sentence, effect)
            elif kind == "search_item":
                add_role("role:item", "Item")
                add(src, "role:item", "searches_role", sentence, effect)
            elif kind == "search_pokemon_no_rule_box":
                add_role("role:no-rule-box", "Pokémon without a Rule Box")
                add(src, "role:no-rule-box", "searches_role", sentence, effect)
            elif kind in {"draw", "draw_until_hand"}:
                add_role(ROLE_DECK, "Deck")
                add(src, ROLE_DECK, "draws", sentence, effect)
            elif kind == "attach_energy_from_deck_per_benched":
                energy = str(effect.get("energy_type") or "Energy")
                role = _energy_role(energy)
                add_role(role, f"{energy} Energy")
                stored = {k: v for k, v in effect.items() if k != "kind"}
                add(src, role, "attaches_from_deck", sentence, stored)
            elif kind == "force_opponent_active":
                add_role(ROLE_OPPONENT_BENCH, "Opponent's Benched Pokémon")
                add(src, ROLE_OPPONENT_BENCH, "force_opponent_active", sentence, effect)
        sentences = [card.text or ""] + [a.text or "" for a in card.abilities] + [a.text or "" for a in card.attacks]
        for other in unique:
            if other is card or len(other.name) < 5:
                continue
            if other.name.lower() == (card.evolves_from or "").lower():
                continue
            pattern = re.compile(rf"\b{re.escape(other.name.lower())}\b")
            hit = next((s for s in sentences if s and pattern.search(s.lower())), "")
            if hit:
                add(src, other.catalog_id or other.name, "named_partner", hit)

    return KG(nodes=list(nodes.values()), edges=edges)


def induce(kg: KG, names_with_counts: list[tuple[str, int]] | Counter) -> KG:
    """Printing nodes in this list, plus the role nodes their edges still touch."""
    counts: Counter = Counter()
    for name, n in names_with_counts.items() if isinstance(names_with_counts, Counter) else names_with_counts:
        counts[name] += int(n)
    kept = [n for n in kg.nodes if n.kind == "printing" and counts[n.name] > 0]
    ids = {n.id for n in kept}
    touching = [e for e in kg.edges if e.src in ids or e.dst in ids]
    role_ids = {end for e in touching for end in (e.src, e.dst) if end not in ids}
    roles = [n for n in kg.nodes if n.id in role_ids]
    nodes = [
        KGNode(id=n.id, kind=n.kind, name=n.name, attributes={**n.attributes, "copies": counts[n.name]})
        for n in kept
    ] + [KGNode(id=n.id, kind=n.kind, name=n.name, attributes=dict(n.attributes)) for n in roles]
    inside = ids | role_ids
    edges = [e for e in touching if e.src in inside and e.dst in inside]
    return KG(nodes=nodes, edges=edges)


def explain_edge(edge: KGEdge | dict[str, Any]) -> str:
    if isinstance(edge, dict):
        return str(edge.get("source") or "")
    return edge.source


def linked_degree(kg: KG, node_id: str) -> int:
    """Non-generic edges. Colorless pay alone does not count as a link."""
    return sum(1 for e in kg.edges if not e.generic and node_id in (e.src, e.dst) and e.kind != "draws")
