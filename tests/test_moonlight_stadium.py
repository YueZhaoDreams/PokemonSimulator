"""Moonlight Stadium (LOT 188) and the early Clefairy Party pivot."""

from random import Random

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, build_fallback_deck, fallback_named

PRINTED = (
    "The Retreat Cost of each Pokémon in play (both yours and your opponent's) "
    "that has any Psychic or Darkness Energy attached to it is Colorless less."
)
OLDER_PRINT = (
    "Each Pokémon (both yours and your opponent's) that has any Psychic or Darkness Energy "
    "attached to it has no Retreat Cost."
)


def test_printed_moonlight_stadium_parses_retreat_cut():
    card = fallback_named("Moonlight Stadium")
    assert card.trainer_kind == "stadium"
    assert card.catalog_id == "sm8-188"
    assert card.text == PRINTED
    eff = parse_ability_effects(card.text)[0]
    assert eff["kind"] == "stadium_retreat_less"
    assert eff["less"] == 1
    assert eff["energy_types"] == ["Psychic", "Darkness"]
    assert eff["both_players"] is True
    zero = parse_ability_effects(OLDER_PRINT)[0]
    assert zero["kind"] == "stadium_retreat_zero"
    assert zero["energy_types"] == ["Psychic", "Darkness"]
    beach = parse_ability_effects(fallback_named("Beach Court").text)
    assert all(e.get("kind") != "stadium_retreat_less" for e in beach)
    zone = next(a.text for a in fallback_named("Clefable ex").abilities if "lunar zone" in a.name.lower())
    assert all(e.get("kind") != "stadium_retreat_zero" for e in parse_ability_effects(zone))


def _names() -> list[str]:
    return (
        ["Clefairy"] * 4
        + ["Mewtwo ex", "Switch", "Battle Cage", "Moonlight Stadium", "Double Colorless Energy", "Darkness Energy"]
        + ["Psychic Energy"] * 8
        + ["Hop"] * 13
    )


def _game(foe_strat: str = "party") -> Game:
    foe = ["Clefairy", "Dragapult ex", "Mewtwo ex"] + ["Psychic Energy"] * 6 + ["Hop"] * 21
    return Game(
        build_fallback_deck(_names()),
        build_fallback_deck(foe),
        standard_60_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(foe_strat),
        Random(1),
        trace=True,
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def test_retreat_cost_follows_the_printed_energy_gate():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = _idxs(me, "Clefairy")[0]
    psychic = _idxs(me, "Psychic Energy")
    darkness = _idxs(me, "Darkness Energy")[0]
    dce = _idxs(me, "Double Colorless Energy")[0]
    bare = Pokemon(card_i=clef)
    paid = Pokemon(card_i=clef, energy=[psychic[0]])
    dark = Pokemon(card_i=clef, energy=[darkness])
    colorless = Pokemon(card_i=clef, energy=[dce])
    assert game._retreat_cost(me, paid) == 2
    game._set_stadium(fallback_named("Moonlight Stadium"))
    assert game._retreat_cost(me, bare) == 2
    assert game._retreat_cost(me, colorless) == 2
    assert game._retreat_cost(me, paid) == 1
    assert game._retreat_cost(me, dark) == 1
    foe_clef = _idxs(foe, "Clefairy")[0]
    foe_pay = _idxs(foe, "Psychic Energy")[0]
    foe.active = Pokemon(card_i=foe_clef, energy=[foe_pay])
    assert game._retreat_cost(foe, foe.active) == 1
    game._set_stadium(fallback_named("Beach Court"))
    assert game._retreat_cost(me, paid) == 1


def _arm(game: Game, *, energy_on_active: bool, switch: bool) -> tuple:
    me = game.players["a"]
    foe = game.players["b"]
    clefs = _idxs(me, "Clefairy")
    mewtwo = _idxs(me, "Mewtwo ex")[0]
    energies = _idxs(me, "Psychic Energy")
    active_energy = [energies[0]] if energy_on_active else []
    me.active = Pokemon(card_i=clefs[0], energy=list(active_energy), played_turn=0)
    me.bench = [
        Pokemon(card_i=clefs[1], played_turn=0),
        Pokemon(card_i=clefs[2], played_turn=0),
        Pokemon(card_i=mewtwo, played_turn=0),
    ]
    hand = [energies[5]]
    if switch:
        hand.append(_idxs(me, "Switch")[0])
    me.hand = hand
    me.deck = list(energies[1:5])
    me.discard = []
    me.retreated = False
    foe.active = Pokemon(card_i=_idxs(foe, "Dragapult ex")[0], played_turn=0)
    game.turn = 4
    return me, clefs


def test_party_pivot_retreats_onto_one_energy_clefairy_then_attaches():
    game = _game()
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, clefs = _arm(game, energy_on_active=True, switch=False)
    leaving = me.active
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") == 1
    assert game.events.get("party_energy") == 4
    assert me.retreated is True
    assert me.active is not leaving
    assert me.card(me.active.card_i).name == "Clefairy"
    assert len(me.active.energy) == 1
    assert me.active.ability_used is True
    # The Clefairy that retreated is back on the bench with the second Party's energy.
    assert any(mon is leaving and len(mon.energy) == 1 for mon in me.bench)
    assert len(me.discard) == 1
    game._attach_energy(me, "a")
    assert len(me.active.energy) == 2
    assert me.card(me.active.energy[-1]).name == "Psychic Energy"
    assert all(mon.card_i != _idxs(me, "Mewtwo ex")[0] or not mon.energy for mon in me.bench)


def test_without_stadium_one_energy_does_not_buy_a_second_party():
    game = _game()
    me, clefs = _arm(game, energy_on_active=True, switch=False)
    active_i = me.active.card_i
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") is None
    assert me.retreated is False
    assert me.active.card_i == active_i
    assert game.events.get("party_energy") == 2


def test_empty_active_cannot_pivot_until_it_has_psychic_or_darkness():
    game = _game()
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=False, switch=False)
    game._use_abilities(me, game.players["b"], "a")
    assert me.retreated is False
    assert game.events.get("moonlight_party_pivot") is None


