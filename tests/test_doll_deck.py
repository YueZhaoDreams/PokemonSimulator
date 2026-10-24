"""Doll is the locked 60. Printed sentences are the effects.

The 1000-game rates in data/lab/set-doll.json come from the fight-script holdout.
Item dolls are Trainers, so Nest Ball does not search them.
"""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects, parse_trainer_effects
from app.engine.game import ST_ASLEEP, Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import SET_DOLL_NAMES, build_doll_deck, fallback_named

_EEEEEK = "Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."
_SWEET = "As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks."
_SHOVEL = (
    "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, "
    "discard the top 2 cards of your opponent's deck."
)
_DEW = "If the Pokémon this card is attached to is Knocked Out, your opponent takes 1 fewer Prize card."
_PATCH = "Attach a basic Darkness Energy card from your discard pile to 1 of your Benched Darkness Pokémon."
_VESSEL = (
    "Once during your turn (before your attack), you may discard all cards attached to this Pokémon "
    "and attach it to 1 of your Pokémon as a Pokémon Tool card. When the Pokémon this card is attached "
    "to is Knocked Out, your opponent takes 1 fewer Prize card."
)
_HAUNT = "Put 3 damage counters on your opponent's Active Pokémon."
_SWIPES = "Flip 3 coins. This attack does 10 damage for each heads."


class _Still(Random):
    def shuffle(self, seq, random=None):
        return None


def _pile() -> list:
    specs = [
        ("cleffa hgss", 4),
        ("Smoochum", 1),
        ("mime jr. col", 1),
        ("Sableye", 2),
        ("Nincada", 1),
        ("Shedinja", 1),
        ("Manaphy", 1),
        ("Lillie's Poké Doll", 2),
        ("Snorlax Doll", 1),
        ("Robo Substitute Team Flare Gear", 1),
        ("Cursed Shovel", 1),
        ("Life Dew", 1),
        ("Dark Patch", 1),
        ("Puzzle of Time", 2),
        ("Team Rocket's Handiwork", 1),
        ("Boss's Orders", 1),
        ("Switch", 1),
        ("Nest Ball", 1),
        ("Level Ball", 1),
        ("Water Energy", 2),
        ("Darkness Energy", 8),
    ]
    cards = []
    for name, count in specs:
        cards.extend(fallback_named(name) for _ in range(count))
    while len(cards) < 40:
        cards.append(fallback_named("Darkness Energy"))
    return cards


class _Board:
    def __init__(self, strat_a="doll", strat_b="balanced"):
        self.game = Game(
            _pile(),
            _pile(),
            standard_60_rules(),
            StrategySpec.from_dict(strat_a),
            StrategySpec.from_dict(strat_b),
            Random(1),
            trace=True,
        )
        self._used = {"a": set(), "b": set()}

    def take(self, who: str, name: str) -> int:
        player = self.game.players[who]
        for i, card in enumerate(player.cards):
            if i in self._used[who] or card.name != name:
                continue
            self._used[who].add(i)
            return i
        raise AssertionError(name)

    def seat(self, who: str, *, active=None, bench=(), hand=(), discard=(), deck=None):
        player = self.game.players[who]
        if active is None:
            player.active = None
        else:
            name, fuels = active
            player.active = Pokemon(
                card_i=self.take(who, name),
                energy=[self.take(who, fuel) for fuel in fuels],
            )
        player.bench = [Pokemon(card_i=self.take(who, name)) for name in bench]
        player.hand = [self.take(who, name) for name in hand]
        player.discard = [self.take(who, name) for name in discard]
        if deck is None:
            player.deck = [i for i in range(len(player.cards)) if i not in self._used[who]]
        else:
            player.deck = [self.take(who, name) for name in deck]
        player.prizes = []
        return player


