"""Mega Starmie ex Jetting Blow is 120 plus 50 to one Benched Pokémon.

The sentence is the effect. Manaphy prevents that 50. Battle Cage prevents
Froslass's checkup counters on the Bench. Prism Energy is every type only on a Basic.
"""

from __future__ import annotations

from random import Random

from app.engine.effects import energy_provided, parse_ability_effects, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, SET_STARMIE60_NAMES, build_fallback_deck, fallback_named

JETTING = (
    "This attack also does 50 damage to 1 of your opponent's Benched Pokémon. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)
SHROUD = (
    "During Pokémon Checkup, put 1 damage counter on each Pokémon that has an Ability "
    "(both yours and your opponent's), except any Froslass."
)


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 40:
        names.append("Nest Ball")
    return names


def _game(a_names: list[str], b_names: list[str], strat_a: str = "starmie") -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _seat(player, active: int, bench: list[int], energy: list[int] | None = None) -> None:
    used = {active, *bench, *(energy or [])}
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        zone[:] = [i for i in zone if i not in used]
    player.active = Pokemon(card_i=active, played_turn=0, energy=list(energy or []))
    player.bench = [Pokemon(card_i=i, played_turn=0) for i in bench]


def test_kudo_list_is_sixty_and_sees_bench_damage():
    assert len(SET_STARMIE60_NAMES) == 60
    deck = build_fallback_deck(list(SET_STARMIE60_NAMES))
    assert len(deck) == 60
    assert {card.name for card in deck} >= {
        "Mega Starmie ex",
        "Froslass",
        "Hilda",
        "Lucian",
        "Surfing Beach",
        "Prism Energy",
        "Legacy Energy",
        "Bubbly Water Energy",
    }
    game = _game(list(SET_M60_NAMES), list(SET_STARMIE60_NAMES), strat_a="mew_baby")
    assert game._foe_has_bench_attack_damage(game.players["a"])


def test_printed_jetting_blow_and_freezing_shroud():
    starmie = fallback_named("Mega Starmie ex")
    jet = next(atk for atk in starmie.attacks if atk.name == "Jetting Blow")
    assert jet.cost == ["Water"]
    assert jet.damage == 120
    assert jet.text == JETTING
    bench = next(eff for eff in jet.effects if eff.get("kind") == "damage_one_pokemon")
    assert bench["amount"] == 50 and bench["bench_only"] is True

    froslass = fallback_named("Froslass")
    assert froslass.abilities[0].text == SHROUD
    shroud = parse_ability_effects(SHROUD)[0]
    assert shroud["kind"] == "checkup_counter_on_ability"
    assert shroud["counters"] == 1
    assert shroud["except_name"] == "froslass"

    refrain = fallback_named("Mega Froslass ex").attacks[0]
    assert any(eff.get("kind") == "opponent_hand_times" and eff.get("per") == 50 for eff in refrain.effects)
    tail = fallback_named("Dudunsparce ex").attacks[0]
    assert any(eff.get("kind") == "opponent_ex_times" and eff.get("per") == 60 for eff in tail.effects)
    clutch = fallback_named("Yveltal").attacks[0]
    assert any(eff.get("kind") == "no_retreat_next_turn" for eff in clutch.effects)


def test_prism_is_any_only_on_a_basic():
    prism = fallback_named("Prism Energy")
    legacy = fallback_named("Legacy Energy")
    bubbly = fallback_named("Bubbly Water Energy")
    staryu = fallback_named("Staryu")
    mega = fallback_named("Mega Starmie ex")
    assert energy_provided(prism, host=staryu) == ["Any"]
    assert energy_provided(prism, host=mega) == ["Colorless"]
    assert energy_provided(prism) == ["Colorless"]
    assert energy_provided(legacy, host=mega) == ["Any"]
    assert energy_provided(bubbly, host=mega) == ["Water"]
    beach = parse_trainer_effects(fallback_named("Surfing Beach").text)
    assert beach == []
    ability = parse_ability_effects(fallback_named("Surfing Beach").text)
    assert ability[0]["kind"] == "switch_typed_active"
    assert ability[0]["energy_type"] == "Water"
    assert parse_trainer_effects(fallback_named("Hilda").text)[0]["kind"] == "search_evolution_and_energy"
    assert parse_trainer_effects(fallback_named("Lucian").text)[0]["kind"] == "lucian_coin_draw"


def test_item_lock_and_retreat_lock_keep_their_own_events():
    pollen = _game(["Budew"], ["Mew ex", "Igglybuff"])
    me = pollen.players["a"]
    foe = pollen.players["b"]
    _seat(me, _idxs(me, "Budew")[0], [])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Igglybuff")[0]])
    pollen._attack(me, foe, "a")
    assert foe.pending_item_lock is True
    assert foe.active.retreat_locked is False
    assert pollen.events["itchy_pollen_lock"] == 1
    assert pollen.events["itchy_pollen_lock_a"] == 1
    assert "retreat_lock" not in pollen.events

    clutch = _game(["Yveltal", "Darkness Energy"], ["Mew ex", "Igglybuff"])
    me = clutch.players["a"]
    foe = clutch.players["b"]
    dark = _idxs(me, "Darkness Energy")[0]
    _seat(me, _idxs(me, "Yveltal")[0], [], energy=[dark])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Igglybuff")[0]])
    clutch._attack(me, foe, "a")
    assert foe.pending_item_lock is False
    assert foe.active.retreat_locked is True
    assert clutch.events["retreat_lock"] == 1
    assert "itchy_pollen_lock" not in clutch.events
    assert clutch._do_retreat_into(foe, 0) is False


def test_jetting_blow_hits_the_bench_for_50_and_manaphy_prevents_it():
    game = _game(
        ["Mega Starmie ex", "Water Energy"],
        ["Mew ex", "Munkidori"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    water = _idxs(me, "Water Energy")[0]
    _seat(me, _idxs(me, "Mega Starmie ex")[0], [], energy=[water])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Munkidori")[0]])
    game._attack(me, foe, "a")
    assert foe.active.damage == 120
    assert foe.bench[0].damage == 50
    assert game.events["attack:Mega Starmie ex:Jetting Blow"] == 1

    shielded = _game(
        ["Mega Starmie ex", "Water Energy"],
        ["Mew ex", "Munkidori", "Manaphy"],
    )
    me = shielded.players["a"]
    foe = shielded.players["b"]
    water = _idxs(me, "Water Energy")[0]
    _seat(me, _idxs(me, "Mega Starmie ex")[0], [], energy=[water])
    _seat(
        foe,
        _idxs(foe, "Mew ex")[0],
        [_idxs(foe, "Munkidori")[0], _idxs(foe, "Manaphy")[0]],
    )
    shielded._attack(me, foe, "a")
    assert foe.active.damage == 120
    assert all(mon.damage == 0 for mon in foe.bench)
    assert shielded.events["wave_veil"] == 1


def test_three_energy_uses_nebula_only_when_it_kos():
    game = _game(
        ["Mega Starmie ex", "Water Energy", "Water Energy", "Water Energy"],
        ["Mew ex", "Munkidori"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    waters = _idxs(me, "Water Energy")[:3]
    _seat(me, _idxs(me, "Mega Starmie ex")[0], [], energy=waters)
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Munkidori")[0]])
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Nebula Beam"
    foe.active.damage = 40
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Jetting Blow"


def test_freezing_shroud_counters_and_battle_cage_blocks_the_bench():
    game = _game(
        ["Froslass", "Munkidori"],
        ["Mew ex", "Munkidori"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    _seat(me, _idxs(me, "Froslass")[0], [_idxs(me, "Munkidori")[0]])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Munkidori")[0]])
    game._set_stadium(fallback_named("Battle Cage"))
    game._between_turns(me)
    assert me.bench[0].damage == 10
    assert foe.active.damage == 10
    assert foe.bench[0].damage == 0
    assert me.active.damage == 0
    assert game.events["freezing_shroud"] == 2
    assert game.events["battle_cage"] >= 1


def test_mega_starmie_does_not_evolve_the_turn_staryu_is_played():
    game = _game(["Staryu", "Mega Starmie ex", "Mega Lucario ex"], ["Mew ex"])
    me = game.players["a"]
    game.turn = 4
    game.first = "b"
    mon = Pokemon(card_i=_idxs(me, "Staryu")[0], played_turn=4)
    mega = me.card(_idxs(me, "Mega Starmie ex")[0])
    lucario = me.card(_idxs(me, "Mega Lucario ex")[0])
    assert not game._can_evolve_now(me, "a", mon, mega)
    mon.played_turn = 0
    assert game._can_evolve_now(me, "a", mon, mega)
    mon.played_turn = 4
    assert game._can_evolve_now(me, "a", mon, lucario)


def test_hilda_finds_an_evolution_and_an_energy():
    game = _game(
        ["Hilda", "Mega Starmie ex", "Water Energy", "Staryu"],
        ["Mew ex"],
    )
    me = game.players["a"]
    hilda = _idxs(me, "Hilda")[0]
    me.hand = [hilda, _idxs(me, "Staryu")[0]]
    me.deck = [_idxs(me, "Mega Starmie ex")[0], _idxs(me, "Water Energy")[0]]
    me.discard = []
    assert game._commit_trainer(me, game.players["b"], "a", hilda)
    hand = {me.card(i).name for i in me.hand}
    assert "Mega Starmie ex" in hand
    assert "Water Energy" in hand
    assert game.events["hilda"] == 1


def test_lucian_puts_the_hand_on_the_bottom_then_draws():
    game = _game(["Lucian"] + ["Nest Ball"] * 12, ["Mew ex"] + ["Nest Ball"] * 8)
    me = game.players["a"]
    foe = game.players["b"]
    lucian = _idxs(me, "Lucian")[0]
    nests = _idxs(me, "Nest Ball")
    kept = nests[:2]
    me.hand = [lucian, *kept]
    me.deck = nests[2:12]
    foe.hand = []
    foe.deck = _idxs(foe, "Nest Ball")[:8]
    assert game._commit_trainer(me, foe, "a", lucian)
    assert set(me.deck[:2]) == set(kept)
    assert len(me.hand) in {3, 6}
    assert game.events["lucian"] == 1


def test_surfing_beach_switches_water_without_paying_retreat():
    game = _game(
        ["Staryu", "Mega Starmie ex", "Water Energy", "Surfing Beach"],
        ["Mew ex", "Munkidori"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    water = _idxs(me, "Water Energy")[0]
    staryu = _idxs(me, "Staryu")[0]
    mega = _idxs(me, "Mega Starmie ex")[0]
    _seat(me, staryu, [mega], energy=[water])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Munkidori")[0]])
    game._set_stadium(fallback_named("Surfing Beach"), me)
    game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Mega Starmie ex"
    assert me.card(me.bench[0].card_i).name == "Staryu"
    assert me.bench[0].energy == [water]
    assert me.retreated is False
    assert game.events["surfing_beach"] == 1
    game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).name == "Mega Starmie ex"
    assert game.events["surfing_beach"] == 1


def test_opponent_hand_and_ex_attacks_use_the_printed_count():
    game = _game(
        ["Mega Froslass ex", "Dudunsparce ex"],
        ["Mew ex", "Mega Starmie ex", "Nest Ball", "Nest Ball", "Nest Ball"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    _seat(me, _idxs(me, "Mega Froslass ex")[0], [])
    _seat(foe, _idxs(foe, "Mew ex")[0], [_idxs(foe, "Mega Starmie ex")[0]])
    foe.hand = _idxs(foe, "Nest Ball")[:3]
    refrain = me.card(me.active.card_i).attacks[0]
    assert game._raw_attack_damage(me, foe, me.active, refrain) == 150
    _seat(me, _idxs(me, "Dudunsparce ex")[0], [])
    tail = me.card(me.active.card_i).attacks[0]
    assert game._raw_attack_damage(me, foe, me.active, tail) == 120


def test_one_starmie_game_finishes():
    rec = run_simulation(
        build_fallback_deck(list(SET_M60_NAMES)),
        build_fallback_deck(list(SET_STARMIE60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("starmie"),
        games=1,
        seed=20261007,
    )
    assert rec["results"]["wins_a"] + rec["results"]["wins_b"] + rec["results"]["ties"] == 1
