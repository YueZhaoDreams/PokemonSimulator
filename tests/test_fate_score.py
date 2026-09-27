import time
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.db import delete_fate_weights
from app.engine.fate.kg import build_catalog_kg, induce
from app.engine.fate.metrics import compute_metrics
from app.engine.fate.score import apply_overlay, boss_equivalent, load_preset, rank_swaps
from app.engine.models import rules_from_preset
from app.main import app
from app.seed_data import SET_G_NAMES, fallback_named


def _rules():
    return rules_from_preset("s60")


def _set_g():
    return [fallback_named(name) for name in SET_G_NAMES]


def _replace(cards, name, replacements):
    pending = list(replacements)
    out = []
    for card in cards:
        if pending and card.name == name:
            out.append(pending.pop(0))
            continue
        out.append(card)
    assert not pending, name
    return out


def _row(report, name):
    return next(row for row in report["rows"] if row["cut"] == name)


def _boss(cards, weights=None):
    rules = _rules()
    weights = weights or load_preset("s60")
    graph = induce(build_catalog_kg(cards, rules), Counter(card.name for card in cards))
    metrics = compute_metrics(graph, rules, cards)
    return boss_equivalent(graph, metrics, cards, weights)


def _four_and_four():
    extra = [fallback_named("Ledyba"), fallback_named("Ledyba"), fallback_named("Ledian"), fallback_named("Ledian")]
    return _replace(_set_g(), "Psychic Energy", extra)


def test_unknown_ecology_is_rejected():
    base = load_preset("s60")
    try:
        apply_overlay(base, {"made_up": 1})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown" in str(exc)
    try:
        apply_overlay(base, {"ecologies": {"nope": 1}})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown ecology" in str(exc)


def test_boss_equivalent_follows_the_weight_data():
    cards = (
        [fallback_named("Ledyba")] * 4
        + [fallback_named("Ledian")] * 4
        + [fallback_named("Boss's Orders")] * 3
    )
    report = _boss(cards)
    boss = next(row for row in report["supporters"] if row["name"] == "Boss's Orders")
    weights = load_preset("s60")
    assert boss["per_copy"] == float(weights["boss_equivalent"]["supporter"]) == 1.0
    assert boss["copies"] == 3
    ledian = next(row for row in report["evolve"] if row["name"] == "Ledian")
    assert ledian["charges"] == 4
    assert ledian["value"] == 4.0

    fewer = []
    removed = False
    for card in cards:
        if not removed and card.name == "Ledian":
            removed = True
            continue
        fewer.append(card)
    dropped = _boss(fewer)
    ledian_3 = next(row for row in dropped["evolve"] if row["name"] == "Ledian")
    assert ledian_3["charges"] == 3
    assert ledian["value"] - ledian_3["value"] == 1
    assert ledian_3["value"] != 0

    doubled = apply_overlay(weights, {"boss_equivalent": {"supporter": 2}})
    assert _boss(cards, doubled)["supporters"][0]["per_copy"] == 2.0


def test_ledian_ranks_above_ledyba_and_clefairy_cites_mega_and_party():
    report = rank_swaps(_four_and_four(), "Mega Clefable ex", None, _rules())
    ledian = _row(report, "Ledian")
    ledyba = _row(report, "Ledyba")
    clefairy = _row(report, "Clefairy")
    assert ledian["rank"] < ledyba["rank"]
    assert "body dependence" in ledian["reason"]
    assert "bodies" in ledian["reason"]
    assert "evolutions" in ledian["reason"]
    assert clefairy["rank"] > ledian["rank"]
    assert "Mega Clefable ex" in clefairy["reason"]
    assert "body dependence" in clefairy["reason"]
    assert "Party charges" in clefairy["reason"]
    assert report["estimate"] is True
    assert "not a win rate" in report["label"]


def test_early_weight_changes_the_conditional_attacker_rank():
    cards = _replace(_set_g(), "Darkness Energy", [fallback_named("Iron Boulder")])
    rules = _rules()
    low = rank_swaps(cards, "Mega Clefable ex", {"early_equal_hands": 0}, rules)
    high = rank_swaps(cards, "Mega Clefable ex", {"early_equal_hands": 5}, rules)
    assert high["weights"]["ecologies"]["early_equal_hands"] == 5
    assert low["weights"]["ecologies"]["early_equal_hands"] == 0
    assert _row(high, "Iron Boulder")["rank"] > _row(low, "Iron Boulder")["rank"]
    default = rank_swaps(cards, "Mega Clefable ex", None, rules)
    boulder = _row(default, "Iron Boulder")
    assert boulder["rank"] > len(default["rows"]) * 0.75


def test_partial_curve_override_keeps_the_other_steps():
    weights = apply_overlay(load_preset("s60"), {"boss_equivalent": {"charge_curve": {"4": 5}}})
    assert float(weights["boss_equivalent"]["charge_curve"]["2"]) == 2
    assert float(weights["boss_equivalent"]["charge_curve"]["4"]) == 5
    cards = [fallback_named("Ledyba")] * 2 + [fallback_named("Ledian")] * 2
    ledian = next(row for row in _boss(cards, weights)["evolve"] if row["name"] == "Ledian")
    assert ledian["charges"] == 2
    assert ledian["value"] == 2
    party = apply_overlay(load_preset("s60"), {"copy_curves": {"party": {"4": 20}}})
    assert float(party["copy_curves"]["party"]["1"]) == 3
    assert float(party["copy_curves"]["party"]["4"]) == 20


def test_non_integer_curve_step_is_rejected():
    try:
        apply_overlay(load_preset("s60"), {"copy_curves": {"party": {"two": 2}}})
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "integer" in str(exc)


