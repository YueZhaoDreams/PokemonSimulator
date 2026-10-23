"""Nincada Dig and Shedinja Vessel of Life, from the printed sentences.

Dig flips one coin. Heads prevents effects of attacks, including damage, during
the opponent's next turn. Vessel of Life discards the cards attached to Shedinja
and attaches Shedinja itself as a Pokémon Tool. The Nincada under Shedinja is
discarded with the Pokémon, not stuck to the Tool. The Tool makes that Knock Out
worth 1 fewer Prize card. Mill puts the Tool on a Wugtrio that is not already
preventing damage.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named, build_fallback_deck

_DIG = (
    "Flip a coin. If heads, prevent all effects of attacks, including damage, "
    "done to this Pokémon during your opponent's next turn."
)
_VESSEL = (
    "Once during your turn (before your attack), you may discard all cards attached to this Pokémon "
    "and attach it to 1 of your Pokémon as a Pokémon Tool card. When the Pokémon this card is attached to "
    "is Knocked Out, your opponent takes 1 fewer Prize card."
)
_HAUNT = "Put 3 damage counters on your opponent's Active Pokémon."


def _coins(*values: float):
    remaining = list(values)

    def random() -> float:
        if not remaining:
            raise AssertionError("extra coin")
        return remaining.pop(0)

    return random


class _Board:
    def __init__(self, strat_a="mill", strat_b="balanced"):
        names = [
            "Nincada",
            "Nincada",
            "Shedinja",
            "Shedinja",
            "Wiglett",
            "Wiglett",
            "Wugtrio",
            "Wugtrio",
            "Pichu",
            "Rescue Carrier",
            "Level Ball",
            "Water Energy",
            "Water Energy",
            "Water Energy",
        ]
        while len(names) < 40:
            names.append("Water Energy")
        self.game = Game(
            build_fallback_deck(names),
            build_fallback_deck(list(names)),
            standard_60_rules(),
            StrategySpec.from_dict(strat_a),
            StrategySpec.from_dict(strat_b),
            Random(1),
            trace=True,
        )
        self._used = {"a": set(), "b": set()}

    def take(self, who: str, name: str) -> int:
        player = self.game.players[who]
        for i, card in enumerate(player.cards):
            if i in self._used[who] or card.name != name:
                continue
            self._used[who].add(i)
            return i
        raise AssertionError(name)

    def seat(self, who: str, *, active=None, bench=(), hand=(), discard=()):
        player = self.game.players[who]
        if active is None:
            player.active = None
        else:
            name, fuels = active
            player.active = Pokemon(
                card_i=self.take(who, name),
                energy=[self.take(who, fuel) for fuel in fuels],
            )
        player.bench = []
        for name in bench:
            if isinstance(name, tuple):
                mon_name, fuels = name
                player.bench.append(
                    Pokemon(
                        card_i=self.take(who, mon_name),
                        energy=[self.take(who, fuel) for fuel in fuels],
                    )
                )
            else:
                player.bench.append(Pokemon(card_i=self.take(who, name)))
        player.hand = [self.take(who, name) for name in hand]
        player.discard = [self.take(who, name) for name in discard]
        player.deck = [i for i in range(len(player.cards)) if i not in self._used[who]]
        player.prizes = []
        return player


def test_printed_dig_vessel_and_haunt():
    nincada = fallback_named("Nincada")
    shedinja = fallback_named("Shedinja")
    assert nincada.catalog_id == "bw6-10"
    assert nincada.hp == 40
    assert nincada.retreat == 2
    assert nincada.attacks[0].name == "Dig"
    assert nincada.attacks[0].text == _DIG
    assert parse_effects(nincada.attacks[0].text) == [{"kind": "coin_prevent_self_damage_next_turn"}]
    assert shedinja.catalog_id == "sm8-95"
    assert shedinja.hp == 40
    assert shedinja.evolves_from == "Nincada"
    assert shedinja.attacks[0].name == "Haunt"
    assert shedinja.attacks[0].text == _HAUNT
    assert parse_effects(shedinja.attacks[0].text) == [{"kind": "active_damage_counters", "counters": 3}]
    ability = shedinja.abilities[0]
    assert ability.name == "Vessel of Life"
    assert ability.text == _VESSEL
    assert parse_ability_effects(ability.text) == [{"kind": "attach_self_as_tool", "fewer_prizes": 1}]


def test_dig_heads_prevents_effects_including_damage():
    board = _Board("balanced")
    me = board.seat("a", active=("Nincada", ["Water Energy"]))
    foe = board.seat("b", active=("Wugtrio", ["Water Energy"]))
    board.game.rng.random = _coins(0.0)
    board.game._attack(me, foe, "a")
    assert me.active.prevent_attack_damage is True
    assert board.game.events.get("twisting_strike") == 1
    board.game.rng.random = _coins(0.0)
    board.game._attack(foe, me, "b")
    assert me.active.damage == 0


def test_haunt_counters_and_dig_shield_stops_them():
    board = _Board("balanced")
    me = board.seat("a", active=("Shedinja", ["Water Energy"]))
    foe = board.seat("b", active=("Wiglett", []))
    board.game._attack(me, foe, "a")
    assert foe.active.damage == 30
    assert board.game.events.get("haunt") == 3

    foe.active.damage = 0
    foe.active.prevent_attack_damage = True
    board.game._attack(me, foe, "a")
    assert foe.active.damage == 0
    assert board.game.events.get("prevent_attack_effect", 0) >= 1


def test_vessel_discards_nincada_and_tools_an_unprotected_wugtrio():
    board = _Board()
    me = board.seat(
        "a",
        active=("Wugtrio", ["Water Energy"]),
        bench=("Nincada",),
        hand=("Shedinja", "Water Energy"),
    )
    me.bench[0].energy = [board.take("a", "Water Energy")]
    me.bench[0].played_turn = 0
    board.game.turn = 4
    board.game._evolve(me, board.game.players["b"], "a")
    assert me.card(me.bench[0].card_i).name == "Shedinja"
    assert [me.card(i).name for i in me.bench[0].underneath] == ["Nincada"]
    board.game._use_vessel_of_life(me, "a")
    assert me.card(me.active.tool).name == "Shedinja"
    assert me.bench == []
    assert [me.card(i).name for i in me.discard] == ["Water Energy", "Nincada"]
    assert board.game.events.get("vessel_of_life") == 1
    assert board.game.events.get("vessel_discard_under") == 1


def test_tooled_wugtrio_gives_one_fewer_prize():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), bench=("Shedinja",))
    foe = board.seat("b", active=("Wiglett", []))
    board.game.turn = 4
    me.bench[0].played_turn = 0
    me.bench[0].underneath = [board.take("a", "Nincada")]
    board.game._use_vessel_of_life(me, "a")
    assert me.card(me.active.tool).name == "Shedinja"
    foe.prizes = [foe.deck.pop(), foe.deck.pop()]
    me.active.damage = 90
    board.game._check_ko(me, foe, "a")
    assert foe.prizes_taken == 0
    assert len(foe.prizes) == 2
    assert board.game.events.get("vessel_prize") == 1
    assert "Shedinja" in [me.card(i).name for i in me.discard]
    assert "Nincada" in [me.card(i).name for i in me.discard]


def test_vessel_skips_a_wugtrio_that_already_prevents_damage():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), bench=("Shedinja", "Wugtrio"))
    board.game.turn = 4
    me.bench[0].played_turn = 0
    me.bench[0].underneath = [board.take("a", "Nincada")]
    me.active.prevent_attack_damage = True
    board.game._use_vessel_of_life(me, "a")
    host = next(mon for mon in me.in_play() if me.card(mon.card_i).name == "Wugtrio" and mon.tool is not None)
    assert me.card(host.tool).name == "Shedinja"
    assert host is not me.active
    assert me.active.tool is None


def test_vessel_does_not_tool_pichu_or_a_second_tool():
    board = _Board()
    me = board.seat("a", active=("Pichu", []), bench=("Shedinja",))
    board.game.turn = 4
    me.bench[0].played_turn = 0
    me.bench[0].underneath = [board.take("a", "Nincada")]
    board.game._use_vessel_of_life(me, "a")
    assert me.active.tool is None
    assert me.card(me.bench[0].card_i).name == "Shedinja"

    me.bench[0].underneath = []
    wug = board.take("a", "Wugtrio")
    me.bench.append(Pokemon(card_i=wug, tool=board.take("a", "Water Energy")))
    board.game._use_vessel_of_life(me, "a")
    assert me.card(me.bench[0].card_i).name == "Shedinja"


def test_mill_does_not_evolve_shedinja_onto_a_shielded_wugtrio():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), bench=("Nincada",), hand=("Shedinja",))
    me.active.prevent_attack_damage = True
    me.bench[0].played_turn = 0
    board.game.turn = 4
    board.game._evolve(me, board.game.players["b"], "a")
    assert me.card(me.bench[0].card_i).name == "Nincada"
    assert [me.card(i).name for i in me.hand] == ["Shedinja"]


def test_level_ball_finds_shedinja_once_wugtrio_is_out():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), bench=("Nincada", "Pichu"), hand=("Level Ball",))
    board.game._level_ball(me, "a", 90)
    assert me.card(me.hand[-1]).name == "Shedinja"


def test_level_ball_finds_wugtrio_ahead_of_pichu():
    board = _Board()
    me = board.seat("a", active=("Wiglett", []), hand=("Level Ball",))
    board.game._level_ball(me, "a", 90)
    assert me.card(me.hand[-1]).name == "Wugtrio"


def test_level_ball_finds_shedinja_ahead_of_a_missing_pichu():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), hand=("Level Ball",))
    board.game._level_ball(me, "a", 90)
    assert me.card(me.hand[-1]).name == "Shedinja"


def test_level_ball_is_saved_until_the_wugtrio_line_can_take_shedinja():
    board = _Board()
    me = board.seat("a", active=("Wiglett", []), hand=("Level Ball", "Wugtrio"))
    ball = next(me.card(i) for i in me.hand if me.card(i).name == "Level Ball")
    assert board.game._mill_trainer_score(me, board.game.players["b"], ball) < 0


def test_level_ball_holds_shedinja_before_nincada_is_benched():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), bench=("Pichu",), hand=("Level Ball",))
    board.game._level_ball(me, "a", 90)
    assert me.card(me.hand[-1]).name == "Shedinja"


def test_mill_benches_nincada_only_after_shedinja_is_in_hand():
    board = _Board()
    me = board.seat("a", active=("Wugtrio", []), hand=("Nincada",))
    board.game._play_basics(me)
    assert me.bench == []
    assert [me.card(i).name for i in me.hand] == ["Nincada"]
    me.hand.append(board.take("a", "Shedinja"))
    board.game._play_basics(me)
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Nincada"]


def test_rescue_carrier_takes_wugtrio_then_nincada():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        discard=("Wiglett", "Wugtrio", "Nincada", "Shedinja"),
        hand=("Rescue Carrier",),
    )
    board.game._rescue_carrier(me, "a", 2, 90)
    assert [me.card(i).name for i in me.hand if me.card(i).name != "Rescue Carrier"] == [
        "Wugtrio",
        "Nincada",
    ]
    assert {me.card(i).name for i in me.discard} == {"Wiglett", "Shedinja"}
    board.game._rescue_carrier(me, "a", 2, 90)
    assert "Shedinja" in [me.card(i).name for i in me.hand]
