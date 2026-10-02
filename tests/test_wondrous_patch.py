"""Wondrous Patch: printed bench attach, and the turn-2 Clefairy Wonder Storm line."""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, build_fallback_deck, fallback_named

PRINTED = (
    "Attach a Basic Psychic Energy card from your discard pile to 1 of your Benched Psychic Pokémon."
)


def test_wondrous_patch_parses_printed_text():
    card = fallback_named("Wondrous Patch")
    assert card.trainer_kind == "item"
    assert card.catalog_id == "me02-094"
    assert card.text == PRINTED
    assert parse_trainer_effects(card.text) == [
        {
            "kind": "wondrous_patch",
            "count": 1,
            "energy_type": "Psychic",
            "bench_only": True,
            "pokemon_type": "Psychic",
        }
    ]
    assert parse_trainer_effects("Draw a card.") == [] or all(
        e.get("kind") != "wondrous_patch" for e in parse_trainer_effects("Draw a card.")
    )


def _take(cards, used, pred, n):
    found = []
    for i, card in enumerate(cards):
        if i in used or not pred(card):
            continue
        found.append(i)
        if len(found) == n:
            break
    assert len(found) == n, pred
    used.update(found)
    return found


def _storm_game(*, extra_bench: bool, deck_fuels: int):
    names = list(SET_C60_NAMES)
    names[names.index("Poké Pad")] = "Wondrous Patch"
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("party"),
        Random(1),
        first="b",
    )
    game.turn = 3
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    clefs = _take(me.cards, used, lambda c: c.name == "Clefairy", 3 if extra_bench else 2)
    ps = _take(
        me.cards,
        used,
        lambda c: c.name == "Psychic Energy",
        5 + deck_fuels,
    )
    patch = _take(me.cards, used, lambda c: c.name == "Wondrous Patch", 1)[0]
    placed = set(ps) | set(clefs) | {patch}
    me.prizes = [i for i in range(len(me.cards)) if i not in placed][:2]
    me.discard = [ps[3]]
    me.hand = [ps[4], patch]
    me.deck = ps[5 : 5 + deck_fuels]
    me.active = Pokemon(card_i=clefs[0], energy=[ps[0]])
    bench = [Pokemon(card_i=clefs[1], energy=[ps[1], ps[2]])]
    if extra_bench:
        bench.append(Pokemon(card_i=clefs[2]))
    me.bench = bench
    me.energy_attached = False
    me.retreated = False
    me.item_lock = False
    # Metal-weak Clefairy, no Stance, so Wonder Storm's printed 20× is the raw hit.
    defender = next(i for i, card in enumerate(foe.cards) if card.name == "Clefairy")
    backup = next(i for i, card in enumerate(foe.cards) if card.is_basic and card.is_pokemon and i != defender)
    foe.active = Pokemon(card_i=defender)
    foe.bench = [Pokemon(card_i=backup)]
    return game, me, clefs, ps


