"""Bench shields vs Dragapult Phantom Dive (printed text wins).

Layers (damage vs counters are different):
- Manaphy Wave Veil: bench damage only, all bench. Does NOT stop Dive counters.
- Shaymin Flower Curtain: bench damage only, non-Rule-Box bench. Does NOT stop counters.
- Rabsca Spherical Shield: bench damage AND attack effects. Stops Dive counters, not Abilities.
- Battle Cage: both benches ignore counter placement from opp attack/ability effects.
  Damage from attacks is still taken.
"""

from random import Random

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
    c60_names_before_bounce,
    fallback_named,
)

# Exact printed wording (curly apostrophes as on the cards).
RABSCA_PRINTED = "Prevent all damage from and effects of attacks from your opponent\u2019s Pok\u00e9mon done to your Benched Pok\u00e9mon."
SHAYMIN_PRINTED = "Prevent all damage done to your Benched Pok\u00e9mon that don\u2019t have a Rule Box by attacks from your opponent\u2019s Pok\u00e9mon. (Pok\u00e9mon ex, Pok\u00e9mon V, etc. have Rule Boxes.)"
CAGE_PRINTED = "Prevent all damage counters from being placed on Benched Pok\u00e9mon (both yours and your opponent\u2019s) by effects of attacks and Abilities from the opponent\u2019s Pok\u00e9mon. (Damage from attacks is still taken.)"
MANAPHY_PRINTED = "Prevent all damage done to your Benched Pok\u00e9mon by attacks from your opponent\u2019s Pok\u00e9mon."


def _game(deck_a_extra=None, deck_b_names=None):
    a = build_fallback_deck(list(SET_C60_NAMES) + list(deck_a_extra or []))
    b = build_fallback_deck(list(deck_b_names or SET_T60_NAMES))
    return Game(
        a,
        b,
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(3),
    )


def _idx(player, name):
    return next(i for i, c in enumerate(player.cards) if c.name == name)


def test_rabsca_parses_damage_and_attack_effects():
    effs = parse_ability_effects(RABSCA_PRINTED)
    assert {"kind": "prevent_bench_damage_and_attack_effects"} in effs
    card = fallback_named("Rabsca")
    assert parse_ability_effects(card.abilities[0].text)[0]["kind"] == "prevent_bench_damage_and_attack_effects"


def test_shaymin_parses_no_rulebox_damage_only():
    effs = parse_ability_effects(SHAYMIN_PRINTED)
    assert {"kind": "prevent_bench_attack_damage_no_rulebox"} in effs
    card = fallback_named("Shaymin")
    assert parse_ability_effects(card.abilities[0].text)[0]["kind"] == "prevent_bench_attack_damage_no_rulebox"


def test_battle_cage_parses_counter_prevention():
    effs = parse_ability_effects(CAGE_PRINTED)
    assert effs[0]["kind"] == "stadium_prevent_bench_counters"
    assert effs[0]["both_benches"] is True
    card = fallback_named("Battle Cage")
    assert parse_ability_effects(card.text)[0]["kind"] == "stadium_prevent_bench_counters"


def test_manaphy_still_parses_damage_only():
    assert parse_ability_effects(MANAPHY_PRINTED)[0]["kind"] == "prevent_bench_attack_damage"


def test_shield_cards_registered():
    rellor = fallback_named("Rellor")
    assert (rellor.hp, rellor.stage, rellor.types) == (50, "Basic", ["Grass"])
    rabsca = fallback_named("Rabsca")
    assert (rabsca.hp, rabsca.evolves_from) == (70, "Rellor")
    assert rabsca.abilities[0].name == "Spherical Shield"
    shaymin = fallback_named("Shaymin")
    assert (shaymin.hp, shaymin.stage) == (80, "Basic")
    assert shaymin.abilities[0].name == "Flower Curtain"
    cage = fallback_named("Battle Cage")
    assert cage.trainer_kind == "stadium"


def test_wave_veil_does_not_block_dive_counters():
    game = _game()
    foe = game.players["a"]
    mana = fallback_named("Manaphy")
    foe.cards.append(mana)
    mana_i = len(foe.cards) - 1
    foe.active = Pokemon(card_i=_idx(foe, "Mewtwo ex"), played_turn=0)
    foe.bench = [
        Pokemon(card_i=mana_i, played_turn=0),
        Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0),
    ]
    game._bench_damage_counters(foe, 6)
    assert foe.bench[1].damage == 60


