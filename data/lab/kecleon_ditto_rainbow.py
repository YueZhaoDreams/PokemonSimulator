#!/usr/bin/env python3
"""Rules model and goldfish Monte Carlo for the Kecleon / Ditto ◇ / Rescue Scarf deck.

Card effects used here are the printed effects verified for the research note in
data/lab/kecleon-ditto-rainbow/README.md. The goldfish does not invent prize
races, search whiffs, or Prism Star routing. Assumptions that are not printed
rules (the opponent's KO clock, the common weakness chart, and the conservative
Rule Box reading) are listed in ASSUMPTIONS and in the results JSON.
"""

from __future__ import annotations

import json
import math
import random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "data" / "lab" / "kecleon-ditto-rainbow"

# Common printed weakness of a defender's type since Sword & Shield.
# This is not a game rule. Dragon was often weak to Dragon before Fairy existed.
WEAK_TO = {
    "Grass": "Fire",
    "Fire": "Water",
    "Water": "Lightning",
    "Lightning": "Fighting",
    "Psychic": "Darkness",
    "Fighting": "Psychic",
    "Darkness": "Grass",
    "Metal": "Fire",
    "Fairy": "Metal",
    "Dragon": "Fairy",
    "Colorless": "Fighting",
}

ASSUMPTIONS = [
    "Goldfish: no opposing deck. A scripted defender has one type, chosen uniformly from the 11 historical types and known from our second turn.",
    "Common weakness chart above is applied only for the toolbox comparison. Kecleon is Colorless, so Colorful Whip is not doubled.",
    "Opponent KOs our Active at the start of our next turn if it attacked. 80% of those KOs are damage from an attack. 20% are damage counters or a Special Condition, so Rescue Scarf does not trigger.",
    "A KO of 110 or more damage takes one Prize. Weakness is ×2 before that check. Spread hits do not take extra Prizes.",
    "Ditto ◇ remains under the Stage 1. This model treats that Pokémon as having a Rule Box, so Reversal Energy stays at one Colorless. That is a conservative reading of the printed Reversal Energy sentence; the sources retrieved for this note do not include a TPCi Q&A that says it in those words. Counter Energy's bonus still applies, because its text excludes Pokémon-GX and Pokémon-EX, not every Rule Box.",
    "You may fail a deck search. The pilot takes a card whenever the category is in the deck and the card is useful.",
    "Shiftry is never evolved: these lists do not contain Nuzleaf. It is a Dawn target and a Grass/Darkness card in hand.",
    "Retreat is not used. Switch is the pivot, because discarding Double Colorless Energy to pay Kecleon's Retreat Cost of 2 would turn off Colorful Whip.",
    "Opening is the current rule: mulligan until a Basic, set aside 6 Prizes, play Basics, then draw at the start of every turn including the first.",
    "The first player cannot attack or play a Supporter on their first turn. Almighty Evolution cannot be used on your first turn or the turn Ditto ◇ was played, for either player.",
    "Triple Acceleration Energy is discarded at the end of the turn, matching the Unbroken Bonds printing.",
    "Colorful Whip reveals every Pokémon in hand. Revealing more cards cannot reduce the number of different types.",
]


def whip_types(type_groups) -> set[str]:
    found: set[str] = set()
    for group in type_groups:
        found.update(group)
    return found


def whip_damage(type_groups) -> int:
    """30 for each different printed type among revealed Pokémon."""
    return 30 * len(whip_types(type_groups))


def can_almighty(turn: int, played_turn: int) -> bool:
    """Printed Almighty Evolution timing. `turn` is 1 on that player's first turn."""
    return turn > 1 and played_turn < turn


def energy_symbols(kind: str, basic_type: str | None, *, evolution: bool, rule_box: bool, gx_ex: bool, behind: bool):
    """Symbols this energy provides while attached, or None if it cannot be attached."""
    if kind == "dce":
        return ["C", "C"]
    if kind == "counter":
        if behind and not gx_ex:
            return ["A", "A"]
        return ["C"]
    if kind == "reversal":
        if behind and evolution and not rule_box:
            return ["A", "A", "A"]
        return ["C"]
    if kind == "triple":
        if not evolution:
            return None
        return ["C", "C", "C"]
    if kind == "ignition":
        # Ignition Energy (White Flare 86). One Colorless on a Basic, three Colorless on an Evolution.
        # The card is discarded at the end of the turn either way.
        if evolution:
            return ["C", "C", "C"]
        return ["C"]
    if kind == "basic":
        return [basic_type or "C"]
    return []


def pays(cost: tuple[str, ...], symbols: list[str]) -> bool:
    pool = list(symbols)
    colorless = 0
    for symbol in cost:
        if symbol == "C":
            colorless += 1
            continue
        if symbol in pool:
            pool.remove(symbol)
        elif "A" in pool:
            pool.remove("A")
        else:
            return False
    return len(pool) >= colorless


def ko_destinations(stack: list[dict], scarf: bool, by_attack: bool) -> list[str]:
    """Where each Pokémon card in the stack goes. Attached cards are discarded separately.

    Rescue Scarf (Dragons Exalted 115) returns every Pokémon card in the stack on an
    attack-damage KO. A Prism Star card that would be discarded goes to the Lost Zone.
    """
    if scarf and by_attack:
        return ["hand"] * len(stack)
    out = []
    for card in stack:
        out.append("lost" if card.get("prism") else "discard")
    return out


def _card(**kwargs):
    kwargs.setdefault("attacks", ())
    kwargs.setdefault("types", ())
    kwargs.setdefault("stage", None)
    kwargs.setdefault("hp", 0)
    kwargs.setdefault("prism", False)
    kwargs.setdefault("gx_ex", False)
    kwargs.setdefault("rule_box", False)
    kwargs.setdefault("power", 0)
    kwargs.setdefault("basic_type", None)
    kwargs.setdefault("energy", None)
    kwargs.setdefault("kind", "pokemon")
    return kwargs


def C(*types, **extra):
    extra.setdefault("kind", "pokemon")
    return _card(types=tuple(types), **extra)


