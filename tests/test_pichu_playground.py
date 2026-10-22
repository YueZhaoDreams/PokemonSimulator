"""HeartGold & SoulSilver Pichu. Printed sentences are the effects.

Playground lets each player bench as many Basics as they like, user first,
then that Pichu falls Asleep. Sweet Sleeping Face prevents attack damage
while it is Asleep. Mill still sends cards; the opponent's bench does not
cancel the attack.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

_FACE = "As long as Pichu is Asleep, prevent all damage done to Pichu by attacks."
_PLAYGROUND = (
    "Each player may search his or her deck for as many Basic Pokémon as he or she likes, "
    "put them onto his or her Bench, and shuffle his or her deck afterward. "
    "(You put your Pokémon on the Bench first.) Pichu is now Asleep."
)
_OPPONENT_ASLEEP = "Your opponent's Active Pokémon is now Asleep."
_FAMILY = "Search your deck for up to 2 Basic Pokémon and put them onto your Bench. Then, shuffle your deck."


def test_playground_and_sweet_sleeping_face_use_the_printed_sentences():
    card = fallback_named("Pichu")
    assert card.catalog_id == "hgss1-28"
    assert card.hp == 30
    assert card.retreat == 0
    assert card.weaknesses == []
    attack = card.attacks[0]
    assert attack.name == "Playground"
    assert attack.cost == []
    assert attack.damage == 0
    assert attack.text == _PLAYGROUND
    parsed = parse_effects(attack.text)
    assert parsed[0] == {"kind": "status", "status": "asleep", "coin": False, "target": "self"}
    assert {"kind": "playground", "user_first": True} in parsed
    assert all(e.get("kind") != "call_family" for e in parsed)
    assert "count" not in next(e for e in parsed if e.get("kind") == "playground")
    face = card.abilities[0]
    assert face.name == "Sweet Sleeping Face"
    assert face.text == _FACE
    assert parse_ability_effects(face.text) == [{"kind": "prevent_attack_damage_while_asleep"}]
    opponent = parse_effects(_OPPONENT_ASLEEP)
    assert opponent == [{"kind": "status", "status": "asleep", "coin": False}]
    family = parse_effects(_FAMILY)
    assert family == [{"kind": "call_family", "count": 2}]


class _Board:
    def __init__(self):
        names = [
            "Pichu",
            "Pichu",
            "Wiglett",
            "Wiglett",
            "Wiglett",
            "Wiglett",
            "Wugtrio",
            "Victini",
            "Switch",
            "Water Energy",
            "Water Energy",
            "Water Energy",
            "Ignition Energy",
        ]
        while len(names) < 40:
            names.append("Water Energy")
        self.game = Game(
            build_fallback_deck(names),
            build_fallback_deck(list(names)),
            standard_60_rules(),
            StrategySpec.from_dict("mill"),
            StrategySpec.from_dict("mill"),
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

    def seat(self, who: str, *, active=None, bench=(), hand=(), deck=()):
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
        for name, fuels in bench:
            player.bench.append(
                Pokemon(
                    card_i=self.take(who, name),
                    energy=[self.take(who, fuel) for fuel in fuels],
                )
            )
        player.hand = [self.take(who, name) for name in hand]
        player.deck = [self.take(who, name) for name in deck]
        player.discard = []
        player.prizes = []
        return player


def test_playground_benches_the_user_first_and_sleeps_only_pichu():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        deck=("Wiglett", "Wiglett", "Victini", "Water Energy"),
    )
    foe = board.seat(
        "b",
        active=("Wiglett", []),
        deck=("Wiglett", "Wiglett", "Victini", "Water Energy"),
    )
    board.game.turn = 3
    board.game._attack(me, foe, "a")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Wiglett", "Wiglett", "Victini"]
    assert [foe.card(mon.card_i).name for mon in foe.bench] == ["Wiglett", "Wiglett", "Victini"]
    assert me.active.status & ST_ASLEEP
    assert not (foe.active.status & ST_ASLEEP)
    log = "\n".join(board.game.trace)
    assert log.index("A Playground benches Wiglett") < log.index("B Playground benches Wiglett")
    assert board.game.events.get("playground", 0) == 6


def test_full_bench_still_puts_pichu_to_sleep():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wiglett", []),) * 4 + (("Victini", []),),
        deck=("Pichu",),
    )
    foe = board.seat("b", active=("Wiglett", []), deck=("Wiglett",))
    before = len(me.bench)
    board.game._attack(me, foe, "a")
    assert len(me.bench) == before
    assert me.active.status & ST_ASLEEP
    assert board.game.events.get("playground", 0) == 1


def test_sweet_sleeping_face_stops_attack_damage_only_while_asleep():
    board = _Board()
    me = board.seat("a", active=("Wiglett", ["Water Energy"]))
    foe = board.seat("b", active=("Pichu", []))
    foe.active.status = ST_ASLEEP
    board.game.rng.random = lambda: 0.9
    board.game._attack(me, foe, "a")
    assert foe.active.damage == 0
    assert board.game.events.get("sweet_sleeping_face", 0) >= 1
    foe.active.status = 0
    board.game._attack(me, foe, "a")
    assert foe.active.damage == 10


def test_asleep_pichu_switches_into_a_wugtrio_that_can_mill():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wugtrio", ["Water Energy", "Water Energy", "Water Energy"]),),
        hand=("Switch",),
    )
    foe = board.seat("b", active=("Wiglett", []))
    me.active.status = ST_ASLEEP
    assert board.game._mill_switch_idx(me) == 0
    board.game._play_trainers(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wugtrio"
    assert me.card(me.bench[0].card_i).name == "Pichu"


def test_asleep_pichu_stays_up_until_the_back_row_can_mill():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wugtrio", []), ("Wiglett", [])),
        hand=("Switch", "Ignition Energy"),
    )
    me.active.status = ST_ASLEEP
    # Asleep Pichu cannot retreat. Ignition pays an Evolution by itself.
    assert board.game._mill_switch_idx(me) == 0
    awake = _Board()
    free = awake.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wugtrio", []), ("Wiglett", [])),
        hand=("Switch", "Ignition Energy"),
    )
    assert awake.game._mill_switch_idx(free) is None
    bare = _Board()
    waiting = bare.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wugtrio", []),),
        hand=("Switch",),
    )
    waiting.active.status = ST_ASLEEP
    assert bare.game._mill_switch_idx(waiting) is None
    assert bare.game._pick_trainer(waiting) is None


def test_pichu_waits_behind_a_basic_until_playground_is_legal():
    board = _Board()
    me = board.seat("a", active=("Pichu", []), bench=(("Wiglett", []), ("Victini", [])))
    foe = board.seat("b", active=("Wiglett", []))
    board.game.turn = 1
    board.game.first = "a"
    board.game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Victini"
    assert "Pichu" in {me.card(mon.card_i).name for mon in me.bench}

    second = _Board()
    me = second.seat("a", active=("Pichu", []), bench=(("Wiglett", []),))
    foe = second.seat("b", active=("Wiglett", []))
    second.game.turn = 1
    second.game.first = "b"
    second.game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Pichu"

    back = _Board()
    me = back.seat("a", active=("Wiglett", ["Water Energy"]), bench=(("Pichu", []),))
    foe = back.seat("b", active=("Wiglett", []))
    back.game.turn = 1
    back.game.first = "b"
    back.game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Pichu"

    held = _Board()
    me = held.seat(
        "a",
        active=("Wiglett", []),
        bench=(("Pichu", []),),
        hand=("Switch",),
    )
    held.game.turn = 1
    held.game.first = "a"
    assert held.game._mill_switch_idx(me) is None
    held.game.turn = 3
    assert held.game._mill_switch_idx(me) == 0


def test_mill_attaches_to_the_bench_line_while_pichu_stalls():
    board = _Board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        bench=(("Wiglett", []),),
        hand=("Water Energy",),
    )
    target = board.game._mill_energy_target(me)
    assert me.card(target.card_i).name == "Wiglett"
