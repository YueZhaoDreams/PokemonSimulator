from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon, play_game
from app.engine.legality import copy_violations
from app.engine.models import default_family_rules, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C_NAMES,
    SET_C60_NAMES,
    SET_D_NAMES,
    SET_T_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
    fallback_named,
)


def test_set_t_is_30_and_two_of():
    assert len(SET_T_NAMES) == 30
    t = build_fallback_deck(list(SET_T_NAMES))
    names = [c.name for c in t]
    counts = {n: names.count(n) for n in set(names)}
    for name, n in counts.items():
        if name.endswith("Energy") and "Double" not in name:
            continue
        assert n <= 2, name
    assert names.count("Dreepy") == 2
    assert names.count("Dragapult ex") == 2
    drap = next(c for c in t if c.name == "Dragapult ex")
    dive = next(a for a in drap.attacks if a.name == "Phantom Dive")
    assert dive.damage == 200
    assert dive.cost == ["Fire", "Psychic"]
    assert "Put 6 damage counters on your opponent's Benched Pokémon in any way you like." in dive.text
    recon = fallback_named("Drakloak")
    abi = next(a for a in recon.abilities if a.name == "Recon Directive")
    effects = parse_ability_effects(abi.text)
    assert effects[0]["kind"] == "look_top_put_hand"
    assert effects[0]["look"] == 2


def test_phantom_dive_parses_bench_counters():
    effects = parse_effects(
        "Put 6 damage counters on your opponent's Benched Pokémon in any way you like."
    )
    assert {"kind": "bench_damage_counters", "counters": 6} in effects


def test_cruel_arrow_parses_accented_pokemon():
    effects = parse_effects(
        "This attack does 100 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)"
    )
    assert {"kind": "damage_one_pokemon", "amount": 100} in effects


def test_itchy_pollen_parses_item_lock():
    effects = parse_effects(
        "During your opponent's next turn, they can't play any Item cards from their hand."
    )
    assert {"kind": "lock_items"} in effects


