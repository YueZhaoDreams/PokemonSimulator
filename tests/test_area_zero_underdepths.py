"""Area Zero Underdepths and Terapagos ex, from the printed sentences."""

from __future__ import annotations

from random import Random

from app.engine.effects import parse_ability_effects, parse_effects
from app.engine.game import Game, Pokemon
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

AREA_ZERO = (
    "Each player who has any Tera Pokémon in play can have up to 8 Pokémon on their Bench. "
    "If a player no longer has any Tera Pokémon in play, that player discards Pokémon from their Bench until they have 5. "
    "When this card leaves play, both players discard Pokémon from their Bench until they have 5, "
    "and the player who played this card discards first."
)
TERA_RULE = (
    "As long as this Pokémon is on your Bench, prevent all damage done to this Pokémon by attacks "
    "(both yours and your opponent's)."
)
BEATDOWN = (
    "If you go second, you can't use this attack during your first turn. "
    "This attack does 30 damage for each of your Benched Pokémon."
)


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 40:
        names.append("Nest Ball")
    return names


def _game(a_names: list[str], b_names: list[str] | None = None) -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names or ["Igglybuff"])),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
        trace=True,
        first="a",
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _drop(player, used: set[int]) -> None:
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        zone[:] = [i for i in zone if i not in used]


def _seat(player, active: int, bench: list[int], hand: list[int] | None = None) -> None:
    hand = list(hand or [])
    used = {active, *bench, *hand}
    _drop(player, used)
    player.active = Pokemon(card_i=active, played_turn=0)
    player.bench = [Pokemon(card_i=i, played_turn=0) for i in bench]
    player.hand = hand
    player.supporter_used = False
    player.energy_attached = False


def _kind(effects: list[dict], kind: str) -> dict:
    found = [eff for eff in effects if eff.get("kind") == kind]
    assert len(found) == 1, effects
    return found[0]


def test_area_zero_and_terapagos_parse_the_printed_sentences():
    stadium = fallback_named("Area Zero Underdepths")
    assert stadium.text == AREA_ZERO
    area = _kind(parse_ability_effects(stadium.text), "stadium_bench_limit")
    assert area["raises"] is True
    assert area["require_tera"] is True
    assert area["limit"] == 8
    assert area["lose_tera_limit"] == 5
    assert area["leave_limit"] == 5
    assert area["owner_discards_first"] is True
    widened = stadium.text.replace("up to 8", "up to 9").replace("have 5", "have 4")
    parsed = _kind(parse_ability_effects(widened), "stadium_bench_limit")
    assert (parsed["limit"], parsed["lose_tera_limit"], parsed["leave_limit"]) == (9, 4, 4)

    tera = fallback_named("Terapagos ex")
    rule = _kind(parse_ability_effects(tera.abilities[0].text), "tera")
    assert rule["kind"] == "tera"
    assert tera.abilities[0].text == TERA_RULE
    assert any(
        eff.get("kind") == "prevent_attack_damage_while_benched"
        for eff in parse_ability_effects(tera.abilities[0].text)
    )
    beatdown = next(atk for atk in tera.attacks if atk.name == "Unified Beatdown")
    assert beatdown.text == BEATDOWN
    effects = parse_effects(beatdown.text, "30×")
    assert _kind(effects, "benched_pokemon_times")["per"] == 30
    assert any(eff.get("kind") == "no_attack_second_first_turn" for eff in effects)
    assert "times" not in {eff.get("kind") for eff in effects}

    bouncy = fallback_named("Igglybuff").attacks[0]
    baby = {eff.get("kind") for eff in parse_effects(bouncy.text, "0")}
    assert "benched_30hp_pokemon_times" in baby
    assert "benched_pokemon_times" not in baby


def test_opening_can_hold_terapagos_before_the_opponent_exists():
    names = ["Mew ex", "Terapagos ex", "Area Zero Underdepths"] + ["Igglybuff"] * 4 + ["Spiky Energy"] * 2
    for seed in range(40):
        Game(
            build_fallback_deck(_pad(names)),
            build_fallback_deck(_pad(["Igglybuff"])),
            standard_60_rules(),
            StrategySpec.from_dict("mew_baby"),
            StrategySpec.from_dict("mew_baby"),
            Random(seed),
            first="a",
        )


