"""Four-Psychic G vs this C60 shipment. One Lillie for Iris; the rest stay out."""

import json
from pathlib import Path

from app.seed_data import SET_G_NAMES

ROOT = Path(__file__).resolve().parents[1]
BLOB = json.loads((ROOT / "data/lab/set-g-four-psychic-arrival.json").read_text())
CONTROLS = json.loads((ROOT / "data/lab/set-g-four-psychic-arrival-controls.json").read_text())


def test_matrix_is_the_four_psychic_list():
    assert BLOB["games_per_seed"] == 3000
    assert BLOB["seeds"] == [20260926, 20260927]
    assert BLOB["lists"]["base"] == list(SET_G_NAMES)
    assert BLOB["lists"]["base"].count("Psychic Energy") == 19
    assert BLOB["lists"]["lillie_iris"].count("Lillie") == 1
    assert "Iris's Fighting Spirit" not in BLOB["lists"]["lillie_iris"]
    assert BLOB["lists"]["slice"].count("Lillie") == 2
    assert BLOB["lists"]["slice"].count("Poké Pad") == 1
    assert BLOB["lists"]["slice"].count("Ultra Ball") == 2
    assert BLOB["lists"]["slice"].count("Clefable") == 1
    assert CONTROLS["seeds"] == [20260926, 20260927]
    assert CONTROLS["cells"]["iris_energy"]["t60"]["games"] == 6000


def test_one_lillie_beats_iris_and_the_package_loses():
    w = BLOB["weighted_competitive"]
    iris_energy = CONTROLS["weighted_competitive"]["iris_energy"]
    assert w["lillie_iris"] > w["base"] + 0.005
    assert w["lillie_iris"] > iris_energy + 0.005
    assert w["lillie2"] - w["lillie_iris"] < 0.005
    assert w["slice"] < w["base"] - 0.01
    assert w["pad"] < w["ledyba_energy"]
    assert w["ledyba_energy"] > w["base"]
    assert w["prank"] < w["base"] - 0.01
    assert w["prank"] < w["munk_energy"]
    assert w["ultra"] < w["ledian_energy"]
    assert w["stretcher"] - w["base"] < 0.005
