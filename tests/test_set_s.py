from random import Random

from app.engine.game import Game, Pokemon, play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, build_fallback_deck


def test_set_s_is_30_grass_and_ace_legal():
    assert len(SET_S_NAMES) == 30
    s = build_fallback_deck(list(SET_S_NAMES))
    assert sum(1 for x in s if x.name == "Sprigatito") == 4
    assert sum(1 for x in s if x.name == "Floragato") == 4
    assert sum(1 for x in s if x.name == "Wo-Chien ex") == 3
    assert sum(1 for x in s if x.name == "Mewtwo ex") == 0
    assert sum(1 for x in s if x.name == "Maximum Belt") == 1
    assert sum(1 for x in s if x.name == "Switch") == 3
    assert sum(1 for x in s if x.name == "Muscle Band") == 0
    assert sum(1 for x in s if x.name == "Grass Energy") == 2
    flora = next(c for c in s if c.name == "Floragato")
    assert flora.evolves_from == "Sprigatito"
    assert not flora.abilities
    assert flora.image
    claw = next(a for a in flora.attacks if a.name == "Slashing Claw")
    assert claw.damage == 90
    assert claw.cost == ["Grass", "Colorless"]
    tank = next(c for c in s if c.name == "Wo-Chien ex")
    assert tank.types == ["Grass"]
    assert not tank.abilities
    assert tank.hp == 230
    blast = next(a for a in tank.attacks if a.name == "Forest Blast")
    assert blast.damage == 220
    oger = next(c for c in build_fallback_deck(list(SET_D_NAMES)) if "Ogerpon" in c.name)
    assert any(w.get("type") == "Grass" for w in (oger.weaknesses or []))


def test_slashing_claw_belt_ohkos_charm_ogerpon():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    flora = next(i for i, card in enumerate(me.cards) if card.name == "Floragato")
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    fuels = [i for i, card in enumerate(me.cards) if card.name in {"Tangela", "Sprigatito"}]
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    me.active = Pokemon(card_i=flora, energy=fuels[:2], tool=belt)
    foe.active = Pokemon(card_i=oger, tool=charm)
    assert not game._stance_prevents(me.card(flora), foe.card(oger))
    assert game._max_hp(foe, foe.active) == 260
    assert game._slash_ko(me, foe)
    atk = next(a for a in me.card(flora).attacks if a.name == "Slashing Claw")
    # 90 + 50 Belt = 140, Grass Weakness ×2 = 280
    assert game._raw_attack_damage(me, foe, me.active, atk) == 280


def test_wo_chien_forest_blast_ohkos_through_stance():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    fuels = [i for i, card in enumerate(me.cards) if card.types == ["Grass"] and i != tank][:4]
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    me.active = Pokemon(card_i=tank, energy=fuels)
    foe.active = Pokemon(card_i=oger, tool=charm)
    assert not game._stance_prevents(me.card(tank), foe.card(oger))
    assert game._slash_ko(me, foe)
    atk = next(a for a in me.card(tank).attacks if a.name == "Forest Blast")
    # 220, Grass Weakness ×2 = 440
    assert game._raw_attack_damage(me, foe, me.active, atk) == 440


def test_paradox_rift_mewtwo_cannot_photon_in_grass_list():
    from app.seed_data import fallback_named

    mewtwo = fallback_named("Mewtwo ex")
    assert mewtwo.types == ["Lightning"]
    photon = next(a for a in mewtwo.attacks if "photon" in a.name.lower())
    assert photon.cost == ["Psychic", "Psychic"]
    assert not mewtwo.abilities


def test_slash_fuels_floragato_not_tank():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(2))
    me = game.players["a"]
    sprig = next(i for i, card in enumerate(me.cards) if card.name == "Sprigatito")
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    me.active = Pokemon(card_i=tank)
    me.bench = [Pokemon(card_i=sprig)]
    target = game._energy_target(me, StrategySpec.from_dict("slash"))
    assert game._is_sprigatito(me.card(target.card_i))


def test_slash_fuels_tank_after_floragato_can_pay():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(7))
    me = game.players["a"]
    flora = next(i for i, card in enumerate(me.cards) if card.name == "Floragato")
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name in {"Tangela", "Sprigatito", "Grass Energy"} and i not in {flora, tank}]
    me.active = Pokemon(card_i=tank)
    me.bench = [Pokemon(card_i=flora, energy=fuels[:2])]
    target = game._energy_target(me, StrategySpec.from_dict("slash"))
    assert game._is_slash_tank(me.card(target.card_i))


