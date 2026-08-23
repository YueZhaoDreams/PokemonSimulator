from random import Random

from app.engine.game import Game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, SET_T_NAMES, build_fallback_deck, fallback_named


def test_mulligan_reshuffles_until_a_basic():
    """Official opening: 7 cards; if no Basic, shuffle back and draw again."""
    bricks = [fallback_named("Hop")] * 30
    legal = [fallback_named("Clefairy")] + [fallback_named("Hop")] * 29
    game = Game(
        bricks,
        legal,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("party"),
        Random(1),
    )
    a, b = game.players["a"], game.players["b"]
    assert a.mulligans == 8
    assert a.active is None
    assert b.active is not None
    assert b.card(b.active.card_i).name == "Clefairy"
    assert b.card(b.active.card_i).is_basic


def test_cdst_opening_always_puts_a_basic_active():
    specs = {
        "c": ("party", SET_C_NAMES, {"Clefairy", "Mewtwo ex"}),
        "d": ("demolish", SET_D_NAMES, {"Cornerstone Mask Ogerpon ex"}),
        "s": ("slash", SET_S_NAMES, {"Sprigatito", "Wo-Chien ex", "Tangela"}),
        "t": ("phantom", SET_T_NAMES, {"Dreepy", "Budew", "Fezandipiti ex"}),
    }
    for key, (strat, names, allowed) in specs.items():
        deck = build_fallback_deck(list(names))
        dummy = build_fallback_deck(list(SET_D_NAMES))
        for seed in range(80):
            game = Game(
                deck,
                dummy,
                default_family_rules(),
                StrategySpec.from_dict(strat),
                StrategySpec.from_dict("demolish"),
                Random(seed),
            )
            me = game.players["a"]
            assert me.active is not None, (key, seed)
            name = me.card(me.active.card_i).name
            assert name in allowed, (key, seed, name)
            assert me.card(me.active.card_i).is_basic
