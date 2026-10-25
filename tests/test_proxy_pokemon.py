"""Items played as Pokémon. The printed sentence is the effect.

Lillie's Poké Doll is 30 HP, cannot retreat, and a Knock Out awards no Prize.
While it is Active, its own sentence discards attached cards and puts the doll
on the bottom of the deck. Snorlax Doll is only played while setting up.
Unidentified Fossil and the DP fossils that say the Knock Out counts still
award a Prize.
"""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

_LILLIE = (
    "Play this card as if it were a 30-HP Colorless Basic Pokémon. "
    "At any time during your turn (before your attack), if this Pokémon is your Active Pokémon, "
    "you may discard all cards from it and put it on the bottom of your deck. "
    "This card can’t retreat. If this card is Knocked Out, your opponent can’t take any Prize cards for it."
)
_ROBO = (
    "Play this card as if it were a 30 HP Colorless Basic Pokémon. "
    "At any time during your turn (before your attack), you may discard this card from play. "
    "This card can't retreat. If this card is Knocked Out, your opponent can't take any Prize cards for it."
)
_SNORLAX = fallback_named("Snorlax Doll").text
_CLEFAIRY = fallback_named("Clefairy Doll").text
_FOSSIL = fallback_named("Mysterious Fossil").text
_UNIDENTIFIED = (
    "Play this card as if it were a 60-HP Colorless Basic Pokémon. "
    "At any time during your turn (before your attack), you may discard this card from play. "
    "This card can't retreat."
)
_RARE = (
    "Play this card as if it were a 70-HP Basic Colorless Pokémon. "
    "At any time during your turn, you may discard this card from play. "
    "This card can't be affected by any Special Conditions, and it can't retreat."
)
_HELIX = (
    "Play Helix Fossil as if it were a Colorless Basic Pokémon. "
    "(Helix Fossil counts as a Trainer card as well, but if Helix Fossil is Knocked Out, "
    "this counts as a Knocked Out Pokémon.) Helix Fossil can't be affected by any Special Conditions "
    "and can't retreat. At any time during your turn before your attack, you may discard Helix Fossil "
    "from play. (This doesn't count as a Knocked Out Pokémon.)"
)
_ANTIQUE = (
    "Play this card as if it were a 60-HP Basic Colorless Pokémon. "
    "This card can't be affected by any Special Conditions and can't retreat. "
    "At any time during your turn, you may discard this card from play."
)


def _effect(text: str) -> dict:
    found = parse_trainer_effects(text)
    assert len(found) == 1
    return found[0]


def test_lillies_doll_sentence():
    effect = _effect(_LILLIE)
    assert effect["kind"] == "play_as_pokemon"
    assert effect["hp"] == 30
    assert effect["no_prize"] is True
    assert effect["cant_retreat"] is True
    assert effect["tuck_bottom"] is True
    assert effect["active_only_tuck"] is True
    assert effect["may_discard"] is False
    assert effect["setup_only"] is False


def test_robo_substitute_discards_and_awards_nothing():
    effect = _effect(_ROBO)
    assert effect["hp"] == 30
    assert effect["no_prize"] is True
    assert effect["may_discard"] is True
    assert effect["tuck_bottom"] is False
    assert effect["cant_retreat"] is True


def test_snorlax_doll_is_setup_only():
    effect = _effect(_SNORLAX)
    assert effect["hp"] == 120
    assert effect["no_prize"] is True
    assert effect["setup_only"] is True
    assert effect["immune_special"] is True
    assert effect["cant_retreat"] is True
    assert effect["may_discard"] is True
    assert fallback_named("Snorlax Doll").hp == 120


def test_clefairy_doll_uses_printed_hp_and_blocks_four_status():
    effect = _effect(_CLEFAIRY)
    assert "hp" not in effect
    assert effect["no_prize"] is True
    assert effect["immune_status"] == ["asleep", "confused", "paralyzed", "poisoned"]
    assert effect["immune_special"] is False
    assert effect["may_discard"] is True
    assert fallback_named("Clefairy Doll").hp == 10


