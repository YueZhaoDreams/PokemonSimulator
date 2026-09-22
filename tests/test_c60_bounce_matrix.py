"""C60 bounce-slot swap matrix: only the five sleeve indexes change."""

import importlib.util
import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_C60_NAMES, build_fallback_deck, c60_names_before_bounce


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_c60_bounce_combo.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load_lab()


def test_bounce_slots_are_the_five_measured_cards():
    indexes = LAB.slot_indexes()
    assert indexes == (31, 32, 33, 34, 35)
    assert tuple(LAB.BASE_NAMES[i] for i in indexes) == LAB.BOUNCE_IN_LOCK
    assert LAB.VARIANTS["live"] == list(LAB.BASE_NAMES)


def test_cage_variant_matches_the_locked_list():
    assert Counter(LAB.VARIANTS["cage"]) == Counter(c60_names_before_bounce())
    assert Counter(LAB.VARIANTS["cage"]) == Counter(SET_C60_NAMES)
    assert LAB.VARIANT_SLOTS["cage"] == LAB.CAGE_IN_SLOTS
    assert SET_C60_NAMES.count("Penny") == 0
    assert SET_C60_NAMES.count("Iono") == 1


def test_variants_only_rewrite_the_five_slots_and_stay_legal():
    rules = standard_60_rules()
    indexes = set(LAB.slot_indexes())
    lock = list(LAB.BASE_NAMES)
    assert list(LAB.VARIANT_SLOTS) == list(LAB.VARIANTS)
    for key, names in LAB.VARIANTS.items():
        assert len(names) == 60, key
        assert copy_violations(build_fallback_deck(names), rules) == [], key
        assert LAB.VARIANT_SLOTS[key] == tuple(names[i] for i in LAB.slot_indexes())
        for i, (kept, trial) in enumerate(zip(lock, names)):
            if i not in indexes:
                assert kept == trial, (key, i, kept, trial)
    assert LAB.VARIANTS["penny2"].count("Penny") == 2
    assert LAB.VARIANTS["penny4"].count("Penny") == 4
    assert LAB.VARIANTS["iono-penny"].count("Penny") == 1
    assert LAB.VARIANTS["iono-penny"].count("Iono") == 0
    assert LAB.VARIANTS["iono-cheren"].count("Cheren's Care") == 1
    assert LAB.VARIANTS["az-for-turo"].count("AZ") == 1
    assert LAB.VARIANTS["az-for-turo"].count("Professor Turo's Scenario") == 0
    assert LAB.VARIANTS["turo-for-briney"].count("Professor Turo's Scenario") == 2
    assert LAB.VARIANTS["turo-for-briney"].count("Mr. Briney's Compassion") == 0
    assert LAB.VARIANTS["briney-for-turo"].count("Mr. Briney's Compassion") == 2
    assert LAB.VARIANTS["no-seeker"].count("Seeker") == 0
    assert LAB.VARIANTS["no-seeker"].count("Energy Switch") == 2
    assert LAB.VARIANTS["cheren-for-turo"].count("Cheren's Care") == 1
    assert LAB.VARIANTS["cage"].count("Penny") == 0


def test_bounce_matrix_json_keeps_the_cage_list():
    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-bounce-combo.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    assert blob["rule_preset"] == "s60"
    assert blob["foes"] == foes
    assert blob["slot_indexes"] == [31, 32, 33, 34, 35]
    assert list(blob["cells"]) == list(LAB.VARIANT_SLOTS)
    assert list(blob["lists"]) == list(LAB.VARIANT_SLOTS)
    cage = blob["cells"]["cage"]
    live = blob["cells"]["live"]
    penny2 = blob["cells"]["penny2"]
    penny4 = blob["cells"]["penny4"]
    iono_penny = blob["cells"]["iono-penny"]
    for row in blob["cells"].values():
        assert list(row) == foes
    assert Counter(blob["lists"]["cage"]) == Counter(SET_C60_NAMES)
    assert blob["lists"]["live"] == list(LAB.BASE_NAMES)
    assert cage["t60"]["a"] > live["t60"]["a"] + 0.08
    assert cage["d60"]["a"] > live["d60"]["a"] + 0.10
    assert cage["hedrick"]["a"] > live["hedrick"]["a"] + 0.04
    assert penny4["t60"]["a"] < penny2["t60"]["a"] < iono_penny["t60"]["a"] < cage["t60"]["a"]
    assert blob["weighted_competitive"]["cage"] > blob["weighted_competitive"]["live"] + 0.08
    assert abs(blob["weighted_competitive"]["iono-seeker"] - blob["weighted_competitive"]["cage"]) < 0.01
    assert cage["t60"]["a"] > blob["cells"]["iono-seeker"]["t60"]["a"] + 0.005
    assert blob["cells"]["iono-seeker"]["g"]["a"] > cage["g"]["a"] + 0.02
    assert blob["cells"]["iono-cheren"]["t60"]["bounce_cheren"] == 0
    assert blob["cells"]["iono-cheren"]["t60"]["bounce_fail"] > 500
    assert live["t60"]["bounce_penny"] > 1000
