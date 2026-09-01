from app.ai.tools import run_tool
from app.db import init_db, save_deck


def test_get_deck_shows_catalog_id_and_attacks():
    init_db()
    saved = save_deck(
        "Spark list",
        [
            {
                "name": "Raichu",
                "catalog_id": "spark",
                "category": "Pokemon",
                "hp": 110,
                "attacks": [{"name": "Ambushing Spark", "damage": 50, "text": "This attack does 20 more."}],
            }
        ],
        source="test",
        deck_id="test-raichu-spark",
    )
    view = run_tool("get_deck", {"deck_id": saved["id"]})
    card = view["cards"][0]
    assert card["name"] == "Raichu"
    assert card["catalog_id"] == "spark"
    assert card["print_unresolved"] is False
    assert card["attacks"][0]["name"] == "Ambushing Spark"


def test_replace_deck_card_swaps_raichu_printing(monkeypatch):
    init_db()
    saved = save_deck(
        "Spark list",
        [
            {
                "name": "Raichu",
                "catalog_id": "spark",
                "category": "Pokemon",
                "hp": 110,
                "attacks": [{"name": "Ambushing Spark", "damage": 50, "text": ""}],
            }
        ],
        source="test",
        deck_id="test-raichu-replace",
    )

    def fake_resolve(name, prefer=None, ocr_text=None, crop_image=None):
        from app.engine.models import Attack, Card

        assert name == "Raichu"
        assert prefer and "electro ball" in " ".join(prefer).lower()
        return Card(
            catalog_id="ball",
            name="Raichu",
            category="Pokemon",
            hp=130,
            attacks=[Attack(name="Electro Ball", cost=["Lightning", "Lightning"], damage=70, text="")],
        )

    monkeypatch.setattr("app.ai.tools.resolve_name", fake_resolve)
    out = run_tool(
        "replace_deck_card",
        {"deck_id": saved["id"], "name": "Raichu", "query": "Raichu Electro Ball"},
    )
    assert out["replaced"] == [0]
    assert out["card"]["catalog_id"] == "ball"
    assert out["card"]["attacks"][0]["name"] == "Electro Ball"
    again = run_tool("get_deck", {"deck_id": saved["id"]})
    assert again["cards"][0]["attacks"][0]["name"] == "Electro Ball"
