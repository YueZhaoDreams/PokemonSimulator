from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_NAMES, build_fallback_deck


def _load():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_g_boss_friday.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load()


def test_live_g_matches_combocub_20260915():
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
    assert counts["Mewtwo"] == 0
    assert counts["Emolga"] == 0
    assert counts["Mewtwo ex"] == 0
    seed = Counter(SET_G_NAMES)
    live = Counter(names)
    assert live - seed == Counter({"Mega Clefable ex": 1, "Tornadus": 1})
    assert seed - live == Counter({"Mewtwo": 1, "Emolga": 1})
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
