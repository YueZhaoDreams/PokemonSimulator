import pytest
from random import Random

from app.engine.game import Game, Pokemon, play_game
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_T60_NAMES,
    build_fallback_deck,
    fallback_named,
)


def test_card_definitions():
    iggly = fallback_named("Igglybuff")
    assert iggly.name == "Igglybuff"
    assert iggly.hp == 30
    assert iggly.retreat == 0
    assert len(iggly.attacks) == 1
    assert iggly.attacks[0].name == "Bouncy Circle"
    assert iggly.attacks[0].cost == []
    assert any(e.get("kind") == "benched_30hp_pokemon_times" for e in iggly.attacks[0].effects)

    mime = fallback_named("Mime Jr.")
    assert mime.name == "Mime Jr."
    assert mime.hp == 30
    assert mime.attacks[0].name == "Mimed Games"
    assert mime.attacks[0].cost == []

    cleffa = fallback_named("Cleffa")
    assert cleffa.name == "Cleffa"
    assert cleffa.hp == 30
    assert cleffa.attacks[0].name == "Grasping Draw"
    assert any(e.get("kind") == "draw_until_hand" for e in cleffa.attacks[0].effects)


def test_bouncy_circle_damage_scaling():
    deck_a = build_fallback_deck(["Mew ex", "Igglybuff", "Budew", "Cleffa", "Mime Jr."] + ["Igglybuff"] * 55)
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    iggly_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    foe.active = Pokemon(card_i=dondozo_i)

    # 1 Igglybuff on bench
    me.bench = [Pokemon(card_i=iggly_i)]
    attacks = game._attacks_for(me, me.active)
    bouncy = next(a for a in attacks if a.name == "Bouncy Circle")
    dmg = game._raw_attack_damage(me, foe, me.active, bouncy)
    assert dmg == 30  # 1 benched 30 HP Pokémon

    # 5 benched 30 HP Pokémon
    budew_i = next(i for i, c in enumerate(me.cards) if c.name == "Budew")
    cleffa_i = next(i for i, c in enumerate(me.cards) if c.name == "Cleffa")
    mime_i = next(i for i, c in enumerate(me.cards) if c.name == "Mime Jr.")
    me.bench = [
        Pokemon(card_i=iggly_i),
        Pokemon(card_i=budew_i),
        Pokemon(card_i=cleffa_i),
        Pokemon(card_i=mime_i),
        Pokemon(card_i=iggly_i),
    ]
    dmg_5 = game._raw_attack_damage(me, foe, me.active, bouncy)
    assert dmg_5 == 150  # 5 * 30 = 150 damage for 0 energy!


def test_mew_ex_copies_itchy_pollen_and_locks_items():
    deck_a = build_fallback_deck(["Mew ex", "Budew"] + ["Igglybuff"] * 58)
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    budew_i = next(i for i, c in enumerate(me.cards) if c.name == "Budew")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=budew_i)]
    foe.active = Pokemon(card_i=dondozo_i)

    attacks = game._attacks_for(me, me.active)
    pollen = next(a for a in attacks if a.name == "Itchy Pollen")
    assert pollen.cost == []
    assert game._raw_attack_damage(me, foe, me.active, pollen) == 10

    # Simulate attack
    game._attack(me, foe, "a")
    assert foe.pending_item_lock is True


def test_mew_ex_copies_grasping_draw():
    deck_a = build_fallback_deck(["Mew ex", "Cleffa"] + ["Igglybuff"] * 58)
    deck_b = build_fallback_deck(["Dondozo"] * 60)
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    cleffa_i = next(i for i, c in enumerate(me.cards) if c.name == "Cleffa")
    dondozo_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dondozo")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=cleffa_i)]
    foe.active = Pokemon(card_i=dondozo_i)
    me.hand = []  # Empty hand

    attacks = game._attacks_for(me, me.active)
    grasp = next(a for a in attacks if a.name == "Grasping Draw")
    assert grasp.cost == []

    # Execute attack directly through resolved logic
    for eff in grasp.effects:
        if eff.get("kind") == "draw_until_hand":
            target = int(eff.get("count") or 7)
            needed = max(0, target - len(me.hand))
            game._draw(me, needed)
    assert len(me.hand) == 7


def test_battle_cage_prevents_bench_damage_counters():
    deck_a = build_fallback_deck(["Mew ex", "Igglybuff", "Battle Cage"] + ["Igglybuff"] * 57)
    deck_b = build_fallback_deck(list(SET_T60_NAMES))
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(42),
    )
    me = game.players["a"]
    cage_i = next(i for i, c in enumerate(me.cards) if c.name == "Battle Cage")
    game._set_stadium(me.card(cage_i))
    assert game.stadium_name == "Battle Cage"
    assert game._stadium_blocks_bench_counters() is True


def test_full_game_mew_baby_runs_smoothly():
    deck_a_names = (
        ["Mew ex"] * 3
        + ["Igglybuff"] * 4
        + ["Budew"] * 3
        + ["Cleffa"] * 2
        + ["Mime Jr."] * 2
        + ["Buddy-Buddy Poffin"] * 4
        + ["Nest Ball"] * 4
        + ["Ultra Ball"] * 3
        + ["Night Stretcher"] * 3
        + ["Battle Cage"] * 3
        + ["Maximum Belt"]
        + ["Bravery Charm"] * 2
        + ["Arven"] * 4
        + ["Iono"] * 4
        + ["Boss's Orders"] * 3
        + ["Professor's Research"] * 4
        + ["Poké Pad"] * 2
        + ["Crushing Hammer"] * 4
        + ["Switch"] * 3
        + ["Counter Catcher"] * 2
    )
    assert len(deck_a_names) == 60

    deck_a = build_fallback_deck(deck_a_names)
    deck_b = build_fallback_deck(list(SET_T60_NAMES))
    res = play_game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(123),
    )
    assert res.winner in {"a", "b"}
    assert res.turns > 0


