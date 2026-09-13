from app.catalog import _tcgdex_low
from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.models import default_rule_presets_for, standard_60_rules
from app.seed import load_seed_deck, load_seed_payload
from app.seed_data import SET_G_NAMES, build_fallback_deck, fallback_named


def test_set_g_is_sixty_after_staraptor_energy_swap():
    assert len(SET_G_NAMES) == 60
    names = list(SET_G_NAMES)
    assert names.count("Staravia") == 2
    assert names.count("Staraptor") == 2
    assert names.count("Plusle") == 1
    assert names.count("Kecleon") == 1
    assert names.count("Potion") == 1
    assert names.count("Trapinch") == 0
    assert names.count("Iron Boulder") == 0
    assert names.count("Scatterbug") == 0
    assert names.count("Misdreavus") == 0
    assert names.count("Psychic Energy") == 17
    assert names.count("Darkness Energy") == 3
    assert names.count("Boomerang Energy") == 1
    assert names.count("Clefairy") == 4
    assert names.count("Ledyba") == 4
    assert names.count("Ledian") == 4
    assert names.count("Mega Clefable ex") == 0
    assert "Tulip" in names
    assert "Surfer" in names
    assert "Drayton" in names
    assert "Jacq" not in names
    assert "Arven" not in names
    pile = build_fallback_deck(names)
    assert [c.name for c in pile] == names
    assert any(c.name == "Boomerang Energy" for c in pile)
    boom = next(c for c in pile if c.name == "Boomerang Energy")
    assert "discarded by an effect of an attack" in (boom.text or "").lower()


def test_set_g_seed_payload_and_s60_preset():
    data = load_seed_payload()
    g = data["g"]
    names = [c["name"] for c in g["cards"]]
    assert g["id"] == "seed-g"
    assert g["name"] == "Carpet Set G (Clefairy / Ledian 60)"
    assert g["sample"] == "set-g-carpet.jpg"
    assert g["kind"] == "list"
    assert names == list(SET_G_NAMES)
    assert len(g["cards"]) == 60
    for card in g["cards"]:
        assert card.get("image"), f"{card['name']} {card.get('catalog_id')} has no image"
        assert str(card["image"]).startswith("http")
    starly = [c for c in g["cards"] if c["name"] == "Starly"]
    assert [c["catalog_id"] for c in starly] == ["swsh9-117", "swsh9-117"]
    assert all(any(a["name"] == "Claw" for a in c["attacks"]) for c in starly)
    staravia = [c for c in g["cards"] if c["name"] == "Staravia"]
    assert [c["catalog_id"] for c in staravia] == ["swsh9-118", "sv01-149"]
    assert staravia[0]["hp"] == 90
    assert staravia[1]["hp"] == 80
    boom = next(c for c in g["cards"] if c["name"] == "Boomerang Energy")
    assert boom["catalog_id"] == "sv06-166"
    poke = next(c for c in g["cards"] if c["name"] == "Poké Ball")
    assert poke.get("image")
    mewtwo = next(c for c in g["cards"] if c["name"] == "Mewtwo")
    assert mewtwo["catalog_id"] == "sv07-059"
    assert any(a["name"] == "Super Psy Bolt" for a in mewtwo["attacks"])
    plusle = next(c for c in g["cards"] if c["name"] == "Plusle")
    assert plusle["catalog_id"] == "sv04-060"
    assert plusle["attacks"][0]["name"] == "Plus Damage"
    kecleon = next(c for c in g["cards"] if c["name"] == "Kecleon")
    assert kecleon["catalog_id"] == "sv08-150"
    indeedee = next(c for c in g["cards"] if c["name"] == "Indeedee")
    assert indeedee["catalog_id"] == "sv01-153"
    supporters = [c["name"] for c in g["cards"] if c["name"] in {"Tulip", "Surfer", "Drayton", "Jacq", "Arven"}]
    assert supporters == ["Tulip", "Surfer", "Drayton"]
    assert default_rule_presets_for("seed-g") == ["s60"]
    assert standard_60_rules().deck_size == 60
    loaded = load_seed_deck("g")
    assert loaded["id"] == "seed-g"
    assert load_seed_deck("10")["id"] == "seed-g"
    assert load_seed_deck("seed-g")["id"] == "seed-g"


