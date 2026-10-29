"""Paldea Evolved Luvdisc: Matching and Water Pulse on the Mill line.

Printed sentences are the effects. Matching takes up to 2 Supporter cards.
Water Pulse does 20 and leaves the opponent's Active Asleep. Slumbering Forest
holds that sleep. Sweet Sleeping Face is the other layer of protection.
"""

from random import Random

from app.engine.effects import parse_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

_MATCHING = (
    "Search your deck for up to 2 Supporter cards, reveal them, and put them into your hand. "
    "Then, shuffle your deck."
)
_PULSE = "Your opponent's Active Pokémon is now Asleep."


def test_luvdisc_uses_the_printed_sentences():
    card = fallback_named("Luvdisc")
    assert card.catalog_id == "sv02-047"
    assert card.hp == 70
    assert card.retreat == 1
    assert [t for t in card.types] == ["Water"]
    matching, pulse = card.attacks
    assert matching.name == "Matching"
    assert matching.cost == ["Colorless"]
    assert matching.damage == 0
    assert matching.text == _MATCHING
    assert parse_effects(matching.text) == [{"kind": "search_supporter", "count": 2}]
    assert pulse.name == "Water Pulse"
    assert pulse.cost == ["Water"]
    assert pulse.damage == 20
    assert pulse.text == _PULSE
    parsed = parse_effects(pulse.text)
    assert parsed == [{"kind": "status", "status": "asleep", "coin": False}]
    assert parsed[0].get("target") != "self"
    one = parse_effects(
        "Search your deck for up to 1 Supporter card, reveal it, and put it into your hand."
    )
    assert one == [{"kind": "search_supporter", "count": 1}]


class _Board:
    def __init__(self, foe: str = "mill"):
        names = [
            "Luvdisc",
            "Pichu",
            "Wiglett",
            "Wiglett",
            "Wugtrio",
            "Victini",
            "Slumbering Forest",
            "Neutralization Zone",
            "Colress's Tenacity",
            "Team Rocket's Handiwork",
            "Miss Fortune Sisters",
            "Boss's Orders",
            "Wally",
            "Water Energy",
            "Water Energy",
            "Water Energy",
            "Water Energy",
            "Double Turbo Energy",
            "Ignition Energy",
            "Switch",
            "Nest Ball",
        ]
        while len(names) < 40:
            names.append("Water Energy")
        self.game = Game(
            build_fallback_deck(names),
            build_fallback_deck(list(names)),
            standard_60_rules(),
            StrategySpec.from_dict("mill"),
            StrategySpec.from_dict(foe),
            Random(2),
            trace=True,
        )
        self.game.turn = 3
        self.game.first = "b"
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
        player.prizes = [0, 1, 2, 3, 4, 5]
        return player


def test_matching_takes_the_two_best_supporters_then_shuffles():
    board = _Board()
    me = board.seat(
        "a",
        active=("Luvdisc", ["Double Turbo Energy"]),
        deck=(
            "Colress's Tenacity",
            "Miss Fortune Sisters",
            "Team Rocket's Handiwork",
            "Boss's Orders",
            "Water Energy",
        ),
    )
    foe = board.seat("b", active=("Wiglett", []), bench=(("Wiglett", []),), deck=("Water Energy",) * 6)
    board.game._attack(me, foe, "a")
    found = [me.card(i).name for i in me.hand]
    assert found == ["Colress's Tenacity", "Miss Fortune Sisters"]
    assert "Water Energy" in [me.card(i).name for i in me.deck]
    assert board.game.events.get("match_use") == 1
    assert board.game.events.get("match_take") == 2
    assert not (me.active.status & ST_ASLEEP)


def test_water_pulse_damages_and_sleeps_only_the_opponent():
    board = _Board()
    me = board.seat("a", active=("Luvdisc", ["Water Energy"]))
    foe = board.seat("b", active=("Wiglett", []))
    board.game._set_stadium(fallback_named("Slumbering Forest"), me)
    board.game._attack(me, foe, "a")
    assert foe.active.damage == 20
    assert foe.active.status & ST_ASLEEP
    assert not (me.active.status & ST_ASLEEP)
    assert board.game.events.get("opponent_asleep") == 1
    flips = iter([0.0, 0.9])
    board.game.rng.random = lambda: next(flips)
    board.game._between_turns(foe)
    assert foe.active.status & ST_ASLEEP
    assert board.game.events.get("slumbering_forest") == 1


