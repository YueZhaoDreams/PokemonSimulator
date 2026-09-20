import pytest
from random import Random

from app.engine.game import Game, Pokemon, ST_PARALYZED, play_game
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_T60_NAMES,
    build_fallback_deck,
    fallback_named,
)


def test_card_definitions():
    zard = fallback_named("Radiant Charizard")
    assert zard.name == "Radiant Charizard"
    assert zard.hp == 160
    assert zard.retreat == 3
    assert len(zard.abilities) == 1
    assert zard.abilities[0].name == "Excited Heart"
    assert len(zard.attacks) == 1
    assert zard.attacks[0].name == "Combustion Blast"
    assert zard.attacks[0].damage == 250
    assert zard.attacks[0].cost == ["Fire", "Colorless", "Colorless", "Colorless"]

    slaking = fallback_named("Slaking V")
    assert slaking.name == "Slaking V"
    assert slaking.hp == 230
    assert slaking.attacks[0].name == "Heavy Impact"
    assert slaking.attacks[0].damage == 260
    assert slaking.attacks[0].cost == ["Colorless", "Colorless", "Colorless", "Colorless"]

    snorlax = fallback_named("Snorlax")
    assert snorlax.name == "Snorlax"
    assert snorlax.hp == 150
    assert snorlax.attacks[0].name == "Rolling Tackle"
    assert snorlax.attacks[0].damage == 100
    assert snorlax.attacks[0].cost == ["Colorless", "Colorless", "Colorless"]

    dunsparce = fallback_named("Dunsparce")
    assert dunsparce.name == "Dunsparce"
    assert dunsparce.hp == 60
    assert dunsparce.attacks[0].name == "Sudden Flash"
    assert dunsparce.attacks[0].damage == 10
    assert dunsparce.attacks[0].cost == ["Colorless"]
    assert any(e.get("kind") == "status" and e.get("status") == "paralyzed" for e in dunsparce.attacks[0].effects)

    regi = fallback_named("Regigigas")
    assert regi.name == "Regigigas"
    assert regi.hp == 150
    assert regi.attacks[0].name == "Giga Impact"
    assert regi.attacks[0].damage == 230
    assert regi.attacks[0].cost == ["Colorless"] * 5


def test_excited_heart_cost_reduction_on_charizard():
    deck_a = build_fallback_deck(["Radiant Charizard"] * 60)
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    zard_i = next(i for i, c in enumerate(me.cards) if c.name == "Radiant Charizard")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=zard_i)
    foe.active = Pokemon(card_i=dondozo_i)
    atk = me.card(zard_i).attacks[0]

    # 0 prizes taken by foe: cost is Fire + 3 Colorless
    foe.prizes_taken = 0
    assert game._attack_cost(me, me.active, atk, foe) == ["Fire", "Colorless", "Colorless", "Colorless"]

    # 1 prize taken: cost is Fire + 2 Colorless
    foe.prizes_taken = 1
    assert game._attack_cost(me, me.active, atk, foe) == ["Fire", "Colorless", "Colorless"]

    # 2 prizes taken: cost is Fire + 1 Colorless
    foe.prizes_taken = 2
    assert game._attack_cost(me, me.active, atk, foe) == ["Fire", "Colorless"]

    # 3 prizes taken: cost is Fire (all Colorless removed)
    foe.prizes_taken = 3
    assert game._attack_cost(me, me.active, atk, foe) == ["Fire"]

    # 4 prizes taken: cost remains Fire
    foe.prizes_taken = 4
    assert game._attack_cost(me, me.active, atk, foe) == ["Fire"]


