from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from app.engine.effects import can_pay_energy, resistance_reduce, weakness_multiplier
from app.engine.models import Card, FamilyRules
from app.engine.strategies import StrategySpec

ST_PARALYZED = 1
ST_ASLEEP = 2
ST_CONFUSED = 4
ST_POISONED = 8
ST_BURNED = 16
VOLATILE = ST_PARALYZED | ST_ASLEEP | ST_CONFUSED


@dataclass
class Pokemon:
    card_i: int
    damage: int = 0
    energy: list[int] = field(default_factory=list)
    status: int = 0
    played_turn: int = 0

    @property
    def remaining(self) -> int:
        return self.damage


@dataclass
class Player:
    name: str
    cards: list[Card]
    deck: list[int]
    hand: list[int]
    prizes: list[int]
    discard: list[int] = field(default_factory=list)
    active: Pokemon | None = None
    bench: list[Pokemon] = field(default_factory=list)
    supporter_used: bool = False
    energy_attached: bool = False
    mulligans: int = 0
    prizes_taken: int = 0
    first_attacks_turn: dict[str, int] = field(default_factory=dict)

    def in_play(self) -> list[Pokemon]:
        mons = []
        if self.active:
            mons.append(self.active)
        mons.extend(self.bench)
        return mons

    def card(self, idx: int) -> Card:
        return self.cards[idx]


@dataclass
class GameResult:
    winner: str  # "a", "b", "tie"
    reason: str
    turns: int
    first_player: str
    events: dict[str, int]
    opening_a: list[str]
    opening_b: list[str]
    prized_a: list[str]
    prized_b: list[str]
    trace: list[str]
    mulligans_a: int
    mulligans_b: int
    prizes_taken_a: int
    prizes_taken_b: int


