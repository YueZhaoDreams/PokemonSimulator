"""Set M plays a Stadium that raises the Bench only when it adds Babies. Printed text wins."""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from random import Random

import pytest

from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import Card, standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck, fallback_named

SKY_FIELD = (
    "Each player can have 8 Pokémon on his or her Bench. "
    "(When this card leaves play, each player discards Benched Pokémon until he or she has 5 Pokémon "
    "on the Bench. The owner of this card discards first.)"
)


def _game(a_names: list[str], b_names: list[str]) -> Game:
    def pad(names: list[str]) -> list[str]:
        out = list(names)
        while len(out) < 40:
            out.append("Nest Ball")
        return out

    return Game(
        build_fallback_deck(pad(a_names)),
        build_fallback_deck(pad(b_names)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("thrifty"),
        Random(1),
    )


def _take(player, name: str, n: int) -> list[int]:
    found: list[int] = []
    for zone in (player.deck, player.hand, player.discard, player.prizes):
        for card_i in list(zone):
            if player.card(card_i).name == name and card_i not in found:
                zone.remove(card_i)
                found.append(card_i)
                if len(found) == n:
                    return found
    raise AssertionError(f"{n} {name} not found")


def _board(game: Game, bench_babies: int, hand: list[tuple[str, int]]):
    """Mew ex Active, Igglybuff on the Bench, and exactly this hand."""
    me = game.players["a"]
    for zone in (me.hand, me.discard, me.prizes):
        me.deck.extend(zone)
        zone.clear()
    for mon in me.in_play():
        me.deck.extend([mon.card_i, *mon.energy])
    me.active = None
    me.bench = []
    me.deck = sorted(set(me.deck))
    me.active = Pokemon(card_i=_take(me, "Mew ex", 1)[0], played_turn=0)
    for card_i in _take(me, "Igglybuff", bench_babies):
        me.bench.append(Pokemon(card_i=card_i, played_turn=0))
    for name, count in hand:
        me.hand.extend(_take(me, name, count))
    return me, game.players["b"]


def _deck_names() -> list[str]:
    return ["Mew ex", "Sky Field", "Battle Cage", "Buddy-Buddy Poffin"] + ["Igglybuff"] * 12


def test_sky_field_is_held_until_waiting_babies_outnumber_the_open_slots():
    card = fallback_named("Sky Field")
    assert card.text == SKY_FIELD
    game = _game(_deck_names(), ["Igglybuff"] * 8)

    me, _foe = _board(game, bench_babies=5, hand=[("Sky Field", 1)])
    assert game._mew_bench_raise_gain(me, card) == 0
    assert game._pick_trainer(me) is None

    me, _foe = _board(game, bench_babies=3, hand=[("Sky Field", 1), ("Igglybuff", 2)])
    assert game._mew_bench_raise_gain(me, card) == 0

    me, _foe = _board(game, bench_babies=5, hand=[("Sky Field", 1), ("Igglybuff", 2)])
    assert game._mew_bench_raise_gain(me, card) == 2
    picked = game._pick_trainer(me)
    assert picked is not None and me.card(picked).name == "Sky Field"


def test_gain_is_capped_by_the_printed_bench_size_not_a_fixed_eight():
    game = _game(_deck_names(), ["Igglybuff"] * 8)
    me, _foe = _board(game, bench_babies=5, hand=[("Sky Field", 1), ("Igglybuff", 4)])
    sky = fallback_named("Sky Field")
    assert game._mew_bench_raise_gain(me, sky) == 3
    narrower = Card(
        catalog_id="sky-alt",
        name="Wide Bench",
        category="Trainer",
        trainer_kind="stadium",
        text=SKY_FIELD.replace("have 8", "have 7").replace("has 5", "has 4"),
        retreat=0,
    )
    assert parse_ability_effects(narrower.text)[0]["limit"] == 7
    assert game._mew_bench_raise_gain(me, narrower) == 2


def test_held_poffin_counts_as_two_waiting_babies():
    game = _game(_deck_names(), ["Igglybuff"] * 8)
    me, _foe = _board(game, bench_babies=5, hand=[("Sky Field", 1), ("Buddy-Buddy Poffin", 1)])
    assert game._mew_babies_waiting(me) == 2
    assert game._mew_bench_raise_gain(me, fallback_named("Sky Field")) == 2


def test_playing_sky_field_benches_the_waiting_babies_in_the_same_turn():
    game = _game(_deck_names(), ["Igglybuff"] * 8)
    me, foe = _board(game, bench_babies=5, hand=[("Sky Field", 1), ("Igglybuff", 2)])
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Sky Field"
    assert game._bench_limit(me) == 8
    assert len(me.bench) == 7
    assert not any(card.name == "Igglybuff" for card in (me.card(i) for i in me.hand))


def test_battle_cage_does_not_replace_sky_field_while_the_bench_is_past_the_printed_size():
    game = _game(_deck_names(), ["Igglybuff"] * 8)
    me, foe = _board(game, bench_babies=7, hand=[("Battle Cage", 1)])
    game._set_stadium(fallback_named("Sky Field"), owner=me)
    assert game._mew_keep_bench_raise(me) is True
    assert game._pick_trainer(me) is None

    me, foe = _board(game, bench_babies=5, hand=[("Battle Cage", 1)])
    assert game._mew_keep_bench_raise(me) is False
    picked = game._pick_trainer(me)
    assert picked is not None and me.card(picked).name == "Battle Cage"


def test_a_held_sky_field_does_not_change_a_list_without_one():
    game = _game(["Mew ex", "Battle Cage"] + ["Igglybuff"] * 12, ["Igglybuff"] * 8)
    me, foe = _board(game, bench_babies=5, hand=[("Battle Cage", 1)])
    assert game._bench_raise_effect(game.stadium_effects) is None
    assert game._mew_keep_bench_raise(me) is False
    picked = game._pick_trainer(me)
    assert picked is not None and me.card(picked).name == "Battle Cage"


def _load_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_m_sky_field.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_lab_swap_keeps_sixty_cards_and_limits_copies():
    lab = _load_lab()
    names = list(SET_M60_NAMES)
    with_sky = lab.swap_one(names, "Night Stretcher", "Sky Field")
    assert len(with_sky) == 60
    assert with_sky.count("Sky Field") == 1
    assert with_sky.count("Night Stretcher") == names.count("Night Stretcher") - 1
    with pytest.raises(ValueError):
        lab.swap_one(with_sky, "Arven", "Sky Field")
    four = names
    for cut in ("Boss's Orders", "Bravery Charm", "Counter Catcher", "Ultra Ball"):
        four = lab.swap_one(four, cut, "Budew")
    assert four.count("Budew") == 4
    with pytest.raises(ValueError):
        lab.swap_one(four, "Arven", "Budew")


def test_sky_field_report_path_is_legal_and_starts_from_the_locked_list():
    lab = _load_lab()
    blob = json.loads((Path(__file__).resolve().parents[1] / "data/lab/set-m-sky-field.json").read_text())
    rep = blob["report"]
    assert rep["done"] is True
    assert rep["seed"] == 20261007
    assert rep["games"] == 1000
    assert rep["list_start"] == rep["array"][0]["list"]
    assert rep["list_start"].count("Team Rocket's Petrel") == 0
    assert list(rep["foes"]) == [key for key, *_ in lab.FOES]
    assert abs(sum(rep["weights"].values()) - 1.0) < 1e-9
    rules = standard_60_rules()
    array = rep["array"]
    assert [row["label"] for row in array] == ["Set M", "Sky Field", "Budew 1", "Budew 2", "Budew 3", "Budew 4"]
    previous = Counter(rep["list_start"])
    for row in array[1:]:
        names = row["list"]
        assert len(names) == 60
        assert copy_violations(build_fallback_deck(names), rules) == []
        now = Counter(names)
        gained = now - previous
        lost = previous - now
        assert sum(gained.values()) == 1 and sum(lost.values()) == 1
        assert list(lost) == [row["cut"]]
        assert list(gained) == ["Sky Field" if row["label"] == "Sky Field" else "Budew"]
        previous = now
    assert array[-1]["list"].count("Sky Field") == 1
    assert array[-1]["list"].count("Budew") == 4
    assert rep["best_index"] == max(range(len(array)), key=lambda i: (array[i]["weighted"], -i))
