from __future__ import annotations

import re
from typing import Any

from app.engine.models import Attack


_TYPE_GLYPHS = {
    "{g}": "grass",
    "{r}": "fire",
    "{w}": "water",
    "{l}": "lightning",
    "{p}": "psychic",
    "{f}": "fighting",
    "{d}": "darkness",
    "{m}": "metal",
    "{y}": "fairy",
    "{n}": "dragon",
    "{c}": "colorless",
}


def _normalize_card_text(text: str) -> str:
    t = (text or "").lower().replace("pokémon", "pokemon").replace("poké", "poke")
    t = t.replace("’", "'").replace("`", "'")
    for glyph, name in _TYPE_GLYPHS.items():
        t = t.replace(glyph, name)
    return t


def parse_draw_until_hand(text: str) -> dict[str, Any] | None:
    """Lillie UPR 125: draw until 6, or until 8 if it is your first turn."""
    t = _normalize_card_text(text)
    first = re.search(
        r"draw cards until you have (\d+) cards in your hand\.?\s*"
        r"if it's your first turn, draw cards until you have (\d+) cards in your hand",
        t,
    )
    if first:
        return {
            "kind": "draw_until_hand",
            "count": int(first.group(1)),
            "first_turn": int(first.group(2)),
        }
    plain = re.search(r"draw cards until you have (\d+) cards in your hand", t)
    if plain:
        return {"kind": "draw_until_hand", "count": int(plain.group(1))}
    return None


def parse_damage(raw: Any) -> int:
    if raw is None or raw == "":
        return 0
    if isinstance(raw, (int, float)):
        return int(raw)
    text = str(raw)
    match = re.search(r"(\d+)", text)
    return int(match.group(1)) if match else 0


def parse_attack_cost(raw_cost: Any) -> list[str]:
    """Printed 0-cost attacks use []. Missing cost still defaults to one Colorless."""
    if raw_cost is None:
        return ["Colorless"]
    return [c for c in raw_cost if c]


def parse_attack(raw: dict[str, Any]) -> Attack:
    text = raw.get("effect") or raw.get("text") or ""
    damage_raw = raw.get("damage")
    return Attack(
        name=raw.get("name") or "Attack",
        cost=parse_attack_cost(raw.get("cost")),
        damage=parse_damage(damage_raw),
        text=text,
        effects=parse_effects(text, str(damage_raw or "")),
    )


