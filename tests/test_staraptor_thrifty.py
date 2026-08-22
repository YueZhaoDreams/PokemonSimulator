from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import fallback_named


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name.lower() == name.lower())


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


def test_power_blast_parses_discard_energy():
    effects = parse_effects("Discard an Energy from this Pokémon.")
    assert {"kind": "discard_energy", "count": 1} in effects


def test_tailspin_away_parses_prevent_basic():
    effects = parse_effects(
        "During your opponent's next turn, prevent all damage done to this Pokémon by attacks from Basic Pokémon."
    )
    assert {"kind": "prevent_basic_damage"} in effects


def test_fallback_staraptor_is_paldea_evolved():
    card = fallback_named("Staraptor")
    assert card.catalog_id == "sv01-150"
    assert card.hp == 150
    assert [a.name for a in card.attacks] == ["Tailspin Away", "Power Blast"]


def test_thrifty_plays_one_starly():
    game = _seed_game()
    me = game.players["a"]
    dondozo = _idx(me, "Dondozo")
    bird = _idx(me, "Starly")
    me.active = Pokemon(card_i=dondozo, played_turn=0)
    me.bench = []
    me.hand = [bird]
    game._play_basics(me)
    assert any(me.card(m.card_i).name == "Starly" for m in me.in_play())
    assert bird not in me.hand


def test_boomerang_returns_after_power_blast():
    game = _seed_game()
    me = game.players["a"]
    foe = game.players["b"]
    bird = _idx(me, "Staraptor")
    boom = _idx(me, "Boomerang Energy")
    metal = _idx(me, "Metal Energy")
    aipom = _idx(me, "Aipom")
    me.active = Pokemon(card_i=bird, energy=[boom, metal, aipom], played_turn=0)
    foe.active = Pokemon(card_i=_idx(foe, "Pikachu"), played_turn=0)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("thrifty"))
    assert atk is not None
    assert atk.name == "Power Blast"
    game._attack(me, foe, "a")
    assert boom in me.active.energy
    assert game.events.get("boomerang_return", 0) == 1


def test_tailspin_blocks_basic_thunder_shock():
    game = _seed_game()
    me = game.players["a"]
    foe = game.players["b"]
    bird = _idx(me, "Staraptor")
    boom = _idx(me, "Boomerang Energy")
    metal = _idx(me, "Metal Energy")
    me.active = Pokemon(card_i=bird, energy=[boom, metal], played_turn=0)
    pika = next(
        i
        for i, card in enumerate(foe.cards)
        if card.name == "Pikachu" and any(atk.name == "Thunder Shock" for atk in card.attacks)
    )
    fuels = [_idx(foe, "Electrike"), next(i for i, card in enumerate(foe.cards) if card.name == "Lightning Energy")]
    foe.active = Pokemon(card_i=pika, energy=list(fuels), played_turn=0)
    game._attack(me, foe, "a")
    assert me.active.prevent_basic_damage
    shock = next(a for a in foe.card(pika).attacks if a.name == "Thunder Shock")
    assert game._effective_damage_for(foe, me, foe.active, shock) == 0
