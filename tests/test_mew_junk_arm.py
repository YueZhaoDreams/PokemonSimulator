"""Junk Arm on the Mew list puts a discarded Trainer into the hand.

Printed sentence: discard 2 cards from your hand, search the discard pile for a
Trainer, show it, put it into the hand. You can't choose Junk Arm.
The 2 cards are Pokémon a Rescue Carrier or Night Stretcher can take back.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck, fallback_named

JUNK_ARM = (
    "Discard 2 cards from your hand. Search your discard pile for a Trainer card, show it to your "
    "opponent, and put it in your hand. You can't choose Junk Arm with this effect."
)
NARROW_CARRIER = (
    "Put up to 2 Pokémon, each with 40 HP or less, from your discard pile into your hand."
)


def _pad(names: list[str]) -> list[str]:
    out = list(names)
    while len(out) < 40:
        out.append("Hop")
    return out


def _take(player, name: str) -> int:
    for zone in (player.deck, player.hand, player.discard, player.prizes):
        for card_i in list(zone):
            if player.card(card_i).name == name:
                zone.remove(card_i)
                return card_i
    raise AssertionError(f"{name} not found")


def _clear(player) -> None:
    for zone in (player.hand, player.discard, player.prizes):
        player.deck.extend(zone)
        zone.clear()
    for mon in player.in_play():
        player.deck.extend([mon.card_i, *mon.energy])
        if mon.tool is not None:
            player.deck.append(mon.tool)
    player.active = None
    player.bench = []
    player.deck = sorted(set(player.deck))
    player.supporter_used = False
    player.item_lock = False


def _mon(player, name: str, damage: int = 0) -> Pokemon:
    mon = Pokemon(card_i=_take(player, name), played_turn=0)
    mon.damage = damage
    return mon


def _built(names: list[str]):
    game = Game(
        build_fallback_deck(_pad(names + ["Hop"] * 8)),
        build_fallback_deck(_pad(["Igglybuff", "Mew ex", "Manaphy"])),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("thrifty"),
        Random(1),
    )
    me, foe = game.players["a"], game.players["b"]
    _clear(me)
    _clear(foe)
    foe.active = _mon(foe, "Igglybuff")
    return game, me, foe


def _zone(me, deck: list[str], hand: list[str], discard: list[str]) -> None:
    deck_i = [_take(me, name) for name in deck]
    hand_i = [_take(me, name) for name in hand]
    discard_i = [_take(me, name) for name in discard]
    me.deck = deck_i
    me.hand = hand_i
    me.discard = discard_i


def test_printed_junk_arm_discards_two_and_cannot_choose_itself():
    card = fallback_named("Junk Arm")
    assert card.text == JUNK_ARM
    assert card.trainer_kind == "item"
    assert parse_trainer_effects(card.text) == [{"kind": "junk_arm", "discard": 2, "exclude_self": True}]
    text = StrategySpec.from_dict("mew_baby").description
    for sentence in (
        "Junk Arm",
        "Counter Catcher",
        "Hero's Cape",
        "Bursting Balloon",
        "Rescue Carrier",
        "Night Stretcher",
    ):
        assert sentence in text


def test_junk_arm_attaches_a_discarded_cape_and_pitches_babies():
    game, me, foe = _built(
        ["Mew ex", "Igglybuff", "Igglybuff", "Junk Arm", "Hero's Cape", "Rescue Carrier", "Hop", "Hop"]
    )
    me.active = _mon(me, "Mew ex")
    _zone(
        me,
        ["Rescue Carrier"],
        ["Junk Arm", "Igglybuff", "Igglybuff"],
        ["Hero's Cape"],
    )
    babies = [i for i in me.hand if me.card(i).name == "Igglybuff"]
    cape = me.discard[0]
    assert game._mew_junk_plan(me, foe)[1] == "hero's cape"
    game._play_trainers(me, foe, "a")
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert game.events["junk_arm_into:Hero's Cape"] == 1
    assert babies[0] in me.discard and babies[1] in me.discard
    assert cape not in me.discard


def test_junk_arm_takes_balloon_while_arven_is_in_hand():
    game, me, foe = _built(
        ["Mew ex", "Igglybuff", "Igglybuff", "Igglybuff", "Junk Arm", "Bursting Balloon", "Arven", "Night Stretcher"]
    )
    me.active = _mon(me, "Mew ex")
    baby = _mon(me, "Igglybuff")
    me.bench = [baby]
    _zone(
        me,
        ["Night Stretcher"],
        ["Junk Arm", "Arven", "Igglybuff", "Igglybuff"],
        ["Bursting Balloon"],
    )
    arven = next(i for i in me.hand if me.card(i).name == "Arven")
    # Balloon is in the discard, so Arven cannot fetch it. Junk Arm is the first play.
    assert game._pick_trainer(me) == next(i for i in me.hand if me.card(i).name == "Junk Arm")
    game._play_trainers(me, foe, "a")
    assert baby.tool is not None
    assert me.card(baby.tool).name == "Bursting Balloon"
    assert game.events["junk_arm_into:Bursting Balloon"] == 1
    # Junk Arm is an Item. Arven still searches the deck, finds Night Stretcher,
    # and that Item returns one of the two Pokémon Junk Arm discarded.
    assert arven not in me.hand
    assert game.events["arven"] == 1
    assert game.events["night_stretcher"] == 1
    assert sum(me.card(i).name == "Igglybuff" for i in me.hand) == 1
    assert sum(me.card(i).name == "Igglybuff" for i in me.discard) == 1


def test_junk_arm_waits_when_nothing_can_recover_the_discarded_pokemon():
    game, me, foe = _built(["Mew ex", "Igglybuff", "Igglybuff", "Junk Arm", "Hero's Cape", "Hop", "Hop"])
    me.active = _mon(me, "Mew ex")
    _zone(me, ["Hop", "Hop"], ["Junk Arm", "Igglybuff", "Igglybuff"], ["Hero's Cape"])
    arm = next(i for i in me.hand if me.card(i).name == "Junk Arm")
    assert game._mew_junk_fodder(me) == []
    assert game._pick_trainer(me) is None
    game._play_trainers(me, foe, "a")
    assert arm in me.hand
    assert me.active.tool is None
    assert any(me.card(i).name == "Hero's Cape" for i in me.discard)


def test_junk_arm_uses_the_printed_carrier_hp():
    game, me, foe = _built(
        ["Mew ex", "Igglybuff", "Igglybuff", "Manaphy", "Manaphy", "Junk Arm", "Hero's Cape", "Rescue Carrier"]
    )
    me.active = _mon(me, "Mew ex")
    _zone(
        me,
        ["Rescue Carrier"],
        ["Junk Arm", "Igglybuff", "Igglybuff", "Manaphy", "Manaphy"],
        ["Hero's Cape"],
    )
    carrier = me.card(me.deck[0])
    assert carrier.name == "Rescue Carrier"
    carrier.text = NARROW_CARRIER
    assert (fallback_named("Manaphy").hp or 0) > 40
    fodder = [me.card(i).name for i in game._mew_junk_fodder(me)]
    assert fodder == ["Igglybuff", "Igglybuff"]
    game._play_trainers(me, foe, "a")
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert sum(me.card(i).name == "Manaphy" for i in me.hand) == 2
    assert sum(me.card(i).name == "Igglybuff" for i in me.discard) == 2


def test_narrow_carrier_does_not_spend_manaphy_without_a_stretcher():
    game, me, foe = _built(["Mew ex", "Manaphy", "Manaphy", "Junk Arm", "Hero's Cape", "Rescue Carrier"])
    me.active = _mon(me, "Mew ex")
    _zone(me, ["Rescue Carrier"], ["Junk Arm", "Manaphy", "Manaphy"], ["Hero's Cape"])
    me.card(me.deck[0]).text = NARROW_CARRIER
    assert game._mew_junk_plan(me, foe) is None
    game._play_trainers(me, foe, "a")
    assert me.active.tool is None
    assert sum(me.card(i).name == "Manaphy" for i in me.hand) == 2


def test_junk_arm_keeps_the_last_mew_ex():
    game, me, foe = _built(
        ["Mew ex", "Mew ex", "Junk Arm", "Hero's Cape", "Night Stretcher", "Hop", "Hop"]
    )
    _zone(me, ["Night Stretcher"], ["Junk Arm", "Mew ex", "Mew ex"], ["Hero's Cape"])
    assert len(game._mew_junk_fodder(me)) == 1
    assert game._mew_junk_plan(me, foe) is None
    game._play_trainers(me, foe, "a")
    assert sum(me.card(i).name == "Mew ex" for i in me.hand) == 2


def test_junk_arm_gusts_with_a_discarded_counter_catcher():
    game, me, foe = _built(
        [
            "Igglybuff",
            "Igglybuff",
            "Igglybuff",
            "Cleffa",
            "Cleffa",
            "Cleffa",
            "Mime Jr.",
            "Junk Arm",
            "Counter Catcher",
            "Rescue Carrier",
        ]
    )
    me.active = _mon(me, "Igglybuff")
    me.bench = [_mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Mime Jr.")]
    foe.bench = [_mon(foe, "Mew ex", 100)]
    _zone(
        me,
        ["Rescue Carrier", "Hop", "Hop", "Hop", "Hop", "Hop", "Hop", "Hop", "Hop"],
        ["Junk Arm", "Igglybuff", "Igglybuff"],
        ["Counter Catcher"],
    )
    me.prizes = [me.deck.pop() for _ in range(5)]
    foe.prizes = [foe.deck.pop() for _ in range(3)]
    assert any(me.card(i).name == "Rescue Carrier" for i in me.deck)
    assert game._mew_gust_plan(me, foe) is not None
    game._play_trainers(me, foe, "a")
    assert foe.card(foe.active.card_i).name == "Mew ex"
    assert game.events["junk_arm_into:Counter Catcher"] == 1


def test_item_lock_holds_junk_arm():
    game, me, foe = _built(
        ["Mew ex", "Igglybuff", "Igglybuff", "Junk Arm", "Hero's Cape", "Rescue Carrier"]
    )
    me.active = _mon(me, "Mew ex")
    _zone(me, ["Rescue Carrier"], ["Junk Arm", "Igglybuff", "Igglybuff"], ["Hero's Cape"])
    me.item_lock = True
    game._play_trainers(me, foe, "a")
    assert me.active.tool is None
    assert any(me.card(i).name == "Junk Arm" for i in me.hand)


def test_same_turn_carrier_returns_the_pitched_babies():
    game, me, foe = _built(
        ["Mew ex", "Igglybuff", "Igglybuff", "Cleffa", "Cleffa", "Cleffa", "Mime Jr.", "Manaphy", "Junk Arm", "Hero's Cape", "Rescue Carrier"]
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [
        _mon(me, "Cleffa"),
        _mon(me, "Cleffa"),
        _mon(me, "Cleffa"),
        _mon(me, "Mime Jr."),
        _mon(me, "Manaphy"),
    ]
    _zone(me, [], ["Junk Arm", "Igglybuff", "Igglybuff", "Rescue Carrier"], ["Hero's Cape"])
    game._play_trainers(me, foe, "a")
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert sum(me.card(i).name == "Igglybuff" for i in me.hand) == 2
    assert any(me.card(i).name == "Rescue Carrier" for i in me.discard)
    assert game.events["rescue_carrier"] == 2


def test_junk_search_starts_from_the_locked_four_petrel_list():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_m_junk_arm.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    label, names = module.starting_list()
    assert label == "Set M (4 Petrel, 3 Sky Field, 4 Budew)"
    assert names == list(SET_M60_NAMES)
    assert Counter(names)["Junk Arm"] == 0
    assert Counter(names)["Team Rocket's Petrel"] == 4
    swapped = module.swap_one(names, "Ultra Ball")
    assert len(swapped) == 60
    assert swapped.count("Junk Arm") == 1
