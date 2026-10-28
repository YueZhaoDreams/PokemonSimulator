"""Doll lock pilot. Printed sentences stay in the parsers; this file only chooses.

The 1000-game holdout (seed 20261025) played the Nest Ball list. Item dolls are
Trainers, so a Pokémon search does not find them. They are played from hand.
Level Ball uses its printed HP line, which includes Shedinja once Nincada is out.
Sweet Sleeping Face, Energy Antics, Sleepy Lost, Junk Hunt, Puzzle of Time,
Handiwork, Dark Patch, Cursed Shovel, Life Dew, and Vessel of Life resolve from
their own text. One Supporter is played each turn. Arven finds an Item and a
Pokémon Tool. Petrel finds one Trainer. The other Supporter stays in hand.
Eeeeeeek stays a shuffle-and-draw. When the doll supply is about to run out,
Cleffa is sent Active to use it, and Life Dew goes on that Cleffa.
"""

from __future__ import annotations

from app.engine.effects import can_pay_energy

SPREAD = {"phantom", "starmie", "nuzzle"}
KEEPERS = {
    "puzzle of time",
    "team rocket's handiwork",
    "vs seeker",
    "switch",
    "level ball",
    "buddy-buddy poffin",
    "crushing hammer",
    "dark patch",
    "cursed shovel",
    "life dew",
    "slumbering forest",
    "battle cage",
    "rescue carrier",
    "field blower",
    "darkness energy",
    "black market",
    "arven",
    "team rocket's petrel",
}


def _asleep(mon) -> bool:
    from app.engine.game import ST_ASLEEP

    return bool(mon.status & ST_ASLEEP)


def _hard(game, player) -> bool:
    return game._foe_strat_name(player) == "demolish"


def _spread(game, player) -> bool:
    return game._foe_strat_name(player) in SPREAD


def _face_cap(game, player) -> int:
    if _hard(game, player):
        return 0
    if _spread(game, player):
        return 1
    return 2


def _face_count(game, player, extra_hand: bool = True) -> int:
    total = sum(1 for mon in player.in_play() if game._sweet_face(player.card(mon.card_i)))
    if extra_hand:
        total += sum(1 for i in player.hand if game._sweet_face(player.card(i)))
    return total


def _bench_room(game, player) -> int:
    return game._bench_limit(player) - len(player.bench)


def _dolls_in_play(game, player) -> int:
    return sum(1 for mon in player.in_play() if game._no_prize_proxy(player.card(mon.card_i)))


def _replayable_doll(game, card) -> bool:
    eff = game._proxy_effect(card) or {}
    return bool(eff.get("no_prize") and not eff.get("setup_only"))


def _replayable_in_play(game, player) -> int:
    return sum(1 for mon in player.in_play() if _replayable_doll(game, player.card(mon.card_i)))


def _replayable_in_deck(game, player) -> int:
    return sum(1 for i in player.deck if _replayable_doll(game, player.card(i)))


def _dolls_in_hand(game, me) -> int:
    return sum(1 for i in me.hand if _replayable_doll(game, me.card(i)))


def _dolls_running_out(game, player) -> bool:
    """The next Knock Out would leave too few dolls, and the deck still has one.

    Two dolls in hand can replace what leaves play. Three replayable dolls
    already in play keep the strict Eeeeeeek. A thinner board sends Cleffa up.
    """
    if _replayable_in_deck(game, player) < 1:
        return False
    if _dolls_in_hand(game, player) >= 2:
        return False
    return _replayable_in_play(game, player) <= 2


def _can_pay(game, me, mon, attack_name: str) -> bool:
    card = me.card(mon.card_i)
    atk = next((a for a in card.attacks if a.name.lower() == attack_name.lower()), None)
    if atk is None:
        return False
    return can_pay_energy(game._energy_pool(me, mon), game._attack_cost(me, mon, atk))


def _discard_items(game, me) -> int:
    return sum(1 for i in me.discard if me.card(i).is_item and not (game._proxy_effect(me.card(i)) or {}).get("setup_only"))


