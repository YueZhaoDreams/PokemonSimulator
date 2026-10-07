"""Eco Arm shuffles Pokémon Tools from the discard pile into the deck.

Ancient Origins 71 prints a fixed count, not "up to". Set M uses that count on
Hero's Cape first, then Bursting Balloon, then Bravery Charm. Battle Cage is a
Stadium and is not a Tool.
"""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

PRINTED = "Shuffle 3 Pokémon Tool cards from your discard pile into your deck."


def _game(hand: list[str], discard: list[str]) -> tuple[Game, object]:
    names = ["Mew ex", "Igglybuff", "Nest Ball"] + hand + discard
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
    iggly = take("Igglybuff")
    me.active = Pokemon(card_i=mew, played_turn=0)
    me.bench = [Pokemon(card_i=iggly, played_turn=0)]
    me.hand = [take(name) for name in hand]
    me.discard = [take(name) for name in discard]
    me.deck = [i for i in range(len(me.cards)) if i not in used and i not in {mew, iggly}]
    me.prizes = []
    return game, me


def _zone(me, zone: str) -> list[str]:
    return [me.card(i).name for i in getattr(me, zone)]


def test_printed_sentence_is_three_tools_into_the_deck():
    card = fallback_named("Eco Arm")
    assert card.text == PRINTED
    assert parse_trainer_effects(card.text) == [{"kind": "shuffle_tools_to_deck", "count": 3}]
    assert parse_trainer_effects(PRINTED.replace("3", "4")) == [
        {"kind": "shuffle_tools_to_deck", "count": 4}
    ]


def test_cape_then_balloon_then_charm_and_the_extra_tool_stays():
    game, me = _game(
        ["Eco Arm"],
        ["Muscle Band", "Bravery Charm", "Bursting Balloon", "Hero's Cape", "Battle Cage"],
    )
    game._play_trainers(me, game.players["b"], "a")
    deck = _zone(me, "deck")
    discard = _zone(me, "discard")
    assert deck.count("Hero's Cape") == 1
    assert deck.count("Bursting Balloon") == 1
    assert deck.count("Bravery Charm") == 1
    assert "Muscle Band" in discard
    assert "Battle Cage" in discard
    assert "Eco Arm" in discard
    assert "Hero's Cape" not in discard
    assert game.events["eco_arm"] == 1
    assert game.events["eco_arm_a"] == 1
    assert game.events["eco_arm_cape"] == 1
    assert game.events["eco_arm_balloon"] == 1
    assert game.events["eco_arm_charm"] == 1


def test_two_tools_and_a_stadium_cannot_play():
    game, me = _game(
        ["Eco Arm"],
        ["Hero's Cape", "Bursting Balloon", "Battle Cage"],
    )
    game._play_trainers(me, game.players["b"], "a")
    assert _zone(me, "hand") == ["Eco Arm"]
    assert "eco_arm" not in game.events
    assert "Hero's Cape" in _zone(me, "discard")


def test_balloon_and_charm_fill_the_three_when_cape_is_absent():
    game, me = _game(
        ["Eco Arm"],
        ["Bursting Balloon", "Bursting Balloon", "Bravery Charm", "Battle Cage"],
    )
    game._play_trainers(me, game.players["b"], "a")
    deck = _zone(me, "deck")
    discard = _zone(me, "discard")
    assert deck.count("Bursting Balloon") == 2
    assert deck.count("Bravery Charm") == 1
    assert "Battle Cage" in discard
    assert "eco_arm_cape" not in game.events
    assert game.events["eco_arm_balloon"] == 2
    assert game.events["eco_arm_charm"] == 1


def test_count_comes_from_the_effect_not_a_hardcoded_three():
    game, me = _game(
        [],
        ["Hero's Cape", "Bursting Balloon", "Bravery Charm", "Muscle Band"],
    )
    game._shuffle_tools_to_deck(me, 4)
    discard = _zone(me, "discard")
    assert discard == []
    assert game.events["eco_arm_cape"] == 1
    assert game.events["eco_arm_balloon"] == 1
    assert game.events["eco_arm_charm"] == 1


def test_cape_is_shuffled_before_arven_searches_for_it():
    game, me = _game(
        ["Eco Arm", "Arven"],
        ["Hero's Cape", "Bursting Balloon", "Bravery Charm"],
    )
    game._play_trainers(me, game.players["b"], "a")
    log = "\n".join(game.trace)
    assert log.index("Eco Arm shuffles Hero's Cape") < log.index("plays Arven")
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert "Bursting Balloon" in _zone(me, "deck")
    assert "Bravery Charm" in _zone(me, "deck")
