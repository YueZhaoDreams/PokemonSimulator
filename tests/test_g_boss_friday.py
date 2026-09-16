from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_NAMES, build_fallback_deck


def _load():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_g_boss_friday.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAB = _load()


def test_live_g_is_friday_minus_three_boss():
    names = LAB.live_g_names()
    assert len(names) == 60
    counts = Counter(names)
    assert counts["Clefairy"] == 4
    assert counts["Ledyba"] == 4
    assert counts["Ledian"] == 4
    assert counts["Mega Clefable ex"] == 1
    assert counts["Tornadus"] == 1
    assert counts["Psychic Energy"] == 17
    assert counts["Boss's Orders"] == 0
    assert counts["Potion"] == 1
    assert counts["Poké Ball"] == 1
    assert counts["Plusle"] == 1
    assert counts["Mewtwo"] == 0
    assert counts["Emolga"] == 0
    assert counts["Mewtwo ex"] == 0
    seed = Counter(SET_G_NAMES)
    live = Counter(names)
    assert live - seed == Counter({"Potion": 1, "Poké Ball": 1, "Plusle": 1})
    assert seed - live == Counter({"Boss's Orders": 3})
    assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []


def test_three_boss_packages_stay_sixty_and_legal():
    base = LAB.live_g_names()
    for key, cuts in LAB.PACKAGES:
        names = LAB.add_boss(base, 3, cuts)
        assert len(names) == 60, key
        assert names.count("Boss's Orders") == 3, key
        assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []
        for cut in cuts:
            assert Counter(names)[cut] == Counter(base)[cut] - cuts.count(cut), (key, cut)


def test_one_boss_cut_each_candidate():
    base = LAB.live_g_names()
    for cut in LAB.CUT_ONE:
        names = LAB.add_boss(base, 1, (cut,))
        assert len(names) == 60
        assert names.count("Boss's Orders") == 1
        assert names.count(cut) == base.count(cut) - 1


def test_friday_g_is_locked_set_g_names():
    names = LAB.friday_g_names()
    live = Counter(LAB.live_g_names())
    friday = Counter(names)
    assert names == list(SET_G_NAMES)
    assert len(names) == 60
    assert friday["Boss's Orders"] == 3
    assert friday["Potion"] == 0
    assert friday["Poké Ball"] == 0
    assert friday["Plusle"] == 0
    assert friday["Mega Clefable ex"] == 1
    assert friday["Tornadus"] == 1
    assert friday["Clefairy"] == 4
    assert friday["Energy Switch"] == 1
    assert friday["Mewtwo"] == 0
    assert friday["Emolga"] == 0
    assert live - friday == Counter({"Potion": 1, "Poké Ball": 1, "Plusle": 1})
    assert friday - live == Counter({"Boss's Orders": 3})
    assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []


def test_friday_json_plusle_beats_baseline_on_dragapult():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-g-boss-friday.json").read_text()
    )
    plusle = blob["cells"]["plusle"]
    base = blob["cells"]["baseline"]
    assert plusle["t60"]["a"] > base["t60"]["a"]
    assert plusle["hedrick"]["a"] > base["hedrick"]["a"]
    assert plusle["unl"]["a"] > base["unl"]["a"]
    assert Counter(blob["lists"]["plusle"]) == Counter(LAB.friday_g_names())
    assert blob["friday_vs_live"] == {"add": ["Boss's Orders"] * 3, "cut": list(LAB.FRIDAY_CUTS)}
    confirm = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-g-boss-friday-confirm.json").read_text()
    )
    assert confirm["games"] == 3000
    assert confirm["weighted"]["plusle"] > confirm["weighted"]["junk"]
    assert confirm["weighted"]["plusle"] > confirm["weighted"]["baseline"]
