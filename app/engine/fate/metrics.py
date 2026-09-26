"""Print-derived numbers on a deck knowledge graph.

Damage per energy, warm-up, evolution dependence, energy supply, reach, and
isolation. All of it is arithmetic on the printed graph and the copy counts.
Nothing here is a win rate, and nothing here is read by the match kernel.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.fate.ceilings import compute_ceilings
from app.engine.fate.kg import KG, KGNode, linked_degree, prize_weight
from app.engine.models import Card, FamilyRules
from app.engine.probability import hypergeometric_at_least_one

# One manual attach per turn. Acceleration adds to this, then the rate is capped
# at the lead attack's energy cost so warm-up never drops below one turn.
_MANUAL_ATTACH_RATE = 1

_ATTACH_FROM_HAND = {"attach_basic_energy_from_hand", "attach_special_energy_from_hand"}


def compute_metrics(
    deck_kg: KG,
    rules: FamilyRules,
    cards: list[Card] | None = None,
) -> dict[str, Any]:
    """Metrics for the induced deck graph.

    ``cards`` is the list the graph was induced from. Reach then uses the same
    hypergeometric helper as copy ceilings, including printed "Draw N cards"
    operators. Search edges are listed beside that probability; they are not
    folded into it.
    """
    printings = _unique_printings(deck_kg)
    by_id = {n.id: n for n in deck_kg.nodes}
    ceilings = compute_ceilings(cards, rules) if cards else None
    seen = int(ceilings["effective_seen"]) if ceilings else int(rules.opening_hand)
    population = len(cards) if cards else sum(int(n.attributes.get("copies") or 0) for n in printings)
    p_by_name = {row["name"]: row for row in (ceilings or {}).get("names") or []}
    card_by_name = {}
    if cards:
        for card in cards:
            card_by_name.setdefault(card.name, card)

    supply, special_colorless = _energy_supply(printings)
    nodes: list[dict[str, Any]] = []
    for node in printings:
        card = card_by_name.get(node.name)
        nodes.append(
            _node_metrics(
                node,
                deck_kg,
                by_id,
                rules,
                card,
                supply,
                p_by_name,
                population,
                seen,
            )
        )
    nodes.sort(key=lambda row: row["name"])
    return {
        "effective_seen": seen,
        "nodes": nodes,
        "lines": _lines(deck_kg, printings),
        "energy_budget": {
            "supply": supply,
            "special_colorless": special_colorless,
            "note": (
                "Supply is grouped by the type the card provides. "
                "A special Colorless card is listed on its own and does not pay a typed cost."
            ),
        },
        "attach_rate": {
            "manual": _MANUAL_ATTACH_RATE,
            "cap": (
                "Rate = min(lead energy cost, 1 + acceleration). "
                "Acceleration is one per attaches_from_deck edge on this printing whose energy "
                "type is in the lead cost, plus one per attach-from-hand ability. "
                "The cap keeps warm-up at least 1 turn when the attack costs energy."
            ),
        },
        "method": (
            "Lead attack is the highest printed damage; a 0-damage setup attack is not averaged in. "
            "dpe_min / dpe_max use a bounded printed bonus (Shooting Moons). "
            "An open 'for each' bonus leaves dpe_max empty. "
            "Reach is P(at least one) at effective seen cards. "
            "Search edges are named beside that probability and are not added into it. "
            "Isolation ignores generic Colorless pay and draw edges."
        ),
        "estimate": True,
    }


def _unique_printings(deck_kg: KG) -> list[KGNode]:
    """One node per name. induce() already stored the summed copy count on each."""
    chosen: dict[str, KGNode] = {}
    for node in deck_kg.nodes:
        if node.kind == "printing":
            chosen.setdefault(node.name, node)
    return list(chosen.values())


def _energy_supply(printings: list[KGNode]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    supply: Counter[str] = Counter()
    special: list[dict[str, Any]] = []
    for node in printings:
        if (node.attributes.get("category") or "").lower() != "energy":
            continue
        copies = int(node.attributes.get("copies") or 0)
        energy_type = str(node.attributes.get("energy_type") or "Colorless")
        if energy_type.lower() == "colorless":
            special.append(
                {
                    "name": node.name,
                    "copies": copies,
                    "pays": "Colorless",
                    "pays_typed_cost": False,
                }
            )
            continue
        supply[energy_type] += copies
    special.sort(key=lambda row: row["name"])
    return dict(sorted(supply.items())), special


def _node_metrics(
    node: KGNode,
    deck_kg: KG,
    by_id: dict[str, KGNode],
    rules: FamilyRules,
    card: Card | None,
    supply: dict[str, int],
    p_by_name: dict[str, dict[str, Any]],
    population: int,
    seen: int,
) -> dict[str, Any]:
    attrs = node.attributes
    copies = int(attrs.get("copies") or 0)
    attacks = list(attrs.get("attacks") or [])
    lead = _lead_attack(attacks)
    row: dict[str, Any] = {
        "id": node.id,
        "name": node.name,
        "category": attrs.get("category"),
        "copies": copies,
        "prize_weight": prize_weight(card, rules) if card else attrs.get("prize_weight"),
        "isolated": linked_degree(deck_kg, node.id) == 0,
        "reach": _reach(node.name, copies, p_by_name, population, seen),
        "searchers": _searchers(node, deck_kg, by_id),
    }
    if lead is None or (attrs.get("category") or "").lower() != "pokemon":
        return row
    cost = [str(part) for part in lead.get("cost") or []]
    energy_lead = len(cost)
    damage_min, damage_max, condition = _damage_span(lead)
    accel = _acceleration(node, deck_kg, cost)
    attach_rate = _attach_rate(energy_lead, accel)
    warm = (energy_lead / attach_rate) if attach_rate else 0
    body = _body_ready(str(attrs.get("stage") or ""))
    typed = Counter(part for part in cost if part.lower() != "colorless")
    row.update(
        {
            "lead_attack": lead.get("name"),
            "lead_cost": cost,
            "lead_damage": int(lead.get("damage") or 0),
            "condition": condition,
            "energy_lead": energy_lead,
            "damage_min": damage_min,
            "damage_max": damage_max,
            "dpe_lead": _per_energy(int(lead.get("damage") or 0), energy_lead),
            "dpe_min": _per_energy(damage_min, energy_lead),
            "dpe_max": _per_energy(damage_max, energy_lead) if damage_max is not None else None,
            "attach_rate": attach_rate,
            "acceleration": accel,
            "warm_up_turns": _num(warm),
            "body_ready": body,
            "readiness": _num(max(body, warm)),
            "typed_cost": dict(typed),
            "typed_payable_from_supply": all(supply.get(energy, 0) >= count for energy, count in typed.items()),
            "colorless_special_pays_typed_cost": False,
        }
    )
    return row


def _lead_attack(attacks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not attacks:
        return None
    return max(attacks, key=lambda attack: (int(attack.get("damage") or 0), -len(attack.get("cost") or [])))


def _damage_span(attack: dict[str, Any]) -> tuple[int, int | None, str | None]:
    printed = int(attack.get("damage") or 0)
    text = str(attack.get("text") or "")
    low = high = printed
    unbounded = False
    for effect in parse_effects(text, str(printed)):
        kind = effect.get("kind")
        if kind == "discard_hand_energy_bonus":
            high = printed + int(effect["per"]) * int(effect["max"])
        elif kind in {"coin_damage_bonus", "opponent_prize_bonus", "attached_named_energy_bonus"}:
            high = max(high, printed + int(effect.get("bonus") or 0))
        elif kind == "energy_in_play_bonus":
            high = max(high, printed + int(effect.get("bonus") or 0))
        elif kind in {
            "psychic_energy_bonus",
            "psychic_energy_times",
            "benched_pokemon_bonus",
            "hand_count_times",
            "damage_counter_bonus",
            "damage_counter_on_self_bonus",
        }:
            unbounded = True
    condition = text if "does nothing" in text.lower() else None
    if unbounded:
        return low, None, condition
    return low, high, condition


def _acceleration(node: KGNode, deck_kg: KG, cost: list[str]) -> int:
    wanted = {part.lower() for part in cost}
    accel = 0
    for edge in deck_kg.edges:
        if edge.src != node.id or edge.kind != "attaches_from_deck":
            continue
        energy = str(edge.effect.get("energy_type") or "").lower()
        if energy in wanted:
            accel += 1
    for ability in node.attributes.get("abilities") or []:
        for effect in parse_ability_effects(str(ability.get("text") or "")):
            if effect.get("kind") in _ATTACH_FROM_HAND and wanted:
                accel += 1
                break
    return accel


def _attach_rate(energy_lead: int, accel: int) -> int | float:
    if energy_lead <= 0:
        return _MANUAL_ATTACH_RATE
    return min(energy_lead, _MANUAL_ATTACH_RATE + accel)


def _body_ready(stage: str) -> int:
    key = stage.lower().replace(" ", "")
    if key in {"stage1"}:
        return 1
    if key in {"stage2"}:
        return 2
    return 0


def _per_energy(damage: int, energy: int) -> int | float | None:
    if energy <= 0:
        return None
    return _num(damage / energy)


def _num(value: float) -> int | float:
    if value == int(value):
        return int(value)
    return value


def _reach(
    name: str,
    copies: int,
    p_by_name: dict[str, dict[str, Any]],
    population: int,
    seen: int,
) -> float | None:
    row = p_by_name.get(name)
    if row is not None:
        return row["p_seen"]
    if population <= 0 or copies <= 0:
        return None
    return hypergeometric_at_least_one(copies, population, seen)


def _searchers(node: KGNode, deck_kg: KG, by_id: dict[str, KGNode]) -> list[str]:
    names: set[str] = set()
    for edge in deck_kg.edges:
        if edge.dst == node.id and edge.kind == "named_partner":
            source = by_id.get(edge.src)
            if source and source.name != node.name:
                names.add(source.name)
        if edge.kind == "searches_role" and _matches_role(node, edge.dst):
            source = by_id.get(edge.src)
            if source and source.name != node.name:
                names.add(source.name)
    return sorted(names)


def _matches_role(node: KGNode, role_id: str) -> bool:
    category = (node.attributes.get("category") or "").lower()
    stage = (node.attributes.get("stage") or "").lower()
    kind = (node.attributes.get("trainer_kind") or "").lower()
    name = node.name.lower()
    if role_id == "role:basic-pokemon":
        return category == "pokemon" and stage in {"basic", ""}
    if role_id == "role:item":
        return category == "trainer" and kind == "item"
    if role_id == "role:no-rule-box":
        return category == "pokemon" and not name.endswith(" ex")
    return False


def _lines(deck_kg: KG, printings: list[KGNode]) -> list[dict[str, Any]]:
    by_id = {n.id: n for n in printings}
    children: dict[str, list[str]] = {}
    for edge in deck_kg.edges:
        if edge.kind == "evolves_into" and edge.src in by_id and edge.dst in by_id:
            children.setdefault(edge.src, []).append(edge.dst)
    rare_candy = any(n.name.lower() == "rare candy" for n in printings)
    rows: list[dict[str, Any]] = []
    for node in printings:
        if (node.attributes.get("category") or "").lower() != "pokemon":
            continue
        if _body_ready(str(node.attributes.get("stage") or "")) != 0:
            continue
        if node.id not in children:
            continue
        for stage1_id in children[node.id]:
            stage1 = by_id[stage1_id]
            stage2_ids = children.get(stage1_id, [])
            bodies = int(node.attributes.get("copies") or 0)
            evolutions = int(stage1.attributes.get("copies") or 0)
            stage2 = sum(int(by_id[child].attributes.get("copies") or 0) for child in stage2_ids)
            rows.append(
                {
                    "basic": node.name,
                    "evolution": stage1.name,
                    "stage2": stage2,
                    "bodies": bodies,
                    "evolutions": evolutions,
                    "charges": min(evolutions, bodies),
                    "charges_stage2": min(stage2, evolutions) if stage2_ids else None,
                    "stranded": evolutions > bodies or stage2 > evolutions,
                    "rare_candy": rare_candy,
                }
            )
    rows.sort(key=lambda row: (row["basic"], row["evolution"]))
    return rows
