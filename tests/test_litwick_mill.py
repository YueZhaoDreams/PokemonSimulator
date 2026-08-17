from random import Random

from app.catalog import fetch_full, normalize_card, resolve_name
from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named


def test_kindling_panic_parses_mill():
    effects = parse_effects("Discard the top card of your opponent's deck.")
    assert {"kind": "mill_opponent", "count": 1} in effects


def test_litwick_preferred_print_is_mill():
    card = resolve_name("Litwick", ["kindling panic", "discard the top"])
    if "Kindling Panic" not in [a.name for a in card.attacks]:
        card = normalize_card(fetch_full("swsh11-024"))
    assert card.catalog_id == "swsh11-024"
    assert any(a.name == "Kindling Panic" for a in card.attacks)


def test_mill_discards_opponent_deck_top():
    lit = fallback_named("Litwick")
    assert any(e.get("kind") == "mill_opponent" for a in lit.attacks for e in a.effects)
    a = build_fallback_deck(["Dondozo"] + ["Sobble"] * 27)
    b = build_fallback_deck(["Litwick", "Slugma"] + ["Hop"] * 4 + ["Cubone"] * 22)
    game = Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict({"name": "mill", "prefer_damage": 0.2, "protect": ["Litwick"], "attach_pokemon_as_energy": 1.0}),
        Random(1),
        trace=True,
    )
    me = game.players["b"]
    foe = game.players["a"]
    lit_i = next(i for i, c in enumerate(me.cards) if c.name == "Litwick")
    fuel_i = next(i for i, c in enumerate(me.cards) if c.name == "Slugma")
    me.active = Pokemon(card_i=lit_i, energy=[fuel_i])
    before = len(foe.deck)
    assert before > 0
    game.current = "b"
    game._attack(me, foe, "b")
    assert len(foe.deck) == before - 1
    assert game.events.get("mill_opponent", 0) >= 1