def parse_ability_effects(text: str) -> list[dict[str, Any]]:
    """Parse Pokémon ability text. The printed sentence is the only source of truth.

    Lab notes, strategy names, and hardcoded look-N values must not invent an effect
    that is not in this text. Attacks already go through parse_effects; abilities
    must go through this function before the engine attaches, searches, or looks.
    """
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    if not t:
        return effects

    energy = re.search(
        r"(grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|colorless) energy",
        t,
    )
    energy_type = (energy.group(1) if energy else "psychic").title()
    benched = re.search(r"benched (\w+)", t)
    benched_name = benched.group(1) if benched else ""
    top = re.search(r"look at the top (\d+)", t)
    each = re.search(r"for each of your benched (\w+)", t)
    search_attach = "search your deck" in t and "attach" in t and "energy" in t

    # LOR 62 Moon-Watching Party: full-deck search, one energy per benched copy.
    if each and search_attach:
        effects.append(
            {
                "kind": "attach_energy_from_deck_per_benched",
                "benched_name": each.group(1),
                "energy_type": energy_type,
                "require_active": "active" in t,
            }
        )
        return effects

    # Only if the printed text actually says to look at the top N.
    if top and "attach" in t and "energy" in t:
        effects.append(
            {
                "kind": "attach_energy_from_top",
                "look": int(top.group(1)),
                "energy_type": energy_type,
                "benched_name": benched_name,
                "any_number": "any number" in t,
            }
        )
    elif top and "into your hand" in t and "attach" not in t:
        effects.append(
            {
                "kind": "look_top_put_hand",
                "look": int(top.group(1)),
                "keep": 1,
                "rest": "bottom" if "bottom" in t else "shuffle",
            }
        )

    if "knocked out during your opponent's last turn" in t and "draw" in t:
        n = re.search(r"draw (\d+)", t)
        effects.append(
            {
                "kind": "draw_if_ko_last_turn",
                "amount": int(n.group(1) if n else 3),
                "once_per_turn": "can't use more than 1" in t or "cannot use more than 1" in t,
            }
        )

    # Energy Carnival-style: attach a Basic Energy from hand to 1 of your Pokémon.
    if (
        "attach" in t
        and "basic energy" in t
        and "from your hand" in t
        and "to 1 of your" in t
    ):
        effects.append({"kind": "attach_basic_energy_from_hand", "once_per_turn": "once during your turn" in t})

    # Lillie's Clefairy ex Fairy Zone: opponent Dragon Weakness becomes Psychic ×2.
    if "dragon" in t and "weakness" in t and "psychic" in t and "opponent" in t:
        effects.append(
            {
                "kind": "fairy_zone",
                "pokemon_type": "Dragon",
                "weakness": "Psychic",
                "multiplier": 2,
            }
        )

    # Jungle Mr. Mime Invisible Wall: prevent attack damage ≥ threshold after W/R.
    if (
        ("30 or more" in t or "30 or more damage" in t)
        and "prevent" in t
        and "damage" in t
        and ("weakness" in t or "resistance" in t)
    ):
        threshold = 30
        n = re.search(r"(\d+) or more", t)
        if n:
            threshold = int(n.group(1))
        effects.append({"kind": "invisible_wall", "threshold": threshold})

    # Munkidori Adrena-Brain: move up to N damage counters, often gated on Darkness Energy.
    move_counters = re.search(
        r"move up to (\d+) damage counters from 1 of your pokemon to 1 of your opponent's pokemon",
        t,
    )
    if move_counters:
        require = None
        gated = re.search(
            r"if this pokemon has any (grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|colorless) energy attached",
            t,
        )
        if gated:
            require = gated.group(1).title()
        effects.append(
            {
                "kind": "move_damage_counters",
                "counters": int(move_counters.group(1)),
                "require_energy": require,
                "once_per_turn": "once during your turn" in t,
            }
        )

    # Ledian Glittering Star Pattern: on evolve, gust a ≤N remaining HP bench Pokémon.
    gust = re.search(
        r"switch in 1 of your opponent's benched pokemon that has (\d+) hp or less remaining",
        t,
    )
    if gust and "evolve" in t:
        effects.append({"kind": "gust_low_hp_on_evolve", "max_remaining": int(gust.group(1))})

    # Flutter Mane Midnight Fluttering: opponent's Active has no Abilities.
    if "has no abilities" in t and "active" in t:
        effects.append({"kind": "suppress_opponent_active_abilities"})

    # Dudunsparce Run Away Draw: draw N, then shuffle this Pokémon into the deck.
    if "shuffle this pokemon" in t and "into your deck" in t and "draw" in t:
        n = re.search(r"draw (\d+)", t)
        effects.append(
            {
                "kind": "draw_then_shuffle_self",
                "amount": int(n.group(1) if n else 3),
                "once_per_turn": "once during your turn" in t,
            }
        )

    # Meowth ex Last-Ditch Catch: play from hand onto Bench, search a Supporter.
    if (
        "from your hand onto your bench" in t
        and "supporter" in t
        and "search your deck" in t
    ):
        lock = "last-ditch" if "last-ditch" in t else None
        effects.append(
            {
                "kind": "search_supporter_on_bench",
                "once_per_turn": True,
                "name_lock": lock,
            }
        )

    # Risky Ruins: chip Basics that hit the Bench.
    stadium_chip = re.search(
        r"puts a basic(?: non-(\w+))? pokemon onto their bench.*?place (\d+) damage counters",
        t,
    )
    if stadium_chip:
        excl = stadium_chip.group(1)
        effects.append(
            {
                "kind": "stadium_bench_damage",
                "counters": int(stadium_chip.group(2)),
                "exclude_type": excl.title() if excl else None,
            }
        )

    # Kecleon Expert Hider: coin-flip prevent attack damage.
    if "prevent that damage" in t and "flip a coin" in t and "attack" in t:
        effects.append({"kind": "coin_prevent_attack_damage"})

    # Pidgeot Quick Search / Forest Seal Star Alchemy: search any one card.
    if "search your deck for a card" in t and "into your hand" in t:
        effects.append(
            {
                "kind": "search_any_card",
                "once_per_turn": "more than 1" in t and "in a game" not in t,
                "once_per_game": "in a game" in t or "vstar" in t,
                "require_attached_v": "attached" in t and "pokemon v" in t,
                "ability_lock": "quick search" if "quick search" in t else None,
            }
        )

    # Raikou V Fleet-Footed: Active only, draw a card. Printed Active gate is required
    # so Prankish-style "if you do, draw a card" does not match.
    if (
        "once during your turn" in t
        and "draw a card" in t
        and "search your deck" not in t
        and "your turn ends" not in t
        and "attach" not in t
        and (
            "if this pokemon is in the active spot" in t
            or "if this pokemon is your active" in t
        )
    ):
        effects.append(
            {
                "kind": "draw",
                "amount": 1,
                "once_per_turn": True,
                "require_active": True,
            }
        )

    # Rotom V Instant Charge: draw, then the turn ends.
    if "your turn ends" in t and "draw" in t:
        n = re.search(r"draw (\d+)", t)
        effects.append(
            {
                "kind": "draw_end_turn",
                "amount": int(n.group(1) if n else 3),
                "once_per_turn": "once during your turn" in t,
            }
        )

    # Bench shields. Damage and damage counters are different layers:
    # "does damage to benched" is damage; "put damage counters on benched" is an effect.
    # Rabsca Spherical Shield (TEF 24): "Prevent all damage from and effects of attacks
    # from your opponent's Pokémon done to your Benched Pokémon." Blocks both layers
    # vs attacks (Phantom Dive counters included), but not Abilities.
    if (
        "prevent all damage" in t
        and "benched" in t
        and "effects of attacks" in t
        and "damage counters" not in t
    ):
        effects.append({"kind": "prevent_bench_damage_and_attack_effects"})
    elif "prevent all damage" in t and "benched" in t and "attack" in t and "damage counters" not in t:
        # Shaymin Flower Curtain (DRI 10): "... to your Benched Pokémon that don't have
        # a Rule Box by attacks ..." Damage only, non-Rule-Box only. Does not stop counters.
        if "rule box" in t:
            effects.append({"kind": "prevent_bench_attack_damage_no_rulebox"})
        else:
            # Manaphy Wave Veil (BRS 41): damage only, all bench. Does not stop counters.
            effects.append({"kind": "prevent_bench_attack_damage"})

    # Battle Cage (ME02 85): "Prevent all damage counters from being placed on Benched
    # Pokémon (both yours and your opponent's) by effects of attacks and Abilities from
    # the opponent's Pokémon. (Damage from attacks is still taken.)" Blocks counter
    # effects (Phantom Dive, Adrena-Brain onto bench) for both benches, not damage.
    if (
        "prevent all damage counters from being placed" in t
        and "benched" in t
        and "effects of attacks" in t
    ):
        effects.append(
            {
                "kind": "stadium_prevent_bench_counters",
                "both_benches": "both yours and your opponent" in t,
                "attack_and_ability": "abilities" in t,
            }
        )

    # Collapsed Stadium: bench size 4; opponent discards first when it enters.
    bench_cap = re.search(r"can't have more than (\d+) benched", t)
    if bench_cap:
        effects.append(
            {
                "kind": "stadium_bench_limit",
                "limit": int(bench_cap.group(1)),
                "opponent_discards_first": "opponent discards first" in t,
            }
        )

    # Dimension Valley: attacks of each Psychic Pokémon in play cost [C] less
    if (
        "dimension valley" in t
        or ("attacks of each" in t and "pokemon in play" in t and "cost" in t and "less" in t)
    ):
        effects.append({"kind": "stadium_psychic_cost_less_colorless"})

    # Octillery Abyssal Hand / draw-until abilities. Count comes from print.
    until = parse_draw_until_hand(text)
    if until and "search your deck" not in t:
        until = dict(until)
        until["once_per_turn"] = "once during your turn" in t
        effects.append(until)

    # Porygon-Z Crazy Code: extra Special Energy attaches, as often as you like.
    if (
        "special energy" in t
        and "from your hand" in t
        and "attach" in t
        and "as often as you like" in t
    ):
        effects.append(
            {
                "kind": "attach_special_energy_from_hand",
                "as_often_as_you_like": True,
                "once_per_turn": False,
            }
        )

    # Lopunny FLF Big Jump / Jumpluff DRX Leave It to the Wind: attachments to *hand*.
    if re.search(
        r"return this (?:pokemon|card) and all cards attached to it to your hand",
        t,
    ) or (
        "put this pokemon and all cards attached to it into your hand" in t
        or "put this pokemon and all attached cards into your hand" in t
    ):
        effects.append(
            {
                "kind": "return_self_to_hand",
                "once_per_turn": "once during your turn" in t,
            }
        )

    # Abra Teleporter: shuffle this Pokémon (Ability). RAD already matched draw+shuffle.
    shuffled_self = "shuffle this pokemon" in t or (
        "shuffle it" in t and "attached" in t and "into your deck" in t
    )
    if (
        shuffled_self
        and "into your deck" in t
        and "draw" not in t
        and not any(e.get("kind") == "draw_then_shuffle_self" for e in effects)
    ):
        effects.append(
            {
                "kind": "shuffle_self_into_deck",
                "require_active": "active" in t,
                "once_per_turn": "once during your turn" in t,
            }
        )

    # Mew ex Memory Helix: copy attacks of any of your Benched Pokémon.
    if "can use the attacks of any of your benched pokemon" in t:
        effects.append({"kind": "copy_benched_attacks"})

    # Radiant Charizard Excited Heart: attacks cost [C] less for each Prize card your opponent has taken.
    if (
        "attacks cost [c] less for each prize card your opponent has taken" in t
        or ("attacks cost" in t and "less for each prize card" in t)
        or "excited heart" in t
    ):
        effects.append({"kind": "cost_less_colorless_per_opponent_prize"})

    # Broken Time-Space: evolve a Pokémon just played or just evolved this turn.
    if "just played" in t and "evolved" in t and "evolve" in t:
        effects.append({"kind": "evolve_just_played_or_evolved"})

    return effects


