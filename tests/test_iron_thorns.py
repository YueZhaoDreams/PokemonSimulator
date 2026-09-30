"""Iron Thorns ex Initialization, from the printed Temporal Forces sentence."""

from __future__ import annotations

from collections import Counter
from random import Random

from app.engine.effects import (
    energy_provided,
    parse_ability_effects,
    parse_effects,
    parse_trainer_effects,
)
from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import IRON_THORNS_NAMES, build_fallback_deck, fallback_named

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


BOOSTER = (
    "The Future Pokémon this card is attached to has no Retreat Cost, and the attacks it uses "
    "do 20 more damage to your opponent's Active Pokémon (before applying Weakness and Resistance)."
)
DTE = (
    "As long as this card is attached to a Pokémon, it provides Colorless Colorless Energy. "
    "The attacks of the Pokémon this card is attached to do 20 less damage to your opponent's "
    "Active Pokémon (before applying Weakness and Resistance)."
)
TURBO_TOOL = (
    "The Pokémon this card is attached to can use the attack on this card. "
    "(You still need the necessary Energy to use this attack.) "
    "If this card is attached to 1 of your Pokémon, discard it at the end of your turn."
)
TURBO_ATTACK = (
    "Search your deck for up to 2 Basic Energy cards and attach them to your Benched Pokémon "
    "in any way you like. Then, shuffle your deck."
)
LOST_CITY = (
    "Whenever a Pokémon (either yours or your opponent's) is Knocked Out, put that Pokémon "
    "in the Lost Zone instead of the discard pile. (Discard all attached cards.)"
)
CATCHER = "Flip a coin. If heads, switch in 1 of your opponent's Benched Pokémon to the Active Spot."
COLOGNE = "Until the end of your turn, your opponent's Active Pokémon has no Abilities."
RADAR = (
    "You must discard a card from your hand in order to use this card. Search your deck for up to 2 "
    "Future cards, reveal them, and put them into your hand. Then, shuffle your deck."
)
CYCLONE = "Move an Energy from this Pokémon to 1 of your Benched Pokémon."


def test_crushing_thorn_list_is_the_worlds_sixty():
    counts = Counter(IRON_THORNS_NAMES)
    assert len(IRON_THORNS_NAMES) == 60
    assert counts["Iron Thorns ex"] == 4
    assert counts["Arven"] == 4
    assert counts["Professor's Research"] == 3
    assert counts["Judge"] == 3
    assert counts["Boss's Orders"] == 3
    assert counts["Colress's Tenacity"] == 2
    assert counts["Pokégear 3.0"] == 4
    assert counts["Crushing Hammer"] == 4
    assert counts["Pokémon Catcher"] == 4
    assert counts["Future Booster Energy Capsule"] == 3
    assert counts["Technical Machine: Turbo Energize"] == 1
    assert counts["Lost City"] == 3
    assert counts["Lightning Energy"] == 7
    assert counts["Double Turbo Energy"] == 4
    deck = build_fallback_deck(list(IRON_THORNS_NAMES))
    assert [card.name for card in deck].count("Iron Thorns ex") == 4
    assert fallback_named("Double Turbo Energy").text == DTE
    assert energy_provided(fallback_named("Double Turbo Energy")) == ["Colorless", "Colorless"]


def test_printed_crushing_thorn_sentences():
    assert parse_effects(CYCLONE) == [{"kind": "move_own_energy_to_bench"}]
    assert parse_effects(TURBO_ATTACK) == [{"kind": "attach_basic_energy_to_bench", "count": 2}]
    assert parse_ability_effects(LOST_CITY) == [{"kind": "ko_to_lost_zone"}]
    assert parse_trainer_effects(CATCHER) == [{"kind": "coin_gust"}]
    assert parse_trainer_effects(COLOGNE) == [{"kind": "blank_opponent_active_abilities"}]
    assert parse_trainer_effects(RADAR) == [{"kind": "search_future", "count": 2, "discard": 1}]
    assert fallback_named("Future Booster Energy Capsule").text == BOOSTER
    assert fallback_named("Technical Machine: Turbo Energize").text == TURBO_TOOL
    assert fallback_named("Technical Machine: Turbo Energize").attacks[0].text == TURBO_ATTACK
    assert fallback_named("Lost City").text == LOST_CITY


def _chain_game() -> Game:
    game = _game(
        [
            "Iron Thorns ex",
            "Iron Thorns ex",
            "Future Booster Energy Capsule",
            "Technical Machine: Turbo Energize",
            "Double Turbo Energy",
            "Lightning Energy",
            "Lightning Energy",
            "Lightning Energy",
            "Clefairy",
        ],
        ["Clefairy", "Clefairy", "Canceling Cologne", "Pokémon Catcher", "Techno Radar", "Lost City"],
    )
    return game


