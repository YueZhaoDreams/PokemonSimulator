from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import FamilyRules, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, build_fallback_deck


def _game(rules=None) -> Game:
    c = build_fallback_deck(list(SET_C_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    return Game(
        c,
        d,
        rules or default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )


def _ko_named(game: Game, name: str) -> tuple[int, int]:
    slayer = game.players["b"]
    victim = game.players["a"]
    target = next(i for i, card in enumerate(victim.cards) if card.name == name)
    spare = next(i for i, card in enumerate(victim.cards) if card.name == "Clefairy" and i != target)
    victim.active = Pokemon(card_i=target, damage=999)
    victim.bench = [Pokemon(card_i=spare)]
    before = slayer.prizes_taken
    leftover = len(slayer.prizes)
    game._check_ko(victim, slayer, "a")
    return slayer.prizes_taken - before, leftover - len(slayer.prizes)


def test_family_rules_ex_prizes_on_by_default():
    rules = default_family_rules()
    assert rules.extra_prize_for_ex is True
    assert rules.prize_count == 3


def test_basic_ko_takes_one_prize():
    taken, cards = _ko_named(_game(), "Clefairy")
    assert taken == 1
    assert cards == 1


def test_ex_ko_takes_two_prizes():
    taken, cards = _ko_named(_game(), "Mewtwo ex")
    assert taken == 2
    assert cards == 2


def test_mega_ex_ko_takes_three_prizes_and_wins():
    game = _game()
    taken, cards = _ko_named(game, "Mega Clefable ex")
    assert taken == 3
    assert cards == 3
    assert game.winner == "b"
    assert game.reason == "took all prize cards"


def test_ex_ko_with_one_prize_left_wins():
    game = _game()
    slayer = game.players["b"]
    slayer.prizes = slayer.prizes[:1]
    slayer.prizes_taken = 2
    taken, cards = _ko_named(game, "Clefable ex")
    assert taken == 1
    assert cards == 1
    assert game.winner == "b"


def test_extra_prize_flag_off_is_one_each():
    rules = FamilyRules(extra_prize_for_ex=False)
    taken, cards = _ko_named(_game(rules), "Mewtwo ex")
    assert taken == 1
    assert cards == 1
    taken, cards = _ko_named(_game(rules), "Mega Clefable ex")
    assert taken == 1
    assert cards == 1
