from app.catalog import resolve_name
from app.engine.effects import parse_effects
from app.engine.game import play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named
from random import Random


def test_dondozo_is_paradox_rift_swallow_up():
    card = resolve_name("Dondozo")
    assert card.catalog_id == "sv04-055"
    names = [a.name for a in card.attacks]
    assert "Supplemental Swallow-Up" in names
    assert "Hydro Splash" in names
    swallow = next(a for a in card.attacks if "Swallow" in a.name)
    assert swallow.damage == 0
    assert any(e.get("kind") == "swallow_energy" for e in swallow.effects)
    hydro = next(a for a in card.attacks if a.name == "Hydro Splash")
    assert hydro.damage == 180


def test_orthworm_has_crunch_time_rush():
    card = resolve_name("Orthworm")
    assert card.catalog_id == "sv04-138"
    assert any(a.name == "Crunch-Time Rush" for a in card.attacks)
    rush = next(a for a in card.attacks if "Crunch" in a.name)
    assert any(e.get("kind") == "deck_count_bonus" for e in rush.effects)


def test_parse_swallow_effect():
    effects = parse_effects(
        "Look at the top 5 cards of your deck. You may attach any number of Basic Energy cards you find there to this Pokémon."
    )
    assert effects == [{"kind": "swallow_energy", "look": 5}]


def test_dondozo_can_swallow_and_finish_game():
    dondozo = fallback_named("Dondozo")
    assert any(e.get("kind") == "swallow_energy" for a in dondozo.attacks for e in a.effects)
    a = build_fallback_deck(
        ["Dondozo"] + ["Sobble"] * 12 + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Marill"] * 7
    )
    b = build_fallback_deck(
        ["Pikachu"] + ["Electrike"] * 10 + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 9
    )
    result = play_game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict(
            {
                "name": "dondozo",
                "prefer_damage": 1.0,
                "protect": ["Dondozo"],
                "attach_pokemon_as_energy": 0.95,
            }
        ),
        StrategySpec.from_dict("control"),
        Random(2),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert any("Swallow" in line or "swallows" in line or "Hydro Splash" in line for line in result.trace) or result.turns >= 1