def test_booster_retreat_and_damage_and_double_turbo_before_weakness():
    game = _chain_game()
    me = game.players["a"]
    foe = game.players["b"]
    thorns = _idx(me, "Iron Thorns ex")
    booster = _idx(me, "Future Booster Energy Capsule")
    dte = _idx(me, "Double Turbo Energy")
    lights = [i for i, card in enumerate(me.cards) if card.name == "Lightning Energy"]
    defender = _idx(foe, "Clefairy")
    me.active = Pokemon(card_i=thorns, energy=[lights[0], lights[1], dte], tool=booster, played_turn=0)
    foe.active = Pokemon(card_i=defender, played_turn=0)
    foe.cards[defender].weaknesses = [{"type": "Lightning", "value": "×2"}]
    atk = next(a for a in me.card(thorns).attacks if a.name == "Volt Cyclone")
    assert game._retreat_cost(me, me.active) == 0
    # 140 + 20 booster − 20 Double Turbo, then Weakness ×2.
    assert game._raw_attack_damage(me, foe, me.active, atk) == 280
    me.active.tool = None
    assert game._raw_attack_damage(me, foe, me.active, atk) == 240
    plain = next(i for i, card in enumerate(me.cards) if card.name == "Clefairy")
    me.active.card_i = plain
    me.active.tool = booster
    assert game._retreat_cost(me, me.active) != 0
    assert game._tool_damage_bonus(me, me.active, foe.card(defender)) == 0


def test_volt_cyclone_moves_an_energy_to_the_bench():
    game = _chain_game()
    me = game.players["a"]
    thorns = [i for i, card in enumerate(me.cards) if card.name == "Iron Thorns ex"]
    light = _idx(me, "Lightning Energy")
    me.active = Pokemon(card_i=thorns[0], energy=[light], played_turn=0)
    me.bench = [Pokemon(card_i=thorns[1], played_turn=0)]
    game._move_own_energy_to_bench(me)
    assert me.active.energy == []
    assert me.bench[0].energy == [light]


def test_lost_city_puts_the_knocked_out_pokemon_in_the_lost_zone():
    game = _chain_game()
    me = game.players["a"]
    city = fallback_named("Lost City")
    game._set_stadium(city)
    thorns = _idx(me, "Iron Thorns ex")
    light = _idx(me, "Lightning Energy")
    mon = Pokemon(card_i=thorns, energy=[light], played_turn=0)
    me.active = mon
    game._discard_mon(me, mon)
    assert thorns in me.lost_zone
    assert light in me.discard
    assert thorns not in me.discard


def test_catcher_heads_gusts_and_cologne_blanks_the_active():
    game = _chain_game()
    me = game.players["a"]
    foe = game.players["b"]
    bench_clef = [i for i, card in enumerate(foe.cards) if card.name == "Clefairy"]
    foe.active = Pokemon(card_i=bench_clef[0], played_turn=0)
    foe.bench = [Pokemon(card_i=bench_clef[1], played_turn=0)]
    game.rng.random = lambda: 0.0
    game._coin_gust(me, foe)
    assert foe.card(foe.active.card_i).name == "Clefairy"
    assert foe.active.card_i == bench_clef[1]
    cologne = parse_trainer_effects(COLOGNE)[0]
    game._resolve_parsed_trainer(foe, me, "b", fallback_named("Canceling Cologne"), None, cologne)
    assert game._abilities_suppressed(me, me.active) if me.active else True
    me.active = Pokemon(card_i=_idx(me, "Iron Thorns ex"), played_turn=0)
    assert game._abilities_suppressed(me, me.active) is True


def test_turbo_energize_attaches_from_deck_and_discards_at_end_of_turn():
    game = _chain_game()
    me = game.players["a"]
    thorns = [i for i, card in enumerate(me.cards) if card.name == "Iron Thorns ex"]
    tm = _idx(me, "Technical Machine: Turbo Energize")
    lights = [i for i, card in enumerate(me.cards) if card.name == "Lightning Energy"]
    me.active = Pokemon(card_i=thorns[0], energy=[lights[0]], tool=tm, played_turn=0)
    me.bench = [Pokemon(card_i=thorns[1], played_turn=0)]
    me.deck = [lights[1], lights[2]]
    attacks = game._attacks_for(me, me.active)
    assert any(atk.name == "Turbo Energize" for atk in attacks)
    game._attach_basic_energy_from_deck_to_bench(me, 2)
    assert set(me.bench[0].energy) == {lights[1], lights[2]}
    game._discard_end_of_turn_tools("a")
    assert me.active.tool is None
    assert tm in me.discard


def test_techno_radar_fails_without_a_second_hand_card():
    game = _chain_game()
    me = game.players["a"]
    me.hand = []
    game._search_future(me, 2)
    assert game.events.get("techno_radar_fail") == 1
    assert me.hand == []
