"""Locked Kecleon list and the printed sentences that list uses."""

from random import Random

from app.engine.effects import (
    can_pay_energy,
    energy_provided,
    parse_ability_effects,
    parse_effects,
    parse_energy_effects,
    parse_trainer_effects,
)
from app.engine.game import ST_ASLEEP, Game, Pokemon
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
    me.deck = package + [
        i
        for i in range(len(me.cards))
        if i not in {kecleon, hoopa, *package} and me.card(i).name != "Jirachi-EX"
    ]
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
        _idx(me, "Energy Loto"),
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
    boss = _idx(me, "VS Seeker")
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


def test_skyliner_lets_a_stuck_basic_retreat_into_kecleon():
    """Printed Skyliner: Your Basic Pokémon in play have no Retreat Cost."""
    deck = build_fallback_deck(
        ["Kecleon", "Druddigon", "Latias ex", "Double Colorless Energy"] + ["Psychic Energy"] * 56
    )
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 59)
    game = Game(
        deck,
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(2),
    )
    me = game.players["a"]
    drud = _idx(me, "Druddigon")
    kec = _idx(me, "Kecleon")
    lat = _idx(me, "Latias ex")
    dce = _idx(me, "Double Colorless Energy")
    me.active = Pokemon(card_i=drud, played_turn=0)
    me.bench = [Pokemon(card_i=kec, energy=[dce], played_turn=0)]
    me.hand = []
    assert game._retreat_cost(me, me.active) == 2
    game._maybe_retreat(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Druddigon"

    me.bench.append(Pokemon(card_i=lat, played_turn=0))
    assert game._retreat_cost(me, me.active) == 0
    game._maybe_retreat(me, game.players["b"], "a")
    assert me.card(me.active.card_i).name == "Kecleon"


def test_promote_and_switch_choose_kecleon():
    deck = build_fallback_deck(
        ["Kecleon", "Druddigon", "Hoopa-EX", "Latias ex", "Double Colorless Energy"] + ["Psychic Energy"] * 55
    )
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 59)
    game = Game(
        deck,
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(3),
    )
    me = game.players["a"]
    me.active = Pokemon(card_i=_idx(me, "Hoopa-EX"), played_turn=0)
    me.bench = [
        Pokemon(card_i=_idx(me, "Druddigon"), played_turn=0),
        Pokemon(card_i=_idx(me, "Latias ex"), played_turn=0),
        Pokemon(card_i=_idx(me, "Kecleon"), energy=[_idx(me, "Double Colorless Energy")], played_turn=0),
    ]
    assert me.card(me.bench[game._promote_idx(me, "a")].card_i).name == "Kecleon"
    assert me.card(me.bench[game._switch_target_idx(me, "a")].card_i).name == "Kecleon"


def test_one_latias_ex_benches_and_does_not_open():
    deck = build_fallback_deck(
        ["Kecleon", "Latias ex", "Latias ex", "Druddigon", "Hoopa-EX"] + ["Psychic Energy"] * 55
    )
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 59)
    game = Game(
        deck,
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(4),
    )
    me = game.players["a"]
    kec = _idx(me, "Kecleon")
    lat = [_idx(me, "Latias ex"), _idx(me, "Latias ex", 1)]
    me.hand = [kec, *lat]
    me.deck = [i for i in range(len(me.cards)) if i not in set(me.hand)]
    me.active = None
    me.bench = []
    game._play_basics(me)
    assert me.card(me.active.card_i).name == "Kecleon"
    benched = [me.card(mon.card_i).name for mon in me.bench]
    assert benched.count("Latias ex") == 1
    spare = next(i for i in lat if i in me.hand)

    me.hand = []
    me.deck = [spare, _idx(me, "Druddigon")]
    game._bench_basic_from_deck(me, "a", source="nest ball")
    assert [me.card(mon.card_i).name for mon in me.bench].count("Latias ex") == 1
    assert me.card(me.bench[-1].card_i).name == "Druddigon"


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


