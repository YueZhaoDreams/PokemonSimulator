from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.main import app
from fastapi.testclient import TestClient


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_new_set_follows_posted_rules_and_rejects_empty(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        created = client.post(
            "/api/decks",
            json={"name": "Both", "cards": [{"name": "Cubone"}], "rule_presets": ["b", "c"]},
        )
        assert created.status_code == 200
        body = created.json()
        assert body["rule_presets"] == ["b", "c"]
        assert body["rule_preset"] == "any"
        assert body["archived"] is True

        only_c = client.put(
            f"/api/decks/{body['id']}",
            json={"rule_presets": ["c"]},
        )
        assert only_c.json()["rule_presets"] == ["c"]
        assert only_c.json()["rule_preset"] == "c"
        assert [c["name"] for c in only_c.json()["cards"]] == ["Cubone"]

        denied = client.put(
            f"/api/decks/{body['id']}",
            json={"rule_presets": []},
        )
        assert denied.status_code == 400
        assert "at least one" in denied.json()["detail"].lower()
        assert client.get(f"/api/decks/{body['id']}").json()["rule_presets"] == ["c"]


def test_create_defaults_to_the_trainer_rule(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid3@example.com", "password": "play"})
        created = client.post("/api/decks", json={"name": "Kid set", "cards": [{"name": "Cubone"}]})
        assert created.json()["rule_presets"] == ["s60"]
        assert created.json()["archived"] is False
        switched = client.put("/api/me/rule", json={"preset": "s30"})
        assert switched.status_code == 200
        standard_30 = client.post("/api/decks", json={"name": "Thirty", "cards": [{"name": "Dreepy"}]})
        assert standard_30.json()["rule_presets"] == ["s30"]
        assert standard_30.json()["archived"] is False
        under_c = client.put(
            f"/api/decks/{created.json()['id']}",
            json={"rule_preset": "c"},
        )
        assert under_c.json()["rule_presets"] == ["c"]
        std = client.put(
            f"/api/decks/{created.json()['id']}",
            json={"rule_presets": ["s30", "s60"]},
        )
        assert std.json()["rule_presets"] == ["s30", "s60"]
        assert std.json()["rule_preset"] == "any"
        assert std.json()["archived"] is False


def test_post_existing_id_keeps_cards_when_omitted(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        created = client.post("/api/decks", json={"name": "Keep", "cards": [{"name": "Cubone"}]})
        deck_id = created.json()["id"]
        again = client.post("/api/decks", json={"id": deck_id, "name": "Kept"})
        assert again.status_code == 200
        assert again.json()["name"] == "Kept"
        assert [c["name"] for c in again.json()["cards"]] == ["Cubone"]


def test_save_deck_does_not_shrink_legacy_household_rules(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, init_db, save_deck

    init_db()
    deck = save_deck("Old household", [{"name": "Cubone"}])
    with connect() as conn:
        conn.execute("UPDATE decks SET rules_json=NULL WHERE id=?", (deck["id"],))
    again = save_deck("Old household", [{"name": "Cubone"}, {"name": "Pikachu"}], deck_id=deck["id"])
    assert again["rule_presets"] == ["b", "c"]
    assert again["rule_preset"] == "any"
    assert again["archived"] is True


def test_seed_t_moves_from_rule_b_to_standard_30(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, get_deck, init_db

    init_db()
    with connect() as conn:
        conn.execute("UPDATE decks SET rules_json=? WHERE id='seed-t'", ('["b"]',))
    init_db()
    assert get_deck("seed-t")["rule_presets"] == ["s30"]


def test_startup_retires_household_rules_without_clobbering_custom(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    import json

    from app.db import connect, get_rules, init_db
    from app.engine.models import FamilyRules

    init_db()
    custom = FamilyRules(
        name="House 60",
        deck_size=60,
        prize_count=3,
        pokemon_as_energy=False,
        max_copies_except_basic_energy=4,
        notes="custom prize count",
    )
    with connect() as conn:
        conn.execute(
            "UPDATE settings SET value_json=? WHERE key='rules'",
            (json.dumps(custom.to_dict()),),
        )
    init_db()
    kept = get_rules()
    assert kept.deck_size == 60
    assert kept.prize_count == 3
    assert kept.notes == "custom prize count"

    with connect() as conn:
        conn.execute(
            "UPDATE settings SET value_json=? WHERE key='rules'",
            (json.dumps(FamilyRules().to_dict()),),
        )
    init_db()
    retired = get_rules()
    assert retired.deck_size == 60
    assert retired.prize_count == 6
    assert retired.pokemon_as_energy is False


def test_seed_m_moves_from_rule_b_to_standard_60(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, get_deck, init_db

    init_db()
    with connect() as conn:
        conn.execute("UPDATE decks SET rules_json=? WHERE id='seed-m60'", ('["b"]',))
    init_db()
    assert get_deck("seed-m60")["rule_presets"] == ["s60"]

