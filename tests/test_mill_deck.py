"""Mill is the locked 60: the thin sleep wall plus one Lillie's Poké Doll. Printed sentences are the effects.

Undersea Tunnel flips 3 coins and discards the top 3 per heads. Victory Star
reflips that attack once when the first result is 0 or 1 heads; Glimwood Tangle
is the fallback and does not stack. Team Rocket's Handiwork flips 2 coins and
discards 2 per heads, and that flip is not an attack. Twisting Strike on heads
keeps that Wiglett through the opponent's next turn. Demolish still lands.
"""

import json
from random import Random

from app.engine.effects import (
    can_pay_energy,
    energy_provided,
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import _is_basic_energy_name, load_seed_deck
from app.seed_data import SET_MILL_NAMES, build_fallback_deck, build_mill_deck, fallback_named

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


def test_mill_list_is_the_locked_60():
    names = list(SET_MILL_NAMES)
    assert len(names) == 60
    assert names.count("Pichu") == 1
    assert names.count("Mime Jr.") == 1
    assert names.count("Smoochum") == 0
    assert names.count("Rellor") == 0
    assert names.count("Rabsca") == 0
    assert names.count("Battle Cage") == 0
    assert names.count("Wiglett") == 4
    assert names.count("Wugtrio") == 4
    assert names.count("Manaphy") == 1
    assert names.count("Cleffa") == 1
    assert names.count("Victini") == 1
    assert names.count("Slumbering Forest") == 1
    assert names.count("Neutralization Zone") == 1
    assert names.count("Buddy-Buddy Poffin") == 4
    assert names.count("Nest Ball") == 1
    assert names.count("Level Ball") == 3
    assert names.count("Rescue Carrier") == 3
    assert names.count("Switch") == 0
    assert names.count("Lillie's Poké Doll") == 1
    assert names.count("Crushing Hammer") == 4
    assert names.count("Colress's Tenacity") == 4
    assert names.count("Miss Fortune Sisters") == 2
    assert names.count("Team Rocket's Handiwork") == 2
    assert names.count("Crispin") == 0
    assert names.count("Wally") == 3
    assert names.count("Ignition Energy") == 4
    assert names.count("Reversal Energy") == 4
    assert names.count("Double Turbo Energy") == 4
    assert names.count("Water Energy") == 3
    assert names.count("Boss's Orders") == 1
    assert names.count("Counter Catcher") == 2
    assert names.count("Fighting Energy") == 0
    assert names.count("Glimwood Tangle") == 0
    assert names.count("Team Rocket's Petrel") == 0
    assert names.count("Pokémon League Headquarters") == 0
    for missing in _ABSENT:
        assert missing not in names
    pile = build_mill_deck()
    assert copy_violations(pile, standard_60_rules()) == []
    assert [c.catalog_id for c in pile if c.name == "Mime Jr."] == ["col1-47"]
    assert [c.catalog_id for c in pile if c.name == "Cleffa"] == ["hgss1-17"]
    assert [c.attacks[0].name for c in pile if c.name == "Cleffa"] == ["Eeeeeeek"]
    assert [c.catalog_id for c in pile if c.name == "Manaphy"] == ["swsh9-041"]
    assert [c.catalog_id for c in pile if c.name == "Lillie's Poké Doll"] == ["sm12-197"]
    assert [c.hp for c in pile if c.name == "Lillie's Poké Doll"] == [30]
    assert fallback_named("Mime Jr.").catalog_id == "sv04.5-031"
    assert fallback_named("Mime Jr.").attacks[0].name == "Mimed Games"
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


def test_mill_card_art_is_the_named_print_not_the_neighbor():
    """sv01-084 is Ralts and sv04-163 is Earthen Vessel. Mill must not wear those pictures."""
    colress = fallback_named("Colress's Tenacity")
    assert colress.catalog_id == "sv06.5-057"
    assert "sv06.5/057" in (colress.image or "")
    assert "sv01/084" not in (colress.image or "")
    turbo = fallback_named("Double Turbo Energy")
    assert turbo.catalog_id == "swsh9-151"
    assert "swsh9/151" in (turbo.image or "")
    assert "sv04/163" not in (turbo.image or "")
    loaded = load_seed_deck("mill")
    colress_cards = [c for c in loaded["cards"] if c["name"] == "Colress's Tenacity"]
    turbo_cards = [c for c in loaded["cards"] if c["name"] == "Double Turbo Energy"]
    assert len(colress_cards) == 4
    assert len(turbo_cards) == 4
    assert {c["catalog_id"] for c in colress_cards} == {"sv06.5-057"}
    assert {c["catalog_id"] for c in turbo_cards} == {"swsh9-151"}
    assert all("sv06.5/057" in c["image"] for c in colress_cards)
    assert all("swsh9/151" in c["image"] for c in turbo_cards)
    assert all("sv01/084" not in c["image"] for c in colress_cards)
    assert all("sv04/163" not in c["image"] for c in turbo_cards)


def test_existing_mill_seed_replaces_ralts_and_earthen_vessel_art(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, init_db

    init_db()
    with connect() as conn:
        raw = conn.execute("SELECT cards_json FROM decks WHERE id='seed-mill'").fetchone()["cards_json"]
        cards = json.loads(raw)
        for card in cards:
            if card.get("name") == "Colress's Tenacity":
                card["catalog_id"] = "sv01-084"
                card["image"] = "https://assets.tcgdex.net/en/sv/sv01/084/low.webp"
            elif card.get("name") == "Double Turbo Energy":
                card["catalog_id"] = "sv04-163"
                card["image"] = "https://assets.tcgdex.net/en/sv/sv04/163/low.webp"
        conn.execute(
            "UPDATE decks SET cards_json=? WHERE id='seed-mill'",
            (json.dumps(cards),),
        )
    init_db()
    with connect() as conn:
        stored = json.loads(
            conn.execute("SELECT cards_json FROM decks WHERE id='seed-mill'").fetchone()["cards_json"]
        )
    colress = next(c for c in stored if c.get("name") == "Colress's Tenacity")
    turbo = next(c for c in stored if c.get("name") == "Double Turbo Energy")
    assert colress["catalog_id"] == "sv06.5-057"
    assert "sv06.5/057" in colress["image"]
    assert "sv01/084" not in colress["image"]
    assert turbo["catalog_id"] == "swsh9-151"
    assert "swsh9/151" in turbo["image"]
    assert "sv04/163" not in turbo["image"]
    assert "Active Pokémon" in (turbo.get("text") or "")


def test_mill_seed_special_energy_keeps_printed_text():
    assert not _is_basic_energy_name("Ignition Energy")
    assert not _is_basic_energy_name("Reversal Energy")
    loaded = load_seed_deck("mill")
    ignition = [c for c in loaded["cards"] if c["name"] == "Ignition Energy"]
    reversal = [c for c in loaded["cards"] if c["name"] == "Reversal Energy"]
    assert len(ignition) == 4
    assert len(reversal) == 4
    assert {c["catalog_id"] for c in ignition} == {"me02-124"}
    assert {c["catalog_id"] for c in reversal} == {"sv02-192"}
    assert all(c["stage"] == "Special" and c["energy_type"] == "Colorless" for c in ignition + reversal)
    ign_kinds = {e["kind"] for e in parse_energy_effects(ignition[0]["text"])}
    assert ign_kinds >= {"provides_colorless_if_evolution", "discard_attached_end_of_turn"}
    rev_kinds = {e["kind"] for e in parse_energy_effects(reversal[0]["text"])}
    assert "provides_any_when" in rev_kinds
    assert ignition[0]["text"] == fallback_named("Ignition Energy").text
    assert reversal[0]["text"] == fallback_named("Reversal Energy").text


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
    prefer = board.game._pokemon_search_prefer(me, "a")
    assert prefer[0] == "Pichu"
    assert prefer.index("Wiglett") < prefer.index("Wugtrio")
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
    board.game._recycle_trainer_from_discard(me)
    assert me.hand == []
    assert [me.card(i).name for i in me.discard] == ["Neutralization Zone"]

    both = _Board("mill")
    me = both.seat("a", active=("Wiglett", []), discard=["Neutralization Zone", "Switch"])
    both.game._recycle_trainer_from_discard(me)
    assert [me.card(i).name for i in me.hand] == ["Switch"]
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


def _grant(board: _Board, who: str, name: str) -> int:
    player = board.game.players[who]
    player.cards.append(fallback_named(name))
    idx = len(player.cards) - 1
    board._used[who].add(idx)
    return idx


def test_twisting_strike_blocks_effects_done_to_that_wiglett():
    board = _Board("balanced")
    me = board.seat("a", active=("Wiglett", ["Water Energy"]), bench=("Wiglett",))
    tool = _grant(board, "a", "Air Balloon")
    me.active.tool = tool
    me.active.prevent_attack_damage = True
    foe = board.seat("b", active=("Wiglett", []))

    zap = _grant(board, "b", "Team Rocket's Zapdos")
    foe.active = Pokemon(card_i=zap, energy=[_grant(board, "b", "Lightning Energy"), _grant(board, "b", "Lightning Energy")])
    board.game._attack(foe, me, "b")
    assert me.active.damage == 0
    assert [me.card(i).name for i in me.active.energy] == ["Water Energy"]
    assert me.bench[0].energy == []

    dun = _grant(board, "b", "Dunsparce")
    foe.active = Pokemon(card_i=dun, energy=[_grant(board, "b", "Water Energy")])
    board.game._attack(foe, me, "b")
    assert me.active.status == 0
    assert me.active.damage == 0

    zek = _grant(board, "b", "Zekrom")
    foe.active = Pokemon(card_i=zek, energy=[_grant(board, "b", "Lightning Energy")])
    board.game._attack(foe, me, "b")
    assert me.active.tool == tool
    assert me.active.damage == 0
    assert "Air Balloon" not in [me.card(i).name for i in me.discard]


def test_shield_follows_that_pokemon_and_demolish_still_ignores_it():
    board = _Board("balanced")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    shielded = me.bench[0]
    shielded.prevent_attack_damage = True
    board.game._add_attack_damage(me, shielded, 30)
    assert shielded.damage == 0
    board.game._add_attack_damage(me, me.active, 30)
    assert me.active.damage == 30
    board.game._add_attack_damage(me, shielded, 140, ignore_effects=True)
    assert shielded.damage == 140


def test_undersea_still_mills_when_the_defender_is_shielded():
    board = _Board("mill")
    me = board.seat(
        "a",
        active=("Wugtrio", ["Water Energy", "Water Energy", "Water Energy"]),
    )
    foe = board.seat("b", active=("Wiglett", []))
    foe.active.prevent_attack_damage = True
    before = len(foe.deck)
    board.game.rng.random = _coins(0.0, 0.0, 0.0)
    board.game._attack(me, foe, "a")
    assert len(foe.deck) == before - 9
    assert foe.active.damage == 0


_IGNITION = (
    "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. "
    "As long as this card is attached to a Pokémon, it provides Colorless Energy. "
    "If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."
)


def _energy_board() -> _Board:
    names = [
        "Pichu",
        "Wiglett",
        "Wiglett",
        "Wugtrio",
        "Wugtrio",
        "Victini",
        "Ignition Energy",
        "Ignition Energy",
        "Reversal Energy",
        "Water Energy",
        "Water Energy",
        "Double Turbo Energy",
        "Fighting Energy",
    ]
    while len(names) < 40:
        names.append("Water Energy")
    board = _Board("mill")
    board.game = Game(
        build_fallback_deck(names),
        build_fallback_deck(list(names)),
        standard_60_rules(),
        StrategySpec.from_dict("mill"),
        StrategySpec.from_dict("mill"),
        Random(1),
        trace=True,
    )
    board._used = {"a": set(), "b": set()}
    return board


def test_ignition_energy_pays_three_colorless_on_an_evolution_and_then_leaves():
    card = fallback_named("Ignition Energy")
    assert card.catalog_id == "me02-124"
    assert card.text == _IGNITION
    parsed = parse_energy_effects(card.text)
    assert {"kind": "provides_colorless_if_evolution", "basic_count": 1, "evolution_count": 3} in parsed
    assert {"kind": "discard_attached_end_of_turn"} in parsed
    assert energy_provided(card, host=fallback_named("Wiglett")) == ["Colorless"]
    assert energy_provided(card, host=fallback_named("Wugtrio")) == ["Colorless", "Colorless", "Colorless"]

    board = _energy_board()
    me = board.seat("a", active=("Wugtrio", []), hand=["Ignition Energy", "Water Energy"])
    foe = board.seat("b", active=("Wiglett", []))
    board.game._attach_energy(me, "a")
    assert [me.card(i).name for i in me.active.energy] == ["Ignition Energy"]
    undersea = next(a for a in me.card(me.active.card_i).attacks if a.name == "Undersea Tunnel")
    assert board.game._energy_pool(me, me.active) == ["Colorless", "Colorless", "Colorless"]
    assert can_pay_energy(
        board.game._energy_pool(me, me.active), board.game._attack_cost(me, me.active, undersea)
    )
    board.game._expire_turn_markers("a")
    assert me.active.energy == []
    assert [me.card(i).name for i in me.discard] == ["Ignition Energy"]
    assert board.game.events.get("discard_attached_end_of_turn") == 1
    assert foe.active is not None


def test_wall_energy_stacks_on_the_bench_line():
    board = _energy_board()
    me = board.seat(
        "a",
        active=("Pichu", []),
        bench=("Wiglett", "Wiglett"),
        hand=["Double Turbo Energy", "Water Energy"],
    )
    me.bench[1].energy.append(board.take("a", "Water Energy"))
    board.seat("b", active=("Wugtrio", []))
    board.game._attach_energy(me, "a")
    assert [me.card(i).name for i in me.active.energy] == []
    assert [me.card(i).name for i in me.bench[0].energy] == []
    assert [me.card(i).name for i in me.bench[1].energy] == ["Water Energy", "Double Turbo Energy"]


def test_ignition_on_wiglett_is_one_colorless_and_mill_attaches_water_instead():
    board = _energy_board()
    me = board.seat("a", active=("Wiglett", []), hand=["Ignition Energy", "Water Energy"])
    board.seat("b", active=("Wugtrio", []))
    board.game._attach_energy(me, "a")
    assert [me.card(i).name for i in me.active.energy] == ["Water Energy"]
    twist = next(a for a in me.card(me.active.card_i).attacks if a.name == "Twisting Strike")
    assert board.game._attack_cost(me, me.active, twist) == ["Water"]


def test_reversal_energy_pays_undersea_while_behind_and_stays():
    board = _energy_board()
    me = board.seat("a", active=("Wugtrio", []), hand=["Reversal Energy", "Ignition Energy"])
    foe = board.seat("b", active=("Wiglett", []))
    me.prizes = [0, 1, 2, 3, 4, 5]
    foe.prizes = [0, 1, 2, 3]
    board.game._attach_energy(me, "a")
    assert [me.card(i).name for i in me.active.energy] == ["Reversal Energy"]
    assert board.game._energy_pool(me, me.active) == ["Any", "Any", "Any"]
    board.game._expire_turn_markers("a")
    assert [me.card(i).name for i in me.active.energy] == ["Reversal Energy"]


def test_reversal_energy_is_one_colorless_when_prizes_are_tied():
    card = fallback_named("Reversal Energy")
    assert energy_provided(card, prizes_behind=False, host=fallback_named("Wugtrio")) == ["Colorless"]
    assert energy_provided(card, prizes_behind=True, host=fallback_named("Wugtrio")) == ["Any", "Any", "Any"]
    assert energy_provided(card, prizes_behind=True, host=fallback_named("Wiglett")) == ["Colorless"]


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


def test_mill_evolves_the_wiglett_that_is_already_legal():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    board.game.turn = 5
    board.game.first = "b"
    me.active.played_turn = board.game.turn
    me.bench[0].played_turn = 0
    me.hand = [board.take("a", "Wugtrio")]
    me.deck = []
    board.game._evolve(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wiglett"
    assert me.card(me.bench[0].card_i).name == "Wugtrio"


def test_wally_evolves_the_wiglett_played_this_turn_then_ignition_pays():
    printed = fallback_named("Wally")
    text = (printed.text or "").lower()
    parsed = parse_trainer_effects(printed.text or "")
    assert parsed[0]["kind"] == "wally_evolve"
    assert parsed[0]["first_turn_ok"] is True
    assert parsed[0]["just_played_ok"] is True
    assert "put into play this turn" in text
    assert "first turn" in text

    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    me.active.played_turn = board.game.turn
    wally = _grant(board, "a", "Wally")
    ignition = _grant(board, "a", "Ignition Energy")
    handi = board.take("a", "Team Rocket's Handiwork")
    me.hand = [wally, ignition, handi]
    me.deck = [board.take("a", "Wugtrio"), board.take("a", "Wugtrio")]
    board.game._play_trainers(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wugtrio"
    assert board.game.events.get("wally") == 1
    board.game._attach_energy(me, "a")
    assert [me.card(i).name for i in me.active.energy] == ["Ignition Energy"]
    assert board.game._mill_can_pay(me, me.active)


def test_wally_waits_when_the_hand_cannot_pay_and_when_evolve_is_already_legal():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    me.active.played_turn = board.game.turn
    wally = _grant(board, "a", "Wally")
    colress = _grant(board, "a", "Colress's Tenacity")
    me.hand = [wally, colress]
    me.deck = [board.take("a", "Wugtrio")]
    board.game._play_trainers(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wiglett"
    assert board.game.events.get("colress") == 1

    later = _Board("mill")
    me = later.seat("a", active=("Wiglett", []))
    foe = later.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    later.game.turn = 5
    later.game.first = "b"
    me.active.played_turn = 0
    wally = _grant(later, "a", "Wally")
    ignition = _grant(later, "a", "Ignition Energy")
    handi = later.take("a", "Team Rocket's Handiwork")
    trio = later.take("a", "Wugtrio")
    me.hand = [wally, ignition, handi, trio]
    me.deck = [later.take("a", "Wugtrio")]
    later.game._play_trainers(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wiglett"
    assert "wally" not in later.game.events


def test_wally_fetches_wugtrio_onto_a_wiglett_that_can_already_pay():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", ["Water Energy", "Water Energy", "Water Energy"]))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    board.game.turn = 5
    board.game.first = "b"
    me.active.played_turn = 0
    wally = _grant(board, "a", "Wally")
    handi = board.take("a", "Team Rocket's Handiwork")
    me.hand = [wally, handi]
    me.deck = [board.take("a", "Wugtrio")]
    board.game._play_trainers(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wugtrio"
    assert board.game.events.get("wally") == 1
    assert board.game._mill_can_pay(me, me.active)


def test_level_ball_plays_before_nest_ball_when_wugtrio_is_in_the_deck():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    level = board.take("a", "Level Ball")
    nest = board.take("a", "Nest Ball")
    trio = board.take("a", "Wugtrio")
    me.hand = [nest, level]
    me.deck = [trio]
    assert me.card(board.game._pick_trainer(me)).name == "Level Ball"
    board.game._play_trainers(me, foe, "a")
    assert [me.card(i).name for i in me.hand] == ["Wugtrio"]


def test_level_ball_finds_wugtrio_ahead_of_a_wall_once_wiglett_is_out():
    board = _Board("mill")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    pichu = _grant(board, "a", "Pichu")
    trio = board.take("a", "Wugtrio")
    me.deck = [pichu, trio]
    me.hand = []
    prefer = board.game._pokemon_search_prefer(me, "a")
    assert prefer[0] == "Wugtrio"
    board.game._resolve_trainer(me, foe, fallback_named("Level Ball"), "a")
    assert [me.card(i).name for i in me.hand] == ["Wugtrio"]
    assert [me.card(i).name for i in me.deck] == ["Pichu"]


def test_survival_brace_attaches_to_a_full_wugtrio():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    trio = board.take("a", "Wugtrio")
    pichu = _grant(board, "a", "Pichu")
    brace = _grant(board, "a", "Survival Brace")
    me.active = Pokemon(card_i=pichu)
    me.bench = [Pokemon(card_i=trio)]
    me.hand = [brace]
    board.game._play_trainers(me, foe, "a")
    assert me.bench[0].tool == brace
    assert me.active.tool is None

    me.bench[0].tool = None
    me.bench[0].damage = 10
    me.hand = [brace]
    me.discard = [i for i in me.discard if i != brace]
    board.game._play_trainers(me, foe, "a")
    assert me.bench[0].tool is None
    assert brace in me.hand


def test_junk_arm_spends_dead_nests_on_level_ball_and_keeps_energy():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 8)
    pichu = _grant(board, "a", "Pichu")
    me.bench = [Pokemon(card_i=pichu)]
    arm = _grant(board, "a", "Junk Arm")
    nest = _grant(board, "a", "Nest Ball")
    nest_b = _grant(board, "a", "Nest Ball")
    level = board.take("a", "Level Ball")
    energy = board.take("a", "Water Energy")
    trio = board.take("a", "Wugtrio")
    me.hand = [arm, nest, nest_b, energy]
    me.discard = [level]
    me.deck = [trio]
    board.game._play_trainers(me, foe, "a")
    assert board.game.events.get("junk_arm") == 1
    assert energy in me.hand
    assert [me.card(i).name for i in me.hand if me.card(i).name == "Wugtrio"] == ["Wugtrio"]
    assert nest in me.discard and nest_b in me.discard


def test_junk_arm_waits_when_the_hand_cannot_pay_two_discards():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    arm = _grant(board, "a", "Junk Arm")
    energy = board.take("a", "Water Energy")
    wally = _grant(board, "a", "Wally")
    level = board.take("a", "Level Ball")
    me.hand = [arm, energy, wally]
    me.discard = [level]
    me.deck = [board.take("a", "Wugtrio")]
    board.game._play_trainers(me, foe, "a")
    assert "junk_arm" not in board.game.events
    assert energy in me.hand
    assert arm in me.hand


def test_opening_cleffa_does_not_need_the_opponent_seat():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []))
    cleffa = _grant(board, "a", "cleffa hgss")
    arm = _grant(board, "a", "Junk Arm")
    me.hand = [cleffa, arm]
    del board.game.players
    # A wall match benches Cleffa. Eeeeeeek still does not fire while Junk Arm is a keeper.
    assert board.game._wants_in_play(me, me.card(cleffa), board.game.strats["a"]) is True
    assert board.game._mill_wants_eeeeeeek(me) is False


def test_cleffa_stays_in_the_deck_against_phantom_dive():
    board = _Board("mill", "phantom")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    cleffa = _grant(board, "a", "cleffa hgss")
    me.hand = [cleffa]
    me.deck = [board.take("a", "Water Energy")]
    board.game.turn = 4
    board.game._play_basics(me)
    assert cleffa in me.hand


def test_cleffa_eeeeeeek_when_the_hand_cannot_continue_undersea():
    printed = fallback_named("cleffa hgss")
    assert printed.hp == 30
    assert any(atk.name == "Eeeeeeek" for atk in printed.attacks)
    assert any(abi.name == "Sweet Sleeping Face" for abi in printed.abilities)
    parsed = parse_effects(next(atk.text for atk in printed.attacks if atk.name == "Eeeeeeek"))
    draw = next(e for e in parsed if e.get("kind") == "shuffle_hand_then_draw")
    assert draw["amount"] == 6

    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    pichu = _grant(board, "a", "Pichu")
    cleffa = _grant(board, "a", "cleffa hgss")
    hammer = _grant(board, "a", "Crushing Hammer")
    hammer_b = _grant(board, "a", "Crushing Hammer")
    me.active = Pokemon(card_i=pichu)
    me.bench = [Pokemon(card_i=cleffa)]
    me.hand = [hammer, hammer_b]
    me.deck = [board.take("a", "Water Energy") for _ in range(8)]
    board.game.turn = 4
    board.game.first = "b"
    board.game.events["used_playground_a"] = 1
    board.game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Cleffa"
    board.game._attack(me, foe, "a")
    assert board.game.events.get("eeeeeeek_shuffle") == 1
    assert me.active.status & ST_ASLEEP
    assert len(me.hand) == 6


def test_cleffa_is_benched_in_a_wall_match_while_the_hand_can_still_pay():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    cleffa = _grant(board, "a", "cleffa hgss")
    energy = board.take("a", "Water Energy")
    me.hand = [cleffa, energy]
    board.game.turn = 4
    board.game._play_basics(me)
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Cleffa"]
    assert energy in me.hand
    assert board.game._mill_wants_eeeeeeek(me) is False


def test_cleffa_waits_for_wave_veil_against_bench_damage():
    board = _Board("mill", "starmie")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(board, "b", "Mega Starmie ex")
    cleffa = _grant(board, "a", "cleffa hgss")
    me.hand = [cleffa]
    board.game.turn = 4
    board.game._play_basics(me)
    assert cleffa in me.hand

    manaphy = _grant(board, "a", "Manaphy")
    me.bench.append(Pokemon(card_i=manaphy))
    board.game._play_basics(me)
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy", "Cleffa"]


def test_cleffa_stays_in_hand_when_manaphy_cannot_stop_bench_counters():
    board = _Board("mill", "phantom")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(board, "b", "Dragapult ex")
    cleffa = _grant(board, "a", "cleffa hgss")
    manaphy = _grant(board, "a", "Manaphy")
    me.bench.append(Pokemon(card_i=manaphy))
    me.hand = [cleffa]
    board.game.turn = 4
    board.game._play_basics(me)
    assert cleffa in me.hand

    wall = _Board("mill", "demolish")
    host = wall.seat("a", active=("Wiglett", []))
    wall.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(wall, "b", "Drifblim")
    stuck = _grant(wall, "a", "cleffa hgss")
    shield = _grant(wall, "a", "Manaphy")
    host.bench.append(Pokemon(card_i=shield))
    host.hand = [stuck]
    wall.game.turn = 4
    wall.game._play_basics(host)
    assert stuck in host.hand


def test_poffin_benches_manaphy_then_cleffa_against_bench_damage():
    board = _Board("mill", "starmie")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(board, "b", "Mega Starmie ex")
    manaphy = _grant(board, "a", "Manaphy")
    cleffa = _grant(board, "a", "cleffa hgss")
    spare = _grant(board, "a", "Wiglett")
    me.deck = [manaphy, cleffa, spare]
    me.hand = []
    board.game._bench_basic_from_deck(me, "a", count=2, max_hp=70, source="poffin")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy", "Cleffa"]
    assert spare in me.deck


def test_poffin_benches_pichu_then_cleffa_in_a_wall_match():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    pichu = _grant(board, "a", "Pichu")
    cleffa = _grant(board, "a", "cleffa hgss")
    mime = _grant(board, "a", "mime jr. col")
    me.deck = [mime, cleffa, pichu]
    me.hand = []
    board.game._bench_basic_from_deck(me, "a", count=2, max_hp=70, source="poffin")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Pichu", "Cleffa"]
    assert mime in me.deck


def test_poffin_without_the_veil_package_still_takes_pichu_then_wiglett():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []))
    board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    pichu = _grant(board, "a", "Pichu")
    mime = _grant(board, "a", "mime jr. col")
    spare = _grant(board, "a", "Wiglett")
    me.deck = [spare, mime, pichu]
    me.hand = []
    board.game._bench_basic_from_deck(me, "a", count=2, max_hp=70, source="poffin")
    # One Sweet Sleeping Face. The second body is Wiglett, and Mime Jr. stays in the deck.
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Pichu", "Wiglett"]
    assert mime in me.deck


def test_level_ball_still_finds_wugtrio_when_manaphy_and_cleffa_are_in_the_deck():
    board = _Board("mill", "starmie")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(board, "b", "Mega Starmie ex")
    trio = board.take("a", "Wugtrio")
    manaphy = _grant(board, "a", "Manaphy")
    cleffa = _grant(board, "a", "cleffa hgss")
    me.deck = [manaphy, cleffa, trio]
    me.hand = []
    board.game._resolve_trainer(me, foe, fallback_named("Level Ball"), "a")
    assert [me.card(i).name for i in me.hand] == ["Wugtrio"]


def test_poffin_plays_before_nest_ball_when_wave_veil_is_missing():
    board = _Board("mill", "starmie")
    me = board.seat("a", active=("Wiglett", []))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    _grant(board, "b", "Mega Starmie ex")
    nest = board.take("a", "Nest Ball")
    poffin = _grant(board, "a", "Buddy-Buddy Poffin")
    level = board.take("a", "Level Ball")
    manaphy = _grant(board, "a", "Manaphy")
    cleffa = _grant(board, "a", "cleffa hgss")
    trio = board.take("a", "Wugtrio")
    me.hand = [nest, level, poffin]
    me.deck = [cleffa, manaphy, trio]
    assert me.card(board.game._pick_trainer(me)).name == "Buddy-Buddy Poffin"
    board.game._play_trainers(me, foe, "a")
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy", "Cleffa"]
    assert [me.card(i).name for i in me.hand if me.card(i).name == "Wugtrio"] == ["Wugtrio"]


def test_paid_wugtrio_comes_up_ahead_of_cleffa():
    board = _Board("mill", "demolish")
    me = board.seat("a", active=("Wiglett", []), bench=("Wiglett",))
    foe = board.seat("b", active=("Wugtrio", []), deck=["Water Energy"] * 4)
    pichu = _grant(board, "a", "Pichu")
    cleffa = _grant(board, "a", "cleffa hgss")
    trio = board.take("a", "Wugtrio")
    fuels = [board.take("a", "Water Energy") for _ in range(3)]
    me.active = Pokemon(card_i=pichu)
    me.bench = [Pokemon(card_i=cleffa), Pokemon(card_i=trio, energy=fuels)]
    me.hand = [_grant(board, "a", "Crushing Hammer")]
    me.deck = [board.take("a", "Water Energy")]
    board.game.turn = 4
    board.game.first = "b"
    board.game.events["used_playground_a"] = 1
    board.game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Wugtrio"
