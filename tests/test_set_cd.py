from random import Random

from app.engine.effects import can_pay_energy, energy_provided, parse_effects
from app.engine.game import Game, Pokemon, play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, build_fallback_deck, fallback_named


def _rcl_fuels(me):
    return [i for i, card in enumerate(me.cards) if card.name == "Clefable"]


def _ex_fuels(me):
    return [i for i, card in enumerate(me.cards) if card.name == "Clefable ex"]


def test_set_cd_counts():
    assert len(SET_C_NAMES) == 30
    assert len(SET_D_NAMES) == 30
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    assert sum(1 for x in c if x.name == "Clefairy") == 4
    assert sum(1 for x in c if x.name == "Mewtwo ex") == 2
    assert sum(1 for x in c if x.name == "Clefable") == 3
    assert sum(1 for x in c if x.name == "Clefable ex") == 4
    assert sum(1 for x in c if x.name == "Mega Clefable ex") == 4
    assert sum(1 for x in c if x.name == "Lillie's Clefairy ex") == 1
    assert sum(1 for x in c if x.name == "Hop") == 3
    assert sum(1 for x in c if x.name == "Nest Ball") == 2
    assert sum(1 for x in c if x.name == "Energy Search") == 3
    assert sum(1 for x in c if x.name == "Switch") == 0
    assert sum(1 for x in c if x.name == "Buddy-Buddy Poffin") == 0
    assert sum(1 for x in c if x.name == "Beach Court") == 0
    assert sum(1 for x in c if x.name == "Maximum Belt") == 1
    assert sum(1 for x in c if x.name == "Tool Box") == 1
    assert sum(1 for x in c if x.name == "Arven") == 1
    assert sum(1 for x in c if x.name == "Boss's Orders") == 1
    assert sum(1 for x in c if x.name == "Psychic Energy") == 0
    assert all(x.catalog_id == "swsh2-75" for x in c if x.name == "Clefable")
    assert sum(1 for x in d if x.name == "Cornerstone Mask Ogerpon ex") == 4
    assert sum(1 for x in d if x.name == "Fighting Energy") == 8
    assert sum(1 for x in d if x.name == "Double Colorless Energy") == 4


def test_dce_pays_two_colorless():
    dce = fallback_named("Double Colorless Energy")
    fighting = fallback_named("Fighting Energy")
    assert energy_provided(dce) == ["Colorless", "Colorless"]
    pool = energy_provided(fighting) + energy_provided(dce)
    assert can_pay_energy(pool, ["Fighting", "Colorless", "Colorless"])


def test_photon_kinesis_and_transfer_parse():
    mewtwo = fallback_named("Mewtwo ex")
    photon = next(a for a in mewtwo.attacks if a.name == "Photon Kinesis")
    transfer = next(a for a in mewtwo.attacks if a.name == "Transfer Charge")
    assert any(e.get("kind") == "psychic_energy_bonus" and e.get("per") == 30 for e in photon.effects)
    assert any(e.get("kind") == "transfer_charge" for e in transfer.effects)
    demolish = next(a for a in fallback_named("Cornerstone Mask Ogerpon ex").attacks if a.name == "Demolish")
    assert any(e.get("kind") == "ignore_wr" for e in demolish.effects) or "isn't affected by weakness" in demolish.text.lower()


def test_stance_blocks_clefairy_not_mewtwo():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    me.active = Pokemon(card_i=clef)
    foe.active = Pokemon(card_i=oger)
    storm = me.card(clef).attacks[0]
    assert game._raw_attack_damage(me, foe, me.active, storm) == 0
    me.active = Pokemon(card_i=mewtwo)
    # 9 Psychic energy attached anywhere: 10 + 30*9 = 280
    fuels = [i for i, card in enumerate(me.cards) if card.types == ["Psychic"] and card.name != "Clefairy"][:9]
    me.bench = [Pokemon(card_i=clef, energy=list(fuels))]
    photon = next(a for a in me.card(mewtwo).attacks if a.name == "Photon Kinesis")
    assert game._raw_attack_damage(me, foe, me.active, photon) == 280