def test_doll_list_is_the_locked_60():
    names = list(SET_DOLL_NAMES)
    assert len(names) == 60
    assert names.count("Cleffa") == 4
    assert names.count("Smoochum") == 2
    assert names.count("Mime Jr.") == 2
    assert names.count("Slumbering Forest") == 2
    assert names.count("Battle Cage") == 4
    assert names.count("Manaphy") == 1
    assert names.count("Switch") == 2
    assert names.count("Sableye") == 2
    assert names.count("Darkness Energy") == 2
    assert names.count("Dark Patch") == 1
    assert names.count("Puzzle of Time") == 4
    assert names.count("VS Seeker") == 4
    assert names.count("Team Rocket's Handiwork") == 4
    assert names.count("Rescue Carrier") == 3
    assert names.count("Robo Substitute Team Flare Gear") == 4
    assert names.count("Lillie's Poké Doll") == 4
    assert names.count("Snorlax Doll") == 2
    assert names.count("Cursed Shovel") == 3
    assert names.count("Life Dew") == 1
    assert names.count("Nincada") == 1
    assert names.count("Shedinja") == 1
    assert names.count("Field Blower") == 1
    assert names.count("Level Ball") == 2
    assert names.count("Nest Ball") == 0
    assert names.count("Buddy-Buddy Poffin") == 2
    assert names.count("Crushing Hammer") == 2
    assert "Miss Fortune Sisters" not in names
    assert "Energy Retrieval" not in names
    pile = build_doll_deck()
    assert copy_violations(pile, standard_60_rules()) == []
    assert [c.catalog_id for c in pile if c.name == "Cleffa"] == ["hgss1-17"] * 4
    assert [c.attacks[0].name for c in pile if c.name == "Cleffa"] == ["Eeeeeeek"] * 4
    assert [c.attacks[0].text for c in pile if c.name == "Cleffa"] == [_EEEEEK] * 4
    assert [c.catalog_id for c in pile if c.name == "Mime Jr."] == ["col1-47"] * 2
    assert [c.attacks[0].name for c in pile if c.name == "Mime Jr."] == ["Sleepy Lost"] * 2
    smoochum = [c for c in pile if c.name == "Smoochum"]
    assert len(smoochum) == 2 and smoochum[0].attacks[0].name == "Energy Antics"
    assert smoochum[0].catalog_id == "hgss1-30"
    assert [c.attacks[0].name for c in pile if c.name == "Sableye"] == ["Junk Hunt"] * 2
    dew = [c for c in pile if c.name == "Life Dew"]
    assert len(dew) == 1 and dew[0].catalog_id == "bw9-107" and dew[0].text == _DEW
    robo = [c for c in pile if c.name == "Robo Substitute Team Flare Gear"]
    assert len(robo) == 4 and {c.catalog_id for c in robo} == {"xy4-102"}
    assert [c.catalog_id for c in pile if c.name == "Cursed Shovel"] == ["swsh2-157"] * 3
    assert [c.catalog_id for c in pile if c.name == "Nincada"] == ["sm8-29"]
    assert [c.attacks[0].text for c in pile if c.name == "Nincada"] == [_SWIPES]
    shed = next(c for c in pile if c.name == "Shedinja")
    assert shed.catalog_id == "sm8-95"
    assert shed.text == _VESSEL
    assert shed.attacks[0].text == _HAUNT
    assert shed.abilities[0].text == _VESSEL
    for doll_name in ("Lillie's Poké Doll", "Robo Substitute Team Flare Gear", "Snorlax Doll"):
        card = next(c for c in pile if c.name == doll_name)
        assert card.is_trainer and not card.is_pokemon
        eff = parse_trainer_effects(card.text)[0]
        assert eff["kind"] == "play_as_pokemon" and eff["no_prize"] is True
    assert fallback_named("Cleffa").attacks[0].name == "Grasping Draw"
    assert fallback_named("Cleffa").catalog_id == "sv03-080"
    assert fallback_named("Robo Substitute").catalog_id == "xy4-102"
    nest = fallback_named("Nest Ball")
    assert "basic" in nest.text.lower()
    level = fallback_named("Level Ball")
    assert level.catalog_id == "swsh5-129"
    parsed_level = parse_trainer_effects(level.text)
    assert parsed_level == [{"kind": "search_pokemon_max_hp", "max_hp": 90}]
    for key in ("doll", "22"):
        loaded = load_seed_deck(key)
        assert loaded["id"] == "seed-doll"
        assert loaded["name"] == "Doll"
        assert [c["name"] for c in loaded["cards"]] == names
        assert [c["catalog_id"] for c in loaded["cards"] if c["name"] == "Cleffa"] == ["hgss1-17"] * 4
    assert default_rule_presets_for("seed-doll") == ["s60"]
    assert "seed-doll" in S60_SEED_IDS
    spec = StrategySpec.from_dict("doll")
    assert spec.name == "doll"
    assert spec.item_spend == 1.0
    assert spec.search_aces == []
    assert spec.attach_pokemon_as_energy == 0.0


