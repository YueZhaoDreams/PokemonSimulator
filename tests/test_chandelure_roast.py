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
INCENSE = (
    "Search your deck for an Evolution Pokémon, reveal it, and put it into your hand. "
    "Then, shuffle your deck."
)
DAWN = (
    "Search your deck for a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon, "
    "reveal them, and put them into your hand. Then, shuffle your deck."
)
HEAVY = (
    "Look at your face-down Prize cards. You may reveal a Basic Pokémon you find there, "
    "put it into your hand, and put this Hisuian Heavy Ball in its place as a face-down Prize card. "
    "(If you don't reveal a Basic Pokémon, put this card in the discard pile.) "
    "Then, shuffle your face-down Prize cards."
)
JACQ = (
    "Search your deck for up to 2 Evolution Pokémon, reveal them, and put them into your hand. "
    "Then, shuffle your deck."
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


def _grant(me, name: str) -> int:
    card = fallback_named(name)
    me.cards.append(card)
    idx = len(me.cards) - 1
    me.deck.append(idx)
    return idx


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
    assert parse_trainer_effects(INCENSE) == [{"kind": "search_evolution_pokemon", "count": 1}]
    assert parse_trainer_effects(DAWN) == [{"kind": "search_basic_stage1_stage2"}]
    assert parse_trainer_effects(HEAVY) == [{"kind": "hisuian_heavy_ball"}]
    assert not any(e.get("kind") == "search_evolution_pokemon" for e in parse_trainer_effects(JACQ))
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
    assert fallback_named("Evolution Incense").text == INCENSE
    assert fallback_named("Dawn").text == DAWN
    assert fallback_named("Hisuian Heavy Ball").text == HEAVY
    assert fallback_named("Jacq").text == JACQ
    assert fallback_named("Grand Tree").text == GRAND_TREE
    assert fallback_named("Rescue Scarf").text == RESCUE_SCARF


def test_roast_deck_is_sixty_and_pichu_is_playground():
    deck = build_roast_deck()
    assert len(deck) == 60
    assert copy_violations(deck, standard_60_rules()) == []
    assert StrategySpec.from_dict("roast").name == "roast"
    names = [card.name for card in deck]
    assert names.count("Pichu") == 3
    assert names.count("Cleffa") == 2
    assert names.count("Level Ball") == 3
    assert names.count("Dawn") == 4
    assert names.count("Evolution Incense") == 0
    assert names.count("Buddy-Buddy Poffin") == 3
    assert names.count("Broken Time-Space") == 3
    assert names.count("Slumbering Forest") == 1
    assert names.count("Fire Energy") == 7
    assert names.count("Grand Tree") == 0
    assert names.count("Colress's Tenacity") == 0
    assert names.count("Ultra Ball") == 1
    assert names.count("Hisuian Heavy Ball") == 1
    assert names.count("Energy Search") == 4
    assert names.count("Switch") == 1
    assert names.count("Jacq") == 0
    assert names.count("Nest Ball") == 0
    assert names.count("Slumbering Forest") == 1
    assert not any("Doll" in name for name in names)
    pichu = [card for card in deck if card.name == "Pichu"]
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
    for card in deck:
        if card.name != "Cleffa":
            continue
        assert any(effect.get("kind") == "shuffle_hand_then_draw" for attack in card.attacks for effect in attack.effects)
        assert "draw 6" in card.attacks[0].text.lower()
        assert any(ability.name == "Sweet Sleeping Face" for ability in card.abilities)
    forest = next(card for card in deck if card.name == "Slumbering Forest")
    assert {"kind": "sleep_check_two_coins"} in parse_ability_effects(forest.text)


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
    tree = _grant(me, "Grand Tree")
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


def test_playground_benches_four_litwick_then_celebi():
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
    assert celebi not in me.deck
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


def _ready_turn(game: Game) -> None:
    game.turn = 5
    game.first = "b"
    game.current = "a"
    game.players["a"].energy_attached = False


def test_one_lampent_hand_evolves_and_brings_celebi():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamp = _pull(me, "Lampent")
    chands = [_pull(me, "Chandelure") for _ in range(3)]
    celebi = _pull(me, "Celebi ◇")
    fire = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lamp, played_turn=0)]
    me.hand = chands + [celebi, fire]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert me.card(me.active.card_i).name == "Celebi ◇"
    assert len(me.active.energy) == 1
    assert [me.card(mon.card_i).name for mon in me.bench].count("Chandelure") == 1
    assert sum(1 for i in me.hand if me.card(i).name == "Chandelure") == 2
    assert len(foe.deck) == before - 3
    assert game.events.get("mountain_roasting", 0) == 1


