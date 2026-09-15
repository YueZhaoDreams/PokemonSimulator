from random import Random

from app.engine.effects import (
    energy_provided,
    is_basic_energy,
    is_special_energy,
    is_telepathic_energy,
    parse_energy_effects,
)
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_T60_NAMES, build_fallback_deck, fallback_named


TELEPATHIC_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Psychic Energy. "
    "When you attach this card from your hand to a Psychic Pokémon, search your deck "
    "for up to 2 Basic Psychic Pokémon and put them onto your Bench. Then, shuffle your deck."
)


def _c60_psychic_baseline() -> list[str]:
    return [
        "Psychic Energy" if n == "Telepathic Psychic Energy" else n
        for n in SET_C60_NAMES
    ]


def _c60_with_telepathic(n: int = 1) -> list[str]:
    names = _c60_psychic_baseline()
    for _ in range(n):
        names[names.index("Psychic Energy")] = "Telepathic Psychic Energy"
    return names


def _game(names: list[str] | None = None) -> Game:
    return Game(
        build_fallback_deck(names or _c60_with_telepathic()),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def test_telepathic_print_parses_hand_attach_bench():
    effects = parse_energy_effects(TELEPATHIC_TEXT)
    assert effects == [
        {
            "kind": "call_family",
            "count": 2,
            "pokemon_type": "Psychic",
            "from_hand": True,
            "require_attach_type": "Psychic",
        }
    ]
    card = fallback_named("Telepathic Energy")
    assert card.name == "Telepathic Psychic Energy"
    assert card.catalog_id == "me03-088"
    assert card.stage.lower() == "special"
    assert is_telepathic_energy(card)
    assert is_special_energy(card)
    assert not is_basic_energy(card)
    assert energy_provided(card) == ["Psychic"]
    assert parse_energy_effects(card.text) == effects


def test_c60_locked_list_has_two_telepathic():
    from app.seed import _is_basic_energy_name, load_seed_deck

    assert SET_C60_NAMES.count("Telepathic Psychic Energy") == 2
    assert SET_C60_NAMES.count("Psychic Energy") == 13
    assert list(SET_C60_NAMES) == _c60_with_telepathic(2)
    assert not _is_basic_energy_name("Telepathic Psychic Energy")
    seed_names = [c["name"] for c in load_seed_deck("c60")["cards"]]
    assert seed_names.count("Telepathic Psychic Energy") == 2
    assert seed_names.count("Telepathic Energy") == 0


def test_four_telepathic_is_legal_five_is_not():
    rules = standard_60_rules()
    four = build_fallback_deck(_c60_with_telepathic(4))
    assert copy_violations(four, rules) == []
    five = list(_c60_with_telepathic(4)) + ["Telepathic Psychic Energy"]
    five.remove("Psychic Energy")
    assert copy_violations(build_fallback_deck(five), rules)


def test_attach_from_hand_benches_two_clefairy():
    game = _game()
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    fairy = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    me.active = Pokemon(card_i=fairy[0], played_turn=0)
    me.bench = []
    me.hand = [tele]
    me.deck = list(fairy[1:])
    me.energy_attached = False
    game._attach_energy(me, "a")
    assert tele in me.active.energy
    assert tele not in me.hand
    assert me.energy_attached
    names = [me.card(m.card_i).name for m in me.bench]
    assert names.count("Clefairy") == 2
    assert game.events.get("telepathic_bench") == 2


def test_attach_from_hand_to_fighting_does_not_search():
    game = _game()
    me = game.players["a"]
    extra = fallback_named("Cornerstone Mask Ogerpon ex")
    me.cards.append(extra)
    ogerpon = len(me.cards) - 1
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=ogerpon, played_turn=0)
    me.bench = []
    me.hand = [tele]
    me.deck = [fairy]
    me.energy_attached = False
    game._attach_energy(me, "a")
    assert tele in me.active.energy
    assert me.bench == []


def test_full_bench_skips_search():
    game = _game()
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    mewtwo = [i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex"]
    me.active = Pokemon(card_i=mewtwo[0], played_turn=0)
    me.bench = [Pokemon(card_i=i, played_turn=0) for i in mewtwo[1:] + fairies[:3]]
    assert len(me.bench) == 5
    leftover = fairies[3]
    me.hand = [tele]
    me.deck = [leftover]
    me.energy_attached = False
    game._attach_energy(me, "a")
    assert leftover in me.deck
    assert all(m.card_i != leftover for m in me.bench)


def test_party_does_not_attach_telepathic_from_deck():
    game = _game()
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    fairy = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    me.active = Pokemon(card_i=fairy[0], played_turn=0)
    me.bench = [Pokemon(card_i=fairy[1], played_turn=0)]
    me.deck = [tele, nrg]
    me.hand = []
    game._moon_watching_party(me, me.active)
    assert tele in me.deck
    assert nrg in me.bench[0].energy


def test_energy_switch_does_not_move_telepathic():
    game = _game()
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    nrg = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    fairy = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=mewtwo, played_turn=0)
    me.bench = [Pokemon(card_i=fairy, energy=[tele], played_turn=0)]
    me.hand = [next(i for i, c in enumerate(me.cards) if c.name == "Energy Switch")]
    game._energy_switch(me)
    assert tele in me.bench[0].energy
    assert tele not in me.active.energy
    me.bench[0].energy.append(nrg)
    game._energy_switch(me)
    assert nrg in me.active.energy
    assert tele in me.bench[0].energy


def test_party_attaches_telepathic_before_party():
    game = _game()
    me = game.players["a"]
    tele = next(i for i, c in enumerate(me.cards) if c.name == "Telepathic Psychic Energy")
    fairies = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    nrg = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"][:2]
    me.active = Pokemon(card_i=fairies[0], played_turn=0)
    me.bench = []
    me.hand = [tele]
    me.deck = fairies[1:] + nrg
    me.energy_attached = False
    game._maybe_attach_telepathic_before_party(me, "a")
    assert tele in me.active.energy or any(tele in m.energy for m in me.bench)
    assert len(me.bench) == 2
    game._moon_watching_party(me, me.active)
    fueled = sum(1 for m in me.bench if m.energy)
    assert fueled == 2