def _hunt_worth(game, me) -> bool:
    puzzles_hand = sum(1 for i in me.hand if me.card(i).name.lower() == "puzzle of time")
    puzzles_disc = sum(1 for i in me.discard if me.card(i).name.lower() == "puzzle of time")
    if puzzles_hand < 2 and puzzles_disc:
        return True
    if _bench_room(game, me) > 0 and any(_replayable_doll(game, me.card(i)) for i in me.discard):
        return True
    useful = {
        "team rocket's handiwork",
        "vs seeker",
        "level ball",
        "buddy-buddy poffin",
        "rescue carrier",
        "switch",
        "crushing hammer",
        "dark patch",
        "field blower",
    }
    return any(me.card(i).name.lower() in useful for i in me.discard)


def _hand_has_keepers(game, me) -> bool:
    for i in me.hand:
        card = me.card(i)
        if card.name.lower() in KEEPERS or _replayable_doll(game, card):
            return True
        if card.is_pokemon and card.name != "Cleffa":
            return True
    return len(me.hand) > 1


def wants_pokemon(game, player, card) -> bool:
    name = card.name.lower()
    copies = game._count_named_in_play(player, card.name)
    if name == "manaphy":
        if _hard(game, player):
            return False
        return copies < 1
    if game._sweet_face(card):
        under_cap = _face_count(game, player, extra_hand=False) < _face_cap(game, player)
        if name == "cleffa" and copies < 1 and _dolls_running_out(game, player):
            return True
        return under_cap
    if name == "sableye":
        return copies < 1
    if name == "nincada":
        if _hard(game, player):
            return False
        shed = any(player.card(mon.card_i).name.lower() == "shedinja" for mon in player.in_play())
        return copies < 1 and not shed and _dolls_in_play(game, player) >= 2
    return False


def starter_score(game, card) -> float:
    if game._sweet_face(card):
        return {"mime jr.": 60, "smoochum": 50, "cleffa": 40}.get(card.name.lower(), 35)
    if card.name.lower() == "sableye":
        return 30
    if card.name.lower() == "nincada":
        return 20
    if card.name.lower() == "manaphy":
        return 10
    return 0


def bench_prio(game, card) -> tuple:
    name = card.name.lower()
    if name == "manaphy":
        return (0, 0)
    if game._sweet_face(card):
        return (1, 0)
    if name == "sableye":
        return (2, 0)
    if name == "nincada":
        return (3, 0)
    return (4, 0)


def search_prefer(game, me) -> list[str]:
    names = {me.card(mon.card_i).name.lower() for mon in me.in_play()}
    names |= {me.card(i).name.lower() for i in me.hand}
    prefer = []
    if _dolls_running_out(game, me) and "cleffa" not in names:
        prefer.append("Cleffa")
    if not _hard(game, me) and "manaphy" not in names:
        prefer.append("Manaphy")
    if _face_count(game, me) < _face_cap(game, me):
        for face in ("Mime Jr.", "Smoochum", "Cleffa"):
            if face not in prefer:
                prefer.append(face)
    if "sableye" not in names:
        prefer.append("Sableye")
    if (
        not _hard(game, me)
        and "nincada" not in names
        and "shedinja" not in names
        and _dolls_in_play(game, me) >= 2
    ):
        prefer.append("Nincada")
    return prefer


def level_ball_name(game, me) -> str | None:
    """Shedinja is the Pokémon Nest Ball cannot find. Take it once Nincada is already in play."""
    if _hard(game, me):
        return None
    in_play = {me.card(mon.card_i).name.lower() for mon in me.in_play()}
    in_hand = {me.card(i).name.lower() for i in me.hand}
    if "nincada" not in in_play or "shedinja" in in_play or "shedinja" in in_hand:
        return None
    if any(me.card(i).name.lower() == "shedinja" for i in me.deck):
        return "Shedinja"
    return None


def energy_target(game, me):
    for mon in me.in_play():
        if me.card(mon.card_i).name.lower() == "sableye" and not _can_pay(game, me, mon, "Junk Hunt"):
            return mon
    return me.active


