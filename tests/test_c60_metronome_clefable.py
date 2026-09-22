"""1-of Metronome Clefable on the C60 2-of slot: we choose the copy."""

from collections import Counter
from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named, c60_names_before_bounce

METRONOME_TEXT = "Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack."


def _load_lab():
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_c60_metronome.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load_lab()


def _game(a_names, b_names, foe_strat: str = "phantom") -> Game:
    return Game(
        build_fallback_deck(a_names),
        build_fallback_deck(b_names),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        Random(1),
        trace=True,
    )


def test_metronome_parses_printed_choose_wording():
    effects = parse_effects(METRONOME_TEXT)
    assert {"kind": "copy_active_attack"} in effects
    clc = fallback_named("Clefable CLC")
    twm = fallback_named("Clefable TWM")
    for card in (clc, twm):
        metro = next(a for a in card.attacks if a.name == "Metronome")
        assert metro.text == METRONOME_TEXT


def test_clc1_and_twm1_are_sixty_legal_two_clefable():
    rules = standard_60_rules()
    assert LAB.VARIANTS["prankish2"] == c60_names_before_bounce()
    for key, names in LAB.VARIANTS.items():
        cards = build_fallback_deck(names)
        assert len(names) == 60, key
        assert copy_violations(cards, rules) == [], key
        assert sum(1 for c in cards if c.name == "Clefable") == 2, key
        catalogs = [c.catalog_id for c in cards if c.name == "Clefable"]
        if key == "prankish2":
            assert catalogs == ["swsh2-75", "swsh2-75"]
        elif key == "clc1":
            assert Counter(catalogs) == Counter(["swsh2-75", "clc-014"])
        else:
            assert Counter(catalogs) == Counter(["swsh2-75", "sv06-079"])