STELLAR = (
    "When you play this Pokémon from your hand onto your Bench, you may search your deck "
    "for a Supporter card, reveal it, and put it into your hand. Shuffle your deck afterward."
)
HYPN = "Both this Pokémon and the Defending Pokémon are now Asleep."
PENNY = "Put 1 of your Basic Pokémon and all attached cards into your hand."
CATCHER = (
    "You can use this card only if you have more Prize cards remaining than your opponent.\n\n"
    "Switch in 1 of your opponent's Benched Pokémon to the Active Spot."
)


def test_jirachi_ex_prints_parse():
    card = fallback_named("Jirachi-EX")
    assert card.text == STELLAR or any(abi.text == STELLAR for abi in card.abilities)
    assert card.types == ["Metal"]
    assert card.hp == 90
    guidance = parse_ability_effects(STELLAR)
    assert guidance[0]["kind"] == "search_supporter_on_bench"
    strike = parse_effects(HYPN, "60")
    assert any(e.get("kind") == "status" and e.get("status") == "asleep" and e.get("target") != "self" for e in strike)
    assert any(e.get("kind") == "status" and e.get("status") == "asleep" and e.get("target") == "self" for e in strike)
    assert {"kind": "return_pokemon_to_hand", "basic_only": True, "attachments": "hand"} in parse_trainer_effects(PENNY)
    assert any(e.get("kind") == "force_opponent_active" for e in parse_trainer_effects(CATCHER))


def test_hoopa_searches_two_dual_types_then_jirachi():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    spare = _idx(me, "Jirachi-EX")
    package = [
        spare,
        _idx(me, "M Gardevoir-EX"),
        _idx(me, "M Steelix-EX"),
        _idx(me, "Volcanion-EX"),
        _idx(me, "M Latios-EX"),
    ]
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = []
    me.hand = [hoopa]
    me.deck = package + [i for i in range(len(me.cards)) if i not in {kecleon, hoopa, *package}]
    me.discard = []
    game._play_basics(me)
    found = {me.card(i).name for i in me.hand}
    assert any(me.card(mon.card_i).name == "Jirachi-EX" for mon in me.bench)
    assert "Jirachi-EX" not in found
    assert len({"M Gardevoir-EX", "M Steelix-EX", "Volcanion-EX", "M Latios-EX"} & found) == 2
    assert game.events.get("scoundrel_ring") == 3
    assert game.events.get("stellar_guidance") == 1


def test_penny_replays_hoopa_and_searches_again():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    penny = _idx(me, "Arven")
    me.cards[penny] = fallback_named("Penny")
    exes = [
        _idx(me, "M Gardevoir-EX"),
        _idx(me, "M Steelix-EX"),
        _idx(me, "Volcanion-EX"),
        _idx(me, "M Sceptile-EX"),
        _idx(me, "M Manectric-EX"),
        _idx(me, "M Latios-EX"),
    ]
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = []
    me.hand = [hoopa, penny]
    me.deck = exes + [i for i in range(len(me.cards)) if i not in {kecleon, hoopa, penny, *exes}]
    me.discard = []
    game._play_basics(me)
    assert game.events.get("scoundrel_ring") == 3
    assert any(me.card(mon.card_i).name == "Hoopa-EX" for mon in me.bench)
    game._play_trainers(me, game.players["b"], "a")
    assert hoopa in me.hand
    assert not any(me.card(mon.card_i).name == "Hoopa-EX" for mon in me.in_play())
    game._play_basics(me)
    assert game.events.get("scoundrel_ring") == 6
    assert any(me.card(mon.card_i).name == "Hoopa-EX" for mon in me.bench)


