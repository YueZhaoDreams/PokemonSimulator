"""Pad + Ultra Ball + Prankish do not enter the energy-lock G. The lab json is the lock."""

import json
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_NAMES, build_fallback_deck


def _load():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_g_pad_ultra_prank.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _blob():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set-g-pad-ultra-prank.json"
    return json.loads(path.read_text())


def test_package_lists_stay_legal_and_base_is_the_energy_lock():
    lab = _load()
    rules = standard_60_rules()
    lists = dict(lab.g_lists())
    assert lists["base"] == list(SET_G_NAMES)
    assert SET_G_NAMES.count("Ledian") == 3
    assert SET_G_NAMES.count("Ledyba") == 4
    assert SET_G_NAMES.count("Munkidori") == 2
    assert SET_G_NAMES.count("Psychic Energy") == 16
    assert SET_G_NAMES.count("Poké Pad") == 0
    assert SET_G_NAMES.count("Clefable") == 0
    assert SET_G_NAMES.count("Ultra Ball") == 1
    full = lists["full"]
    assert full.count("Poké Pad") == 1
    assert full.count("Ultra Ball") == 2
    assert full.count("Clefable") == 1
    assert full.count("Ledyba") == 3
    assert full.count("Ledian") == 2
    assert full.count("Munkidori") == 1
    for key, names in lists.items():
        assert len(names) == 60, key
        assert copy_violations(build_fallback_deck(names), rules) == [], key


def test_bakeoff_keeps_pad_ultra_and_prankish_out():
    blob = _blob()
    assert blob["games"] == 3000
    assert blob["seed"] == 20260923
    assert blob["policy"] == "fixed_prefer"
    cells = blob["cells"]
    base = cells["base"]
    comp = blob["weighted_competitive"]
    # Shipped search, not the on-demand hole picker (that base was Hedrick 36.3 / S60 71.9).
    assert base["hedrick"]["a"] > 0.40
    assert base["s60"]["a"] > 0.80
    assert comp["full"] < comp["base"] - 0.008
    assert cells["full"]["hedrick"]["a"] < base["hedrick"]["a"] - 0.01
    assert cells["full"]["d60"]["a"] < base["d60"]["a"] - 0.01
    assert cells["full"]["unl"]["a"] < base["unl"]["a"] - 0.015
    assert cells["full"]["c60"]["a"] < base["c60"]["a"] - 0.01
    assert cells["ultra"]["hedrick"]["a"] < base["hedrick"]["a"] - 0.02
    assert cells["ultra"]["c60"]["a"] < base["c60"]["a"] - 0.02
    assert comp["ultra"] < comp["base"] - 0.005
    assert comp["prank"] < comp["base"]
    assert comp["ultra_prank"] < comp["full"]
    # Pad does take Prankish when both are sleeved. The pair still loses.
    assert cells["pad_prank"]["t60"]["pad_prank"] > 100
    assert comp["pad_prank"] < comp["base"]
    # Pad alone and the three-Psychic control are inside 1 pp of wComp, and
    # the energy control gives up D60. Neither replaces the lock.
    assert comp["pad"] - comp["base"] < 0.01
    assert comp["thin_energy"] - comp["base"] < 0.01
    assert cells["thin_energy"]["d60"]["a"] < base["d60"]["a"]
