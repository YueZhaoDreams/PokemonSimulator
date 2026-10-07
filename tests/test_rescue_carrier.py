"""Rescue Carrier returns up to two Pokémon whose printed HP is 90 or less.

The Evolving Skies sentence is the effect. Mew ex is 160 HP and stays in the
discard. Two 30 HP babies can come back on the same Item.
"""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

CARRIER = "Put up to 2 Pokémon, each with 90 HP or less, from your discard pile into your hand."


def _game(hand: list[str], discard: list[str]) -> tuple[Game, object]:
    names = ["Mew ex", "Nest Ball"] + hand + discard
    while len(names) < 40:
        names.append("Nest Ball")
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(["Mew ex"] + ["Nest Ball"] * 39),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("starmie"),
        Random(1),
        trace=True,
    )
    me = game.players["a"]
    used: list[int] = []

    def take(name: str) -> int:
        for i, card in enumerate(me.cards):
            if card.name == name and i not in used:
                used.append(i)
                return i
        raise AssertionError(name)

    mew = take("Mew ex")
    me.active = Pokemon(card_i=mew, played_turn=0)
    me.bench = []
    me.hand = [take(name) for name in hand]
    me.discard = [take(name) for name in discard]
    me.deck = [i for i in range(len(me.cards)) if i not in used and i != mew]
    me.prizes = []
    return game, me


def test_printed_sentence_is_two_pokemon_at_90_hp():
    spec = parse_trainer_effects(fallback_named("Rescue Carrier").text)[0]
    assert fallback_named("Rescue Carrier").text == CARRIER
    assert spec == {"kind": "rescue_carrier", "count": 2, "max_hp": 90}


def test_two_babies_return_and_mew_ex_stays_in_the_discard():
    game, me = _game(
        ["Rescue Carrier"],
        ["Igglybuff", "Mime Jr.", "Mew ex"],
    )
    game._play_trainers(me, game.players["b"], "a")
    hand = [me.card(i).name for i in me.hand]
    discard = [me.card(i).name for i in me.discard]
    assert hand.count("Igglybuff") == 1
    assert hand.count("Mime Jr.") == 1
    assert "Mew ex" not in hand
    assert "Mew ex" in discard
    assert "Rescue Carrier" in discard
    assert game.events["rescue_carrier"] == 2
    assert game.events["rescue_carrier_a"] == 2


def test_manaphy_returns_when_it_is_the_only_pokemon_at_or_under_90():
    game, me = _game(["Rescue Carrier"], ["Manaphy", "Mew ex"])
    game._play_trainers(me, game.players["b"], "a")
    assert [me.card(i).name for i in me.hand] == ["Manaphy"]
    assert "Mew ex" in [me.card(i).name for i in me.discard]
    assert game.events["rescue_carrier"] == 1


def test_empty_discard_does_not_play_the_item():
    game, me = _game(["Rescue Carrier"], [])
    game._play_trainers(me, game.players["b"], "a")
    assert [me.card(i).name for i in me.hand] == ["Rescue Carrier"]
    assert "rescue_carrier" not in game.events


def test_babies_come_back_before_night_stretcher_takes_mew():
    game, me = _game(
        ["Rescue Carrier", "Night Stretcher"],
        ["Igglybuff", "Igglybuff", "Mew ex"],
    )
    game._play_trainers(me, game.players["b"], "a")
    log = "\n".join(game.trace)
    assert log.index("Rescue Carrier takes") < log.index("Night Stretcher takes")
    hand = [me.card(i).name for i in me.hand]
    assert hand.count("Igglybuff") == 2
    assert hand.count("Mew ex") == 1