def energy_card(game, me, target):
    if me.card(target.card_i).name.lower() != "sableye":
        return None
    if _can_pay(game, me, target, "Junk Hunt"):
        return None
    for i in me.hand:
        if me.card(i).name.lower() == "darkness energy":
            return i
    return None


def _awake_face_idx(game, me):
    best = None
    for idx, mon in enumerate(me.bench):
        card = me.card(mon.card_i)
        if not game._sweet_face(card) or _asleep(mon):
            continue
        name = card.name.lower()
        rank = {"mime jr.": 0, "smoochum": 1, "cleffa": 2}.get(name, 4)
        if name == "cleffa" and _hand_has_keepers(game, me):
            rank = 8
        if best is None or rank < best[0]:
            best = (rank, idx)
    return None if best is None else best[1]


def _asleep_face_idx(game, me):
    for idx, mon in enumerate(me.bench):
        if game._sweet_face(me.card(mon.card_i)) and _asleep(mon):
            return idx
    return None


def _doll_bench_idx(game, me):
    best = None
    for idx, mon in enumerate(me.bench):
        card = me.card(mon.card_i)
        if not game._no_prize_proxy(card):
            continue
        rank = 0 if (game._proxy_effect(card) or {}).get("setup_only") else 1
        if best is None or rank < best[0]:
            best = (rank, idx)
    return None if best is None else best[1]


def switch_idx(game, me):
    if not me.active or not me.bench:
        return None
    card = me.card(me.active.card_i)
    name = card.name.lower()
    asleep = _asleep(me.active)
    face = game._sweet_face(card)
    if (
        name == "sableye"
        and _can_pay(game, me, me.active, "Junk Hunt")
        and _discard_items(game, me) >= 2
        and _hunt_worth(game, me)
    ):
        return None
    for idx, mon in enumerate(me.bench):
        if (
            me.card(mon.card_i).name.lower() == "sableye"
            and _can_pay(game, me, mon, "Junk Hunt")
            and _discard_items(game, me) >= 2
            and _hunt_worth(game, me)
        ):
            return idx
    if _dolls_running_out(game, me):
        if name == "cleffa" and not asleep:
            return None
        cleffa = _awake_cleffa_idx(game, me)
        if cleffa is not None:
            return cleffa
    if _hard(game, me):
        if game._no_prize_proxy(card):
            return None
        return _doll_bench_idx(game, me)
    if face and not asleep:
        if name == "cleffa" and _hand_has_keepers(game, me):
            return _awake_face_idx(game, me)
        return None
    if face and asleep:
        return _awake_face_idx(game, me)
    awake = _awake_face_idx(game, me)
    if awake is not None:
        return awake
    return _asleep_face_idx(game, me)


def _awake_cleffa_idx(game, me):
    for idx, mon in enumerate(me.bench):
        if me.card(mon.card_i).name.lower() == "cleffa" and not _asleep(mon):
            return idx
    return None


def retreat(game, me) -> None:
    if any(me.card(i).name.lower() == "switch" for i in me.hand):
        return
    idx = switch_idx(game, me)
    if idx is None or not me.active:
        return
    active = me.card(me.active.card_i)
    if game._retreat_cost(me, me.active) == 0 and not game._proxy_cant_retreat(active):
        if game._do_retreat_into(me, idx):
            return
    # Printed item dolls can't retreat. Lillie's own sentence puts it on the
    # bottom of the deck; Robo Substitute and Snorlax Doll discard themselves.
    # Another Pokémon has to stay benched so the Eeeeeeek hand is still playable.
    if me.card(me.bench[idx].card_i).name.lower() != "cleffa":
        return
    if len(me.bench) < 2 or not game._no_prize_proxy(active):
        return
    game._remove_proxy(me, me.active)


def _in_deck(me, name: str) -> bool:
    want = name.lower()
    return any(me.card(i).name.lower() == want for i in me.deck)


