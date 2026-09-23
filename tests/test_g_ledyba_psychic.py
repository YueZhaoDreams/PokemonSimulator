"""Live G is the Ledyba → Psychic row of the joint matrix."""

import json
from pathlib import Path

from app.seed_data import SET_G_NAMES

ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "data" / "lab" / "set-g-ledyba-lillie.json"


def test_live_g_is_the_ledyba_psychic_row():
    blob = json.loads(BLOB.read_text())
    assert list(SET_G_NAMES) == blob["lists"]["ledyba_energy"]
    assert blob["lists"]["ledyba_energy"].count("Psychic Energy") == 20
    assert blob["lists"]["ledyba_energy"].count("Ledyba") == 2
    assert blob["lists"]["ledyba_energy"].count("Iris's Fighting Spirit") == 1
    assert blob["lists"]["ledyba_energy"].count("Lillie") == 0


def test_ledyba_psychic_beats_the_joint_lillie_swap():
    blob = json.loads(BLOB.read_text())
    w = blob["weighted_competitive"]
    assert w["ledyba_energy"] > w["base"] + 0.01
    assert w["ledyba_energy"] > w["both"] + 0.004
    assert w["ledyba_energy"] > w["both_energy"]
    assert abs(w["lillie_iris"] - w["base"]) < 0.002
    cells = blob["cells"]
    for seed in ("20260928", "20260929"):
        for foe in ("t60", "hedrick", "d60"):
            energy = cells["ledyba_energy"][foe]["by_seed"][seed]["wins"]
            base = cells["base"][foe]["by_seed"][seed]["wins"]
            assert energy > base
        assert cells["ledyba_energy"]["hedrick"]["by_seed"][seed]["wins"] > cells["both"]["hedrick"]["by_seed"][seed]["wins"]
        assert cells["ledyba_energy"]["c60"]["by_seed"][seed]["wins"] > cells["both"]["c60"]["by_seed"][seed]["wins"]
