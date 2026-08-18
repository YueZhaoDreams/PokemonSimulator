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
        player._opening_prizes = list(player.prizes)  # type: ignore[attr-defined]
        basics = [i for i in player.hand if player.card(i).is_basic]
        if not basics:
            return
        active_i = self._pick_starter(player, basics, strat)
        player.hand.remove(active_i)
        player.active = Pokemon(card_i=active_i, played_turn=0)
        self._bump(f"saw_play:{player.card(active_i).name}")
        remaining = [i for i in player.hand if player.card(i).is_basic]
        if strat.hold_as_energy:
            # Family Cup: Pokémon on the field cannot be attached as energy.
            # Opening puts down only the Active — extras stay in hand as fuel.
            return
        aces = {n.lower() for n in strat.search_aces}
        ace_cards = [i for i in remaining if player.card(i).name.lower() in aces]
        fillers = [i for i in remaining if i not in ace_cards]
        for card_i in ace_cards:
            if len(player.bench) >= self.rules.bench_size:
                break
            player.hand.remove(card_i)
            player.bench.append(Pokemon(card_i=card_i, played_turn=0))
            self._bump(f"saw_play:{player.card(card_i).name}")
        ace_out = player.card(active_i).name.lower() in aces or bool(ace_cards)
        reserve = 1 if aces and not ace_out else 0
        if aces:
            self.rng.shuffle(fillers)
            cap = self.rules.bench_size - reserve
            for card_i in fillers:
                if len(player.bench) >= cap:
                    break
                player.hand.remove(card_i)
                player.bench.append(Pokemon(card_i=card_i, played_turn=0))
                self._bump(f"saw_play:{player.card(card_i).name}")
        else:
            self.rng.shuffle(remaining)
            for card_i in remaining[: self.rules.bench_size]:
                player.hand.remove(card_i)
                player.bench.append(Pokemon(card_i=card_i, played_turn=0))
                self._bump(f"saw_play:{player.card(card_i).name}")

    def _in_play_names(self, player: Player) -> list[str]:
        return [player.card(m.card_i).name.lower() for m in player.in_play()]

    def _count_named_in_play(self, player: Player, name: str) -> int:
        key = name.lower()
        return sum(1 for n in self._in_play_names(player) if n == key)

    def _name_in_zones(self, player: Player, names: set[str], zones: str) -> bool:
        idxs: list[int] = []
        if "hand" in zones:
            idxs.extend(player.hand)
        if "deck" in zones:
            idxs.extend(player.deck)
        if "play" in zones:
            if player.active:
                idxs.append(player.active.card_i)
            idxs.extend(p.card_i for p in player.bench)
        return any(player.card(i).name.lower() in names for i in idxs)

    def _ace_energy_types(self, player: Player, strat: StrategySpec) -> set[str]:
        aces = {n.lower() for n in strat.search_aces}
        types: set[str] = set()
        for card in player.cards:
            if card.name.lower() in aces and card.types:
                types.add(card.types[0])
        return types

    def _ace_in_play(self, player: Player, strat: StrategySpec) -> bool:
        aces = {n.lower() for n in strat.search_aces}
        return (not aces) or any(n in aces for n in self._in_play_names(player))

    def _print_value(self, card, strat: StrategySpec | None = None) -> float:
        """Prefer the stronger printing, or the chip+para printing when prefer_chip."""
        dmg = max((atk.damage for atk in card.attacks), default=0)
        para = any("paralyze" in (atk.text or "").lower() for atk in card.attacks)
        if strat and strat.prefer_chip:
            chip = 0.0
            for atk in card.attacks:
                if "paralyze" in (atk.text or "").lower() and atk.damage > 0:
                    chip = max(chip, float(atk.damage) + 40.0)
            if chip:
                return chip
            return 25.0 if para else float(dmg)
        return float(dmg) + (25.0 if para else 0.0)

    def _is_family_caller(self, card) -> bool:
        return any(e.get("kind") == "call_family" for atk in card.attacks for e in atk.effects)

    def _is_protected_from_energy(self, me: Player, card, strat: StrategySpec) -> bool:
        """Keep the last copy of a protected attacker off the energy pile.

        Extra copies (second Pikachu) may still pay Lightning once one ace is in play.
        Closers like Plusle stay in hand until they occupy the field.
        """
        name = card.name.lower()
        closers = {n.lower() for n in strat.closers}
        aces = {n.lower() for n in strat.search_aces}
        if name in closers:
            return self._count_named_in_play(me, name) == 0
        if name in aces:
            return not any(n in aces for n in self._in_play_names(me))
        if name not in {n.lower() for n in strat.protect}:
            return False
        return self._count_named_in_play(me, name) == 0

    def _wants_in_play(self, player: Player, card, strat: StrategySpec, ace_out: bool | None = None) -> bool:
        """True if this Basic should occupy the field instead of staying in hand as energy."""
        if not card.is_basic:
            return False
        name = card.name.lower()
        aces = {n.lower() for n in strat.search_aces}
        backups = {n.lower() for n in strat.backups}
        insurance = {n.lower() for n in (strat.insurance or strat.backups)}
        copies = self._count_named_in_play(player, name)

        if name in aces:
            if strat.hold_as_energy:
                ace_count = sum(1 for n in self._in_play_names(player) if n in aces)
                return ace_count < max(1, strat.max_ace_copies)
            return True
        if not strat.hold_as_energy:
            return True

        ace_out = self._ace_in_play(player, strat) if ace_out is None else ace_out
        ace_reachable = (not aces) or self._name_in_zones(player, aces, "play+hand+deck")
        fallback_out = sum(1 for n in self._in_play_names(player) if n in backups)
        closers = {n.lower() for n in strat.closers}

        if name in closers:
            closer_out = any(n in closers for n in self._in_play_names(player))
            return (ace_out or not ace_reachable) and not closer_out

        # Ace is prized or otherwise gone — this backup is now the attacker.
        if name in backups and not ace_reachable:
            return copies < 1 and fallback_out < 1

        # One extra Pokémon so a single KO does not lose on the spot.
        sponge_count = sum(
            1
            for m in player.bench
            if player.card(m.card_i).name.lower() not in aces
            and player.card(m.card_i).name.lower() not in closers
        )
        if ace_out and strat.insurance_bench > 0 and sponge_count < strat.insurance_bench:
            if name in insurance:
                return True
            if strat.insurance_non_fuel and name not in aces and name not in closers:
                fuel = self._ace_energy_types(player, strat)
                if (card.as_energy_type or "") not in fuel:
                    return True

        # Carbink / Emolga: only while the ace is still in the deck.
        ace_in_hand = self._name_in_zones(player, aces, "hand")
        if not ace_out and not ace_in_hand and ace_reachable:
            if self._is_ace_searcher(card) or self._is_family_caller(card):
                searcher_out = any(
                    self._is_ace_searcher(player.card(m.card_i)) or self._is_family_caller(player.card(m.card_i))
                    for m in player.in_play()
                )
                return not searcher_out
        return False

    def _is_ace_searcher(self, card) -> bool:
        return any(
            any(e.get("kind") == "search_item" for e in atk.effects) for atk in card.attacks
        )

    def _pick_starter(self, player: Player, basics: list[int], strat: StrategySpec) -> int:
        aces = {n.lower() for n in strat.search_aces}
        backups = {n.lower() for n in strat.backups}
        ace_in_hand = any(player.card(i).name.lower() in aces for i in basics)
        ace_in_deck = self._name_in_zones(player, aces, "deck") if aces else True

        def score(i: int) -> float:
            card = player.card(i)
            if card.name.lower() in aces:
                return 1000 + self._print_value(card, strat)
            if strat.hold_as_energy:
                if not ace_in_hand and ace_in_deck and (
                    self._is_ace_searcher(card) or self._is_family_caller(card)
                ):
                    return 500 + float(card.hp or 0)
                if not ace_in_hand and card.name.lower() in backups:
                    return (400 if not ace_in_deck else 200) + float(card.hp or 0)
                # Cheap placeholder — keep stronger Pokémon in hand as energy.
                return 50 - float(card.hp or 0)
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
            prized_a=self.names(a, getattr(a, "_opening_prizes", a.prizes)),
            prized_b=self.names(b, getattr(b, "_opening_prizes", b.prizes)),
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
            prized_a=self.names(a, getattr(a, "_opening_prizes", a.prizes)),
            prized_b=self.names(b, getattr(b, "_opening_prizes", b.prizes)),
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
        # Tutored Basics (Ultra/Poké Ball, Energy Search) can be played the same turn.
        self._play_basics(me)
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
        who = "a" if me.name == "A" else "b"
        strat = self.strats[who]
        aces = {n.lower() for n in strat.search_aces}
        backups = {n.lower() for n in strat.backups}
        insurance = {n.lower() for n in strat.insurance}
        closers = {n.lower() for n in strat.closers}
        ace_out = (not aces) or any(me.card(m.card_i).name.lower() in aces for m in me.in_play())

        def prio(card_i: int) -> tuple:
            card = me.card(card_i)
            name = card.name.lower()
            if name in aces:
                return (0, -self._print_value(card, strat))
            if name in closers:
                return (1, 0)
            if name in backups:
                return (2, -(card.hp or 0))
            if name in insurance:
                return (3, -(card.hp or 0))
            fuel = self._ace_energy_types(me, strat)
            if strat.insurance_non_fuel and name not in aces and name not in closers and (
                card.as_energy_type or ""
            ) not in fuel:
                return (4, -(card.hp or 0))
            if self._is_ace_searcher(card) or self._is_family_caller(card):
                return (5, 0)
            return (9, 0)

        # Aces, then fallback attackers, then KO insurance — never random fuel.
        ordered = sorted((i for i in list(me.hand) if me.card(i).is_basic), key=prio)
        for card_i in ordered:
            card = me.card(card_i)
            if card_i not in me.hand:
                continue
            if not self._wants_in_play(me, card, strat, ace_out=ace_out):
                continue
            if me.active is None:
                me.hand.remove(card_i)
                me.active = Pokemon(card_i=card_i, played_turn=self.turn)
                self._bump(f"saw_play:{card.name}")
                self._log(f"{me.name} promotes {card.name}")
            elif len(me.bench) < self.rules.bench_size:
                me.hand.remove(card_i)
                me.bench.append(Pokemon(card_i=card_i, played_turn=self.turn))
                self._bump(f"saw_play:{card.name}")
                self._log(f"{me.name} benches {card.name}")
            if card.name.lower() in aces:
                ace_out = True
        if strat.hold_as_energy:
            return
        reserve = 0 if ace_out else 1
        if self.rng.random() > strat.bench_fill and len(me.bench) >= 1:
            return
        basics = [i for i in list(me.hand) if me.card(i).is_basic]
        while basics and len(me.bench) < self.rules.bench_size - reserve:
            card_i = basics.pop(0)
            if card_i not in me.hand:
                continue
            me.hand.remove(card_i)
            me.bench.append(Pokemon(card_i=card_i, played_turn=self.turn))
            self._bump(f"saw_play:{me.card(card_i).name}")
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
        strat = self.strats[who]
        # Greedy AI dumps every Item. Thrifty family play holds them unless needed.
        max_plays = 10 if strat.item_spend >= 0.75 else 1
        for _ in range(max_plays):
            found = self._pick_trainer(me)
            if found is None:
                return
            card = me.card(found)
            if card.is_supporter:
                me.supporter_used = True
            me.hand.remove(found)
            # Ultra Ball discards happen inside resolver before searching.
            if card.name.lower() not in {"ultra ball"}:
                me.discard.append(found)
            self._resolve_trainer(me, foe, card, who=who, card_i=found)
            self._log(f"{me.name} plays {card.name}")

    def _pick_trainer(self, me: Player) -> int | None:
        """Prefer search items (balls) when key Pokémon are not yet available."""
        who = "a" if me.name == "A" else "b"
        strat = self.strats[who]
        in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
        in_hand = {me.card(i).name.lower() for i in me.hand}
        hunt = [n.lower() for n in (strat.search_aces or strat.protect)]
        if strat.hold_as_energy and hunt:
            missing_ace = [] if any(n in in_play or n in in_hand for n in hunt) else hunt
        else:
            missing_ace = [n for n in hunt if n not in in_play and n not in in_hand]
        missing_protect = missing_ace

        candidates: list[tuple[float, int]] = []
        for card_i in me.hand:
            card = me.card(card_i)
            if not card.is_trainer or card.name.lower() == "rare candy":
                continue
            if card.is_supporter and me.supporter_used:
                continue
            name = card.name.lower()
            score = 0.0
            if name in {"ultra ball", "poké ball", "poke ball"} and missing_protect:
                score += 8
            elif name in {"ultra ball", "poké ball", "poke ball"}:
                score += 3
            elif name == "energy search":
                if missing_protect and self.rules.pokemon_as_energy:
                    score += 8
                elif missing_protect:
                    score += 4
                elif me.active and not self._hand_has_attachable_energy(me, who):
                    score += 5
                else:
                    score += 0.5
            elif name == "tulip":
                score += 2
                psychic_discard = sum(
                    1
                    for i in me.discard
                    if (me.card(i).is_pokemon and me.card(i).types and me.card(i).types[0] == "Psychic")
                    or (me.card(i).is_energy and (me.card(i).energy_type or "") == "Psychic")
                )
                if psychic_discard >= 2 and (not me.active or not me.active.energy):
                    score += 5
            elif name == "energy switch":
                score += 7 if self._energy_switch_helps(me) else 1
            elif name in {"trekking shoes", "tool box"}:
                score += 1
            else:
                score += 0.5
            # Greedy Family Cup: Energy Search is also a Pokémon tutor.
            if name == "energy search" and self.rules.pokemon_as_energy and strat.item_spend >= 0.75:
                score += 3
            candidates.append((score, card_i))
        if not candidates:
            return None
        candidates.sort(reverse=True)
        score, card_i = candidates[0]
        # item_spend 1.0 plays anything; 0.2 only plays high-need tutors / Energy Switch.
        min_score = (1.0 - strat.item_spend) * 4.0
        if score < min_score:
            return None
        return card_i

    def _hand_has_attachable_energy(self, me: Player, who: str) -> bool:
        protect = {n.lower() for n in self.strats[who].protect}
        for i in me.hand:
            card = me.card(i)
            if card.is_energy:
                return True
            if (
                self.rules.pokemon_as_energy
                and card.is_pokemon
                and card.as_energy_type
                and card.name.lower() not in protect
            ):
                return True
        return False

    def _energy_switch_helps(self, me: Player) -> bool:
        if not me.active or not me.bench:
            return False
        card = me.card(me.active.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in me.active.energy]
        if any(atk.damage >= 80 and can_pay_energy(attached, atk.cost) for atk in card.attacks):
            return False
        for mon in me.bench:
            for energy_i in mon.energy:
                extra = attached + [me.card(energy_i).as_energy_type or "Colorless"]
                if any(atk.damage >= 80 and can_pay_energy(extra, atk.cost) for atk in card.attacks):
                    return True
        return False

    def _active_can_pay_damage(self, me: Player, min_damage: int = 100) -> bool:
        if not me.active:
            return False
        card = me.card(me.active.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in me.active.energy]
        return any(atk.damage >= min_damage and can_pay_energy(attached, atk.cost) for atk in card.attacks)

    def _resolve_trainer(self, me: Player, foe: Player, card: Card, who: str = "a", card_i: int | None = None) -> None:
        name = card.name.lower()
        if name in {"hop"}:
            self._draw(me, 3)
        elif name in {"youngster", "shauna"}:
            me.deck.extend(me.hand)
            me.hand.clear()
            self.rng.shuffle(me.deck)
            self._draw(me, 5)
        elif name in {"quick ball", "great ball", "nest ball", "nesting ball", "poké ball", "poke ball"}:
            if name in {"poké ball", "poke ball"} and self.rng.random() < 0.5:
                self._bump("poke_ball_miss")
                self._log(f"{me.name} Poké Ball missed (tails)")
                return
            prefer = self._pokemon_search_prefer(me, who)
            found = self._search(me, lambda c: c.is_pokemon, prefer=prefer, source="poke ball")
            if found:
                self._bump("ball_search_hit")
                self._log(f"{me.name} ball finds {me.card(found).name}")
        elif name == "ultra ball":
            # Cost: discard Ultra Ball + 2 other cards from hand.
            if card_i is not None:
                me.discard.append(card_i)
            discarded = self._discard_for_ultra_ball(me, n=2)
            if discarded < 2:
                self._bump("ultra_ball_fail")
                return
            prefer = self._pokemon_search_prefer(me, who)
            found = self._search(me, lambda c: c.is_pokemon, prefer=prefer, source="ultra ball")
            if found:
                self._bump("ball_search_hit")
                self._bump("ultra_ball_hit")
                self._log(f"{me.name} Ultra Ball finds {me.card(found).name}")
        elif name == "energy search":
            # Family Cup: Pokémon count as Basic Energy of their type, so Energy Search
            # may fetch a Pokémon to attach later as energy (or to play).
            prefer = self._energy_search_prefer(me, who)
            found = self._search(
                me,
                lambda c: c.is_energy
                or (self.rules.pokemon_as_energy and c.is_pokemon and bool(c.as_energy_type)),
                prefer=prefer,
                source="energy search",
            )
            if found:
                card_found = me.card(found)
                self._bump("energy_search_hit")
                if card_found.is_pokemon:
                    self._bump("energy_search_pokemon")
                self._log(
                    f"{me.name} Energy Search finds {card_found.name}"
                    + (" (as energy)" if card_found.is_pokemon else "")
                )
        elif name == "energy retrieval":
            found = [i for i in me.discard if me.card(i).is_energy][:2]
            for i in found:
                me.discard.remove(i)
                me.hand.append(i)
        elif name == "energy switch":
            self._energy_switch(me)
        elif name == "tulip":
            self._tulip(me)
        elif name == "trekking shoes":
            if me.deck:
                top = me.deck.pop(0)
                # Prefer keeping protect/search cards.
                card_top = me.card(top)
                protect = {n.lower() for n in self.strats["a" if me.name == "A" else "b"].protect}
                keep = (
                    card_top.name.lower() in protect
                    or card_top.is_energy
                    or card_top.name.lower() in {"ultra ball", "poké ball", "poke ball", "energy search"}
                    or self.rng.random() < 0.55
                )
                if keep:
                    me.hand.append(top)
                else:
                    me.discard.append(top)
                    self._draw(me, 1)
        elif name == "picnic basket":
            for mon in me.in_play():
                mon.damage = max(0, mon.damage - 30)
        else:
            self._draw(me, 1)

    def _discard_for_ultra_ball(self, me: Player, n: int = 2) -> int:
        protect = {n.lower() for n in self.strats["a" if me.name == "A" else "b"].protect}
        scored: list[tuple[float, int]] = []
        for i in list(me.hand):
            card = me.card(i)
            score = 0.0
            if card.name.lower() in protect:
                score -= 10
            if card.name.lower() in {"ultra ball", "poké ball", "poke ball"}:
                score -= 5
            if card.is_energy:
                score -= 1
            if card.hp and card.hp >= 140:
                score -= 3
            if card.is_trainer:
                score += 2
            if card.is_pokemon and card.hp and card.hp <= 70:
                score += 3
            scored.append((score, i))
        scored.sort(reverse=True)
        taken = 0
        for _, i in scored[:n]:
            if i in me.hand:
                me.hand.remove(i)
                me.discard.append(i)
                taken += 1
        return taken

    def _pokemon_search_prefer(self, me: Player, who: str) -> list[str]:
        strat = self.strats[who]
        if strat.hold_as_energy:
            prefer = list(strat.search_aces)
            aces = {n.lower() for n in strat.search_aces}
            if aces and not self._name_in_zones(me, aces, "play+hand+deck"):
                prefer += list(strat.backups)
            return list(dict.fromkeys(prefer))
        prefer = list(strat.search_aces) + list(strat.protect)
        # Side defaults for carpet sets.
        if who == "a":
            prefer += ["Dondozo", "Orthworm", "Flutter Mane", "Carbink"]
        else:
            prefer += ["Pikachu", "Emolga", "Gimmighoul", "Electrike", "Wailmer"]
        return list(dict.fromkeys(prefer))

    def _energy_search_prefer(self, me: Player, who: str) -> list[str]:
        """What Energy Search should dig for under Family Cup."""
        strat = self.strats[who]
        prefer: list[str] = []
        in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
        in_hand = {me.card(i).name.lower() for i in me.hand}
        missing_aces = [n for n in strat.search_aces if n.lower() not in in_play and n.lower() not in in_hand]
        if strat.hold_as_energy and strat.search_aces:
            have_one = any(n.lower() in in_play or n.lower() in in_hand for n in strat.search_aces)
            missing_aces = [] if have_one else missing_aces
        # Family play: Energy Search can fetch the main attacker if it is still in the deck.
        if missing_aces and self.rules.pokemon_as_energy:
            prefer.extend(missing_aces)
        if me.active:
            need = self._needed_types(me, me.active)
            # Named energies first.
            for et in need:
                prefer.append(f"{et} Energy")
            # Then Pokémon that pay those types (and protected aces).
            type_prefer = {
                "Water": ["Dondozo", "Seel", "Corphish", "Wailmer", "Poliwhirl"],
                "Metal": ["Orthworm", "Bronzor", "Metang", "Aron", "Ferroseed"],
                "Psychic": ["Flutter Mane", "Pumpkaboo", "Kadabra", "Gimmighoul"],
                "Lightning": ["Pikachu", "Electrike", "Emolga", "Plusle"],
                "Fire": ["Slugma", "Litwick", "Crocalor", "Salazzle"],
                "Grass": ["Roselia", "Tangela", "Oddish"],
                "Fighting": ["Rockruff", "Relicanth", "Carbink"],
            }
            for et in need:
                prefer.extend(type_prefer.get(et, []))
        prefer.extend(self._pokemon_search_prefer(me, who))
        if who == "b":
            prefer = prefer + ["Grass Energy", "Pikachu", "Electrike", "Emolga"]
        else:
            prefer = prefer + ["Psychic Energy", "Dondozo", "Orthworm", "Flutter Mane"]
        return list(dict.fromkeys(prefer))

    def _search(self, me: Player, pred, prefer: list[str] | None = None, n: int = 1, source: str = "search") -> int | None:
        prefer_l = [p.lower() for p in (prefer or [])]
        in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
        in_hand = {me.card(i).name.lower() for i in me.hand}
        scored: list[tuple[float, int, int]] = []
        for idx, card_i in enumerate(me.deck):
            card = me.card(card_i)
            if not pred(card):
                continue
            score = 0.0
            name = card.name.lower()
            if name in prefer_l:
                score += 20 - prefer_l.index(name)
            if name in in_play or name in in_hand:
                score -= 8
            who = "a" if me.name == "A" else "b"
            strat = self.strats[who]
            if strat.hold_as_energy and name in {n.lower() for n in strat.search_aces} and name in in_play:
                score -= 25
            score += self._print_value(card, strat) / 20.0
            if card.is_basic:
                score += 1
            if card.hp >= 140:
                score += 3
            scored.append((score, idx, card_i))
        if not scored:
            return None
        scored.sort(reverse=True)
        last = None
        for i, (_, idx, card_i) in enumerate(scored[:n]):
            # Recompute index each time since deck mutates.
            try:
                real_idx = me.deck.index(card_i)
            except ValueError:
                continue
            me.deck.pop(real_idx)
            me.hand.append(card_i)
            last = card_i
            found_name = me.card(card_i).name
            self._bump(f"tutor:{found_name}")
            self._bump(f"tutor:{found_name}:{source}")
        self.rng.shuffle(me.deck)
        return last

    def _search_items(self, me: Player, count: int = 2, prefer_names: list[str] | None = None) -> list[int]:
        prefer = [n.lower() for n in (prefer_names or ["ultra ball", "poké ball", "poke ball", "energy search", "energy switch"])]
        in_hand = {me.card(i).name.lower() for i in me.hand}
        scored: list[tuple[float, int]] = []
        for card_i in me.deck:
            card = me.card(card_i)
            if not card.is_item and not (card.is_trainer and (card.trainer_kind or "").lower() == "item"):
                # Some seeds mark items with stage Item.
                if not (card.is_trainer and "item" in (card.stage or "").lower()):
                    if not card.is_trainer or card.is_supporter:
                        continue
                    if (card.trainer_kind or "").lower() == "supporter":
                        continue
            name = card.name.lower()
            score = 0.0
            if name in prefer:
                score += 30 - prefer.index(name)
            if name in in_hand:
                score -= 5
            if "ball" in name:
                score += 5
            scored.append((score, card_i))
        scored.sort(reverse=True)
        found: list[int] = []
        for _, card_i in scored[:count]:
            try:
                me.deck.remove(card_i)
            except ValueError:
                continue
            me.hand.append(card_i)
            found.append(card_i)
            self._bump("lucky_find_item")
            self._log(f"{me.name} Lucky Find gets {me.card(card_i).name}")
        self.rng.shuffle(me.deck)
        return found

    def _call_family(self, me: Player, who: str, count: int = 1) -> None:
        strat = self.strats[who]
        prefer = [p.lower() for p in self._pokemon_search_prefer(me, who)]
        allow = {n.lower() for n in strat.search_aces}
        if strat.hold_as_energy:
            aces = {n.lower() for n in strat.search_aces}
            if aces and not self._name_in_zones(me, aces, "play+hand+deck"):
                allow |= {n.lower() for n in strat.backups}
        slots = self.rules.bench_size - len(me.bench)
        take = min(count, max(0, slots))
        for _ in range(take):
            scored: list[tuple[float, int]] = []
            in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
            for card_i in me.deck:
                card = me.card(card_i)
                if not card.is_basic:
                    continue
                name = card.name.lower()
                if strat.hold_as_energy and allow and name not in allow:
                    continue
                score = 0.0
                if name in prefer:
                    score += 20 - prefer.index(name)
                if name in in_play:
                    score -= 4
                if card.hp >= 140:
                    score += 2
                scored.append((score, card_i))
            if not scored:
                break
            scored.sort(reverse=True)
            card_i = scored[0][1]
            me.deck.remove(card_i)
            me.bench.append(Pokemon(card_i=card_i, played_turn=self.turn))
            self._bump("call_family")
            self._log(f"{me.name} Call for Family benches {me.card(card_i).name}")
            self.rng.shuffle(me.deck)

    def _energy_switch(self, me: Player) -> None:
        donors = [m for m in me.in_play() if m.energy]
        if not donors or not me.active:
            return
        # Move one energy onto active if active needs it.
        if me.active.energy and all(len(m.energy) <= len(me.active.energy) for m in donors):
            return
        donor = max(donors, key=lambda m: len(m.energy))
        if donor is me.active and len(donors) == 1:
            return
        if donor is me.active:
            others = [m for m in donors if m is not me.active]
            if not others:
                return
            # Prefer charging active: take from bench instead.
            donor = max(others, key=lambda m: len(m.energy))
        energy_i = donor.energy.pop()
        me.active.energy.append(energy_i)
        self._log(f"{me.name} Energy Switch onto {me.card(me.active.card_i).name}")

    def _tulip(self, me: Player) -> None:
        picked = []
        for i in list(me.discard):
            card = me.card(i)
            is_psychic_pkm = card.is_pokemon and card.types and card.types[0] == "Psychic"
            is_psychic_nrg = card.is_energy and (card.energy_type or "") == "Psychic"
            if is_psychic_pkm or is_psychic_nrg:
                picked.append(i)
            if len(picked) >= 4:
                break
        for i in picked:
            me.discard.remove(i)
            me.hand.append(i)
        if picked:
            self._log(f"{me.name} Tulip recovers {len(picked)} Psychic cards")

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
        closers = {n.lower() for n in strat.closers}
        if closers and self._active_can_chip(me, strat):
            for mon in me.bench:
                if me.card(mon.card_i).name.lower() not in closers:
                    continue
                attached = [me.card(i).as_energy_type or "Colorless" for i in mon.energy]
                card = me.card(mon.card_i)
                if not any(can_pay_energy(attached, atk.cost) for atk in card.attacks):
                    return mon
        return me.active

    def _active_can_chip(self, me: Player, strat: StrategySpec) -> bool:
        if not me.active:
            return False
        card = me.card(me.active.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in me.active.energy]
        if strat.prefer_chip:
            return any(
                can_pay_energy(attached, atk.cost)
                and atk.damage >= 20
                and "paralyze" in (atk.text or "").lower()
                for atk in card.attacks
            )
        return any(
            can_pay_energy(attached, atk.cost)
            and (atk.damage >= 10 or any(e.get("kind") == "status" for e in atk.effects))
            for atk in card.attacks
        )

    def _choose_energy_card(self, me: Player, target: Pokemon, strat: StrategySpec) -> int | None:
        need = self._needed_types(me, target)
        energies = [i for i in me.hand if me.card(i).is_energy]
        matching_nrg = [
            i
            for i in energies
            if (me.card(i).as_energy_type in need or me.card(i).as_energy_type == "Colorless" or not need)
        ]
        if matching_nrg:
            return matching_nrg[0]
        if not self.rules.pokemon_as_energy:
            return energies[0] if energies else None
        if self.rng.random() > strat.attach_pokemon_as_energy:
            return energies[0] if energies else None
        candidates = []
        for i in me.hand:
            card = me.card(i)
            if not card.is_pokemon:
                continue
            if self._is_protected_from_energy(me, card, strat):
                continue
            et = card.as_energy_type
            score = 2 if et in need else 0
            score -= 1 if card.hp >= 120 else 0
            candidates.append((score, i))
        if not candidates:
            return energies[0] if energies else None
        candidates.sort(reverse=True)
        if candidates[0][0] >= 0 or need:
            return candidates[0][1]
        return energies[0] if energies else None

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
        aces = {n.lower() for n in strat.search_aces}
        active_is_ace = me.card(me.active.card_i).name.lower() in aces
        if aces and not active_is_ace:
            for idx, mon in enumerate(me.bench):
                if me.card(mon.card_i).name.lower() in aces:
                    incoming_idx = idx
                    break
        if incoming_idx is None and foe.active and strat.closers:
            closers = {n.lower() for n in strat.closers}
            foe_hp = max(0, foe.card(foe.active.card_i).hp - foe.active.damage)
            for idx, mon in enumerate(me.bench):
                if me.card(mon.card_i).name.lower() not in closers:
                    continue
                for atk in me.card(mon.card_i).attacks:
                    attached = [me.card(i).as_energy_type or "Colorless" for i in mon.energy]
                    if not can_pay_energy(attached, atk.cost):
                        continue
                    if self._effective_damage_for(me, foe, mon, atk) >= foe_hp > 0:
                        incoming_idx = idx
                        break
                if incoming_idx is not None:
                    break
        if incoming_idx is None and foe.active and strat.prefer_status >= 0.6:
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
        has_psychic_scale = any(e.get("kind") == "psychic_energy_times" for e in atk.effects)
        if has_psychic_scale:
            per = 20
            for effect in atk.effects:
                if effect.get("kind") == "psychic_energy_times":
                    per = int(effect.get("per") or atk.damage or 20)
                    break
            count = self._count_psychic_energy_in_play(me)
            dmg = per * count
            self._bump("wonder_storm_energy", count)
        elif self._damage_counter_bonus(atk) is not None:
            dmg = atk.damage + self._damage_counter_bonus(atk) * (foe.active.damage // 10)
            self._bump("plusle_scale", foe.active.damage // 10)
        elif any(e.get("kind") == "times" for e in atk.effects):
            # Legacy Tatsugiri-style scaling.
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
                self._call_family(me, who, count=int(effect.get("count") or 1))
            elif effect.get("kind") == "search_item":
                prefer = ["Ultra Ball", "Poké Ball", "Poke Ball", "Energy Search", "Energy Switch", "Trekking Shoes"]
                self._search_items(me, count=int(effect.get("count") or 2), prefer_names=prefer)
            elif effect.get("kind") == "swallow_energy":
                look = int(effect.get("look") or 5)
                strat = self.strats[who]
                if strat.swallow_look:
                    look = min(look, int(strat.swallow_look))
                self._swallow_energy(me, look, stop_when_powered=strat.item_spend < 0.75)
            elif effect.get("kind") == "bench_damage_counters":
                self._bench_damage_counters(foe, int(effect.get("counters") or 1))
            elif effect.get("kind") == "mill_opponent":
                self._mill_opponent(me, foe, int(effect.get("count") or 1))

    def _mill_opponent(self, me: Player, foe: Player, count: int = 1) -> None:
        milled = 0
        for _ in range(max(1, count)):
            if not foe.deck:
                break
            card_i = foe.deck.pop(0)
            foe.discard.append(card_i)
            milled += 1
            self._bump("mill_opponent")
            self._log(f"{me.name} mills {foe.card(card_i).name} from {foe.name}'s deck")
        if milled:
            self._bump("mill_attack")

    def _count_psychic_energy_in_play(self, me: Player) -> int:
        """Count Psychic Energy attached to all of this player's Pokémon.

        Under Family Cup, a Pokémon card attached as energy counts if its type is Psychic.
        """
        total = 0
        for mon in me.in_play():
            for energy_i in mon.energy:
                card = me.card(energy_i)
                if card.is_energy and (card.energy_type or (card.types[0] if card.types else "")) == "Psychic":
                    total += 1
                elif card.is_pokemon and card.types and card.types[0] == "Psychic":
                    total += 1
        return total

    def _swallow_energy(self, me: Player, look: int, stop_when_powered: bool = False) -> None:
        """Supplemental Swallow-Up: attach Basic Energy from the top of the deck.

        Under Family Cup, Pokémon may also be attached as matching Basic Energy.
        Thrifty play looks at fewer cards and stops once a big attack is payable.
        """
        if not me.active:
            return
        who = "a" if me.name == "A" else "b"
        strat = self.strats[who]
        taken = min(look, len(me.deck))
        top = [me.deck.pop(0) for _ in range(taken)]
        keep: list[int] = []
        attached = 0
        powered = stop_when_powered and self._active_can_pay_damage(me)
        for card_i in top:
            card = me.card(card_i)
            attachable = (not powered) and (
                card.is_energy
                or (
                    self.rules.pokemon_as_energy
                    and card.is_pokemon
                    and card.as_energy_type
                    and not self._is_protected_from_energy(me, card, strat)
                )
            )
            if attachable:
                me.active.energy.append(card_i)
                attached += 1
                if card.is_pokemon:
                    self._bump("pokemon_as_energy")
                self._bump("swallow_energy")
                self._log(f"{me.name} swallows {card.name} onto {me.card(me.active.card_i).name}")
                if stop_when_powered and self._active_can_pay_damage(me):
                    powered = True
            else:
                keep.append(card_i)
        me.deck.extend(keep)
        self.rng.shuffle(me.deck)
        if attached:
            self._log(f"{me.name} Supplemental Swallow-Up attached {attached} energy (looked at {taken})")

    def _bench_damage_counters(self, foe: Player, counters: int) -> None:
        if not foe.bench:
            return
        damage = 10 * max(1, counters)
        # Dump all counters onto the lowest-HP bench Pokémon (simple AI).
        target = min(foe.bench, key=lambda m: foe.card(m.card_i).hp - m.damage)
        target.damage += damage
        self._bump("bench_damage", damage)
        self._log(f"Bench {foe.card(target.card_i).name} took {damage} from Hex-style attack")

    def _damage_counter_bonus(self, atk) -> int | None:
        for effect in atk.effects:
            if effect.get("kind") == "damage_counter_bonus":
                return int(effect.get("per") or 10)
        text = (atk.text or "").lower()
        if "damage counter" in text and "more damage" in text and "opponent" in text:
            return 10
        return None

    def _effective_damage_for(self, me: Player, foe: Player, mon: Pokemon, atk) -> int:
        attacker = me.card(mon.card_i)
        defender = foe.card(foe.active.card_i)
        dmg = atk.damage
        if any(e.get("kind") == "psychic_energy_times" for e in atk.effects):
            per = 20
            for effect in atk.effects:
                if effect.get("kind") == "psychic_energy_times":
                    per = int(effect.get("per") or atk.damage or 20)
                    break
            dmg = per * self._count_psychic_energy_in_play(me)
        elif self._damage_counter_bonus(atk) is not None:
            dmg = atk.damage + self._damage_counter_bonus(atk) * (foe.active.damage // 10)
        dmg *= weakness_multiplier(defender.weaknesses, attacker.types)
        return max(0, dmg - resistance_reduce(defender.resistances, attacker.types))

    def _effective_damage(self, me: Player, foe: Player, atk) -> int:
        assert me.active
        return self._effective_damage_for(me, foe, me.active, atk)

    def _choose_attack(self, me: Player, foe: Player, strat: StrategySpec):
        assert me.active and foe.active
        card = me.card(me.active.card_i)
        attached = [me.card(i).as_energy_type or "Colorless" for i in me.active.energy]
        legal = [atk for atk in card.attacks if can_pay_energy(attached, atk.cost)]
        if not legal:
            return None
        foe_name = foe.card(foe.active.card_i).name
        foe_hp = max(0, foe.card(foe.active.card_i).hp - foe.active.damage)
        already_para = bool(foe.active.status & ST_PARALYZED)
        has_big = any(a.damage >= 100 for a in legal)
        best = None
        best_score = -1e9
        for atk in legal:
            effective = self._effective_damage(me, foe, atk)
            score = float(effective)
            has_status = any(e.get("kind") == "status" for e in atk.effects)
            has_para = any(e.get("kind") == "status" and e.get("status") == "paralyzed" for e in atk.effects)
            if effective >= foe_hp > 0:
                score += 1000
            if has_status:
                if has_para and already_para:
                    score -= 40
                elif effective < foe_hp:
                    score += 35 * strat.prefer_status
                    if foe_name.lower() in {n.lower() for n in strat.status_targets}:
                        score += 25 * strat.prefer_status
            # 0-damage Nuzzle loses to a real hit once Volt Tackle / Thunder Shock is online.
            if atk.damage == 0 and has_status and any(self._effective_damage(me, foe, a) >= 40 for a in legal):
                score -= 80
            if any(e.get("kind") == "psychic_energy_times" for e in atk.effects):
                score = max(score, float(effective) * max(0.6, strat.prefer_damage))
            if any(e.get("kind") == "swallow_energy" for e in atk.effects) and not has_big:
                score += 120 * max(0.4, strat.prefer_damage)
            if any(e.get("kind") == "deck_count_bonus" for e in atk.effects) and len(me.deck) <= 3:
                score += 150
            if any(e.get("kind") == "search_item" for e in atk.effects):
                need_balls = any(
                    me.card(i).name.lower() in {"ultra ball", "poké ball", "poke ball"} for i in me.deck
                ) and not any(
                    me.card(i).name.lower() in {"ultra ball", "poké ball", "poke ball"} for i in me.hand
                )
                hunt = [n.lower() for n in (strat.search_aces or strat.protect)]
                missing_ace = [
                    n
                    for n in hunt
                    if n not in {me.card(m.card_i).name.lower() for m in me.in_play()}
                    and n not in {me.card(i).name.lower() for i in me.hand}
                ]
                if strat.item_spend < 0.75:
                    score += 90 if need_balls and missing_ace else -15
                else:
                    score += 100 if need_balls else 25
            if any(e.get("kind") == "call_family" for e in atk.effects):
                slots = self.rules.bench_size - len(me.bench)
                missing_ace = [
                    n
                    for n in strat.search_aces
                    if n.lower() not in {me.card(m.card_i).name.lower() for m in me.in_play()}
                    and n.lower() not in {me.card(i).name.lower() for i in me.hand}
                ]
                if strat.hold_as_energy:
                    score += 80 if slots > 0 and missing_ace else -40
                else:
                    score += 70 if slots > 0 and missing_ace else (20 if slots > 0 else -20)
            if any(e.get("kind") == "mill_opponent" for e in atk.effects):
                score += 15 if strat.hold_as_energy else 55
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
