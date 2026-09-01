from app.ai.tools import run_tool
from app.db import init_db


def test_simulate_match_infers_rule_c_for_carpet_e_vs_f():
    init_db()
    rec = run_tool(
        "simulate_match",
        {
            "deck_a_id": "seed-e",
            "deck_b_id": "seed-f",
            "games": 8,
            "queries": [],
            "question": "E vs F",
        },
    )
    assert rec["method"]["rules"]["pokemon_as_energy"] is False
    assert rec["learning"]["status"].get("pokemon_as_energy_per_game", 0) == 0


def test_simulate_match_keeps_rule_b_for_seed_a_vs_b():
    init_db()
    rec = run_tool(
        "simulate_match",
        {"deck_a_id": "seed-a", "deck_b_id": "seed-b", "games": 8, "queries": []},
    )
    assert rec["method"]["rules"]["pokemon_as_energy"] is True


def test_simulate_match_rule_preset_c_overrides_rule_b_decks():
    init_db()
    rec = run_tool(
        "simulate_match",
        {
            "deck_a_id": "seed-a",
            "deck_b_id": "seed-b",
            "games": 8,
            "queries": [],
            "rule_preset": "c",
        },
    )
    assert rec["method"]["rules"]["pokemon_as_energy"] is False
    assert rec["learning"]["status"].get("pokemon_as_energy_per_game", 0) == 0


def test_simulate_match_rejects_unknown_rule_preset():
    init_db()
    rec = run_tool(
        "simulate_match",
        {"deck_a_id": "seed-a", "deck_b_id": "seed-b", "games": 4, "rule_preset": "zzz"},
    )
    assert rec["error"]
    assert "rule_preset" in rec["error"]
