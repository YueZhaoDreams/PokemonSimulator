"""Penny / Turo / Briney / Seeker lines on the printed sentences.

Leaving play removes damage counters, so the replay is a new Pokémon at full HP.
Cheren's Care is Colorless-only and does not pick up Clefairy.
"""

from random import Random

from app.engine.effects import parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, build_fallback_deck, fallback_named

PENNY = "Put 1 of your Basic Pokémon and all attached cards into your hand."
TURO = "Put 1 of your Pokémon into your hand. (Discard all attached cards.)"
AZ = "Put 1 of your Pokémon into your hand. (Discard all cards attached to that Pokémon.)"
CHEREN = (
    "Put 1 of your Colorless Pokémon that has any damage counters on it "
    "and all attached cards into your hand."
)
BRINEY = (
    "Choose 1 of your Pokémon in play (excluding Pokémon-ex). "
    "Return that Pokémon and all cards attached to it to your hand."
)
SEEKER = (
    "Each player returns 1 of his or her Benched Pokémon and all cards attached to it "
    "to his or her hand. (You return your Pokémon first.)"
)


def _script_names() -> list[str]:
    """Cage lock plus the four supporters these lines script.

    The win-rate matrix left those supporters out of SET_C60_NAMES.
    """
    names = list(SET_C60_NAMES)
    if (
        names.count("Penny") >= 1
        and "Professor Turo's Scenario" in names
        and "Mr. Briney's Compassion" in names
        and "Seeker" in names
    ):
        return names
    for cut, add in (
        ("Hop", "Penny"),
        ("Lillie", "Penny"),
        ("Lillie's Determination", "Professor Turo's Scenario"),
        ("Iono", "Mr. Briney's Compassion"),
        ("Energy Switch", "Seeker"),
    ):
        names.remove(cut)
        names.append(add)
    return names


def _game() -> Game:
    foe = ["Dreepy", "Drakloak", "Dragapult ex", "Fire Energy", "Fire Energy"]
    return Game(
        build_fallback_deck(_script_names()),
        build_fallback_deck(foe * 12),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def _add(game: Game, name: str) -> int:
    me = game.players["a"]
    me.cards.append(fallback_named(name))
    return len(me.cards) - 1


def test_printed_bounce_sentences():
    penny = parse_trainer_effects(PENNY)[0]
    assert penny["basic_only"] is True and penny["attachments"] == "hand"
    turo = parse_trainer_effects(TURO)[0]
    az = parse_trainer_effects(AZ)[0]
    assert turo["attachments"] == "discard" and az["attachments"] == "discard"
    assert "basic_only" not in turo and "basic_only" not in az
    cheren = parse_trainer_effects(CHEREN)[0]
    assert cheren["colorless_only"] is True and cheren["require_damage"] is True
    briney = parse_trainer_effects(BRINEY)[0]
    assert briney["exclude_ex"] is True and briney["attachments"] == "hand"
    seeker = parse_trainer_effects(SEEKER)[0]
    assert seeker["bench_only"] is True and seeker["both_players"] is True
    assert parse_trainer_effects(fallback_named("Penny").text)[0]["kind"] == "return_pokemon_to_hand"
    assert parse_trainer_effects(fallback_named("Professor Turo's Scenario").text)[0]["attachments"] == "discard"


def test_penny_telepathic_then_second_party_replays_at_full_hp():
    game = _game()
    game.turn = 3
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    penny = next(i for i, c in enumerate(me.cards) if c.name == "Penny")
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    energies = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=fairies[0], played_turn=0, damage=40)
    me.bench = []
    me.hand = [tele, penny]
    me.deck = fairies[1:3] + energies[:6]
    me.energy_attached = False
    me.supporter_used = False
    game._maybe_attach_telepathic_before_party(me, "a")
    assert [me.card(m.card_i).name for m in me.bench].count("Clefairy") == 2
    game._moon_watching_party(me, me.active)
    assert me.active.ability_used
    assert game.events.get("party_energy") == 2
    game._party_bounce_combo(me, game.players["b"], "a")
    assert game.events.get("bounce:Penny") == 1
    assert game.events.get("bounce_a:Penny") == 1
    assert game.events.get("bounce_b:Penny") is None
    assert penny in me.discard
    assert tele in me.hand
    assert fairies[0] in me.hand or any(m.card_i == fairies[0] for m in me.in_play())
    replayed = next(m for m in me.in_play() if m.card_i == fairies[0])
    assert replayed.damage == 0
    assert replayed.played_turn == 3
    assert game.events.get("bounce_heal") == 1
    assert game.events.get("party_energy", 0) >= 3
    assert me.card(me.active.card_i).name == "Clefairy"
    assert not any(m.card_i == fairies[0] and m.damage for m in me.in_play())