def test_bravery_charm_hp_and_acerola():
    d = build_fallback_deck(list(SET_D_NAMES))
    c = build_fallback_deck(list(SET_C_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    foe = game.players["b"]
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    foe.active = Pokemon(card_i=oger, damage=160, tool=charm)
    assert game._max_hp(foe, foe.active) == 260
    assert game._max_hp(foe, foe.active) > foe.active.damage


def test_moon_watching_party_searches_one_per_benched_clefairy():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = _rcl_fuels(me)
    extra = _ex_fuels(me)
    me.active = Pokemon(card_i=clefs[0])
    me.bench = [Pokemon(card_i=clefs[1]), Pokemon(card_i=clefs[2])]
    fillers = [i for i, card in enumerate(me.cards) if card.name in {"Energy Search", "Arven", "Hop", "Nest Ball"}]
    me.deck = fillers + fuels[:3]
    me.hand = [extra[0]]
    game._moon_watching_party(me, me.active)
    assert [len(m.energy) for m in me.bench] == [1, 1]
    assert me.active.ability_used is True
    assert len(me.deck) == len(fillers) + 1


def test_moon_watching_party_searches_the_whole_deck():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    fillers = [i for i, card in enumerate(me.cards) if card.name in {"Energy Search", "Arven", "Hop", "Nest Ball"}]
    assert len(fillers) >= 6
    me.active = Pokemon(card_i=clefs[0])
    me.bench = [Pokemon(card_i=clefs[1])]
    me.hand = [fuels[1]]
    me.deck = [fuels[0]] + fillers
    game._moon_watching_party(me, me.active)
    assert me.bench[0].energy == [fuels[0]]
    assert me.active.ability_used is True


def test_party_does_not_full_search_when_text_says_top_six():
    """Engine follows printed text. A top-6 sentence must not search the rest of the deck."""
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    fillers = [i for i, card in enumerate(me.cards) if card.name in {"Energy Search", "Arven", "Hop", "Nest Ball"}]
    assert len(fillers) >= 6
    me.cards[clefs[0]].abilities[0].text = (
        "Once during your turn, if this Pokémon is in the Active Spot, look at the top 6 cards "
        "of your deck. Attach any number of Psychic Energy cards you find there to your Benched "
        "Clefairy in any way you like. Shuffle the other cards back into your deck."
    )
    me.active = Pokemon(card_i=clefs[0])
    me.bench = [Pokemon(card_i=clefs[1])]
    me.hand = [fuels[1]]
    me.deck = [fuels[0]] + fillers
    game._moon_watching_party(me, me.active)
    assert me.bench[0].energy == []
    assert fuels[0] in me.deck


def test_moon_watching_party_uses_deck_clefable_as_energy():
    """Keep 1 Clefable as a Pokémon; extras in the deck are legal Party fuel."""
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    me.active = Pokemon(card_i=clefs[0])
    me.bench = [Pokemon(card_i=clefs[1]), Pokemon(card_i=clefs[2])]
    me.hand = []
    me.deck = list(fuels)
    game._moon_watching_party(me, me.active)
    assert [len(m.energy) for m in me.bench] == [1, 1]
    assert sum(1 for i in me.deck if me.card(i).name == "Clefable") == 1


def test_party_vs_demolish_game_completes():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    result = play_game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(20260818),
        trace=True,
        first="a",
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.first_player == "a"
    assert result.turns >= 1


def _cd_game():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    return Game(c, d, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("demolish"), Random(1))


def test_prankish_bounces_fighting_not_dce():
    game = _cd_game()
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 1
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    clefable = next(i for i, card in enumerate(me.cards) if card.name == "Clefable")
    foe.active = Pokemon(card_i=oger, energy=[dce, fighting])
    foe.deck = []
    me.active = Pokemon(card_i=clef, ability_used=True, played_turn=0)
    me.hand = [clefable]
    game._do_evolve(me, me.active, clefable)
    assert foe.deck[0] == fighting
    assert fighting not in foe.active.energy
    assert dce in foe.active.energy


def test_party_attaches_energy_to_benched_mewtwo():
    game = _cd_game()
    me = game.players["a"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    wall = Pokemon(card_i=mega)
    closer = Pokemon(card_i=mewtwo)
    me.active = wall
    me.bench = [closer]
    assert game._energy_target(me, StrategySpec.from_dict("party")) is closer


def test_party_while_mega_walls_then_restores():
    game = _cd_game()
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 3
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    zone = next(i for i, card in enumerate(me.cards) if card.name == "Clefable ex")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    me.cards = list(me.cards) + [fallback_named("Switch")]
    switch = len(me.cards) - 1
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    fillers = [i for i, card in enumerate(me.cards) if card.name in {"Energy Search", "Arven"}]
    me.active = Pokemon(card_i=mega, energy=[fuels[0]])
    me.bench = [
        Pokemon(card_i=clefs[0], energy=[fuels[1]]),
        Pokemon(card_i=clefs[1]),
        Pokemon(card_i=zone),
        Pokemon(card_i=mewtwo),
    ]
    extra = _ex_fuels(me)
    me.hand = [switch]
    me.deck = fillers + extra[:2]
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce])
    game._use_abilities(me, foe, "a")
    assert "mega clefable" in me.card(me.active.card_i).name.lower()
    partied = sum(1 for mon in me.in_play() if game._is_clefairy(me.card(mon.card_i)) and mon.ability_used)
    assert partied >= 1
    assert game.events.get("party_while_wall") or game.events.get("moon_watching_party")


def test_retreat_pays_exact_cost_not_extra():
    game = _cd_game()
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 3
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:2]
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    me.active = Pokemon(card_i=clef, energy=list(fuels))
    me.bench = [Pokemon(card_i=mewtwo)]
    me.hand = []
    me.discard = []
    foe.active = Pokemon(card_i=oger)
    game._retreat_for_transfer(me, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))
    assert game._discard_psychic_count(me) == 2
    assert me.retreated is True
    assert game._do_retreat_into(me, 0) is False