def test_printed_doll_sentences():
    eee = parse_effects(_EEEEEK)
    kinds = [e["kind"] for e in eee]
    assert "shuffle_hand_then_draw" in kinds
    assert "draw" not in kinds
    drawn = next(e for e in eee if e["kind"] == "shuffle_hand_then_draw")
    assert drawn["amount"] == 6
    assert any(e.get("kind") == "status" and e.get("status") == "asleep" and e.get("target") == "self" for e in eee)
    face = parse_ability_effects(_SWEET)
    assert face[0]["kind"] == "prevent_attack_damage_while_asleep"
    youngster = parse_effects("Shuffle your hand into your deck and draw 5 cards.")
    assert [e["kind"] for e in youngster] == ["draw"]
    celebration = parse_effects(
        "If you have exactly 30 cards in your hand, take 2 Prize cards. If you do, shuffle your hand into your deck."
    )
    assert "shuffle_hand_then_draw" not in [e["kind"] for e in celebration]
    shovel = parse_trainer_effects(_SHOVEL)
    assert shovel == [{"kind": "mill_top_on_attack_ko", "count": 2}]
    dew = parse_trainer_effects(_DEW)[0]
    assert dew["kind"] == "fewer_prizes_on_ko" and dew["count"] == 1 and dew["attack_only"] is False
    patch = parse_trainer_effects(_PATCH)[0]
    assert patch["kind"] == "attach_basic_energy_from_discard"
    assert patch["count"] == 1 and patch["bench_only"] is True
    vessel_abi = parse_ability_effects(_VESSEL)
    assert any(e["kind"] == "attach_self_as_tool" for e in vessel_abi)
    vessel_tool = parse_trainer_effects(_VESSEL)
    assert vessel_tool[0]["kind"] == "fewer_prizes_on_ko"
    assert vessel_tool[0]["count"] == 1 and vessel_tool[0]["attack_only"] is False
    puzzle = parse_trainer_effects(fallback_named("Puzzle of Time").text)
    assert puzzle[0]["pair_count"] == 2


def test_doll_goes_first_even_when_the_caller_says_otherwise():
    one = [fallback_named("Cleffa")] + [fallback_named("Darkness Energy")] * 20
    game = Game(
        one,
        list(one),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict("balanced"),
        Random(0),
        first="b",
    )
    assert game.first == "a"
    assert game.current == "a"
    assert game.events["doll_go_first"] == 1
    other = Game(
        list(one),
        list(one),
        standard_60_rules(),
        StrategySpec.from_dict("balanced"),
        StrategySpec.from_dict("doll"),
        Random(0),
        first="a",
    )
    assert other.first == "b"
    both = Game(
        list(one),
        list(one),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict("doll"),
        Random(0),
        first="b",
    )
    assert both.first == "a"


def test_doll_opening_benches_one_snorlax_doll():
    cards = [fallback_named("Darkness Energy")] * 60
    cards[59] = fallback_named("cleffa hgss")
    cards[58] = fallback_named("Snorlax Doll")
    cards[57] = fallback_named("Snorlax Doll")
    game = Game(
        cards,
        list(cards),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict("balanced"),
        _Still(0),
    )
    me = game.players["a"]
    assert me.card(me.active.card_i).name == "Cleffa"
    assert [me.card(mon.card_i).name for mon in me.bench] == ["Snorlax Doll"]
    assert sum(1 for i in me.hand if me.card(i).name == "Snorlax Doll") == 1


def test_eeeeeeek_shuffles_then_draws_once():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        hand=["Water Energy"],
        deck=["Darkness Energy"] * 8,
    )
    board.seat("b", active=("Sableye", []))
    board.game._attack(me, board.game.players["b"], "a")
    assert board.game.events["eeeeeeek_shuffle"] == 1
    assert len(me.hand) == 6
    assert len(me.deck) == 3
    assert me.active.status & ST_ASLEEP
    assert board.game._choose_attack(me, board.game.players["b"], board.game.strats["a"]) is None


def test_doll_does_not_use_fury_swipes_or_haunt():
    board = _Board()
    me = board.seat("a", active=("Nincada", ["Darkness Energy"]))
    foe = board.seat("b", active=("Sableye", []))
    assert board.game._choose_attack(me, foe, board.game.strats["a"]) is None
    me2 = board.seat("a", active=("Shedinja", ["Darkness Energy"]))
    assert board.game._choose_attack(me2, foe, board.game.strats["a"]) is None


