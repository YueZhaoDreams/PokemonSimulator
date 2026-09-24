from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.engine.effects import parse_ability_effects, parse_trainer_effects
from app.engine.fate.kg import build_catalog_kg, explain_edge, induce, linked_degree, prize_weight
from app.engine.models import Attack, Card, rules_from_preset
from app.main import app
from app.seed_data import SET_G_NAMES, build_fallback_deck, fallback_named

LEDIAN = (
    "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
    "you may switch in 1 of your opponent's Benched Pokémon that has 90 HP or less remaining "
    "to the Active Spot."
)
BOSS = "Switch in 1 of your opponent's Benched Pokémon to the Active Spot."
PARTY = (
    "Once during your turn, if this Pokémon is in the Active Spot, for each of your Benched Clefairy, "
    "you may search your deck for a Psychic Energy card and attach it to that Clefairy. Then, shuffle your deck."
)


def _isolated() -> Card:
    return Card(
        catalog_id="fixture-isolated",
        name="Isolated Tackle",
        category="Pokemon",
        stage="Basic",
        types=["Colorless"],
        hp=50,
        attacks=[Attack(name="Tackle", cost=["Colorless"], damage=10, text="")],
    )


def test_ledian_and_boss_share_force_opponent_active():
    ledian = parse_ability_effects(LEDIAN)
    boss = parse_trainer_effects(BOSS)
    ledian_hook = next(e for e in ledian if e["kind"] == "force_opponent_active")
    boss_hook = next(e for e in boss if e["kind"] == "force_opponent_active")
    assert ledian_hook["trigger"] == "on_evolve"
    assert ledian_hook["max_remaining_hp"] == 90
    assert boss_hook["kind"] == ledian_hook["kind"]
    assert "max_remaining_hp" not in boss_hook


def test_clefairy_attach_edge_has_no_look_and_isolated_has_no_real_link():
    clefairy = fallback_named("Clefairy")
    psychic = fallback_named("Psychic Energy")
    isolated = _isolated()
    kg = build_catalog_kg([clefairy, psychic, isolated], rules_from_preset("s60"))
    party = [
        e
        for e in kg.edges
        if e.kind == "attaches_from_deck" and e.src == clefairy.catalog_id
    ]
    assert len(party) == 1
    assert party[0].effect.get("energy_type") == "Psychic"
    assert "look" not in party[0].effect
    assert "look" not in explain_edge(party[0]).lower()
    assert linked_degree(kg, isolated.catalog_id) == 0
    again = build_catalog_kg([clefairy, psychic, isolated], rules_from_preset("s60"))
    assert [(e.kind, e.src, e.dst) for e in again.edges] == [(e.kind, e.src, e.dst) for e in kg.edges]


def test_colorless_pay_is_generic_and_set_g_induce_keeps_ledian_and_clefairy():
    cards = build_fallback_deck(list(SET_G_NAMES))
    kg = build_catalog_kg(cards, rules_from_preset("s60"))
    colorless = [e for e in kg.edges if e.kind == "pays_energy" and e.effect.get("energy_type") == "Colorless"]
    assert colorless and all(e.generic for e in colorless)
    deck = induce(kg, [(c.name, 1) for c in cards])
    ledian = next(n for n in deck.nodes if n.name == "Ledian")
    gust = next(e for e in deck.edges if e.src == ledian.id and e.kind == "force_opponent_active")
    assert gust.effect["trigger"] == "on_evolve"
    assert gust.effect["max_remaining_hp"] == 90
    assert "90 HP or less" in explain_edge(gust)
    clefairy = next(n for n in deck.nodes if n.name == "Clefairy")
    attach = next(e for e in deck.edges if e.src == clefairy.id and e.kind == "attaches_from_deck")
    assert attach.effect["benched_name"] == "clefairy"
    assert "look" not in attach.effect


def test_prize_weight_requires_the_ex_suffix():
    rules = rules_from_preset("s60")
    ex = Card(catalog_id="ex", name="Clefable ex", category="Pokemon")
    mega = Card(catalog_id="mega", name="Mega Clefable ex", category="Pokemon")
    calyrex = Card(catalog_id="cal", name="Calyrex", category="Pokemon")
    assert prize_weight(ex, rules) == 2
    assert prize_weight(mega, rules) == 3
    assert prize_weight(calyrex, rules) == 1


def test_evolves_from_links_every_printing_of_that_name():
    a = Card(catalog_id="base-a", name="Clefairy", category="Pokemon", stage="Basic", hp=60)
    b = Card(catalog_id="base-b", name="Clefairy", category="Pokemon", stage="Basic", hp=50)
    stage = Card(
        catalog_id="stage",
        name="Clefable",
        category="Pokemon",
        stage="Stage1",
        hp=90,
        evolves_from="Clefairy",
    )
    kg = build_catalog_kg([a, b, stage])
    srcs = {e.src for e in kg.edges if e.kind == "evolves_into" and e.dst == "stage"}
    assert srcs == {"base-a", "base-b"}
    deck = induce(kg, [("Clefairy", 1), ("Clefairy", 3), ("Clefable", 1)])
    copies = {n.name: n.attributes["copies"] for n in deck.nodes if n.kind == "printing"}
    assert copies["Clefairy"] == 4
    assert "copies" not in next(n for n in kg.nodes if n.name == "Clefairy").attributes
    partner = Card(
        catalog_id="namer",
        name="Namer",
        category="Trainer",
        text="Search your deck for a Clefable.",
    )
    named = build_catalog_kg([partner, stage])
    edge = next(e for e in named.edges if e.kind == "named_partner")
    assert edge.source == "Search your deck for a Clefable."


def test_party_sentence_parses_without_look():
    effects = parse_ability_effects(PARTY)
    assert effects[0]["kind"] == "attach_energy_from_deck_per_benched"
    assert "look" not in effects[0]


def test_kg_route_and_tool(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        body = client.get("/api/decks/seed-g/fate/kg").json()
        assert body["deck_id"] == "seed-g"
        assert any(e["kind"] == "force_opponent_active" for e in body["edges"])
        assert any(e["kind"] == "attaches_from_deck" and "look" not in e["effect"] for e in body["edges"])
        token = use_viewer(client.get("/api/auth/me").json())
        try:
            tool = run_tool("deck_kg", {"deck_id": "seed-g"})
        finally:
            reset_viewer(token)
        assert tool["deck_id"] == "seed-g"
        assert tool["edges"]
