"""Locked Kecleon list and the printed sentences that list uses."""

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import SET_KECLEON_NAMES, build_fallback_deck, build_kecleon_deck, fallback_named

WHIP = (
    "Reveal any number of Pokémon from your hand, and this attack does 30 damage "
    "for each different type of Pokémon you revealed in this way."
)
RING = (
    "When you play this Pokémon from your hand onto your Bench, you may search your deck "
    "for up to 3 Pokémon-EX (except for Hoopa-EX), reveal them, and put them into your hand. "
    "Shuffle your deck afterward."
)
RADAR = (
    "Look at the top 5 cards of your deck, choose as many Pokémon as you like, show them to your "
    "opponent, and put them into your hand. Put the other cards back on top of your deck. "
    "Shuffle your deck afterward."
)
TEAMMATES = (
    "You can play this card only if 1 of your Pokémon was Knocked Out during your opponent's last turn. "
    "Search your deck for up to 2 cards and put them into your hand. Shuffle your deck afterward."
)


def test_printed_sentences_parse_their_numbers():
    whip = parse_effects(WHIP, "30×")
    assert {"kind": "reveal_hand_types", "per": 30} in whip
    assert not any(e.get("kind") == "times" for e in whip)
    ring = parse_ability_effects(RING)
    assert {
        "kind": "search_hyphen_ex_from_hand",
        "count": 3,
        "except_name": "hoopa-ex",
    } in ring
    radar = parse_trainer_effects(RADAR)
    assert {"kind": "look_top_pokemon", "look": 5} in radar
    mates = parse_trainer_effects(TEAMMATES)
    assert {"kind": "search_if_ko_last_turn", "count": 2} in mates


def test_kecleon_list_is_sixty_and_named():
    assert len(SET_KECLEON_NAMES) == 60
    deck = build_kecleon_deck()
    assert [c.name for c in deck] == list(SET_KECLEON_NAMES)
    assert copy_violations(deck, standard_60_rules()) == []
    kecleon = fallback_named("Kecleon")
    assert kecleon.catalog_id == "me6-83"
    assert kecleon.hp == 90
    assert any(a.name == "Colorful Whip" for a in kecleon.attacks)
    locked = load_seed_deck("kecleon")
    assert locked["name"] == "Kecleon"
    assert locked["id"] == "seed-kecleon"
    assert [c["name"] for c in locked["cards"]] == list(SET_KECLEON_NAMES)


def _game():
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 4 + ["Psychic Energy"] * 4 + ["Cubone"] * 51)
    return Game(
        build_kecleon_deck(),
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(1),
    )


def _idx(player, name, skip=0):
    found = [i for i, card in enumerate(player.cards) if card.name == name]
    return found[skip]


def test_colorful_whip_counts_each_type_on_a_dual_type_card():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    kecleon = _idx(me, "Kecleon")
    extra = _idx(me, "Kecleon", 1)
    volcanion = _idx(me, "Volcanion-EX")
    dce = _idx(me, "Double Colorless Energy")
    me.active = Pokemon(card_i=kecleon, energy=[dce], played_turn=0)
    me.bench = []
    me.hand = [extra, volcanion]
    me.deck = [i for i in range(len(me.cards)) if i not in {kecleon, extra, volcanion, dce}]
    me.discard = []
    foe.active = Pokemon(card_i=_idx(foe, "Starly"), played_turn=0)
    whip = next(a for a in me.card(kecleon).attacks if a.name == "Colorful Whip")
    # Extra Kecleon is Colorless. Volcanion-EX is Fire and Water.
    assert game._raw_attack_damage(me, foe, me.active, whip) == 90
    me.hand = [volcanion]
    assert game._raw_attack_damage(me, foe, me.active, whip) == 60
    game._attack(me, foe, "a")
    assert foe.active.damage == 60
    assert game.events.get("colorful_whip") == 1
    assert game.events.get("colorful_whip_types") == 2


def test_scoundrel_ring_searches_only_from_the_hand():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    package = [
        _idx(me, "M Gardevoir-EX"),
        _idx(me, "M Steelix-EX"),
        _idx(me, "Volcanion-EX"),
        _idx(me, "M Latios-EX"),
        _idx(me, "Fezandipiti ex"),
    ]
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = []
    me.hand = [hoopa]
    me.deck = package + [i for i in range(len(me.cards)) if i not in {kecleon, hoopa, *package}]
    me.discard = []
    game._play_basics(me)
    assert any(me.card(mon.card_i).name == "Hoopa-EX" for mon in me.bench)
    found = {me.card(i).name for i in me.hand}
    assert {"M Gardevoir-EX", "M Steelix-EX", "Volcanion-EX"} <= found
    assert "Hoopa-EX" not in found
    assert "Fezandipiti ex" not in found
    assert "M Latios-EX" not in found
    assert game.events.get("scoundrel_ring") == 3

    game.events.clear()
    me.bench.clear()
    me.hand = []
    me.deck = [_idx(me, "Hoopa-EX", 1), _idx(me, "Volcanion-EX")]
    game._bench_basic_from_deck(me, "a", source="nest ball")
    assert me.bench == []
    assert game.events.get("scoundrel_ring") is None


def test_poke_radar_takes_every_pokemon_from_the_printed_look():
    game = _game()
    me = game.players["a"]
    radar = _idx(me, "Poké Radar")
    top = [
        _idx(me, "Kecleon"),
        _idx(me, "Fire Energy"),
        _idx(me, "Druddigon"),
        _idx(me, "Switch"),
        _idx(me, "Psychic Energy"),
    ]
    me.hand = [radar]
    me.deck = list(top)
    me.discard = []
    card = me.card(radar)
    game._resolve_trainer(me, game.players["b"], card, who="a", card_i=radar)
    assert _idx(me, "Kecleon") in me.hand
    assert _idx(me, "Druddigon") in me.hand
    assert _idx(me, "Fire Energy") not in me.hand
    assert game.events.get("poke_radar") == 2


def test_teammates_waits_for_the_knock_out():
    game = _game()
    me = game.players["a"]
    mates = _idx(me, "Teammates")
    dce = _idx(me, "Double Colorless Energy")
    boss = _idx(me, "Boss's Orders")
    me.hand = []
    me.deck = [dce, boss]
    me.discard = [mates]
    me.ko_since_opp_turn = False
    me.supporter_used = True
    game._resolve_trainer(me, game.players["b"], me.card(mates), who="a", card_i=mates)
    assert mates in me.hand
    assert me.deck == [dce, boss]
    assert me.supporter_used is False

    me.hand.remove(mates)
    me.discard.append(mates)
    me.supporter_used = True
    me.ko_since_opp_turn = True
    game._resolve_trainer(me, game.players["b"], me.card(mates), who="a", card_i=mates)
    assert {dce, boss} <= set(me.hand)
    assert game.events.get("teammates") == 1


def test_energy_retrieval_leaves_special_energy():
    game = _game()
    me = game.players["a"]
    retrieval = _idx(me, "Energy Retrieval")
    fire = _idx(me, "Fire Energy")
    dce = _idx(me, "Double Colorless Energy")
    me.hand = [retrieval]
    me.discard = [dce, fire]
    game._resolve_trainer(me, game.players["b"], me.card(retrieval), who="a", card_i=retrieval)
    assert fire in me.hand
    assert dce in me.discard
