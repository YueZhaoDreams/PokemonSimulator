"""Stellar Crown Tornadus 120 and Surging Sparks Oranguru extra attack effects."""

from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Attack, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

STORM_BARRIER_TEXT = (
    "During your opponent's next turn, this Pokémon takes 50 less damage from attacks "
    "(after applying Weakness and Resistance)."
)
NOW_YOURE_TEXT = (
    "Until the end of your next turn, the Defending Pokémon's Weakness is now Colorless. "
    "(The amount of Weakness doesn't change.)"
)


def test_storm_barrier_and_now_youre_parse_from_print():
    assert parse_effects(STORM_BARRIER_TEXT) == [{"kind": "reduce_damage_next_turn", "amount": 50}]
    assert parse_effects(NOW_YOURE_TEXT) == [
        {"kind": "set_defender_weakness", "weakness": "Colorless", "until": "end_of_your_next_turn"}
    ]
    minimize = parse_effects(
        "During your opponent's next turn, this Pokémon takes 20 less damage from attacks "
        "(after applying Weakness and Resistance)."
    )
    assert minimize == [{"kind": "reduce_damage_next_turn", "amount": 20}]


def test_fallback_prints_match_stellar_crown_and_surging_sparks():
    tornadus = fallback_named("Tornadus")
    assert tornadus.catalog_id == "sv07-120"
    assert tornadus.hp == 110
    assert [a.name for a in tornadus.attacks] == ["Knuckle Punch", "Storm Barrier"]
    barrier = tornadus.attacks[1]
    assert barrier.damage == 100
    assert barrier.effects == [{"kind": "reduce_damage_next_turn", "amount": 50}]
    oranguru = fallback_named("Oranguru")
    assert oranguru.catalog_id == "sv08-156"
    assert oranguru.hp == 120
    assert [a.name for a in oranguru.attacks] == ["Now You're in My Power", "Smack"]
    setup = oranguru.attacks[0]
    assert setup.damage == 0
    assert setup.effects == [
        {"kind": "set_defender_weakness", "weakness": "Colorless", "until": "end_of_your_next_turn"}
    ]


def _combo_game():
    a = build_fallback_deck(
        ["Tornadus", "Oranguru", "Clefairy", "Staraptor"]
        + ["Psychic Energy"] * 8
        + ["Hop"] * 4
        + ["Cubone"] * 12
    )
    b = build_fallback_deck(
        ["Dreepy", "Dragapult ex", "Clefairy"] + ["Fire Energy"] * 8 + ["Hop"] * 4 + ["Cubone"] * 13
    )
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict("phantom"),
        Random(1),
        trace=True,
    )


def test_storm_barrier_subtracts_fifty_after_weakness():
    game = _combo_game()
    me = game.players["a"]
    foe = game.players["b"]
    tornadus = next(i for i, c in enumerate(me.cards) if c.name == "Tornadus")
    snack = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    nrg = [i for i, c in enumerate(foe.cards) if c.is_energy][:2]
    me.active = Pokemon(card_i=tornadus, reduce_damage_next_turn=50, played_turn=0)
    foe.active = Pokemon(card_i=snack, energy=list(nrg), played_turn=0)
    peck = Attack(name="Peck", cost=["Colorless"], damage=80)
    assert game._raw_attack_damage(foe, me, foe.active, peck) == 30


def test_oranguru_makes_no_weakness_pokemon_colorless_x2():
    game = _combo_game()
    me = game.players["a"]
    foe = game.players["b"]
    oranguru = next(i for i, c in enumerate(me.cards) if c.name == "Oranguru")
    tornadus = next(i for i, c in enumerate(me.cards) if c.name == "Tornadus")
    pult = next(i for i, c in enumerate(foe.cards) if "Dragapult" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.is_energy][:3]
    me.active = Pokemon(card_i=oranguru, energy=[fuels[0]], played_turn=0)
    foe.active = Pokemon(card_i=pult, played_turn=0)
    assert not foe.card(pult).weaknesses
    game.turn = 3
    game._attack(me, foe, "a")
    assert game.events.get("now_youre_in_my_power") == 1
    assert foe.active.weakness_override == {"type": "Colorless", "value": "×2"}
    me.active = Pokemon(card_i=tornadus, energy=list(fuels), played_turn=0)
    barrier = next(a for a in me.card(tornadus).attacks if a.name == "Storm Barrier")
    assert game._raw_attack_damage(me, foe, me.active, barrier) == 200
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=clef, energy=list(fuels), played_turn=0)
    storm = next(a for a in me.card(clef).attacks if "Wonder Storm" in a.name)
    psychic_hit = game._raw_attack_damage(me, foe, me.active, storm)
    assert psychic_hit < 200


def test_oranguru_weakness_lasts_until_end_of_users_next_turn():
    game = _combo_game()
    me = game.players["a"]
    foe = game.players["b"]
    oranguru = next(i for i, c in enumerate(me.cards) if c.name == "Oranguru")
    pult = next(i for i, c in enumerate(foe.cards) if "Dragapult" in c.name)
    nrg = next(i for i, c in enumerate(me.cards) if c.is_energy)
    me.active = Pokemon(card_i=oranguru, energy=[nrg], played_turn=0)
    foe.active = Pokemon(card_i=pult, played_turn=0)
    game.turn = 3
    game._attack(me, foe, "a")
    assert foe.active.weakness_override_expires == (5, "a")
    game._expire_turn_markers("a")
    assert foe.active.weakness_override is not None
    game.turn = 4
    game._expire_turn_markers("b")
    assert foe.active.weakness_override is not None
    game.turn = 5
    game._expire_turn_markers("a")
    assert foe.active.weakness_override is None


def test_g_prefers_now_youre_over_smack_and_barrier_over_punch():
    game = _combo_game()
    me = game.players["a"]
    foe = game.players["b"]
    oranguru = next(i for i, c in enumerate(me.cards) if c.name == "Oranguru")
    tornadus = next(i for i, c in enumerate(me.cards) if c.name == "Tornadus")
    pult = next(i for i, c in enumerate(foe.cards) if "Dragapult" in c.name)
    fuels = [i for i, c in enumerate(me.cards) if c.is_energy][:3]
    foe.active = Pokemon(card_i=pult, played_turn=0)
    me.active = Pokemon(card_i=oranguru, energy=list(fuels), played_turn=0)
    picked = game._choose_attack(me, foe, game.strats["a"])
    assert picked is not None
    assert picked.name == "Now You're in My Power"
    me.active = Pokemon(card_i=tornadus, energy=list(fuels), played_turn=0)
    picked = game._choose_attack(me, foe, game.strats["a"])
    assert picked is not None
    assert picked.name == "Storm Barrier"
