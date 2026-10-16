"""Set M gusts only for a bigger Knock Out this turn, and pulls the Pokémon that gives it.

Boss's Orders and Counter Catcher both print "Switch in 1 of your opponent's Benched Pokémon to
the Active Spot." Counter Catcher adds "only if you have more Prize cards remaining than your
opponent". Neither card says anything about HP, so the lowest-HP Benched Pokémon is not the target.
"""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck

BOSS = "Switch in 1 of your opponent's Benched Pokémon to the Active Spot."
COUNTER_CATCHER = (
    "You can use this card only if you have more Prize cards remaining than your opponent.\n\n"
    "Switch in 1 of your opponent's Benched Pokémon to the Active Spot."
)

POOL = ["Mew ex", "Igglybuff", "Cleffa", "Mime Jr.", "Manaphy"] * 4 + ["Boss's Orders", "Counter Catcher"] * 2


def _game(strategy: str = "mew_baby") -> Game:
    def pad(names: list[str]) -> list[str]:
        out = list(names)
        while len(out) < 40:
            out.append("Nest Ball")
        return out

    return Game(
        build_fallback_deck(pad(POOL)),
        build_fallback_deck(pad(POOL)),
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
    player.active = None
    player.bench = []
    player.deck = sorted(set(player.deck))


def _mon(player, name: str, damage: int = 0) -> Pokemon:
    mon = Pokemon(card_i=_take(player, name), played_turn=0)
    mon.damage = damage
    return mon


def _board(foe_active: tuple[str, int], foe_bench: list[tuple[str, int]], strategy: str = "mew_baby"):
    """Igglybuff Active with four Benched 30 HP Pokémon: Bouncy Circle does 120."""
    game = _game(strategy)
    me, foe = game.players["a"], game.players["b"]
    _clear(me)
    _clear(foe)
    me.active = _mon(me, "Igglybuff")
    me.bench = [_mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Cleffa"), _mon(me, "Mime Jr.")]
    foe.active = _mon(foe, foe_active[0], foe_active[1])
    foe.bench = [_mon(foe, name, damage) for name, damage in foe_bench]
    return game, me, foe


def _name(player, mon) -> str:
    return player.card(mon.card_i).name


def _set_prizes(player, count: int) -> None:
    player.prizes = [player.deck.pop() for _ in range(count)]


def test_printed_wording_is_one_switch_in_hook_for_both_cards():
    boss = [e for e in parse_trainer_effects(BOSS) if e["kind"] == "force_opponent_active"]
    catcher = [e for e in parse_trainer_effects(COUNTER_CATCHER) if e["kind"] == "force_opponent_active"]
    assert len(boss) == len(catcher) == 1
    assert "max_remaining_hp" not in boss[0] and "max_remaining_hp" not in catcher[0]


def test_gust_pulls_the_two_prize_knock_out_not_the_lowest_hp_bench():
    game, me, foe = _board(("Manaphy", 0), [("Igglybuff", 0), ("Mew ex", 100)])
    assert _name(foe, game._hp_min_bench(foe)) == "Igglybuff"
    plan = game._mew_gust_plan(me, foe)
    assert plan is not None
    target, with_gust, without = plan
    assert _name(foe, target) == "Mew ex"
    assert (with_gust, without) == (2, 1)
    assert game._boss_pull_target(foe, me, "a") is target


def test_gust_is_scored_by_the_prizes_it_takes():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 100)])
    assert game._mew_gust_score(me, foe) == 30
    me.prizes_taken = 4
    assert game._mew_gust_score(me, foe) == 48


def test_no_gust_when_the_active_already_gives_the_same_prizes():
    game, me, foe = _board(("Mew ex", 100), [("Mew ex", 100), ("Igglybuff", 0)])
    assert game._mew_gust_plan(me, foe) is None
    assert game._mew_gust_score(me, foe) == -6
    me.hand = [_take(me, "Boss's Orders")]
    assert game._pick_trainer(me) is None


def test_no_gust_when_the_active_is_worth_more_than_anything_on_the_bench():
    game, me, foe = _board(("Mew ex", 100), [("Igglybuff", 0), ("Manaphy", 0)])
    assert game._mew_gust_plan(me, foe) is None


def test_no_gust_when_nothing_on_the_bench_can_be_knocked_out():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 0)])
    assert game._mew_gust_plan(me, foe) is None
    me.hand = [_take(me, "Boss's Orders")]
    assert game._pick_trainer(me) is None


def test_no_gust_once_the_active_already_takes_the_last_prize():
    game, me, foe = _board(("Mew ex", 100), [("Igglybuff", 0)])
    me.prizes_taken = 4
    assert game._mew_gust_plan(me, foe) is None


def test_boss_is_played_and_brings_the_planned_target_active():
    game, me, foe = _board(("Manaphy", 0), [("Igglybuff", 0), ("Mew ex", 100)])
    boss = _take(me, "Boss's Orders")
    me.hand = [boss]
    assert game._pick_trainer(me) == boss
    game._play_trainers(me, foe, "a")
    assert _name(foe, foe.active) == "Mew ex"
    assert boss in me.discard


def test_counter_catcher_needs_more_prizes_remaining_than_the_opponent():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 100)])
    catcher = _take(me, "Counter Catcher")
    me.hand = [catcher]
    _set_prizes(me, 4)
    _set_prizes(foe, 4)
    assert game._pick_trainer(me) is None
    _set_prizes(me, 5)
    assert game._pick_trainer(me) == catcher
    game._play_trainers(me, foe, "a")
    assert _name(foe, foe.active) == "Mew ex"


def test_counter_catcher_is_held_when_behind_but_the_gust_gains_nothing():
    game, me, foe = _board(("Mew ex", 100), [("Mew ex", 100)])
    me.hand = [_take(me, "Counter Catcher")]
    _set_prizes(me, 5)
    _set_prizes(foe, 3)
    assert game._pick_trainer(me) is None


def test_counter_catcher_goes_ahead_of_boss_for_the_same_pull():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 100)])
    boss = _take(me, "Boss's Orders")
    catcher = _take(me, "Counter Catcher")
    me.hand = [boss, catcher]
    _set_prizes(me, 5)
    _set_prizes(foe, 3)
    assert game._pick_trainer(me) == catcher
    game._play_trainers(me, foe, "a")
    assert _name(foe, foe.active) == "Mew ex"
    assert boss in me.hand


def test_benched_pokemon_only_strike_when_the_active_can_get_out_of_the_way():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 0)])
    me.active = _mon(me, "Manaphy")
    assert game._retreat_cost(me, me.active) == 1
    assert game._mew_strikers(me) == [me.active]
    me.active.energy.append(_take(me, "Mew ex"))
    assert game._mew_strikers(me) == [me.active, *me.bench]


def test_other_strategies_keep_the_lowest_hp_pull():
    game, me, foe = _board(("Manaphy", 0), [("Igglybuff", 0), ("Mew ex", 100)], strategy="thrifty")
    assert game._boss_pull_target(foe, me, "a") is game._hp_min_bench(foe)
    assert _name(foe, game._hp_min_bench(foe)) == "Igglybuff"


def test_gust_check_leaves_both_boards_as_they_were():
    game, me, foe = _board(("Manaphy", 0), [("Igglybuff", 0), ("Mew ex", 100)])
    mine = (me.active, list(me.bench))
    theirs = (foe.active, list(foe.bench))
    game._mew_gust_plan(me, foe)
    assert me.active is mine[0] and all(a is b for a, b in zip(me.bench, mine[1]))
    assert foe.active is theirs[0] and all(a is b for a, b in zip(foe.bench, theirs[1]))