def test_shaymin_does_not_block_dive_counters():
    game = _game(deck_a_extra=["Shaymin"])
    foe = game.players["a"]
    foe.active = Pokemon(card_i=_idx(foe, "Mewtwo ex"), played_turn=0)
    foe.bench = [
        Pokemon(card_i=_idx(foe, "Shaymin"), played_turn=0),
        Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0),
    ]
    game._bench_damage_counters(foe, 6)
    assert foe.bench[1].damage == 60
    assert game.events.get("spherical_shield") is None
    assert game.events.get("battle_cage") is None


def test_rabsca_blocks_dive_counters():
    game = _game(deck_a_extra=["Rabsca"])
    foe = game.players["a"]
    foe.active = Pokemon(card_i=_idx(foe, "Mewtwo ex"), played_turn=0)
    foe.bench = [
        Pokemon(card_i=_idx(foe, "Rabsca"), played_turn=0),
        Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0),
    ]
    game._bench_damage_counters(foe, 6)
    assert foe.bench[0].damage == 0
    assert foe.bench[1].damage == 0
    assert game.events.get("spherical_shield") == 1


def test_battle_cage_blocks_dive_counters_for_both_benches():
    game = _game(deck_a_extra=["Battle Cage"])
    me = game.players["a"]
    foe = game.players["b"]
    game._set_stadium(fallback_named("Battle Cage"))
    assert game.stadium_name == "Battle Cage"
    me.active = Pokemon(card_i=_idx(me, "Mewtwo ex"), played_turn=0)
    me.bench = [Pokemon(card_i=_idx(me, "Clefairy"), played_turn=0)]
    foe.active = Pokemon(card_i=_idx(foe, "Dragapult ex"), played_turn=0)
    foe.bench = [Pokemon(card_i=_idx(foe, "Dreepy"), played_turn=0)]
    game._bench_damage_counters(me, 6)
    game._bench_damage_counters(foe, 6)
    assert me.bench[0].damage == 0
    assert foe.bench[0].damage == 0
    assert game.events.get("battle_cage") == 2


def test_battle_cage_does_not_block_cruel_arrow_bench_damage():
    game = _game(deck_a_extra=["Battle Cage"])
    me = game.players["b"]
    foe = game.players["a"]
    game._set_stadium(fallback_named("Battle Cage"))
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Mega Clefable ex"), played_turn=0)
    bench_i = _idx(foe, "Clefairy")
    foe.bench = [Pokemon(card_i=bench_i, played_turn=0)]
    game._damage_one_pokemon(me, foe, 100)
    assert foe.bench[0].damage == 100


def test_shaymin_redirects_bench_damage_to_active_for_plain_bench():
    game = _game(deck_a_extra=["Shaymin"])
    me = game.players["b"]
    foe = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Mega Clefable ex"), played_turn=0)
    foe.bench = [Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0)]
    # Shaymin sits on the bench beside the Clefairy.
    foe.bench.append(Pokemon(card_i=_idx(foe, "Shaymin"), played_turn=0))
    game._damage_one_pokemon(me, foe, 100)
    assert foe.bench[0].damage == 0
    assert foe.active.damage == 100
    assert game.events.get("flower_curtain") == 1


def test_shaymin_leaves_ex_bench_exposed():
    game = _game(deck_a_extra=["Shaymin"])
    me = game.players["b"]
    foe = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Mega Clefable ex"), played_turn=0)
    foe.bench = [
        Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0),
        Pokemon(card_i=_idx(foe, "Shaymin"), played_turn=0),
        Pokemon(card_i=_idx(foe, "Mewtwo ex"), played_turn=0),
    ]
    game._damage_one_pokemon(me, foe, 100)
    assert foe.bench[2].damage == 100
    assert foe.bench[0].damage == 0


def test_rabsca_redirects_bench_damage_to_active():
    game = _game(deck_a_extra=["Rabsca"])
    me = game.players["b"]
    foe = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Mega Clefable ex"), played_turn=0)
    foe.bench = [
        Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0),
        Pokemon(card_i=_idx(foe, "Rabsca"), played_turn=0),
    ]
    game._damage_one_pokemon(me, foe, 100)
    assert foe.bench[0].damage == 0
    assert foe.active.damage == 100
    assert game.events.get("spherical_shield") == 1


