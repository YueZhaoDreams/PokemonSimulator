from __future__ import annotations

import re
from typing import Any

from app.engine.models import Attack


_POKEMON_TYPE_WORDS = {
    "psychic",
    "darkness",
    "grass",
    "fire",
    "water",
    "lightning",
    "fighting",
    "metal",
    "fairy",
    "dragon",
}


def _printed_type_list(fragment: str) -> list[str]:
    found: list[str] = []
    for part in re.split(r"\s+or\s+|\s+and\s+|,\s*", fragment):
        name = part.strip()
        if name in _POKEMON_TYPE_WORDS:
            titled = name.title()
            if titled not in found:
                found.append(titled)
    return found


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

    # Hariyama Heave-Ho Catcher: on evolve, gust any Benched Pokémon.
    # Ledian's sentence adds "90 HP or less remaining" and is parsed below.
    if (
        "when you play this pokemon from your hand to evolve" in t
        and "switch in 1 of your opponent's benched" in t
        and "or less remaining" not in t
    ):
        effects.append({"kind": "force_opponent_active", "trigger": "on_evolve"})

    # Lunatone Lunar Cycle: Solrock in play, discard a Basic Fighting Energy, draw 3.
    if "discard a basic fighting energy" in t and "draw" in t and "solrock in play" in t:
        n = re.search(r"draw (\d+)", t)
        effects.append(
            {
                "kind": "lunar_cycle",
                "draw": int(n.group(1) if n else 3),
                "require_in_play": "Solrock",
                "energy_type": "Fighting",
                "once_per_turn": "can't use more than 1" in t or "cannot use more than 1" in t,
            }
        )

    # Gravity Mountain: Stage 2 Pokémon in play get -N HP.
    stage_hp = re.search(r"each stage 2 pokemon in play.*gets (-\d+) hp", t)
    if stage_hp:
        effects.append({"kind": "stage2_hp", "delta": int(stage_hp.group(1))})

    # Lively Stadium: each Basic in play gets +N HP. The number stays in the effect.
    stadium_hp = re.search(
        r"each (basic |stage 1 |stage 2 )?pokemon in play.*?gets \+(\d+) hp",
        t,
    )
    if stadium_hp:
        stage = (stadium_hp.group(1) or "").strip()
        effects.append(
            {
                "kind": "stadium_hp",
                "amount": int(stadium_hp.group(2)),
                "basic_only": stage == "basic",
            }
        )

    # Ledian Glittering Star Pattern: on evolve, gust a ≤N remaining HP bench Pokémon.
    gust = re.search(
        r"switch in 1 of your opponent's benched pokemon that has (\d+) hp or less remaining",
        t,
    )
    if gust and "evolve" in t:
        effects.append({"kind": "gust_low_hp_on_evolve", "max_remaining": int(gust.group(1))})
        effects.append(
            {
                "kind": "force_opponent_active",
                "trigger": "on_evolve",
                "max_remaining_hp": int(gust.group(1)),
            }
        )

    # Iron Thorns ex Initialization: Rule Box Pokémon in play have no Abilities.
    # Checked before Midnight Fluttering so "have no Abilities" is not that lock.
    if "no abilities" in t and "rule box" in t:
        except_trait = "future" if "except for future" in t else None
        effects.append(
            {
                "kind": "suppress_rulebox_abilities",
                "except_trait": except_trait,
                "require_active": "in the active spot" in t,
            }
        )
    # Flutter Mane Midnight Fluttering: opponent's Active has no Abilities.
    elif "has no abilities" in t and "active" in t:
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

    # Great Encounters 100: "The Retreat Cost for each Psychic and Darkness Pokémon
    # (both yours and your opponent's) is 0." The Pokémon's type, both players,
    # retreat cost 0. No Energy has to be attached.
    # Beach Court says "each Basic Pokémon" and "Colorless less".
    # Lunar Zone says "your Pokémon", not both players.
    typed_zero = re.search(r"retreat cost (?:of|for) each ([a-z ]+?) pokemon\b", t)
    if (
        typed_zero
        and "both yours and your opponent" in t
        and re.search(r"\bis 0\b", t)
        and "energy attached" not in t
    ):
        poke_types = _printed_type_list(typed_zero.group(1))
        if poke_types:
            effects.append(
                {
                    "kind": "stadium_retreat_zero",
                    "pokemon_types": poke_types,
                    "both_players": True,
                }
            )

    # Lost Thunder 188: retreat is Colorless less when any Psychic or Darkness
    # Energy is attached. An older print of that same gate "has no Retreat Cost."
    retreat_gate = re.search(r"any ([a-z ]+?) energy attached", t)
    if (
        retreat_gate
        and "both yours and your opponent" in t
        and "retreat" in t
    ):
        types = _printed_type_list(retreat_gate.group(1))
        if types and "no retreat cost" in t:
            effects.append(
                {
                    "kind": "stadium_retreat_zero",
                    "energy_types": types,
                    "both_players": True,
                }
            )
        elif types and "retreat cost" in t and "less" in t:
            less = len(re.findall(r"colorless", t))
            effects.append(
                {
                    "kind": "stadium_retreat_less",
                    "less": less if less > 0 else 1,
                    "energy_types": types,
                    "both_players": True,
                }
            )

    # Surging Sparks 76 Skyliner: "Your Basic Pokémon in play have no Retreat Cost."
    # Owner's Basics only, while the Pokémon with this Ability is in play.
    # A both-players stadium, and Lunar Zone's Energy gate, are different sentences.
    if "your basic pokemon in play have no retreat cost" in t:
        effects.append(
            {
                "kind": "basic_retreat_zero",
                "basic_only": True,
                "owner_only": True,
            }
        )

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

    # Lost City: the Knocked Out Pokémon goes to the Lost Zone; attachments are discarded.
    if "knocked out" in t and "lost zone" in t and "discard pile" in t:
        effects.append({"kind": "ko_to_lost_zone"})

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

    # Tera rule printed on the Pokémon. Area Zero looks for this sentence, not the name.
    if (
        "as long as this pokemon is on your bench" in t
        and "prevent all damage done to this pokemon by attacks" in t
    ):
        effects.append({"kind": "tera"})
        effects.append({"kind": "prevent_attack_damage_while_benched"})

    _extend_expanded_ability_effects(t, effects)
    return effects