DECKS: dict[str, list[dict]] = {
    "rainbow": [
        C("Colorless", name="Kecleon", set="Delta Reign", number="83/103", count=4, stage="basic", hp=90, power=0,
          attacks=(("whip", ("C", "C"), 0),), idx_name="kecleon"),
        C("Colorless", name="Ditto ◇", set="Lost Thunder", number="154/214", count=1, stage="basic", hp=40, prism=True, rule_box=True,
          attacks=(), idx_name="ditto"),
        C("Fire", "Grass", name="Volcarona", set="Steam Siege", number="15/114", count=2, stage="stage1", hp=110, power=120,
          attacks=(("burst", ("C", "C", "C"), 120), ("scales", ("Grass",), 20)), idx_name="volcarona"),
        C("Fairy", "Water", name="Azumarill", set="Steam Siege", number="77/114", count=2, stage="stage1", hp=100, power=30,
          attacks=(("coin30", ("C", "C"), 30),), idx_name="azumarill"),
        C("Fighting", "Metal", name="Marowak δ", set="Delta Species", number="10/113", count=2, stage="stage1", hp=80, power=50,
          attacks=(("crusher", ("Fighting", "C", "C"), 50),), idx_name="marowak-d"),
        C("Lightning", "Darkness", name="Dark Magneton", set="Team Rocket Returns", number="39/109", count=2, stage="stage1", hp=70, power=20,
          attacks=(("lines", ("Lightning", "C"), 20),), idx_name="magneton"),
        C("Psychic", "Darkness", name="Dark Hypno", set="Team Rocket Returns", number="6/109", count=2, stage="stage1", hp=70, power=0,
          attacks=(("link", ("C",), 0),), idx_name="hypno"),
        C("Dragon", name="Druddigon", set="White Flare", number="71/86", count=2, stage="basic", hp=120, power=40,
          attacks=(("shred", ("C",), 40),), idx_name="druddigon"),
        C("Lightning", "Grass", name="Galvantula", set="Steam Siege", number="42/114", count=1, stage="stage1", hp=90, power=30,
          attacks=(("spread", ("C",), 30),), idx_name="galvantula"),
        C("Darkness", "Metal", name="Bisharp", set="Steam Siege", number="64/114", count=1, stage="stage1", hp=100, power=30,
          attacks=(("retaliate", ("C",), 30),), idx_name="bisharp"),
        C("Grass", "Darkness", name="Shiftry", set="Steam Siege", number="11/114", count=1, stage="stage2", hp=140, power=60,
          attacks=(("samehand", ("C", "C"), 60),), idx_name="shiftry"),
        _card(kind="trainer", name="Dawn", set="Phantasmal Flames", number="87/94", count=4, effect="dawn"),
        _card(kind="trainer", name="Hilda", set="White Flare", number="84/86", count=3, effect="hilda"),
        _card(kind="trainer", name="Hyper Aroma", set="Twilight Masquerade", number="152/167", count=1, effect="aroma", ace=True),
        _card(kind="trainer", name="Ultra Ball", set="Mega Evolution", number="131/132", count=4, effect="ultra"),
        _card(kind="trainer", name="Nest Ball", set="Scarlet & Violet", number="181/198", count=3, effect="nest"),
        _card(kind="trainer", name="Buddy-Buddy Poffin", set="Temporal Forces", number="144/162", count=2, effect="poffin"),
        _card(kind="trainer", name="Rescue Scarf", set="Dragons Exalted", number="115/124", count=3, effect="scarf"),
        _card(kind="trainer", name="Night Stretcher", set="Shrouded Fable", number="61/64", count=2, effect="night"),
        _card(kind="trainer", name="Rescue Stretcher", set="Guardians Rising", number="130/145", count=2, effect="rescue"),
        _card(kind="trainer", name="Switch", set="Mega Evolution", number="130/132", count=2, effect="switch"),
        _card(kind="trainer", name="Boss's Orders", set="Mega Evolution", number="114/132", count=2, effect="boss"),
        _card(kind="energy", name="Double Colorless Energy", set="Fates Collide", number="114/124", count=4, energy="dce"),
        _card(kind="energy", name="Counter Energy", set="Crimson Invasion", number="100/111", count=4, energy="counter"),
        _card(kind="energy", name="Triple Acceleration Energy", set="Unbroken Bonds", number="190/214", count=2, energy="triple"),
        _card(kind="energy", name="Fighting Energy", set="Crown Zenith", number="157/159", count=2, energy="basic", basic_type="Fighting"),
    ],
    "hybrid": [
        C("Colorless", name="Kecleon", set="Delta Reign", number="83/103", count=4, stage="basic", hp=90,
          attacks=(("whip", ("C", "C"), 0),), idx_name="kecleon"),
        C("Colorless", name="Ditto ◇", set="Lost Thunder", number="154/214", count=1, stage="basic", hp=40, prism=True, rule_box=True,
          attacks=(), idx_name="ditto"),
        C("Fairy", "Water", name="Azumarill", set="Steam Siege", number="77/114", count=2, stage="stage1", hp=100, power=30,
          attacks=(("coin30", ("C", "C"), 30),), idx_name="azumarill"),
        C("Lightning", "Grass", name="Galvantula", set="Steam Siege", number="42/114", count=2, stage="stage1", hp=90, power=30,
          attacks=(("spread", ("C",), 30),), idx_name="galvantula"),
        C("Darkness", "Metal", name="Bisharp", set="Steam Siege", number="64/114", count=2, stage="stage1", hp=100, power=30,
          attacks=(("retaliate", ("C",), 30),), idx_name="bisharp"),
        C("Fire", "Grass", name="Volcarona", set="Steam Siege", number="15/114", count=2, stage="stage1", hp=110, power=120,
          attacks=(("burst", ("C", "C", "C"), 120), ("scales", ("Grass",), 20)), idx_name="volcarona"),
        C("Fighting", name="Marowak", set="Stellar Crown", number="73/142", count=2, stage="stage1", hp=120, power=60,
          attacks=(("bone", ("C", "C"), 60),), idx_name="marowak"),
        C("Psychic", name="Banette", set="Pitch Black", number="34/84", count=2, stage="stage1", hp=80, power=80,
          attacks=(("search", ("Psychic",), 80),), idx_name="banette"),
        C("Dragon", name="Druddigon", set="White Flare", number="71/86", count=2, stage="basic", hp=120, power=40,
          attacks=(("shred", ("C",), 40),), idx_name="druddigon"),
        C("Grass", "Darkness", name="Shiftry", set="Steam Siege", number="11/114", count=1, stage="stage2", hp=140, power=60,
          attacks=(("samehand", ("C", "C"), 60),), idx_name="shiftry"),
        _card(kind="trainer", name="Dawn", set="Phantasmal Flames", number="87/94", count=4, effect="dawn"),
        _card(kind="trainer", name="Hilda", set="White Flare", number="84/86", count=3, effect="hilda"),
        _card(kind="trainer", name="Hyper Aroma", set="Twilight Masquerade", number="152/167", count=1, effect="aroma", ace=True),
        _card(kind="trainer", name="Ultra Ball", set="Mega Evolution", number="131/132", count=4, effect="ultra"),
        _card(kind="trainer", name="Nest Ball", set="Scarlet & Violet", number="181/198", count=3, effect="nest"),
        _card(kind="trainer", name="Buddy-Buddy Poffin", set="Temporal Forces", number="144/162", count=2, effect="poffin"),
        _card(kind="trainer", name="Rescue Scarf", set="Dragons Exalted", number="115/124", count=3, effect="scarf"),
        _card(kind="trainer", name="Night Stretcher", set="Shrouded Fable", number="61/64", count=2, effect="night"),
        _card(kind="trainer", name="Rescue Stretcher", set="Guardians Rising", number="130/145", count=2, effect="rescue"),
        _card(kind="trainer", name="Switch", set="Mega Evolution", number="130/132", count=2, effect="switch"),
        _card(kind="trainer", name="Boss's Orders", set="Mega Evolution", number="114/132", count=2, effect="boss"),
        _card(kind="energy", name="Double Colorless Energy", set="Fates Collide", number="114/124", count=4, energy="dce"),
        _card(kind="energy", name="Counter Energy", set="Crimson Invasion", number="100/111", count=4, energy="counter"),
        _card(kind="energy", name="Triple Acceleration Energy", set="Unbroken Bonds", number="190/214", count=2, energy="triple"),
        _card(kind="energy", name="Psychic Energy", set="Crown Zenith", number="156/159", count=2, energy="basic", basic_type="Psychic"),
    ],
    "toolbox": [
        C("Colorless", name="Kecleon", set="Delta Reign", number="83/103", count=3, stage="basic", hp=90,
          attacks=(("whip", ("C", "C"), 0),), idx_name="kecleon"),
        C("Colorless", name="Ditto ◇", set="Lost Thunder", number="154/214", count=1, stage="basic", hp=40, prism=True, rule_box=True,
          attacks=(), idx_name="ditto"),
        C("Darkness", "Metal", name="Bisharp", set="Steam Siege", number="64/114", count=2, stage="stage1", hp=100, power=30,
          attacks=(("retaliate", ("C",), 30),), idx_name="bisharp"),
        C("Lightning", "Grass", name="Galvantula", set="Steam Siege", number="42/114", count=2, stage="stage1", hp=90, power=30,
          attacks=(("spread", ("C",), 30),), idx_name="galvantula"),
        C("Water", name="Seaking", set="Prismatic Evolutions", number="21/131", count=2, stage="stage1", hp=110, power=60,
          attacks=(("draw2", ("C",), 60),), idx_name="seaking"),
        C("Psychic", name="Banette", set="Pitch Black", number="34/84", count=2, stage="stage1", hp=80, power=80,
          attacks=(("search", ("Psychic",), 80),), idx_name="banette"),
        C("Dragon", name="Druddigon", set="White Flare", number="71/86", count=2, stage="basic", hp=120, power=40,
          attacks=(("shred", ("C",), 40),), idx_name="druddigon"),
        C("Fighting", name="Marowak", set="Stellar Crown", number="73/142", count=1, stage="stage1", hp=120, power=60,
          attacks=(("bone", ("C", "C"), 60),), idx_name="marowak"),
        C("Colorless", name="Aerodactyl", set="151", number="142/165", count=1, stage="stage1", hp=130, power=100,
          attacks=(("devolve", ("C", "C"), 100), ("glide", ("C",), 30)), idx_name="aerodactyl"),
        C("Grass", "Darkness", name="Shiftry", set="Steam Siege", number="11/114", count=1, stage="stage2", hp=140, power=60,
          attacks=(("samehand", ("C", "C"), 60),), idx_name="shiftry"),
        _card(kind="trainer", name="Dawn", set="Phantasmal Flames", number="87/94", count=4, effect="dawn"),
        _card(kind="trainer", name="Hilda", set="White Flare", number="84/86", count=3, effect="hilda"),
        _card(kind="trainer", name="Hyper Aroma", set="Twilight Masquerade", number="152/167", count=1, effect="aroma", ace=True),
        _card(kind="trainer", name="Ultra Ball", set="Mega Evolution", number="131/132", count=4, effect="ultra"),
        _card(kind="trainer", name="Nest Ball", set="Scarlet & Violet", number="181/198", count=3, effect="nest"),
        _card(kind="trainer", name="Buddy-Buddy Poffin", set="Temporal Forces", number="144/162", count=2, effect="poffin"),
        _card(kind="trainer", name="Rescue Scarf", set="Dragons Exalted", number="115/124", count=3, effect="scarf"),
        _card(kind="trainer", name="Night Stretcher", set="Shrouded Fable", number="61/64", count=3, effect="night"),
        _card(kind="trainer", name="Rescue Stretcher", set="Guardians Rising", number="130/145", count=2, effect="rescue"),
        _card(kind="trainer", name="Switch", set="Mega Evolution", number="130/132", count=2, effect="switch"),
        _card(kind="trainer", name="Boss's Orders", set="Mega Evolution", number="114/132", count=2, effect="boss"),
        _card(kind="trainer", name="Professor's Research", set="Paldean Fates", number="87/91", count=2, effect="research"),
        _card(kind="energy", name="Double Colorless Energy", set="Fates Collide", number="114/124", count=4, energy="dce"),
        _card(kind="energy", name="Counter Energy", set="Crimson Invasion", number="100/111", count=4, energy="counter"),
        _card(kind="energy", name="Triple Acceleration Energy", set="Unbroken Bonds", number="190/214", count=2, energy="triple"),
        _card(kind="energy", name="Psychic Energy", set="Crown Zenith", number="156/159", count=2, energy="basic", basic_type="Psychic"),
    ],
}


