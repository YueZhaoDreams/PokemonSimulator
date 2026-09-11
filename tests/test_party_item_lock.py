from app.engine.effects import parse_effects
from app.seed_data import SET_C60_NAMES, fallback_named


def test_itchy_pollen_locks_items_not_supporters():
    effects = parse_effects(
        "During your opponent's next turn, they can't play any Item cards from their hand."
    )
    assert {"kind": "lock_items"} in effects
    assert not any(e.get("kind") == "lock_trainers" for e in effects)
    pollen = next(a for a in fallback_named("Budew").attacks if a.name == "Itchy Pollen")
    assert pollen.cost == []
    assert pollen.damage == 10


def test_c60_locked_list_has_no_budew():
    assert "Budew" not in SET_C60_NAMES
    assert list(SET_C60_NAMES).count("Psychic Energy") == 15
