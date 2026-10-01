"""One Mew ex in play. A second copy stays in hand so the bench can be 30 HP babies.

Bouncy Circle does 30 damage for each benched Pokémon with a maximum HP of 30.
Mew ex retreats for 0. The flag stays off unless a strategy turns it on.
"""

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.montecarlo import _apply_queries
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def _strat(one_mew: bool) -> StrategySpec:
    data = StrategySpec.from_dict("mew_baby").to_dict()
    data["one_mew"] = one_mew
    return StrategySpec.from_dict(data)


def _game(one_mew: bool) -> Game:
    names = ["Mew ex", "Mew ex", "Igglybuff", "Igglybuff", "Mime Jr.", "Nest Ball", "Night Stretcher"]
    names += ["Hop"] * (60 - len(names))
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dondozo"] * 60),
        standard_60_rules(),
        _strat(one_mew),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def _add(player, name: str) -> int:
    player.cards.append(fallback_named(name))
    return len(player.cards) - 1


def _fill(game: Game, hand: list[str]) -> None:
    me = game.players["a"]
    me.active = None
    me.bench = []
    me.deck = []
    me.discard = []
    me.prizes = []
    me.hand = [_add(me, name) for name in hand]


def _names(player, idxs) -> list[str]:
    return [player.card(i).name for i in idxs]


def test_opening_keeps_the_second_mew_in_hand():
    game = _game(True)
    me = game.players["a"]
    me.hand = []
    me.deck = []
    me.prizes = []
    me.active = None
    me.bench = []
    # _draw pops the end of the deck. The opening hand is these seven cards.
    opening = ["Mew ex", "Mew ex", "Igglybuff", "Igglybuff", "Hop", "Hop", "Hop"]
    me.deck = [_add(me, "Hop") for _ in range(53)]
    me.deck.extend(_add(me, name) for name in reversed(opening))
    game.rng.shuffle = lambda _seq: None
    game._opening(me, game.strats["a"])
    assert me.card(me.active.card_i).name == "Mew ex"
    benched = [me.card(mon.card_i).name for mon in me.bench]
    assert benched.count("Mew ex") == 0
    assert benched.count("Igglybuff") == 2
    assert [me.card(i).name for i in me.hand].count("Mew ex") == 1


def test_one_mew_leaves_the_spare_in_hand_and_benches_babies():
    game = _game(True)
    me = game.players["a"]
    _fill(game, ["Mew ex", "Mew ex", "Igglybuff", "Igglybuff"])
    game._play_basics(me)
    assert me.card(me.active.card_i).name == "Mew ex"
    assert _names(me, [mon.card_i for mon in me.bench]) == ["Igglybuff", "Igglybuff"]
    assert _names(me, me.hand) == ["Mew ex"]


def test_old_board_benches_the_second_mew():
    game = _game(False)
    me = game.players["a"]
    _fill(game, ["Mew ex", "Mew ex", "Igglybuff", "Igglybuff"])
    game._play_basics(me)
    assert me.card(me.active.card_i).name == "Mew ex"
    assert _names(me, [mon.card_i for mon in me.bench]).count("Mew ex") == 1
    assert _names(me, [mon.card_i for mon in me.bench]).count("Igglybuff") == 2
    assert me.hand == []


def test_one_mew_plays_the_spare_after_the_first_leaves_play():
    game = _game(True)
    me = game.players["a"]
    _fill(game, ["Mew ex", "Mew ex", "Igglybuff"])
    game._play_basics(me)
    spare = me.hand[0]
    me.hand.append(me.active.card_i)
    me.active = me.bench.pop(0)
    game._play_basics(me)
    assert me.card(me.active.card_i).name == "Igglybuff"
    assert any(mon.card_i == spare and me.card(mon.card_i).name == "Mew ex" for mon in me.bench)


def test_night_stretcher_takes_a_baby_while_a_mew_is_in_play():
    game = _game(True)
    me = game.players["a"]
    mew = _add(me, "Mew ex")
    iggly = _add(me, "Igglybuff")
    spare = _add(me, "Mew ex")
    me.active = Pokemon(card_i=mew)
    me.bench = []
    me.hand = []
    me.deck = []
    me.discard = [spare, iggly]
    game._night_stretcher(me, "a")
    assert me.hand == [iggly]
    assert spare in me.discard


def test_night_stretcher_takes_mew_when_none_is_in_play():
    game = _game(True)
    me = game.players["a"]
    baby = _add(me, "Igglybuff")
    mew = _add(me, "Mew ex")
    iggly = _add(me, "Igglybuff")
    me.active = Pokemon(card_i=baby)
    me.bench = []
    me.hand = []
    me.deck = []
    me.discard = [iggly, mew]
    game._night_stretcher(me, "a")
    assert me.hand == [mew]


def test_nest_ball_does_not_bench_a_second_mew():
    game = _game(True)
    me = game.players["a"]
    mew = _add(me, "Mew ex")
    spare = _add(me, "Mew ex")
    iggly = _add(me, "Igglybuff")
    me.active = Pokemon(card_i=mew)
    me.bench = []
    me.hand = []
    me.discard = []
    me.deck = [spare, iggly]
    game._bench_basic_from_deck(me, "a", source="nest ball")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Igglybuff"]
    assert spare in me.deck


def test_nest_ball_leaves_the_bench_slot_empty_when_only_a_second_mew_remains():
    game = _game(True)
    me = game.players["a"]
    mew = _add(me, "Mew ex")
    spare = _add(me, "Mew ex")
    me.active = Pokemon(card_i=mew)
    me.bench = []
    me.hand = []
    me.discard = []
    me.deck = [spare]
    game._bench_basic_from_deck(me, "a", source="nest ball")
    assert me.bench == []
    assert me.deck == [spare]


def test_event_sum_adds_the_bench_count():
    class Result:
        opening_a: list[str] = []
        opening_b: list[str] = []
        events = {"bench30_sum_a": 12, "bench30_n_a": 3, "two_mew_a": 1}

    hits: dict[str, int] = {}
    _apply_queries(
        Result(),
        [
            {"type": "event_sum", "prefix": "bench30_sum_a", "key": "bench_sum"},
            {"type": "event_prefix", "prefix": "two_mew_a", "key": "two_mew"},
        ],
        hits,
    )
    assert hits == {"bench_sum": 12, "two_mew": 1}
