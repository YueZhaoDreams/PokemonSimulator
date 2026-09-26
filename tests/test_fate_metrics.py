from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.engine.fate import compute_metrics
from app.engine.fate.kg import build_catalog_kg, induce
from app.engine.models import Attack, Card, rules_from_preset
from app.main import app
from app.seed_data import SET_G_NAMES, build_fallback_deck, fallback_named

PARTY = (
    "Once during your turn, if this Pokémon is in the Active Spot, for each of your Benched Clefairy, "
    "you may search your deck for a Psychic Energy card and attach it to that Clefairy. Then, shuffle your deck."
)


def _mon(name, damage, cost=("Psychic", "Colorless"), text="", stage="Basic", evolves_from=None, abilities=None):
    return Card(
        catalog_id=name.lower().replace(" ", "-"),
        name=name,
        category="Pokemon",
        stage=stage,
        types=["Psychic"],
        hp=100,
        evolves_from=evolves_from,
        attacks=[Attack(name="Hit", cost=list(cost), damage=damage, text=text)],
        abilities=list(abilities or []),
    )


def _energy(name, energy_type, stage="Basic"):
    return Card(
        catalog_id=name.lower().replace(" ", "-"),
        name=name,
        category="Energy",
        stage=stage,
        types=[energy_type],
        energy_type=energy_type,
    )


def _report(cards, rules=None):
    rules = rules or rules_from_preset("s60")
    graph = induce(build_catalog_kg(cards, rules), Counter(c.name for c in cards))
    return compute_metrics(graph, rules, cards)


def _node(report, name):
    return next(row for row in report["nodes"] if row["name"] == name)


def _line(report, evolution):
    return next(row for row in report["lines"] if row["evolution"] == evolution)


def test_same_cost_pair_reports_damage_per_energy():
    report = _report([_mon("Fifty", 50), _mon("Hundred", 100)])
    assert _node(report, "Fifty")["dpe_lead"] == 25
    assert _node(report, "Hundred")["dpe_lead"] == 50


def test_mega_clefable_ex_bounds_and_warm_up_from_print():
    mega = fallback_named("Mega Clefable ex")
    report = _report([mega])
    row = _node(report, "Mega Clefable ex")
    assert row["dpe_min"] == 60
    assert row["dpe_max"] == 140
    assert row["warm_up_turns"] == 2
    assert row["prize_weight"] == 3


def test_iron_boulder_keeps_its_printed_condition():
    boulder = fallback_named("Iron Boulder")
    report = _report([boulder])
    row = _node(report, "Iron Boulder")
    assert row["lead_damage"] == 170
    assert row["energy_lead"] == 2
    assert row["dpe_lead"] == 85
    assert "does nothing" in row["condition"]


def test_ledyba_ledian_charges_follow_the_shorter_stage():
    def line(bodies, evolutions):
        cards = [_mon("Ledyba", 30, ("Colorless", "Colorless"))] * bodies
        cards += [
            _mon("Ledian", 70, ("Colorless", "Colorless"), stage="Stage1", evolves_from="Ledyba")
        ] * evolutions
        return _line(_report(cards), "Ledian")

    full = line(4, 4)
    assert full["charges"] == 4 and full["stranded"] is False
    short_bodies = line(3, 4)
    assert short_bodies["charges"] == 3 and short_bodies["stranded"] is True
    short_evos = line(4, 3)
    assert short_evos["charges"] == 3 and short_evos["stranded"] is False


def test_rare_candy_is_a_path_not_a_body():
    cards = [_mon("Ledyba", 30, ("Colorless", "Colorless"))] * 4
    cards += [_mon("Ledian", 70, ("Colorless", "Colorless"), stage="Stage1", evolves_from="Ledyba")] * 4
    cards.append(
        Card(catalog_id="candy", name="Rare Candy", category="Trainer", trainer_kind="item", text="Evolve a Basic.")
    )
    row = _line(_report(cards), "Ledian")
    assert row["bodies"] == 4
    assert row["charges"] == 4
    assert row["rare_candy"] is True


