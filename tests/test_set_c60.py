from collections import Counter
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
    SET_H_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)


def _energy_names(names: list[str]) -> list[str]:
    return [n for n in names if n.endswith("Energy")]


def test_family_cup_set_c_stays_thirty_without_energy():
    assert len(SET_C_NAMES) == 30
    assert "Psychic Energy" not in SET_C_NAMES
    assert "Telepathic Psychic Energy" not in SET_C_NAMES


def test_set_c60_is_standard_sixty_with_psychic_energy():
    names = list(SET_C60_NAMES)
    assert len(names) == 60
    assert names.count("Clefairy") == 4
    assert names.count("Mewtwo ex") == 3
    assert names.count("Clefable") == 1
    assert names.count("Clefable CLC") == 1
    assert names.count("Clefable ex") == 3
    assert names.count("Mega Clefable ex") == 1
    assert names.count("Poké Pad") == 1
    assert names.count("Psychic Energy") == 14
    assert names.count("Telepathic Psychic Energy") == 2
    assert names.count("Energy Search") == 0
    assert names.count("Switch") == 2
    assert names.count("Buddy-Buddy Poffin") == 4
    assert names.count("Boss's Orders") == 3
    assert names.count("Maximum Belt") == 1
    assert names.count("Tool Box") == 0
    assert names.count("Arven") == 1
    assert names.count("Battle Cage") == 3
    assert names.count("Iono") == 1
    assert names.count("Penny") == 0
    assert names.count("Professor Turo's Scenario") == 0
    assert names.count("Mr. Briney's Compassion") == 0
    assert names.count("Seeker") == 0
    assert names.count("AZ") == 0
    assert names.count("Cheren's Care") == 0
    assert names.count("Energy Switch") == 2
    assert names.count("Hop") == 2
    assert names.count("Lillie") == 2
    assert names.count("Lillie's Determination") == 2
    assert names.count("Jacq") == 0
    assert names.count("Energy Retrieval") == 0
    pile = build_fallback_deck(names)
    rules = standard_60_rules()
    assert copy_violations(pile, rules) == []
    fables = [c for c in pile if c.name == "Clefable"]
    assert Counter(c.catalog_id for c in fables) == Counter({"swsh2-75": 1, "clc-014": 1})
    prankish = next(c for c in fables if c.catalog_id == "swsh2-75")
    clc = next(c for c in fables if c.catalog_id == "clc-014")
    assert any(a.name == "Prankish" for a in prankish.abilities)
    assert any(a.name == "Metronome" for a in clc.attacks)
    assert any(c.is_energy and c.name == "Psychic Energy" for c in pile)
    assert sum(1 for c in pile if c.name == "Telepathic Psychic Energy") == 2
    assert rules.pokemon_as_energy is False
    assert rules.deck_size == 60
    assert rules.prize_count == 6


def test_s60_foe_lists_are_legal_sixty():
    rules = standard_60_rules()
    for names in (
        SET_D60_NAMES,
        SET_T60_NAMES,
        SET_S60_NAMES,
        SET_G_NAMES,
        SET_H_NAMES,
        SET_T_META_NAMES,
        SET_T_UNL_NAMES,
    ):
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


def test_set_c60_unl_matrix_json_is_square():
    import json
    from pathlib import Path

    blob = json.loads((Path(__file__).resolve().parents[1] / "data/lab/set-c60-unl-matrix.json").read_text())
    keys = blob["decks"]
    assert keys == ["c60", "t60", "hedrick", "unl", "d60", "s60", "g"]
    for row in keys:
        assert row not in blob["cells"][row]
        assert set(blob["cells"][row]) == set(keys) - {row}


def test_set_c60_dimension_valley_bakeoff_json():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-dimension-valley.json").read_text()
    )
    assert blob["games"] == 3000
    assert set(blob["variants"]) == {"cage3_dv0", "cage2_dv1", "cage1_dv2", "cage0_dv3"}
    assert list(blob["cells"]["cage3_dv0"]) == ["t60", "hedrick", "unl", "d60", "g", "s60"]
    # Verify baseline 3 Battle Cage outperforms 0 Battle Cage / 3 DV vs T60 Dragapult
    assert blob["cells"]["cage3_dv0"]["t60"]["a"] > blob["cells"]["cage0_dv3"]["t60"]["a"]