def test_set_g_printings_match_carpet_attacks():
    ledian = fallback_named("Ledian")
    assert ledian.catalog_id == "sv07-003"
    assert any(a.name == "Swift" for a in ledian.attacks)
    assert ledian.abilities and ledian.abilities[0].name == "Glittering Star Pattern"
    munk = fallback_named("Munkidori")
    assert munk.abilities[0].name == "Adrena-Brain"
    assert "{D}" in (munk.abilities[0].text or "")
    boulder = fallback_named("Iron Boulder")
    assert boulder.types == ["Psychic"]
    horn = next(a for a in boulder.attacks if a.name == "Adjusted Horn")
    assert horn.text == (
        "If you don't have the same number of cards in your hand as your opponent, this attack does nothing."
    )
    assert any(e.get("kind") == "require_equal_hands" for e in horn.effects)
    assert not any(e.get("kind") == "coin_whiff" for e in horn.effects)
    assert parse_effects(horn.text) == [{"kind": "require_equal_hands"}]
    flutter = fallback_named("Flutter Mane")
    assert any(a.name == "Midnight Fluttering" for a in flutter.abilities)
    dedenne = fallback_named("Dedenne")
    flash = next(a for a in dedenne.attacks if a.name == "Dede-Flash")
    assert flash.text == (
        "If your opponent has exactly 1 Prize card remaining, this attack does 60 more damage, "
        "and your opponent's Active Pokémon is now Confused."
    )
    kinds = {e.get("kind") for e in parse_effects(flash.text)}
    assert "opponent_prize_bonus" in kinds
    confuse = next(e for e in parse_effects(flash.text) if e.get("kind") == "status")
    assert confuse.get("if_opponent_prizes") == 1
    balloon = next(a for a in fallback_named("Drifblim").attacks if a.name == "Spooky Balloon")
    assert balloon.text == "Put 2 damage counters on 1 of your opponent's Benched Pokémon."
    assert any(e.get("kind") == "bench_damage_counters" for e in parse_effects(balloon.text))
    spin = next(a for a in fallback_named("Drifloon").attacks if a.name == "Triple Spin")
    assert spin.text == "Flip 3 coins. This attack does 10 damage for each heads."
    assert parse_effects(spin.text, "10×") == [{"kind": "coin_times", "flips": 3, "per": 10}]
    assert _tcgdex_low("me03-031") == "https://assets.tcgdex.net/en/me/me03/031/low.webp"
    assert _tcgdex_low("pl1-83") == "https://assets.tcgdex.net/en/pl/pl1/83/low.webp"
    missy = fallback_named("Misdreavus")
    assert missy.catalog_id == "pl1-83"
    assert missy.hp == 50
    assert [a.name for a in missy.attacks] == ["Take Back", "Tackle"]
    take = next(a for a in missy.attacks if a.name == "Take Back")
    assert take.cost == []
    assert take.text == (
        "Flip a coin. If heads, search your discard pile for a Trainer card, "
        "show it to your opponent, and put it into your hand."
    )
    assert parse_effects(take.text) == [{"kind": "recycle_trainer_from_discard", "coin": True}]
    mag = fallback_named("Mismagius")
    assert mag.catalog_id == "pl1-55"
    assert mag.hp == 90
    assert [a.name for a in mag.attacks] == ["Upper Hand", "Psybeam"]
    hand = next(a for a in mag.attacks if a.name == "Upper Hand")
    assert hand.damage == 30
    assert hand.text == (
        "Choose 1 of the Defending Pokémon's attacks. "
        "That Pokémon can't use that attack during your opponent's next turn."
    )
    assert parse_effects(hand.text) == [{"kind": "disable_attack"}]
    beam = next(a for a in mag.attacks if a.name == "Psybeam")
    assert beam.damage == 60
    assert beam.cost == ["Psychic", "Colorless", "Colorless"]
    assert parse_effects(beam.text) == [{"kind": "status", "status": "confused", "coin": True}]
    tulip = next(c for c in load_seed_payload()["g"]["cards"] if c["name"] == "Tulip")
    surf = next(c for c in load_seed_payload()["g"]["cards"] if c["name"] == "Surfer")
    assert tulip["catalog_id"] == "sv04-181"
    assert surf["catalog_id"] == "sv08-187"


