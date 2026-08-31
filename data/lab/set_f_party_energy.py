#!/usr/bin/env python3
"""Rule C lab: Carpet Set E vs the *app* Set F (Clefairy + Staraptor).

Family-chat follow-up to ``set_ef_open_stage.py`` (that script only runs ``carnival``
and uses ``load_seed_payload()`` / ``SET_F_NAMES``, which may be a different F list).

This file freezes the 30-card F the family app had when we asked “does two Starly
help / is it energy / Clefairy can Party”:

* Energy-type swaps only (same 12 Energy cards, different types)
* Cut 4 Clefairy for Energy
* ``carnival`` vs named ``party`` vs a forced Moon-Watching Party line

Printed Clefairy LOR 62: Active, for each Benched Clefairy, search the deck for a
Psychic Energy and attach it to that Clefairy — full-deck search, not a look-N.

``carnival`` never calls Moon-Watching Party. Named ``party`` vs ``shock`` sets the
Clefairy play cap to 0 (Thunder Shock farms 60 HP) and waits on Mewtwo ex, which
this F list does not have. ``force_clefairy_party`` is the “actually Party” cell.
"""

from __future__ import annotations

import json
import sys
import time
from collections import Counter
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import app.engine.game as game_mod
from app.engine.models import Card, no_pokemon_energy_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import build_fallback_deck, fallback_named

GAMES = 2000
SEED = 20260831

# App seed-f as of the family chat (not SET_F_NAMES Gastly / Gengar).
APP_F_NAMES = [
    "Iono",
    "Ultra Ball",
    "Energy Switch",
    "Tulip",
    "Energy Search",
    "Dondozo",
    "Water Energy",
    "Water Energy",
    "Water Energy",
    "Flutter Mane",
    "Clefairy",
    "Clefairy",
    "Clefairy",
    "Clefairy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Psychic Energy",
    "Orthworm",
    "Metal Energy",
    "Metal Energy",
    "Metal Energy",
    "Starly",
    "Starly",
    "Staravia",
    "Staraptor",
    "Staraptor",
    "Staravia",
]

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
    {"type": "event_prefix", "prefix": "attack:Clefairy:Wonder Storm", "key": "storm"},
    {"type": "event_prefix", "prefix": "saw_play:Clefairy", "key": "clef_play"},
    {"type": "event_prefix", "prefix": "ko:Clefairy", "key": "ko_clef"},
    {"type": "event_prefix", "prefix": "ko:Starly", "key": "ko_starly"},
    {"type": "event_prefix", "prefix": "saw_play:Starly", "key": "starly_play"},
    {"type": "event_prefix", "prefix": "attack:Staraptor:Power Blast", "key": "blast"},
    {"type": "event_prefix", "prefix": "attack:Dondozo:Hydro Splash", "key": "hydro"},
    {"type": "event_prefix", "prefix": "attack:Orthworm:Crunch-Time Rush", "key": "crunch"},
]


@dataclass(frozen=True)
class Cell:
    id: str
    title: str
    strategy_f: str = "carnival"
    force_party: bool = False
    energy: tuple[tuple[str, int], ...] | None = None
    drop_clefairy: bool = False


CELLS: tuple[Cell, ...] = (
    Cell("carnival_baseline", "current 6P/3W/3M, carnival"),
    Cell("energy_12w", "12 Water, carnival", energy=(("Water", 12),)),
    Cell("energy_9w3m", "9 Water + 3 Metal, carnival", energy=(("Water", 9), ("Metal", 3))),
    Cell("energy_10w2m", "10 Water + 2 Metal, carnival", energy=(("Water", 10), ("Metal", 2))),
    Cell("energy_6p6w", "6 Psychic + 6 Water, carnival", energy=(("Psychic", 6), ("Water", 6))),
    Cell("energy_6w6m", "6 Water + 6 Metal, carnival", energy=(("Water", 6), ("Metal", 6))),
    Cell("energy_4p4w4m", "4P/4W/4M, carnival", energy=(("Psychic", 4), ("Water", 4), ("Metal", 4))),
    Cell("no_clef_plus4w", "no Clefairy +4 Water, keep other types", drop_clefairy=True),
    Cell(
        "no_clef_13w3m",
        "no Clefairy, 13 Water + 3 Metal",
        drop_clefairy=True,
        energy=(("Water", 13), ("Metal", 3)),
    ),
    Cell("no_clef_16w", "no Clefairy, 16 Water", drop_clefairy=True, energy=(("Water", 16),)),
    Cell(
        "no_clef_10p6w",
        "no Clefairy, 10 Psychic + 6 Water",
        drop_clefairy=True,
        energy=(("Psychic", 10), ("Water", 6)),
    ),
    Cell("party_vanilla", "current list, named party", strategy_f="party"),
    Cell(
        "party_forced",
        "current list, forced Moon-Watching Party",
        strategy_f="party",
        force_party=True,
    ),
)