def parse_effects(text: str, damage_raw: str = "") -> list[dict[str, Any]]:
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    coin = "flip a coin" in t or ("flip" in t and "heads" in t)

    hand_prizes = re.search(
        r"if you have exactly (\d+) cards in your hand, take (\d+) prize cards",
        t,
    )
    if hand_prizes:
        effects.append(
            {
                "kind": "take_prizes_if_hand",
                "hand": int(hand_prizes.group(1)),
                "prizes": int(hand_prizes.group(2)),
                "shuffle_hand": "shuffle your hand into your deck" in t,
            }
        )

    items_from_discard = re.search(
        r"put (\d+) item cards from your discard pile into your hand",
        t,
    )
    if items_from_discard:
        effects.append(
            {
                "kind": "recycle_items_from_discard",
                "count": int(items_from_discard.group(1)),
            }
        )

    if "paralyze" in t:
        effects.append({"kind": "status", "status": "paralyzed", "coin": coin})
    if "poison" in t:
        effects.append({"kind": "status", "status": "poisoned", "coin": coin and "poison" in t})
    if "burn" in t:
        effects.append({"kind": "status", "status": "burned", "coin": coin})
    if "asleep" in t or "put to sleep" in t:
        effects.append({"kind": "status", "status": "asleep", "coin": coin})

    recoil = re.search(r"(?:also )?does (\d+) damage to itself", t)
    if recoil:
        effects.append({"kind": "recoil", "amount": int(recoil.group(1))})

    lock = re.search(r"(\d+) or less energy attached", t)
    if lock and ("can't attack" in t or "cannot attack" in t):
        effects.append({"kind": "energy_attack_lock", "max_energy": int(lock.group(1))})

    if "prevent all damage" in t and "basic" in t:
        effects.append({"kind": "prevent_basic_damage"})

    less = re.search(r"takes (\d+) less damage from attacks", t)
    if less and "next turn" in t:
        effects.append({"kind": "reduce_damage_next_turn", "amount": int(less.group(1))})

    weak_now = re.search(
        r"weakness is now (grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|dragon|colorless)",
        t,
    )
    if weak_now:
        until = "end_of_your_next_turn" if "until the end of your next turn" in t else "opponent_next_turn"
        effects.append(
            {
                "kind": "set_defender_weakness",
                "weakness": weak_now.group(1).title(),
                "until": until,
            }
        )

    if "discard an energy" in t or "discard 1 energy" in t or "discard a energy" in t:
        n = re.search(r"discard (\d+) energy", t)
        effects.append({"kind": "discard_energy", "count": int(n.group(1)) if n else 1})
    prize_swing = re.search(
        r"exactly (\d+) prize cards? remaining.*?(\d+) more damage",
        t,
    )
    if prize_swing:
        effects.append(
            {
                "kind": "opponent_prize_bonus",
                "prizes": int(prize_swing.group(1)),
                "bonus": int(prize_swing.group(2)),
            }
        )
        if "confus" in t:
            effects.append(
                {
                    "kind": "status",
                    "status": "confused",
                    "coin": coin,
                    "if_opponent_prizes": int(prize_swing.group(1)),
                }
            )
    elif "confus" in t:
        effects.append({"kind": "status", "status": "confused", "coin": coin})

    heal = re.search(r"heal (\d+)", t)
    if heal:
        effects.append({"kind": "heal", "amount": int(heal.group(1))})

    # Igglybuff Bouncy Circle: 30 damage for each benched Pokémon with 30 HP
    if "benched pok" in t and ("30 hp" in t or "maximum hp of 30" in t):
        per = 30
        n = re.search(r"(\d+) damage for each", t)
        if n:
            per = int(n.group(1))
        effects.append({"kind": "benched_30hp_pokemon_times", "per": per})

    if "draw" in t and "search your deck" not in t:
        until = parse_draw_until_hand(t)
        if until:
            effects.append(until)
        else:
            n = re.search(r"draw (\d+)", t)
            effects.append({"kind": "draw", "amount": int(n.group(1)) if n else 1})

    # MEW 035 Moon-Viewing Invitation: bench a named Pokémon (not any Basic).
    named_bench = re.search(
        r"search your deck for up to (\d+) ([a-z]+)(?: cards?)? and put them onto your bench",
        t,
    )
    if named_bench and named_bench.group(2) not in {"basic", "item", "energy"}:
        effects.append(
            {
                "kind": "call_family",
                "count": int(named_bench.group(1)),
                "name": named_bench.group(2),
            }
        )
    # Call for Family / bench a Basic from deck
    elif (
        "call for family" in t
        or ("basic" in t and "bench" in t and "search your deck" in t)
        or "search your deck for a basic" in t
        or "search your deck for up to" in t and "basic" in t and "bench" in t
    ):
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "call_family", "count": int(up_to.group(1)) if up_to else 1})

    # Carbink Lucky Find / item search attacks
    if "search your deck" in t and "item" in t:
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "search_item", "count": int(up_to.group(1)) if up_to else 1})

    # Litwick Kindling Panic / opponent deck mill
    if "discard the top" in t and "opponent" in t and "deck" in t:
        top = re.search(r"top (\d+)", t)
        effects.append({"kind": "mill_opponent", "count": int(top.group(1)) if top else 1})

    # Platinum Misdreavus Take Back: coin, then a Trainer from discard to hand.
    if "discard pile" in t and "trainer" in t and "into your hand" in t:
        effects.append({"kind": "recycle_trainer_from_discard", "coin": coin})

    # Platinum Mismagius Upper Hand: lock one named attack on the defender.
    if "can't use that attack" in t or "cannot use that attack" in t:
        effects.append({"kind": "disable_attack"})

    # Radiant Charizard / Regigigas: can't use attack or can't attack during next turn
    if "during your next turn, this pokemon can't" in t or "during your next turn, this pokemon cannot" in t:
        effects.append({"kind": "disable_self_attack_next_turn"})

    if "this attack does nothing" in t:
        if "same number of cards in your hand" in t:
            effects.append({"kind": "require_equal_hands"})
        elif "prize" in t:
            pair = re.search(r"exactly (\d+) or (\d+) prize", t)
            one = re.search(r"exactly (\d+) prize", t)
            if pair:
                effects.append(
                    {
                        "kind": "require_opponent_prizes",
                        "values": [int(pair.group(1)), int(pair.group(2))],
                    }
                )
            elif one:
                effects.append({"kind": "require_opponent_prizes", "values": [int(one.group(1))]})
        else:
            effects.append({"kind": "coin_whiff"})

    # Relicanth Into the Deep: basic Energy from discard to hand (not attach).
    if (
        "discard pile" in t
        and "energy" in t
        and "into your hand" in t
        and "trainer" not in t
        and "attach" not in t
    ):
        n = re.search(r"up to (\d+)", t)
        effects.append({"kind": "recycle_energy_from_discard", "count": int(n.group(1) if n else 2)})

    # Indeedee Expert Nurturer: search an Evolution and put it onto the matching Pokémon.
    if "evolves from 1 of your pokemon" in t and "put it onto that pokemon" in t:
        effects.append({"kind": "evolve_from_deck"})
    if "discard pile" in t and "attach" in t and "energy" in t and "up to" in t:
        up = re.search(r"up to (\d+)", t)
        effects.append({"kind": "transfer_charge", "count": int(up.group(1)) if up else 2})

    if "isn't affected by weakness" in t or "not affected by weakness" in t:
        effects.append({"kind": "ignore_wr"})
    if ("isn't affected" in t or "not affected" in t) and "effects" in t and "active" in t:
        effects.append({"kind": "ignore_active_effects"})

    if "choose 1 of your opponent's active" in t and "attack" in t and "use it as this attack" in t:
        effects.append({"kind": "copy_active_attack"})

    # Clefable ex Wondrous Moon (sv03-082): move Psychic Energy after the hit.
    if re.search(
        r"you may move any amount of psychic energy from your pokemon to your other pokemon",
        t,
    ):
        effects.append({"kind": "move_psychic_energy"})

    if "can't play any item" in t or "cannot play any item" in t:
        effects.append({"kind": "lock_items"})

    one_poke = re.search(r"does (\d+) damage to 1 of your opponent'?s? pokemon", t)
    if one_poke:
        effects.append({"kind": "damage_one_pokemon", "amount": int(one_poke.group(1))})

    own_bench = re.search(r"does (\d+) damage to 1 of your benched pokemon", t)
    if own_bench and "opponent" not in t.split("benched")[0][-24:]:
        effects.append({"kind": "self_bench_damage", "amount": int(own_bench.group(1))})

    if "move an energy from your opponent's active" in t and "benched" in t:
        effects.append({"kind": "move_opp_active_energy_to_bench"})

    if "discard all pokemon tools from your opponent's active" in t:
        effects.append({"kind": "discard_defender_tools"})

    # Mega Clefable ex Shooting Moons: discard Energy from hand for bonus damage.
    hand_discard = re.search(
        r"discard up to (\d+) energy cards? from your hand.*?(\d+) more damage",
        t,
    )
    if hand_discard and "discarded" in t:
        effects.append(
            {
                "kind": "discard_hand_energy_bonus",
                "max": int(hand_discard.group(1)),
                "per": int(hand_discard.group(2)),
            }
        )

    # Plusle Plus Damage / Jungle Meditate: N more for each damage counter on the defender.
    counter_bonus = re.search(r"(\d+) more damage for each damage counter", t)
    psychic_ref = "psychic energy" in t or "{p} energy" in t or "{p}" in t
    both_bench = re.search(r"(\d+) more damage for each benched pokemon", t)
    opp_bench = re.search(r"(\d+) more damage for each of your opponent's benched pokemon", t)
    in_play_nrg = re.search(
        r"at least (\d+) (grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|colorless) energy in play.*?(\d+) more damage",
        t,
    )
    fewer_prizes = re.search(
        r"(\d+) or fewer prize cards? remaining.*?(\d+) more damage",
        t,
    )
    heads_bonus = re.search(r"if heads, this attack does (\d+) more damage", t)
    named_nrg = re.search(
        r"has any ([a-z][a-z' ]+?) energy attached, this attack does (\d+) more damage",
        t,
    )
    if opp_bench:
        effects.append(
            {
                "kind": "benched_pokemon_bonus",
                "per": int(opp_bench.group(1)),
                "sides": "opponent",
            }
        )
    elif both_bench and ("both" in t or "yours and" in t):
        effects.append(
            {
                "kind": "benched_pokemon_bonus",
                "per": int(both_bench.group(1)),
                "sides": "both",
            }
        )
    elif counter_bonus and ("opponent" in t or "defending" in t):
        effects.append({"kind": "damage_counter_bonus", "per": int(counter_bonus.group(1))})
    elif counter_bonus and "this pokemon" in t:
        effects.append({"kind": "damage_counter_on_self_bonus", "per": int(counter_bonus.group(1))})
    elif in_play_nrg:
        effects.append(
            {
                "kind": "energy_in_play_bonus",
                "count": int(in_play_nrg.group(1)),
                "energy_type": in_play_nrg.group(2).title(),
                "bonus": int(in_play_nrg.group(3)),
            }
        )
    elif fewer_prizes:
        effects.append(
            {
                "kind": "opponent_prize_bonus",
                "prizes": int(fewer_prizes.group(1)),
                "bonus": int(fewer_prizes.group(2)),
                "op": "at_most",
            }
        )
    elif heads_bonus and coin:
        effects.append({"kind": "coin_damage_bonus", "bonus": int(heads_bonus.group(1))})
    elif named_nrg:
        effects.append(
            {
                "kind": "attached_named_energy_bonus",
                "name": named_nrg.group(1).strip(),
                "bonus": int(named_nrg.group(2)),
            }
        )
    elif "lost zone" in t and "tool" in t:
        pass
    elif psychic_ref and "more damage" in t and "for each" in t:
        n = re.search(r"(\d+) more damage for each", t)
        effects.append({"kind": "psychic_energy_bonus", "per": int(n.group(1)) if n else 30})
    elif "×" in damage_raw or "x" in damage_raw.lower() or "for each" in t:
        # Clefairy Wonder Storm style: scale by Psychic Energy in play.
        if psychic_ref and "attached" in t and "discarded" not in t:
            effects.append({"kind": "psychic_energy_times", "per": parse_damage(damage_raw) or 20})
        elif "discarded" not in t:
            hand_times = re.search(r"does (\d+) damage for each card in your hand", t)
            coin_times = re.search(r"flip (\d+) coins?.*?for each heads", t)
            if hand_times:
                effects.append({"kind": "hand_count_times", "per": int(hand_times.group(1))})
            elif coin_times:
                effects.append(
                    {
                        "kind": "coin_times",
                        "flips": int(coin_times.group(1)),
                        "per": parse_damage(damage_raw) or 10,
                    }
                )
            else:
                effects.append({"kind": "times", "note": damage_raw or text})

    # Dondozo (Paradox Rift): Supplemental Swallow-Up
    if "attach any number of basic energy" in t and "top" in t:
        top = re.search(r"top (\d+)", t)
        effects.append({"kind": "swallow_energy", "look": int(top.group(1)) if top else 5})

    # Orthworm Crunch-Time Rush style: more damage when deck is thin
    more = re.search(r"(\d+) or fewer cards in your deck.*?(\d+) more damage", t)
    if more:
        effects.append(
            {
                "kind": "deck_count_bonus",
                "max_deck": int(more.group(1)),
                "bonus": int(more.group(2)),
            }
        )

    # Rotom V Scrap Short: Tools to the Lost Zone, +N per card.
    lost_tools = re.search(
        r"(\d+) more damage for each card (?:you )?put in the lost zone",
        t,
    )
    if "lost zone" in t and "tool" in t:
        effects.append(
            {
                "kind": "tools_to_lost_zone_bonus",
                "per": int(lost_tools.group(1) if lost_tools else 40),
            }
        )

    if "discard a stadium" in t:
        effects.append({"kind": "may_discard_stadium"})

    if "shuffle this pokemon" in t and "into your deck" in t:
        effects.append({"kind": "shuffle_self_into_deck"})

    # Flutter Mane Hex Hurl: damage counters on benched Pokémon
    bench = re.search(
        r"put (\d+) damage counters? on (?:1 of )?your opponent'?s? benched",
        t,
    )
    if bench:
        effects.append({"kind": "bench_damage_counters", "counters": int(bench.group(1))})

    if "switch this pokemon with 1 of your benched" in t:
        effects.append({"kind": "switch_with_benched"})
    if (
        "put this pokemon and all attached cards into your hand" in t
        or "put this pokemon and all cards attached to it back into your hand" in t
        or re.search(
            r"return this (?:pokemon|card) and all cards attached to it to your hand",
            t,
        )
    ):
        effects.append({"kind": "return_self_to_hand"})

    return effects


