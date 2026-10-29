"""Sleepy Voice on Mill, using Doll's benefit rule.

Printed text (Cosmic Eclipse 168): once during your turn, before your attack,
you may flip a coin. Heads, the opponent's Active Pokémon is now Asleep. If
you use this Ability, your turn ends. It does not say the Active Spot, so a
Benched copy can use it. Undersea Tunnel, Playground, Sleepy Lost, and
Eeeeeeek stay ahead of the coin. The coin replaces that attack only when the
hit ignores effects on the Active, as Demolish does.
"""

from random import Random

from app.engine.game import ST_ASLEEP, Game, Pokemon, play_game
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_D60_NAMES, SET_MILL_NAMES, build_fallback_deck, fallback_named, mill_named


_TEXT = (
    "Once during your turn (before your attack), you may flip a coin. "
    "If heads, your opponent's Active Pokémon is now Asleep. "
    "If you use this Ability, your turn ends."
)


class _Coin(Random):
    def __init__(self, value: float):
        super().__init__(1)
        self.value = value

    def random(self):
        return self.value


def _cards(*names: str):
    out = [mill_named(name) for name in names]
    while len(out) < 60:
        out.append(fallback_named("Water Energy"))
    return out


def _game(foe: str = "balanced", rng=None, extra: list[str] | None = None) -> Game:
    ours = [
        "Wiglett",
        "Wugtrio",
        "Pichu",
        "Igglybuff",
        "Manaphy",
        "Cleffa",
        "Level Ball",
        "Water Energy",
        "Water Energy",
        "Water Energy",
        "Fighting Energy",
    ]
    if foe == "demolish":
        theirs = ["Cornerstone Mask Ogerpon ex", "Fighting Energy"]
    else:
        theirs = ["Dragapult ex"]
    return Game(
        _cards(*(ours + (extra or []))),
        _cards(*theirs),
        standard_60_rules(),
        StrategySpec.from_dict("mill"),
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


def _ready(game: Game) -> None:
    game.turn = 4
    game.first = "b"


def test_mill_print_is_sleepy_voice_and_the_lock_has_zero():
    sleepy = mill_named("Igglybuff")
    assert sleepy.catalog_id == "sm12-168"
    assert sleepy.abilities[0].text == _TEXT
    assert SET_MILL_NAMES.count("Igglybuff") == 0
    assert fallback_named("Igglybuff").attacks[0].name == "Bouncy Circle"


def test_demolish_spends_undersea_on_the_coin():
    game = _game("demolish", _Coin(0.0))
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy", "Water Energy", "Water Energy", "Water Energy"],
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
    attack = game._choose_attack(me, foe, game.strats["a"])
    assert attack is not None and attack.name == "Undersea Tunnel"
    assert game._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP
    assert me.bench[0].ability_used
    assert game.turn_ended_by_ability
    assert game.events.get("mill_sleepy_flip") == 1
    assert game.events.get("mill_sleepy_heads") == 1


def test_undersea_stays_against_a_normal_hit():
    game = _game("phantom", _Coin(0.0))
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy", "Water Energy", "Water Energy", "Water Energy"],
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Water Energy", "Water Energy"])
    _pay(me, ["Water Energy", "Water Energy", "Water Energy"])
    _pay(foe, ["Water Energy"])
    attack = game._choose_attack(me, foe, game.strats["a"])
    assert attack is not None and attack.name == "Undersea Tunnel"
    assert game._try_sleepy_voice(me, "a") is False
    assert "mill_sleepy_flip" not in game.events
    assert not game.turn_ended_by_ability


def test_playground_stays_and_demolish_spends_it_on_the_coin():
    normal = _game("phantom", _Coin(0.0))
    _ready(normal)
    me = _seat(normal, "a", active="Pichu", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(normal, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 2)
    _pay(foe, ["Water Energy"])
    assert normal._choose_attack(me, foe, normal.strats["a"]).name == "Playground"
    assert normal._try_sleepy_voice(me, "a") is False

    hard = _game("demolish", _Coin(0.0))
    _ready(hard)
    me = _seat(hard, "a", active="Pichu", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(
        hard,
        "b",
        active="Cornerstone Mask Ogerpon ex",
        hand=[],
        deck=["Fighting Energy", "Water Energy", "Water Energy", "Water Energy"],
    )
    _pay(foe, ["Fighting Energy", "Water Energy", "Water Energy"])
    assert hard._choose_attack(me, foe, hard.strats["a"]).name == "Playground"
    assert hard._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP


def test_a_free_coin_when_this_turn_cannot_attack():
    game = _game("phantom", _Coin(0.0))
    _ready(game)
    me = _seat(game, "a", active="Wiglett", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 2)
    _pay(foe, ["Water Energy"])
    assert game._choose_attack(me, foe, game.strats["a"]) is None
    assert game._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP

    opening = _game("phantom", _Coin(0.0))
    opening.turn = 1
    opening.first = "a"
    me = _seat(opening, "a", active="Pichu", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(opening, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 2)
    _pay(foe, ["Water Energy"])
    assert opening._mill_can_attack_turn(me) is False
    assert opening._try_sleepy_voice(me, "a") is True


def test_asleep_without_a_face_still_flips_and_a_face_declines():
    game = _game("phantom", _Coin(0.0))
    _ready(game)
    me = _seat(game, "a", active="Wiglett", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    me.active.status |= ST_ASLEEP
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 2)
    _pay(foe, ["Water Energy"])
    assert game._try_sleepy_voice(me, "a") is True

    walled = _game("phantom", _Coin(0.0))
    _ready(walled)
    me = _seat(walled, "a", active="Pichu", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    me.active.status |= ST_ASLEEP
    foe = _seat(walled, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 2)
    _pay(foe, ["Water Energy"])
    assert walled._try_sleepy_voice(me, "a") is False
    assert "mill_sleepy_flip" not in walled.events


def test_no_flip_when_their_attack_cannot_be_paid_or_they_are_asleep():
    game = _game("phantom", _Coin(0.0))
    _ready(game)
    me = _seat(game, "a", active="Wiglett", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(game, "b", active="Dragapult ex", hand=[], deck=["Water Energy"] * 4)
    assert game._try_sleepy_voice(me, "a") is False

    asleep = _game("demolish", _Coin(0.0))
    _ready(asleep)
    me = _seat(
        asleep,
        "a",
        active="Wugtrio",
        hand=[],
        deck=["Water Energy"] * 4,
        bench=["Igglybuff"],
    )
    foe = _seat(
        asleep,
        "b",
        active="Cornerstone Mask Ogerpon ex",
        hand=[],
        deck=["Fighting Energy", "Water Energy", "Water Energy", "Water Energy"],
    )
    _pay(me, ["Water Energy", "Water Energy", "Water Energy"])
    _pay(foe, ["Fighting Energy", "Water Energy", "Water Energy"])
    foe.active.status |= ST_ASLEEP
    assert asleep._try_sleepy_voice(me, "a") is False


def test_tails_ends_the_turn_without_sleep():
    game = _game("demolish", _Coin(0.99))
    _ready(game)
    me = _seat(game, "a", active="Wiglett", hand=[], deck=["Water Energy"] * 4, bench=["Igglybuff"])
    foe = _seat(
        game,
        "b",
        active="Cornerstone Mask Ogerpon ex",
        hand=[],
        deck=["Fighting Energy", "Water Energy", "Water Energy", "Water Energy"],
    )
    _pay(foe, ["Fighting Energy", "Water Energy", "Water Energy"])
    assert game._try_sleepy_voice(me, "a") is True
    assert not (foe.active.status & ST_ASLEEP)
    assert game.turn_ended_by_ability
    assert game.events.get("mill_sleepy_flip") == 1
    assert "mill_sleepy_heads" not in game.events


def test_level_ball_keeps_wugtrio_ahead_of_igglybuff():
    game = _game("demolish")
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=[],
        deck=["Pichu", "Igglybuff", "Wugtrio", "Water Energy"],
    )
    game._level_ball(me, "a", 90)
    assert [me.card(i).name for i in me.hand] == ["Wugtrio"]


def test_level_ball_takes_igglybuff_once_the_line_is_in_hand_against_demolish():
    game = _game("demolish")
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=["Wugtrio"],
        deck=["Pichu", "Igglybuff", "Water Energy"],
    )
    game._level_ball(me, "a", 90)
    assert me.card(me.hand[-1]).name == "Igglybuff"


def test_poffin_takes_wiglett_then_igglybuff_against_demolish():
    game = _game("demolish")
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Manaphy",
        hand=[],
        deck=["Wiglett", "Igglybuff", "Pichu", "Water Energy"],
    )
    wiglett = next(me.card(i) for i in me.deck if me.card(i).name == "Wiglett")
    iggly = next(me.card(i) for i in me.deck if me.card(i).name == "Igglybuff")
    pichu = next(me.card(i) for i in me.deck if me.card(i).name == "Pichu")
    assert game._mill_bench_search_score(me, wiglett) > game._mill_bench_search_score(me, iggly)
    assert game._mill_bench_search_score(me, iggly) > game._mill_bench_search_score(me, pichu)


def test_one_copy_is_benched_and_phantom_dive_leaves_it_in_the_deck():
    game = _game("demolish", extra=["Wiglett", "Wiglett", "Wiglett", "Wiglett"])
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=["Igglybuff", "Pichu"],
        deck=["Water Energy"] * 4,
        bench=["Wiglett", "Wiglett", "Wiglett", "Wiglett"],
    )
    game._play_basics(me)
    assert me.card(me.bench[-1].card_i).name == "Igglybuff"
    assert any(me.card(i).name == "Pichu" for i in me.hand)

    spread = _game("phantom")
    _ready(spread)
    me = _seat(spread, "a", active="Wiglett", hand=["Igglybuff"], deck=["Water Energy"] * 4)
    assert spread._wants_in_play(me, me.card(me.hand[0]), spread.strats["a"]) is False
    spread._play_basics(me)
    assert me.card(me.hand[0]).name == "Igglybuff"
    assert spread._mill_card_keeps(me, me.card(me.hand[0])) is False


def test_a_second_copy_stays_in_the_deck():
    game = _game("demolish", extra=["Igglybuff"])
    _ready(game)
    me = _seat(
        game,
        "a",
        active="Wiglett",
        hand=["Igglybuff"],
        deck=["Water Energy"],
        bench=["Igglybuff"],
    )
    assert game._wants_in_play(me, me.card(me.hand[0]), game.strats["a"]) is False


def test_greedy_script_swaps_one_legal_copy():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data/lab/set_mill_igglybuff.py"
    spec = importlib.util.spec_from_file_location("set_mill_igglybuff", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    swapped = module._swap(list(SET_MILL_NAMES), "Crushing Hammer", "Igglybuff")
    module._check_list(swapped)
    assert swapped.count("Igglybuff") == 1
    assert module.ADD == "Igglybuff"
    assert module.POLICY == "benefit"


def test_one_swapped_copy_is_legal_and_one_game_finishes():
    names = list(SET_MILL_NAMES)
    names.remove("Crushing Hammer")
    names.append("Igglybuff")
    cards = [mill_named(name) for name in names]
    assert len(cards) == 60
    assert copy_violations(cards, standard_60_rules()) == []
    assert sum(card.catalog_id == "sm12-168" for card in cards) == 1
    result = play_game(
        cards,
        build_fallback_deck(list(SET_D60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("mill"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )
    assert result.winner in {"a", "b", "tie"}
