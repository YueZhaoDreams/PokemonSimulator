"""Printed H/G-plus attacks from the live carpet lists. Texts are the DB wordings."""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def test_h_prints_parse_from_database_wording():
    fickle = parse_effects(
        "If your opponent doesn't have exactly 3 or 4 Prize cards remaining, this attack does nothing.",
        "120",
    )
    assert fickle == [{"kind": "require_opponent_prizes", "values": [3, 4]}]
    deep = parse_effects("Put up to 2 basic Energy cards from your discard pile into your hand.")
    assert deep == [{"kind": "recycle_energy_from_discard", "count": 2}]
    nurse = parse_effects(
        "Search your deck for a card that evolves from 1 of your Pokémon and put it onto that "
        "Pokémon to evolve it. Then, shuffle your deck."
    )
    assert nurse == [{"kind": "evolve_from_deck"}]
    thunder = parse_effects(
        "This attack does 20 more damage for each of your opponent's Benched Pokémon.",
        "20",
    )
    assert {"kind": "benched_pokemon_bonus", "per": 20, "sides": "opponent"} in thunder
    fall = parse_effects(
        "If you have at least 4 {L} Energy in play, this attack does 90 more damage.",
        "30",
    )
    assert {
        "kind": "energy_in_play_bonus",
        "count": 4,
        "energy_type": "Lightning",
        "bonus": 90,
    } in fall
    pressure = parse_effects(
        "If your opponent has 3 or fewer Prize cards remaining, this attack does 50 more damage.",
        "10",
    )
    assert {
        "kind": "opponent_prize_bonus",
        "prizes": 3,
        "bonus": 50,
        "op": "at_most",
    } in pressure
    hider = parse_ability_effects(
        "If any damage is done to this Pokémon by attacks, flip a coin. If heads, prevent that damage."
    )
    assert hider == [{"kind": "coin_prevent_attack_damage"}]
    jam = parse_effects(
        "You may move an Energy from your opponent's Active Pokémon to 1 of their Benched Pokémon.",
        "30",
    )
    assert {"kind": "move_opp_active_energy_to_bench"} in jam
    claw = parse_effects("Flip a coin. If tails, this attack does nothing.", "30")
    assert claw == [{"kind": "coin_whiff"}]


def test_gplus_alias_uses_g_strategy():
    spec = StrategySpec.from_dict("gplus")
    assert spec.name == "g"
    assert "Indeedee" in spec.protect
    assert "Hop's Cramorant" in spec.closers
    assert "Plusle" in spec.protect
    assert "Kecleon" in spec.protect
    assert "Iron Boulder" in spec.protect


def test_gplus_fallback_prints_match_live_db_wording():
    nurse = fallback_named("Indeedee")
    assert nurse.catalog_id == "sv01-153"
    assert [a.name for a in nurse.attacks] == ["Expert Nurturer", "Hypnoblast"]
    assert any(e.get("kind") == "evolve_from_deck" for e in nurse.attacks[0].effects)
    deep = fallback_named("Relicanth")
    assert any(e.get("kind") == "recycle_energy_from_discard" for e in deep.attacks[0].effects)
    spit = fallback_named("Hop's Cramorant")
    assert spit.attacks[0].name == "Fickle Spitting"
    assert spit.attacks[0].effects == [{"kind": "require_opponent_prizes", "values": [3, 4]}]


def _plus_game():
    a = build_fallback_deck(
        ["Clefairy"] * 4
        + ["Ledyba", "Ledian", "Starly", "Staravia", "Staraptor", "Indeedee", "Relicanth", "Emolga", "Hop's Cramorant", "Iron Boulder", "Plusle", "Kecleon"]
        + ["Potion", "Energy Retrieval"]
        + ["Psychic Energy"] * 10
        + ["Hop"] * 4
        + ["Cubone"] * 6
    )
    b = build_fallback_deck(
        ["Starly", "Clefairy", "Cornerstone Mask Ogerpon ex"] + ["Psychic Energy"] * 8 + ["Hop"] * 4 + ["Cubone"] * 15
    )
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict("party"),
        Random(1),
        trace=True,
    )


def test_g_benches_iron_boulder_with_clefairy_active():
    game = _plus_game()
    me = game.players["a"]
    boulder = next(i for i, c in enumerate(me.cards) if c.name == "Iron Boulder")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=clef, played_turn=0)
    me.bench = []
    me.hand = [boulder]
    game._play_basics(me)
    names = {me.card(m.card_i).name for m in me.in_play()}
    assert "Iron Boulder" in names