def test_recon_uses_printed_look_not_hardcoded():
    t = build_fallback_deck(list(SET_T_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(t, d, default_family_rules(), StrategySpec.from_dict("phantom"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    from app.engine.game import Pokemon

    drak_i = next(i for i, c in enumerate(me.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=drak_i, played_turn=0)
    candy = next(i for i, c in enumerate(me.cards) if c.name == "Rare Candy")
    me.deck = [i for i in me.deck if i != candy] + [candy]
    game._use_passive_abilities(me, "a")
    assert candy in me.hand
    assert game.events.get("recon_directive")


def test_phantom_vs_demolish_completes():
    t = build_fallback_deck(list(SET_T_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    result = play_game(
        t,
        d,
        default_family_rules(),
        StrategySpec.from_dict("phantom"),
        StrategySpec.from_dict("demolish"),
        Random(3),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1


WONDROUS_MOON_TEXT = (
    "You may move any amount of Psychic Energy from your Pokémon to your other Pokémon in any way you like."
)


def test_wondrous_moon_parses_move_psychic_energy():
    effects = parse_effects(WONDROUS_MOON_TEXT)
    assert {"kind": "move_psychic_energy"} in effects


def _party_vs_phantom_game(seed: int = 1) -> Game:
    c = build_fallback_deck(list(SET_C_NAMES))
    t = build_fallback_deck(list(SET_T_NAMES))
    return Game(
        c,
        t,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(seed),
    )


def test_party_vs_phantom_opens_on_clefairy():
    game = _party_vs_phantom_game()
    me = game.players["a"]
    clef = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    picked = game._pick_starter(me, [clef, mewtwo], StrategySpec.from_dict("party"))
    assert picked == clef
    assert game._facing_phantom(me)
    assert game._clefairy_play_cap(me) == 3
    assert game._want_four_one_line(me, game.players["b"]) is False


def test_party_vs_phantom_ends_on_mega_when_dive_would_ko_clefairy():
    game = _party_vs_phantom_game()
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    fuels = [i for i, card in enumerate(foe.cards) if card.name in {"Fire Energy", "Psychic Energy"}]
    me.active = Pokemon(card_i=clefs[0], energy=[clefs[2], clefs[3]], played_turn=0)
    me.bench = [Pokemon(card_i=mega, played_turn=0)]
    foe.active = Pokemon(card_i=pult, energy=fuels[:2])
    game._maybe_retreat(me, foe, "a")
    assert "mega clefable" in me.card(me.active.card_i).name.lower()


def test_party_vs_phantom_swaps_chipped_mega_to_full_mewtwo():
    game = _party_vs_phantom_game(2)
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    fuel = next(i for i, card in enumerate(me.cards) if card.name == "Clefable")
    me.active = Pokemon(card_i=mega, energy=[fuel], damage=200, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    foe.active = Pokemon(card_i=pult)
    assert not game._survives_dive(me, me.active)
    assert game._survives_dive(me, me.bench[0])
    game._maybe_retreat(me, foe, "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_party_vs_phantom_does_not_gift_chipped_mega():
    """A 120 HP Mega is a 3-prize Dive KO. Keep the 1-prize Clefairy."""
    game = _party_vs_phantom_game(4)
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=clefs[0], energy=[clefs[1], clefs[2]], played_turn=0)
    me.bench = [Pokemon(card_i=mega, damage=200, played_turn=0)]
    foe.active = Pokemon(card_i=pult)
    game._maybe_retreat(me, foe, "a")
    assert game._is_clefairy(me.card(me.active.card_i))


def test_party_vs_phantom_wondrous_moon_chips_after_party():
    """Vs T, Moon 170 is a chip we take. Two hits plus Dive leftovers close 320."""
    game = _party_vs_phantom_game(5)
    me = game.players["a"]
    foe = game.players["b"]
    ex = next(i for i, card in enumerate(me.cards) if card.name == "Clefable ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:3]
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=ex, energy=fuels, played_turn=0)
    foe.active = Pokemon(card_i=pult)
    assert game._can_pay_wondrous_moon(me, me.active)
    assert not game._moon_ko(me, foe)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("party"))
    assert atk is not None
    assert atk.name == "Wondrous Moon"


def test_party_vs_phantom_wondrous_moon_when_it_kos():
    game = _party_vs_phantom_game(6)
    me = game.players["a"]
    foe = game.players["b"]
    ex = next(i for i, card in enumerate(me.cards) if card.name == "Clefable ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:3]
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=ex, energy=fuels, played_turn=0)
    foe.active = Pokemon(card_i=pult, damage=160)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("party"))
    assert atk is not None
    assert atk.name == "Wondrous Moon"


def test_party_vs_phantom_shooting_moons_chips():
    game = _party_vs_phantom_game(7)
    me = game.players["a"]
    foe = game.players["b"]
    mega = next(i for i, card in enumerate(me.cards) if "Mega Clefable" in card.name)
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:2]
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=mega, energy=fuels, played_turn=0)
    foe.active = Pokemon(card_i=pult)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("party"))
    assert atk is not None
    assert atk.name == "Shooting Moons"


def test_party_vs_phantom_photon_chips_instead_of_passing():
    game = _party_vs_phantom_game(8)
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Clefable"][:2]
    pult = next(i for i, card in enumerate(foe.cards) if card.name == "Dragapult ex")
    me.active = Pokemon(card_i=mewtwo, energy=fuels, played_turn=0)
    foe.active = Pokemon(card_i=pult)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("party"))
    assert atk is not None
    assert "kinesis" in atk.name.lower()
    assert game._effective_damage(me, foe, atk) > 0
    assert game._effective_damage(me, foe, atk) < game._max_hp(foe, foe.active)


def test_party_vs_demolish_four_one_still_chumps():
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )
    me = game.players["a"]
    foe = game.players["b"]
    game.turn = 3
    game.first = "b"
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    extras = [i for i, card in enumerate(me.cards) if card.name == "Clefable"]
    exs = [i for i, card in enumerate(me.cards) if card.name == "Clefable ex"]
    belt = next(i for i, card in enumerate(me.cards) if card.name == "Maximum Belt")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    charm = next(i for i, card in enumerate(foe.cards) if card.name == "Bravery Charm")
    fighting = next(i for i, card in enumerate(foe.cards) if card.name == "Fighting Energy")
    dce = next(i for i, card in enumerate(foe.cards) if card.name == "Double Colorless Energy")
    me.active = Pokemon(card_i=clefs[0], energy=[], ability_used=True, played_turn=0)
    me.bench = [
        Pokemon(card_i=clefs[1], energy=[extras[0]], ability_used=True, played_turn=0),
        Pokemon(card_i=clefs[2], energy=[extras[1]], ability_used=True, played_turn=0),
        Pokemon(card_i=clefs[3], energy=[extras[2]], ability_used=True, played_turn=0),
        Pokemon(card_i=mewtwo, energy=[exs[0], exs[1]], tool=belt, played_turn=0),
    ]
    me.hand = []
    me.discard = []
    foe.active = Pokemon(card_i=oger, energy=[fighting, dce], tool=charm)
    assert game._facing_demolish(me)
    assert not game._facing_phantom(me)
    assert game._want_four_one_line(me, foe)
    game._maybe_retreat(me, foe, "a")
    assert game._is_clefairy(me.card(me.active.card_i))


def _party_vs_meta_pult_game(seed: int = 1) -> Game:
    c = build_fallback_deck(list(SET_C60_NAMES))
    t = build_fallback_deck(list(SET_T_META_NAMES))
    return Game(
        c,
        t,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(seed),
    )


def test_adrena_brain_parses_printed_wording():
    munk = fallback_named("Munkidori")
    abi = next(a for a in munk.abilities if a.name == "Adrena-Brain")
    effects = parse_ability_effects(abi.text)
    assert effects[0]["kind"] == "move_damage_counters"
    assert effects[0]["counters"] == 3
    assert effects[0]["require_energy"] == "Darkness"


def test_adrena_brain_snipes_clefairy_when_darkness_is_attached():
    game = _party_vs_meta_pult_game(9)
    me = game.players["b"]
    foe = game.players["a"]
    munk = next(i for i, card in enumerate(me.cards) if card.name == "Munkidori")
    dark = next(i for i, card in enumerate(me.cards) if card.name == "Darkness Energy")
    pult = next(i for i, card in enumerate(me.cards) if card.name == "Dragapult ex")
    clef = next(i for i, card in enumerate(foe.cards) if card.name == "Clefairy")
    me.active = Pokemon(card_i=pult, damage=30, played_turn=0)
    me.bench = [Pokemon(card_i=munk, energy=[dark], played_turn=0)]
    foe.active = Pokemon(card_i=clef, damage=30, played_turn=0)
    game._use_passive_abilities(me, "b", foe)
    assert game.events.get("adrena_brain") == 1
    assert me.active.damage == 0
    assert game.events.get("ko:Clefairy") == 1


def test_adrena_brain_needs_darkness_energy():
    game = _party_vs_meta_pult_game(10)
    me = game.players["b"]
    foe = game.players["a"]
    munk = next(i for i, card in enumerate(me.cards) if card.name == "Munkidori")
    pult = next(i for i, card in enumerate(me.cards) if card.name == "Dragapult ex")
    clef = next(i for i, card in enumerate(foe.cards) if card.name == "Clefairy")
    me.active = Pokemon(card_i=pult, damage=30, played_turn=0)
    me.bench = [Pokemon(card_i=munk, energy=[], played_turn=0)]
    foe.active = Pokemon(card_i=clef, damage=30, played_turn=0)
    game._use_passive_abilities(me, "b", foe)
    assert not game.events.get("adrena_brain")
    assert me.active.damage == 30


def test_hedrick_shaped_dragapult_is_legal_sixty():
    names = list(SET_T_META_NAMES)
    assert len(names) == 60
    assert names.count("Dragapult ex") == 3
    assert names.count("Munkidori") == 2
    assert names.count("Drakloak") == 4
    pile = build_fallback_deck(names)
    assert copy_violations(pile, standard_60_rules()) == []


def test_c60_vs_hedrick_shaped_dragapult_completes():
    c = build_fallback_deck(list(SET_C60_NAMES))
    t = build_fallback_deck(list(SET_T_META_NAMES))
    result = play_game(
        c,
        t,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(11),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1