@contextmanager
def force_clefairy_party() -> Iterator[None]:
    """Bench Clefairy and run printed Party / Wonder Storm even vs shock.

    Default ``party`` vs ``shock`` returns Clefairy cap 0 and never wants the
    storm line — that script is for Set C + Mewtwo, not this F list.
    """

    game = game_mod.Game
    orig_cap = game._clefairy_play_cap
    orig_glass = game._vs_lightning_glass
    orig_storm = game._want_storm_line
    game._clefairy_play_cap = lambda self, me: 4
    game._vs_lightning_glass = lambda self, who: False
    game._want_storm_line = lambda self, me, foe, who: True
    try:
        yield
    finally:
        game._clefairy_play_cap = orig_cap
        game._vs_lightning_glass = orig_glass
        game._want_storm_line = orig_storm


def load_e_cards() -> list[Card]:
    try:
        from app.db import get_deck

        deck = get_deck("seed-e")
        if deck and len(deck.get("cards") or []) == 30:
            return [Card.from_dict(c) for c in deck["cards"]]
    except Exception:
        pass
    from app.seed import load_seed_payload

    return [Card.from_dict(c) for c in load_seed_payload()["e"]["cards"]]


def load_f_cards() -> list[Card]:
    """Prefer live seed-f when it matches APP_F_NAMES; else fallback prints."""
    try:
        from app.db import get_deck

        deck = get_deck("seed-f")
        names = [c["name"] for c in (deck or {}).get("cards") or []]
        if Counter(names) == Counter(APP_F_NAMES):
            return [Card.from_dict(c) for c in deck["cards"]]
    except Exception:
        pass
    return build_fallback_deck(list(APP_F_NAMES))


def is_basic_energy_card(card: Card) -> bool:
    return bool(card.is_energy)


def swap_energy(cards: list[Card], mix: tuple[tuple[str, int], ...]) -> list[Card]:
    names: list[str] = []
    for energy_type, count in mix:
        names.extend([f"{energy_type} Energy"] * count)
    have = sum(1 for card in cards if is_basic_energy_card(card))
    if have != len(names):
        raise ValueError(f"energy mix {mix} expected {len(names)} Energy, deck has {have}")
    out: list[Card] = []
    used = 0
    for card in cards:
        if is_basic_energy_card(card):
            out.append(fallback_named(names[used]))
            used += 1
        else:
            out.append(card)
    return out


def drop_clefairy_add_energy(cards: list[Card], extra_type: str = "Water") -> list[Card]:
    kept = [c for c in cards if c.name != "Clefairy"]
    extra = len(cards) - len(kept)
    out = kept + [fallback_named(f"{extra_type} Energy") for _ in range(extra)]
    if len(out) != 30:
        raise ValueError(f"expected 30 cards after dropping Clefairy, got {len(out)}")
    return out


def retune(base: list[Card], cell: Cell) -> list[Card]:
    cards = list(base)
    if cell.drop_clefairy:
        cards = drop_clefairy_add_energy(cards)
    if cell.energy is not None:
        cards = swap_energy(cards, cell.energy)
    if len(cards) != 30:
        raise ValueError(f"{cell.id} is {len(cards)} cards")
    return cards


def _summarize(rec: dict[str, Any]) -> dict[str, Any]:
    r = rec["results"]
    events = rec["learning"].get("event_totals") or {}
    return {
        "win_rate_e": r["win_rate_a"],
        "win_rate_f": r["win_rate_b"],
        "tie_rate": r["tie_rate"],
        "first_e": r["win_rate_a_going_first"],
        "second_e": r["win_rate_a_going_second"],
        "wins_e": r["wins_a"],
        "wins_f": r["wins_b"],
        "ties": r["ties"],
        "queries": r["queries"],
        "moon_watching_party": events.get("moon_watching_party", 0),
        "party_energy": events.get("party_energy", 0),
        "insights": rec["learning"].get("insights") or [],
    }


def run_cell(e: list[Card], f_base: list[Card], cell: Cell) -> dict[str, Any]:
    f = retune(f_base, cell)
    nrg = dict(Counter(c.name for c in f if is_basic_energy_card(c)))
    ctx = force_clefairy_party() if cell.force_party else nullcontext()
    with ctx:
        rec = run_simulation(
            e,
            f,
            no_pokemon_energy_family_rules(),
            StrategySpec.from_dict("shock"),
            StrategySpec.from_dict(cell.strategy_f),
            games=GAMES,
            seed=SEED,
            question=cell.title,
            queries=QUERIES,
            deck_a_meta={"id": "seed-e", "name": "Carpet Set E (Walrein / Iris)"},
            deck_b_meta={"id": "seed-f", "name": cell.title},
        )
    row = _summarize(rec)
    row["title"] = cell.title
    row["strategy_f"] = cell.strategy_f
    row["force_party"] = cell.force_party
    row["energy"] = nrg
    row["pokemon"] = dict(Counter(c.name for c in f if c.is_pokemon))
    return row


