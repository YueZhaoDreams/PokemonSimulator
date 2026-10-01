"""Bursting Balloon, from the printed XY—BREAKpoint sentence."""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

PRINTED = (
    "If this card is attached to 1 of your Pokémon, discard it at the end of your opponent’s turn.\n\n"
    "If the Pokémon this card is attached to is your Active Pokémon and is damaged by an opponent’s attack "
    "(even if that Pokémon is Knocked Out), put 6 damage counters on the Attacking Pokémon."
)


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 40:
        names.append("Nest Ball")
    return names


def _game(a_names: list[str], b_names: list[str]) -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _seat(player, active: int, bench: list[int], tool: int | None = None) -> None:
    used = {active, *bench}
    if tool is not None:
        used.add(tool)
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        zone[:] = [i for i in zone if i not in used]
    player.active = Pokemon(card_i=active, played_turn=0, tool=tool)
    player.bench = [Pokemon(card_i=i, played_turn=0) for i in bench]


def test_printed_bursting_balloon_sentence():
    card = fallback_named("Bursting Balloon")
    assert card.text == PRINTED
    assert (card.trainer_kind or "").lower() == "tool"
    effects = parse_trainer_effects(PRINTED)
    assert effects == [
        {"kind": "counters_on_attacker", "counters": 6},
        {"kind": "discard_end_of_opponents_turn"},
    ]


def test_balloon_goes_on_a_baby_and_charm_stays_for_mew():
    game = _game(
        ["Mew ex", "Budew", "Igglybuff", "Bursting Balloon", "Bravery Charm", "Hero's Cape"],
        ["Clefairy"],
    )
    me = game.players["a"]
    mew = _idxs(me, "Mew ex")[0]
    budew = _idxs(me, "Budew")[0]
    iggly = _idxs(me, "Igglybuff")[0]
    balloon = _idxs(me, "Bursting Balloon")[0]
    charm = _idxs(me, "Bravery Charm")[0]
    cape = _idxs(me, "Hero's Cape")[0]
    _seat(me, mew, [budew, iggly])
    assert game._tool_target(me, "a", me.card(balloon)) is me.bench[0]
    assert game._tool_target(me, "a", me.card(charm)) is me.active
    assert game._tool_target(me, "a", me.card(cape)) is me.active

    _seat(me, budew, [mew])
    assert game._tool_target(me, "a", me.card(balloon)) is me.active
    assert me.card(game._tool_target(me, "a", me.card(charm)).card_i).name == "Mew ex"
    assert me.card(game._tool_target(me, "a", me.card(cape)).card_i).name == "Mew ex"

    _seat(me, budew, [])
    assert game._tool_target(me, "a", me.card(charm)) is None
    assert game._tool_target(me, "a", me.card(cape)) is None
    _seat(me, mew, [])
    assert game._tool_target(me, "a", me.card(balloon)) is None


def test_balloon_puts_printed_counters_on_the_attacker_then_discards():
    game = _game(
        ["Budew", "Bravery Charm", "Mew ex"],
        ["Budew", "Bursting Balloon", "Mew ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    charm = _idxs(me, "Bravery Charm")[0]
    defender = _idxs(foe, "Budew")[0]
    balloon = _idxs(foe, "Bursting Balloon")[0]
    _seat(me, attacker, [], tool=charm)
    _seat(foe, defender, [], tool=balloon)

    game._attack(me, foe, "a")
    assert foe.active.damage == 10
    assert me.active.damage == 60
    assert foe.active.tool == balloon
    assert game.events["bursting_balloon"] == 6

    game._discard_opponent_turn_tools("a")
    assert foe.active.tool is None
    assert balloon in foe.discard
    assert game.events["bursting_balloon_discard"] == 1


def test_balloon_still_counters_when_the_baby_is_knocked_out():
    game = _game(
        ["Igglybuff", "Budew", "Mew ex"],
        ["Budew", "Bursting Balloon", "Mew ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    iggly = _idxs(me, "Igglybuff")[0]
    bench_baby = _idxs(me, "Budew")[0]
    mew_a = _idxs(me, "Mew ex")[0]
    defender = _idxs(foe, "Budew")[0]
    balloon = _idxs(foe, "Bursting Balloon")[0]
    mew_b = _idxs(foe, "Mew ex")[0]
    _seat(me, iggly, [bench_baby, mew_a])
    _seat(foe, defender, [mew_b], tool=balloon)
    prizes_a = me.prizes_taken
    prizes_b = foe.prizes_taken

    game._attack(me, foe, "a")
    assert me.active.damage == 60
    assert game._check_ko(foe, me, "b") is False
    assert game._check_ko(me, foe, "a") is False
    assert me.prizes_taken == prizes_a + 1
    assert foe.prizes_taken == prizes_b + 1
    assert balloon in foe.discard
    assert me.card(me.active.card_i).name == "Mew ex"
    assert foe.card(foe.active.card_i).name == "Mew ex"


def test_bench_damage_does_not_pop_the_balloon():
    game = _game(
        ["Budew", "Mew ex"],
        ["Mew ex", "Budew", "Bursting Balloon"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    mew = _idxs(foe, "Mew ex")[0]
    baby = _idxs(foe, "Budew")[0]
    balloon = _idxs(foe, "Bursting Balloon")[0]
    _seat(me, attacker, [])
    _seat(foe, mew, [baby])
    foe.bench[0].tool = balloon

    game._add_attack_damage(foe, foe.bench[0], 10)
    assert me.active.damage == 0
    assert foe.bench[0].tool == balloon
    assert "bursting_balloon" not in game.events


def test_arven_takes_cape_for_an_open_mew_and_balloon_for_a_bare_baby():
    game = _game(
        ["Mew ex", "Budew", "Bursting Balloon", "Bravery Charm", "Hero's Cape", "Nest Ball", "Arven"],
        ["Clefairy"],
    )
    me = game.players["a"]
    mew = _idxs(me, "Mew ex")[0]
    budew = _idxs(me, "Budew")[0]
    balloon = _idxs(me, "Bursting Balloon")
    charm = _idxs(me, "Bravery Charm")
    cape = _idxs(me, "Hero's Cape")
    nest = _idxs(me, "Nest Ball")
    arven = _idxs(me, "Arven")

    def _deck() -> None:
        for zone_name in ("hand", "deck", "prizes", "discard"):
            zone = getattr(me, zone_name)
            zone[:] = [i for i in zone if i not in set(balloon + charm + cape + nest + arven)]
        me.deck = balloon + charm + cape + nest
        me.hand = list(arven)

    _seat(me, budew, [mew])
    _deck()
    game._arven(me, "a")
    assert any(me.card(i).name == "Hero's Cape" for i in me.hand)
    assert any(me.card(i).name == "Bursting Balloon" for i in me.deck)

    me.bench[0].tool = charm[0]
    _deck()
    game._arven(me, "a")
    assert any(me.card(i).name == "Bursting Balloon" for i in me.hand)
    assert any(me.card(i).name == "Bravery Charm" for i in me.deck)
    assert any(me.card(i).name == "Hero's Cape" for i in me.deck)
