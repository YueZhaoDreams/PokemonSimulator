"""1 Prankish + 1 Metronome + 1 Poké Pad: 3-way non-Rule-Box search."""

import importlib.util
from collections import Counter
from pathlib import Path
from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T60_NAMES, build_fallback_deck, fallback_named

PAD_TEXT = (
    "Search your deck for a Pokémon that doesn't have a Rule Box, reveal it, "
    "and put it into your hand. Then, shuffle your deck. "
    "(Pokémon ex, Pokémon V, etc. have Rule Boxes.)"
)
METRONOME_TEXT = "Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack."


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_c60_pad_metronome.py"
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


def test_printed_pad_and_metronome_sentences():
    pad = fallback_named("Poké Pad")
    assert parse_trainer_effects(PAD_TEXT) == [{"kind": "search_pokemon_no_rule_box"}]
    assert parse_trainer_effects(pad.text or "") == [{"kind": "search_pokemon_no_rule_box"}]
    clc = fallback_named("Clefable CLC")
    metro = next(a for a in clc.attacks if a.name == "Metronome")
    assert metro.text == METRONOME_TEXT


def test_pad_clc_list_is_one_prankish_one_clc_one_pad():
    rules = standard_60_rules()
    by_key = dict(LAB.variant_lists())
    assert list(by_key) == ["prankish2", "clc1", "pad", "pad_clc"]
    assert Counter(by_key["prankish2"]) == Counter(SET_C60_NAMES)
    pad_clc = by_key["pad_clc"]
    assert len(pad_clc) == 60
    assert pad_clc.count("Poké Pad") == 1
    assert pad_clc.count("Hop") == 1
    cards = build_fallback_deck(pad_clc)
    fables = [c for c in cards if c.name == "Clefable"]
    assert len(fables) == 2
    catalogs = Counter(c.catalog_id for c in fables)
    assert catalogs == Counter({"swsh2-75": 1, "clc-014": 1})
    assert copy_violations(cards, rules) == []
    pad = by_key["pad"]
    assert pad.count("Clefable") == 1
    assert pad.count("Poké Pad") == 1


def test_pad_finds_clefairy_not_ex():
    game = _game(LAB.pad_clc_list(), list(SET_T60_NAMES))
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    ex = next(i for i, c in enumerate(me.cards) if c.name == "Clefable ex")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [fairy, clc, ex]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert fairy in me.hand
    assert clc in me.deck
    assert ex in me.deck
    assert game.events.get("tutor_a:Clefairy:poke pad") == 1


def test_pad_finds_metronome_vs_phantom_not_prankish():
    game = _game(LAB.pad_clc_list(), list(SET_T60_NAMES), "phantom")
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    rcl = next(i for i, c in enumerate(me.cards) if c.catalog_id == "swsh2-75")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [rcl, clc]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert clc in me.hand
    assert rcl in me.deck
    assert game.events.get("pad_metro_a") == 1


def test_pad_finds_prankish_vs_demolish_not_metronome():
    game = _game(
        LAB.pad_clc_list(),
        ["Cornerstone Mask Ogerpon ex"] + ["Cubone"] * 59,
        "demolish",
    )
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    rcl = next(i for i, c in enumerate(me.cards) if c.catalog_id == "swsh2-75")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [clc, rcl]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert rcl in me.hand
    assert clc in me.deck
    assert game.events.get("pad_prankish_a") == 1


def test_pad_never_takes_a_rule_box_pokemon():
    game = _game(LAB.pad_clc_list(), list(SET_T60_NAMES))
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    ex = next(i for i, c in enumerate(me.cards) if c.name == "Clefable ex")
    mega = next(i for i, c in enumerate(me.cards) if c.name == "Mega Clefable ex")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [ex, mega, mewtwo]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert me.hand == []
    assert set(me.deck) == {ex, mega, mewtwo}


def test_party_plays_pad_over_hop_to_fetch_metronome():
    game = _game(LAB.pad_clc_list(), list(SET_T60_NAMES), "phantom")
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    clc = next(i for i, c in enumerate(me.cards) if c.catalog_id == "clc-014")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.hand = [pad, hop]
    me.deck = [clc]
    game.turn = 4
    game.first = "b"
    assert game._pick_trainer(me) == pad


def test_phantom_pad_still_hunts_dreepy():
    names = list(SET_T60_NAMES)
    if "Poké Pad" not in names:
        names[names.index("Nest Ball")] = "Poké Pad"
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("phantom"),
        StrategySpec.from_dict("party"),
        Random(1),
    )
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    dreepy = next(i for i, c in enumerate(me.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(me.cards) if c.name == "Drakloak")
    budew = next((i for i, c in enumerate(me.cards) if c.name == "Budew"), drak)
    me.active = Pokemon(card_i=budew, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [drak, dreepy]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert dreepy in me.hand
    assert drak in me.deck


def test_party_strategy_mentions_three_way_pad():
    text = StrategySpec.from_dict("party").description.lower()
    assert "poké pad" in text
    assert "metronome" in text
    assert "prankish" in text
    assert "rule box" in text


def test_pad_metronome_json_cells_follow_foe_order():
    import json

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-pad-metronome.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    assert list(blob["foes"]) == foes
    assert list(blob["cells"]) == ["prankish2", "clc1", "pad", "pad_clc"]
    assert blob["lock"].startswith("none")
    for row in blob["cells"].values():
        assert list(row) == foes
    assert blob["cells"]["pad_clc"]["t60"]["pad_metro"] > 0
    assert blob["cells"]["pad_clc"]["d60"]["pad_prankish"] > blob["cells"]["pad_clc"]["d60"]["pad_metro"]
    assert blob["cells"]["pad"]["t60"]["copy_dive"] == 0
    assert SET_C60_NAMES.count("Clefable") == 2
    assert SET_C60_NAMES.count("Poké Pad") == 0