def test_three_legal_lampent_bring_celebi_and_mill_nine():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamps = [_pull(me, "Lampent") for _ in range(3)]
    chands = [_pull(me, "Chandelure") for _ in range(3)]
    celebi = _pull(me, "Celebi ◇")
    fire = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lamp, played_turn=0) for lamp in lamps]
    me.hand = chands + [celebi, fire]
    _ready_turn(game)
    before = len(foe.deck)
    assert before >= 9
    assert game._roast_nine_ready(me, "a") is True
    game._roast_main(me, foe, "a")
    assert me.card(me.active.card_i).name == "Celebi ◇"
    assert len(me.active.energy) == 1
    assert [me.card(mon.card_i).name for mon in me.bench].count("Chandelure") == 3
    assert len(foe.deck) == before - 9
    assert game.events.get("mountain_roasting", 0) == 3
    assert game.events.get("roast_mill_wave:9", 0) == 1


def test_sleep_evolves_lampent_when_chandelure_already_has_a_target():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    ready = _pull(me, "Lampent")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=ready, played_turn=0), Pokemon(card_i=lit, played_turn=0)]
    me.hand = [lamp, chand]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    names = [me.card(mon.card_i).name for mon in me.bench]
    assert names.count("Lampent") == 1
    assert names.count("Chandelure") == 1
    assert chand not in me.hand
    assert len(foe.deck) == before - 3


def test_broken_time_space_evolves_litwick_to_chandelure_and_mills():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    bts = _pull(me, "Broken Time-Space")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=5)]
    me.hand = [lamp, chand, bts]
    me.deck = []
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert (game.stadium_name or "").lower() == "broken time-space"
    assert me.card(me.bench[0].card_i).name == "Chandelure"
    assert me.bench[0].underneath
    assert len(foe.deck) == before - 3
    assert game.events.get("mountain_roasting", 0) == 1
    assert game.events.get("roast_bts_a", 0) == 1


def test_petrel_finds_broken_time_space_before_another_dawn():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    petrel = _pull(me, "Team Rocket's Petrel")
    bts = _pull(me, "Broken Time-Space")
    dawn = _pull(me, "Dawn")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=5)]
    me.hand = [lamp, chand, petrel]
    me.deck = [bts, dawn]
    _ready_turn(game)
    before = len(foe.deck)
    assert game._roast_petrel_want(me, "a") == "Broken Time-Space"
    game._roast_main(me, foe, "a")
    assert (game.stadium_name or "").lower() == "broken time-space"
    assert me.card(me.bench[0].card_i).name == "Chandelure"
    assert len(foe.deck) == before - 3


def test_lampent_played_this_turn_cannot_take_chandelure():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    litwicks = [_pull(me, "Litwick") for _ in range(3)]
    lamps = [_pull(me, "Lampent") for _ in range(3)]
    chands = [_pull(me, "Chandelure") for _ in range(3)]
    celebi = _pull(me, "Celebi ◇")
    fire = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0) for lit in litwicks]
    me.hand = lamps + chands + [celebi, fire]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert [me.card(mon.card_i).name for mon in me.bench].count("Lampent") == 3
    assert all(card in me.hand for card in chands)
    assert len(foe.deck) == before