def _holding_tool(me, name: str) -> bool:
    want = name.lower()
    if any(me.card(i).name.lower() == want for i in me.hand):
        return True
    return any(mon.tool is not None and me.card(mon.tool).name.lower() == want for mon in me.in_play())


def _need_doll(game, me) -> bool:
    """One doll leaves play on a typical turn. The hand keeps the replacement."""
    return _dolls_in_hand(game, me) < 1


def _tool_name(game, me) -> str | None:
    """One tool. Shovel mills the doll that gets Knocked Out. Life Dew is the other."""
    if not _holding_tool(me, "cursed shovel") and _in_deck(me, "cursed shovel"):
        return "Cursed Shovel"
    if not _holding_tool(me, "life dew") and _in_deck(me, "life dew"):
        return "Life Dew"
    return None


def _face_asleep(game, me) -> bool:
    return bool(me.active and _asleep(me.active) and game._sweet_face(me.card(me.active.card_i)))


def _stadium_name(game, me) -> str | None:
    """The Stadium this position would play, when that card is still in the deck."""
    stadium = (game.stadium_name or "").lower()
    hand = {me.card(i).name.lower() for i in me.hand}
    spread = _spread(game, me)
    if "battle cage" not in hand and stadium != "battle cage" and (spread or _hard(game, me)) and _in_deck(me, "battle cage"):
        return "Battle Cage"
    cage_blocks_forest = spread and (stadium == "battle cage" or "battle cage" in hand)
    if (
        not cage_blocks_forest
        and "slumbering forest" not in hand
        and stadium != "slumbering forest"
        and _face_asleep(game, me)
        and _in_deck(me, "slumbering forest")
    ):
        return "Slumbering Forest"
    cage_blocks_market = (spread or _hard(game, me)) and stadium == "battle cage"
    forest_blocks_market = stadium == "slumbering forest" and _face_asleep(game, me)
    if (
        _sableye_market_ready(game, me)
        and not cage_blocks_market
        and not (spread and "battle cage" in hand)
        and not forest_blocks_market
        and "black market" not in hand
        and stadium != "black market"
        and _in_deck(me, "black market")
    ):
        return "Black Market"
    return None


def _spare_items(game, me, foe) -> list[str]:
    """Item half of Arven once a doll is already in hand."""
    prefer = []
    if level_ball_name(game, me):
        prefer.append("Level Ball")
    unpaid = any(
        me.card(mon.card_i).name.lower() == "sableye" and not _can_pay(game, me, mon, "Junk Hunt")
        for mon in me.in_play()
    )
    if unpaid:
        prefer.append("Dark Patch")
    puzzles = sum(1 for i in me.hand if me.card(i).name.lower() == "puzzle of time")
    if puzzles < 2:
        prefer.append("Puzzle of Time")
    if _bench_room(game, me) > 0:
        prefer.append("Buddy-Buddy Poffin")
    if switch_idx(game, me) is not None:
        prefer.append("Switch")
    if foe.active and foe.active.energy:
        prefer.append("Crushing Hammer")
    if game.stadium_owner is foe or any(mon.tool is not None for mon in foe.in_play()):
        prefer.append("Field Blower")
    return [name for name in prefer if _in_deck(me, name)]


def _petrel_want(game, me, foe) -> str | None:
    """One Trainer. The hand keeps whichever Supporter was not played."""
    hand = {me.card(i).name.lower() for i in me.hand}
    if _need_doll(game, me) and any(_replayable_doll(game, me.card(i)) for i in me.deck):
        return "doll"
    stadium = _stadium_name(game, me)
    if stadium:
        return stadium
    if foe.deck and "team rocket's handiwork" not in hand and _in_deck(me, "team rocket's handiwork"):
        return "Team Rocket's Handiwork"
    if "arven" not in hand:
        tool = _tool_name(game, me)
        if tool:
            return tool
    if (
        "arven" not in hand
        and _in_deck(me, "arven")
        and (_need_doll(game, me) or _tool_name(game, me))
    ):
        return "Arven"
    if (
        "vs seeker" not in hand
        and any(me.card(i).name.lower() == "team rocket's handiwork" for i in me.discard)
        and _in_deck(me, "vs seeker")
    ):
        return "VS Seeker"
    return None


