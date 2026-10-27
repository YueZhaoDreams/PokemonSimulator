"""Celebi ◇ Time Distortion and Lost Origin Chandelure.

Printed sentences are the engine source. Grand Tree evolves from the deck, so
Mountain Roasting does not mill. Playing Chandelure from the hand does.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects, parse_trainer_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, build_roast_deck, fallback_named

TIME_DISTORTION = (
    "Devolve any number of your Benched Pokémon as many times as you like. "
    "Put each Evolution card removed this way into your hand."
)
MOUNTAIN_ROASTING = (
    "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
    "you may discard the top 3 cards of your opponent's deck."
)
FREEFLOATING = "If this Pokémon has no Energy attached to it, this Pokémon has no Retreat Cost."
RESCUE_SCARF = (
    "If the Pokémon this card is attached to is Knocked Out by damage from an attack, "
    "put that Pokémon into your hand. (Discard all cards attached to that Pokémon.)"
)
GRAND_TREE = (
    "You can't have more than 1 ACE SPEC card in your deck. "
    "Once during each player's turn, that player may search their deck for a Stage 1 Pokémon "
    "that evolves from 1 of their Basic Pokémon and put it onto that Pokémon to evolve it. "
    "If that Pokémon was evolved in this way, that player may search their deck for a Stage 2 "
    "Pokémon that evolves from that Pokémon and put it onto that Pokémon to evolve it. "
    "Then, that player shuffles their deck. (Players can't evolve a Basic Pokémon during their "
    "first turn or a Basic Pokémon that was put into play this turn.)"
)


def _game() -> Game:
    foe = build_fallback_deck(["Dondozo"] + ["Hop"] * 59)
    return Game(
        build_roast_deck(),
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("roast"),
        StrategySpec.from_dict("balanced"),
        Random(1),
    )


def _reclaim(me) -> None:
    found: list[int] = []
    mons = ([me.active] if me.active else []) + list(me.bench)
    for mon in mons:
        found.append(mon.card_i)
        found.extend(mon.underneath)
        found.extend(mon.energy)
        if mon.tool is not None:
            found.append(mon.tool)
    me.active = None
    me.bench.clear()
    me.hand.extend(found)


def _pull(me, name: str) -> int:
    for zone in (me.hand, me.deck, me.prizes, me.discard, me.lost_zone):
        for card_i in list(zone):
            if me.card(card_i).name == name:
                zone.remove(card_i)
                return card_i
    raise AssertionError(name)


def test_printed_sentences_parse_without_a_fixed_devolve_count():
    devolve = next(e for e in parse_effects(TIME_DISTORTION) if e.get("kind") == "devolve_benched")
    assert "count" not in devolve
    roasted = parse_ability_effects(MOUNTAIN_ROASTING)
    assert roasted == [{"kind": "mill_on_play_from_hand", "count": 3}]
    four = parse_ability_effects(MOUNTAIN_ROASTING.replace("top 3", "top 4"))
    assert four == [{"kind": "mill_on_play_from_hand", "count": 4}]
    assert parse_ability_effects(FREEFLOATING) == [{"kind": "retreat_zero_if_no_energy"}]
    assert {"kind": "grand_tree"} in parse_ability_effects(GRAND_TREE)
    assert not any(e.get("kind") == "mill_on_play_from_hand" for e in parse_ability_effects(GRAND_TREE))
    scarf = parse_trainer_effects(RESCUE_SCARF)
    assert {"kind": "ko_to_hand", "attack_only": True} in scarf

    celebi = fallback_named("Celebi ◇")
    assert celebi.attacks[0].text == TIME_DISTORTION
    assert any(e.get("kind") == "devolve_benched" for e in celebi.attacks[0].effects)
    assert "prism star" in [t.lower() for t in celebi.traits]
    lampent = fallback_named("Lampent")
    assert lampent.abilities[0].text == FREEFLOATING
    chandelure = fallback_named("Chandelure")
    assert chandelure.abilities[0].text == MOUNTAIN_ROASTING
    assert fallback_named("Grand Tree").text == GRAND_TREE
    assert fallback_named("Rescue Scarf").text == RESCUE_SCARF


def test_roast_deck_is_sixty_and_pichu_is_playground():
    deck = build_roast_deck()
    assert len(deck) == 60
    assert copy_violations(deck, standard_60_rules()) == []
    assert StrategySpec.from_dict("roast").name == "roast"
    pichu = [card for card in deck if card.name == "Pichu"]
    assert len(pichu) == 3
    for card in pichu:
        playground = next(
            effect
            for attack in card.attacks
            for effect in attack.effects
            if effect.get("kind") == "playground"
        )
        assert "count" not in playground
        assert playground.get("user_first") is True
        assert any(ability.name == "Sweet Sleeping Face" for ability in card.abilities)
        assert "as many" in card.attacks[0].text.lower()


def test_devolve_any_number_of_times_and_roast_takes_one_step():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    celebi = _pull(me, "Celebi ◇")
    me.active = Pokemon(card_i=celebi, played_turn=0)
    mon = Pokemon(card_i=chand, played_turn=0)
    mon.underneath = [lit, lamp]
    me.bench = [mon]
    returned = game._devolve_times(me, mon, 2)
    assert [me.card(i).name for i in returned] == ["Chandelure", "Lampent"]
    assert me.card(mon.card_i).name == "Litwick"
    assert chand in me.hand and lamp in me.hand

    mon.card_i = chand
    me.hand.remove(chand)
    me.hand.remove(lamp)
    mon.underneath = [lit, lamp]
    game.current = "a"
    game._time_distortion(me, "a")
    assert me.card(mon.card_i).name == "Lampent"
    assert chand in me.hand
    assert lamp not in me.hand
    assert game.events.get("time_distortion", 0) == 1


def test_grand_tree_mills_nothing_and_hand_evolve_mills_three():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    tree = _pull(me, "Grand Tree")
    me.deck.extend([lamp, chand])
    me.active = Pokemon(card_i=celebi, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0)]
    game.turn = 4
    game.first = "b"
    game.current = "a"
    game._set_stadium(me.card(tree), owner=me)
    before = len(foe.deck)
    game._use_grand_tree(me, "a")
    assert me.card(me.bench[0].card_i).name == "Chandelure"
    assert len(foe.deck) == before
    assert game.events.get("mountain_roasting", 0) == 0
    assert game.events.get("grand_tree", 0) == 1
    game._time_distortion(me, "a")
    assert me.card(me.bench[0].card_i).name == "Lampent"
    assert any(me.card(i).name == "Chandelure" for i in me.hand)
    # Grand Tree played Lampent this turn. It can take Chandelure from the hand next turn.
    game.turn = 5
    game._roast_hand_evolve(me, "a")
    assert me.card(me.bench[0].card_i).name == "Chandelure"
    assert len(foe.deck) == before - 3
    assert game.events.get("mountain_roasting", 0) == 1
    game._note_roast_mill("a")
    assert game.events.get("roast_mill_wave:3", 0) == 1


def test_freefloating_retreat_is_zero_only_with_no_energy():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    fire = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=lamp, played_turn=0)
    assert game._retreat_cost(me, me.active) == 0
    me.active.energy = [fire]
    assert game._retreat_cost(me, me.active) == 1
    me.bench = [Pokemon(card_i=chand, played_turn=0)]
    assert game._retreat_cost(me, me.bench[0]) == 2


def test_rescue_scarf_returns_celebi_and_a_bare_prism_is_lost():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    scarf = _pull(me, "Rescue Scarf")
    fire = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=celebi, energy=[fire], tool=scarf, played_turn=0)
    game._add_attack_damage(me, me.active, 200)
    game._check_ko(me, foe, "a")
    assert celebi in me.hand
    assert celebi not in me.lost_zone
    assert celebi not in me.discard
    assert scarf in me.discard
    assert fire in me.discard
    assert game.events.get("rescue_scarf", 0) == 1
    assert game.events.get("prism_lost_zone", 0) == 0

    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    me.active = Pokemon(card_i=celebi, played_turn=0)
    game._add_attack_damage(me, me.active, 200)
    game._check_ko(me, foe, "a")
    assert celebi in me.lost_zone
    assert celebi not in me.discard
    assert celebi not in me.hand
    assert game.events.get("prism_lost_zone", 0) == 1

    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    scarf = _pull(me, "Rescue Scarf")
    me.active = Pokemon(card_i=celebi, tool=scarf, played_turn=0)
    me.active.damage = 200
    game._check_ko(me, foe, "a")
    assert celebi in me.lost_zone
    assert celebi not in me.hand


def test_scarf_beats_lost_city_on_an_attack_knock_out():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    scarf = _pull(me, "Rescue Scarf")
    me.active = Pokemon(card_i=celebi, tool=scarf, played_turn=0)
    game.stadium_effects = [{"kind": "ko_to_lost_zone"}]
    game._add_attack_damage(me, me.active, 200)
    game._check_ko(me, foe, "a")
    assert celebi in me.hand
    assert celebi not in me.lost_zone
    assert game.events.get("rescue_scarf", 0) == 1
    assert game.events.get("lost_city", 0) == 0


def _foe_basic(foe) -> int:
    for mon in list(foe.bench):
        card = foe.card(mon.card_i)
        if card.is_basic and card.is_pokemon:
            foe.bench.remove(mon)
            return mon.card_i
    for zone in (foe.hand, foe.deck, foe.prizes, foe.discard, foe.lost_zone):
        for card_i in list(zone):
            card = foe.card(card_i)
            if card.is_basic and card.is_pokemon:
                zone.remove(card_i)
                return card_i
    if foe.active is not None and foe.card(foe.active.card_i).is_basic:
        card_i = foe.active.card_i
        foe.active = None
        return card_i
    raise AssertionError("foe basic")


def test_playground_benches_four_litwick_and_celebi_then_stops():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    extra = _pull(me, "Pichu")
    celebi = _pull(me, "Celebi ◇")
    litwicks = [_pull(me, "Litwick") for _ in range(4)]
    me.hand.clear()
    me.deck = litwicks + [celebi, extra]
    me.bench = []
    me.active = Pokemon(card_i=pichu, played_turn=0)
    basic = _foe_basic(foe)
    foe.bench.clear()
    foe.deck = [basic]
    game._playground(me, foe, "a", user_first=True)
    names = [me.card(mon.card_i).name for mon in me.bench]
    assert names.count("Litwick") == 4
    assert names.count("Celebi ◇") == 1
    assert extra in me.deck
    assert len(foe.bench) == 1
    assert game._roast_playground_pick(me) is None
    assert game.events.get("playground", 0) == 6
    assert game.events.get("used_playground_a", 0) == 1


def test_playground_passes_when_a_benched_chandelure_can_devolve():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    celebi = _pull(me, "Celebi ◇")
    fire = _pull(me, "Fire Energy")
    evolved = Pokemon(card_i=chand, played_turn=0, underneath=[lit, lamp])
    me.deck = [_pull(me, "Litwick") for _ in range(3)]
    me.hand.clear()
    me.active = Pokemon(card_i=pichu, played_turn=0)
    me.bench = [evolved, Pokemon(card_i=celebi, played_turn=0, energy=[fire])]
    assert game._roast_wants_playground(me, "a") is False
    assert game._choose_attack(me, foe, game.strats["a"]) is None
    me.active = Pokemon(card_i=celebi, played_turn=0, energy=[fire])
    me.bench = [evolved, Pokemon(card_i=pichu, played_turn=0)]
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None and chosen.name == "Time Distortion"


def test_asleep_pichu_uses_switch_to_bring_celebi_active():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    celebi = _pull(me, "Celebi ◇")
    switch = _pull(me, "Switch")
    me.active = Pokemon(card_i=pichu, played_turn=0, status=ST_ASLEEP)
    me.bench = [Pokemon(card_i=celebi, played_turn=0)]
    me.hand.clear()
    assert game._roast_bring(me, "a", lambda mon: "celebi" in me.card(mon.card_i).name.lower()) is False
    assert me.card(me.active.card_i).name == "Pichu"
    me.hand.append(switch)
    assert game._roast_bring(me, "a", lambda mon: "celebi" in me.card(mon.card_i).name.lower()) is True
    assert me.card(me.active.card_i).name == "Celebi ◇"
