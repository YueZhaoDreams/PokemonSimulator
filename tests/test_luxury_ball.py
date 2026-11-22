"""Stormfront Luxury Ball: one Pokémon other than LV.X, then the discard lock."""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Card, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, build_kecleon_deck, fallback_named

LUXURY_BALL = (
    "Search your deck for a Pokémon (excluding Pokémon LV.X), show it to your opponent, "
    "and put it into your hand. Shuffle your deck afterward. "
    "If any Luxury Ball is in your discard pile, you can't play this card."
)


class _Rolls:
    def __init__(self):
        self.shuffles = 0

    def random(self) -> float:
        return 0.0

    def shuffle(self, seq) -> None:
        self.shuffles += 1
        seq.reverse()


def _game() -> Game:
    foe = build_fallback_deck(["Starly"] * 60)
    return Game(
        build_kecleon_deck(),
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(1),
    )


def _idx(player, name: str) -> int:
    return next(i for i, card in enumerate(player.cards) if card.name == name)


def _add(player, card: Card) -> int:
    player.cards.append(card)
    return len(player.cards) - 1


def _board(game: Game) -> None:
    me = game.players["a"]
    me.hand = []
    me.deck = []
    me.discard = []
    me.prizes = []
    me.bench = []
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    game.rng = _Rolls()


def test_stormfront_sentence_parses_the_discard_lock():
    card = fallback_named("Luxury Ball")
    assert card.text == LUXURY_BALL
    assert card.catalog_id == "dp7-86"
    assert card.image == "https://assets.tcgdex.net/en/dp/dp7/86/low.webp"
    assert parse_trainer_effects(LUXURY_BALL) == [
        {
            "kind": "search_pokemon_except_lvx",
            "exclude_lv_x": True,
            "unplayable_if_in_discard": "luxury ball",
        }
    ]


def test_takes_latios_and_leaves_lv_x_in_the_deck():
    game = _game()
    me = game.players["a"]
    _board(game)
    latios = _idx(me, "M Latios-EX")
    energy = _idx(me, "Fire Energy")
    lv_x = _add(
        me,
        Card(
            catalog_id="lvx-1",
            name="Pikachu LV.X",
            category="Pokemon",
            stage="LV.X",
            types=["Lightning"],
            hp=90,
        ),
    )
    me.deck = [lv_x, energy, latios]
    game._resolve_trainer(me, game.players["b"], fallback_named("Luxury Ball"), who="a")
    assert [me.card(i).name for i in me.hand] == ["M Latios-EX"]
    assert {me.card(i).name for i in me.deck} == {"Pikachu LV.X", "Fire Energy"}
    assert game.events["luxury_ball"] == 1
    assert game.events["luxury_ball_a"] == 1
    assert game.rng.shuffles >= 1


def test_lv_x_alone_is_not_taken_and_the_deck_is_shuffled():
    game = _game()
    me = game.players["a"]
    _board(game)
    energy = _idx(me, "Fire Energy")
    lv_x = _add(
        me,
        Card(
            catalog_id="lvx-1",
            name="Pikachu LV.X",
            category="Pokemon",
            stage="LV.X",
            types=["Lightning"],
            hp=90,
        ),
    )
    me.deck = [lv_x, energy]
    game._resolve_trainer(me, game.players["b"], fallback_named("Luxury Ball"), who="a")
    assert me.hand == []
    assert {me.card(i).name for i in me.deck} == {"Pikachu LV.X", "Fire Energy"}
    assert game.events["luxury_ball_miss"] == 1
    assert game.events.get("luxury_ball") is None
    assert game.rng.shuffles == 1


def test_a_copy_already_in_the_discard_cannot_be_played():
    game = _game()
    me = game.players["a"]
    _board(game)
    first = _add(me, fallback_named("Luxury Ball"))
    second = _add(me, fallback_named("Luxury Ball"))
    latios = _idx(me, "M Latios-EX")
    me.discard = [first]
    me.deck = [latios]
    game._resolve_trainer(me, game.players["b"], me.card(second), who="a", card_i=second)
    assert me.hand == []
    assert me.deck == [latios]
    assert game.events["luxury_ball_illegal"] == 1

    me.hand = [second]
    assert game._pick_trainer(me) is None


def test_the_copy_being_played_does_not_lock_itself():
    game = _game()
    me = game.players["a"]
    _board(game)
    ball = _add(me, fallback_named("Luxury Ball"))
    latios = _idx(me, "M Latios-EX")
    me.hand = [ball]
    me.deck = [latios]
    assert game._pick_trainer(me) == ball
    game._play_trainers(me, game.players["b"], "a")
    assert ball in me.discard
    assert latios in me.hand
    assert game.events["luxury_ball"] == 1
    assert game.events.get("luxury_ball_illegal") is None
