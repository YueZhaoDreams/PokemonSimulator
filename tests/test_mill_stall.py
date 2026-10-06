"""Great Tusk mill stall. Counts come from the printed sentences."""

from random import Random

from app.engine.effects import (
    energy_provided,
    is_basic_energy,
    is_special_energy,
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)
from app.engine.game import Game, Pokemon
from app.engine.models import Attack
from app.engine.legality import copy_violations
from app.engine.models import default_family_rules, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import SET_MILL60_NAMES, build_fallback_deck, fallback_named

_LAND = (
    "Discard the top card of your opponent's deck. If you played an Ancient Supporter "
    "card from your hand during this turn, discard 3 more cards in this way."
)
_HORN = "Discard the top 2 cards of your opponent's deck."
_TUNNEL = "Flip 3 coins. For each heads, discard the top 3 cards of your opponent's deck."
_DIG = "Flip a coin. If heads, discard the top card of your opponent's deck."
_SADA = (
    "Choose up to 2 of your Ancient Pokémon and attach a Basic Energy card from your discard pile "
    "to each of them. If you attached any Energy in this way, draw 3 cards."
)
_GUIDANCE = "Look at the top 6 cards of your deck and put 2 of them into your hand. Discard the other cards."
_SISTERS = (
    "Look at the top 5 cards of your opponent's deck and discard any number of Item cards you find there. "
    "Your opponent shuffles the other cards back into their deck."
)


def _take(player, name: str, n: int = 1) -> list[int]:
    found = [i for i, card in enumerate(player.cards) if card.name == name][:n]
    assert len(found) == n
    for card_i in found:
        for zone in (player.deck, player.hand, player.discard, player.prizes):
            if card_i in zone:
                zone.remove(card_i)
    return found


def _game() -> Game:
    bench = ["Great Tusk", "Houndoom-EX", "Wugtrio", "Professor Sada's Vitality", "Explorer's Guidance"]
    me = build_fallback_deck(["Mew ex", "Wiglett"] + bench + ["Fire Energy"] * 6 + ["Hop"] * 16)
    foe = build_fallback_deck(["Dondozo"] + ["Nest Ball"] * 8 + ["Sobble"] * 21)
    return Game(
        foe,
        me,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(2),
        trace=True,
    )


def test_printed_sentences_keep_their_counts():
    land = parse_effects(_LAND)
    assert land[0]["kind"] == "mill_opponent"
    assert land[0]["count"] == 1
    assert land[0]["extra_if_ancient_supporter"] == 3
    horn = parse_effects(_HORN)
    assert {"kind": "mill_opponent", "count": 2} in horn
    tunnel = parse_effects(_TUNNEL)
    assert tunnel[0]["coins"] == 3
    assert tunnel[0]["count"] == 3
    dig = parse_effects(_DIG)
    assert dig[0]["coins"] == 1
    assert dig[0]["count"] == 1
    sada = parse_trainer_effects(_SADA)
    assert sada[0]["kind"] == "attach_energy_to_ancient"
    assert sada[0]["count"] == 2
    assert sada[0]["draw"] == 3
    guidance = parse_trainer_effects(_GUIDANCE)
    assert guidance[0] == {"kind": "look_top_keep", "look": 6, "keep": 2}
    sisters = parse_trainer_effects(_SISTERS)
    assert sisters[0] == {"kind": "discard_top_items", "look": 5}


def test_fallback_cards_use_those_sentences():
    tusk = fallback_named("Great Tusk")
    assert tusk.traits == ["Ancient"]
    assert tusk.attacks[0].name == "Land Collapse"
    assert tusk.attacks[0].text == _LAND
    assert any(e.get("extra_if_ancient_supporter") == 3 for e in tusk.attacks[0].effects)
    hound = fallback_named("Houndoom-EX")
    assert hound.attacks[0].text == _HORN
    assert fallback_named("Wugtrio").attacks[1].text == _TUNNEL
    assert fallback_named("Wiglett").attacks[0].text == _DIG
    assert fallback_named("Professor Sada's Vitality").traits == ["Ancient"]
    assert fallback_named("Explorer's Guidance").traits == ["Ancient"]
    assert fallback_named("Miss Fortune Sisters").text == _SISTERS


