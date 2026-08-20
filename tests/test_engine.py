from random import Random

from app.engine.effects import can_pay_energy
from app.engine.game import ST_PARALYZED, play_game
from app.engine.models import default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def test_pokemon_pays_as_matching_energy():
    water = fallback_named("Sobble")
    assert water.as_energy_type == "Water"
    assert can_pay_energy(["Water", "Water", "Colorless", "Colorless"], ["Water", "Water", "Colorless", "Colorless"])
    assert not can_pay_energy(["Fire", "Fire"], ["Water", "Water"])


def test_family_rules_defaults():
    rules = default_family_rules()
    assert rules.deck_size == 30
    assert rules.prize_count == 3
    assert rules.pokemon_as_energy is True
    assert rules.opening_hand == 7


def test_one_game_completes():
    a = build_fallback_deck(["Dondozo", "Sobble", "Marill", "Pikachu"] + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Litten"] * 16)
    b = build_fallback_deck(["Pikachu", "Electrike", "Wailmer"] + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 17)
    result = play_game(a, b, default_family_rules(), StrategySpec.from_dict("balanced"), StrategySpec.from_dict("control"), Random(1), trace=True)
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1
    assert len(result.opening_a) == 7
    assert len(result.prized_a) == 3


def test_paralysis_blocks_attack_flag():
    assert ST_PARALYZED == 1


def test_small_monte_carlo():
    a = build_fallback_deck(["Dondozo"] + ["Sobble"] * 10 + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Litten"] * 9)
    b = build_fallback_deck(["Pikachu"] + ["Electrike"] * 10 + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 9)
    record = run_simulation(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("control"),
        games=40,
        seed=3,
        question="Can Pikachu paralyze Dondozo?",
    )
    assert record["results"]["wins_a"] + record["results"]["wins_b"] + record["results"]["ties"] == 40
    assert "insights" in record["learning"]
    assert record["method"]["games"] == 40
