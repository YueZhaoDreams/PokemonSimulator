from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

METRONOME_TEXT = "Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack."


def test_metronome_parses_printed_wording():
    effects = parse_effects(METRONOME_TEXT)
    assert {"kind": "copy_active_attack"} in effects


def test_twm_and_clc_fallbacks_do_not_overwrite_prankish():
    rcl = fallback_named("Clefable")
    twm = fallback_named("Clefable TWM")
    clc = fallback_named("Clefable CLC")
    cmc = fallback_named("Clefable CMC 014")
    assert rcl.catalog_id == "swsh2-75"
    assert any(a.name == "Prankish" for a in rcl.abilities)
    assert twm.catalog_id == "sv06-079"
    assert clc.catalog_id == "clc-014"
    assert cmc.catalog_id == "clc-014"
    assert twm.types == ["Psychic"]
    assert clc.types == ["Colorless"]
    assert clc.hp == 70
    twm_metro = next(a for a in twm.attacks if a.name == "Metronome")
    clc_metro = next(a for a in clc.attacks if a.name == "Metronome")
    assert twm_metro.cost == ["Colorless", "Colorless"]
    assert clc_metro.cost == ["Colorless"]
    assert twm_metro.text == METRONOME_TEXT
    assert clc_metro.text == METRONOME_TEXT
    assert not twm.abilities
    assert not clc.abilities


def _party_game(a_names, b_names) -> Game:
    a = build_fallback_deck(a_names)
    b = build_fallback_deck(b_names)
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(1),
        trace=True,
    )


def test_clc_copies_demolish_through_stance():
    """CLC has no Ability, so Cornerstone Stance does not zero Metronome-copied Demolish."""
    game = _party_game(
        ["Clefable CLC", "Clefairy", "Psychic Energy"] + ["Hop"] * 27,
        ["Cornerstone Mask Ogerpon ex"] + ["Cubone"] * 29,
    )
    me, foe = game.players["a"], game.players["b"]
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    oger = next(i for i, c in enumerate(foe.cards) if "Ogerpon" in c.name)
    me.active = Pokemon(card_i=clc_i, energy=[fuel], played_turn=0)
    foe.active = Pokemon(card_i=oger)
    metro = next(a for a in me.card(clc_i).attacks if a.name == "Metronome")
    resolved = game._resolved_attack(me, foe, metro)
    assert resolved.name == "Demolish"
    assert game._raw_attack_damage(me, foe, me.active, resolved) == 140
    game._attack(me, foe, "a")
    assert foe.active.damage == 140
    assert game.events.get("metronome:Demolish")


def test_clc_copies_phantom_dive_bench_counters():
    game = Game(
        build_fallback_deck(["Clefable CLC", "Clefairy", "Psychic Energy"] + ["Hop"] * 27),
        build_fallback_deck(["Dragapult ex", "Dreepy"] + ["Cubone"] * 28),
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
        trace=True,
    )
    me, foe = game.players["a"], game.players["b"]
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    drap = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    me.active = Pokemon(card_i=clc_i, energy=[fuel], played_turn=0)
    foe.active = Pokemon(card_i=drap)
    foe.bench = [Pokemon(card_i=dreepy)]
    metro = next(a for a in me.card(clc_i).attacks if a.name == "Metronome")
    resolved = game._resolved_attack(me, foe, metro)
    assert resolved.name == "Phantom Dive"
    assert game._raw_attack_damage(me, foe, me.active, resolved) == 200
    game._attack(me, foe, "a")
    assert foe.active.damage == 200
    assert foe.bench[0].damage == 60
    assert game.events.get("metronome:Phantom Dive")


def test_metronome_does_not_copy_metronome():
    game = _party_game(
        ["Clefable CLC", "Clefairy", "Psychic Energy"] + ["Hop"] * 27,
        ["Clefable TWM", "Clefairy"] + ["Cubone"] * 28,
    )
    me, foe = game.players["a"], game.players["b"]
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    twm_i = next(i for i, c in enumerate(foe.cards) if c.catalog_id == "sv06-079")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=clc_i, energy=[fuel], played_turn=0)
    foe.active = Pokemon(card_i=twm_i)
    metro = next(a for a in me.card(clc_i).attacks if a.name == "Metronome")
    resolved = game._resolved_attack(me, foe, metro)
    assert resolved.name == "Magical Shot"
    assert not game._is_copy_attack(resolved)


def test_clc_copies_hydro_splash_and_party_evolves_for_the_ko():
    game = Game(
        build_fallback_deck(["Clefable CLC", "Clefairy", "Psychic Energy"] + ["Hop"] * 27),
        build_fallback_deck(["Dondozo"] + ["Cubone"] * 29),
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("thrifty"),
        Random(1),
        trace=True,
    )
    me, foe = game.players["a"], game.players["b"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    zo = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")
    me.active = Pokemon(card_i=fairy, energy=[fuel], played_turn=0)
    me.hand = [clc_i]
    me.bench = []
    foe.active = Pokemon(card_i=zo)
    game.turn = 3
    game._evolve_party(me, foe, "a")
    assert me.card(me.active.card_i).catalog_id == "clc-014"
    game._attack(me, foe, "a")
    assert foe.active.damage >= 160
    assert game.events.get("metronome:Hydro Splash")
