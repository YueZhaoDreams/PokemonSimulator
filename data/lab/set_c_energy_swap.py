#!/usr/bin/env python3
"""Bake off Set C's last Psychic Energy vs Clefable-line copies. 1k games / cell, seed 20260823."""

from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, as_completed

from app.engine.models import Card, default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload

GAMES = 3000
SEED = 20260819
FOES = ("a", "b", "d", "s", "t")
STRATS = {"a": "thrifty", "b": "shock", "c": "party", "d": "demolish", "s": "slash", "t": "phantom"}

# 28-card core; each package is the last two slots (Boss is already locked).
PACKAGES = {
    "energy_boss": ["Psychic Energy", "Boss's Orders"],
    "clefable_boss": ["Clefable", "Boss's Orders"],
    "clefable_ex_boss": ["Clefable ex", "Boss's Orders"],
    "mega_boss": ["Mega Clefable ex", "Boss's Orders"],
}


CORE = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 2
    + ["Clefable"] * 4
    + ["Clefable ex"] * 4
    + ["Mega Clefable ex"] * 3
    + ["Hop"] * 3
    + ["Nest Ball"] * 2
    + ["Energy Search"] * 3
    + ["Maximum Belt"]
    + ["Tool Box"]
    + ["Arven"]
)


def _c_list(adds: list[str]) -> list[str]:
    names = list(CORE) + list(adds)
    assert len(names) == 30
    return names


def _run(pkg: str, foe: str) -> tuple[str, str, float]:
    from app.seed_data import build_fallback_deck

    payload = load_seed_payload()
    c = build_fallback_deck(_c_list(PACKAGES[pkg]))
    b = [Card.from_dict(x) for x in payload[foe]["cards"]]
    rec = run_simulation(
        c,
        b,
        default_family_rules(),
        StrategySpec.from_dict("party"),
        StrategySpec.from_dict(STRATS[foe]),
        games=GAMES,
        seed=SEED,
        queries=[],
    )
    return pkg, foe, rec["results"]["win_rate_a"]


def main() -> None:
    pairs = [(pkg, foe) for pkg in PACKAGES for foe in FOES]
    scores: dict[str, dict[str, float]] = {pkg: {} for pkg in PACKAGES}
    with ProcessPoolExecutor(max_workers=min(8, len(pairs))) as pool:
        futs = [pool.submit(_run, pkg, foe) for pkg, foe in pairs]
        for fut in as_completed(futs):
            pkg, foe, rate = fut.result()
            scores[pkg][foe] = rate
            print(f"{pkg:16} vs {foe.upper()}: {rate:.1%}", flush=True)
    print("\n| package | A | B | D | S | T | mean | D+T |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    ranked = []
    for pkg, row in scores.items():
        mean = sum(row[f] for f in FOES) / len(FOES)
        dt = (row["d"] + row["t"]) / 2
        ranked.append((dt, mean, pkg, row))
    ranked.sort(reverse=True)
    for dt, mean, pkg, row in ranked:
        cells = " | ".join(f"{row[f]:.1%}" for f in FOES)
        print(f"| {pkg} | {cells} | {mean:.1%} | {dt:.1%} |")


if __name__ == "__main__":
    main()
