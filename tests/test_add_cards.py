from app.catalog import pick_search_hit, search_local
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.main import app
from fastapi.testclient import TestClient


def test_pick_search_hit_prefers_pinned_print_when_names_collide():
    hits = [
        {"id": "sm12-66", "name": "Pikachu", "image": "nuzzle"},
        {"id": "sm3-40", "name": "Pikachu", "image": "shock"},
    ]
    pick = pick_search_hit("Pikachu", hits)
    assert pick["id"] == "sm3-40"
    hits = [
        {"id": "x", "name": "Picnic Basket", "image": ""},
        {"id": "sm3-40", "name": "Pikachu", "image": ""},
    ]
    assert pick_search_hit("Pikachu", hits)["name"] == "Pikachu"
    assert pick_search_hit("pika", hits)["name"] == "Picnic Basket"
    assert pick_search_hit("poke ball", [{"name": "Poké Ball"}])["name"] == "Poké Ball"
    assert pick_search_hit("Cubone", [])["name"] == "Cubone"
    assert pick_search_hit("  ", []) is None


def test_add_cards_via_search_resolve_and_put(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        hits = client.get("/api/cards/search", params={"q": "pika", "scope": "local"}).json()
        pick = pick_search_hit("Pikachu", hits)
        assert pick["name"] == "Pikachu"

        created = client.post(
            "/api/decks",
            json={"name": "Add probe", "cards": [{"name": "Cubone"}], "source": "search"},
        )
        assert created.status_code == 200
        deck = created.json()
        assert deck["count"] == 1
        assert [c["name"] for c in deck["cards"]] == ["Cubone"]

        nest = next(h for h in search_local("nest ball", remote=False) if h["name"] == "Nest Ball")
        appended = client.put(
            f"/api/decks/{deck['id']}",
            json={"cards": deck["cards"] + [{"name": nest["name"], "catalog_id": nest["id"]}]},
        )
        assert appended.status_code == 200
        body = appended.json()
        assert body["count"] == 2
        assert [c["name"] for c in body["cards"]] == ["Cubone", "Nest Ball"]

        again = client.put(
            f"/api/decks/{deck['id']}",
            json={"cards": body["cards"] + [{"name": "Pikachu"}]},
        )
        assert again.json()["count"] == 3
        assert [c["name"] for c in again.json()["cards"]] == ["Cubone", "Nest Ball", "Pikachu"]

        fetched = client.get(f"/api/decks/{deck['id']}").json()
        assert fetched["count"] == 3


def test_put_keeps_existing_cards_when_cards_omitted(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        created = client.post("/api/decks", json={"name": "Keep", "cards": [{"name": "Cubone"}]})
        deck_id = created.json()["id"]
        renamed = client.put(f"/api/decks/{deck_id}", json={"name": "Kept"})
        assert renamed.json()["name"] == "Kept"
        assert [c["name"] for c in renamed.json()["cards"]] == ["Cubone"]
        assert renamed.json()["count"] == 1


def test_member_can_delete_own_set_not_seed(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/register", json={"email": "kid2@example.com", "password": "play"})
        created = client.post("/api/decks", json={"name": "Toss", "cards": [{"name": "Cubone"}]})
        deck_id = created.json()["id"]
        assert client.delete(f"/api/decks/{deck_id}").status_code == 200
        assert client.get(f"/api/decks/{deck_id}").status_code == 404
        assert client.get("/api/decks").json() == []
        assert client.delete("/api/decks/seed-a").status_code == 404


def test_admin_can_delete_created_set(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        created = client.post("/api/decks", json={"name": "Admin toss", "cards": [{"name": "Cubone"}]})
        deck_id = created.json()["id"]
        assert client.delete(f"/api/decks/{deck_id}").json() == {"ok": True}
        ids = {d["id"] for d in client.get("/api/decks").json()}
        assert deck_id not in ids
        blocked = client.delete("/api/decks/seed-a")
        assert blocked.status_code == 400
