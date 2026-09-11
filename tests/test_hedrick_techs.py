from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T_META_NAMES, build_fallback_deck, fallback_named


def _game() -> Game:
    return Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T_META_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_hedrick_list_is_printed_sixty():
    names = list(SET_T_META_NAMES)
    assert len(names) == 60
    assert names.count("Dudunsparce") == 1
    assert names.count("Crushing Hammer") == 4
    assert names.count("Fire Energy") == 3


def test_run_away_draw_parses_printed_wording():
    card = fallback_named("Dudunsparce")
    abi = next(a for a in card.abilities if a.name == "Run Away Draw")
    effects = parse_ability_effects(abi.text)
    assert effects[0]["kind"] == "draw_then_shuffle_self"
    assert effects[0]["amount"] == 3


def test_last_ditch_catch_parses_printed_wording():
    card = fallback_named("Meowth ex")
    abi = next(a for a in card.abilities if a.name == "Last-Ditch Catch")
    effects = parse_ability_effects(abi.text)
    assert effects[0]["kind"] == "search_supporter_on_bench"
    assert effects[0]["name_lock"] == "last-ditch"


def test_risky_ruins_parses_printed_wording():
    card = fallback_named("Risky Ruins")
    effects = parse_ability_effects(card.text)
    assert effects[0]["kind"] == "stadium_bench_damage"
    assert effects[0]["counters"] == 2
    assert effects[0]["exclude_type"] == "Darkness"


def test_rosa_and_red_card_print():
    rosa = fallback_named("Rosa's Encouragement")
    red = fallback_named("Special Red Card")
    assert "more Prize cards remaining" in rosa.text
    assert "3 or fewer Prize cards remaining" in red.text


def test_trading_places_and_tuck_tail_parse():
    assert {"kind": "switch_with_benched"} in parse_effects(
        "Switch this Pokémon with 1 of your Benched Pokémon."
    )
    assert {"kind": "return_self_to_hand"} in parse_effects(
        "Put this Pokémon and all attached cards into your hand."
    )


def test_risky_ruins_chips_clefairy_not_fez():
    game = _game()
    me = game.players["a"]
    ruins = next(i for i, c in enumerate(me.cards) if c.name == "Risky Ruins") if any(
        c.name == "Risky Ruins" for c in me.cards
    ) else None
    t = game.players["b"]
    ruins = next(i for i, c in enumerate(t.cards) if c.name == "Risky Ruins")
    game._set_stadium(t.card(ruins))
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fez = next(i for i, c in enumerate(t.cards) if c.name == "Fezandipiti ex")
    me.bench = [Pokemon(card_i=clef, played_turn=0)]
    game._apply_stadium_bench(me, me.bench[0])
    assert me.bench[0].damage == 20
    t.bench = [Pokemon(card_i=fez, played_turn=0)]
    game._apply_stadium_bench(t, t.bench[0])
    assert t.bench[0].damage == 0


def test_rosa_attaches_two_from_discard_to_dragapult():
    game = _game()
    me = game.players["b"]
    foe = game.players["a"]
    pult = next(i for i, c in enumerate(me.cards) if c.name == "Dragapult ex")
    fires = [i for i, c in enumerate(me.cards) if c.name == "Fire Energy"][:2]
    me.active = Pokemon(card_i=pult, played_turn=0)
    me.discard = list(fires)
    me.prizes = [0, 1, 2, 3, 4, 5]
    foe.prizes = [0, 1, 2]
    assert game._rosa_can_play(me, foe)
    game._rosa_encouragement(me, foe)
    assert len(me.active.energy) == 2
    assert not me.discard


def test_special_red_card_bottoms_hand_when_three_prizes():
    game = _game()
    foe = game.players["a"]
    foe.prizes = [0, 1, 2]
    foe.hand = foe.deck[:5]
    foe.deck = foe.deck[5:]
    before = len(foe.deck)
    game._special_red_card(foe)
    assert len(foe.hand) == 3
    assert len(foe.deck) == before + 2


def test_last_ditch_catch_searches_supporter_from_hand_bench():
    game = _game()
    me = game.players["b"]
    meow = next(i for i, c in enumerate(me.cards) if c.name == "Meowth ex")
    # Put a supporter in deck so search can hit.
    rosa = next(i for i, c in enumerate(me.cards) if c.name == "Rosa's Encouragement")
    me.deck = [rosa]
    me.hand = [meow]
    me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Dreepy"), played_turn=0)
    me.bench = []
    me.hand.remove(meow)
    me.bench.append(Pokemon(card_i=meow, played_turn=game.turn))
    game._on_benched(me, me.bench[0], from_hand=True)
    assert game.events.get("last_ditch_catch") == 1
    assert rosa in me.hand


def test_run_away_draw_shuffles_self_when_another_body_is_out():
    game = _game()
    me = game.players["b"]
    dudu = next(i for i, c in enumerate(me.cards) if c.name == "Dudunsparce")
    dreepy = next(i for i, c in enumerate(me.cards) if c.name == "Dreepy")
    me.active = Pokemon(card_i=dreepy, played_turn=0)
    me.bench = [Pokemon(card_i=dudu, played_turn=0)]
    me.hand = []
    me.deck = list(range(10, 20))
    game._use_passive_abilities(me, "b", game.players["a"])
    assert game.events.get("run_away_draw") == 1
    assert all(me.card(m.card_i).name != "Dudunsparce" for m in me.in_play())
    assert len(me.hand) == 3