def test_jirachi_from_hand_searches_penny_for_the_board():
    deck = build_fallback_deck(
        ["Kecleon", "Hoopa-EX", "Jirachi-EX", "Penny", "Arven", "Double Colorless Energy"] + ["Psychic Energy"] * 54
    )
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 4 + ["Psychic Energy"] * 55)
    game = Game(
        deck,
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(3),
    )
    me = game.players["a"]
    foe_p = game.players["b"]
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    jirachi = _idx(me, "Jirachi-EX")
    penny = _idx(me, "Penny")
    arven = _idx(me, "Arven")
    ex = _idx(me, "Hoopa-EX")  # only one; deck still needs an EX for the penny target after Hoopa is out
    # A second EX so Penny's replay line is live while Jirachi chooses.
    spare = _idx(me, "Psychic Energy")
    me.cards[spare] = fallback_named("Volcanion-EX")
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = [Pokemon(card_i=hoopa, played_turn=0)]
    me.hand = [jirachi]
    me.deck = [penny, arven, spare]
    me.discard = []
    foe_p.active = Pokemon(card_i=_idx(foe_p, "Starly"), played_turn=0)
    game._play_basics(me)
    assert any(me.card(mon.card_i).name == "Jirachi-EX" for mon in me.bench)
    assert penny in me.hand
    assert game.events.get("stellar_guidance") == 1
    assert (me.active.status & ST_ASLEEP) == 0


def test_hypnostrike_sleeps_both_pokemon():
    deck = build_fallback_deck(["Jirachi-EX", "Metal Energy"] + ["Psychic Energy"] * 58)
    foe = build_fallback_deck(["Starly"] + ["Hop"] * 59)
    game = Game(
        deck,
        foe,
        standard_60_rules(),
        StrategySpec.from_dict("kecleon"),
        StrategySpec.from_dict("balanced"),
        Random(5),
    )
    me = game.players["a"]
    foe_p = game.players["b"]
    jirachi = _idx(me, "Jirachi-EX")
    energy = [_idx(me, "Metal Energy"), _idx(me, "Psychic Energy"), _idx(me, "Psychic Energy", 1)]
    me.active = Pokemon(card_i=jirachi, energy=energy, played_turn=0)
    me.hand = []
    me.bench = []
    foe_p.active = Pokemon(card_i=_idx(foe_p, "Starly"), played_turn=0)
    game._attack(me, foe_p, "a")
    assert me.active.status & ST_ASLEEP
    assert foe_p.active.status & ST_ASLEEP


PRISM = (
    "As long as this card is attached to a Pokémon, it provides {C} Energy.\n\n"
    "If this card is attached to a Basic Pokémon, this card provides every type of Energy "
    "but provides only 1 Energy at a time."
)


def test_prism_energy_is_every_type_on_a_basic():
    prism = fallback_named("Prism Energy")
    assert prism.text == PRISM
    spec = next(e for e in parse_energy_effects(prism.text) if e["kind"] == "provides_any_when")
    assert spec["count"] == 1
    assert spec["basic_only"] is True
    assert energy_provided(prism, host=fallback_named("Kecleon")) == ["Any"]
    assert energy_provided(prism, host=fallback_named("Druddigon")) == ["Any"]
    assert energy_provided(prism, host=fallback_named("Fezandipiti ex")) == ["Any"]
    assert energy_provided(prism, host=fallback_named("M Gardevoir-EX")) == ["Colorless"]
    assert can_pay_energy(["Any"], ["Fire"])
    assert can_pay_energy(["Any"], ["Water"])
    assert not can_pay_energy(["Colorless"], ["Fire"])


def test_teammates_can_find_prism_energy():
    game = _game()
    me = game.players["a"]
    me.hand = []
    prefer = game._kecleon_teammates_prefer(me)
    assert prefer.index("Double Colorless Energy") < prefer.index("Prism Energy")
    assert prefer.index("Prism Energy") < prefer.index("Latias ex")


