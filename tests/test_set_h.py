from app.engine.legality import copy_violations
from app.engine.models import default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import SET_H_NAMES, build_fallback_deck


def test_set_h_is_sixty_zapdos_pikachu_carpet():
    assert len(SET_H_NAMES) == 60
    names = list(SET_H_NAMES)
    assert names.count("Zapdos") == 4
    assert names.count("Pikachu") == 4
    assert names.count("Helioptile") == 2
    assert names.count("Grookey") == 2
    assert names.count("Zekrom") == 2
    assert names.count("Lightning Energy") == 22
    assert names.count("Double Colorless Energy") == 1
    assert "Wattrel" in names
    assert "Raichu" in names
    assert "Jolteon" in names
    assert "Tynamo" in names
    assert "Surfer" in names
    assert "Iris's Fighting Spirit" in names
    assert "Hisuian Electrode" in names
    assert "Lechonk" in names
    pile = build_fallback_deck(names)
    assert [c.name for c in pile] == names
    assert copy_violations(pile, standard_60_rules()) == []


def test_set_h_seed_payload_and_s60_preset():
    data = load_seed_payload()
    h = data["h"]
    names = [c["name"] for c in h["cards"]]
    assert h["id"] == "seed-h"
    assert h["name"] == "Carpet Set H (Zapdos / Pikachu 60)"
    assert h["sample"] == "set-h-carpet.jpg"
    assert h["kind"] == "list"
    assert names == list(SET_H_NAMES)
    assert len(h["cards"]) == 60
    for card in h["cards"]:
        assert card.get("image"), f"{card['name']} {card.get('catalog_id')} has no image"
        assert str(card["image"]).startswith("http")
    zapdos = [c for c in h["cards"] if c["name"] == "Zapdos"]
    assert all(c.get("catalog_id") == "xy6-23" for c in zapdos)
    wattrel = next(c for c in h["cards"] if c["name"] == "Wattrel")
    assert wattrel["catalog_id"] == "sv01-077"
    jolteon = next(c for c in h["cards"] if c["name"] == "Jolteon")
    assert jolteon["catalog_id"] == "sv08.5-029"
    heli = [c for c in h["cards"] if c["name"] == "Helioptile"]
    assert all(c.get("catalog_id") == "xy2-36" for c in heli)
    dce = next(c for c in h["cards"] if c["name"] == "Double Colorless Energy")
    assert dce.get("image")
    assert default_rule_presets_for("seed-h") == ["s60"]
    assert load_seed_deck("h")["id"] == "seed-h"
    assert load_seed_deck("17")["id"] == "seed-h"
    assert load_seed_deck("seed-h")["id"] == "seed-h"
