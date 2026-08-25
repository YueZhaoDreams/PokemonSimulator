from random import Random

from app.engine.effects import parse_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C_NAMES, SET_D_NAMES, build_fallback_deck, fallback_named


INVITE_TEXT = (
    "Search your deck for up to 3 Clefairy and put them onto your Bench. Then, shuffle your deck."
)


def _c_with_invite(n: int) -> list[str]:
    rest = [name for name in SET_C_NAMES if name != "Clefairy"]
    return ["Clefairy MEW"] * n + ["Clefairy"] * (4 - n) + rest


def test_moon_viewing_invitation_parses_named_bench():
    effects = parse_effects(INVITE_TEXT)
    assert any(e.get("kind") == "call_family" and e.get("count") == 3 and e.get("name") == "clefairy" for e in effects)


def test_invitation_fallback_does_not_overwrite_party():
    party = fallback_named("Clefairy")
    invite = fallback_named("Clefairy MEW")
    assert party.catalog_id == "swsh11-062"
    assert any("Moon-Watching Party" == a.name for a in party.abilities)
    assert invite.catalog_id == "sv03.5-035"
    assert invite.abilities == []
    assert invite.name == "Clefairy"
    invite_atk = next(a for a in invite.attacks if a.name == "Moon-Viewing Invitation")
    assert invite_atk.cost == ["Psychic"]
    assert any(e.get("kind") == "call_family" and e.get("name") == "clefairy" for e in invite_atk.effects)


def test_mixed_clefairy_prints_are_legal_four_of():
    cards = build_fallback_deck(_c_with_invite(1))
    assert len(cards) == 30
    assert sum(1 for c in cards if c.name == "Clefairy") == 4
    assert sum(1 for c in cards if c.catalog_id == "sv03.5-035") == 1
    assert sum(1 for c in cards if c.catalog_id == "swsh11-062") == 3
    assert copy_violations(cards) == []


def test_invitation_benches_party_clefairy_and_respects_cap():
    c = build_fallback_deck(_c_with_invite(1))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )
    me = game.players["a"]
    invite = next(i for i, card in enumerate(me.cards) if card.catalog_id == "sv03.5-035")
    party = [i for i, card in enumerate(me.cards) if card.catalog_id == "swsh11-062"]
    fuel = next(i for i, card in enumerate(me.cards) if card.name == "Clefable")
    mewtwo = next(i for i, card in enumerate(me.cards) if card.name == "Mewtwo ex")
    me.active = Pokemon(card_i=invite, energy=[fuel])
    me.bench = []
    me.hand = [mewtwo]
    me.deck = list(party)
    game._call_family(me, "a", count=3, name="clefairy")
    # Cap 3 vs Ogerpon, 1 Invitation already Active → bench 2 Party engines.
    assert len(me.bench) == 2
    assert [me.card(m.card_i).catalog_id for m in me.bench] == ["swsh11-062", "swsh11-062"]
    assert game.events.get("moon_viewing_invitation") == 2
    assert len(me.deck) == 1
    assert me.card(me.deck[0]).catalog_id == "swsh11-062"


def test_party_attacks_with_zero_damage_invitation():
    c = build_fallback_deck(_c_with_invite(1))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(
        c,
        d,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("demolish"),
        Random(1),
    )
    me = game.players["a"]
    foe = game.players["b"]
    invite = next(i for i, card in enumerate(me.cards) if card.catalog_id == "sv03.5-035")
    party = [i for i, card in enumerate(me.cards) if card.catalog_id == "swsh11-062"]
    fuel = next(i for i, card in enumerate(me.cards) if card.name == "Clefable")
    oger = next(i for i, card in enumerate(foe.cards) if "Ogerpon" in card.name)
    me.active = Pokemon(card_i=invite, energy=[fuel])
    me.bench = []
    me.deck = list(party)
    foe.active = Pokemon(card_i=oger)
    chosen = game._choose_attack(me, foe, game.strats["a"])
    assert chosen is not None
    assert chosen.name == "Moon-Viewing Invitation"
