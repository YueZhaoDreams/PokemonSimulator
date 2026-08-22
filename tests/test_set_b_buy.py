import importlib.util
from pathlib import Path

from app.seed_data import SET_B_NAMES, build_fallback_deck, fallback_named


def _load_lab(filename: str):
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / filename
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_set_b_buy_swap_keeps_thirty_cards():
    mod = _load_lab("set_b_buy_sim.py")
    deck = build_fallback_deck(SET_B_NAMES)
    assert len(deck) == 30
    out = mod.replace(deck, "Crocalor", fallback_named("Lightning Energy"))
    assert len(out) == 30
    assert sum(1 for card in out if card.name == "Crocalor") == 0
    assert sum(1 for card in out if card.name == "Lightning Energy") == 2


def test_set_b_confirm_swap_keeps_thirty_cards():
    mod = _load_lab("set_b_buy_confirm.py")
    deck = build_fallback_deck(SET_B_NAMES)
    out = mod.replace(deck, "Crocalor", fallback_named("Poké Ball"))
    assert len(out) == 30
    assert any(card.name == "Poké Ball" for card in out)
