from collections import Counter

from fastapi.testclient import TestClient

from app.ai.tools import reset_viewer, run_tool, use_viewer
from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.engine.fate import compute_ceilings, printed_draw_operators
from app.engine.models import rules_from_preset
from app.engine.probability import draw_probability
from app.main import app
from app.seed_data import SET_C_NAMES, SET_G_NAMES, build_fallback_deck, fallback_named


def _set_g():
    return build_fallback_deck(list(SET_G_NAMES))


def _row(report: dict, name: str) -> dict:
    return next(row for row in report["names"] if row["name"] == name)


def test_set_g_matches_draw_probability_and_caps_from_s60():
    cards = _set_g()
    names = [c.name for c in cards]
    report = compute_ceilings(cards, rules_from_preset("s60"), preset="s60")

    assert report["rules"] == {
        "preset": "s60",
        "name": "Standard 60 cards, 4 of a name",
        "deck_size": 60,
        "opening_hand": 7,
        "copy_cap": 4,
    }
    assert report["deck_size"] == 60
    assert report["size_matches_rules"] is True
    assert report["estimate"] is True
    assert Counter(row["name"] for row in report["names"]) == Counter(set(names))
    for row in report["names"]:
        expected = draw_probability(row["name"], names, 7)
        assert row["copies"] == expected["copies"]
        assert abs(row["p_opening"] - expected["p_at_least_one"]) < 1e-9

    ledian = _row(report, "Ledian")
    mewtwo = _row(report, "Mewtwo")
    assert ledian["copies"] == 4 and ledian["copy_cap"] == 4 and ledian["at_cap"] is True
    assert mewtwo["copies"] == 1 and mewtwo["at_cap"] is False
    assert ledian["p_opening"] > mewtwo["p_opening"]
    assert abs(mewtwo["p_opening"] - 7 / 60) < 1e-9

    psychic = _row(report, "Psychic Energy")
    assert psychic["copies"] == 17 and psychic["copy_cap"] is None and psychic["over_cap"] is False
    boomerang = _row(report, "Boomerang Energy")
    assert boomerang["copy_cap"] == 4

    assert all(row["name"] != "Mega Clefable ex" for row in report["names"])


def test_thirty_card_presets_report_their_own_size_and_cap():
    cards = build_fallback_deck(list(SET_C_NAMES))
    assert len(cards) == 30

    rule_c = compute_ceilings(cards, rules_from_preset("c"), preset="c")
    assert rule_c["rules"]["deck_size"] == 30
    assert rule_c["rules"]["copy_cap"] == 4
    assert rule_c["deck_size"] == 30

    s30 = compute_ceilings(cards, rules_from_preset("s30"), preset="s30")
    assert s30["rules"]["copy_cap"] == 2
    clefairy = _row(s30, "Clefairy")
    assert clefairy["copy_cap"] == 2
    assert clefairy["over_cap"] is (clefairy["copies"] > 2)


def test_set_g_has_no_unconditional_draw_operator():
    cards = _set_g()
    report = compute_ceilings(cards, rules_from_preset("s60"))
    assert report["effective_seen"] == report["opening_hand"] == 7
    listed = {op["name"]: op for op in report["draw_operators"]}
    # Surfer draws until 5 in hand: shown, not counted, no amount invented.
    assert listed["Surfer"]["counted"] is False
    assert listed["Surfer"]["amount"] is None
    assert listed["Surfer"]["kind"] == "draw_until_hand"
    for row in report["names"]:
        assert row["p_seen"] == row["p_opening"]
        assert row["p_gain"] == 0


