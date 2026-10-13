"""Fate panel accept path: a new owned set, starter sets left alone."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.db import get_fate_weights
from app.main import app


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def _lab_times() -> dict[str, int]:
    lab = Path("data/lab")
    return {path.name: path.stat().st_mtime_ns for path in lab.iterdir() if path.is_file()}


def test_accepting_a_swap_saves_a_new_set_and_leaves_the_starter(tmp_path, monkeypatch):
    before = _lab_times()
    with _client(tmp_path, monkeypatch) as client:
        assert client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}).status_code == 200
        original = client.get("/api/decks/seed-g").json()
        cards = list(original["cards"])
        cut_at = next(index for index, card in enumerate(cards) if card["name"] == "Buddy-Buddy Poffin")
        boss = next(card for card in cards if card["name"] == "Boss's Orders")
        cards.pop(cut_at)
        cards.append(boss)
        created = client.post(
            "/api/decks",
            json={
                "name": "Carpet Set G · cut Buddy-Buddy Poffin",
                "cards": cards,
                "rule_presets": ["s60"],
            },
        )
        assert created.status_code == 200, created.text
        saved = created.json()
        assert not str(saved["id"]).startswith("seed-")
        assert sum(card["name"] == "Boss's Orders" for card in saved["cards"]) == 4
        assert sum(card["name"] == "Buddy-Buddy Poffin" for card in saved["cards"]) == 3
        starter = client.get("/api/decks/seed-g").json()
        assert sum(card["name"] == "Buddy-Buddy Poffin" for card in starter["cards"]) == 4
        assert sum(card["name"] == "Boss's Orders" for card in starter["cards"]) == 3

        client.post("/api/auth/register", json={"email": "kid-fate@example.com", "password": "play"})
        assert client.get(f"/api/decks/{saved['id']}").status_code == 404
        assert client.get("/api/decks/seed-g/fate/ceilings").status_code == 404
    assert _lab_times() == before


def test_weight_overlay_stays_with_the_trainer_who_saved_it(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        admin = client.get("/api/auth/me").json()
        saved = client.post(
            "/api/decks/seed-g/fate/swaps",
            json={"add": "Boss's Orders", "save": True, "weights": {"ecologies": {"control": 9}}},
        )
        assert saved.status_code == 200, saved.text
        assert saved.json()["weights"]["ecologies"]["control"] == 9
        assert saved.json()["label"] == "fast estimate, not a win rate"
        assert get_fate_weights(admin["id"], "s60")["ecologies"]["control"] == 9

        client.post("/api/auth/register", json={"email": "kid-weights@example.com", "password": "play"})
        kid = client.get("/api/auth/me").json()
        assert get_fate_weights(kid["id"], "s60") is None