def test_area_zero_limit_is_per_player_and_needs_a_tera():
    game = _game(["Terapagos ex"] + ["Igglybuff"] * 8, ["Igglybuff"] * 8)
    owner = game.players["a"]
    other = game.players["b"]
    game._set_stadium(fallback_named("Area Zero Underdepths"), owner=owner)
    assert game._bench_limit() == 5
    assert game._bench_limit(other) == 5
    owner_ids = _idxs(owner, "Igglybuff")
    tera = _idxs(owner, "Terapagos ex")[0]
    _seat(owner, owner_ids[0], [tera] + owner_ids[1:8])
    other_ids = _idxs(other, "Igglybuff")
    _seat(other, other_ids[0], other_ids[1:6])
    assert game._bench_limit(owner) == 8
    assert game._bench_limit(other) == 5
    assert len(owner.bench) == 8
    assert len(other.bench) == 5


def test_losing_the_tera_or_the_stadium_discards_down_to_five():
    game = _game(["Mew ex", "Terapagos ex"] + ["Igglybuff"] * 8, ["Igglybuff"] * 2)
    owner = game.players["a"]
    game._set_stadium(fallback_named("Area Zero Underdepths"), owner=owner)
    iggly = _idxs(owner, "Igglybuff")
    tera = _idxs(owner, "Terapagos ex")[0]
    mew = _idxs(owner, "Mew ex")[0]
    _seat(owner, mew, [tera] + iggly[:7])
    anchor = next(mon for mon in owner.bench if owner.card(mon.card_i).name == "Terapagos ex")
    anchor.damage = 230
    assert game._check_ko(owner, game.players["b"], "a") is False
    assert len(owner.bench) == 5
    assert all(owner.card(mon.card_i).name == "Igglybuff" for mon in owner.bench)

    kept = _game(["Mew ex", "Terapagos ex"] + ["Igglybuff"] * 8, ["Igglybuff"])
    kept._set_stadium(fallback_named("Area Zero Underdepths"), owner=kept.players["a"])
    owner = kept.players["a"]
    iggly = _idxs(owner, "Igglybuff")
    _seat(owner, _idxs(owner, "Mew ex")[0], [_idxs(owner, "Terapagos ex")[0]] + iggly[:7])
    kept._clear_stadium()
    assert len(owner.bench) == 5
    assert all(owner.card(mon.card_i).name == "Igglybuff" for mon in owner.bench)
    assert "Terapagos ex" in {owner.card(i).name for i in owner.discard}

    both = _game(["Igglybuff"] * 9, ["Igglybuff"] * 9)
    both._set_stadium(fallback_named("Area Zero Underdepths"), owner=both.players["b"])
    for who in ("a", "b"):
        player = both.players[who]
        ids = _idxs(player, "Igglybuff")
        _seat(player, ids[0], ids[1:9])
    assert len(both.players["a"].bench) == 8
    assert len(both.players["b"].bench) == 8
    both.trace.clear()
    both._clear_stadium()
    assert len(both.players["a"].bench) == 5
    assert len(both.players["b"].bench) == 5
    discards = [line for line in both.trace if "discards benched" in line]
    assert discards[0].startswith("B ")
    assert any(line.startswith("A ") for line in discards)


def test_beatdown_counts_mew_and_bouncy_does_not():
    names = ["Mew ex", "Terapagos ex"] + ["Igglybuff"] * 8
    game = _game(names, ["Igglybuff"])
    me = game.players["a"]
    foe = game.players["b"]
    foe_active = _idxs(foe, "Igglybuff")[0]
    _seat(foe, foe_active, [])
    iggly = _idxs(me, "Igglybuff")
    mew = _idxs(me, "Mew ex")[0]
    tera = _idxs(me, "Terapagos ex")[0]

    _seat(me, tera, [mew] + iggly[:7])
    beatdown = next(atk for atk in me.card(me.active.card_i).attacks if atk.name == "Unified Beatdown")
    assert game._raw_attack_damage(me, foe, me.active, beatdown) == 240

    _seat(me, iggly[0], [mew, tera] + iggly[1:7])
    bouncy = me.card(me.active.card_i).attacks[0]
    assert game._raw_attack_damage(me, foe, me.active, bouncy) == 180

    _seat(me, mew, [tera] + iggly[:7])
    copied = game._attacks_for(me, me.active)
    bouncy = next(atk for atk in copied if atk.name == "Bouncy Circle")
    beatdown = next(atk for atk in copied if atk.name == "Unified Beatdown")
    assert game._raw_attack_damage(me, foe, me.active, bouncy) == 210
    assert game._raw_attack_damage(me, foe, me.active, beatdown) == 240