def parse_energy_effects(text: str) -> list[dict[str, Any]]:
    """Parse Special Energy printed text. The sentence is the only source of truth."""
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    if not t:
        return effects
    # POR 88 / ME03 88 Telepathic Psychic Energy: attach from hand, then bench Basics.
    attach_search = re.search(
        r"when you attach this card from your hand to (?:one of your )?a? ?(\w+) pokemon,?\s*"
        r"(?:you may )?search your deck for up to (\d+) basic (\w+) pokemon",
        t,
    )
    if attach_search:
        effects.append(
            {
                "kind": "call_family",
                "count": int(attach_search.group(2)),
                "pokemon_type": attach_search.group(3).title(),
                "from_hand": True,
                "require_attach_type": attach_search.group(1).title(),
            }
        )
    # Speed Lightning Energy: draw N only if attached from hand to a typed Pokémon.
    typed_attach_draw = re.search(
        r"when you attach this card from your hand to (?:one of your )?a "
        r"(grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|dragon|colorless) "
        r"pokemon, draw (\d+) cards",
        t,
    )
    if typed_attach_draw:
        effects.append(
            {
                "kind": "draw_on_attach_from_hand",
                "amount": int(typed_attach_draw.group(2)),
                "require_attach_type": typed_attach_draw.group(1).title(),
            }
        )
    # Enriching Energy / Draw Energy: draw N (or "a card" = 1) when attached from hand.
    attach_draw = re.search(
        r"when you attach this card from your hand to a pokemon, draw (?:(\d+) cards|a card)",
        t,
    )
    if attach_draw and not typed_attach_draw:
        effects.append(
            {
                "kind": "draw_on_attach_from_hand",
                "amount": int(attach_draw.group(1) or 1),
            }
        )
    return effects