def test_houndoom_ex_gives_two_prizes():
    game = _game()
    assert game._prizes_for_ko(fallback_named("Houndoom-EX")) == 2
    assert game._prizes_for_ko(fallback_named("Great Tusk")) == 1
    assert game._prizes_for_ko(fallback_named("Mew ex")) == 2


def test_sada_is_not_professor_research_and_sets_the_flag():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    sada = _take(me, "Professor Sada's Vitality")[0]
    other = _take(me, "Hop")[0]
    me.hand = [sada, other]
    game.first = "a"
    game.turn = 2
    game.current = "b"
    assert game._commit_trainer(me, foe, "b", sada)
    assert other in me.hand
    assert me.ancient_supporter_played
    assert game.events.get("ancient_energy_draw", 0) == 0


def test_mew_copies_land_collapse_for_four_after_sada():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    mew = _take(me, "Mew ex")[0]
    tusk = _take(me, "Great Tusk")[0]
    fires = _take(me, "Fire Energy", 2)
    me.active = Pokemon(card_i=mew, energy=fires)
    me.bench = [Pokemon(card_i=tusk)]
    me.ancient_supporter_played = True
    before = len(foe.deck)
    game.current = "b"
    game._attack(me, foe, "b")
    assert len(foe.deck) == before - 4
    assert game.events.get("ancient_mill_extra", 0) == 1


def test_land_collapse_mills_one_without_the_flag():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    tusk = _take(me, "Great Tusk")[0]
    fires = _take(me, "Fire Energy", 2)
    me.active = Pokemon(card_i=tusk, energy=fires)
    me.bench = []
    me.ancient_supporter_played = False
    before = len(foe.deck)
    game.current = "b"
    game._attack(me, foe, "b")
    assert len(foe.deck) == before - 1


def test_melting_horn_mills_two():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    hound = _take(me, "Houndoom-EX")[0]
    fire = _take(me, "Fire Energy")[0]
    me.active = Pokemon(card_i=hound, energy=[fire])
    me.bench = []
    before = len(foe.deck)
    game.current = "b"
    game._attack(me, foe, "b")
    assert len(foe.deck) == before - 2


def test_undersea_tunnel_is_zero_three_six_or_nine():
    losses = []
    for seed in range(60):
        game = Game(
            build_fallback_deck(["Dondozo"] + ["Sobble"] * 29),
            build_fallback_deck(["Wugtrio", "Wiglett"] + ["Fire Energy"] * 6 + ["Hop"] * 22),
            default_family_rules(),
            StrategySpec.from_dict("balanced"),
            StrategySpec.from_dict("mill"),
            Random(seed),
        )
        me = game.players["b"]
        foe = game.players["a"]
        wug = _take(me, "Wugtrio")[0]
        fires = _take(me, "Fire Energy", 3)
        me.active = Pokemon(card_i=wug, energy=fires)
        me.bench = []
        before = len(foe.deck)
        game.current = "b"
        game._attack(me, foe, "b")
        losses.append(before - len(foe.deck))
    assert set(losses) <= {0, 3, 6, 9}
    assert 3.2 < (sum(losses) / len(losses)) < 5.8


def test_guidance_keeps_two_and_discards_the_other_four():
    game = _game()
    me = game.players["b"]
    wanted = _take(me, "Mew ex") + _take(me, "Great Tusk")
    junk = _take(me, "Hop", 4)
    rest = list(me.deck)
    me.deck = wanted + junk + rest
    me.hand.clear()
    me.active = None
    me.bench.clear()
    before = len(me.deck)
    game._look_top_keep(me, "b", 6, 2)
    assert len(me.hand) == 2
    assert {me.card(i).name for i in me.hand} == {"Mew ex", "Great Tusk"}
    assert len(me.deck) == before - 6
    assert sum(1 for i in me.discard if me.card(i).name == "Hop") >= 4