def test_mimed_games_resolution_and_selection():
    # Mew ex active with Mime Jr. and 2 Igglybuff on bench (Bouncy Circle = 60 dmg)
    deck_a = build_fallback_deck(["Mew ex", "Mime Jr.", "Igglybuff", "Igglybuff"] + ["Igglybuff"] * 56)
    # Foe only has Cornerstone Ogerpon in play (Demolish 140 dmg)
    deck_b = build_fallback_deck(list(SET_D60_NAMES))

    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]

    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    mime_i = next(i for i, c in enumerate(me.cards) if c.name == "Mime Jr.")
    iggly_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    oger_i = next(i for i, c in enumerate(foe.cards) if "ogerpon" in c.name.lower())

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=mime_i), Pokemon(card_i=iggly_i), Pokemon(card_i=iggly_i)]
    foe.active = Pokemon(card_i=oger_i)
    foe.bench = []

    mimed_games = next(a for a in me.card(mime_i).attacks if a.name == "Mimed Games")
    resolved = game._resolved_attack(me, foe, mimed_games)
    # Foe only has Demolish (140 dmg), so resolved MUST be Demolish!
    assert resolved.name == "Demolish"
    assert resolved.damage == 140

    # Since Demolish (140 dmg) > Bouncy Circle (2 babies = 60 dmg),
    # Mew ex should choose Mimed Games!
    strat = StrategySpec.from_dict("mew_baby")
    chosen = game._choose_attack(me, foe, strat)
    assert chosen is not None
    assert chosen.name == "Mimed Games"

    # Execute attack
    game._attack(me, foe, "a")
    assert foe.active.damage == 140


def test_mime_jr_tutor_priority_vs_cornerstone():
    deck_a = build_fallback_deck(["Mew ex", "Igglybuff", "Mime Jr."] + ["Igglybuff"] * 57)
    deck_b = build_fallback_deck(list(SET_D60_NAMES))
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("demolish"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    oger_i = next(i for i, c in enumerate(foe.cards) if "ogerpon" in c.name.lower())
    me.active = Pokemon(card_i=mew_i)
    me.bench = []
    foe.active = Pokemon(card_i=oger_i)
    foe.bench = []

    prefer = game._pokemon_search_prefer(me, "a")
    # Facing Cornerstone Stance without Mime Jr. in play: Mime Jr. MUST be prioritized!
    assert "Mime Jr." in prefer
    # Mime Jr. should appear before other babies because Bouncy Circle is blocked!
    assert prefer.index("Mime Jr.") < prefer.index("Igglybuff")


def test_mimed_games_seizes_lethal_ko_over_bouncy():
    # Mew ex active with Mime Jr. + 2 Igglybuff (Bouncy Circle = 60 dmg)
    deck_a = build_fallback_deck(["Mew ex", "Mime Jr.", "Igglybuff", "Igglybuff"] + ["Igglybuff"] * 56)
    deck_b = build_fallback_deck(list(SET_T60_NAMES))
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    mime_i = next(i for i, c in enumerate(me.cards) if c.name == "Mime Jr.")
    iggly_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    drag_i = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=mime_i), Pokemon(card_i=iggly_i)]
    foe.active = Pokemon(card_i=drag_i)
    foe.bench = []

    # Set Dragapult HP so that 70 dmg is a lethal KO, but 60 dmg (Bouncy Circle) is not!
    # Dragapult max HP is 320. If damage is 250, remaining HP is 70.
    foe.active.damage = 250
    strat = StrategySpec.from_dict("mew_baby")
    chosen = game._choose_attack(me, foe, strat)
    assert chosen is not None
    # Jet Headbutt deals 70, which exactly KOs Dragapult (250 + 70 = 320)!
    assert chosen.name == "Mimed Games"


def test_bouncy_chosen_when_foe_has_weak_attack():
    # Mew ex active with Mime Jr. + 4 Igglybuff (Bouncy Circle = 120 dmg)
    deck_a = build_fallback_deck(["Mew ex", "Mime Jr."] + ["Igglybuff"] * 58)
    deck_b = build_fallback_deck(list(SET_T60_NAMES))
    game = Game(
        deck_a,
        deck_b,
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(42),
    )
    me = game.players["a"]
    foe = game.players["b"]
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    mime_i = next(i for i, c in enumerate(me.cards) if c.name == "Mime Jr.")
    iggly_i = next(i for i, c in enumerate(me.cards) if c.name == "Igglybuff")
    # Foe has Budew active (Itchy Pollen 10 dmg)
    budew_foe_i = next(i for i, c in enumerate(foe.cards) if c.name == "Budew")

    me.active = Pokemon(card_i=mew_i)
    me.bench = [Pokemon(card_i=mime_i)] + [Pokemon(card_i=iggly_i)] * 4  # 5 benched = 150 dmg
    foe.active = Pokemon(card_i=budew_foe_i)
    foe.bench = []

    strat = StrategySpec.from_dict("mew_baby")
    chosen = game._choose_attack(me, foe, strat)
    assert chosen is not None
    # Bouncy Circle deals 150 (or KOs 30 HP Budew), easily beating Mimed Games 10 dmg!
    assert chosen.name == "Bouncy Circle"


