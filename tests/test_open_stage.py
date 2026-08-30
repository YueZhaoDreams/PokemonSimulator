from random import Random

from app.engine.game import play_game
from app.engine.models import default_family_rules, open_stage_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_E_NAMES, SET_F_NAMES, build_fallback_deck, fallback_named


def test_open_stage_rules_preset():
    rules = open_stage_family_rules()
    assert rules.any_stage_playable is True
    assert rules.pokemon_as_energy is True
    assert rules.deck_size == 30
    assert default_family_rules().any_stage_playable is False


def test_open_stage_plays_quaquaval_from_hand():
    """Without Quaxly, Quaquaval can still start under Open Stage."""
    deck = build_fallback_deck(
        ["Quaquaval"]
        + ["Hop"] * 6
        + ["Water Energy"] * 8
        + ["Orthworm"] * 5
        + ["Metal Energy"] * 10
    )
    fodder = build_fallback_deck(
        ["Pikachu"] + ["Hop"] * 9 + ["Lightning Energy"] * 10 + ["Electrike"] * 10
    )
    result = play_game(
        deck,
        fodder,
        open_stage_family_rules(),
        StrategySpec.from_dict("carnival"),
        StrategySpec.from_dict("shock"),
        Random(7),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert "Quaquaval" in result.opening_a or any(
        "Quaquaval" in line for line in (result.trace or [])
    )


def test_rule_b_still_requires_basic():
    bricks = [fallback_named("Quaquaval")] + [fallback_named("Hop")] * 29
    legal = [fallback_named("Pikachu")] + [fallback_named("Hop")] * 29
    result = play_game(
        bricks,
        legal,
        default_family_rules(),
        StrategySpec.from_dict("carnival"),
        StrategySpec.from_dict("shock"),
        Random(3),
        trace=True,
    )
    # A has only Stage 2 + trainers — no Basic → loses opening under Rule B.
    assert result.winner == "b"
    assert "Basic" in (result.reason or "")


def test_set_e_and_f_sizes():
    assert len(SET_E_NAMES) == 30
    assert len(SET_F_NAMES) == 30
    assert SET_F_NAMES.count("Quaquaval") == 1
    assert "Quaxly" not in SET_F_NAMES
