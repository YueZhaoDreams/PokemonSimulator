"""The Sky Field copies lab report is a legal one-swap path from the locked Set M list."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path

import pytest

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"


def _load_copies():
    sys.path.insert(0, str(LAB))
    try:
        spec = importlib.util.spec_from_file_location("set_m_sky_copies", LAB / "set_m_sky_copies.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(LAB))
    return module


def _report() -> dict:
    return json.loads((LAB / "set-m-sky-copies.json").read_text())["report"]


def test_copies_report_adds_one_sky_field_per_step_and_stays_legal():
    rep = _report()
    assert rep["done"] is True
    assert rep["seed"] == 20261007
    assert rep["games"] == 1000
    historical = json.loads((LAB / "set-m-sky-field.json").read_text())["report"]["list_start"]
    assert rep["list_start"] == historical
    assert abs(sum(rep["weights"].values()) - 1.0) < 1e-9
    array = rep["array"]
    assert [row["label"] for row in array] == ["Set M", "Sky Field 1", "Sky Field 2", "Sky Field 3", "Sky Field 4"]
    assert [row["sky"] for row in array] == [0, 1, 2, 3, 4]
    rules = standard_60_rules()
    previous = Counter(historical)
    for row in array[1:]:
        names = row["list"]
        assert len(names) == 60
        assert copy_violations(build_fallback_deck(names), rules) == []
        now = Counter(names)
        gained = now - previous
        lost = previous - now
        assert dict(gained) == {"Sky Field": 1}
        assert list(lost) == [row["cut"]] and sum(lost.values()) == 1
        previous = now
    assert "Budew" not in array[-1]["list"]
    assert rep["list"] == array[-1]["list"]


def test_copies_report_best_indexes_match_the_rows():
    rep = _report()
    array = rep["array"]
    assert rep["best_index"] == max(range(len(array)), key=lambda i: (array[i]["weighted"], -i))
    assert rep["best_pooled_index"] == max(
        range(len(array)), key=lambda i: (array[i]["pooled"]["weighted"], -i)
    )
    for row in array:
        first, second, pooled = row["holdout"], row["holdout2"], row["pooled"]
        low = min(first["weighted"], second["weighted"])
        high = max(first["weighted"], second["weighted"])
        assert low - 1e-9 <= pooled["weighted"] <= high + 1e-9
        assert pooled["games"] == rep["holdout_games"] + rep["holdout2_games"]
    assert rep["holdout_seed"] != rep["seed"] != rep["holdout2_seed"]
    assert rep["holdout_seed"] != rep["holdout2_seed"]


def test_pool_weights_each_seed_by_its_games():
    copies = _load_copies()
    keys = [key for key, *_ in copies.FOES]
    weights = {key: 1 / len(keys) for key in keys}
    first = {key: {"a": 0.5, "games": 1000} for key in keys}
    second = {key: {"a": 0.8, "games": 3000} for key in keys}
    pooled = copies.pool(first, second, weights)
    assert pooled["games"] == 4000
    for key in keys:
        assert pooled["cells"][key]["games"] == 4000
        assert pooled["cells"][key]["a"] == pytest.approx((0.5 * 1000 + 0.8 * 3000) / 4000)
    assert pooled["weighted"] == pytest.approx(0.725)
    expected_se = math.sqrt(sum((1 / len(keys)) ** 2 * 0.725 * 0.275 / 4000 for _ in keys))
    assert pooled["se"] == pytest.approx(expected_se)
    assert pooled["mean"] == pytest.approx(0.725)
    assert pooled["worst"] == pytest.approx(0.725)


def test_confirm_report_compares_set_m_with_the_two_sky_field_row_on_a_new_seed():
    rep = json.loads((LAB / "set-m-sky-confirm.json").read_text())["report"]
    copies = _report()
    assert rep["list_set_m"] == copies["list_start"]
    assert rep["list_two_sky"] == copies["array"][2]["list"]
    assert rep["list_two_sky"].count("Sky Field") == 2
    assert rep["weights"] == copies["weights"]
    used = {copies["seed"], copies["holdout_seed"], copies["holdout2_seed"]}
    assert rep["seed"] not in used
    assert rep["games"] == 8000
    for key in ("set_m", "two_sky"):
        assert all(cell["games"] == rep["games"] for cell in rep[key]["cells"].values())
    diff = rep["two_sky"]["weighted"] - rep["set_m"]["weighted"]
    assert rep["diff"] == pytest.approx(diff)
    se = (rep["two_sky"]["se"] ** 2 + rep["set_m"]["se"] ** 2) ** 0.5
    assert rep["z"] == pytest.approx(diff / se)