def test_active_litwick_evolves_and_same_turn_lampent_cannot_take_chandelure():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chands = [_pull(me, "Chandelure") for _ in range(2)]
    cleffa = _pull(me, "Cleffa")
    switch = _pull(me, "Switch")
    fuel = _pull(me, "Fire Energy")
    me.active = Pokemon(card_i=lit, played_turn=0)
    me.bench = [Pokemon(card_i=cleffa, played_turn=0)]
    me.hand = [lamp, switch] + chands
    me.deck = [fuel]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert me.card(me.active.card_i).name == "Cleffa"
    assert [me.card(mon.card_i).name for mon in me.bench].count("Lampent") == 1
    assert all(card in me.hand for card in chands)
    assert game._roast_celebi(me) is None
    assert len(foe.deck) == before

    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    me.active = Pokemon(card_i=lit, played_turn=0)
    me.bench = []
    me.hand = [lamp, chand]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert me.active is not None and me.card(me.active.card_i).name == "Lampent"
    assert chand in me.hand
    assert len(foe.deck) == before


def test_level_ball_finds_cleffa_before_lampent_when_the_wall_is_missing():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    lit = _pull(me, "Litwick")
    cleffa = _pull(me, "Cleffa")
    lamp = _pull(me, "Lampent")
    ball = _pull(me, "Level Ball")
    me.active = Pokemon(card_i=lit, played_turn=0)
    me.bench = []
    me.hand = [ball]
    me.deck = [lamp, cleffa]
    _ready_turn(game)
    game._level_ball(me, "a", 90)
    assert cleffa in me.hand
    assert lamp in me.deck


def test_playground_litwick_cannot_grand_tree_on_the_same_turn():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    tree = _grant(me, "Grand Tree")
    me.hand.clear()
    me.deck = [lit, lamp, chand]
    me.active = Pokemon(card_i=pichu, played_turn=0)
    me.bench = []
    _ready_turn(game)
    game._playground(me, foe, "a", user_first=True)
    game._set_stadium(me.card(tree), owner=me)
    game._use_grand_tree(me, "a")
    assert me.card(me.bench[0].card_i).name == "Litwick"
    assert game.events.get("grand_tree", 0) in (None, 0)
    assert game.events.get("mountain_roasting", 0) in (None, 0)


def test_two_incense_and_broken_time_space_mill_six():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lits = [_pull(me, "Litwick") for _ in range(2)]
    lamps = [_pull(me, "Lampent") for _ in range(2)]
    chands = [_pull(me, "Chandelure") for _ in range(2)]
    incense = [_grant(me, "Evolution Incense") for _ in range(4)]
    bts = _pull(me, "Broken Time-Space")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0) for lit in lits]
    me.hand = incense
    me.deck = lamps + chands
    _ready_turn(game)
    game._set_stadium(me.card(bts), owner=me)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    names = [me.card(mon.card_i).name for mon in me.bench]
    assert names.count("Chandelure") == 2
    assert len(foe.deck) == before - 6
    assert game.events.get("evolution_incense", 0) == 4
    assert game.events.get("mountain_roasting", 0) == 2


def test_incense_does_not_find_a_basic():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    other = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    incense = _grant(me, "Evolution Incense")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0)]
    me.hand = [incense]
    me.deck = [other, lamp]
    _ready_turn(game)
    game._roast_trainers(me, game.players["b"], "a")
    assert lamp in me.hand
    assert other in me.deck


def test_incense_takes_chandelure_when_spare_lampent_remain():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lits = [_pull(me, "Litwick") for _ in range(2)]
    lamps = [_pull(me, "Lampent") for _ in range(2)]
    spare = _pull(me, "Lampent")
    chands = [_pull(me, "Chandelure") for _ in range(2)]
    incense = [_grant(me, "Evolution Incense") for _ in range(2)]
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0) for lit in lits]
    me.hand = lamps + incense
    me.deck = [spare] + chands
    _ready_turn(game)
    game._roast_trainers(me, game.players["b"], "a")
    assert all(card in me.hand for card in chands)
    assert spare in me.deck