def test_sisters_discard_items_and_shuffle_the_rest_back():
    game = _game()
    foe = game.players["a"]
    items = _take(foe, "Nest Ball", 2)
    pokemon = _take(foe, "Sobble", 3)
    foe.deck = items + pokemon + list(foe.deck)
    before = len(foe.deck)
    game._discard_top_items(foe, 5)
    assert sum(1 for i in foe.discard if foe.card(i).name == "Nest Ball") == 2
    assert len(foe.deck) == before - 2
    assert all(i not in foe.discard for i in pokemon)


def _collapse_board(game: Game):
    me = game.players["b"]
    mew = _take(me, "Mew ex")[0]
    tusk = _take(me, "Great Tusk")[0]
    fires = _take(me, "Fire Energy", 2)
    me.active = Pokemon(card_i=mew, energy=fires)
    me.bench = [Pokemon(card_i=tusk)]
    game.turn = 2
    game.first = "a"
    return me


def test_energy_goes_to_the_tusk_that_will_attack():
    game = _game()
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    wiglett = _take(me, "Wiglett")[0]
    me.active = Pokemon(card_i=tusk)
    me.bench = [Pokemon(card_i=wiglett)]
    assert game._mill_energy_target(me) is me.active
    me.active.energy = _take(me, "Fire Energy", 2)
    assert game._mill_paid(me, me.active)


def test_sada_is_for_the_land_collapse_turn():
    game = _game()
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    fires = _take(me, "Fire Energy", 2)
    me.active = Pokemon(card_i=tusk, energy=fires)
    me.bench = []
    me.hand = [i for i in me.hand if not me.card(i).is_energy]
    game.turn = 2
    game.first = "a"
    assert game._mill_sada_score(me) == 28
    game.turn = 1
    game.first = "b"
    assert game._mill_sada_score(me) == -18
    game.turn = 2
    game.first = "a"
    me.active = None
    assert game._mill_sada_score(me) == -18


def test_switch_brings_tusk_active_when_retreat_is_short():
    game = _game()
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    wiglett = _take(me, "Wiglett")[0]
    me.active = Pokemon(card_i=wiglett)
    me.bench = [Pokemon(card_i=tusk)]
    me.hand = [i for i in me.hand if not me.card(i).is_energy]
    assert game._mill_wants_switch(me)
    assert game._play_switch(me, "b")
    assert me.card(me.active.card_i).name == "Great Tusk"


def test_only_tusk_latias_and_meowth_take_the_board():
    game = _game()
    me = game.players["b"]
    strat = StrategySpec.from_dict("mill")
    assert game._wants_in_play(me, fallback_named("Houndoom-EX"), strat) is False
    assert game._wants_in_play(me, fallback_named("Mew ex"), strat) is False
    assert game._wants_in_play(me, fallback_named("Great Tusk"), strat) is True


def test_meowth_stays_in_hand_when_an_ancient_supporter_is_there():
    game = _game()
    me = game.players["b"]
    strat = StrategySpec.from_dict("mill")
    meowth = fallback_named("Meowth ex")
    sada = _take(me, "Professor Sada's Vitality")[0]
    me.hand = [sada]
    assert game._wants_in_play(me, meowth, strat) is False
    me.hand = []
    assert game._wants_in_play(me, meowth, strat) is True


def test_penny_picks_up_a_scratched_mew():
    game = _game()
    me = _collapse_board(game)
    me.active.damage = 50
    assert game._mill_wants_penny(me)


_LIVELY = "Each Basic Pokémon in play (both yours and your opponent's) gets +30 HP."
_CAPSULE = (
    "The Ancient Pokémon this card is attached to gets +60 HP, recovers from all Special Conditions, "
    "and can't be affected by any Special Conditions."
)
_DRUM = "Draw a card for each of your Ancient Pokémon in play."