def _ghost_game():
    from random import Random

    from app.engine.game import Game
    from app.engine.models import default_family_rules
    from app.engine.strategies import StrategySpec

    a = build_fallback_deck(["Misdreavus", "Mismagius", "Ultra Ball"] + ["Psychic Energy"] * 4 + ["Hop"] * 4 + ["Cubone"] * 19)
    b = build_fallback_deck(["Staraptor", "Starly"] + ["Psychic Energy"] * 4 + ["Hop"] * 4 + ["Cubone"] * 20)
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("thrifty"),
        Random(1),
        trace=True,
    )


def test_take_back_recycles_trainer_on_heads():
    from app.engine.game import Pokemon

    game = _ghost_game()
    me = game.players["a"]
    foe = game.players["b"]
    missy = next(i for i, c in enumerate(me.cards) if c.name == "Misdreavus")
    ball = next(i for i, c in enumerate(me.cards) if c.name == "Ultra Ball")
    me.active = Pokemon(card_i=missy, played_turn=0)
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    me.discard = [ball]
    me.hand = []
    game.rng.random = lambda: 0.9
    game._attack(me, foe, "a")
    assert ball in me.hand
    assert ball not in me.discard
    assert game.events.get("take_back") == 1


def test_take_back_tails_leaves_discard():
    from app.engine.game import Pokemon

    game = _ghost_game()
    me = game.players["a"]
    foe = game.players["b"]
    missy = next(i for i, c in enumerate(me.cards) if c.name == "Misdreavus")
    ball = next(i for i, c in enumerate(me.cards) if c.name == "Ultra Ball")
    me.active = Pokemon(card_i=missy, played_turn=0)
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    me.discard = [ball]
    me.hand = []
    game.rng.random = lambda: 0.1
    game._attack(me, foe, "a")
    assert ball in me.discard
    assert ball not in me.hand
    assert game.events.get("take_back_tails") == 1


def test_upper_hand_locks_strongest_attack_until_end_of_next_turn():
    from app.engine.game import Pokemon
    from app.engine.strategies import StrategySpec

    game = _ghost_game()
    me = game.players["a"]
    foe = game.players["b"]
    mag = next(i for i, c in enumerate(me.cards) if c.name == "Mismagius")
    raptor = next(i for i, c in enumerate(foe.cards) if c.name == "Staraptor")
    fuels = [i for i, c in enumerate(foe.cards) if c.name == "Psychic Energy"][:3]
    psychic = next(i for i, c in enumerate(me.cards) if c.name == "Psychic Energy")
    me.active = Pokemon(card_i=mag, energy=[psychic], played_turn=0)
    foe.active = Pokemon(card_i=raptor, energy=list(fuels), played_turn=0)
    game._attack(me, foe, "a")
    assert foe.active.disabled_attack == "Power Blast"
    picked = game._choose_attack(foe, me, StrategySpec.from_dict("thrifty"))
    assert picked is not None
    assert picked.name == "Tailspin Away"
    game._expire_disabled_attacks(foe)
    assert foe.active.disabled_attack is None


def _skill_game(strat_a="g", strat_b="party"):
    from random import Random

    from app.engine.game import Game
    from app.engine.models import default_family_rules
    from app.engine.strategies import StrategySpec

    a = build_fallback_deck(
        ["Clefairy"] * 4
        + ["Ledyba", "Ledian", "Flutter Mane", "Munkidori", "Surfer"]
        + ["Psychic Energy"] * 8
        + ["Darkness Energy"] * 3
        + ["Hop"] * 4
        + ["Cubone"] * 6
    )
    b = build_fallback_deck(
        ["Clefairy"] * 4
        + ["Clefable ex", "Starly", "Staraptor", "Flutter Mane", "Munkidori"]
        + ["Psychic Energy"] * 8
        + ["Darkness Energy"] * 2
        + ["Hop"] * 4
        + ["Cubone"] * 7
    )
    return Game(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict(strat_a),
        StrategySpec.from_dict(strat_b),
        Random(1),
        trace=True,
    )


