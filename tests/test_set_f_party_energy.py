"""Smoke tests for the Set F Party / energy lab helpers."""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from random import Random

from app.engine.game import Game, play_game
from app.engine.models import no_pokemon_energy_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_E_NAMES, build_fallback_deck

LAB = Path(__file__).resolve().parents[1] / "data/lab/set_f_party_energy.py"


def _lab():
    spec = spec_from_file_location("set_f_party_energy", LAB)
    assert spec and spec.loader
    mod = module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_app_f_names_is_a_30_with_party_clefairy():
    lab = _lab()
    assert len(lab.APP_F_NAMES) == 30
    assert lab.APP_F_NAMES.count("Clefairy") == 4
    assert lab.APP_F_NAMES.count("Starly") == 2
    assert lab.APP_F_NAMES.count("Psychic Energy") == 6
    f = build_fallback_deck(list(lab.APP_F_NAMES))
    clef = next(c for c in f if c.name == "Clefairy")
    assert any("moon-watching" in (a.name or "").lower() for a in clef.abilities)
    assert "for each of your Benched Clefairy" in (clef.abilities[0].text or "")


def test_energy_swap_keeps_thirty():
    lab = _lab()
    f = build_fallback_deck(list(lab.APP_F_NAMES))
    swapped = lab.swap_energy(f, (("Water", 12),))
    assert len(swapped) == 30
    assert sum(1 for c in swapped if c.name == "Water Energy") == 12
    cut = lab.drop_clefairy_add_energy(f)
    assert len(cut) == 30
    assert all(c.name != "Clefairy" for c in cut)


def test_carnival_does_not_fire_moon_watching_party():
    lab = _lab()
    e = build_fallback_deck(list(SET_E_NAMES))
    f = build_fallback_deck(list(lab.APP_F_NAMES))
    result = play_game(
        e,
        f,
        no_pokemon_energy_family_rules(),
        StrategySpec.from_dict("shock"),
        StrategySpec.from_dict("carnival"),
        Random(11),
    )
    assert result.events.get("moon_watching_party", 0) == 0


def test_forced_party_caps_clefairy_at_four():
    lab = _lab()
    with lab.force_clefairy_party():
        dummy = object()
        assert lab.game_mod.Game._clefairy_play_cap(dummy, dummy) == 4
        assert lab.game_mod.Game._want_storm_line(dummy, dummy, dummy, dummy) is True

    e = build_fallback_deck(list(SET_E_NAMES))
    f = build_fallback_deck(list(lab.APP_F_NAMES))
    g = Game(
        e,
        f,
        no_pokemon_energy_family_rules(),
        StrategySpec.from_dict("shock"),
        StrategySpec.from_dict("party"),
        Random(0),
    )
    assert g._clefairy_play_cap(g.players["b"]) == 0
