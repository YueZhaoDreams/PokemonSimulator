"""Plasma Storm Colress draws for each Benched Pokémon, then the hand is shuffled back.

Professor's Research discards the hand and draws 7. Colress does not discard those cards.
The draw count is the benches in play, both players, which Sky Field can raise to 8 each.
"""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_discard_hand_draw, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

COLRESS = (
    "Shuffle your hand into your deck. Then, draw a number of cards equal to the number of "
    "Benched Pokémon (both yours and your opponent\u2019s)."
)

POOL = (
    ["Mew ex", "Igglybuff", "Mime Jr.", "Budew", "Manaphy"] * 4
    + ["Colress", "Professor's Research", "Iono", "Team Rocket's Petrel", "Nest Ball"] * 4
    + ["Night Stretcher", "Crushing Hammer"]
    + ["Nest Ball"] * 20
)


def test_printed_sentence_counts_every_benched_pokemon():
    card = fallback_named("Colress")
    assert card.text == COLRESS
    assert card.is_supporter
    assert parse_trainer_effects(card.text) == [{"kind": "shuffle_hand_draw_per_bench", "whose": "both"}]
    assert parse_discard_hand_draw(fallback_named("Professor's Research").text) == 7
    opponent_only = (
        "Shuffle your hand into your deck. Then, draw a number of cards equal to the number of "
        "Benched Pokémon (your opponent's)."
    )
    assert parse_trainer_effects(opponent_only) == [{"kind": "shuffle_hand_draw_per_bench", "whose": "opponent"}]
    youngster = parse_trainer_effects("Shuffle your hand into your deck and draw 5 cards.")
    assert all(effect.get("kind") != "shuffle_hand_draw_per_bench" for effect in youngster)
    research = parse_trainer_effects("Discard your hand and draw 7 cards.")
    assert all(effect.get("kind") != "shuffle_hand_draw_per_bench" for effect in research)


def _game() -> Game:
    return Game(
        build_fallback_deck(list(POOL)),
        build_fallback_deck(list(POOL)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )


def _gather(player) -> None:
    for zone in (player.hand, player.discard, player.prizes):
        player.deck.extend(zone)
        zone.clear()
    for mon in player.in_play():
        player.deck.append(mon.card_i)
        player.deck.extend(mon.energy)
        if mon.tool is not None:
            player.deck.append(mon.tool)
    player.active = None
    player.bench = []
    player.deck = list(dict.fromkeys(player.deck))
    player.supporter_used = False


def _take(player, name: str) -> int:
    for card_i in list(player.deck):
        if player.card(card_i).name == name:
            player.deck.remove(card_i)
            return card_i
    raise AssertionError(name)


def _bench(player, names: list[str]) -> None:
    player.bench = [Pokemon(card_i=_take(player, name), played_turn=0) for name in names]


def _ready(game: Game, own: int, foe_n: int, hand: list[str]) -> tuple[object, object]:
    me = game.players["a"]
    foe = game.players["b"]
    _gather(me)
    _gather(foe)
    me.active = Pokemon(card_i=_take(me, "Mew ex"), played_turn=0)
    foe.active = Pokemon(card_i=_take(foe, "Mew ex"), played_turn=0)
    own_names = (["Igglybuff"] * 4 + ["Budew"] * 4 + ["Mime Jr."] * 4)[:own]
    foe_names = (["Igglybuff"] * 4 + ["Budew"] * 4 + ["Mime Jr."] * 4)[:foe_n]
    _bench(me, own_names)
    _bench(foe, foe_names)
    me.hand = [_take(me, name) for name in hand]
    return me, foe


def test_full_sky_field_benches_draw_sixteen_and_keep_the_hand():
    game = _game()
    me, foe = _ready(game, 8, 8, ["Colress", "Night Stretcher", "Crushing Hammer"])
    game._play_trainers(me, foe, "a")
    hand = [me.card(i).name for i in me.hand]
    discard = [me.card(i).name for i in me.discard]
    assert len(hand) == 16
    assert discard == ["Colress"]
    assert "Night Stretcher" not in discard
    assert "Crushing Hammer" not in discard
    assert game.events["shuffle_hand_draw_per_bench_a"] == 1
    assert game.events["colress_drawn_a"] == 16


def test_small_bench_plays_research_and_a_wide_bench_plays_colress():
    game = _game()
    me, foe = _ready(game, 1, 1, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Professor's Research"

    game = _game()
    me, foe = _ready(game, 4, 4, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Colress"


def test_one_or_two_short_of_research_only_when_the_hand_would_be_discarded():
    game = _game()
    me, foe = _ready(game, 3, 3, ["Colress", "Professor's Research", "Nest Ball", "Nest Ball", "Nest Ball"])
    picked = game._pick_trainer(me)
    assert me.card(picked).name == "Colress"

    game = _game()
    me, foe = _ready(game, 3, 3, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert me.card(picked).name == "Professor's Research"


def test_petrel_fetches_colress_once_the_benches_reach_research():
    game = _game()
    me, foe = _ready(game, 4, 4, ["Team Rocket's Petrel"])
    me.deck = [_take(me, name) for name in ("Colress", "Iono", "Professor's Research")]
    assert game._mew_petrel_collapse(me, foe)[1] == "colress"

    game = _game()
    me, foe = _ready(game, 1, 1, ["Team Rocket's Petrel"])
    me.deck = [_take(me, name) for name in ("Colress", "Iono", "Professor's Research")]
    assert game._mew_petrel_collapse(me, foe)[1] == "iono"