def test_turn_two_patch_storm_deals_at_least_80():
    """Active Clefairy has 1 Energy. Attach, retreat for 2, Party, one Patch.

    Wonder Storm counts every Psychic Energy. One other Clefairy is 4 Energy = 80.
    """
    game, me, clefs, ps = _storm_game(extra_bench=False, deck_fuels=1)
    assert game._try_patch_storm(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Clefairy"
    assert me.active.card_i == clefs[1]
    assert game._can_pay_wonder_storm(me, me.active)
    assert game._count_psychic_energy_in_play(me) == 4
    storm = game._wonder_storm_attack(me, me.active)
    assert game._raw_attack_damage(me, game.players["b"], me.active, storm) == 80
    assert ps[0] in me.discard and ps[4] in me.discard
    assert any(me.card(i).name == "Wondrous Patch" for i in me.discard)
    assert game.events.get("patch_storm", 0) >= 1
    assert game.events.get("wondrous_patch", 0) >= 1


def test_more_benched_clefairy_adds_storm_damage():
    game, me, _clefs, _ps = _storm_game(extra_bench=True, deck_fuels=3)
    base, _me, _c, _p = _storm_game(extra_bench=False, deck_fuels=1)
    assert game._try_patch_storm(me, game.players["b"], "a")
    assert base._try_patch_storm(_me, base.players["b"], "a")
    assert game._count_psychic_energy_in_play(me) > base._count_psychic_energy_in_play(_me)
    storm = game._wonder_storm_attack(me, me.active)
    base_storm = base._wonder_storm_attack(_me, _me.active)
    assert game._raw_attack_damage(me, game.players["b"], me.active, storm) > base._raw_attack_damage(
        _me, base.players["b"], _me.active, base_storm
    )


def test_patch_attaches_only_to_a_benched_psychic():
    game, me, clefs, ps = _storm_game(extra_bench=False, deck_fuels=1)
    assert game._attach_wondrous_patch_energy(me, me.active, 1) == 0
    mewtwo = _take(me.cards, set(), lambda c: c.name == "Mewtwo ex", 1)[0]
    me.bench.append(Pokemon(card_i=mewtwo))
    assert game._attach_wondrous_patch_energy(me, me.bench[-1], 1) == 0
    assert ps[3] in me.discard

    tele = next(i for i, card in enumerate(me.cards) if card.name == "Telepathic Psychic Energy")
    me.discard = [tele]
    ex = next(i for i, card in enumerate(me.cards) if card.name == "Clefable ex")
    me.bench.append(Pokemon(card_i=ex))
    assert game._wondrous_patch_target(me, "a") is None
    assert game._attach_wondrous_patch_energy(me, me.bench[-1], 1) == 0

    me.discard = [ps[3]]
    target = game._wondrous_patch_target(me, "a")
    assert target is not None
    assert me.card(target.card_i).name == "Clefable ex"
    assert game._spend_wondrous_patch(me, target)
    assert ps[3] in target.energy
    assert target is not me.active


def test_empty_discard_retreats_elsewhere_then_switch():
    """No Basic Psychic in the discard yet. Retreat into a different Bench Pokémon,
    Patch the still-Benched two-Energy Clefairy, then Switch it Active.

    That Clefairy pays Wonder Storm with 3 Energy. One other Psychic Energy
    on the pivot makes the printed 20× hit 80.
    """
    names = list(SET_C60_NAMES)
    names[names.index("Poké Pad")] = "Wondrous Patch"
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("party"),
        Random(1),
        first="b",
    )
    game.turn = 3
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    clefs = _take(me.cards, used, lambda c: c.name == "Clefairy", 3)
    ps = _take(me.cards, used, lambda c: c.name == "Psychic Energy", 5)
    patch = _take(me.cards, used, lambda c: c.name == "Wondrous Patch", 1)[0]
    switch = _take(me.cards, used, lambda c: c.name == "Switch", 1)[0]
    placed = set(ps) | set(clefs) | {patch, switch}
    me.prizes = [i for i in range(len(me.cards)) if i not in placed][:2]
    me.discard = []
    me.hand = [ps[4], patch, switch]
    me.deck = []
    me.active = Pokemon(card_i=clefs[0], energy=[ps[0]])
    storm = Pokemon(card_i=clefs[1], energy=[ps[1], ps[2]])
    me.bench = [storm, Pokemon(card_i=clefs[2], energy=[ps[3]])]
    me.energy_attached = False
    me.retreated = False
    me.item_lock = False
    defender = next(i for i, card in enumerate(foe.cards) if card.name == "Clefairy")
    backup = next(i for i, card in enumerate(foe.cards) if card.is_basic and card.is_pokemon and i != defender)
    foe.active = Pokemon(card_i=defender)
    foe.bench = [Pokemon(card_i=backup)]

    assert game._try_patch_storm(me, foe, "a")
    assert me.active is not None and me.active.card_i == clefs[1]
    assert len(me.active.energy) == 3
    assert game._can_pay_wonder_storm(me, me.active)
    assert game._count_psychic_energy_in_play(me) == 4
    attack = game._wonder_storm_attack(me, me.active)
    assert game._raw_attack_damage(me, foe, me.active, attack) == 80
    assert ps[0] in me.discard
    assert any(i in me.active.energy for i in (ps[0], ps[4]))
    assert switch in me.discard
    assert patch in me.discard
    assert game.events.get("retreat", 0) >= 1
    assert game.events.get("switch", 0) >= 1
    assert game.events.get("wondrous_patch", 0) >= 1
    assert game.events.get("patch_storm", 0) >= 1


def test_take_turn_plays_the_patch_storm_line():
    game, me, clefs, ps = _storm_game(extra_bench=False, deck_fuels=2)
    # Draw consumes the first deck card. One Party fuel remains.
    assert game._take_turn("a") is False
    assert game.events.get("patch_storm", 0) >= 1
    assert me.active is not None and me.active.card_i == clefs[1]
    assert game._can_pay_wonder_storm(me, me.active)
    assert game._count_psychic_energy_in_play(me) >= 4
    assert ps[0] in me.discard
