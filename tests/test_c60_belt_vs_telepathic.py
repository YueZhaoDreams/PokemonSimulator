import sys
from pathlib import Path
from random import Random

from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T60_NAMES, build_fallback_deck

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "data" / "lab"))
from set_c60_belt_vs_telepathic import extra, variant_lists


def test_locked_c60_still_has_belt_package_and_two_telepathic():
    names = list(SET_C60_NAMES)
    assert names.count("Maximum Belt") == 1
    assert names.count("Tool Box") == 1
    assert names.count("Arven") == 1
    assert names.count("Telepathic Psychic Energy") == 2
    assert names.count("Psychic Energy") == 13


def test_trial_lists_are_legal_sixty_without_belt_package():
    rules = standard_60_rules()
    seen = []
    for key, names in variant_lists():
        assert len(names) == 60, key
        pile = build_fallback_deck(names)
        assert copy_violations(pile, rules) == [], key
        seen.append(key)
        if key == "belt":
            assert names.count("Maximum Belt") == 1
            continue
        assert names.count("Maximum Belt") == 0, key
        assert names.count("Tool Box") == 0, key
        assert names.count("Arven") == 0, key
    assert "belt" in seen
    assert "energy3" in seen
    assert "tele2_energy" in seen
    assert "psy2_stretcher" in seen


def test_tele2_trials_are_four_telepathic_psy2_keep_two():
    by_key = dict(variant_lists())
    assert by_key["tele2_energy"].count("Telepathic Psychic Energy") == 4
    assert by_key["tele2_energy"].count("Psychic Energy") == 14
    assert by_key["tele2_stretcher"].count("Telepathic Psychic Energy") == 4
    assert by_key["tele2_stretcher"].count("Night Stretcher") == 2
    assert by_key["psy2_stretcher"].count("Telepathic Psychic Energy") == 2
    assert by_key["psy2_stretcher"].count("Psychic Energy") == 15
    assert by_key["energy3"].count("Psychic Energy") == 16
    assert extra(
        "Telepathic Psychic Energy", "Telepathic Psychic Energy", "Boss's Orders"
    ).count("Boss's Orders") == 4


def test_photon_counts_telepathic_and_belt_is_fifty_vs_ex():
    game = Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )
    me = game.players["a"]
    foe = game.players["b"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    pult = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    me.active = Pokemon(card_i=mewtwo, energy=[tele], played_turn=0)
    foe.active = Pokemon(card_i=pult, played_turn=0)
    assert game._count_psychic_energy_in_play(me) == 1
    assert game._photon_damage_for(me, foe, 1, False) == 40
    assert game._photon_damage_for(me, foe, 1, True) == 90
    assert game._photon_damage_for(me, foe, 7, False) == 220
    assert game._photon_damage_for(me, foe, 7, True) == 270
    assert game._photon_damage_for(me, foe, 9, False) == 280
