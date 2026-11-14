"""C60 vs Mew: switch ex, and do not leave a Clefairy Bouncy Circle can Knock Out."""

from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_M60_NAMES, build_fallback_deck, fallback_named


def _game() -> Game:
    game = Game(
        build_fallback_deck(list(SET_C60_NAMES)),
        build_fallback_deck(list(SET_M60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )
    game.turn = 5
    game.first = "b"
    return game


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _mew_board(game: Game, babies: int) -> None:
    """Mew ex Active, with that many 30 HP Benched Pokémon. Bouncy Circle uses the printed count."""
    foe = game.players["b"]
    mew = _idxs(foe, "Mew ex")[0]
    bodies = _idxs(foe, "Igglybuff") + _idxs(foe, "Budew")
    foe.active = Pokemon(card_i=mew, played_turn=0)
    foe.bench = [Pokemon(card_i=bodies[i], played_turn=0) for i in range(babies)]
    foe.hand = []


def test_bouncy_circle_sentence_is_the_hit():
    iggly = fallback_named("Igglybuff")
    circle = next(a for a in iggly.attacks if a.name == "Bouncy Circle")
    assert circle.text == (
        "This attack does 30 damage for each of your Benched Pokémon that has a maximum HP of 30."
    )
    assert {"kind": "benched_30hp_pokemon_times", "per": 30} in parse_effects(circle.text, str(circle.damage or ""))
    helix = next(a for a in fallback_named("Mew ex").abilities if a.name == "Memory Helix")
    assert "any of your Benched Pokémon" in helix.text


def test_wondrous_moon_sentence_moves_psychic_energy():
    moon = next(a for a in fallback_named("Clefable ex").attacks if a.name == "Wondrous Moon")
    assert "move any amount of Psychic Energy from your Pokémon to your other Pokémon" in moon.text
    assert any(e.get("kind") == "move_psychic_energy" for e in parse_effects(moon.text, str(moon.damage or "")))


def test_party_vs_mew_does_not_retreat_onto_a_clefairy_the_hit_knocks_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    me.active = Pokemon(card_i=mewtwo, energy=list(fuel), played_turn=1)
    me.bench = [Pokemon(card_i=clef, played_turn=1)]
    me.hand = []
    assert game._mew_hit(game.players["b"], me) == 120
    assert game._remaining_hp(me, me.bench[0]) <= 120
    game._retreat_party(me, game.players["b"], "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_party_vs_mew_switches_a_dying_clefairy_onto_clefable_ex():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    clef = _idxs(me, "Clefairy")[0]
    ex = _idxs(me, "Clefable ex")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    switch = _idxs(me, "Switch")[0]
    me.active = Pokemon(card_i=clef, energy=list(fuel), played_turn=1)
    me.bench = [Pokemon(card_i=ex, played_turn=1)]
    me.hand = [switch]
    game._retreat_party(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Clefable ex"
    assert game.events.get("mew_ex_switch")


def test_party_vs_mew_stays_on_clefairy_while_bouncy_circle_cannot_ko():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 0)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    switch = _idxs(me, "Switch")[0]
    me.active = Pokemon(card_i=mewtwo, played_turn=1)
    me.bench = [Pokemon(card_i=clef, played_turn=1)]
    me.hand = [switch]
    assert game._mew_hit(game.players["b"], me) == 0
    game._retreat_party(me, game.players["b"], "a")
    assert game._is_clefairy(me.card(me.active.card_i))


def test_party_vs_mew_evolves_the_clefairy_bouncy_circle_would_knock_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    clef = _idxs(me, "Clefairy")[0]
    ex = _idxs(me, "Clefable ex")[0]
    me.active = Pokemon(card_i=clef, played_turn=1)
    me.bench = []
    me.hand = [ex]
    game._evolve_party(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Clefable ex"
    assert game.events.get("mew_evolve_ex")
    assert (fallback_named("Clefable ex").hp or 0) - me.active.damage > game._mew_hit(game.players["b"], me)


def test_wondrous_moon_moves_energy_off_the_pokemon_mew_would_knock_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 8)
    ex = _idxs(me, "Clefable ex")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    fuel = _idxs(me, "Psychic Energy")[:3]
    me.active = Pokemon(card_i=ex, energy=list(fuel), damage=40, played_turn=1)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=1)]
    hit = game._mew_hit(game.players["b"], me)
    assert hit == 240
    assert game._remaining_hp(me, me.active) <= hit
    game._move_psychic_energy(me, me.active)
    assert me.active.energy == []
    assert me.bench[0].energy == fuel
    assert game.events.get("mew_moon_save") == 3


def test_attach_finishes_wondrous_moon_before_it_feeds_mewtwo():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    ex = _idxs(me, "Clefable ex")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    me.active = Pokemon(card_i=mewtwo, played_turn=1)
    me.bench = [Pokemon(card_i=ex, energy=list(fuel), played_turn=1)]
    me.hand = []
    assert game._energy_target(me, game.strats["a"]) is me.bench[0]


def test_energy_switch_finishes_wondrous_moon_instead_of_stripping_it():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    ex = _idxs(me, "Clefable ex")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    fuel = _idxs(me, "Psychic Energy")
    me.active = Pokemon(card_i=mewtwo, played_turn=1)
    me.bench = [
        Pokemon(card_i=ex, energy=list(fuel[:2]), played_turn=1),
        Pokemon(card_i=clef, energy=[fuel[2]], played_turn=1),
    ]
    me.hand = [_idxs(me, "Energy Switch")[0]]
    game._energy_switch(me)
    assert len(me.bench[0].energy) == 3
    assert me.active.energy == []
    assert game._can_pay_wondrous_moon(me, me.bench[0])


def test_party_vs_mew_moons_from_clefable_when_a_pokemon_would_be_knocked_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    ex = _idxs(me, "Clefable ex")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    fuel = _idxs(me, "Psychic Energy")[:3]
    switch = _idxs(me, "Switch")[0]
    me.active = Pokemon(card_i=clef, played_turn=1)
    me.bench = [
        Pokemon(card_i=mewtwo, played_turn=1),
        Pokemon(card_i=ex, energy=list(fuel), played_turn=1),
    ]
    me.hand = [switch]
    game._retreat_party(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Clefable ex"


def test_promoted_mewtwo_is_where_the_attach_and_energy_switch_go():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    me.active = Pokemon(card_i=mewtwo, played_turn=1)
    me.bench = [Pokemon(card_i=clef, energy=list(fuel), played_turn=1)]
    me.hand = []
    assert game._energy_target(me, game.strats["a"]) is me.active
    game._energy_switch(me)
    assert len(me.active.energy) == 1
    assert any(me.card(i).name == "Psychic Energy" for i in me.active.energy)
    assert len(me.bench[0].energy) == 1


def _poffin_threat(game: Game, benched: int) -> None:
    """Mew Active, `benched` 30 HP Pokémon, and a Buddy-Buddy Poffin in hand."""
    foe = game.players["b"]
    _mew_board(game, benched)
    bodies = _idxs(foe, "Igglybuff") + _idxs(foe, "Budew")
    used = {foe.active.card_i, *(mon.card_i for mon in foe.bench)}
    foe.deck = [i for i in bodies if i not in used]
    foe.hand = [_idxs(foe, "Buddy-Buddy Poffin")[0]]
    foe.prizes = []
    foe.discard = []


def test_mew_hit_counts_babies_a_held_poffin_can_bench():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _poffin_threat(game, 1)
    me.active = Pokemon(card_i=_idxs(me, "Clefairy")[0], played_turn=1)
    me.bench = []
    poffin = foe.card(foe.hand[0])
    assert "up to 2" in poffin.text
    assert "70 HP or less" in poffin.text
    circle = next(a for a in fallback_named("Igglybuff").attacks if a.name == "Bouncy Circle")
    per = next(e["per"] for e in circle.effects if e.get("kind") == "benched_30hp_pokemon_times")
    # One already Benched, plus the two the printed Poffin can bench.
    assert game._mew_hit(foe, game.players["a"]) == per * 3


def test_party_vs_mew_leaves_clefairy_when_a_held_poffin_makes_the_hit_a_ko():
    game = _game()
    me = game.players["a"]
    _poffin_threat(game, 1)
    clef = _idxs(me, "Clefairy")[0]
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    switch = _idxs(me, "Switch")[0]
    me.active = Pokemon(card_i=clef, played_turn=1)
    me.bench = [Pokemon(card_i=mewtwo, played_turn=1)]
    me.hand = [switch]
    assert game._mew_hit(game.players["b"], me) > game._remaining_hp(me, me.active)
    game._retreat_party(me, game.players["b"], "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_promote_vs_mew_prefers_a_fresh_clefairy_over_a_mewtwo_the_hit_knocks_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    me.active = None
    me.bench = [
        Pokemon(card_i=mewtwo, damage=120, played_turn=1),
        Pokemon(card_i=clef, played_turn=1),
    ]
    assert game._mew_hit(game.players["b"], me, me.bench[0]) == 120
    assert game._remaining_hp(me, me.bench[0]) <= 120
    idx = game._promote_idx(me, "a")
    assert game._is_clefairy(me.card(me.bench[idx].card_i))


def test_promote_vs_mew_brings_a_mewtwo_that_knocks_out_before_the_return_hit():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _mew_board(game, 4)
    foe.active.damage = 100
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    me.active = None
    me.bench = [
        Pokemon(card_i=clef, played_turn=1),
        Pokemon(card_i=mewtwo, energy=list(fuel), damage=120, played_turn=1),
    ]
    assert game._mewtwo_photon_kos(me, foe, me.bench[1])
    assert game._remaining_hp(me, me.bench[1]) <= game._mew_hit(foe, me, me.bench[1])
    idx = game._promote_idx(me, "a")
    assert game._is_mewtwo(me.card(me.bench[idx].card_i))


def test_promote_vs_mew_brings_clefable_ex_when_it_survives_and_mewtwo_does_not():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 5)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    ex = _idxs(me, "Clefable ex")[0]
    me.active = None
    me.bench = [
        Pokemon(card_i=mewtwo, damage=100, played_turn=1),
        Pokemon(card_i=ex, played_turn=1),
    ]
    assert game._mew_hit(game.players["b"], me, me.bench[1]) == 150
    idx = game._promote_idx(me, "a")
    assert me.card(me.bench[idx].card_i).name == "Clefable ex"


def test_party_vs_mew_keeps_mewtwo_ahead_of_latias_when_both_survive():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    latias = _idxs(me, "Latias ex")[0]
    switch = _idxs(me, "Switch")[0]
    me.active = Pokemon(card_i=latias, played_turn=1)
    me.bench = [Pokemon(card_i=mewtwo, damage=80, played_turn=1)]
    me.hand = [switch]
    assert game._mew_hit(game.players["b"], me) == 120
    assert game._remaining_hp(me, me.bench[0]) > 120
    game._retreat_party(me, game.players["b"], "a")
    assert game._is_mewtwo(me.card(me.active.card_i))


def test_mew_hit_counts_a_stadium_a_trainer_search_would_play():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _mew_board(game, 5)
    me.active = Pokemon(card_i=_idxs(me, "Clefairy")[0], played_turn=1)
    me.bench = []
    bodies = _idxs(foe, "Igglybuff") + _idxs(foe, "Budew")
    used = {foe.active.card_i, *(mon.card_i for mon in foe.bench)}
    spare = [i for i in bodies if i not in used]
    sky = _idxs(foe, "Sky Field")[0]
    foe.deck = spare + [sky]
    foe.hand = [_idxs(foe, "Team Rocket's Petrel")[0], _idxs(foe, "Buddy-Buddy Poffin")[0], spare[0]]
    foe.deck = [i for i in foe.deck if i not in foe.hand]
    # Prize indices are this player's own cards. Matching the count keeps Counter Catcher quiet.
    energies = [i for i in _idxs(foe, "Psychic Energy") if i not in foe.hand and i not in foe.deck and i not in used]
    foe.prizes = energies[: len(me.prizes)]
    foe.discard = []
    circle = next(a for a in fallback_named("Igglybuff").attacks if a.name == "Bouncy Circle")
    per = next(e["per"] for e in circle.effects if e.get("kind") == "benched_30hp_pokemon_times")
    # Five already Benched. Petrel takes Sky Field (8 Bench). Poffin plus the Basic in hand fill three spots.
    assert game._mew_hit(foe, me) == per * 8


def test_promote_vs_mew_brings_mewtwo_when_it_survives_the_hit():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    clef = _idxs(me, "Clefairy")[0]
    me.active = None
    me.bench = [
        Pokemon(card_i=clef, played_turn=1),
        Pokemon(card_i=mewtwo, played_turn=1),
    ]
    idx = game._promote_idx(me, "a")
    assert game._is_mewtwo(me.card(me.bench[idx].card_i))


def test_promote_brings_up_clefable_ex_ahead_of_clefairy():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    clef = _idxs(me, "Clefairy")[0]
    ex = _idxs(me, "Clefable ex")[0]
    me.active = None
    me.bench = [
        Pokemon(card_i=clef, played_turn=1),
        Pokemon(card_i=ex, played_turn=1),
    ]
    idx = game._promote_idx(me, "a")
    assert me.card(me.bench[idx].card_i).name == "Clefable ex"


def test_photon_chips_mew_when_it_does_not_knock_out():
    game = _game()
    me = game.players["a"]
    _mew_board(game, 4)
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    fuel = _idxs(me, "Psychic Energy")[:2]
    me.active = Pokemon(card_i=mewtwo, energy=list(fuel), played_turn=1)
    me.bench = []
    atk = game._choose_attack(me, game.players["b"], game.strats["a"])
    assert atk is not None
    assert "kinesis" in atk.name.lower()
    assert game._effective_damage(me, game.players["b"], atk) < game._max_hp(game.players["b"], game.players["b"].active)