def parse_effects(text: str, damage_raw: str = "") -> list[dict[str, Any]]:
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    effects.extend(_attack_spread_effects(t))
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

    # Buzzap Thunder's paralyze is gated on extra Lightning. A bare "Paralyzed"
    # in that sentence must not also become an unconditional status.
    if "paralyze" in t and not any(e.get("kind") == "paralyze_if_extra_energy" for e in effects):
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

    if "if you go second" in t and (
        "can't use this attack during your first turn" in t
        or "cannot use this attack during your first turn" in t
    ):
        effects.append({"kind": "no_attack_second_first_turn"})

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
    # Call for Family / bench a Basic from deck. Turbo Energize attaches Basic Energy, not a Basic Pokémon.
    elif "basic energy" not in t and (
        "call for family" in t
        or ("basic" in t and "bench" in t and "search your deck" in t)
        or "search your deck for a basic" in t
        or ("search your deck for up to" in t and "basic" in t and "bench" in t)
    ):
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "call_family", "count": int(up_to.group(1)) if up_to else 1})

    # Carbink Lucky Find / item search attacks
    if "search your deck" in t and "item" in t:
        up_to = re.search(r"up to (\d+)", t)
        effects.append({"kind": "search_item", "count": int(up_to.group(1)) if up_to else 1})

    # Litwick Kindling Panic, Great Tusk Land Collapse, Houndoom-EX Melting Horn,
    # Wiglett Dig a Little, Wugtrio Undersea Tunnel. Counts and coin flips stay
    # on the printed sentence.
    if "discard the top" in t and "opponent" in t and "deck" in t:
        top = re.search(r"top (\d+)", t)
        spec: dict[str, Any] = {"kind": "mill_opponent", "count": int(top.group(1)) if top else 1}
        flips = re.search(r"flip (\d+) coins", t)
        if flips and "for each heads" in t:
            spec["coins"] = int(flips.group(1))
        elif "flip a coin" in t and "if heads" in t:
            spec["coins"] = 1
        extra = re.search(r"discard (\d+) more cards in this way", t)
        if extra and "ancient supporter" in t:
            spec["extra_if_ancient_supporter"] = int(extra.group(1))
        effects.append(spec)

    # Houndoom-EX Grand Flame: one Fire from discard onto a Benched Pokémon.
    if "attach a fire energy card from your discard pile" in t and "benched" in t:
        onto = re.search(r"to (\d+) of your benched", t)
        effects.append(
            {
                "kind": "attach_typed_energy_from_discard",
                "energy_type": "Fire",
                "count": int(onto.group(1) if onto else 1),
                "bench_only": True,
            }
        )

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
        bench_named = re.search(
            r"if you don't have ([a-z0-9 .'-]+?) on your bench, this attack does nothing",
            t,
        )
        if bench_named:
            effects.append({"kind": "require_named_on_bench", "name": bench_named.group(1).strip()})
        elif "same number of cards in your hand" in t:
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
    if "basic fighting energy" in t and "discard pile" in t and "attach" in t and "benched" in t:
        up = re.search(r"up to (\d+)", t)
        effects.append(
            {
                "kind": "attach_typed_energy_from_discard",
                "count": int(up.group(1) if up else 3),
                "energy_type": "Fighting",
                "bench_only": True,
            }
        )
    elif "discard pile" in t and "attach" in t and "energy" in t and "up to" in t:
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
            own_bench = re.search(
                r"this attack does (\d+) damage for each of your benched pokemon",
                t,
            )
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
            elif own_bench and "maximum hp" not in t and "30 hp" not in t:
                # Unified Beatdown: 30 for each benched Pokémon. The printed "30×"
                # is the per-Pokémon amount, not a base plus a bonus.
                effects.append({"kind": "benched_pokemon_times", "per": int(own_bench.group(1))})
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

    # Volt Cyclone: move one attached Energy onto a Benched Pokémon.
    if "move an energy from this pokemon" in t and "benched" in t:
        effects.append({"kind": "move_own_energy_to_bench"})

    # Technical Machine: Turbo Energize. The count stays in the printed "up to N".
    turbo = re.search(
        r"search your deck for up to (\d+) basic energy cards and attach them to your benched pokemon",
        t,
    )
    if turbo:
        effects.append({"kind": "attach_basic_energy_to_bench", "count": int(turbo.group(1))})

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
    # Journey Together Spiky Energy. Each attached copy is its own sentence, so the
    # counters stack with other copies and with a Tool that has the same kind of sentence.
    # This printing has no Pokémon Tool clause. The count is the printed number.
    spiked = re.search(
        r"in the active spot and is damaged by an attack from your opponent's pokemon "
        r"\(even if this pokemon is knocked out\), put (\d+) damage counters on the attacking pokemon",
        t,
    )
    if spiked:
        effects.append({"kind": "counters_on_attacker", "counters": int(spiked.group(1))})
    _extend_conditional_energy_effects(t, effects)
    return effects


