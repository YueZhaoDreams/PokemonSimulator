from app.catalog import energy_card, lookup_seed_card, resolve_name
from app.db import _deck_kind
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import SET_SPARE_NAMES, build_fallback_deck, fallback_named


def test_spare_is_a_leftover_pile_not_a_thirty():
    assert SET_SPARE_NAMES == [
        "Tool Box",
        "Lickilicky",
        "Fighting Energy",
        "Gimmighoul",
    ]
    assert len(SET_SPARE_NAMES) == 4
    pile = build_fallback_deck(list(SET_SPARE_NAMES))
    assert [c.name for c in pile] == SET_SPARE_NAMES
    assert pile[0].category == "Trainer"
    assert pile[1].name == "Lickilicky"
    assert pile[2].energy_type == "Fighting"


def test_gimmighoul_household_print_has_paradox_rift_art():
    """Resolve/add uses lookup_seed_card; missing fallback art left Set E tiles blank."""
    card = fallback_named("Gimmighoul")
    assert card.catalog_id == "sv04-087"
    assert card.image
    assert "sv04/087" in card.image
    seed = lookup_seed_card(catalog_id="sv04-087")
    assert seed is not None
    assert seed.name == "Gimmighoul"
    assert seed.image
    assert "sv04/087" in seed.image


def test_orthworm_household_print_has_paradox_rift_art():
    """Replace/resolve used lookup_seed_card; Orthworm had catalog_id but no fallback art."""
    card = fallback_named("Orthworm")
    assert card.catalog_id == "sv04-138"
    assert card.image
    assert "sv04/138" in card.image
    seed = lookup_seed_card(catalog_id="sv04-138")
    assert seed is not None
    assert seed.name == "Orthworm"
    assert seed.image
    assert "sv04/138" in seed.image


def test_dark_energy_alias_is_darkness():
    card = resolve_name("Dark Energy")
    assert card.name == "Darkness Energy"
    assert card.energy_type == "Darkness"
    assert energy_card("Darkness").catalog_id == "swsh12.5-158"


def test_seed_payload_includes_spare_cards():
    data = load_seed_payload()
    spare = data["spare"]
    names = [c["name"] for c in spare["cards"]]
    assert spare["id"] == "seed-spare"
    assert spare["kind"] == "spare"
    assert spare["name"] == "Spare Cards"
    assert names == list(SET_SPARE_NAMES)
    for card in spare["cards"]:
        assert card.get("image"), f"{card['name']} {card.get('catalog_id')} has no image"
        assert str(card["image"]).startswith("http")
    loaded = load_seed_deck("spare")
    assert loaded["id"] == "seed-spare"
    assert load_seed_deck("seed-spare")["id"] == "seed-spare"
    assert load_seed_deck("6")["id"] == "seed-spare"
    assert _deck_kind("seed-spare") == "spare"
    assert _deck_kind("seed-c") == "list"
