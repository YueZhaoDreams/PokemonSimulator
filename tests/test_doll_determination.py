"""Lillie's Determination on Doll.

Printed text shuffles the hand into the deck, draws 6, and draws 8 instead
when exactly 6 Prize cards remain. Doll plays it when the hand has no
replayable doll and the deck still has one. Arven, Petrel, and Handiwork
outrank that redraw. Petrel still takes the doll.
"""

from random import Random

from app.engine.doll import trainer_score
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named

_TEXT = (
    "Shuffle your hand into your deck. Then, draw 6 cards. "
    "If you have exactly 6 Prize cards remaining, draw 8 cards instead."
)


class _Still(Random):
    def shuffle(self, seq, random=None):
        return None


def _cards(*names: str):
    out = [fallback_named(name) for name in names]
    while len(out) < 60:
        out.append(fallback_named("Darkness Energy"))
    return out


def _game(rng=None) -> Game:
    pile = _cards(
        "Cleffa",
        "Lillie's Determination",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Cursed Shovel",
        "Life Dew",
        "Arven",
        "Team Rocket's Petrel",
        "Team Rocket's Handiwork",
        "Field Blower",
        "Puzzle of Time",
        "Puzzle of Time",
    )
    return Game(
        pile,
        _cards("Cleffa"),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict("balanced"),
        rng or Random(1),
    )


def _take(game: Game, who: str, name: str, used: set[int]) -> int:
    player = game.players[who]
    for i, card in enumerate(player.cards):
        if i in used or card.name != name:
            continue
        used.add(i)
        return i
    raise AssertionError(name)


def _seat(
    game: Game,
    who: str,
    *,
    active: str,
    hand: list[str],
    deck: list[str],
    bench: list[str] | None = None,
):
    used: set[int] = set()
    player = game.players[who]
    player.active = Pokemon(card_i=_take(game, who, active, used))
    player.bench = [Pokemon(card_i=_take(game, who, name, used)) for name in (bench or [])]
    player.hand = [_take(game, who, name, used) for name in hand]
    player.deck = [_take(game, who, name, used) for name in deck]
    player.discard = []
    player.prizes = []
    return player, used


def _names(game: Game, who: str, idxs) -> list[str]:
    player = game.players[who]
    return [player.card(i).name for i in idxs]


def _total(game: Game, me, foe, card) -> float:
    generic = 9 if len(me.hand) <= 5 else 5
    return generic + trainer_score(game, me, foe, card)


def test_printed_sentence():
    card = fallback_named("Lillie's Determination")
    assert card.catalog_id == "me01-119"
    assert card.trainer_kind == "supporter"
    assert card.text == _TEXT


def test_score_digs_only_when_the_dolls_are_running_out():
    game = _game()
    me, used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination"],
        deck=["Lillie's Poké Doll", "Lillie's Poké Doll"] + ["Darkness Energy"] * 6,
    )
    foe = game.players["b"]
    det = me.hand[0]
    assert _total(game, me, foe, me.card(det)) == 11

    me.hand = [det, *[_take(game, "a", "Darkness Energy", used) for _ in range(5)]]
    # The six-card hand still has no doll. The generic bonus drops from 9 to 5.
    assert len(me.hand) == 6
    assert _total(game, me, foe, me.card(det)) == 11

    # Two dolls in hand is the replacement pair. The redraw stays down.
    dolls = [i for i in me.deck if me.card(i).name == "Lillie's Poké Doll"]
    me.hand = [det, dolls[0], dolls[1]]
    me.deck = [i for i in me.deck if i not in set(dolls)]
    assert trainer_score(game, me, foe, me.card(det)) == -30

    # Three dolls already in play keep the strict line, even with an empty hand.
    third = _take(game, "a", "Lillie's Poké Doll", used)
    fourth = _take(game, "a", "Lillie's Poké Doll", used)
    me.hand = [det]
    me.bench = [Pokemon(card_i=dolls[0]), Pokemon(card_i=dolls[1]), Pokemon(card_i=third)]
    me.deck = [fourth]
    assert trainer_score(game, me, foe, me.card(det)) == -30


def test_redraws_six_and_plays_the_doll_it_draws():
    game = _game(_Still(1))
    me, _used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination", "Field Blower"],
        deck=["Darkness Energy"] * 12 + ["Lillie's Poké Doll"],
    )
    deck_n = len(me.deck)
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("doll_determination") == 1
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.in_play())
    assert len(me.deck) == deck_n + 1 - 6
    assert me.supporter_used


def test_exactly_six_prizes_draws_eight():
    game = _game(_Still(1))
    me, used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination", "Field Blower"],
        deck=["Darkness Energy"] * 12 + ["Lillie's Poké Doll"],
    )
    prizes = []
    for i, card in enumerate(me.cards):
        if i in used or card.name != "Darkness Energy":
            continue
        used.add(i)
        prizes.append(i)
        if len(prizes) == 6:
            break
    me.prizes = prizes
    deck_n = len(me.deck)
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("doll_determination") == 1
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.in_play())
    assert len(me.deck) == deck_n + 1 - 8


def test_a_stocked_board_plays_the_doll_and_keeps_the_redraw():
    game = _game()
    me, _used = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        hand=["Lillie's Determination", "Lillie's Poké Doll"],
        deck=["Lillie's Poké Doll"],
        bench=["Lillie's Poké Doll", "Lillie's Poké Doll"],
    )
    game._play_trainers(me, game.players["b"], "a")
    assert "doll_determination" not in game.events
    assert "Lillie's Determination" in _names(game, "a", me.hand)
    assert sum(1 for mon in me.in_play() if me.card(mon.card_i).name == "Lillie's Poké Doll") == 4
    assert not me.supporter_used


def test_arven_outranks_the_redraw_and_takes_the_doll():
    game = _game()
    me, _used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination", "Arven"],
        deck=["Lillie's Poké Doll", "Cursed Shovel"],
    )
    game._play_trainers(me, game.players["b"], "a")
    assert "arven" in game.events
    assert "doll_determination" not in game.events
    assert "Lillie's Determination" in _names(game, "a", me.hand)
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.in_play())


def test_handiwork_yields_and_life_dew_attaches_before_the_redraw():
    game = _game(_Still(1))
    me, _used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination", "Team Rocket's Handiwork", "Life Dew"],
        deck=["Darkness Energy"] * 12 + ["Lillie's Poké Doll"],
    )
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("doll_determination") == 1
    assert me.active is not None and me.active.tool is not None
    assert me.card(me.active.tool).name == "Life Dew"
    assert "Team Rocket's Handiwork" not in _names(game, "a", me.discard)


def test_petrel_takes_the_doll_ahead_of_determination():
    game = _game()
    me, _used = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Team Rocket's Petrel"],
        deck=["Lillie's Determination", "Lillie's Poké Doll"],
    )
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("petrel_into:Lillie's Poké Doll") == 1
    assert "Lillie's Determination" in _names(game, "a", me.deck)
    assert "doll_determination" not in game.events