def test_mew_ex_copies_colorless_attacks_with_radiant_charizard_bench():
    deck_a = build_fallback_deck(
        ["Mew ex", "Radiant Charizard", "Slaking V", "Snorlax", "Dunsparce", "Regigigas", "Igglybuff"]
        + ["Igglybuff"] * 53
    )
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    zard_i = next(i for i, c in enumerate(me.cards) if c.name == "Radiant Charizard")
    slaking_i = next(i for i, c in enumerate(me.cards) if c.name == "Slaking V")
    snorlax_i = next(i for i, c in enumerate(me.cards) if c.name == "Snorlax")
    dunsparce_i = next(i for i, c in enumerate(me.cards) if c.name == "Dunsparce")
    regi_i = next(i for i, c in enumerate(me.cards) if c.name == "Regigigas")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [
        Pokemon(card_i=zard_i),
        Pokemon(card_i=slaking_i),
        Pokemon(card_i=snorlax_i),
        Pokemon(card_i=dunsparce_i),
        Pokemon(card_i=regi_i),
    ]
    foe.active = Pokemon(card_i=dondozo_i)

    heavy_impact = next(a for a in me.card(slaking_i).attacks if a.name == "Heavy Impact")
    rolling_tackle = next(a for a in me.card(snorlax_i).attacks if a.name == "Rolling Tackle")
    sudden_flash = next(a for a in me.card(dunsparce_i).attacks if a.name == "Sudden Flash")
    giga_impact = next(a for a in me.card(regi_i).attacks if a.name == "Giga Impact")

    # When 0 prizes taken by foe:
    foe.prizes_taken = 0
    assert game._attack_cost(me, me.active, sudden_flash, foe) == ["Colorless"]
    assert game._attack_cost(me, me.active, rolling_tackle, foe) == ["Colorless", "Colorless", "Colorless"]
    assert game._attack_cost(me, me.active, heavy_impact, foe) == ["Colorless"] * 4
    assert game._attack_cost(me, me.active, giga_impact, foe) == ["Colorless"] * 5

    # When 1 prize taken: Sudden Flash (1 [C]) becomes FREE ([]), others decrease by 1
    foe.prizes_taken = 1
    assert game._attack_cost(me, me.active, sudden_flash, foe) == []
    assert game._attack_cost(me, me.active, rolling_tackle, foe) == ["Colorless", "Colorless"]
    assert game._attack_cost(me, me.active, heavy_impact, foe) == ["Colorless"] * 3
    assert game._attack_cost(me, me.active, giga_impact, foe) == ["Colorless"] * 4

    # When 3 prizes taken: Rolling Tackle (3 [C]) becomes FREE ([])
    foe.prizes_taken = 3
    assert game._attack_cost(me, me.active, rolling_tackle, foe) == []
    assert game._attack_cost(me, me.active, heavy_impact, foe) == ["Colorless"]

    # When 4 prizes taken: Heavy Impact (4 [C]) becomes FREE ([])!
    foe.prizes_taken = 4
    assert game._attack_cost(me, me.active, heavy_impact, foe) == []
    assert game._attack_cost(me, me.active, giga_impact, foe) == ["Colorless"]

    # When 5 prizes taken: Giga Impact (5 [C]) becomes FREE ([])!
    foe.prizes_taken = 5
    assert game._attack_cost(me, me.active, giga_impact, foe) == []


def test_mew_without_radiant_charizard_cannot_reduce():
    deck_a = build_fallback_deck(["Mew ex", "Slaking V"] + ["Igglybuff"] * 58)
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    slaking_i = next(i for i, c in enumerate(me.cards) if c.name == "Slaking V")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=slaking_i)]
    foe.active = Pokemon(card_i=dondozo_i)

    heavy_impact = next(a for a in me.card(slaking_i).attacks if a.name == "Heavy Impact")

    # Even with 5 prizes taken by foe, without Radiant Charizard in play, cost is NOT reduced
    foe.prizes_taken = 5
    assert game._attack_cost(me, me.active, heavy_impact, foe) == ["Colorless"] * 4