def deck_size(cards: list[dict]) -> int:
    return sum(c["count"] for c in cards)


def _expand(cards: list[dict]) -> list[int]:
    zone = []
    for i, card in enumerate(cards):
        zone.extend([i] * card["count"])
    if len(zone) != 60:
        raise ValueError(f"deck is {len(zone)} cards")
    return zone


class Mon:
    __slots__ = ("stack", "energy", "tool", "played_turn", "attacked")

    def __init__(self, idx: int, turn: int):
        self.stack = [idx]
        self.energy: list[int] = []
        self.tool: int | None = None
        self.played_turn = turn
        self.attacked = False

    def top(self) -> int:
        return self.stack[-1]


class Game:
    def __init__(self, cards: list[dict], going_first: bool, rng: random.Random):
        self.cards = cards
        self.going_first = going_first
        self.rng = rng
        self.deck: list[int] = []
        self.hand: list[int] = []
        self.discard: list[int] = []
        self.lost: list[int] = []
        self.prizes: list[int] = []
        self.active: Mon | None = None
        self.bench: list[Mon] = []
        self.turn = 0
        self.my_prizes = 6
        self.opp_prizes = 6
        self.opp_type = rng.choice(list(WEAK_TO))
        self.known = False
        self.ko_last_turn = False
        self.lost_game = False
        self.deckout = False
        self.mulligans = 0
        self.whip_hits: list[int] = []
        self.whip_types_n: list[int] = []
        self.turn_kecleon = None
        self.turn_ditto_evo = None
        self.turn_ditto_atk = None
        self.turn_first = None
        self.kecleon_recovered = 0
        self.ditto_recovered = 0
        self.ditto_lost = False
        self.attacks_after_recovery = 0
        self.recovered_ready = False
        self.weakness_hit = False
        self.scarf_on_ditto = False
        self.scarf_on_kecleon = False
        self.research_played = 0
        self.types_when_attacking: list[int] = []
        self.empty_hand_pokemon = 0
        self.max_types = 0
        self.seen_kecleon_turn = None
        self.seen_ditto_turn = None
        self.seen_scarf_turn = None

    def P(self, idx: int) -> dict:
        return self.cards[idx]

    def is_pokemon(self, idx: int) -> bool:
        return self.P(idx)["kind"] == "pokemon"

    def name_is(self, idx: int, key: str) -> bool:
        return self.P(idx).get("idx_name") == key or self.P(idx).get("effect") == key or self.P(idx).get("energy") == key

    def in_play(self) -> list[Mon]:
        mons = list(self.bench)
        if self.active is not None:
            mons.append(self.active)
        return mons

    def find_mon(self, key: str) -> Mon | None:
        for mon in self.in_play():
            if any(self.P(i).get("idx_name") == key for i in mon.stack):
                return mon
        return None

    def hand_types(self) -> set[str]:
        found: set[str] = set()
        for idx in self.hand:
            if self.is_pokemon(idx):
                found.update(self.P(idx)["types"])
        return found

    def _shuffle_deck(self) -> None:
        self.rng.shuffle(self.deck)

    def draw(self, n: int = 1) -> list[int]:
        drawn = []
        for _ in range(n):
            if not self.deck:
                self.deckout = True
                self.lost_game = True
                break
            drawn.append(self.deck.pop())
        self.hand.extend(drawn)
        self._note_seen(drawn)
        return drawn

    def _note_seen(self, idxs) -> None:
        for idx in idxs:
            card = self.P(idx)
            if card.get("idx_name") == "kecleon" and self.seen_kecleon_turn is None:
                self.seen_kecleon_turn = self.turn
            if card.get("idx_name") == "ditto" and self.seen_ditto_turn is None:
                self.seen_ditto_turn = self.turn
            if card.get("effect") == "scarf" and self.seen_scarf_turn is None:
                self.seen_scarf_turn = self.turn

    def setup(self) -> None:
        while True:
            self.deck = _expand(self.cards)
            self._shuffle_deck()
            self.hand = [self.deck.pop() for _ in range(7)]
            if any(self.is_pokemon(i) and self.P(i)["stage"] == "basic" for i in self.hand):
                break
            self.mulligans += 1
            self.hand.clear()
            if self.mulligans > 30:
                self.lost_game = True
                return
        self._note_seen(self.hand)
        self.turn = 0
        self.prizes = [self.deck.pop() for _ in range(6)]
        self._play_basics(setup=True)

    def _play_at(self, hand_index: int, setup: bool) -> None:
        idx = self.hand.pop(hand_index)
        mon = Mon(idx, 0 if setup else self.turn)
        if self.active is None:
            self.active = mon
        elif len(self.bench) < 5:
            self.bench.append(mon)
        else:
            self.hand.append(idx)

    def _locs(self, key: str) -> list[int]:
        return [i for i, idx in enumerate(self.hand) if self.P(idx).get("idx_name") == key]

    def _play_basics(self, setup: bool = False) -> None:
        if self.active is None:
            locs = [i for i, idx in enumerate(self.hand) if self.is_pokemon(idx) and self.P(idx)["stage"] == "basic"]
            if locs:
                self._play_at(self._choose_basic_index(locs), setup)
        if self.find_mon("ditto") is None and len(self.bench) < 5:
            locs = self._locs("ditto")
            if locs:
                self._play_at(locs[0], setup)
        if len(self.bench) < 5:
            locs = self._locs("kecleon")
            if self.find_mon("kecleon") is None and locs:
                self._play_at(locs[0], setup)
            elif len(self._locs("kecleon")) >= 2:
                self._play_at(self._locs("kecleon")[0], setup)
        if len(self.bench) < 5:
            locs = self._locs("druddigon")
            in_play = self.find_mon("druddigon") is not None
            if locs and not in_play and len(locs) >= 2:
                self._play_at(locs[0], setup)

    def _choose_basic_index(self, locs: list[int]) -> int:
        ranked = sorted(locs, key=lambda i: {"kecleon": 0, "druddigon": 1, "ditto": 2}.get(self.P(self.hand[i]).get("idx_name"), 3))
        return ranked[0]

    def behind(self) -> bool:
        return self.my_prizes > self.opp_prizes

    def symbols_on(self, mon: Mon, *, evolution: bool | None = None) -> list[str]:
        top = self.P(mon.top())
        if evolution is None:
            evolution = len(mon.stack) > 1 or top["stage"] != "basic"
        rule_box = any(self.P(i).get("prism") or self.P(i).get("rule_box") for i in mon.stack)
        gx_ex = any(self.P(i).get("gx_ex") for i in mon.stack)
        symbols: list[str] = []
        for energy in mon.energy:
            kind = self.P(energy).get("energy")
            got = energy_symbols(kind, self.P(energy).get("basic_type"), evolution=evolution, rule_box=rule_box, gx_ex=gx_ex, behind=self.behind())
            if got:
                symbols.extend(got)
        return symbols

    def achievable_damage(self, mon: Mon, card: dict) -> int:
        """Damage of `card` if it were the top of `mon` and we attached one energy from hand."""
        symbols = self.symbols_on(mon, evolution=True)
        best = self._damage_from(card, symbols)
        for idx in self.hand:
            if self.P(idx)["kind"] != "energy":
                continue
            extra = energy_symbols(
                self.P(idx).get("energy"),
                self.P(idx).get("basic_type"),
                evolution=True,
                rule_box=True,
                gx_ex=card.get("gx_ex", False),
                behind=self.behind(),
            )
            if not extra:
                continue
            best = max(best, self._damage_from(card, symbols + extra))
        return best

    def _damage_from(self, card: dict, symbols: list[str]) -> int:
        best = 0
        for tag, cost, base in card["attacks"]:
            if not pays(cost, symbols):
                continue
            damage = base
            if tag == "crusher" and self.known and self.opp_type == "Metal":
                damage = 90
            if tag == "retaliate" and self.ko_last_turn:
                damage += 60
            if tag != "spread" and self.known and damage and WEAK_TO[self.opp_type] in card["types"]:
                damage *= 2
            best = max(best, damage)
        return best

    def attack_options(self, mon: Mon) -> tuple[int, dict] | None:
        top = self.P(mon.top())
        symbols = self.symbols_on(mon)
        best = None
        for tag, cost, base in top["attacks"]:
            if not pays(cost, symbols):
                continue
            damage = base
            if tag == "whip":
                groups = [self.P(i)["types"] for i in self.hand if self.is_pokemon(i)]
                damage = whip_damage(groups)
                types_n = len(whip_types(groups))
            else:
                types_n = None
            if tag == "crusher" and self.known and self.opp_type == "Metal":
                damage = 90
            if tag == "retaliate" and self.ko_last_turn:
                damage += 60
            if tag == "coin30" and self.rng.random() < 0.5:
                damage += 30
            if tag != "spread" and self.known and damage and WEAK_TO[self.opp_type] in top["types"]:
                damage *= 2
            if best is None or damage > best[0]:
                best = (damage, {"tag": tag, "types_n": types_n, "top": top})
        return best

    def knockout(self, mon: Mon, by_attack: bool) -> None:
        scarf = mon.tool is not None and self.P(mon.tool).get("effect") == "scarf"
        dest = ko_destinations([self.P(i) for i in mon.stack], scarf, by_attack)
        returned_attacker = False
        for idx, where in zip(mon.stack, dest):
            card = self.P(idx)
            if where == "hand":
                self.hand.append(idx)
                if card.get("idx_name") == "kecleon":
                    self.kecleon_recovered += 1
                    returned_attacker = True
                if card.get("prism"):
                    self.ditto_recovered += 1
                    returned_attacker = True
            elif where == "lost":
                self.lost.append(idx)
                if card.get("prism"):
                    self.ditto_lost = True
            else:
                self.discard.append(idx)
        if returned_attacker:
            self.recovered_ready = True
        self.discard.extend(mon.energy)
        if mon.tool is not None:
            self.discard.append(mon.tool)
        self.opp_prizes -= 1
        self.ko_last_turn = by_attack

    def resolve_enemy_ko(self) -> None:
        if self.active is None or not self.active.attacked:
            self.ko_last_turn = False
            return
        by_attack = self.rng.random() < 0.80
        victim = self.active
        self.active = None
        self.knockout(victim, by_attack)
        if self.bench:
            self.active = self.bench.pop(0)
            # Prefer a Kecleon or an evolved Ditto as the new Active.
            for i, mon in enumerate(self.bench):
                top = self.P(mon.top())
                active_top = self.P(self.active.top())
                if top.get("idx_name") == "kecleon" and active_top.get("idx_name") != "kecleon":
                    self.bench[i] = self.active
                    self.active = mon
                    break
        else:
            self.lost_game = True

    def take(self, zone: list[int], pred) -> int | None:
        for i, idx in enumerate(zone):
            if pred(idx):
                picked = zone.pop(i)
                if zone is self.deck:
                    self._note_seen([picked])
                return picked
        return None

    def want_stage1(self, force: bool = False) -> int | None:
        def score(idx: int) -> tuple:
            card = self.P(idx)
            new = len(set(card["types"]) - self.hand_types())
            hit = int(self.known and WEAK_TO[self.opp_type] in card["types"])
            return (hit, new, card["power"])

        options = [idx for idx in self.deck if self.is_pokemon(idx) and self.P(idx)["stage"] == "stage1"]
        if not options:
            return None
        best = max(options, key=score)
        # Dawn and Hilda name a Stage 1 without "up to", so the search takes one when the deck has one.
        if not force and score(best) == (0, 0, 0) and self.P(best)["power"] < 30:
            return None
        self.deck.remove(best)
        self._note_seen([best])
        return best

    def play_aroma(self) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "aroma"), None)
        if loc is None:
            return False
        picked = []
        for _ in range(3):
            choice = self.want_stage1()
            if choice is None:
                break
            picked.append(choice)
        if not picked:
            return False
        self.discard.append(self.hand.pop(loc))
        self.hand.extend(picked)
        self._shuffle_deck()
        return True

    def play_poffin(self) -> bool:
        if any(self.P(i).get("idx_name") == "ditto" for mon in self.in_play() for i in mon.stack):
            return False
        if len(self.bench) >= 5:
            return False
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "poffin"), None)
        if loc is None:
            return False
        ditto = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == "ditto" and self.P(idx)["hp"] <= 70)
        if ditto is None:
            return False
        self.discard.append(self.hand.pop(loc))
        self.bench.append(Mon(ditto, self.turn))
        self._shuffle_deck()
        return True

    def play_nest(self) -> bool:
        if len(self.bench) >= 5 and self.active is not None:
            return False
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "nest"), None)
        if loc is None:
            return False
        need = None
        if self.find_mon("kecleon") is None:
            need = "kecleon"
        elif self.find_mon("ditto") is None:
            need = "ditto"
        elif self.find_mon("druddigon") is None and any(self.P(i).get("idx_name") == "druddigon" for i in self.hand):
            need = "druddigon"
        if need is None:
            return False
        basic = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == need)
        if basic is None:
            return False
        self.discard.append(self.hand.pop(loc))
        mon = Mon(basic, self.turn)
        if self.active is None:
            self.active = mon
        else:
            self.bench.append(mon)
        self._shuffle_deck()
        return True

    def _discard_cost(self, n: int) -> list[int] | None:
        """Discard n cards without giving away the last copy of a type still only in hand."""
        hand_types = self.hand_types()
        ranked = []
        for i, idx in enumerate(self.hand):
            card = self.P(idx)
            if card["kind"] == "energy":
                rank = 0
            elif card.get("effect") in {"boss", "research"}:
                rank = 1
            elif card["kind"] == "trainer":
                rank = 2
            else:
                types = set(card["types"])
                others = hand_types - types
                # Recompute whether another card keeps the type.
                copies = 0
                for j, other in enumerate(self.hand):
                    if j != i and self.is_pokemon(other) and types & set(self.P(other)["types"]):
                        copies += 1
                rank = 3 if copies else 5
            ranked.append((rank, i))
        ranked.sort()
        if len(ranked) < n:
            return None
        chosen = sorted((i for _, i in ranked[:n]), reverse=True)
        # Do not discard a unique type Pokémon.
        if any(ranked[k][0] >= 5 for k in range(n)):
            return None
        return [self.hand.pop(i) for i in chosen]

    def play_ultra(self) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "ultra"), None)
        if loc is None:
            return False
        # Temporarily ignore the Ultra Ball itself when paying.
        ball = self.hand.pop(loc)
        cost = self._discard_cost(2)
        if cost is None:
            self.hand.insert(loc, ball)
            return False
        choice = None
        if self.find_mon("kecleon") is None and not any(self.P(i).get("idx_name") == "kecleon" for i in self.hand):
            choice = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == "kecleon")
        if choice is None and self.find_mon("ditto") is None and not any(self.P(i).get("idx_name") == "ditto" for i in self.hand):
            choice = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == "ditto")
        if choice is None:
            choice = self.want_stage1()
        if choice is None:
            choice = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == "druddigon")
        if choice is None:
            self.deck.extend(cost)
            self.hand.insert(loc, ball)
            self._shuffle_deck()
            return False
        self.discard.append(ball)
        self.discard.extend(cost)
        self.hand.append(choice)
        self._shuffle_deck()
        return True

    def play_stretcher(self, effect: str) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == effect), None)
        if loc is None:
            return False
        pokemon = [idx for idx in self.discard if self.is_pokemon(idx)]
        if not pokemon:
            return False

        def rank(idx: int) -> tuple:
            card = self.P(idx)
            missing = self.find_mon(card.get("idx_name")) is None
            return (card.get("idx_name") == "kecleon", card.get("idx_name") == "ditto", missing, card.get("power", 0))

        best = max(pokemon, key=rank)
        self.discard.remove(best)
        self.discard.append(self.hand.pop(loc))
        self.hand.append(best)
        return True

    def play_scarf(self) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "scarf"), None)
        if loc is None:
            return False
        # The scripted Knock Out hits the Active attacker. Kecleon is that attacker
        # in most games, so the first Scarf goes there. Ditto ◇ gets the next one.
        target = self.find_mon("kecleon")
        placed = "kecleon"
        if target is None or target.tool is not None:
            target = self.find_mon("ditto")
            placed = "ditto"
        if target is None or target.tool is not None:
            return False
        target.tool = self.hand.pop(loc)
        if placed == "ditto":
            self.scarf_on_ditto = True
        else:
            self.scarf_on_kecleon = True
        return True

    def play_dawn(self) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "dawn"), None)
        if loc is None:
            return False
        picks = []
        if not any(self.P(i).get("idx_name") == "kecleon" for i in self.hand) and self.find_mon("kecleon") is None:
            got = self.take(self.deck, lambda idx: self.P(idx).get("idx_name") == "kecleon")
            if got is not None:
                picks.append(got)
        if not picks:
            got = self.take(self.deck, lambda idx: self.is_pokemon(idx) and self.P(idx)["stage"] == "basic")
            if got is not None:
                picks.append(got)
        stage1 = self.want_stage1(force=True)
        if stage1 is not None:
            picks.append(stage1)
        stage2 = self.take(self.deck, lambda idx: self.is_pokemon(idx) and self.P(idx)["stage"] == "stage2")
        if stage2 is not None:
            picks.append(stage2)
        if not picks:
            return False
        self.discard.append(self.hand.pop(loc))
        self.hand.extend(picks)
        self._shuffle_deck()
        return True

    def play_hilda(self) -> bool:
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "hilda"), None)
        if loc is None:
            return False
        evo = self.want_stage1(force=True) or self.take(self.deck, lambda idx: self.is_pokemon(idx) and self.P(idx)["stage"] in {"stage1", "stage2"})
        energy = self.take(self.deck, lambda idx: self.P(idx).get("energy") == "dce")
        if energy is None:
            energy = self.take(self.deck, lambda idx: self.P(idx)["kind"] == "energy")
        if evo is None and energy is None:
            return False
        self.discard.append(self.hand.pop(loc))
        if evo is not None:
            self.hand.append(evo)
        if energy is not None:
            self.hand.append(energy)
        self._shuffle_deck()
        return True

    def play_research(self) -> bool:
        if len(self.hand_types()) > 2:
            return False
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "research"), None)
        if loc is None:
            return False
        ball = self.hand.pop(loc)
        self.discard.append(ball)
        self.discard.extend(self.hand)
        self.hand = []
        self.draw(7)
        self.research_played += 1
        return True

    def play_supporter(self) -> None:
        if self.going_first and self.turn == 1:
            return
        if self.play_research():
            return
        missing_kecleon = self.find_mon("kecleon") is None and not any(self.P(i).get("idx_name") == "kecleon" for i in self.hand)
        thin_types = len(self.hand_types()) < 4
        if missing_kecleon or thin_types:
            if self.play_dawn():
                return
        if self.play_hilda():
            return
        self.play_dawn()

    def item_pass(self) -> None:
        for _ in range(10):
            did = False
            did = self.play_aroma() or did
            did = self.play_poffin() or did
            did = self.play_nest() or did
            did = self.play_ultra() or did
            did = self.play_stretcher("night") or did
            did = self.play_stretcher("rescue") or did
            did = self.play_scarf() or did
            if not did:
                return

    def evolve(self) -> None:
        mon = self.find_mon("ditto")
        if mon is None or not can_almighty(self.turn, mon.played_turn):
            return
        if len(mon.stack) > 1:
            return
        options = [i for i, idx in enumerate(self.hand) if self.P(idx)["stage"] == "stage1"]
        if not options:
            return

        def score(i: int) -> tuple:
            card = self.P(self.hand[i])
            damage = self.achievable_damage(mon, card)
            hit = int(self.known and damage and WEAK_TO[self.opp_type] in card["types"] and damage >= 80)
            unique = 0
            for typ in card["types"]:
                holders = [j for j in self.hand if self.is_pokemon(j) and typ in self.P(j)["types"]]
                if len(holders) <= 1:
                    unique += 1
            kecleon = self.find_mon("kecleon")
            whip_option = self.attack_options(kecleon) if kecleon is not None else None
            whip_now = whip_option[0] if whip_option else 0
            spendable = unique == 0 or damage >= whip_now or whip_now < 180
            return (int(spendable), hit, damage, -unique)

        best_i = max(options, key=score)
        spendable, _hit, damage, _unique = score(best_i)
        if not spendable or damage < 30:
            return
        idx = self.hand.pop(best_i)
        mon.stack.append(idx)
        if self.turn_ditto_evo is None:
            self.turn_ditto_evo = self.turn

    def attach(self) -> None:
        def take_energy(kind: str) -> int | None:
            return self.take(self.hand, lambda idx: self.P(idx).get("energy") == kind)

        kecleon = self.find_mon("kecleon")
        ditto = self.find_mon("ditto")
        if kecleon is not None and self.attack_options(kecleon) is None:
            energy = take_energy("dce") or take_energy("counter") or take_energy("basic")
            if energy is not None:
                kecleon.energy.append(energy)
                return
        if ditto is not None and len(ditto.stack) > 1 and self.attack_options(ditto) is None:
            top = self.P(ditto.top())
            needs_three = any(len(cost) >= 3 for _, cost, _ in top["attacks"])
            energy = None
            if needs_three:
                energy = take_energy("triple")
            if energy is None:
                energy = take_energy("dce") or (take_energy("counter") if self.behind() else None) or take_energy("basic")
            if energy is not None and not (self.P(energy).get("energy") == "triple" and len(ditto.stack) == 1):
                ditto.energy.append(energy)
                return
        if ditto is not None and len(ditto.stack) == 1 and not ditto.energy:
            energy = take_energy("dce")
            if energy is not None:
                ditto.energy.append(energy)

    def switch(self) -> None:
        if self.active is None or not self.bench:
            return
        loc = next((i for i, idx in enumerate(self.hand) if self.P(idx).get("effect") == "switch"), None)
        if loc is None:
            return
        current = self.attack_options(self.active)
        best_i = None
        best_val = current[0] if current else -1
        for i, mon in enumerate(self.bench):
            option = self.attack_options(mon)
            val = option[0] if option else -1
            if val > best_val:
                best_val = val
                best_i = i
        if best_i is None:
            return
        self.discard.append(self.hand.pop(loc))
        incoming = self.bench.pop(best_i)
        self.bench.append(self.active)
        self.active = incoming

    def attack(self) -> None:
        if self.going_first and self.turn == 1:
            return
        if self.active is None:
            return
        option = self.attack_options(self.active)
        if option is None:
            return
        damage, info = option
        self.active.attacked = True
        if self.turn_first is None:
            self.turn_first = self.turn
        top = info["top"]
        if top.get("idx_name") == "kecleon" and self.turn_kecleon is None and info["tag"] == "whip":
            self.turn_kecleon = self.turn
        if any(self.P(i).get("prism") for i in self.active.stack) and len(self.active.stack) > 1 and self.turn_ditto_atk is None:
            self.turn_ditto_atk = self.turn
        if info["tag"] == "burst":
            # Power Hurricane discards all Energy attached to Volcarona.
            self.discard.extend(self.active.energy)
            self.active.energy = []
        if info["tag"] == "whip":
            self.whip_hits.append(damage)
            self.whip_types_n.append(info["types_n"] or 0)
            self.max_types = max(self.max_types, info["types_n"] or 0)
        if self.known and damage and WEAK_TO[self.opp_type] in top["types"] and info["tag"] != "whip":
            self.weakness_hit = True
        if damage >= 110 and self.my_prizes > 0:
            self.my_prizes -= 1
        if self.recovered_ready:
            self.attacks_after_recovery += 1
            self.recovered_ready = False
        if info["tag"] == "draw2":
            self.draw(2)
        if info["tag"] == "search":
            choice = self.want_stage1() or self.take(self.deck, self.is_pokemon)
            if choice is not None:
                self.hand.append(choice)
                self._shuffle_deck()

    def end_turn(self) -> None:
        for mon in self.in_play():
            keep = []
            for energy in mon.energy:
                if self.P(energy).get("energy") in {"triple", "ignition"}:
                    self.discard.append(energy)
                else:
                    keep.append(energy)
            mon.energy = keep

    def turn_tick(self) -> None:
        self.turn += 1
        if self.turn >= 2:
            self.known = True
        self.resolve_enemy_ko()
        if self.lost_game:
            return
        self.draw(1)
        if self.lost_game:
            return
        if not any(self.is_pokemon(i) for i in self.hand):
            self.empty_hand_pokemon += 1
        self.item_pass()
        self.play_supporter()
        self.item_pass()
        self._play_basics()
        self.evolve()
        self.attach()
        self.switch()
        self.attack()
        self.end_turn()
        self.types_when_attacking.append(len(self.hand_types()))

    def run(self, turns: int = 12) -> dict:
        self.setup()
        if self.seen_kecleon_turn is None and any(self.P(i).get("idx_name") == "kecleon" for i in self.hand):
            self.seen_kecleon_turn = 0
        while self.turn < turns and not self.lost_game and self.my_prizes > 0:
            self.turn_tick()
        return self.summary()

    def summary(self) -> dict:
        return {
            "mulligans": self.mulligans,
            "opened_kecleon": self.seen_kecleon_turn == 0,
            "opened_ditto": self.seen_ditto_turn == 0,
            "opened_scarf": self.seen_scarf_turn == 0,
            "saw_kecleon": self.seen_kecleon_turn is not None,
            "saw_ditto": self.seen_ditto_turn is not None,
            "saw_scarf": self.seen_scarf_turn is not None,
            "kecleon_by_3": self.seen_kecleon_turn is not None and self.seen_kecleon_turn <= 3,
            "whip_hits": self.whip_hits,
            "whip_types": self.whip_types_n,
            "turn_kecleon": self.turn_kecleon,
            "turn_ditto_evo": self.turn_ditto_evo,
            "turn_ditto_atk": self.turn_ditto_atk,
            "turn_first": self.turn_first,
            "both": self.turn_kecleon is not None and self.turn_ditto_atk is not None,
            "kecleon_recovered": self.kecleon_recovered,
            "ditto_recovered": self.ditto_recovered,
            "ditto_lost": self.ditto_lost,
            "extra_attacks": self.attacks_after_recovery,
            "weakness": self.weakness_hit,
            "scarf_ditto": self.scarf_on_ditto,
            "scarf_kecleon": self.scarf_on_kecleon,
            "lost": self.lost_game,
            "deckout": self.deckout,
            "empty_pokemon_turns": self.empty_hand_pokemon,
            "max_types": self.max_types,
            "prizes": 6 - self.my_prizes,
            "research_played": self.research_played,
        }


