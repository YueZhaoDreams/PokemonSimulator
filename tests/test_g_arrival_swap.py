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


def _pad_game() -> Game:
    names = list(SET_G_NAMES)
    names[names.index("Iris's Fighting Spirit")] = "Lillie"
    names[names.index("Darkness Energy")] = "Clefable"
    names[names.index("Energy Switch")] = "Poké Pad"
    return Game(
        build_fallback_deck(names),
        build_fallback_deck(["Dragapult ex", "Fire Energy"] + ["Cubone"] * 28),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def _bench(card_i: int) -> Pokemon:
    return Pokemon(card_i=card_i, played_turn=0)


def test_g_pad_fetches_ledian_ahead_of_starly():
    game = _pad_game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    clefs = [_pull(me, "Clefairy", used) for _ in range(3)]
    ledyba = _pull(me, "Ledyba", used)
    ledian = _pull(me, "Ledian", used)
    starly = _pull(me, "Starly", used)
    pad = _pull(me, "Poké Pad", used)
    prank = _pull(me, "Clefable", used)
    me.active = _bench(clefs[0])
    me.bench = [_bench(clefs[1]), _bench(clefs[2]), _bench(ledyba)]
    me.hand = [pad]
    me.deck = [ledian, starly]
    me.discard.append(prank)
    foe.active = _bench(_pull(foe, "Dragapult ex", set()))
    assert game._g_tutor_hole(me, "a", kind="pad") == "Ledian"
    game._resolve_trainer(me, foe, me.card(pad), who="a", card_i=pad)
    assert ledian in me.hand
    assert starly in me.deck


def test_g_pad_fetches_prankish_when_the_bounce_is_live():
    game = _pad_game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    clefs = [_pull(me, "Clefairy", used) for _ in range(3)]
    ledyba = _pull(me, "Ledyba", used)
    ledian = _pull(me, "Ledian", used)
    prank = _pull(me, "Clefable", used)
    pad = _pull(me, "Poké Pad", used)
    me.active = _bench(clefs[0])
    me.bench = [_bench(clefs[1]), _bench(clefs[2]), _bench(ledyba)]
    me.hand = [pad]
    me.deck = [prank, ledian]
    foe_used: set[int] = set()
    fuel = _pull(foe, "Fire Energy", foe_used)
    foe.active = Pokemon(card_i=_pull(foe, "Dragapult ex", foe_used), energy=[fuel], played_turn=0)
    assert game._g_tutor_hole(me, "a", kind="pad") == "Clefable"
    game._resolve_trainer(me, foe, me.card(pad), who="a", card_i=pad)
    assert prank in me.hand
    assert ledian in me.deck


def test_g_pad_and_ultra_ball_are_held_when_the_holes_are_filled():
    game = _pad_game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    clefs = [_pull(me, "Clefairy", used) for _ in range(3)]
    ledyba = _pull(me, "Ledyba", used)
    ledian = _pull(me, "Ledian", used)
    munk = _pull(me, "Munkidori", used)
    starly = _pull(me, "Starly", used)
    staravia = _pull(me, "Staravia", used)
    staraptor = _pull(me, "Staraptor", used)
    prank = _pull(me, "Clefable", used)
    ex = _pull(me, "Clefable ex", used)
    pad = _pull(me, "Poké Pad", used)
    ultra = _pull(me, "Ultra Ball", used)
    me.active = _bench(clefs[0])
    me.bench = [
        _bench(clefs[1]),
        _bench(clefs[2]),
        _bench(ledyba),
        _bench(munk),
        _bench(staraptor),
    ]
    me.hand = [pad, ultra, ledian, starly, staravia, prank, ex]
    me.deck = [_pull(me, "Ledyba", used)]
    foe.active = _bench(_pull(foe, "Dragapult ex", set()))
    assert game._g_tutor_hole(me, "a", kind="pad") is None
    assert game._g_tutor_hole(me, "a", kind="ultra") is None
    assert game._pick_trainer(me) is None


def test_g_ultra_ball_fetches_ledian_once_clefable_ex_is_in_hand():
    game = _pad_game()
    me, foe = game.players["a"], game.players["b"]
    used: set[int] = set()
    clefs = [_pull(me, "Clefairy", used) for _ in range(3)]
    ledyba = _pull(me, "Ledyba", used)
    ledian = _pull(me, "Ledian", used)
    ex = _pull(me, "Clefable ex", used)
    mega = _pull(me, "Mega Clefable ex", used)
    ultra = _pull(me, "Ultra Ball", used)
    junk = [_pull(me, "Psychic Energy", used) for _ in range(2)]
    prank = _pull(me, "Clefable", used)
    me.active = _bench(clefs[0])
    me.bench = [_bench(clefs[1]), _bench(clefs[2]), _bench(ledyba)]
    me.hand = [ultra, ex, *junk]
    me.deck = [ledian, mega]
    me.discard.append(prank)
    foe.active = _bench(_pull(foe, "Dragapult ex", set()))
    assert game._g_tutor_hole(me, "a", kind="ultra") == "Ledian"
    assert game._pick_trainer(me) == ultra
    game._resolve_trainer(me, foe, me.card(ultra), who="a", card_i=ultra)
    assert ledian in me.hand
    assert mega in me.deck


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