def test_mew_ex_executes_slaking_heavy_impact():
    deck_a = build_fallback_deck(
        ["Mew ex", "Radiant Charizard", "Slaking V", "Igglybuff"] + ["Igglybuff"] * 56
    )
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    zard_i = next(i for i, c in enumerate(me.cards) if c.name == "Radiant Charizard")
    slaking_i = next(i for i, c in enumerate(me.cards) if c.name == "Slaking V")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=zard_i), Pokemon(card_i=slaking_i)]
    foe.active = Pokemon(card_i=dondozo_i)
    foe.prizes_taken = 4  # Opponent has taken 4 prizes!

    strat = StrategySpec.from_dict("mew_baby")
    chosen = game._choose_attack(me, foe, strat)
    assert chosen is not None
    assert chosen.name == "Heavy Impact"
    assert chosen.damage == 260

    # Execute attack
    game._attack(me, foe, "a")
    assert foe.active.damage == 260


def test_mew_ex_executes_dunsparce_paralyze():
    deck_a = build_fallback_deck(
        ["Mew ex", "Radiant Charizard", "Dunsparce"] + ["Igglybuff"] * 57
    )
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    zard_i = next(i for i, c in enumerate(me.cards) if c.name == "Radiant Charizard")
    dunsparce_i = next(i for i, c in enumerate(me.cards) if c.name == "Dunsparce")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=zard_i), Pokemon(card_i=dunsparce_i)]
    foe.active = Pokemon(card_i=dondozo_i)
    foe.prizes_taken = 1  # 1 prize taken unlocks Sudden Flash

    sudden_flash = next(a for a in me.card(dunsparce_i).attacks if a.name == "Sudden Flash")
    assert game._attack_cost(me, me.active, sudden_flash, foe) == []

    # Choose and execute attack
    game._attack(me, foe, "a")
    assert foe.active.damage >= 10
    # Opponent should now have paralyzed status bit set
    assert bool(foe.active.status & ST_PARALYZED)


def test_dimension_valley_and_dodrio_scaling():
    deck_a = build_fallback_deck(
        ["Mew ex", "Dunsparce", "Dodrio", "Dimension Valley"] + ["Igglybuff"] * 56
    )
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    dunsparce_i = next(i for i, c in enumerate(me.cards) if c.name == "Dunsparce")
    dodrio_i = next(i for i, c in enumerate(me.cards) if c.name == "Dodrio")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=dunsparce_i), Pokemon(card_i=dodrio_i)]
    foe.active = Pokemon(card_i=dondozo_i)

    sudden_flash = next(a for a in me.card(dunsparce_i).attacks if a.name == "Sudden Flash")
    ballistic_beak = next(a for a in me.card(dodrio_i).attacks if a.name == "Ballistic Beak")

    # Without Dimension Valley and 0 prizes taken: cost is 1 [C]
    foe.prizes_taken = 0
    assert game._attack_cost(me, me.active, sudden_flash, foe) == ["Colorless"]

    # Play Dimension Valley!
    valley_card = fallback_named("Dimension Valley")
    game._set_stadium(valley_card)
    assert game.stadium_name == "Dimension Valley"

    # Because Mew ex is Psychic, Sudden Flash (1 [C]) becomes 0 ENERGY on Turn 1!
    assert game._attack_cost(me, me.active, sudden_flash, foe) == []
    # Ballistic Beak (1 [C]) also becomes 0 ENERGY!
    assert game._attack_cost(me, me.active, ballistic_beak, foe) == []

    # Execute Sudden Flash -> 0 energy, 10 damage + Paralyzed!
    game._attack(me, foe, "a")
    assert foe.active.damage == 10
    assert bool(foe.active.status & ST_PARALYZED)

    # Now simulate Mew ex having 100 damage (10 damage counters):
    me.active.damage = 100
    strat = StrategySpec.from_dict("mew_baby")
    chosen = game._choose_attack(me, foe, strat)
    assert chosen is not None
    assert chosen.name == "Ballistic Beak"

    # Ballistic Beak deals: 10 base + 30 * 10 counters = 310 damage!
    game._attack(me, foe, "a")
    assert foe.active.damage == 10 + 310

