"""Mew ex uses Penny only to pick up a charged Mew that would be Knocked Out next turn.

Printed Penny: put one Basic Pokémon and all attached cards into your hand.
With no Energy on the damaged Mew ex, Max Potion is the heal.
"""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

PENNY = "Put 1 of your Basic Pokémon and all attached cards into your hand."


def _game() -> Game:
    names = ["Mew ex", "Igglybuff", "Penny", "Max Potion", "Spiky Energy", "Arven", "Boss's Orders", "Iono", "Hero's Cape"]
    names += ["Hop"] * (60 - len(names))
    game = Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dondozo"] * 60),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )
    game.turn = 4
    return game


def _add(player, name: str) -> int:
    player.cards.append(fallback_named(name))
    return len(player.cards) - 1


def _take(player, name: str) -> int:
    for card_i, card in enumerate(player.cards):
        if card.name == name:
            return card_i
    return _add(player, name)


def _reset_me(me, active, hand, bench=None, deck=None) -> None:
    me.active = active
    me.bench = list(bench or [])
    me.hand = list(hand)
    me.deck = list(deck or [])
    me.discard = []
    me.prizes = []
    me.supporter_used = False
    me.item_lock = False
    me.energy_attached = False


def _quiet_foe(game: Game) -> None:
    foe = game.players["b"]
    foe.active = Pokemon(card_i=_take(foe, "Dondozo"))
    foe.bench = []
    foe.hand = []
    foe.deck = []


def _arm_dragapult(game: Game, attached: list[str], hand: list[str] | None = None, bench: list[tuple[str, list[str]]] | None = None) -> None:
    foe = game.players["b"]
    drag = _add(foe, "Dragapult ex")
    foe.active = Pokemon(card_i=drag, energy=[_add(foe, name) for name in attached])
    foe.bench = []
    for name, energies in bench or []:
        mon_i = _add(foe, name)
        foe.bench.append(Pokemon(card_i=mon_i, energy=[_add(foe, energy) for energy in energies]))
    foe.hand = [_add(foe, name) for name in (hand or [])]
    foe.deck = []


def _mew_board(game: Game, *, damage: int, energy: bool, hand: list[str], deck: list[str] | None = None):
    me = game.players["a"]
    mew_i = _take(me, "Mew ex")
    baby_i = _take(me, "Igglybuff")
    attached = [_take(me, "Spiky Energy")] if energy else []
    mew = Pokemon(card_i=mew_i, damage=damage, energy=attached)
    baby = Pokemon(card_i=baby_i)
    hand_ids = [_take(me, name) for name in hand]
    deck_ids = [_take(me, name) for name in (deck or [])]
    # A name reused from the board must not also sit in hand.
    used = {mew_i, baby_i, *attached, *hand_ids, *deck_ids}
    assert len(used) == 2 + len(attached) + len(hand_ids) + len(deck_ids)
    _reset_me(me, mew, hand_ids, bench=[baby], deck=deck_ids)
    return me


def test_penny_sentence_picks_up_a_basic_and_its_attachments():
    parsed = parse_trainer_effects(PENNY)[0]
    assert parsed["kind"] == "return_pokemon_to_hand"
    assert parsed["basic_only"] is True
    assert parsed["attachments"] == "hand"
    assert fallback_named("Penny").text == PENNY


def test_no_energy_uses_max_potion_even_when_penny_is_in_hand():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=80, energy=False, hand=["Penny", "Max Potion"])
    assert me.card(game._pick_trainer(me)).name == "Max Potion"
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert game.events.get("max_potion") == 1
    assert "bounce:Penny" not in game.events
    assert any(me.card(i).name == "Penny" for i in me.hand)


def test_charged_mew_that_survives_holds_penny_and_max_potion():
    game = _game()
    _quiet_foe(game)
    me = _mew_board(game, damage=40, energy=True, hand=["Penny", "Max Potion", "Iono"])
    picked = game._pick_trainer(me)
    assert picked is None or me.card(picked).name not in {"Penny", "Max Potion"}
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 40
    assert me.active.energy
    assert "max_potion" not in game.events
    assert "bounce:Penny" not in game.events


