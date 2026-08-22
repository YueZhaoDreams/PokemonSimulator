from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
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
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict("shock"),
        Random(seed),
        trace=True,
    )


def test_megaton_fall_parses_recoil_from_printed_text():
    effects = parse_effects("This Pokémon also does 50 damage to itself.")
    assert {"kind": "recoil", "amount": 50} in effects


def test_frigid_fangs_parses_energy_attack_lock():
    effects = parse_effects(
        "During your opponent's next turn, Pokémon that have 2 or less Energy attached can't attack. "
        "(This includes new Pokémon that come into play.)"
    )
    assert {"kind": "energy_attack_lock", "max_energy": 2} in effects


def test_fallback_walrein_is_surging_sparks_print():
    card = fallback_named("Walrein")
    assert card.catalog_id == "sv08-045"
    assert card.hp == 170
    assert card.evolves_from == "Sealeo"
    names = [a.name for a in card.attacks]
    assert names == ["Frigid Fangs", "Megaton Fall"]
    megaton = next(a for a in card.attacks if a.name == "Megaton Fall")
    assert megaton.damage == 170
    assert megaton.cost == ["Water", "Water"]


def test_shock_plays_one_spheal():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    pup = _idx(me, "Spheal")
    me.active = Pokemon(card_i=shock, played_turn=0)
    me.bench = []
    me.hand = [pup]
    game._play_basics(me)
    assert any(game._is_walrein_line(me.card(m.card_i)) for m in me.in_play())
    assert pup not in me.hand


def test_shock_opens_spheal_over_roselia_with_water():
    game = _seed_game()
    me = game.players["b"]
    pup = _idx(me, "Spheal")
    rose = _idx(me, "Roselia")
    water = next(i for i, card in enumerate(me.cards) if card.name == "Water Energy")
    me.hand = [pup, rose, water]
    picked = game._pick_starter(me, [pup, rose], StrategySpec.from_dict("shock"))
    assert picked == pup


def test_shock_still_opens_pikachu_over_spheal():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    pup = _idx(me, "Spheal")
    water = next(i for i, card in enumerate(me.cards) if card.name == "Water Energy")
    me.hand = [shock, pup, water]
    picked = game._pick_starter(me, [shock, pup], StrategySpec.from_dict("shock"))
    assert picked == shock


def test_unpaid_walrein_gets_water_before_plusle():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    wall = _idx(me, "Walrein")
    plusle = _idx(me, "Plusle")
    fuels = [_idx(me, "Electrike"), next(i for i, card in enumerate(me.cards) if card.name == "Lightning Energy")]
    me.active = Pokemon(card_i=shock, energy=list(fuels), played_turn=0)
    me.bench = [Pokemon(card_i=wall, played_turn=0), Pokemon(card_i=plusle, played_turn=0)]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert me.card(target.card_i).name == "Walrein"


def test_megaton_fall_kos_dondozo_then_recoils():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    wall = _idx(me, "Walrein")
    waters = [i for i, card in enumerate(me.cards) if card.name == "Water Energy"]
    me.active = Pokemon(card_i=wall, energy=list(waters[:2]), played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("shock"))
    assert atk is not None
    assert atk.name == "Megaton Fall"
    assert game._effective_damage(me, foe, atk) >= 160
    game._attack(me, foe, "b")
    assert foe.active.damage >= 160
    assert me.active.damage == 50


def test_frigid_fangs_blocks_low_energy_dondozo():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    wall = _idx(me, "Walrein")
    water = next(i for i, card in enumerate(me.cards) if card.name == "Water Energy")
    me.active = Pokemon(card_i=wall, energy=[water], played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    game._attack(me, foe, "b")
    assert "a" in game.energy_attack_lock
    assert game._energy_attack_blocked(foe, "a") is True


def test_shock_retreats_into_walrein_for_the_knock_out():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    shock = _shock_idx(me)
    wall = _idx(me, "Walrein")
    pik_fuel = [_idx(me, "Electrike"), next(i for i, card in enumerate(me.cards) if card.name == "Lightning Energy")]
    waters = [i for i, card in enumerate(me.cards) if card.name == "Water Energy"]
    me.active = Pokemon(card_i=shock, energy=list(pik_fuel), played_turn=0)
    me.bench = [Pokemon(card_i=wall, energy=list(waters[:2]), played_turn=0)]
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    game._maybe_retreat(me, foe, "b")
    assert me.card(me.active.card_i).name == "Walrein"