def test_g_fuels_unpaid_boulder_on_the_bench():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    boulder = next(i for i, c in enumerate(me.cards) if c.name == "Iron Boulder")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    snack = next(i for i, c in enumerate(foe.cards) if c.name == "Starly")
    me.active = Pokemon(card_i=clef, played_turn=0)
    me.bench = [Pokemon(card_i=boulder, energy=[], played_turn=0)]
    me.hand = [nrg]
    me.energy_attached = False
    foe.active = Pokemon(card_i=snack, played_turn=0)
    game._attach_energy(me, "a")
    assert me.bench[0].energy == [nrg]
    assert me.hand == []


def test_g_benches_indeedee_and_ledyba_with_clefairy_active():
    game = _plus_game()
    me = game.players["a"]
    indeedee = next(i for i, c in enumerate(me.cards) if c.name == "Indeedee")
    ledyba = next(i for i, c in enumerate(me.cards) if c.name == "Ledyba")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=clef, played_turn=0)
    me.bench = []
    me.hand = [indeedee, ledyba]
    game._play_basics(me)
    names = {me.card(m.card_i).name for m in me.in_play()}
    assert names >= {"Clefairy", "Indeedee", "Ledyba"}


def test_indeedee_nurturer_evolves_ledyba_from_deck():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    indeedee = next(i for i, c in enumerate(me.cards) if c.name == "Indeedee")
    ledyba = next(i for i, c in enumerate(me.cards) if c.name == "Ledyba")
    ledian = next(i for i, c in enumerate(me.cards) if c.name == "Ledian")
    snack = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    raptor = next(i for i, c in enumerate(foe.cards) if c.name == "Starly")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=indeedee, energy=[nrg], played_turn=0)
    me.bench = [Pokemon(card_i=ledyba, played_turn=0)]
    me.deck = [ledian]
    me.hand = []
    foe.active = Pokemon(card_i=raptor, played_turn=0)
    foe.bench = [Pokemon(card_i=snack, played_turn=0)]
    game.turn = 2
    game._attack(me, foe, "a")
    assert me.card(me.bench[0].card_i).name == "Ledian"
    assert game.events.get("expert_nurturer") == 1
    assert foe.card(foe.active.card_i).name == "Clefairy"


def test_relicanth_into_the_deep_recovers_two_energy():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    relic = next(i for i, c in enumerate(me.cards) if c.name == "Relicanth")
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"][:3]
    me.active = Pokemon(card_i=relic, energy=[fuels[2]], played_turn=0)
    me.discard = list(fuels[:2])
    me.hand = []
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    game._attack(me, foe, "a")
    assert set(me.hand) == set(fuels[:2])
    assert game.events.get("into_the_deep") == 2


def test_cramorant_only_hits_on_three_or_four_prizes():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    bird = next(i for i, c in enumerate(me.cards) if c.name == "Hop's Cramorant")
    me.active = Pokemon(card_i=bird, energy=[next(i for i, c in enumerate(me.cards) if c.is_energy)], played_turn=0)
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    atk = me.card(bird).attacks[0]
    foe.prizes = [0, 1, 2, 3, 4, 5]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 0
    foe.prizes = [0, 1, 2]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 120
    foe.prizes = [0, 1, 2, 3]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 120


def _horn_board(game):
    me = game.players["a"]
    foe = game.players["b"]
    boulder = next(i for i, c in enumerate(me.cards) if c.name == "Iron Boulder")
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    snack = next(i for i, c in enumerate(foe.cards) if c.name == "Starly")
    me.active = Pokemon(card_i=boulder, energy=[fuels[0], fuels[1]], played_turn=0)
    me.energy_attached = True
    foe.active = Pokemon(card_i=snack, played_turn=0)
    return me, foe, fuels


def test_adjusted_horn_zero_unless_hands_match():
    game = _plus_game()
    me, foe, _fuels = _horn_board(game)
    horn = next(a for a in me.card(me.active.card_i).attacks if a.name == "Adjusted Horn")
    me.hand = []
    foe.hand = [0]
    assert game._raw_attack_damage(me, foe, me.active, horn) == 0
    foe.hand = []
    assert game._raw_attack_damage(me, foe, me.active, horn) == 170


def test_g_dumps_potion_to_match_adjusted_horn():
    game = _plus_game()
    me, foe, _fuels = _horn_board(game)
    potion = next(i for i, c in enumerate(me.cards) if c.name == "Potion")
    extra = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    me.hand = [potion]
    foe.hand = []
    game._g_match_horn_hands(me, foe, "a")
    assert me.hand == []
    assert game.events.get("horn_match") == 1
    game._attack(me, foe, "a")
    assert foe.active.damage >= 170
    assert game.events.get("adjusted_horn") == 1