class Game:
    def __init__(
        self,
        cards_a: list[Card],
        cards_b: list[Card],
        rules: FamilyRules,
        strat_a: StrategySpec,
        strat_b: StrategySpec,
        rng: random.Random,
        trace: bool = False,
    ) -> None:
        self.rules = rules
        self.rng = rng
        self.trace_on = trace
        self.trace: list[str] = []
        self.events: dict[str, int] = {}
        self.turn = 0
        self.strats = {"a": strat_a, "b": strat_b}
        self.players = {
            "a": self._deal("A", cards_a, strat_a),
            "b": self._deal("B", cards_b, strat_b),
        }
        self.first = "a" if rng.random() < 0.5 else "b"
        self.current = self.first

    def _log(self, message: str) -> None:
        if self.trace_on:
            self.trace.append(message)

    def _bump(self, key: str, n: int = 1) -> None:
        self.events[key] = self.events.get(key, 0) + n

    def _deal(self, name: str, cards: list[Card], strat: StrategySpec) -> Player:
        order = list(range(len(cards)))
        self.rng.shuffle(order)
        player = Player(name=name, cards=cards, deck=order, hand=[], prizes=[])
        self._opening(player, strat)
        return player

    def _draw(self, player: Player, n: int = 1) -> list[int]:
        drawn = []
        for _ in range(n):
            if not player.deck:
                return drawn
            card_i = player.deck.pop()
            player.hand.append(card_i)
            drawn.append(card_i)
        return drawn

    def _has_basic(self, player: Player, zone: list[int]) -> bool:
        return any(player.card(i).is_basic for i in zone)

    def _opening(self, player: Player, strat: StrategySpec) -> None:
        hand_n = self.rules.opening_hand
        while True:
            self._draw(player, hand_n)
            if self._has_basic(player, player.hand) or player.mulligans >= 8:
                break
            player.mulligans += 1
            player.deck.extend(player.hand)
            player.hand.clear()
            self.rng.shuffle(player.deck)
        prize_n = min(self.rules.prize_count, len(player.deck))
        for _ in range(prize_n):
            player.prizes.append(player.deck.pop())
        basics = [i for i in player.hand if player.card(i).is_basic]
        if not basics:
            return
        active_i = self._pick_starter(player, basics, strat)
        player.hand.remove(active_i)
        player.active = Pokemon(card_i=active_i, played_turn=0)
        remaining = [i for i in player.hand if player.card(i).is_basic]
        self.rng.shuffle(remaining)
        for card_i in remaining[: self.rules.bench_size]:
            player.hand.remove(card_i)
            player.bench.append(Pokemon(card_i=card_i, played_turn=0))

    def _pick_starter(self, player: Player, basics: list[int], strat: StrategySpec) -> int:
        def score(i: int) -> float:
            card = player.card(i)
            value = float(card.hp or 50)
            if any("paralyze" in (atk.text or "").lower() for atk in card.attacks):
                value += 90 * strat.prefer_status
            if card.name in strat.protect:
                value += 40
            return value

        return max(basics, key=score)

    def names(self, player: Player, idxs: list[int]) -> list[str]:
        return [player.card(i).name for i in idxs]

    def play(self) -> GameResult:
        a = self.players["a"]
        b = self.players["b"]
        opening_a = self.names(a, list(a.hand) + ([a.active.card_i] if a.active else []) + [p.card_i for p in a.bench])
        # True opening hand is the 7 cards before placing — reconstruct from remaining + in play + not prizes/deck.
        # We stored after setup. Capture prize + in-play + hand is not the opening 7.
        # Track opening before placing: we didn't. Approximate: cards not left in deck after prizes
        # Better: record during _opening. Patch by storing on player.
        result_opening_a = getattr(a, "_opening_names", self.names(a, a.hand))
        result_opening_b = getattr(b, "_opening_names", self.names(b, b.hand))

        if not a.active:
            return self._finish("b", "a had no Basic Pokémon")
        if not b.active:
            return self._finish("a", "b had no Basic Pokémon")

        self._log(f"First player: {self.first.upper()}")
        for _ in range(self.rules.max_turns):
            self.turn += 1
            who = self.current
            if self._take_turn(who):
                break
            self.current = "b" if who == "a" else "a"
        else:
            self._finish_by_damage()

        return GameResult(
            winner=self.winner,
            reason=self.reason,
            turns=self.turn,
            first_player=self.first,
            events=self.events,
            opening_a=result_opening_a,
            opening_b=result_opening_b,
            prized_a=self.names(a, a.prizes),
            prized_b=self.names(b, b.prizes),
            trace=self.trace,
            mulligans_a=a.mulligans,
            mulligans_b=b.mulligans,
            prizes_taken_a=a.prizes_taken,
            prizes_taken_b=b.prizes_taken,
        )

    def _finish(self, winner: str, reason: str) -> GameResult:
        self.winner = winner
        self.reason = reason
        a = self.players["a"]
        b = self.players["b"]
        return GameResult(
            winner=winner,
            reason=reason,
            turns=self.turn,
            first_player=self.first,
            events=self.events,
            opening_a=getattr(a, "_opening_names", []),
            opening_b=getattr(b, "_opening_names", []),
            prized_a=self.names(a, a.prizes),
            prized_b=self.names(b, b.prizes),
            trace=self.trace,
            mulligans_a=a.mulligans,
            mulligans_b=b.mulligans,
            prizes_taken_a=a.prizes_taken,
            prizes_taken_b=b.prizes_taken,
        )

    def _finish_by_damage(self) -> None:
        a = self.players["a"]
        b = self.players["b"]
        a_hp = sum(max(0, a.card(p.card_i).hp - p.damage) for p in a.in_play())
        b_hp = sum(max(0, b.card(p.card_i).hp - p.damage) for p in b.in_play())
        if a.prizes_taken != b.prizes_taken:
            winner = "a" if a.prizes_taken > b.prizes_taken else "b"
            self.winner, self.reason = winner, "more prizes at turn limit"
        elif a_hp != b_hp:
            winner = "a" if a_hp > b_hp else "b"
            self.winner, self.reason = winner, "more remaining HP at turn limit"
        else:
            self.winner, self.reason = "tie", "turn limit"

    def _take_turn(self, who: str) -> bool:
        me = self.players[who]
        foe = self.players["b" if who == "a" else "a"]
        me.supporter_used = False
        me.energy_attached = False
        self._between_turns(me)
        if self._check_ko(me, foe, who):
            return True

        first_turn = self.turn == 1
        skip_draw = first_turn and who == self.first and self.rules.first_player_no_draw
        if not skip_draw:
            drawn = self._draw(me, 1)
            if not drawn:
                self.winner, self.reason = ("b" if who == "a" else "a"), f"{who} decked out"
                return True

        self._play_basics(me)
        self._play_trainers(me, foe, who)
        self._evolve(me)
        self._attach_energy(me, who)
        self._maybe_retreat(me, foe, who)

        can_attack = not (first_turn and who == self.first and self.rules.first_player_no_attack)
        if can_attack and me.active and not (me.active.status & (ST_PARALYZED | ST_ASLEEP)):
            self._attack(me, foe, who)
            if self._check_ko(foe, me, "b" if who == "a" else "a"):
                return True
            if self._check_ko(me, foe, who):
                return True

        if me.active:
            me.active.status &= ~ST_PARALYZED
        return False

    def _between_turns(self, me: Player) -> None:
        if not me.active:
            return
        mon = me.active
        if mon.status & ST_POISONED:
            mon.damage += 10
            self._bump("poison_ticks")
        if mon.status & ST_BURNED:
            mon.damage += 20
            self._bump("burn_ticks")
            if self.rng.random() < 0.5:
                mon.status &= ~ST_BURNED
        if mon.status & ST_ASLEEP:
            if self.rng.random() < 0.5:
                mon.status &= ~ST_ASLEEP

    def _play_basics(self, me: Player) -> None:
        strat = self.strats["a" if me.name == "A" else "b"]
        if self.rng.random() > strat.bench_fill and len(me.bench) >= 1:
            return
        basics = [i for i in list(me.hand) if me.card(i).is_basic]
        while basics and len(me.bench) < self.rules.bench_size:
            card_i = basics.pop(0)
            me.hand.remove(card_i)
            me.bench.append(Pokemon(card_i=card_i, played_turn=self.turn))
            self._log(f"{me.name} benches {me.card(card_i).name}")

    def _evolve(self, me: Player) -> None:
        strat = self.strats["a" if me.name == "A" else "b"]
        if self.rng.random() > strat.evolve_asap:
            return
        changed = True
        while changed:
            changed = False
            for evo_i in list(me.hand):
                evo = me.card(evo_i)
                if not evo.is_pokemon or not evo.evolves_from:
                    continue
                target = self._find_evolve_target(me, evo)
                if target is None:
                    continue
                if target.played_turn == self.turn and not self._has_named(me, "Rare Candy"):
                    continue
                self._do_evolve(me, target, evo_i)
                changed = True
                break

    def _find_evolve_target(self, me: Player, evo: Card) -> Pokemon | None:
        want = (evo.evolves_from or "").lower()
        for mon in me.in_play():
            if me.card(mon.card_i).name.lower() == want:
                return mon
        if self._has_named(me, "Rare Candy") and (evo.stage or "").lower() in {"stage2", "stage 2"}:
            # Find a basic in the same family by name prefix is unreliable; try dex later.
            for mon in me.in_play():
                base = me.card(mon.card_i)
                if base.is_basic and self._same_line(base, evo):
                    return mon
        return None

    def _same_line(self, basic: Card, evo: Card) -> bool:
        if evo.evolves_from and evo.evolves_from.lower() == basic.name.lower():
            return True
        # Weak fallback: shared type and basic hp lower.
        return bool(basic.types and evo.types and basic.types[0] == evo.types[0] and basic.is_basic)

    def _do_evolve(self, me: Player, target: Pokemon, evo_i: int) -> None:
        me.hand.remove(evo_i)
        me.discard.append(target.card_i)
        if self._has_named(me, "Rare Candy") and (me.card(evo_i).stage or "").lower() in {"stage2", "stage 2"}:
            candy = self._first_named(me, "Rare Candy")
            if candy is not None:
                me.hand.remove(candy)
                me.discard.append(candy)
                self._bump("rare_candy")
        target.card_i = evo_i
        target.played_turn = self.turn
        self._log(f"{me.name} evolves into {me.card(evo_i).name}")

    def _has_named(self, me: Player, name: str) -> bool:
        return any(me.card(i).name.lower() == name.lower() for i in me.hand)

    def _first_named(self, me: Player, name: str) -> int | None:
        for i in me.hand:
            if me.card(i).name.lower() == name.lower():
                return i
        return None

    def _play_trainers(self, me: Player, foe: Player, who: str) -> None:
        for _ in range(10):
            found = None
            for card_i in me.hand:
                card = me.card(card_i)
                if not card.is_trainer or card.name.lower() == "rare candy":
                    continue
                if card.is_supporter and me.supporter_used:
                    continue
                found = card_i
                break
            if found is None:
                return
            card = me.card(found)
            if card.is_supporter:
                me.supporter_used = True
            me.hand.remove(found)
            me.discard.append(found)
            self._resolve_trainer(me, foe, card)
            self._log(f"{me.name} plays {card.name}")

    def _resolve_trainer(self, me: Player, foe: Player, card: Card) -> None:
        name = card.name.lower()
        if name in {"hop"}:
            self._draw(me, 3)
        elif name in {"youngster", "shauna"}:
            me.deck.extend(me.hand)
            me.hand.clear()
            self.rng.shuffle(me.deck)
            self._draw(me, 5)
        elif name in {"quick ball", "great ball", "nest ball", "nesting ball"}:
            self._search(me, lambda c: c.is_pokemon and (c.is_basic if "nest" in name or "quick" in name else True))
        elif name == "energy search":
            self._search(me, lambda c: c.is_energy)
        elif name == "energy retrieval":
            found = [i for i in me.discard if me.card(i).is_energy][:2]
            for i in found:
                me.discard.remove(i)
                me.hand.append(i)
        elif name == "picnic basket":
            for mon in me.in_play():
                mon.damage = max(0, mon.damage - 30)
        else:
            self._draw(me, 1)

    def _search(self, me: Player, pred) -> None:
        for idx, card_i in enumerate(list(me.deck)):
            if pred(me.card(card_i)):
                me.deck.pop(idx)
                me.hand.append(card_i)
                self.rng.shuffle(me.deck)
                return

    def _attach_energy(self, me: Player, who: str) -> None:
        if not me.active or me.energy_attached:
            return
        strat = self.strats[who]
        target = self._energy_target(me, strat)
        energy_i = self._choose_energy_card(me, target, strat)
        if energy_i is None:
            return
        me.hand.remove(energy_i)
        target.energy.append(energy_i)
        me.energy_attached = True
        src = me.card(energy_i)
        self._log(f"{me.name} attaches {src.name} as {src.as_energy_type} energy to {me.card(target.card_i).name}")
        if src.is_pokemon:
            self._bump("pokemon_as_energy")

    def _energy_target(self, me: Player, strat: StrategySpec) -> Pokemon:
        assert me.active
        return me.active

    def _choose_energy_card(self, me: Player, target: Pokemon, strat: StrategySpec) -> int | None:
        need = self._needed_types(me, target)
        energies = [i for i in me.hand if me.card(i).is_energy]
        if energies:
            for i in energies:
                et = me.card(i).as_energy_type
                if et in need or et == "Colorless" or not need:
                    return i
            return energies[0]
        if not self.rules.pokemon_as_energy:
            return None
        if self.rng.random() > strat.attach_pokemon_as_energy:
            return None
        protect = {n.lower() for n in strat.protect}
        candidates = []
        for i in me.hand:
            card = me.card(i)
            if not card.is_pokemon:
                continue
            if card.name.lower() in protect:
                continue
            # Keep at least one copy of a basic line in hand/play if it is the only fighter.
            et = card.as_energy_type
            score = 2 if et in need else 0
            score -= 1 if card.hp >= 120 else 0
            candidates.append((score, i))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        return candidates[0][1] if candidates[0][0] >= 0 or need else None

    def _needed_types(self, me: Player, target: Pokemon) -> set[str]:
        card = me.card(target.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in target.energy]
        needed: set[str] = set()
        for atk in card.attacks:
            if can_pay_energy(attached, atk.cost):
                continue
            for c in atk.cost:
                if c != "Colorless":
                    needed.add(c)
        if not needed and card.types:
            needed.add(card.types[0])
        return needed

    def _maybe_retreat(self, me: Player, foe: Player, who: str) -> None:
        if not me.active or not me.bench:
            return
        if me.active.status & (ST_PARALYZED | ST_ASLEEP):
            return
        strat = self.strats[who]
        incoming_idx = None
        if foe.active and strat.prefer_status >= 0.6:
            active_card = me.card(me.active.card_i)
            active_has_status = any("paralyze" in (a.text or "").lower() for a in active_card.attacks)
            if not active_has_status:
                for idx, mon in enumerate(me.bench):
                    bcard = me.card(mon.card_i)
                    if any("paralyze" in (a.text or "").lower() for a in bcard.attacks):
                        incoming_idx = idx
                        break
        hp_left = me.card(me.active.card_i).hp - me.active.damage
        if incoming_idx is None and hp_left > 30:
            return
        cost = me.card(me.active.card_i).retreat
        if len(me.active.energy) < cost:
            return
        for _ in range(cost):
            me.discard.append(me.active.energy.pop())
        incoming = me.bench.pop(0 if incoming_idx is None else incoming_idx)
        me.bench.append(me.active)
        me.active = incoming
        self._log(f"{me.name} retreats into {me.card(incoming.card_i).name}")

    def _attack(self, me: Player, foe: Player, who: str) -> None:
        if not me.active or not foe.active:
            return
        strat = self.strats[who]
        atk = self._choose_attack(me, foe, strat)
        if atk is None:
            return
        attacker = me.card(me.active.card_i)
        defender = me.card(foe.active.card_i) if False else foe.card(foe.active.card_i)
        self._bump(f"attack:{attacker.name}:{atk.name}")
        self._bump(f"attack_by:{who}")

        if me.active.status & ST_CONFUSED:
            if self.rng.random() < 0.5:
                me.active.damage += 30
                self._log(f"{attacker.name} hit itself in confusion")
                return

        for effect in atk.effects:
            if effect.get("kind") == "coin_whiff" and self.rng.random() < 0.5:
                self._log(f"{attacker.name} used {atk.name} but it did nothing")
                return

        dmg = atk.damage
        if any(e.get("kind") == "times" for e in atk.effects):
            dmg = atk.damage * max(1, sum(1 for i in me.discard if "tatsu" in me.card(i).name.lower()))
        for effect in atk.effects:
            if effect.get("kind") == "deck_count_bonus" and len(me.deck) <= int(effect.get("max_deck") or 0):
                dmg += int(effect.get("bonus") or 0)
        dmg *= weakness_multiplier(defender.weaknesses, attacker.types)
        dmg = max(0, dmg - resistance_reduce(defender.resistances, attacker.types))
        foe.active.damage += dmg
        self._bump("damage_dealt", dmg)
        self._log(f"{attacker.name} used {atk.name} for {dmg} on {defender.name}")

        if attacker.name not in me.first_attacks_turn:
            me.first_attacks_turn[attacker.name] = self.turn

        for effect in atk.effects:
            if effect.get("kind") == "status":
                if effect.get("coin") and self.rng.random() < 0.5:
                    self._bump(f"status_fail:{attacker.name}:{defender.name}:{effect['status']}")
                    continue
                self._apply_status(foe.active, effect["status"])
                self._bump(f"status:{attacker.name}:{defender.name}:{effect['status']}")
                self._bump(f"status:{effect['status']}")
            elif effect.get("kind") == "heal":
                me.active.damage = max(0, me.active.damage - int(effect.get("amount") or 0))
            elif effect.get("kind") == "draw":
                self._draw(me, int(effect.get("amount") or 1))
            elif effect.get("kind") == "call_family":
                self._search(me, lambda c: c.is_basic)
                self._play_basics(me)
            elif effect.get("kind") == "swallow_energy":
                self._swallow_energy(me, int(effect.get("look") or 5))
            elif effect.get("kind") == "bench_damage_counters":
                self._bench_damage_counters(foe, int(effect.get("counters") or 1))

    def _swallow_energy(self, me: Player, look: int) -> None:
        """Supplemental Swallow-Up: attach Basic Energy from the top of the deck.

        Under Family Cup, Pokémon may also be attached as matching Basic Energy.
        """
        if not me.active:
            return
        protect = {n.lower() for n in self.strats["a" if me.name == "A" else "b"].protect}
        taken = min(look, len(me.deck))
        top = [me.deck.pop(0) for _ in range(taken)]
        keep: list[int] = []
        attached = 0
        for card_i in top:
            card = me.card(card_i)
            attachable = card.is_energy or (
                self.rules.pokemon_as_energy
                and card.is_pokemon
                and card.as_energy_type
                and card.name.lower() not in protect
            )
            if attachable:
                me.active.energy.append(card_i)
                attached += 1
                if card.is_pokemon:
                    self._bump("pokemon_as_energy")
                self._bump("swallow_energy")
                self._log(f"{me.name} swallows {card.name} onto {me.card(me.active.card_i).name}")
            else:
                keep.append(card_i)
        me.deck.extend(keep)
        self.rng.shuffle(me.deck)
        if attached:
            self._log(f"{me.name} Supplemental Swallow-Up attached {attached} energy")

    def _bench_damage_counters(self, foe: Player, counters: int) -> None:
        if not foe.bench:
            return
        damage = 10 * max(1, counters)
        # Dump all counters onto the lowest-HP bench Pokémon (simple AI).
        target = min(foe.bench, key=lambda m: foe.card(m.card_i).hp - m.damage)
        target.damage += damage
        self._bump("bench_damage", damage)
        self._log(f"Bench {foe.card(target.card_i).name} took {damage} from Hex-style attack")

    def _choose_attack(self, me: Player, foe: Player, strat: StrategySpec):
        assert me.active and foe.active
        card = me.card(me.active.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in me.active.energy]
        legal = [atk for atk in card.attacks if can_pay_energy(attached, atk.cost)]
        if not legal:
            return None
        foe_name = foe.card(foe.active.card_i).name
        has_big = any(a.damage >= 100 for a in legal)
        best = None
        best_score = -1e9
        for atk in legal:
            score = atk.damage * strat.prefer_damage
            has_status = any(e.get("kind") == "status" for e in atk.effects)
            if has_status:
                score += 40 * strat.prefer_status
                if foe_name in strat.status_targets or foe_name.lower() in {n.lower() for n in strat.status_targets}:
                    score += 50 * strat.prefer_status
            if any(e.get("kind") == "swallow_energy" for e in atk.effects) and not has_big:
                # Charge Dondozo before Hydro Splash is online.
                score += 120 * max(0.4, strat.prefer_damage)
            if any(e.get("kind") == "deck_count_bonus" for e in atk.effects) and len(me.deck) <= 3:
                score += 150
            if any(e.get("kind") == "draw" for e in atk.effects) and atk.damage <= 30:
                score += 15
            if best is None or score > best_score:
                best, best_score = atk, score
        return best

    def _apply_status(self, mon: Pokemon, status: str) -> None:
        bit = {
            "paralyzed": ST_PARALYZED,
            "asleep": ST_ASLEEP,
            "confused": ST_CONFUSED,
            "poisoned": ST_POISONED,
            "burned": ST_BURNED,
        }.get(status)
        if not bit:
            return
        if bit & VOLATILE:
            mon.status &= ~VOLATILE
        mon.status |= bit

    def _check_ko(self, victim_owner: Player, slayer: Player, victim_who: str) -> bool:
        knocked = []
        if victim_owner.active and victim_owner.card(victim_owner.active.card_i).hp <= victim_owner.active.damage:
            knocked.append(("active", victim_owner.active))
        still_bench = []
        for mon in victim_owner.bench:
            if victim_owner.card(mon.card_i).hp <= mon.damage:
                knocked.append(("bench", mon))
            else:
                still_bench.append(mon)
        victim_owner.bench = still_bench
        if not knocked:
            return False
        for where, mon in knocked:
            name = victim_owner.card(mon.card_i).name
            self._discard_mon(victim_owner, mon)
            self._take_prize(slayer)
            self._bump(f"ko:{name}")
            self._log(f"{name} was Knocked Out")
            if slayer.prizes_taken >= self.rules.prize_count or not slayer.prizes:
                slayer_who = "a" if slayer.name == "A" else "b"
                self.winner, self.reason = slayer_who, "took all prize cards"
                return True
        if victim_owner.active and victim_owner.card(victim_owner.active.card_i).hp <= victim_owner.active.damage:
            victim_owner.active = None
        if victim_owner.active is None:
            if not victim_owner.bench:
                slayer_who = "a" if slayer.name == "A" else "b"
                self.winner, self.reason = slayer_who, "opponent has no Pokémon in play"
                return True
            victim_owner.active = victim_owner.bench.pop(0)
        return False

    def _discard_mon(self, player: Player, mon: Pokemon) -> None:
        player.discard.append(mon.card_i)
        player.discard.extend(mon.energy)
        if player.active is mon:
            player.active = None

    def _take_prize(self, player: Player) -> None:
        if player.prizes:
            player.hand.append(player.prizes.pop())
        player.prizes_taken += 1


def _capture_opening(player: Player) -> None:
    # After deal, opening 7 is: hand + active + bench, which together were the opening hand.
    names = [player.card(i).name for i in player.hand]
    if player.active:
        names.append(player.card(player.active.card_i).name)
    names.extend(player.card(p.card_i).name for p in player.bench)
    player._opening_names = names  # type: ignore[attr-defined]


def play_game(
    cards_a: list[Card],
    cards_b: list[Card],
    rules: FamilyRules,
    strat_a: StrategySpec,
    strat_b: StrategySpec,
    rng: random.Random,
    trace: bool = False,
) -> GameResult:
    game = Game(cards_a, cards_b, rules, strat_a, strat_b, rng, trace=trace)
    _capture_opening(game.players["a"])
    _capture_opening(game.players["b"])
    return game.play()
