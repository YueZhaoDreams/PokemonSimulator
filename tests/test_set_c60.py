from random import Random

from app.engine.game import play_game
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C_NAMES,
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    build_fallback_deck,
)


def _energy_names(names: list[str]) -> list[str]:
    return [n for n in names if n.endswith("Energy")]


def test_family_cup_set_c_stays_thirty_without_energy():
    assert len(SET_C_NAMES) == 30
    assert "Psychic Energy" not in SET_C_NAMES


def test_set_c60_is_standard_sixty_with_psychic_energy():
    names = list(SET_C60_NAMES)
    assert len(names) == 60
    assert names.count("Clefairy") == 4
    assert names.count("Mewtwo ex") == 3
    assert names.count("Clefable") == 2
    assert names.count("Clefable ex") == 3
    assert names.count("Mega Clefable ex") == 2
    assert names.count("Psychic Energy") == 14
    assert names.count("Switch") == 2
    assert names.count("Buddy-Buddy Poffin") == 4
    assert names.count("Boss's Orders") == 3
    assert names.count("Maximum Belt") == 1
    pile = build_fallback_deck(names)
    rules = standard_60_rules()
    assert copy_violations(pile, rules) == []
    assert any(c.is_energy and c.name == "Psychic Energy" for c in pile)
    assert rules.pokemon_as_energy is False
    assert rules.deck_size == 60
    assert rules.prize_count == 6


def test_s60_foe_lists_are_legal_sixty():
    rules = standard_60_rules()
    for names in (SET_D60_NAMES, SET_T60_NAMES, SET_S60_NAMES, SET_G_NAMES):
        listed = list(names)
        assert len(listed) == 60, len(listed)
        pile = build_fallback_deck(listed)
        assert copy_violations(pile, rules) == []
        assert _energy_names(listed), "s60 lists need Energy cards"


def test_set_c60_vs_ogerpon60_completes_under_s60():
    c = build_fallback_deck(list(SET_C60_NAMES))
    d = build_fallback_deck(list(SET_D60_NAMES))
    result = play_game(
        c,
        d,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(11),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1


def test_set_c60_lab_json_cells_follow_foe_order():
    import json
    from pathlib import Path

    blob = json.loads((Path(__file__).resolve().parents[1] / "data/lab/set-c60-standard.json").read_text())
    assert list(blob["cells"]) == ["g", "d60", "t60", "s60"]
