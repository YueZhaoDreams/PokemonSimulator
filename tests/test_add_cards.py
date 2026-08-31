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
    numbered = [
        {"id": "sv01-148", "name": "Starly", "local_id": "148"},
        {
            "id": "swsh9-117",
            "name": "Starly",
            "local_id": "117",
            "code": "117/172",
        },
    ]
    assert pick_search_hit("117/172", numbered)["id"] == "swsh9-117"
    assert pick_search_hit("starly 117", numbered)["id"] == "swsh9-117"
    assert pick_search_hit("Starly", numbered)["id"] == "sv01-148"
    mixed = [
        {"id": "sv01-117", "name": "Grapploct", "local_id": "117", "code": "117/193"},
        {"id": "swsh9-117", "name": "Starly", "local_id": "117", "code": "117/172"},
    ]
    assert pick_search_hit("starly 117", mixed)["id"] == "swsh9-117"
    miss = pick_search_hit("starly 117", [mixed[0]])
    assert miss["name"] == "Starly"
    assert miss.get("id") != "sv01-117"


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


def test_resolve_uses_catalog_id_and_pinned_name_without_full_search(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    def _block_fetch(*_a, **_k):
        raise AssertionError("TCGDex should not run for seed cards")

    monkeypatch.setattr("app.main.fetch_full", _block_fetch)
    monkeypatch.setattr(
        "app.main.resolve_name",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("name search should not run")),
    )

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        by_id = client.post("/api/cards/resolve", json={"id": "sv06-112", "name": "Cornerstone Mask Ogerpon ex"})
        assert by_id.status_code == 200
        assert by_id.json()["catalog_id"] == "sv06-112"
        assert by_id.json()["name"] == "Cornerstone Mask Ogerpon ex"
        by_name = client.post("/api/cards/resolve", json={"name": "Cornerstone Mask Ogerpon ex"})
        assert by_name.status_code == 200
        assert by_name.json()["catalog_id"] == "sv06-112"


def test_resolve_and_replace_drayton_without_network(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr("app.catalog._remote_search_briefs", lambda q: [])

    def _timeout(*_a, **_k):
        raise TimeoutError("timed out")

    monkeypatch.setattr("app.catalog._CLIENT.get", _timeout)
    monkeypatch.setattr("app.main.fetch_full", _timeout)

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        resolved = client.post("/api/cards/resolve", json={"id": "sv08-174", "name": "Drayton"})
        assert resolved.status_code == 200
        card = resolved.json()
        assert card["catalog_id"] == "sv08-174"
        assert card["name"] == "Drayton"
        assert card["trainer_kind"] == "supporter"
        assert "top 7" in (card.get("text") or "").lower()

        stale = client.post("/api/cards/resolve", json={"id": "missing-print", "name": "Drayton"})
        assert stale.status_code == 200
        assert stale.json()["catalog_id"] == "sv08-174"

        created = client.post(
            "/api/decks",
            json={"name": "Replace probe", "cards": [{"name": "Cubone"}], "source": "search"},
        )
        deck = created.json()
        replaced = client.put(
            f"/api/decks/{deck['id']}",
            json={"cards": [card]},
        )
        assert replaced.status_code == 200
        assert replaced.json()["cards"][0]["name"] == "Drayton"
        assert replaced.json()["cards"][0]["catalog_id"] == "sv08-174"
