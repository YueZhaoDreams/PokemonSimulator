"""G → C60 Telepathic count: 2–4 copies, legal sixties, g attaches before Party."""

from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_C60_NAMES, SET_G_NAMES, SET_G_NEST_ZONE_NAMES, build_fallback_deck


def _load(name: str):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAB = _load("set_g_c60_telepathic.py")


def _blob():
    import json
    from pathlib import Path

    return json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-g-c60-telepathic.json").read_text()
    )


def test_tele_lists_are_sixty_and_legal():
    rules = standard_60_rules()
    by_c60 = dict(LAB.c60_lists())
    by_g = dict(LAB.g_lists())
    assert list(by_c60) == ["tele0", "tele2", "tele3", "tele4"]
    assert list(by_g) == ["tele0", "tele2", "tele3", "tele4"]
    assert by_c60["tele2"] == list(SET_C60_NAMES)
    assert by_g["tele0"] == list(SET_G_NEST_ZONE_NAMES)
    for key, names in [*by_c60.items(), *by_g.items()]:
        assert len(names) == 60, key
        n = int(key.replace("tele", ""))
        assert names.count("Telepathic Psychic Energy") == n, key
        assert copy_violations(build_fallback_deck(names), rules) == [], key
    assert by_c60["tele4"].count("Psychic Energy") == 12
    assert by_g["tele4"].count("Psychic Energy") == 13
    assert by_g["tele2"].count("Psychic Energy") == 15


def test_nest_zone_g_has_no_telepathic():
    names = list(SET_G_NEST_ZONE_NAMES)
    assert names.count("Telepathic Psychic Energy") == 0
    assert names.count("Psychic Energy") == 17
    assert names.count("Clefable ex") == 3
    assert names.count("Nest Ball") == 4
    assert names.count("Buddy-Buddy Poffin") == 4
    assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []


def test_four_telepathic_is_legal_on_both_lists():
    rules = standard_60_rules()
    assert copy_violations(build_fallback_deck(LAB.with_telepathic(SET_C60_NAMES, 4)), rules) == []
    assert copy_violations(build_fallback_deck(LAB.with_telepathic(SET_G_NEST_ZONE_NAMES, 4)), rules) == []
    five_c60 = LAB.with_telepathic(SET_C60_NAMES, 4)
    five_c60[five_c60.index("Psychic Energy")] = "Telepathic Psychic Energy"
    assert copy_violations(build_fallback_deck(five_c60), rules)


def test_g_lock_is_nest_zone_plus_two_telepathic():
    locked = Counter(SET_G_NAMES)
    nest = Counter(SET_G_NEST_ZONE_NAMES)
    assert len(SET_G_NAMES) == 60
    assert nest - locked == Counter({"Psychic Energy": 2})
    assert locked - nest == Counter({"Telepathic Psychic Energy": 2})
    assert locked["Psychic Energy"] == 15
    assert locked["Telepathic Psychic Energy"] == 2
    assert list(SET_G_NAMES) == LAB.with_telepathic(SET_G_NEST_ZONE_NAMES, 2)
    assert list(dict(LAB.g_lists())["tele2"]) == list(SET_G_NAMES)
    assert list(dict(LAB.c60_lists())["tele2"]) == list(SET_C60_NAMES)
    assert copy_violations(build_fallback_deck(list(SET_G_NAMES)), standard_60_rules()) == []


def test_bakeoff_sleeves_two_not_four():
    blob = _blob()
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    c60 = blob["c60"]
    g = blob["g"]
    assert c60["weighted_all"]["tele2"] > c60["weighted_all"]["tele4"]
    assert c60["weighted_all"]["tele2"] > c60["weighted_all"]["tele0"]
    assert c60["cells"]["tele2"]["hedrick"]["a"] > c60["cells"]["tele4"]["hedrick"]["a"] + 0.01
    assert c60["cells"]["tele2"]["t60"]["second"] > c60["cells"]["tele4"]["t60"]["second"]
    assert g["cells"]["tele2"]["t60"]["a"] > g["cells"]["tele0"]["t60"]["a"] + 0.03
    assert g["cells"]["tele2"]["hedrick"]["a"] > g["cells"]["tele0"]["hedrick"]["a"] + 0.04
    assert g["weighted_competitive"]["tele2"] > g["weighted_competitive"]["tele0"]
    assert g["weighted_competitive"]["tele2"] > g["weighted_competitive"]["tele4"]
    assert g["cells"]["tele2"]["d60"]["a"] >= g["cells"]["tele4"]["d60"]["a"]
    assert Counter(c60["lists"]["tele2"]) == Counter(SET_C60_NAMES)
    assert Counter(g["lists"]["tele2"]) == Counter(SET_G_NAMES)
    assert Counter(g["lists"]["tele0"]) == Counter(SET_G_NEST_ZONE_NAMES)


def test_g_strategy_mentions_telepathic_before_party():
    from app.engine.strategies import StrategySpec

    spec = StrategySpec.from_dict("g")
    text = spec.description.lower()
    assert "telepathic" in text
    assert "before" in text and "party" in text