def test_phantom_pivot_keeps_switch_for_the_tank():
    game = _game("phantom")
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=True, switch=True)
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") == 1
    assert any(me.card(i).name == "Switch" for i in me.hand)
    assert me.card(me.active.card_i).name == "Clefairy"
    game._attach_energy(me, "a")
    assert len(me.active.energy) == 2
    promoted = me.active
    game._maybe_retreat(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Mewtwo ex"
    assert any(me.card(i).name == "Switch" for i in me.discard)
    assert promoted in me.bench
    assert len(promoted.energy) == 2


def test_phantom_without_switch_does_not_strand_clefairy():
    game = _game("phantom")
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=True, switch=False)
    active_i = me.active.card_i
    game._use_abilities(me, game.players["b"], "a")
    assert me.retreated is False
    assert me.active.card_i == active_i
    assert game.events.get("moonlight_party_pivot") is None


def test_early_moonlight_plays_before_cage_and_cage_waits():
    game = _game("phantom")
    me = game.players["a"]
    clefs = _idxs(me, "Clefairy")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], played_turn=0)]
    moon = _idxs(me, "Moonlight Stadium")[0]
    cage = _idxs(me, "Battle Cage")[0]
    me.hand = [moon, cage]
    assert me.card(game._pick_trainer(me)).name == "Moonlight Stadium"
    game._set_stadium(me.card(moon))
    me.hand = [cage]
    assert game._pick_trainer(me) is None
    fuels = _idxs(me, "Psychic Energy")[:6]
    me.active.energy = list(fuels)
    assert me.card(game._pick_trainer(me)).name == "Battle Cage"


def test_non_phantom_does_not_bump_moonlight_with_cage():
    game = _game("party")
    me = game.players["a"]
    clefs = _idxs(me, "Clefairy")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.hand = [_idxs(me, "Battle Cage")[0]]
    game._set_stadium(fallback_named("Moonlight Stadium"))
    assert game._pick_trainer(me) is None


def test_live_c60_has_no_moonlight_until_a_cut_wins():
    assert "Moonlight Stadium" not in SET_C60_NAMES


def test_moonlight_swap_matrix_keeps_the_lock():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-moonlight-stadium.json").read_text()
    )
    assert blob["games"] == 3000
    assert blob["seed"] == 20260926
    assert set(blob["cells"]) == {"lock", *blob["cuts"]}
    assert blob["weighted_competitive"]["lock"] == max(blob["weighted_competitive"].values())
    assert blob["weighted_all"]["lock"] == max(blob["weighted_all"].values())
    t60 = {key: row["t60"]["a"] for key, row in blob["cells"].items()}
    assert t60["lock"] == max(t60.values())
