"""Family Cup 30-card A–T win-rate matrix. 3k games / ordered pair, seed 20260819."""

from __future__ import annotations

import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from app.engine.models import Card, default_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260819
STRATS = {"a": "thrifty", "b": "shock", "c": "party", "d": "demolish", "s": "slash", "t": "phantom"}
KEYS = ("a", "b", "c", "d", "s", "t")


def _run_cell(left: str, right: str) -> tuple[str, str, dict]:
    payload = load_seed_payload()
    a = [Card.from_dict(c) for c in payload[left]["cards"]]
    b = [Card.from_dict(c) for c in payload[right]["cards"]]
    rec = run_simulation(
        a,
        b,
        default_family_rules(),
        StrategySpec.from_dict(STRATS[left]),
        StrategySpec.from_dict(STRATS[right]),
        games=GAMES,
        seed=SEED,
        queries=[],
    )
    r = rec["results"]
    return left, right, {
        "a": r["win_rate_a"],
        "b": r["win_rate_b"],
        "tie": r["tie_rate"],
        "first": r["win_rate_a_going_first"],
        "second": r["win_rate_a_going_second"],
    }


def main() -> None:
    started = time.perf_counter()
    matrix: dict[str, dict[str, dict]] = {k: {} for k in KEYS}
    pairs = [(i, j) for i in KEYS for j in KEYS if i != j]
    with ProcessPoolExecutor(max_workers=min(8, len(pairs))) as pool:
        futs = [pool.submit(_run_cell, i, j) for i, j in pairs]
        for fut in as_completed(futs):
            left, right, detail = fut.result()
            matrix[left][right] = detail
            print(f"{left.upper()} vs {right.upper()}: {detail['a']:.1%}  (first {detail['first']:.1%} / second {detail['second']:.1%})", flush=True)
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "strats": STRATS,
        "matrix": matrix,
    }
    dest = ROOT / "data/lab/family-cup-30-matrix.json"
    dest.write_text(json.dumps(out, indent=2))
    print("\nRow = that set's win rate\n")
    header = " | ".join(["  "] + [k.upper() for k in KEYS])
    print("| " + header + " |")
    print("| " + " | ".join(["---"] * (len(KEYS) + 1)) + " |")
    for row in KEYS:
        cells = []
        for col in KEYS:
            if row == col:
                cells.append("—")
            else:
                cells.append(f"{matrix[row][col]['a']:.1%}")
        print("| **" + row.upper() + "** | " + " | ".join(cells) + " |")
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
