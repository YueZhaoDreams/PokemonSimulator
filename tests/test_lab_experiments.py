from app.ai.tools import TOOL_SCHEMAS, reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, ROOT
from app.db import LAB_SCRIPT_MAX_CHARS, list_simulations
from app.main import app
from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_lab_experiments_are_owned_and_stay_out_of_git(tmp_path, monkeypatch):
    lab_dir = ROOT / "data" / "lab"
    before = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}

    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-a@example.com", "password": "play"})
        created = client.post(
            "/api/lab/experiments",
            json={
                "owner_id": "not-mine",
                "id": "client-chosen-id",
                "question": "carnival vs party",
                "cells": [{"id": "baseline", "strategy_b": "carnival"}],
                "queries": [{"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"}],
                "games": 200,
                "seed": 20260831,
                "script_text": "print('lab')\n",
            },
        )
        assert created.status_code == 200, created.text
        exp = created.json()
        kid_a = client.get("/api/auth/me").json()
        assert exp["owner_id"] == kid_a["id"]
        assert exp["id"] != "client-chosen-id"
        assert exp["question"] == "carnival vs party"
        assert exp["cells"][0]["id"] == "baseline"
        assert exp["script_text"] == "print('lab')\n"

        listed = client.get("/api/lab/experiments").json()
        assert len(listed) == 1
        assert listed[0]["id"] == exp["id"]
        assert "script_text" not in listed[0]
        assert listed[0]["script_present"] is True

        fetched = client.get(f"/api/lab/experiments/{exp['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["script_text"] == "print('lab')\n"
        assert run_tool("list_lab_experiments", {}) == {"error": "sign in required"}
        assert run_tool("get_lab_experiment", {"experiment_id": exp["id"]}) == {
            "error": "experiment not found"
        }

        locked = client.put(
            f"/api/lab/experiments/{exp['id']}",
            json={
                "results": {"cells": [{"id": "baseline", "win_rate_a": 0.62}]},
                "locked_cell_id": "baseline",
                "lock_reason": "party hit more",
            },
        )
        assert locked.status_code == 200
        token = use_viewer(kid_a)
        try:
            updated = run_tool(
                "save_lab_experiment",
                {"experiment_id": exp["id"], "question": "carnival vs party (kept)"},
            )
            assert updated["question"] == "carnival vs party (kept)"
            assert updated["results"]["cells"][0]["win_rate_a"] == 0.62
            assert updated["locked_cell_id"] == "baseline"
            assert updated["lock_reason"] == "party hit more"
            assert updated["script_text"] == "print('lab')\n"
        finally:
            reset_viewer(token)

        client.post("/api/auth/logout")
        kid_b = client.post("/api/auth/register", json={"email": "kid-b@example.com", "password": "play"}).json()
        hidden = client.get(f"/api/lab/experiments/{exp['id']}")
        assert hidden.status_code == 404
        assert client.get("/api/lab/experiments").json() == []
        steal = client.post(
            "/api/lab/experiments",
            json={"id": exp["id"], "question": "stolen", "owner_id": exp["owner_id"]},
        )
        assert steal.status_code == 200
        assert steal.json()["id"] != exp["id"]
        assert steal.json()["owner_id"] == kid_b["id"]
        token = use_viewer(kid_b)
        try:
            assert run_tool("get_lab_experiment", {"experiment_id": exp["id"]}) == {
                "error": "experiment not found"
            }
            listed_tools = run_tool("list_lab_experiments", {})
            assert all(item["id"] != exp["id"] for item in listed_tools)
        finally:
            reset_viewer(token)

        client.post("/api/auth/logout")
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        admin_get = client.get(f"/api/lab/experiments/{exp['id']}")
        assert admin_get.status_code == 200
        assert admin_get.json()["question"] == "carnival vs party (kept)"
        assert admin_get.json()["owner_id"] == kid_a["id"]

        sim = client.post(
            "/api/simulate",
            json={"deck_a_id": "seed-a", "deck_b_id": "seed-b", "games": 4, "question": "still works"},
        )
        assert sim.status_code == 200
        assert sim.json()["id"]
        assert list_simulations()

    after = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    assert after == before


def test_lab_script_text_rejects_blobs(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-c@example.com", "password": "play"})
        too_big = client.post(
            "/api/lab/experiments",
            json={"question": "big", "script_text": "x" * (LAB_SCRIPT_MAX_CHARS + 1)},
        )
        assert too_big.status_code == 400
        assert "at most" in too_big.json()["detail"]

        nul = client.post(
            "/api/lab/experiments",
            json={"question": "nul", "script_text": "print(1)\x00os.system('x')"},
        )
        assert nul.status_code == 400
        assert "must be text" in nul.json()["detail"]


def test_save_lab_experiment_tool_schema_includes_results_and_lock():
    schema = next(item for item in TOOL_SCHEMAS if item["name"] == "save_lab_experiment")
    assert {"results", "locked_cell_id", "lock_reason"} <= set(schema["parameters"]["properties"])