def _arven_score(game, me, foe) -> float:
    """Added to the generic Supporter score. A doll in the hand outranks the mill."""
    doll = _need_doll(game, me) and any(_replayable_doll(game, me.card(i)) for i in me.deck)
    tool = _tool_name(game, me)
    spare = _spare_items(game, me, foe)
    if doll:
        return 22
    if tool:
        return 12
    if spare:
        return 4
    return -14


def _petrel_score(game, me, foe) -> float:
    want = _petrel_want(game, me, foe)
    if want == "doll":
        return 24
    if want == "Battle Cage":
        return 32
    if want == "Slumbering Forest":
        return 22
    if want == "Team Rocket's Handiwork":
        return 18
    if want in {"Cursed Shovel", "Life Dew"}:
        return 16
    if want == "Black Market":
        return 20
    if want == "Arven":
        return 10
    if want == "VS Seeker":
        return 14
    return -12


def play_arven(game, me, foe) -> None:
    """Printed Arven: one Item and one Pokémon Tool, then one shuffle per search."""
    tool = _tool_name(game, me)
    found = False
    if tool:
        got = game._search(me, lambda c, tool=tool: c.name.lower() == tool.lower(), prefer=[tool], source="arven")
        found = got is not None or found
    if _need_doll(game, me) and any(_replayable_doll(game, me.card(i)) for i in me.deck):
        got = game._search(
            me,
            lambda c: _replayable_doll(game, c),
            prefer=["Lillie's Poké Doll", "Robo Substitute Team Flare Gear"],
            source="arven",
        )
        found = got is not None or found
    else:
        spare = _spare_items(game, me, foe)
        if spare:
            wanted = {name.lower() for name in spare}
            got = game._search(
                me,
                lambda c, wanted=wanted: c.is_item and not _replayable_doll(game, c) and c.name.lower() in wanted,
                prefer=spare,
                source="arven",
            )
            found = got is not None or found
    if found:
        game._bump("arven")
        game._bump("doll_arven")


def play_petrel(game, me, foe) -> None:
    """Printed Petrel: one Trainer. A doll, the Stadium, or the mill, in that order."""
    want = _petrel_want(game, me, foe)
    if want is None:
        game._bump("petrel_whiff")
        return
    if want == "doll":
        found = game._search(
            me,
            lambda c: _replayable_doll(game, c),
            prefer=["Lillie's Poké Doll", "Robo Substitute Team Flare Gear"],
            source="petrel",
        )
    else:
        found = game._search(
            me,
            lambda c, want=want: c.is_trainer and c.name.lower() == want.lower(),
            prefer=[want],
            source="petrel",
        )
    if found is None:
        game._bump("petrel_whiff")
        return
    found_name = me.card(found).name
    game._bump("petrel")
    game._bump("doll_petrel")
    game._bump(f"petrel_into:{found_name}")
    game._log(f"{me.name} Petrel takes {found_name}")


