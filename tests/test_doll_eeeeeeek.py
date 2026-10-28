"""Cleffa uses Eeeeeeek when the doll supply is about to run out.

The attack still shuffles the hand and draws six. It is not a search. Life Dew
goes on the Cleffa that is sent up. Junk Hunt stays ahead of that switch.
Three replayable dolls in play, or two dolls already in hand, keep the strict rule.
"""

from random import Random

from app.engine.doll import (
    choose_attack,
    promote_rank,
    retreat,
    search_prefer,
    switch_idx,
    tool_host,
    wants_pokemon,
)
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


def _game(strat_b: str = "demolish") -> Game:
    pile = _cards(
        "Cleffa",
        "Cleffa",
        "Sableye",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Lillie's Poké Doll",
        "Team Rocket's Handiwork",
        "Arven",
        "Life Dew",
        "VS Seeker",
        "Darkness Energy",
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


def test_thin_board_sends_cleffa_up_and_screams():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Cleffa", "Lillie's Poké Doll"],
        hand=["Team Rocket's Handiwork", "Arven"],
        deck=["Lillie's Poké Doll"],
    )
    idx = switch_idx(game, me)
    assert idx is not None
    assert me.card(me.bench[idx].card_i).name == "Cleffa"
    dolls_before = sum(1 for i in me.deck if me.card(i).name == "Lillie's Poké Doll")
    retreat(game, me)
    assert me.card(me.active.card_i).name == "Cleffa"
    assert any(me.card(mon.card_i).name == "Lillie's Poké Doll" for mon in me.bench)
    dolls_after = sum(1 for i in me.deck if me.card(i).name == "Lillie's Poké Doll")
    assert dolls_after == dolls_before + 1
    atk = choose_attack(game, me, game.players["b"])
    assert atk is not None and atk.name == "Eeeeeeek"


def test_three_dolls_in_play_keep_the_strict_rule():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Lillie's Poké Doll", "Lillie's Poké Doll"],
        hand=["Team Rocket's Handiwork", "Arven"],
        deck=["Lillie's Poké Doll", "Cleffa"],
    )
    assert switch_idx(game, me) is None
    cleffa = next(i for i in me.deck if me.card(i).name == "Cleffa")
    me.deck.remove(cleffa)
    me.bench.append(me.active)
    me.active = Pokemon(card_i=cleffa)
    assert choose_attack(game, me, game.players["b"]) is None


def test_two_dolls_in_hand_do_not_send_cleffa_up():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Cleffa", "Lillie's Poké Doll"],
        hand=["Lillie's Poké Doll", "Lillie's Poké Doll", "Arven"],
        deck=["Lillie's Poké Doll"],
    )
    assert switch_idx(game, me) is None
    assert choose_attack(game, me, game.players["b"]) is None


def test_demolish_still_benches_cleffa_when_the_supply_is_low():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Lillie's Poké Doll"],
        hand=["Arven"],
        deck=["Cleffa", "Lillie's Poké Doll"],
    )
    cleffa = me.card(next(i for i in me.deck if me.card(i).name == "Cleffa"))
    assert wants_pokemon(game, me, cleffa) is True
    assert search_prefer(game, me)[0] == "Cleffa"


def test_life_dew_goes_on_the_cleffa_that_will_be_sent_up():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Cleffa",
        bench=["Sableye", "Lillie's Poké Doll"],
        hand=["Life Dew"],
        deck=["Lillie's Poké Doll"],
    )
    dew = me.card(next(i for i in me.hand if me.card(i).name == "Life Dew"))
    host = tool_host(game, me, dew)
    assert me.card(host.card_i).name == "Cleffa"


def test_the_last_doll_is_not_tucked_when_cleffa_would_be_left_alone():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Cleffa"],
        hand=["Team Rocket's Handiwork", "Arven"],
        deck=["Lillie's Poké Doll"],
    )
    retreat(game, me)
    assert me.card(me.active.card_i).name == "Lillie's Poké Doll"
    assert choose_attack(game, me, game.players["b"]) is None


def test_a_knock_out_promotes_awake_cleffa_ahead_of_a_doll():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Cleffa", "Lillie's Poké Doll"],
        hand=["Arven"],
        deck=["Lillie's Poké Doll"],
    )
    cleffa = next(i for i, mon in enumerate(me.bench) if me.card(mon.card_i).name == "Cleffa")
    doll = next(i for i, mon in enumerate(me.bench) if me.card(mon.card_i).name == "Lillie's Poké Doll")
    assert promote_rank(game, me, cleffa) < promote_rank(game, me, doll)


def test_scream_does_not_fire_when_cleffa_is_the_only_pokemon():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Team Rocket's Handiwork", "Arven"],
        deck=["Lillie's Poké Doll"],
    )
    assert switch_idx(game, me) is None
    assert choose_attack(game, me, game.players["b"]) is None


def test_empty_hand_still_screams_with_an_empty_bench():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=[],
        deck=["Darkness Energy"] * 6,
    )
    atk = choose_attack(game, me, game.players["b"])
    assert atk is not None and atk.name == "Eeeeeeek"


def test_junk_hunt_stays_ahead_of_the_scream():
    game = _game()
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        bench=["Cleffa", "Sableye"],
        hand=["Arven"],
        deck=["Lillie's Poké Doll"],
    )
    used: set[int] = set(me.hand + me.deck + [me.active.card_i] + [mon.card_i for mon in me.bench])
    dark = _take(game, "a", "Darkness Energy", used)
    doll_a = _take(game, "a", "Lillie's Poké Doll", used)
    doll_b = _take(game, "a", "Lillie's Poké Doll", used)
    sable = next(mon for mon in me.bench if me.card(mon.card_i).name == "Sableye")
    sable.energy = [dark]
    me.discard = [doll_a, doll_b]
    idx = switch_idx(game, me)
    assert idx is not None
    assert me.card(me.bench[idx].card_i).name == "Sableye"
    retreat(game, me)
    assert me.card(me.active.card_i).name == "Lillie's Poké Doll"