def _attached_tool_reactive(t: str) -> list[dict[str, Any]]:
    """Bursting Balloon: counters on the attacker, then discard at the end of the opponent's turn.

    The counter count is the printed number. A miss returns nothing so other trainers keep parsing.
    """
    counters = re.search(
        r"damaged by an opponent's attack \(even if that pokemon is knocked out\), "
        r"put (\d+) damage counters on the attacking pokemon",
        t,
    )
    if not counters:
        return []
    effects: list[dict[str, Any]] = [
        {"kind": "counters_on_attacker", "counters": int(counters.group(1))}
    ]
    if "discard it at the end of your opponent" in t and "turn" in t:
        effects.append({"kind": "discard_end_of_opponents_turn"})
    return effects


def parse_trainer_effects(text: str) -> list[dict[str, Any]]:
    """Parse Item/Supporter/Stadium sentences. Printed numbers stay in the effect dict."""
    t = _normalize_card_text(text)
    effects: list[dict[str, Any]] = []
    if not t:
        return effects
    # Wondrous Patch (ME02 94 / Perfect Order 117): one Basic Psychic from
    # discard onto one Benched Psychic Pokémon. The "1" is the printed count.
    if (
        "attach a basic psychic energy card from your discard pile" in t
        and "benched psychic pokemon" in t
    ):
        effects.append(
            {
                "kind": "wondrous_patch",
                "count": 1,
                "energy_type": "Psychic",
                "bench_only": True,
                "pokemon_type": "Psychic",
            }
        )
        return effects
    reactive = _attached_tool_reactive(t)
    if reactive:
        return reactive

    # Professor Sada's Vitality: up to N Basic Energy from discard onto Ancient Pokémon.
    if "ancient pokemon" in t and "basic energy card from your discard pile" in t:
        up_to = re.search(r"up to (\d+)", t)
        draw = re.search(r"draw (\d+) cards", t)
        effects.append(
            {
                "kind": "attach_energy_to_ancient",
                "count": int(up_to.group(1) if up_to else 1),
                "draw": int(draw.group(1) if draw else 0),
                "trait": "ancient",
            }
        )
        return effects

    # Explorer's Guidance: look N, keep K, discard the rest. Keep 1 stays on the
    # older look_top_keep_one hook.
    keep = re.search(
        r"look at the top (\d+) cards of your deck and put (\d+) of them into your hand",
        t,
    )
    if keep and "discard the other" in t and int(keep.group(2)) != 1:
        effects.append(
            {
                "kind": "look_top_keep",
                "look": int(keep.group(1)),
                "keep": int(keep.group(2)),
            }
        )
        return effects

    # Awakening Drum: draw one card for each in-play Pokémon of the printed trait.
    drum = re.search(r"draw a card for each of your (\w+) pokemon in play", t)
    if drum:
        effects.append({"kind": "draw_per_trait", "trait": drum.group(1)})
        return effects

    # Miss Fortune Sisters: look at the top N of the opponent's deck, discard Items.
    sisters = re.search(
        r"look at the top (\d+) cards of your opponent's deck and discard any number of item cards",
        t,
    )
    if sisters:
        effects.append({"kind": "discard_top_items", "look": int(sisters.group(1))})
        return effects

    expanded = _expanded_trainer_effects(t)
    if expanded:
        return expanded

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

    # Premium Power Pro: Fighting attacks do N more to the Active this turn.
    power = re.search(
        r"during this turn, attacks used by your fighting pokemon do (\d+) more damage",
        t,
    )
    if power:
        effects.append({"kind": "fighting_damage_this_turn", "amount": int(power.group(1))})
        return effects

    # Fighting Gong: Basic Fighting Energy or Basic Fighting Pokémon to hand.
    if "search your deck" in t and "basic fighting energy" in t and "basic fighting pokemon" in t:
        effects.append({"kind": "search_fighting_basic"})
        return effects

    # Team Rocket's Petrel: any Trainer from the deck.
    if "search your deck for a trainer card" in t and "into your hand" in t:
        effects.append({"kind": "search_trainer"})
        return effects

    # Wally's Compassion: heal a Mega Evolution Pokémon ex, then return its Energy.
    if "heal all damage" in t and "mega evolution" in t and "energy attached" in t:
        effects.append({"kind": "heal_mega_return_energy"})
        return effects

    # Max Potion. "If you do" (current errata) and "Then, discard all Energy attached"
    # both discard Energy only after a heal. The Mega sentence above is not this card.
    if "heal all damage" in t and "mega evolution" not in t:
        effects.append(
            {
                "kind": "heal_all",
                "discard_energy": "discard all energy" in t,
            }
        )
        return effects

    # Poké Pad ME02.5 198: a Pokémon without a Rule Box, not a look-N.
    if "search your deck for a pokemon" in t and "rule box" in t and "doesn't have" in t:
        effects.append({"kind": "search_pokemon_no_rule_box"})
        return effects

    crushing = _crushing_thorn_trainer(t)
    if crushing:
        effects.append(crushing)
        return effects

    # Penny, Turo, AZ, Cheren's Care, Mr. Briney's Compassion, Seeker.
    # Damage counters are not cards: leaving play clears them.
    bounce = _return_pokemon_to_hand_effect(t)
    if bounce:
        effects.append(bounce)
        return effects

    # Boss's Orders: the same hook as an on-evolve gust, with no HP filter.
    # The HP-limited sentence stays on the ability parser.
    if "switch in 1 of your opponent's benched" in t and "hp or less" not in t:
        effects.append({"kind": "force_opponent_active", "trigger": "play"})

    return effects


