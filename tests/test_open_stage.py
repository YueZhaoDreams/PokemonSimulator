from random import Random

from app.engine.game import play_game
from app.engine.models import default_family_rules, no_pokemon_energy_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_E_NAMES, SET_F_NAMES, build_fallback_deck, fallback_named


def test_no_pokemon_energy_rules_preset():
    rules = no_pokemon_energy_family_rules()
    assert rules.pokemon_as_energy is False
    assert rules.deck_size == 30
    assert rules.prize_count == 3
    assert default_family_rules().pokemon_as_energy is True


def test_rule_b_still_treats_pokemon_as_energy():
    from app.engine.effects import is_basic_energy

    pika = fallback_named("Pikachu")
    assert is_basic_energy(pika, pokemon_as_energy=True)
    assert not is_basic_energy(pika, pokemon_as_energy=False)


def test_set_e_and_f_sizes():
    assert len(SET_E_NAMES) == 30
    assert len(SET_F_NAMES) == 30
    assert "Iris's Fighting Spirit" in SET_E_NAMES
    assert "Hippopotas" in SET_E_NAMES
    assert "Glimmet" not in SET_E_NAMES
    assert "Quaquaval" not in SET_F_NAMES
    assert "Iono" in SET_F_NAMES


def test_e_vs_f_completes_without_pokemon_energy():
    e = build_fallback_deck(SET_E_NAMES)
    f = build_fallback_deck(SET_F_NAMES)
    result = play_game(
        e,
        f,
        no_pokemon_energy_family_rules(),
        StrategySpec.from_dict("shock"),
        StrategySpec.from_dict("carnival"),
        Random(11),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
