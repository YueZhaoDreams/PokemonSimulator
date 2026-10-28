"""Arven and Team Rocket's Petrel on Doll.

One Supporter is played. Arven takes an Item and a Pokémon Tool. When the hand
has no doll, that Item is a doll. Petrel takes the one Trainer the position is
missing. The other Supporter stays in hand.
"""

from random import Random

from app.engine.doll import trainer_score
from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named


def _cards(*names: str):
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        else:
            out.append(fallback_named(name))
    while len(out) < 60:
        out.append(fallback_named("Darkness Energy"))
    return out


def _game(strat_b: str = "balanced") -> Game:
    pile = _cards(
        "Cleffa",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Robo Substitute Team Flare Gear",
        "Cursed Shovel",
        "Life Dew",
        "Battle Cage",
        "Team Rocket's Handiwork",
        "Arven",
        "Team Rocket's Petrel",
        "VS Seeker",
        "Puzzle of Time",
    )
    return Game(
        pile,
        _cards("Cleffa"),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict(strat_b),
        Random(1),
    )


def _take(game: Game, who: str, name: str, used: set[int]) -> int:
    player = game.players[who]
    for i, card in enumerate(player.cards):
        if i in used or card.name != name:
            continue
        used.add(i)
        return i
    raise AssertionError(name)


def _seat(game: Game, who: str, *, active: str, hand: list[str], deck: list[str], bench: list[str] | None = None):
    used: set[int] = set()
    player = game.players[who]
    player.active = Pokemon(card_i=_take(game, who, active, used))
    player.bench = [Pokemon(card_i=_take(game, who, name, used)) for name in (bench or [])]
    player.hand = [_take(game, who, name, used) for name in hand]
    player.deck = [_take(game, who, name, used) for name in deck]
    player.discard = []
    player.prizes = []
    return player


def _names(game: Game, who: str, idxs) -> list[str]:
    player = game.players[who]
    return [player.card(i).name for i in idxs]


def test_printed_sentences():
    arven = fallback_named("Arven")
    petrel = fallback_named("Team Rocket's Petrel")
    assert "Item" in arven.text and "Pokémon Tool" in arven.text
    assert parse_trainer_effects(petrel.text) == [{"kind": "search_trainer"}]
    assert "Trainer card" in petrel.text


def test_arven_takes_a_doll_and_a_shovel_then_plays_the_doll():
    game = _game()
    _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Arven", "Team Rocket's Petrel"],
        deck=["Lillie's Poké Doll", "Cursed Shovel", "Life Dew", "Team Rocket's Handiwork"],
    )
    game._play_trainers(game.players["a"], game.players["b"], "a")
    me = game.players["a"]
    assert "arven" in game.events
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.in_play())
    assert any(mon.tool is not None and me.card(mon.tool).name == "Cursed Shovel" for mon in me.in_play())
    assert "Team Rocket's Petrel" in _names(game, "a", me.hand)
    assert me.supporter_used


def test_arven_leaves_the_doll_in_the_deck_when_the_hand_already_has_one():
    game = _game()
    _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Arven", "Lillie's Poké Doll"],
        deck=["Robo Substitute Team Flare Gear", "Life Dew", "Puzzle of Time"],
        bench=["Lillie's Poké Doll"] * 5,
    )
    game._play_trainers(game.players["a"], game.players["b"], "a")
    me = game.players["a"]
    assert "arven" in game.events
    assert "Robo Substitute Team Flare Gear" in _names(game, "a", me.deck)
    assert "Life Dew" in _names(game, "a", me.hand) or any(
        mon.tool is not None and me.card(mon.tool).name == "Life Dew" for mon in me.in_play()
    )


def test_petrel_takes_the_doll_ahead_of_battle_cage():
    game = _game("phantom")
    _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Team Rocket's Petrel", "Team Rocket's Handiwork"],
        deck=["Lillie's Poké Doll", "Battle Cage"],
    )
    game._play_trainers(game.players["a"], game.players["b"], "a")
    me = game.players["a"]
    assert game.events.get("petrel_into:Lillie's Poké Doll") == 1
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.in_play())
    assert "Battle Cage" in _names(game, "a", me.deck)
    assert "Team Rocket's Handiwork" in _names(game, "a", me.hand)


def test_petrel_takes_battle_cage_when_a_doll_is_already_in_hand():
    game = _game("phantom")
    _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Team Rocket's Petrel", "Lillie's Poké Doll"],
        deck=["Battle Cage", "Team Rocket's Handiwork"],
    )
    game._play_trainers(game.players["a"], game.players["b"], "a")
    assert game.events.get("petrel_into:Battle Cage") == 1
    assert game.stadium_name == "Battle Cage"


def test_handiwork_plays_when_petrel_would_only_find_arven():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Team Rocket's Petrel", "Team Rocket's Handiwork", "Lillie's Poké Doll"],
        deck=["Arven"],
        bench=["Lillie's Poké Doll"],
    )
    foe = game.players["b"]
    petrel = next(i for i in me.hand if me.card(i).name == "Team Rocket's Petrel")
    handiwork = next(i for i in me.hand if me.card(i).name == "Team Rocket's Handiwork")
    assert trainer_score(game, me, foe, me.card(handiwork)) > trainer_score(game, me, foe, me.card(petrel))


def test_arven_outranks_handiwork_when_the_hand_has_no_doll():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Arven", "Team Rocket's Handiwork"],
        deck=["Lillie's Poké Doll", "Cursed Shovel"],
    )
    foe = game.players["b"]
    arven = next(i for i in me.hand if me.card(i).name == "Arven")
    handiwork = next(i for i in me.hand if me.card(i).name == "Team Rocket's Handiwork")
    # The picker also adds 6 to Arven before this score.
    assert trainer_score(game, me, foe, me.card(arven)) + 6 > trainer_score(game, me, foe, me.card(handiwork))
