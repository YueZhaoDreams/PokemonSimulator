"""Poké Vital A follows the printed sentences: heal 150, and it stays in the discard pile."""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

POKE_VITAL_A_TEXT = (
    "Heal 150 damage from 1 of your Pokémon. "
    "This card can't be put into your hand or deck from the discard pile."
)


def _game(names: list[str]) -> Game:
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dondozo"] * 60),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )


def _reset(me, active, hand, deck, bench=None) -> None:
    me.active = active
    me.bench = list(bench or [])
    me.hand = list(hand)
    me.deck = list(deck)
    me.discard = []
    me.prizes = []
    me.supporter_used = False
    me.item_lock = False


def test_poke_vital_a_parses_printed_sentences():
    card = fallback_named("Poké Vital A")
    alias = fallback_named("Poke Vital A")
    assert card.text == POKE_VITAL_A_TEXT
    assert card.trainer_kind == "item"
    assert card.catalog_id == "sv06.5-062"
    assert alias.name == "Poké Vital A"
    assert alias.catalog_id == "sv06.5-062"
    assert parse_trainer_effects(card.text) == [{"kind": "heal", "amount": 150}]
    potion = parse_trainer_effects(fallback_named("Max Potion").text)
    assert potion == [{"kind": "heal_all", "discard_energy": True}]


def test_poke_vital_a_heals_150_and_stops_at_zero():
    game = _game(["Mew ex", "Poké Vital A", "Psychic Energy"] + ["Hop"] * 57)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    energy_i = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    _reset(me, Pokemon(card_i=mew_i, damage=160, energy=[energy_i]), [vital_i], [])
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 10
    assert me.active.energy == [energy_i]
    assert vital_i in me.discard
    assert game.events["poke_vital_a"] == 1

    me.active.damage = 40
    me.hand = [vital_i]
    me.discard = []
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0


def test_poke_vital_a_heals_the_active_mew_before_a_more_damaged_bench():
    game = _game(["Mew ex", "Mew ex", "Poké Vital A"] + ["Hop"] * 57)
    me = game.players["a"]
    mews = [i for i, c in enumerate(me.cards) if c.name == "Mew ex"]
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    active = Pokemon(card_i=mews[0], damage=40)
    bench = Pokemon(card_i=mews[1], damage=140)
    _reset(me, active, [vital_i], [], bench=[bench])
    game._play_trainers(me, game.players["b"], "a")
    assert active.damage == 0
    assert bench.damage == 140


def test_mew_baby_holds_poke_vital_a_until_the_hole_is_real():
    game = _game(["Mew ex", "Poké Vital A", "Hop"] + ["Igglybuff"] * 57)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    hop_i = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    _reset(me, Pokemon(card_i=mew_i, damage=10), [vital_i, hop_i], [])
    game._play_trainers(me, game.players["b"], "a")
    assert vital_i in me.hand
    assert "poke_vital_a" not in game.events

    me.active.damage = 40
    assert game._pick_trainer(me) == vital_i


def test_max_potion_is_played_before_poke_vital_a():
    game = _game(["Mew ex", "Max Potion", "Poké Vital A"] + ["Hop"] * 57)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    potion_i = next(i for i, c in enumerate(me.cards) if c.name == "Max Potion")
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    _reset(me, Pokemon(card_i=mew_i, damage=120), [potion_i, vital_i], [])
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert game.events["max_potion"] == 1
    assert "poke_vital_a" not in game.events
    assert vital_i in me.hand
    assert potion_i in me.discard


def test_arven_finds_poke_vital_a_for_a_damaged_mew():
    game = _game(["Mew ex", "Arven", "Poké Vital A", "Bravery Charm"] + ["Hop"] * 56)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    arven_i = next(i for i, c in enumerate(me.cards) if c.name == "Arven")
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    charm_i = next(i for i, c in enumerate(me.cards) if c.name == "Bravery Charm")
    _reset(me, Pokemon(card_i=mew_i, damage=80), [arven_i], [vital_i, charm_i])
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert game.events["poke_vital_a"] == 1
    assert game.events["arven"] == 1
    assert me.active.tool == charm_i


def test_discard_recyclers_leave_poke_vital_a():
    game = _game(["Poké Vital A", "Switch", "Hop", "Nest Ball"] + ["Igglybuff"] * 56)
    me = game.players["a"]
    vital_i = next(i for i, c in enumerate(me.cards) if c.name == "Poké Vital A")
    switch_i = next(i for i, c in enumerate(me.cards) if c.name == "Switch")
    hop_i = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    nest_i = next(i for i, c in enumerate(me.cards) if c.name == "Nest Ball")

    me.discard = [vital_i, switch_i]
    me.hand = []
    game._recycle_items_from_discard(me, 2)
    assert switch_i in me.hand
    assert vital_i in me.discard

    me.discard = [vital_i, hop_i]
    me.hand = []
    game._retrieve_from_discard(me, 1)
    assert hop_i in me.hand
    assert vital_i in me.discard
    assert "puzzle_retrieve" in game.events

    me.discard = [vital_i, nest_i]
    me.hand = []
    game._recycle_trainer_from_discard(me)
    assert nest_i in me.hand
    assert vital_i in me.discard

    babies = [i for i, c in enumerate(me.cards) if c.name == "Igglybuff"]
    me.hand = [babies[0], babies[1]]
    me.discard = [vital_i, switch_i]
    game._junk_arm(me, "a", me.card(vital_i), 2, True)
    assert switch_i in me.hand
    assert vital_i in me.discard