def test_slash_tanks_demolish_on_wo_chien():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(3))
    me = game.players["a"]
    foe = game.players["b"]
    sprig = next(i for i, card in enumerate(me.cards) if card.name == "Sprigatito")
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    tangela = next(i for i, card in enumerate(me.cards) if card.name == "Tangela")
    me.active = Pokemon(card_i=sprig, energy=[tangela], ability_used=False, played_turn=0)
    me.bench = [Pokemon(card_i=tank, played_turn=0)]
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce])
    assert game._foe_can_demolish(foe)
    game._retreat_slash(me, foe, "a")
    assert game._is_slash_tank(me.card(me.active.card_i))


def test_slash_stays_on_tank_until_floragato_can_ko():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(5))
    me = game.players["a"]
    foe = game.players["b"]
    flora = next(i for i, card in enumerate(me.cards) if card.name == "Floragato")
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    fuels = [i for i, card in enumerate(me.cards) if card.name in {"Tangela", "Sprigatito"}]
    me.active = Pokemon(card_i=tank, played_turn=0)
    me.bench = [Pokemon(card_i=flora, energy=fuels[:1], played_turn=0)]
    foe.active = Pokemon(card_i=oger, energy=[fighting])
    game._retreat_slash(me, foe, "a")
    assert game._is_slash_tank(me.card(me.active.card_i))
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    switch = next(i for i, card in enumerate(me.cards) if card.name == "Switch")
    me.hand = [switch]
    me.bench[0] = Pokemon(card_i=flora, energy=fuels[:2], tool=belt, played_turn=0)
    game._retreat_slash(me, foe, "a")
    assert game._is_floragato(me.card(me.active.card_i))


def test_slash_holds_belt_for_floragato():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(6))
    me = game.players["a"]
    tank = next(i for i, card in enumerate(me.cards) if card.name == "Wo-Chien ex")
    belt = next(c for c in me.cards if c.name == "Maximum Belt")
    me.active = Pokemon(card_i=tank)
    assert game._tool_target(me, "a", belt) is None


def test_slash_vs_demolish_completes():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    result = play_game(
        s,
        d,
        default_family_rules(),
        StrategySpec.from_dict("slash"),
        StrategySpec.from_dict("demolish"),
        Random(4),
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1


def _party_vs_slash_game(seed: int = 1) -> Game:
    c = build_fallback_deck(list(SET_C_NAMES))
    s = build_fallback_deck(list(SET_S_NAMES))
    return Game(
        c,
        s,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("slash"),
        Random(seed),
    )


def test_party_vs_slash_opens_on_mewtwo():
    """Going first, empty Clefairy is KO'd on S's T2 Claw. Open the 230 HP closer."""
    game = _party_vs_slash_game()
    me = game.players["a"]
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    picked = game._pick_starter(me, [clef, mewtwo], StrategySpec.from_dict("party"))
    assert picked == mewtwo
    game = _party_vs_slash_game()
    me = game.players["a"]
    assert game._facing_slash(me)
    assert game._clefairy_play_cap(me) == 3
    assert game._want_four_one_line(me, game.players["b"]) is False


def test_slash_hit_damage_is_zero_without_active():
    game = _party_vs_slash_game()
    foe = game.players["b"]
    foe.active = None
    assert game._slash_hit_damage(foe) == 0


def test_party_vs_slash_pays_clefairy_retreat_then_hides_on_mega():
    """Slashing Claw 90 farms empty 60 HP Clefairy. Attach for Retreat 2, hide on Mega."""
    game = _party_vs_slash_game()
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    flora = next(i for i, card in enumerate(foe.cards) if card.name == "Floragato")
    fuels = [i for i, card in enumerate(foe.cards) if card.name in {"Tangela", "Grass Energy", "Sprigatito"}]
    me.active = Pokemon(card_i=clefs[0], energy=[], played_turn=0)
    me.bench = [
        Pokemon(card_i=clefs[1], played_turn=0),
        Pokemon(card_i=mega, played_turn=0),
    ]
    foe.active = Pokemon(card_i=flora, energy=fuels[:2])
    target = game._energy_target(me, StrategySpec.from_dict("party"))
    assert target is me.active
    me.active.energy = [clefs[2], clefs[3]]
    game._maybe_retreat(me, foe, "a")
    assert "mega clefable" in me.card(me.active.card_i).name.lower()


def test_party_vs_slash_photon_finish_brings_mewtwo():
    game = _party_vs_slash_game(3)
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    flora = next(i for i, card in enumerate(foe.cards) if card.name == "Floragato")
    psychics = [i for i, card in enumerate(me.cards) if card.types == ["Psychic"] and card.name != "Clefairy"][:6]
    me.active = Pokemon(card_i=clef, energy=psychics[:2], played_turn=0)
    me.bench = [
        Pokemon(card_i=mewtwo, energy=psychics[2:], played_turn=0),
        Pokemon(card_i=mega, played_turn=0),
    ]
    foe.active = Pokemon(card_i=flora)
    assert game._photon_finish(me, foe, "a")
    game._maybe_retreat(me, foe, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))
