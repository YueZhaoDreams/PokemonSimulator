import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_FRIDAY_NAMES, SET_G_NAMES, build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"


def _load_stages():
    import importlib.util

    path = LAB / "set_g_stages.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_stages_chain_from_none_to_lock():
    mod = _load_stages()
    lists = mod.stage_lists()
    assert list(lists) == ["s0_none", "s1_mega", "s2_boss", "s3_poffin"]
    counts = {s: Counter(n) for s, n in lists.items()}
    for s, names in lists.items():
        assert len(names) == 60, s
        assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []
    assert counts["s0_none"]["Mega Clefable ex"] == 0
    assert counts["s0_none"]["Boss's Orders"] == 0
    assert counts["s0_none"]["Buddy-Buddy Poffin"] == 0
    assert counts["s0_none"]["Emolga"] == 1
    assert counts["s1_mega"] - counts["s0_none"] == Counter({"Mega Clefable ex": 1})
    assert counts["s0_none"] - counts["s1_mega"] == Counter({"Emolga": 1})
    assert counts["s2_boss"] - counts["s1_mega"] == Counter({"Boss's Orders": 3})
    assert counts["s1_mega"] - counts["s2_boss"] == Counter(
        {"Potion": 1, "Poké Ball": 1, "Plusle": 1}
    )
    assert counts["s2_boss"] == Counter(SET_G_FRIDAY_NAMES)
    assert counts["s3_poffin"] == Counter(SET_G_NAMES)
    assert counts["s3_poffin"] - counts["s2_boss"] == Counter({"Buddy-Buddy Poffin": 4})


def test_stages_json_covers_all_cells():
    blob = json.loads((LAB / "set-g-stages.json").read_text())
    assert blob["seed"] == 20260915
    assert blob["games"] == 3000
    foes = ("t60", "hedrick", "d60", "unl", "c60", "s60", "h")
    for stage in ("s0_none", "s1_mega", "s2_boss", "s3_poffin"):
        assert set(blob["cells"][stage]) == set(foes)
        for foe in foes:
            cell = blob["cells"][stage][foe]
            assert 0.0 <= cell["a"] <= 1.0
    for stage in ("s1_mega", "s2_boss", "s3_poffin"):
        assert set(blob["deltas_vs_prev"][stage]) == set(foes)