def test_energy_budget_keeps_colorless_special_off_a_typed_cost():
    attacker = _mon("Pair", 100, ("Psychic", "Psychic"))
    psychic = [_energy("Psychic Energy", "Psychic")] * 4
    darkness = [_energy("Darkness Energy", "Darkness")] * 3
    boomerang = fallback_named("Boomerang Energy")
    report = _report([attacker, *psychic, *darkness, boomerang])
    budget = report["energy_budget"]
    assert budget["supply"]["Psychic"] == 4
    assert budget["supply"]["Darkness"] == 3
    assert "Boomerang" not in budget["supply"]
    assert budget["special_colorless"] == [
        {"name": "Boomerang Energy", "copies": 1, "pays": "Colorless", "pays_typed_cost": False}
    ]
    row = _node(report, "Pair")
    assert row["colorless_special_pays_typed_cost"] is False
    assert row["typed_payable_from_supply"] is True

    unpaid = _report([attacker, *darkness, boomerang])
    assert _node(unpaid, "Pair")["typed_payable_from_supply"] is False
    assert _node(unpaid, "Pair")["colorless_special_pays_typed_cost"] is False


def test_only_generic_energy_pay_is_isolated():
    lonely = _mon("Lonely", 10, ("Colorless",))
    report = _report([lonely, _energy("Psychic Energy", "Psychic")])
    assert _node(report, "Lonely")["isolated"] is True
    linked = _report(
        [
            _mon("Ledyba", 30, ("Colorless",)),
            _mon("Ledian", 70, ("Colorless",), stage="Stage1", evolves_from="Ledyba"),
        ]
    )
    assert _node(linked, "Ledian")["isolated"] is False
    assert _node(linked, "Ledyba")["isolated"] is False


def test_two_printings_of_one_name_keep_their_own_attacks():
    first = _mon("Twin", 50)
    second = _mon("Twin", 100)
    first.catalog_id = "twin-a"
    second.catalog_id = "twin-b"

    def rows(cards):
        report = _report(cards)
        return sorted(
            (row["id"], row["dpe_lead"], row["copies"])
            for row in report["nodes"]
            if row["name"] == "Twin"
        )

    assert rows([first, second]) == rows([second, first]) == [("twin-a", 25, 1), ("twin-b", 50, 1)]


def test_colorless_cost_counts_any_attach_from_deck():
    from app.engine.models import Ability

    party = [Ability(name="Moon-Watching Party", text=PARTY)]
    colorless = _mon("Clefairy", 30, ("Colorless", "Colorless"), abilities=party)
    row = _node(_report([colorless]), "Clefairy")
    assert row["acceleration"] == 1
    assert row["warm_up_turns"] == 1
    typed = _mon("Clefairy", 30, ("Fire", "Fire"), abilities=party)
    assert _node(_report([typed]), "Clefairy")["acceleration"] == 0


def test_attach_from_deck_raises_attach_rate_up_to_the_lead_cost():
    from app.engine.models import Ability

    clefairy = _mon(
        "Clefairy",
        30,
        ("Psychic", "Psychic", "Psychic"),
        abilities=[Ability(name="Moon-Watching Party", text=PARTY)],
    )
    row = _node(_report([clefairy]), "Clefairy")
    assert row["acceleration"] == 1
    assert row["attach_rate"] == 2
    assert row["warm_up_turns"] == 1.5


def test_set_g_mega_and_ledian_follow_the_locked_list():
    report = _report(build_fallback_deck(list(SET_G_NAMES)))
    mega = _node(report, "Mega Clefable ex")
    assert mega["dpe_min"] == 60 and mega["dpe_max"] == 140 and mega["warm_up_turns"] == 2
    ledian = _line(report, "Ledian")
    assert ledian["bodies"] == 2 and ledian["evolutions"] == 2
    assert ledian["charges"] == 2 and ledian["stranded"] is False
    assert report["energy_budget"]["supply"]["Psychic"] > report["energy_budget"]["supply"]["Darkness"]
    assert report["energy_budget"]["special_colorless"] == []


def test_metrics_do_not_name_a_strategy():
    source = Path("app/engine/fate/metrics.py").read_text()
    assert "strat.name" not in source
    assert "app.engine.game" not in source


def test_metrics_route_and_tool(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        body = client.get("/api/decks/seed-g/fate/metrics").json()
        assert body["deck_id"] == "seed-g"
        assert body["estimate"] is True
        mega = next(row for row in body["nodes"] if row["name"] == "Mega Clefable ex")
        assert mega["dpe_min"] == 60 and mega["warm_up_turns"] == 2
        token = use_viewer(client.get("/api/auth/me").json())
        try:
            tool = run_tool("deck_metrics", {"deck_id": "seed-g"})
        finally:
            reset_viewer(token)
        assert tool["deck_id"] == "seed-g"
        assert tool["nodes"]