def test_prism_attaches_to_the_basic_fighter_that_needs_the_type():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    druddigon = _idx(me, "Druddigon")
    dce = _idx(me, "Double Colorless Energy")
    fire = _idx(me, "Fire Energy")
    psychic = _idx(me, "Psychic Energy")
    me.cards[psychic] = fallback_named("Prism Energy")
    prism = psychic
    me.active = Pokemon(card_i=druddigon, played_turn=0)
    me.bench = [Pokemon(card_i=kecleon, energy=[dce], played_turn=0)]
    me.hand = [prism, fire]
    me.deck = [i for i in range(len(me.cards)) if i not in me.hand and i != kecleon and i != druddigon and i != dce]
    strat = StrategySpec.from_dict("kecleon")
    assert me.card(game._kecleon_energy_target(me).card_i).name == "Druddigon"
    assert game._choose_energy_card(me, me.active, strat) == fire

    me.hand = [prism, _idx(me, "Psychic Energy", 1)]
    assert game._choose_energy_card(me, me.active, strat) == prism
    game._attach_energy(me, "a")
    assert me.active.energy == [prism]
    assert energy_provided(me.card(prism), host=me.card(druddigon)) == ["Any"]
    assert game.events.get("prism_any_a") == 1
    shred = next(atk for atk in me.card(druddigon).attacks if atk.name == "Shred")
    assert can_pay_energy(game._energy_pool(me, me.active), shred.cost)

    unpaid = Pokemon(card_i=_idx(me, "Kecleon", 1), played_turn=0)
    me.active = unpaid
    me.bench = []
    me.energy_attached = False
    me.hand = [dce, prism]
    assert game._choose_energy_card(me, unpaid, strat) == dce


def test_second_counter_catcher_leaves_the_last_counter_gain():
    from data.lab.kecleon_greedy import _leave_last_counter_gain

    assert _leave_last_counter_gain("Counter Catcher", 2, "Counter Gain", 1)
    assert not _leave_last_counter_gain("Counter Catcher", 2, "Energy Loto", 3)
    assert not _leave_last_counter_gain("Counter Catcher", 1, "Counter Gain", 2)
    assert not _leave_last_counter_gain("Penny", 2, "Counter Gain", 1)


def test_penny_and_jirachi_stop_at_two_copies():
    from data.lab.kecleon_greedy import INCOMING, _copy_cap

    assert _copy_cap("Penny") == 2
    assert _copy_cap("Jirachi-EX") == 2
    assert _copy_cap("Counter Catcher") == 4
    assert _copy_cap("Prism Energy") == 4
    assert INCOMING[-2:] == ("Prism Energy", "Scoop Up Cyclone")
    assert _copy_cap("Scoop Up Cyclone") == 1


CYCLONE = (
    "You can't have more than 1 ACE SPEC card in your deck.\n\n"
    "Put 1 of your Pokémon and all attached cards into your hand."
)


def test_scoop_up_cyclone_sentence_returns_any_pokemon_with_attachments():
    card = fallback_named("Scoop Up Cyclone")
    assert card.catalog_id == "sv06-162"
    assert card.trainer_kind == "item"
    assert card.text == CYCLONE
    assert "ace spec" in [trait.lower() for trait in card.traits]
    assert parse_trainer_effects(CYCLONE) == [
        {"kind": "return_pokemon_to_hand", "attachments": "hand"}
    ]
    assert parse_trainer_effects(PENNY) == [
        {"kind": "return_pokemon_to_hand", "basic_only": True, "attachments": "hand"}
    ]
    plasma = "Put 1 of your Pokémon and all cards attached to it into your hand."
    assert all(effect.get("kind") != "return_pokemon_to_hand" for effect in parse_trainer_effects(plasma))


STELLAR = (
    "When you play this Pokémon from your hand onto your Bench, you may search your deck "
    "for a Supporter card, reveal it, and put it into your hand. Shuffle your deck afterward."
)


