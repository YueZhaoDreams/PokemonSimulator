"""The best-search lab report is a legal one-swap path from the Budew list, and its fresh-seed tables line up."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.seed_data import build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"
ADDS = {"Sky Field", "Budew", "Igglybuff", "Mime Jr.", "Cleffa"}


def _report(name: str) -> dict:
    return json.loads((LAB / name).read_text())["report"]


def test_best_search_path_is_legal_one_swap_steps_from_the_budew_list():
    rep = _report("set-m-best-search.json")
    policy = _report("set-m-budew-policy.json")
    assert rep["done"] is True
    assert rep["list_set_m"] == policy["list_start"]
    assert rep["list_start"] == policy["array"][-1]["list"]
    assert rep["weights"] == policy["weights"]
    path = rep["path"]
    assert path[0]["label"] == "Budew 4 (start)" and path[0]["list"] == rep["list_start"]
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


def test_best_search_fresh_and_clean_tables_cover_the_path():
    rep = _report("set-m-best-search.json")
    path = rep["path"]
    labels = ["Set M", "Sky Field"] + [row["label"] for row in path]
    assert [row["label"] for row in rep["fresh"]] == labels
    for row in rep["fresh"]:
        low = min(row["seed1"]["weighted"], row["seed2"]["weighted"])
        high = max(row["seed1"]["weighted"], row["seed2"]["weighted"])
        assert low - 1e-9 <= row["pooled"]["weighted"] <= high + 1e-9
        assert all(
            cell["games"] == rep["holdout_games"] + rep["holdout2_games"] for cell in row["pooled"]["cells"].values()
        )
    clean = {row["label"]: row for row in rep["clean_rows"]}
    assert {"Set M", "Budew 4 (start)", path[-1]["label"], rep["best_fresh_label"]} == set(clean)
    fresh = {row["label"]: row for row in rep["fresh"]}
    assert rep["best_fresh_label"] == max(
        (row["label"] for row in path), key=lambda label: fresh[label]["pooled"]["weighted"]
    )
    assert all(
        cell["games"] == rep["clean_games"] for row in clean.values() for cell in row["clean"]["cells"].values()
    )
    used = {rep["seed"], rep["holdout_seed"], rep["holdout2_seed"]}
    assert rep["clean_seed"] not in used and len(used) == 3
    assert abs(sum(rep["weights"].values()) - 1.0) < 1e-9