def trainer_score(game, me, foe, card) -> float:
    name = card.name.lower()
    if game._proxy_effect(card):
        eff = game._proxy_effect(card) or {}
        if eff.get("setup_only") or not eff.get("no_prize"):
            return -20
        if _bench_room(game, me) <= 0 and me.active is not None:
            return -8
        return 30
    if name == "arven":
        return _arven_score(game, me, foe)
    if name == "team rocket's petrel":
        return _petrel_score(game, me, foe)
    spread = _spread(game, me)
    stadium = (game.stadium_name or "").lower()
    face_asleep = bool(me.active and _asleep(me.active) and game._sweet_face(me.card(me.active.card_i)))
    face_out = any(game._sweet_face(me.card(mon.card_i)) for mon in me.in_play())
    if name == "slumbering forest":
        if stadium == name:
            return -8
        if spread and stadium == "battle cage":
            return -20
        if spread and any(me.card(i).name.lower() == "battle cage" for i in me.hand):
            return -12
        if face_asleep:
            return 24
        if spread:
            return -6
        if face_out:
            return 18
        return -8
    if name == "battle cage":
        if stadium == "battle cage":
            return -8
        if spread or _hard(game, me):
            return 32
        if face_asleep:
            return -8
        return -4
    if name == "black market":
        # Prize line needs a Darkness Pokémon with Darkness Energy. Sableye is that Pokémon.
        # Battle Cage stays against spread. Slumbering Forest stays while a face is Asleep.
        if stadium == "black market":
            return -8
        if not _sableye_market_ready(game, me):
            return -6
        if (spread or _hard(game, me)) and stadium == "battle cage":
            return -20
        if spread and any(me.card(i).name.lower() == "battle cage" for i in me.hand):
            return -12
        if stadium == "slumbering forest" and face_asleep:
            return -10
        return 18
    if name in {"nest ball", "nesting ball"}:
        return 20 if _bench_room(game, me) > 0 else -8
    if name == "level ball":
        if level_ball_name(game, me):
            return 24
        deck = {me.card(i).name.lower() for i in me.deck}
        if _bench_room(game, me) > 0 and any(want.lower() in deck for want in search_prefer(game, me)):
            return 18
        return -8
    if name in {"buddy-buddy poffin", "buddy buddy poffin"}:
        return 26 if _bench_room(game, me) > 0 else -8
    if name == "rescue carrier":
        return 16 if game._rescue_carrier_targets(me, 90) else -8
    if name == "crushing hammer":
        if foe.active and foe.active.energy:
            return 12
        if any(mon.energy for mon in foe.in_play()):
            return 8
        return -6
    if name == "team rocket's handiwork":
        return 16 if foe.deck else -4
    if name == "puzzle of time":
        puzzles = sum(1 for i in me.hand if me.card(i).name.lower() == name)
        if puzzles >= 2 and _puzzle_targets(game, me):
            return 15
        return -4
    if name == "vs seeker":
        have = any(me.card(i).name.lower() == "team rocket's handiwork" for i in me.discard)
        return 13 if have else -6
    if name == "switch":
        return 26 if switch_idx(game, me) is not None else -20
    if name == "dark patch":
        energy = any(me.card(i).name.lower() == "darkness energy" for i in me.discard)
        bare = any(
            me.card(mon.card_i).name.lower() == "sableye" and not _can_pay(game, me, mon, "Junk Hunt")
            for mon in me.bench
        )
        return 22 if energy and bare else -6
    if name == "field blower":
        if game.stadium_name and game.stadium_owner is foe:
            return 22 if spread else 10
        if any(mon.tool is not None for mon in foe.in_play()):
            return 6
        return -8
    if name == "cursed shovel":
        return 14 if tool_host(game, me, card) is not None else -8
    if name == "life dew":
        return 12 if tool_host(game, me, card) is not None else -8
    return 0


def choose_attack(game, me, foe):
    if not me.active or _asleep(me.active):
        return None
    card = me.card(me.active.card_i)
    legal = []
    locked = me.active.disabled_attack or getattr(me.active, "disabled_self", None)
    attached = game._energy_pool(me, me.active)
    for atk in card.attacks:
        if atk.name == locked:
            continue
        if can_pay_energy(attached, game._attack_cost(me, me.active, atk, foe)):
            legal.append(atk)
    by_name = {atk.name.lower(): atk for atk in legal}
    name = card.name.lower()
    if name == "mime jr." and "sleepy lost" in by_name:
        return by_name["sleepy lost"]
    if name == "smoochum" and "energy antics" in by_name:
        return by_name["energy antics"]
    if name == "cleffa" and "eeeeeeek" in by_name:
        panic = not _hand_has_keepers(game, me)
        # An empty Bench would end the game before the new six cards are played.
        sacrifice = _dolls_running_out(game, me) and bool(me.bench)
        if panic or sacrifice:
            return by_name["eeeeeeek"]
    if name == "sableye" and "junk hunt" in by_name and _discard_items(game, me) >= 2 and _hunt_worth(game, me):
        return by_name["junk hunt"]
    return None


