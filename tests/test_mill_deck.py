"""Mill is the Sisters 60. Printed sentences are the effects.

Undersea Tunnel flips 3 coins and discards the top 3 per heads. Victory Star
reflips that attack once when the first result is 0 or 1 heads; Glimwood Tangle
is the fallback and does not stack. Team Rocket's Handiwork flips 2 coins and
discards 2 per heads, and that flip is not an attack. Twisting Strike on heads
keeps that Wiglett through the opponent's next turn. Demolish still lands.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import SET_MILL_NAMES, build_fallback_deck, fallback_named

_ABSENT = (
    "Eri",
    "Acerola's Mischief",
    "Redeemable Ticket",
    "Hero's Cape",
    "Mew ex",
    "Great Tusk",
)

_WIGLETT = (
    "Flip a coin. If heads, during your opponent's next turn, prevent all damage "
    "from and effects of attacks done to this Pokémon."
)
_UNDERSEA = "Flip 3 coins. For each heads, discard the top 3 cards of your opponent's deck."
_STORED = "Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."
_GLIMWOOD = (
    "Once during each player's turn, after that player flips any coins for an attack, "
    "they may ignore all results of those coin flips and begin flipping those coins again."
)
_SISTERS = (
    "Look at the top 5 cards of your opponent's deck and discard any number of Item cards "
    "you find there. Your opponent shuffles the other cards back into their deck."
)
_HANDIWORK = "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."
_LEVEL = (
    "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. "
    "Then, shuffle your deck."
)
_HQ = "Attacks used by each Basic Pokémon in play (both yours and your opponent's) cost {C} more."


def _coins(*values: float):
    remaining = list(values)

    def random() -> float:
        if not remaining:
            raise AssertionError("extra coin")
        return remaining.pop(0)

    return random


class _Board:
    def __init__(self, strat_a="balanced", strat_b="balanced"):
        names = [
            "Wiglett",
            "Wiglett",
            "Wiglett",
            "Wugtrio",
            "Wugtrio",
            "Victini",
            "Mew ex",
            "Cornerstone Mask Ogerpon ex",
            "Electrode-GX",
            "Raikou V",
            "Neutralization Zone",
            "Glimwood Tangle",
            "Pokémon League Headquarters",
            "Miss Fortune Sisters",
            "Team Rocket's Handiwork",
            "Level Ball",
            "Nest Ball",
            "Switch",
            "Boss's Orders",
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

    def seat(self, who: str, *, active=None, bench=(), hand=(), discard=(), deck=None):
        player = self.game.players[who]
        if active is None:
            player.active = None
        else:
            name, fuels = active
            player.active = Pokemon(
                card_i=self.take(who, name),
                energy=[self.take(who, fuel) for fuel in fuels],
            )
        player.bench = [Pokemon(card_i=self.take(who, name)) for name in bench]
        player.hand = [self.take(who, name) for name in hand]
        player.discard = [self.take(who, name) for name in discard]
        if deck is None:
            player.deck = [i for i in range(len(player.cards)) if i not in self._used[who]]
        else:
            player.deck = [self.take(who, name) for name in deck]
        player.prizes = []
        return player


def test_mill_list_is_the_sisters_sixty():
    names = list(SET_MILL_NAMES)
    assert len(names) == 60
    assert names.count("Wiglett") == 4
    assert names.count("Wugtrio") == 4
    assert names.count("Victini") == 1
    assert names.count("Level Ball") == 3
    assert names.count("Nest Ball") == 3
    assert names.count("Buddy-Buddy Poffin") == 4
    assert names.count("Rescue Carrier") == 4
    assert names.count("Crushing Hammer") == 4
    assert names.count("Counter Catcher") == 2
    assert names.count("Switch") == 1
    assert names.count("Miss Fortune Sisters") == 2
    assert names.count("Crispin") == 3
    assert names.count("Boss's Orders") == 2
    assert names.count("Team Rocket's Handiwork") == 2
    assert names.count("Colress's Tenacity") == 4
    assert names.count("Team Rocket's Petrel") == 1
    assert names.count("Glimwood Tangle") == 1
    assert names.count("Neutralization Zone") == 1
    assert names.count("Pokémon League Headquarters") == 3
    assert names.count("Double Turbo Energy") == 4
    assert names.count("Water Energy") == 4
    assert names.count("Fighting Energy") == 3
    for missing in _ABSENT:
        assert missing not in names
    pile = build_fallback_deck(names)
    assert copy_violations(pile, standard_60_rules()) == []
    for key in ("mill", "wugtrio", "21"):
        loaded = load_seed_deck(key)
        assert loaded["id"] == "seed-mill"
        assert loaded["name"] == "Mill"
        assert [c["name"] for c in loaded["cards"]] == names
    assert default_rule_presets_for("seed-mill") == ["s60"]
    assert "seed-mill" in S60_SEED_IDS
    assert StrategySpec.from_dict("mill").reflip_heads_at_most == 1
    assert StrategySpec.from_dict("balanced").reflip_heads_at_most is None
    assert StrategySpec.from_dict({"name": "balanced"}).reflip_heads_at_most is None
    assert StrategySpec.from_dict({"name": "mill", "reflip_heads_at_most": None}).reflip_heads_at_most == 1


def test_printed_sentences_parse_to_the_mill_effects():
    wiglett = fallback_named("Wiglett")
    assert wiglett.catalog_id == "sv01-055"
    twist = next(a for a in wiglett.attacks if a.name == "Twisting Strike")
    assert twist.text == _WIGLETT
    assert parse_effects(twist.text) == [{"kind": "coin_prevent_self_damage_next_turn"}]

    undersea = next(a for a in fallback_named("Wugtrio").attacks if a.name == "Undersea Tunnel")
    assert undersea.text == _UNDERSEA
    parsed = parse_effects(undersea.text)
    assert parsed == [{"kind": "coin_mill_opponent", "flips": 3, "per": 3}]
    assert all(e.get("kind") not in {"mill_opponent", "coin_times", "times"} for e in parsed)

    victini = fallback_named("Victini")
    star = next(a for a in victini.abilities if a.name == "Victory Star")
    assert "can\u2019t" in star.text
    assert parse_ability_effects(star.text) == [
        {"kind": "reflip_attack_coins", "limit_name": "victory star"}
    ]
    stored = next(a for a in victini.attacks if a.name == "Stored Power")
    assert stored.text == _STORED
    assert parse_effects(stored.text) == [{"kind": "move_all_energy_to_bench"}]

    glimwood = fallback_named("Glimwood Tangle")
    assert glimwood.text == _GLIMWOOD
    assert parse_ability_effects(glimwood.text) == [{"kind": "reflip_attack_coins", "each_player": True}]

    zone = fallback_named("Neutralization Zone")
    zone_fx = parse_ability_effects(zone.text)
    assert {"kind": "prevent_ex_v_damage_no_rule_box", "both_players": True} in zone_fx
    assert {"kind": "cannot_leave_discard"} in zone_fx

    hq = fallback_named("Pokémon League Headquarters")
    assert hq.text == _HQ
    assert parse_ability_effects(hq.text) == [
        {"kind": "stadium_basic_attack_cost_more", "colorless": 1, "both_players": True}
    ]
    assert all(e.get("kind") != "stadium_psychic_cost_less_colorless" for e in parse_ability_effects(hq.text))

    sisters = fallback_named("Miss Fortune Sisters")
    assert sisters.text == _SISTERS
    assert parse_trainer_effects(sisters.text) == [{"kind": "look_opp_discard_items", "look": 5}]
    handiwork = fallback_named("Team Rocket's Handiwork")
    assert handiwork.text == _HANDIWORK
    assert parse_trainer_effects(handiwork.text) == [{"kind": "coin_mill_top", "flips": 2, "per": 2}]
    level = fallback_named("Level Ball")
    assert level.text == _LEVEL
    assert parse_trainer_effects(level.text) == [{"kind": "search_pokemon_max_hp", "max_hp": 90}]
    assert {"kind": "mill_opponent", "count": 1} in parse_effects("Discard the top card of your opponent's deck.")


def _undersea(board: _Board, coins: tuple[float, ...]) -> tuple[Game, object, int]:
    me = board.seat(
        "a",
        active=("Wugtrio", ["Water Energy", "Water Energy", "Water Energy"]),
        bench=("Victini",),
    )
    foe = board.seat("b", active=("Wiglett", []))
    board.game._set_stadium(fallback_named("Glimwood Tangle"), me)
    before = len(foe.deck)
    assert before >= 9
    board.game.rng.random = _coins(*coins)
    board.game._attack(me, foe, "a")
    return board.game, foe, before


def test_zero_heads_uses_victory_star_once_and_mills_nine():
    game, foe, before = _undersea(_Board("mill"), (0.9, 0.9, 0.9, 0.0, 0.0, 0.0))
    me = game.players["a"]
    assert len(foe.deck) == before - 9
    assert game.events.get("victory_star_reflip") == 1
    assert game.events.get("glimwood_reflip", 0) == 0
    assert me.victory_star_used is True
    assert me.glimwood_used is False
    log = "\n".join(game.trace)
    assert log.count("Victory Star reflip") == 1
    assert "Glimwood Tangle reflip" not in log
    try:
        game.rng.random()
    except AssertionError as exc:
        assert "extra coin" in str(exc)
    else:
        raise AssertionError("reflip consumed a seventh coin")


def test_two_heads_declines_the_reflip_and_mills_six():
    game, foe, before = _undersea(_Board("mill"), (0.0, 0.0, 0.9))
    assert len(foe.deck) == before - 6
    assert game.events.get("victory_star_reflip", 0) == 0
    assert game.events.get("glimwood_reflip", 0) == 0
    try:
        game.rng.random()
    except AssertionError as exc:
        assert "extra coin" in str(exc)
    else:
        raise AssertionError("two heads still reflipped")


def test_balanced_strategy_declines_the_reflip():
    game, foe, before = _undersea(_Board("balanced"), (0.9, 0.9, 0.9))
    assert len(foe.deck) == before
    assert game.events.get("victory_star_reflip", 0) == 0
    assert game.events.get("glimwood_reflip", 0) == 0
    assert game.events.get("mill_opponent", 0) == 0


def test_handiwork_flips_two_coins_and_does_not_reflip():
    board = _Board("mill")
    me = board.seat("a", active=("Wugtrio", []), bench=("Victini",))
    foe = board.seat("b", active=("Wiglett", []))
    board.game._set_stadium(fallback_named("Glimwood Tangle"), me)
    before = len(foe.deck)
    board.game.rng.random = _coins(0.0, 0.9)
    board.game._resolve_trainer(me, foe, fallback_named("Team Rocket's Handiwork"), "a")
    assert len(foe.deck) == before - 2
    assert board.game.events.get("handiwork") == 1
    assert board.game.events.get("victory_star_reflip", 0) == 0
    assert board.game.events.get("glimwood_reflip", 0) == 0
    try:
        board.game.rng.random()
    except AssertionError as exc:
        assert "extra coin" in str(exc)
    else:
        raise AssertionError("Handiwork reflipped")

    tails = _Board("mill")
    me = tails.seat("a", active=("Victini", []), bench=("Wugtrio",))
    foe = tails.seat("b", active=("Wiglett", []))
    tails.game._set_stadium(fallback_named("Glimwood Tangle"), me)
    before = len(foe.deck)
    tails.game.rng.random = _coins(0.9, 0.9)
    tails.game._resolve_trainer(me, foe, fallback_named("Team Rocket's Handiwork"), "a")
    assert len(foe.deck) == before
    assert tails.game.events.get("mill_opponent", 0) == 0
    assert tails.game.events.get("handiwork_tails") == 1


def test_sisters_discards_the_items_in_the_top_five():
    board = _Board("mill")
    me = board.seat("a", active=("Wugtrio", []))
    foe = board.seat(
        "b",
        active=("Wiglett", []),
        deck=["Nest Ball", "Water Energy", "Wiglett", "Switch", "Boss's Orders"],
    )
    board.game._resolve_trainer(me, foe, fallback_named("Miss Fortune Sisters"), "a")
    assert sorted(foe.card(i).name for i in foe.discard) == ["Nest Ball", "Switch"]
    assert sorted(foe.card(i).name for i in foe.deck) == ["Boss's Orders", "Water Energy", "Wiglett"]


def test_level_ball_takes_wiglett_and_leaves_mew_ex():
    board = _Board("mill")
    me = board.seat("a", active=("Victini", []), deck=["Mew ex", "Wiglett"])
    assert board.game._pokemon_search_prefer(me, "a")[0] == "Wiglett"
    board.game._resolve_trainer(me, board.game.players["b"], fallback_named("Level Ball"), "a")
    hand = [me.card(i).name for i in me.hand]
    deck = [me.card(i).name for i in me.deck]
    assert hand == ["Wiglett"]
    assert "Mew ex" not in hand
    assert deck == ["Mew ex"]


def test_neutralization_zone_stays_in_the_discard():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []), discard=["Neutralization Zone"])
    board.game._retrieve_from_discard(me, 1)
    assert me.hand == []
    assert [me.card(i).name for i in me.discard] == ["Neutralization Zone"]


def test_headquarters_taxes_basic_attacks_only():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", ["Water Energy"]), bench=("Wugtrio",))
    board.game._set_stadium(fallback_named("Pokémon League Headquarters"), me)
    twist = next(a for a in me.card(me.active.card_i).attacks if a.name == "Twisting Strike")
    assert board.game._attack_cost(me, me.active, twist) == ["Water", "Colorless"]
    trio = me.bench[0]
    undersea = next(a for a in me.card(trio.card_i).attacks if a.name == "Undersea Tunnel")
    assert board.game._attack_cost(me, trio, undersea) == ["Colorless", "Colorless", "Colorless"]


def _strike(board: _Board, attacker: str, attack: str, defender: str) -> int:
    me = board.seat("a", active=(attacker, []))
    foe = board.seat("b", active=(defender, []))
    atk = next(a for a in me.card(me.active.card_i).attacks if a.name == attack)
    return board.game._raw_attack_damage(me, foe, me.active, atk)


def test_neutralization_zone_stops_ex_and_v_and_demolish_still_lands():
    def damage(attacker: str, attack: str, defender: str) -> tuple[int, dict]:
        board = _Board("balanced")
        board.game._set_stadium(fallback_named("Neutralization Zone"))
        dealt = _strike(board, attacker, attack, defender)
        return dealt, board.game.events

    dealt, events = damage("Mew ex", "Teleportation Burst", "Wiglett")
    assert dealt == 0
    assert events.get("neutralization_zone", 0) >= 1
    assert damage("Raikou V", "Lightning Streak", "Wiglett")[0] == 0
    assert damage("Electrode-GX", "Electro Ball", "Wiglett")[0] == 100
    assert damage("Wugtrio", "Headbutt", "Wiglett")[0] == 30
    dealt, events = damage("Cornerstone Mask Ogerpon ex", "Demolish", "Wiglett")
    assert dealt == 140
    assert events.get("neutralization_zone", 0) == 0
    assert damage("Mew ex", "Teleportation Burst", "Mew ex")[0] == 30


def test_twisting_strike_heads_blocks_the_next_attack_and_demolish_lands():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", ["Water Energy"]))
    foe = board.seat("b", active=("Wugtrio", []))
    board.game.rng.random = _coins(0.0)
    board.game._attack(me, foe, "a")
    assert me.active.prevent_attack_damage is True
    assert board.game.events.get("twisting_strike") == 1
    headbutt = next(a for a in foe.card(foe.active.card_i).attacks if a.name == "Headbutt")
    assert board.game._raw_attack_damage(foe, me, foe.active, headbutt) == 0
    oger = board.take("b", "Cornerstone Mask Ogerpon ex")
    foe.active = Pokemon(card_i=oger)
    demolish = next(a for a in foe.card(oger).attacks if a.name == "Demolish")
    assert board.game._raw_attack_damage(foe, me, foe.active, demolish) == 140
    board.game._expire_turn_markers("b")
    assert me.active.prevent_attack_damage is False


def test_twisting_strike_tails_then_victory_star_buys_the_extra_turn():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", ["Water Energy"]), bench=("Victini",))
    foe = board.seat("b", active=("Wugtrio", []))
    board.game.rng.random = _coins(0.9, 0.0)
    board.game._attack(me, foe, "a")
    assert me.active.prevent_attack_damage is True
    assert board.game.events.get("victory_star_reflip") == 1
    assert me.victory_star_used is True
    try:
        board.game.rng.random()
    except AssertionError as exc:
        assert "extra coin" in str(exc)
    else:
        raise AssertionError("Twisting Strike reflipped twice")
