"""Chris Brewer Lucario Hariyama: printed text and the fast Mega line."""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_ability_effects, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import S60_SEED_IDS, default_rule_presets_for, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed import load_seed_deck
from app.seed_data import SET_L60_NAMES, SET_T60_NAMES, build_fallback_deck, fallback_named


def test_brewer_list_is_60_and_seeded():
    assert len(SET_L60_NAMES) == 60
    assert SET_L60_NAMES.count("Mega Lucario ex") == 3
    assert SET_L60_NAMES.count("Fighting Gong") == 4
    assert SET_L60_NAMES.count("Premium Power Pro") == 4
    assert SET_L60_NAMES.count("Fighting Energy") == 11
    rules = standard_60_rules()
    assert copy_violations(build_fallback_deck(list(SET_L60_NAMES)), rules) == []
    deck = load_seed_deck("lucario")
    assert deck["id"] == "seed-l60"
    assert load_seed_deck("brewer")["id"] == "seed-l60"
    assert load_seed_deck("20")["id"] == "seed-l60"
    assert default_rule_presets_for("seed-l60") == ["s60"]
    assert "seed-l60" in S60_SEED_IDS
    assert len(deck["cards"]) == 60


def test_printed_lucario_sentences():
    lucario = fallback_named("Mega Lucario ex")
    jab = lucario.attacks[0]
    assert jab.name == "Aura Jab"
    assert any(
        e.get("kind") == "attach_typed_energy_from_discard" and e.get("count") == 3 and e.get("energy_type") == "Fighting"
        for e in jab.effects
    )
    assert not any(e.get("kind") == "transfer_charge" for e in jab.effects)
    brave = lucario.attacks[1]
    assert any(e.get("kind") == "disable_self_attack_next_turn" for e in brave.effects)

    beam = fallback_named("Solrock").attacks[0]
    assert any(e.get("kind") == "require_named_on_bench" and e.get("name") == "lunatone" for e in beam.effects)
    assert any(e.get("kind") == "ignore_wr" for e in beam.effects)
    assert not any(e.get("kind") == "coin_whiff" for e in beam.effects)

    cycle = parse_ability_effects(fallback_named("Lunatone").abilities[0].text)
    assert any(e.get("kind") == "lunar_cycle" and e.get("draw") == 3 for e in cycle)

    hari = fallback_named("Hariyama")
    assert any(
        e.get("kind") == "force_opponent_active" and e.get("trigger") == "on_evolve"
        for e in parse_ability_effects(hari.abilities[0].text)
    )
    assert any(e.get("kind") == "recoil" and e.get("amount") == 70 for e in hari.attacks[0].effects)

    assert any(
        e.get("kind") == "fighting_damage_this_turn" and e.get("amount") == 30
        for e in parse_trainer_effects(fallback_named("Premium Power Pro").text)
    )
    assert any(e.get("kind") == "search_fighting_basic" for e in parse_trainer_effects(fallback_named("Fighting Gong").text))
    assert any(
        e.get("kind") == "stage2_hp" and e.get("delta") == -30
        for e in parse_ability_effects(fallback_named("Gravity Mountain").text)
    )
    balloon = (fallback_named("Air Balloon").text or "").lower()
    assert balloon.count("[c]") == 2


def _game() -> Game:
    return Game(
        build_fallback_deck(list(SET_L60_NAMES)),
        build_fallback_deck(list(SET_T60_NAMES)),
        standard_60_rules(),
        StrategySpec.from_dict("aura"),
        StrategySpec.from_dict("phantom"),
        Random(1),
    )


def _reclaim(player) -> None:
    if player.active:
        player.deck.append(player.active.card_i)
        player.active = None
    for mon in list(player.bench):
        player.deck.append(mon.card_i)
    player.bench.clear()


def _pull(player, name: str) -> int:
    used = set()
    if player.active:
        used.add(player.active.card_i)
    used.update(m.card_i for m in player.bench)
    for zone in (player.deck, player.hand, player.discard, player.prizes):
        for i in list(zone):
            if i in used:
                continue
            if player.card(i).name == name:
                zone.remove(i)
                return i
    raise AssertionError(name)


def test_mega_lucario_evolves_the_turn_riolu_is_played_and_aura_jab_loads_bench():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    _reclaim(foe)

    riolu = _pull(me, "Riolu")
    mega = _pull(me, "Mega Lucario ex")
    bench_riolu = _pull(me, "Riolu")
    energies = [_pull(me, "Fighting Energy") for _ in range(4)]
    drag = _pull(foe, "Dragapult ex")

    me.active = Pokemon(card_i=riolu, played_turn=game.turn)
    me.hand.append(mega)
    me.bench.append(Pokemon(card_i=bench_riolu, played_turn=0))
    game._evolve(me, foe, "a")
    assert me.card(me.active.card_i).name == "Mega Lucario ex"

    me.active.energy.append(energies[0])
    me.discard.extend(energies[1:])
    foe.active = Pokemon(card_i=drag, played_turn=0)
    foe.bench.clear()
    game._attack(me, foe, "a")
    assert len(me.bench[0].energy) == 3
    assert game.events.get("aura_jab_attach") == 3


def test_cosmic_beam_needs_lunatone_and_gravity_cuts_stage2():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    _reclaim(me)
    _reclaim(foe)
    sol = _pull(me, "Solrock")
    luna = _pull(me, "Lunatone")
    energy = _pull(me, "Fighting Energy")
    drag = _pull(foe, "Dragapult ex")
    me.active = Pokemon(card_i=sol, played_turn=0, energy=[energy])
    me.bench.clear()
    foe.active = Pokemon(card_i=drag, played_turn=0)
    atk = me.card(sol).attacks[0]
    assert game._raw_attack_damage(me, foe, me.active, atk) == 0
    me.bench.append(Pokemon(card_i=luna, played_turn=0))
    assert game._raw_attack_damage(me, foe, me.active, atk) == 70

    mountain = fallback_named("Gravity Mountain")
    game._set_stadium(mountain)
    assert game._max_hp(foe, foe.active) == 290
    me.fighting_boost = 30
    lucario = fallback_named("Mega Lucario ex")
    brave = lucario.attacks[1]
    # 270 + 30 Premium Power Pro, before weakness. Dragapult is Dragon, no Fighting weakness.
    me.active = Pokemon(card_i=_pull(me, "Mega Lucario ex"), played_turn=0)
    assert game._raw_attack_damage(me, foe, me.active, brave) == 300
