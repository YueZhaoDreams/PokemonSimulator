"""Journey Together Spiky Energy. Copies stack, and the card is not a Tool."""

from __future__ import annotations

from random import Random

from app.engine.effects import energy_provided, is_basic_energy, is_special_energy, parse_energy_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import _is_basic_energy_name
from app.seed_data import build_fallback_deck, fallback_named

PRINTED = (
    "As long as this card is attached to a Pokémon, it provides Colorless Energy.\n\n"
    "If the Pokémon this card is attached to is in the Active Spot and is damaged by an attack "
    "from your opponent's Pokémon (even if this Pokémon is Knocked Out), put 2 damage counters "
    "on the Attacking Pokémon."
)


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 40:
        names.append("Nest Ball")
    return names


def _game(a_names: list[str], b_names: list[str]) -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _take(player, card_i: int) -> None:
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        if card_i in zone:
            zone.remove(card_i)


def _seat(player, active: int, bench: list[int], tool: int | None = None, energy: list[int] | None = None) -> None:
    used = {active, *bench}
    if tool is not None:
        used.add(tool)
    for card_i in energy or []:
        used.add(card_i)
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        zone[:] = [i for i in zone if i not in used]
    player.active = Pokemon(card_i=active, played_turn=0, tool=tool, energy=list(energy or []))
    player.bench = [Pokemon(card_i=i, played_turn=0) for i in bench]


def test_printed_spiky_energy_sentence():
    card = fallback_named("Spiky Energy")
    alias = fallback_named("Spike Energy")
    assert card.text == PRINTED
    assert alias.catalog_id == card.catalog_id
    assert "tool" not in card.text.lower()
    assert card.stage == "Special"
    assert is_special_energy(card)
    assert not is_basic_energy(card)
    assert not _is_basic_energy_name("Spiky Energy")
    assert not _is_basic_energy_name("Spike Energy")
    assert energy_provided(card) == ["Colorless"]
    assert parse_energy_effects(PRINTED) == [{"kind": "counters_on_attacker", "counters": 2}]
    assert parse_energy_effects(card.text) == [{"kind": "counters_on_attacker", "counters": 2}]


def test_four_spiky_is_legal_five_is_not():
    rules = standard_60_rules()
    four = ["Mew ex"] + ["Spiky Energy"] * 4 + ["Psychic Energy"] * 55
    assert copy_violations(build_fallback_deck(four), rules) == []
    five = ["Mew ex"] + ["Spiky Energy"] * 5 + ["Psychic Energy"] * 54
    violations = copy_violations(build_fallback_deck(five), rules)
    assert violations == [{"name": "Spiky Energy", "count": 5, "max": 4}]


def test_spiky_attaches_to_active_mew_that_already_has_a_tool():
    game = _game(
        ["Igglybuff", "Mew ex", "Spiky Energy", "Hero's Cape"],
        ["Budew"],
    )
    me = game.players["a"]
    iggly = _idxs(me, "Igglybuff")[0]
    mew = _idxs(me, "Mew ex")[0]
    spike = _idxs(me, "Spiky Energy")[0]
    cape = _idxs(me, "Hero's Cape")[0]
    _seat(me, iggly, [mew])
    me.bench[0].tool = cape
    _take(me, cape)
    _take(me, spike)
    me.hand.append(spike)

    target = game._energy_target(me, game.strats["a"])
    assert target is me.bench[0]
    assert game._choose_energy_card(me, target, game.strats["a"]) == spike
    game._attach_energy(me, "a")
    assert me.bench[0].energy == [spike]
    assert me.bench[0].tool == cape


def test_tool_still_attaches_when_spiky_is_already_there():
    game = _game(
        ["Igglybuff", "Mew ex", "Spiky Energy", "Hero's Cape"],
        ["Budew"],
    )
    me = game.players["a"]
    iggly = _idxs(me, "Igglybuff")[0]
    mew = _idxs(me, "Mew ex")[0]
    spike = _idxs(me, "Spiky Energy")[0]
    cape = _idxs(me, "Hero's Cape")[0]
    _seat(me, iggly, [mew])
    me.bench[0].energy = [spike]
    _take(me, spike)
    _take(me, cape)
    me.hand.append(cape)

    assert game._tool_target(me, "a", me.card(cape)) is me.bench[0]
    assert game._attach_tool(me, "a", cape)
    assert me.bench[0].tool == cape
    assert me.bench[0].energy == [spike]


