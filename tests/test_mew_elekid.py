"""Elekid in Set M: one more 30 HP Baby, and a finisher that is used only for an extreme Knock Out.

Elekid (Paradox Rift 59) prints "Crackling Shot", no Energy cost: "This attack does 30 damage to 1 of
your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)"
Mew ex's Memory Helix lets it use the attacks of any Benched Pokémon, so Mew ex copies it and stays Active.
Elekid itself goes Active only when Mew ex cannot use the attack and the Knock Out is extreme:
it wins the game, or it takes at least 2 prizes the Active attack cannot.
"""

from __future__ import annotations

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck

POOL = ["Mew ex", "Igglybuff", "Cleffa", "Mime Jr.", "Manaphy", "Elekid", "Budew"] * 4 + [
    "Boss's Orders",
    "Counter Catcher",
] * 2
FOE_POOL = POOL + ["Iron Thorns ex"]


def _game(strategy: str = "mew_baby", mine: list[str] | None = None) -> Game:
    def pad(names: list[str]) -> list[str]:
        out = list(names)
        while len(out) < 40:
            out.append("Nest Ball")
        return out

    return Game(
        build_fallback_deck(pad(mine if mine is not None else POOL)),
        build_fallback_deck(pad(FOE_POOL)),
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


def _name(player, mon) -> str:
    return player.card(mon.card_i).name


def _board(
    foe_active: tuple[str, int],
    foe_bench: list[tuple[str, int]],
    active: str = "Mew ex",
    bench: tuple[str, ...] = ("Elekid", "Igglybuff", "Igglybuff", "Cleffa"),
    mine: list[str] | None = None,
):
    """Mew ex Active, Elekid and three more 30 HP Babies on the Bench: Bouncy Circle copies for 120."""
    game = _game(mine=mine)
    me, foe = game.players["a"], game.players["b"]
    _clear(me)
    _clear(foe)
    me.active = _mon(me, active)
    me.bench = [_mon(me, name) for name in bench]
    foe.active = _mon(foe, foe_active[0], foe_active[1])
    foe.bench = [_mon(foe, name, damage) for name, damage in foe_bench]
    return game, me, foe


def _attack_names(game: Game, me, mon) -> list[str]:
    return [atk.name for atk in game._attacks_for(me, mon)]


def test_elekid_counts_for_bouncy_circle_and_mew_copies_its_hit():
    game, me, foe = _board(("Mew ex", 0), [("Mew ex", 0)])
    names = _attack_names(game, me, me.active)
    assert "Crackling Shot" in names and "Bouncy Circle" in names
    bouncy = next(a for a in game._attacks_for(me, me.active) if a.name == "Bouncy Circle")
    assert game._effective_damage(me, foe, bouncy) == 120
    assert game._snipe_amount(me, foe) == 30


def test_crackling_shot_hits_one_pokemon_once():
    game, me, foe = _board(("Mime Jr.", 0), [("Mew ex", 130)], active="Elekid", bench=("Igglybuff",))
    me.prizes = [me.deck.pop() for _ in range(6)]
    game._attack(me, foe, "a")
    assert [mon.damage for mon in foe.in_play()] == [0, 160]
    assert sum(mon.damage for mon in foe.in_play()) == 160


def test_snipe_takes_the_two_prize_bench_knock_out_over_a_one_prize_active():
    game, me, foe = _board(("Mime Jr.", 0), [("Igglybuff", 0), ("Mew ex", 130)])
    target, prizes = game._snipe_pick(me, foe, 30)
    assert (_name(foe, target), prizes) == ("Mew ex", 2)


def test_snipe_takes_the_active_on_a_tie_of_prizes():
    game, me, foe = _board(("Cleffa", 0), [("Igglybuff", 0)])
    target, prizes = game._snipe_pick(me, foe, 30)
    assert target is foe.active and prizes == 1


def test_snipe_finds_no_knock_out_when_everything_has_more_than_thirty_left():
    game, me, foe = _board(("Mew ex", 0), [("Mew ex", 100)])
    assert game._snipe_pick(me, foe, 30) is None


def test_snipe_skips_a_bench_that_wave_veil_protects():
    game, me, foe = _board(("Mew ex", 0), [("Manaphy", 0), ("Mew ex", 130)])
    assert game._snipe_pick(me, foe, 30) is None


def test_snipe_applies_weakness_to_the_active_only():
    game, me, foe = _board(("Manaphy", 0), [("Mew ex", 0)], active="Elekid", bench=("Igglybuff",))
    assert [w["type"] for w in foe.card(foe.active.card_i).weaknesses] == ["Lightning"]
    assert game._snipe_damage_on(me, foe, foe.active, 30) == 60
    assert game._snipe_damage_on(me, foe, foe.bench[0], 30) == 30


def test_cruel_arrow_keeps_its_target_and_crackling_shot_takes_the_bigger_knock_out():
    game, me, foe = _board(("Mew ex", 0), [("Igglybuff", 0), ("Mew ex", 70)])
    game._damage_one_pokemon(me, foe, 100)
    assert [mon.damage for mon in foe.in_play()] == [0, 100, 70]
    game, me, foe = _board(("Mime Jr.", 0), [("Igglybuff", 0), ("Mew ex", 130)])
    game._damage_one_pokemon(me, foe, 30, finisher=True)
    assert [mon.damage for mon in foe.in_play()] == [0, 0, 160]


def test_the_snipe_knock_out_replaces_the_gust():
    game, me, foe = _board(("Mew ex", 0), [("Mew ex", 130)])
    assert game._mew_strike_prizes(me, foe, game._mew_strikers(me)) == 2
    assert game._mew_gust_plan(me, foe) is None
    assert game._mew_gust_score(me, foe) == -6


def test_a_one_prize_snipe_does_not_replace_the_gust():
    game, me, foe = _board(("Mew ex", 0), [("Igglybuff", 0), ("Mew ex", 40)])
    assert game._snipe_pick(me, foe, 30)[1] == 1
    assert game._mew_strike_prizes(me, foe, game._mew_strikers(me)) == 0
    plan = game._mew_gust_plan(me, foe)
    assert plan is not None
    target, with_gust, without = plan
    assert (_name(foe, target), with_gust, without) == ("Mew ex", 2, 0)


def test_without_elekid_the_same_board_needs_the_gust():
    game, me, foe = _board(("Mew ex", 0), [("Mew ex", 130)], bench=("Cleffa", "Igglybuff", "Igglybuff", "Cleffa"))
    assert not game._has_snipe(me)
    plan = game._mew_gust_plan(me, foe)
    assert plan is not None and (_name(foe, plan[0]), plan[1], plan[2]) == ("Mew ex", 2, 0)
    assert game._snipe_holder(me, foe) is None


def test_mew_ex_copies_the_extreme_knock_out_and_elekid_stays_benched():
    game, me, foe = _board(("Mime Jr.", 0), [("Igglybuff", 0), ("Mew ex", 130)])
    assert game._mew_can_crackling(me, foe)
    assert game._snipe_holder(me, foe) is None
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mew ex"
    assert "Elekid" in [_name(me, m) for m in me.bench]
    atk = game._choose_attack(me, foe, game.strats["a"])
    assert atk.name == "Crackling Shot"
    me.prizes = [me.deck.pop() for _ in range(6)]
    game._attack(me, foe, "a")
    assert game._check_ko(foe, me, "b") is False
    assert me.prizes_taken == 2
    assert [_name(foe, m) for m in foe.in_play()] == ["Mime Jr.", "Igglybuff"]


def test_a_one_prize_bench_knock_out_does_not_use_crackling_shot():
    game, me, foe = _board(("Mew ex", 0), [("Igglybuff", 0)])
    assert game._snipe_pick(me, foe, 30) == (foe.bench[0], 1)
    assert game._snipe_holder(me, foe) is None
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mew ex"
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Bouncy Circle"
    assert game._mew_strike_prizes(me, foe, game._mew_strikers(me)) == 0


def test_crackling_shot_is_used_when_the_one_prize_knock_out_wins_the_game():
    game, me, foe = _board(("Mew ex", 0), [("Igglybuff", 0)])
    me.prizes_taken = 5
    assert game._snipe_holder(me, foe) is None
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mew ex"
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Crackling Shot"
    assert game._mew_strike_prizes(me, foe, game._mew_strikers(me)) == 1
    assert game._mew_gust_plan(me, foe) is None


def test_elekid_passes_when_its_only_knock_out_is_not_extreme():
    game, me, foe = _board(("Mew ex", 0), [("Igglybuff", 0)], active="Elekid", bench=("Igglybuff",))
    assert game._snipe_holder(me, foe) is None
    assert game._choose_attack(me, foe, game.strats["a"]) is None


def test_mew_ex_stays_active_when_bouncy_circle_takes_the_same_prizes():
    game, me, foe = _board(("Mime Jr.", 0), [("Igglybuff", 0), ("Mew ex", 100)])
    assert game._snipe_holder(me, foe) is None
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Mew ex"
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Bouncy Circle"


def test_bouncy_circle_knock_out_beats_a_smaller_bench_snipe():
    game, me, foe = _board(("Mew ex", 40), [("Igglybuff", 0)])
    assert game._snipe_pick(me, foe, 30)[1] == 1
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Bouncy Circle"


def test_snipe_is_chosen_for_the_prizes_when_mew_ex_is_the_only_attacker():
    game, me, foe = _board(("Mime Jr.", 0), [("Mew ex", 130)], bench=("Elekid",))
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Crackling Shot"


def test_iron_thorns_lock_puts_elekid_in_front_for_a_bench_knock_out():
    game, me, foe = _board(
        ("Iron Thorns ex", 0),
        [("Mew ex", 130)],
        bench=("Budew", "Elekid", "Igglybuff", "Cleffa"),
    )
    assert game._rulebox_lock_on_opponent(me)
    assert not game._mew_can_crackling(me, foe)
    assert "Crackling Shot" not in _attack_names(game, me, me.active)
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Elekid"
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Crackling Shot"


def test_iron_thorns_lock_does_not_put_elekid_in_front_for_a_one_prize_snipe():
    game, me, foe = _board(
        ("Iron Thorns ex", 0),
        [("Igglybuff", 0)],
        bench=("Budew", "Elekid", "Cleffa"),
    )
    assert game._snipe_pick(me, foe, 30)[1] == 1
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Budew"


def test_iron_thorns_lock_puts_elekid_in_front_when_the_snipe_wins_the_game():
    game, me, foe = _board(
        ("Iron Thorns ex", 0),
        [("Igglybuff", 0)],
        bench=("Budew", "Elekid", "Cleffa"),
    )
    me.prizes_taken = 5
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Elekid"
    assert game._choose_attack(me, foe, game.strats["a"]).name == "Crackling Shot"


def test_iron_thorns_lock_keeps_budew_in_front_without_a_knock_out():
    game, me, foe = _board(
        ("Iron Thorns ex", 0),
        [("Mew ex", 0)],
        bench=("Budew", "Elekid", "Cleffa"),
    )
    game._retreat_baby(me, foe, "a")
    assert _name(me, me.active) == "Budew"


def test_search_asks_for_elekid_only_when_the_list_plays_it():
    game, me, _foe = _board(("Mew ex", 0), [], bench=("Igglybuff",))
    assert "Elekid" in game._pokemon_search_prefer(me, "a")
    plain = _game(mine=[n for n in POOL if n != "Elekid"])
    me2 = plain.players["a"]
    assert "Elekid" not in plain._pokemon_search_prefer(me2, "a")


def test_elekid_is_a_baby_for_recovery():
    game, me, _foe = _board(("Mew ex", 0), [], bench=("Igglybuff",))
    me.discard.extend([_take(me, "Cleffa"), _take(me, "Elekid")])
    game._night_stretcher(me, "a")
    assert [me.card(i).name for i in me.hand] == ["Elekid"]
    me.hand.clear()
    me.discard.extend([_take(me, "Cleffa"), _take(me, "Elekid")])
    game._rescue_carrier(me, "a", 1, 30)
    assert [me.card(i).name for i in me.hand] == ["Elekid"]


def test_elekid_ranks_as_a_baby_wall_and_promotes_after_igglybuff():
    game, me, _foe = _board(("Mew ex", 0), [], active="Igglybuff", bench=("Elekid", "Igglybuff"))
    assert game._baby_wall_rank(me.card(me.bench[0].card_i)) < 9
    me.active = None
    assert me.bench and _name(me, me.bench[game._promote_idx(me, "a")]) == "Igglybuff"


def test_elekid_is_a_starter_after_cleffa_and_before_igglybuff():
    game = _game()
    me = game.players["a"]
    basics = [_take(me, "Igglybuff"), _take(me, "Elekid"), _take(me, "Manaphy")]
    assert me.card(game._pick_starter(me, basics, game.strats["a"])).name == "Elekid"