def test_ledian_and_flutter_mane_abilities_parse_printed_text():
    ledian = fallback_named("Ledian")
    gust = parse_ability_effects(ledian.abilities[0].text)
    assert gust == [{"kind": "gust_low_hp_on_evolve", "max_remaining": 90}]
    flutter = fallback_named("Flutter Mane")
    kinds = [e.get("kind") for abi in flutter.abilities for e in parse_ability_effects(abi.text)]
    assert "suppress_opponent_active_abilities" in kinds


def test_g_strategy_fires_moon_watching_party():
    from app.engine.game import Pokemon

    game = _skill_game("g", "party")
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], played_turn=0), Pokemon(card_i=clefs[2], played_turn=0)]
    me.deck = list(fuels[:4])
    me.hand = []
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    game._use_abilities(me, foe, "a")
    assert game.events.get("moon_watching_party") == 1
    assert [len(m.energy) for m in me.bench] == [1, 1]


def test_carnival_still_skips_party_on_the_same_board():
    from app.engine.game import Pokemon

    game = _skill_game("carnival", "party")
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], played_turn=0)]
    me.deck = list(fuels[:3])
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Starly"), played_turn=0)
    game._use_abilities(me, foe, "a")
    assert game.events.get("moon_watching_party", 0) == 0
    assert me.bench[0].energy == []


def test_ledian_gusts_low_hp_bench_on_evolve():
    from app.engine.game import Pokemon

    game = _skill_game("g", "party")
    me = game.players["a"]
    foe = game.players["b"]
    ledyba = next(i for i, c in enumerate(me.cards) if c.name == "Ledyba")
    ledian = next(i for i, c in enumerate(me.cards) if c.name == "Ledian")
    raptor = next(i for i, c in enumerate(foe.cards) if c.name == "Staraptor")
    snack = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=ledyba, played_turn=0)
    me.hand = [ledian]
    foe.active = Pokemon(card_i=raptor, played_turn=0)
    foe.bench = [Pokemon(card_i=snack, played_turn=0)]
    game.turn = 2
    game._do_evolve(me, me.active, ledian)
    assert me.card(me.active.card_i).name == "Ledian"
    assert foe.card(foe.active.card_i).name == "Clefairy"
    assert game.events.get("glittering_star") == 1


def test_flutter_mane_shuts_active_party_but_not_benched_adrena_brain():
    from app.engine.game import Pokemon

    game = _skill_game("party", "g")
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    flutter = next(i for i, c in enumerate(foe.cards) if c.name == "Flutter Mane")
    munk = next(i for i, c in enumerate(foe.cards) if c.name == "Munkidori")
    dark = next(i for i, c in enumerate(foe.cards) if c.name == "Darkness Energy")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], played_turn=0)]
    me.deck = list(fuels[:3])
    foe.active = Pokemon(card_i=flutter, damage=30, played_turn=0)
    foe.bench = [Pokemon(card_i=munk, energy=[dark], played_turn=0)]
    game._use_abilities(me, foe, "a")
    assert game.events.get("moon_watching_party", 0) == 0
    assert me.bench[0].energy == []
    assert game._abilities_suppressed(me, me.active) is True
    game._use_abilities(foe, me, "b")
    assert game.events.get("adrena_brain") == 1
    assert me.active.damage == 30
    assert foe.active.damage == 0


def test_surfer_holds_until_g_wants_the_loaded_clefairy():
    from app.engine.game import Pokemon

    game = _skill_game("g", "party")
    me = game.players["a"]
    foe = game.players["b"]
    clefs = [i for i, c in enumerate(me.cards) if c.name == "Clefairy"]
    fuels = [i for i, c in enumerate(me.cards) if c.name == "Psychic Energy"]
    surf = next(i for i, c in enumerate(me.cards) if c.name == "Surfer")
    me.active = Pokemon(card_i=clefs[0], played_turn=0)
    me.bench = [Pokemon(card_i=clefs[1], energy=list(fuels[:3]), played_turn=0)]
    me.hand = [surf]
    foe.active = Pokemon(card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Staraptor"), played_turn=0)
    assert game._g_incoming_idx(me, "a") is None
    me.active.ability_used = True
    assert game._g_incoming_idx(me, "a") == 0
    game._resolve_trainer(me, foe, me.card(surf), "a", surf)
    assert me.card(me.active.card_i).name == "Clefairy"
    assert len(me.active.energy) == 3