def _return_pokemon_to_hand_effect(t: str) -> dict[str, Any] | None:
    """Printed bounce Supporters. The sentence decides targets and attachments."""
    if "into your hand" not in t and "to your hand" not in t and "to his or her hand" not in t:
        return None
    both_bench = (
        "benched pokemon" in t
        and "each" in t
        and "return" in t
        and "supporter" not in t
        and "discard pile" not in t
    )
    if both_bench:
        return {
            "kind": "return_pokemon_to_hand",
            "bench_only": True,
            "both_players": True,
            "attachments": "hand",
        }
    if "excluding pokemon-ex" in t and "return that pokemon" in t:
        return {
            "kind": "return_pokemon_to_hand",
            "exclude_ex": True,
            "attachments": "hand",
        }
    discards_attached = "discard all" in t and "attached" in t
    if re.search(r"put 1 of your pokemon into your hand", t) and discards_attached:
        return {
            "kind": "return_pokemon_to_hand",
            "attachments": "discard",
        }
    if "basic pokemon" in t and "all attached cards into your hand" in t and "put 1 of your" in t:
        return {
            "kind": "return_pokemon_to_hand",
            "basic_only": True,
            "attachments": "hand",
        }
    if "damage counter" in t and "attached" in t and "colorless" in t and "put 1 of your" in t:
        return {
            "kind": "return_pokemon_to_hand",
            "colorless_only": True,
            "require_damage": True,
            "attachments": "hand",
        }
    return None


