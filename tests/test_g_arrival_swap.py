"""G plays the C60 arrivals without eating the Party Active."""

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_G_NAMES, build_fallback_deck

PRANKISH = (
    "When you play this Pokémon from your hand to evolve 1 of your Pokémon during your turn, "
    "you may put an Energy attached to your opponent's Active Pokémon on top of their deck."
)


def _game() -> Game:
    names = list(SET_G_NAMES)
    names[names.index("Iris's Fighting Spirit")] = "Lillie"
    names[names.index("Darkness Energy")] = "Clefable"
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dragapult ex", "Fire Energy"] + ["Cubone"] * 28),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def _pull(player, name: str, used: set[int]) -> int:
    idx = next(i for i, card in enumerate(player.cards) if card.name == name and i not in used)
    used.add(idx)
    for zone in (player.deck, player.hand, player.prizes, player.discard):
        if idx in zone:
            zone.remove(idx)
    return idx


def test_prankish_print_is_rebel_clash():
    from app.seed_data import fallback_named

    card = fallback_named("Clefable")
    assert card.catalog_id == "swsh2-75"
    ability = next(a for a in card.abilities if a.name == "Prankish")
    assert ability.text == PRANKISH


def test_g_prankish_evolves_a_bench_clefairy_and_bounces_energy():
    game = _game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    active = _pull(me, "Clefairy", used)
    bench = _pull(me, "Clefairy", used)
    prank = _pull(me, "Clefable", used)
    foe_used: set[int] = set()
    fuel = _pull(foe, "Fire Energy", foe_used)
    foe_active = _pull(foe, "Dragapult ex", foe_used)
    me.active = Pokemon(card_i=active, played_turn=0)
    me.bench = [Pokemon(card_i=bench, played_turn=0)]
    me.hand = [prank]
    foe.active = Pokemon(card_i=foe_active, energy=[fuel], played_turn=0)
    game.turn = 4
    game.first = "b"
    game.strats["a"].evolve_asap = 1.0
    game._evolve(me, foe, "a")
    assert me.card(me.active.card_i).name == "Clefairy"
    assert me.card(me.bench[0].card_i).name == "Clefable"
    assert fuel not in foe.active.energy
    assert foe.deck[0] == fuel
    assert game.events.get("prankish")


def test_g_does_not_spend_the_only_clefairy_on_prankish():
    game = _game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    active = _pull(me, "Clefairy", used)
    prank = _pull(me, "Clefable", used)
    foe_used: set[int] = set()
    fuel = _pull(foe, "Fire Energy", foe_used)
    foe_active = _pull(foe, "Dragapult ex", foe_used)
    me.active = Pokemon(card_i=active, played_turn=0)
    me.bench = []
    me.hand = [prank]
    foe.active = Pokemon(card_i=foe_active, energy=[fuel], played_turn=0)
    game.turn = 4
    game.first = "b"
    game.strats["a"].evolve_asap = 1.0
    game._evolve(me, foe, "a")
    assert me.card(me.active.card_i).name == "Clefairy"
    assert prank in me.hand
    assert fuel in foe.active.energy


def test_g_holds_prankish_when_there_is_no_energy_to_bounce():
    game = _game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    active = _pull(me, "Clefairy", used)
    bench = _pull(me, "Clefairy", used)
    prank = _pull(me, "Clefable", used)
    foe_active = _pull(foe, "Dragapult ex", set())
    me.active = Pokemon(card_i=active, played_turn=0)
    me.bench = [Pokemon(card_i=bench, played_turn=0)]
    me.hand = [prank]
    foe.active = Pokemon(card_i=foe_active, energy=[], played_turn=0)
    game.turn = 4
    game.first = "b"
    game.strats["a"].evolve_asap = 1.0
    game._evolve(me, foe, "a")
    assert prank in me.hand
    assert me.card(me.bench[0].card_i).name == "Clefairy"


def test_g_lillie_outranks_drayton_when_it_draws():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    lillie = _pull(me, "Lillie", used)
    drayton = _pull(me, "Drayton", used)
    me.hand = [lillie, drayton]
    game.turn = 4
    game.first = "b"
    assert game._pick_trainer(me) == lillie