def promote_rank(game, player, index: int) -> tuple:
    mon = player.bench[index]
    card = player.card(mon.card_i)
    if (
        card.name.lower() == "sableye"
        and _can_pay(game, player, mon, "Junk Hunt")
        and _discard_items(game, player) >= 2
        and _hunt_worth(game, player)
    ):
        return (-2, 0)
    if _dolls_running_out(game, player) and card.name.lower() == "cleffa" and not _asleep(mon):
        return (-1, 0)
    hard = _hard(game, player)
    asleep_face = game._sweet_face(card) and _asleep(mon)
    if game._no_prize_proxy(card) and hard:
        return (0, 0)
    if asleep_face:
        return (5, 0) if hard else (0, 0)
    if game._sweet_face(card):
        return (5, 0) if hard else (1, 0)
    if game._no_prize_proxy(card):
        return (1, 0) if hard else (2, 0)
    if card.name.lower() == "sableye":
        return (2, 0) if hard else (4, 0)
    if card.name.lower() == "manaphy":
        return (8, 0)
    return (6, 0)


PUZZLE_PREFER = (
    "team rocket's handiwork",
    "arven",
    "team rocket's petrel",
    "vs seeker",
    "dark patch",
    "robo substitute team flare gear",
    "lillie's poké doll",
    "cursed shovel",
    "switch",
    "level ball",
    "buddy-buddy poffin",
    "crushing hammer",
    "darkness energy",
    "sableye",
    "slumbering forest",
    "battle cage",
    "rescue carrier",
    "cleffa",
    "smoochum",
    "mime jr.",
    "manaphy",
    "nincada",
)


def _puzzle_targets(game, me) -> list[int]:
    ranked = []
    for i in me.discard:
        card_i = me.card(i)
        name = card_i.name.lower()
        if name == "puzzle of time":
            continue
        if (game._proxy_effect(card_i) or {}).get("setup_only"):
            continue
        ranked.append((PUZZLE_PREFER.index(name) if name in PUZZLE_PREFER else 40, i))
    ranked.sort()
    return [i for _, i in ranked]


def play_puzzle(game, me, card, pair_count: int) -> bool:
    second = next((i for i in me.hand if me.card(i).name.lower() == card.name.lower()), None)
    if second is None or pair_count <= 0:
        return False
    ranked = _puzzle_targets(game, me)
    if not ranked:
        return False
    me.hand.remove(second)
    me.discard.append(second)
    taken = 0
    for card_i in ranked:
        if taken >= pair_count or card_i not in me.discard:
            continue
        me.discard.remove(card_i)
        me.hand.append(card_i)
        taken += 1
        game._bump("puzzle_retrieve")
    if taken == 0:
        me.discard.remove(second)
        me.hand.append(second)
        return False
    game._bump("puzzle_pair")
    return True


def seeker(game, me) -> None:
    supporters = [i for i in me.discard if me.card(i).is_supporter]
    if not supporters:
        game._bump("vs_seeker_miss")
        return
    prefer = ["team rocket's handiwork", "arven", "team rocket's petrel"]

    def rank(idx: int) -> int:
        name = me.card(idx).name.lower()
        return prefer.index(name) if name in prefer else 10

    pick = min(supporters, key=rank)
    me.discard.remove(pick)
    me.hand.append(pick)
    game._bump("vs_seeker")


