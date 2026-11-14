"""Printed-text checks for the Kecleon / Ditto ◇ research model."""

import csv
from pathlib import Path

from data.lab.kecleon_ditto_rainbow import (
    DECKS,
    can_almighty,
    deck_size,
    energy_symbols,
    ko_destinations,
    pays,
    whip_damage,
    whip_types,
    Game,
)
import random

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "lab" / "kecleon-ditto-rainbow"


def test_colorful_whip_counts_each_printed_type_once():
    groups = [("Fire", "Grass"), ("Fire", "Water"), ("Colorless",)]
    assert whip_types(groups) == {"Fire", "Grass", "Water", "Colorless"}
    assert whip_damage(groups) == 120


def test_eleven_types_are_330_and_a_repeated_darkness_does_not_add_a_twelfth():
    groups = [
        ("Fire", "Grass"),
        ("Fairy", "Water"),
        ("Fighting", "Metal"),
        ("Lightning", "Darkness"),
        ("Psychic", "Darkness"),
        ("Dragon",),
        ("Colorless",),
    ]
    assert len(whip_types(groups)) == 11
    assert whip_damage(groups) == 330


def test_almighty_evolution_cannot_be_used_on_the_first_turn_or_the_turn_ditto_was_played():
    assert can_almighty(1, 0) is False
    assert can_almighty(2, 2) is False
    assert can_almighty(3, 2) is True


def test_rescue_scarf_returns_the_whole_stack_only_after_attack_damage():
    stack = [{"prism": True, "name": "Ditto"}, {"prism": False, "name": "Azumarill"}]
    assert ko_destinations(stack, scarf=True, by_attack=True) == ["hand", "hand"]
    assert ko_destinations(stack, scarf=True, by_attack=False) == ["lost", "discard"]
    assert ko_destinations(stack, scarf=False, by_attack=True) == ["lost", "discard"]


def test_reversal_stays_colorless_on_a_rule_box_and_counter_does_not():
    blocked = energy_symbols("reversal", None, evolution=True, rule_box=True, gx_ex=False, behind=True)
    live = energy_symbols("reversal", None, evolution=True, rule_box=False, gx_ex=False, behind=True)
    counter = energy_symbols("counter", None, evolution=True, rule_box=True, gx_ex=False, behind=True)
    assert blocked == ["C"]
    assert live == ["A", "A", "A"]
    assert counter == ["A", "A"]
    assert pays(("C", "C"), energy_symbols("dce", None, evolution=False, rule_box=False, gx_ex=False, behind=False))
    assert energy_symbols("triple", None, evolution=False, rule_box=False, gx_ex=False, behind=False) is None


def test_each_researched_deck_is_sixty_cards_and_one_ditto():
    for name, cards in DECKS.items():
        assert deck_size(cards) == 60
        dittos = [card for card in cards if card.get("idx_name") == "ditto"]
        assert len(dittos) == 1 and dittos[0]["count"] == 1


def test_a_goldfish_game_finishes():
    game = Game(DECKS["hybrid"], going_first=False, rng=random.Random(7))
    summary = game.run(turns=8)
    assert "whip_hits" in summary
    assert summary["max_types"] <= 11


def test_dual_type_database_has_no_dragon_pair():
    path = OUT / "dual_type_pokemon.csv"
    assert path.exists()
    with path.open() as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 106
    for row in rows:
        assert "Dragon" not in (row["type_1"], row["type_2"], row["extra_types"])
    basics = list(csv.DictReader((OUT / "basic_dual_type_pokemon.csv").open()))
    assert len(basics) == 17
    assert all(row["stage"] == "Basic" for row in basics)
