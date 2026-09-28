"""Moonlight Stadium (Great Encounters 100) and the early Clefairy Party pivot."""

from random import Random

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Card, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, build_fallback_deck, fallback_named

PRINTED = (
    "The Retreat Cost for each Psychic and Darkness Pokémon "
    "(both yours and your opponent's) is 0."
)
GLYPH = (
    "The Retreat Cost for each {P} and {D} Pokémon (both yours and your opponent's) is 0."
)
ENERGY_LESS = (
    "The Retreat Cost of each Pokémon in play (both yours and your opponent's) "
    "that has any Psychic or Darkness Energy attached to it is Colorless less."
)
ENERGY_ZERO = (
    "Each Pokémon (both yours and your opponent's) that has any Psychic or Darkness Energy "
    "attached to it has no Retreat Cost."
)


def _stadium(text: str) -> Card:
    return Card(
        catalog_id="test-moonlight",
        name="Moonlight Stadium",
        category="Trainer",
        trainer_kind="stadium",
        text=text,
    )


def test_printed_moonlight_stadium_parses_free_retreat():
    card = fallback_named("Moonlight Stadium")
    assert card.trainer_kind == "stadium"
    assert card.catalog_id == "dp4-100"
    assert card.image == "https://assets.tcgdex.net/en/dp/dp4/100/low.webp"
    assert card.text == PRINTED
    eff = parse_ability_effects(card.text)[0]
    assert eff["kind"] == "stadium_retreat_zero"
    assert eff["pokemon_types"] == ["Psychic", "Darkness"]
    assert eff.get("energy_types") is None
    assert eff["both_players"] is True
    glyph = parse_ability_effects(GLYPH)[0]
    assert glyph["kind"] == "stadium_retreat_zero"
    assert glyph["pokemon_types"] == ["Psychic", "Darkness"]
    less = parse_ability_effects(ENERGY_LESS)[0]
    assert less["kind"] == "stadium_retreat_less"
    assert less["less"] == 1
    assert less["energy_types"] == ["Psychic", "Darkness"]
    zero = parse_ability_effects(ENERGY_ZERO)[0]
    assert zero["kind"] == "stadium_retreat_zero"
    assert zero["energy_types"] == ["Psychic", "Darkness"]
    assert "pokemon_types" not in zero
    beach = parse_ability_effects(fallback_named("Beach Court").text)
    assert all(e.get("kind") not in {"stadium_retreat_less", "stadium_retreat_zero"} for e in beach)
    zone = next(a.text for a in fallback_named("Clefable ex").abilities if "lunar zone" in a.name.lower())
    assert all(e.get("kind") != "stadium_retreat_zero" for e in parse_ability_effects(zone))
    basic_zero = (
        "The Retreat Cost of each Basic Pokémon in play (both yours and your opponent's) is 0."
    )
    assert all(e.get("kind") != "stadium_retreat_zero" for e in parse_ability_effects(basic_zero))


