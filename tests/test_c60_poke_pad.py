"""C60 1 Prankish Clefable → Poké Pad: printed search, party superposition, lists."""

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


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_c60_poke_pad.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


LAB = _load_lab()


def _pad_game() -> Game:
    return Game(
        build_fallback_deck(LAB.pad_list()),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_poke_pad_printed_sentence():
    card = fallback_named("Poké Pad")
    assert "doesn't have a Rule Box" in (card.text or "")
    parsed = parse_trainer_effects(PAD_TEXT)
    assert parsed == [{"kind": "search_pokemon_no_rule_box"}]
    assert parse_trainer_effects(card.text or "") == parsed


def test_locked_c60_keeps_two_prankish_and_no_pad():
    names = list(SET_C60_NAMES)
    assert names.count("Clefable") == 2
    assert names.count("Poké Pad") == 0
    pile = build_fallback_deck(names)
    assert sum(1 for c in pile if c.name == "Clefable") == 2
    assert all(any(a.name == "Prankish" for a in c.abilities) for c in pile if c.name == "Clefable")


def test_pad_trial_is_legal_sixty_with_one_clefable():
    rules = standard_60_rules()
    by_key = dict(LAB.variant_lists())
    assert list(by_key) == ["clefable2", "pad"]
    assert Counter(by_key["clefable2"]) == Counter(SET_C60_NAMES)
    pad = by_key["pad"]
    assert len(pad) == 60
    assert pad.count("Clefable") == 1
    assert pad.count("Poké Pad") == 1
    assert pad.count("Clefairy") == 4
    assert copy_violations(build_fallback_deck(pad), rules) == []
    assert copy_violations(build_fallback_deck(by_key["clefable2"]), rules) == []


def test_pad_finds_clefairy_not_ex_when_engine_is_missing():
    game = _pad_game()
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fable = next(i for i, c in enumerate(me.cards) if c.name == "Clefable")
    ex = next(i for i, c in enumerate(me.cards) if c.name == "Clefable ex")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [fairy, fable, ex]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert fairy in me.hand
    assert fable in me.deck
    assert ex in me.deck
    assert game.events.get("tutor_a:Clefairy:poke pad") == 1
    assert game.events.get("poke_pad_hit_a") == 1


def test_pad_finds_prankish_when_clefairy_is_already_in_play():
    game = _pad_game()
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fable = next(
        i
        for i, c in enumerate(me.cards)
        if c.name == "Clefable" and any(a.name == "Prankish" for a in c.abilities)
    )
    extra = [i for i, c in enumerate(me.cards) if c.name == "Clefairy" and i != fairy][0]
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [extra, fable]
    game._resolve_trainer(me, game.players["b"], me.card(pad), who="a", card_i=pad)
    assert fable in me.hand
    assert extra in me.deck
    assert game.events.get("tutor_a:Clefable:poke pad") == 1


def test_pad_never_takes_a_rule_box_pokemon():
    game = _pad_game()
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
    assert game.events.get("poke_pad_hit_a") is None


def test_party_plays_pad_over_ultra_ball_for_prankish():
    game = _pad_game()
    me = game.players["a"]
    pad = next(i for i, c in enumerate(me.cards) if c.name == "Poké Pad")
    ultra = next(i for i, c in enumerate(me.cards) if c.name == "Ultra Ball")
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fable = next(i for i, c in enumerate(me.cards) if c.name == "Clefable")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=0)]
    me.hand = [pad, ultra, hop, nrg]
    me.deck = [fable]
    me.supporter_used = True
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


def test_party_strategy_mentions_poke_pad_superposition():
    text = StrategySpec.from_dict("party").description.lower()
    assert "poké pad" in text
    assert "rule box" in text
    assert "prankish" in text


def test_poke_pad_json_keeps_the_two_clefable_lock():
    import json

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-poke-pad.json").read_text()
    )
    foes = ["t60", "hedrick", "unl", "d60", "s60", "g"]
    assert blob["games"] == 3000
    assert blob["seed"] == 20260922
    assert blob["rule_preset"] == "s60"
    assert blob["foes"] == foes
    assert list(blob["cells"]) == ["clefable2", "pad"]
    assert Counter(blob["lists"]["clefable2"]) == Counter(SET_C60_NAMES)
    assert blob["lists"]["pad"].count("Clefable") == 1
    assert blob["lists"]["pad"].count("Poké Pad") == 1
    for row in blob["cells"].values():
        assert list(row) == foes
    locked = blob["cells"]["clefable2"]
    pad = blob["cells"]["pad"]
    assert locked["t60"]["pad_hit"] == 0
    assert pad["t60"]["pad_hit"] > 500
    assert pad["t60"]["pad_clefable"] > pad["t60"]["pad_clefairy"]
    assert pad["d60"]["a"] > locked["d60"]["a"] + 0.01
    assert blob["weighted_competitive"]["pad"] > blob["weighted_competitive"]["clefable2"]
    assert SET_C60_NAMES.count("Clefable") == 2
    assert SET_C60_NAMES.count("Poké Pad") == 0