def test_mill_sleeps_with_water_pulse_when_forest_is_up():
    board = _Board()
    me = board.seat(
        "a",
        active=("Luvdisc", ["Water Energy"]),
        bench=(("Wiglett", []),),
        deck=("Water Energy",),
    )
    foe = board.seat("b", active=("Wiglett", []))
    board.game._set_stadium(fallback_named("Slumbering Forest"), me)
    board.game._retreat_mill(me, "a")
    assert me.card(me.active.card_i).name == "Luvdisc"
    chosen = board.game._choose_attack(me, foe, StrategySpec.from_dict("mill"))
    assert chosen is not None and chosen.name == "Water Pulse"


def test_mill_matches_when_water_pulse_cannot_be_paid():
    board = _Board()
    me = board.seat(
        "a",
        active=("Luvdisc", ["Double Turbo Energy"]),
        deck=("Colress's Tenacity", "Miss Fortune Sisters", "Water Energy"),
    )
    foe = board.seat("b", active=("Wiglett", []), bench=(("Wiglett", []),), deck=("Water Energy",) * 6)
    chosen = board.game._choose_attack(me, foe, StrategySpec.from_dict("mill"))
    assert chosen is not None and chosen.name == "Matching"


def test_paid_wugtrio_comes_up_ahead_of_luvdisc():
    board = _Board()
    me = board.seat(
        "a",
        active=("Luvdisc", ["Water Energy"]),
        bench=(("Wugtrio", ["Water Energy", "Water Energy", "Water Energy"]),),
    )
    board.seat("b", active=("Wiglett", []))
    board.game._set_stadium(fallback_named("Slumbering Forest"), me)
    board.game._retreat_mill(me, "a")
    assert me.card(me.active.card_i).name == "Wugtrio"


def test_energy_reaches_luvdisc_only_when_the_line_is_not_out():
    board = _Board()
    charged = board.seat(
        "a",
        active=("Wiglett", ["Water Energy"]),
        bench=(("Luvdisc", []),),
        hand=("Water Energy", "Double Turbo Energy"),
    )
    board.seat("b", active=("Wiglett", []))
    assert board.game._mill_energy_target(charged).card_i == charged.bench[0].card_i
    board.game._attach_energy(charged, "a")
    assert [charged.card(i).name for i in charged.bench[0].energy] == ["Water Energy"]

    wall = _Board()
    pichu = wall.seat(
        "a",
        active=("Pichu", []),
        bench=(("Luvdisc", []), ("Wiglett", [])),
        hand=("Water Energy",),
    )
    wall.seat("b", active=("Wiglett", []))
    target = wall.game._mill_energy_target(pichu)
    assert pichu.card(target.card_i).name == "Wiglett"


def test_forest_is_played_for_either_sleep_layer():
    board = _Board()
    bare = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wiglett", []))
    forest = fallback_named("Slumbering Forest")
    assert board.game._mill_trainer_score(bare, foe, forest) == -8

    locked = _Board()
    me = locked.seat("a", active=("Luvdisc", ["Water Energy"]))
    foe = locked.seat("b", active=("Wiglett", []))
    assert locked.game._mill_trainer_score(me, foe, forest) == 18

    baby = _Board()
    me = baby.seat("a", active=("Pichu", []))
    foe = baby.seat("b", active=("Wiglett", []))
    assert baby.game._mill_trainer_score(me, foe, forest) == 15


def test_opener_is_the_face_in_a_wall_and_luvdisc_otherwise():
    board = _Board()
    me = board.game.players["a"]
    luv = board.take("a", "Luvdisc")
    wig = board.take("a", "Wiglett")
    pichu = board.take("a", "Pichu")
    assert board.game._pick_starter(me, [luv, wig], board.game.strats["a"]) == luv
    assert board.game._pick_starter(me, [luv, pichu], board.game.strats["a"]) == pichu

    spread = _Board("phantom")
    me = spread.game.players["a"]
    luv = spread.take("a", "Luvdisc")
    pichu = spread.take("a", "Pichu")
    assert spread.game._pick_starter(me, [luv, pichu], spread.game.strats["a"]) == luv