def test_lively_stadium_and_capsule_use_the_printed_numbers():
    lively = parse_ability_effects(_LIVELY)
    assert lively[0] == {"kind": "stadium_hp", "amount": 30, "basic_only": True}
    assert {"kind": "draw_per_trait", "trait": "ancient"} in parse_trainer_effects(_DRUM)
    capsule = fallback_named("Ancient Booster Energy Capsule")
    assert capsule.text == _CAPSULE
    stadium = fallback_named("Lively Stadium")
    assert stadium.text == _LIVELY


def test_capsule_adds_60_only_on_ancient_and_stadium_adds_30_to_basics():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(
            ["Great Tusk", "Latias ex", "Ancient Booster Energy Capsule", "Lively Stadium"] + ["Hop"] * 6
        ),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(3),
    )
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    latias = _take(me, "Latias ex")[0]
    capsule = _take(me, "Ancient Booster Energy Capsule")[0]
    stadium = _take(me, "Lively Stadium")[0]
    me.active = Pokemon(card_i=tusk, tool=capsule)
    me.bench = [Pokemon(card_i=latias)]
    game._set_stadium(me.card(stadium), owner=me)
    assert game._max_hp(me, me.active) == 230
    assert game._max_hp(me, me.bench[0]) == 240
    me.bench[0].tool = capsule
    me.active.tool = None
    assert game._max_hp(me, me.bench[0]) == 240
    assert game._max_hp(me, me.active) == 170


def test_awakening_drum_draws_one_per_ancient_in_play():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(["Great Tusk", "Great Tusk", "Latias ex", "Awakening Drum"] + ["Hop"] * 10),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(4),
    )
    me = game.players["b"]
    tusks = _take(me, "Great Tusk", 2)
    latias = _take(me, "Latias ex")[0]
    drum = _take(me, "Awakening Drum")[0]
    me.active = Pokemon(card_i=tusks[0])
    me.bench = [Pokemon(card_i=tusks[1]), Pokemon(card_i=latias)]
    me.hand = []
    me.deck = _take(me, "Hop", 5)
    game._resolve_trainer(me, game.players["a"], me.card(drum), who="b", card_i=drum)
    assert len(me.hand) == 2
    assert game.events.get("draw_per_trait") == 2


def test_one_double_colorless_pays_land_collapse():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 19),
        build_fallback_deck(["Great Tusk", "Double Colorless Energy"] + ["Hop"] * 18),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(5),
    )
    me = game.players["b"]
    foe = game.players["a"]
    tusk = _take(me, "Great Tusk")[0]
    dce = _take(me, "Double Colorless Energy")[0]
    me.active = Pokemon(card_i=tusk)
    me.bench = []
    me.hand = [dce]
    game.turn = 2
    game.first = "a"
    game.current = "b"
    assert game._mill_sada_score(me) == 28
    me.active.energy = [dce]
    me.hand = []
    me.ancient_supporter_played = True
    before = len(foe.deck)
    game._attack(me, foe, "b")
    assert len(foe.deck) == before - 4


def test_earthen_vessel_discards_one_and_takes_two_fighting():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(
            ["Great Tusk", "Earthen Vessel", "Nest Ball"] + ["Fighting Energy"] * 4 + ["Hop"] * 8
        ),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(6),
    )
    me = game.players["b"]
    nest = _take(me, "Nest Ball")[0]
    fighting = _take(me, "Fighting Energy", 4)
    me.hand = [nest]
    me.deck = fighting
    game._earthen_vessel(me, "b")
    assert nest in me.discard
    assert sum(1 for i in me.hand if me.card(i).name == "Fighting Energy") == 2
    assert sum(1 for i in me.deck if me.card(i).name == "Fighting Energy") == 2


