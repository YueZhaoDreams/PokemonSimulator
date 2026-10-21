"""The gust search report is a legal one-swap path from the best Sky Field and Budew list, and its tables line up."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"
ADDS = {"Boss's Orders", "Counter Catcher"}


def _report(name: str) -> dict:
    return json.loads((LAB / name).read_text())["report"]


def test_gust_search_path_is_legal_one_swap_steps_from_the_best_list():
    rep = _report("set-m-gust-search.json")
    prior = _report("set-m-best-search.json")
    start = next(row["list"] for row in prior["path"] if row["label"] == prior["best_fresh_label"])
    assert rep["done"] is True
    assert rep["list_set_m"] == prior["list_set_m"]
    assert rep["list_start"] == start
    assert rep["weights"] == prior["weights"]
    path = rep["path"]
    assert path[0]["list"] == rep["list_start"]
    rules = standard_60_rules()
    previous = Counter(path[0]["list"])
    for before, row in zip(path, path[1:]):
        names = row["list"]
        assert len(names) == 60
        assert copy_violations(build_fallback_deck(names), rules) == []
        now = Counter(names)
        gained, lost = now - previous, previous - now
        assert list(gained) == [row["add"]] and sum(gained.values()) == 1
        assert row["add"] in ADDS
        assert list(lost) == [row["cut"]] and sum(lost.values()) == 1
        assert row["weighted"] > before["weighted"]
        previous = now
    assert rep["list"] == path[-1]["list"]
    taken = [step for step in rep["steps"] if step["accepted"]]
    assert len(taken) == len(path) - 1
    assert all(not step["accepted"] for step in rep["steps"][len(taken):])


def test_gust_search_fresh_and_clean_tables_cover_the_path():
    rep = _report("set-m-gust-search.json")
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


def test_gust_search_clean_seed_matches_the_run_before_the_fix():
    rep = _report("set-m-gust-search.json")
    prior = _report("set-m-best-search.json")
    assert (rep["clean_seed"], rep["clean_games"]) == (prior["clean_seed"], prior["clean_games"])
    before = rep["before_fix"]
    clean_before = {row["label"]: row["clean"] for row in prior["clean_rows"]}
    assert before["Set M"]["weighted"] == clean_before["Set M"]["weighted"]
    assert before["start"]["weighted"] == clean_before[rep["start_label"]]["weighted"]


def test_gust_plays_are_counted_per_game():
    rep = _report("set-m-gust-search.json")
    for row in rep["path"]:
        assert 0 <= row["usage"]["boss"] < 1 and 0 <= row["usage"]["catcher"] < 1
    set_m = next(row for row in rep["fresh"] if row["label"] == "Set M")
    assert set_m["pooled"]["usage"]["boss"] > 0