def _crushing_thorn_trainer(t: str) -> dict[str, Any] | None:
    """Trainers from the Worlds 2024 Crushing Thorn list. The sentence is the effect."""
    look = re.search(r"look at the top (\d+)", t)
    if look and "supporter" in t and "energy card" not in t and "put it into your hand" in t:
        return {"kind": "look_top_take", "look": int(look.group(1)), "want": "supporter"}
    if look and "energy card" in t and "stadium" not in t and "put it into your hand" in t:
        return {"kind": "look_top_take", "look": int(look.group(1)), "want": "energy"}
    if "flip a coin" in t and "switch in" in t and "opponent" in t and "benched" in t:
        return {"kind": "coin_gust"}
    if "switch in 1 of your opponent's benched" in t and "switch your active" in t:
        return {"kind": "gust_and_switch"}
    if "future" in t and "search your deck" in t and "discard" in t and "in order to use" in t:
        return {
            "kind": "search_future",
            "count": int(re.search(r"up to (\d+)", t).group(1) if re.search(r"up to (\d+)", t) else 2),
            "discard": 1,
        }
    if "until the end of your turn" in t and "no abilities" in t and "opponent" in t:
        return {"kind": "blank_opponent_active_abilities"}
    if "search your deck" in t and "stadium" in t and "energy card" in t:
        return {"kind": "search_stadium_and_energy"}
    if "energy attached to your opponent" in t and "into their hand" in t and "attach an energy" in t:
        return {"kind": "swap_active_energy_with_hand"}
    if "lost zone" in t and "pokemon tool" in t and "stadium" in t and "discard pile" in t:
        return {"kind": "lost_vacuum"}
    return None


def is_double_colorless(card: Any) -> bool:
    return "double colorless" in (getattr(card, "name", "") or "").lower()


def is_double_turbo(card: Any) -> bool:
    return "double turbo" in (getattr(card, "name", "") or "").lower()


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
        or is_double_turbo(card)
        or is_boomerang_energy(card)
        or is_telepathic_energy(card)
        or is_enriching_energy(card)
        or is_speed_lightning_energy(card)
        or is_draw_energy(card)
    ):
        return True
    return (getattr(card, "stage", "") or "").lower() == "special"


_TYPE_WORD = (
    "grass|fire|water|lightning|psychic|fighting|darkness|metal|fairy|colorless|dragon"
)


