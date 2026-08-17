from random import Random

from app.catalog import resolve_name
from app.engine.effects import parse_effects
from app.engine.game import play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def test_lucky_find_parses_item_search():
    effects = parse_effects(
        "Search your deck for up to 2 Item cards, reveal them, and put them into your hand."
    )
    assert {"kind": "search_item", "count": 2} in effects


def test_call_family_parses_up_to_two():
    effects = parse_effects(
        "Search your deck for up to 2 Basic Pokémon and put them onto your Bench. Then, shuffle your deck."
    )
    assert any(e.get("kind") == "call_family" and e.get("count") == 2 for e in effects)


def test_gimmighoul_is_call_for_family_print():
    card = resolve_name("Gimmighoul")
    assert card.catalog_id == "sv04-087"
    assert any(a.name == "Call for Family" for a in card.attacks)


def test_balls_and_energy_search_find_pokemon_under_family_rules():
    """Poké/Ultra Ball tutor aces; Energy Search may fetch a Pokémon as energy."""
    a = build_fallback_deck(
        ["Carbink", "Dondozo", "Orthworm", "Flutter Mane", "Ultra Ball", "Poké Ball"]
        + ["Hop"] * 2
        + ["Psychic Energy"] * 2
        + ["Sobble"] * 16
    )
    b = build_fallback_deck(
        ["Emolga", "Gimmighoul", "Pikachu", "Energy Search", "Electrike"]
        + ["Shauna"] * 2
        + ["Grass Energy"] * 2
        + ["Cubone"] * 19
    )
    # Force a deterministic game with tracing; just ensure effects fire somehow across seeds.
    hits = {"ball": 0, "lucky": 0, "family": 0, "energy_pkm": 0}
    for seed in range(40):
        result = play_game(
            a,
            b,
            default_family_rules(),
            StrategySpec.from_dict(
                {
                    "name": "a",
                    "prefer_damage": 0.6,
                    "protect": ["Dondozo", "Orthworm", "Flutter Mane"],
                    "attach_pokemon_as_energy": 0.9,
                }
            ),
            StrategySpec.from_dict(
                {
                    "name": "b",
                    "prefer_damage": 0.4,
                    "prefer_status": 1.0,
                    "protect": ["Pikachu"],
                    "attach_pokemon_as_energy": 0.9,
                }
            ),
            Random(seed),
            trace=True,
        )
        blob = " ".join(result.trace).lower()
        if "ball finds" in blob or "ultra ball finds" in blob:
            hits["ball"] += 1
        if "lucky find gets" in blob:
            hits["lucky"] += 1
        if "call for family" in blob:
            hits["family"] += 1
        if "energy search finds" in blob and "(as energy)" in blob:
            hits["energy_pkm"] += 1
    # Across 40 seeds these tutor lines should show up at least occasionally.
    assert hits["ball"] + hits["lucky"] >= 1
    assert hits["family"] >= 1
    assert sum(hits.values()) >= 3


def test_carbink_fallback_has_lucky_find_effect():
    card = fallback_named("Carbink")
    lucky = next(a for a in card.attacks if a.name == "Lucky Find")
    assert any(e.get("kind") == "search_item" for e in lucky.effects)
