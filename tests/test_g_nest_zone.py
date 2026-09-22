"""Nest / Zone arrival: 10 cards in, bird line thinned to 1-1-1."""

from collections import Counter

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_G_NAMES, SET_G_NEST_ZONE_NAMES, SET_G_POFFIN_NAMES, build_fallback_deck


def _load(name: str):
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / name
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


LAB = _load("set_g_nest_zone.py")

ADDS = Counter(
    {
        "Nest Ball": 4,
        "Clefable ex": 3,
        "Energy Switch": 1,
        "Switch": 2,
    }
)
CUTS = Counter(
    {
        "Starly": 1,
        "Staravia": 1,
        "Staraptor": 1,
        "Surfer": 1,
        "Kecleon": 1,
        "Boomerang Energy": 1,
        "Flutter Mane": 1,
        "Energy Search": 1,
        "Trekking Shoes": 1,
        "Tulip": 1,
    }
)


def _blob():
    import json
    from pathlib import Path

    return json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-g-nest-zone.json").read_text()
    )


def test_packages_are_sixty_and_legal():
    for key, cuts in LAB.PACKAGES:
        names = LAB.arrive(cuts)
        assert len(names) == 60, key
        assert names.count("Nest Ball") == 4, key
        assert names.count("Clefable ex") == 3, key
        assert names.count("Switch") == 2, key
        assert names.count("Energy Switch") == 2, key
        assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []


def test_bird_thin_is_the_lock():
    locked = Counter(SET_G_NEST_ZONE_NAMES)
    poffin = Counter(SET_G_POFFIN_NAMES)
    assert len(SET_G_NEST_ZONE_NAMES) == 60
    assert len(SET_G_NAMES) == 60
    assert poffin - locked == CUTS
    assert locked - poffin == ADDS
    assert locked["Ledian"] == 4
    assert locked["Ledyba"] == 4
    assert locked["Psychic Energy"] == 17
    assert locked["Darkness Energy"] == 3
    assert locked["Munkidori"] == 2
    assert copy_violations(build_fallback_deck(list(SET_G_NEST_ZONE_NAMES)), standard_60_rules()) == []


def test_bird_thin_beats_poffin_lock_on_both_weights():
    blob = _blob()
    assert blob["packages"]["bird_thin"] == list(CUTS.elements())
    w = blob["weighted_all"]
    c = blob["weighted_competitive"]
    assert w["bird_thin"] > w["baseline"]
    assert w["bird_thin"] > w["ledian_thin"] > w["baseline"]
    assert c["bird_thin"] > c["baseline"]
    assert w["psychic3"] < w["baseline"]
    assert w["dark_out"] < w["baseline"]
    confirm = blob["confirm"]
    assert confirm["bird_thin"]["t60"]["a"] > confirm["baseline"]["t60"]["a"]
    assert confirm["bird_thin"]["hedrick"]["a"] > confirm["baseline"]["hedrick"]["a"] + 0.03
    assert confirm["bird_thin"]["s60"]["a"] > confirm["baseline"]["s60"]["a"]
    assert confirm["bird_thin"]["unl"]["a"] > confirm["baseline"]["unl"]["a"]
    assert blob["confirm_weighted"]["bird_thin"] > blob["confirm_weighted"]["baseline"]
