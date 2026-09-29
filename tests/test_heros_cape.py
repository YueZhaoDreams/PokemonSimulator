"""Hero's Cape follows the printed sentence: +100 HP, and no Special Conditions."""

from random import Random

from app.engine.game import Game, Pokemon, ST_POISONED
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

HEROS_CAPE_TEXT = (
    "The Pokémon this card is attached to gets +100 HP, and can't be affected by any Special Conditions."
)


def _game() -> Game:
    names = ["Mew ex", "Igglybuff", "Hero's Cape", "Bravery Charm"] + ["Hop"] * 56
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dondozo"] * 60),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )


def test_heros_cape_printed_text_and_hp():
    card = fallback_named("Hero's Cape")
    assert card.text == HEROS_CAPE_TEXT
    assert card.catalog_id == "sv05-152"
    game = _game()
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    cape_i = next(i for i, c in enumerate(me.cards) if c.name == "Hero's Cape")
    charm_i = next(i for i, c in enumerate(me.cards) if c.name == "Bravery Charm")
    mew = Pokemon(card_i=mew_i)
    baby_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    baby = Pokemon(card_i=baby_i)
    me.active = mew
    me.bench = [baby]
    me.hand = [cape_i, charm_i]
    me.deck = []
    assert game._max_hp(me, mew) == 160
    assert game._attach_tool(me, "a", cape_i)
    assert mew.tool == cape_i
    assert game._max_hp(me, mew) == 260
    # Charm stays +50 on a Basic, and does not also take the cape's slot.
    baby.tool = charm_i
    assert game._max_hp(me, baby) == 80


def test_heros_cape_blocks_and_clears_special_conditions():
    game = _game()
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    cape_i = next(i for i, c in enumerate(me.cards) if c.name == "Hero's Cape")
    mew = Pokemon(card_i=mew_i, status=ST_POISONED)
    me.active = mew
    assert game._attach_tool(me, "a", cape_i)
    assert mew.status == 0
    game._apply_status(mew, "paralyzed")
    assert mew.status == 0
    assert game.events["special_condition_blocked"] == 1


def test_mew_baby_attaches_cape_to_an_open_mew_before_a_baby():
    game = _game()
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    baby_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    cape_i = next(i for i, c in enumerate(me.cards) if c.name == "Hero's Cape")
    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=baby_i)]
    me.hand = [cape_i]
    me.deck = []
    me.discard = []
    me.prizes = []
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.tool == cape_i
    assert game._max_hp(me, me.active) == 260
