"""Customer card/strategy overlays. JSON only; never mutates Game or git."""

from __future__ import annotations

from typing import Any

from app.engine.models import Attack, Card

# Kinds parse_effects / parse_ability_effects may emit. Overlay cannot invent a new kind.
PUBLISHED_EFFECT_KINDS = frozenset(
    {
        "draw_until_hand",
        "attach_energy_from_deck_per_benched",
        "attach_energy_from_top",
        "look_top_put_hand",
        "draw_if_ko_last_turn",
        "attach_basic_energy_from_hand",
        "fairy_zone",
        "invisible_wall",
        "status",
        "recoil",
        "energy_attack_lock",
        "prevent_basic_damage",
        "discard_energy",
        "heal",
        "draw",
        "call_family",
        "search_item",
        "mill_opponent",
        "coin_whiff",
        "transfer_charge",
        "ignore_wr",
        "ignore_active_effects",
        "copy_active_attack",
        "move_psychic_energy",
        "lock_items",
        "damage_one_pokemon",
        "discard_hand_energy_bonus",
        "benched_pokemon_bonus",
        "damage_counter_bonus",
        "psychic_energy_bonus",
        "psychic_energy_times",
        "times",
        "swallow_energy",
        "deck_count_bonus",
        "bench_damage_counters",
    }
)

_PRINTING_KEYS = {"params", "effects", "attack", "decisions", "program"}


class OverlayError(ValueError):
    """Reject an overlay that would invent a hook or rewrite print."""


def overlay_for_side(shared: dict[str, Any] | None, side: dict[str, Any] | None) -> dict[str, Any] | None:
    """Per-side overlay wins whenever it is provided, including {}."""
    return shared if side is None else side


def apply_card_overlay(cards: list[Card], overlay: dict[str, Any] | None) -> list[Card]:
    """Return copies with catalog_id-keyed JSON programs applied.

    Does not mutate the input list or Game. Unknown kinds and look-above-print fail closed.
    """
    if not overlay:
        return list(cards)
    if not isinstance(overlay, dict):
        raise OverlayError("card_overlay must be an object keyed by catalog_id")
    out = [Card.from_dict(card.to_dict()) for card in cards]
    for catalog_id, patch in overlay.items():
        cid = str(catalog_id or "").strip()
        if not cid:
            raise OverlayError("card_overlay keys must be catalog ids")
        if not isinstance(patch, dict):
            raise OverlayError(f"overlay for {cid} must be an object")
        unknown = set(patch) - _PRINTING_KEYS
        if unknown:
            raise OverlayError(f"overlay for {cid} has unknown keys: {sorted(unknown)}")
        matched = [card for card in out if (card.catalog_id or "") == cid]
        if not matched:
            continue
        for card in matched:
            _apply_printing_patch(card, cid, patch)
    return out


def _apply_printing_patch(card: Card, cid: str, patch: dict[str, Any]) -> None:
    params = patch.get("params") or {}
    if params and not isinstance(params, dict):
        raise OverlayError(f"overlay params for {cid} must be an object")
    decisions = patch.get("decisions")
    if decisions is not None and not isinstance(decisions, dict):
        raise OverlayError(f"overlay decisions for {cid} must be an object")
    if decisions:
        raise OverlayError(
            f"overlay decisions for {cid} are not applied; put when-clauses on the strategy overlay"
        )
    effects = patch.get("effects")
    if effects is None and patch.get("program") is not None:
        effects = patch.get("program")
    attack_name = str(patch.get("attack") or "").strip().lower()
    printed_look = _printed_swallow_look(card)
    if effects is not None:
        if not isinstance(effects, list) or not effects:
            raise OverlayError(f"overlay effects for {cid} must be a non-empty list")
        checked = [_validate_effect(cid, item) for item in effects]
        overlay_look = next((int(e["look"]) for e in checked if e.get("kind") == "swallow_energy"), None)
        if overlay_look is not None and printed_look is not None and overlay_look > printed_look:
            raise OverlayError(f"overlay look {overlay_look} is above printed look {printed_look} on {cid}")
        target = _target_attack(card, attack_name, checked)
        target.effects = checked
    if "look" in params:
        look = _as_positive_int(params.get("look"), f"{cid} params.look")
        if printed_look is not None and look > printed_look:
            raise OverlayError(f"overlay look {look} is above printed look {printed_look} on {cid}")
        _set_swallow_look(card, look, attack_name)


def _printed_swallow_look(card: Card) -> int | None:
    looks = [int(e["look"]) for a in card.attacks for e in a.effects if e.get("kind") == "swallow_energy" and e.get("look") is not None]
    return max(looks) if looks else None


def _set_swallow_look(card: Card, look: int, attack_name: str) -> None:
    for attack in card.attacks:
        if attack_name and (attack.name or "").lower() != attack_name:
            continue
        for effect in attack.effects:
            if effect.get("kind") == "swallow_energy":
                effect["look"] = look
                return
    raise OverlayError("params.look needs a swallow_energy effect on that printing")


def _target_attack(card: Card, attack_name: str, effects: list[dict[str, Any]]) -> Attack:
    if attack_name:
        for attack in card.attacks:
            if (attack.name or "").lower() == attack_name:
                return attack
        raise OverlayError(f"no attack named {attack_name} on {card.catalog_id}")
    if any(e.get("kind") == "swallow_energy" for e in effects):
        for attack in card.attacks:
            if any(e.get("kind") == "swallow_energy" for e in attack.effects) or "swallow" in (attack.name or "").lower():
                return attack
    if not card.attacks:
        raise OverlayError(f"{card.catalog_id} has no attacks to overlay")
    return card.attacks[0]


def _validate_effect(cid: str, item: Any) -> dict[str, Any]:
    if not isinstance(item, dict) or not item.get("kind"):
        raise OverlayError(f"overlay effect on {cid} must be an object with kind")
    kind = str(item["kind"])
    if kind not in PUBLISHED_EFFECT_KINDS:
        raise OverlayError(f"overlay on {cid} uses unpublished kind {kind}")
    out = dict(item)
    if kind == "swallow_energy":
        out["look"] = _as_positive_int(out.get("look"), f"{cid} swallow_energy.look")
    return out


def _as_positive_int(value: Any, field: str) -> int:
    try:
        n = int(value)
    except (TypeError, ValueError) as exc:
        raise OverlayError(f"{field} must be an integer") from exc
    if n < 1:
        raise OverlayError(f"{field} must be >= 1")
    return n