def test_double_prankish_with_briney_keeps_energy_and_full_hp():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    clefable = next(
        i
        for i, c in enumerate(me.cards)
        if c.name == "Clefable" and any(a.name == "Prankish" for a in c.abilities)
    )
    briney = next(i for i, c in enumerate(me.cards) if c.name == "Mr. Briney's Compassion")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    fires = [i for i, c in enumerate(foe.cards) if c.name == "Fire Energy"]
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=fairies[0], played_turn=0, damage=30, energy=[nrg], ability_used=True)
    me.bench = [Pokemon(card_i=fairies[1], played_turn=0)]
    me.hand = [clefable, briney]
    me.deck = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy" and i != nrg][:3]
    me.supporter_used = False
    foe.active = Pokemon(card_i=dreepy, played_turn=0, energy=fires[:2])
    foe.bench = []
    game._party_bounce_combo(me, foe, "a")
    assert game.events.get("prankish") == 2
    assert briney in me.discard
    assert nrg in me.hand
    replayed = next(m for m in me.in_play() if m.card_i == fairies[0])
    assert replayed.damage == 0
    assert replayed.played_turn == 4
    assert any(me.card(m.card_i).name == "Clefable" for m in me.in_play())
    assert not any(m.card_i == fairies[0] and me.card(m.card_i).name == "Clefable" for m in me.in_play())
    assert foe.card(foe.deck[0]).name == "Fire Energy"
    assert foe.card(foe.deck[1]).name == "Fire Energy"
    assert drak not in foe.hand


def test_seeker_returns_both_benches_and_pranks_twice():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    clefable = next(
        i
        for i, c in enumerate(me.cards)
        if c.name == "Clefable" and any(a.name == "Prankish" for a in c.abilities)
    )
    seeker = next(i for i, c in enumerate(me.cards) if c.name == "Seeker")
    switch = next(i for i, c in enumerate(me.cards) if c.name == "Switch")
    fires = [i for i, c in enumerate(foe.cards) if c.name == "Fire Energy"]
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=fairies[0], played_turn=0, ability_used=True)
    me.bench = [Pokemon(card_i=fairies[1], played_turn=0)]
    me.hand = [clefable, seeker, switch]
    for briney in [i for i, c in enumerate(me.cards) if c.name == "Mr. Briney's Compassion"]:
        if briney in me.hand:
            me.hand.remove(briney)
    me.deck = []
    me.supporter_used = False
    foe.active = Pokemon(card_i=dreepy, played_turn=0, energy=fires[:2])
    foe.bench = [Pokemon(card_i=drak, played_turn=0, damage=20)]
    foe.hand = []
    game._party_bounce_combo(me, foe, "a")
    assert game.events.get("prankish") == 2
    assert seeker in me.discard
    assert switch in me.discard
    assert drak in foe.hand
    assert not any(m.card_i == drak for m in foe.in_play())
    replayed = [m for m in foe.in_play() if m.card_i == drak]
    assert replayed == []
    assert game.events.get("bounce:Seeker") == 2


def test_turo_discards_attachments_and_replay_is_full_hp():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    turo = next(i for i, c in enumerate(me.cards) if c.name == "Professor Turo's Scenario")
    me.active = Pokemon(card_i=mewtwo, played_turn=0, damage=200, energy=[nrg])
    me.bench = [Pokemon(card_i=fairy, played_turn=0)]
    me.hand = [turo]
    me.supporter_used = False
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy"), played_turn=0)
    foe.bench = []
    game._party_bounce_combo(me, foe, "a")
    assert turo in me.discard
    assert nrg in me.discard
    assert mewtwo in me.hand or any(m.card_i == mewtwo for m in me.in_play())
    body = next(m for m in me.in_play() if m.card_i == mewtwo)
    assert body.damage == 0
    assert game.events.get("bounce:Professor Turo's Scenario") == 1


