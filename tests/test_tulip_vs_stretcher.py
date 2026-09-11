from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T60_NAMES, build_fallback_deck, fallback_named


def _game() -> Game:
    return Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_party_night_stretcher_takes_mewtwo_over_energy():
    game = _game()
    me = game.players["a"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.discard = [nrg, mewtwo]
    me.hand = []
    game._night_stretcher(me, "a")
    assert mewtwo in me.hand
    assert nrg in me.discard


def test_party_night_stretcher_takes_energy_over_clefairy():
    game = _game()
    me = game.players["a"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.discard = [fairy, nrg]
    me.hand = []
    game._night_stretcher(me, "a")
    assert nrg in me.hand
    assert fairy in me.discard


def test_party_tulip_beats_hop_when_discard_is_fat():
    game = _game()
    me, foe = game.players["a"], game.players["b"]
    game.turn = 4
    game.first = "b"
    me.supporter_used = False
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"][:3]
    hop = next(i for i, c in enumerate(me.cards) if c.name == "Hop")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    extra = fallback_named("Tulip")
    me.cards.append(extra)
    tulip = len(me.cards) - 1
    me.discard = list(fairies)
    me.hand = [hop, tulip]
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    game._play_trainers(me, foe, "a")
    assert tulip in me.discard
    assert hop in me.hand
    assert all(i in me.hand for i in fairies)


def test_party_does_not_play_stretcher_for_special_energy_only():
    game = _game()
    me, foe = game.players["a"], game.players["b"]
    dce = fallback_named("Double Colorless Energy")
    me.cards.append(dce)
    dce_i = len(me.cards) - 1
    stretcher = next(i for i, c in enumerate(me.cards) if c.name == "Night Stretcher")
    me.discard = [dce_i]
    me.hand = [stretcher]
    me.active = Pokemon(
        card_i=next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex"),
        played_turn=0,
    )
    game._play_trainers(me, foe, "a")
    assert stretcher in me.hand
    assert dce_i in me.discard
