from random import Random

from app.engine.effects import can_pay_energy, energy_provided, parse_effects
from app.engine.game import Game, Pokemon, play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, build_fallback_deck, fallback_named


def test_set_cd_counts():
    assert len(SET_C_NAMES) == 28
    assert len(SET_D_NAMES) == 28
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    assert sum(1 for x in c if x.name == "Clefairy") == 4
    assert sum(1 for x in c if x.name == "Mewtwo ex") == 2
    assert sum(1 for x in c if x.name == "Clefable") == 4
    assert sum(1 for x in c if x.name == "Clefable ex") == 4
    assert sum(1 for x in c if x.name == "Mega Clefable ex") == 3
    assert sum(1 for x in c if x.name == "Hop") == 3
    assert sum(1 for x in c if x.name == "Nest Ball") == 2
    assert sum(1 for x in c if x.name == "Energy Search") == 3
    assert sum(1 for x in c if x.name == "Switch") == 0
    assert sum(1 for x in c if x.name == "Buddy-Buddy Poffin") == 0
    assert sum(1 for x in c if x.name == "Beach Court") == 0
    assert sum(1 for x in c if x.name == "Maximum Belt") == 1
    assert sum(1 for x in c if x.name == "Tool Box") == 1
    assert sum(1 for x in c if x.name == "Arven") == 1
    assert sum(1 for x in d if x.name == "Cornerstone Mask Ogerpon ex") == 4
    assert sum(1 for x in d if x.name == "Fighting Energy") == 6
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
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    me.active = Pokemon(card_i=clefs[0])
    me.bench = [Pokemon(card_i=clefs[1]), Pokemon(card_i=clefs[2])]
    fillers = [i for i, card in enumerate(me.cards) if card.name in {"Energy Search", "Arven", "Hop", "Nest Ball"}]
    me.deck = fillers + fuels[:3]
    me.hand = [fuels[3]]
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
    assert sum(1 for i in me.deck if me.card(i).name == "Clefable") == 2


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
    me.hand = [fuels[3], switch]
    me.deck = fillers + [fuels[2]]
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
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    pika = next(i for i, card in enumerate(foe.cards) if card.name == "Pikachu")
    me.active = Pokemon(card_i=clefs[0], energy=fuels[:3], ability_used=True, played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], energy=[fuels[3]], ability_used=True, played_turn=0)]
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


def test_storm_line_not_vs_thrifty_dondozo():
    """Dondozo is 160 HP — keep Photon; Clefairy engine still allowed for Party ramp."""
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
    assert game._clefairy_play_cap(me) == 3
    assert game._energy_target(me, StrategySpec.from_dict("party")) is me.bench[0]
