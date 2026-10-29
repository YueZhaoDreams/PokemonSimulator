"""Igglybuff Sleepy Voice on Doll.

Printed text (Cosmic Eclipse 168): once during your turn, before your attack,
you may flip a coin. Heads, the opponent's Active Pokémon is now Asleep. If
you use this Ability, your turn ends. It does not say the Active Spot, so a
Benched copy can use it. fallback_named("Igglybuff") stays Bouncy Circle.
"""

from random import Random

from app.engine.doll import choose_attack, level_ball_name, search_prefer, wants_pokemon
from app.engine.effects import parse_ability_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named

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
    out = []
    for name in names:
        if name == "Cleffa":
            out.append(fallback_named("cleffa hgss"))
        elif name == "Igglybuff":
            out.append(fallback_named("igglybuff sleepy"))
        else:
            out.append(fallback_named(name))
    while len(out) < 60:
        out.append(fallback_named("Darkness Energy"))
    return out


def _game(foe: str = "balanced", rng=None) -> Game:
    return Game(
        _cards(
            "Cleffa",
            "Igglybuff",
            "Lillie's Determination",
            "Lillie's Poké Doll",
            "Lillie's Poké Doll",
            "Lillie's Poké Doll",
            "Nincada",
            "Shedinja",
        ),
        _cards("Cleffa"),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
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
    return player


def test_printed_sentence_parses_as_sleepy_voice():
    effects = parse_ability_effects(_TEXT)
    assert effects == [{"kind": "sleepy_voice", "once_per_turn": True, "ends_turn": True}]
    assert not any(eff.get("kind") == "draw_end_turn" for eff in effects)
    attack = "Flip a coin. If heads, your opponent's Active Pokémon is now Asleep."
    assert not any(eff.get("kind") == "sleepy_voice" for eff in parse_ability_effects(attack))


def test_default_igglybuff_stays_bouncy_circle():
    bouncy = fallback_named("Igglybuff")
    assert bouncy.catalog_id != "sm12-168"
    assert bouncy.hp == 30
    assert bouncy.attacks[0].name == "Bouncy Circle"
    assert bouncy.abilities == []
    sleepy = fallback_named("igglybuff sleepy")
    assert sleepy.catalog_id == "sm12-168"
    assert sleepy.hp == 60
    assert sleepy.retreat == 0
    assert sleepy.attacks == []
    assert sleepy.abilities[0].name == "Sleepy Voice"
    assert sleepy.abilities[0].text == _TEXT
    assert not wants_pokemon(_game(), _game().players["a"], bouncy)


def test_heads_from_the_bench_sleeps_the_opponent_and_ends_the_turn():
    game = _game(rng=_Coin(0.0))
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=["Lillie's Determination"],
        deck=["Darkness Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Cleffa", hand=[], deck=["Darkness Energy"] * 8)
    iggly = me.bench[0]
    attack = choose_attack(game, me, foe)
    assert attack is not None and attack.name == "Eeeeeeek"
    assert game._try_draw_end_turn(me, "a") is False
    assert game._try_sleepy_voice(me, "a") is True
    assert foe.active.status & ST_ASLEEP
    assert not (me.active.status & ST_ASLEEP)
    assert iggly.ability_used
    assert not me.active.ability_used
    assert game.turn_ended_by_ability
    assert game.events.get("doll_sleepy_flip") == 1
    assert game.events.get("doll_sleepy_heads") == 1
    assert game._try_sleepy_voice(me, "a") is False
    assert game.events.get("doll_sleepy_flip") == 1


def test_tails_ends_the_turn_without_sleep():
    game = _game(rng=_Coin(0.99))
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=[],
        deck=["Darkness Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Cleffa", hand=[], deck=["Darkness Energy"] * 8)
    assert game._try_sleepy_voice(me, "a") is True
    assert not (foe.active.status & ST_ASLEEP)
    assert game.turn_ended_by_ability
    assert game.events.get("doll_sleepy_flip") == 1
    assert "doll_sleepy_heads" not in game.events


def test_an_asleep_active_declines_the_may():
    game = _game(rng=_Coin(0.0))
    me = _seat(
        game,
        "a",
        active="Cleffa",
        hand=[],
        deck=["Darkness Energy"] * 8,
        bench=["Igglybuff"],
    )
    foe = _seat(game, "b", active="Cleffa", hand=[], deck=["Darkness Energy"] * 8)
    foe.active.status |= ST_ASLEEP
    assert game._try_sleepy_voice(me, "a") is False
    assert not me.bench[0].ability_used
    assert not game.turn_ended_by_ability
    assert "doll_sleepy_flip" not in game.events


def test_one_copy_in_play_and_the_search_order():
    game = _game("demolish")
    me = _seat(
        game,
        "a",
        active="Lillie's Poké Doll",
        hand=[],
        deck=["Igglybuff", "Shedinja", "Darkness Energy"],
        bench=["Lillie's Poké Doll", "Lillie's Poké Doll"],
    )
    card = fallback_named("igglybuff sleepy")
    assert wants_pokemon(game, me, card) is True
    prefer = search_prefer(game, me)
    assert prefer[0] == "Igglybuff"
    assert "Manaphy" not in prefer
    assert level_ball_name(game, me) == "Igglybuff"
    iggly = me.deck.pop(0)
    me.bench.append(Pokemon(card_i=iggly))
    assert wants_pokemon(game, me, me.card(iggly)) is False
    assert level_ball_name(game, me) is None


def test_level_ball_without_igglybuff_still_takes_shedinja():
    game = _game("balanced")
    me = _seat(
        game,
        "a",
        active="Nincada",
        hand=[],
        deck=["Shedinja", "Darkness Energy"],
    )
    # The padded deck still holds the Sleepy Voice print. Move it out of the deck.
    sleepy = [i for i in me.deck if me.card(i).name == "Igglybuff"]
    me.discard.extend(sleepy)
    me.deck = [i for i in me.deck if i not in set(sleepy)]
    assert level_ball_name(game, me) == "Shedinja"

    hard = _game("demolish")
    hard_me = _seat(
        hard,
        "a",
        active="Nincada",
        hand=[],
        deck=["Shedinja", "Darkness Energy"],
    )
    sleepy = [i for i in hard_me.deck if hard_me.card(i).name == "Igglybuff"]
    hard_me.discard.extend(sleepy)
    hard_me.deck = [i for i in hard_me.deck if i not in set(sleepy)]
    assert level_ball_name(hard, hard_me) is None
