"""Compare 3 Hop vs 2 Hop + 1 SM Lillie (UPR: until 6, until 8 on your first turn).

Family Cup: first player cannot play a Supporter on turn 1, so the 8-card
draw is the second player's first turn. Later turns are draw-until-6.

Only C-involved cells move. 3000 games / ordered pair, seed 20260819.
"""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from app.engine.models import Card, default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload
from app.seed_data import build_fallback_deck

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260819
STRATS = {"a": "thrifty", "b": "shock", "c": "party", "d": "demolish", "s": "slash", "t": "phantom"}
FOES = ("a", "b", "d", "s", "t")

BODY = (
    ["Clefairy"] * 4
    + ["Mewtwo ex"] * 2
    + ["Clefable"] * 4
    + ["Clefable ex"] * 4
    + ["Mega Clefable ex"] * 4
)
TAIL = (
    ["Nest Ball"] * 2
    + ["Energy Search"] * 3
    + ["Maximum Belt", "Tool Box", "Arven", "Boss's Orders"]
)

VARIANTS: dict[str, list[str]] = {
    "three_hop": list(BODY) + ["Hop"] * 3 + list(TAIL),
    "two_hop_lillie": list(BODY) + ["Hop"] * 2 + ["Lillie"] + list(TAIL),
}


def _run(variant: str, left: str, right: str) -> tuple[str, str, str, dict]:
    payload = load_seed_payload()
    names = VARIANTS[variant]
    assert len(names) == 30, (variant, len(names))
    c_cards = build_fallback_deck(list(names))

    def deck(key: str) -> list[Card]:
        if key == "c":
            return list(c_cards)
        return [Card.from_dict(card) for card in payload[key]["cards"]]

    rec = run_simulation(
        deck(left),
        deck(right),
        default_family_rules(),
        StrategySpec.from_dict(STRATS[left]),
        StrategySpec.from_dict(STRATS[right]),
        games=GAMES,
        seed=SEED,
        queries=[],
    )
    r = rec["results"]
    return variant, left, right, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
    }


def main() -> None:
    started = time.perf_counter()
    jobs = []
    for variant in VARIANTS:
        for foe in FOES:
            jobs.append((variant, "c", foe))
            jobs.append((variant, foe, "c"))
    results: dict[str, dict[str, dict[str, dict]]] = {v: {} for v in VARIANTS}
    with ProcessPoolExecutor(max_workers=min(8, len(jobs))) as pool:
        futs = [pool.submit(_run, *job) for job in jobs]
        for fut in as_completed(futs):
            variant, left, right, detail = fut.result()
            results[variant].setdefault(left, {})[right] = detail
            print(
                f"{variant:16} {left.upper()} vs {right.upper()}: {detail['a']:.1%}",
                flush=True,
            )
    elapsed = time.perf_counter() - started
    print("\nC row (C's win rate) and T vs C\n")
    print("| cut | vs A | vs B | vs D | vs S | vs T | T vs C | C avg |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    scored: list[tuple[float, str]] = []
    for variant, matrix in results.items():
        row = [matrix["c"][f]["a"] for f in FOES]
        avg = sum(row) / len(row)
        t_vs_c = matrix["t"]["c"]["a"]
        scored.append((avg, variant))
        cells = " | ".join(f"{matrix['c'][f]['a']:.1%}" for f in FOES)
        print(f"| `{variant}` | {cells} | {t_vs_c:.1%} | {avg:.1%} |")
    scored.sort(reverse=True)
    print(f"\nbest C-row average: {scored[0][1]} ({scored[0][0]:.1%})")
    dest = ROOT / "data/lab/c-sm-lillie-hop.json"
    dest.write_text(
        json.dumps(
            {"games": GAMES, "seed": SEED, "elapsed": elapsed, "variants": results},
            indent=2,
        )
    )
    print(f"elapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
