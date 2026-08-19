import json

from app.config import DATA_DIR
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.engine.trades import _needs, suggest_trades
from app.seed_data import SET_A_NAMES, SET_B_NAMES, SET_C_NAMES, SET_D_NAMES, SET_S_NAMES, build_fallback_deck


def test_seed_counts():
    assert len(SET_A_NAMES) == 28
    assert len(SET_B_NAMES) == 28
    assert len(SET_C_NAMES) == 28
    assert len(SET_D_NAMES) == 28
    assert len(SET_S_NAMES) == 28
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    assert sum(1 for c in a if c.name == "Dondozo") == 1
    assert any(c.name == "Tulip" for c in a)
    assert any(c.name == "Pumpkaboo" for c in a)
    assert not any(c.name == "Flittle" for c in a)
    assert not any(c.name == "Pikachu" for c in a)
    assert sum(1 for c in b if c.name == "Pikachu") == 2
    assert not any(c.name == "Tulip" for c in b)
    assert any(
        c.name == "Pikachu" and any("paralyze" in (atk.text or "").lower() for atk in c.attacks) for c in b
    )


def test_seed_decks_record_pikachu_tulip_trade():
    data = json.loads((DATA_DIR / "seed_decks.json").read_text())
    a_names = [c["name"] for c in data["a"]["cards"]]
    b_names = [c["name"] for c in data["b"]["cards"]]
    a_ids = [c["catalog_id"] for c in data["a"]["cards"]]
    b_ids = [c["catalog_id"] for c in data["b"]["cards"]]
    assert "Tulip" in a_names
    assert "Pumpkaboo" in a_names
    assert "Flittle" not in a_names
    assert "Pikachu" not in a_names
    assert a_ids.count("sv04-181") == 1
    assert "sm12-66" not in a_ids
    assert b_names.count("Pikachu") == 2
    assert "Tulip" not in b_names
    assert "sm3-40" in b_ids
    assert "sm12-66" in b_ids


def test_seed_decks_include_set_c_and_d():
    from app.seed import load_seed_payload

    data = load_seed_payload()
    c_names = [c["name"] for c in data["c"]["cards"]]
    d_names = [c["name"] for c in data["d"]["cards"]]
    s_names = [c["name"] for c in data["s"]["cards"]]
    assert "e" not in data
    assert data["c"]["id"] == "seed-c"
    assert data["d"]["id"] == "seed-d"
    assert data["s"]["id"] == "seed-s"
    assert len(c_names) == 28
    assert len(d_names) == 28
    assert len(s_names) == 28
    assert s_names.count("Sprigatito") == 4
    assert s_names.count("Floragato") == 4
    assert s_names.count("Mewtwo ex") == 3
    assert s_names.count("Maximum Belt") == 1
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
    clefairy_text = next(c["abilities"][0]["text"] for c in data["c"]["cards"] if c["name"] == "Clefairy")
    assert "for each of your Benched Clefairy" in clefairy_text
    assert "search your deck" in clefairy_text
    assert "top 6" not in clefairy_text.lower()
    from app.engine.effects import parse_ability_effects

    assert parse_ability_effects(clefairy_text)[0]["kind"] == "attach_energy_from_deck_per_benched"
    assert d_names.count("Cornerstone Mask Ogerpon ex") == 4
    assert d_names.count("Double Colorless Energy") == 4
    assert d_names.count("Fighting Energy") == 6


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
