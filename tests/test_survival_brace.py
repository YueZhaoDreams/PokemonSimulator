"""Survival Brace follows the printed sentence: full HP, lethal attack damage, left at 10, then discard."""

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

SURVIVAL_BRACE_TEXT = (
    "If the Pokémon this card is attached to has full HP and would be Knocked Out by damage "
    "from an attack from your opponent's Pokémon, it is not Knocked Out, and its remaining HP "
    "becomes 10. Then, discard this card."
)


def _game(names: list[str], foe: list[str] | None = None) -> Game:
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(foe or ["Dondozo"] * 60),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_survival_brace_printed_text():
    card = fallback_named("Survival Brace")
    assert card.text == SURVIVAL_BRACE_TEXT
    assert card.catalog_id == "sv06-164"


def test_phantom_dive_leaves_a_full_mew_at_10_and_discards_the_brace():
    game = _game(
        ["Dragapult ex", "Fire Energy", "Psychic Energy"] + ["Hop"] * 57,
        ["Mew ex", "Survival Brace"] + ["Hop"] * 58,
    )
    me, foe = game.players["a"], game.players["b"]
    drag = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    fire = next(i for i, c in enumerate(me.cards) if c.name == "Fire Energy")
    psychic = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    mew_i = next(i for i, c in enumerate(foe.cards) if c.name == "Mew ex")
    brace_i = next(i for i, c in enumerate(foe.cards) if c.name == "Survival Brace")
    me.active = Pokemon(card_i=drag, energy=[fire, psychic])
    foe.active = Pokemon(card_i=mew_i, tool=brace_i)
    game._attack(me, foe, "a")
    assert foe.active is not None
    assert game._max_hp(foe, foe.active) - foe.active.damage == 10
    assert foe.active.tool is None
    assert brace_i in foe.discard
    assert game.events["survival_brace"] == 1


def test_dive_bench_counters_do_not_trigger_survival_brace():
    game = _game(
        ["Dragapult ex", "Fire Energy", "Psychic Energy"] + ["Hop"] * 57,
        ["Mew ex", "Igglybuff", "Survival Brace"] + ["Hop"] * 57,
    )
    me, foe = game.players["a"], game.players["b"]
    drag = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    fire = next(i for i, c in enumerate(me.cards) if c.name == "Fire Energy")
    psychic = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    mew_i = next(i for i, c in enumerate(foe.cards) if c.name == "Mew ex")
    baby_i = next(i for i, c in enumerate(foe.cards) if c.name == "Igglybuff")
    brace_i = next(i for i, c in enumerate(foe.cards) if c.name == "Survival Brace")
    me.active = Pokemon(card_i=drag, energy=[fire, psychic])
    foe.active = Pokemon(card_i=mew_i)
    foe.bench = [Pokemon(card_i=baby_i, tool=brace_i)]
    game._attack(me, foe, "a")
    assert foe.bench[0].damage == 60
    assert foe.bench[0].tool == brace_i
    assert "survival_brace" not in game.events


def test_brace_does_not_save_a_mew_that_was_already_damaged():
    game = _game(
        ["Dragapult ex", "Fire Energy", "Psychic Energy"] + ["Hop"] * 57,
        ["Mew ex", "Survival Brace"] + ["Hop"] * 58,
    )
    me, foe = game.players["a"], game.players["b"]
    drag = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    fire = next(i for i, c in enumerate(me.cards) if c.name == "Fire Energy")
    psychic = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    mew_i = next(i for i, c in enumerate(foe.cards) if c.name == "Mew ex")
    brace_i = next(i for i, c in enumerate(foe.cards) if c.name == "Survival Brace")
    me.active = Pokemon(card_i=drag, energy=[fire, psychic])
    foe.active = Pokemon(card_i=mew_i, tool=brace_i, damage=10)
    game._attack(me, foe, "a")
    assert foe.active.damage == 210
    assert foe.active.tool == brace_i
    assert "survival_brace" not in game.events


def test_demolish_ignores_survival_brace():
    game = Game(
        build_fallback_deck(["Cornerstone Mask Ogerpon ex"] + ["Fighting Energy"] * 3 + ["Hop"] * 56),
        build_fallback_deck(["Igglybuff", "Survival Brace"] + ["Hop"] * 58),
        standard_60_rules(),
        StrategySpec.from_dict("demolish"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )
    me, foe = game.players["a"], game.players["b"]
    oger = next(i for i, c in enumerate(me.cards) if "Ogerpon" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Fighting Energy"][:3]
    baby_i = next(i for i, c in enumerate(foe.cards) if c.name == "Igglybuff")
    brace_i = next(i for i, c in enumerate(foe.cards) if c.name == "Survival Brace")
    me.active = Pokemon(card_i=oger, energy=fuels)
    foe.active = Pokemon(card_i=baby_i, tool=brace_i)
    game._attack(me, foe, "a")
    assert foe.active.damage == 140
    assert foe.active.tool == brace_i
    assert "survival_brace" not in game.events


def test_charm_takes_the_active_mew_and_brace_the_next_one():
    game = _game(["Mew ex", "Mew ex", "Bravery Charm", "Survival Brace"] + ["Hop"] * 56)
    me = game.players["a"]
    mews = [i for i, c in enumerate(me.cards) if c.name == "Mew ex"]
    charm_i = next(i for i, c in enumerate(me.cards) if c.name == "Bravery Charm")
    brace_i = next(i for i, c in enumerate(me.cards) if c.name == "Survival Brace")
    me.active = Pokemon(card_i=mews[0])
    me.bench = [Pokemon(card_i=mews[1])]
    me.hand = [brace_i, charm_i]
    me.deck = []
    me.discard = []
    me.prizes = []
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.tool == charm_i
    assert me.bench[0].tool == brace_i


def test_arven_takes_bravery_charm_ahead_of_survival_brace():
    game = _game(["Mew ex", "Bravery Charm", "Survival Brace", "Nest Ball"] + ["Hop"] * 56)
    me = game.players["a"]
    charm_i = next(i for i, c in enumerate(me.cards) if c.name == "Bravery Charm")
    brace_i = next(i for i, c in enumerate(me.cards) if c.name == "Survival Brace")
    nest_i = next(i for i, c in enumerate(me.cards) if c.name == "Nest Ball")
    me.hand = []
    me.deck = [brace_i, charm_i, nest_i]
    me.discard = []
    me.prizes = []
    game._arven(me, "a")
    assert charm_i in me.hand
    assert brace_i in me.deck
