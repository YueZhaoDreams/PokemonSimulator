"""Black Market ◇, Team Up 134. The printed sentences are the effect.

Dark Market is that Stadium. One copy. A discard puts it in the Lost Zone.
A Darkness Pokémon with Darkness Energy attached gives one fewer Prize when an
opponent's attack Knocks it Out. An Item or Supporter cannot affect the Stadium.
"""

from random import Random

from app.engine.doll import tool_host, trainer_score
from app.engine.effects import parse_ability_effects
from app.engine.game import Game, Pokemon
from app.engine.legality import copy_violations
from app.engine.models import standard_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import fallback_named


def _deck() -> list:
    return (
        [fallback_named("cleffa hgss") for _ in range(8)]
        + [fallback_named("Sableye"), fallback_named("Sableye")]
        + [fallback_named("Black Market")]
        + [fallback_named("Life Dew")]
        + [fallback_named("Battle Cage")]
        + [fallback_named("Field Blower")]
        + [fallback_named("Dark Patch")]
        + [fallback_named("Darkness Energy") for _ in range(20)]
    )


def _game(strat_b: str = "balanced") -> Game:
    return Game(
        _deck(),
        _deck(),
        standard_60_rules(),
        StrategySpec.from_dict("doll"),
        StrategySpec.from_dict(strat_b),
        Random(1),
    )


def _idx(game: Game, who: str, name: str, used: set[int]) -> int:
    player = game.players[who]
    for i, card in enumerate(player.cards):
        if i in used or card.name != name:
            continue
        used.add(i)
        return i
    raise AssertionError(name)


def test_printed_black_market_sentences():
    card = fallback_named("Dark Market")
    assert card.name == "Black Market"
    assert card.trainer_kind == "stadium"
    assert card.catalog_id == "sm9-134"
    parsed = parse_ability_effects(card.text)
    assert "ko_to_lost_zone" not in [e["kind"] for e in parsed]
    prize = next(e for e in parsed if e["kind"] == "fewer_prizes_on_ko")
    assert prize == {
        "kind": "fewer_prizes_on_ko",
        "count": 1,
        "attack_only": True,
        "require_type": "Darkness",
        "require_energy": "Darkness",
        "both_players": True,
    }
    assert any(e["kind"] == "stadium_item_safe" for e in parsed)
    assert copy_violations([fallback_named("Black Market"), fallback_named("Black Market")]) == [
        {"name": "Black Market", "count": 2, "max": 1}
    ]
    assert copy_violations([fallback_named("Black Market")]) == []


def _prizes(game: Game, who: str, n: int = 4) -> None:
    player = game.players[who]
    used = set()
    for mon in player.in_play():
        used.add(mon.card_i)
        used.update(mon.energy)
    used.update(player.hand)
    used.update(player.discard)
    used.update(player.lost_zone)
    used.update(player.deck)
    player.prizes = [_idx(game, who, "Darkness Energy", used) for _ in range(n)]
    player.prizes_taken = 0


def test_prize_line_needs_darkness_pokemon_and_darkness_energy_from_an_attack():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    sable = _idx(game, "a", "Sableye", used)
    dark = _idx(game, "a", "Darkness Energy", used)
    cleffa = _idx(game, "a", "Cleffa", used)
    me.active = Pokemon(card_i=sable, energy=[dark])
    me.bench = []
    me.hand = []
    me.deck = []
    foe.active = Pokemon(card_i=_idx(game, "b", "Cleffa", set()))
    game._set_stadium(fallback_named("Black Market"), owner=me)
    _prizes(game, "b")

    game._add_attack_damage(me, me.active, 70)
    game._check_ko(me, foe, "a")
    assert foe.prizes_taken == 0
    assert game.events["market_prize_cut"] == 1

    game2 = _game()
    me2 = game2.players["a"]
    foe2 = game2.players["b"]
    used2: set[int] = set()
    bare = _idx(game2, "a", "Sableye", used2)
    me2.active = Pokemon(card_i=bare)
    foe2.active = Pokemon(card_i=_idx(game2, "b", "Cleffa", set()))
    game2._set_stadium(fallback_named("Black Market"), owner=me2)
    _prizes(game2, "b")
    game2._add_attack_damage(me2, me2.active, 70)
    game2._check_ko(me2, foe2, "a")
    assert foe2.prizes_taken == 1
    assert "market_prize_cut" not in game2.events

    game3 = _game()
    me3 = game3.players["a"]
    foe3 = game3.players["b"]
    used3: set[int] = set()
    face = _idx(game3, "a", "Cleffa", used3)
    fuel = _idx(game3, "a", "Darkness Energy", used3)
    me3.active = Pokemon(card_i=face, energy=[fuel])
    foe3.active = Pokemon(card_i=_idx(game3, "b", "Cleffa", set()))
    game3._set_stadium(fallback_named("Black Market"), owner=me3)
    _prizes(game3, "b")
    game3._add_attack_damage(me3, me3.active, 30)
    game3._check_ko(me3, foe3, "a")
    assert foe3.prizes_taken == 1

    game4 = _game()
    me4 = game4.players["a"]
    foe4 = game4.players["b"]
    used4: set[int] = set()
    quiet = _idx(game4, "a", "Sableye", used4)
    fuel4 = _idx(game4, "a", "Darkness Energy", used4)
    me4.active = Pokemon(card_i=quiet, energy=[fuel4])
    foe4.active = Pokemon(card_i=_idx(game4, "b", "Cleffa", set()))
    game4._set_stadium(fallback_named("Black Market"), owner=me4)
    _prizes(game4, "b")
    me4.active.damage = game4._max_hp(me4, me4.active)
    game4._check_ko(me4, foe4, "a")
    assert foe4.prizes_taken == 1
    assert "market_prize_cut" not in game4.events


