from app.catalog import energy_card, fallback_card
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, ROOT
from app.engine.effects import is_basic_energy
from app.engine.models import Card
from app.engine.montecarlo import query_key
from app.lab.patches import apply_deck_patch
from app.main import app
from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_apply_deck_patch_swaps_basic_energy_and_drops_names():
    cards = [
        energy_card("Grass").to_dict(),
        energy_card("Grass").to_dict(),
        fallback_card("Cubone").to_dict(),
        fallback_card("Hop").to_dict(),
    ]
    out = apply_deck_patch(
        cards,
        {
            "swap_energy": {"from": "Grass Energy", "to": "Lightning Energy", "count": 1},
            "drop": ["Hop"],
            "add": ["Boss's Orders"],
        },
    )
    names = [c["name"] for c in out]
    assert names.count("Lightning Energy") == 1
    assert names.count("Grass Energy") == 1
    assert "Hop" not in names
    assert "Boss's Orders" in names
    assert is_basic_energy(Card.from_dict(out[0]), pokemon_as_energy=False)


def test_lab_query_key_matches_montecarlo_default():
    assert query_key({"type": "opening_hand_contains", "side": "a", "card": "Cubone"}) == "opening_hand_contains:a:Cubone"
    assert query_key({"type": "event_prefix", "prefix": "saw_play:Cubone", "key": "cubone_play"}) == "cubone_play"
    assert query_key({"type": "event_prefix", "prefix": "saw_play:Cubone"}) == "event_prefix:saw_play:Cubone"


def test_two_cell_lab_run_uses_custom_queries_and_stays_out_of_git(tmp_path, monkeypatch):
    lab_dir = ROOT / "data" / "lab"
    before = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    grass = energy_card("Grass").to_dict()
    cubone = {"name": "Cubone"}

    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid-run@example.com", "password": "play"})
        deck_a = client.post("/api/decks", json={"name": "Lab A", "cards": [cubone, grass]}).json()
        deck_b = client.post("/api/decks", json={"name": "Lab B", "cards": [cubone, grass]}).json()
        created = client.post(
            "/api/lab/experiments",
            json={
                "question": "carnival vs lightning energy",
                "games": 6,
                "seed": 20260831,
                "queries": [{"type": "event_prefix", "prefix": "saw_play:Cubone", "key": "cubone_play"}],
                "cells": [
                    {
                        "id": "baseline",
                        "title": "shock",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": "shock",
                    },
                    {
                        "id": "lightning",
                        "title": "lightning B",
                        "deck_a_id": deck_a["id"],
                        "deck_b_id": deck_b["id"],
                        "strategy_a": "thrifty",
                        "strategy_b": "shock",
                        "patch_b": {"swap_energy": {"from": "Grass Energy", "to": "Lightning Energy"}},
                    },
                ],
            },
        )
        assert created.status_code == 200, created.text
        exp_id = created.json()["id"]
        ran = client.post(f"/api/lab/experiments/{exp_id}/run", json={})
        assert ran.status_code == 200, ran.text
        blob = ran.json()["results"]
        assert blob["seed"] == 20260831
        assert blob["games"] == 6
        assert [cell["id"] for cell in blob["cells"]] == ["baseline", "lightning"]
        for cell in blob["cells"]:
            assert "win_rate_a" in cell
            assert "cubone_play" in cell["queries"]
            assert "dondozo_opening_a" not in cell["queries"]

        client.post("/api/auth/logout")
        client.post("/api/auth/register", json={"email": "kid-other@example.com", "password": "play"})
        hidden = client.post(f"/api/lab/experiments/{exp_id}/run", json={})
        assert hidden.status_code == 404

        client.post("/api/auth/logout")
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        sim = client.post(
            "/api/simulate",
            json={
                "deck_a_id": "seed-a",
                "deck_b_id": "seed-b",
                "games": 4,
                "queries": [{"type": "event_prefix", "prefix": "saw_play:Cubone", "key": "only_cubone"}],
            },
        )
        assert sim.status_code == 200
        keys = set(sim.json()["results"]["queries"])
        assert "dondozo_opening_a" not in keys
        assert "dondozo_saw_play" not in keys

    after = {path.name: path.stat().st_mtime_ns for path in lab_dir.glob("*")} if lab_dir.exists() else {}
    assert after == before


def test_lab_tab_script_lists_experiment_matrix():
    text = (ROOT / "app" / "static" / "app.js").read_text()
    assert "/api/lab/experiments" in text
    assert "lab-matrix" in text
    assert "Open matrix" in text
