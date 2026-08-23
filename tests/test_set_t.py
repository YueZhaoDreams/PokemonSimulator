from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, play_game
from app.engine.models import default_family_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_D_NAMES, SET_T_NAMES, build_fallback_deck, fallback_named


def test_set_t_is_30_and_two_of():
    assert len(SET_T_NAMES) == 30
    t = build_fallback_deck(list(SET_T_NAMES))
    names = [c.name for c in t]
    counts = {n: names.count(n) for n in set(names)}
    for name, n in counts.items():
        if name.endswith("Energy") and "Double" not in name:
            continue
        assert n <= 2, name
    assert names.count("Dreepy") == 2
    assert names.count("Dragapult ex") == 2
    drap = next(c for c in t if c.name == "Dragapult ex")
    dive = next(a for a in drap.attacks if a.name == "Phantom Dive")
    assert dive.damage == 200
    assert dive.cost == ["Fire", "Psychic"]
    assert "Put 6 damage counters on your opponent's Benched Pokémon in any way you like." in dive.text
    recon = fallback_named("Drakloak")
    abi = next(a for a in recon.abilities if a.name == "Recon Directive")
    effects = parse_ability_effects(abi.text)
    assert effects[0]["kind"] == "look_top_put_hand"
    assert effects[0]["look"] == 2


def test_phantom_dive_parses_bench_counters():
    effects = parse_effects(
        "Put 6 damage counters on your opponent's Benched Pokémon in any way you like."
    )
    assert {"kind": "bench_damage_counters", "counters": 6} in effects


def test_cruel_arrow_parses_accented_pokemon():
    effects = parse_effects(
        "This attack does 100 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)"
    )
    assert {"kind": "damage_one_pokemon", "amount": 100} in effects


def test_itchy_pollen_parses_item_lock():
    effects = parse_effects(
        "During your opponent's next turn, they can't play any Item cards from their hand."
    )
    assert {"kind": "lock_items"} in effects


def test_recon_uses_printed_look_not_hardcoded():
    t = build_fallback_deck(list(SET_T_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    game = Game(t, d, default_family_rules(), StrategySpec.from_dict("phantom"), StrategySpec.from_dict("demolish"), Random(1))
    me = game.players["a"]
    from app.engine.game import Pokemon

    drak_i = next(i for i, c in enumerate(me.cards) if c.name == "Drakloak")
    me.active = Pokemon(card_i=drak_i, played_turn=0)
    candy = next(i for i, c in enumerate(me.cards) if c.name == "Rare Candy")
    me.deck = [i for i in me.deck if i != candy] + [candy]
    game._use_passive_abilities(me, "a")
    assert candy in me.hand
    assert game.events.get("recon_directive")


def test_phantom_vs_demolish_completes():
    t = build_fallback_deck(list(SET_T_NAMES))
    d = build_fallback_deck(list(SET_D_NAMES))
    result = play_game(
        t,
        d,
        default_family_rules(),
        StrategySpec.from_dict("phantom"),
        StrategySpec.from_dict("demolish"),
        Random(3),
        trace=True,
    )
    assert result.winner in {"a", "b", "tie"}
    assert result.turns >= 1