def test_cheren_ignores_psychic_and_lifts_a_damaged_colorless():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    aipom = _add(game, "Aipom")
    cheren = _add(game, "Cheren's Care")
    holder = Pokemon(card_i=fairy, played_turn=0, damage=40, energy=[nrg])
    colorless = Pokemon(card_i=aipom, played_turn=0, damage=30, energy=[])
    # Give the Colorless body the energy so the printed sentence can return it.
    holder.energy = []
    colorless.energy = [nrg]
    me.active = holder
    me.bench = [colorless]
    me.hand = [cheren]
    eff = parse_trainer_effects(me.card(cheren).text)[0]
    assert holder not in game._legal_bounce_targets(me, eff)
    assert colorless in game._legal_bounce_targets(me, eff)
    game._forced_bounce_target = colorless
    game._commit_trainer(me, foe, "a", cheren)
    assert aipom in me.hand
    assert nrg in me.hand
    assert fairy in [m.card_i for m in me.in_play()]
    me.hand.remove(aipom)
    played = Pokemon(card_i=aipom, played_turn=game.turn)
    assert played.damage == 0


def test_briney_refuses_pokemon_ex():
    game = _game()
    me = game.players["a"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    briney = next(i for i, c in enumerate(me.cards) if c.name == "Mr. Briney's Compassion")
    me.active = Pokemon(card_i=mewtwo, played_turn=0, damage=50)
    me.bench = [Pokemon(card_i=fairy, played_turn=0, damage=20)]
    eff = parse_trainer_effects(me.card(briney).text)[0]
    legal = game._legal_bounce_targets(me, eff)
    assert me.active not in legal
    assert me.bench[0] in legal


def test_az_discards_attached_cards():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    az = _add(game, "AZ")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    other = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"][1]
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=fairy, played_turn=0, damage=50, energy=[nrg])
    me.bench = [Pokemon(card_i=other, played_turn=0)]
    me.hand = [az]
    game._forced_bounce_target = me.active
    game._commit_trainer(me, foe, "a", az)
    assert nrg in me.discard
    assert fairy in me.hand
    assert game.events.get("bounce_heal") == 1


def test_seeker_with_no_bench_still_returns_the_opponents():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    seeker = next(i for i, c in enumerate(me.cards) if c.name == "Seeker")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = [seeker]
    me.supporter_used = False
    foe.active = Pokemon(card_i=dreepy, played_turn=0)
    foe.bench = [Pokemon(card_i=drak, played_turn=0, damage=20)]
    game._commit_trainer(me, foe, "a", seeker)
    assert drak in foe.hand
    assert foe.bench == []
    assert me.active is not None and me.active.card_i == fairy
    assert game.events.get("bounce_fail") is None
    assert game.events.get("bounce_b:Seeker") == 1
    assert game.events.get("bounce_a:Seeker") is None


def test_seeker_board_wipe_kos_the_last_active():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    energies = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    seeker = next(i for i, c in enumerate(me.cards) if c.name == "Seeker")
    lillie = next(i for i, c in enumerate(me.cards) if c.name == "Lillie")
    penny = next(i for i, c in enumerate(me.cards) if c.name == "Penny")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=mewtwo, played_turn=0, energy=energies[:2])
    fueled = Pokemon(card_i=fairies[0], played_turn=0, energy=energies[2:4])
    empty = Pokemon(card_i=fairies[1], played_turn=0)
    me.bench = [fueled, empty]
    me.hand = [seeker, lillie, penny]
    me.supporter_used = False
    me.energy_attached = True
    foe.active = Pokemon(card_i=dreepy, played_turn=0)
    foe.bench = [Pokemon(card_i=drak, played_turn=0)]
    hp = game._max_hp(foe, foe.active)
    foe.active.damage = max(0, hp - 100)
    assert game._can_active_ko(me, foe)
    hand_before = list(me.hand)
    energy_before = [list(mon.energy) for mon in me.in_play()]
    assert game._seeker_wipe_pending(me, foe, "a")
    assert list(me.hand) == hand_before
    assert [list(mon.energy) for mon in me.in_play()] == energy_before
    assert game._pick_trainer(me) not in {lillie, seeker, penny}
    assert game._try_seeker_board_wipe(me, foe, "a")
    assert fairies[1] in me.hand
    assert fairies[0] not in me.hand
    assert drak in foe.hand
    assert foe.bench == []
    assert game.events.get("seeker_board_wipe") == 1
    game._attack(me, foe, "a")
    assert game._check_ko(foe, me, "b")
    assert game.winner == "a"
    assert game.reason == "opponent has no Pokémon in play"


