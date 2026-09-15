from random import Random

from app.engine.effects import parse_ability_effects, parse_effects, parse_energy_effects, parse_trainer_effects
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
ENRICHING_TEXT = (
    "As long as this card is attached to a Pokémon, it provides Colorless Energy. "
    "When you attach this card from your hand to a Pokémon, draw 4 cards."
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
    assert names.count("Abra") == 3
    assert names.count("Porygon-Z") == 2
    assert names.count("Octillery") == 2
    assert names.count("Sableye") == 2
    assert names.count("Gimmighoul") == 3
    assert names.count("Gholdengo") == 2
    assert names.count("Mew ex") == 1
    assert names.count("Puzzle of Time") == 4
    assert names.count("Scoop Up Net") == 4
    assert names.count("Junk Arm") == 4
    assert names.count("Broken Time-Space") == 3
    assert names.count("Enriching Energy") == 1
    assert names.count("Metal Energy") == 3
    assert names.count("Darkness Energy") == 1
    pile = build_g30_deck()
    assert copy_violations(pile, standard_60_rules()) == []
    gimmighoul = [c for c in pile if c.name == "Gimmighoul"]
    assert len(gimmighoul) == 3
    assert all(c.types == ["Metal"] and c.hp == 60 for c in gimmighoul)
    assert fallback_named("Gimmighoul").types == ["Psychic"]
    gholdengo = next(c for c in pile if c.name == "Gholdengo")
    assert gholdengo.attacks[0].name == "Celebration"
    assert "exactly 30" in gholdengo.attacks[0].text


def test_celebration_parses_printed_wording():
    effects = parse_effects(CELEBRATION_TEXT)
    spec = next(e for e in effects if e["kind"] == "take_prizes_if_hand")
    assert spec["hand"] == 30
    assert spec["prizes"] == 2
    assert spec["shuffle_hand"] is True


def test_crazy_code_and_teleporter_and_memory_helix_parse():
    crazy = parse_ability_effects(CRAZY_CODE_TEXT)
    assert crazy[0]["kind"] == "attach_special_energy_from_hand"
    assert crazy[0]["as_often_as_you_like"] is True
    tele = parse_ability_effects(TELEPORTER_TEXT)
    assert tele[0]["kind"] == "shuffle_self_into_deck"
    assert tele[0]["require_active"] is True
    helix = parse_ability_effects(MEMORY_HELIX_TEXT)
    assert helix[0]["kind"] == "copy_benched_attacks"


def test_enriching_and_abyssal_and_bts_parse():
    enrich = parse_energy_effects(ENRICHING_TEXT)
    draw = next(e for e in enrich if e["kind"] == "draw_on_attach_from_hand")
    assert draw["amount"] == 4
    until = parse_ability_effects(ABYSSAL_TEXT)
    assert until[0]["kind"] == "draw_until_hand"
    assert until[0]["count"] == 5
    bts = parse_ability_effects(BTS_TEXT)
    assert bts[0]["kind"] == "evolve_just_played_or_evolved"


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
    assert fallback_named("Gholdengo").attacks[0].text == CELEBRATION_TEXT
    assert next(a.text for a in fallback_named("Porygon-Z").abilities) == CRAZY_CODE_TEXT
    assert fallback_named("Puzzle of Time").text == PUZZLE_TEXT
    assert fallback_named("Scoop Up Net").text == NET_TEXT
    assert fallback_named("Enriching Energy").text == ENRICHING_TEXT
    assert fallback_named("Broken Time-Space").text == BTS_TEXT
    assert next(a.text for a in fallback_named("Mew ex").abilities) == MEMORY_HELIX_TEXT


def test_loop_parks_enriching_at_exactly_thirty():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    mew = _take(me, "Mew ex", used)
    gholdengo = _take(me, "Gholdengo", used)
    poryz = _take(me, "Porygon-Z", used)
    octillery = _take(me, "Octillery", used)
    abra = _take(me, "Abra", used)
    enrich = _take(me, "Enriching Energy", used)
    metal = _take(me, "Metal Energy", used)
    puzzles = [_take(me, "Puzzle of Time", used) for _ in range(4)]
    nets = [_take(me, "Scoop Up Net", used) for _ in range(2)]
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=mew, energy=[metal], played_turn=0)
    me.bench = [
        Pokemon(card_i=gholdengo, played_turn=0),
        Pokemon(card_i=poryz, played_turn=0),
        Pokemon(card_i=octillery, played_turn=0),
        Pokemon(card_i=abra, played_turn=0),
    ]
    me.prizes = rest[:6]
    rest = rest[6:]
    # 25 in hand: attach (+3) → bounce (+2 net from start) → attach parks at 30.
    me.hand = [enrich, *puzzles, *nets, *rest[:18]]
    me.deck = rest[18:]
    me.discard = []
    game.turn = 2
    game._celebration_engine(me, "a")
    assert len(me.hand) == 30
    assert game.events.get("hand_thirty")
    host = next(m for m in me.in_play() if me.card(m.card_i).name == "Abra")
    assert any("enriching" in me.card(i).name.lower() for i in host.energy)
    assert host is not me.active


def test_celebration_takes_two_prizes_and_shuffles_hand():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    mew = _take(me, "Mew ex", used)
    gholdengo = _take(me, "Gholdengo", used)
    metal = _take(me, "Metal Energy", used)
    rest = [i for i in range(len(me.cards)) if i not in used]
    me.active = Pokemon(card_i=mew, energy=[metal], played_turn=0)
    me.bench = [Pokemon(card_i=gholdengo, played_turn=0)]
    me.prizes = rest[:6]
    me.hand = rest[6:36]
    me.deck = rest[36:]
    me.discard = []
    foe.active = Pokemon(card_i=0, played_turn=0)
    assert len(me.hand) == 30
    game.turn = 2
    game._attack(me, foe, "a")
    assert me.prizes_taken == 2
    assert len(me.prizes) == 4
    assert not me.hand
    assert game.events.get("celebration") == 2


def test_memory_helix_copies_benched_celebration():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    mew = _take(me, "Mew ex", used)
    gholdengo = _take(me, "Gholdengo", used)
    me.active = Pokemon(card_i=mew, played_turn=0)
    me.bench = [Pokemon(card_i=gholdengo, played_turn=0)]
    names = {atk.name for atk in game._attacks_for(me, me.active)}
    assert "Celebration" in names
    assert "Teleportation Burst" in names


def test_bts_allows_same_turn_porygon_line():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    pory = _take(me, "Porygon", used)
    pory2 = _take(me, "Porygon2", used)
    poryz = _take(me, "Porygon-Z", used)
    bts = _take(me, "Broken Time-Space", used)
    me.active = Pokemon(card_i=pory, played_turn=2)
    me.bench = []
    me.hand = [pory2, poryz]
    me.deck = []
    game.turn = 2
    game._set_stadium(me.card(bts))
    assert game._stadium_allows_immediate_evolve()
    assert game._can_evolve_now(me, "a", me.active)
    game._evolve(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Porygon-Z"


def test_scoop_net_is_legal_on_mew_ex_not_required():
    game = _game()
    mew = fallback_named("Mew ex")
    gholdengo = fallback_named("Gholdengo")
    assert game._scoop_legal(mew)
    assert game._scoop_legal(gholdengo)
    assert game._scoop_legal(fallback_named("Abra"))


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
