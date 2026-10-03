"""Spread, brick rate, and the tolerance tie-break for two lists."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.db import get_simulation
from app.engine.fate.uncertainty import (
    OUTPUTS,
    _chain_broken,
    compare_lists,
    load_uncertainty_preset,
    uncertainty,
)
from app.engine.models import rules_from_preset
from app.engine.strategies import STRATEGY_LIBRARY
from app.main import app
from app.seed_data import SET_G_NAMES, fallback_named


def _rules():
    return rules_from_preset("s60")


def _set_g():
    return [fallback_named(name) for name in SET_G_NAMES]


def _replace(cards, name, replacements):
    pending = list(replacements)
    out = []
    for card in cards:
        if pending and card.name == name:
            out.append(pending.pop(0))
            continue
        out.append(card)
    assert not pending, name
    return out


def _line_list(cards):
    """A 1-1 Pidgey line in place of two Psychic Energy. The list stays 60 cards."""
    return _replace(
        cards,
        "Psychic Energy",
        [fallback_named("Pidgey"), fallback_named("Pidgeotto")],
    )


def _block(sim_id, mean, variance, brick, chain, n=8):
    stat = {"mean": mean, "variance": variance, "n": n}
    return {
        "id": sim_id,
        "created_at": "2026-10-03T00:00:00+00:00",
        "uncertainty": {
            "sim_id": sim_id,
            "mean": mean,
            "variance": variance,
            "games": n,
            "brick_turn": 3,
            "energy_turn": 3,
            "lead_attack": None,
            "brick_rate": brick,
            "chain_break_rate": chain,
            "outputs": {name: dict(stat) for name in OUTPUTS},
        },
    }


def _preference(mean_a, var_a, brick_a, chain_a, mean_b, var_b, brick_b, chain_b, tol):
    if abs(mean_a - mean_b) < tol:
        score_a = (var_a, brick_a, chain_a)
        score_b = (var_b, brick_b, chain_b)
        if score_a < score_b:
            return "a"
        if score_b < score_a:
            return "b"
        return "tie"
    return "a" if mean_a > mean_b else "b"


def test_spare_middle_stage_is_not_a_broken_chain_when_the_later_stage_is_in_play():
    lines = [
        {"basic": "Clefairy", "evolution": "Clefable ex"},
        {"basic": "Clefable ex", "evolution": "Mega Clefable ex"},
        {"basic": "Ledyba", "evolution": "Ledian"},
    ]
    assert _chain_broken(lines, ["Clefable ex"], ["Mega Clefable ex"]) is False
    assert _chain_broken(lines, ["Clefable ex"], []) is True
    assert _chain_broken(lines, ["Ledian"], ["Ledyba"]) is False
    assert _chain_broken(lines, ["Ledian"], ["Ledian"]) is False
    assert _chain_broken(lines, ["Ledian"], [], ["Ledian"]) is False
    assert _chain_broken(lines, ["Ledian"], [], ["Ledyba"]) is True


def test_uncertainty_refuses_a_number_without_a_sim_id():
    try:
        uncertainty({"uncertainty": {"mean": 1.0, "variance": 0.0}})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "simulation id" in str(exc)


def test_unknown_output_is_rejected_before_a_run():
    try:
        compare_lists(_set_g(), _set_g(), _rules(), 4, 1, "nope", None)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown output" in str(exc)
    try:
        compare_lists(_set_g(), _set_g(), _rules(), 4, 1, "prizes_taken", {"nope": 1})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown output" in str(exc)


def test_within_tolerance_prefers_lower_variance_and_broken_chain(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _block("sim-a", 2.0, 0.2, 0.1, 0.1)
        return _block("sim-b", 2.2, 3.0, 0.4, 0.5)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = compare_lists(_set_g()[:4], _set_g()[:4], _rules(), 12, 7, "prizes_taken", {"prizes_taken": 0.5})
    assert report["preferred"] == "a"
    assert report["tolerance_used"] == 0.5
    assert "within tolerance" in report["reason"]
    assert "variance" in report["reason"].lower()
    assert "broken chain" in report["reason"].lower()
    assert report["a"]["sim_id"] == "sim-a"
    assert report["b"]["sim_id"] == "sim-b"
    assert "sim-a" in report["reason"] and "sim-b" in report["reason"]


def test_outside_tolerance_prefers_the_higher_mean(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _block("sim-a", 1.0, 0.1, 0.0, 0.0)
        return _block("sim-b", 3.0, 9.0, 0.8, 0.8)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = compare_lists(_set_g()[:4], _set_g()[:4], _rules(), 12, 7, "prizes_taken", {"prizes_taken": 0.5})
    assert report["preferred"] == "b"
    assert "outside tolerance" in report["reason"]
    assert "higher mean" in report["reason"]


def test_fewer_mulligans_wins_when_means_are_outside_tolerance(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _block("sim-a", 2.0, 0.1, 0.0, 0.0)
        return _block("sim-b", 0.2, 4.0, 0.5, 0.5)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = compare_lists(_set_g()[:4], _set_g()[:4], _rules(), 12, 7, "mulligans", {"mulligans": 0.25})
    assert report["higher_is_better"] is False
    assert report["preferred"] == "b"
    assert "lower mean" in report["reason"]


def test_games_cap_is_echoed(monkeypatch):
    seen = []

    def fake(*args, **kwargs):
        seen.append(kwargs["games"])
        return _block(f"sim-{len(seen)}", 1.0, 0.0, 0.0, 0.0)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = compare_lists(_set_g()[:4], _set_g()[:4], _rules(), 999999, 1, "win_rate", None)
    assert seen == [25000, 25000]
    assert report["games"] == 25000
    assert report["tolerance"]["win_rate"] == load_uncertainty_preset("s60")["tolerance"]["win_rate"]


def test_seeded_lists_carry_sim_ids_and_apply_the_rule():
    rules = _rules()
    left = _set_g()
    right = _line_list(left)
    assert len(left) == 60 and len(right) == 60
    assert sum(1 for card in right if card.name == "Pidgey") == 1
    assert sum(1 for card in right if card.name == "Pidgeotto") == 1
    report = compare_lists(left, right, rules, 4, 7, "prizes_taken", None)
    for side in ("a", "b"):
        block = report[side]
        assert block["sim_id"]
        assert block["variance"] is not None
        assert block["brick_rate"] is not None
        assert block["chain_break_rate"] is not None
        assert block["mean"] is not None
        record = report["runs"][side]
        spread = uncertainty(record)
        assert spread["sim_id"] == record["id"] == block["sim_id"]
        assert spread["variance"] == block["variance"]
    assert report["preferred"] == _preference(
        report["a"]["mean"],
        report["a"]["variance"],
        report["a"]["brick_rate"],
        report["a"]["chain_break_rate"],
        report["b"]["mean"],
        report["b"]["variance"],
        report["b"]["brick_rate"],
        report["b"]["chain_break_rate"],
        report["tolerance_used"],
    )
    assert "variance" in report["reason"].lower()
    assert "broken chain" in report["reason"].lower()
    assert report["a"]["sim_id"] in report["reason"]
    assert report["seed"] == 7
    assert report["games"] == 4
    assert STRATEGY_LIBRARY["balanced"].name == "balanced"


def test_observation_does_not_branch_on_a_strategy_name():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app/engine/fate/uncertainty.py").read_text()
    game = (root / "app/engine/game.py").read_text()
    assert "strat.name" not in source
    assert "app.engine.game" not in source
    assert "fate_first_attack" in game
    assert "top 6" not in game


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_compare_route_saves_both_sims_and_is_owner_scoped(tmp_path, monkeypatch):
    def fake(cards_a, cards_b, rules, games, seed, output, tolerance):
        if output not in OUTPUTS:
            raise ValueError(f"unknown output: {output}")
        assert games == 4
        return {
            "output": output,
            "tolerance": load_uncertainty_preset("s60")["tolerance"],
            "tolerance_used": 0.5,
            "games": games,
            "seed": 7,
            "preferred": "tie",
            "reason": "Means are within tolerance, and variance and broken chain match. Simulation sim-a and sim-b.",
            "a": {
                "sim_id": "sim-a",
                "mean": 1.0,
                "variance": 0.0,
                "n": 4,
                "brick_rate": 0.25,
                "chain_break_rate": 0.0,
                "lead_attack": None,
            },
            "b": {
                "sim_id": "sim-b",
                "mean": 1.0,
                "variance": 0.0,
                "n": 4,
                "brick_rate": 0.25,
                "chain_break_rate": 0.0,
                "lead_attack": None,
            },
            "runs": {
                "a": {"id": "sim-a", "created_at": "2026-10-03T00:00:00+00:00", "question": "fate compare"},
                "b": {"id": "sim-b", "created_at": "2026-10-03T00:00:00+00:00", "question": "fate compare"},
            },
        }

    monkeypatch.setattr("app.main.compare_lists", fake)
    monkeypatch.setattr("app.ai.tools.compare_lists", fake)
    with _client(tmp_path, monkeypatch) as client:
        assert client.post("/api/fate/compare", json={"deck_a_id": "seed-g", "deck_b_id": "seed-g"}).status_code == 401
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        response = client.post(
            "/api/fate/compare",
            json={"deck_a_id": "seed-g", "deck_b_id": "seed-g", "games": 4, "seed": 7},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["preferred"] == "tie"
        assert body["a"]["sim_id"] == "sim-a"
        assert "runs" not in body
        assert get_simulation("sim-a")["id"] == "sim-a"
        assert get_simulation("sim-b")["id"] == "sim-b"
        bad = client.post(
            "/api/fate/compare",
            json={"deck_a_id": "seed-g", "deck_b_id": "seed-g", "output": "nope"},
        )
        assert bad.status_code == 400

        client.post("/api/auth/register", json={"email": "kid-fate@example.com", "password": "play"})
        denied = client.post(
            "/api/fate/compare",
            json={"deck_a_id": "seed-g", "deck_b_id": "seed-g", "games": 4},
        )
        assert denied.status_code == 400
        me = client.get("/api/auth/me").json()
        token = use_viewer(me)
        try:
            assert run_tool("compare_fates", {"deck_a_id": "seed-g", "deck_b_id": "seed-g"})["error"]
        finally:
            reset_viewer(token)
