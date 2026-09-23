"""Review matrix on fresh seeds: Pad ties Ledyba, the second Ultra Ball loses."""

import json
from pathlib import Path

from app.seed_data import SET_G_NAMES


def _blob(name: str):
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / name
    return json.loads(path.read_text())


def test_review_uses_fresh_seeds_and_6000_games():
    blob = _blob("set-g-pad-ultra-review.json")
    assert blob["policy"] == "ultra_fixed"
    assert blob["seeds"] == [20260924, 20260925]
    assert blob["lists"]["base"] == list(SET_G_NAMES)
    assert all(cell["games"] == 6000 for row in blob["cells"].values() for cell in row.values())


def test_review_reading():
    blob = _blob("set-g-pad-ultra-review.json")
    comp = blob["weighted_competitive"]
    cells = blob["cells"]
    assert abs(comp["pad"] - comp["base"]) < 0.01
    assert comp["ultra"] < comp["base"] - 0.015
    assert comp["ultra"] < comp["ledian_energy"] - 0.015
    assert comp["full"] < comp["base"] - 0.01
    assert comp["prank"] < comp["munk_energy"] - 0.008
    assert comp["thin_energy"] > comp["base"]
    assert cells["ultra"]["t60"]["a"] < cells["base"]["t60"]["a"] - 0.02


def test_held_ultra_ball_lost_to_the_fixed_order_on_the_base_list():
    held = _blob("set-g-pad-ultra-review-ultrahole.json")["cells"]["base"]
    fixed = _blob("set-g-pad-ultra-review.json")["cells"]["base"]
    for foe in ("t60", "hedrick", "c60"):
        assert held[foe]["a"] < fixed[foe]["a"], foe