def parse_trainer_effects(text: str) -> list[dict[str, Any]]:
    """Parse Item/Supporter/Stadium sentences. Printed numbers stay in the effect dict."""
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    if not t:
        return effects

    look = re.search(r"look at the top (\d+)", t)
    pair = re.search(r"put (\d+) cards from your discard pile into your hand", t)
    if "you may play 2" in t and look and pair:
        effects.append(
            {
                "kind": "puzzle_of_time",
                "look": int(look.group(1)),
                "pair_count": int(pair.group(1)),
            }
        )
        return effects

    if (
        "isn't a pokemon v" in t
        and ("pokemon-gx" in t or "pokemon gx" in t)
        and "into your hand" in t
    ):
        effects.append(
            {
                "kind": "scoop_non_v_gx_to_hand",
                "discard_attached": "discard all attached" in t,
            }
        )
        return effects

    if "junk arm" in t and "discard pile" in t and "trainer" in t:
        n = re.search(r"discard (\d+) cards from your hand", t)
        effects.append(
            {
                "kind": "junk_arm",
                "discard": int(n.group(1) if n else 2),
                "exclude_self": "can't choose junk arm" in t or "cannot choose junk arm" in t,
            }
        )
        return effects

    mill = re.search(
        r"search your deck for up to (\d+) cards and discard them",
        t,
    )
    if mill:
        effects.append({"kind": "mill_own_deck", "count": int(mill.group(1))})
        return effects

    if (
        "supporter" in t
        and "discard pile" in t
        and "into your hand" in t
        and "search your deck" not in t
        and "item" not in t
    ):
        effects.append({"kind": "recycle_supporter_from_discard"})
        return effects

    if "evolves from 1 of your pokemon" in t and "put it onto that pokemon" in t:
        effects.append(
            {
                "kind": "wally_evolve",
                "first_turn_ok": "first turn" in t,
                "just_played_ok": "put into play this turn" in t,
            }
        )
        return effects

    if "just played" in t and "evolved" in t and "evolve" in t:
        effects.append({"kind": "evolve_just_played_or_evolved"})
        return effects

    return effects