def test_beach_court_retreat_discards_one():
    game = _cd_game()
    me = game.players["a"]
    game.turn = 3
    game.stadium_name = "Beach Court"
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:2]
    me.active = Pokemon(card_i=clef, energy=list(fuels))
    me.bench = [Pokemon(card_i=mewtwo)]
    me.discard = []
    assert game._retreat_cost(me, me.active) == 1
    game._retreat_for_transfer(me, "a")
    assert game._discard_psychic_count(me) == 1
    assert game._transfer_charge
    game._transfer_charge(me, count=2)
    assert game._psychic_on(me, me.active) == 1


def test_first_player_cannot_play_supporter_or_evolve_on_turn_one():
    game = _cd_game()
    game.first = "a"
    game.turn = 1
    me = game.players["a"]
    foe = game.players["b"]
    arven = next(i for i, card in enumerate(me.cards) if card.name == "Arven")
    clefable = next(i for i, card in enumerate(me.cards) if card.name == "Clefable")
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    me.active = Pokemon(card_i=clef, played_turn=0, ability_used=True)
    me.hand = [arven, clefable]
    me.supporter_used = False
    assert game._can_play_supporter("a") is False
    assert game._pick_trainer(me) is None or me.card(game._pick_trainer(me)).name != "Arven"
    game._evolve_party(me, foe, "a")
    assert me.card(me.active.card_i).name == "Clefairy"


def test_second_player_can_play_supporter_but_not_evolve_on_their_first_turn():
    game = _cd_game()
    game.first = "a"
    game.turn = 2
    me = game.players["a"]
    assert game._can_play_supporter("a") is True
    assert game._is_players_first_turn("a") is False
    assert game._is_players_first_turn("b") is True
    assert game._can_play_supporter("b") is True


def test_end_turn_on_mewtwo_when_demolish_is_coming():
    game = _cd_game()
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 3
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:2]
    me.active = Pokemon(card_i=clefs[0], energy=list(fuels), ability_used=True, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce])
    assert game._foe_can_demolish(foe)
    game._retreat_party(me, foe, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_play_mewtwo_before_clefairy_is_in_play():
    game = _cd_game()
    me = game.players["a"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    me.active = None
    me.bench = []
    me.hand = [mewtwo]
    strat = StrategySpec.from_dict("party")
    assert game._wants_in_play(me, me.card(mewtwo), strat, ace_out=False)
    game._play_basics(me)
    assert game._mewtwo_mon(me) is not None


def test_fast_line_allows_mewtwo_to_tank_demolish():
    game = _cd_game()
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 3
    game.first = "b"
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    fuels = [i for i, card in enumerate(me.cards) if card.types == ["Psychic"] and card.name != "Clefairy"]
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    me.active = Pokemon(card_i=clefs[0], energy=fuels[:6], ability_used=True, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, tool=belt), Pokemon(card_i=clefs[1], ability_used=True, played_turn=0)]
    me.hand = [clefs[2]]
    me.discard = []
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce], tool=charm)
    assert game._foe_can_demolish(foe)
    assert game._max_hp(foe, foe.active) == 260
    assert game._should_transfer_combo(me, foe)
    sim = game._simulate_fast_line(me, foe, "a")
    assert sim is not None
    assert sim["pp"]
    assert sim["psychic"] == 7
    assert sim["ko_next"] or sim["ko_next_no_attach"]


