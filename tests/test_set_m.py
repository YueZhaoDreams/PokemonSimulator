from __future__ import annotations

from random import Random

from app.engine.game import play_game
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import (
    SET_D60_NAMES,
    SET_M_NAMES,
    SET_M60_NAMES,
    SET_T60_NAMES,
    build_fallback_deck,
)


def test_set_m_card_count_and_composition():
    assert len(SET_M60_NAMES) == 60
    assert len(SET_M_NAMES) == 60
    assert SET_M_NAMES == SET_M60_NAMES

    # Count Pokémon
    assert SET_M60_NAMES.count("Mew ex") == 4
    assert SET_M60_NAMES.count("Mime Jr.") == 2
    assert SET_M60_NAMES.count("Igglybuff") == 4
    assert SET_M60_NAMES.count("Budew") == 3
    assert SET_M60_NAMES.count("Cleffa") == 2
    total_pokemon = 4 + 2 + 4 + 3 + 2
    assert total_pokemon == 15

    # Count Key Trainers
    assert SET_M60_NAMES.count("Buddy-Buddy Poffin") == 4
    assert SET_M60_NAMES.count("Battle Cage") == 4
    assert SET_M60_NAMES.count("Bravery Charm") == 4
    assert SET_M60_NAMES.count("Maximum Belt") == 1
    assert SET_M60_NAMES.count("Night Stretcher") == 4
    assert SET_M60_NAMES.count("Crushing Hammer") == 4
    assert SET_M60_NAMES.count("Switch") == 1


def test_load_seed_deck_m():
    deck_m60 = load_seed_deck("m60")
    assert deck_m60["id"] == "seed-m60"
    assert "Mew ex" in deck_m60["name"]
    assert len(deck_m60["cards"]) == 60
    assert default_rule_presets_for("seed-m60") == ["s60"]
    assert "seed-m60" in S60_SEED_IDS

    # "m" and "mew" alias to seed-m60
    deck_m = load_seed_deck("m")
    assert deck_m["id"] == "seed-m60"
    assert len(deck_m["cards"]) == 60

    deck_alias = load_seed_deck("mew")
    assert deck_alias["id"] == deck_m60["id"]


def test_set_m_gameplay_vs_t60_and_d60():
    deck_m = build_fallback_deck(list(SET_M60_NAMES))
    deck_t60 = build_fallback_deck(list(SET_T60_NAMES))
    deck_d60 = build_fallback_deck(list(SET_D60_NAMES))

    rules = standard_60_rules()
    strat_m = StrategySpec.from_dict("mew_baby")
    strat_t = StrategySpec.from_dict("phantom")
    strat_d = StrategySpec.from_dict("demolish")

    res_t = play_game(deck_m, deck_t60, rules, strat_m, strat_t, Random(42))
    assert res_t.winner in {"a", "b"}
    assert res_t.turns > 0

    res_d = play_game(deck_m, deck_d60, rules, strat_m, strat_d, Random(42))
    assert res_d.winner in {"a", "b"}
    assert res_d.turns > 0
