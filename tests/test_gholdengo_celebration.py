from random import Random

from app.engine.effects import (
    energy_provided,
    is_draw_energy,
    is_enriching_energy,
    is_special_energy,
    is_speed_lightning_energy,
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


def test_g30_list_is_printed_sixty():
    names = list(SET_G30_NAMES)
    assert len(names) == 60
    assert names.count("Buneary") == 3
    assert names.count("Lopunny") == 2
    assert names.count("Abra") == 0
    assert names.count("Porygon-Z") == 2
    assert names.count("Porygon2") == 0
    assert names.count("Octillery") == 0
    assert names.count("Remoraid") == 0
    assert names.count("Sableye") == 0
    assert names.count("Aipom") == 4
    assert names.count("Ambipom") == 4
    assert names.count("Pikachu") == 0
    assert names.count("Raikou V") == 1
    assert names.count("Gholdengo") == 0
    assert names.count("Puzzle of Time") == 4
    assert names.count("Scoop Up Net") == 2
    assert names.count("Nest Ball") == 1
    assert names.count("Rare Candy") == 4
    assert names.count("Forest Seal Stone") == 1
    assert names.count("Enriching Energy") == 1
    assert names.count("Speed Lightning Energy") == 4
    assert names.count("Lightning Energy") == 3
    assert names.count("Draw Energy") == 4
    pile = build_g30_deck()
    assert copy_violations(pile, standard_60_rules()) == []
    aipom = [c for c in pile if c.name == "Aipom"]
    assert len(aipom) == 4
    assert all(c.catalog_id == "sv04-145" for c in aipom)
    assert fallback_named("Aipom").catalog_id == "swsh11-144"
    ambipom = next(c for c in pile if c.name == "Ambipom")
    assert ambipom.attacks[-1].name == "Hand Fling"
    assert ambipom.attacks[-1].text == HAND_FLING_TEXT
    lopunny = next(c for c in pile if c.name == "Lopunny")
    assert lopunny.catalog_id == "xy2-85"
    assert lopunny.abilities[0].name == "Big Jump"
    assert lopunny.abilities[0].text == BIG_JUMP_TEXT
    buneary = next(c for c in pile if c.name == "Buneary")
    assert buneary.catalog_id == "xy2-84"
    assert buneary.hp == 60
    raikou = next(c for c in pile if c.name == "Raikou V")
    assert "Lightning" in raikou.types
    assert raikou.catalog_id == "swsh9-48"
    assert raikou.abilities[0].name == "Fleet-Footed"
    assert raikou.abilities[0].text == FLEET_FOOTED_TEXT
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
    stone = next(c for c in pile if c.name == "Forest Seal Stone")
    assert stone.catalog_id == "swsh12-156"


def test_celebration_parses_printed_wording():
    effects = parse_effects(CELEBRATION_TEXT)
    spec = next(e for e in effects if e["kind"] == "take_prizes_if_hand")
    assert spec["hand"] == 30
    assert spec["prizes"] == 2
    assert spec["shuffle_hand"] is True


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


def test_fallback_prints_use_lab_wording():
    assert fallback_named("Ambipom").attacks[-1].text == HAND_FLING_TEXT
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


def test_speed_l_draws_only_on_lightning():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    raikou = _take(me, "Raikou V", used)
    ambipom = _take(me, "Ambipom", used)
    speed = _take(me, "Speed Lightning Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=raikou, played_turn=0)
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
    raikou2 = _take(me2, "Raikou V", used2)
    ambipom2 = _take(me2, "Ambipom", used2)
    speed2 = _take(me2, "Speed Lightning Energy", used2)
    rest2 = [i for i in range(len(me2.cards)) if i not in used2]
    me2.active = Pokemon(card_i=ambipom2, played_turn=0)
    me2.bench = [Pokemon(card_i=raikou2, played_turn=0)]
    me2.hand = []
    me2.deck = rest2
    game2._resolve_energy_attach_from_hand(me2, "a", me2.active, speed2)
    assert me2.hand == []
    assert not game2.events.get("speed_l_draw")


def test_hand_fling_scales_with_hand_size():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    ambipom = _take(me, "Ambipom", used)
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.hand = rest[:12]
    atk = next(a for a in me.card(ambipom).attacks if a.name == "Hand Fling")
    assert game._raw_attack_damage(me, foe, me.active, atk) == 20 * 12
    me.hand = rest[:16]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 20 * 16


def test_engine_grows_hand_and_pays_hand_fling():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    ambipom = _take(me, "Ambipom", used)
    poryz = _take(me, "Porygon-Z", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    raikou = _take(me, "Raikou V", used)
    enrich = _take(me, "Enriching Energy", used)
    draws = [_take(me, "Draw Energy", used) for _ in range(4)]
    bts = _take(me, "Broken Time-Space", used)
    speeds = [_take(me, "Speed Lightning Energy", used) for _ in range(4)]
    mewtwo = next(i for i, c in enumerate(foe.cards) if c.name == "Mewtwo ex")
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=poryz, played_turn=0)
    me.bench = [
        Pokemon(card_i=ambipom, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
        Pokemon(card_i=raikou, played_turn=0),
    ]
    me.prizes = rest[:6]
    rest = rest[6:]
    me.hand = [enrich, *speeds, *draws]
    me.deck = rest
    me.discard = []
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    game.turn = 2
    game._set_stadium(me.card(bts))
    start = len(me.hand)
    game._celebration_engine(me, "a")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Raikou V")
    attacker = next(m for m in me.in_play() if me.card(m.card_i).name == "Ambipom")
    assert any(is_speed_lightning_energy(me.card(i)) for i in host.energy)
    assert game.events.get("speed_l_draw")
    assert game.events.get("draw_energy_draw")
    # 4/4 Aipom–Ambipom draws Switch earlier; once Hand Fling already KOs, skip Big Jump.
    assert game.events.get("big_jump") or game.events.get("return_self_to_hand") or game._hand_fling_would_ko(me, foe)
    assert game._ambipom_can_pay(me, attacker)
    assert len(me.hand) > start
    assert game._hand_fling_would_ko(me, foe)
    game._celebration_align_attacker(me, "a")
    assert me.card(me.active.card_i).name == "Ambipom"
    game._attack(me, foe, "a")
    assert game.events.get("hand_fling")
    assert foe.active is None or foe.active.damage >= foe.card(mewtwo).hp


def test_evolve_keeps_buneary_under_lopunny_and_big_jump_returns_stack():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    raikou = _take(me, "Raikou V", used)
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
    assert me.card(me.active.card_i).name == "Raikou V"


def test_bts_allows_same_turn_aipom_line():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    aipom = _take(me, "Aipom", used)
    ambipom = _take(me, "Ambipom", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=aipom, played_turn=2)
    me.bench = []
    me.hand = [ambipom]
    me.deck = []
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert game._stadium_allows_immediate_evolve()
    assert game._can_evolve_now(me, "a", me.active)
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Ambipom"


def test_scoop_net_skips_speed_l_host():
    game = _game()
    raikou = fallback_named("Raikou V")
    ambipom = fallback_named("Ambipom")
    abra = fallback_named("Abra")
    assert not game._scoop_legal(raikou)
    assert game._scoop_legal(ambipom)
    assert game._scoop_legal(abra)


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
    aipom = _take(me, "Aipom", used)
    raikou = _take(me, "Raikou V", used)
    strat = game.strats["a"]
    pick = game._pick_starter(me, [raikou, buneary, aipom, porygon], strat)
    assert me.card(pick).name == "Porygon"
    pick = game._pick_starter(me, [raikou, aipom, buneary], strat)
    assert me.card(pick).name == "Buneary"


def test_celebration_benches_buneary_before_raikou_on_last_slot():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    extra_porygon = _take(me, "Porygon", used)
    aipom = _take(me, "Aipom", used)
    raikou = _take(me, "Raikou V", used)
    extra_aipom = _take(me, "Aipom", used)
    spare_aipom = _take(me, "Aipom", used)
    buneary = _take(me, "Buneary", used)
    me.active = Pokemon(card_i=porygon, played_turn=0)
    me.bench = [
        Pokemon(card_i=extra_porygon, played_turn=0),
        Pokemon(card_i=aipom, played_turn=0),
        Pokemon(card_i=raikou, played_turn=0),
        Pokemon(card_i=extra_aipom, played_turn=0),
    ]
    me.hand = [spare_aipom, buneary]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert "Buneary" in names
    assert names.count("Raikou V") == 1
    assert names.count("Aipom") == 2


def test_celebration_poffin_benches_buneary_ahead_of_aipom():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    buneary = _take(me, "Buneary", used)
    aipom = _take(me, "Aipom", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=porygon, played_turn=0)
    me.bench = []
    me.hand = []
    me.deck = [aipom, buneary, *rest]
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
    ambipom = _take(me, "Ambipom", used)
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


def test_celebration_searches_second_ambipom_while_one_in_play():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    porygon = _take(me, "Porygon", used)
    poryz = _take(me, "Porygon-Z", used)
    aipom = _take(me, "Aipom", used)
    ambipom = _take(me, "Ambipom", used)
    ambipom2 = _take(me, "Ambipom", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.bench = [
        Pokemon(card_i=poryz, played_turn=0, underneath=[porygon]),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
        Pokemon(card_i=aipom, played_turn=0),
    ]
    me.hand = []
    me.deck = [ambipom2]
    assert game._celebration_needs_ambipom(me)
    assert game._celebration_wally_helps(me)
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "ambipom"


def test_celebration_hunts_backup_aipom_after_first_ambipom():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    ambipom = _take(me, "Ambipom", used)
    poryz = _take(me, "Porygon-Z", used)
    buneary = _take(me, "Buneary", used)
    lopunny = _take(me, "Lopunny", used)
    aipom = _take(me, "Aipom", used)
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.bench = [
        Pokemon(card_i=poryz, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = []
    me.deck = [aipom]
    in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
    in_hand = {me.card(i).name.lower() for i in me.hand}
    assert "aipom" in game._celebration_missing_hunt(me, in_play, in_hand)
    prefer = [n.lower() for n in game._pokemon_search_prefer(me, "a")]
    assert prefer[0] == "aipom"


def test_celebration_benches_replacement_aipom_after_ambipom():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    ambipom = _take(me, "Ambipom", used)
    aipom = _take(me, "Aipom", used)
    poryz = _take(me, "Porygon-Z", used)
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.bench = [Pokemon(card_i=poryz, played_turn=0)]
    me.hand = [aipom]
    game._play_basics(me)
    names = [me.card(m.card_i).name for m in me.in_play()]
    assert names.count("Aipom") == 1
    assert names.count("Ambipom") == 1


def test_celebration_big_jump_when_hand_fling_not_ready():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    ambipom = _take(me, "Ambipom", used)
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
        Pokemon(card_i=ambipom, played_turn=0),
        Pokemon(card_i=lopunny, played_turn=0, underneath=[buneary]),
    ]
    me.hand = [enrich, draw]
    me.deck = rest
    me.discard = []
    foe.active = Pokemon(card_i=mewtwo, played_turn=0)
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert not game._hand_fling_would_ko(me, foe)
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
    ambipom = _take(me, "Ambipom", used)
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
    raikou = _take(me, "Raikou V", used)
    ambipom = _take(me, "Ambipom", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
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
    raikou2 = _take(me2, "Raikou V", used2)
    ambipom2 = _take(me2, "Ambipom", used2)
    rest2 = [i for i in range(len(me2.cards)) if i not in used2]
    me2.active = Pokemon(card_i=ambipom2, played_turn=0)
    me2.bench = [Pokemon(card_i=raikou2, played_turn=0)]
    me2.hand = []
    me2.deck = rest2
    game2._use_passive_abilities(me2, "a")
    assert not game2.events.get("fleet_footed")


def test_forest_seal_on_raikou_searches_any_card():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    raikou = _take(me, "Raikou V", used)
    ambipom = _take(me, "Ambipom", used)
    stone = _take(me, "Forest Seal Stone", used)
    candy = _take(me, "Rare Candy", used)
    me.active = Pokemon(card_i=ambipom, played_turn=0)
    me.bench = [Pokemon(card_i=raikou, played_turn=0, tool=stone)]
    me.hand = []
    me.deck = [candy]
    game._use_passive_abilities(me, "a")
    assert game.events.get("star_alchemy") == 1
    assert candy in me.hand
    assert me.vstar_used is True


def test_rare_candy_skips_porygon_to_z_without_porygon2_in_sixty():
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
    assert "Porygon2" not in {c.name for c in me.cards}


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