def test_incense_stays_unplayed_without_a_line():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    incense = _grant(me, "Evolution Incense")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = []
    me.hand = [incense]
    me.deck = [lamp, chand]
    _ready_turn(game)
    game._roast_trainers(me, game.players["b"], "a")
    assert incense in me.hand
    assert lamp in me.deck
    assert chand in me.deck


def test_dawn_finds_each_stage_and_the_chandelure_mills_on_a_legal_lampent():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamp_play = _pull(me, "Lampent")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    dawn = _grant(me, "Dawn")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lamp_play, played_turn=0)]
    me.hand = [dawn]
    me.deck = [lit, lamp, chand]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    names = [me.card(mon.card_i).name for mon in me.in_play()]
    assert names.count("Litwick") == 1
    assert names.count("Chandelure") == 1
    assert lamp in me.hand
    assert dawn in me.discard
    assert len(foe.deck) == before - 3
    assert game.events.get("dawn", 0) == 1
    assert game.events.get("mountain_roasting", 0) == 1


def test_dawn_cannot_evolve_the_basic_it_just_put_into_play():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    dawn = _grant(me, "Dawn")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.hand = [dawn]
    me.deck = [lit, lamp, chand]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert me.card(me.bench[0].card_i).name == "Litwick"
    assert lamp in me.hand
    assert chand in me.hand
    assert len(foe.deck) == before
    assert game.events.get("mountain_roasting", 0) in (None, 0)


def test_dawn_skips_a_stage_the_deck_does_not_have():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    dawn = _grant(me, "Dawn")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.hand = [dawn]
    me.deck = [lit, lamp]
    _ready_turn(game)
    game._roast_trainers(me, game.players["b"], "a")
    assert lit in me.hand
    assert lamp in me.hand
    assert game.events.get("dawn_cards", 0) == 2


def test_one_chandelure_mills_three_on_three_lampent():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamps = [_pull(me, "Lampent") for _ in range(3)]
    chand = _pull(me, "Chandelure")
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lamp, played_turn=0) for lamp in lamps]
    me.hand = [chand]
    _ready_turn(game)
    before = len(foe.deck)
    game._roast_main(me, foe, "a")
    assert [me.card(mon.card_i).name for mon in me.bench].count("Chandelure") == 1
    assert [me.card(mon.card_i).name for mon in me.bench].count("Lampent") == 2
    assert len(foe.deck) == before - 3


def test_level_ball_takes_lampent_when_playground_is_certain():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    ball = _pull(me, "Level Ball")
    me.active = Pokemon(card_i=pichu, played_turn=0)
    me.bench = []
    me.hand = [ball]
    me.deck = [lit, lamp]
    _ready_turn(game)
    assert game._roast_wants_playground(me, "a")
    game._roast_trainers(me, game.players["b"], "a")
    assert lamp in me.hand
    assert lit in me.deck
    assert ball in me.discard


def test_heavy_ball_takes_celebi_and_leaves_the_prized_litwick():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    lit = _pull(me, "Litwick")
    ball = _grant(me, "Hisuian Heavy Ball")
    me.deck.remove(ball)
    me.active = None
    me.bench = []
    me.hand = [ball]
    me.deck = []
    me.prizes = [lit, celebi]
    _ready_turn(game)
    assert game._roast_heavy_best(me) == (celebi, 100)
    game._roast_trainers(me, game.players["b"], "a")
    assert celebi in me.hand
    assert lit in me.prizes
    assert ball in me.prizes
    assert ball not in me.discard
    assert len(me.prizes) == 2


def test_heavy_ball_discards_itself_when_the_prize_is_not_basic():
    game = _game()
    me = game.players["a"]
    lamp = _pull(me, "Lampent")
    ball = _grant(me, "Hisuian Heavy Ball")
    me.deck.remove(ball)
    me.discard.append(ball)
    me.prizes = [lamp]
    game._hisuian_heavy_ball(me, "a", ball)
    assert ball in me.discard
    assert ball not in me.prizes
    assert lamp in me.prizes
    assert me.discard.count(ball) == 1


