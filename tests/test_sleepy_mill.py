"""Sleepy Voice on Mill and Celebi Mill.

Same benefit rule as Doll. Demolish spends the turn on the coin. Undersea
Tunnel, Sleepy Lost, Eeeeeeek, Playground, Time Distortion, and Kindling Panic
stay ahead against every other deck. A turn with none of those still flips
when the opponent's hit would land.
"""

from random import Random

from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named


class _Coin(Random):
    def __init__(self, value: float):
        super().__init__(1)
        self.value = value

    def random(self):
        return self.value


def _card(name: str):
    if name == "Cleffa":
        return fallback_named("cleffa hgss")
    if name == "Mime Jr.":
        return fallback_named("mime jr. col")
    if name == "Igglybuff":
        return fallback_named("igglybuff sleepy")
    return fallback_named(name)


def _cards(*names: str):
    out = [_card(name) for name in names]
    fillers = ("Water Energy", "Fire Energy", "Darkness Energy", "Fighting Energy")
    i = 0
    while len(out) < 60:
        out.append(fallback_named(fillers[i % 4]))
        i += 1
    return out


def _game(strat: str, foe: str, rng=None) -> Game:
    return Game(
        _cards(
            "Igglybuff",
            "Wiglett",
            "Wugtrio",
            "Pichu",
            "Cleffa",
            "Mime Jr.",
            "Celebi ◇",
            "Chandelure",
            "Litwick",
            "Litwick",
            "Litwick",
            "Litwick",
            "Victini",
        ),
        _cards("Dragapult ex", "Cornerstone Mask Ogerpon ex"),
        standard_60_rules(),
        StrategySpec.from_dict(strat),
        StrategySpec.from_dict(foe),
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


def _pay(player, names: list[str]) -> None:
    paid = []
    for name in names:
        idx = next(i for i in player.deck if player.card(i).name == name)
        player.deck.remove(idx)
        paid.append(idx)
    player.active.energy = paid


def test_undersea_stays_against_a_normal_knock_out():
    game = _game("mill", "phantom", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(me, ["Water Energy", "Water Energy", "Water Energy"])
    _pay(foe, ["Darkness Energy"])
    assert game._mill_plan_attack(me, foe) is True
    assert game._try_sleepy_voice(me, "a") is False
    assert not (foe.active.status & ST_ASLEEP)
    assert "sleepy_flip" not in game.events


def test_demolish_spends_undersea_on_the_coin():
    game = _game("mill", "demolish", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(
        game,
        "b",
        active="Cornerstone Mask Ogerpon ex",
        hand=[],
        deck=["Fighting Energy", "Water Energy", "Water Energy", "Water Energy"],
    )
    _pay(me, ["Water Energy", "Water Energy", "Water Energy"])
    _pay(foe, ["Fighting Energy", "Water Energy", "Water Energy"])
    assert game._mill_plan_attack(me, foe) is True
    assert game._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP
    assert game.turn_ended_by_ability
    assert game.events.get("sleepy_flip") == 1
    assert game.events.get("sleepy_heads") == 1


def test_headbutt_does_not_stay_ahead_of_the_coin():
    game = _game("mill", "phantom", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(me, ["Water Energy"])
    _pay(foe, ["Darkness Energy"])
    assert game._mill_plan_attack(me, foe) is False
    assert game._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP


def test_a_free_coin_when_mill_cannot_attack():
    game = _game("mill", "phantom", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(foe, ["Darkness Energy"])
    assert game._mill_plan_attack(me, foe) is False
    assert game._try_sleepy_voice(me, "a") is True


def test_no_flip_when_the_mill_opponent_cannot_attack():
    game = _game("mill", "phantom", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 4)
    assert game._try_sleepy_voice(me, "a") is False
    assert "sleepy_flip" not in game.events


def test_sleepy_lost_and_the_first_playground_stay():
    lost = _game("mill", "phantom", _Coin(0.0))
    lost.turn = 2
    me = _seat(
        lost,
        "a",
        active="Mime Jr.",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(lost, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(foe, ["Darkness Energy"])
    assert lost._mill_plan_attack(me, foe) is True
    assert lost._try_sleepy_voice(me, "a") is False

    play = _game("mill", "phantom", _Coin(0.0))
    play.turn = 2
    me = _seat(
        play,
        "a",
        active="Pichu",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(play, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(foe, ["Darkness Energy"])
    assert play._mill_plan_attack(me, foe) is True
    assert play._try_sleepy_voice(me, "a") is False
    play.events["used_playground_a"] = 1
    assert play._mill_plan_attack(me, foe) is False
    assert play._try_sleepy_voice(me, "a") is True


def test_one_igglybuff_and_poffin_order():
    game = _game("mill", "phantom")
    me = _seat(
        game,
        "a",
        active="Victini",
        hand=[],
        deck=["Igglybuff", "Wiglett", "Water Energy"],
    )
    iggly = next(card for card in me.cards if card.name == "Igglybuff" and card.catalog_id == "sm12-168")
    wiglett = next(card for card in me.cards if card.name == "Wiglett")
    assert game._wants_in_play(me, iggly, game.strats["a"]) is True
    assert game._mill_bench_search_score(me, wiglett) > game._mill_bench_search_score(me, iggly)
    me.bench.append(Pokemon(card_i=next(i for i in me.deck if me.card(i).name == "Wiglett")))
    me.deck = [i for i in me.deck if i != me.bench[0].card_i]
    assert game._mill_bench_search_score(me, iggly) > game._mill_bench_search_score(me, wiglett)
    prefer = game._pokemon_search_prefer(me, "a")
    assert prefer[0] == "Wugtrio"
    assert "Igglybuff" in prefer
    assert prefer.index("Wugtrio") < prefer.index("Igglybuff")
    iggly_i = next(i for i in me.deck if me.card(i).name == "Igglybuff")
    me.bench.append(Pokemon(card_i=iggly_i))
    assert game._wants_in_play(me, me.card(iggly_i), game.strats["a"]) is False


def test_time_distortion_stays_and_demolish_spends_it():
    stay = _game("roast", "phantom", _Coin(0.0))
    stay.turn = 2
    me = _seat(
        stay,
        "a",
        active="Celebi ◇",
        hand=[],
        deck=["Fire Energy"] * 8,
        bench=["Igglybuff", "Chandelure"],
    )
    foe = _seat(stay, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(me, ["Fire Energy"])
    _pay(foe, ["Darkness Energy"])
    assert stay._roast_plan_attack(me, foe, "a") is True
    assert stay._try_sleepy_voice(me, "a") is False

    spend = _game("roast", "demolish", _Coin(0.0))
    spend.turn = 2
    me = _seat(
        spend,
        "a",
        active="Celebi ◇",
        hand=[],
        deck=["Fire Energy", "Fighting Energy", "Water Energy", "Water Energy"],
        bench=["Igglybuff", "Chandelure"],
    )
    foe = _seat(
        spend,
        "b",
        active="Cornerstone Mask Ogerpon ex",
        hand=[],
        deck=["Fighting Energy", "Water Energy", "Water Energy", "Water Energy"],
    )
    _pay(me, ["Fire Energy"])
    _pay(foe, ["Fighting Energy", "Water Energy", "Water Energy"])
    assert spend._roast_plan_attack(me, foe, "a") is True
    assert spend._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP


def test_celebi_mill_flips_on_a_turn_that_cannot_mill():
    game = _game("roast", "phantom", _Coin(0.0))
    game.turn = 2
    me = _seat(
        game,
        "a",
        active="Celebi ◇",
        hand=[],
        deck=["Water Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Darkness Energy"] * 4)
    _pay(foe, ["Darkness Energy"])
    assert game._roast_plan_attack(me, foe, "a") is False
    assert game._try_sleepy_voice(me, "a") is True


def test_roast_benches_one_sleeper_after_three_lines():
    game = _game("roast", "phantom")
    me = _seat(
        game,
        "a",
        active="Water Energy",
        hand=["Pichu", "Litwick", "Litwick", "Litwick", "Litwick", "Igglybuff", "Celebi ◇"],
        deck=["Water Energy"] * 4,
    )
    me.active = None
    game._roast_bench(me, "a")
    play = [me.card(mon.card_i).name for mon in me.in_play()]
    assert play.count("Litwick") == 3
    assert play.count("Igglybuff") == 1
    assert me.card(me.active.card_i).name == "Pichu"
    assert "Celebi ◇" in play
    assert [me.card(i).name for i in me.hand] == ["Litwick"]
