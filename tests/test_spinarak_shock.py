from random import Random

from app.engine.game import ST_POISONED, Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import fallback_named


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
    b.append(fallback_named("Spinarak"))
    b.append(fallback_named("Darkness Energy"))
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict("shock"),
        Random(seed),
        trace=True,
    )


def test_shock_plays_one_spinarak():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    bug = _idx(me, "Spinarak")
    me.active = Pokemon(card_i=shock, played_turn=0)
    me.bench = []
    me.hand = [bug]
    game._play_basics(me)
    assert any(game._is_spinarak(me.card(m.card_i)) for m in me.in_play())
    assert bug not in me.hand


def test_shock_opens_spinarak_over_wailmer_but_not_roselia():
    game = _seed_game()
    me = game.players["b"]
    bug = _idx(me, "Spinarak")
    wailmer = _idx(me, "Wailmer")
    rose = _idx(me, "Roselia")
    dark = _idx(me, "Darkness Energy")
    grass = next(i for i, card in enumerate(me.cards) if card.name == "Grass Energy")
    me.hand = [bug, wailmer, dark]
    picked = game._pick_starter(me, [bug, wailmer], StrategySpec.from_dict("shock"))
    assert picked == bug
    me.hand = [bug, rose, dark, grass]
    picked = game._pick_starter(me, [bug, rose], StrategySpec.from_dict("shock"))
    assert picked == rose


def test_unpaid_spinarak_gets_darkness_before_roselia():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    bug = _idx(me, "Spinarak")
    rose = _idx(me, "Roselia")
    fuels = [_idx(me, "Electrike"), _idx(me, "Lightning Energy")]
    me.active = Pokemon(card_i=shock, energy=list(fuels), played_turn=0)
    me.bench = [Pokemon(card_i=rose, played_turn=0), Pokemon(card_i=bug, played_turn=0)]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert game._is_spinarak(me.card(target.card_i))


def test_darkness_goes_to_spinarak_not_unpaid_pikachu():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    bug = _idx(me, "Spinarak")
    dark = _idx(me, "Darkness Energy")
    me.active = Pokemon(card_i=shock, played_turn=0)
    me.bench = [Pokemon(card_i=bug, played_turn=0)]
    me.hand = [dark]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert game._is_spinarak(me.card(target.card_i))
    energy_i = game._choose_energy_card(me, target, StrategySpec.from_dict("shock"))
    assert energy_i == dark


def test_stay_on_spinarak_to_poison_if_pikachu_cannot_shock():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    shock = _shock_idx(me)
    bug = _idx(me, "Spinarak")
    dark = _idx(me, "Darkness Energy")
    me.active = Pokemon(card_i=bug, energy=[dark], played_turn=0)
    me.bench = [Pokemon(card_i=shock, played_turn=0)]
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    game._retreat_shock(me, foe, "b")
    assert game._is_spinarak(me.card(me.active.card_i))


def test_poison_sting_poisons_dondozo():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    bug = _idx(me, "Spinarak")
    dark = _idx(me, "Darkness Energy")
    me.active = Pokemon(card_i=bug, energy=[dark], played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    assert game._spinarak_can_sting(me, me.active)
    game._attack(me, foe, "b")
    assert foe.active.status & ST_POISONED
    assert foe.active.damage == 10