def recycle_items(game, me, count: int) -> None:
    pool = [
        i
        for i in me.discard
        if me.card(i).is_item and not (game._proxy_effect(me.card(i)) or {}).get("setup_only")
    ]
    puzzles_hand = sum(1 for i in me.hand if me.card(i).name.lower() == "puzzle of time")
    need_pair = puzzles_hand < 2
    need_bodies = _bench_room(game, me) > 0 or _dolls_in_play(game, me) < 3
    thin = _dolls_in_play(game, me) < 2
    unpaid = any(
        me.card(mon.card_i).name.lower() == "sableye" and not _can_pay(game, me, mon, "Junk Hunt")
        for mon in me.in_play()
    )
    business = [
        "dark patch",
        "vs seeker",
        "level ball",
        "buddy-buddy poffin",
        "rescue carrier",
        "switch",
        "crushing hammer",
        "field blower",
    ]

    def rank(idx: int) -> tuple:
        card = me.card(idx)
        name = card.name.lower()
        if unpaid and name == "dark patch":
            return (0, 0)
        if thin and _replayable_doll(game, card):
            return (1, 0)
        if name == "puzzle of time":
            return (2 if need_pair else 5, 0)
        if _replayable_doll(game, card) and need_bodies:
            return (3, 0)
        if name in business:
            return (4, business.index(name))
        if _replayable_doll(game, card):
            return (6, 0)
        return (7, 0)

    pool.sort(key=rank)
    taken = 0
    for card_i in pool:
        if taken >= count:
            break
        if card_i not in me.discard:
            continue
        me.discard.remove(card_i)
        me.hand.append(card_i)
        taken += 1
        game._bump("junk_hunt")
        game._log(f"{me.name} Junk Hunt takes {me.card(card_i).name}")


def _sableye_market_ready(game, me) -> bool:
    """Sableye is in play and can have Darkness Energy on it this turn.

    Trainers resolve before the Energy attach, so a Darkness Energy still in hand counts.
    Dark Patch can put one from the discard onto a Benched Sableye during this same window.
    """
    darkness_hand = any(me.card(i).name.lower() == "darkness energy" for i in me.hand)
    patch = any(me.card(i).name.lower() == "dark patch" for i in me.hand)
    darkness_discard = any(me.card(i).name.lower() == "darkness energy" for i in me.discard)
    for mon in me.in_play():
        if me.card(mon.card_i).name.lower() != "sableye":
            continue
        if _can_pay(game, me, mon, "Junk Hunt") or darkness_hand:
            return True
        if mon is not me.active and patch and darkness_discard:
            return True
    return False


def _market_for_sableye(game, me) -> bool:
    if (game.stadium_name or "").lower() == "black market":
        return True
    return any(me.card(i).name.lower() == "black market" for i in me.hand)


def tool_host(game, me, card):
    name = card.name.lower()
    open_mons = [mon for mon in me.in_play() if mon.tool is None]
    if not open_mons:
        return None
    if name == "cursed shovel":
        dolls = [mon for mon in open_mons if game._no_prize_proxy(me.card(mon.card_i))]
        if not dolls:
            return None
        if me.active in dolls:
            return me.active
        return dolls[0]
    if name == "life dew":
        # The sacrificed Cleffa is the Knock Out. Life Dew makes that Prize cheaper.
        if _dolls_running_out(game, me):
            for mon in open_mons:
                if me.card(mon.card_i).name.lower() == "cleffa":
                    return mon
        # Black Market already cuts the Prize on an energized Sableye, so the tool
        # stays off that body and can go on a Pokémon that still gives a Prize.
        skip_sableye = _market_for_sableye(game, me)
        for mon in open_mons:
            if me.card(mon.card_i).name.lower() == "sableye" and not skip_sableye:
                return mon
        for mon in open_mons:
            if game._sweet_face(me.card(mon.card_i)):
                return mon
        return None
    return None


def claims_tool(card) -> bool:
    return card.name.lower() in {"cursed shovel", "life dew"}


def vessel_host(game, me, shed):
    hosts = []
    for mon in me.in_play():
        if mon is shed or mon.tool is not None:
            continue
        card = me.card(mon.card_i)
        if game._no_prize_proxy(card):
            continue
        rank = {"sableye": 0, "cleffa": 1, "smoochum": 1, "mime jr.": 1, "manaphy": 3, "nincada": 4}.get(
            card.name.lower(), 5
        )
        hosts.append((rank, mon))
    if not hosts:
        return None
    hosts.sort(key=lambda row: row[0])
    return hosts[0][1]
