#!/usr/bin/env python3
"""Set C bakeoff: 4× LOR 62 Party vs mixing 151 MEW 035 Invitation Clefairy.

Same 4-of Clefairy name. Invitation is an attack that benches up to 3 Clefairy.
The locked list has no Switch, so Party only fires from Active.
"""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed

from app.engine.models import Card, default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import SET_C_NAMES, build_fallback_deck

GAMES = 3000
SEED = 20260819
FOES = ("a", "b", "d", "s", "t")
STRATS = {"a": "thrifty", "b": "shock", "c": "party", "d": "demolish", "s": "slash", "t": "phantom"}

QUERIES = [
    {"type": "event_prefix", "prefix": "moon_viewing_invitation", "key": "invitation"},
    {"type": "event_prefix", "prefix": "moon_watching_party", "key": "party"},
]


def _c_names(invite: int) -> list[str]:
    rest = [name for name in SET_C_NAMES if name != "Clefairy"]
    names = ["Clefairy MEW"] * invite + ["Clefairy"] * (4 - invite) + rest
    assert len(names) == 30, len(names)
    return names


PACKAGES = {
    "4 party": _c_names(0),
    "3 party + 1 invite": _c_names(1),
    "2 party + 2 invite": _c_names(2),
}


def _run(pkg: str, foe: str) -> tuple[str, str, dict]:
    payload = load_seed_payload()
    c = build_fallback_deck(PACKAGES[pkg])
    b = [Card.from_dict(x) for x in payload[foe]["cards"]]
    rec = run_simulation(
        c,
        b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(STRATS[foe]),
        games=GAMES,
        seed=SEED,
        queries=QUERIES,
    )
    r = rec["results"]
    return pkg, foe, {
        "a": r["win_rate_a"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
        "invitation": r["queries"].get("invitation", 0.0),
        "party": r["queries"].get("party", 0.0),
    }


def main() -> None:
    pairs = [(pkg, foe) for pkg in PACKAGES for foe in FOES]
    scores: dict[str, dict[str, dict]] = {pkg: {} for pkg in PACKAGES}
    with ProcessPoolExecutor(max_workers=min(8, len(pairs))) as pool:
        futs = [pool.submit(_run, pkg, foe) for pkg, foe in pairs]
        for fut in as_completed(futs):
            pkg, foe, row = fut.result()
            scores[pkg][foe] = row
            print(
                f"{pkg:20} vs {foe.upper()}: {row['a']:.1%}  "
                f"(first {row['first']:.1%} / second {row['second']:.1%}, "
                f"invite {row['invitation']:.1%})",
                flush=True,
            )
    print("\n| package | A | B | D | S | T | mean | D+T | invite vs D |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    ranked = []
    for pkg, rows in scores.items():
        mean = sum(rows[f]["a"] for f in FOES) / len(FOES)
        dt = (rows["d"]["a"] + rows["t"]["a"]) / 2
        ranked.append((dt, mean, pkg, rows))
    ranked.sort(reverse=True)
    for dt, mean, pkg, rows in ranked:
        cells = " | ".join(f"{rows[f]['a']:.1%}" for f in FOES)
        print(f"| {pkg} | {cells} | {mean:.1%} | {dt:.1%} | {rows['d']['invitation']:.1%} |")
    print("\nVs D first/second:")
    for pkg, rows in scores.items():
        d = rows["d"]
        print(f"  {pkg}: {d['a']:.1%}  first {d['first']:.1%}  second {d['second']:.1%}")


if __name__ == "__main__":
    main()
