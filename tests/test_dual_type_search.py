from app.catalog import search_local
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, STATIC_DIR
from app.dual_type import dual_type_record, load_dual_type_cards, search_dual_type
from app.main import app
from fastapi.testclient import TestClient


def test_dual_type_category_lists_every_physical_printing():
    cards = load_dual_type_cards()
    assert len(cards) == 106
    assert {card["stage"] for card in cards} == {"Basic", "Stage 1", "Stage 2", "LEGEND", "MEGA"}
    assert all(len(card["types"]) >= 2 for card in cards)
    ids = [card["id"] for card in cards]
    assert len(ids) == len(set(ids))
    assert "me55c-99" in ids and "me55c-100" in ids
    assert any(card["id"] == "xyp-XY173" and card["stage"] == "Basic" for card in cards)
    assert any("Colorless" in card["types"] for card in cards)
    assert not any(card["id"].startswith(("C1", "tcgp")) for card in cards)


def test_dual_type_search_sorts_by_printed_attack_number():
    hits = search_dual_type("")
    assert len(hits) == 106
    assert all(hit["search_category"] == "双属性" for hit in hits)
    values = [hit["attack_value"] for hit in hits]
    assert values == sorted(values, reverse=True)
    assert hits[0]["name"] == "M Steelix-EX"
    assert hits[0]["attack"] == "160"
    kyogre = next(hit for hit in hits if hit["name"] == "Kyogre & Groudon LEGEND")
    assert kyogre["attack"] == "100×"
    assert kyogre["attack_value"] == 100
    assert hits[-1]["attack_value"] == 0

    named = search_dual_type("", sort="name")
    assert [hit["name"] for hit in named] == sorted((hit["name"] for hit in named), key=str.casefold)
    assert len(named) == 106


def test_dual_type_search_filters_stage_and_name():
    assert {hit["stage"] for hit in search_dual_type("基础")} == {"Basic"}
    assert {hit["stage"] for hit in search_dual_type("basic")} == {"Basic"}
    evolution = {hit["stage"] for hit in search_dual_type("进化")}
    assert evolution == {"Stage 1", "Stage 2", "MEGA"}
    assert {hit["stage"] for hit in search_dual_type("传说")} == {"LEGEND"}
    assert len(search_dual_type("传说")) == 16
    assert len(search_dual_type("legend")) == 16
    found = search_dual_type("cacturne")
    assert [hit["id"] for hit in found] == ["ex4-1"]
    assert found[0]["types"] == ["Grass", "Darkness"]
    assert search_dual_type("双属性") == search_dual_type("")


def test_dual_type_resolve_keeps_printed_attack_text():
    card = dual_type_record("ex4-10")
    assert card["types"] == ["Fire", "Darkness"]
    assert card["stage"] == "Stage 1"
    assert card["search_category"] == "双属性"
    spurt = next(attack for attack in card["attacks"] if attack["name"] == "Magma Spurt")
    assert spurt["printed_damage"] == "30×"
    assert spurt["damage"] == 30
    assert spurt["text"] == (
        "Discard the top 5 cards from your deck. This attack does 30 damage "
        "times the number of Fire and Fighting basic Energy cards discarded in this way."
    )
    assert "Fire" in spurt["cost"] and "Colorless" in spurt["cost"]

    for raw in load_dual_type_cards():
        resolved = dual_type_record(raw["id"])
        assert resolved["name"] == raw["name"]
        assert resolved["types"] == raw["types"]
        assert len(resolved["attacks"]) == len(raw["attacks"])
        for attack, printed in zip(resolved["attacks"], raw["attacks"]):
            assert attack["text"] == printed["text"]
            assert attack["printed_damage"] == printed["damage"]
            if printed["cost"]:
                assert "".join(attack["cost"]) == printed["cost"].replace(" ", "")


def test_dual_type_search_endpoint_does_not_call_remote(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr(
        "app.catalog._remote_search_briefs",
        lambda q: (_ for _ in ()).throw(AssertionError(q)),
    )

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        listed = client.get("/api/cards/search", params={"category": "dual", "sort": "attack"})
        assert listed.status_code == 200
        body = listed.json()
        assert len(body) == 106
        assert body[0]["attack_value"] >= body[-1]["attack_value"]
        alias = client.get("/api/cards/search", params={"q": "双属性"})
        assert alias.status_code == 200
        assert len(alias.json()) == 106
        named = client.get("/api/cards/search", params={"q": "pika", "scope": "local"})
        assert named.status_code == 200
        assert any(hit["name"] == "Pikachu" for hit in named.json())

    assert any(hit["name"] == "Pikachu" for hit in search_local("pika", remote=False))


def test_card_search_ui_has_dual_type_category():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    cards = html[html.index('id="view-cards"') : html.index('id="view-fight"')]
    assert 'id="cardCatDual"' in cards
    assert ">双属性<" in cards
    assert 'id="dualSort"' in cards
    assert 'value="attack"' in cards
    js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "function setCardCategory" in js
    assert 'params.set("category", "dual")' in js
    assert "printed_damage" in js
    css = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
    assert '.pad-device[data-mode="pokemon"] #padCardCats' in css