def test_printed_draw_three_raises_seen_cards_by_three():
    cards = _set_g()
    # Cut one Psychic Energy for Hop so the list stays 60 cards.
    cut = next(i for i, c in enumerate(cards) if c.name == "Psychic Energy")
    cards[cut] = fallback_named("Hop")
    assert cards[cut].text == "Draw 3 cards."

    report = compute_ceilings(cards, rules_from_preset("s60"))
    assert report["effective_seen"] == 10
    hop = next(op for op in report["draw_operators"] if op["name"] == "Hop")
    assert hop == {
        "name": "Hop",
        "copies": 1,
        "kind": "draw",
        "amount": 3,
        "counted": True,
        "note": "+3 seen cards per copy",
        "source": "Draw 3 cards.",
    }

    one_of = _row(report, "Mewtwo")
    assert abs(one_of["p_gain"] - 3 / 60) < 1e-6

    four_of = _row(report, "Ledian")
    assert four_of["p_gain"] > 3 / 60
    assert abs(four_of["p_seen"] - draw_probability("Ledian", [c.name for c in cards], 10)["p_at_least_one"]) < 1e-9


def test_two_hops_count_per_copy_and_conditional_draws_do_not():
    cards = _set_g()
    energy = [i for i, c in enumerate(cards) if c.name == "Psychic Energy"]
    cards[energy[0]] = fallback_named("Hop")
    cards[energy[1]] = fallback_named("Hop")
    ops = printed_draw_operators(cards)
    hop = next(op for op in ops if op["name"] == "Hop")
    assert hop["copies"] == 2 and hop["counted"] is True
    report = compute_ceilings(cards, rules_from_preset("s60"))
    assert report["effective_seen"] == 7 + 3 * 2

    iono = fallback_named("Iono")
    if iono.text:
        listed = printed_draw_operators([iono])
        assert not listed or listed[0]["counted"] is False


def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    return TestClient(app)


def test_route_uses_deck_rules_and_accepts_preset_override(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        deck = client.get("/api/decks/seed-g").json()
        assert deck["rule_presets"] == ["s60"]

        body = client.get("/api/decks/seed-g/fate/ceilings").json()
        assert body["deck_id"] == "seed-g"
        assert body["rules"]["preset"] == "s60"
        assert body["rules"]["deck_size"] == 60 and body["rules"]["copy_cap"] == 4
        assert body["deck_size"] == 60
        names = [c["name"] for c in deck["cards"]]
        ledian = _row(body, "Ledian")
        assert abs(ledian["p_opening"] - draw_probability("Ledian", names, 7)["p_at_least_one"]) < 1e-9

        overridden = client.get("/api/decks/seed-g/fate/ceilings", params={"rule_preset": "s30"}).json()
        assert overridden["rules"]["preset"] == "s30"
        assert overridden["rules"]["copy_cap"] == 2
        assert _row(overridden, "Ledian")["over_cap"] is True

        bad = client.get("/api/decks/seed-g/fate/ceilings", params={"rule_preset": "s99"})
        assert bad.status_code == 400


def test_route_and_tool_are_owner_scoped(tmp_path, monkeypatch):
    with _client(tmp_path, monkeypatch) as client:
        client.post("/api/auth/register", json={"email": "kid@example.com", "password": "play"})
        mine = client.post("/api/decks", json={"name": "Mine", "cards": [{"name": "Clefairy"}] * 4}).json()
        assert client.get(f"/api/decks/{mine['id']}/fate/ceilings").json()["deck_size"] == 4
        assert client.get("/api/decks/seed-g/fate/ceilings").status_code == 404

        token = use_viewer(client.get("/api/auth/me").json())
        try:
            report = run_tool("deck_ceilings", {"deck_id": mine["id"]})
            assert report["rules"]["preset"] == "b"
            assert report["rules"]["deck_size"] == 30 and report["rules"]["copy_cap"] == 4
            assert _row(report, "Clefairy")["copies"] == 4
            assert run_tool("deck_ceilings", {"deck_id": "seed-g"}) == {"error": "deck not found"}
            assert run_tool("deck_ceilings", {"deck_id": mine["id"], "rule_preset": "nope"}).get("error")
        finally:
            reset_viewer(token)