def test_party_boss_gusts_dragapult_then_metronome_copies_dive():
    """Budew Active / Dreepy + Dragapult bench: HP-min is Dreepy; we Boss Dive."""
    game = _game(
        [
            "Clefable CLC",
            "Clefairy",
            "Psychic Energy",
            "Boss's Orders",
            "Hop",
            "Mewtwo ex",
        ]
        + ["Nest Ball"] * 24,
        ["Dragapult ex", "Dreepy", "Budew"] + ["Cubone"] * 27,
    )
    me, foe = game.players["a"], game.players["b"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    boss = next(i for i, c in enumerate(me.cards) if c.name == "Boss's Orders")
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    drap = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    budew = next(i for i, c in enumerate(foe.cards) if c.name == "Budew")
    me.active = Pokemon(card_i=fairy, energy=[fuel], played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    me.hand = [clc_i, boss, hop]
    me.energy_attached = False
    foe.active = Pokemon(card_i=budew)
    foe.bench = [Pokemon(card_i=dreepy), Pokemon(card_i=drap)]
    game.turn = 4

    hp_min = game._hp_min_bench(foe)
    assert hp_min is foe.bench[0]
    assert foe.card(hp_min.card_i).name == "Dreepy"
    target = game._metronome_boss_target(me, foe)
    assert target is not None
    assert foe.card(target.card_i).name == "Dragapult ex"

    picked = game._pick_trainer(me)
    assert picked == boss
    game._play_trainers(me, foe, "a")
    assert foe.card(foe.active.card_i).name == "Dragapult ex"
    assert game.events.get("boss_orders_a")

    game._evolve_party(me, foe, "a")
    assert me.card(me.active.card_i).catalog_id == "clc-014"
    assert game.events.get("metronome_evolve")

    game._maybe_retreat(me, foe, "a")
    assert me.card(me.active.card_i).catalog_id == "clc-014"
    game._attack(me, foe, "a")
    assert game.events.get("metronome:Phantom Dive")
    assert foe.active.damage == 200


def test_metronome_chooses_dive_over_jet_headbutt():
    game = _game(
        ["Clefable CLC", "Clefairy", "Psychic Energy"] + ["Hop"] * 27,
        ["Dragapult ex"] + ["Cubone"] * 29,
    )
    me, foe = game.players["a"], game.players["b"]
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    drap = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    me.active = Pokemon(card_i=clc_i, energy=[fuel], played_turn=0)
    foe.active = Pokemon(card_i=drap)
    metro = next(a for a in me.card(clc_i).attacks if a.name == "Metronome")
    resolved = game._resolved_attack(me, foe, metro)
    assert resolved.name == "Phantom Dive"
    dive = next(a for a in foe.card(drap).attacks if a.name == "Phantom Dive")
    jet = next(a for a in foe.card(drap).attacks if a.name == "Jet Headbutt")
    assert game._metronome_hit_score(me, foe, me.active, dive) > game._metronome_hit_score(
        me, foe, me.active, jet
    )


def test_ultra_ball_prefers_clc_vs_phantom_and_prankish_vs_demolish():
    names = (
        ["Clefable CLC", "Clefable", "Clefairy", "Ultra Ball"]
        + ["Psychic Energy"] * 4
        + ["Hop"] * 22
    )
    phantom = _game(names, ["Dragapult ex"] + ["Cubone"] * 29, "phantom")
    demolish = _game(names, ["Cornerstone Mask Ogerpon ex"] + ["Cubone"] * 29, "demolish")
    for game in (phantom, demolish):
        me = game.players["a"]
        clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
        rcl = next(
            i for i, c in enumerate(me.cards) if c.name == "Clefable" and c.catalog_id == "swsh2-75"
        )
        me.deck = [clc_i, rcl]
        me.hand = []
        me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Clefairy"))
        me.bench = []
    found_p = phantom._search(phantom.players["a"], lambda c: c.is_pokemon, source="ultra ball")
    found_d = demolish._search(demolish.players["a"], lambda c: c.is_pokemon, source="ultra ball")
    assert phantom.players["a"].card(found_p).catalog_id == "clc-014"
    assert demolish.players["a"].card(found_d).catalog_id == "swsh2-75"


def test_party_holds_boss_when_metronome_cannot_copy():
    game = _game(
        ["Clefable", "Clefairy", "Psychic Energy", "Boss's Orders", "Hop"] + ["Nest Ball"] * 25,
        ["Dragapult ex", "Dreepy", "Budew"] + ["Cubone"] * 27,
    )
    me, foe = game.players["a"], game.players["b"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    boss = next(i for i, c in enumerate(me.cards) if c.name == "Boss's Orders")
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    drap = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    budew = next(i for i, c in enumerate(foe.cards) if c.name == "Budew")
    me.active = Pokemon(card_i=fairy, energy=[fuel], played_turn=0)
    me.hand = [boss, hop]
    foe.active = Pokemon(card_i=budew)
    foe.bench = [Pokemon(card_i=dreepy), Pokemon(card_i=drap)]
    game.turn = 4
    assert game._metronome_boss_target(me, foe) is None
    picked = game._pick_trainer(me)
    assert picked == hop


def test_metronome_json_cells_follow_foe_order():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-metronome.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    assert list(blob["foes"]) == foes
    assert list(blob["cells"]) == ["prankish2", "clc1", "twm1"]
    assert blob["lock"].startswith("none")
    for row in blob["cells"].values():
        assert list(row) == foes
    assert blob["cells"]["clc1"]["t60"]["copy_dive"] > 0
    assert blob["cells"]["prankish2"]["t60"]["copy_dive"] == 0


def test_battle_cage_is_held_when_copying_dive():
    game = _game(
        ["Clefable CLC", "Clefairy", "Psychic Energy", "Battle Cage", "Hop"] + ["Nest Ball"] * 25,
        ["Dragapult ex", "Dreepy"] + ["Cubone"] * 28,
    )
    me, foe = game.players["a"], game.players["b"]
    clc_i = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    fuel = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    cage = next(i for i, c in enumerate(me.cards) if c.name == "Battle Cage")
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    drap = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    me.active = Pokemon(card_i=clc_i, energy=[fuel], played_turn=0)
    me.hand = [cage, hop]
    me.deck = [i for i in range(len(me.cards)) if i not in {clc_i, fuel, cage, hop}]
    foe.active = Pokemon(card_i=drap)
    foe.bench = [Pokemon(card_i=dreepy)]
    game.turn = 4
    assert game._metronome_line_this_turn(me, foe)
    picked = game._pick_trainer(me)
    assert picked == hop