def test_playing_black_market_goes_to_the_lost_zone_and_field_blower_misses():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    market = _idx(game, "a", "Black Market", used)
    sable = _idx(game, "a", "Sableye", used)
    dark = _idx(game, "a", "Darkness Energy", used)
    cleffa = _idx(game, "a", "Cleffa", used)
    me.active = Pokemon(card_i=cleffa)
    me.bench = [Pokemon(card_i=sable, energy=[dark])]
    me.hand = [market]
    me.discard = []
    me.lost_zone = []
    me.deck = []
    game._clear_stadium()
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Black Market"
    assert market in me.lost_zone
    assert market not in me.discard
    assert market not in me.hand

    foe_used: set[int] = set()
    blower = _idx(game, "b", "Field Blower", foe_used)
    foe.hand = [blower]
    game._resolve_trainer(foe, me, foe.card(blower), who="b", card_i=blower)
    assert game.stadium_name == "Black Market"
    game._set_stadium(fallback_named("Battle Cage"), owner=me)
    game._resolve_trainer(foe, me, foe.card(blower), who="b", card_i=blower)
    assert game.stadium_name is None


def test_mill_sends_a_prism_star_to_the_lost_zone():
    game = _game()
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    market = _idx(game, "b", "Black Market", used)
    foe.deck = [market]
    foe.discard = []
    foe.lost_zone = []
    game._mill_opponent(me, foe, 1)
    assert market in foe.lost_zone
    assert market not in foe.discard


def test_doll_plays_black_market_for_sableye_and_keeps_battle_cage_against_spread():
    game = _game("phantom")
    me = game.players["a"]
    foe = game.players["b"]
    used: set[int] = set()
    market = _idx(game, "a", "Black Market", used)
    cage = _idx(game, "a", "Battle Cage", used)
    sable = _idx(game, "a", "Sableye", used)
    dark = _idx(game, "a", "Darkness Energy", used)
    cleffa = _idx(game, "a", "Cleffa", used)
    me.active = Pokemon(card_i=cleffa)
    me.bench = [Pokemon(card_i=sable)]
    me.hand = [market, cage, dark]
    me.discard = []
    me.lost_zone = []
    me.deck = []
    game._clear_stadium()
    assert trainer_score(game, me, foe, me.card(market)) < 0
    assert trainer_score(game, me, foe, me.card(cage)) > 0
    game._play_trainers(me, foe, "a")
    assert game.stadium_name == "Battle Cage"
    assert market in me.hand


def test_life_dew_stays_off_sableye_when_black_market_is_in_hand():
    game = _game()
    me = game.players["a"]
    used: set[int] = set()
    dew = _idx(game, "a", "Life Dew", used)
    market = _idx(game, "a", "Black Market", used)
    sable = _idx(game, "a", "Sableye", used)
    cleffa = _idx(game, "a", "Cleffa", used)
    me.active = Pokemon(card_i=cleffa)
    me.bench = [Pokemon(card_i=sable)]
    me.hand = [dew, market]
    me.deck = []
    host = tool_host(game, me, me.card(dew))
    assert me.card(host.card_i).name == "Cleffa"
    me.hand = [dew]
    host = tool_host(game, me, me.card(dew))
    assert me.card(host.card_i).name == "Sableye"