def _names() -> list[str]:
    return (
        ["Clefairy"] * 4
        + ["Mewtwo ex", "Clefable ex", "Fezandipiti ex", "Switch", "Battle Cage", "Moonlight Stadium"]
        + ["Double Colorless Energy", "Darkness Energy"]
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


def test_retreat_cost_is_zero_for_psychic_and_darkness_pokemon():
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
    mewtwo = Pokemon(card_i=_idxs(me, "Mewtwo ex")[0], energy=[psychic[1]])
    fez = Pokemon(card_i=_idxs(me, "Fezandipiti ex")[0])
    assert game._retreat_cost(me, bare) == 2
    game._set_stadium(fallback_named("Moonlight Stadium"))
    assert game._retreat_cost(me, bare) == 0
    assert game._retreat_cost(me, colorless) == 0
    assert game._retreat_cost(me, paid) == 0
    assert game._retreat_cost(me, dark) == 0
    assert me.card(mewtwo.card_i).types == ["Lightning"]
    assert game._retreat_cost(me, mewtwo) == 2
    assert me.card(fez.card_i).types == ["Darkness"]
    assert me.card(fez.card_i).retreat == 1
    assert game._retreat_cost(me, fez) == 0
    foe_clef = _idxs(foe, "Clefairy")[0]
    foe.active = Pokemon(card_i=foe_clef)
    assert game._retreat_cost(foe, foe.active) == 0
    pult = Pokemon(card_i=_idxs(foe, "Dragapult ex")[0])
    assert foe.card(pult.card_i).types == ["Dragon"]
    assert foe.card(pult.card_i).retreat == 1
    assert game._retreat_cost(foe, pult) == 1
    game._set_stadium(fallback_named("Beach Court"))
    assert game._retreat_cost(me, paid) == 1


def test_energy_gated_prints_still_need_psychic_or_darkness_energy():
    game = _game()
    me = game.players["a"]
    clef = _idxs(me, "Clefairy")[0]
    psychic = _idxs(me, "Psychic Energy")[0]
    dce = _idxs(me, "Double Colorless Energy")[0]
    bare = Pokemon(card_i=clef)
    paid = Pokemon(card_i=clef, energy=[psychic])
    colorless = Pokemon(card_i=clef, energy=[dce])
    game._set_stadium(_stadium(ENERGY_LESS))
    assert game._retreat_cost(me, bare) == 2
    assert game._retreat_cost(me, colorless) == 2
    assert game._retreat_cost(me, paid) == 1
    game._set_stadium(_stadium(ENERGY_ZERO))
    assert game._retreat_cost(me, bare) == 2
    assert game._retreat_cost(me, paid) == 0


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


def test_empty_active_parties_retreats_free_then_attaches():
    game = _game()
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=False, switch=False)
    leaving = me.active
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") == 1
    assert game.events.get("party_energy") == 4
    assert me.retreated is True
    assert me.active is not leaving
    assert me.card(me.active.card_i).name == "Clefairy"
    assert len(me.active.energy) == 1
    assert me.active.ability_used is True
    assert any(mon is leaving and len(mon.energy) == 1 for mon in me.bench)
    assert me.discard == []
    assert not any(me.card(i).name == "Switch" for i in me.discard)
    game._attach_energy(me, "a")
    assert len(me.active.energy) == 2
    assert me.card(me.active.energy[-1]).name == "Psychic Energy"
    assert all(mon.card_i != _idxs(me, "Mewtwo ex")[0] or not mon.energy for mon in me.bench)


def test_pivot_keeps_energy_already_on_the_active():
    game = _game()
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=True, switch=True)
    leaving = me.active
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") == 1
    assert me.discard == []
    assert any(me.card(i).name == "Switch" for i in me.hand)
    assert any(mon is leaving and len(mon.energy) == 2 for mon in me.bench)
    assert len(me.active.energy) == 1


def test_without_stadium_one_energy_does_not_buy_a_second_party():
    game = _game()
    me, _clefs = _arm(game, energy_on_active=True, switch=False)
    active_i = me.active.card_i
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") is None
    assert me.retreated is False
    assert me.active.card_i == active_i
    assert game.events.get("party_energy") == 2


def test_lunar_zone_alone_does_not_use_the_stadium_pivot():
    game = _game()
    me, _clefs = _arm(game, energy_on_active=True, switch=False)
    me.bench.append(Pokemon(card_i=_idxs(me, "Clefable ex")[0], played_turn=0))
    game._use_abilities(me, game.players["b"], "a")
    assert game.events.get("moonlight_party_pivot") is None


def test_phantom_pivot_keeps_switch_for_the_tank():
    game = _game("phantom")
    game._set_stadium(fallback_named("Moonlight Stadium"))
    me, _clefs = _arm(game, energy_on_active=False, switch=True)
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
    me, _clefs = _arm(game, energy_on_active=False, switch=False)
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


def test_live_c60_swaps_one_ultra_ball_for_moonlight():
    assert SET_C60_NAMES.count("Moonlight Stadium") == 1
    assert SET_C60_NAMES.count("Ultra Ball") == 1
    assert len(SET_C60_NAMES) == 60


def test_moonlight_swap_matrix_keeps_the_lock():
    import json
    from pathlib import Path

    blob = json.loads(
        (Path(__file__).resolve().parents[1] / "data/lab/set-c60-moonlight-stadium.json").read_text()
    )
    assert blob["games"] == 3000
    assert blob["seed"] == 20260926
    assert blob["catalog_id"] == "dp4-100"
    assert blob["printed"] == PRINTED
    assert set(blob["cells"]) == {"lock", *blob["cuts"]}
    wcomp = blob["weighted_competitive"]
    assert max(wcomp, key=wcomp.get) == "ultra"
    t60 = {key: row["t60"]["a"] for key, row in blob["cells"].items()}
    assert max(t60, key=t60.get) == "lock"
    lock = blob["cells"]["lock"]
    for key, row in blob["cells"].items():
        if key == "lock":
            continue
        assert not all(row[foe]["a"] > lock[foe]["a"] for foe in ("t60", "hedrick", "d60"))
