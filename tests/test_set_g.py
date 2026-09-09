from app.catalog import _tcgdex_low
from app.engine.effects import parse_effects
from app.engine.models import default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import SET_G_NAMES, build_fallback_deck, fallback_named


def test_set_g_is_sixty_after_staraptor_energy_swap():
    assert len(SET_G_NAMES) == 60
    names = list(SET_G_NAMES)
    assert names.count("Staravia") == 2
    assert names.count("Staraptor") == 2
    assert names.count("Drifblim") == 1
    assert names.count("Psychic Energy") == 17
    assert names.count("Darkness Energy") == 3
    assert names.count("Boomerang Energy") == 1
    assert names.count("Clefairy") == 4
    assert names.count("Ledyba") == 4
    assert names.count("Ledian") == 4
    assert names.count("Mega Clefable ex") == 0
    assert "Jacq" in names
    assert "Drayton" in names
    pile = build_fallback_deck(names)
    assert [c.name for c in pile] == names
    assert any(c.name == "Boomerang Energy" for c in pile)
    boom = next(c for c in pile if c.name == "Boomerang Energy")
    assert "discarded by an effect of an attack" in (boom.text or "").lower()


def test_set_g_seed_payload_and_s60_preset():
    data = load_seed_payload()
    g = data["g"]
    names = [c["name"] for c in g["cards"]]
    assert g["id"] == "seed-g"
    assert g["name"] == "Carpet Set G (Clefairy / Ledian 60)"
    assert g["sample"] == "set-g-carpet.jpg"
    assert g["kind"] == "list"
    assert names == list(SET_G_NAMES)
    assert len(g["cards"]) == 60
    for card in g["cards"]:
        assert card.get("image"), f"{card['name']} {card.get('catalog_id')} has no image"
        assert str(card["image"]).startswith("http")
    starly = [c for c in g["cards"] if c["name"] == "Starly"]
    assert [c["catalog_id"] for c in starly] == ["swsh9-117", "swsh9-117"]
    assert all(any(a["name"] == "Claw" for a in c["attacks"]) for c in starly)
    staravia = [c for c in g["cards"] if c["name"] == "Staravia"]
    assert [c["catalog_id"] for c in staravia] == ["swsh9-118", "sv01-149"]
    assert staravia[0]["hp"] == 90
    assert staravia[1]["hp"] == 80
    boom = next(c for c in g["cards"] if c["name"] == "Boomerang Energy")
    assert boom["catalog_id"] == "sv06-166"
    poke = next(c for c in g["cards"] if c["name"] == "Poké Ball")
    assert poke.get("image")
    mewtwo = next(c for c in g["cards"] if c["name"] == "Mewtwo")
    assert mewtwo["catalog_id"] == "sv07-059"
    assert any(a["name"] == "Super Psy Bolt" for a in mewtwo["attacks"])
    assert default_rule_presets_for("seed-g") == ["s60"]
    assert standard_60_rules().deck_size == 60
    loaded = load_seed_deck("g")
    assert loaded["id"] == "seed-g"
    assert load_seed_deck("10")["id"] == "seed-g"
    assert load_seed_deck("seed-g")["id"] == "seed-g"


def test_set_g_printings_match_carpet_attacks():
    ledian = fallback_named("Ledian")
    assert ledian.catalog_id == "sv07-003"
    assert any(a.name == "Swift" for a in ledian.attacks)
    assert ledian.abilities and ledian.abilities[0].name == "Glittering Star Pattern"
    munk = fallback_named("Munkidori")
    assert munk.abilities[0].name == "Adrena-Brain"
    assert "{D}" in (munk.abilities[0].text or "")
    boulder = fallback_named("Iron Boulder")
    assert boulder.types == ["Psychic"]
    horn = next(a for a in boulder.attacks if a.name == "Adjusted Horn")
    assert horn.text == (
        "If you don't have the same number of cards in your hand as your opponent, this attack does nothing."
    )
    assert any(e.get("kind") == "require_equal_hands" for e in horn.effects)
    assert not any(e.get("kind") == "coin_whiff" for e in horn.effects)
    assert parse_effects(horn.text) == [{"kind": "require_equal_hands"}]
    flutter = fallback_named("Flutter Mane")
    assert any(a.name == "Midnight Fluttering" for a in flutter.abilities)
    dedenne = fallback_named("Dedenne")
    flash = next(a for a in dedenne.attacks if a.name == "Dede-Flash")
    assert flash.text == (
        "If your opponent has exactly 1 Prize card remaining, this attack does 60 more damage, "
        "and your opponent's Active Pokémon is now Confused."
    )
    kinds = {e.get("kind") for e in parse_effects(flash.text)}
    assert "opponent_prize_bonus" in kinds
    confuse = next(e for e in parse_effects(flash.text) if e.get("kind") == "status")
    assert confuse.get("if_opponent_prizes") == 1
    balloon = next(a for a in fallback_named("Drifblim").attacks if a.name == "Spooky Balloon")
    assert balloon.text == "Put 2 damage counters on 1 of your opponent's Benched Pokémon."
    assert any(e.get("kind") == "bench_damage_counters" for e in parse_effects(balloon.text))
    spin = next(a for a in fallback_named("Drifloon").attacks if a.name == "Triple Spin")
    assert spin.text == "Flip 3 coins. This attack does 10 damage for each heads."
    assert parse_effects(spin.text, "10×") == [{"kind": "coin_times", "flips": 3, "per": 10}]
    assert _tcgdex_low("me03-031") == "https://assets.tcgdex.net/en/me/me03/031/low.webp"