def test_going_second_cannot_use_beatdown_on_the_first_turn():
    game = _game(
        ["Mew ex"],
        ["Mew ex", "Terapagos ex", "Igglybuff"] + ["Spiky Energy"] * 2,
    )
    me = game.players["b"]
    foe = game.players["a"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    spikes = _idxs(me, "Spiky Energy")
    _seat(
        me,
        _idxs(me, "Mew ex")[0],
        [_idxs(me, "Terapagos ex")[0], _idxs(me, "Igglybuff")[0]],
    )
    me.active.energy = spikes
    game.first = "a"
    game.turn = 2
    game.current = "b"
    chosen = game._choose_attack(me, foe, game.strats["b"])
    assert chosen is not None
    assert chosen.name == "Bouncy Circle"
    game.turn = 4
    chosen = game._choose_attack(me, foe, game.strats["b"])
    assert chosen is not None
    assert chosen.name == "Unified Beatdown"


def test_benched_tera_takes_no_attack_damage_but_still_takes_counters():
    game = _game(["Mew ex", "Terapagos ex"], ["Igglybuff"])
    me = game.players["a"]
    tera_i = _idxs(me, "Terapagos ex")[0]
    mew_i = _idxs(me, "Mew ex")[0]
    _seat(me, mew_i, [tera_i])
    anchor = me.bench[0]
    game._add_attack_damage(me, anchor, 60)
    assert anchor.damage == 0
    game._bench_damage_counters(me, 2)
    assert anchor.damage == 20
    me.active, me.bench[0] = me.bench[0], me.active
    me.active.damage = 0
    game._add_attack_damage(me, me.active, 40)
    assert me.active.damage == 40


def test_mew_baby_plays_area_zero_for_the_burst_and_not_over_it():
    names = ["Mew ex", "Terapagos ex"] + ["Igglybuff"] * 5 + ["Area Zero Underdepths", "Battle Cage"] + ["Spiky Energy"] * 2
    game = _game(names, ["Igglybuff"])
    me = game.players["a"]
    foe = game.players["b"]
    _seat(foe, _idxs(foe, "Igglybuff")[0], [])
    iggly = _idxs(me, "Igglybuff")
    spikes = _idxs(me, "Spiky Energy")
    _seat(
        me,
        _idxs(me, "Mew ex")[0],
        iggly[:4],
        hand=[_idxs(me, "Terapagos ex")[0], _idxs(me, "Area Zero Underdepths")[0], _idxs(me, "Battle Cage")[0]],
    )
    me.active.energy = spikes
    game.turn = 6
    game._play_basics(me)
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Area Zero Underdepths"
    assert any(me.card(mon.card_i).name == "Terapagos ex" for mon in me.bench)
    assert "Battle Cage" not in {me.card(i).name for i in me.discard}
    assert len(me.bench) == 5


def test_full_bench_pennies_a_baby_then_plays_the_burst():
    names = (
        ["Mew ex", "Terapagos ex"]
        + ["Igglybuff"] * 5
        + ["Area Zero Underdepths", "Battle Cage", "Penny"]
        + ["Spiky Energy"] * 2
    )
    game = _game(names, ["Igglybuff"])
    me = game.players["a"]
    foe = game.players["b"]
    _seat(foe, _idxs(foe, "Igglybuff")[0], [])
    iggly = _idxs(me, "Igglybuff")
    _seat(
        me,
        _idxs(me, "Mew ex")[0],
        iggly[:5],
        hand=[
            _idxs(me, "Terapagos ex")[0],
            _idxs(me, "Area Zero Underdepths")[0],
            _idxs(me, "Battle Cage")[0],
            _idxs(me, "Penny")[0],
        ],
    )
    me.active.energy = _idxs(me, "Spiky Energy")
    game.turn = 6
    game._play_basics(me)
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Area Zero Underdepths"
    assert any(me.card(mon.card_i).name == "Terapagos ex" for mon in me.in_play())
    assert me.card(me.active.card_i).name == "Mew ex"
    assert "Penny" in {me.card(i).name for i in me.discard}
    assert "Battle Cage" not in {me.card(i).name for i in me.discard}
