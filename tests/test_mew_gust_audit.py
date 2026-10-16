"""The gust audit report compares the same Set M games before and after the gust fix."""

from __future__ import annotations

import json
from pathlib import Path

LAB = Path(__file__).resolve().parents[1] / "data" / "lab"
CARDS = ("Boss's Orders", "Counter Catcher")


def _audit() -> dict:
    return json.loads((LAB / "set-m-gust-audit.json").read_text())


def test_audit_runs_the_same_games_before_and_after():
    audit = _audit()
    before, after = audit["before"], audit["after"]
    assert (before["label"], after["label"]) == ("before", "after")
    assert before["seed"] == after["seed"]
    assert before["games_per_foe"] == after["games_per_foe"]
    assert list(before["foes"]) == list(after["foes"]) == ["t60", "hedrick", "c60", "d60", "thorns", "starmie"]


def test_after_the_fix_every_gust_play_takes_a_bigger_knock_out():
    audit = _audit()
    for card in CARDS:
        before, after = audit["before"]["all"][card], audit["after"]["all"][card]
        assert before["plays"] > after["plays"] > 0
        assert after["pull_worse_than_active"] == 0
        assert after["no_prize_that_turn"] < 0.05 < before["no_prize_that_turn"]
        assert after["target_knocked_out"] > before["target_knocked_out"]
        assert after["prizes_that_turn"] > before["prizes_that_turn"]


def test_audit_markdown_names_the_measures_in_the_json():
    text = (LAB / "set-m-gust-audit.md").read_text()
    audit = _audit()
    boss = audit["after"]["all"]["Boss's Orders"]
    assert f"{boss['per_game']:.3f}" in text
    assert "Plays with no prize that turn" in text