def test_mysterious_fossil_awards_no_prize():
    effect = _effect(_FOSSIL)
    assert effect["no_prize"] is True
    assert effect["immune_special"] is True
    assert effect["cant_retreat"] is True
    assert fallback_named("Mysterious Fossil").hp == 50
    assert fallback_named("Root Fossil").hp == 40
    assert fallback_named("Claw Fossil").hp == 40
    assert _effect(fallback_named("Root Fossil").text)["no_prize"] is True
    assert _effect(fallback_named("Claw Fossil").text)["no_prize"] is True


def test_fossils_that_count_as_a_knock_out_still_award_a_prize():
    assert _effect(_UNIDENTIFIED)["no_prize"] is False
    assert _effect(_UNIDENTIFIED)["hp"] == 60
    assert _effect(_RARE)["no_prize"] is False
    assert _effect(_RARE)["hp"] == 70
    assert _effect(_HELIX)["no_prize"] is False
    assert _effect(_ANTIQUE)["no_prize"] is False


class _Board:
    def __init__(self):
        names = [
            "Lillie's Poké Doll",
            "Robo Substitute",
            "Snorlax Doll",
            "Clefairy Doll",
            "Wugtrio",
            "Wiglett",
            "Cornerstone Mask Ogerpon ex",
            "Water Energy",
            "Water Energy",
            "Water Energy",
            "Water Energy",
            "Fighting Energy",
            "Fighting Energy",
            "Fighting Energy",
        ]
        while len(names) < 40:
            names.append("Water Energy")
        self.game = Game(
            build_fallback_deck(names),
            build_fallback_deck(list(names)),
            standard_60_rules(),
            StrategySpec.from_dict("mill"),
            StrategySpec.from_dict("demolish"),
            Random(2),
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
        player.active = None
        player.bench = []
        player.hand = []
        player.discard = []
        player.prizes = []
        if active is not None:
            name, fuels, damage = active
            player.active = Pokemon(
                card_i=self.take(who, name),
                energy=[self.take(who, fuel) for fuel in fuels],
                damage=damage,
            )
        player.bench = [Pokemon(card_i=self.take(who, name)) for name in bench]
        player.hand = [self.take(who, name) for name in hand]
        player.deck = [self.take(who, name) for name in deck]
        player.prizes = [self.take(who, "Water Energy") for _ in range(6)]
        return player


def test_knocking_out_lillies_doll_awards_no_prize():
    board = _Board()
    game = board.game
    me = board.seat("a", active=("Lillie's Poké Doll", [], 30), bench=("Wiglett",), deck=("Water Energy",) * 12)
    foe = board.seat("b", active=("Wiglett", ["Water Energy"], 0), deck=("Water Energy",) * 12)
    assert game._max_hp(me, me.active) == 30
    assert game._check_ko(me, foe, "a") is False
    assert foe.prizes_taken == 0
    assert game.events.get("ko_no_prize") == 1
    assert me.card(me.discard[-1]).name == "Lillie's Poké Doll"
    assert me.card(me.active.card_i).name == "Wiglett"


def test_lillies_doll_tucks_to_the_bottom_and_discards_attachments():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Lillie's Poké Doll", ["Water Energy"], 0),
        bench=("Wugtrio",),
        deck=("Water Energy",) * 8,
    )
    assert game._remove_proxy(me, me.active)
    assert me.card(me.deck[0]).name == "Lillie's Poké Doll"
    assert any(me.card(i).name == "Water Energy" for i in me.discard)
    assert me.card(me.active.card_i).name == "Wugtrio"
    assert game.events.get("proxy_tuck") == 1


