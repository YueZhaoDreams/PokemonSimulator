"""C60 bounce-slot swap matrix: only the five sleeve indexes change."""

import importlib.util
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


def test_bounce_slots_are_the_five_live_cards():
    indexes = LAB.slot_indexes()
    assert len(indexes) == 5
    assert tuple(SET_C60_NAMES[i] for i in indexes) == LAB.BOUNCE_IN_LOCK
    assert LAB.VARIANTS["live"] == list(SET_C60_NAMES)


def test_cage_variant_matches_pre_bounce_lock():
    assert Counter(LAB.VARIANTS["cage"]) == Counter(c60_names_before_bounce())
    assert LAB.VARIANT_SLOTS["cage"] == LAB.CAGE_IN_SLOTS


def test_variants_only_rewrite_the_five_slots_and_stay_legal():
    rules = standard_60_rules()
    indexes = set(LAB.slot_indexes())
    lock = list(SET_C60_NAMES)
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