def test_seeker_board_wipe_refuses_when_the_ko_needs_the_only_bench():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    energies = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    seeker = next(i for i, c in enumerate(me.cards) if c.name == "Seeker")
    drag = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=mewtwo, played_turn=0, energy=energies[:2])
    me.bench = [Pokemon(card_i=fairy, played_turn=0, energy=energies[2:4])]
    me.hand = [seeker]
    me.supporter_used = False
    me.energy_attached = True
    foe.active = Pokemon(card_i=drag, played_turn=0)
    foe.bench = [Pokemon(card_i=drak, played_turn=0)]
    hp = game._max_hp(foe, foe.active)
    foe.active.damage = hp - 100
    assert game._can_active_ko(me, foe)
    assert game._try_seeker_board_wipe(me, foe, "a") is False
    assert seeker in me.hand
    assert foe.bench


def test_seeker_board_wipe_needs_exactly_one_bench():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    foe = game.players["b"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    energies = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    seeker = next(i for i, c in enumerate(me.cards) if c.name == "Seeker")
    dreepy = next(i for i, c in enumerate(foe.cards) if c.name == "Dreepy")
    drak = next(i for i, c in enumerate(foe.cards) if c.name == "Drakloak")
    drag = next(i for i, c in enumerate(foe.cards) if c.name == "Dragapult ex")
    me.active = Pokemon(card_i=mewtwo, played_turn=0, energy=energies[:4])
    me.bench = []
    me.hand = [seeker]
    me.supporter_used = False
    me.energy_attached = True
    foe.active = Pokemon(card_i=dreepy, played_turn=0)
    foe.active.damage = game._max_hp(foe, foe.active) - 40
    foe.bench = [
        Pokemon(card_i=drak, played_turn=0),
        Pokemon(card_i=drag, played_turn=0),
    ]
    assert game._can_active_ko(me, foe)
    hand_before = list(me.hand)
    energy_before = list(me.active.energy)
    assert game._seeker_wipe_pending(me, foe, "a") is False
    assert list(me.hand) == hand_before
    assert list(me.active.energy) == energy_before
    assert game._try_seeker_board_wipe(me, foe, "a") is False
    assert len(foe.bench) == 2


def test_party_holds_lillie_while_penny_line_is_ready():
    game = _game()
    game.turn = 3
    me = game.players["a"]
    penny = next(i for i, c in enumerate(me.cards) if c.name == "Penny")
    lillie = next(i for i, c in enumerate(me.cards) if c.name == "Lillie")
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=fairy, played_turn=0)
    me.bench = []
    me.hand = [penny, lillie, tele]
    me.deck = [i for i, c in enumerate(me.cards) if c.name == "Clefairy" and i != fairy]
    me.supporter_used = False
    picked = game._pick_trainer(me)
    assert picked != lillie


def test_turo_is_not_scored_as_professors_research():
    game = _game()
    game.turn = 4
    me = game.players["a"]
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    turo = next(i for i, c in enumerate(me.cards) if c.name == "Professor Turo's Scenario")
    energies = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    iono = _add(game, "Iono")
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = []
    me.hand = [turo, iono, energies[0], energies[1]]
    me.deck = energies[2:]
    me.supporter_used = False
    assert game._pick_trainer(me) == iono