def test_g_skips_energy_attach_to_keep_horn_match():
    game = _plus_game()
    me, foe, fuels = _horn_board(game)
    me.energy_attached = False
    me.hand = [fuels[2]]
    foe.hand = [next(i for i, c in enumerate(foe.cards) if c.name == "Hop")]
    game._attach_energy(me, "a")
    assert me.hand == [fuels[2]]
    assert me.energy_attached is False


def test_g_retrieves_energy_to_match_horn():
    game = _plus_game()
    me, foe, fuels = _horn_board(game)
    retr = next(i for i, c in enumerate(me.cards) if c.name == "Energy Retrieval")
    me.hand = [retr]
    me.discard = [fuels[2], fuels[3]]
    foe.hand = [0, 1]
    game._g_match_horn_hands(me, foe, "a")
    assert len(me.hand) == 2
    assert game.events.get("horn_match") == 1
    game._attack(me, foe, "a")
    assert foe.active.damage >= 170


def test_horn_pierces_cornerstone_stance():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    boulder = next(i for i, c in enumerate(me.cards) if c.name == "Iron Boulder")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    oger = next(i for i, c in enumerate(foe.cards) if "Ogerpon" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=boulder, energy=[fuels[0], fuels[1]], played_turn=0)
    me.hand = []
    foe.active = Pokemon(card_i=oger, played_turn=0)
    foe.hand = []
    horn = next(a for a in me.card(boulder).attacks if a.name == "Adjusted Horn")
    assert me.card(boulder).abilities == []
    assert game._raw_attack_damage(me, foe, me.active, horn) == 170
    me.active = Pokemon(card_i=clef, energy=list(fuels[:3]), played_turn=0)
    storm = next(a for a in me.card(clef).attacks if "Wonder Storm" in a.name)
    assert game._raw_attack_damage(me, foe, me.active, storm) == 0


def test_plusle_plus_damage_pierces_stance_and_scales():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    plusle = next(i for i, c in enumerate(me.cards) if c.name == "Plusle")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    oger = next(i for i, c in enumerate(foe.cards) if "Ogerpon" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=plusle, energy=[fuels[0], fuels[1]], played_turn=0)
    foe.active = Pokemon(card_i=oger, played_turn=0, damage=100)
    plus = next(a for a in me.card(plusle).attacks if a.name == "Plus Damage")
    assert me.card(plusle).abilities == []
    assert game._raw_attack_damage(me, foe, me.active, plus) == 110
    remaining = game._max_hp(foe, foe.active) - foe.active.damage
    assert remaining == 110
    me.active = Pokemon(card_i=clef, energy=list(fuels[:3]), played_turn=0)
    storm = next(a for a in me.card(clef).attacks if "Wonder Storm" in a.name)
    assert game._raw_attack_damage(me, foe, me.active, storm) == 0


def test_g_fuels_plusle_only_when_plus_damage_would_ko():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    plusle = next(i for i, c in enumerate(me.cards) if c.name == "Plusle")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    oger = next(i for i, c in enumerate(foe.cards) if "Ogerpon" in c.name)
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=clef, energy=[], played_turn=0)
    me.bench = [Pokemon(card_i=plusle, energy=[], played_turn=0)]
    me.hand = [nrg]
    me.energy_attached = False
    foe.active = Pokemon(card_i=oger, played_turn=0, damage=100)
    game._attach_energy(me, "a")
    assert me.bench[0].energy == [nrg]
    assert me.active.energy == []

    me.bench[0].energy = []
    me.hand = [nrg]
    me.energy_attached = False
    foe.active.damage = 0
    game._attach_energy(me, "a")
    assert me.active.energy == [nrg]
    assert me.bench[0].energy == []


def test_g_switches_plusle_in_to_ko_damaged_stance():
    game = _plus_game()
    me = game.players["a"]
    foe = game.players["b"]
    plusle = next(i for i, c in enumerate(me.cards) if c.name == "Plusle")
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    oger = next(i for i, c in enumerate(foe.cards) if "Ogerpon" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=clef, energy=[fuels[2], fuels[3]], played_turn=0)
    me.bench = [Pokemon(card_i=plusle, energy=[fuels[0], fuels[1]], played_turn=0)]
    foe.active = Pokemon(card_i=oger, played_turn=0, damage=100)
    game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Plusle"


def test_fallback_plusle_is_live_h_print():
    card = fallback_named("Plusle")
    assert card.catalog_id == "sv04-060"
    assert card.attacks[0].name == "Plus Damage"
    assert "damage counter" in (card.attacks[0].text or "").lower()

