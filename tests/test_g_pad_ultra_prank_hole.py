"""Held Pad and Ultra Ball still do not beat the energy-lock list."""

import json
from pathlib import Path


def _blob():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set-g-pad-ultra-prank-hole.json"
    return json.loads(path.read_text())


def test_hole_hold_keeps_the_three_card_package_out():
    blob = _blob()
    assert blob["games"] == 3000
    assert blob["seed"] == 20260923
    assert blob["policy"] == "hole_ex"
    cells = blob["cells"]
    base = cells["base"]
    comp = blob["weighted_competitive"]
    assert comp["full"] < comp["base"] - 0.008
    assert cells["full"]["t60"]["a"] < base["t60"]["a"]
    assert cells["full"]["hedrick"]["a"] < base["hedrick"]["a"] - 0.01
    assert cells["full"]["d60"]["a"] < base["d60"]["a"]
    assert cells["ultra"]["hedrick"]["a"] < base["hedrick"]["a"] - 0.02
    assert comp["ultra"] < comp["base"] - 0.01
    # Pad finds Clefairy and Ledian. The T60 gain on this base is not the Pad.
    assert cells["pad"]["t60"]["pad_fairy"] > cells["pad"]["t60"]["pad_ledian"] > 50
    assert cells["pad"]["t60"]["a"] < base["t60"]["a"]
    assert comp["pad"] - comp["base"] < 0.01
    assert cells["thin_energy"]["d60"]["a"] < base["d60"]["a"]
    assert comp["thin_energy"] > comp["base"]