def test_vs_shock_fuels_mewtwo_not_clefairy():
    """Thunder Shock para-locks Clefairy — vs B keep the Photon line on Mewtwo."""
    from app.seed_data import SET_B_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    b = build_fallback_deck(list(SET_B_NAMES))
    game = Game(c, b, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("shock"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    pika = next(i for i, card in enumerate(foe.cards) if card.name == "Pikachu")
    me.active = Pokemon(card_i=clefs[0], energy=[], ability_used=False, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    foe.active = Pokemon(card_i=pika)
    assert game._want_storm_line(me, foe, "a") is False
    assert game._clefairy_play_cap(me) == 0
    assert game._vs_lightning_glass("a")
    target = game._energy_target(me, StrategySpec.from_dict("party"))
    assert target is me.bench[0]
    assert game._is_mewtwo(me.card(target.card_i))


def test_wonder_storm_kos_pikachu_with_four_psychic():
    from app.seed_data import SET_B_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    b = build_fallback_deck(list(SET_B_NAMES))
    game = Game(c, b, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("shock"), Random(2))
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = _rcl_fuels(me)
    extra = _ex_fuels(me)
    pika = next(i for i, card in enumerate(foe.cards) if card.name == "Pikachu")
    me.active = Pokemon(card_i=clefs[0], energy=fuels[:3], ability_used=True, played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], energy=[extra[0]], ability_used=True, played_turn=0)]
    foe.active = Pokemon(card_i=pika)
    assert game._can_pay_wonder_storm(me, me.active)
    assert game._count_psychic_energy_in_play(me) == 4
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("party"))
    assert atk is not None
    assert "wonder storm" in atk.name.lower()
    assert game._effective_damage(me, foe, atk) >= game._max_hp(foe, foe.active)


