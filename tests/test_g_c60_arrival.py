"""This C60 shipment does not enter live G. The lab json is the lock."""

import json
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_NAMES, build_fallback_deck


def _load():
    import importlib.util

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_g_c60_arrival.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _blob():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set-g-c60-arrival.json"
    return json.loads(path.read_text())


def test_arrival_lists_stay_legal_and_live_is_the_lock():
    lab = _load()
    rules = standard_60_rules()
    lists = dict(lab.g_lists())
    assert lists["live"] == list(SET_G_NAMES)
    assert SET_G_NAMES.count("Ledian") == 3
    assert SET_G_NAMES.count("Ledyba") == 4
    assert SET_G_NAMES.count("Munkidori") == 2
    assert SET_G_NAMES.count("Psychic Energy") == 16
    assert SET_G_NAMES.count("Lillie") == 0
    assert SET_G_NAMES.count("Poké Pad") == 0
    assert SET_G_NAMES.count("Night Stretcher") == 0
    assert SET_G_NAMES.count("Clefable") == 0
    assert SET_G_NAMES.count("Ultra Ball") == 1
    assert "Drayton" in SET_G_NAMES
    assert "Energy Retrieval" in SET_G_NAMES
    for key, names in lists.items():
        assert len(names) == 60, key
        assert copy_violations(build_fallback_deck(names), rules) == [], key


def test_bakeoff_boxes_the_shipment():
    blob = _blob()
    assert blob["games"] == 3000
    assert blob["seed"] == 20260923
    comp = blob["weighted_competitive"]
    cells = blob["cells"]
    live = cells["live"]
    assert comp["slice"] < comp["live"] - 0.02
    assert cells["stretcher"]["hedrick"]["a"] < live["hedrick"]["a"] - 0.015
    assert cells["stretcher"]["c60"]["a"] < live["c60"]["a"] - 0.02
    assert cells["lillie_drayton"]["t60"]["a"] < live["t60"]["a"] - 0.01
    assert comp["l2s_prank2"] < comp["l2s_prank"] < comp["live"]
    assert comp["l2s_ultra"] < comp["live"]
    assert comp["l2s_pad2"] < comp["live"]
    # The Pad-for-Ledian bump is the Ledian cut. A 16th Psychic beats the Pad
    # on Hedrick, the C60 mirror, and the whole field.
    assert cells["ledian_energy"]["hedrick"]["a"] > cells["pad_ledian"]["hedrick"]["a"]
    assert cells["ledian_energy"]["c60"]["a"] > cells["pad_ledian"]["c60"]["a"]
    assert blob["weighted_all"]["ledian_energy"] > blob["weighted_all"]["pad_ledian"]
    assert cells["iris_pad"]["t60"]["a"] < live["t60"]["a"]
    assert cells["psychic_pad"]["hedrick"]["a"] < live["hedrick"]["a"]
