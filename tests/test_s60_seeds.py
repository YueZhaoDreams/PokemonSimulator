from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G30_NAMES,
    SET_M60_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
)


def test_s60_lab_lists_are_seed_decks():
    data = load_seed_payload()
    want = {
        "c60": ("seed-c60", "Set C Standard 60 (Clefairy / Mewtwo)", SET_C60_NAMES),
        "d60": ("seed-d60", "Set D Standard 60 (Charm Ogerpon)", SET_D60_NAMES),
        "m60": ("seed-m60", "Set M Standard 60 (Zero-Energy Mew ex / Baby Box)", SET_M60_NAMES),
        "s60": ("seed-s60", "Set S Standard 60 (Floragato hunter)", SET_S60_NAMES),
        "t60": ("seed-t60", "Set T Standard 60 (Dragapult ex)", SET_T60_NAMES),
        "t-meta": ("seed-t-meta", "Worlds 2026 Hedrick Dragapult", SET_T_META_NAMES),
        "t-unl": ("seed-t-unl", "Unlimited Dragapult (Pidgeot / Rotom V)", SET_T_UNL_NAMES),
        "g30": ("seed-g30", "Unlimited 60 (Ambipom Hand Fling)", SET_G30_NAMES),
    }
    rules = standard_60_rules()
    for key, (deck_id, name, names) in want.items():
        blob = data[key]
        have = [c["name"] for c in blob["cards"]]
        assert blob["id"] == deck_id
        assert blob["name"] == name
        assert blob["kind"] == "list"
        assert have == list(names)
        assert len(have) == 60
        assert default_rule_presets_for(deck_id) == ["s60"]
        assert deck_id in S60_SEED_IDS
        for card in blob["cards"]:
            assert card.get("image"), f"{deck_id} {card['name']} {card.get('catalog_id')} has no image"
        if key == "g30":
            assert copy_violations(build_g30_deck(), rules) == []
            aipom = [c for c in blob["cards"] if c["name"] == "Aipom"]
            assert len(aipom) == 4
            assert all(c.get("catalog_id") == "sv04-145" for c in aipom)
            ambipom = next(c for c in blob["cards"] if c["name"] == "Ambipom")
            assert any(a.get("name") == "Hand Fling" for a in (ambipom.get("attacks") or []))
            speed = [c for c in blob["cards"] if c["name"] == "Speed Lightning Energy"]
            assert len(speed) == 4
            assert all(c.get("catalog_id") == "swsh2-173" for c in speed)
            assert [c["name"] for c in blob["cards"]].count("Ambipom") == 4
            assert [c["name"] for c in blob["cards"]].count("Raikou V") == 1
            assert [c["name"] for c in blob["cards"]].count("Draw Energy") == 4
            assert [c["name"] for c in blob["cards"]].count("Rare Candy") == 4
            assert [c["name"] for c in blob["cards"]].count("Forest Seal Stone") == 1
            assert [c["name"] for c in blob["cards"]].count("Nest Ball") == 1
            assert [c["name"] for c in blob["cards"]].count("Porygon2") == 0
            assert [c["name"] for c in blob["cards"]].count("Sableye") == 0
        else:
            assert copy_violations(build_fallback_deck(list(names)), rules) == []


def test_s60_seed_aliases_and_prankish_c60():
    assert load_seed_deck("c60")["id"] == "seed-c60"
    assert load_seed_deck("11")["id"] == "seed-c60"
    assert load_seed_deck("seed-c60")["id"] == "seed-c60"
    assert load_seed_deck("hedrick")["id"] == "seed-t-meta"
    assert load_seed_deck("15")["id"] == "seed-t-meta"
    assert load_seed_deck("unl")["id"] == "seed-t-unl"
    c60 = load_seed_deck("c60")
    names = [c["name"] for c in c60["cards"]]
    assert names.count("Psychic Energy") == 14
    assert names.count("Telepathic Psychic Energy") == 2
    assert names.count("Energy Search") == 0
    fables = [c for c in c60["cards"] if c["name"] == "Clefable"]
    assert len(fables) == 2
    assert all(c.get("catalog_id") == "swsh2-75" for c in fables)
    assert all(any(a.get("name") == "Prankish" for a in (c.get("abilities") or [])) for c in fables)
    hedrick = load_seed_deck("t-meta")
    assert [c["name"] for c in hedrick["cards"]].count("Rare Candy") == 0
    assert [c["name"] for c in hedrick["cards"]].count("Dragapult ex") == 3
    unl = load_seed_deck("t-unl")
    assert [c["name"] for c in unl["cards"]].count("Pidgeot ex") == 2
    assert [c["name"] for c in unl["cards"]].count("Rotom V") == 1
    assert load_seed_deck("g30")["id"] == "seed-g30"
    assert load_seed_deck("gholdengo")["id"] == "seed-g30"
    g30 = load_seed_deck("g30")
    assert [c["name"] for c in g30["cards"]].count("Aipom") == 4
    assert [c["name"] for c in g30["cards"]].count("Ambipom") == 4
    assert [c["name"] for c in g30["cards"]].count("Lopunny") == 2
    assert [c["name"] for c in g30["cards"]].count("Buneary") == 3
    assert [c["name"] for c in g30["cards"]].count("Speed Lightning Energy") == 4
    assert [c["name"] for c in g30["cards"]].count("Enriching Energy") == 1
    assert [c["name"] for c in g30["cards"]].count("Raikou V") == 1
    assert [c["name"] for c in g30["cards"]].count("Forest Seal Stone") == 1
    assert [c["name"] for c in g30["cards"]].count("Nest Ball") == 1
    assert [c["name"] for c in g30["cards"]].count("Draw Energy") == 4
    assert [c["name"] for c in g30["cards"]].count("Rare Candy") == 4
    assert load_seed_deck("raikou")["id"] == "seed-g30"
    assert load_seed_deck("ambipom")["id"] == "seed-g30"
    assert load_seed_deck("lopunny")["id"] == "seed-g30"
