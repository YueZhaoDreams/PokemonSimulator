"""Surging Sparks 76 Latias ex: Skyliner from the printed sentence, Nest Ball finds it."""

from random import Random

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, build_fallback_deck, fallback_named

PRINTED = "Your Basic Pokémon in play have no Retreat Cost."
EON = "During your next turn, this Pokémon can't attack."


def test_printed_skyliner_parses_basic_retreat_zero():
    card = fallback_named("Latias ex")
    assert card.catalog_id == "sv08-076"
    assert card.stage == "Basic"
    assert card.hp == 210
    assert card.retreat == 2
    assert card.types == ["Psychic"]
    assert card.weaknesses == [{"type": "Darkness", "value": "×2"}]
    assert card.resistances == [{"type": "Fighting", "value": "-30"}]
    assert card.image == "https://assets.tcgdex.net/en/sv/sv08/076/low.webp"
    abi = next(a for a in card.abilities if a.name == "Skyliner")
    assert abi.text == PRINTED
    eff = parse_ability_effects(abi.text)[0]
    assert eff["kind"] == "basic_retreat_zero"
    assert eff["basic_only"] is True
    assert eff["owner_only"] is True
    atk = card.attacks[0]
    assert atk.name == "Eon Blade"
    assert atk.damage == 200
    assert atk.cost == ["Psychic", "Psychic", "Colorless"]
    assert atk.text == EON
    assert any(e.get("kind") == "disable_self_attack_next_turn" for e in atk.effects)
    zone = next(a.text for a in fallback_named("Clefable ex").abilities if "lunar zone" in a.name.lower())
    moon = fallback_named("Moonlight Stadium").text
    beach = fallback_named("Beach Court").text
    for text in (zone, moon, beach):
        assert all(e.get("kind") != "basic_retreat_zero" for e in parse_ability_effects(text))


def _names() -> list[str]:
    return (
        ["Clefairy"] * 4
        + ["Latias ex", "Mewtwo ex", "Clefable ex", "Switch", "Nest Ball"]
        + ["Psychic Energy"] * 8
        + ["Hop"] * 14
    )