def test_dark_patch_attaches_to_benched_sableye():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        bench=["Sableye"],
        hand=["Dark Patch"],
        discard=["Darkness Energy"],
    )
    board.game._resolve_trainer(me, board.game.players["b"], me.card(me.hand[0]), who="a", card_i=me.hand[0])
    sable = me.bench[0]
    assert len(sable.energy) == 1
    assert me.card(sable.energy[0]).name == "Darkness Energy"
    assert board.game.events["dark_patch"] == 1


def test_shovel_mills_the_printed_count_only_after_attack_damage():
    board = _Board()
    me = board.seat("a", active=("Lillie's Poké Doll", []), deck=["Darkness Energy"] * 4)
    foe = board.seat("b", active=("Sableye", []), deck=["Darkness Energy"] * 4)
    shovel = board.take("a", "Cursed Shovel")
    me.active.tool = shovel
    board.game._add_attack_damage(me, me.active, 30)
    board.game._check_ko(me, foe, "a")
    assert len(foe.deck) == 2
    assert board.game.events["shovel_mill"] == 1
    assert foe.prizes_taken == 0

    board2 = _Board()
    me2 = board2.seat("a", active=("Lillie's Poké Doll", []))
    foe2 = board2.seat("b", active=("Sableye", []), deck=["Darkness Energy"] * 4)
    me2.active.tool = board2.take("a", "Cursed Shovel")
    me2.active.damage = board2.game._max_hp(me2, me2.active)
    board2.game._attack_damaged_ids.clear()
    board2.game._check_ko(me2, foe2, "a")
    assert len(foe2.deck) == 4
    assert "shovel_mill" not in board2.game.events

    board3 = _Board()
    me3 = board3.seat("a", active=("Lillie's Poké Doll", []))
    foe3 = board3.seat("b", active=("Sableye", []), deck=["Darkness Energy"] * 4)
    shovel3 = board3.take("a", "Cursed Shovel")
    me3.cards[shovel3].text = (
        "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, "
        "discard the top 3 cards of your opponent's deck."
    )
    me3.active.tool = shovel3
    board3.game._add_attack_damage(me3, me3.active, 30)
    board3.game._check_ko(me3, foe3, "a")
    assert len(foe3.deck) == 1


def test_shovel_ignores_damage_from_your_own_attack():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        bench=["Lillie's Poké Doll"],
        deck=["Darkness Energy"] * 4,
    )
    foe = board.seat("b", active=("Sableye", []), deck=["Darkness Energy"] * 4)
    me.bench[0].tool = board.take("a", "Cursed Shovel")
    board.game._self_bench_damage(me, 30)
    board.game._check_ko(me, foe, "a")
    assert me.bench == []
    assert "shovel_mill" not in board.game.events
    assert len(foe.deck) == 4
    assert len(me.deck) == 4


def test_haunt_places_the_printed_counters():
    parsed = parse_effects(_HAUNT)
    assert parsed == [{"kind": "active_damage_counters", "counters": 3}]
    bench = parse_effects("Put 3 damage counters on 1 of your opponent's Benched Pokémon.")
    assert {"kind": "bench_damage_counters", "counters": 3} in bench
    assert all(effect["kind"] != "active_damage_counters" for effect in bench)
    board = _Board(strat_a="balanced", strat_b="balanced")
    me = board.seat("a", active=("Shedinja", ["Darkness Energy"]), deck=["Darkness Energy"] * 4)
    foe = board.seat("b", active=("Lillie's Poké Doll", []), deck=["Darkness Energy"] * 4)
    foe.active.tool = board.take("b", "Cursed Shovel")
    board.game._attack(me, foe, "a")
    assert foe.active is not None and foe.active.damage == 30
    board.game._check_ko(foe, me, "b")
    assert "shovel_mill" not in board.game.events
    assert len(me.deck) == 4
    assert len(foe.deck) == 4


def test_life_dew_cuts_one_prize_without_an_attack():
    board = _Board()
    me = board.seat("a", active=("Sableye", []))
    foe = board.seat("b", active=("Cleffa", []))
    foe.prizes = [board.take("b", "Darkness Energy") for _ in range(4)]
    me.active.tool = board.take("a", "Life Dew")
    me.active.damage = board.game._max_hp(me, me.active)
    board.game._check_ko(me, foe, "a")
    assert foe.prizes_taken == 0
    assert len(foe.prizes) == 4
    assert board.game.events["ko_no_prize"] == 1


