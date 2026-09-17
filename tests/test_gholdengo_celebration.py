from random import Random

from app.engine.effects import (
    can_pay_energy,
    energy_provided,
    is_draw_energy,
    is_enriching_energy,
    is_special_energy,
    is_speed_lightning_energy,
    is_voltaic_energy,
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)
from app.engine.game import Game, Pokemon, play_game
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_C60_NAMES, SET_G30_NAMES, build_fallback_deck, build_g30_deck, fallback_named


CELEBRATION_TEXT = (
    "If you have exactly 30 cards in your hand, take 2 Prize cards. "
    "If you do, shuffle your hand into your deck."
)
CRAZY_CODE_TEXT = (
    "As often as you like during your turn (before your attack), you may attach a "
    "Special Energy card from your hand to 1 of your Pokémon."
)
TELEPORTER_TEXT = (
    "Once during your turn, if this Pokémon is in the Active Spot, you may shuffle it "
    "and all attached cards into your deck."
)
BIG_JUMP_TEXT = (
    "Once during your turn (before your attack), you may return this Pokémon "
    "and all cards attached to it to your hand."
)
ENRICHING_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Colorless Energy. "
    "When you attach this card from your hand to a Pokémon, draw 4 cards."
)
SPEED_L_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Lightning Energy. "
    "When you attach this card from your hand to a Lightning Pokémon, draw 2 cards."
)
HAND_FLING_TEXT = "This attack does 20 damage for each card in your hand."
TREASURE_RUSH_TEXT = "This attack does 10 damage for each card in your hand."
PAY_DAY_TEXT = "Draw a card."
DRAW_ENERGY_TEXT = (
    "This card provides Colorless Energy. "
    "When you attach this card from your hand to a Pokémon, draw a card."
)
FLEET_FOOTED_TEXT = (
    "Once during your turn, if this Pokémon is in the Active Spot, you may draw a card."
)
RARE_CANDY_TEXT = (
    "Choose 1 of your Basic Pokémon in play. If you have a Stage 2 card that evolves "
    "from that Pokémon in your hand, put that card onto the Basic Pokémon to evolve it, "
    "skipping the Stage 1. You can't use this card during your first turn or on a Basic "
    "Pokémon that was put into play this turn."
)
PUZZLE_TEXT = (
    "You may play 2 Puzzle of Time cards at once.\n"
    "• If you played 1 card, look at the top 3 cards of your deck and put them back in any order.\n"
    "• If you played 2 cards, put 2 cards from your discard pile into your hand."
)
NET_TEXT = (
    "Put 1 of your Pokémon that isn't a Pokémon V or a Pokémon-GX into your hand. "
    "(Discard all attached cards.)"
)
BTS_TEXT = (
    "Each player may evolve a Pokémon that he or she just played or evolved during that turn."
)
WALLY_TEXT = (
    "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) "
    "and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. "
    "You can use this card during your first turn or on a Pokémon that was put into play this turn."
)
ABYSSAL_TEXT = (
    "Once during your turn (before your attack), you may draw cards until you have 5 cards in your hand."
)
JUNK_HUNT_TEXT = "Put 2 Item cards from your discard pile into your hand."
JUNK_ARM_TEXT = (
    "Discard 2 cards from your hand. Search your discard pile for a Trainer card, show it to your "
    "opponent, and put it in your hand. You can't choose Junk Arm with this effect."
)
MEMORY_HELIX_TEXT = (
    "This Pokémon can use the attacks of any of your Benched Pokémon. "
    "(You still need the necessary Energy to use each attack.)"
)
CELEBRATION_WIND_TEXT = (
    "Once during your turn, when you put Shaymin from your hand onto your Bench, "
    "you may move as many Energy cards attached to your Pokémon as you like to any of your other Pokémon."
)
PENNY_TEXT = "Put 1 of your Basic Pokémon and all attached cards into your hand."
AMP_YOU_VERY_MUCH_TEXT = (
    "If your opponent's Pokémon is Knocked Out by damage from this attack, take 1 more Prize card."
)
FERMENTING_LIQUID_TEXT = (
    "Whenever you attach an Energy card from your hand to Shuckle, draw a card."
)
VOLTAIC_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Lightning Energy. "
    "Attacks used by the Lightning Pokémon this card is attached to do 20 more damage "
    "to your opponent's Active Pokémon (before applying Weakness and Resistance)."
)
SMASH_TURN_TEXT = "You may switch this Pokémon with 1 of your Benched Pokémon."
ELECTROBULLET_TEXT = (
    "This attack also does 30 damage to 1 of your opponent's Benched Pokémon. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)


def _game() -> Game:
    return Game(
        build_g30_deck(),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("celebration"),
        StrategySpec.from_dict("party"),
        Random(1),
    )


def _take(me, name: str, used: set[int]) -> int:
    key = name.lower()
    for i, card in enumerate(me.cards):
        if i in used:
            continue
        if card.name.lower() == key:
            used.add(i)
            return i
    raise AssertionError(f"missing {name}")


def _inject(me, name: str) -> int:
    me.cards.append(fallback_named(name))
    return len(me.cards) - 1


def test_g30_list_is_printed_sixty():
    names = list(SET_G30_NAMES)
    assert len(names) == 60
    assert names.count("Buneary") == 3
    assert names.count("Lopunny") == 2
    assert names.count("Abra") == 0
    assert names.count("Porygon") == 3
    assert names.count("Porygon2") == 2
    assert names.count("Porygon-Z") == 2
    assert names.count("Octillery") == 0
    assert names.count("Remoraid") == 0
    assert names.count("Sableye") == 0
    assert names.count("Aipom") == 0
    assert names.count("Ambipom") == 0
    assert names.count("Galarian Meowth") == 0
    assert names.count("Pikachu") == 0
    assert names.count("Raikou V") == 0
    assert names.count("Iron Hands ex") == 0
    assert names.count("Boltund V") == 4
    assert names.count("Shuckle") == 2
    assert names.count("Shaymin") == 4
    assert names.count("Gholdengo") == 0
    assert names.count("Puzzle of Time") == 4
    assert names.count("Scoop Up Net") == 2
    assert names.count("Nest Ball") == 2
    assert names.count("Ultra Ball") == 1
    assert names.count("VS Seeker") == 1
    assert names.count("Wally") == 1
    assert names.count("Penny") == 2
    assert names.count("Professor's Research") == 0
    assert names.count("Battle Compressor") == 0
    assert names.count("Rare Candy") == 2
    assert names.count("Forest Seal Stone") == 0
    assert names.count("Enriching Energy") == 1
    assert names.count("Speed Lightning Energy") == 4
    assert names.count("Voltaic Lightning Energy") == 4
    assert names.count("Metal Energy") == 0
    assert names.count("Lightning Energy") == 3
    assert names.count("Draw Energy") == 4
    pile = build_g30_deck()
    assert copy_violations(pile, standard_60_rules()) == []
    boltund = [c for c in pile if c.name == "Boltund V"]
    assert len(boltund) == 4
    assert all(c.catalog_id == "swsh8-103" for c in boltund)
    assert all(c.hp == 200 for c in boltund)
    assert all("Lightning" in c.types for c in boltund)
    assert all(c.retreat == 1 for c in boltund)
    assert all(c.attacks[0].name == "Smash Turn" for c in boltund)
    assert all(c.attacks[0].cost == ["Lightning"] for c in boltund)
    assert all(c.attacks[0].damage == 30 for c in boltund)
    assert all(c.attacks[0].text == SMASH_TURN_TEXT for c in boltund)
    assert all(c.attacks[1].name == "Electrobullet" for c in boltund)
    assert all(c.attacks[1].cost == ["Lightning", "Lightning", "Colorless"] for c in boltund)
    assert all(c.attacks[1].damage == 120 for c in boltund)
    assert all(c.attacks[1].text == ELECTROBULLET_TEXT for c in boltund)
    voltaic = [c for c in pile if c.name == "Voltaic Lightning Energy"]
    assert len(voltaic) == 4
    assert all(c.catalog_id == "me5-84" for c in voltaic)
    assert all(c.text == VOLTAIC_TEXT for c in voltaic)
    assert all(is_voltaic_energy(c) for c in voltaic)
    assert all(is_special_energy(c) for c in voltaic)
    assert all(energy_provided(c) == ["Lightning"] for c in voltaic)
    porygon2 = next(c for c in pile if c.name == "Porygon2")
    assert porygon2.evolves_from == "Porygon"
    lopunny = next(c for c in pile if c.name == "Lopunny")
    assert lopunny.catalog_id == "xy2-85"
    assert lopunny.abilities[0].name == "Big Jump"
    assert lopunny.abilities[0].text == BIG_JUMP_TEXT
    buneary = next(c for c in pile if c.name == "Buneary")
    assert buneary.catalog_id == "xy2-84"
    assert buneary.hp == 60
    speed = next(c for c in pile if c.name == "Speed Lightning Energy")
    assert speed.catalog_id == "swsh2-173"
    assert is_speed_lightning_energy(speed)
    assert is_special_energy(speed)
    assert energy_provided(speed) == ["Lightning"]
    draw = next(c for c in pile if c.name == "Draw Energy")
    assert draw.catalog_id == "sm12-209"
    assert is_draw_energy(draw)
    assert is_special_energy(draw)
    assert energy_provided(draw) == ["Colorless"]
    candy = next(c for c in pile if c.name == "Rare Candy")
    assert candy.text == RARE_CANDY_TEXT
    shaymin = next(c for c in pile if c.name == "Shaymin")
    assert shaymin.catalog_id == "hgss2-8"
    assert shaymin.hp == 70
    assert shaymin.abilities[0].name == "Celebration Wind"
    penny = next(c for c in pile if c.name == "Penny")
    assert penny.catalog_id == "sv01-183"
    assert penny.is_supporter
    shuckle = next(c for c in pile if c.name == "Shuckle")
    assert shuckle.catalog_id == "hgssp-HGSS15"
    assert shuckle.hp == 60
    assert "Fighting" in shuckle.types
    assert shuckle.abilities[0].name == "Fermenting Liquid"
    assert shuckle.abilities[0].text == FERMENTING_LIQUID_TEXT


def test_celebration_parses_printed_wording():
    effects = parse_effects(CELEBRATION_TEXT)
    spec = next(e for e in effects if e["kind"] == "take_prizes_if_hand")
    assert spec["hand"] == 30
    assert spec["prizes"] == 2
    assert spec["shuffle_hand"] is True


def test_treasure_rush_parses_printed_wording():
    effects = parse_effects(TREASURE_RUSH_TEXT, "10×")
    spec = next(e for e in effects if e["kind"] == "hand_count_times")
    assert spec["per"] == 10
    assert not any(e["kind"] == "times" for e in effects)
    pay = parse_effects(PAY_DAY_TEXT)
    assert pay[0]["kind"] == "draw"
    assert pay[0]["amount"] == 1


def test_hand_fling_parses_printed_wording():
    effects = parse_effects(HAND_FLING_TEXT, "20×")
    spec = next(e for e in effects if e["kind"] == "hand_count_times")
    assert spec["per"] == 20
    assert not any(e["kind"] == "times" for e in effects)
    collect = parse_effects("Draw 2 cards.")
    assert collect[0]["kind"] == "draw"
    assert collect[0]["amount"] == 2


def test_crazy_code_and_teleporter_and_memory_helix_parse():
    crazy = parse_ability_effects(CRAZY_CODE_TEXT)
    assert crazy[0]["kind"] == "attach_special_energy_from_hand"
    assert crazy[0]["as_often_as_you_like"] is True
    tele = parse_ability_effects(TELEPORTER_TEXT)
    assert tele[0]["kind"] == "shuffle_self_into_deck"
    assert tele[0]["require_active"] is True
    helix = parse_ability_effects(MEMORY_HELIX_TEXT)
    assert helix[0]["kind"] == "copy_benched_attacks"


def test_big_jump_and_leave_it_to_the_wind_parse_printed_wording():
    effects = parse_ability_effects(BIG_JUMP_TEXT)
    assert effects[0]["kind"] == "return_self_to_hand"
    assert effects[0]["once_per_turn"] is True
    lopunny = fallback_named("Lopunny")
    jumpluff = fallback_named("Jumpluff")
    assert lopunny.abilities[0].name == "Big Jump"
    assert lopunny.abilities[0].text == BIG_JUMP_TEXT
    assert jumpluff.abilities[0].name == "Leave It to the Wind"
    assert jumpluff.abilities[0].text == BIG_JUMP_TEXT
    assert parse_ability_effects(lopunny.abilities[0].text) == effects
    assert parse_ability_effects(jumpluff.abilities[0].text) == effects
    serebii = parse_ability_effects(
        "Once during your turn (before you attack), you may return this card "
        "and all cards attached to it to your hand."
    )
    assert serebii[0]["kind"] == "return_self_to_hand"


def test_enriching_and_abyssal_and_bts_parse():
    enrich = parse_energy_effects(ENRICHING_TEXT)
    draw = next(e for e in enrich if e["kind"] == "draw_on_attach_from_hand")
    assert draw["amount"] == 4
    assert "require_attach_type" not in draw
    until = parse_ability_effects(ABYSSAL_TEXT)
    assert until[0]["kind"] == "draw_until_hand"
    assert until[0]["count"] == 5
    bts = parse_ability_effects(BTS_TEXT)
    assert bts[0]["kind"] == "evolve_just_played_or_evolved"


def test_speed_lightning_parses_typed_attach_draw():
    effects = parse_energy_effects(SPEED_L_TEXT)
    draw = next(e for e in effects if e["kind"] == "draw_on_attach_from_hand")
    assert draw["amount"] == 2
    assert draw["require_attach_type"] == "Lightning"
    card = fallback_named("Speed Lightning Energy")
    assert card.text == SPEED_L_TEXT
    assert parse_energy_effects(card.text) == effects


def test_puzzle_net_junk_arm_wally_parse_from_print():
    puzzle = parse_trainer_effects(PUZZLE_TEXT)
    assert puzzle[0]["kind"] == "puzzle_of_time"
    assert puzzle[0]["look"] == 3
    assert puzzle[0]["pair_count"] == 2
    net = parse_trainer_effects(NET_TEXT)
    assert net[0]["kind"] == "scoop_non_v_gx_to_hand"
    junk = parse_trainer_effects(JUNK_ARM_TEXT)
    assert junk[0]["kind"] == "junk_arm"
    assert junk[0]["discard"] == 2
    assert junk[0]["exclude_self"] is True
    wally = parse_trainer_effects(WALLY_TEXT)
    assert wally[0]["kind"] == "wally_evolve"
    assert wally[0]["first_turn_ok"] is True
    hunt = parse_effects(JUNK_HUNT_TEXT)
    rec = next(e for e in hunt if e["kind"] == "recycle_items_from_discard")
    assert rec["count"] == 2


def test_celebration_wind_and_penny_parse_printed_wording():
    wind = parse_ability_effects(CELEBRATION_WIND_TEXT)
    assert wind[0]["kind"] == "move_any_energy_when_benched_from_hand"
    shaymin = fallback_named("Shaymin")
    assert shaymin.catalog_id == "hgss2-8"
    assert shaymin.abilities[0].name == "Celebration Wind"
    assert shaymin.abilities[0].text == CELEBRATION_WIND_TEXT
    assert parse_ability_effects(shaymin.abilities[0].text) == wind
    penny = parse_trainer_effects(PENNY_TEXT)
    assert penny[0]["kind"] == "return_one_basic_and_attached_to_hand"
    card = fallback_named("Penny")
    assert card.text == PENNY_TEXT
    assert parse_trainer_effects(card.text) == penny


def test_fallback_prints_use_lab_wording():
    assert fallback_named("Ambipom").attacks[-1].text == HAND_FLING_TEXT
    assert fallback_named("galarian meowth 30th").attacks[-1].text == TREASURE_RUSH_TEXT
    assert fallback_named("galarian meowth 30th").attacks[-1].cost == ["Metal"]
    assert fallback_named("galarian meowth 30th").attacks[0].text == PAY_DAY_TEXT
    rush = fallback_named("galarian meowth 30th").attacks[-1]
    assert not can_pay_energy(["Colorless", "Colorless"], rush.cost)
    assert can_pay_energy(["Metal"], rush.cost)
    assert fallback_named("aipom par").attacks[0].name == "Filch"
    assert next(a.text for a in fallback_named("Porygon-Z").abilities) == CRAZY_CODE_TEXT
    assert fallback_named("Puzzle of Time").text == PUZZLE_TEXT
    assert fallback_named("Scoop Up Net").text == NET_TEXT
    assert fallback_named("Enriching Energy").text == ENRICHING_TEXT
    assert fallback_named("Speed Lightning Energy").text == SPEED_L_TEXT
    assert fallback_named("Draw Energy").text == DRAW_ENERGY_TEXT
    assert fallback_named("Broken Time-Space").text == BTS_TEXT
    assert fallback_named("Lopunny").abilities[0].text == BIG_JUMP_TEXT
    assert fallback_named("Jumpluff").abilities[0].text == BIG_JUMP_TEXT
    assert fallback_named("Shaymin").abilities[0].text == CELEBRATION_WIND_TEXT
    assert fallback_named("Penny").text == PENNY_TEXT
    assert fallback_named("Shuckle").abilities[0].text == FERMENTING_LIQUID_TEXT
    assert fallback_named("Shuckle").catalog_id == "hgssp-HGSS15"
    assert fallback_named("Boltund V").catalog_id == "swsh8-103"
    assert fallback_named("Boltund V").attacks[1].text == ELECTROBULLET_TEXT
    assert fallback_named("Voltaic Lightning Energy").text == VOLTAIC_TEXT
    assert fallback_named("voltaic").text == VOLTAIC_TEXT


def test_voltaic_parses_energy_damage_bonus():
    effects = parse_energy_effects(VOLTAIC_TEXT)
    bonus = next(e for e in effects if e["kind"] == "energy_damage_bonus")
    assert bonus["amount"] == 20
    assert bonus["require_pokemon_type"] == "Lightning"
    card = fallback_named("Voltaic Lightning Energy")
    assert card.text == VOLTAIC_TEXT
    assert parse_energy_effects(card.text) == effects


def test_electrobullet_parses_bench_snipe():
    effects = parse_effects(ELECTROBULLET_TEXT, "120")
    snipe = next(e for e in effects if e["kind"] == "bench_damage_counters")
    assert snipe["counters"] == 3
    switch = parse_effects(SMASH_TURN_TEXT, "30")
    assert any(e["kind"] == "switch_with_benched" for e in switch)


def test_speed_l_draws_only_on_lightning():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    hands = _take(me, "Boltund V", used)
    ambipom = _take(me, "Porygon", used)
    speed = _take(me, "Speed Lightning Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=hands, played_turn=0)
    me.bench = [Pokemon(card_i=ambipom, played_turn=0)]
    me.hand = []
    me.deck = rest
    before = len(me.hand)
    game._resolve_energy_attach_from_hand(me, "a", me.active, speed)
    assert len(me.hand) == before + 2
    assert game.events.get("speed_l_draw") == 2

    game2 = _game()
    me2 = game2.players["a"]
    used2: set[int] = set()
    hands2 = _take(me2, "Boltund V", used2)
    meowth2 = _take(me2, "Porygon", used2)
    speed2 = _take(me2, "Speed Lightning Energy", used2)
    rest2 = [i for i in range(len(me2.cards)) if i not in used2]
    me2.active = Pokemon(card_i=meowth2, played_turn=0)
    me2.bench = [Pokemon(card_i=hands2, played_turn=0)]
    me2.hand = []
    me2.deck = rest2
    game2._resolve_energy_attach_from_hand(me2, "a", me2.active, speed2)
    assert me2.hand == []
    assert not game2.events.get("speed_l_draw")


def test_hand_fling_scales_with_hand_size():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    meowth = _inject(me, "galarian meowth 30th")
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=meowth, played_turn=0)
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    rest = [i for i in range(len(me.cards)) if i != meowth]
    me.hand = rest[:23]
    atk = next(a for a in me.card(meowth).attacks if a.name == "Treasure Rush")
    assert game._raw_attack_damage(me, foe, me.active, atk) == 10 * 23
    me.hand = rest[:32]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 10 * 32


def test_electrobullet_beats_smash_turn_when_lethal():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    draw = _take(me, "Draw Energy", used)
    clefairy = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, draw])
    foe.active = Pokemon(card_i=clefairy, played_turn=0)
    me.hand = []
    atk = game._choose_attack(me, foe, game.strats["a"])
    assert atk is not None
    assert atk.name == "Electrobullet"

    game2 = _game()
    me2 = game2.players["a"]
    foe2 = game2.players["b"]
    used2: set[int] = set()
    boltund2 = _take(me2, "Boltund V", used2)
    light2 = _take(me2, "Lightning Energy", used2)
    clefairy2 = next(i for i, c in enumerate(foe2.cards) if c.name == "Clefairy")
    me2.active = Pokemon(card_i=boltund2, played_turn=0, energy=[light2])
    foe2.active = Pokemon(card_i=clefairy2, played_turn=0, damage=30)
    me2.hand = []
    atk2 = game2._choose_attack(me2, foe2, game2.strats["a"])
    assert atk2 is not None
    assert atk2.name == "Smash Turn"