def test_doll_cannot_retreat():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Lillie's Poké Doll", ["Water Energy", "Water Energy"], 0),
        bench=("Wiglett",),
        deck=("Water Energy",) * 8,
    )
    assert game._do_retreat_into(me, 0) is False
    assert me.card(me.active.card_i).name == "Lillie's Poké Doll"


def test_mill_plays_the_doll_onto_the_bench():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Wiglett", [], 0),
        hand=("Lillie's Poké Doll",),
        deck=("Water Energy",) * 12,
    )
    board.seat("b", active=("Wiglett", [], 0), deck=("Water Energy",) * 12)
    game._play_trainers(me, game.players["b"], "a")
    assert len(me.bench) == 1
    assert me.card(me.bench[0].card_i).name == "Lillie's Poké Doll"
    assert "Lillie's Poké Doll" not in {me.card(i).name for i in me.discard}


def test_snorlax_doll_is_not_an_item_play_and_can_be_set_up():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Wiglett", [], 0),
        hand=("Snorlax Doll",),
        deck=("Water Energy",) * 12,
    )
    board.seat("b", active=("Wiglett", [], 0), deck=("Water Energy",) * 12)
    game._play_trainers(me, game.players["b"], "a")
    assert me.bench == []
    assert me.card(me.hand[0]).name == "Snorlax Doll"
    game._place_setup_proxy(me)
    assert me.card(me.bench[0].card_i).name == "Snorlax Doll"
    assert game._max_hp(me, me.bench[0]) == 120


def test_clefairy_doll_blocks_poison_and_not_burn():
    board = _Board()
    game = board.game
    me = board.seat("a", active=("Clefairy Doll", [], 0), deck=("Water Energy",) * 8)
    game._apply_status(me.active, "poisoned")
    assert me.active.status == 0
    game._apply_status(me.active, "burned")
    assert me.active.status != 0


def test_mill_retreats_into_the_doll_when_the_knock_out_would_take_the_last_prizes():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Wugtrio", ["Water Energy", "Water Energy"], 0),
        bench=("Lillie's Poké Doll",),
        deck=("Water Energy",) * 12,
    )
    foe = board.seat(
        "b",
        active=("Cornerstone Mask Ogerpon ex", ["Fighting Energy", "Fighting Energy", "Fighting Energy"], 0),
        deck=("Water Energy",) * 12,
    )
    foe.prizes = foe.prizes[:1]
    game._retreat_mill(me, "a")
    assert me.card(me.active.card_i).name == "Lillie's Poké Doll"
    assert game.events.get("proxy_stall") == 1


def test_mill_keeps_the_doll_active_when_wugtrio_would_be_knocked_out():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Lillie's Poké Doll", [], 0),
        bench=("Wugtrio",),
        deck=("Water Energy",) * 12,
    )
    for _ in range(3):
        me.bench[0].energy.append(board.take("a", "Water Energy"))
    foe = board.seat(
        "b",
        active=("Cornerstone Mask Ogerpon ex", ["Fighting Energy", "Fighting Energy", "Fighting Energy"], 0),
        deck=("Water Energy",) * 12,
    )
    game._mill_proxy_turn(me, foe)
    assert me.card(me.active.card_i).name == "Lillie's Poké Doll"
    assert game.events.get("proxy_hold") == 1


def test_mill_tucks_the_doll_when_wugtrio_can_attack_safely():
    board = _Board()
    game = board.game
    me = board.seat(
        "a",
        active=("Lillie's Poké Doll", [], 0),
        bench=("Wugtrio",),
        deck=("Water Energy",) * 12,
    )
    for _ in range(3):
        me.bench[0].energy.append(board.take("a", "Water Energy"))
    foe = board.seat("b", active=("Wiglett", [], 0), deck=("Water Energy",) * 12)
    game._mill_proxy_turn(me, foe)
    assert me.card(me.active.card_i).name == "Wugtrio"
    assert me.card(me.deck[0]).name == "Lillie's Poké Doll"
