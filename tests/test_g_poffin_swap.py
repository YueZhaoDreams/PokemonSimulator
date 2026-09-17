from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import build_fallback_deck, fallback_named


def _load():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_g_poffin_swap.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAB = _load()


def test_poffin_baseline_is_prefriday_live_g():
    names = LAB.baseline_g_names()
    assert len(names) == 60
    counts = Counter(names)
    assert counts["Boss's Orders"] == 0
    assert counts["Buddy-Buddy Poffin"] == 0
    assert counts["Potion"] == 1
    assert counts["Poké Ball"] == 1
    assert counts["Plusle"] == 1
    assert counts["Mega Clefable ex"] == 1
    assert counts["Tornadus"] == 1
    assert counts["Clefairy"] == 4
    assert counts["Psychic Energy"] == 17
    assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []


def test_poffin_print_and_targets_match_live_g():
    poffin = fallback_named("Buddy-Buddy Poffin")
    assert poffin.catalog_id == "sv05-144"
    assert "70 HP or less" in (poffin.text or "")
    targets = {
        name
        for name in set(LAB.baseline_g_names())
        if (c := fallback_named(name)).category == "Pokemon"
        and (c.stage or "").lower() == "basic"
        and (c.hp or 999) <= 70
    }
    assert {"Clefairy", "Ledyba", "Starly", "Kecleon"} <= targets


def test_poffin_packages_stay_sixty_and_legal():
    base = LAB.baseline_g_names()
    for key, cuts in LAB.PACKAGES:
        names = LAB.add_poffin(base, cuts)
        assert len(names) == 60, key
        assert names.count("Buddy-Buddy Poffin") == len(cuts), key
        assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []
        for cut in set(cuts):
            assert Counter(names)[cut] == Counter(base)[cut] - cuts.count(cut), (key, cut)