def test_one_energy_short_of_phantom_dive_still_plays_penny():
    game = _game()
    _arm_dragapult(game, ["Fire Energy"], hand=["Psychic Energy"])
    me = _mew_board(game, damage=0, energy=True, hand=["Penny", "Iono"])
    assert me.card(game._pick_trainer(me)).name == "Penny"


def test_one_colorless_attack_does_not_pick_up_a_healthy_mew():
    game = _game()
    _arm_dragapult(game, [], hand=["Fire Energy"])
    me = _mew_board(game, damage=0, energy=True, hand=["Penny", "Max Potion"])
    assert game._pick_trainer(me) is None


def test_benched_dragapult_that_can_retreat_in_plays_penny():
    game = _game()
    foe = game.players["b"]
    dreepy = _add(foe, "Dreepy")
    foe.active = Pokemon(card_i=dreepy, energy=[_add(foe, "Fire Energy")])
    drag = _add(foe, "Dragapult ex")
    foe.bench = [Pokemon(card_i=drag, energy=[_add(foe, "Fire Energy"), _add(foe, "Psychic Energy")])]
    foe.hand = []
    foe.deck = []
    me = _mew_board(game, damage=30, energy=True, hand=["Penny", "Professor's Research"])
    assert me.card(game._pick_trainer(me)).name == "Penny"


def test_penny_returns_the_charged_mew_then_it_is_replayed_active():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=90, energy=True, hand=["Penny"])
    mew_i = me.active.card_i
    spike_i = me.active.energy[0]
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("bounce:Penny") == 1
    assert mew_i in me.hand
    assert spike_i in me.hand
    assert me.card(me.active.card_i).name == "Igglybuff"
    game._play_basics(me)
    game._attach_energy(me, "a")
    game._maybe_retreat(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Mew ex"
    assert me.active.card_i == mew_i
    assert me.active.damage == 0
    assert me.active.energy == [spike_i]


def test_missing_penny_still_max_potions_a_charged_mew_that_would_be_koed():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=40, energy=True, hand=["Max Potion"])
    game._play_trainers(me, game.players["b"], "a")
    assert me.active.damage == 0
    assert me.active.energy == []
    assert game.events.get("max_potion_discard_energy") == 1


def test_cape_in_hand_saves_the_charged_mew_without_penny():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=50, energy=True, hand=["Penny", "Hero's Cape"])
    spike_i = me.active.energy[0]
    game._play_trainers(me, game.players["b"], "a")
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert me.active.energy == [spike_i]
    assert me.active.damage == 50
    assert "bounce:Penny" not in game.events


def test_arven_cape_beats_penny_when_the_cape_prevents_the_ko():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=50, energy=True, hand=["Penny", "Arven"], deck=["Hero's Cape"])
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("arven") == 1
    assert me.card(me.active.tool).name == "Hero's Cape"
    assert me.active.energy
    assert "bounce:Penny" not in game.events


def test_penny_beats_arven_when_the_cape_cannot_prevent_the_ko():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"])
    me = _mew_board(game, damage=150, energy=True, hand=["Penny", "Arven"], deck=["Hero's Cape"])
    assert me.card(game._pick_trainer(me)).name == "Penny"


def test_boss_that_takes_the_last_prize_beats_penny():
    game = _game()
    _arm_dragapult(game, ["Fire Energy", "Psychic Energy"], bench=[("Igglybuff", [])])
    me = _mew_board(game, damage=40, energy=True, hand=["Penny", "Boss's Orders"])
    me.prizes_taken = 5
    assert me.card(game._pick_trainer(me)).name == "Boss's Orders"
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("boss_orders") == 1
    assert "bounce:Penny" not in game.events
    assert me.active.energy
