"""Max Potion follows the printed sentence: full heal, then discard Energy if you healed."""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

MAX_POTION_TEXT = (
    "Heal all damage from 1 of your Pokémon. If you do, discard all Energy from that Pokémon."
)
OLD_MAX_POTION_TEXT = (
    "Heal all damage from 1 of your Pokémon. Then, discard all Energy attached to that Pokémon."
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


def test_max_potion_parses_printed_sentence():
    card = fallback_named("Max Potion")
    assert card.text == MAX_POTION_TEXT
    assert card.trainer_kind == "item"
    assert parse_trainer_effects(card.text) == [{"kind": "heal_all", "discard_energy": True}]
    assert parse_trainer_effects(OLD_MAX_POTION_TEXT) == [{"kind": "heal_all", "discard_energy": True}]
    wally = parse_trainer_effects(fallback_named("Wally's Compassion").text)
    assert wally[0]["kind"] == "heal_mega_return_energy"


def test_max_potion_heals_mew_and_discards_energy_only_when_attached():
    game = _game(["Mew ex", "Igglybuff", "Max Potion", "Psychic Energy"] + ["Hop"] * 56)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    baby_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    energy_i = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    mew = Pokemon(card_i=mew_i, damage=10, energy=[energy_i])
    baby = Pokemon(card_i=baby_i, damage=20)
    _reset(me, mew, [], [], bench=[baby])
    game._heal_all(me, discard_energy=True)
    assert mew.damage == 0
    assert mew.energy == []
    assert me.discard == [energy_i]
    assert baby.damage == 20
    assert game.events["max_potion"] == 1
    assert game.events["max_potion_discard_energy"] == 1


def test_max_potion_on_zero_energy_mew_discards_nothing():
    game = _game(["Mew ex", "Max Potion"] + ["Hop"] * 58)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    _reset(me, Pokemon(card_i=mew_i, damage=150), [], [])
    game._resolve_trainer(me, game.players["b"], me.card(next(i for i, c in enumerate(me.cards) if c.name == "Max Potion")))
    assert me.active.damage == 0
    assert me.active.energy == []
    assert "max_potion_discard_energy" not in game.events


def test_max_potion_whiffs_when_nothing_is_damaged():
    game = _game(["Mew ex", "Psychic Energy"] + ["Hop"] * 58)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    energy_i = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    _reset(me, Pokemon(card_i=mew_i, damage=0, energy=[energy_i]), [], [])
    game._heal_all(me, discard_energy=True)
    assert me.active.energy == [energy_i]
    assert game.events["max_potion_whiff"] == 1
    assert "max_potion" not in game.events


def test_mew_baby_holds_max_potion_until_mew_is_hurt_then_plays_it():
    game = _game(["Mew ex", "Max Potion", "Hop"] + ["Igglybuff"] * 57)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    potion_i = next(i for i, c in enumerate(me.cards) if c.name == "Max Potion")
    hop_i = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    _reset(me, Pokemon(card_i=mew_i, damage=0), [potion_i, hop_i], [])
    assert game._pick_trainer(me) != potion_i
    game._play_trainers(me, game.players["b"], "a")
    assert "max_potion" not in game.events
    assert potion_i in me.hand

    me.active.damage = 40
    me.hand = [potion_i, hop_i]
    assert game._pick_trainer(me) == potion_i
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert game.events["max_potion"] == 1


def test_arven_finds_max_potion_for_a_damaged_mew_and_plays_it():
    game = _game(["Mew ex", "Arven", "Max Potion", "Bravery Charm"] + ["Hop"] * 56)
    me = game.players["a"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    arven_i = next(i for i, c in enumerate(me.cards) if c.name == "Arven")
    potion_i = next(i for i, c in enumerate(me.cards) if c.name == "Max Potion")
    charm_i = next(i for i, c in enumerate(me.cards) if c.name == "Bravery Charm")
    _reset(me, Pokemon(card_i=mew_i, damage=80), [arven_i], [potion_i, charm_i])
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert game.events["max_potion"] == 1
    assert game.events["arven"] == 1
