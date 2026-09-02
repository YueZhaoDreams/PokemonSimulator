from random import Random

import pytest

from app.ai.cursor_agent import FAMILY_CUP_BRIEF, FOLLOWUP_TOOL_HINT, product_chat_agent_options
from app.ai.tools import run_tool
from app.config import COACH_SANDBOX_DIR, ROOT
from app.db import init_db
from app.engine.decisions import LOOK_THEN_ATTACH
from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.overlay import OverlayError, apply_card_overlay
from app.engine.strategies import StrategySpec
from app.seed_data import FALLBACK_BY_NAME, SET_A_NAMES, SET_B_NAMES, build_fallback_deck


def _swallow_look(card) -> int | None:
    looks = [
        int(effect["look"])
        for attack in card.attacks
        for effect in attack.effects
        if effect.get("kind") == "swallow_energy" and effect.get("look") is not None
    ]
    return max(looks) if looks else None


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name.lower() == name.lower())


def test_overlay_cannot_invent_a_hook():
    dondozo = FALLBACK_BY_NAME["dondozo"]
    with pytest.raises(OverlayError, match="unpublished kind"):
        apply_card_overlay(
            [dondozo],
            {"sv04-055": {"effects": [{"kind": "time_travel", "look": 5}]}},
        )


def test_overlay_cannot_raise_look_above_print():
    dondozo = FALLBACK_BY_NAME["dondozo"]
    assert _swallow_look(dondozo) == 5
    with pytest.raises(OverlayError, match="above printed look"):
        apply_card_overlay([dondozo], {"sv04-055": {"params": {"look": 7}}})
    with pytest.raises(OverlayError, match="above printed look"):
        apply_card_overlay(
            [dondozo],
            {"sv04-055": {"effects": [{"kind": "swallow_energy", "look": 7}]}},
        )


def test_overlay_look_below_print_does_not_mutate_fallback_or_english():
    original = FALLBACK_BY_NAME["dondozo"]
    text_before = original.attacks[0].text
    look_before = _swallow_look(original)
    patched = apply_card_overlay([original], {"sv04-055": {"params": {"look": 3}}})
    assert _swallow_look(patched[0]) == 3
    assert patched[0].attacks[0].text == text_before
    assert _swallow_look(original) == look_before == 5
    assert original.attacks[0].text == text_before
    assert original is not patched[0]


def test_overlay_program_alias_uses_published_kinds_only():
    original = FALLBACK_BY_NAME["dondozo"]
    patched = apply_card_overlay(
        [original],
        {"sv04-055": {"program": [{"kind": "swallow_energy", "look": 4}]}},
    )
    assert _swallow_look(patched[0]) == 4
    assert _swallow_look(original) == 5


def test_overlay_decisions_fail_closed_until_applied():
    dondozo = FALLBACK_BY_NAME["dondozo"]
    with pytest.raises(OverlayError, match="not applied"):
        apply_card_overlay(
            [dondozo],
            {"sv04-055": {"decisions": {"look_then_attach.how_many": {"max_attach": 1}}}},
        )


def test_empty_side_overlay_overrides_shared():
    from app.engine.overlay import overlay_for_side

    shared = {"sv04-055": {"params": {"look": 3}}}
    assert overlay_for_side(shared, None) == shared
    assert overlay_for_side(shared, {}) == {}


def test_simulate_match_strategy_schema_declares_string_or_object():
    from app.ai.tools import TOOL_SCHEMAS

    sim = next(item for item in TOOL_SCHEMAS if item["name"] == "simulate_match")
    assert sim["parameters"]["properties"]["strategy_a"]["type"] == ["string", "object"]
    assert sim["parameters"]["properties"]["strategy_b"]["type"] == ["string", "object"]


def test_balanced_swallow_attaches_the_looked_energy():
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    game = Game(a, b, default_family_rules(), StrategySpec.from_dict("balanced"), StrategySpec.from_dict("control"), Random(1), trace=True)
    me = game.players["a"]
    dondozo = _idx(me, "Dondozo")
    psychic = _idx(me, "Water Energy")
    seel = _idx(me, "Corphish")
    bronzor = _idx(me, "Bronzor")
    oddish = _idx(me, "Oddish")
    gloom = _idx(me, "Aipom")
    me.active = Pokemon(card_i=dondozo, played_turn=0)
    me.hand = []
    me.bench = []
    me.deck = [psychic, seel, bronzor, oddish, gloom]
    game._swallow_energy(me, 5)
    assert len(me.active.energy) == 5
    assert me.deck == []
    assert any("looked at 5" in line for line in game.trace)
    assert game.events.get(f"decision:{LOOK_THEN_ATTACH}") == 1


def test_thrifty_swallow_attaches_fewer_when_hand_already_has_energy():
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    game = Game(a, b, default_family_rules(), StrategySpec.from_dict("thrifty"), StrategySpec.from_dict("control"), Random(1), trace=True)
    me = game.players["a"]
    dondozo = _idx(me, "Dondozo")
    me.active = Pokemon(card_i=dondozo, played_turn=0)
    me.hand = [_idx(me, "Water Energy")]
    me.bench = []
    me.deck = [
        _idx(me, "Corphish"),
        _idx(me, "Bronzor"),
        _idx(me, "Oddish"),
        _idx(me, "Aipom"),
        _idx(me, "Baltoy"),
    ]
    game._swallow_energy(me, 5)
    assert any("looked at 5" in line for line in game.trace)
    assert len(me.active.energy) < 5
    assert len(me.active.energy) + len(me.deck) == 5


def test_simulate_match_applies_card_overlay_and_rejects_illegal_look():
    init_db()
    ok = run_tool(
        "simulate_match",
        {
            "deck_a_id": "seed-a",
            "deck_b_id": "seed-b",
            "games": 4,
            "queries": [],
            "card_overlay": {"sv04-055": {"params": {"look": 3}}},
        },
    )
    assert "error" not in ok
    assert ok["method"]["card_overlay"]["shared"] == {"sv04-055": {"params": {"look": 3}}}
    bad = run_tool(
        "simulate_match",
        {
            "deck_a_id": "seed-a",
            "deck_b_id": "seed-b",
            "games": 4,
            "card_overlay": {"sv04-055": {"params": {"look": 7}}},
        },
    )
    assert "above printed look" in bad["error"]


def test_product_chat_still_cannot_edit_the_repo():
    opts = product_chat_agent_options(name="Family Cup chat")
    payload = opts.to_json()
    assert payload["tools"]["names"] == ["mcp"]
    disallowed = set(payload["disallowedTools"])
    assert {"shell", "edit", "delete", "task"} <= disallowed
    assert "card_overlay" in FAMILY_CUP_BRIEF
    assert "card_overlay" in FOLLOWUP_TOOL_HINT
    assert "cannot edit the git checkout" in FAMILY_CUP_BRIEF
    assert COACH_SANDBOX_DIR.resolve() != ROOT.resolve()
