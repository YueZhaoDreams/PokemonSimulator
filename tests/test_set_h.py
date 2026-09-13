from app.engine.legality import copy_violations
from app.engine.models import default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import SET_H_NAMES, build_fallback_deck

_ABSENT = (
    "Helioptile",
    "Grookey",
    "Tynamo",
    "Eelektrik",
    "Magby",
    "Houndour",
    "Cramorant",
    "Treecko",
    "Dubwool",
    "Togedemaru",
    "Hisuian Electrode",
    "Electrode",
    "Trapinch",
    "Gogoat",
    "Drifloon",
    "Zapdos",
)


def test_set_h_is_sixty_team_rocket_zapdos_carpet():
    assert len(SET_H_NAMES) == 60
    names = list(SET_H_NAMES)
    assert names.count("Team Rocket's Zapdos") == 4
    assert names.count("Pikachu") == 2
    assert names.count("Zekrom") == 1
    assert names.count("Plusle") == 2
    assert names.count("Zoroark") == 3
    assert names.count("Lightning Energy") == 25
    assert names.count("Double Colorless Energy") == 1
    assert "Wattrel" in names
    assert "Raichu" in names
    assert "Jolteon" in names
    assert "Ledyba" in names
    assert "Ledian" in names
    assert "Minun" in names
    assert "Kecleon" in names
    assert "Hisuian Voltorb" in names
    assert "Drifblim" in names
    assert "Surfer" in names
    assert "Iris's Fighting Spirit" in names
    assert "Lechonk" in names
    for missing in _ABSENT:
        assert missing not in names
    pile = build_fallback_deck(names)
    assert [c.name for c in pile] == names
    assert copy_violations(pile, standard_60_rules()) == []
    zapdos = next(c for c in pile if c.name == "Team Rocket's Zapdos")
    assert [a.name for a in zapdos.attacks] == ["Jamming Wing", "Wicked Thunder"]
    zekrom = next(c for c in pile if c.name == "Zekrom")
    assert zekrom.image
    assert [a.name for a in zekrom.attacks] == ["Crushing Short", "Raging Thunder"]


def test_set_h_seed_payload_and_s60_preset():
    data = load_seed_payload()
    h = data["h"]
    names = [c["name"] for c in h["cards"]]
    assert h["id"] == "seed-h"
    assert h["name"] == "Carpet Set H (Team Rocket's Zapdos / Pikachu 60)"
    assert h["sample"] == "set-h-carpet.jpg"
    assert h["kind"] == "list"
    assert names == list(SET_H_NAMES)
    assert len(h["cards"]) == 60
    for card in h["cards"]:
        assert card.get("image"), f"{card['name']} {card.get('catalog_id')} has no image"
        assert str(card["image"]).startswith("http")
    zapdos = [c for c in h["cards"] if c["name"] == "Team Rocket's Zapdos"]
    assert all(c.get("catalog_id") == "sv10-070" for c in zapdos)
    assert all(c.get("image") for c in zapdos)
    assert "Jamming Wing" in [a["name"] for a in zapdos[0]["attacks"]]
    pikachu = [c for c in h["cards"] if c["name"] == "Pikachu"]
    assert [c.get("catalog_id") for c in pikachu] == ["sm12-66", "sm3-40"]
    zekrom = next(c for c in h["cards"] if c["name"] == "Zekrom")
    assert zekrom["catalog_id"] == "sv04-066"
    assert zekrom.get("image")
    assert zekrom["hp"] == 130
    wattrel = next(c for c in h["cards"] if c["name"] == "Wattrel")
    assert wattrel["catalog_id"] == "sv01-077"
    jolteon = next(c for c in h["cards"] if c["name"] == "Jolteon")
    assert jolteon["catalog_id"] == "sv08.5-029"
    dce = next(c for c in h["cards"] if c["name"] == "Double Colorless Energy")
    assert dce.get("image")
    assert default_rule_presets_for("seed-h") == ["s60"]
    assert load_seed_deck("h")["id"] == "seed-h"
    assert load_seed_deck("17")["id"] == "seed-h"
    assert load_seed_deck("seed-h")["id"] == "seed-h"