def test_mill_list_is_a_legal_sixty():
    assert len(SET_MILL60_NAMES) == 60
    assert SET_MILL60_NAMES.count("Great Tusk") == 4
    assert SET_MILL60_NAMES.count("Latias ex") == 2
    assert SET_MILL60_NAMES.count("Meowth ex") == 2
    assert SET_MILL60_NAMES.count("Mew ex") == 0
    assert SET_MILL60_NAMES.count("Professor Sada's Vitality") == 4
    assert SET_MILL60_NAMES.count("Explorer's Guidance") == 2
    assert SET_MILL60_NAMES.count("Ancient Booster Energy Capsule") == 4
    assert SET_MILL60_NAMES.count("Lively Stadium") == 4
    assert SET_MILL60_NAMES.count("Night Stretcher") == 4
    assert SET_MILL60_NAMES.count("Earthen Vessel") == 4
    assert SET_MILL60_NAMES.count("Awakening Drum") == 0
    assert SET_MILL60_NAMES.count("Hero's Cape") == 1
    assert SET_MILL60_NAMES.count("Max Potion") == 2
    assert SET_MILL60_NAMES.count("Double Colorless Energy") == 4
    assert SET_MILL60_NAMES.count("Stone Fighting Energy") == 4
    assert SET_MILL60_NAMES.count("Fighting Energy") == 13
    rules = standard_60_rules()
    assert copy_violations(build_fallback_deck(list(SET_MILL60_NAMES)), rules) == []
    deck = load_seed_deck("mill")
    assert deck["id"] == "seed-mill"
    assert load_seed_deck("tusk")["id"] == "seed-mill"
    assert len(deck["cards"]) == 60
    stones = [c for c in deck["cards"] if c["name"] == "Stone Fighting Energy"]
    assert len(stones) == 4
    assert stones[0]["catalog_id"] == "swsh4-164"
    assert "takes 20 less damage" in stones[0]["text"]


_STONE = (
    "As long as this card is attached to a Pokémon, it provides Fighting Energy.\n\n"
    "The Fighting Pokémon this card is attached to takes 20 less damage from attacks "
    "from your opponent's Pokémon (after applying Weakness and Resistance)."
)


def test_stone_fighting_energy_uses_the_printed_sentence():
    card = fallback_named("Stone Energy")
    assert card.name == "Stone Fighting Energy"
    assert card.text == _STONE
    assert card.stage.lower() == "special"
    parsed = parse_energy_effects(card.text)
    assert {"kind": "less_damage_taken", "pokemon_type": "Fighting", "amount": 20} in parsed
    assert energy_provided(card) == ["Fighting"]
    assert is_special_energy(card)
    assert not is_basic_energy(card)


def test_two_stones_reduce_damage_on_great_tusk_after_weakness():
    game = Game(
        build_fallback_deck(["Latias ex", "Dondozo"] + ["Sobble"] * 8),
        build_fallback_deck(["Great Tusk", "Latias ex"] + ["Stone Fighting Energy"] * 2 + ["Hop"] * 6),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(7),
    )
    me = game.players["b"]
    foe = game.players["a"]
    tusk = _take(me, "Great Tusk")[0]
    stones = _take(me, "Stone Fighting Energy", 2)
    bench_latias = _take(me, "Latias ex")[0]
    attacker = _take(foe, "Latias ex")[0]
    me.active = Pokemon(card_i=tusk, energy=stones)
    me.bench = [Pokemon(card_i=bench_latias)]
    foe.active = Pokemon(card_i=attacker)
    peck = Attack(name="Peck", cost=["Colorless"], damage=30)
    # Psychic weakness doubles 30 to 60, then each Stone takes off its printed 20.
    assert game._raw_attack_damage(foe, me, foe.active, peck) == 20
    me.bench[0].energy = list(me.active.energy)
    me.active.energy = []
    assert game._raw_attack_damage(foe, me, foe.active, peck) == 60
    me.active.energy = [me.bench[0].energy.pop()]
    assert game._raw_attack_damage(foe, me, foe.active, peck) == 40


