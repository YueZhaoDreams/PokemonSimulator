from app.auth import hash_password, verify_password
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.db import get_deck, init_db, list_decks, list_users
from app.main import app
from fastapi.testclient import TestClient


def test_password_hash_is_not_plaintext():
    stored = hash_password("1013")
    assert stored != "1013"
    assert verify_password("1013", stored)
    assert not verify_password("wrong", stored)


def test_admin_owns_seed_decks_and_members_are_isolated(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        blocked = client.get("/api/decks")
        assert blocked.status_code == 401

        bad = client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": "nope"})
        assert bad.status_code == 401

        login = client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert login.status_code == 200
        admin = login.json()
        assert admin["email"] == ADMIN_EMAIL.lower()
        assert admin["role"] == "admin"

        me = client.get("/api/auth/me")
        assert me.status_code == 200
        assert me.json()["role"] == "admin"

        decks = client.get("/api/decks").json()
        assert {d["id"] for d in decks} >= {"seed-a", "seed-b", "seed-c"}
        assert all(d["owner_id"] == admin["id"] for d in decks)

        users = client.get("/api/users").json()
        assert any(u["email"] == ADMIN_EMAIL.lower() for u in users)

        client.post("/api/auth/logout")

        register = client.post(
            "/api/auth/register",
            json={"email": "kid@example.com", "password": "play"},
        )
        assert register.status_code == 200
        member = register.json()
        assert member["role"] == "member"

        mine = client.get("/api/decks").json()
        assert mine == []

        created = client.post(
            "/api/decks",
            json={"name": "Kid set", "cards": [{"name": "Cubone"}]},
        )
        assert created.status_code == 200
        assert created.json()["owner_id"] == member["id"]
        assert client.get("/api/decks").json()[0]["name"] == "Kid set"
        assert client.get("/api/decks/seed-a").status_code == 404
        assert client.get("/api/users").status_code == 403

        again = client.post(
            "/api/auth/register",
            json={"email": "Kid@example.com", "password": "play"},
        )
        assert again.status_code == 409

        steal = client.post(
            "/api/decks",
            json={"id": "seed-a", "name": "Hijack", "cards": [{"name": "Cubone"}]},
        )
        assert steal.status_code == 409
        assert get_deck("seed-a")["name"] != "Hijack"

        from app.db import save_chat, save_deck

        blank = save_deck("Orphan", [{"name": "Cubone"}], deck_id="orphan-deck")
        assert not blank["owner_id"]
        filled = save_deck("Orphan", [{"name": "Cubone"}], deck_id="orphan-deck", owner_id=member["id"])
        assert filled["owner_id"] == member["id"]
        chat = save_chat([{"role": "user", "content": "hi"}], chat_id="orphan-chat")
        assert not chat["owner_id"]
        owned = save_chat([{"role": "user", "content": "hi"}], chat_id="orphan-chat", owner_id=member["id"])
        assert owned["owner_id"] == member["id"]

    from app.ai.tools import reset_viewer, run_tool, use_viewer

    init_db()
    member = {"id": "member-1", "role": "member"}
    token = use_viewer(member)
    try:
        listed = run_tool("list_decks", {})
        assert all(item["id"] != "seed-a" for item in listed)
        assert run_tool("get_deck", {"deck_id": "seed-a"}) == {"error": "deck not found"}
    finally:
        reset_viewer(token)


def test_init_assigns_existing_decks_to_admin(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    init_db()
    admin = next(u for u in list_users() if u["role"] == "admin")
    assert admin["email"] == ADMIN_EMAIL.lower()
    for deck in list_decks():
        assert deck["owner_id"] == admin["id"]
    seed = get_deck("seed-a")
    assert seed["owner_id"] == admin["id"]
