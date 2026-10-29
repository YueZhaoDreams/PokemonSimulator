"""The one-card greedy step used for Mill's Sleepy Voice search."""

import pytest

from app.engine.greedy_swap import choose_swap, confirm_cuts


def _row(cut, weighted, se=0.01, worst=0.05):
    return {"cut": cut, "weighted": weighted, "se": se, "worst": worst}


def test_confirm_keeps_cuts_close_to_the_best_screen_score():
    rows = [
        _row(None, 0.50, se=0.01),
        _row("Rescue Carrier", 0.56, se=0.01),
        _row("Crushing Hammer", 0.55, se=0.01),
        _row("Water Energy", 0.40, se=0.01),
    ]
    assert confirm_cuts(rows) == ["baseline", "Rescue Carrier", "Crushing Hammer"]


def test_best_cut_is_confirmed_when_it_sits_below_the_baseline_band():
    rows = [
        _row(None, 0.50, se=0.005),
        _row("Wally", 0.42, se=0.005),
        _row("Hop", 0.10, se=0.005),
    ]
    assert confirm_cuts(rows) == ["baseline", "Wally"]


def test_choose_swap_keeps_the_higher_weighted_rate():
    baseline = _row(None, 0.50, worst=0.07)
    swaps = [
        _row("Rescue Carrier", 0.54, worst=0.08),
        _row("Crushing Hammer", 0.55, worst=0.06),
    ]
    best, kept = choose_swap(baseline, swaps)
    assert kept
    assert best["cut"] == "Crushing Hammer"


def test_a_lower_confirm_stops_the_greedy():
    baseline = _row(None, 0.50, worst=0.07)
    best, kept = choose_swap(baseline, [_row("Wally", 0.49, worst=0.20)])
    assert best["cut"] == "Wally"
    assert not kept


def test_an_exact_tie_takes_the_alphabetically_earlier_cut():
    baseline = _row(None, 0.50)
    best, kept = choose_swap(baseline, [_row("Wally", 0.55), _row("Boss's Orders", 0.55)])
    assert kept
    assert best["cut"] == "Boss's Orders"


def test_two_steps_stop_when_the_next_copy_does_not_raise_the_score():
    first, kept = choose_swap(_row(None, 0.417), [_row("Crushing Hammer", 0.438)])
    assert kept and first["cut"] == "Crushing Hammer"
    _second, kept_again = choose_swap(_row(None, 0.438), [_row("Level Ball", 0.431)])
    assert not kept_again


def test_confirm_limit_counts_the_baseline():
    rows = [_row(None, 0.50)] + [_row(f"Card {index}", 0.60 - index * 0.001) for index in range(12)]
    labels = confirm_cuts(rows, limit=4)
    assert labels[0] == "baseline"
    assert len(labels) == 4


def test_confirm_rejects_an_empty_limit():
    with pytest.raises(ValueError):
        confirm_cuts([], limit=0)