def test_pick_starter_prefers_mewtwo_vs_shock():
    from app.seed_data import SET_B_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    b = build_fallback_deck(list(SET_B_NAMES))
    game = Game(c, b, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("shock"), Random(3))
    me = game.players["a"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    pick = game._pick_starter(me, [clefs[0], mewtwo], StrategySpec.from_dict("party"))
    assert pick == mewtwo


def test_vs_thrifty_caps_clefairy_and_opens_mewtwo():
    """Vs Dondozo: at most one Clefairy; prefer Mewtwo opener for Photon."""
    from app.seed_data import SET_A_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    a = build_fallback_deck(list(SET_A_NAMES))
    game = Game(c, a, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("thrifty"), Random(5))
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    dozo = next(i for i, card in enumerate(foe.cards) if card.name == "Dondozo")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    foe.active = Pokemon(card_i=dozo)
    assert game._want_storm_line(me, foe, "a") is False
    assert game._clefairy_play_cap(me) == 1
    assert game._vs_lightning_glass("a")
    assert game._energy_target(me, StrategySpec.from_dict("party")) is me.bench[0]
    pick = game._pick_starter(me, [clefs[0], mewtwo], StrategySpec.from_dict("party"))
    assert pick == mewtwo


def _party_trainer_board(game):
    me = game.players["a"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    fillers = [
        i
        for i, card in enumerate(me.cards)
        if card.name in {"Clefable", "Clefable ex", "Mega Clefable ex"}
    ]
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = [Pokemon(card_i=clef, played_turn=0)]
    me.supporter_used = False
    return me, {
        "arven": next(i for i, card in enumerate(me.cards) if card.name == "Arven"),
        "box": next(i for i, card in enumerate(me.cards) if card.name == "Tool Box"),
        "hop": next(i for i, card in enumerate(me.cards) if card.name == "Hop"),
        "search": next(i for i, card in enumerate(me.cards) if card.name == "Energy Search"),
        "nest": next(i for i, card in enumerate(me.cards) if card.name == "Nest Ball"),
        "belt": next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt"),
        "fillers": fillers,
    }


def test_party_picks_arven_before_tool_box_hop_and_tutors():
    """Hunt Belt first. Arven is Tool + Item, so it outranks Tool Box."""
    game = _cd_game()
    game.turn = 3
    me, ids = _party_trainer_board(game)
    me.hand = [ids["arven"], ids["box"], ids["hop"], ids["search"], ids["nest"]]
    me.deck = [ids["belt"]] + ids["fillers"]
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Arven"


def test_party_picks_tool_box_before_hop_when_belt_is_in_the_deck():
    game = _cd_game()
    game.turn = 3
    me, ids = _party_trainer_board(game)
    me.hand = [ids["box"], ids["hop"], ids["search"], ids["nest"]]
    me.deck = [ids["belt"]] + ids["fillers"]
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Tool Box"


def test_party_picks_hop_before_energy_search_and_nest():
    """Hop draws 3 before Search/Nest strip hits out of the deck."""
    game = _cd_game()
    game.turn = 3
    me, ids = _party_trainer_board(game)
    me.hand = [ids["hop"], ids["search"], ids["nest"]]
    me.deck = ids["fillers"] + [ids["belt"]]
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Hop"


def test_party_attaches_found_belt_before_hop():
    game = _cd_game()
    game.turn = 3
    me, ids = _party_trainer_board(game)
    me.hand = [ids["belt"], ids["hop"], ids["search"], ids["nest"]]
    me.deck = ids["fillers"]
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Maximum Belt"


def test_seed_json_empty_effects_still_parse_shooting_moons():
    """Matrix / API decks load via Card.from_dict; stale empty effects must not hide printed text."""
    from app.engine.models import Card

    raw = {
        "catalog_id": "me03-031",
        "name": "Mega Clefable ex",
        "category": "Pokemon",
        "stage": "Stage1",
        "types": ["Psychic"],
        "hp": 320,
        "attacks": [
            {
                "name": "Shooting Moons",
                "cost": ["Psychic", "Psychic"],
                "damage": 120,
                "text": (
                    "You may discard up to 4 Energy cards from your hand, and this attack "
                    "does 40 more damage for each card you discarded in this way."
                ),
                "effects": [],
            }
        ],
    }
    card = Card.from_dict(raw)
    moons = card.attacks[0]
    assert any(
        e.get("kind") == "discard_hand_energy_bonus" and e.get("max") == 4 and e.get("per") == 40
        for e in moons.effects
    )
    mega = fallback_named("Mega Clefable ex")
    moons = next(a for a in mega.attacks if a.name == "Shooting Moons")
    assert any(
        e.get("kind") == "discard_hand_energy_bonus" and e.get("max") == 4 and e.get("per") == 40
        for e in moons.effects
    )


def test_shooting_moons_discards_one_energy_to_ko_dondozo():
    from app.seed_data import SET_A_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    a = build_fallback_deck(list(SET_A_NAMES))
    game = Game(c, a, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("thrifty"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    fuels = _rcl_fuels(me)
    extra = _ex_fuels(me)
    dozo = next(i for i, card in enumerate(foe.cards) if card.name == "Dondozo")
    me.active = Pokemon(card_i=mega, energy=list(fuels[:2]))
    me.hand = [fuels[2], extra[0]]
    foe.active = Pokemon(card_i=dozo)
    moons = next(a for a in me.card(mega).attacks if a.name == "Shooting Moons")
    assert game._raw_attack_damage(me, foe, me.active, moons) == 160
    game._attack(me, foe, "a")
    assert foe.active.damage >= 160
    assert game.events.get("shooting_moons_discard") == 1
    assert len(me.hand) == 1


def test_mega_rush_skips_ogerpon_stance():
    game = _cd_game()
    game.turn = 3
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    me.active = Pokemon(card_i=mega, energy=list(fuels[:2]))
    me.hand = list(fuels[2:])
    foe.active = Pokemon(card_i=oger)
    assert game._want_mega_rush(me, foe, "a") is False
    me.active = Pokemon(card_i=clef, energy=list(fuels[:2]))
    me.hand = [mega] + fuels[2:]
    assert game._want_mega_rush(me, foe, "a") is False


def test_mega_rush_evolves_when_moons_kos_dondozo():
    from app.seed_data import SET_A_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    a = build_fallback_deck(list(SET_A_NAMES))
    game = Game(c, a, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("thrifty"), Random(1))
    game.turn = 3
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    dozo = next(i for i, card in enumerate(foe.cards) if card.name == "Dondozo")
    me.active = Pokemon(card_i=clefs[0], energy=list(fuels[:2]), played_turn=0)
    me.bench = []
    me.hand = [mega, fuels[2]]
    foe.active = Pokemon(card_i=dozo)
    assert game._want_mega_rush(me, foe, "a") is True
    game._evolve_party(me, foe, "a")
    assert "mega clefable" in me.card(me.active.card_i).name.lower()


def test_mega_rush_skips_transfer_charge_combo():
    """A same-turn Moons KO beats retreating to Mewtwo for Transfer Charge."""
    from app.seed_data import SET_A_NAMES

    c = build_fallback_deck(list(SET_C_NAMES))
    a = build_fallback_deck(list(SET_A_NAMES))
    game = Game(c, a, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("thrifty"), Random(1))
    game.turn = 3
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    ex_fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable ex"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    dozo = next(i for i, card in enumerate(foe.cards) if card.name == "Dondozo")
    me.active = Pokemon(card_i=clefs[0], energy=list(fuels[:2]), played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, energy=list(ex_fuels[:1]))]
    me.hand = [mega, fuels[2]]
    foe.active = Pokemon(card_i=dozo)
    assert game._want_mega_rush(me, foe, "a") is True
    assert game._should_transfer_combo(me, foe) is False


def test_fairy_zone_parses_and_doubles_psychic_not_lightning():
    from app.engine.effects import parse_ability_effects
    from app.seed_data import SET_T_NAMES

    lillie = fallback_named("Lillie's Clefairy ex")
    zone = next(a for a in lillie.abilities if a.name == "Fairy Zone")
    assert any(e.get("kind") == "fairy_zone" and e.get("weakness") == "Psychic" for e in parse_ability_effects(zone.text))
    assert any(
        e.get("kind") == "fairy_zone"
        for e in parse_ability_effects(
            "The Weakness of each of your opponent's {N} Pokémon in play is now {P}. (Apply Weakness as ×2.)"
        )
    )
    rondo = next(a for a in lillie.attacks if a.name == "Full Moon Rondo")
    assert any(e.get("kind") == "benched_pokemon_bonus" and e.get("per") == 20 and e.get("sides") == "both" for e in rondo.effects)

    c = build_fallback_deck(list(SET_C_NAMES))
    t = build_fallback_deck(list(SET_T_NAMES))
    game = Game(c, t, default_family_rules(), StrategySpec.from_dict("party"), StrategySpec.from_dict("phantom"), Random(1))
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    lillie_i = next(i for i, card in enumerate(me.cards) if "Lillie's Clefairy" in card.name)
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    drap = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=mega, energy=list(fuels[:2]))
    me.bench = [Pokemon(card_i=lillie_i)]
    me.hand = [fuels[2]]
    foe.active = Pokemon(card_i=drap)
    moons = next(a for a in me.card(mega).attacks if a.name == "Shooting Moons")
    # 120 + 40 one discard, Psychic vs Fairy Zone = 320.
    assert game._raw_attack_damage(me, foe, me.active, moons) == 320
    me.active = Pokemon(card_i=mewtwo, energy=list(fuels[:2]))
    photon = next(a for a in me.card(mewtwo).attacks if "Kinesis" in a.name)
    # Paradox Rift Mewtwo is Lightning; Fairy Zone is Psychic Weakness, so no ×2.
    assert game._raw_attack_damage(me, foe, me.active, photon) == 10 + 30 * 2
    rondo = next(a for a in me.card(lillie_i).attacks if a.name == "Full Moon Rondo")
    me.active = Pokemon(card_i=lillie_i, energy=list(fuels[:2]))
    me.bench = [Pokemon(card_i=mega)]
    # 20 + 20×1 our bench ×2 = 80.
    assert game._raw_attack_damage(me, foe, me.active, rondo) == 80
    assert game._wants_in_play(me, me.card(lillie_i), game.strats["a"]) is False  # already in play as Active; copies>=1
    me.bench = []
    me.active = Pokemon(card_i=mega)
    assert game._wants_in_play(me, me.card(lillie_i), game.strats["a"]) is True

