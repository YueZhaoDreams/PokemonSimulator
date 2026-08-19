from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from app.engine.effects import can_pay_energy, energy_provided, is_basic_energy, is_double_colorless, parse_ability_effects, resistance_reduce, weakness_multiplier
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
    tool: int | None = None
    ability_used: bool = False

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
    retreated: bool = False
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
        first: str | None = None,
    ) -> None:
        self.rules = rules
        self.rng = rng
        self.trace_on = trace
        self.trace: list[str] = []
        self.events: dict[str, int] = {}
        self.turn = 0
        self.stadium_name: str | None = None
        self.strats = {"a": strat_a, "b": strat_b}
        self.players = {
            "a": self._deal("A", cards_a, strat_a),
            "b": self._deal("B", cards_b, strat_b),
        }
        self.first = first if first in {"a", "b"} else ("a" if rng.random() < 0.5 else "b")
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

    def _copies_hand_and_play(self, me: Player, name: str) -> int:
        key = name.lower()
        return sum(1 for i in me.hand if me.card(i).name.lower() == key) + sum(
            1 for m in me.in_play() if me.card(m.card_i).name.lower() == key
        )

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
            if strat.name == "party":
                return True
            return self._count_named_in_play(me, name) == 0
        if strat.name == "party":
            if "mega clefable" in name:
                return self._copies_hand_and_play(me, "Mega Clefable ex") <= 1
            if name == "clefable ex":
                return self._copies_hand_and_play(me, "Clefable ex") <= 1
            if name == "clefable":
                return self._copies_hand_and_play(me, "Clefable") <= 1
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
                cap = self._clefairy_play_cap(player) if strat.name == "party" else max(1, strat.max_ace_copies)
                return ace_count < cap
            return True
        if not strat.hold_as_energy:
            return True

        ace_out = self._ace_in_play(player, strat) if ace_out is None else ace_out
        ace_reachable = (not aces) or self._name_in_zones(player, aces, "play+hand+deck")
        fallback_out = sum(1 for n in self._in_play_names(player) if n in backups)
        closers = {n.lower() for n in strat.closers}

        if name in closers:
            closer_out = any(n in closers for n in self._in_play_names(player))
            if strat.name == "party":
                # Mewtwo is the Demolish tank as well as the closer — play it even before Clefairy.
                return not closer_out
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
        a_hp = sum(max(0, self._max_hp(a, p) - p.damage) for p in a.in_play())
        b_hp = sum(max(0, self._max_hp(b, p) - p.damage) for p in b.in_play())
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
        me.retreated = False
        for mon in me.in_play():
            mon.ability_used = False
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
        self._play_basics(me)
        if self.strats[who].name in {"party", "demolish"}:
            self._play_trainers(me, foe, who)
            self._play_basics(me)
        self._use_abilities(me, foe, who)
        self._evolve(me, foe, who)
        self._play_basics(me)
        if self.strats[who].name in {"party", "demolish"}:
            self._play_trainers(me, foe, who)
        self._use_abilities(me, foe, who)
        if self.strats[who].name == "party" and self._should_transfer_combo(me, foe):
            self._retreat_for_transfer(me, who)
            self._attach_energy(me, who)
            if not me.active or not self._is_mewtwo(me.card(me.active.card_i)):
                self._maybe_retreat(me, foe, who)
        else:
            self._attach_energy(me, who)
            self._maybe_retreat(me, foe, who)

        if self.strats[who].name == "party":
            # After attach, Mewtwo/Mega can pay retreat and Party again, then return to the tank.
            self._use_abilities(me, foe, who)
            self._note_party_progress(me, who)
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

    def _evolve(self, me: Player, foe: Player | None = None, who: str | None = None) -> None:
        who = who or ("a" if me.name == "A" else "b")
        foe = foe or self.players["b" if who == "a" else "a"]
        strat = self.strats[who]
        if strat.name == "party":
            self._evolve_party(me, foe, who)
            return
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
                if not self._can_evolve_now(me, who, target):
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
        target.ability_used = False
        evo_name = me.card(evo_i).name.lower()
        if "mega clefable" in evo_name:
            self._bump("mega_in_play")
        if evo_name == "clefable ex":
            self._bump("lunar_zone_play")
        self._log(f"{me.name} evolves into {me.card(evo_i).name}")
        self._on_evolve(me, foe=self.players["b" if me.name == "A" else "a"], evolved=target)

    def _has_named(self, me: Player, name: str) -> bool:
        return any(me.card(i).name.lower() == name.lower() for i in me.hand)

    def _first_named(self, me: Player, name: str) -> int | None:
        for i in me.hand:
            if me.card(i).name.lower() == name.lower():
                return i
        return None

    def _is_players_first_turn(self, who: str) -> bool:
        if who == self.first:
            return self.turn == 1
        return self.turn == 2

    def _can_play_supporter(self, who: str) -> bool:
        if not self.rules.first_player_no_supporter:
            return True
        return not (who == self.first and self.turn == 1)

    def _can_evolve_now(self, me: Player, who: str, target: Pokemon) -> bool:
        if self.rules.first_turn_no_evolve and self._is_players_first_turn(who):
            return False
        if target.played_turn == self.turn and not self._has_named(me, "Rare Candy"):
            return False
        return True

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
            name = card.name.lower()
            if self._is_tool_card(card):
                if not self._attach_tool(me, who, found):
                    me.hand.append(found)
                    if card.is_supporter:
                        me.supporter_used = False
                    return
                self._log(f"{me.name} plays {card.name}")
                continue
            if name not in {"ultra ball"}:
                me.discard.append(found)
            self._resolve_trainer(me, foe, card, who=who, card_i=found)
            self._log(f"{me.name} plays {card.name}")

    def _pick_trainer(self, me: Player) -> int | None:
        """Prefer search items (balls) when key Pokémon are not yet available."""
        who = "a" if me.name == "A" else "b"
        foe = self.players["b" if who == "a" else "a"]
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
            if card.is_supporter and not self._can_play_supporter(who):
                continue
            name = card.name.lower()
            score = 0.0
            if name in {"ultra ball", "poké ball", "poke ball"} and missing_protect:
                score += 8
            elif name in {"ultra ball", "poké ball", "poke ball"}:
                score += 3
            elif name in {"nest ball", "nesting ball"}:
                slots = self.rules.bench_size - len(me.bench)
                aces = {n.lower() for n in strat.search_aces}
                copies = sum(1 for n in self._in_play_names(me) if n in aces)
                if copies >= max(1, strat.max_ace_copies) and strat.name == "demolish":
                    score -= 8
                elif strat.name == "party" and slots > 0:
                    have_mewtwo = self._mewtwo_mon(me) is not None or any(
                        self._is_mewtwo(me.card(i)) for i in me.hand
                    )
                    if not have_mewtwo:
                        score += 13
                    elif self._count_named_in_play(me, "Clefairy") < self._clefairy_play_cap(me):
                        score += 6
                    else:
                        score += 2
                elif strat.name == "invisible" and slots > 0:
                    have_mime = any(self._is_mr_mime(me.card(m.card_i)) for m in me.in_play())
                    have_worm = any(self._is_orthworm(me.card(m.card_i)) for m in me.in_play())
                    if not have_mime:
                        score += 14
                    elif not have_worm:
                        score += 10
                    elif copies < max(1, strat.max_ace_copies):
                        score += 5
                    else:
                        score += 1
                elif strat.name == "crunch" and slots > 0:
                    have_worm = any(self._is_orthworm(me.card(m.card_i)) for m in me.in_play())
                    if not have_worm:
                        score += 14
                    else:
                        score -= 6
                elif missing_protect and slots > 0:
                    score += 10
                elif slots > 0:
                    score += 3
                else:
                    score -= 5
            elif name in {"buddy-buddy poffin", "buddy buddy poffin"}:
                slots = self.rules.bench_size - len(me.bench)
                clef = self._count_named_in_play(me, "Clefairy")
                cap = self._clefairy_play_cap(me) if strat.name == "party" else max(1, strat.max_ace_copies)
                have_mewtwo = self._mewtwo_mon(me) is not None or any(
                    self._is_mewtwo(me.card(i)) for i in me.hand
                )
                if slots > 0 and clef < cap:
                    # Hunt Mewtwo first; extra Poffin copies are 60 HP prize fodder.
                    score += 6 if not have_mewtwo else 11
                    if have_mewtwo and clef <= 1:
                        score += 3
                else:
                    score -= 5
            elif name == "energy search":
                if strat.name == "party":
                    have_mewtwo = any(self._is_mewtwo(me.card(m.card_i)) for m in me.in_play()) or any(
                        self._is_mewtwo(me.card(i)) for i in me.hand
                    )
                    clef = self._count_named_in_play(me, "Clefairy") + sum(
                        1 for i in me.hand if self._is_clefairy(me.card(i))
                    )
                    if not have_mewtwo:
                        score += 12
                    elif clef < self._clefairy_play_cap(me):
                        score += 8
                    else:
                        score += 5
                elif missing_protect and self.rules.pokemon_as_energy:
                    score += 8
                elif missing_protect:
                    score += 4
                elif me.active and not self._hand_has_attachable_energy(me, who):
                    score += 5
                else:
                    score += 0.5
            elif name == "switch":
                if strat.name == "party":
                    score -= 20
                elif strat.name == "demolish" and me.active and not self._is_ogerpon(me.card(me.active.card_i)) and me.bench:
                    score += 9
                elif strat.name == "crunch" and me.active and not self._is_orthworm(me.card(me.active.card_i)) and me.bench:
                    score += 10
                elif me.bench:
                    score += 1
                else:
                    score -= 5
            elif name == "arven":
                belt_ready = any(
                    m.tool is not None and "maximum belt" in me.card(m.tool).name.lower()
                    for m in me.in_play()
                ) or any("maximum belt" in me.card(i).name.lower() for i in me.hand)
                charm_ready = any(
                    m.tool is not None and "bravery charm" in me.card(m.tool).name.lower()
                    for m in me.in_play()
                ) or any("bravery charm" in me.card(i).name.lower() for i in me.hand)
                if strat.name == "party" and not belt_ready:
                    score += 10
                elif strat.name == "crunch" and (not belt_ready or not charm_ready):
                    score += 11
                else:
                    score += 6
            elif name == "hop":
                if strat.name == "crunch":
                    # Thin toward ≤3 for Crunch-Time Rush; avoid deck-out.
                    if len(me.deck) <= 3:
                        score -= 20
                    elif len(me.deck) <= 6:
                        score += 12
                    else:
                        score += 9
                elif len(me.deck) <= 8:
                    score -= 10
                else:
                    score += 7 if strat.name == "party" else 3
            elif name == "jacq":
                if strat.name == "party" and self._mega_mon(me) is None:
                    score += 8
                else:
                    score += 3
            elif "professor" in name:
                mewtwo_only_in_hand = self._mewtwo_mon(me) is None and any(
                    self._is_mewtwo(me.card(i)) for i in me.hand
                )
                score += -12 if mewtwo_only_in_hand else (8 if len(me.hand) <= 4 else 4)
            elif name == "acerola":
                score += 9 if self._acerola_helps(me, foe, who) else -8
            elif name == "beach court":
                score += 8 if strat.name == "party" and self.stadium_name != "Beach Court" else (3 if self.stadium_name != "Beach Court" else -4)
            elif self._is_tool_card(card):
                score += 8 if self._tool_target(me, who, card) is not None else -6
            elif name == "tulip":
                score += 2
                psychic_discard = sum(
                    1
                    for i in me.discard
                    if (me.card(i).is_pokemon and me.card(i).types and me.card(i).types[0] == "Psychic")
                    or (me.card(i).is_energy and (me.card(i).energy_type or "") == "Psychic")
                )
                if strat.name == "party" and psychic_discard >= 2:
                    score += 8
                elif psychic_discard >= 2 and (not me.active or not me.active.energy):
                    score += 5
            elif name == "energy switch":
                score += 8 if self._energy_switch_helps(me) else 1
            elif name == "super rod":
                recyclable = sum(
                    1
                    for i in me.discard
                    if me.card(i).is_pokemon or me.card(i).is_energy
                )
                if recyclable >= 2 and len(me.deck) <= 12:
                    score += 11
                elif recyclable >= 3:
                    score += 6
                else:
                    score -= 4
            elif name == "earthen vessel":
                if len(me.hand) <= 1:
                    score -= 8
                elif strat.name == "party":
                    have_mewtwo = self._mewtwo_mon(me) is not None or any(
                        self._is_mewtwo(me.card(i)) for i in me.hand
                    )
                    score += 11 if not have_mewtwo else 7
                else:
                    score += 4
            elif name in {"trekking shoes"}:
                score += 1
            elif name == "tool box":
                belt_ready = any(
                    m.tool is not None and "maximum belt" in me.card(m.tool).name.lower()
                    for m in me.in_play()
                ) or any("maximum belt" in me.card(i).name.lower() for i in me.hand)
                belt_in_deck = any("maximum belt" in me.card(i).name.lower() for i in me.deck)
                if strat.name == "party" and not belt_ready and belt_in_deck:
                    score += 10
                elif not belt_ready and belt_in_deck:
                    score += 6
                else:
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
        mewtwo = self._mewtwo_mon(me)
        if mewtwo is not None and not self._mewtwo_can_pay_photon(me, mewtwo):
            for mon in me.in_play():
                if mon is mewtwo:
                    continue
                if any(self._is_psychic_energy_card(me.card(i)) for i in mon.energy):
                    return True
        if not me.active or not me.bench:
            return False
        card = me.card(me.active.card_i)
        attached = self._energy_pool(me, me.active)
        if any(atk.damage >= 80 and can_pay_energy(attached, atk.cost) for atk in card.attacks):
            return False
        for mon in me.bench:
            for energy_i in mon.energy:
                extra = attached + energy_provided(me.card(energy_i))
                if any(atk.damage >= 80 and can_pay_energy(extra, atk.cost) for atk in card.attacks):
                    return True
        return False

    def _active_can_pay_damage(self, me: Player, min_damage: int = 100) -> bool:
        if not me.active:
            return False
        card = me.card(me.active.card_i)
        attached = self._energy_pool(me, me.active)
        return any(atk.damage >= min_damage and can_pay_energy(attached, atk.cost) for atk in card.attacks)

    def _resolve_trainer(self, me: Player, foe: Player, card: Card, who: str = "a", card_i: int | None = None) -> None:
        name = card.name.lower()
        if name in {"hop"}:
            self._draw(me, 3)
        elif name == "jacq":
            self._search(
                me,
                lambda c: c.is_pokemon and bool(c.evolves_from),
                prefer=["Mega Clefable ex", "Clefable ex", "Clefable"],
                n=2,
                source="jacq",
            )
        elif "professor" in name:
            me.discard.extend(list(me.hand))
            me.hand.clear()
            self._draw(me, 7)
        elif name in {"youngster", "shauna"}:
            me.deck.extend(me.hand)
            me.hand.clear()
            self.rng.shuffle(me.deck)
            self._draw(me, 5)
        elif name in {"quick ball", "great ball", "poké ball", "poke ball"}:
            if name in {"poké ball", "poke ball"} and self.rng.random() < 0.5:
                self._bump("poke_ball_miss")
                self._log(f"{me.name} Poké Ball missed (tails)")
                return
            prefer = self._pokemon_search_prefer(me, who)
            found = self._search(me, lambda c: c.is_pokemon, prefer=prefer, source="poke ball")
            if found:
                self._bump("ball_search_hit")
                self._log(f"{me.name} ball finds {me.card(found).name}")
        elif name in {"nest ball", "nesting ball"}:
            self._bench_basic_from_deck(me, who, count=1, source="nest ball")
        elif name in {"buddy-buddy poffin", "buddy buddy poffin"}:
            self._bench_basic_from_deck(me, who, count=2, max_hp=70, source="poffin")
        elif name == "switch":
            self._play_switch(me, who)
        elif name == "arven":
            self._arven(me, who)
        elif name == "acerola":
            self._acerola(me, who)
        elif name == "beach court":
            self.stadium_name = "Beach Court"
            self._bump("stadium:Beach Court")
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
                lambda c: is_basic_energy(c, pokemon_as_energy=self.rules.pokemon_as_energy),
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
        elif name == "super rod":
            self._super_rod(me)
        elif name == "earthen vessel":
            self._earthen_vessel(me, who)
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
        elif name == "tool box":
            self._tool_box(me)
        elif name == "picnic basket":
            for mon in me.in_play():
                mon.damage = max(0, mon.damage - 30)
        else:
            self._draw(me, 1)

    def _tool_box(self, me: Player) -> None:
        """Printed Tool Box: look at the top 7; put any Pokémon Tools into the hand."""
        look = me.deck[:7]
        me.deck = me.deck[len(look) :]
        kept: list[int] = []
        rest: list[int] = []
        for card_i in look:
            if self._is_tool_card(me.card(card_i)):
                me.hand.append(card_i)
                kept.append(card_i)
            else:
                rest.append(card_i)
        me.deck = rest + me.deck
        self.rng.shuffle(me.deck)
        if kept:
            self._bump("tool_box", len(kept))
            self._log(f"{me.name} Tool Box finds {', '.join(me.card(i).name for i in kept)}")
        else:
            self._bump("tool_box_miss")
            self._log(f"{me.name} Tool Box finds no Tools")

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
        if strat.name == "party":
            prefer: list[str] = []
            if self._mewtwo_mon(me) is None and not any(self._is_mewtwo(me.card(i)) for i in me.hand):
                prefer.append("Mewtwo ex")
            prefer.append("Clefairy")
            return list(dict.fromkeys(prefer))
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
        if strat.name == "party":
            if not any(self._is_mewtwo(me.card(m.card_i)) for m in me.in_play()) and not any(
                self._is_mewtwo(me.card(i)) for i in me.hand
            ):
                prefer.insert(0, "Mewtwo ex")
            if self._count_named_in_play(me, "Clefairy") + sum(1 for i in me.hand if self._is_clefairy(me.card(i))) < self._clefairy_play_cap(me):
                prefer.append("Clefairy")
            if not any("mega clefable" in me.card(m.card_i).name.lower() for m in me.in_play()):
                prefer.append("Mega Clefable ex")
            if not self._has_lunar_zone(me):
                prefer.append("Clefable ex")
            prefer.extend(["Clefable", "Clefable ex", "Mega Clefable ex", "Clefairy"])
            return list(dict.fromkeys(prefer))
        if strat.name == "demolish":
            if not any(self._is_ogerpon(me.card(m.card_i)) for m in me.in_play()) and not any(
                self._is_ogerpon(me.card(i)) for i in me.hand
            ):
                prefer.insert(0, "Cornerstone Mask Ogerpon ex")
            prefer.append("Fighting Energy")
            return list(dict.fromkeys(prefer))
        if strat.name == "invisible":
            have_mime = any(self._is_mr_mime(me.card(m.card_i)) for m in me.in_play()) or any(
                self._is_mr_mime(me.card(i)) for i in me.hand
            )
            if not have_mime:
                prefer.insert(0, "Mr. Mime")
            if not any(self._is_orthworm(me.card(m.card_i)) for m in me.in_play()) and not any(
                self._is_orthworm(me.card(i)) for i in me.hand
            ):
                prefer.append("Orthworm")
            prefer.extend(["Mr. Mime", "Orthworm", "Ferroseed", "Aron", "Metal Energy"])
            return list(dict.fromkeys(prefer))
        if strat.name == "crunch":
            have_worm = any(self._is_orthworm(me.card(m.card_i)) for m in me.in_play()) or any(
                self._is_orthworm(me.card(i)) for i in me.hand
            )
            if not have_worm:
                prefer.insert(0, "Orthworm")
            prefer.extend(["Orthworm", "Ferroseed", "Aron", "Metal Energy"])
            return list(dict.fromkeys(prefer))
        if me.active:
            need = self._needed_types(me, me.active)
            # Named energies first.
            for et in need:
                prefer.append(f"{et} Energy")
            # Then Pokémon that pay those types (and protected aces).
            type_prefer = {
                "Water": ["Dondozo", "Seel", "Corphish", "Wailmer", "Poliwhirl"],
                "Metal": ["Orthworm", "Bronzor", "Metang", "Aron", "Ferroseed"],
                "Psychic": ["Mr. Mime", "Clefairy", "Clefable", "Clefable ex", "Mega Clefable ex", "Flutter Mane", "Pumpkaboo", "Kadabra"],
                "Lightning": ["Mewtwo ex", "Pikachu", "Electrike", "Emolga", "Plusle"],
                "Fire": ["Slugma", "Litwick", "Crocalor", "Salazzle"],
                "Grass": ["Roselia", "Tangela", "Oddish"],
                "Fighting": ["Cornerstone Mask Ogerpon ex", "Rockruff", "Relicanth", "Carbink"],
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
            if strat.hold_as_energy and name in {n.lower() for n in strat.search_aces}:
                copies = sum(1 for n in self._in_play_names(me) if n == name)
                cap = self._clefairy_play_cap(me) if strat.name == "party" else max(1, strat.max_ace_copies)
                if copies >= cap:
                    score -= 25
                elif copies:
                    score -= 4
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
        mewtwo = self._mewtwo_mon(me)
        if mewtwo is not None and not self._mewtwo_can_pay_photon(me, mewtwo):
            for mon in me.in_play():
                if mon is mewtwo:
                    continue
                fuels = [i for i in mon.energy if self._is_psychic_energy_card(me.card(i))]
                if not fuels:
                    continue
                energy_i = fuels[0]
                mon.energy.remove(energy_i)
                mewtwo.energy.append(energy_i)
                self._log(f"{me.name} Energy Switch onto {me.card(mewtwo.card_i).name}")
                return
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

    def _super_rod(self, me: Player) -> None:
        scored: list[tuple[int, int]] = []
        for i in me.discard:
            card = me.card(i)
            if not (card.is_pokemon or card.is_energy):
                continue
            name = card.name.lower()
            rank = 0
            if "clefairy" == name:
                rank = 5
            elif "clefable" in name:
                rank = 4
            elif "mewtwo" in name:
                rank = 3
            elif card.is_energy:
                rank = 2
            else:
                rank = 1
            scored.append((rank, i))
        scored.sort(reverse=True)
        taken = [i for _, i in scored[:3]]
        for i in taken:
            me.discard.remove(i)
            me.deck.append(i)
        if taken:
            self.rng.shuffle(me.deck)
            self._bump("super_rod", len(taken))
            self._log(f"{me.name} Super Rod shuffles {len(taken)} cards into the deck")

    def _earthen_vessel(self, me: Player, who: str) -> None:
        if not me.hand:
            return
        strat = self.strats[who]
        protect = {n.lower() for n in strat.protect}

        def discard_rank(card_i: int) -> int:
            card = me.card(card_i)
            name = card.name.lower()
            if name in protect or self._is_mewtwo(card):
                return 100
            if self._is_clefairy(card) and self._count_named_in_play(me, "Clefairy") < 2:
                return 80
            if card.is_supporter:
                return 40
            if "clefable" in name:
                return 5
            return 0

        victim = min(me.hand, key=discard_rank)
        if discard_rank(victim) >= 80:
            return
        me.hand.remove(victim)
        me.discard.append(victim)
        prefer = self._energy_search_prefer(me, who)
        self._search(
            me,
            lambda c: is_basic_energy(c, pokemon_as_energy=self.rules.pokemon_as_energy),
            prefer=prefer,
            n=2,
            source="earthen vessel",
        )

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

    def _energy_pool(self, me: Player, mon: Pokemon) -> list[str]:
        pool: list[str] = []
        for energy_i in mon.energy:
            pool.extend(energy_provided(me.card(energy_i)))
        return pool

    def _energy_target(self, me: Player, strat: StrategySpec) -> Pokemon:
        assert me.active
        if strat.name == "party":
            mewtwo = self._mewtwo_mon(me)
            if mewtwo is not None:
                return mewtwo
            if me.active and self._is_wall_mon(me, me.active) and not me.active.energy:
                return me.active
            return me.active
        if strat.name == "invisible":
            for mon in me.in_play():
                if not self._is_orthworm(me.card(mon.card_i)):
                    continue
                attached = self._energy_pool(me, mon)
                rush = next((a for a in me.card(mon.card_i).attacks if "crunch" in a.name.lower()), None)
                if rush is None or not can_pay_energy(attached, rush.cost):
                    return mon
            if me.active and self._is_mr_mime(me.card(me.active.card_i)):
                meditate = next((a for a in me.card(me.active.card_i).attacks if "meditate" in a.name.lower()), None)
                if meditate and not can_pay_energy(self._energy_pool(me, me.active), meditate.cost):
                    return me.active
            return me.active
        if strat.name == "crunch":
            for mon in me.in_play():
                if self._is_orthworm(me.card(mon.card_i)):
                    return mon
            return me.active
        closers = {n.lower() for n in strat.closers}
        if closers and self._active_can_chip(me, strat):
            for mon in me.bench:
                if me.card(mon.card_i).name.lower() not in closers:
                    continue
                attached = self._energy_pool(me, mon)
                card = me.card(mon.card_i)
                if not any(can_pay_energy(attached, atk.cost) for atk in card.attacks):
                    return mon
        return me.active

    def _active_can_chip(self, me: Player, strat: StrategySpec) -> bool:
        if not me.active:
            return False
        card = me.card(me.active.card_i)
        attached = self._energy_pool(me, me.active)
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
        pool = self._energy_pool(me, target)
        card = me.card(target.card_i)
        # DCE completes [F][C][C] after a Fighting is attached.
        dce = [i for i in me.hand if is_double_colorless(me.card(i))]
        if dce and any(atk.cost.count("Colorless") >= 2 and not can_pay_energy(pool, atk.cost) for atk in card.attacks):
            fighting_ok = "Fighting" not in need or "Fighting" in pool
            if fighting_ok:
                return dce[0]
        energies = [i for i in me.hand if me.card(i).is_energy]
        matching_nrg = [
            i
            for i in energies
            if (me.card(i).as_energy_type in need or me.card(i).as_energy_type == "Colorless" or not need)
            and not is_double_colorless(me.card(i))
        ]
        if matching_nrg:
            typed = [i for i in matching_nrg if me.card(i).as_energy_type in need]
            return (typed or matching_nrg)[0]
        if dce and (not need or "Colorless" in need or not need):
            return dce[0]
        if not self.rules.pokemon_as_energy:
            return energies[0] if energies else None
        if self.rng.random() > strat.attach_pokemon_as_energy:
            return energies[0] if energies else None
        candidates = []
        for i in me.hand:
            pkm = me.card(i)
            if not pkm.is_pokemon:
                continue
            if self._is_protected_from_energy(me, pkm, strat):
                continue
            et = pkm.as_energy_type
            score = 2 if et in need else 0
            score -= 1 if pkm.hp >= 120 else 0
            candidates.append((score, i))
        if not candidates:
            return energies[0] if energies else None
        candidates.sort(reverse=True)
        if candidates[0][0] >= 0 or need:
            return candidates[0][1]
        return energies[0] if energies else None

    def _needed_types(self, me: Player, target: Pokemon) -> set[str]:
        card = me.card(target.card_i)
        attached = self._energy_pool(me, target)
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
        if strat.name == "party":
            self._retreat_party(me, foe, who)
            return
        if strat.name == "demolish":
            self._retreat_demolish(me, who)
            return
        if strat.name == "invisible":
            self._retreat_invisible(me, foe, who)
            return
        if strat.name == "crunch":
            self._retreat_crunch(me, who)
            return
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
                    attached = self._energy_pool(me, mon)
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
        hp_left = self._max_hp(me, me.active) - me.active.damage
        if incoming_idx is None and hp_left > 30:
            return
        cost = self._retreat_cost(me, me.active)
        if len(me.active.energy) < cost:
            return
        if incoming_idx is None:
            incoming_idx = 0
        self._do_retreat_into(me, incoming_idx)

    def _attack(self, me: Player, foe: Player, who: str) -> None:
        if not me.active or not foe.active:
            return
        strat = self.strats[who]
        atk = self._choose_attack(me, foe, strat)
        if atk is None:
            return
        attacker = me.card(me.active.card_i)
        defender = foe.card(foe.active.card_i)
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

        dmg = self._raw_attack_damage(me, foe, me.active, atk)
        was_undamaged = foe.active.damage == 0
        foe.active.damage += dmg
        self._bump("damage_dealt", dmg)
        self._log(f"{attacker.name} used {atk.name} for {dmg} on {defender.name}")
        if (
            atk.name.lower() == "demolish"
            and self._is_mewtwo(defender)
            and foe.active
            and self._max_hp(foe, foe.active) > foe.active.damage
            and was_undamaged
            and ("transfer_charge" in self.events or "fast_line_7p_belt" in self.events)
        ):
            self._bump("mewtwo_tank_demolish")

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
            elif effect.get("kind") == "transfer_charge":
                self._transfer_charge(me, count=int(effect.get("count") or 2))
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
        if "damage counter" in text and "more damage" in text and ("opponent" in text or "defending" in text):
            return 10
        return None

    def _effective_damage_for(self, me: Player, foe: Player, mon: Pokemon, atk) -> int:
        return self._raw_attack_damage(me, foe, mon, atk)

    def _effective_damage(self, me: Player, foe: Player, atk) -> int:
        assert me.active
        return self._effective_damage_for(me, foe, me.active, atk)

    def _choose_attack(self, me: Player, foe: Player, strat: StrategySpec):
        assert me.active and foe.active
        card = me.card(me.active.card_i)
        attached = self._energy_pool(me, me.active)
        legal = [atk for atk in card.attacks if can_pay_energy(attached, atk.cost)]
        if not legal:
            return None
        foe_name = foe.card(foe.active.card_i).name
        foe_hp = max(0, self._max_hp(foe, foe.active) - foe.active.damage)
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
            elif strat.name == "party" and "mewtwo" in card.name.lower() and effective > 0:
                # Acerola resets a non-KO. Wait for 260+ unless Transfer Charge is setting up.
                if any(e.get("kind") == "transfer_charge" for e in atk.effects):
                    score += 80
                else:
                    score -= 400
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
            if any(e.get("kind") in {"psychic_energy_times", "psychic_energy_bonus"} for e in atk.effects):
                score = max(score, float(effective) * max(0.6, strat.prefer_damage))
            if any(e.get("kind") == "transfer_charge" for e in atk.effects):
                if strat.name == "party" and not any(
                    self._effective_damage(me, foe, a) >= foe_hp > 0 for a in legal
                ):
                    score += 90
                else:
                    score -= 20
            if any(e.get("kind") == "swallow_energy" for e in atk.effects) and not has_big:
                score += 120 * max(0.4, strat.prefer_damage)
            if any(e.get("kind") == "deck_count_bonus" for e in atk.effects) and len(me.deck) <= 3:
                score += 150
            if strat.name == "crunch":
                if "crunch" in atk.name.lower():
                    if effective >= foe_hp > 0:
                        score += 500
                    elif len(me.deck) <= 3:
                        score += 80
                    else:
                        score += 20
                elif "punch" in atk.name.lower() and effective < foe_hp:
                    # Draw 2 while loading toward the thin-deck OHKO.
                    score += 40
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
        if strat.name == "party" and best is not None:
            effective = self._effective_damage(me, foe, best)
            transfer = any(e.get("kind") == "transfer_charge" for e in best.effects)
            if effective <= 0 and not transfer:
                return None
            if (
                effective < foe_hp
                and not transfer
                and "mewtwo" in card.name.lower()
            ):
                return None
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
        if victim_owner.active and self._max_hp(victim_owner, victim_owner.active) <= victim_owner.active.damage:
            knocked.append(("active", victim_owner.active))
        still_bench = []
        for mon in victim_owner.bench:
            if self._max_hp(victim_owner, mon) <= mon.damage:
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
        if victim_owner.active and self._max_hp(victim_owner, victim_owner.active) <= victim_owner.active.damage:
            victim_owner.active = None
        if victim_owner.active is None:
            if not victim_owner.bench:
                slayer_who = "a" if slayer.name == "A" else "b"
                self.winner, self.reason = slayer_who, "opponent has no Pokémon in play"
                return True
            idx = self._promote_idx(victim_owner, victim_who)
            victim_owner.active = victim_owner.bench.pop(idx)
        return False

    def _promote_idx(self, player: Player, who: str) -> int:
        if not player.bench:
            return 0
        strat = self.strats[who]

        def prio(i: int) -> int:
            name = player.card(player.bench[i].card_i).name.lower()
            if strat.name == "party":
                if "mega clefable" in name:
                    return 0
                if "mewtwo" in name:
                    return 1
                if name == "clefable ex":
                    return 2
                if name == "clefable":
                    return 3
                return 9
            if strat.name == "demolish" and "ogerpon" in name:
                return 0
            return 5

        return min(range(len(player.bench)), key=prio)

    def _discard_mon(self, player: Player, mon: Pokemon) -> None:
        player.discard.append(mon.card_i)
        player.discard.extend(mon.energy)
        if mon.tool is not None:
            player.discard.append(mon.tool)
            mon.tool = None
        if player.active is mon:
            player.active = None

    def _take_prize(self, player: Player) -> None:
        if player.prizes:
            player.hand.append(player.prizes.pop())
        player.prizes_taken += 1

    def _is_ex(self, card: Card) -> bool:
        return card.name.lower().rstrip().endswith(" ex")

    def _is_ogerpon(self, card: Card) -> bool:
        return "ogerpon" in card.name.lower()

    def _is_mr_mime(self, card: Card) -> bool:
        return card.name.lower() in {"mr. mime", "mr mime"}

    def _is_orthworm(self, card: Card) -> bool:
        return "orthworm" in card.name.lower()

    def _is_clefairy(self, card: Card) -> bool:
        return card.name.lower() == "clefairy"

    def _is_mewtwo(self, card: Card) -> bool:
        return "mewtwo" in card.name.lower()

    def _is_tool_card(self, card: Card) -> bool:
        name = card.name.lower()
        if name in {"maximum belt", "bravery charm"}:
            return True
        text = (card.text or "").lower()
        return card.is_item and "this card is attached" in text

    def _is_psychic_energy_card(self, card: Card) -> bool:
        return self._is_type_energy_card(card, "Psychic")

    def _is_type_energy_card(self, card: Card, energy_type: str) -> bool:
        et = (energy_type or "Psychic").title()
        if card.is_energy and (card.energy_type or "") == et:
            return True
        return bool(self.rules.pokemon_as_energy and card.is_pokemon and card.types and card.types[0] == et)

    def _has_psychic_energy_on(self, me: Player, mon: Pokemon) -> bool:
        return any(self._is_psychic_energy_card(me.card(i)) for i in mon.energy)

    def _has_lunar_zone(self, me: Player) -> bool:
        for mon in me.in_play():
            for abi in me.card(mon.card_i).abilities:
                if "lunar zone" in (abi.name or "").lower():
                    return True
        return False

    def _max_hp(self, player: Player, mon: Pokemon) -> int:
        card = player.card(mon.card_i)
        hp = card.hp or 0
        if mon.tool is None:
            return hp
        tool = player.card(mon.tool)
        if "bravery charm" in tool.name.lower() and card.is_basic:
            hp += 50
        return hp

    def _retreat_cost(self, me: Player, mon: Pokemon) -> int:
        card = me.card(mon.card_i)
        cost = int(card.retreat or 0)
        if self.stadium_name == "Beach Court" and card.is_basic:
            cost = max(0, cost - 1)
        if self._has_lunar_zone(me) and self._has_psychic_energy_on(me, mon):
            return 0
        return max(0, cost)

    def _stance_prevents(self, attacker: Card, defender: Card) -> bool:
        stance = any(
            "cornerstone stance" in (a.name or "").lower()
            or ("prevent all damage" in (a.text or "").lower() and "ability" in (a.text or "").lower())
            for a in defender.abilities
        )
        return stance and bool(attacker.abilities)

    def _invisible_wall_threshold(self, defender_mon: Pokemon, defender: Card) -> int | None:
        """Return the printed Invisible Wall threshold, or None if it does not apply."""
        if defender_mon.status & (ST_ASLEEP | ST_CONFUSED | ST_PARALYZED):
            return None
        for abi in defender.abilities:
            for eff in self._ability_effects(abi):
                if eff.get("kind") == "invisible_wall":
                    return int(eff.get("threshold") or 30)
            text = (abi.text or "").lower()
            if "30 or more" in text and "prevent" in text and "damage" in text:
                return 30
        return None

    def _raw_attack_damage(self, me: Player, foe: Player, mon: Pokemon, atk) -> int:
        if not foe.active:
            return 0
        attacker = me.card(mon.card_i)
        defender = foe.card(foe.active.card_i)
        dmg = atk.damage
        if any(e.get("kind") == "psychic_energy_times" for e in atk.effects):
            per = 20
            for effect in atk.effects:
                if effect.get("kind") == "psychic_energy_times":
                    per = int(effect.get("per") or atk.damage or 20)
            dmg = per * self._count_psychic_energy_in_play(me)
        elif any(e.get("kind") == "psychic_energy_bonus" for e in atk.effects):
            per = 30
            for effect in atk.effects:
                if effect.get("kind") == "psychic_energy_bonus":
                    per = int(effect.get("per") or 30)
            dmg = atk.damage + per * self._count_psychic_energy_in_play(me)
        elif self._damage_counter_bonus(atk) is not None:
            dmg = atk.damage + self._damage_counter_bonus(atk) * (foe.active.damage // 10)
        elif any(e.get("kind") == "times" for e in atk.effects):
            dmg = atk.damage * max(1, sum(1 for i in me.discard if "tatsu" in me.card(i).name.lower()))
        for effect in atk.effects:
            if effect.get("kind") == "deck_count_bonus" and len(me.deck) <= int(effect.get("max_deck") or 0):
                dmg += int(effect.get("bonus") or 0)
        if mon.tool is not None and "maximum belt" in me.card(mon.tool).name.lower() and self._is_ex(defender):
            dmg += 50
        ignore_wr = any(e.get("kind") == "ignore_wr" for e in atk.effects) or "isn't affected by weakness" in (
            atk.text or ""
        ).lower()
        if not ignore_wr:
            dmg *= weakness_multiplier(defender.weaknesses, attacker.types)
            dmg = max(0, dmg - resistance_reduce(defender.resistances, attacker.types))
        if self._stance_prevents(attacker, defender):
            self._bump("stance_block")
            return 0
        ignore_effects = any(e.get("kind") == "ignore_active_effects" for e in atk.effects) or (
            "effects" in (atk.text or "").lower() and "isn't affected" in (atk.text or "").lower()
        )
        wall = None if ignore_effects else self._invisible_wall_threshold(foe.active, defender)
        if wall is not None and dmg >= wall:
            self._bump("invisible_wall")
            return 0
        return dmg

    def _photon_ko(self, me: Player, foe: Player, mon: Pokemon | None = None) -> bool:
        if not foe.active:
            return False
        mon = mon or next((m for m in me.in_play() if self._is_mewtwo(me.card(m.card_i))), None)
        if mon is None:
            return False
        card = me.card(mon.card_i)
        atk = next((a for a in card.attacks if "kinesis" in a.name.lower()), None)
        if atk is None:
            return False
        if not can_pay_energy(self._energy_pool(me, mon), atk.cost):
            return False
        hp = self._max_hp(foe, foe.active) - foe.active.damage
        return self._raw_attack_damage(me, foe, mon, atk) >= hp > 0

    def _foe_can_demolish(self, foe: Player) -> bool:
        if not foe.active:
            return False
        card = foe.card(foe.active.card_i)
        atk = next((a for a in card.attacks if a.name.lower() == "demolish"), None)
        if atk is None:
            return False
        return can_pay_energy(self._energy_pool(foe, foe.active), atk.cost)

    def _tool_target(self, me: Player, who: str, card: Card) -> Pokemon | None:
        name = card.name.lower()
        if name == "bravery charm":
            for mon in me.in_play():
                if mon.tool is None and me.card(mon.card_i).is_basic:
                    if (
                        self._is_ogerpon(me.card(mon.card_i))
                        or self._is_mewtwo(me.card(mon.card_i))
                        or self._is_orthworm(me.card(mon.card_i))
                        or self._is_mr_mime(me.card(mon.card_i))
                    ):
                        return mon
            for mon in me.in_play():
                if mon.tool is None and me.card(mon.card_i).is_basic:
                    return mon
            return None
        if name == "maximum belt":
            for mon in me.in_play():
                if mon.tool is None and self._is_orthworm(me.card(mon.card_i)):
                    return mon
            for mon in me.in_play():
                if mon.tool is None and self._is_mewtwo(me.card(mon.card_i)):
                    return mon
            for mon in me.in_play():
                if mon.tool is None and self._is_ex(me.card(mon.card_i)):
                    return mon
            return None
        for mon in me.in_play():
            if mon.tool is None:
                return mon
        return None

    def _attach_tool(self, me: Player, who: str, card_i: int) -> bool:
        target = self._tool_target(me, who, me.card(card_i))
        if target is None:
            return False
        target.tool = card_i
        self._bump(f"tool:{me.card(card_i).name}")
        self._log(f"{me.name} attaches {me.card(card_i).name} to {me.card(target.card_i).name}")
        return True

    def _bench_basic_from_deck(self, me: Player, who: str, count: int = 1, max_hp: int | None = None, source: str = "ball") -> None:
        strat = self.strats[who]
        prefer = [p.lower() for p in self._pokemon_search_prefer(me, who)]
        take = min(count, max(0, self.rules.bench_size - len(me.bench)))
        for _ in range(take):
            scored: list[tuple[float, int]] = []
            in_play = {me.card(m.card_i).name.lower() for m in me.in_play()}
            for card_i in me.deck:
                card = me.card(card_i)
                if not card.is_basic:
                    continue
                if max_hp is not None and (card.hp or 0) > max_hp:
                    continue
                name = card.name.lower()
                score = 0.0
                if name in prefer:
                    score += 20 - prefer.index(name)
                if name in in_play:
                    score -= 3
                if strat.hold_as_energy and name in {n.lower() for n in strat.search_aces}:
                    copies = sum(1 for n in self._in_play_names(me) if n == name)
                    cap = self._clefairy_play_cap(me) if strat.name == "party" else max(1, strat.max_ace_copies)
                    if copies >= cap:
                        continue
                    if copies:
                        score -= 8
                scored.append((score, card_i))
            if not scored:
                break
            scored.sort(reverse=True)
            card_i = scored[0][1]
            me.deck.remove(card_i)
            me.bench.append(Pokemon(card_i=card_i, played_turn=self.turn))
            self._bump(f"saw_play:{me.card(card_i).name}")
            self._bump(f"tutor:{me.card(card_i).name}:{source}")
            self._log(f"{me.name} {source} benches {me.card(card_i).name}")
            self.rng.shuffle(me.deck)

    def _switch_target_idx(self, me: Player, who: str) -> int | None:
        if not me.bench:
            return None
        strat = self.strats[who]
        if strat.name == "party":
            for idx, mon in enumerate(me.bench):
                if self._is_clefairy(me.card(mon.card_i)) and not mon.ability_used:
                    return idx
            for idx, mon in enumerate(me.bench):
                if self._is_mewtwo(me.card(mon.card_i)):
                    return idx
            for idx, mon in enumerate(me.bench):
                if "mega clefable" in me.card(mon.card_i).name.lower():
                    return idx
        if strat.name == "demolish":
            for idx, mon in enumerate(me.bench):
                if self._is_ogerpon(me.card(mon.card_i)):
                    return idx
        return 0

    def _play_switch(self, me: Player, who: str, target_idx: int | None = None) -> bool:
        if not me.active or not me.bench:
            return False
        idx = self._switch_target_idx(me, who) if target_idx is None else target_idx
        if idx is None:
            return False
        incoming = me.bench.pop(idx)
        me.bench.append(me.active)
        me.active = incoming
        self._bump("switch")
        self._log(f"{me.name} Switch into {me.card(incoming.card_i).name}")
        return True

    def _do_retreat_into(self, me: Player, incoming_idx: int) -> bool:
        if not me.active or incoming_idx < 0 or incoming_idx >= len(me.bench):
            return False
        if self.rules.one_retreat_per_turn and me.retreated:
            return False
        cost = self._retreat_cost(me, me.active)
        if len(me.active.energy) < cost:
            return False
        for _ in range(cost):
            me.discard.append(me.active.energy.pop())
        incoming = me.bench.pop(incoming_idx)
        me.bench.append(me.active)
        me.active = incoming
        me.retreated = True
        self._bump("retreat")
        self._log(f"{me.name} retreats into {me.card(incoming.card_i).name}")
        return True

    def _arven(self, me: Player, who: str) -> None:
        tool_names = {"maximum belt", "bravery charm"}
        item_prefer = ["Energy Search", "Nest Ball", "Switch", "Buddy-Buddy Poffin", "Tool Box", "Maximum Belt", "Bravery Charm"]
        found_tool = self._search(
            me,
            lambda c: c.name.lower() in tool_names or self._is_tool_card(c),
            prefer=["Maximum Belt", "Bravery Charm"],
            source="arven",
        )
        found_item = self._search(
            me,
            lambda c: c.is_item and c.name.lower() not in tool_names and (found_tool is None or c.name != me.card(found_tool).name),
            prefer=item_prefer,
            source="arven",
        )
        if found_tool or found_item:
            self._bump("arven")

    def _acerola_helps(self, me: Player, foe: Player, who: str) -> bool:
        if not me.active or me.active.damage <= 0:
            return False
        if len(me.in_play()) < 2:
            return False
        if self._foe_can_demolish(foe) is False and who == "a":
            return False
        remaining = self._max_hp(me, me.active) - me.active.damage
        if remaining <= 140 or (foe.active and self._photon_ko(foe, me) is False and remaining < self._max_hp(me, me.active)):
            if self.strats[who].name == "demolish" and not self._can_active_ko(me, foe):
                return True
        return self.strats[who].name == "demolish" and me.active.damage > 0 and not self._can_active_ko(me, foe)

    def _can_active_ko(self, me: Player, foe: Player) -> bool:
        if not me.active or not foe.active:
            return False
        attached = self._energy_pool(me, me.active)
        for atk in me.card(me.active.card_i).attacks:
            if can_pay_energy(attached, atk.cost) and self._raw_attack_damage(me, foe, me.active, atk) >= (
                self._max_hp(foe, foe.active) - foe.active.damage
            ) > 0:
                return True
        return False

    def _acerola(self, me: Player, who: str) -> None:
        damaged = [m for m in me.in_play() if m.damage > 0]
        if not damaged:
            return
        mon = me.active if me.active in damaged else damaged[0]
        if mon is me.active and not me.bench:
            return
        me.hand.append(mon.card_i)
        me.hand.extend(mon.energy)
        if mon.tool is not None:
            me.hand.append(mon.tool)
        self._bump("acerola")
        self._log(f"{me.name} Acerola picks up {me.card(mon.card_i).name}")
        mon.energy = []
        mon.tool = None
        mon.damage = 0
        if mon is me.active:
            me.active = me.bench.pop(0)
        elif mon in me.bench:
            me.bench.remove(mon)

    def _prankish_pick(self, foe: Player) -> int | None:
        if not foe.active or not foe.active.energy:
            return None

        def score(i: int) -> int:
            card = foe.card(i)
            name = card.name.lower()
            energy_type = (card.as_energy_type or card.energy_type or "")
            if energy_type == "Fighting" or "fighting" in name:
                return 3
            if is_double_colorless(card):
                return 1
            return 0

        return max(foe.active.energy, key=score)

    def _prankish_stops_demolish(self, foe: Player) -> bool:
        pick = self._prankish_pick(foe)
        if pick is None or not foe.active:
            return False
        pool: list[str] = []
        for i in foe.active.energy:
            if i == pick:
                continue
            pool.extend(energy_provided(foe.card(i)))
        atk = next((a for a in foe.card(foe.active.card_i).attacks if a.name.lower() == "demolish"), None)
        if atk is None:
            return False
        return not can_pay_energy(pool, atk.cost)

    def _on_evolve(self, me: Player, foe: Player, evolved: Pokemon) -> None:
        card = me.card(evolved.card_i)
        if not any("prankish" in (a.name or "").lower() for a in card.abilities):
            return
        energy_i = self._prankish_pick(foe)
        if energy_i is None or not foe.active:
            return
        foe.active.energy.remove(energy_i)
        foe.deck.insert(0, energy_i)
        self._bump("prankish")
        self._bump("prankish_evo_eligible_turn")
        self._log(f"{me.name} Prankish puts {foe.card(energy_i).name} on top of {foe.name}'s deck")

    def _party_engines(self, me: Player) -> list[Pokemon]:
        return [m for m in me.in_play() if self._is_clefairy(me.card(m.card_i))]

    def _party_fuel_ok(self, me: Player, card_i: int, energy_type: str = "Psychic") -> bool:
        if not self._is_type_energy_card(me.card(card_i), energy_type):
            return False
        name = me.card(card_i).name.lower()
        if "mewtwo" in name:
            return False
        # Keep 1 Clefable-line copy in hand, play, or deck as a Pokémon; extras are energy.
        if "mega clefable" in name or name in {"clefable ex", "clefable"}:
            total = sum(
                1
                for i in list(me.hand) + list(me.deck) + [m.card_i for m in me.in_play()]
                if me.card(i).name.lower() == name
            )
            return total >= 2
        return True

    def _mewtwo_mon(self, me: Player) -> Pokemon | None:
        for mon in me.in_play():
            if self._is_mewtwo(me.card(mon.card_i)):
                return mon
        return None

    def _psychic_on(self, me: Player, mon: Pokemon) -> int:
        return sum(1 for i in mon.energy if self._is_psychic_energy_card(me.card(i)))

    def _is_wall_mon(self, me: Player, mon: Pokemon) -> bool:
        name = me.card(mon.card_i).name.lower()
        return "mega clefable" in name or name == "clefable ex"

    def _survives_demolish(self, me: Player, mon: Pokemon) -> bool:
        return self._max_hp(me, mon) - mon.damage > 140

    def _is_tank_mon(self, me: Player, mon: Pokemon) -> bool:
        name = me.card(mon.card_i).name.lower()
        return "mega clefable" in name or name == "clefable ex" or self._is_mewtwo(me.card(mon.card_i))

    def _best_tank_idx(self, me: Player) -> int | None:
        """Bench index of the best Demolish sponge. Prefer a body that survives 140."""
        scored: list[tuple[int, int, int, int]] = []
        for idx, mon in enumerate(me.bench):
            if not self._is_tank_mon(me, mon):
                continue
            survives = 1 if self._survives_demolish(me, mon) else 0
            name = me.card(mon.card_i).name.lower()
            if "mega clefable" in name:
                role = 3
            elif self._is_mewtwo(me.card(mon.card_i)):
                role = 2
            else:
                role = 1
            hp = self._max_hp(me, mon) - mon.damage
            scored.append((survives, role, hp, idx))
        if not scored:
            return None
        scored.sort(reverse=True)
        return scored[0][3]

    def _end_on_tank(self, me: Player, foe: Player, who: str) -> bool:
        """Never leave 60 HP Clefairy Active into Demolish."""
        if not me.active or not me.bench:
            return False
        if self._photon_ko(me, foe) or self._want_fast_line(me, foe, who):
            return False
        if not self._ogerpon_threat(foe):
            return False
        if self._is_tank_mon(me, me.active) and self._survives_demolish(me, me.active):
            return True
        idx = self._best_tank_idx(me)
        if idx is None:
            return False
        return self._swap_to_bench(me, who, idx, allow_paid=True)

    def _discard_psychic_count(self, me: Player) -> int:
        return sum(1 for i in me.discard if self._is_psychic_energy_card(me.card(i)))

    def _hand_has_psychic_attach(self, me: Player, who: str) -> bool:
        strat = self.strats[who]
        for i in me.hand:
            card = me.card(i)
            if not self._is_psychic_energy_card(card):
                continue
            if card.is_pokemon and self._is_protected_from_energy(me, card, strat):
                continue
            return True
        return False

    def _clefairy_play_cap(self, me: Player) -> int:
        """Party wants benched Clefairy, but a 4th 60 HP body is prize fodder and blocks Mega."""
        return 3

    def _mega_mon(self, me: Player) -> Pokemon | None:
        for mon in me.in_play():
            if "mega clefable" in me.card(mon.card_i).name.lower():
                return mon
        return None

    def _belt_on(self, me: Player, mon: Pokemon) -> bool:
        return mon.tool is not None and "maximum belt" in me.card(mon.tool).name.lower()

    def _belt_available(self, me: Player, who: str, mewtwo: Pokemon | None = None) -> bool:
        mewtwo = mewtwo or self._mewtwo_mon(me)
        if mewtwo is not None and self._belt_on(me, mewtwo):
            return True
        if any("maximum belt" in me.card(i).name.lower() for i in me.hand):
            return True
        if (
            any("maximum belt" in me.card(i).name.lower() for i in me.deck)
            and self._can_play_supporter(who)
            and not me.supporter_used
            and self._has_named(me, "Arven")
        ):
            return True
        return False

    def _mewtwo_can_pay_photon(self, me: Player, mon: Pokemon | None = None) -> bool:
        mon = mon or self._mewtwo_mon(me)
        if mon is None:
            return False
        atk = next((a for a in me.card(mon.card_i).attacks if "kinesis" in a.name.lower()), None)
        return bool(atk) and can_pay_energy(self._energy_pool(me, mon), atk.cost)

    def _photon_damage_for(self, me: Player, foe: Player, psychic: int, belt: bool) -> int:
        dmg = 10 + 30 * psychic
        if belt and foe.active and self._is_ex(foe.card(foe.active.card_i)):
            dmg += 50
        return dmg

    def _photon_ko_with(self, me: Player, foe: Player, psychic: int, belt: bool) -> bool:
        if not foe.active:
            return False
        hp = self._max_hp(foe, foe.active) - foe.active.damage
        return self._photon_damage_for(me, foe, psychic, belt) >= hp > 0

    def _simulate_fast_line(self, me: Player, foe: Player, who: str) -> dict[str, int | bool] | None:
        """Net Psychic / Mewtwo PP after one exact-cost retreat + optional hand attach + Transfer Charge."""
        mewtwo = self._mewtwo_mon(me)
        if mewtwo is None or not me.active:
            return None
        psychic = self._count_psychic_energy_in_play(me)
        on_mewtwo = self._psychic_on(me, mewtwo)
        discard = self._discard_psychic_count(me)
        hand = 1 if (not me.energy_attached and self._hand_has_psychic_attach(me, who)) else 0
        if self._is_mewtwo(me.card(me.active.card_i)):
            cost = 0
            discarded = 0
        else:
            if self.rules.one_retreat_per_turn and me.retreated:
                return None
            cost = self._retreat_cost(me, me.active)
            if len(me.active.energy) < cost:
                return None
            discarded = cost
        psychic = psychic - discarded + hand
        discard = discard + discarded
        retrieved = min(2, discard)
        psychic += retrieved
        on_mewtwo = on_mewtwo + hand + retrieved
        belt = self._belt_available(me, who, mewtwo)
        next_psychic = psychic + 1
        return {
            "psychic": psychic,
            "on_mewtwo": on_mewtwo,
            "retrieved": retrieved,
            "discarded": discarded,
            "pp": on_mewtwo >= 2,
            "belt": belt,
            "ko_next": self._photon_ko_with(me, foe, next_psychic, belt),
            "ko_next_no_attach": self._photon_ko_with(me, foe, psychic, belt),
        }

    def _want_fast_line(self, me: Player, foe: Player, who: str) -> bool:
        if self._photon_ko(me, foe):
            return False
        sim = self._simulate_fast_line(me, foe, who)
        if sim is None or not sim["pp"]:
            return False
        if sim["ko_next"] or sim["ko_next_no_attach"]:
            return True
        # Load Mewtwo while tanking; Photon can fire the turn after.
        return self._ogerpon_threat(foe)

    def _mega_dies_to_next_demolish(self, me: Player) -> bool:
        mega = self._mega_mon(me)
        if mega is None:
            return False
        return self._max_hp(me, mega) - mega.damage <= 140

    def _note_party_progress(self, me: Player, who: str) -> None:
        engines = self._party_engines(me)
        if len(engines) >= 4:
            self._bump("board_4_clefairy")
        if self._mega_mon(me) is not None and self._has_lunar_zone(me) and len(engines) >= 2:
            self._bump("wall_4_clefairy")
        psychic = self._count_psychic_energy_in_play(me)
        if psychic >= 7:
            self._bump("had_7p")
        if psychic >= 9:
            self._bump("had_9p")
        mewtwo = self._mewtwo_mon(me)
        if mewtwo is not None:
            self._bump("mewtwo_in_play")
            if self._mewtwo_can_pay_photon(me, mewtwo):
                self._bump("mewtwo_pp")
            if self._belt_on(me, mewtwo):
                self._bump("belt_on_mewtwo")
        unused = [m for m in self._party_engines(me) if not m.ability_used]
        if unused and self._switch_count(me) == 0 and me.retreated:
            self._bump("stranded_party")

    def _pick_party_fuel_from_deck(self, me: Player, energy_type: str = "Psychic") -> int | None:
        """Search the whole deck for one energy of the printed type. Prefer leftover Clefable-line copies."""
        fuels = [i for i in me.deck if self._party_fuel_ok(me, i, energy_type)]
        if not fuels:
            return None
        if self._count_named_in_play(me, "Clefairy") < self._clefairy_play_cap(me):
            others = [i for i in fuels if not self._is_clefairy(me.card(i))]
            if others:
                fuels = others

        def score(card_i: int) -> int:
            name = me.card(card_i).name.lower()
            if name == "clefable":
                return 0
            if name == "clefable ex":
                return 1
            if "mega clefable" in name:
                return 2
            if self._is_clefairy(me.card(card_i)):
                return 3
            return 4

        return min(fuels, key=score)

    def _ability_effects(self, abi) -> list[dict[str, Any]]:
        """Always parse the printed ability text. Stored effect lists can be stale."""
        return parse_ability_effects(abi.text)

    def _benched_named(self, me: Player, name: str) -> list[Pokemon]:
        want = (name or "").lower()
        if not want:
            return []
        return [m for m in me.bench if me.card(m.card_i).name.lower() == want]

    def _attach_energy_from_deck_per_benched(self, me: Player, active: Pokemon, eff: dict[str, Any]) -> int:
        benched = self._benched_named(me, str(eff.get("benched_name") or ""))
        if not benched:
            return 0
        energy_type = str(eff.get("energy_type") or "Psychic")
        attached = 0
        for target in benched:
            card_i = self._pick_party_fuel_from_deck(me, energy_type)
            if card_i is None:
                break
            me.deck.remove(card_i)
            target.energy.append(card_i)
            attached += 1
            if me.card(card_i).is_pokemon:
                self._bump("pokemon_as_energy")
        self.rng.shuffle(me.deck)
        return attached

    def _attach_energy_from_top(self, me: Player, active: Pokemon, eff: dict[str, Any]) -> int:
        look = int(eff.get("look") or 0)
        if look <= 0:
            return 0
        benched = self._benched_named(me, str(eff.get("benched_name") or ""))
        if not benched:
            return 0
        energy_type = str(eff.get("energy_type") or "Psychic")
        n = min(look, len(me.deck))
        top = [me.deck.pop() for _ in range(n)]
        fuels = [i for i in top if self._party_fuel_ok(me, i, energy_type)]
        others = [i for i in top if i not in fuels]
        attached = 0
        for card_i in fuels:
            target = sorted(benched, key=lambda m: len(m.energy))[0]
            target.energy.append(card_i)
            attached += 1
            if me.card(card_i).is_pokemon:
                self._bump("pokemon_as_energy")
        me.deck.extend(others)
        self.rng.shuffle(me.deck)
        return attached

    def _moon_watching_party(self, me: Player, active: Pokemon) -> None:
        """Run attach-energy abilities printed on the Active Pokémon. No hardcoded look-N."""
        attached = 0
        found = False
        for abi in me.card(active.card_i).abilities:
            for eff in self._ability_effects(abi):
                kind = eff.get("kind")
                if kind == "attach_energy_from_deck_per_benched":
                    attached += self._attach_energy_from_deck_per_benched(me, active, eff)
                    found = True
                elif kind == "attach_energy_from_top":
                    attached += self._attach_energy_from_top(me, active, eff)
                    found = True
        if found:
            active.ability_used = True
        if attached:
            self._bump("moon_watching_party")
            self._bump("party_energy", attached)
            self._log(f"{me.name} ability attached {attached} Energy from the printed text")

    def _swap_to_bench(self, me: Player, who: str, idx: int, allow_paid: bool = False) -> bool:
        if not me.active or idx < 0 or idx >= len(me.bench):
            return False
        switch_i = self._first_named(me, "Switch")
        if switch_i is not None:
            me.hand.remove(switch_i)
            me.discard.append(switch_i)
            return self._play_switch(me, who, idx)
        if self.rules.one_retreat_per_turn and me.retreated:
            return False
        if self._retreat_cost(me, me.active) == 0 or allow_paid:
            return self._do_retreat_into(me, idx)
        return False

    def _switch_count(self, me: Player) -> int:
        return sum(1 for i in me.hand if me.card(i).name.lower() == "switch")

    def _can_reboard_wall(self, me: Player, dest: Pokemon) -> bool:
        """Leave the wall only if we can still restore it (Switch + at most one retreat)."""
        switches = self._switch_count(me)
        leave_cost = self._retreat_cost(me, me.active)
        can_leave = switches >= 1 or (
            not me.retreated and (leave_cost == 0 or len(me.active.energy) >= leave_cost)
        )
        if not can_leave:
            return False
        leave_uses_switch = switches >= 1
        dest_cost = self._retreat_cost(me, dest)
        dest_return = dest_cost == 0 or len(dest.energy) >= dest_cost
        if leave_uses_switch:
            return dest_return or (not me.retreated) or switches >= 2
        return dest_return or switches >= 1

    def _restore_wall(self, me: Player, who: str) -> bool:
        if not me.active or not me.bench:
            return False
        if "mega clefable" in me.card(me.active.card_i).name.lower():
            return True
        for idx, mon in enumerate(me.bench):
            if "mega clefable" in me.card(mon.card_i).name.lower():
                if self._swap_to_bench(me, who, idx, allow_paid=True):
                    self._bump("wall_restore")
                    return True
                return False
        if me.card(me.active.card_i).name.lower() == "clefable ex":
            return True
        for idx, mon in enumerate(me.bench):
            if me.card(mon.card_i).name.lower() == "clefable ex":
                if self._swap_to_bench(me, who, idx, allow_paid=True):
                    self._bump("wall_restore")
                    return True
                return False
        return False

    def _use_abilities(self, me: Player, foe: Player, who: str) -> None:
        if self.strats[who].name != "party":
            return
        if not me.active:
            return
        walling = any(self._is_tank_mon(me, mon) for mon in me.in_play())
        for _ in range(6):
            if not me.active:
                return
            if not me.active.ability_used:
                before = self.events.get("moon_watching_party", 0)
                self._moon_watching_party(me, me.active)
                if walling and self.events.get("moon_watching_party", 0) > before:
                    self._bump("party_while_wall")
                if (
                    self._is_clefairy(me.card(me.active.card_i))
                    and not any(self._is_clefairy(me.card(m.card_i)) for m in me.bench)
                ):
                    me.active.ability_used = True
            unused_fueled = next(
                (
                    idx
                    for idx, mon in enumerate(me.bench)
                    if self._is_clefairy(me.card(mon.card_i))
                    and not mon.ability_used
                    and self._has_psychic_energy_on(me, mon)
                ),
                None,
            )
            unused = unused_fueled if unused_fueled is not None else next(
                (
                    idx
                    for idx, mon in enumerate(me.bench)
                    if self._is_clefairy(me.card(mon.card_i)) and not mon.ability_used
                ),
                None,
            )
            if unused is None:
                break
            dest = me.bench[unused]
            threatened = self._ogerpon_threat(foe)
            if (
                self._is_tank_mon(me, me.active)
                and threatened
                and not self._can_reboard_wall(me, dest)
            ):
                break
            other_clef = self._is_clefairy(me.card(me.active.card_i)) or any(
                self._is_clefairy(me.card(m.card_i)) for i, m in enumerate(me.bench) if i != unused
            )
            if not other_clef:
                break
            # Save the one retreat for the tank whenever Demolish is coming and no Switch is left.
            if threatened and self._best_tank_idx(me) is not None and self._first_named(me, "Switch") is None:
                break
            if not self._swap_to_bench(me, who, unused):
                break
        if self._photon_ko(me, foe) or self._want_fast_line(me, foe, who):
            return
        if self._ogerpon_threat(foe):
            self._end_on_tank(me, foe, who)

    def _evolve_party(self, me: Player, foe: Player, who: str) -> None:
        if self.rules.first_turn_no_evolve and self._is_players_first_turn(who):
            return
        engines = self._party_engines(me)
        can_kill = self._photon_ko(me, foe)
        fast = self._want_fast_line(me, foe, who)

        def evo_in_hand(name: str) -> int | None:
            for i in me.hand:
                if me.card(i).name.lower() == name.lower():
                    return i
            return None

        def evolve_named(evo_name: str, prefer_active: bool, require_used: bool = False) -> bool:
            evo_i = evo_in_hand(evo_name)
            if evo_i is None:
                return False
            evo = me.card(evo_i)
            candidates = []
            for mon in me.in_play():
                if me.card(mon.card_i).name.lower() != (evo.evolves_from or "").lower():
                    continue
                if not self._can_evolve_now(me, who, mon):
                    continue
                candidates.append(mon)
            if not candidates:
                return False
            used = [m for m in candidates if m.ability_used]
            fueled_used = [m for m in used if m.energy]
            fueled = [m for m in candidates if m.energy]
            if require_used and not used:
                return False
            if prefer_active and me.active in candidates and me.active.energy:
                target = me.active
            elif prefer_active:
                target = (fueled_used or fueled or used or candidates)[0]
            else:
                target = (used or candidates)[0]
            self._do_evolve(me, target, evo_i)
            return True

        # Plan A: do not spend Clefairy engines on RCL / Clefable ex / Mega.
        if can_kill or fast:
            return

        # Prankish only if bouncing energy actually delays Demolish and a used engine exists.
        if (
            foe.active
            and self._is_ogerpon(foe.card(foe.active.card_i))
            and foe.active.energy
            and self._prankish_stops_demolish(foe)
            and len(engines) >= 2
        ):
            evolve_named("Clefable", prefer_active=False, require_used=True)

        if self._foe_can_demolish(foe):
            mewtwo = self._mewtwo_mon(me)
            mewtwo_tanks = mewtwo is not None and self._survives_demolish(me, mewtwo)
            # Plan B only: do not spend a Clefairy on Mega while Mewtwo can still eat one 140.
            if not mewtwo_tanks or len(engines) >= 4:
                evolve_named("Mega Clefable ex", prefer_active=True)

        mega_out = self._mega_mon(me) is not None
        mewtwo_out = self._mewtwo_mon(me) is not None
        engines_after_zone = len(self._party_engines(me)) - 1
        # Lunar Zone costs a Clefairy. Worth it to keep Party rotating while a tank is Active.
        zone_worth = engines_after_zone >= 2 and (
            mega_out
            or (mewtwo_out and self._ogerpon_threat(foe))
            or (self._mega_dies_to_next_demolish(me) and self._switch_count(me) == 0)
        )
        if not self._has_lunar_zone(me) and zone_worth:
            evolve_named("Clefable ex", prefer_active=False, require_used=True)

    def _ogerpon_threat(self, foe: Player) -> bool:
        if not foe.active or not self._is_ogerpon(foe.card(foe.active.card_i)):
            return False
        # One more attach completes Demolish (F then DCE), or it is already payable.
        return bool(foe.active.energy) or self._foe_can_demolish(foe)

    def _should_transfer_combo(self, me: Player, foe: Player) -> bool:
        who = "a" if me.name == "A" else "b"
        if self._photon_ko(me, foe):
            return False
        return self._want_fast_line(me, foe, who)

    def _retreat_for_transfer(self, me: Player, who: str) -> None:
        if not me.active or not me.bench:
            return
        mewtwo_idx = next((idx for idx, mon in enumerate(me.bench) if self._is_mewtwo(me.card(mon.card_i))), None)
        if mewtwo_idx is None:
            return
        if self._is_mewtwo(me.card(me.active.card_i)):
            return
        # Pay the printed (modified) cost only — Beach Court 1, not a fake 2.
        self._do_retreat_into(me, mewtwo_idx)

    def _retreat_party(self, me: Player, foe: Player, who: str) -> None:
        if not me.active or not me.bench:
            return
        if self._photon_ko(me, foe) or self._want_fast_line(me, foe, who):
            if self._is_mewtwo(me.card(me.active.card_i)):
                return
            for idx, mon in enumerate(me.bench):
                if self._is_mewtwo(me.card(mon.card_i)):
                    self._swap_to_bench(me, who, idx, allow_paid=True)
                    return
        # Mega must leave before a third Demolish (320 → 180 → 40).
        if me.active and "mega clefable" in me.card(me.active.card_i).name.lower() and self._mega_dies_to_next_demolish(me):
            for idx, mon in enumerate(me.bench):
                if self._is_mewtwo(me.card(mon.card_i)):
                    if self._swap_to_bench(me, who, idx, allow_paid=True):
                        return
            for idx, mon in enumerate(me.bench):
                if me.card(mon.card_i).name.lower() == "clefable ex":
                    if self._swap_to_bench(me, who, idx, allow_paid=True):
                        return
            return
        if self._want_fast_line(me, foe, who):
            return
        if self._ogerpon_threat(foe):
            self._end_on_tank(me, foe, who)
            return
        if not self._is_clefairy(me.card(me.active.card_i)):
            for idx, mon in enumerate(me.bench):
                if self._is_clefairy(me.card(mon.card_i)) and not mon.ability_used:
                    self._swap_to_bench(me, who, idx)
                    return

    def _retreat_demolish(self, me: Player, who: str) -> None:
        if not me.active or self._is_ogerpon(me.card(me.active.card_i)):
            return
        for idx, mon in enumerate(me.bench):
            if self._is_ogerpon(me.card(mon.card_i)):
                self._do_retreat_into(me, idx)
                return

    def _orthworm_can_ko(self, me: Player, foe: Player, mon: Pokemon) -> bool:
        if not foe.active:
            return False
        card = me.card(mon.card_i)
        if not self._is_orthworm(card):
            return False
        attached = self._energy_pool(me, mon)
        foe_hp = max(0, self._max_hp(foe, foe.active) - foe.active.damage)
        for atk in card.attacks:
            if can_pay_energy(attached, atk.cost) and self._effective_damage_for(me, foe, mon, atk) >= foe_hp > 0:
                return True
        return False

    def _retreat_invisible(self, me: Player, foe: Player, who: str) -> None:
        if not me.active or not me.bench:
            return
        active = me.card(me.active.card_i)
        # Swing with Orthworm only when it KOs; otherwise stay on Mime.
        if self._is_mr_mime(active):
            for idx, mon in enumerate(me.bench):
                if self._orthworm_can_ko(me, foe, mon):
                    if self._swap_to_bench(me, who, idx, allow_paid=True):
                        self._bump("mime_swing")
                    return
            return
        if self._is_orthworm(active):
            if self._orthworm_can_ko(me, foe, me.active):
                return
            for idx, mon in enumerate(me.bench):
                if self._is_mr_mime(me.card(mon.card_i)):
                    if self._swap_to_bench(me, who, idx, allow_paid=True):
                        self._bump("mime_restore")
                    return
            return
        for idx, mon in enumerate(me.bench):
            if self._is_mr_mime(me.card(mon.card_i)):
                self._swap_to_bench(me, who, idx, allow_paid=True)
                return

    def _retreat_crunch(self, me: Player, who: str) -> None:
        if not me.active or self._is_orthworm(me.card(me.active.card_i)):
            return
        for idx, mon in enumerate(me.bench):
            if self._is_orthworm(me.card(mon.card_i)):
                self._do_retreat_into(me, idx)
                return

    def _transfer_charge(self, me: Player, count: int = 2) -> None:
        fuels = [i for i in me.discard if self._is_psychic_energy_card(me.card(i))][:count]
        if not fuels:
            return
        target = None
        for mon in me.in_play():
            if self._is_mewtwo(me.card(mon.card_i)):
                target = mon
                break
        target = target or me.active
        if target is None:
            return
        for i in fuels:
            me.discard.remove(i)
            target.energy.append(i)
            if me.card(i).is_pokemon:
                self._bump("pokemon_as_energy")
        self._bump("transfer_charge", len(fuels))
        self._log(f"{me.name} Transfer Charge attaches {len(fuels)} Psychic Energy to {me.card(target.card_i).name}")
        if self._is_mewtwo(me.card(target.card_i)):
            psychic = self._count_psychic_energy_in_play(me)
            if psychic >= 7 and self._mewtwo_can_pay_photon(me, target) and self._belt_on(me, target):
                self._bump("fast_line_7p_belt")


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
    first: str | None = None,
) -> GameResult:
    game = Game(cards_a, cards_b, rules, strat_a, strat_b, rng, trace=trace, first=first)
    _capture_opening(game.players["a"])
    _capture_opening(game.players["b"])
    return game.play()
