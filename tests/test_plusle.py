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


def _nuzzle_idx(player) -> int:
    return next(
        i
        for i, card in enumerate(player.cards)
        if card.name == "Pikachu" and any(atk.name == "Volt Tackle" for atk in card.attacks)
    )


def _seed_game(strat_b: str = "shock", seed: int = 1) -> Game:
    payload = load_seed_payload()
    a = [Card.from_dict(c) for c in payload["a"]["cards"]]
    b = [Card.from_dict(c) for c in payload["b"]["cards"]]
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict(strat_b),
        Random(seed),
        trace=True,
    )


def test_plusle_parses_damage_counter_bonus():
    effects = parse_effects(
        "This attack does 10 more damage for each damage counter on your opponent's Active Pokémon.",
        "10+",
    )
    assert {"kind": "damage_counter_bonus", "per": 10} in effects


def test_plusle_formula_is_damage_plus_ten_times_weakness():
    """80 on Dondozo → (80+10)×2 = 180. 40 on Dondozo → 100, not a KO."""
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    plusle = _idx(me, "Plusle")
    dondozo = _idx(foe, "Dondozo")
    fuels = [_idx(me, "Electrike"), _idx(me, "Emolga")]
    me.active = Pokemon(card_i=plusle, played_turn=0, energy=list(fuels))
    foe.active = Pokemon(card_i=dondozo, played_turn=0, damage=80)
    atk = next(a for a in me.card(plusle).attacks if a.name == "Plus Damage")
    assert game._effective_damage(me, foe, atk) == 180
    foe.active.damage = 40
    assert game._effective_damage(me, foe, atk) == 100


def test_shock_prefers_thunder_shock_pikachu_over_nuzzle():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    nuzzle = _nuzzle_idx(me)
    picked = game._pick_starter(me, [nuzzle, shock], StrategySpec.from_dict("shock"))
    assert picked == shock


def test_shock_prefers_electrike_over_nuzzle_pikachu():
    game = _seed_game()
    me = game.players["b"]
    nuzzle = _nuzzle_idx(me)
    electrike = _idx(me, "Electrike")
    picked = game._pick_starter(me, [nuzzle, electrike], StrategySpec.from_dict("shock"))
    assert picked == electrike


def test_shock_benches_plusle_and_keeps_nuzzle_as_energy():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    nuzzle = _nuzzle_idx(me)
    plusle = _idx(me, "Plusle")
    me.active = Pokemon(card_i=shock, played_turn=0)
    me.bench = []
    me.hand = [plusle, nuzzle]
    game._play_basics(me)
    assert [me.card(m.card_i).name for m in me.bench] == ["Plusle"]
    assert nuzzle in me.hand


def test_shock_attaches_to_benched_plusle_once_thunder_shock_is_online():
    game = _seed_game()
    me = game.players["b"]
    shock = _shock_idx(me)
    plusle = _idx(me, "Plusle")
    fuel = [_idx(me, "Electrike"), _idx(me, "Grass Energy")]
    extra = _idx(me, "Gible")
    me.active = Pokemon(card_i=shock, played_turn=0, energy=list(fuel))
    me.bench = [Pokemon(card_i=plusle, played_turn=0)]
    me.hand = [extra]
    target = game._energy_target(me, StrategySpec.from_dict("shock"))
    assert target is me.bench[0]


def test_shock_retreats_into_plusle_for_the_knock_out():
    game = _seed_game()
    me = game.players["b"]
    foe = game.players["a"]
    shock = _shock_idx(me)
    plusle = _idx(me, "Plusle")
    pik_fuel = [_idx(me, "Emolga"), _idx(me, "Grass Energy")]
    plus_fuel = [_idx(me, "Electrike"), _idx(me, "Seel")]
    me.active = Pokemon(card_i=shock, played_turn=0, energy=list(pik_fuel))
    me.bench = [Pokemon(card_i=plusle, played_turn=0, energy=list(plus_fuel))]
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0, damage=80)
    game._maybe_retreat(me, foe, "b")
    assert me.card(me.active.card_i).name == "Plusle"


def test_fallback_plusle_has_the_scaling_text():
    card = fallback_named("Plusle")
    assert "damage counter" in (card.attacks[0].text or "").lower()