def test_second_copy_stacks_on_the_same_mew():
    game = _game(
        ["Mew ex", "Igglybuff", "Spiky Energy", "Spiky Energy", "Hero's Cape"],
        ["Budew"],
    )
    me = game.players["a"]
    mew = _idxs(me, "Mew ex")[0]
    iggly = _idxs(me, "Igglybuff")[0]
    first, second = _idxs(me, "Spiky Energy")
    cape = _idxs(me, "Hero's Cape")[0]
    _seat(me, mew, [iggly], tool=cape, energy=[first])
    _take(me, second)
    me.hand.append(second)

    assert game._energy_target(me, game.strats["a"]) is me.active
    game._attach_energy(me, "a")
    assert me.active.energy == [first, second]
    assert me.active.tool == cape


def test_each_spiky_copy_places_its_own_counters():
    game = _game(
        ["Budew", "Mew ex"],
        ["Mew ex", "Spiky Energy", "Spiky Energy", "Spiky Energy", "Spiky Energy", "Hero's Cape"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    defender = _idxs(foe, "Mew ex")[0]
    spikes = _idxs(foe, "Spiky Energy")
    cape = _idxs(foe, "Hero's Cape")[0]
    _seat(me, attacker, [])

    _seat(foe, defender, [], tool=cape, energy=spikes[:1])
    game._attack(me, foe, "a")
    assert me.active.damage == 20
    assert game.events["spiky_energy"] == 2

    me.active.damage = 0
    game.events.pop("spiky_energy", None)
    foe.active.energy = spikes[:2]
    game._attack(me, foe, "a")
    assert me.active.damage == 40
    assert game.events["spiky_energy"] == 4

    me.active.damage = 0
    game.events.pop("spiky_energy", None)
    foe.active.energy = list(spikes)
    game._attack(me, foe, "a")
    assert me.active.damage == 80
    assert game.events["spiky_energy"] == 8
    assert foe.active.tool == cape


def test_spiky_stacks_with_bursting_balloon():
    game = _game(
        ["Budew", "Mew ex"],
        ["Budew", "Spiky Energy", "Spiky Energy", "Bursting Balloon", "Mew ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    defender = _idxs(foe, "Budew")[0]
    spikes = _idxs(foe, "Spiky Energy")
    balloon = _idxs(foe, "Bursting Balloon")[0]
    _seat(me, attacker, [])
    _seat(foe, defender, [], tool=balloon, energy=spikes)

    game._attack(me, foe, "a")
    assert foe.active.damage == 10
    assert me.active.damage == 100
    assert game.events["bursting_balloon"] == 6
    assert game.events["spiky_energy"] == 4
    assert foe.active.tool == balloon
    assert foe.active.energy == spikes


def test_bench_copy_does_not_add_counters():
    game = _game(
        ["Budew", "Mew ex"],
        ["Mew ex", "Igglybuff", "Spiky Energy", "Spiky Energy"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    mew = _idxs(foe, "Mew ex")[0]
    baby = _idxs(foe, "Igglybuff")[0]
    on_active, on_bench = _idxs(foe, "Spiky Energy")
    _seat(me, attacker, [])
    _seat(foe, mew, [baby], energy=[on_active])
    foe.bench[0].energy = [on_bench]
    _take(foe, on_bench)

    game._attack(me, foe, "a")
    assert me.active.damage == 20
    assert game.events["spiky_energy"] == 2

    me.active.damage = 0
    game.events.clear()
    game._add_attack_damage(foe, foe.bench[0], 10)
    assert me.active.damage == 0
    assert "spiky_energy" not in game.events


def test_both_copies_still_counter_when_the_active_is_knocked_out():
    game = _game(
        ["Igglybuff", "Budew", "Mew ex"],
        ["Budew", "Spiky Energy", "Spiky Energy", "Mew ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    iggly = _idxs(me, "Igglybuff")[0]
    bench_baby = _idxs(me, "Budew")[0]
    mew_a = _idxs(me, "Mew ex")[0]
    defender = _idxs(foe, "Budew")[0]
    spikes = _idxs(foe, "Spiky Energy")
    mew_b = _idxs(foe, "Mew ex")[0]
    _seat(me, iggly, [bench_baby, mew_a])
    _seat(foe, defender, [mew_b], energy=spikes)
    prizes_a = me.prizes_taken
    prizes_b = foe.prizes_taken

    game._attack(me, foe, "a")
    assert me.active.damage == 40
    assert game.events["spiky_energy"] == 4
    assert game._check_ko(foe, me, "b") is False
    assert game._check_ko(me, foe, "a") is False
    assert me.prizes_taken == prizes_a + 1
    assert foe.prizes_taken == prizes_b + 1
    assert all(spike in foe.discard for spike in spikes)
    assert me.card(me.active.card_i).name == "Mew ex"
    assert foe.card(foe.active.card_i).name == "Mew ex"


def test_demolish_ignores_stacked_spiky_and_balloon():
    game = _game(
        ["Cornerstone Mask Ogerpon ex", "Fighting Energy", "Psychic Energy", "Psychic Energy"],
        ["Mew ex", "Spiky Energy", "Spiky Energy", "Bursting Balloon", "Hero's Cape"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    oger = _idxs(me, "Cornerstone Mask Ogerpon ex")[0]
    fuel = _idxs(me, "Fighting Energy") + _idxs(me, "Psychic Energy")
    defender = _idxs(foe, "Mew ex")[0]
    spikes = _idxs(foe, "Spiky Energy")
    balloon = _idxs(foe, "Bursting Balloon")[0]
    _seat(me, oger, [], energy=fuel)
    _seat(foe, defender, [], tool=balloon, energy=spikes)

    game._attack(me, foe, "a")
    assert foe.active.damage == 140
    assert me.active.damage == 0
    assert "spiky_energy" not in game.events
    assert "bursting_balloon" not in game.events
    assert foe.active.energy == spikes
    assert foe.active.tool == balloon


def test_zero_damage_does_not_place_counters():
    game = _game(["Budew"], ["Mew ex", "Spiky Energy"])
    me = game.players["a"]
    foe = game.players["b"]
    attacker = _idxs(me, "Budew")[0]
    defender = _idxs(foe, "Mew ex")[0]
    spike = _idxs(foe, "Spiky Energy")[0]
    _seat(me, attacker, [])
    _seat(foe, defender, [], energy=[spike])
    game._add_attack_damage(foe, foe.active, 0)
    assert me.active.damage == 0
    assert "spiky_energy" not in game.events


def test_under_iron_thorns_spiky_stacks_on_the_baby_wall():
    game = _game(
        ["Mew ex", "Igglybuff", "Spiky Energy", "Spiky Energy", "Hero's Cape"],
        ["Iron Thorns ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    mew = _idxs(me, "Mew ex")[0]
    iggly = _idxs(me, "Igglybuff")[0]
    first, second = _idxs(me, "Spiky Energy")
    cape = _idxs(me, "Hero's Cape")[0]
    thorns = _idxs(foe, "Iron Thorns ex")[0]
    _seat(foe, thorns, [])
    _seat(me, mew, [iggly], tool=cape)
    _take(me, first)
    me.hand.append(first)

    assert game._rulebox_lock_on_opponent(me)
    assert game._energy_target(me, game.strats["a"]) is me.bench[0]
    game._attach_energy(me, "a")
    assert me.bench[0].energy == [first]
    assert me.active.tool == cape

    me.active, me.bench[0] = me.bench[0], me.active
    _take(me, second)
    me.hand.append(second)
    me.energy_attached = False
    assert game._energy_target(me, game.strats["a"]) is me.active
    game._attach_energy(me, "a")
    assert me.active.energy == [first, second]
    assert me.card(me.active.card_i).name == "Igglybuff"