def test_battle_cage_forces_adrena_brain_onto_active():
    game = _game(deck_b_names=list(SET_T_META_NAMES))
    me = game.players["b"]
    foe = game.players["a"]
    game._set_stadium(fallback_named("Battle Cage"))
    munk_i = _idx(me, "Munkidori")
    dark_i = next(i for i, c in enumerate(me.cards) if c.name == "Darkness Energy")
    donor = Pokemon(card_i=_idx(me, "Dreepy"), played_turn=0, damage=60)
    src = Pokemon(card_i=munk_i, played_turn=0, energy=[dark_i])
    me.active = src
    me.bench = [donor]
    foe.active = Pokemon(card_i=_idx(foe, "Mewtwo ex"), played_turn=0)
    foe.bench = [Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0)]
    eff = {"kind": "move_damage_counters", "counters": 3, "require_energy": "Darkness"}
    assert game._move_damage_counters(me, foe, src, eff) is True
    assert foe.active.damage == 30
    assert foe.bench[0].damage == 0
    assert donor.damage == 30


def test_rabsca_does_not_block_adrena_brain():
    game = _game(deck_a_extra=["Rabsca"], deck_b_names=list(SET_T_META_NAMES))
    me = game.players["b"]
    foe = game.players["a"]
    munk_i = _idx(me, "Munkidori")
    dark_i = next(i for i, c in enumerate(me.cards) if c.name == "Darkness Energy")
    donor = Pokemon(card_i=_idx(me, "Dreepy"), played_turn=0, damage=60)
    src = Pokemon(card_i=munk_i, played_turn=0, energy=[dark_i])
    me.active = src
    me.bench = [donor]
    foe.active = Pokemon(card_i=_idx(foe, "Mega Clefable ex"), played_turn=0)
    clef = Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0, damage=40)
    foe.bench = [
        Pokemon(card_i=_idx(foe, "Rabsca"), played_turn=0),
        clef,
    ]
    eff = {"kind": "move_damage_counters", "counters": 3, "require_energy": "Darkness"}
    assert game._move_damage_counters(me, foe, src, eff) is True
    # Rabsca is attacks-only: the Ability still snipes the 60 HP bench.
    assert clef.damage == 70


def test_bench_shield_jsons_follow_schema():
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[1] / "data" / "lab"
    bake = json.loads((root / "set-c60-bench-shield.json").read_text())
    assert bake["games"] == 3000
    assert bake["seed"] == 20260911
    assert list(bake["variants"]) == [
        "base",
        "cage2-hop-iono",
        "cage2-jacq-retr",
        "cage1-iono",
        "rabsca-hop-iono",
        "rabsca-jacq-retr",
        "shaymin-iono",
    ]
    for row in bake["cells"].values():
        assert set(row) == {"t60", "hedrick", "unl", "d60"}
    final = json.loads((root / "set-c60-bench-shield-final.json").read_text())
    assert final["games"] == 3000
    assert final["seed"] == 20260911
    assert list(final["cells"]) == [
        "base(pre-shield)",
        "cage2(-Jacq-Retrieval+2Cage)",
        "LOCKED(-Jacq-Retrieval-Iono+3Cage)",
    ]
    for row in final["cells"].values():
        assert set(row) == {"g", "d60", "t60", "hedrick", "unl", "s60"}
    from collections import Counter

    locked = final["variants"]["LOCKED(-Jacq-Retrieval-Iono+3Cage)"]
    assert locked.count("Battle Cage") == 3
    assert locked.count("Penny") == 0
    assert Counter(locked) == Counter(c60_names_before_bounce())


def test_locked_c60_has_three_cages_and_stays_legal():
    names = list(SET_C60_NAMES)
    assert len(names) == 60
    assert names.count("Battle Cage") == 3
    assert names.count("Iono") == 1
    assert names.count("Penny") == 0
    assert names.count("Jacq") == 0
    assert names.count("Energy Retrieval") == 0
    assert copy_violations(build_fallback_deck(names), standard_60_rules()) == []
