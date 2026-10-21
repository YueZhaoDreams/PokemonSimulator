"""The Elekid search report is a legal one-swap path from the best gust-search list, and its tables line up."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import SET_M60_NAMES, build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"


def _report(name: str) -> dict:
    return json.loads((LAB / name).read_text())["report"]


def test_elekid_search_path_adds_one_elekid_per_step_from_the_best_list():
    rep = _report("set-m-elekid.json")
    prior = _report("set-m-gust-search.json")
    start = next(row["list"] for row in prior["path"] if row["label"] == prior["best_fresh_label"])
    assert rep["done"] is True
    assert rep["list_set_m"] == list(SET_M60_NAMES) == prior["list_set_m"]
    assert rep["list_start"] == start
    assert rep["weights"] == prior["weights"]
    path = rep["path"]
    assert path[0]["list"] == start and Counter(start)["Elekid"] == 0
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
    assert len(rep["steps"]) == len(path) - 1


def test_elekid_search_fresh_and_clean_tables_cover_the_path():
    rep = _report("set-m-elekid.json")
    path = rep["path"]
    labels = ["Set M"] + [row["label"] for row in path]
    assert [row["label"] for row in rep["fresh"]] == labels
    games = rep["fresh1_games"] + rep["fresh2_games"]
    for row in rep["fresh"]:
        low = min(row["seed1"]["weighted"], row["seed2"]["weighted"])
        high = max(row["seed1"]["weighted"], row["seed2"]["weighted"])
        assert low - 1e-9 <= row["pooled"]["weighted"] <= high + 1e-9
        assert all(cell["games"] == games for cell in row["pooled"]["cells"].values())
    clean = {row["label"]: row for row in rep["clean_rows"]}
    assert {"Set M", path[0]["label"], path[-1]["label"], rep["best_fresh_label"]} == set(clean)
    fresh = {row["label"]: row for row in rep["fresh"]}
    assert rep["best_fresh_label"] == max(
        (row["label"] for row in path), key=lambda label: fresh[label]["pooled"]["weighted"]
    )
    assert all(
        cell["games"] == rep["clean_games"] for row in clean.values() for cell in row["clean"]["cells"].values()
    )
    seeds = {rep["seed"], rep["fresh1_seed"], rep["fresh2_seed"], rep["clean_seed"]}
    assert len(seeds) == 4
    assert abs(sum(rep["weights"].values()) - 1.0) < 1e-9


def test_elekid_search_clean_seed_matches_the_run_before_the_engine_change():
    rep = _report("set-m-elekid.json")
    prior = _report("set-m-gust-search.json")
    assert (rep["clean_seed"], rep["clean_games"]) == (prior["clean_seed"], prior["clean_games"])
    before = rep["before_engine"]
    clean_before = {row["label"]: row["clean"] for row in prior["clean_rows"]}
    assert before["Set M"]["weighted"] == clean_before["Set M"]["weighted"]
    assert before["start"]["weighted"] == clean_before[rep["start_label"]]["weighted"]


def test_elekid_use_is_counted_per_game():
    rep = _report("set-m-elekid.json")
    start, *with_elekid = rep["path"]
    assert start["usage"]["elekid_own"] == 0 and start["usage"]["elekid_games"] == 0
    for row in with_elekid:
        use = row["usage"]
        assert 0 < use["elekid_games"] <= 1
        assert use["elekid_own"] + use["elekid_mew"] >= use["elekid_games"]
        assert use["snipe_ko_bench"] <= use["snipe_ko"]
