#!/usr/bin/env python3
"""What Set M's Boss's Orders and Counter Catcher plays did, turn by turn.

`run LABEL OUT.json [GAMES]` plays the locked Set M against the six foes and records every Boss's Orders
and Counter Catcher play: what the Active Spot could already Knock Out, what the pulled Pokémon was, and
whether a prize came of it that turn. The check only reads the board, so it runs on any commit; the
"before" column of `set-m-gust-audit.md` is this script on the commit before the gust fix.

`render BEFORE.json AFTER.json` writes `set-m-gust-audit.json` and `set-m-gust-audit.md`.
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from app.engine import game as G  # noqa: E402
from app.engine.models import standard_60_rules  # noqa: E402
from app.engine.strategies import StrategySpec  # noqa: E402
from app.seed_data import SET_M60_NAMES, build_fallback_deck  # noqa: E402
from set_m_sky_field import FOES  # noqa: E402

SEED = 20261007
GAMES = 300
TRAINERS = ("Boss's Orders", "Counter Catcher")


def audit_foe(foe_names, foe_strat: str, games: int) -> list[dict]:
    rng = random.Random(SEED)
    deck_a = build_fallback_deck(list(SET_M60_NAMES))
    deck_b = build_fallback_deck(list(foe_names))
    strat_a = StrategySpec.from_dict("mew_baby")
    strat_b = StrategySpec.from_dict(foe_strat)
    rows: list[dict] = []
    cur: dict = {"trainer": None, "turn_rows": []}

    orig_resolve = G.Game._resolve_trainer
    orig_boss = G.Game._boss_orders
    orig_turn = G.Game._take_turn

    def resolve(self, me, foe, card, who=None, card_i=None):
        cur["trainer"] = card.name if me.name == "A" else None
        try:
            return orig_resolve(self, me, foe, card, who=who, card_i=card_i)
        finally:
            cur["trainer"] = None

    def boss(self, me, foe):
        if me.name == "A" and cur["trainer"] in TRAINERS and foe.bench and foe.active:
            can_ko = self._attacker_can_ko_active(me, foe)
            active_prizes = self._prizes_for_ko(foe.card(foe.active.card_i)) if can_ko else 0
            target = self._boss_pull_target(foe, me, "a")
            target_ko = False
            target_prizes = 0
            if target is not None:
                restore = self._view_as_active(foe, target)
                try:
                    target_ko = self._attacker_can_ko_active(me, foe)
                    target_prizes = self._prizes_for_ko(foe.card(foe.active.card_i)) if target_ko else 0
                finally:
                    restore()
            cur["turn_rows"].append(
                {
                    "trainer": cur["trainer"],
                    "active_ko": can_ko,
                    "active_prizes": active_prizes,
                    "target_ko": target_ko,
                    "target_prizes": target_prizes,
                    "target": target,
                }
            )
        return orig_boss(self, me, foe)

    def take_turn(self, who):
        if who != "a":
            return orig_turn(self, who)
        cur["turn_rows"] = []
        before = self.players["a"].prizes_taken
        result = orig_turn(self, who)
        foe_player = self.players["b"]
        gained = self.players["a"].prizes_taken - before
        for rec in cur["turn_rows"]:
            rec["gained"] = gained
            rec["target_gone"] = rec["target"] not in foe_player.in_play()
            rec.pop("target")
            rows.append(rec)
        return result

    G.Game._resolve_trainer = resolve
    G.Game._boss_orders = boss
    G.Game._take_turn = take_turn
    try:
        for _ in range(games):
            G.play_game(deck_a, deck_b, standard_60_rules(), strat_a, strat_b, rng)
    finally:
        G.Game._resolve_trainer = orig_resolve
        G.Game._boss_orders = orig_boss
        G.Game._take_turn = orig_turn
    return rows


def summarize(rows: list[dict], games: int) -> dict:
    out = {}
    for name in TRAINERS:
        mine = [r for r in rows if r["trainer"] == name]
        n = len(mine)
        if not n:
            out[name] = {"plays": 0, "per_game": 0.0}
            continue
        worse = [
            r
            for r in mine
            if r["active_ko"] and (not r["target_ko"] or r["target_prizes"] < r["active_prizes"])
        ]
        out[name] = {
            "plays": n,
            "per_game": n / games,
            "no_prize_that_turn": sum(1 for r in mine if r["gained"] == 0) / n,
            "target_knocked_out": sum(r["target_gone"] for r in mine) / n,
            "active_already_knocked_out": sum(r["active_ko"] for r in mine) / n,
            "pull_worse_than_active": len(worse) / n,
            "prizes_that_turn": sum(r["gained"] for r in mine) / n,
        }
    return out


def run(label: str, dest: Path, games: int) -> None:
    started = time.perf_counter()
    every: list[dict] = []
    foes = {}
    for key, _name, names, strat in FOES:
        rows = audit_foe(names, strat, games)
        every.extend(rows)
        foes[key] = summarize(rows, games)
        print(f"{label} {key}: {json.dumps(foes[key][TRAINERS[0]])}", flush=True)
    report = {
        "label": label,
        "seed": SEED,
        "games_per_foe": games,
        "elapsed": time.perf_counter() - started,
        "all": summarize(every, games * len(FOES)),
        "foes": foes,
    }
    dest.write_text(json.dumps(report, indent=1) + "\n")


def pct(value: float) -> str:
    return f"{value:.0%}"


def render(before: dict, after: dict) -> str:
    lines = [
        "# Set M gust audit: Boss's Orders and Counter Catcher plays",
        "",
        "The locked Set M (`SET_M60_NAMES`: one Boss's Orders, two Counter Catcher) against the six foes, "
        f"{before['games_per_foe']} games per foe on seed `{before['seed']}`. "
        "Every play is checked at the moment it is made and again at the end of the turn. "
        "`before` is the engine before the gust fix, `after` is the engine after it. "
        "Both columns come from `data/lab/set_m_gust_audit.py`.",
        "",
        "| Card | Measure | Before | After |",
        "| :--- | :--- | ---: | ---: |",
    ]
    measures = [
        ("per_game", "Plays per game", lambda v: f"{v:.3f}"),
        ("no_prize_that_turn", "Plays with no prize that turn", pct),
        ("target_knocked_out", "Pulled Pokémon Knocked Out that turn", pct),
        ("active_already_knocked_out", "Active could already be Knocked Out", pct),
        ("pull_worse_than_active", "Active could be Knocked Out, pull cannot or takes fewer prizes", pct),
        ("prizes_that_turn", "Prizes taken that turn, per play", lambda v: f"{v:.2f}"),
    ]
    for name in TRAINERS:
        for key, text, fmt in measures:
            b = before["all"][name].get(key)
            a = after["all"][name].get(key)
            lines.append(
                f"| {name} | {text} | {fmt(b) if b is not None else '—'} | {fmt(a) if a is not None else '—'} |"
            )
    lines.extend(["", "## Boss's Orders by foe", "", "| Foe | Plays per game (before) | (after) | No prize that turn (before) | (after) |", "| :--- | ---: | ---: | ---: | ---: |"])
    for key, *_ in FOES:
        b = before["foes"][key]["Boss's Orders"]
        a = after["foes"][key]["Boss's Orders"]
        lines.append(
            f"| {key} | {b['per_game']:.3f} | {a['per_game']:.3f} | "
            f"{pct(b['no_prize_that_turn']) if b['plays'] else '—'} | {pct(a['no_prize_that_turn']) if a['plays'] else '—'} |"
        )
    lines.extend(
        [
            "",
            "## What was wrong",
            "",
            "- Boss's Orders scored +8 whenever the opponent had a Bench, level with or above Professor's Research and above Arven, "
            "so it was played before the draw and used the Supporter for the turn even when the pull changed nothing.",
            "- Counter Catcher scored +10 whenever Set M was behind on prizes, again with no check that the pull helped.",
            "- The pull was the lowest remaining HP on the Bench, not the Knock Out that takes the most prizes.",
            "- The only check, \"this gust wins the game\", looked at every Benched Pokémon, but the pull took only the lowest-HP one.",
            "- That check used the Active Spot's own attack, so a Bench Pokémon the Active could retreat into never counted.",
            "",
            "## The fix",
            "",
            "Set M plays Boss's Orders or Counter Catcher only when the Pokémon it pulls can be Knocked Out this turn for more prizes "
            "than the Active Spot already gives, counting a Benched attacker the Active can retreat for. The pull is that Knock Out, "
            "most prizes first, then most attached Energy. Counter Catcher still needs more Prize cards remaining than the opponent, "
            "as printed, and goes ahead of Boss's Orders so the Supporter stays in hand (`tests/test_mew_gust.py`).",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "run" and len(sys.argv) >= 4:
        games = int(sys.argv[4]) if len(sys.argv) > 4 else GAMES
        run(sys.argv[2], Path(sys.argv[3]), games)
    elif mode == "render" and len(sys.argv) == 4:
        before = json.loads(Path(sys.argv[2]).read_text())
        after = json.loads(Path(sys.argv[3]).read_text())
        (HERE / "set-m-gust-audit.json").write_text(json.dumps({"before": before, "after": after}, indent=1) + "\n")
        (HERE / "set-m-gust-audit.md").write_text(render(before, after))
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main()
