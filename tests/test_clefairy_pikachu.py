from random import Random

from app.catalog import fetch_full, normalize_card
from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import Card, default_family_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import build_fallback_deck, fallback_named


def test_wonder_storm_parses_psychic_energy_times():
    effects = parse_effects(
        "This attack does 20 damage for each Psychic Energy attached to all of your Pokémon.",
        "20×",
    )
    assert {"kind": "psychic_energy_times", "per": 20} in effects


def test_wonder_storm_counts_psychic_pokemon_as_energy():
    """Family Cup: Psychic Pokémon attached as energy count toward Wonder Storm."""
    a = build_fallback_deck(
        ["Clefairy", "Pumpkaboo", "Kadabra", "Dusclops", "Flutter Mane", "Psychic Energy"] + ["Sobble"] * 22
    )
    b = build_fallback_deck(["Pikachu"] + ["Cubone"] * 27)
    game = Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("control"),
        Random(1),
        trace=True,
    )
    me = game.players["a"]
    # Put Clefairy active with 3 energy slots filled by Psychic Energy + Psychic Pokémon-as-energy.
    clef_i = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fuel = [i for i, c in enumerate(me.cards) if c.name in {"Psychic Energy", "Pumpkaboo", "Kadabra", "Dusclops"}][:4]
    from app.engine.game import Pokemon

    me.active = Pokemon(card_i=clef_i, energy=list(fuel))
    me.hand = []
    me.bench = []
    count = game._count_psychic_energy_in_play(me)
    assert count >= 4
    # Damage should be 20 × count (80–100 range when well fueled).
    assert 20 * count >= 80


def test_two_carpet_pikachu_prints_differ():
    nuzzle = normalize_card(fetch_full("sm12-66"))
    shock = normalize_card(fetch_full("sm3-40"))
    assert [a.name for a in nuzzle.attacks] == ["Nuzzle", "Volt Tackle"]
    assert [a.name for a in shock.attacks] == ["Tail Whap", "Thunder Shock"]


def test_clefairy_fallback_has_scaling_effect():
    card = fallback_named("Clefairy")
    assert any(e.get("kind") == "psychic_energy_times" for a in card.attacks for e in a.effects)
    party = next(a for a in card.abilities if "moon-watching" in (a.name or "").lower())
    assert "for each of your Benched Clefairy" in party.text
    assert "search your deck" in party.text.lower()
    assert "top 6" not in party.text.lower()
    effects = parse_ability_effects(party.text)
    assert effects[0]["kind"] == "attach_energy_from_deck_per_benched"
    assert effects[0]["benched_name"] == "clefairy"
    assert effects[0]["energy_type"] == "Psychic"


def test_ability_parser_does_not_invent_a_top_look():
    official = fallback_named("Clefairy").abilities[0].text
    assert parse_ability_effects(official)[0]["kind"] == "attach_energy_from_deck_per_benched"
    fake = (
        "Once during your turn, if this Pokémon is in the Active Spot, look at the top 6 cards "
        "of your deck. Attach any number of Psychic Energy cards you find there to your Benched "
        "Clefairy in any way you like. Shuffle the other cards back into your deck."
    )
    fake_eff = parse_ability_effects(fake)
    assert fake_eff[0]["kind"] == "attach_energy_from_top"
    assert fake_eff[0]["look"] == 6
    assert all(e["kind"] != "attach_energy_from_deck_per_benched" for e in fake_eff)


def _cb_game() -> Game:
    payload = load_seed_payload()
    c = [Card.from_dict(x) for x in payload["c"]["cards"]]
    b = [Card.from_dict(x) for x in payload["b"]["cards"]]
    return Game(
        c,
        b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict("shock"),
        Random(1),
    )


def test_wonder_storm_with_three_psychic_kos_pikachu():
    """Printed Wonder Storm is 20 × Psychic in play. 3 energy = 60, one-shots 60 HP Pikachu."""
    game = _cb_game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    fuels = [i for i, c in enumerate(me.cards) if c.types == ["Psychic"] and c.name != "Clefairy"][:3]
    pika = next(
        i
        for i, c in enumerate(foe.cards)
        if c.name == "Pikachu" and any(a.name == "Thunder Shock" for a in c.attacks)
    )
    me.active = Pokemon(card_i=clef, energy=list(fuels))
    foe.active = Pokemon(card_i=pika)
    atk = next(a for a in me.card(clef).attacks if a.name == "Wonder Storm")
    assert "for each Psychic Energy attached to all of your Pokémon" in atk.text
    assert game._effective_damage(me, foe, atk) == 60
    assert game._wonder_storm_ko(me, foe)


def test_party_charges_active_clefairy_vs_pikachu_not_mewtwo():
    """Wonder Storm costs Colorless × 3. Turn attach must go to Active Clefairy vs B, not benched Mewtwo."""
    game = _cb_game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    pika = next(i for i, c in enumerate(foe.cards) if c.name == "Pikachu")
    me.active = Pokemon(card_i=clef)
    me.bench = [Pokemon(card_i=mewtwo)]
    foe.active = Pokemon(card_i=pika)
    assert game._energy_target(me, StrategySpec.from_dict("party")) is me.active
    assert game._want_wonder_storm(me, foe)


def test_party_stays_on_clefairy_when_wonder_storm_kos():
    game = _cb_game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fuels = [i for i, c in enumerate(me.cards) if c.types == ["Psychic"] and c.name != "Clefairy"][:3]
    pika = next(i for i, c in enumerate(foe.cards) if c.name == "Pikachu")
    me.active = Pokemon(card_i=clef, energy=list(fuels), ability_used=True)
    me.bench = [Pokemon(card_i=mewtwo)]
    foe.active = Pokemon(card_i=pika)
    game._retreat_party(me, foe, "a")
    assert me.card(me.active.card_i).name == "Clefairy"


def test_party_does_not_fast_line_off_clefairy_vs_pikachu():
    """Retreat cost 2 would dump Wonder Storm energy to chase Photon into 60 HP."""
    game = _cb_game()
    me = game.players["a"]
    foe = game.players["b"]
    clef = next(i for i, c in enumerate(me.cards) if c.name == "Clefairy")
    mewtwo = next(i for i, c in enumerate(me.cards) if c.name == "Mewtwo ex")
    fuels = [i for i, c in enumerate(me.cards) if c.types == ["Psychic"] and c.name != "Clefairy"][:2]
    pika = next(i for i, c in enumerate(foe.cards) if c.name == "Pikachu")
    me.active = Pokemon(card_i=clef, energy=list(fuels), ability_used=True)
    me.bench = [Pokemon(card_i=mewtwo)]
    foe.active = Pokemon(card_i=pika)
    assert game._should_transfer_combo(me, foe) is False