def _attack_spread_effects(t: str) -> list[dict[str, Any]]:
    """Attack sentences whose numbers stay inside the effect dict."""
    flat = _flat_text(t)
    effects: list[dict[str, Any]] = []
    rain = re.search(
        rf"discard any amount of ({_TYPE_WORD}) energy from this pokemon\."
        rf".*for each energy you discarded in this way.*do (\d+) damage to it",
        flat,
    )
    if rain:
        effects.append(
            {
                "kind": "discard_typed_energy_damage_per_card",
                "energy_type": rain.group(1).title(),
                "per_card": int(rain.group(2)),
                "repeat_ok": "more than once" in flat,
                "ignore_wr_all": "isn't affected by weakness" in flat or "not affected by weakness" in flat,
            }
        )
    times = re.search(
        rf"does (\d+) damage times the amount of ({_TYPE_WORD}) energy attached to this pokemon",
        flat,
    )
    if times:
        effects.append(
            {
                "kind": "attached_energy_times",
                "per": int(times.group(1)),
                "energy_type": times.group(2).title(),
            }
        )
    extra = re.search(
        rf"at least (\d+) extra ({_TYPE_WORD}) energy attached to it "
        rf"\(in addition to this attack's cost\).*paralyzed",
        flat,
    )
    if extra:
        effects.append(
            {
                "kind": "paralyze_if_extra_energy",
                "extra": int(extra.group(1)),
                "energy_type": extra.group(2).title(),
            }
        )
    discard_typed = re.search(rf"then, discard all ({_TYPE_WORD}) energy from this pokemon", flat)
    if not discard_typed:
        discard_typed = re.search(rf"discard all ({_TYPE_WORD}) energy from this pokemon", flat)
    if discard_typed and "any amount" not in flat:
        effects.append(
            {
                "kind": "discard_all_typed_energy",
                "energy_type": discard_typed.group(1).title(),
            }
        )
    flip = re.search(
        r"does (\d+) damage to each of your opponent's pokemon that has any damage counters on it",
        flat,
    )
    if flip:
        effects.append(
            {
                "kind": "damage_each_with_counters",
                "amount": int(flip.group(1)),
                "ignore_wr_bench": "don't apply weakness and resistance for benched" in flat
                or "do not apply weakness and resistance for benched" in flat,
            }
        )
    many = re.search(r"does (\d+) damage to (\d+) of your opponent's pokemon", flat)
    if many and "damage counters" not in flat:
        effects.append(
            {
                "kind": "damage_n_opponent_pokemon",
                "amount": int(many.group(1)),
                "count": int(many.group(2)),
                "ignore_wr_bench": "don't apply weakness and resistance for benched" in flat
                or "do not apply weakness and resistance for benched" in flat,
                "repeat_ok": "more than once" in flat,
            }
        )
    if re.search(r"discard all energy from this pokemon", flat) and not re.search(
        rf"discard all ({_TYPE_WORD}) energy from this pokemon", flat
    ):
        effects.append({"kind": "discard_all_energy"})
    if "choose an attack from a dragon pokemon in your discard pile and use it as this attack" in flat:
        effects.append({"kind": "copy_discard_dragon_attack"})
    if "can't use more than 1 vstar power" in flat or "cannot use more than 1 vstar power" in flat:
        effects.append({"kind": "once_per_game", "flag": "vstar"})
    roar = re.search(r"discard the top (\d+) cards of your deck", flat)
    if roar and "energy" in flat and "attach them to this pokemon" in flat:
        effects.append({"kind": "discard_top_attach_energy", "count": int(roar.group(1))})
    bench_one = re.search(r"does (\d+) damage to 1 of your opponent's benched pokemon", flat)
    if bench_one:
        effects.append(
            {
                "kind": "damage_one_pokemon",
                "amount": int(bench_one.group(1)),
                "bench_only": True,
                "ignore_wr_bench": "don't apply weakness and resistance for benched" in flat
                or "do not apply weakness and resistance for benched" in flat,
            }
        )
    return effects