def test_heavy_ball_stays_in_hand_when_four_lines_and_celebi_are_already_out():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    celebi = _pull(me, "Celebi ◇")
    lines = [_pull(me, "Chandelure") for _ in range(4)]
    extra = _pull(me, "Litwick")
    ball = _grant(me, "Hisuian Heavy Ball")
    me.deck.remove(ball)
    me.active = Pokemon(card_i=pichu, played_turn=0)
    me.bench = [Pokemon(card_i=card_i, played_turn=0) for card_i in lines]
    me.bench.append(Pokemon(card_i=celebi, played_turn=0))
    me.hand = [ball]
    me.deck = []
    me.prizes = [extra]
    _ready_turn(game)
    assert game._roast_heavy_best(me) is None
    game._roast_trainers(me, game.players["b"], "a")
    assert ball in me.hand
    assert extra in me.prizes


def test_petrel_takes_heavy_ball_before_dawn_when_celebi_is_prized():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    celebi = _pull(me, "Celebi ◇")
    lamp = _pull(me, "Lampent")
    ball = _grant(me, "Hisuian Heavy Ball")
    dawn = _pull(me, "Dawn")
    me.deck.remove(ball)
    me.hand = []
    me.deck = [ball, dawn, lamp]
    me.prizes = [celebi]
    me.active = None
    me.bench = []
    assert game._roast_petrel_want(me, "a") == "Hisuian Heavy Ball"
    assert game._roast_trainer_score(me, "a", me.card(dawn)) == 100


def test_jacq_takes_lampent_then_chandelure_for_one_legal_litwick():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lit = _pull(me, "Litwick")
    lamp = _pull(me, "Lampent")
    chand = _pull(me, "Chandelure")
    jacq = _grant(me, "Jacq")
    me.deck.remove(jacq)
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=lit, played_turn=0)]
    me.hand = [jacq]
    me.deck = [lamp, chand]
    _ready_turn(game)
    assert game._roast_jacq_picks(me, "a") == ["Lampent", "Chandelure"]
    game._roast_trainers(me, game.players["b"], "a")
    assert lamp in me.hand
    assert chand in me.hand
    assert jacq in me.discard
    assert game.events.get("jacq_cards", 0) == 2


def test_jacq_takes_two_lampent_when_playground_will_bench_litwick():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    pichu = _pull(me, "Pichu")
    litwick = [_pull(me, "Litwick") for _ in range(3)]
    lamps = [_pull(me, "Lampent") for _ in range(2)]
    chand = _pull(me, "Chandelure")
    jacq = _grant(me, "Jacq")
    me.deck.remove(jacq)
    me.active = Pokemon(card_i=pichu, played_turn=0)
    me.bench = []
    me.hand = [jacq]
    me.deck = litwick + lamps + [chand]
    _ready_turn(game)
    assert game._roast_wants_playground(me, "a")
    assert game._roast_jacq_picks(me, "a") == ["Lampent", "Lampent"]
    game._roast_trainers(me, game.players["b"], "a")
    assert all(card_i in me.hand for card_i in lamps)
    assert all(card_i in me.deck for card_i in litwick)
    assert chand in me.deck
    assert jacq in me.discard


def test_jacq_takes_two_chandelure_when_lampent_are_already_out():
    game = _game()
    me = game.players["a"]
    _reclaim(me)
    cleffa = _pull(me, "Cleffa")
    lamps = [_pull(me, "Lampent") for _ in range(2)]
    chands = [_pull(me, "Chandelure") for _ in range(2)]
    jacq = _grant(me, "Jacq")
    me.deck.remove(jacq)
    me.active = Pokemon(card_i=cleffa, played_turn=0)
    me.bench = [Pokemon(card_i=card_i, played_turn=0) for card_i in lamps]
    me.hand = [jacq]
    me.deck = list(chands)
    _ready_turn(game)
    assert game._roast_jacq_picks(me, "a") == ["Chandelure", "Chandelure"]
    game._roast_trainers(me, game.players["b"], "a")
    assert all(card_i in me.hand for card_i in chands)
    assert jacq in me.discard
