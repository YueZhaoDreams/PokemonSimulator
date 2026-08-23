from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, build_fallback_deck, fallback_named


def test_muscle_band_adds_twenty_before_weakness():
    c = build_fallback_deck(
        ["Mewtwo ex", "Muscle Band", "Maximum Belt"]
        + ["Clefable"] * 8
        + ["Clefairy"]
        + ["Hop"] * 14
    )
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(6),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    band = next(i for i, card in enumerate(me.cards) if card.name == "Muscle Band")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:8]
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    me.active = Pokemon(card_i=mewtwo, energy=list(fuels[:2]), tool=band)
    me.bench = [Pokemon(card_i=clef, energy=list(fuels[2:]))]
    foe.active = Pokemon(card_i=oger, tool=charm)
    photon = next(a for a in me.card(mewtwo).attacks if a.name == "Photon Kinesis")
    assert game._count_psychic_energy_in_play(me) == 8
    # 10 + 30*8 + 20 Muscle Band = 270
    assert game._raw_attack_damage(me, foe, me.active, photon) == 270


def test_tool_box_takes_tools_from_top_seven():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(5),
    )
    me = game.players["a"]
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    hop = next(i for i, card in enumerate(me.cards) if card.name == "Hop")
    nest = next(i for i, card in enumerate(me.cards) if card.name == "Nest Ball")
    fillers = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:4]
    me.deck = [hop, belt, nest] + fillers
    me.hand = []
    game._tool_box(me)
    assert belt in me.hand
    assert hop not in me.hand
    assert nest not in me.hand
    assert len(me.deck) == 6
    assert game.events.get("tool_box", 0) == 1


def test_invisible_wall_parses_from_printed_text():
    mime = fallback_named("Mr. Mime")
    wall = mime.abilities[0]
    assert wall.name == "Invisible Wall"
    effects = parse_ability_effects(wall.text)
    assert effects[0]["kind"] == "invisible_wall"
    assert effects[0]["threshold"] == 30
    meditate = parse_effects(mime.attacks[0].text, "10")
    assert {"kind": "damage_counter_bonus", "per": 10} in meditate


def test_invisible_wall_blocks_photon_not_demolish():
    c = build_fallback_deck(list(SET_C_NAMES))
    b = build_fallback_deck(["Mr. Mime"] + ["Ferroseed"] * 27)
    game = Game(
        c,
        b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("crunch"),
        Random(1),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    mime = next(i for i, card in enumerate(foe.cards) if card.name == "Mr. Mime")
    fuels = [i for i, card in enumerate(me.cards) if card.types == ["Psychic"]][:9]
    me.active = Pokemon(card_i=mewtwo, energy=list(fuels))
    foe.active = Pokemon(card_i=mime)
    photon = next(a for a in me.card(mewtwo).attacks if a.name == "Photon Kinesis")
    assert game._raw_attack_damage(me, foe, me.active, photon) == 0
    assert game.events.get("invisible_wall", 0) >= 1

    d = build_fallback_deck(list(SET_D_NAMES))
    game2 = Game(
        d,
        b,
        default_family_rules(),
        StrategySpec.from_dict("demolish"),
        StrategySpec.from_dict("crunch"),
        Random(2),
    )
    atk_p = game2.players["a"]
    def_p = game2.players["b"]
    oger = next(i for i, card in enumerate(atk_p.cards) if "Ogerpon" in card.name)
    mime_i = next(i for i, card in enumerate(def_p.cards) if card.name == "Mr. Mime")
    fighting = next(i for i, c in enumerate(atk_p.cards) if c.name == "Fighting Energy")
    dce = next(i for i, c in enumerate(atk_p.cards) if c.name == "Double Colorless Energy")
    atk_p.active = Pokemon(card_i=oger, energy=[fighting, dce])
    def_p.active = Pokemon(card_i=mime_i)
    demolish = next(a for a in atk_p.card(oger).attacks if a.name == "Demolish")
    assert game2._raw_attack_damage(atk_p, def_p, atk_p.active, demolish) == 140


def test_set_c_belt_photon_ohkos_charm_ogerpon():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(3),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    fuels = [i for i, card in enumerate(me.cards) if card.types == ["Psychic"] and card.name != "Clefairy"]
    assert len(fuels) >= 7
    me.active = Pokemon(card_i=mewtwo, energy=list(fuels[:2]), tool=belt)
    me.bench = [Pokemon(card_i=clef, energy=list(fuels[2:7]))]
    foe.active = Pokemon(card_i=oger, tool=charm)
    photon = next(a for a in me.card(mewtwo).attacks if a.name == "Photon Kinesis")
    assert game._max_hp(foe, foe.active) == 260
    assert game._count_psychic_energy_in_play(me) == 7
    assert game._raw_attack_damage(me, foe, me.active, photon) == 270
