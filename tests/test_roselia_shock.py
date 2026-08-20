from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name.lower() == name.lower())


def _shock_idx(player) -> int:
    return next(
        i
        for i, card in enumerate(player.cards)
        if card.name == "Pikachu" and any(atk.name == "Thunder Shock" for atk in card.attacks)
    )


def _seed_game(seed: int = 1) -> Game:
    payload = load_seed_payload()
    a = [Card.from_dict(c) for c in payload["a"]["cards"]]
    b = [Card.from_dict(c) for c in payload["b"]["cards"]]
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict("shock"),
        Random(seed),
        trace=True,
    )


def test_shock_plays_one_roselia():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    me.active = Pokemon(card_i=shock, played_turn=0)
    me.bench = []
    me.hand = [rose]
    game._play_basics(me)
    assert any(game._is_roselia(me.card(m.card_i)) for m in me.in_play())
    assert rose not in me.hand


def test_shock_opens_roselia_when_no_lightning_attacker():
    game = _seed_game()
    me = game.players["b"]
    rose = _idx(me, "Roselia")
    wailmer = _idx(me, "Wailmer")
    grass = _idx(me, "Grass Energy")
    me.hand = [rose, wailmer, grass]
    picked = game._pick_starter(me, [rose, wailmer], StrategySpec.from_dict("shock"))
    assert picked == rose


def test_shock_still_opens_pikachu_over_roselia():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    grass = _idx(me, "Grass Energy")
    me.hand = [shock, rose, grass]
    picked = game._pick_starter(me, [shock, rose], StrategySpec.from_dict("shock"))
    assert picked == shock


def test_unpaid_roselia_gets_the_extra_grass():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    fuels = [_idx(me, "Electrike"), _idx(me, "Lightning Energy")]
    me.active = Pokemon(card_i=shock, energy=list(fuels), played_turn=0)
    me.bench = [Pokemon(card_i=rose, played_turn=0)]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert game._is_roselia(me.card(target.card_i))


def test_scent_ready_roselia_loads_benched_pikachu():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    grass = _idx(me, "Grass Energy")
    me.active = Pokemon(card_i=rose, energy=[grass], played_turn=0)
    me.bench = [Pokemon(card_i=shock, played_turn=0)]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert me.card(target.card_i).name == "Pikachu"


def test_stay_on_roselia_to_scent_if_pikachu_cannot_shock():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    grass = _idx(me, "Grass Energy")
    me.active = Pokemon(card_i=rose, energy=[grass], played_turn=0)
    me.bench = [Pokemon(card_i=shock, played_turn=0)]
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    game._retreat_shock(me, foe, "b")
    assert game._is_roselia(me.card(me.active.card_i))


def test_retreat_from_roselia_into_payable_thunder_shock():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    shock = _shock_idx(me)
    rose = _idx(me, "Roselia")
    grass = _idx(me, "Grass Energy")
    fuels = [_idx(me, "Electrike"), _idx(me, "Lightning Energy")]
    me.active = Pokemon(card_i=rose, energy=[grass], played_turn=0)
    me.bench = [Pokemon(card_i=shock, energy=list(fuels), played_turn=0)]
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    game._retreat_shock(me, foe, "b")
    assert me.card(me.active.card_i).name == "Pikachu"


def test_soothing_scent_puts_dondozo_asleep():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    rose = _idx(me, "Roselia")
    grass = _idx(me, "Grass Energy")
    me.active = Pokemon(card_i=rose, energy=[grass], played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    assert game._roselia_can_scent(me, me.active)
    game._attack(me, foe, "b")
    from app.engine.game import ST_ASLEEP

    assert foe.active.status & ST_ASLEEP
