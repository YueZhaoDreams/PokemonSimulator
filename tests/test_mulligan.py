from random import Random

from app.engine.game import Game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, SET_T_NAMES, build_fallback_deck, fallback_named


def _zones(player) -> int:
    n = len(player.hand) + len(player.deck) + len(player.prizes)
    if player.active:
        n += 1
    n += len(player.bench)
    return n


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
        trace=True,
    )
    a, b = game.players["a"], game.players["b"]
    assert a.mulligans == 8
    assert a.active is None
    assert b.active is not None
    assert b.card(b.active.card_i).name == "Clefairy"
    assert b.card(b.active.card_i).is_basic
    # B draws one card per A's mulligans after prizes (always taken).
    assert game.events.get("mulligan_bonus_draw:b") == 8
    assert _zones(a) == 30
    assert _zones(b) == 30
    setup_b = 7
    assert len(b.hand) + 1 + len(b.bench) == setup_b + a.mulligans
    assert len(b.prizes) == 3
    assert any("draws 8 for opponent mulligans" in line for line in game.trace)


def test_cdst_opening_always_puts_a_basic_active():
    specs = {
        "c": ("party", SET_C_NAMES, {"Clefairy", "Mewtwo ex", "Lillie's Clefairy ex"}),
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


def test_bonus_draws_are_one_per_opponent_mulligan():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    saw = False
    for seed in range(250):
        game = Game(
            c,
            d,
            default_family_rules(),
            StrategySpec.from_dict("party"),
            StrategySpec.from_dict("demolish"),
            Random(seed),
        )
        me, foe = game.players["a"], game.players["b"]
        assert _zones(me) == 30
        assert _zones(foe) == 30
        assert game.events.get("mulligan_bonus_draw:a", 0) == foe.mulligans
        assert game.events.get("mulligan_bonus_draw:b", 0) == me.mulligans
        setup = getattr(me, "_opening_names")
        assert len(setup) == 7
        if foe.mulligans:
            saw = True
            assert len(me.hand) + 1 + len(me.bench) == 7 + foe.mulligans
    assert saw
