from random import Random

from app.catalog import fetch_full, normalize_card
from app.engine.effects import parse_effects
from app.engine.game import Game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def test_wonder_storm_parses_psychic_energy_times():
    effects = parse_effects(
        "This attack does 20 damage for each Psychic Energy attached to all of your Pokémon.",
        "20×",
    )
    assert {"kind": "psychic_energy_times", "per": 20} in effects


def test_wonder_storm_counts_psychic_pokemon_as_energy():
    """Family Cup: Psychic Pokémon attached as energy count toward Wonder Storm."""
    a = build_fallback_deck(
        ["Clefairy", "Pumpkaboo", "Kadabra", "Dusclops", "Flutter Mane", "Psychic Energy"] + ["Sobble"] * 22
    )
    b = build_fallback_deck(["Pikachu"] + ["Cubone"] * 27)
    game = Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("control"),
        Random(1),
        trace=True,
    )
    me = game.players["a"]
    # Put Clefairy active with 3 energy slots filled by Psychic Energy + Psychic Pokémon-as-energy.
    clef_i = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fuel = [i for i, c in enumerate(me.cards) if c.name in {"Psychic Energy", "Pumpkaboo", "Kadabra", "Dusclops"}][:4]
    from app.engine.game import Pokemon

    me.active = Pokemon(card_i=clef_i, energy=list(fuel))
    me.hand = []
    me.bench = []
    count = game._count_psychic_energy_in_play(me)
    assert count >= 4
    # Damage should be 20 × count (80–100 range when well fueled).
    assert 20 * count >= 80


def test_two_carpet_pikachu_prints_differ():
    nuzzle = normalize_card(fetch_full("sm12-66"))
    shock = normalize_card(fetch_full("sm3-40"))
    assert [a.name for a in nuzzle.attacks] == ["Nuzzle", "Volt Tackle"]
    assert [a.name for a in shock.attacks] == ["Tail Whap", "Thunder Shock"]


def test_clefairy_fallback_has_scaling_effect():
    card = fallback_named("Clefairy")
    assert any(e.get("kind") == "psychic_energy_times" for a in card.attacks for e in a.effects)
