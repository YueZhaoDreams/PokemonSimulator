"""Call of Legends Mime Jr., HGSS Smoochum, and Unified Minds Slumbering Forest.

Printed sentences are the effects. Sleepy Lost sends the opponent's top card
to the Lost Zone. Energy Antics moves one of their Energy cards. Slumbering
Forest flips two coins between turns.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

_SLEEPY = "Put the top card of your opponent's deck in the Lost Zone. Mime Jr. is now Asleep."
_ANTICS = (
    "Move an Energy card attached to 1 of your opponent's Pokémon to another of "
    "your opponent's Pokémon. Smoochum is now Asleep."
)
_FOREST = (
    "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition "
    "between turns. If either of them is tails, that Pokémon is still Asleep."
)


def test_sleepy_lost_and_energy_antics_use_the_printed_sentences():
    mime = fallback_named("mime jr. col")
    assert mime.name == "Mime Jr."
    assert mime.catalog_id == "col1-47"
    assert mime.hp == 30
    assert mime.retreat == 0
    assert mime.attacks[0].name == "Sleepy Lost"
    assert mime.attacks[0].cost == []
    assert mime.attacks[0].text == _SLEEPY
    assert parse_effects(mime.attacks[0].text) == [
        {"kind": "status", "status": "asleep", "coin": False, "target": "self"},
        {"kind": "topdeck_lost_zone", "whose": "opponent"},
    ]
    assert parse_ability_effects(mime.abilities[0].text) == [
        {"kind": "prevent_attack_damage_while_asleep"}
    ]
    smooch = fallback_named("Smoochum")
    assert smooch.catalog_id == "hgss1-30"
    assert smooch.hp == 30
    assert smooch.attacks[0].name == "Energy Antics"
    assert smooch.attacks[0].cost == []
    assert smooch.attacks[0].text == _ANTICS
    parsed = parse_effects(smooch.attacks[0].text)
    assert {"kind": "status", "status": "asleep", "coin": False, "target": "self"} in parsed
    assert {"kind": "move_opponent_energy"} in parsed
    forest = fallback_named("Slumbering Forest")
    assert forest.catalog_id == "sm11-207"
    assert forest.text == _FOREST
    assert parse_ability_effects(forest.text) == [{"kind": "sleep_check_two_coins"}]


class _Board:
    def __init__(self):
        names = [
            "Mime Jr.",
            "Smoochum",
            "Pichu",
            "Wiglett",
            "Wugtrio",
            "Slumbering Forest",
            "Water Energy",
            "Water Energy",
            "Nest Ball",
            "Switch",
        ]
        while len(names) < 30:
            names.append("Water Energy")
        # The seat takes "Mime Jr." from fallback, which is Mimed Games.
        # Swap the first Mime Jr. for the Call of Legends print after build.
        deck_a = build_fallback_deck(names)
        deck_b = build_fallback_deck(list(names))
        for deck in (deck_a, deck_b):
            for i, card in enumerate(deck):
                if card.name == "Mime Jr.":
                    deck[i] = fallback_named("mime jr. col")
                    break
        self.game = Game(
            deck_a,
            deck_b,
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
        player.lost_zone = []
        return player


def test_sleepy_lost_sends_the_opponents_top_card_and_sleeps():
    board = _Board()
    me = board.seat("a", active=("Mime Jr.", []), deck=("Water Energy",))
    foe = board.seat("b", active=("Wiglett", []), deck=("Nest Ball", "Switch"))
    board.game._attack(me, foe, "a")
    assert [foe.card(i).name for i in foe.lost_zone] == ["Nest Ball"]
    assert [foe.card(i).name for i in foe.deck] == ["Switch"]
    assert me.lost_zone == []
    assert me.active.status & ST_ASLEEP
    assert board.game.events.get("sleepy_lost") == 1


def test_energy_antics_moves_off_the_active_then_sleeps():
    board = _Board()
    me = board.seat("a", active=("Smoochum", []))
    foe = board.seat(
        "b",
        active=("Wiglett", ["Water Energy"]),
        bench=(("Wugtrio", []),),
    )
    board.game._attack(me, foe, "a")
    assert foe.active.energy == []
    assert len(foe.bench[0].energy) == 1
    assert me.active.status & ST_ASLEEP
    assert board.game.events.get("energy_antics") == 1

    alone = _Board()
    me = alone.seat("a", active=("Smoochum", []))
    foe = alone.seat("b", active=("Wiglett", ["Water Energy"]))
    alone.game._attack(me, foe, "a")
    assert len(foe.active.energy) == 1
    assert me.active.status & ST_ASLEEP
    assert alone.game.events.get("energy_antics_fail") == 1


def test_slumbering_forest_stays_asleep_unless_both_coins_are_heads():
    board = _Board()
    me = board.seat("a", active=("Pichu", []))
    board.seat("b", active=("Wiglett", []))
    me.active.status = ST_ASLEEP
    board.game._set_stadium(fallback_named("Slumbering Forest"), me)
    flips = iter([0.0, 0.9])
    board.game.rng.random = lambda: next(flips)
    board.game._between_turns(me)
    assert me.active.status & ST_ASLEEP
    assert board.game.events.get("slumbering_forest") == 1

    awake = _Board()
    me = awake.seat("a", active=("Pichu", []))
    awake.seat("b", active=("Wiglett", []))
    me.active.status = ST_ASLEEP
    awake.game._set_stadium(fallback_named("Slumbering Forest"), me)
    heads = iter([0.0, 0.0])
    awake.game.rng.random = lambda: next(heads)
    awake.game._between_turns(me)
    assert not (me.active.status & ST_ASLEEP)
