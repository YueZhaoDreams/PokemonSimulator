"""Manaphy is the damage layer next to Battle Cage on the Mew baby list.

Wave Veil prevents attack damage to the Bench. It is played only when an
opposing attack can do that damage. Penny or one Energy gets it off the Active
Spot. Battle Cage remains the card that stops damage counters.
"""

from random import Random

from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import (
    SET_D60_NAMES,
    SET_M60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    build_fallback_deck,
    fallback_named,
)


def _game(foe_names: list[str]) -> Game:
    ours = list(SET_M60_NAMES)
    ours[ours.index("Crushing Hammer")] = "Manaphy"
    return Game(
        build_fallback_deck(ours),
        build_fallback_deck(list(foe_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("phantom" if "Dragapult ex" in foe_names else "demolish"),
        Random(1),
    )


def _add(player, name: str) -> int:
    player.cards.append(fallback_named(name))
    return len(player.cards) - 1


def test_dragapult_lists_do_bench_damage_and_ogerpon_does_not():
    drag = _game(list(SET_T60_NAMES))
    hedrick = _game(list(SET_T_META_NAMES))
    oger = _game(list(SET_D60_NAMES))
    assert drag._foe_has_bench_attack_damage(drag.players["a"])
    assert hedrick._foe_has_bench_attack_damage(hedrick.players["a"])
    assert not oger._foe_has_bench_attack_damage(oger.players["a"])


def test_manaphy_benches_against_cruel_arrow_and_stays_in_hand_otherwise():
    drag = _game(list(SET_T60_NAMES))
    me = drag.players["a"]
    me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Mew ex"))
    me.bench = []
    me.hand = [next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")]
    me.deck = []
    drag._play_basics(me)
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy"]

    quiet = _game(list(SET_D60_NAMES))
    me = quiet.players["a"]
    me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Mew ex"))
    me.bench = []
    mana = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    me.hand = [mana]
    me.deck = []
    quiet._play_basics(me)
    assert me.bench == []
    assert mana in me.hand


def test_babies_fill_before_manaphy_keeps_the_last_slot():
    game = _game(list(SET_T60_NAMES))
    me = game.players["a"]
    names = ["Igglybuff", "Igglybuff", "Budew", "Mime Jr.", "Mime Jr.", "Manaphy"]
    idxs = []
    for name in names:
        me.cards.append(fallback_named(name))
        idxs.append(len(me.cards) - 1)
    me.active = Pokemon(card_i=next(i for i, c in enumerate(me.cards) if c.name == "Mew ex"))
    me.bench = []
    me.hand = idxs
    me.deck = []
    game._play_basics(me)
    benched = [me.card(mon.card_i).name for mon in me.bench]
    assert benched[-1] == "Manaphy"
    assert benched.count("Manaphy") == 1
    assert len(benched) == 5
    assert sum(1 for name in benched if name != "Manaphy") == 4


def test_penny_returns_active_manaphy_then_it_is_replayed_to_the_bench():
    game = _game(list(SET_T60_NAMES))
    me = game.players["a"]
    mana_i = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    penny_i = next(i for i, c in enumerate(me.cards) if c.name == "Penny")
    me.active = Pokemon(card_i=mana_i)
    me.bench = [Pokemon(card_i=mew_i)]
    me.hand = [penny_i]
    me.deck = []
    me.discard = []
    me.supporter_used = False
    game._play_trainers(me, game.players["b"], "a")
    assert game.events.get("bounce:Penny") == 1
    assert me.card(me.active.card_i).name == "Mew ex"
    assert mana_i in me.hand
    game._play_basics(me)
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy"]


def test_penny_keeps_manaphy_in_hand_when_the_foe_has_no_bench_damage():
    game = _game(list(SET_D60_NAMES))
    me = game.players["a"]
    mana_i = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    penny_i = next(i for i, c in enumerate(me.cards) if c.name == "Penny")
    me.active = Pokemon(card_i=mana_i)
    me.bench = [Pokemon(card_i=mew_i)]
    me.hand = [penny_i]
    me.deck = []
    me.discard = []
    me.supporter_used = False
    game._play_trainers(me, game.players["b"], "a")
    game._play_basics(me)
    assert me.card(me.active.card_i).name == "Mew ex"
    assert mana_i in me.hand
    assert me.bench == []


def test_one_energy_retreats_active_manaphy_onto_the_bench():
    game = _game(list(SET_T60_NAMES))
    me = game.players["a"]
    mana_i = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    spike_i = next(i for i, c in enumerate(me.cards) if c.name == "Spiky Energy")
    me.active = Pokemon(card_i=mana_i, energy=[spike_i])
    me.bench = [Pokemon(card_i=mew_i)]
    me.hand = []
    me.retreated = False
    game._retreat_baby(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Mew ex"
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy"]
    assert spike_i in me.discard


def test_spiky_attaches_to_active_manaphy_so_it_can_retreat():
    game = _game(list(SET_T60_NAMES))
    me = game.players["a"]
    mana_i = next(i for i, c in enumerate(me.cards) if c.name == "Manaphy")
    mew_i = next(i for i, c in enumerate(me.cards) if c.name == "Mew ex")
    spike_i = next(i for i, c in enumerate(me.cards) if c.name == "Spiky Energy")
    me.active = Pokemon(card_i=mana_i)
    me.bench = [Pokemon(card_i=mew_i)]
    me.hand = [spike_i]
    me.deck = []
    me.energy_attached = False
    assert game._energy_target(me, game.strats["a"]) is me.active
    game._attach_energy(me, "a")
    game._retreat_baby(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Mew ex"
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Manaphy"]