def test_voltaic_bonus_adds_twenty_per_copy_on_lightning():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    draw = _take(me, "Draw Energy", used)
    voltaics = [_take(me, "Voltaic Lightning Energy", used) for _ in range(4)]
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, draw])
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    atk = next(a for a in me.card(boltund).attacks if a.name == "Electrobullet")
    assert game._raw_attack_damage(me, foe, me.active, atk) == 120
    me.active.energy.extend(voltaics[:2])
    assert game._raw_attack_damage(me, foe, me.active, atk) == 160
    me.active.energy.extend(voltaics[2:])
    assert game._raw_attack_damage(me, foe, me.active, atk) == 200


def test_voltaic_bonus_skips_non_lightning_host():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    shuckle = _take(me, "Shuckle", used)
    voltaic = _take(me, "Voltaic Lightning Energy", used)
    me.active = Pokemon(card_i=shuckle, played_turn=0, energy=[voltaic])
    assert game._energy_damage_bonus(me, me.active) == 0


def test_celebration_attaches_lightning_to_pay_electrobullet():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    light = _take(me, "Lightning Energy", used)
    draw = _take(me, "Draw Energy", used)
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.hand = [light, draw]
    game._attach_energy(me, "a")
    assert light in me.active.energy
    assert draw in me.hand
    assert game._boltund_unpaid(me, me.active)


