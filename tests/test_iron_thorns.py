"""Iron Thorns ex Initialization, from the printed Temporal Forces sentence."""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

PRINTED = (
    "As long as this Pokémon is in the Active Spot, Pokémon with a Rule Box in play "
    "(both yours and your opponent's) have no Abilities, except for Future Pokémon. "
    "(Pokémon ex, Pokémon V, etc. have Rule Boxes.)"
)


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 12:
        names.append("Lightning Energy")
    return names


def _game(a_names: list[str], b_names: list[str]) -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names)),
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("party"),
        Random(1),
    )


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name == name)


def _future_clefable() -> Card:
    data = fallback_named("Clefable ex").to_dict()
    data["name"] = "Future Clefable ex"
    data["catalog_id"] = "future-clefable-ex"
    data["traits"] = ["Future"]
    return Card.from_dict(data)


def test_initialization_parses_the_printed_sentence():
    card = fallback_named("Iron Thorns ex")
    assert card.abilities[0].name == "Initialization"
    assert card.abilities[0].text == PRINTED
    assert card.traits == ["Future"]
    assert parse_ability_effects(PRINTED) == [
        {
            "kind": "suppress_rulebox_abilities",
            "except_trait": "future",
            "require_active": True,
        }
    ]
    assert parse_ability_effects(card.abilities[0].text) == parse_ability_effects(PRINTED)
    flutter = fallback_named("Flutter Mane")
    kinds = [e.get("kind") for abi in flutter.abilities for e in parse_ability_effects(abi.text)]
    assert kinds == ["suppress_opponent_active_abilities"]


def test_initialization_shuts_rule_box_abilities_and_leaves_clefairy():
    game = _game(
        ["Clefairy", "Clefairy", "Clefable ex", "Psychic Energy", "Psychic Energy"],
        ["Iron Thorns ex", "Clefairy"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, card in enumerate(me.cards) if card.name == "Clefairy"]
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Psychic Energy"]
    clefable = _idx(me, "Clefable ex")
    thorns = _idx(foe, "Iron Thorns ex")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [
        Pokemon(card_i=clefs[1], played_turn=0),
        Pokemon(card_i=clefable, energy=[fuels[0]], played_turn=0),
    ]
    me.deck = list(fuels[1:])
    foe.active = Pokemon(card_i=thorns, played_turn=0)
    foe.bench = []

    assert game._abilities_suppressed(foe, foe.active) is False
    assert game._abilities_suppressed(me, me.active) is False
    assert game._abilities_suppressed(me, me.bench[1]) is True
    assert game._retreat_cost(me, me.bench[1]) == 2

    game._use_abilities(me, foe, "a")
    assert game.events.get("moon_watching_party", 0) == 1
    assert me.bench[0].energy

    foe.bench = [foe.active]
    foe.active = Pokemon(card_i=_idx(foe, "Clefairy"), played_turn=0)
    assert game._abilities_suppressed(me, me.bench[1]) is False
    assert game._retreat_cost(me, me.bench[1]) == 0


def test_future_rule_box_keeps_its_ability():
    future = _future_clefable()
    cards_a = build_fallback_deck(_pad(["Iron Thorns ex"]))
    cards_b = [future, fallback_named("Psychic Energy")] + build_fallback_deck(["Lightning Energy"] * 10)
    game = Game(
        cards_a,
        cards_b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("party"),
        Random(2),
    )
    me = game.players["a"]
    foe = game.players["b"]
    me.active = Pokemon(card_i=_idx(me, "Iron Thorns ex"), played_turn=0)
    psychic = next(i for i, card in enumerate(foe.cards) if card.name == "Psychic Energy")
    future_i = next(i for i, card in enumerate(foe.cards) if card.name == "Future Clefable ex")
    foe.active = Pokemon(card_i=future_i, energy=[psychic], played_turn=0)
    assert game._has_rule_box(foe.card(future_i)) is True
    assert game._abilities_suppressed(foe, foe.active) is False
    assert game._retreat_cost(foe, foe.active) == 0


def test_cornerstone_stance_stops_blocking_while_initialization_is_active():
    game = _game(
        ["Iron Thorns ex", "Clefairy"],
        ["Cornerstone Mask Ogerpon ex", "Clefairy"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    thorns = _idx(me, "Iron Thorns ex")
    clef = _idx(me, "Clefairy")
    mask = _idx(foe, "Cornerstone Mask Ogerpon ex")
    me.active = Pokemon(card_i=thorns, played_turn=0)
    foe.active = Pokemon(card_i=mask, played_turn=0)
    cyclone = next(atk for atk in me.card(thorns).attacks if atk.name == "Volt Cyclone")
    assert game._raw_attack_damage(me, foe, me.active, cyclone) == 140

    me.bench = [me.active]
    me.active = Pokemon(card_i=clef, played_turn=0)
    storm = next(atk for atk in me.card(clef).attacks if atk.name == "Wonder Storm")
    assert game._raw_attack_damage(me, foe, me.active, storm) == 0


def test_flutter_mane_shuts_initialization_so_benched_ex_keeps_lunar_zone():
    game = _game(
        ["Iron Thorns ex", "Clefable ex", "Psychic Energy"],
        ["Flutter Mane", "Clefairy"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    thorns = _idx(me, "Iron Thorns ex")
    clefable = _idx(me, "Clefable ex")
    psychic = _idx(me, "Psychic Energy")
    flutter = _idx(foe, "Flutter Mane")
    me.active = Pokemon(card_i=thorns, played_turn=0)
    me.bench = [Pokemon(card_i=clefable, energy=[psychic], played_turn=0)]
    foe.active = Pokemon(card_i=flutter, played_turn=0)

    assert game._abilities_suppressed(me, me.active) is True
    assert game._abilities_suppressed(me, me.bench[0]) is False
    assert game._retreat_cost(me, me.bench[0]) == 0