def _game(foe_strat: str = "party") -> Game:
    foe = ["Clefairy", "Dragapult ex", "Mewtwo ex"] + ["Psychic Energy"] * 6 + ["Hop"] * 21
    return Game(
        build_fallback_deck(_names()),
        build_fallback_deck(foe),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        Random(1),
        trace=True,
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def test_skyliner_zeros_only_your_basics():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = _idxs(me, "Clefairy")[0]
    latias = _idxs(me, "Latias ex")[0]
    evolved = _idxs(me, "Clefable ex")[0]
    bare = Pokemon(card_i=clef)
    stage = Pokemon(card_i=evolved)
    assert game._retreat_cost(me, bare) == 2
    me.bench = [Pokemon(card_i=latias, played_turn=0)]
    assert game._retreat_cost(me, bare) == 0
    assert game._retreat_cost(me, Pokemon(card_i=latias)) == 0
    assert me.card(evolved).retreat == 2
    assert game._retreat_cost(me, stage) == 2
    foe_clef = Pokemon(card_i=_idxs(foe, "Clefairy")[0])
    foe.active = foe_clef
    assert game._retreat_cost(foe, foe_clef) == 2
    me.bench.clear()
    assert game._retreat_cost(me, bare) == 2
    assert game._prizes_for_ko(me.card(latias)) == 2


def test_empty_active_parties_off_skyliner_without_a_stadium():
    game = _game("phantom")
    me = game.players["a"]
    foe = game.players["b"]
    clefs = _idxs(me, "Clefairy")
    energies = _idxs(me, "Psychic Energy")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [
        Pokemon(card_i=clefs[1], played_turn=0),
        Pokemon(card_i=clefs[2], played_turn=0),
        Pokemon(card_i=_idxs(me, "Latias ex")[0], played_turn=0),
    ]
    me.hand = [energies[5], _idxs(me, "Switch")[0]]
    me.deck = list(energies[1:5])
    me.discard = []
    me.retreated = False
    foe.active = Pokemon(card_i=_idxs(foe, "Dragapult ex")[0], played_turn=0)
    game.turn = 4
    leaving = me.active
    game._use_abilities(me, foe, "a")
    assert game.events.get("skyliner_party_pivot") == 1
    assert game.events.get("moonlight_party_pivot") is None
    assert me.retreated is True
    assert me.active is not leaving
    assert me.card(me.active.card_i).name == "Clefairy"
    assert any(me.card(i).name == "Switch" for i in me.hand)
    assert me.discard == []


def test_do_not_open_on_latias_and_nest_waits_for_a_clefairy():
    game = _game()
    me = game.players["a"]
    clefs = _idxs(me, "Clefairy")
    latias = _idxs(me, "Latias ex")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    strat = game.strats["a"]
    opener = game._pick_starter(me, [latias, clefs[0], mewtwo], strat)
    assert me.card(opener).name == "Clefairy"
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [latias, clefs[1]]
    game._bench_basic_from_deck(me, "a", count=1, source="nest ball")
    assert me.card(me.bench[0].card_i).name == "Clefairy"
    me.deck = [latias, clefs[2], mewtwo]
    game._bench_basic_from_deck(me, "a", count=1, source="nest ball")
    assert me.card(me.bench[-1].card_i).name == "Latias ex"
    still = _idxs(me, "Latias ex")[0]
    # The benched copy is the same card; a second search must not take it again.
    assert still not in me.deck


def test_poffin_cannot_fetch_210_hp():
    game = _game()
    me = game.players["a"]
    clef = _idxs(me, "Clefairy")[1]
    latias = _idxs(me, "Latias ex")[0]
    me.active = Pokemon(card_i=_idxs(me, "Clefairy")[0], played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [latias, clef]
    game._bench_basic_from_deck(me, "a", count=1, max_hp=70, source="poffin")
    assert me.card(me.bench[0].card_i).name == "Clefairy"
    assert latias in me.deck


def test_latias_matrix_prefers_one_copy_and_an_ultra_ball():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-latias-ex.json").read_text()
    )
    assert blob["games"] == 3000
    assert blob["seed"] == 20260926
    assert blob["catalog_id"] == "sv08-076"
    assert blob["printed"] == PRINTED
    assert set(blob["cells"]) == {"lock", "latias2", "latias_ultra"}
    assert blob["lists"]["lock"].count("Moonlight Stadium") == 2
    assert blob["lists"]["latias2"].count("Latias ex") == 2
    assert blob["lists"]["latias_ultra"].count("Latias ex") == 1
    assert blob["lists"]["latias_ultra"].count("Ultra Ball") == 1
    wcomp = blob["weighted_competitive"]
    wall = blob["weighted_all"]
    assert max(wcomp, key=wcomp.get) == "latias_ultra"
    assert max(wall, key=wall.get) == "latias_ultra"
    cells = blob["cells"]
    lock = cells["lock"]
    mixed = cells["latias_ultra"]
    two = cells["latias2"]
    for foe in ("t60", "hedrick", "unl", "d60", "s60", "g"):
        assert mixed[foe]["a"] > lock[foe]["a"]
    assert two["d60"]["a"] < lock["d60"]["a"]
    assert two["hedrick"]["a"] > mixed["hedrick"]["a"]
    assert mixed["t60"]["eon"] < 30
    assert two["d60"]["eon"] == 0


def test_latias_for_two_stadiums_is_a_legal_sixty():
    names = list(SET_C60_NAMES)
    assert names.count("Moonlight Stadium") == 2
    for _ in range(2):
        names[names.index("Moonlight Stadium")] = "Latias ex"
    mixed = list(SET_C60_NAMES)
    mixed[mixed.index("Moonlight Stadium")] = "Latias ex"
    mixed[mixed.index("Moonlight Stadium")] = "Ultra Ball"
    rules = standard_60_rules()
    for pile in (names, mixed):
        assert len(pile) == 60
        assert copy_violations(build_fallback_deck(pile), rules) == []
    assert names.count("Latias ex") == 2
    assert names.count("Moonlight Stadium") == 0
    assert mixed.count("Latias ex") == 1
    assert mixed.count("Ultra Ball") == 1
    assert mixed.count("Moonlight Stadium") == 0
