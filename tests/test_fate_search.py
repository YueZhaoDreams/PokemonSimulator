"""Bounded one-swap search: prune with the score, confirm a few with a simulation."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.db import get_simulation
from app.engine.fate.search import LABEL, apply_budget, load_budget, search
from app.engine.fate.uncertainty import uncertainty
from app.engine.models import Attack, Card, rules_from_preset
from app.main import app


def _rules():
    return rules_from_preset("s60")


def _mon(name, damage, cost=("Colorless", "Colorless"), text="", stage="Basic", evolves_from=None):
    return Card(
        catalog_id=name.lower(),
        name=name,
        category="Pokemon",
        stage=stage,
        types=["Colorless"],
        hp=100,
        evolves_from=evolves_from,
        attacks=[Attack(name="Hit", cost=list(cost), damage=damage, text=text)],
    )


def _energy():
    return Card(
        catalog_id="psychic-energy",
        name="Psychic Energy",
        category="Energy",
        stage="Basic",
        types=["Psychic"],
        energy_type="Psychic",
    )


def _seed():
    lonely = _mon("Lonely", 50, stage="Stage1", evolves_from="Missing")
    buddy = _mon("Buddy", 40, text="Search your deck for a Strong.")
    return [lonely, buddy] + [_energy() for _ in range(58)]


def _strong():
    return _mon("Strong", 100)


def _budget(**overrides):
    base = {"max_candidates": 24, "top_k": 1, "games_per_candidate": 2, "depth": 1}
    base.update(overrides)
    return base


def _record(sim_id, win, variance, brick, chain):
    outputs = {
        name: {"mean": win, "variance": variance, "n": 4}
        for name in (
            "prizes_taken",
            "mulligans",
            "energy_by_turn_3",
            "first_lead_attack_turn",
            "win_rate",
        )
    }
    return {
        "id": sim_id,
        "created_at": "2026-10-03T00:00:00+00:00",
        "uncertainty": {
            "sim_id": sim_id,
            "games": 4,
            "brick_rate": brick,
            "chain_break_rate": chain,
            "lead_attack": None,
            "outputs": outputs,
        },
    }


def test_linked_substitute_for_the_isolated_attacker_ranks_first(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        return _record(f"sim-{calls['n']}", 0.4, 0.2, 0.2, 0.2)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = search(_seed(), [_strong()], _rules(), None, _budget(top_k=3), seed_int=7)
    assert len(_seed()) == 60
    top = report["survivors"][0]
    assert top["cut"] == "Lonely"
    assert top["add"] == "Strong"
    assert "isolated" in top["reason"]
    assert "linked" in top["reason"]
    assert "damage per energy" in top["reason"]
    assert top["delta_s"] > report["survivors"][1]["delta_s"]
    assert report["deck_size"] == 60
    assert report["label"] == LABEL
    assert "best deck" in report["label"]
    assert report["relative"] is True
    assert report["depth"] == 1


def test_locking_the_attacker_removes_that_cut(monkeypatch):
    monkeypatch.setattr("app.engine.montecarlo.run_simulation", lambda *_a, **_k: _record("sim", 0.4, 0.1, 0.1, 0.1))
    report = search(_seed(), [_strong()], _rules(), None, _budget(top_k=3), locks=["Lonely"], seed_int=7)
    cuts = [row["cut"] for row in report["survivors"]] + [row["cut"] for row in report["pruned"]]
    assert "Lonely" not in cuts
    assert cuts


def test_pruned_rows_keep_delta_s_and_skip_the_simulation(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        return _record(f"sim-{calls['n']}", 0.4, 0.1, 0.1, 0.1)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = search(_seed(), [_strong()], _rules(), None, _budget(top_k=1), seed_int=7)
    assert calls["n"] == 1
    assert len(report["survivors"]) == 1
    assert report["survivors"][0]["sim_id"] == "sim-1"
    assert "win_rate" in report["survivors"][0]
    assert "delta_s" in report["survivors"][0]
    assert report["pruned"]
    for row in report["pruned"]:
        assert set(row) == {"cut", "add", "delta_s"}
    assert report["budget"]["games_run"] == 2
    assert report["budget"]["candidates_scored"] <= report["budget"]["max_candidates"]
    assert report["budget"]["games_run"] <= report["budget"]["budget_games"]


def test_a_fifth_copy_is_not_a_neighbor(monkeypatch):
    monkeypatch.setattr("app.engine.montecarlo.run_simulation", lambda *_a, **_k: _record("sim", 0.2, 0.1, 0.1, 0.1))
    buddy = _mon("Buddy", 40, text="Search your deck for a Strong.")
    seed = [buddy for _ in range(4)] + [_energy() for _ in range(56)]
    report = search(seed, [buddy, _strong()], _rules(), None, _budget(top_k=3, max_candidates=24), seed_int=1)
    rows = report["survivors"] + report["pruned"]
    assert rows
    assert all(row["add"] != "Buddy" for row in rows)
    assert report["deck_size"] == 60


def test_budget_stops_before_the_rest_of_a_large_pool(monkeypatch):
    monkeypatch.setattr("app.engine.montecarlo.run_simulation", lambda *_a, **_k: _record("sim", 0.2, 0.1, 0.1, 0.1))
    pool = [_strong()] + [_mon(f"Extra{i}", 10) for i in range(40)]
    report = search(_seed(), pool, _rules(), None, _budget(max_candidates=2, top_k=1), seed_int=1)
    assert report["budget"]["candidates_scored"] == 2
    assert report["budget"]["games_run"] == 2


def test_near_tie_prefers_the_steadier_list(monkeypatch):
    calls = {"n": 0}

    def fake(*_args, **_kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            return _record("wide", 0.55, 4.0, 0.4, 0.4)
        return _record("steady", 0.52, 0.1, 0.1, 0.1)

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", fake)
    report = search(_seed(), [_strong()], _rules(), None, _budget(top_k=2), seed_int=3)
    assert abs(report["survivors"][0]["win_rate"] - report["survivors"][1]["win_rate"]) < report["tolerance_used"]
    assert report["survivors"][0]["sim_id"] == "steady"
    assert report["survivors"][0]["variance"] < report["survivors"][1]["variance"]


def test_a_real_simulation_carries_its_id():
    report = search(_seed(), [_strong()], _rules(), None, _budget(top_k=1), seed_int=11)
    top = report["survivors"][0]
    assert top["cut"] == "Lonely"
    assert top["sim_id"]
    assert top["win_rate"] is not None
    assert "delta_s" in top
    block = uncertainty(report["runs"][0])
    assert block["sim_id"] == top["sim_id"] == report["runs"][0]["id"]


def test_budget_cannot_grow_past_the_file():
    base = load_budget()
    try:
        apply_budget(base, {"max_candidates": base["max_candidates"] + 1})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "above" in str(exc)
    try:
        apply_budget(base, {"depth": 2})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "depth" in str(exc)
    try:
        search(_seed(), [_strong()], _rules(), None, {"nope": 1})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown budget" in str(exc)


def test_search_does_not_branch_on_a_strategy_name():
    source = Path("app/engine/fate/search.py").read_text()
    assert "strat.name" not in source
    assert "SET_G" not in source
    assert "FALLBACK_BY_NAME" not in source


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_search_route_is_owner_scoped_and_saves_the_sim(tmp_path, monkeypatch):
    def fake(seed, pool, rules, weights, budget, locks, opponent, seed_int):
        assert budget["max_candidates"] == 2
        return {
            "label": LABEL,
            "relative": True,
            "depth": 1,
            "budget": {"max_candidates": 2, "top_k": 1, "games_per_candidate": 2, "depth": 1, "candidates_scored": 1, "games_run": 2, "budget_games": 4},
            "tolerance_used": 0.05,
            "seed": 7,
            "weights": {},
            "survivors": [
                {
                    "rank": 1,
                    "cut": "Lonely",
                    "add": "Strong",
                    "delta_s": 1.5,
                    "reason": "Lonely is isolated",
                    "win_rate": 0.5,
                    "variance": 0.1,
                    "brick_rate": 0.0,
                    "chain_break_rate": 0.0,
                    "sim_id": "sim-search",
                    "games": 2,
                }
            ],
            "pruned": [{"cut": "Buddy", "add": "Strong", "delta_s": 0.2}],
            "runs": [{"id": "sim-search", "created_at": "2026-10-03T00:00:00+00:00", "question": "fate search"}],
        }

    monkeypatch.setattr("app.main.search_fate", fake)
    monkeypatch.setattr("app.ai.tools.search_fate", fake)
    with _client(tmp_path, monkeypatch) as client:
        assert client.post("/api/decks/seed-g/fate/search", json={}).status_code == 401
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        response = client.post(
            "/api/decks/seed-g/fate/search",
            json={"pool": ["Mega Clefable ex"], "budget": {"max_candidates": 2, "top_k": 1, "games_per_candidate": 2, "depth": 1}, "seed": 7},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["label"] == LABEL
        assert body["survivors"][0]["sim_id"] == "sim-search"
        assert "win_rate" not in body["pruned"][0]
        assert get_simulation("sim-search")["id"] == "sim-search"
        assert "runs" not in body

        client.post("/api/auth/register", json={"email": "kid-search@example.com", "password": "play"})
        assert client.post("/api/decks/seed-g/fate/search", json={}).status_code == 404
        me = client.get("/api/auth/me").json()
        token = use_viewer(me)
        try:
            assert run_tool("search_fate", {"deck_id": "seed-g"}).get("error")
        finally:
            reset_viewer(token)