def _mean(values) -> float:
    return sum(values) / len(values) if values else 0.0


def _pct(flags) -> float:
    return sum(bool(v) for v in flags) / len(flags) if flags else 0.0


def hypergeometric_at_least(population: int, successes: int, draws: int, need: int = 1) -> float:
    total = math.comb(population, draws)
    below = 0
    for k in range(need):
        below += math.comb(successes, k) * math.comb(population - successes, draws - k)
    return 1 - below / total


def run_simulation(deck_name: str, going_first: bool, games: int, seed: int) -> dict:
    cards = DECKS[deck_name]
    rng = random.Random(seed)
    rows = []
    for i in range(games):
        game = Game(cards, going_first, random.Random(rng.randrange(1 << 30)))
        rows.append(game.run())
    whips = [d for row in rows for d in row["whip_hits"]]
    type_ns = [n for row in rows for n in row["whip_types"]]
    kecleon_turns = [row["turn_kecleon"] for row in rows if row["turn_kecleon"]]
    ditto_turns = [row["turn_ditto_evo"] for row in rows if row["turn_ditto_evo"]]
    first_turns = [row["turn_first"] for row in rows if row["turn_first"]]
    copies = Counter()
    for card in cards:
        copies[card.get("idx_name") or card.get("effect") or card["name"]] += card["count"]
    exact_open_kecleon = hypergeometric_at_least(60, copies.get("kecleon", 0), 7, 1)
    return {
        "deck": deck_name,
        "going_first": going_first,
        "games": games,
        "seed": seed,
        "exact_open_kecleon_ignoring_mulligan": exact_open_kecleon,
        "mulligan_rate": _mean([row["mulligans"] > 0 for row in rows]),
        "mean_mulligans": _mean([row["mulligans"] for row in rows]),
        "p_open_kecleon": _pct([row["opened_kecleon"] for row in rows]),
        "p_kecleon_by_turn_3": _pct([row["kecleon_by_3"] for row in rows]),
        "p_open_ditto": _pct([row["opened_ditto"] for row in rows]),
        "p_saw_ditto": _pct([row["saw_ditto"] for row in rows]),
        "p_open_scarf": _pct([row["opened_scarf"] for row in rows]),
        "p_saw_scarf": _pct([row["saw_scarf"] for row in rows]),
        "p_scarf_on_ditto": _pct([row["scarf_ditto"] for row in rows]),
        "p_scarf_on_kecleon": _pct([row["scarf_kecleon"] for row in rows]),
        "p_kecleon_attack": _pct([row["turn_kecleon"] for row in rows]),
        "mean_turn_kecleon_attack": _mean(kecleon_turns),
        "p_ditto_evolved": _pct([row["turn_ditto_evo"] for row in rows]),
        "mean_turn_ditto_evolved": _mean(ditto_turns),
        "p_ditto_attack": _pct([row["turn_ditto_atk"] for row in rows]),
        "p_both_engines": _pct([row["both"] for row in rows]),
        "p_any_attacker": _pct([row["turn_first"] for row in rows]),
        "mean_turn_first_attacker": _mean(first_turns),
        "p_weakness": _pct([row["weakness"] for row in rows]),
        "mean_whip": _mean(whips),
        "mean_types_on_whip": _mean(type_ns),
        "mean_best_types": _mean([row["max_types"] for row in rows]),
        "p_whip_180": _pct([max(row["whip_hits"], default=0) >= 180 for row in rows]),
        "p_whip_240": _pct([max(row["whip_hits"], default=0) >= 240 for row in rows]),
        "p_whip_270": _pct([max(row["whip_hits"], default=0) >= 270 for row in rows]),
        "p_whip_300": _pct([max(row["whip_hits"], default=0) >= 300 for row in rows]),
        "p_whip_330": _pct([max(row["whip_hits"], default=0) >= 330 for row in rows]),
        "p_kecleon_recovered": _pct([row["kecleon_recovered"] for row in rows]),
        "p_ditto_recovered": _pct([row["ditto_recovered"] for row in rows]),
        "p_ditto_lost": _pct([row["ditto_lost"] for row in rows]),
        "mean_extra_attacks": _mean([row["extra_attacks"] for row in rows]),
        "p_loss": _pct([row["lost"] for row in rows]),
        "p_deckout": _pct([row["deckout"] for row in rows]),
        "mean_empty_pokemon_turns": _mean([row["empty_pokemon_turns"] for row in rows]),
        "mean_prizes": _mean([row["prizes"] for row in rows]),
        "whip_attacks_per_game": len(whips) / games,
    }


def decklist_rows(deck_name: str) -> list[dict]:
    rows = []
    for card in DECKS[deck_name]:
        rows.append({
            "count": card["count"],
            "name": card["name"],
            "set": card.get("set"),
            "number": card.get("number"),
            "kind": card["kind"],
            "types": list(card.get("types") or []),
            "stage": card.get("stage"),
        })
    return rows


def main() -> None:
    games = 100_000
    seed = 20261113
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = {"assumptions": ASSUMPTIONS, "runs": []}
    for name in ("rainbow", "hybrid", "toolbox"):
        if deck_size(DECKS[name]) != 60:
            raise SystemExit(f"{name} is {deck_size(DECKS[name])} cards")
        for going_first in (False, True):
            print(f"sim {name} going_first={going_first} n={games}", flush=True)
            results["runs"].append(run_simulation(name, going_first, games, seed))
    path = OUT_DIR / "simulation_results.json"
    path.write_text(json.dumps(results, indent=2))
    print(path)


if __name__ == "__main__":
    main()
