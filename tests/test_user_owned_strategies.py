from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ROOT
from app.engine.strategies import STRATEGY_LIBRARY
from app.main import app
from fastapi.testclient import TestClient

OVERLAY = {"name": "lock-mill", "prefer_damage": 0.17, "protect": ["Litwick"]}


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_lock_saves_personal_strategy_hidden_from_second_trainer(tmp_path, monkeypatch):
    lab_dir = ROOT / "data" / "lab"
    app_dir = ROOT / "app"
    strategies_py = ROOT / "app" / "engine" / "strategies.py"
    before_lab = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    before_app = {path.name: path.stat().st_mtime_ns for path in app_dir.glob("*")}
    before_lib_mtime = strategies_py.stat().st_mtime_ns
    library_names = list(STRATEGY_LIBRARY)

    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-lock@example.com", "password": "play"})
        deck_a = client.post("/api/decks", json={"name": "Lock A", "cards": [{"name": "Cubone"}]}).json()
        deck_b = client.post("/api/decks", json={"name": "Lock B", "cards": [{"name": "Cubone"}]}).json()
        created = client.post(
            "/api/lab/experiments",
            json={
                "question": "lock mill overlay",
                "games": 4,
                "seed": 20260831,
                "cells": [
                    {
                        "id": "mill-run",
                        "title": "tried mill overlay",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": OVERLAY,
                    }
                ],
            },
        )
        assert created.status_code == 200, created.text
        exp_id = created.json()["id"]
        ran = client.post(f"/api/lab/experiments/{exp_id}/run", json={})
        assert ran.status_code == 200, ran.text

        locked = client.post(
            f"/api/lab/experiments/{exp_id}/lock",
            json={"cell_id": "mill-run", "reason": "keep mill"},
        )
        assert locked.status_code == 200, locked.text
        strategy = locked.json()["strategy"]
        sid = strategy["id"]
        assert sid.startswith("user:")
        assert strategy["spec"]["prefer_damage"] == 0.17
        assert locked.json()["experiment"]["locked_cell_id"] == "mill-run"

        listed = client.get("/api/strategies").json()
        library_ids = [row["id"] for row in listed if row.get("source") == "library"]
        assert "thrifty" in library_ids
        assert "shock" in library_ids
        mine = [row for row in listed if row.get("id") == sid]
        assert len(mine) == 1
        assert mine[0]["name"] == "tried mill overlay"

        sim = client.post(
            "/api/simulate",
            json={
                "deck_a_id": deck_a["id"],
                "deck_b_id": deck_b["id"],
                "games": 4,
                "strategy_a": "thrifty",
                "strategy_b": sid,
            },
        )
        assert sim.status_code == 200, sim.text
        assert sim.json()["strategies"]["b"]["prefer_damage"] == 0.17
        assert sim.json()["strategies"]["b"]["protect"] == ["Litwick"]

        token = use_viewer(client.get("/api/auth/me").json())
        try:
            tool_list = run_tool("list_strategies", {})
            assert any(row.get("id") == sid for row in tool_list)
            chat_sim = run_tool(
                "simulate_match",
                {
                    "deck_a_id": deck_a["id"],
                    "deck_b_id": deck_b["id"],
                    "games": 4,
                    "strategy_b": sid,
                },
            )
            assert chat_sim.get("strategies", {}).get("b", {}).get("prefer_damage") == 0.17
            again = run_tool("lock_lab_cell", {"experiment_id": exp_id, "cell_id": "mill-run"})
            assert again["strategy"]["id"] == sid
            listed_again = [row for row in run_tool("list_strategies", {}) if row.get("source") == "user"]
            assert len(listed_again) == 1
        finally:
            reset_viewer(token)

        client.post("/api/auth/logout")
        client.post("/api/auth/register", json={"email": "kid-other-lock@example.com", "password": "play"})
        other_list = client.get("/api/strategies").json()
        assert not any(row.get("id") == sid for row in other_list)
        hidden_lock = client.post(f"/api/lab/experiments/{exp_id}/lock", json={"cell_id": "mill-run"})
        assert hidden_lock.status_code == 404
        denied = client.post(
            "/api/simulate",
            json={
                "deck_a_id": deck_a["id"],
                "deck_b_id": deck_b["id"],
                "games": 4,
                "strategy_b": sid,
            },
        )
        assert denied.status_code in (400, 404)
        other_deck_a = client.post("/api/decks", json={"name": "Other A", "cards": [{"name": "Cubone"}]}).json()
        other_deck_b = client.post("/api/decks", json={"name": "Other B", "cards": [{"name": "Cubone"}]}).json()
        denied_own_decks = client.post(
            "/api/simulate",
            json={
                "deck_a_id": other_deck_a["id"],
                "deck_b_id": other_deck_b["id"],
                "games": 4,
                "strategy_b": sid,
            },
        )
        assert denied_own_decks.status_code == 400
        bad_spec = client.post("/api/strategies", json={"name": "nope", "spec": "shock"})
        assert bad_spec.status_code == 400

        token_b = use_viewer(client.get("/api/auth/me").json())
        try:
            hidden_tool = run_tool("list_strategies", {})
            assert not any(row.get("id") == sid for row in hidden_tool)
            assert run_tool("simulate_match", {"deck_a_id": other_deck_a["id"], "deck_b_id": other_deck_b["id"], "strategy_b": sid, "games": 4}).get("error")
        finally:
            reset_viewer(token_b)

    assert list(STRATEGY_LIBRARY) == library_names
    assert strategies_py.stat().st_mtime_ns == before_lib_mtime
    after_lab = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    after_app = {path.name: path.stat().st_mtime_ns for path in app_dir.glob("*")}
    assert after_lab == before_lab
    assert after_app == before_app


def test_fight_dropdown_includes_saved_strategy_id():
    text = (ROOT / "app" / "static" / "app.js").read_text()
    assert 's.id || s.name' in text
    assert "Lock this run" in text
    assert "/lock" in text
    assert "source === \"user\"" in text
