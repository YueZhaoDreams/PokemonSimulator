"""Team Rocket's Petrel on the Mew list collapses into the Trainer that list would play next.

Printed sentence: search the deck for a Trainer, reveal it, put it into the hand, shuffle.
An Item, Tool, or Stadium is played in the same turn. A Supporter stays for the next turn.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from random import Random

import pytest

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import Card, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck, fallback_named

PETREL = (
    "Search your deck for a Trainer card, reveal it, and put it into your hand. Then, shuffle your deck."
)
SKY_FIELD = (
    "Each player can have 8 Pokémon on his or her Bench. "
    "(When this card leaves play, each player discards Benched Pokémon until he or she has 5 Pokémon "
    "on the Bench. The owner of this card discards first.)"
)

POOL = (
    ["Mew ex", "Igglybuff", "Cleffa", "Mime Jr.", "Manaphy"] * 4
    + ["Team Rocket's Petrel", "Boss's Orders", "Counter Catcher", "Buddy-Buddy Poffin"] * 2
    + ["Max Potion", "Hero's Cape", "Bravery Charm", "Battle Cage", "Arven", "Penny", "Psychic Energy"]
    + ["Hop"] * 8
)


def _pad(names: list[str]) -> list[str]:
    out = list(names)
    while len(out) < 40:
        out.append("Hop")
    return out


def _game(strategy: str = "mew_baby") -> Game:
    return Game(
        build_fallback_deck(_pad(POOL)),
        build_fallback_deck(_pad(POOL)),
        standard_60_rules(),
        StrategySpec.from_dict(strategy),
        StrategySpec.from_dict("thrifty"),
        Random(1),
    )


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


def _fresh(strategy: str = "mew_baby"):
    game = _game(strategy)
    me, foe = game.players["a"], game.players["b"]
    _clear(me)
    _clear(foe)
    foe.active = _mon(foe, "Manaphy")
    return game, me, foe


def _set_prizes(player, count: int) -> None:
    player.prizes = [player.deck.pop() for _ in range(count)]


def _built(names: list[str], foe_names: list[str] | None = None):
    """A cleared board whose deck contains these names, plus a live foe Active."""

    def pad(seq: list[str]) -> list[str]:
        out = list(seq)
        while len(out) < 40:
            out.append("Hop")
        return out

    game = Game(
        build_fallback_deck(pad(names)),
        build_fallback_deck(pad(foe_names or ["Igglybuff", "Manaphy"])),
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


def _zone(me, deck: list[str], hand: list[str]) -> tuple[list[int], list[int]]:
    """Leave only these cards in deck and hand. Names are taken before the zones are replaced."""
    deck_i = [_take(me, name) for name in deck]
    hand_i = [_take(me, name) for name in hand]
    me.deck = deck_i
    me.hand = hand_i
    me.discard = []
    return deck_i, hand_i


def test_printed_petrel_searches_any_trainer():
    card = fallback_named("Team Rocket's Petrel")
    assert card.text == PETREL
    assert card.trainer_kind == "supporter"
    assert parse_trainer_effects(card.text) == [{"kind": "search_trainer"}]
    text = StrategySpec.from_dict("mew_baby").description
    for sentence in (
        "Team Rocket's Petrel",
        "Buddy-Buddy Poffin",
        "Max Potion",
        "Counter Catcher",
        "Hero's Cape",
        "Sky Field",
        "Area Zero Underdepths",
        "Arven cannot fetch a Stadium",
    ):
        assert sentence in text


def test_petrel_benches_two_basics_from_poffin_when_the_bench_is_open():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex")
    _zone(me, ["Buddy-Buddy Poffin", "Igglybuff", "Igglybuff"], ["Team Rocket's Petrel"])
    assert game._mew_petrel_collapse(me, foe) == (25, "buddy-buddy poffin")
    game.strats["a"] = StrategySpec.from_dict("baby")
    assert game._mew_petrel_collapse(me, foe)[1] == "buddy-buddy poffin"
    game.strats["a"] = StrategySpec.from_dict("mew_baby")
    game._play_trainers(me, foe, "a")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Igglybuff", "Igglybuff"]
    assert all((me.card(mon.card_i).hp or 0) <= 70 for mon in me.bench)
    assert game.events["petrel_into:Buddy-Buddy Poffin"] == 1


def test_petrel_heals_with_max_potion_ahead_of_poffin():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex", damage=40)
    _zone(
        me,
        ["Max Potion", "Buddy-Buddy Poffin", "Igglybuff", "Igglybuff"],
        ["Team Rocket's Petrel"],
    )
    assert game._mew_petrel_collapse(me, foe) == (30, "max potion")
    game._play_trainers(me, foe, "a")
    assert me.active.damage == 0
    assert me.bench == []
    assert game.events["max_potion"] == 1
    assert game.events["petrel_into:Max Potion"] == 1


def test_potion_already_in_hand_is_played_and_petrel_stays():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex", damage=40)
    _deck, hand = _zone(me, [], ["Team Rocket's Petrel", "Max Potion"])
    petrel, potion = hand
    assert game._pick_trainer(me) == potion
    game._play_trainers(me, foe, "a")
    assert me.active.damage == 0
    assert petrel in me.hand
    assert "petrel" not in game.events


def test_arven_in_hand_fetches_the_potion_and_petrel_stays():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex", damage=40)
    _deck, hand = _zone(me, ["Max Potion", "Bravery Charm"], ["Team Rocket's Petrel", "Arven"])
    petrel, arven = hand
    assert game._pick_trainer(me) == arven
    game._play_trainers(me, foe, "a")
    assert me.active.damage == 0
    assert petrel in me.hand
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Bravery Charm"


def test_petrel_gusts_with_counter_catcher_when_boss_is_not_in_hand():
    game, me, foe = _fresh()
    me.active = _mon(me, "Igglybuff")
    me.bench = [_mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Mime Jr.")]
    foe.bench = [_mon(foe, "Igglybuff"), _mon(foe, "Mew ex", 100)]
    _take(me, "Boss's Orders")
    catcher = _take(me, "Counter Catcher")
    petrel = _take(me, "Team Rocket's Petrel")
    _set_prizes(me, 5)
    _set_prizes(foe, 3)
    me.deck = [catcher]
    me.hand = [petrel]
    me.discard = []
    assert game._mew_gust_plan(me, foe) is not None
    assert game._mew_petrel_collapse(me, foe)[1] == "counter catcher"
    game._play_trainers(me, foe, "a")
    assert foe.card(foe.active.card_i).name == "Mew ex"
    assert game.events["petrel_into:Counter Catcher"] == 1
    assert game.events["counter_catcher"] == 1


def test_boss_already_in_hand_gusts_and_petrel_stays():
    game, me, foe = _fresh()
    me.active = _mon(me, "Igglybuff")
    me.bench = [_mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Mime Jr.")]
    foe.bench = [_mon(foe, "Mew ex", 100)]
    boss = _take(me, "Boss's Orders")
    petrel = _take(me, "Team Rocket's Petrel")
    catcher = _take(me, "Counter Catcher")
    _set_prizes(me, 5)
    _set_prizes(foe, 3)
    me.deck = [catcher]
    me.hand = [boss, petrel]
    me.discard = []
    assert game._pick_trainer(me) == boss
    game._play_trainers(me, foe, "a")
    assert foe.card(foe.active.card_i).name == "Mew ex"
    assert petrel in me.hand
    assert catcher in me.deck


def test_petrel_holds_boss_for_next_turn_when_catcher_cannot_be_played():
    game, me, foe = _fresh()
    me.active = _mon(me, "Igglybuff")
    me.bench = [
        _mon(me, "Cleffa"),
        _mon(me, "Cleffa"),
        _mon(me, "Cleffa"),
        _mon(me, "Mime Jr."),
        _mon(me, "Igglybuff"),
    ]
    foe.bench = [_mon(foe, "Mew ex", 100)]
    game.stadium_name = "Battle Cage"
    boss = _take(me, "Boss's Orders")
    petrel = _take(me, "Team Rocket's Petrel")
    hops = [_take(me, "Hop") for _ in range(4)]
    _set_prizes(me, 3)
    _set_prizes(foe, 3)
    me.deck = [boss]
    me.hand = [petrel, *hops]
    me.discard = []
    assert game._mew_petrel_collapse(me, foe)[1] == "boss's orders"
    active_before = foe.active
    game._play_trainers(me, foe, "a")
    assert foe.active is active_before
    assert boss in me.hand
    assert game.events["petrel_into:Boss's Orders"] == 1


def test_petrel_attaches_cape_when_that_stops_the_knock_out():
    game, me, foe = _fresh()
    mew = _mon(me, "Mew ex", damage=80)
    mew.energy.append(_take(me, "Psychic Energy"))
    me.active = mew
    foe.active = _mon(foe, "Igglybuff")
    foe.bench = [_mon(foe, "Cleffa"), _mon(foe, "Cleffa"), _mon(foe, "Cleffa"), _mon(foe, "Mime Jr.")]
    _zone(
        me,
        ["Hero's Cape", "Buddy-Buddy Poffin", "Bravery Charm", "Igglybuff", "Igglybuff"],
        ["Team Rocket's Petrel"],
    )
    collapse = game._mew_petrel_collapse(me, foe)
    assert collapse == (46, "hero's cape")
    game._play_trainers(me, foe, "a")
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert me.active.damage == 80
    assert game.events["petrel_into:Hero's Cape"] == 1


def test_arven_keeps_the_cape_that_stops_the_knock_out():
    game, me, foe = _fresh()
    mew = _mon(me, "Mew ex", damage=80)
    mew.energy.append(_take(me, "Psychic Energy"))
    me.active = mew
    foe.active = _mon(foe, "Igglybuff")
    foe.bench = [_mon(foe, "Cleffa"), _mon(foe, "Cleffa"), _mon(foe, "Cleffa"), _mon(foe, "Mime Jr.")]
    _deck, hand = _zone(me, ["Hero's Cape"], ["Team Rocket's Petrel", "Arven"])
    petrel, arven = hand
    assert game._pick_trainer(me) == arven
    game._play_trainers(me, foe, "a")
    assert petrel in me.hand
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Hero's Cape"


def test_petrel_finds_penny_when_manaphy_is_active():
    game, me, foe = _fresh()
    me.active = _mon(me, "Manaphy")
    me.bench = [
        _mon(me, "Igglybuff"),
        _mon(me, "Igglybuff"),
        _mon(me, "Cleffa"),
        _mon(me, "Cleffa"),
        _mon(me, "Mime Jr."),
    ]
    game.stadium_name = "Battle Cage"
    foe.bench = []
    penny = _take(me, "Penny")
    petrel = _take(me, "Team Rocket's Petrel")
    hops = [_take(me, "Hop") for _ in range(4)]
    me.deck = [penny]
    me.hand = [petrel, *hops]
    me.discard = []
    assert game._mew_petrel_collapse(me, foe) == (9, "penny")
    game._play_trainers(me, foe, "a")
    assert penny in me.hand
    assert me.card(me.active.card_i).name == "Manaphy"
    assert game.events["petrel_into:Penny"] == 1


def test_item_lock_plays_battle_cage_and_leaves_poffin_in_the_deck():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex")
    me.item_lock = True
    _deck, _hand = _zone(
        me,
        ["Buddy-Buddy Poffin", "Battle Cage", "Igglybuff", "Igglybuff"],
        ["Team Rocket's Petrel"],
    )
    poffin = _deck[0]
    assert game._mew_petrel_collapse(me, foe) == (15, "battle cage")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Battle Cage"
    assert poffin in me.deck
    assert game.events["petrel_into:Battle Cage"] == 1


def test_item_lock_holds_poffin_until_the_next_turn():
    game, me, foe = _fresh()
    me.active = _mon(me, "Mew ex")
    me.item_lock = True
    game.stadium_name = "Battle Cage"
    _deck, _hand = _zone(me, ["Buddy-Buddy Poffin", "Igglybuff", "Igglybuff"], ["Team Rocket's Petrel"])
    poffin = _deck[0]
    assert game._mew_petrel_collapse(me, foe) == (9, "buddy-buddy poffin")
    game._play_trainers(me, foe, "a")
    assert me.bench == []
    assert poffin in me.hand
    assert game.events["petrel_into:Buddy-Buddy Poffin"] == 1


def test_petrel_plays_sky_field_then_the_poffin_that_was_waiting():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Sky Field", "Battle Cage", "Buddy-Buddy Poffin"] + ["Igglybuff"] * 8
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Igglybuff") for _ in range(5)]
    sky = _take(me, "Sky Field")
    cage = _take(me, "Battle Cage")
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [sky, cage, *babies]
    me.hand = [petrel, poffin]
    me.discard = []
    assert me.card(sky).text == SKY_FIELD
    assert game._mew_bench_raise_gain(me, me.card(sky)) == 2
    assert game._mew_stadium_score(me, me.card(sky)) == 30
    assert game._mew_petrel_collapse(me, foe) == (30, "sky field")
    assert game._pick_trainer(me) == petrel
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Sky Field"
    assert game._bench_limit(me) == 8
    assert len(me.bench) == 7
    assert cage in me.deck
    assert poffin not in me.hand
    assert game.events["petrel_into:Sky Field"] == 1


def test_petrel_still_takes_sky_field_when_arven_is_in_hand():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Sky Field", "Buddy-Buddy Poffin", "Arven"] + ["Igglybuff"] * 8
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Igglybuff") for _ in range(5)]
    sky = _take(me, "Sky Field")
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    arven = _take(me, "Arven")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [sky, *babies]
    me.hand = [petrel, poffin, arven]
    me.discard = []
    assert game._mew_arven_score(me, foe) < 30
    assert game._pick_trainer(me) == petrel
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Sky Field"
    assert len(me.bench) == 7
    assert arven in me.hand


def test_arven_keeps_the_knock_out_save_ahead_of_sky_field():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Sky Field", "Buddy-Buddy Poffin", "Arven", "Hero's Cape", "Psychic Energy"]
        + ["Igglybuff"] * 8,
        foe_names=["Igglybuff"] * 8,
    )
    mew = _mon(me, "Mew ex", damage=80)
    mew.energy.append(_take(me, "Psychic Energy"))
    me.active = mew
    me.bench = [_mon(me, "Igglybuff") for _ in range(5)]
    foe.active = _mon(foe, "Igglybuff")
    foe.bench = [_mon(foe, "Igglybuff") for _ in range(4)]
    sky = _take(me, "Sky Field")
    cape = _take(me, "Hero's Cape")
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    arven = _take(me, "Arven")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [sky, cape, *babies]
    me.hand = [petrel, poffin, arven]
    me.discard = []
    assert game._mew_stadium_score(me, me.card(sky)) == 30
    assert game._mew_arven_score(me, foe) == 46
    assert game._pick_trainer(me) == arven
    game._play_trainers(me, foe, "a")
    assert petrel in me.hand
    assert sky in me.deck
    assert me.active.tool is not None
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert game.stadium_name is None


def test_petrel_takes_poffin_when_sky_field_adds_no_baby():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Sky Field", "Buddy-Buddy Poffin"] + ["Igglybuff"] * 6
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Igglybuff") for _ in range(3)]
    sky = _take(me, "Sky Field")
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [sky, poffin, *babies]
    me.hand = [petrel]
    me.discard = []
    assert game._mew_bench_raise_gain(me, me.card(sky)) == 0
    assert game._mew_stadium_score(me, me.card(sky)) == -20
    assert game._mew_petrel_collapse(me, foe) == (25, "buddy-buddy poffin")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name is None
    assert sky in me.deck
    assert len(me.bench) == 5


def test_petrel_reads_the_printed_bench_sentence_on_any_stadium():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Buddy-Buddy Poffin"] + ["Igglybuff"] * 8
    )
    wider = Card(
        catalog_id="sky-alt",
        name="Wide Bench",
        category="Trainer",
        trainer_kind="stadium",
        text=SKY_FIELD.replace("have 8", "have 7").replace("has 5", "has 4"),
        retreat=0,
    )
    wider_i = len(me.cards)
    me.cards.append(wider)
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Igglybuff") for _ in range(5)]
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [wider_i, *babies]
    me.hand = [petrel, poffin]
    me.discard = []
    assert game._mew_bench_raise_gain(me, wider) == 2
    assert game._mew_petrel_collapse(me, foe) == (30, "wide bench")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Wide Bench"
    assert game._bench_limit(me) == 7
    assert len(me.bench) == 7


def test_item_lock_plays_sky_field_and_holds_the_poffin():
    game, me, foe = _built(
        ["Mew ex", "Team Rocket's Petrel", "Sky Field", "Buddy-Buddy Poffin"] + ["Igglybuff"] * 8
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Igglybuff") for _ in range(5)]
    me.item_lock = True
    sky = _take(me, "Sky Field")
    poffin = _take(me, "Buddy-Buddy Poffin")
    petrel = _take(me, "Team Rocket's Petrel")
    babies = [_take(me, "Igglybuff") for _ in range(2)]
    me.deck = [sky, *babies]
    me.hand = [petrel, poffin]
    me.discard = []
    assert game._mew_petrel_collapse(me, foe) == (30, "sky field")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Sky Field"
    assert game._bench_limit(me) == 8
    assert len(me.bench) == 5
    assert poffin in me.hand


def test_petrel_plays_area_zero_when_the_burst_is_ready():
    game, me, foe = _built(
        ["Mew ex", "Terapagos ex", "Team Rocket's Petrel", "Area Zero Underdepths", "Battle Cage"]
        + ["Igglybuff"] * 6
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Terapagos ex")] + [_mon(me, "Igglybuff") for _ in range(4)]
    game.turn = 6
    area = _take(me, "Area Zero Underdepths")
    cage = _take(me, "Battle Cage")
    petrel = _take(me, "Team Rocket's Petrel")
    me.deck = [area, cage]
    me.hand = [petrel]
    me.discard = []
    assert game._player_has_tera(me)
    assert game._mew_burst_ready(me, holding=True)
    assert game._mew_petrel_collapse(me, foe) == (32, "area zero underdepths")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Area Zero Underdepths"
    assert cage in me.deck
    assert game.events["petrel_into:Area Zero Underdepths"] == 1


def test_petrel_leaves_area_zero_until_the_burst_is_ready():
    game, me, foe = _built(
        ["Mew ex", "Terapagos ex", "Team Rocket's Petrel", "Area Zero Underdepths", "Battle Cage"]
        + ["Igglybuff"] * 6
    )
    me.active = _mon(me, "Mew ex")
    me.bench = [_mon(me, "Terapagos ex")] + [_mon(me, "Igglybuff") for _ in range(4)]
    game.turn = 0
    area = _take(me, "Area Zero Underdepths")
    cage = _take(me, "Battle Cage")
    petrel = _take(me, "Team Rocket's Petrel")
    me.deck = [area, cage]
    me.hand = [petrel]
    me.discard = []
    assert game._mew_burst_ready(me, holding=True) is False
    assert game._mew_stadium_score(me, me.card(area)) == -20
    assert game._mew_petrel_collapse(me, foe) == (15, "battle cage")
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Battle Cage"
    assert area in me.deck


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_m_petrel.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_petrel_swap_keeps_sixty_cards_and_stops_at_four():
    lab = _load_lab()
    historical = json.loads(
        (Path(__file__).resolve().parents[1] / "data" / "lab" / "set-m-sky-field.json").read_text()
    )["report"]["list_start"]
    names = list(historical)
    assert names.count("Team Rocket's Petrel") == 0
    swapped = lab.swap_one(names, "Night Stretcher")
    assert len(swapped) == 60
    assert swapped.count("Team Rocket's Petrel") == 1
    assert swapped.count("Night Stretcher") == names.count("Night Stretcher") - 1
    four = names
    for cut in ("Boss's Orders", "Bravery Charm", "Counter Catcher", "Ultra Ball"):
        four = lab.swap_one(four, cut)
    assert four.count("Team Rocket's Petrel") == 4
    with pytest.raises(ValueError):
        lab.swap_one(four, "Arven")


def test_petrel_search_starts_from_the_four_sky_field_list():
    lab = _load_lab()
    label, names = lab.starting_list()
    assert label == "Start (4 Sky Field, 4 Budew)"
    assert len(names) == 60
    assert names.count("Sky Field") == 4
    assert names.count("Budew") == 4
    assert names.count("Team Rocket's Petrel") == 0
    assert names.count("Boss's Orders") == 0
    assert Counter(names) != Counter(SET_M60_NAMES)


def test_petrel_report_is_the_finished_four_sky_field_search():
    lab = _load_lab()
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set-m-petrel.json"
    report = json.loads(path.read_text())["report"]
    label, names = lab.starting_list()
    assert report["done"] is True
    assert report["start_label"] == label == "Start (4 Sky Field, 4 Budew)"
    assert report["list_start"] == names
    assert report["copies"] == 4
    assert [row["cut"] for row in report["array"][1:]] == ["Ultra Ball", "Penny", "Penny", "Sky Field"]
    final = Counter(report["list"])
    assert len(report["list"]) == 60
    assert final["Team Rocket's Petrel"] == 4
    assert final["Sky Field"] == 3
    assert final["Budew"] == 4
    assert final["Penny"] == 0
    assert final["Ultra Ball"] == 1
    assert copy_violations(build_fallback_deck(report["list"]), standard_60_rules()) == []
    hold = {row["copies"]: row for row in report["holdout"]}
    weights = report["weights"]
    _delta, _se, z40 = lab._pair(hold[4], hold[0], weights)
    _delta, _se, z43 = lab._pair(hold[4], hold[3], weights)
    assert z40 == pytest.approx(2.73, abs=0.01)
    assert z43 < 2
    text = path.with_suffix(".md").read_text()
    assert text == lab.render_md(report)
    assert "## Result" in text
    assert "2.73 standard errors" in text
    assert "0.266" in text
    assert "locked as `SET_M60_NAMES`" in text
    assert final["Junk Arm"] == 0
    live = Counter(SET_M60_NAMES)
    walked = list(report["list"])
    walked[walked.index("Ultra Ball")] = "Junk Arm"
    walked[walked.index("Battle Cage")] = "Elekid"
    walked[walked.index("Crushing Hammer")] = "Colress"
    walked[walked.index("Crushing Hammer")] = "Penny"
    assert Counter(walked) == live
    assert copy_violations(build_fallback_deck(list(SET_M60_NAMES)), standard_60_rules()) == []


def test_aura_petrel_still_takes_boss_ahead_of_an_item():
    game, me, _foe = _fresh("aura")
    boss = _take(me, "Boss's Orders")
    poffin = _take(me, "Buddy-Buddy Poffin")
    me.deck = [poffin, boss]
    me.hand = []
    me.discard = []
    game._search_trainer(me, "a")
    assert [me.card(i).name for i in me.hand] == ["Boss's Orders"]