def test_draw_energy_pays_only_colorless_part_of_electrobullet():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    draw = _take(me, "Draw Energy", used)
    lights = [_take(me, "Lightning Energy", used) for _ in range(2)]
    me.active = Pokemon(card_i=boltund, played_turn=0, energy=[draw])
    assert game._boltund_unpaid(me, me.active)
    me.active.energy.extend(lights)
    assert not game._boltund_unpaid(me, me.active)


def test_celebration_skips_draw_attach_until_lightning_pays_boltund():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    draw = _take(me, "Draw Energy", used)
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.hand = [draw]
    game._attach_energy(me, "a")
    assert draw in me.hand
    assert me.active.energy == []
    assert not me.energy_attached


def test_engine_grows_hand_and_pays_electrobullet():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    poryz = _take(me, "Porygon-Z", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    enrich = _take(me, "Enriching Energy", used)
    draws = [_take(me, "Draw Energy", used) for _ in range(4)]
    bts = _take(me, "Broken Time-Space", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(4)]
    voltaics = [_take(me, "Voltaic Lightning Energy", used) for _ in range(2)]
    clefairy = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=boltund, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.prizes = rest[:6]
    rest = rest[6:]
    me.hand = [enrich, *speeds, *draws, *voltaics]
    me.deck = rest
    me.discard = []
    foe.active = Pokemon(card_i=clefairy, played_turn=0)
    game.turn = 2
    game._set_stadium(me.card(bts))
    start = len(me.hand)
    game._celebration_engine(me, "a")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    assert any(is_speed_lightning_energy(me.card(i)) for i in attacker.energy)
    assert game.events.get("speed_l_draw")
    assert game.events.get("draw_energy_draw")
    assert game.events.get("big_jump") or game.events.get("return_self_to_hand") or game._celebration_closer_ready(me, foe)
    assert not game._boltund_unpaid(me, attacker)
    assert len(me.hand) > start
    assert game._celebration_closer_ready(me, foe)
    game._celebration_align_attacker(me, "a")
    assert me.card(me.active.card_i).name == "Boltund V"
    game._attack(me, foe, "a")
    assert game.events.get("attack:Boltund V:Electrobullet")
    assert foe.active is None or foe.active.damage >= foe.card(clefairy).hp


def test_evolve_keeps_buneary_under_lopunny_and_big_jump_returns_stack():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    raikou = _take(me, "Boltund V", used)
    enrich = _take(me, "Enriching Energy", used)
    bts = _take(me, "Broken Time-Space", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=buneary, played_turn=2)
    me.bench = [Pokemon(card_i=raikou, played_turn=0)]
    me.hand = [lopunny, enrich]
    me.deck = rest
    me.discard = []
    game.turn = 2
    game._set_stadium(me.card(bts))
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Lopunny"
    assert me.active.underneath == [buneary]
    assert buneary not in me.discard
    me.active.energy.append(enrich)
    me.hand.remove(enrich)
    assert game._return_mon_to_hand(me, me.active, event="big_jump")
    names = [me.card(i).name for i in me.hand]
    assert names.count("Lopunny") == 1
    assert names.count("Buneary") == 1
    assert names.count("Enriching Energy") == 1
    assert me.card(me.active.card_i).name == "Boltund V"


def test_bts_allows_same_turn_buneary_line():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=buneary, played_turn=2)
    me.bench = []
    me.hand = [lopunny]
    me.deck = []
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert game._stadium_allows_immediate_evolve()
    assert game._can_evolve_now(me, "a", me.active)
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Lopunny"


