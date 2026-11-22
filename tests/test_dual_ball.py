"""Dual Ball uses the Delta Species sentence: two coins, one Basic per heads."""

import json
from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, build_kecleon_deck, fallback_named

DUAL_BALL = (
    "Flip 2 coins. For each head, search your deck for a Basic Pokémon card, "
    "show it to your opponent, and put it into your hand. Shuffle your deck afterward."
)


class _Rolls:
    def __init__(self, rolls: list[float]):
        self.rolls = list(rolls)
        self.shuffles = 0

    def random(self) -> float:
        return self.rolls.pop(0)

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


def _idx(player, name: str, skip: int = 0) -> int:
    found = [i for i, card in enumerate(player.cards) if card.name == name]
    return found[skip]


def test_delta_species_sentence_parses_two_coins():
    card = fallback_named("Dual Ball")
    assert card.text == DUAL_BALL
    assert card.catalog_id == "ex11-89"
    assert card.image == "https://assets.tcgdex.net/en/ex/ex11/89/low.webp"


def test_saved_deck_fills_blank_dual_ball_art(tmp_path, monkeypatch):
    """ex11-89 does not build a TCGdex path, so a stored blank stays blank unless pinned."""
    from app.catalog import fill_missing_card_image

    filled = fill_missing_card_image({"name": "Dual Ball", "catalog_id": "ex11-89", "image": None})
    assert filled["image"] == "https://assets.tcgdex.net/en/ex/ex11/89/low.webp"

    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    from app.db import connect, init_db

    init_db()
    with connect() as conn:
        raw = conn.execute("SELECT cards_json FROM decks WHERE id='seed-kecleon'").fetchone()["cards_json"]
        cards = json.loads(raw)
        for card in cards:
            if card.get("name") == "Dual Ball":
                card["image"] = None
        conn.execute(
            "UPDATE decks SET cards_json=? WHERE id='seed-kecleon'",
            (json.dumps(cards),),
        )
    init_db()
    with connect() as conn:
        stored = json.loads(
            conn.execute("SELECT cards_json FROM decks WHERE id='seed-kecleon'").fetchone()["cards_json"]
        )
    images = {card.get("image") for card in stored if card.get("name") == "Dual Ball"}
    assert images == {"https://assets.tcgdex.net/en/ex/ex11/89/low.webp"}
    assert parse_trainer_effects(DUAL_BALL) == [
        {
            "kind": "coin_search_basic_to_hand",
            "flips": 2,
            "exclude_baby": False,
            "shuffle": "after",
        }
    ]
    legends = (
        "Flip 2 coins. For each heads, search your deck for a Basic Pokémon, "
        "show it to your opponent, and put it into your hand. If you do, shuffle your deck afterward."
    )
    parsed = parse_trainer_effects(legends)[0]
    assert parsed["flips"] == 2
    assert parsed["shuffle"] == "if_found"
    expedition = (
        "Flip 2 coins. For each heads, search your deck for a Basic Pokémon card "
        "other than a Baby Pokémon card, show it to your opponent, and put it into your hand. "
        "Shuffle your deck afterward."
    )
    assert parse_trainer_effects(expedition)[0]["exclude_baby"] is True


def test_two_heads_take_kecleon_then_hoopa_and_leave_the_mega():
    game = _game()
    me = game.players["a"]
    mega = _idx(me, "M Gardevoir-EX")
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    latias = _idx(me, "Latias ex")
    energy = _idx(me, "Fire Energy")
    assert me.card(mega).is_basic is False
    me.hand = []
    me.deck = [mega, kecleon, hoopa, latias, energy]
    me.discard = []
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    me.bench = []
    rolls = _Rolls([0.0, 0.0])
    game.rng = rolls
    game._resolve_trainer(me, game.players["b"], fallback_named("Dual Ball"), who="a")
    assert [me.card(i).name for i in me.hand] == ["Kecleon", "Hoopa-EX"]
    assert {me.card(i).name for i in me.deck} == {"M Gardevoir-EX", "Latias ex", "Fire Energy"}
    assert game.events["dual_ball"] == 1
    assert game.events["dual_ball_basic"] == 2
    assert rolls.shuffles >= 1


def test_tails_and_a_mega_only_deck_do_not_take_a_card():
    game = _game()
    me = game.players["a"]
    mega = _idx(me, "M Gardevoir-EX")
    energy = _idx(me, "Fire Energy")
    me.hand = []
    me.deck = [mega, energy]
    me.discard = []
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    me.bench = []
    rolls = _Rolls([0.9, 0.9])
    game.rng = rolls
    game._resolve_trainer(me, game.players["b"], fallback_named("Dual Ball"), who="a")
    assert me.hand == []
    assert {me.card(i).name for i in me.deck} == {"M Gardevoir-EX", "Fire Energy"}
    assert game.events["dual_ball"] == 1
    assert game.events.get("dual_ball_basic") is None
    assert rolls.shuffles == 1

    me.deck = [mega, energy, _idx(me, "Kecleon")]
    rolls.rolls = [0.0, 0.0]
    game.events.clear()
    game._resolve_trainer(me, game.players["b"], fallback_named("Dual Ball"), who="a")
    assert [me.card(i).name for i in me.hand] == ["Kecleon"]
    assert "M Gardevoir-EX" in {me.card(i).name for i in me.deck}


def test_kecleon_plays_dual_ball_while_kecleon_is_still_in_the_deck():
    game = _game()
    me = game.players["a"]
    ball = fallback_named("Dual Ball")
    # The registered card is not in the built deck. Score the sentence itself.
    me.hand = []
    me.deck = [_idx(me, "Kecleon")]
    me.active = Pokemon(card_i=_idx(me, "Fezandipiti ex"), played_turn=0)
    me.bench = []
    assert game._kecleon_trainer_score(me, game.players["b"], ball) == 24.0
