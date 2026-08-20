from random import Random

from app.engine.game import Game, Pokemon, play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_D_NAMES, SET_S_NAMES, build_fallback_deck


def test_set_s_is_30_and_ace_legal():
    assert len(SET_S_NAMES) == 30
    s = build_fallback_deck(list(SET_S_NAMES))
    assert sum(1 for x in s if x.name == "Sprigatito") == 4
    assert sum(1 for x in s if x.name == "Floragato") == 4
    assert sum(1 for x in s if x.name == "Mewtwo ex") == 3
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


def test_slash_fuels_floragato_not_mewtwo():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(2))
    me = game.players["a"]
    sprig = next(i for i, card in enumerate(me.cards) if card.name == "Sprigatito")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    me.active = Pokemon(card_i=mewtwo)
    me.bench = [Pokemon(card_i=sprig)]
    target = game._energy_target(me, StrategySpec.from_dict("slash"))
    assert game._is_sprigatito(me.card(target.card_i))


def test_slash_tanks_demolish_on_mewtwo():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(3))
    me = game.players["a"]
    foe = game.players["b"]
    sprig = next(i for i, card in enumerate(me.cards) if card.name == "Sprigatito")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    tangela = next(i for i, card in enumerate(me.cards) if card.name == "Tangela")
    me.active = Pokemon(card_i=sprig, energy=[tangela], ability_used=False, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce])
    assert game._foe_can_demolish(foe)
    game._retreat_slash(me, foe, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_slash_stays_on_mewtwo_until_floragato_can_ko():
    s = build_fallback_deck(list(SET_S_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(s, d, default_family_rules(), StrategySpec.from_dict("slash"), StrategySpec.from_dict("demolish"), Random(5))
    me = game.players["a"]
    foe = game.players["b"]
    flora = next(i for i, card in enumerate(me.cards) if card.name == "Floragato")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    fuels = [i for i, card in enumerate(me.cards) if card.name in {"Tangela", "Sprigatito"}]
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = [Pokemon(card_i=flora, energy=fuels[:1], played_turn=0)]
    foe.active = Pokemon(card_i=oger, energy=[fighting])
    game._retreat_slash(me, foe, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))
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
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    belt = next(c for c in me.cards if c.name == "Maximum Belt")
    me.active = Pokemon(card_i=mewtwo)
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