def is_double_colorless(card: Any) -> bool:
    return "double colorless" in (getattr(card, "name", "") or "").lower()


def is_boomerang_energy(card: Any) -> bool:
    return "boomerang energy" in (getattr(card, "name", "") or "").lower()


def is_telepathic_energy(card: Any) -> bool:
    return "telepathic" in (getattr(card, "name", "") or "").lower() and getattr(card, "is_energy", False)


def is_enriching_energy(card: Any) -> bool:
    return "enriching" in (getattr(card, "name", "") or "").lower() and getattr(card, "is_energy", False)


def is_speed_lightning_energy(card: Any) -> bool:
    name = (getattr(card, "name", "") or "").lower()
    return "speed lightning" in name and getattr(card, "is_energy", False)


def is_draw_energy(card: Any) -> bool:
    name = (getattr(card, "name", "") or "").lower()
    return name == "draw energy" and getattr(card, "is_energy", False)


def is_special_energy(card: Any) -> bool:
    if not getattr(card, "is_energy", False):
        return False
    if (
        is_double_colorless(card)
        or is_boomerang_energy(card)
        or is_telepathic_energy(card)
        or is_enriching_energy(card)
        or is_speed_lightning_energy(card)
        or is_draw_energy(card)
    ):
        return True
    return (getattr(card, "stage", "") or "").lower() == "special"


