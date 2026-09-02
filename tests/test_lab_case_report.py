from app.config import ROOT
from app.lab.report import cells_from_attempts, human_title
from app.main import app
from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_cells_from_attempts_uses_nested_input_and_titles():
    cells = cells_from_attempts(
        [
            {
                "id": "carnival",
                "title": "tried carnival",
                "input": {
                    "deck_a_id": "seed-a",
                    "deck_b_id": "seed-b",
                    "strategy_b": "carnival",
                },
            },
            {"deck_a_id": "seed-a", "strategy_a": "thrifty", "patch_b": {"drop": ["Hop"]}},
        ]
    )
    assert cells[0]["id"] == "carnival"
    assert cells[0]["title"] == "tried carnival"
    assert cells[0]["strategy_b"] == "carnival"
    assert cells[1]["id"] == "run-2"
    assert "deck patch" in human_title(cells[1], 1)


def test_save_attempts_and_conclusion_round_trip(tmp_path, monkeypatch):
    lab_dir = ROOT / "data" / "lab"
    before = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}

    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-report@example.com", "password": "play"})
        cubone = {"name": "Cubone"}
        deck_a = client.post("/api/decks", json={"name": "Report A", "cards": [cubone]}).json()
        deck_b = client.post("/api/decks", json={"name": "Report B", "cards": [cubone]}).json()
        created = client.post(
            "/api/lab/experiments",
            json={
                "question": "does carnival beat shock?",
                "conclusion": "Not sure yet.",
                "games": 4,
                "seed": 20260831,
                "attempts": [
                    {
                        "id": "shock",
                        "title": "tried shock",
                        "input": {
                            "deck_a_id": deck_a["id"],
                            "deck_b_id": deck_b["id"],
                            "strategy_a": "thrifty",
                            "strategy_b": "shock",
                        },
                    },
                    {
                        "id": "carnival",
                        "title": "tried carnival",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": "carnival",
                    },
                ],
            },
        )
        assert created.status_code == 200, created.text
        exp = created.json()
        assert exp["cells"][0]["id"] == "shock"
        assert exp["cells"][1]["strategy_b"] == "carnival"
        assert [row["title"] for row in exp["attempts"]] == ["tried shock", "tried carnival"]
        assert exp["conclusion"] == "Not sure yet."

        ran = client.post(f"/api/lab/experiments/{exp['id']}/run", json={})
        assert ran.status_code == 200, ran.text
        report = ran.json()
        assert report["conclusion"] == "Not sure yet."
        assert [row["id"] for row in report["attempts"]] == ["shock", "carnival"]
        for attempt in report["attempts"]:
            assert attempt["win_rate_a"] is not None
            assert attempt["insights"]
        assert [cell["id"] for cell in report["results"]["cells"]] == ["shock", "carnival"]

        updated = client.put(
            f"/api/lab/experiments/{exp['id']}",
            json={"conclusion": "Carnival was the wrong read; try overlay next."},
        )
        assert updated.status_code == 200
        assert updated.json()["conclusion"] == "Carnival was the wrong read; try overlay next."
        assert len(updated.json()["attempts"]) == 2
        assert updated.json()["attempts"][0]["win_rate_a"] is not None

        same_runs = client.put(
            f"/api/lab/experiments/{exp['id']}",
            json={"attempts": updated.json()["attempts"]},
        )
        assert same_runs.status_code == 200
        assert same_runs.json()["results"] is not None
        assert same_runs.json()["attempts"][0]["win_rate_a"] is not None

        relabeled = client.put(
            f"/api/lab/experiments/{exp['id']}",
            json={
                "attempts": [
                    {
                        "id": "shock",
                        "title": "tried shock",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": "party",
                    },
                    {
                        "id": "carnival",
                        "title": "tried carnival",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": "carnival",
                    },
                ]
            },
        )
        assert relabeled.status_code == 200
        assert relabeled.json()["results"] is None
        assert all(row["win_rate_a"] is None for row in relabeled.json()["attempts"])
        assert relabeled.json()["conclusion"].startswith("Carnival")

        listed = client.get("/api/lab/experiments").json()
        assert listed[0]["attempts"][0]["title"] == "tried shock"
        assert listed[0]["conclusion"].startswith("Carnival")

    after = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    assert after == before


def test_attempts_win_over_cells_and_reject_bad_payload(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-shape@example.com", "password": "play"})
        created = client.post(
            "/api/lab/experiments",
            json={
                "question": "shape",
                "cells": [{"id": "old", "strategy_b": "shock"}],
                "attempts": [{"id": "new", "strategy_b": "carnival"}],
            },
        )
        assert created.status_code == 200
        assert created.json()["cells"][0]["id"] == "new"
        bad = client.post("/api/lab/experiments", json={"question": "bad", "attempts": "nope"})
        assert bad.status_code == 400
