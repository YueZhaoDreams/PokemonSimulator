"""Expanded Raichu / Electrode and Regidrago sentences. Printed text wins."""

from __future__ import annotations

from random import Random

from app.engine.effects import (
    can_pay_energy,
    energy_provided,
    parse_ability_effects,
    parse_effects,
    parse_trainer_effects,
)
from app.engine.game import ST_PARALYZED, Game, Pokemon
from app.engine.models import Card, expanded_60_rules
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck, fallback_named

ELECTRO_RAIN = (
    "Discard any amount of Lightning Energy from this Pokémon. Then, for each Energy you discarded "
    "in this way, choose 1 of your opponent's Pokémon and do 30 damage to it. (You can choose the "
    "same Pokémon more than once.) This damage isn't affected by Weakness or Resistance."
)
BUZZAP_THUNDER = (
    "This attack does 60 damage times the amount of Lightning Energy attached to this Pokémon. "
    "If this Pokémon has at least 3 extra Lightning Energy attached to it (in addition to this "
    "attack's cost), your opponent's Active Pokémon is now Paralyzed. Then, discard all Lightning "
    "Energy from this Pokémon."
)
FLYING_FLIP = (
    "This attack does 40 damage to each of your opponent's Pokémon that has any damage counters on it. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)
EXTRA_ENERGY_BOMB = (
    "Once during your turn (before your attack), you may attach up to 5 Energy cards from your discard pile "
    "to your Pokémon, except Pokémon-GX or Pokémon-EX, in any way you like. If you do, this Pokémon "
    "is Knocked Out."
)
SKY_FIELD = (
    "Each player can have 8 Pokémon on his or her Bench. "
    "(When this card leaves play, each player discards Benched Pokémon until he or she has 5 Pokémon "
    "on the Bench. The owner of this card discards first.)"
)
COUNTER_ENERGY = (
    "This card provides Colorless Energy. If you have more Prize cards remaining than your opponent, "
    "and if this card is attached to a Pokémon that isn't a Pokémon-GX or Pokémon-EX, this card provides "
    "every type of Energy but provides only 2 Energy at a time."
)
REVERSAL_ENERGY = (
    "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize "
    "cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't "
    "have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy "
    "but provides only 3 Energy at a time."
)
TRIFROST = (
    "Discard all Energy from this Pokémon. This attack does 110 damage to 3 of your opponent's Pokémon. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)
APEX_DRAGON = (
    "Choose an attack from a Dragon Pokémon in your discard pile and use it as this attack. "
    "(You can't use more than 1 VSTAR Power in a game.)"
)
DANCE = (
    "Once during your turn (before your attack), if this Pokémon is on your Bench, you may choose 2 of "
    "your Benched Pokémon and attach a Lightning Energy card from your discard pile to each of them. "
    "If you do, discard all cards from this Pokémon and put it in the Lost Zone."
)
THUNDERCLAP = "Each of your Pokémon that has any Lightning Energy attached to it has no Retreat Cost."
FLOATING = "If this Pokémon has any Energy attached to it, it has no Retreat Cost."
THUNDER_MOUNTAIN = (
    "The attacks of Lightning Pokémon (both yours and your opponent's) cost Lightning less. "
    "Whenever any player plays an Item or Supporter card from their hand, prevent all effects of that "
    "card done to this Stadium card."
)
ACRO_BIKE = "Look at the top 2 cards of your deck and put 1 of them into your hand. Discard the other card."
RESCUE = (
    "Put a Pokémon from your discard pile into your hand, or put 3 Pokémon from your discard pile into "
    "your deck and shuffle your deck."
)
SPECIAL_CHARGE = "Shuffle 2 Special Energy cards from your discard pile into your deck."
COUNTER_GAIN = (
    "If you have more Prize cards remaining than your opponent, the attacks of the Pokémon this card is "
    "attached to cost Colorless less."
)
FIELD_BLOWER = "You may discard up to 2 Pokémon Tool cards or Stadium cards from play, or 1 of each."
CHOICE_BAND = (
    "The attacks of the Pokémon this card is attached to do 30 more damage to your opponent's Active "
    "Pokémon-GX or Active Pokémon-EX (before applying Weakness and Resistance)."
)
GUZMA = (
    "Switch 1 of your opponent's Benched Pokémon with their Active Pokémon. If you do, switch your "
    "Active Pokémon with 1 of your Benched Pokémon."
)
CELESTIAL = (
    "Discard the top 3 cards of your deck. If any Energy cards were discarded in this way, attach them "
    "to this Pokémon."
)
DRAGON_LASER = (
    "This attack also does 30 damage to 1 of your opponent's Benched Pokémon. "
    "(Don't apply Weakness and Resistance for Benched Pokémon.)"
)
PATH = (
    "Pokémon with a Rule Box in play (both yours and your opponent's) have no Abilities. "
    "(Pokémon V, Pokémon-GX, etc. have Rule Boxes.)"
)
DOUBLE_DRAGON = (
    "This card can only be attached to Dragon Pokémon. This card provides every type of Energy, but "
    "provides only 2 Energy at a time, only while this card is attached to a Dragon Pokémon. "
    "(If this card is attached to anything other than a Dragon Pokémon, discard this card.)"
)
PLASMA = "During your next turn, this Pokémon can't attack."


def _pad(names: list[str]) -> list[str]:
    names = list(names)
    while len(names) < 40:
        names.append("Nest Ball")
    return names


def _game(a_names: list[str], b_names: list[str], strat_b: str = "electro_rain") -> Game:
    return Game(
        build_fallback_deck(_pad(a_names)),
        build_fallback_deck(_pad(b_names)),
        expanded_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(strat_b),
        Random(1),
    )


def _idxs(player, name: str) -> list[int]:
    return [i for i, card in enumerate(player.cards) if card.name == name]


def _drop(player, used: set[int]) -> None:
    for zone_name in ("hand", "deck", "prizes", "discard"):
        zone = getattr(player, zone_name)
        zone[:] = [i for i in zone if i not in used]


def _seat(player, active: int, bench: list[int], tool: int | None = None) -> None:
    used = {active, *bench}
    if tool is not None:
        used.add(tool)
    _drop(player, used)
    player.active = Pokemon(card_i=active, played_turn=0, tool=tool)
    player.bench = [Pokemon(card_i=i, played_turn=0) for i in bench]


def _in_play(player) -> set[int]:
    used: set[int] = set()
    for mon in player.in_play():
        used.add(mon.card_i)
        used.update(mon.energy)
        if mon.tool is not None:
            used.add(mon.tool)
    return used


def _take(player, name: str, n: int) -> list[int]:
    found: list[int] = []
    for zone_name in ("deck", "hand", "discard", "prizes"):
        zone = getattr(player, zone_name)
        for card_i in list(zone):
            if player.card(card_i).name != name:
                continue
            zone.remove(card_i)
            found.append(card_i)
            if len(found) == n:
                return found
    busy = _in_play(player)
    for card_i, card in enumerate(player.cards):
        if card.name == name and card_i not in busy and card_i not in found:
            found.append(card_i)
            if len(found) == n:
                break
    assert len(found) == n, name
    return found


def _attach(player, mon: Pokemon, name: str, n: int) -> list[int]:
    found = _take(player, name, n)
    mon.energy.extend(found)
    return found


def _behind(attacker, defender) -> None:
    while len(attacker.prizes) <= len(defender.prizes) and defender.prizes:
        defender.hand.append(defender.prizes.pop())


def _kind(effects, kind: str) -> dict:
    return next(e for e in effects if e.get("kind") == kind)


def test_set_m_list_is_unchanged():
    assert len(SET_M60_NAMES) == 60
    assert "Electrode-GX" not in SET_M60_NAMES
    assert "Alolan Raichu" not in SET_M60_NAMES
    assert "Sky Field" not in SET_M60_NAMES


def test_electro_rain_sentence_counts_discarded_cards():
    card = fallback_named("Alolan Raichu")
    text = card.attacks[0].text
    assert text == ELECTRO_RAIN
    rain = _kind(parse_effects(text), "discard_typed_energy_damage_per_card")
    assert rain["energy_type"] == "Lightning"
    assert rain["per_card"] == 30
    assert rain["repeat_ok"] is True
    assert rain["ignore_wr_all"] is True
    alt = text.replace("do 30 damage", "do 45 damage")
    assert _kind(parse_effects(alt), "discard_typed_energy_damage_per_card")["per_card"] == 45


def test_electro_rain_is_damage_and_battle_cage_does_not_stop_it():
    game = _game(
        ["Igglybuff", "Igglybuff", "Bursting Balloon", "Sobble", "Battle Cage"],
        ["Alolan Raichu", "Lightning Energy", "Lightning Energy", "Battle Cage"],
    )
    babies = game.players["a"]
    rain = game.players["b"]
    active = _idxs(babies, "Igglybuff")[0]
    bench = _idxs(babies, "Igglybuff")[1]
    balloon = _idxs(babies, "Bursting Balloon")[0]
    raichu = _idxs(rain, "Alolan Raichu")[0]
    _seat(babies, active, [bench], tool=balloon)
    _seat(rain, raichu, [])
    _attach(rain, rain.active, "Lightning Energy", 2)
    game._set_stadium(fallback_named("Battle Cage"), owner=babies)

    game._attack(rain, babies, "b")
    assert babies.bench[0].damage == 30
    assert babies.active.damage == 30
    assert rain.active.energy == []
    assert game.events.get("battle_cage") is None
    assert game.events.get("bursting_balloon_trigger") == 1
    assert game.events.get("bursting_balloon") == 6

    game._check_ko(babies, rain, "a")
    assert game.events.get("baby_ko_bench_a") == 1
    assert game.events.get("baby_ko_active_a") == 1


def test_electro_rain_ignores_weakness_and_one_special_is_one_card():
    game = _game(
        ["Sobble", "Igglybuff"],
        ["Alolan Raichu", "Counter Energy", "Lightning Energy"],
    )
    foe = game.players["a"]
    me = game.players["b"]
    sobble = _idxs(foe, "Sobble")[0]
    baby = _idxs(foe, "Igglybuff")[0]
    raichu = _idxs(me, "Alolan Raichu")[0]
    _seat(foe, sobble, [baby])
    _seat(me, raichu, [])
    _behind(me, foe)
    _attach(me, me.active, "Counter Energy", 1)
    host = me.card(me.active.card_i)
    assert energy_provided(me.card(me.active.energy[0]), prizes_behind=True, host=host) == ["Any", "Any"]

    game._attack(me, foe, "b")
    assert foe.bench[0].damage == 30
    assert foe.active.damage == 0
    assert me.active.energy == []
    assert game.events.get("electro_rain_cards") == 1


def test_reversal_on_gx_is_colorless_and_electro_rain_skips_it():
    gx = fallback_named("Electrode-GX")
    raichu = fallback_named("Alolan Raichu")
    reversal = fallback_named("Reversal Energy")
    assert reversal.text == REVERSAL_ENERGY
    assert energy_provided(reversal, prizes_behind=True, host=gx) == ["Colorless"]
    assert energy_provided(reversal, prizes_behind=True, host=raichu) == ["Any", "Any", "Any"]
    assert energy_provided(reversal, prizes_behind=False, host=raichu) == ["Colorless"]
    pikachu = fallback_named("Pikachu")
    assert energy_provided(reversal, prizes_behind=True, host=pikachu) == ["Colorless"]

    game = _game(
        ["Igglybuff"],
        ["Electrode-GX", "Reversal Energy", "Lightning Energy"],
    )
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Igglybuff")[0], [])
    _seat(me, _idxs(me, "Electrode-GX")[0], [])
    _behind(me, foe)
    _attach(me, me.active, "Reversal Energy", 1)
    _attach(me, me.active, "Lightning Energy", 1)
    effect = _kind(parse_effects(ELECTRO_RAIN), "discard_typed_energy_damage_per_card")
    kept = me.active.energy[0]
    game._electro_rain(me, foe, me.active, effect)
    assert me.active.energy == [kept]
    assert me.card(kept).name == "Reversal Energy"
    assert foe.active.damage == 30


def test_counter_energy_sentence():
    card = fallback_named("Counter Energy")
    assert card.text == COUNTER_ENERGY
    from app.engine.effects import parse_energy_effects

    spec = _kind(parse_energy_effects(card.text), "provides_any_when")
    assert spec["count"] == 2
    assert spec["exclude_gx_ex"] is True
    assert spec["requires_behind"] is True
    gx = fallback_named("Electrode-GX")
    raichu = fallback_named("Alolan Raichu")
    assert energy_provided(card, prizes_behind=True, host=gx) == ["Colorless"]
    assert energy_provided(card, prizes_behind=False, host=raichu) == ["Colorless"]
    assert energy_provided(card, prizes_behind=True, host=raichu) == ["Any", "Any"]
    alt = card.text.replace("only 2 Energy", "only 4 Energy")
    assert _kind(parse_energy_effects(alt), "provides_any_when")["count"] == 4


def test_flying_flip_damages_only_pokemon_that_already_have_counters():
    assert fallback_named("Tapu Koko ◇").attacks[0].text == FLYING_FLIP
    flip = _kind(parse_effects(FLYING_FLIP), "damage_each_with_counters")
    assert flip["amount"] == 40
    alt = FLYING_FLIP.replace("does 40 damage", "does 15 damage")
    assert _kind(parse_effects(alt), "damage_each_with_counters")["amount"] == 15

    game = _game(
        ["Mew ex", "Igglybuff", "Igglybuff", "Battle Cage"],
        ["Tapu Koko ◇", "Lightning Energy", "Lightning Energy"],
    )
    foe = game.players["a"]
    me = game.players["b"]
    hurt = _idxs(foe, "Igglybuff")[0]
    fine = _idxs(foe, "Igglybuff")[1]
    _seat(foe, _idxs(foe, "Mew ex")[0], [hurt, fine])
    _seat(me, _idxs(me, "Tapu Koko ◇")[0], [])
    _attach(me, me.active, "Lightning Energy", 2)
    foe.bench[0].damage = 10
    game._set_stadium(fallback_named("Battle Cage"), owner=foe)
    game._attack(me, foe, "b")
    assert foe.bench[0].damage == 50
    assert foe.bench[1].damage == 0
    assert foe.active.damage == 0
    assert game.events.get("battle_cage") is None


def test_buzzap_thunder_scales_then_discards_and_paralyzes_on_three_extra():
    atk = next(a for a in fallback_named("Electrode-GX").attacks if a.name == "Buzzap Thunder")
    assert atk.text == BUZZAP_THUNDER
    times = _kind(parse_effects(atk.text), "attached_energy_times")
    extra = _kind(parse_effects(atk.text), "paralyze_if_extra_energy")
    assert times == {"kind": "attached_energy_times", "per": 60, "energy_type": "Lightning"}
    assert extra == {"kind": "paralyze_if_extra_energy", "extra": 3, "energy_type": "Lightning"}
    alt = atk.text.replace("does 60 damage", "does 70 damage").replace("at least 3 extra", "at least 2 extra")
    assert _kind(parse_effects(alt), "attached_energy_times")["per"] == 70
    assert _kind(parse_effects(alt), "paralyze_if_extra_energy")["extra"] == 2

    game = _game(
        ["Mew ex"],
        ["Electrode-GX"] + ["Lightning Energy"] * 5,
    )
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    _seat(me, _idxs(me, "Electrode-GX")[0], [])
    _attach(me, me.active, "Lightning Energy", 5)
    game._attack(me, foe, "b")
    assert foe.active.damage == 300
    assert foe.active.status & ST_PARALYZED
    assert me.active.energy == []

    game = _game(["Mew ex"], ["Electrode-GX"] + ["Lightning Energy"] * 3)
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    _seat(me, _idxs(me, "Electrode-GX")[0], [])
    _attach(me, me.active, "Lightning Energy", 3)
    game._attack(me, foe, "b")
    assert foe.active.damage == 180
    assert not (foe.active.status & ST_PARALYZED)
    assert me.active.energy == []

    game = _game(["Mew ex"], ["Electrode-GX", "Lightning Energy", "Lightning Energy"])
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    _seat(me, _idxs(me, "Electrode-GX")[0], [])
    _attach(me, me.active, "Lightning Energy", 2)
    game._attack(me, foe, "b")
    assert foe.active.damage == 50
    assert me.active.energy

    game = _game(
        ["Mew ex"],
        ["Electrode-GX", "Thunder Mountain ◇"] + ["Lightning Energy"] * 4,
    )
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    _seat(me, _idxs(me, "Electrode-GX")[0], [])
    _attach(me, me.active, "Lightning Energy", 4)
    game._set_stadium(fallback_named("Thunder Mountain ◇"), owner=me)
    game._attack(me, foe, "b")
    assert foe.active.damage == 240
    assert foe.active.status & ST_PARALYZED


def test_sky_field_replaces_battle_cage_and_uses_the_printed_limit():
    card = fallback_named("Sky Field")
    assert card.text == SKY_FIELD
    sky = _kind(parse_ability_effects(card.text), "stadium_bench_limit")
    assert sky["raises"] is True
    assert sky["limit"] == 8
    assert sky["leave_limit"] == 5
    assert sky["owner_discards_first"] is True
    alt = card.text.replace("have 8", "have 7").replace("has 5", "has 4")
    parsed = _kind(parse_ability_effects(alt), "stadium_bench_limit")
    assert (parsed["limit"], parsed["leave_limit"]) == (7, 4)

    game = _game(["Battle Cage"] + ["Igglybuff"] * 8, ["Sky Field"] + ["Igglybuff"] * 8)
    game._set_stadium(fallback_named("Battle Cage"), owner=game.players["a"])
    game._play_stadium(game.players["b"], game.players["a"], card)
    assert game.stadium_name == "Sky Field"
    assert game._bench_limit() == sky["limit"]
    assert not any(e.get("kind") == "stadium_prevent_bench_counters" for e in game.stadium_effects)
    for who in ("a", "b"):
        player = game.players[who]
        ids = _idxs(player, "Igglybuff")
        _seat(player, ids[0], ids[1:7])
    game._note_bench30_end()
    assert game.events.get("sky_field_turns") == 1
    assert game.events.get("sky_field_with_cage") is None
    game._clear_stadium()
    assert len(game.players["a"].bench) == sky["leave_limit"]
    assert len(game.players["b"].bench) == sky["leave_limit"]

    widened = Card(
        catalog_id="sky-alt",
        name="Wide Bench",
        category="Trainer",
        trainer_kind="stadium",
        text=alt,
        retreat=0,
    )
    game._play_stadium(game.players["a"], game.players["b"], widened)
    assert game._bench_limit() == 7


def test_thunder_mountain_lowers_lightning_cost_and_field_blower_cannot_discard_it():
    mountain = fallback_named("Thunder Mountain ◇")
    assert mountain.text == THUNDER_MOUNTAIN
    less = _kind(parse_ability_effects(mountain.text), "stadium_attack_cost_less")
    assert less["pokemon_type"] == "Lightning"
    assert less["energy_type"] == "Lightning"
    assert any(e.get("kind") == "stadium_item_safe" for e in parse_ability_effects(mountain.text))
    blower = fallback_named("Field Blower")
    assert blower.text == FIELD_BLOWER
    assert _kind(parse_trainer_effects(blower.text), "discard_tools_and_stadiums")["count"] == 2

    game = _game(
        ["Alolan Raichu", "Lightning Energy"],
        ["Mew ex", "Field Blower", "Battle Cage"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    _seat(me, _idxs(me, "Alolan Raichu")[0], [])
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    game._set_stadium(mountain, owner=foe)
    rain = next(a for a in me.card(me.active.card_i).attacks if a.name == "Electro Rain")
    assert game._attack_cost(me, me.active, rain, foe) == []
    game._discard_tools_and_stadiums(me, foe, 2)
    assert game.stadium_name == "Thunder Mountain ◇"
    game._set_stadium(fallback_named("Battle Cage"), owner=foe)
    game._discard_tools_and_stadiums(me, foe, 2)
    assert game.stadium_name is None


def test_extra_energy_bomb_attaches_up_to_five_then_the_gx_gives_two_prizes():
    gx = fallback_named("Electrode-GX")
    assert gx.abilities[0].text == EXTRA_ENERGY_BOMB
    bomb = _kind(parse_ability_effects(gx.abilities[0].text), "attach_energy_from_discard_except_gx_ex")
    assert bomb["count"] == 5
    assert bomb["ko_self"] is True
    alt = gx.abilities[0].text.replace("up to 5", "up to 4")
    assert _kind(parse_ability_effects(alt), "attach_energy_from_discard_except_gx_ex")["count"] == 4

    game = _game(
        ["Mew ex"],
        ["Electrode-GX", "Pikachu"] + ["Lightning Energy"] * 5,
    )
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    pikachu = _idxs(me, "Pikachu")[0]
    _seat(me, _idxs(me, "Electrode-GX")[0], [pikachu])
    fuels = _take(me, "Lightning Energy", 5)
    me.discard.extend(fuels)
    game._use_passive_abilities(me, "b", foe)
    assert foe.prizes_taken == 2
    assert me.card(me.active.card_i).name == "Pikachu"
    assert len(me.active.energy) == 5
    assert any(me.card(i).name == "Electrode-GX" for i in me.discard)


def test_dance_of_the_ancients_and_retreat_abilities():
    koko = fallback_named("Tapu Koko ◇")
    assert koko.abilities[0].text == DANCE
    dance = _kind(parse_ability_effects(DANCE), "bench_attach_discard_energy_lost_zone")
    assert dance["count"] == 2
    assert dance["energy_type"] == "Lightning"
    assert _kind(parse_ability_effects(THUNDERCLAP), "retreat_zero_if_typed_energy")["energy_type"] == "Lightning"
    assert _kind(parse_ability_effects(FLOATING), "retreat_zero_if_any_energy")
    assert fallback_named("Zeraora-GX").abilities[0].text == THUNDERCLAP
    assert fallback_named("Voltorb").abilities[0].text == FLOATING

    game = _game(
        ["Mew ex"],
        ["Tapu Koko ◇", "Pikachu", "Voltorb", "Zeraora-GX"] + ["Lightning Energy"] * 3,
    )
    me = game.players["b"]
    foe = game.players["a"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    koko_i, pika, volt, zera = (
        _idxs(me, "Tapu Koko ◇")[0],
        _idxs(me, "Pikachu")[0],
        _idxs(me, "Voltorb")[0],
        _idxs(me, "Zeraora-GX")[0],
    )
    _seat(me, zera, [koko_i, pika, volt])
    fuels = _take(me, "Lightning Energy", 2)
    me.discard.extend(fuels)
    assert game._dance_of_the_ancients(me, me.bench[0], dance) is True
    assert koko_i in me.lost_zone
    assert all(len(mon.energy) == 1 for mon in me.bench)
    assert game._retreat_cost(me, me.bench[0]) == 0
    game._set_stadium(fallback_named("Path to the Peak"), owner=foe)
    assert game._abilities_suppressed(me, me.active)
    assert game._retreat_cost(me, me.bench[0]) == 1


def test_choice_band_hits_hyphen_gx_and_not_mew_ex():
    band = fallback_named("Choice Band")
    assert band.text == CHOICE_BAND
    assert _kind(parse_trainer_effects(band.text), "tool_damage_vs_gx_ex")["amount"] == 30
    game = _game(
        ["Electrode-GX", "Choice Band"] + ["Lightning Energy"] * 2,
        ["Electrode-GX", "Mew ex"],
    )
    me = game.players["a"]
    foe = game.players["b"]
    band_i = _idxs(me, "Choice Band")[0]
    _seat(me, _idxs(me, "Electrode-GX")[0], [], tool=band_i)
    _seat(foe, _idxs(foe, "Electrode-GX")[0], [])
    _attach(me, me.active, "Lightning Energy", 2)
    game._attack(me, foe, "a")
    assert foe.active.damage == 80
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    game._attack(me, foe, "a")
    assert foe.active.damage == 50


def test_trifrost_is_110_damage_to_three_and_cage_does_not_stop_it():
    kyurem = fallback_named("Kyurem")
    assert kyurem.attacks[0].text == TRIFROST
    spread = _kind(parse_effects(TRIFROST), "damage_n_opponent_pokemon")
    assert spread["amount"] == 110
    assert spread["count"] == 3
    assert any(e.get("kind") == "discard_all_energy" for e in parse_effects(TRIFROST))
    alt = TRIFROST.replace("110 damage", "80 damage").replace("to 3 of", "to 2 of")
    parsed = _kind(parse_effects(alt), "damage_n_opponent_pokemon")
    assert (parsed["amount"], parsed["count"]) == (80, 2)

    game = _game(
        ["Igglybuff", "Igglybuff", "Mew ex", "Battle Cage"],
        ["Kyurem", "Water Energy", "Water Energy", "Metal Energy", "Metal Energy", "Lightning Energy"],
        strat_b="regidrago",
    )
    foe = game.players["a"]
    me = game.players["b"]
    babies = _idxs(foe, "Igglybuff")
    _seat(foe, _idxs(foe, "Mew ex")[0], babies)
    _seat(me, _idxs(me, "Kyurem")[0], [])
    _attach(me, me.active, "Water Energy", 2)
    _attach(me, me.active, "Metal Energy", 2)
    _attach(me, me.active, "Lightning Energy", 1)
    game._set_stadium(fallback_named("Battle Cage"), owner=foe)
    game._attack(me, foe, "b")
    assert foe.active.damage == 110
    assert [mon.damage for mon in foe.bench] == [110, 110]
    assert me.active.energy == []
    assert game.events.get("battle_cage") is None
    game._check_ko(foe, me, "a")
    assert game.events.get("baby_ko_bench_a") == 2


def test_apex_dragon_copies_trifrost_and_is_once_per_game():
    vstar = fallback_named("Regidrago VSTAR")
    assert vstar.attacks[0].text == APEX_DRAGON
    effects = parse_effects(APEX_DRAGON)
    assert any(e.get("kind") == "copy_discard_dragon_attack" for e in effects)
    assert _kind(effects, "once_per_game")["flag"] == "vstar"
    drago = fallback_named("Regidrago V")
    dde = fallback_named("Double Dragon Energy")
    assert dde.text == DOUBLE_DRAGON
    assert energy_provided(dde, host=drago) == ["Any", "Any"]
    assert energy_provided(dde, host=None) == ["Any", "Any"]
    assert energy_provided(dde, host=fallback_named("Pikachu")) == []
    assert can_pay_energy(["Any", "Any", "Any", "Any"], ["Grass", "Grass", "Fire"])

    game = _game(
        ["Mew ex", "Igglybuff", "Igglybuff", "Battle Cage"],
        ["Regidrago VSTAR", "Kyurem", "Double Dragon Energy", "Double Dragon Energy", "Pikachu"],
        strat_b="regidrago",
    )
    foe = game.players["a"]
    me = game.players["b"]
    _seat(foe, _idxs(foe, "Mew ex")[0], _idxs(foe, "Igglybuff"))
    pika = _idxs(me, "Pikachu")[0]
    _seat(me, _idxs(me, "Regidrago VSTAR")[0], [pika])
    kyurem = _take(me, "Kyurem", 1)
    me.discard.extend(kyurem)
    dragons = _attach(me, me.active, "Double Dragon Energy", 2)
    game._set_stadium(fallback_named("Battle Cage"), owner=foe)
    assert game._discard_dragon_attacks(me)
    game._attack(me, foe, "b")
    assert foe.active.damage == 110
    assert [mon.damage for mon in foe.bench] == [110, 110]
    assert me.active.energy == []
    assert me.vstar_used is True
    me.active.energy.extend(dragons)
    for card_i in dragons:
        if card_i in me.discard:
            me.discard.remove(card_i)
    assert game._choose_attack(me, foe, game.strats["b"]) is None
    donor = me.active.energy.pop(0)
    me.bench[0].energy.append(donor)
    game._scrap_illegal_energy(me, me.bench[0])
    assert me.bench[0].energy == []
    assert donor in me.discard


def test_path_to_the_peak_shuts_rule_box_abilities():
    path = fallback_named("Path to the Peak")
    assert path.text == PATH
    assert _kind(parse_ability_effects(path.text), "suppress_rulebox_abilities")
    game = _game(["Mew ex", "Igglybuff"], ["Budew"])
    me = game.players["a"]
    _seat(me, _idxs(me, "Mew ex")[0], _idxs(me, "Igglybuff"))
    assert any(atk.name == "Bouncy Circle" for atk in game._attacks_for(me, me.active))
    game._set_stadium(path, owner=game.players["b"])
    assert game._abilities_suppressed(me, me.active)
    assert game._rulebox_lock_on_opponent(me) is True
    assert not any(atk.name == "Bouncy Circle" for atk in game._attacks_for(me, me.active))


def test_remaining_printed_trainer_and_attack_sentences():
    assert fallback_named("Acro Bike").text == ACRO_BIKE
    assert _kind(parse_trainer_effects(ACRO_BIKE), "look_top_keep_one")["look"] == 2
    assert _kind(parse_trainer_effects(ACRO_BIKE.replace("top 2", "top 4")), "look_top_keep_one")["look"] == 4
    assert fallback_named("Rescue Stretcher").text == RESCUE
    assert _kind(parse_trainer_effects(RESCUE), "rescue_stretcher")["shuffle_count"] == 3
    assert fallback_named("Special Charge").text == SPECIAL_CHARGE
    assert _kind(parse_trainer_effects(SPECIAL_CHARGE), "shuffle_special_energy_to_deck")["count"] == 2
    assert fallback_named("Counter Gain").text == COUNTER_GAIN
    assert _kind(parse_trainer_effects(COUNTER_GAIN), "cost_colorless_less_if_behind")
    assert fallback_named("Guzma").text == GUZMA
    assert _kind(parse_trainer_effects(GUZMA), "gust_and_switch")
    roar = next(a for a in fallback_named("Regidrago V").attacks if a.name == "Celestial Roar")
    laser = next(a for a in fallback_named("Regidrago V").attacks if a.name == "Dragon Laser")
    assert roar.text == CELESTIAL
    assert _kind(parse_effects(CELESTIAL), "discard_top_attach_energy")["count"] == 3
    assert laser.text == DRAGON_LASER
    bench = _kind(parse_effects(DRAGON_LASER), "damage_one_pokemon")
    assert bench["amount"] == 30 and bench["bench_only"] is True
    plasma = fallback_named("Zeraora-GX").attacks[0]
    assert plasma.text == PLASMA
    assert any(e.get("kind") == "disable_self_attack_next_turn" for e in parse_effects(PLASMA))

    game = _game(["Mew ex"], ["Alolan Raichu", "Counter Gain", "Lightning Energy", "Lightning Energy"])
    me = game.players["b"]
    foe = game.players["a"]
    _seat(foe, _idxs(foe, "Mew ex")[0], [])
    _seat(me, _idxs(me, "Alolan Raichu")[0], [], tool=_idxs(me, "Counter Gain")[0])
    ball = next(a for a in me.card(me.active.card_i).attacks if a.name == "Electric Ball")
    assert game._attack_cost(me, me.active, ball, foe).count("Colorless") == 2
    _behind(me, foe)
    assert game._attack_cost(me, me.active, ball, foe).count("Colorless") == 1