def test_stone_or_double_colorless_is_what_gets_attached():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(
            ["Great Tusk", "Double Colorless Energy", "Stone Fighting Energy", "Fighting Energy"]
            + ["Hop"] * 6
        ),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(8),
    )
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    dce = _take(me, "Double Colorless Energy")[0]
    stone = _take(me, "Stone Fighting Energy")[0]
    fighting = _take(me, "Fighting Energy")[0]
    me.active = Pokemon(card_i=tusk)
    me.hand = [dce, stone, fighting]
    assert me.card(game._mill_energy_card(me, me.active)).name == "Double Colorless Energy"
    me.active.energy = [fighting]
    me.hand = [stone]
    assert me.card(game._mill_energy_card(me, me.active)).name == "Stone Fighting Energy"
    me.active.energy = [dce]
    assert me.card(game._mill_energy_card(me, me.active)).name == "Stone Fighting Energy"


def test_max_potion_heals_a_bare_tusk_and_a_low_tusk_that_can_reattach():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(
            ["Great Tusk", "Max Potion", "Double Colorless Energy", "Fighting Energy"] + ["Hop"] * 6
        ),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(9),
    )
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    fighting = _take(me, "Fighting Energy")[0]
    dce = _take(me, "Double Colorless Energy")[0]
    me.active = Pokemon(card_i=tusk, damage=40)
    me.hand = []
    assert game._mill_potion_target(me) is me.active
    game._heal_all(me, discard_energy=True)
    assert me.active.damage == 0
    me.active.damage = 30
    me.active.energy = [fighting]
    me.hand = []
    assert game._mill_potion_target(me) is None
    me.hand = [dce]
    assert game._mill_potion_target(me) is me.active
    game._heal_all(me, discard_energy=True)
    assert me.active.damage == 0
    assert me.active.energy == []
    assert fighting in me.discard


def test_sada_does_not_draw_when_double_colorless_already_finishes():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(
            ["Great Tusk", "Professor Sada's Vitality", "Double Colorless Energy", "Fighting Energy"]
            + ["Hop"] * 6
        ),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(10),
    )
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    fighting = _take(me, "Fighting Energy")[0]
    dce = _take(me, "Double Colorless Energy")[0]
    sada = fallback_named("Professor Sada's Vitality")
    me.active = Pokemon(card_i=tusk)
    me.hand = [dce]
    me.discard = [fighting]
    game._attach_energy_to_ancient(me, "b", parse_trainer_effects(sada.text)[0])
    assert me.active.energy == []
    assert fighting in me.discard
    assert game.events.get("ancient_energy_draw", 0) == 0


def test_heros_cape_goes_on_great_tusk():
    game = Game(
        build_fallback_deck(["Dondozo"] + ["Sobble"] * 9),
        build_fallback_deck(["Great Tusk", "Latias ex", "Hero's Cape", "Lively Stadium"] + ["Hop"] * 6),
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("mill"),
        Random(11),
    )
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    latias = _take(me, "Latias ex")[0]
    cape = fallback_named("Hero's Cape")
    stadium = _take(me, "Lively Stadium")[0]
    me.active = Pokemon(card_i=tusk)
    me.bench = [Pokemon(card_i=latias)]
    target = game._tool_target(me, "b", cape)
    assert target is me.active
    me.active.tool = _take(me, "Hero's Cape")[0]
    game._set_stadium(me.card(stadium), owner=me)
    assert game._max_hp(me, me.active) == 270


def test_guidance_waits_until_great_tusk_is_missing():
    game = _game()
    me = game.players["b"]
    tusk = _take(me, "Great Tusk")[0]
    me.active = Pokemon(card_i=tusk)
    me.deck = _take(me, "Hop", 16)
    assert game._mill_guidance_score(me) == -30
    me.hand = [tusk]
    me.active = None
    assert game._mill_guidance_score(me) == -30
    me.hand = []
    assert game._mill_guidance_score(me) == 22
