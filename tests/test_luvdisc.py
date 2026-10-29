"""Paldea Evolved Luvdisc. Matching and Water Pulse use the printed sentences.

Matching searches for up to 2 Supporter cards. Water Pulse costs Water and
puts the opponent's Active Pokémon to sleep. Slumbering Forest then flips 2
coins between turns. The roast list itself stays the locked 60 until a
greedy search says otherwise.
"""

from app.engine.effects import parse_effects
from app.engine.game import ST_ASLEEP, Pokemon
from app.seed_data import build_roast_deck, fallback_named
from tests.test_chandelure_roast import _game, _pull, _ready_turn, _reclaim

MATCHING = (
    "Search your deck for up to 2 Supporter cards, reveal them, and put them into your hand. "
    "Then, shuffle your deck."
)
PULSE = "Your opponent's Active Pokémon is now Asleep."


def test_matching_count_comes_from_the_printed_sentence():
    parsed = parse_effects(MATCHING)
    assert parsed == [{"kind": "search_supporter", "count": 2}]
    four = parse_effects(MATCHING.replace("up to 2", "up to 4"))
    assert {"kind": "search_supporter", "count": 4} in four
    assert not any(e.get("kind") == "search_supporter" and e.get("count") == 2 for e in four)


def test_water_pulse_sleeps_the_opponent():
    parsed = parse_effects(PULSE)
    assert parsed == [{"kind": "status", "status": "asleep", "coin": False}]
    assert "target" not in parsed[0]


def test_luvdisc_is_the_paldea_evolved_print():
    card = fallback_named("Luvdisc")
    assert card.catalog_id == "sv02-047"
    assert card.hp == 70
    assert card.retreat == 1
    assert card.types == ["Water"]
    assert [weak["type"] for weak in card.weaknesses] == ["Lightning"]
    matching = next(atk for atk in card.attacks if atk.name == "Matching")
    pulse = next(atk for atk in card.attacks if atk.name == "Water Pulse")
    assert matching.cost == ["Colorless"]
    assert matching.damage == 0
    assert matching.text == MATCHING
    assert matching.effects == [{"kind": "search_supporter", "count": 2}]
    assert pulse.cost == ["Water"]
    assert pulse.damage == 20
    assert pulse.text == PULSE
    assert pulse.effects == [{"kind": "status", "status": "asleep", "coin": False}]
    names = [c.name for c in build_roast_deck()]
    assert names.count("Luvdisc") == 0
    assert names.count("Fire Energy") == 7
    assert names.count("Water Energy") == 0


def _board(game):
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    _ready_turn(game)
    assert foe.active is not None
    foe.active.status = 0
    game.stadium_name = None
    game.stadium_effects = []
    me.discard.extend(me.prizes)
    me.prizes.clear()
    return me, foe


def _idx(me, name: str) -> int:
    try:
        return _pull(me, name)
    except AssertionError:
        card = fallback_named(name)
        me.cards.append(card)
        return len(me.cards) - 1


def test_matching_takes_dawn_then_petrel():
    game = _game()
    me, foe = _board(game)
    luv = _idx(me, "Luvdisc")
    fire = _idx(me, "Fire Energy")
    lit = _idx(me, "Litwick")
    dawn = _idx(me, "Dawn")
    petrel = _idx(me, "Team Rocket's Petrel")
    lamp = _idx(me, "Lampent")
    chand = _idx(me, "Chandelure")
    bts = _idx(me, "Broken Time-Space")
    me.hand.clear()
    me.deck = [dawn, petrel, lamp, chand, bts]
    me.active = Pokemon(card_i=luv, energy=[fire], played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0)]
    assert game._roast_wants_playground(me, "a") is False
    assert game._roast_wants_matching(me, "a") is True
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Matching"
    game._attack(me, foe, "a")
    found = [me.card(i).name for i in me.hand]
    assert found.count("Dawn") == 1
    assert found.count("Team Rocket's Petrel") == 1
    assert game.events.get("luvdisc_matching", 0) == 2
    assert not (foe.active.status & ST_ASLEEP)


def test_water_pulse_is_the_attack_when_no_supporter_is_useful():
    game = _game()
    me, foe = _board(game)
    luv = _idx(me, "Luvdisc")
    water = _idx(me, "Water Energy")
    me.hand.clear()
    me.deck = []
    me.active = Pokemon(card_i=luv, energy=[water], played_turn=0)
    me.bench = []
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Water Pulse"
    game._attack(me, foe, "a")
    assert foe.active.status & ST_ASLEEP
    assert game.events.get("water_pulse", 0) == 1


