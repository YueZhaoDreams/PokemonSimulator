from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
)


def test_s60_lab_lists_are_seed_decks():
    data = load_seed_payload()
    want = {
        "c60": ("seed-c60", "Set C Standard 60 (Clefairy / Mewtwo)", SET_C60_NAMES),
        "d60": ("seed-d60", "Set D Standard 60 (Charm Ogerpon)", SET_D60_NAMES),
        "s60": ("seed-s60", "Set S Standard 60 (Floragato hunter)", SET_S60_NAMES),
        "t60": ("seed-t60", "Set T Standard 60 (Dragapult ex)", SET_T60_NAMES),
        "t-meta": ("seed-t-meta", "Worlds 2026 Hedrick Dragapult", SET_T_META_NAMES),
        "t-unl": ("seed-t-unl", "Unlimited Dragapult (Pidgeot / Rotom V)", SET_T_UNL_NAMES),
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
    assert names.count("Psychic Energy") == 15
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