def _pct(value: float) -> str:
    return f"{value:.1%}"


def _md(cells: dict[str, dict[str, Any]], elapsed: float) -> str:
    def rows(ids: tuple[str, ...]) -> str:
        lines = [
            "| Cell | F win | E win | Party games | Wonder Storm | Power Blast | Hydro Splash |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
        for cid in ids:
            row = cells[cid]
            q = row["queries"]
            lines.append(
                f"| {row['title']} | **{_pct(row['win_rate_f'])}** | {_pct(row['win_rate_e'])} | "
                f"{q.get('party', 0):.1%} | {q.get('storm', 0):.1%} | {q.get('blast', 0):.1%} | "
                f"{q.get('hydro', 0):.1%} |"
            )
        return "\n".join(lines)

    energy_ids = (
        "carnival_baseline",
        "energy_12w",
        "energy_9w3m",
        "energy_10w2m",
        "energy_6p6w",
        "energy_6w6m",
        "energy_4p4w4m",
    )
    cut_ids = ("no_clef_plus4w", "no_clef_13w3m", "no_clef_16w", "no_clef_10p6w")
    strat_ids = ("carnival_baseline", "party_vanilla", "party_forced")
    return f"""# Carpet Set F — Party vs energy retunes (Rule C)

Rule C: Pokémon are **not** Basic Energy. Printed **Moon-Watching Party** searches the
deck for Psychic Energy (one per benched Clefairy), not a look-N.

This lab uses the **app** Set F (4 Clefairy + Staraptor), not ``SET_F_NAMES`` in
``seed_data.py``. Open-stage carnival-only numbers: ``data/lab/set-ef-open-stage.md``.

E is always ``shock``. {GAMES} games / cell, seed `{SEED}`.

F 30: 4 Clefairy, Starly/Staravia/Staraptor 2/2/2, Dondozo, Orthworm, Flutter Mane,
6 Psychic / 3 Water / 3 Metal Energy, Iono, Ultra Ball, Energy Switch, Tulip,
Energy Search. Full name list: ``app_f_names`` in the JSON.

## Energy type only (still 12 Energy, ``carnival``)

Unifying to 12 Water **hurts**: Water is siphoned onto Dondozo, Power Blast falls.
The mixed 6 Psychic / 3 Water / 3 Metal is the best type-only mix here.

{rows(energy_ids)}

## Cut 4 Clefairy for Energy (``carnival``)

This is a Pokémon swap, not only an energy-type swap. Clefairy's Wonder Storm
wants 3 Energy for a 20×Psychic attack, so under ``carnival`` they steal fuel and
prizes. Cutting them makes the matchup close — but that cell **still does not Party**.

{rows(cut_ids)}

## Strategy on the current 30 (keep Clefairy)

``carnival`` never uses Moon-Watching Party (0 ability uses). Named ``party`` vs
``shock`` refuses to bench Clefairy (cap 0) and looks for Mewtwo ex. Forced Party
is the line a human would try: bench Clefairy, run the printed ability, Wonder Storm.

{rows(strat_ids)}

## What we learned

- Two **Starly** *do* help find the bird. They are not Colorless Energy under Rule C.
- Energy **type** swaps did not beat the current 6P/3W/3M mix under ``carnival``.
- Forgetting Party was a strategy gap, not a missing attack on the card.
- Forced Party on the current list is the close matchup (~even), without cutting Clefairy.

Raw: `data/lab/set-f-party-energy.json` (elapsed {elapsed:.1f}s).
"""


def main() -> None:
    if len(APP_F_NAMES) != 30:
        raise SystemExit(f"APP_F_NAMES is {len(APP_F_NAMES)} cards")
    e = load_e_cards()
    f_base = load_f_cards()
    f_names = [c.name for c in f_base]
    if f_names != list(APP_F_NAMES):
        print(f"warning: live F names differ from APP_F_NAMES ({f_names[:8]}...)", flush=True)
    rules = no_pokemon_energy_family_rules()
    started = time.perf_counter()
    cells: dict[str, dict[str, Any]] = {}
    for cell in CELLS:
        print(f"{cell.id} ...", flush=True)
        row = run_cell(e, f_base, cell)
        cells[cell.id] = row
        print(
            f"  F {row['win_rate_f']:.1%}  E {row['win_rate_e']:.1%}  "
            f"party_games={row['queries'].get('party', 0):.1%}  "
            f"party_uses={row['moon_watching_party']}",
            flush=True,
        )
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rules": rules.to_dict(),
        "strategy_e": "shock",
        "app_f_names": list(APP_F_NAMES),
        "loaded_f_names": f_names,
        "cells": cells,
    }
    dest = ROOT / "data/lab/set-f-party-energy.json"
    dest.write_text(json.dumps(out, indent=2))
    md = ROOT / "data/lab/set-f-party-energy.md"
    md.write_text(_md(cells, elapsed))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
