"""The Elekid search report is a legal one-swap path from the locked Set M, and its tables line up."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_M60_NAMES, build_fallback_deck
from data.lab.set_m_sky_field import FOES, loss_weights

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"


def _report(name: str) -> dict:
    return json.loads((LAB / name).read_text())["report"]


def test_elekid_search_path_adds_one_elekid_per_step_from_the_locked_list():
    rep = _report("set-m-elekid.json")
    start = list(rep["list_start"])
    assert rep["done"] is True
    assert rep["list_set_m"] == start
    assert rep["start_label"] == "Start (no Elekid)"
    assert rep["weights_from"] == "locked Set M on the selection seed"
    assert Counter(start)["Elekid"] == 0
    assert Counter(start)["Battle Cage"] == 4
    assert Counter(start)["Manaphy"] == 1
    assert Counter(start)["Counter Catcher"] == 1
    live = Counter(SET_M60_NAMES)
    assert live - Counter(start) == Counter({"Elekid": 1})
    assert Counter(start) - live == Counter({"Battle Cage": 1})
    path = rep["path"]
    assert path[0]["list"] == start and Counter(start)["Elekid"] == 0
    assert path[0]["cut"] is None
    rates = {key: path[0]["cells"][key]["a"] for key, *_ in FOES}
    assert rep["weights"] == loss_weights(rates)
    rules = standard_60_rules()
    previous = Counter(start)
    for copies, row in enumerate(path):
        names = row["list"]
        assert len(names) == 60
        assert copy_violations(build_fallback_deck(names), rules) == []
        assert row["copies"] == copies == Counter(names)["Elekid"]
        if copies == 0:
            continue
        now = Counter(names)
        gained, lost = now - previous, previous - now
        assert dict(gained) == {"Elekid": 1}
        assert list(lost) == [row["cut"]] and sum(lost.values()) == 1
        previous = now
    assert rep["list"] == path[-1]["list"]
    assert len(rep["steps"]) == len(path) - 1 == 4


def test_elekid_search_fresh_and_clean_tables_cover_the_path():
    rep = _report("set-m-elekid.json")
    path = rep["path"]
    labels = [row["label"] for row in path]
    assert [row["label"] for row in rep["fresh"]] == labels
    games = rep["fresh1_games"] + rep["fresh2_games"]
    for row in rep["fresh"]:
        low = min(row["seed1"]["weighted"], row["seed2"]["weighted"])
        high = max(row["seed1"]["weighted"], row["seed2"]["weighted"])
        assert low - 1e-9 <= row["pooled"]["weighted"] <= high + 1e-9
        assert all(cell["games"] == games for cell in row["pooled"]["cells"].values())
    clean = {row["label"]: row for row in rep["clean_rows"]}
    assert {path[0]["label"], path[-1]["label"], rep["best_fresh_label"]} <= set(clean)
    assert clean[path[0]["label"]]["list"] == list(rep["list_start"])
    fresh = {row["label"]: row for row in rep["fresh"]}
    assert rep["best_fresh_label"] == max(
        (row["label"] for row in path), key=lambda label: fresh[label]["pooled"]["weighted"]
    )
    assert all(
        cell["games"] == rep["clean_games"] for row in clean.values() for cell in row["clean"]["cells"].values()
    )
    seeds = {rep["seed"], rep["fresh1_seed"], rep["fresh2_seed"], rep["clean_seed"]}
    assert len(seeds) == 4
    assert (rep["clean_seed"], rep["clean_games"]) == (20261029, 8000)
    assert abs(sum(rep["weights"].values()) - 1.0) < 1e-9
    assert set(rep["weights"]) == {key for key, *_ in FOES}


def test_elekid_use_is_counted_per_game():
    rep = _report("set-m-elekid.json")
    start, *with_elekid = rep["path"]
    assert start["usage"]["elekid_own"] == 0
    assert start["usage"]["elekid_mew"] == 0
    assert start["usage"]["elekid_games"] == 0
    for row in with_elekid:
        use = row["usage"]
        assert 0 <= use["elekid_games"] <= 1
        assert use["elekid_own"] + use["elekid_mew"] + 1e-9 >= use["elekid_games"]
        assert use["snipe_ko_bench"] <= use["snipe_ko"] + 1e-9
        assert "elekid_own" in row["usage"] and "elekid_mew" in row["usage"]
