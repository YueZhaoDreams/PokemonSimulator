"""Elekid (Paradox Rift 59) as printed, and a "1 of your opponent's Pokémon" sentence is one hit."""

from __future__ import annotations

from app.engine.effects import parse_effects
from app.seed_data import fallback_named

CRACKLING_SHOT = (
    "This attack does 30 damage to 1 of your opponent's Pokémon. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)


def test_elekid_prints_thirty_hp_free_snipe():
    card = fallback_named("Elekid")
    assert (card.stage, card.hp, card.types, card.retreat) == ("Basic", 30, ["Lightning"], 0)
    assert [(w["type"], w["value"]) for w in card.weaknesses] == [("Fighting", "×2")]
    assert (card.set_name, card.catalog_id) == ("Paradox Rift", "sv04-059")
    (atk,) = card.attacks
    assert (atk.name, atk.cost, atk.damage, atk.text) == ("Crackling Shot", [], 0, CRACKLING_SHOT)
    assert atk.effects == [{"kind": "damage_one_pokemon", "amount": 30}]


def test_one_pokemon_sentence_is_one_hit_not_two():
    effects = parse_effects(CRACKLING_SHOT)
    assert [e["kind"] for e in effects].count("damage_one_pokemon") == 1
    assert "damage_n_opponent_pokemon" not in {e["kind"] for e in effects}
    cruel_arrow = fallback_named("Fezandipiti ex").attacks[0]
    kinds = [e["kind"] for e in cruel_arrow.effects]
    assert kinds.count("damage_one_pokemon") == 1 and "damage_n_opponent_pokemon" not in kinds


def test_three_pokemon_sentence_still_spreads():
    effects = parse_effects("This attack does 20 damage to 3 of your opponent's Pokémon.")
    spread = [e for e in effects if e["kind"] == "damage_n_opponent_pokemon"]
    assert [(e["amount"], e["count"]) for e in spread] == [(20, 3)]
    assert "damage_one_pokemon" not in {e["kind"] for e in effects}
