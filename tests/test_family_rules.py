from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.engine.trades import _needs, suggest_trades
from app.seed_data import SET_A_NAMES, SET_B_NAMES, SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, SET_T_NAMES, SET_SPARE_NAMES, build_fallback_deck


def test_seed_counts():
    assert len(SET_A_NAMES) == 30
    assert len(SET_B_NAMES) == 30
    assert len(SET_C_NAMES) == 30
    assert len(SET_D_NAMES) == 30
    assert len(SET_S_NAMES) == 30
    assert len(SET_T_NAMES) == 30
    assert len(SET_SPARE_NAMES) == 4
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    assert sum(1 for c in a if c.name == "Dondozo") == 1
    assert any(c.name == "Tulip" for c in a)
    assert any(c.name == "Staraptor" for c in a)
    assert any(c.name == "Starly" for c in a)
    assert any(c.name == "Boomerang Energy" for c in a)
    assert any(c.name == "Aipom" for c in a)
    assert not any(c.name == "Flittle" for c in a)
    assert not any(c.name == "Pikachu" for c in a)
    assert not any(c.name == "Clefairy" for c in a)
    assert not any(c.name == "Pumpkaboo" for c in a)
    assert not any(c.name == "Trekking Shoes" for c in a)
    assert sum(1 for c in a if c.name == "Water Energy") == 1
    assert sum(1 for c in a if c.name == "Metal Energy") == 1
    assert sum(1 for c in a if c.name == "Psychic Energy") == 2
    assert not any(c.name == "Tool Box" for c in a)
    assert sum(1 for c in b if c.name == "Pikachu") == 2
    assert sum(1 for c in b if c.name == "Lightning Energy") == 4
    assert sum(1 for c in b if c.name == "Grass Energy") == 3
    assert sum(1 for c in b if c.name == "Water Energy") == 2
    assert any(c.name == "Walrein" for c in b)
    assert any(c.name == "Spheal" for c in b)
    assert any(c.name == "Sealeo" for c in b)
    assert any(c.name == "Trekking Shoes" for c in b)
    assert not any(c.name == "Fire Energy" for c in b)
    assert not any(c.name == "Darkness Energy" for c in b)
    assert not any(c.name == "Spinarak" for c in b)
    assert not any(c.name == "Gimmighoul" for c in b)
    assert not any(c.name == "Lickilicky" for c in b)
    assert any(c.name == "Aipom" for c in a)
    assert not any(c.name == "Aipom" for c in b)
    assert not any(c.name == "Clefairy" for c in b)
    assert not any(c.name == "Tulip" for c in b)
    assert any(
        c.name == "Pikachu" and any("paralyze" in (atk.text or "").lower() for atk in c.attacks) for c in b
    )


def test_seed_decks_record_pikachu_tulip_trade():
    from app.seed import load_seed_payload

    data = load_seed_payload()
    a_names = [c["name"] for c in data["a"]["cards"]]
    b_names = [c["name"] for c in data["b"]["cards"]]
    a_ids = [c["catalog_id"] for c in data["a"]["cards"]]
    b_ids = [c["catalog_id"] for c in data["b"]["cards"]]
    assert len(a_names) == 30
    assert len(b_names) == 30
    assert "Tulip" in a_names
    assert "Staraptor" in a_names
    assert "Boomerang Energy" in a_names
    assert "Aipom" in a_names
    assert "Pumpkaboo" not in a_names
    assert "Flittle" not in a_names
    assert "Pikachu" not in a_names
    assert "Tool Box" not in a_names
    assert "Clefairy" not in a_names
    assert "Trekking Shoes" not in a_names
    assert a_names.count("Water Energy") == 1
    assert a_names.count("Metal Energy") == 1
    assert a_names.count("Psychic Energy") == 2
    assert a_ids.count("sv04-181") == 1
    assert "sm12-66" not in a_ids
    assert b_names.count("Pikachu") == 2
    assert b_names.count("Lightning Energy") == 4
    assert b_names.count("Grass Energy") == 3
    assert b_names.count("Water Energy") == 2
    assert "Walrein" in b_names
    assert "Spheal" in b_names
    assert "Trekking Shoes" in b_names
    assert "Fire Energy" not in b_names
    assert "Darkness Energy" not in b_names
    assert "Spinarak" not in b_names
    assert "Gimmighoul" not in b_names
    assert "Lickilicky" not in b_names
    assert "Aipom" not in b_names
    assert "Clefairy" not in b_names
    assert "Tulip" not in b_names
    assert "sm3-40" in b_ids
    assert "sm12-66" in b_ids


