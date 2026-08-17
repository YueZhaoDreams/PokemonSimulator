from app.engine.models import Card
from app.engine.trades import _needs, suggest_trades
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_A_NAMES, SET_B_NAMES, build_fallback_deck


def test_seed_counts():
    assert len(SET_A_NAMES) == 28
    assert len(SET_B_NAMES) == 28
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    assert sum(1 for c in a if c.name == "Dondozo") == 1
    assert any(c.name == "Pikachu" and any("paralyze" in (atk.text or "").lower() for atk in c.attacks) for c in b)


def test_set_b_has_orphan_evolutions():
    b = build_fallback_deck(SET_B_NAMES)
    needs = _needs(b)
    assert "evolution_basic" in needs


def test_trade_suggestions_run():
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    rec = suggest_trades(a, b, default_family_rules(), StrategySpec.from_dict("balanced"), StrategySpec.from_dict("control"), games=40, seed=2)
    assert "recommendations" in rec
    assert rec["method"]