def test_scoop_net_skips_speed_l_host():
    game = _game()
    boltund = fallback_named("Boltund V")
    hands = fallback_named("Iron Hands ex")
    ambipom = fallback_named("Ambipom")
    abra = fallback_named("Abra")
    assert not game._scoop_legal(boltund)
    assert game._scoop_legal(hands)
    assert game._scoop_legal(ambipom)
    assert game._scoop_legal(abra)
    assert "boltund v" in game._celebration_keep_names()
    assert "shuckle" in game._celebration_keep_names()
    assert game._scoop_legal(fallback_named("Shuckle"))


def test_g30_vs_c60_completes():
    result = play_game(
        build_g30_deck(),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("celebration"),
        StrategySpec.from_dict("party"),
        Random(11),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1


def test_celebration_does_not_hold_basics_as_energy():
    spec = StrategySpec.from_dict("celebration")
    assert spec.hold_as_energy is False
    assert spec.search_aces[0] == "Buneary"


def test_celebration_starter_prefers_porygon_then_buneary():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    buneary = _take(me, "Buneary", used)
    boltund = _take(me, "Boltund V", used)
    strat = game.strats["a"]
    pick = game._pick_starter(me, [boltund, buneary, porygon], strat)
    assert me.card(pick).name == "Porygon"
    pick = game._pick_starter(me, [boltund, buneary], strat)
    assert me.card(pick).name == "Buneary"


def test_celebration_benches_buneary_before_boltund_on_last_slot():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    extra_porygon = _take(me, "Porygon", used)
    boltund = _take(me, "Boltund V", used)
    shaymin = _take(me, "Shaymin", used)
    lopunny = _take(me, "Lopunny", used)
    spare_boltund = _take(me, "Boltund V", used)
    buneary = _take(me, "Buneary", used)
    me.active = Pokemon(card_i=porygon, played_turn=0)
    me.bench = [
        Pokemon(card_i=extra_porygon, played_turn=0),
        Pokemon(card_i=boltund, played_turn=0),
        Pokemon(card_i=shaymin, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0),
    ]
    me.hand = [spare_boltund, buneary]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert "Buneary" in names
    assert names.count("Boltund V") == 1
    assert any(me.card(i).name == "Boltund V" for i in me.hand)


def test_celebration_poffin_benches_buneary_ahead_of_porygon():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    buneary = _take(me, "Buneary", used)
    porygon = _take(me, "Porygon", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [porygon, buneary, *rest]
    game.turn = 1
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "buneary"
    game._bench_basic_from_deck(me, "a", count=1, max_hp=70, source="poffin")
    assert me.bench
    assert me.card(me.bench[0].card_i).name == "Buneary"


def test_celebration_loop_gate_sees_enriching_on_lopunny():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    lopunny = _take(me, "Lopunny", used)
    buneary = _take(me, "Buneary", used)
    enrich = _take(me, "Enriching Energy", used)
    extra_porygon = _take(me, "Porygon", used)
    ambipom = _take(me, "Boltund V", used)
    puzzles = [_take(me, "Puzzle of Time", used) for _ in range(2)]
    net = _take(me, "Scoop Up Net", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary], energy=[enrich]),
        Pokemon(card_i=extra_porygon, played_turn=0),
        Pokemon(card_i=ambipom, played_turn=0),
    ]
    me.hand = []
    me.discard = [*puzzles, net]
    assert game._celebration_can_loop(me)
    assert not game._celebration_needs_loop_items(me)
    assert not game._celebration_needs_junk_hunt(me)
    assert game._celebration_combo_ready(me)