def test_seed_decks_have_images():
    from app.seed import load_seed_payload

    data = load_seed_payload()
    for key in ("a", "b", "c", "d", "s", "t", "spare"):
        for card in data[key]["cards"]:
            assert card.get("image"), f"{key} {card['name']} {card.get('catalog_id')} has no image"
            assert str(card["image"]).startswith("http")
    flora = next(c for c in data["s"]["cards"] if c["name"] == "Floragato")
    assert any(a["name"] == "Slashing Claw" for a in flora["attacks"])
    assert flora["catalog_id"] == "sv01-014"


def test_seed_decks_include_set_c_and_d():
    from app.seed import load_seed_payload

    data = load_seed_payload()
    c_names = [c["name"] for c in data["c"]["cards"]]
    d_names = [c["name"] for c in data["d"]["cards"]]
    s_names = [c["name"] for c in data["s"]["cards"]]
    t_names = [c["name"] for c in data["t"]["cards"]]
    assert "e" not in data
    assert data["c"]["id"] == "seed-c"
    assert data["d"]["id"] == "seed-d"
    assert data["s"]["id"] == "seed-s"
    assert data["t"]["id"] == "seed-t"
    assert data["t"]["name"] == "Set T (Dragapult ex)"
    assert data["spare"]["id"] == "seed-spare"
    assert data["spare"]["kind"] == "spare"
    assert data["spare"]["name"] == "Spare Cards"
    spare_names = [c["name"] for c in data["spare"]["cards"]]
    assert spare_names == ["Tool Box", "Lickilicky", "Fighting Energy", "Gimmighoul"]
    assert len(c_names) == 30
    assert len(d_names) == 30
    assert len(s_names) == 30
    assert s_names.count("Sprigatito") == 4
    assert s_names.count("Floragato") == 4
    assert s_names.count("Wo-Chien ex") == 3
    assert s_names.count("Mewtwo ex") == 0
    assert s_names.count("Maximum Belt") == 1
    assert s_names.count("Switch") == 3
    assert s_names.count("Muscle Band") == 0
    assert s_names.count("Grass Energy") == 2
    assert len(t_names) == 30
    assert t_names.count("Dreepy") == 2
    assert t_names.count("Drakloak") == 2
    assert t_names.count("Dragapult ex") == 2
    assert t_names.count("Fezandipiti ex") == 1
    assert t_names.count("Budew") == 1
    assert t_names.count("Unfair Stamp") == 1
    assert t_names.count("Psychic Energy") == 2
    assert t_names.count("Fire Energy") == 2
    assert t_names.count("Darkness Energy") == 1
    assert c_names.count("Clefairy") == 4
    assert c_names.count("Mewtwo ex") == 2
    assert c_names.count("Hop") == 3
    assert c_names.count("Nest Ball") == 2
    assert c_names.count("Energy Search") == 3
    assert c_names.count("Switch") == 0
    assert c_names.count("Buddy-Buddy Poffin") == 0
    assert c_names.count("Beach Court") == 0
    assert c_names.count("Maximum Belt") == 1
    assert c_names.count("Tool Box") == 1
    assert c_names.count("Arven") == 1
    assert c_names.count("Psychic Energy") == 2
    clefairy_text = next(c["abilities"][0]["text"] for c in data["c"]["cards"] if c["name"] == "Clefairy")
    assert "for each of your Benched Clefairy" in clefairy_text
    assert "search your deck" in clefairy_text
    assert "top 6" not in clefairy_text.lower()
    from app.engine.effects import parse_ability_effects

    assert parse_ability_effects(clefairy_text)[0]["kind"] == "attach_energy_from_deck_per_benched"
    assert d_names.count("Cornerstone Mask Ogerpon ex") == 4
    assert d_names.count("Double Colorless Energy") == 4
    assert d_names.count("Fighting Energy") == 8


def test_set_b_has_orphan_evolutions():
    b = build_fallback_deck(SET_B_NAMES)
    needs = _needs(b)
    assert "evolution_basic" in needs


def test_trade_suggestions_run():
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    rec = suggest_trades(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("control"),
        games=40,
        seed=2,
    )
    assert "recommendations" in rec
    assert rec["method"]