def test_scoop_up_cyclone_returns_hoopa_while_the_deck_has_another_ex():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    hoopa = _idx(me, "Hoopa-EX")
    mega = _idx(me, "M Gardevoir-EX")
    jirachi = _idx(me, "Jirachi-EX")
    cyclone = _idx(me, "Special Charge")
    me.cards[cyclone] = fallback_named("Scoop Up Cyclone")
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = [
        Pokemon(card_i=hoopa, played_turn=0),
        Pokemon(card_i=jirachi, played_turn=0),
        Pokemon(card_i=mega, played_turn=0, damage=40),
    ]
    me.hand = [cyclone]
    used = {kecleon, hoopa, mega, jirachi, cyclone}
    me.deck = [i for i in range(len(me.cards)) if i not in used]
    me.discard = []
    game._play_trainers(me, game.players["b"], "a")
    assert hoopa in me.hand
    assert cyclone in me.discard
    assert any(me.card(mon.card_i).name == "M Gardevoir-EX" for mon in me.in_play())
    assert any(me.card(mon.card_i).name == "Jirachi-EX" for mon in me.in_play())
    assert game.events.get("bounce_a:Scoop Up Cyclone") == 1


def test_scoop_up_cyclone_returns_jirachi_and_searches_a_supporter():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    jirachi = _idx(me, "Jirachi-EX")
    assert me.cards[jirachi].abilities[0].text == STELLAR
    mega = _idx(me, "M Gardevoir-EX")
    energy = _idx(me, "Psychic Energy")
    cyclone = _idx(me, "Special Charge")
    me.cards[cyclone] = fallback_named("Scoop Up Cyclone")
    me.active = Pokemon(card_i=kecleon, played_turn=0)
    me.bench = [
        Pokemon(card_i=jirachi, played_turn=0),
        Pokemon(card_i=mega, played_turn=0, damage=30, energy=[energy]),
    ]
    me.hand = [cyclone]
    used = {kecleon, jirachi, mega, energy, cyclone}
    me.deck = [i for i in range(len(me.cards)) if i not in used]
    me.discard = []
    assert any(me.card(i).is_supporter for i in me.deck)
    game._play_trainers(me, game.players["b"], "a")
    assert jirachi in me.hand
    gardevoir = next(mon for mon in me.in_play() if me.card(mon.card_i).name == "M Gardevoir-EX")
    assert energy in gardevoir.energy
    game._play_basics(me)
    assert any(me.card(mon.card_i).name == "Jirachi-EX" for mon in me.in_play())
    assert any(me.card(i).is_supporter for i in me.hand)
    assert game.events.get("stellar_guidance_a") == 1
    assert cyclone in me.discard


def test_scoop_up_cyclone_returns_a_damaged_mega_and_its_energy():
    game = _game()
    me = game.players["a"]
    kecleon = _idx(me, "Kecleon")
    mega = _idx(me, "M Gardevoir-EX")
    energy = _idx(me, "Psychic Energy")
    cyclone = _idx(me, "Special Charge")
    me.cards[cyclone] = fallback_named("Scoop Up Cyclone")
    me.active = Pokemon(card_i=kecleon, played_turn=0, damage=10)
    me.bench = [Pokemon(card_i=mega, played_turn=0, damage=30, energy=[energy])]
    me.hand = [cyclone]
    used = {kecleon, mega, energy, cyclone}
    me.deck = [i for i in range(len(me.cards)) if i not in used and me.card(i).name != "Hoopa-EX"]
    me.discard = []
    game._play_trainers(me, game.players["b"], "a")
    assert mega in me.hand
    assert energy in me.hand
    assert kecleon == me.active.card_i
    assert cyclone in me.discard
    assert game.events.get("bounce_a:Scoop Up Cyclone") == 1


def test_second_penny_stops_when_its_best_cut_is_below_one_penny():
    from data.lab.kecleon_greedy import _leave_negative_second_penny

    assert _leave_negative_second_penny("Penny", 2, -0.0032)
    assert not _leave_negative_second_penny("Penny", 2, 0.001)
    assert not _leave_negative_second_penny("Penny", 2, 0.0)
    assert not _leave_negative_second_penny("Penny", 1, -0.01)
    assert not _leave_negative_second_penny("Jirachi-EX", 2, -0.01)
