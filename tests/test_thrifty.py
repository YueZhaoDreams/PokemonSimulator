from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_A_NAMES, SET_B_NAMES, build_fallback_deck


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name.lower() == name.lower())


def _carpet_game(strat_a: StrategySpec, seed: int = 1) -> Game:
    a = build_fallback_deck(SET_A_NAMES)
    b = build_fallback_deck(SET_B_NAMES)
    return Game(a, b, default_family_rules(), strat_a, StrategySpec.from_dict("control"), Random(seed), trace=True)


def test_thrifty_strategy_knobs():
    strat = StrategySpec.from_dict("thrifty")
    assert strat.item_spend == 0.2
    assert strat.swallow_look == 3
    assert strat.search_aces == ["Dondozo"]
    assert strat.hold_as_energy is True
    assert strat.bench_fill == 0
    assert strat.insurance_bench == 1
    assert strat.backups == ["Orthworm", "Flutter Mane"]
    assert strat.insurance_non_fuel is True


def test_thrifty_opening_does_not_fill_the_bench():
    """Basics stay in hand as Family Cup energy until they are the intended attacker."""
    for seed in range(15):
        game = _carpet_game(StrategySpec.from_dict("thrifty"), seed)
        me = game.players["a"]
        assert me.active is not None
        names = [me.card(m.card_i).name for m in me.bench]
        assert set(names) <= {"Starly", "Orthworm"}
        assert names.count("Starly") <= 1
        if me.card(me.active.card_i).name == "Dondozo":
            continue
        # Ace in the opening 7 must be the Active, not left in hand.
        assert "Dondozo" not in [me.card(i).name for i in me.hand]


def test_thrifty_does_not_bench_energy_fuel():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    corphish = _idx(me, "Corphish")
    me.hand = [corphish]
    game._play_basics(me)
    assert me.bench == []
    assert corphish in me.hand


def test_thrifty_benches_non_water_as_insurance():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    oddish = _idx(me, "Oddish")
    corphish = _idx(me, "Corphish")
    me.hand = [oddish, corphish]
    game._play_basics(me)
    assert [me.card(m.card_i).name for m in me.bench] == ["Oddish"]
    assert corphish in me.hand


def test_thrifty_holds_balls_when_dondozo_is_in_play():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    me.hand = [_idx(me, "Ultra Ball"), _idx(me, "Poké Ball"), _idx(me, "Aipom")]
    assert game._pick_trainer(me) is None


def test_ultra_ball_benches_dondozo_same_turn():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    foe = game.players["b"]
    dondozo = _idx(me, "Dondozo")
    ball = _idx(me, "Ultra Ball")
    seel = _idx(me, "Corphish")
    bronzor = _idx(me, "Bronzor")
    oddish = _idx(me, "Oddish")
    me.active = Pokemon(card_i=seel, played_turn=0)
    me.bench = []
    me.hand = [ball, bronzor, oddish]
    me.deck = [dondozo]
    me.discard = []
    game._play_trainers(me, foe, "a")
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert "Dondozo" in names
    assert game.events.get("tutor:Dondozo:ultra ball", 0) == 1


def test_thrifty_holds_filler_items_when_ace_is_in_play():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    me.hand = [_idx(me, "Energy Switch"), _idx(me, "Lake Acuity")]
    assert game._pick_trainer(me) is None


def test_balanced_still_plays_filler_items():
    game = _carpet_game(StrategySpec.from_dict("balanced"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    me.hand = [_idx(me, "Energy Switch"), _idx(me, "Poké Ball")]
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name in {"Energy Switch", "Poké Ball"}


def test_swallow_look_three_leaves_the_rest_in_deck():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    dondozo = _idx(me, "Dondozo")
    psychic = _idx(me, "Water Energy")
    seel = _idx(me, "Corphish")
    bronzor = _idx(me, "Bronzor")
    oddish = _idx(me, "Oddish")
    gloom = _idx(me, "Aipom")
    me.active = Pokemon(card_i=dondozo, played_turn=0)
    me.hand = []
    me.bench = []
    me.deck = [psychic, seel, bronzor, oddish, gloom]
    game._swallow_energy(me, look=3, stop_when_powered=True)
    assert len(me.active.energy) <= 3
    assert len(me.deck) == 5 - len(me.active.energy)
    assert all(i in me.active.energy or i in me.deck for i in [psychic, seel, bronzor, oddish, gloom])
    # Only the looked-at prefix can be attached.
    assert gloom not in me.active.energy
    assert oddish not in me.active.energy


def test_thrifty_benches_orthworm_as_ko_insurance():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Dondozo"), played_turn=0)
    me.bench = []
    orth = _idx(me, "Orthworm")
    seel = _idx(me, "Corphish")
    me.hand = [orth, seel]
    game._play_basics(me)
    assert [me.card(m.card_i).name for m in me.bench] == ["Orthworm"]
    assert seel in me.hand


def test_thrifty_plays_orthworm_when_dondozo_is_gone():
    game = _carpet_game(StrategySpec.from_dict("thrifty"))
    me = game.players["a"]
    dondozo = _idx(me, "Dondozo")
    me.active = Pokemon(card_i=_idx(me, "Corphish"), played_turn=0)
    me.bench = []
    me.hand = [_idx(me, "Orthworm"), _idx(me, "Oddish")]
    me.deck = []
    me.prizes = [dondozo]
    me.discard = []
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert "Orthworm" in names
    assert "Oddish" not in names