def test_vessel_of_life_attaches_shedinja_as_a_tool():
    board = _Board()
    me = board.game.players["a"]
    shed = board.take("a", "Shedinja")
    nincada = board.take("a", "Nincada")
    energy = board.take("a", "Darkness Energy")
    sable = board.take("a", "Sableye")
    me.active = Pokemon(card_i=shed, energy=[energy], underneath=[nincada])
    me.bench = [Pokemon(card_i=sable)]
    me.hand = []
    me.discard = []
    me.deck = []
    board.seat("b", active=("Cleffa", []))
    assert board.game._use_abilities(me, board.game.players["b"], "a") is False
    host = me.active
    assert me.card(host.card_i).name == "Sableye"
    assert host.tool == shed
    assert nincada in me.discard and energy in me.discard
    assert board.game.events["vessel"] == 1
    assert all(mon.card_i != shed for mon in me.in_play())


def test_level_ball_takes_shedinja_once_nincada_is_out():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        bench=["Nincada"],
        hand=["Level Ball"],
        deck=["Shedinja", "Manaphy", "Sableye"],
    )
    board.seat("b", active=("Sableye", []))
    played = me.hand[0]
    me.hand.remove(played)
    me.discard.append(played)
    board.game._resolve_trainer(me, board.game.players["b"], me.card(played), who="a", card_i=played)
    assert [me.card(i).name for i in me.hand] == ["Shedinja"]
    assert board.game.events["level_ball"] == 1


def test_level_ball_takes_a_basic_before_nincada_is_out():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        hand=["Level Ball"],
        deck=["Shedinja", "Manaphy"],
    )
    board.seat("b", active=("Sableye", []))
    played = me.hand[0]
    me.hand.remove(played)
    me.discard.append(played)
    board.game._resolve_trainer(me, board.game.players["b"], me.card(played), who="a", card_i=played)
    assert [me.card(i).name for i in me.hand] == ["Manaphy"]


def test_puzzle_pair_leaves_the_second_card_when_only_snorlax_is_there():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        hand=["Puzzle of Time", "Puzzle of Time"],
        discard=["Snorlax Doll"],
        deck=["Darkness Energy", "Switch", "Nest Ball", "Water Energy"],
    )
    board.seat("b", active=("Sableye", []))
    assert board.game._pick_trainer(me) is None
    before = [me.card(i).name for i in me.deck]
    played = me.hand[0]
    me.hand.remove(played)
    me.discard.append(played)
    board.game._resolve_trainer(me, board.game.players["b"], me.card(played), who="a", card_i=played)
    assert [me.card(i).name for i in me.hand] == ["Puzzle of Time"]
    assert [me.card(i).name for i in me.discard] == ["Snorlax Doll", "Puzzle of Time"]
    assert "puzzle_pair" not in board.game.events
    assert board.game.events["puzzle_look"] == 3
    assert sorted(me.card(i).name for i in me.deck) == sorted(before)


def test_puzzle_pair_takes_a_real_card_and_leaves_snorlax():
    board = _Board()
    me = board.seat(
        "a",
        active=("Cleffa", []),
        hand=["Puzzle of Time", "Puzzle of Time"],
        discard=["Snorlax Doll", "Lillie's Poké Doll"],
        deck=["Darkness Energy"] * 4,
    )
    board.seat("b", active=("Sableye", []))
    picked = board.game._pick_trainer(me)
    assert picked is not None and me.card(picked).name == "Puzzle of Time"
    me.hand.remove(picked)
    me.discard.append(picked)
    board.game._resolve_trainer(me, board.game.players["b"], me.card(picked), who="a", card_i=picked)
    assert [me.card(i).name for i in me.hand] == ["Lillie's Poké Doll"]
    assert [me.card(i).name for i in me.discard] == ["Snorlax Doll", "Puzzle of Time", "Puzzle of Time"]
    assert board.game.events["puzzle_pair"] == 1
    assert board.game.events["puzzle_retrieve"] == 1
    assert "puzzle_look" not in board.game.events


def test_junk_hunt_skips_snorlax_and_pays_for_the_patch_first():
    board = _Board()
    me = board.seat(
        "a",
        active=("Sableye", []),
        discard=["Snorlax Doll", "Lillie's Poké Doll", "Dark Patch"],
    )
    board.game._recycle_items_from_discard(me, 2)
    assert [me.card(i).name for i in me.hand] == ["Dark Patch", "Lillie's Poké Doll"]
    assert [me.card(i).name for i in me.discard] == ["Snorlax Doll"]
