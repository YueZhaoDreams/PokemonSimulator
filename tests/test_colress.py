"""Plasma Storm Colress draws for each Benched Pokémon, then the hand is shuffled back.

Professor's Research discards the hand and draws 7. Colress does not discard those cards.
The draw count is the benches in play, both players, which Sky Field can raise to 8 each.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from pathlib import Path
from random import Random

import pytest

from app.engine.effects import parse_discard_hand_draw, parse_trainer_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck, fallback_named

COLRESS = (
    "Shuffle your hand into your deck. Then, draw a number of cards equal to the number of "
    "Benched Pokémon (both yours and your opponent\u2019s)."
)

POOL = (
    ["Mew ex", "Igglybuff", "Mime Jr.", "Budew", "Manaphy"] * 4
    + ["Colress", "Professor's Research", "Iono", "Team Rocket's Petrel", "Nest Ball"] * 4
    + ["Night Stretcher", "Crushing Hammer"]
    + ["Nest Ball"] * 20
)


def test_printed_sentence_counts_every_benched_pokemon():
    card = fallback_named("Colress")
    assert card.text == COLRESS
    assert card.is_supporter
    assert parse_trainer_effects(card.text) == [{"kind": "shuffle_hand_draw_per_bench", "whose": "both"}]
    assert parse_discard_hand_draw(fallback_named("Professor's Research").text) == 7
    opponent_only = (
        "Shuffle your hand into your deck. Then, draw a number of cards equal to the number of "
        "Benched Pokémon (your opponent's)."
    )
    assert parse_trainer_effects(opponent_only) == [{"kind": "shuffle_hand_draw_per_bench", "whose": "opponent"}]
    youngster = parse_trainer_effects("Shuffle your hand into your deck and draw 5 cards.")
    assert all(effect.get("kind") != "shuffle_hand_draw_per_bench" for effect in youngster)
    research = parse_trainer_effects("Discard your hand and draw 7 cards.")
    assert all(effect.get("kind") != "shuffle_hand_draw_per_bench" for effect in research)


def _game() -> Game:
    return Game(
        build_fallback_deck(list(POOL)),
        build_fallback_deck(list(POOL)),
        standard_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict("mew_baby"),
        Random(1),
    )


def _gather(player) -> None:
    for zone in (player.hand, player.discard, player.prizes):
        player.deck.extend(zone)
        zone.clear()
    for mon in player.in_play():
        player.deck.append(mon.card_i)
        player.deck.extend(mon.energy)
        if mon.tool is not None:
            player.deck.append(mon.tool)
    player.active = None
    player.bench = []
    player.deck = list(dict.fromkeys(player.deck))
    player.supporter_used = False


def _take(player, name: str) -> int:
    for card_i in list(player.deck):
        if player.card(card_i).name == name:
            player.deck.remove(card_i)
            return card_i
    raise AssertionError(name)


def _bench(player, names: list[str]) -> None:
    player.bench = [Pokemon(card_i=_take(player, name), played_turn=0) for name in names]


def _ready(game: Game, own: int, foe_n: int, hand: list[str]) -> tuple[object, object]:
    me = game.players["a"]
    foe = game.players["b"]
    _gather(me)
    _gather(foe)
    me.active = Pokemon(card_i=_take(me, "Mew ex"), played_turn=0)
    foe.active = Pokemon(card_i=_take(foe, "Mew ex"), played_turn=0)
    own_names = (["Igglybuff"] * 4 + ["Budew"] * 4 + ["Mime Jr."] * 4)[:own]
    foe_names = (["Igglybuff"] * 4 + ["Budew"] * 4 + ["Mime Jr."] * 4)[:foe_n]
    _bench(me, own_names)
    _bench(foe, foe_names)
    me.hand = [_take(me, name) for name in hand]
    return me, foe


def test_full_sky_field_benches_draw_sixteen_and_keep_the_hand():
    game = _game()
    me, foe = _ready(game, 8, 8, ["Colress", "Night Stretcher", "Crushing Hammer"])
    game._play_trainers(me, foe, "a")
    hand = [me.card(i).name for i in me.hand]
    discard = [me.card(i).name for i in me.discard]
    assert len(hand) == 16
    assert discard == ["Colress"]
    assert "Night Stretcher" not in discard
    assert "Crushing Hammer" not in discard
    assert game.events["shuffle_hand_draw_per_bench_a"] == 1
    assert game.events["colress_drawn_a"] == 16


def test_small_bench_plays_research_and_a_wide_bench_plays_colress():
    game = _game()
    me, foe = _ready(game, 1, 1, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Professor's Research"

    game = _game()
    me, foe = _ready(game, 4, 4, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert picked is not None
    assert me.card(picked).name == "Colress"


def test_one_or_two_short_of_research_only_when_the_hand_would_be_discarded():
    game = _game()
    me, foe = _ready(game, 3, 3, ["Colress", "Professor's Research", "Nest Ball", "Nest Ball", "Nest Ball"])
    picked = game._pick_trainer(me)
    assert me.card(picked).name == "Colress"

    game = _game()
    me, foe = _ready(game, 3, 3, ["Colress", "Professor's Research"])
    picked = game._pick_trainer(me)
    assert me.card(picked).name == "Professor's Research"


def test_petrel_fetches_colress_once_the_benches_reach_research():
    game = _game()
    me, foe = _ready(game, 4, 4, ["Team Rocket's Petrel"])
    me.deck = [_take(me, name) for name in ("Colress", "Iono", "Professor's Research")]
    assert game._mew_petrel_collapse(me, foe)[1] == "colress"

    game = _game()
    me, foe = _ready(game, 1, 1, ["Team Rocket's Petrel"])
    me.deck = [_take(me, name) for name in ("Colress", "Iono", "Professor's Research")]
    assert game._mew_petrel_collapse(me, foe)[1] == "iono"


def _colress_lab():
    path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set_m_colress.py"
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_colress_report_keeps_three_on_the_selection_seed_and_leaves_set_m():
    module = _colress_lab()
    report_path = Path(__file__).resolve().parents[1] / "data" / "lab" / "set-m-colress.json"
    report = json.loads(report_path.read_text())["report"]
    assert report["done"] is True
    assert report["copies"] == 3
    assert [row["cut"] for row in report["array"][1:]] == [
        "Crushing Hammer",
        "Sky Field",
        "Bravery Charm",
    ]
    start = Counter(report["list_start"])
    assert start["Elekid"] == 0
    assert start["Battle Cage"] == 4
    assert start["Colress"] == 0
    assert SET_M60_NAMES.count("Elekid") == 1
    assert SET_M60_NAMES.count("Battle Cage") == 3
    assert SET_M60_NAMES.count("Colress") == 0
    assert len(report["list"]) == 60
    assert report["list"].count("Colress") == 3
    assert copy_violations(build_fallback_deck(list(SET_M60_NAMES)), standard_60_rules()) == []
    assert copy_violations(build_fallback_deck(report["list"]), standard_60_rules()) == []
    weights = report["weights"]
    hold = {row["copies"]: row for row in report["holdout"]}
    _delta, _se, z_hold = module._pair(hold[3], hold[0], weights)
    assert z_hold == pytest.approx(1.26, abs=0.01)
    assert z_hold < 2
    _delta, _se, z_one = module._pair(hold[1], hold[0], weights)
    assert z_one == pytest.approx(-1.60, abs=0.01)
    text = report_path.with_suffix(".md").read_text()
    assert text == module.render_md(report)
    lines = text.splitlines()
    for index, line in enumerate(lines[:-1]):
        nxt = lines[index + 1]
        if (
            line.startswith("|")
            and nxt.startswith("|")
            and "-" in nxt
            and not nxt.replace("|", "").replace(":", "").replace("-", "").strip()
        ):
            header = [cell for cell in line.split("|") if cell.strip()]
            delim = [cell for cell in nxt.split("|") if cell.strip()]
            assert len(header) == len(delim), (line, nxt)
    assert "The selection seed kept 3." in text
    assert "That path cuts Crushing Hammer, then Sky Field, then Bravery Charm." in text
    assert "Professor's Research is rank 13 at 91.5%" in text
    assert "Iono is rank 15 at 91.2%" in text
    assert "No holdout count is 2 standard errors above zero copies." in text
    assert "3 copies against zero is +0.74% (1.26 standard errors)." in text
    assert "1 copy is -1.00% (-1.60 standard errors), below the starting 60." in text
    assert "`SET_M60_NAMES` stays the starting 60." in text
    assert "2 against 1 is +1.34% (2.17 standard errors)" in text
    assert "3 against 2 is +0.40% (0.68 standard errors)" in text
    assert "3 against 1 is +1.74% (2.86 standard errors)" in text
    assert "2 and 3 against 1 clear 2 standard errors." in text
    assert "locked as `SET_M60_NAMES`" not in text
