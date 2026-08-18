from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import build_fallback_deck, fallback_named


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name.lower() == name.lower())


def _nuzzle_idx(player) -> int:
    return next(
        i
        for i, card in enumerate(player.cards)
        if card.name == "Pikachu" and any(atk.name == "Volt Tackle" for atk in card.attacks)
    )


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
        StrategySpec.from_dict("nuzzle"),
        Random(seed),
        trace=True,
    )


def test_nuzzle_strategy_knobs():
    strat = StrategySpec.from_dict("nuzzle")
    assert strat.hold_as_energy is True
    assert strat.search_aces == ["Pikachu"]
    assert strat.insurance == ["Wailmer", "Sudowoodo", "Relicanth"]
    assert strat.insurance_bench == 2
    assert strat.insurance_non_fuel is True
    assert strat.max_ace_copies == 1


def test_nuzzle_opening_does_not_fill_the_bench():
    for seed in range(12):
        game = _seed_game(seed)
        me = game.players["b"]
        assert me.active is not None
        assert me.bench == []


def test_only_one_pikachu_enters_play():
    game = _seed_game()
    me = game.players["b"]
    nuzzle = _nuzzle_idx(me)
    shock = _shock_idx(me)
    me.active = Pokemon(card_i=nuzzle, played_turn=0)
    me.bench = []
    me.hand = [shock, _idx(me, "Electrike"), _idx(me, "Plusle")]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert names.count("Pikachu") == 1
    assert shock in me.hand
    assert _idx(me, "Electrike") in me.hand


def test_starter_prefers_volt_tackle_pikachu():
    game = _seed_game()
    me = game.players["b"]
    nuzzle = _nuzzle_idx(me)
    shock = _shock_idx(me)
    picked = game._pick_starter(me, [shock, nuzzle], StrategySpec.from_dict("nuzzle"))
    assert picked == nuzzle


def test_volt_tackle_beats_nuzzle_once_payable():
    a = build_fallback_deck(["Dondozo"] + ["Seel"] * 10 + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Oddish"] * 9)
    nuzzle = fallback_named("pikachu-nuzzle")
    rest = build_fallback_deck(["Electrike"] * 10 + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 9)
    game = Game(
        a,
        [nuzzle] + rest,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict("nuzzle"),
        Random(1),
        trace=True,
    )
    me = game.players["b"]
    foe = game.players["a"]
    pika = next(i for i, card in enumerate(me.cards) if any(atk.name == "Volt Tackle" for atk in card.attacks))
    fuels = [i for i, card in enumerate(me.cards) if card.name == "Electrike"][:3]
    me.active = Pokemon(card_i=pika, played_turn=0, energy=list(fuels))
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("nuzzle"))
    assert atk is not None
    assert atk.name == "Volt Tackle"


def test_nuzzle_while_volt_tackle_is_not_payable():
    a = build_fallback_deck(["Dondozo"] + ["Seel"] * 10 + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Oddish"] * 9)
    nuzzle = fallback_named("pikachu-nuzzle")
    rest = build_fallback_deck(["Electrike"] * 10 + ["Shauna"] * 4 + ["Grass Energy"] * 4 + ["Cubone"] * 9)
    game = Game(
        a,
        [nuzzle] + rest,
        default_family_rules(),
        StrategySpec.from_dict("thrifty"),
        StrategySpec.from_dict("nuzzle"),
        Random(1),
        trace=True,
    )
    me = game.players["b"]
    foe = game.players["a"]
    pika = next(i for i, card in enumerate(me.cards) if any(atk.name == "Volt Tackle" for atk in card.attacks))
    fuel = next(i for i, card in enumerate(me.cards) if card.name == "Electrike")
    me.active = Pokemon(card_i=pika, played_turn=0, energy=[fuel])
    foe.active = Pokemon(card_i=_idx(foe, "Dondozo"), played_turn=0)
    atk = game._choose_attack(me, foe, StrategySpec.from_dict("nuzzle"))
    assert atk is not None
    assert atk.name == "Nuzzle"


def test_second_pikachu_pays_lightning_energy():
    game = _seed_game()
    me = game.players["b"]
    nuzzle = _nuzzle_idx(me)
    shock = _shock_idx(me)
    me.active = Pokemon(card_i=nuzzle, played_turn=0, energy=[])
    me.bench = []
    me.hand = [shock]
    chosen = game._choose_energy_card(me, me.active, StrategySpec.from_dict("nuzzle"))
    assert chosen == shock


def test_grass_energy_does_not_beat_lightning_pokemon():
    game = _seed_game()
    me = game.players["b"]
    nuzzle = _nuzzle_idx(me)
    grass = _idx(me, "Grass Energy")
    electrike = _idx(me, "Electrike")
    me.active = Pokemon(card_i=nuzzle, played_turn=0, energy=[])
    me.hand = [grass, electrike]
    chosen = game._choose_energy_card(me, me.active, StrategySpec.from_dict("nuzzle"))
    assert chosen == electrike


def test_nuzzle_benches_two_non_lightning_sponges():
    game = _seed_game()
    me = game.players["b"]
    me.active = Pokemon(card_i=_nuzzle_idx(me), played_turn=0)
    me.bench = []
    wailmer = _idx(me, "Wailmer")
    gible = _idx(me, "Gible")
    electrike = _idx(me, "Electrike")
    me.hand = [wailmer, gible, electrike]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.bench]
    assert names == ["Wailmer", "Gible"]
    assert electrike in me.hand


def test_call_family_only_fetches_pikachu():
    game = _seed_game()
    me = game.players["b"]
    pika = _nuzzle_idx(me)
    emolga = _idx(me, "Emolga")
    gible = _idx(me, "Gible")
    me.active = Pokemon(card_i=emolga, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [pika, gible]
    game._call_family(me, "b", count=2)
    assert [me.card(m.card_i).name for m in me.bench] == ["Pikachu"]
    assert gible in me.deck
