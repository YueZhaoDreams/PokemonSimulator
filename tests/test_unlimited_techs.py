from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.engine.game import play_game
from app.seed_data import SET_C60_NAMES, SET_T_UNL_NAMES, build_fallback_deck, fallback_named


def _game() -> Game:
    return Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T_UNL_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_unl_list_is_printed_sixty():
    names = list(SET_T_UNL_NAMES)
    assert len(names) == 60
    assert names.count("Pidgeot ex") == 2
    assert names.count("Rotom V") == 1
    assert names.count("Counter Catcher") == 2
    assert names.count("Forest Seal Stone") == 1
    assert names.count("Lumineon V") == 1
    assert names.count("Manaphy") == 1
    assert names.count("Professor Turo's Scenario") == 1
    assert names.count("Collapsed Stadium") == 1
    pile = build_fallback_deck(names)
    assert copy_violations(pile, standard_60_rules()) == []


def test_pidgey_obf_is_gust_not_call_for_family():
    card = fallback_named("Pidgey")
    assert card.hp == 60
    assert card.attacks[0].name == "Gust"
    kinds = {e["kind"] for a in card.attacks for e in parse_effects(a.text)}
    assert "call_family" not in kinds


def test_quick_search_parses_once_per_turn():
    card = fallback_named("Pidgeot ex")
    abi = next(a for a in card.abilities if a.name == "Quick Search")
    eff = parse_ability_effects(abi.text)[0]
    assert eff["kind"] == "search_any_card"
    assert eff["once_per_turn"] is True
    assert eff["ability_lock"] == "quick search"


def test_instant_charge_parses_draw_end_turn():
    card = fallback_named("Rotom V")
    abi = next(a for a in card.abilities if a.name == "Instant Charge")
    eff = parse_ability_effects(abi.text)[0]
    assert eff["kind"] == "draw_end_turn"
    assert eff["amount"] == 3


def test_luminous_sign_and_wave_veil_parse():
    lum = fallback_named("Lumineon V")
    mana = fallback_named("Manaphy")
    sign = parse_ability_effects(next(a.text for a in lum.abilities))
    veil = parse_ability_effects(next(a.text for a in mana.abilities))
    assert sign[0]["kind"] == "search_supporter_on_bench"
    assert sign[0].get("name_lock") is None
    assert veil[0]["kind"] == "prevent_bench_attack_damage"


def test_forest_seal_star_alchemy_is_vstar_search():
    card = fallback_named("Forest Seal Stone")
    eff = parse_ability_effects(card.text)[0]
    assert eff["kind"] == "search_any_card"
    assert eff["once_per_game"] is True
    assert eff["require_attached_v"] is True


def test_scrap_short_and_blustery_wind_parse():
    rotom = fallback_named("Rotom V")
    pidgeot = fallback_named("Pidgeot ex")
    scrap = parse_effects(rotom.attacks[0].text, "40+")
    wind = parse_effects(pidgeot.attacks[0].text)
    assert {"kind": "tools_to_lost_zone_bonus", "per": 40} in scrap
    assert {"kind": "may_discard_stadium"} in wind
    assert "times" not in {e["kind"] for e in scrap}


def test_collapsed_stadium_parses_bench_limit():
    card = fallback_named("Collapsed Stadium")
    eff = parse_ability_effects(card.text)[0]
    assert eff["kind"] == "stadium_bench_limit"
    assert eff["limit"] == 4
    assert eff["opponent_discards_first"] is True


def test_rotom_v_is_two_prizes():
    game = _game()
    rotom = fallback_named("Rotom V")
    assert game._prizes_for_ko(rotom) == 2


def test_wave_veil_blocks_dive_bench_not_ability_chip():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    mana = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    dreepy = next(i for i, c in enumerate(me.cards) if c.name == "Dreepy")
    pult = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    me.active = Pokemon(card_i=pult, played_turn=0)
    me.bench = [Pokemon(card_i=mana, played_turn=0), Pokemon(card_i=dreepy, played_turn=0)]
    game._bench_damage_counters(me, 6)
    assert me.bench[1].damage == 0
    assert game.events.get("wave_veil") == 1


def test_lumineon_still_searches_after_last_ditch():
    game = _game()
    me = game.players["b"]
    game.last_ditch_used = True
    lum = next(i for i, c in enumerate(me.cards) if c.name == "Lumineon V")
    iono = next(i for i, c in enumerate(me.cards) if c.name == "Iono")
    me.deck = [iono]
    me.hand = []
    me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Dreepy"), played_turn=0)
    me.bench = [Pokemon(card_i=lum, played_turn=game.turn)]
    game._on_benched(me, me.bench[0], from_hand=True)
    assert game.events.get("luminous_sign") == 1
    assert iono in me.hand


def test_counter_catcher_needs_more_prizes():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    me.prizes = [0, 1, 2, 3]
    foe.prizes = [0, 1, 2, 3, 4]
    catcher = fallback_named("Counter Catcher")
    game._resolve_trainer(me, foe, catcher, who="b")
    assert game.events.get("counter_catcher_fail") == 1


def test_instant_charge_skips_when_dive_is_ready():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    rotom = next(i for i, c in enumerate(me.cards) if c.name == "Rotom V")
    pult = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    fire = next(i for i, c in enumerate(me.cards) if c.name == "Fire Energy")
    psy = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=pult, energy=[fire, psy], played_turn=0)
    me.bench = [Pokemon(card_i=rotom, played_turn=0)]
    me.deck = list(range(10))
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy"), played_turn=0)
    assert game._try_draw_end_turn(me, "b") is False
    assert not game.events.get("instant_charge")


def test_quick_search_once_per_turn():
    game = _game()
    me = game.players["b"]
    pidgeots = [i for i, c in enumerate(me.cards) if c.name == "Pidgeot ex"]
    candy = next(i for i, c in enumerate(me.cards) if c.name == "Rare Candy")
    me.deck = [candy]
    me.active = Pokemon(card_i=pidgeots[0], played_turn=0)
    me.bench = [Pokemon(card_i=pidgeots[1], played_turn=0)]
    game._use_passive_abilities(me, "b")
    assert game.events.get("quick_search") == 1
    assert candy in me.hand


def test_c60_vs_unl_dragapult_completes():
    result = play_game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T_UNL_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(11),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