def test_celebration_wally_helps_buneary_into_lopunny():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    porygon = _take(me, "Porygon", used)
    me.active = Pokemon(card_i=porygon, played_turn=0)
    me.bench = [Pokemon(card_i=buneary, played_turn=0)]
    me.hand = []
    me.deck = [lopunny]
    assert game._celebration_wally_helps(me)
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "lopunny"


def test_celebration_searches_second_boltund_while_one_in_play():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    boltund = _take(me, "Boltund V", used)
    boltund2 = _take(me, "Boltund V", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.bench = [
        Pokemon(card_i=poryz, played_turn=0, underneath=[porygon]),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = []
    me.deck = [boltund2]
    assert game._celebration_needs_closer(me)
    assert not game._celebration_wally_helps(me)
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "boltund v"


def test_celebration_hunts_backup_boltund_after_first_closer():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    poryz = _take(me, "Porygon-Z", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    boltund2 = _take(me, "Boltund V", used)
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.bench = [
        Pokemon(card_i=poryz, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = []
    me.deck = [boltund2]
    in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
    in_hand = {me.card(i).name.lower() for i in me.hand}
    assert "boltund v" in game._celebration_missing_hunt(me, in_play, in_hand)
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "boltund v"


def test_celebration_benches_replacement_boltund_after_first():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    boltund2 = _take(me, "Boltund V", used)
    poryz = _take(me, "Porygon-Z", used)
    me.active = Pokemon(card_i=boltund, played_turn=0)
    me.bench = [Pokemon(card_i=poryz, played_turn=0)]
    me.hand = [boltund2]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert names.count("Boltund V") == 1
    assert any(me.card(i).name == "Boltund V" for i in me.hand)


def test_celebration_big_jump_when_electrobullet_not_ready():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    poryz = _take(me, "Porygon-Z", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    enrich = _take(me, "Enriching Energy", used)
    draw = _take(me, "Draw Energy", used)
    bts = _take(me, "Broken Time-Space", used)
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=boltund, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = [enrich, draw]
    me.deck = rest
    me.discard = []
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert not game._celebration_closer_ready(me, foe)
    game._celebration_engine(me, "a")
    assert game.events.get("big_jump") or game.events.get("return_self_to_hand")
    assert any(is_enriching_energy(me.card(i)) for i in me.hand) or game._enriching_on_bounce_host(me)


def test_draw_energy_parses_draw_a_card():
    effects = parse_energy_effects(DRAW_ENERGY_TEXT)
    draw = next(e for e in effects if e["kind"] == "draw_on_attach_from_hand")
    assert draw["amount"] == 1
    assert "require_attach_type" not in draw
    card = fallback_named("Draw Energy")
    assert card.text == DRAW_ENERGY_TEXT
    assert parse_energy_effects(card.text) == effects


def test_draw_energy_attach_draws_one():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    ambipom = _take(me, "Boltund V", used)
    draw = _take(me, "Draw Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.hand = []
    me.deck = rest
    before = len(me.hand)
    game._resolve_energy_attach_from_hand(me, "a", me.active, draw)
    assert len(me.hand) == before + 1
    assert game.events.get("draw_energy_draw") == 1


def test_fleet_footed_parses_active_draw():
    effects = parse_ability_effects(FLEET_FOOTED_TEXT)
    assert effects[0]["kind"] == "draw"
    assert effects[0]["amount"] == 1
    assert effects[0]["require_active"] is True
    raikou = fallback_named("Raikou V")
    assert parse_ability_effects(raikou.abilities[0].text) == effects


def test_fleet_footed_draws_only_when_active():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    ambipom = _take(me, "Boltund V", used)
    raikou = _inject(me, "Raikou V")
    rest = [i for i in range(len(me.cards)) if i not in used and i != raikou]
    me.active = Pokemon(card_i=raikou, played_turn=0)
    me.bench = [Pokemon(card_i=ambipom, played_turn=0)]
    me.hand = []
    me.deck = rest
    game._use_passive_abilities(me, "a")
    assert game.events.get("fleet_footed") == 1
    assert me.active.ability_used is True

    game2 = _game()
    me2 = game2.players["a"]
    used2: set[int] = set()
    meowth2 = _take(me2, "Boltund V", used2)
    raikou2 = _inject(me2, "Raikou V")
    rest2 = [i for i in range(len(me2.cards)) if i not in used2 and i != raikou2]
    me2.active = Pokemon(card_i=meowth2, played_turn=0)
    me2.bench = [Pokemon(card_i=raikou2, played_turn=0)]
    me2.hand = []
    me2.deck = rest2
    game2._use_passive_abilities(me2, "a")
    assert not game2.events.get("fleet_footed")


def test_forest_seal_on_raikou_searches_any_card():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    ambipom = _take(me, "Boltund V", used)
    candy = _take(me, "Rare Candy", used)
    raikou = _inject(me, "Raikou V")
    stone = _inject(me, "Forest Seal Stone")
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.bench = [Pokemon(card_i=raikou, played_turn=0, tool=stone)]
    me.hand = []
    me.deck = [candy]
    game._use_passive_abilities(me, "a")
    assert game.events.get("star_alchemy") == 1
    assert candy in me.hand
    assert me.vstar_used is True


def test_rare_candy_skips_porygon_to_z():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    candy = _take(me, "Rare Candy", used)
    me.active = Pokemon(card_i=porygon, played_turn=0)
    me.bench = []
    me.hand = [poryz, candy]
    me.deck = []
    game.turn = 3
    game.first = "b"
    assert game._same_line(me.card(porygon), me.card(poryz))
    assert game._can_evolve_now(me, "a", me.active, me.card(poryz))
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Porygon-Z"
    assert porygon in me.active.underneath
    assert candy in me.discard
    assert game.events.get("rare_candy") == 1


def test_bts_evolves_porygon_to_porygon2_to_z_same_turn():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    porygon2 = _take(me, "Porygon2", used)
    poryz = _take(me, "Porygon-Z", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=porygon, played_turn=2)
    me.bench = []
    me.hand = [porygon2, poryz]
    me.deck = []
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert game._stadium_allows_immediate_evolve()
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Porygon-Z"
    assert porygon in me.active.underneath
    assert porygon2 in me.active.underneath


def test_same_line_does_not_guess_by_shared_type():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    assert game._same_line(me.card(porygon), me.card(poryz))
    assert game._same_line(fallback_named("Tinkatink"), fallback_named("Tinkaton"))
    assert not game._same_line(fallback_named("Clefairy"), fallback_named("Tinkaton"))
    assert not game._same_line(fallback_named("Tinkatink"), fallback_named("Porygon-Z"))


def test_rare_candy_blocked_same_turn_even_with_bts():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    candy = _take(me, "Rare Candy", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=porygon, played_turn=3)
    me.hand = [poryz, candy]
    game.turn = 3
    game.first = "b"
    game._set_stadium(me.card(bts))
    assert game._stadium_allows_immediate_evolve()
    assert not game._can_evolve_now(me, "a", me.active, me.card(poryz))
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Porygon"
    assert candy in me.hand


def test_evolve_g_does_not_candy_same_turn_basic_with_bts():
    game = Game(
        build_g30_deck(),
        build_fallback_deck(list(SET_C60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("g"),
        StrategySpec.from_dict("party"),
        Random(1),
    )
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    candy = _take(me, "Rare Candy", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=porygon, played_turn=3)
    me.hand = [poryz, candy]
    game.turn = 3
    game.first = "b"
    game.strats["a"].evolve_asap = 1.0
    game._set_stadium(me.card(bts))
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Porygon"
    assert candy in me.hand


def test_celebration_wind_moves_speed_l_and_keeps_voltaic_on_boltund():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    boltund = _take(me, "Boltund V", used)
    voltaic = _take(me, "Voltaic Lightning Energy", used)
    light = _take(me, "Lightning Energy", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    shaymin = _take(me, "Shaymin", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=boltund, played_turn=0, energy=[voltaic, light, *speeds]),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = [shaymin]
    me.deck = rest
    before_draw = game.events.get("speed_l_draw", 0)
    assert game._celebration_play_shaymin(me, "a")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    bounce = next(m for m in me.in_play() if me.card(m.card_i).name == "Lopunny")
    assert voltaic in attacker.energy
    assert light in attacker.energy
    assert all(i in bounce.energy for i in speeds)
    assert all(i not in attacker.energy for i in speeds)
    assert game.events.get("celebration_wind") == 2
    assert game.events.get("speed_l_draw", 0) == before_draw


def test_celebration_wind_does_not_fire_when_benched_from_deck():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    raikou = _take(me, "Boltund V", used)
    lopunny = _take(me, "Lopunny", used)
    buneary = _take(me, "Buneary", used)
    shaymin = _take(me, "Shaymin", used)
    speed = _take(me, "Speed Lightning Energy", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
        Pokemon(card_i=raikou, played_turn=0, energy=[speed]),
        Pokemon(card_i=shaymin, played_turn=0),
    ]
    me.hand = []
    game._on_benched(me, me.bench[-1], from_hand=False)
    assert speed in me.bench[1].energy
    assert not game.events.get("celebration_wind")
    game._on_benched(me, me.bench[-1], from_hand=True)
    bounce = next(m for m in me.in_play() if me.card(m.card_i).name == "Lopunny")
    assert speed in bounce.energy
    assert game.events.get("celebration_wind") == 1


def test_penny_returns_shaymin_with_attachments():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shaymin = _take(me, "Shaymin", used)
    draw = _take(me, "Draw Energy", used)
    penny = _take(me, "Penny", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=shaymin, played_turn=0, energy=[draw])]
    me.hand = [penny]
    assert game._play_named_supporter(me, game.players["b"], "a", "Penny")
    names = [me.card(i).name for i in me.hand]
    assert names.count("Shaymin") == 1
    assert names.count("Draw Energy") == 1
    assert game.events.get("penny") == 1
    assert all(me.card(m.card_i).name != "Shaymin" for m in me.in_play())


def test_shaymin_net_replay_recycles_speed_l_to_thirty():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    boltund = _take(me, "Boltund V", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    shaymin = _take(me, "Shaymin", used)
    enrich = _take(me, "Enriching Energy", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(4)]
    draws = [_take(me, "Draw Energy", used) for _ in range(4)]
    nets = [_take(me, "Scoop Up Net", used) for _ in range(2)]
    penny = _take(me, "Penny", used)
    bts = _take(me, "Broken Time-Space", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=boltund, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = [shaymin, enrich, *speeds, *draws, *nets, penny]
    me.deck = rest
    me.discard = []
    me.prizes = []
    foe.active = Pokemon(
        card_i=next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex"),
        played_turn=0,
    )
    game.turn = 2
    game._set_stadium(me.card(bts))
    start = len(me.hand)
    game._celebration_engine(me, "a")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    assert game.events.get("celebration_wind")
    assert game.events.get("big_jump") or game.events.get("return_self_to_hand")
    assert game.events.get("scoop_net") or game.events.get("penny")
    assert game.events.get("speed_l_draw", 0) >= 8
    assert not game._boltund_unpaid(me, attacker)
    assert len(me.hand) >= 30
    assert len(me.hand) > start


def test_amp_you_very_much_parses_printed_extra_prize():
    effects = parse_effects(AMP_YOU_VERY_MUCH_TEXT)
    spec = next(e for e in effects if e["kind"] == "extra_prize_on_ko")
    assert spec["count"] == 1
    card = fallback_named("Iron Hands ex")
    assert card.attacks[1].text == AMP_YOU_VERY_MUCH_TEXT
    assert parse_effects(card.attacks[1].text) == effects


def test_amp_you_very_much_takes_two_prizes_on_clefairy():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    hands = _inject(me, "Iron Hands ex")
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(4)]
    clefairy = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    spare = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=hands, played_turn=0, energy=list(speeds))
    me.hand = []
    foe.active = Pokemon(card_i=clefairy, played_turn=0)
    foe.bench = [Pokemon(card_i=spare, played_turn=0)]
    atk = game._choose_attack(me, foe, game.strats["a"])
    assert atk is not None
    assert atk.name == "Amp You Very Much"
    before = me.prizes_taken
    leftover = len(me.prizes)
    game._attack(me, foe, "a")
    game._check_ko(foe, me, "b", extra_prizes=game._pending_attack_extra_prizes)
    assert me.prizes_taken - before == 2
    assert leftover - len(me.prizes) == 2
    assert game.events.get("extra_prize_on_ko") == 1


def test_paid_boltund_moves_in_over_unpaid_bench():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    draw = _take(me, "Draw Energy", used)
    switch = _take(me, "Switch", used)
    clefairy = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    spare = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, draw])]
    me.hand = [switch]
    foe.active = Pokemon(card_i=clefairy, played_turn=0)
    foe.bench = [Pokemon(card_i=spare, played_turn=0)]
    assert game._mon_best_ko_prizes(me, foe, me.active) == 0
    assert game._mon_best_ko_prizes(me, foe, me.bench[0]) == 1
    game._celebration_align_attacker(me, "a")
    assert me.card(me.active.card_i).name == "Boltund V"
    atk = game._choose_attack(me, foe, game.strats["a"])
    assert atk is not None
    assert atk.name == "Electrobullet"


def test_electrobullet_snipes_bench_for_thirty():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    draw = _take(me, "Draw Energy", used)
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    spare = next(i for i, c in enumerate(foe.cards) if c.name == "Clefairy")
    me.active = Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, draw])
    me.hand = []
    foe.active = Pokemon(card_i=mewtwo, played_turn=0, damage=110)
    foe.bench = [Pokemon(card_i=spare, played_turn=0)]
    atk = game._choose_attack(me, foe, game.strats["a"])
    assert atk is not None
    assert atk.name == "Electrobullet"
    game._attack(me, foe, "a")
    assert foe.active.damage == 230
    assert foe.bench[0].damage == 30
    assert game.events.get("bench_damage") == 30


def test_fermenting_liquid_parses_printed_wording():
    effects = parse_ability_effects(FERMENTING_LIQUID_TEXT)
    spec = next(e for e in effects if e["kind"] == "draw_on_energy_attach_from_hand")
    assert spec["amount"] == 1
    card = fallback_named("Shuckle")
    assert card.abilities[0].name == "Fermenting Liquid"
    assert card.abilities[0].text == FERMENTING_LIQUID_TEXT
    assert parse_ability_effects(card.abilities[0].text) == effects


def test_draw_energy_on_shuckle_draws_two():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    shuckle = _take(me, "Shuckle", used)
    meowth = _take(me, "Boltund V", used)
    draw = _take(me, "Draw Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=meowth, played_turn=0)
    me.bench = [Pokemon(card_i=shuckle, played_turn=0)]
    me.hand = []
    me.deck = rest
    before = len(me.hand)
    game._resolve_energy_attach_from_hand(me, "a", me.bench[0], draw)
    assert len(me.hand) == before + 2
    assert game.events.get("draw_energy_draw") == 1
    assert game.events.get("fermenting_liquid") == 1


def test_draw_energy_on_boltund_skips_fermenting():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    meowth = _take(me, "Boltund V", used)
    draw = _take(me, "Draw Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=meowth, played_turn=0)
    me.hand = []
    me.deck = rest
    before = len(me.hand)
    game._resolve_energy_attach_from_hand(me, "a", me.active, draw)
    assert len(me.hand) == before + 1
    assert game.events.get("draw_energy_draw") == 1
    assert not game.events.get("fermenting_liquid")


def test_speed_l_on_shuckle_is_fermenting_only():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    shuckle = _take(me, "Shuckle", used)
    speed = _take(me, "Speed Lightning Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=shuckle, played_turn=0)
    me.hand = []
    me.deck = rest
    before = len(me.hand)
    game._resolve_energy_attach_from_hand(me, "a", me.active, speed)
    assert len(me.hand) == before + 1
    assert not game.events.get("speed_l_draw")
    assert game.events.get("fermenting_liquid") == 1


def test_celebration_wind_does_not_retrigger_fermenting():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shuckle = _take(me, "Shuckle", used)
    lopunny = _take(me, "Lopunny", used)
    buneary = _take(me, "Buneary", used)
    shaymin = _take(me, "Shaymin", used)
    draw = _take(me, "Draw Energy", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
        Pokemon(card_i=shuckle, played_turn=0, energy=[draw]),
    ]
    me.hand = [shaymin]
    before = game.events.get("fermenting_liquid", 0)
    assert game._celebration_play_shaymin(me, "a")
    bounce = next(m for m in me.in_play() if me.card(m.card_i).name == "Lopunny")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Shuckle")
    assert draw in bounce.energy
    assert host.energy == []
    assert game.events.get("celebration_wind") == 1
    assert game.events.get("fermenting_liquid", 0) == before


def test_crazy_code_parks_draw_energy_on_shuckle():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shuckle = _take(me, "Shuckle", used)
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    enrich = _take(me, "Enriching Energy", used)
    draws = [_take(me, "Draw Energy", used) for _ in range(4)]
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=shuckle, played_turn=0),
        Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, enrich]),
    ]
    me.hand = list(draws)
    me.deck = rest
    for _ in range(4):
        assert game._celebration_attach_draw_energy(me, "a")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Shuckle")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    assert len(host.energy) == 4
    assert all(is_draw_energy(me.card(i)) for i in host.energy)
    assert attacker.energy == [*speeds, enrich]
    assert game.events.get("draw_energy_draw") == 4
    assert game.events.get("fermenting_liquid") == 4
    assert game.events.get("crazy_code") == 4


def test_crazy_code_parks_voltaic_on_boltund():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shuckle = _take(me, "Shuckle", used)
    boltund = _take(me, "Boltund V", used)
    voltaics = [_take(me, "Voltaic Lightning Energy", used) for _ in range(4)]
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=shuckle, played_turn=0),
        Pokemon(card_i=boltund, played_turn=0),
    ]
    me.hand = list(voltaics)
    me.deck = rest
    for _ in range(4):
        assert game._celebration_attach_voltaic(me, "a")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Shuckle")
    assert len(attacker.energy) == 4
    assert all(is_voltaic_energy(me.card(i)) for i in attacker.energy)
    assert host.energy == []
    assert game.events.get("crazy_code") == 4
    assert not game.events.get("fermenting_liquid")


def test_enriching_on_shuckle_when_wind_ready():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shuckle = _take(me, "Shuckle", used)
    lopunny = _take(me, "Lopunny", used)
    buneary = _take(me, "Buneary", used)
    shaymin = _take(me, "Shaymin", used)
    enrich = _take(me, "Enriching Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=shuckle, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = [enrich, shaymin]
    me.deck = rest
    assert game._celebration_can_wind(me)
    assert game._celebration_attach_enriching(me, "a")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Shuckle")
    bounce = next(m for m in me.in_play() if me.card(m.card_i).name == "Lopunny")
    assert enrich in host.energy
    assert enrich not in bounce.energy
    assert game.events.get("enriching_draw") == 4
    assert game.events.get("fermenting_liquid") == 1


def test_play_shaymin_skips_when_one_already_in_play():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    first = _take(me, "Shaymin", used)
    second = _take(me, "Shaymin", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=first, played_turn=0)]
    me.hand = [second]
    assert not game._celebration_play_shaymin(me, "a")
    assert me.hand == [second]
    assert sum(1 for m in me.in_play() if me.card(m.card_i).name == "Shaymin") == 1


def test_opening_holds_shuckle_off_the_bench():
    for seed in range(80):
        game = Game(
            build_g30_deck(),
            build_fallback_deck(list(SET_C60_NAMES)),
            standard_60_rules(),
            StrategySpec.from_dict("celebration"),
            StrategySpec.from_dict("party"),
            Random(seed),
        )
        me = game.players["a"]
        assert "Shuckle" not in [me.card(m.card_i).name for m in me.bench]


def test_shuckle_stays_in_hand_until_attach_ready():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    meowth = _take(me, "Boltund V", used)
    shuckle = _take(me, "Shuckle", used)
    strat = game.strats["a"]
    me.active = Pokemon(card_i=meowth, played_turn=0)
    me.hand = [shuckle]
    assert not game._celebration_shuckle_ready(me)
    assert not game._wants_in_play(me, me.card(shuckle), strat)
    assert not game._celebration_play_shuckle(me, "a")
    assert me.hand == [shuckle]
    poryz = _take(me, "Porygon-Z", used)
    draw = _take(me, "Draw Energy", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=meowth, played_turn=0)]
    me.hand = [shuckle, draw]
    assert game._has_crazy_code(me)
    assert game._celebration_shuckle_ready(me)
    assert game._wants_in_play(me, me.card(shuckle), strat)
    assert game._celebration_play_shuckle(me, "a")
    assert shuckle not in me.hand
    assert any(me.card(m.card_i).name == "Shuckle" for m in me.in_play())


