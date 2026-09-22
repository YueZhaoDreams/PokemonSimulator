"""Pad + CLC paid by cutting Clefable ex / energy / other 1-ofs, not only Hop."""

import importlib.util
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_C60_NAMES, build_fallback_deck


def _load(name: str):
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load("set_c60_pad_clc_cuts.py")
PAD = _load("set_c60_pad_metronome.py")


def test_cut_keys_and_baselines():
    by_key = dict(LAB.variant_lists())
    assert list(by_key)[:2] == ["prankish2", "pad"]
    assert [key for key, _card in LAB.CUTS] == list(by_key)[2:]
    assert Counter(by_key["prankish2"]) == Counter(SET_C60_NAMES)
    assert Counter(by_key["pad"]) == Counter(PAD.pad_list())
    assert by_key["pad"].count("Clefable") == 1
    assert by_key["pad"].count("Poké Pad") == 1
    assert "Clefable CLC" not in by_key["pad"]


def test_each_cut_is_pad_plus_one_clc_minus_that_card():
    rules = standard_60_rules()
    pad = Counter(LAB.pad_list())
    by_key = dict(LAB.variant_lists())
    for key, card in LAB.CUTS:
        names = by_key[key]
        assert len(names) == 60, key
        cards = build_fallback_deck(names)
        assert copy_violations(cards, rules) == [], key
        got = Counter(names)
        want = pad.copy()
        want[card] -= 1
        if want[card] == 0:
            del want[card]
        want["Clefable CLC"] += 1
        assert got == want, key
        assert names.count("Poké Pad") == 1, key
        assert names.count("Clefable CLC") == 1, key
        fables = [c for c in cards if c.name == "Clefable"]
        assert Counter(c.catalog_id for c in fables) == Counter({"swsh2-75": 1, "clc-014": 1}), key


def test_hop_cut_matches_previous_pad_clc_list():
    assert Counter(LAB.pad_plus_clc("Hop")) == Counter(PAD.pad_clc_list())
    assert LAB.pad_plus_clc("Hop").count("Hop") == 1
    assert LAB.pad_list().count("Hop") == 2


def test_ex_and_energy_cuts_leave_two_ex_and_thirteen_psychic():
    by_key = dict(LAB.variant_lists())
    assert by_key["ex"].count("Clefable ex") == 2
    assert by_key["energy"].count("Psychic Energy") == 13
    assert by_key["pad"].count("Clefable ex") == 3
    assert by_key["pad"].count("Psychic Energy") == 14
    assert SET_C60_NAMES.count("Clefable") == 2
    assert SET_C60_NAMES.count("Poké Pad") == 0


def test_pad_clc_cuts_json_cells_follow_foe_order():
    import json

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-pad-clc-cuts.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    assert list(blob["foes"]) == foes
    assert list(blob["cells"])[:2] == ["prankish2", "pad"]
    assert list(blob["cells"])[2:] == [key for key, _card in LAB.CUTS]
    assert blob["lock"].startswith("none")
    for row in blob["cells"].values():
        assert list(row) == foes
    pad = blob["cells"]["pad"]
    # Named cuts the designer asked about all lose T60 to pad-only.
    assert blob["cells"]["hop"]["t60"]["a"] < pad["t60"]["a"]
    assert blob["cells"]["ex"]["t60"]["a"] < pad["t60"]["a"]
    assert blob["cells"]["energy"]["t60"]["a"] < pad["t60"]["a"]
    assert blob["weighted_competitive"]["hop"] < blob["weighted_competitive"]["pad"]
    assert blob["cells"]["ultra"]["t60"]["pad_metro"] > 0
    assert blob["cells"]["mega"]["t60"]["copy_dive"] > 0
    assert pad["t60"]["copy_dive"] == 0
    assert SET_C60_NAMES.count("Clefable") == 2
    assert SET_C60_NAMES.count("Poké Pad") == 0
