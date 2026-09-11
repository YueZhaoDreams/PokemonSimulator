from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T60_NAMES, build_fallback_deck, fallback_named


def test_c60_locked_list_has_no_lillie_clefairy_ex():
    assert "Lillie's Clefairy ex" not in SET_C60_NAMES


def test_party_benches_one_lillie_clefairy_ex():
    names = list(SET_C60_NAMES)
    names[names.index("Psychic Energy")] = "Lillie's Clefairy ex"
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )
    me = game.players["a"]
    lillie = next(i for i, c in enumerate(me.cards) if c.name == "Lillie's Clefairy ex")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = [lillie]
    game._play_basics(me)
    assert any(me.card(m.card_i).name == "Lillie's Clefairy ex" for m in me.in_play())
    assert lillie not in me.hand


def test_lillie_clefairy_is_not_a_party_engine():
    card = fallback_named("Lillie's Clefairy ex")
    game = Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )
    assert game._is_clefairy(card) is False