def test_corrupt_weight_overlay_is_ignored(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, get_fate_weights, init_db, save_fate_weights

    init_db()
    save_fate_weights("owner", "s60", {"early_equal_hands": 0})
    with connect() as conn:
        conn.execute(
            "UPDATE fate_weight_overlays SET weights_json=? WHERE owner_id=?",
            ("{", "owner"),
        )
    assert get_fate_weights("owner", "s60") is None


def test_echoed_weights_round_trip():
    cards = [fallback_named("Ledyba")] * 2 + [fallback_named("Ledian")] * 2
    rules = _rules()
    first = rank_swaps(cards, "Mega Clefable ex", None, rules)
    second = rank_swaps(cards, "Mega Clefable ex", first["weights"], rules)
    assert second["weights"]["ecologies"] == first["weights"]["ecologies"]
    assert second["rows"][0]["delta_s"] == first["rows"][0]["delta_s"]


def test_add_can_be_a_catalog_id_and_unknown_cards_fail():
    mega = fallback_named("Mega Clefable ex")
    cards = [fallback_named("Ledyba")] * 2 + [fallback_named("Ledian")] * 2
    report = rank_swaps(cards, mega.catalog_id, None, _rules())
    assert report["add"] == "Mega Clefable ex"
    assert report["rows"]
    try:
        rank_swaps(cards, "Not A Real Pokemon XYZ", None, _rules())
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "unknown card" in str(exc)


def test_score_does_not_touch_the_match_kernel():
    root = Path(__file__).resolve().parents[1]
    source = (root / "app/engine/fate/score.py").read_text()
    game = (root / "app/engine/game.py").read_text()
    assert "strat.name" not in source
    assert "app.engine.game" not in source
    assert "run_simulation" not in source
    assert "Boss's Orders" not in source
    assert "Iron Boulder" not in source
    assert "Ledian" not in source
    assert "early_equal_hands" not in game


def test_swap_route_and_tool(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    def _boom(*_args, **_kwargs):
        raise AssertionError("run_simulation")

    monkeypatch.setattr("app.engine.montecarlo.run_simulation", _boom)
    monkeypatch.setattr("app.main.run_simulation", _boom)
    monkeypatch.setattr("app.ai.tools.run_simulation", _boom)

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        started = time.perf_counter()
        response = client.post("/api/decks/seed-g/fate/swaps", json={"add": "Mega Clefable ex"})
        elapsed = time.perf_counter() - started
        assert response.status_code == 200, response.text
        body = response.json()
        assert elapsed < 2
        assert body["estimate"] is True
        assert "not a win rate" in body["label"]
        assert body["deck_id"] == "seed-g"
        names = {card["name"] for card in client.get("/api/decks/seed-g").json()["cards"]}
        assert len(body["rows"]) == len(names)
        assert [row["rank"] for row in body["rows"]] == list(range(1, len(body["rows"]) + 1))
        assert body["rows"][0]["delta_s"] >= body["rows"][-1]["delta_s"]
        assert "ecologies" in body["rows"][0]
        assert "early_equal_hands" in body["weights"]["ecologies"]
        ledian = _row(body, "Ledian")
        ledyba = _row(body, "Ledyba")
        clefairy = _row(body, "Clefairy")
        assert ledian["rank"] < ledyba["rank"]
        assert "bodies" in ledian["reason"] and "evolutions" in ledian["reason"]
        assert clefairy["rank"] > ledian["rank"]
        assert "Mega Clefable ex" in clefairy["reason"]
        assert "Party charges" in clefairy["reason"]
        boss = next(row for row in body["boss_equivalent"]["supporters"] if row["name"] == "Boss's Orders")
        assert boss["per_copy"] == 1.0
        evolve = next(row for row in body["boss_equivalent"]["evolve"] if row["name"] == "Ledian")
        assert evolve["charges"] == 2
        assert evolve["value"] == 2.0

        unknown = client.post("/api/decks/seed-g/fate/swaps", json={"add": "Mega Clefable ex", "weights": {"nope": 1}})
        assert unknown.status_code == 400

        bare_save = client.post(
            "/api/decks/seed-g/fate/swaps",
            json={"add": "Mega Clefable ex", "save": True},
        )
        assert bare_save.status_code == 400

        failed_save = client.post(
            "/api/decks/seed-g/fate/swaps",
            json={"add": "Not A Real Pokemon XYZ", "weights": {"early_equal_hands": 0}, "save": True},
        )
        assert failed_save.status_code == 400
        untouched = client.post("/api/decks/seed-g/fate/swaps", json={"add": "Mega Clefable ex"})
        assert untouched.json()["weights"]["ecologies"]["early_equal_hands"] == 1

        saved = client.post(
            "/api/decks/seed-g/fate/swaps",
            json={"add": "Mega Clefable ex", "weights": {"early_equal_hands": 0}, "save": True},
        )
        assert saved.status_code == 200
        assert saved.json()["weights"]["ecologies"]["early_equal_hands"] == 0
        echoed = client.post("/api/decks/seed-g/fate/swaps", json={"add": "Mega Clefable ex"})
        assert echoed.json()["weights"]["ecologies"]["early_equal_hands"] == 0
        me = client.get("/api/auth/me").json()
        delete_fate_weights(me["id"], "s60")

        token = use_viewer(me)
        try:
            tool = run_tool("rank_fate_swaps", {"deck_id": "seed-g", "add": "Mega Clefable ex"})
        finally:
            reset_viewer(token)
        assert tool["deck_id"] == "seed-g"
        assert tool["estimate"] is True
        assert tool["rows"]