def energy_provided(card: Any) -> list[str]:
    """Energy units one attached card pays. DCE pays two Colorless."""
    if is_double_colorless(card):
        return ["Colorless", "Colorless"]
    if is_boomerang_energy(card):
        return ["Colorless"]
    if is_telepathic_energy(card):
        return ["Psychic"]
    if is_enriching_energy(card):
        return ["Colorless"]
    if is_speed_lightning_energy(card):
        return ["Lightning"]
    if is_draw_energy(card):
        return ["Colorless"]
    et = getattr(card, "as_energy_type", None)
    if callable(et):
        et = card.as_energy_type
    if not et and getattr(card, "is_energy", False):
        et = getattr(card, "energy_type", None) or (card.types[0] if getattr(card, "types", None) else None)
    return [et] if et else []


def is_basic_energy(card: Any, pokemon_as_energy: bool = False) -> bool:
    if is_special_energy(card):
        return False
    if getattr(card, "is_energy", False):
        return True
    if pokemon_as_energy and getattr(card, "is_pokemon", False) and getattr(card, "as_energy_type", None):
        return True
    return False


def can_pay_energy(attached_types: list[str], cost: list[str]) -> bool:
    pool = list(attached_types)
    for need in [c for c in cost if c != "Colorless"]:
        if need in pool:
            pool.remove(need)
        else:
            return False
    colorless = sum(1 for c in cost if c == "Colorless")
    return len(pool) >= colorless


def weakness_multiplier(defender_weaknesses: list[dict[str, str]], attack_types: list[str]) -> int:
    for weak in defender_weaknesses or []:
        if weak.get("type") in attack_types:
            value = weak.get("value") or "×2"
            if "2" in value:
                return 2
    return 1


def resistance_reduce(defender_resistances: list[dict[str, str]], attack_types: list[str]) -> int:
    for resist in defender_resistances or []:
        if resist.get("type") in attack_types:
            value = resist.get("value") or "-30"
            match = re.search(r"(\d+)", value)
            return int(match.group(1)) if match else 30
    return 0