def _extend_expanded_ability_effects(t: str, effects: list[dict[str, Any]]) -> None:
    flat = _flat_text(t)
    sky = re.search(r"each player can have (\d+) pokemon on (?:his or her|their) bench", flat)
    if sky:
        leave = re.search(r"has (\d+) pokemon on the bench", flat)
        effects.append(
            {
                "kind": "stadium_bench_limit",
                "limit": int(sky.group(1)),
                "raises": True,
                "leave_limit": int(leave.group(1)) if leave else None,
                "owner_discards_first": "owner of this card discards first" in flat,
            }
        )
    area = re.search(
        r"each player who has any tera pokemon in play can have up to (\d+) pokemon on their bench",
        flat,
    )
    if area:
        lose = re.search(
            r"no longer has any tera pokemon in play, that player discards pokemon from their bench until they have (\d+)",
            flat,
        )
        leave = re.search(
            r"when this card leaves play, both players discard pokemon from their bench until they have (\d+)",
            flat,
        )
        effects.append(
            {
                "kind": "stadium_bench_limit",
                "limit": int(area.group(1)),
                "raises": True,
                "require_tera": True,
                "lose_tera_limit": int(lose.group(1)) if lose else None,
                "leave_limit": int(leave.group(1)) if leave else None,
                "owner_discards_first": "the player who played this card discards first" in flat,
            }
        )
    mountain = re.search(
        rf"attacks of ({_TYPE_WORD}) pokemon \(both yours and your opponent's\) cost \1 less",
        flat,
    )
    if mountain:
        effects.append(
            {
                "kind": "stadium_attack_cost_less",
                "pokemon_type": mountain.group(1).title(),
                "energy_type": mountain.group(1).title(),
                "both_players": True,
            }
        )
    if "prevent all effects of that card done to this stadium" in flat:
        effects.append({"kind": "stadium_item_safe"})
    bomb = re.search(
        r"attach (?:up to )?(\d+) energy cards from your discard pile to your pokemon, except pokemon-gx or pokemon-ex",
        flat,
    )
    if bomb:
        effects.append(
            {
                "kind": "attach_energy_from_discard_except_gx_ex",
                "count": int(bomb.group(1)),
                "ko_self": "this pokemon is knocked out" in flat,
                "once_per_turn": "once during your turn" in flat,
            }
        )
    dance = re.search(
        rf"choose (\d+) of your benched pokemon and attach a ({_TYPE_WORD}) energy card "
        rf"from your discard pile to each",
        flat,
    )
    if dance and "lost zone" in flat:
        effects.append(
            {
                "kind": "bench_attach_discard_energy_lost_zone",
                "count": int(dance.group(1)),
                "energy_type": dance.group(2).title(),
                "once_per_turn": "once during your turn" in flat,
                "require_bench": "on your bench" in flat,
            }
        )
    zone = re.search(
        rf"each of your pokemon that has any ({_TYPE_WORD}) energy attached to it has no retreat cost",
        flat,
    )
    if zone:
        effects.append({"kind": "retreat_zero_if_typed_energy", "energy_type": zone.group(1).title()})
    if "if this pokemon has any energy attached to it, it has no retreat cost" in flat:
        effects.append({"kind": "retreat_zero_if_any_energy"})


def _extend_conditional_energy_effects(t: str, effects: list[dict[str, Any]]) -> None:
    flat = _flat_text(t)
    every = re.search(
        r"provides every type of energy,? but provides only (\d+) energy at a time",
        flat,
    )
    if every:
        effects.append(
            {
                "kind": "provides_any_when",
                "count": int(every.group(1)),
                "requires_behind": "more prize cards remaining" in flat,
                "exclude_gx_ex": "isn't a pokemon-gx or pokemon-ex" in flat
                or "is not a pokemon-gx or pokemon-ex" in flat,
                "evolution_only": "evolution pokemon" in flat,
                "no_rule_box": "doesn't have a rule box" in flat or "does not have a rule box" in flat,
                "dragon_only": "dragon" in flat and "only while" in flat,
            }
        )
    if "discard this card" in flat and "other than a dragon" in flat:
        effects.append({"kind": "discard_if_not_dragon"})


def _expanded_trainer_effects(t: str) -> list[dict[str, Any]]:
    flat = _flat_text(t)
    effects: list[dict[str, Any]] = []
    look = re.search(
        r"look at the top (\d+) cards of your deck and put 1 of them into your hand",
        flat,
    )
    if look and "discard the other" in flat:
        effects.append({"kind": "look_top_keep_one", "look": int(look.group(1))})
        return effects
    rescue = re.search(r"put (\d+) pokemon from your discard pile into your deck", flat)
    if "put a pokemon from your discard pile into your hand" in flat and rescue:
        effects.append({"kind": "rescue_stretcher", "shuffle_count": int(rescue.group(1))})
        return effects
    charge = re.search(r"shuffle (\d+) special energy cards from your discard pile into your deck", flat)
    if charge:
        effects.append({"kind": "shuffle_special_energy_to_deck", "count": int(charge.group(1))})
        return effects
    if "pokemon tool" in flat and "stadium" in flat and "from play" in flat and "discard" in flat:
        n = re.search(r"up to (\d+)", flat)
        effects.append({"kind": "discard_tools_and_stadiums", "count": int(n.group(1) if n else 1)})
        return effects
    if (
        "more prize cards remaining" in flat
        and "cost colorless less" in flat
        and "attached" in flat
    ):
        effects.append({"kind": "cost_colorless_less_if_behind"})
        return effects
    band = re.search(
        r"do (\d+) more damage to your opponent's active pokemon-gx or active pokemon-ex",
        flat,
    )
    if band:
        effects.append({"kind": "tool_damage_vs_gx_ex", "amount": int(band.group(1))})
        return effects
    if (
        "switch 1 of your opponent's benched pokemon with their active" in flat
        and "switch your active" in flat
    ):
        effects.append({"kind": "gust_and_switch"})
        return effects
    return effects


