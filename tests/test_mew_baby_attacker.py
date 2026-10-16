"""Set M puts the Baby that hits hardest in the Active Spot, not the one with the Item lock.

Budew's Itchy Pollen chips for 10 and locks Items. Igglybuff's Bouncy Circle does 30 for each
Benched Pokémon with a maximum HP of 30. Both numbers come from the printed attack text.
"""

from __future__ import annotations

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck


def _game(a_names: list[str], b_names: list[str]) -> Game:
    def pad(names: list[str]) -> list[str]:
        out = list(names)
        while len(out) < 40:
            out.append("Nest Ball")
        return out

    return Game(
        build_fallback_deck(pad(a_names)),
        build_fallback_deck(pad(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
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


POOL = ["Mew ex", "Budew", "Igglybuff", "Cleffa", "Mime Jr."] * 6


def _board(active: str | None, bench: list[str], foe_active: str = "Igglybuff"):
    game = _game(POOL, POOL + ["Iron Thorns ex"])
    me, foe = game.players["a"], game.players["b"]
    _clear(me)
    _clear(foe)
    if active is not None:
        me.active = Pokemon(card_i=_take(me, active), played_turn=0)
    for name in bench:
        me.bench.append(Pokemon(card_i=_take(me, name), played_turn=0))
    foe.active = Pokemon(card_i=_take(foe, foe_active), played_turn=0)
    return game, me, foe


def _name(me, mon) -> str:
    return me.card(mon.card_i).name


def test_printed_damage_of_each_baby_from_the_active_spot():
    game, me, foe = _board("Budew", ["Igglybuff", "Mime Jr.", "Cleffa", "Cleffa"])
    budew, iggly, mime, *_ = me.active, *me.bench
    assert game._baby_damage_if_active(me, foe, budew) == 10
    assert game._baby_damage_if_active(me, foe, iggly) == 30 * 4
    assert game._baby_damage_if_active(me, foe, mime) == 0


def test_damage_check_leaves_the_board_as_it_was():
    game, me, foe = _board("Budew", ["Igglybuff", "Mime Jr.", "Cleffa"])
    before = (me.active, list(me.bench))
    for mon in me.in_play():
        game._baby_damage_if_active(me, foe, mon)
    assert me.active is before[0]
    assert all(a is b for a, b in zip(me.bench, before[1])) and len(me.bench) == len(before[1])

    game, me, foe = _board(None, ["Budew", "Igglybuff", "Cleffa"])
    bench = list(me.bench)
    game._baby_damage_if_active(me, foe, bench[1])
    assert me.active is None
    assert all(a is b for a, b in zip(me.bench, bench))


def test_budew_gives_way_to_igglybuff_without_a_mew_ex():
    game, me, foe = _board("Budew", ["Igglybuff", "Mime Jr.", "Cleffa"])
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Igglybuff"
    assert "Budew" in [_name(me, mon) for mon in me.bench]


def test_budew_gives_way_to_igglybuff_under_the_rule_box_lock():
    game, me, foe = _board("Budew", ["Igglybuff", "Cleffa"], foe_active="Iron Thorns ex")
    assert game._rulebox_lock_on_opponent(me)
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Igglybuff"


def test_budew_stays_when_no_baby_hits_harder():
    game, me, foe = _board("Budew", ["Mime Jr.", "Cleffa"])
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Budew"

    game, me, foe = _board("Budew", ["Mime Jr.", "Cleffa"], foe_active="Iron Thorns ex")
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Budew"


def test_a_benched_mew_ex_still_takes_the_active_spot():
    game, me, foe = _board("Budew", ["Igglybuff", "Mew ex"])
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mew ex"


def test_lists_without_budew_keep_their_baby_in_front():
    game, me, foe = _board("Mime Jr.", ["Igglybuff", "Cleffa"])
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mime Jr."


def test_promotion_takes_the_harder_hitting_baby_over_budew():
    game, me, _foe = _board(None, ["Budew", "Igglybuff", "Mime Jr."])
    assert _name(me, me.bench[game._promote_idx(me, "a")]) == "Igglybuff"

    game, me, _foe = _board(None, ["Budew", "Mime Jr."])
    assert _name(me, me.bench[game._promote_idx(me, "a")]) == "Budew"

    game, me, _foe = _board(None, ["Budew", "Igglybuff", "Cleffa"], foe_active="Iron Thorns ex")
    assert game._rulebox_lock_on_opponent(me)
    assert _name(me, me.bench[game._promote_idx(me, "a")]) == "Igglybuff"

    game, me, _foe = _board(None, ["Budew", "Cleffa", "Mime Jr."], foe_active="Iron Thorns ex")
    assert _name(me, me.bench[game._promote_idx(me, "a")]) == "Budew"


def test_spiky_energy_goes_to_the_baby_that_will_attack():
    game, me, _foe = _board("Budew", ["Igglybuff", "Cleffa"])
    target = game._mew_counter_energy_target(me)
    assert _name(me, target) == "Igglybuff"

    game, me, _foe = _board("Budew", ["Igglybuff", "Cleffa"], foe_active="Iron Thorns ex")
    assert _name(me, game._mew_counter_energy_target(me)) == "Igglybuff"

    game, me, _foe = _board("Budew", ["Cleffa"])
    assert _name(me, game._mew_counter_energy_target(me)) == "Budew"


def test_locked_set_m_list_has_no_budew():
    assert "Budew" not in SET_M60_NAMES