def test_fire_energy_pays_matching_and_not_water_pulse():
    game = _game()
    me, foe = _board(game)
    luv = _idx(me, "Luvdisc")
    fire = _idx(me, "Fire Energy")
    me.hand.clear()
    me.deck = []
    me.active = Pokemon(card_i=luv, energy=[fire], played_turn=0)
    assert game._choose_attack(me, foe, game.strats["a"]) is None
    assert not (foe.active.status & ST_ASLEEP)


def test_celebi_still_mills_when_luvdisc_is_benched():
    game = _game()
    me, foe = _board(game)
    celebi = _idx(me, "Celebi ◇")
    luv = _idx(me, "Luvdisc")
    water = _idx(me, "Water Energy")
    lit = _idx(me, "Litwick")
    lamp = _idx(me, "Lampent")
    chand = _idx(me, "Chandelure")
    evolved = Pokemon(card_i=chand, played_turn=0, underneath=[lit, lamp])
    me.hand.clear()
    me.deck = []
    me.active = Pokemon(card_i=celebi, energy=[water], played_turn=0)
    me.bench = [evolved, Pokemon(card_i=luv, played_turn=0)]
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Time Distortion"


def test_water_attaches_to_luvdisc_until_the_mill_is_close():
    game = _game()
    me, _foe = _board(game)
    celebi = _idx(me, "Celebi ◇")
    luv = _idx(me, "Luvdisc")
    water = _idx(me, "Water Energy")
    lamp = _idx(me, "Lampent")
    me.hand = [water]
    me.deck = []
    me.active = Pokemon(card_i=lamp, played_turn=0)
    me.bench = [
        Pokemon(card_i=celebi, played_turn=0),
        Pokemon(card_i=luv, played_turn=0),
    ]
    game._roast_attach(me)
    assert water in me.bench[1].energy
    assert me.bench[0].energy == []

    game = _game()
    me, _foe = _board(game)
    celebi = _idx(me, "Celebi ◇")
    luv = _idx(me, "Luvdisc")
    water = _idx(me, "Water Energy")
    lit = _idx(me, "Litwick")
    lamp = _idx(me, "Lampent")
    chand = _idx(me, "Chandelure")
    me.hand = [water]
    me.deck = []
    me.active = Pokemon(card_i=luv, played_turn=0)
    me.bench = [
        Pokemon(card_i=celebi, played_turn=0),
        Pokemon(card_i=chand, played_turn=0, underneath=[lit, lamp]),
    ]
    game._roast_attach(me)
    assert water in me.bench[0].energy
    assert me.active.energy == []


def test_playground_saves_slots_for_celebi_and_luvdisc():
    game = _game()
    me, foe = _board(game)
    pichu = _idx(me, "Pichu")
    celebi = _idx(me, "Celebi ◇")
    luv = _idx(me, "Luvdisc")
    litwicks = [_idx(me, "Litwick") for _ in range(4)]
    me.hand.clear()
    me.deck = litwicks + [celebi, luv]
    me.bench = []
    me.active = Pokemon(card_i=pichu, played_turn=0)
    foe.deck = []
    foe.bench.clear()
    game._playground(me, foe, "a", user_first=True)
    names = [me.card(mon.card_i).name for mon in me.bench]
    assert names == ["Litwick", "Litwick", "Litwick", "Celebi ◇", "Luvdisc"]


def test_forest_score_rises_only_for_the_sleep_package():
    game = _game()
    me, _foe = _board(game)
    forest = _idx(me, "Slumbering Forest")
    me.hand = [forest]
    me.deck = []
    me.active = Pokemon(card_i=_idx(me, "Pichu"), played_turn=0)
    assert game._roast_trainer_score(me, "a", me.card(forest)) == 70

    game = _game()
    me, foe = _board(game)
    forest = _idx(me, "Slumbering Forest")
    luv = _idx(me, "Luvdisc")
    water = _idx(me, "Water Energy")
    me.hand = [forest, water]
    me.deck = []
    me.active = Pokemon(card_i=luv, played_turn=0)
    me.bench = []
    foe.active.status = 0
    assert game._roast_trainer_score(me, "a", me.card(forest)) == 168

    bts = _idx(me, "Broken Time-Space")
    lit = _idx(me, "Litwick")
    lamp = _idx(me, "Lampent")
    me.hand = [forest, water, bts, lamp]
    me.deck = []
    me.bench = [Pokemon(card_i=lit, played_turn=0)]
    assert game._roast_bts_stays(me, "a") is True
    assert game._roast_trainer_score(me, "a", me.card(forest)) == -1