def host_name(host: Any) -> str:
    return (getattr(host, "name", "") or "").lower().rstrip()


def host_has_rule_box(host: Any) -> bool:
    """Pokémon ex, Pokémon-EX, Pokémon-GX, V, VSTAR, and VMAX."""
    name = host_name(host)
    if not name:
        return False
    return (
        name.endswith(" ex")
        or name.endswith("-ex")
        or name.endswith(" gx")
        or name.endswith("-gx")
        or " vmax" in name
        or name.endswith(" vmax")
        or "vstar" in name
        or name.endswith(" v")
        or " v " in name
    )


def host_is_gx_or_hyphen_ex(host: Any) -> bool:
    """Pokémon-GX / Pokémon-EX as printed on Sun & Moon cards.

    A modern name ending in " ex" (Mew ex) is not Pokémon-EX.
    """
    name = host_name(host)
    return name.endswith("-gx") or name.endswith(" gx") or name.endswith("-ex")


def host_is_evolution(host: Any) -> bool:
    stage = (getattr(host, "stage", "") or "").lower().replace(" ", "")
    return bool(stage) and stage not in {"basic"}


def host_is_dragon(host: Any) -> bool:
    return any(str(t).lower() == "dragon" for t in (getattr(host, "types", None) or []))


def _flat_text(t: str) -> str:
    return re.sub(r"\s+", " ", t or "")


def _any_energy_applies(spec: dict[str, Any], *, prizes_behind: bool, host: Any) -> bool:
    if spec.get("requires_behind") and not prizes_behind:
        return False
    if host is None:
        return False
    if spec.get("exclude_gx_ex") and host_is_gx_or_hyphen_ex(host):
        return False
    if spec.get("evolution_only") and not host_is_evolution(host):
        return False
    if spec.get("no_rule_box") and host_has_rule_box(host):
        return False
    if spec.get("dragon_only") and not host_is_dragon(host):
        return False
    return True


def _conditional_energy_units(card: Any, *, prizes_behind: bool, host: Any) -> list[str] | None:
    spec = next(
        (e for e in parse_energy_effects(getattr(card, "text", "") or "") if e.get("kind") == "provides_any_when"),
        None,
    )
    if spec is None:
        return None
    count = int(spec.get("count") or 0)
    if _any_energy_applies(spec, prizes_behind=prizes_behind, host=host):
        return ["Any"] * count
    if spec.get("dragon_only"):
        # Not attached yet: the card can still be put on a Dragon.
        if host is None:
            return ["Any"] * count
        return []
    return ["Colorless"]


def energy_provided(card: Any, *, prizes_behind: bool = False, host: Any = None) -> list[str]:
    """Energy units one attached card pays. DCE pays two Colorless.

    Conditional special energy reads its own sentence. Defaults keep older
    callers on the printed Colorless (or typed) line.
    """
    if is_double_colorless(card) or is_double_turbo(card):
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
    conditional = _conditional_energy_units(card, prizes_behind=prizes_behind, host=host)
    if conditional is not None:
        return conditional
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
    """Any pays a specific type or Colorless. It is the "every type" unit."""
    pool = [p for p in attached_types if p != "Any"]
    wild = sum(1 for p in attached_types if p == "Any")
    for need in [c for c in cost if c != "Colorless"]:
        if need in pool:
            pool.remove(need)
        elif wild:
            wild -= 1
        else:
            return False
    colorless = sum(1 for c in cost if c == "Colorless")
    return len(pool) + wild >= colorless


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
