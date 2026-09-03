from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ROOT
from app.engine.game import Game
from app.lab.sandbox import classify_lab_script
from app.main import app
from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def _bakeoff(deck_a_id: str, deck_b_id: str) -> str:
    return f"""
a = decks[{deck_a_id!r}]
b = decks[{deck_b_id!r}]
rows = []
for name in ["shock", "carnival"]:
    rec = run_simulation(
        a["cards"],
        b["cards"],
        rules,
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict(name),
        games=games,
        seed=seed,
        queries=queries,
    )
    rows.append({{
        "id": name,
        "win_rate_a": rec["results"]["win_rate_a"],
        "queries": rec["results"]["queries"],
        "insights": rec["learning"]["insights"],
    }})
print("debug bakeoff")
report({{"seed": seed, "games": games, "cells": rows}})
"""


HOSTILE = {
    "import_os": "import os\nreport({'cells': []})\n",
    "import_subprocess": "import subprocess\nreport({'cells': []})\n",
    "import_socket": "import socket\nreport({'cells': []})\n",
    "import_urllib": "import urllib.request\nreport({'cells': []})\n",
    "read_env": "open('.env').read()\nreport({'cells': []})\n",
    "read_game": "open('app/engine/game.py').read()\nreport({'cells': []})\n",
    "write_lab": "open('data/lab/pwn.py', 'w').write('x')\nreport({'cells': []})\n",
    "binary": "x = b'\\x00\\xff'\nreport({'cells': []})\n",
    "game_import": "import app.engine.game as game_mod\ngame_mod.Game = None\nreport({'cells': []})\n",
}


def test_classify_rejects_hostile_and_accepts_bakeoff():
    ok = classify_lab_script(_bakeoff("seed-a", "seed-b"))
    assert ok.executable
    assert not classify_lab_script("run_simulation = 0\nreport({'cells': []})\n").executable
    assert not classify_lab_script("(run_simulation := 0)\nrun_simulation()\nreport({'cells': []})\n").executable
    assert not classify_lab_script(
        "def run_simulation(*a, **k):\n    return {'results': {}}\nrun_simulation()\nreport({'cells': []})\n"
    ).executable
    for name, src in HOSTILE.items():
        verdict = classify_lab_script(src)
        assert not verdict.executable, name


def test_lab_script_runs_in_db_and_hostile_stays_non_executable(tmp_path, monkeypatch):
    lab_dir = ROOT / "data" / "lab"
    app_dir = ROOT / "app"
    before_lab = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")}
    before_app = {path.name: path.stat().st_mtime_ns for path in app_dir.glob("*")}
    game_before = Game.__dict__.get("play_game", None)

    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-py@example.com", "password": "play"})
        deck_a = client.post("/api/decks", json={"name": "Py A", "cards": [{"name": "Cubone"}, {"name": "Grass Energy"}]}).json()
        deck_b = client.post("/api/decks", json={"name": "Py B", "cards": [{"name": "Cubone"}, {"name": "Grass Energy"}]}).json()
        script = _bakeoff(deck_a["id"], deck_b["id"])
        created = client.post(
            "/api/lab/experiments",
            json={
                "question": "shock vs carnival bakeoff",
                "games": 6,
                "seed": 20260831,
                "queries": [{"type": "event_prefix", "prefix": "saw_play:Cubone", "key": "cubone_play"}],
                "cells": [{"id": "placeholder", "strategy_b": "shock"}],
                "script_text": script,
            },
        )
        assert created.status_code == 200, created.text
        exp = created.json()
        assert exp["script_executable"] is True
        assert exp["script_text"] == script

        ran = client.post(f"/api/lab/experiments/{exp['id']}/run-script", json={})
        assert ran.status_code == 200, ran.text
        cells = ran.json()["results"]["cells"]
        assert [cell["id"] for cell in cells] == ["shock", "carnival"]
        for cell in cells:
            assert "win_rate_a" in cell
            assert "cubone_play" in cell["queries"]
            assert cell["insights"]
        attempts = ran.json()["attempts"]
        assert [row["id"] for row in attempts] == ["shock", "carnival"]
        assert all(row["win_rate_a"] is not None for row in attempts)

        kid = client.get("/api/auth/me").json()
        token = use_viewer(kid)
        try:
            tool = run_tool("run_lab_script", {"experiment_id": exp["id"]})
            assert "error" not in tool
            assert tool["results"]["cells"]
        finally:
            reset_viewer(token)

        for name, src in HOSTILE.items():
            saved = client.post("/api/lab/experiments", json={"question": name, "script_text": src})
            assert saved.status_code == 200, saved.text
            body = saved.json()
            assert body["script_text"] == src
            assert body["script_executable"] is False
            blocked = client.post(f"/api/lab/experiments/{body['id']}/run-script", json={})
            assert blocked.status_code == 400, name
            assert body["id"]

        patched = f"""
a = decks[{deck_a["id"]!r}]
b = decks[{deck_b["id"]!r}]
rec = run_simulation(a["cards"], b["cards"], rules, StrategySpec.from_dict("shock"), StrategySpec.from_dict("shock"), games=games, seed=seed, queries=queries)
def boom(data):
    raise RuntimeError("mutated Card")
Card.from_dict = boom
report({{"cells": [{{"id": "patched", "win_rate_a": rec["results"]["win_rate_a"]}}]}})
"""
        mutate = client.post("/api/lab/experiments", json={"question": "patch card", "script_text": patched})
        assert mutate.json()["script_executable"] is True
        mutate_run = client.post(f"/api/lab/experiments/{mutate.json()['id']}/run-script", json={})
        assert mutate_run.status_code == 200, mutate_run.text
        sim = client.post(
            "/api/simulate",
            json={"deck_a_id": deck_a["id"], "deck_b_id": deck_b["id"], "games": 4},
        )
        assert sim.status_code == 200, sim.text
        assert sim.json()["results"]["win_rate_a"] is not None

        client.post("/api/auth/logout")
        client.post("/api/auth/register", json={"email": "kid-other-py@example.com", "password": "play"})
        hidden = client.post(f"/api/lab/experiments/{exp['id']}/run-script", json={})
        assert hidden.status_code == 404
        hidden_get = client.get(f"/api/lab/experiments/{exp['id']}")
        assert hidden_get.status_code == 404

    after_lab = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")}
    after_app = {path.name: path.stat().st_mtime_ns for path in app_dir.glob("*")}
    assert after_lab == before_lab
    assert after_app == before_app
    assert Game.__dict__.get("play_game", None) == game_before