def test_can_wind_false_when_penny_already_spent():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shaymin = _take(me, "Shaymin", used)
    penny = _take(me, "Penny", used)
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=shaymin, played_turn=0)]
    me.hand = [penny]
    me.supporter_used = True
    assert not game._celebration_can_wind(me)
    extra = _take(me, "Shaymin", used)
    me.hand = [penny, extra]
    assert not game._celebration_can_wind(me)
    me.supporter_used = False
    assert game._celebration_can_wind(me)


def test_engine_benches_shuckle_before_draw_energy():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    poryz = _take(me, "Porygon-Z", used)
    shuckle = _take(me, "Shuckle", used)
    boltund = _take(me, "Boltund V", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(2)]
    enrich = _take(me, "Enriching Energy", used)
    draws = [_take(me, "Draw Energy", used) for _ in range(4)]
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [Pokemon(card_i=boltund, played_turn=0, energy=[*speeds, enrich])]
    me.hand = [shuckle, *draws]
    me.deck = rest
    game._celebration_engine(me, "a")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Shuckle")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Boltund V")
    assert len(host.energy) == 4
    assert all(is_draw_energy(me.card(i)) for i in host.energy)
    assert set([*speeds, enrich]) <= set(attacker.energy)
    assert game.events.get("draw_energy_draw") == 4
    assert game.events.get("fermenting_liquid") == 4
    assert game.events.get("crazy_code", 0) >= 4


