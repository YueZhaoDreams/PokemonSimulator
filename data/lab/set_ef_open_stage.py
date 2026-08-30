"""Open Stage Rule C — Carpet Set E vs Set F win rates.

Rule B decks (A–T) stay selectable. Sets E/F are the new 30-card carpet lists.
Open Stage: any Pokémon stage may enter play from hand (mulligan until any Pokémon).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from app.engine.models import Card, open_stage_family_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed import load_seed_payload

ROOT = Path(__file__).resolve().parents[2]
GAMES = 3000
SEED = 20260830
STRATS = {"e": "shock", "f": "carnival"}


def main() -> None:
    payload = load_seed_payload()
    e = [Card.from_dict(c) for c in payload["e"]["cards"]]
    f = [Card.from_dict(c) for c in payload["f"]["cards"]]
    rules = open_stage_family_rules()
    started = time.perf_counter()
    cells = {}
    for left, right in (("e", "f"), ("f", "e")):
        a = e if left == "e" else f
        b = f if right == "f" else e
        rec = run_simulation(
            a,
            b,
            rules,
            StrategySpec.from_dict(STRATS[left]),
            StrategySpec.from_dict(STRATS[right]),
            games=GAMES,
            seed=SEED,
            queries=[],
            deck_a_meta={"id": f"seed-{left}", "name": payload[left]["name"]},
            deck_b_meta={"id": f"seed-{right}", "name": payload[right]["name"]},
        )
        r = rec["results"]
        cells[f"{left}_vs_{right}"] = {
            "win_rate_a": r["win_rate_a"],
            "win_rate_b": r["win_rate_b"],
            "tie_rate": r["tie_rate"],
            "first": r["win_rate_a_going_first"],
            "second": r["win_rate_a_going_second"],
            "wins_a": r["wins_a"],
            "wins_b": r["wins_b"],
            "ties": r["ties"],
        }
        print(
            f"{left.upper()} vs {right.upper()}: {r['win_rate_a']:.1%}  "
            f"(first {r['win_rate_a_going_first']:.1%} / second {r['win_rate_a_going_second']:.1%})",
            flush=True,
        )
    elapsed = time.perf_counter() - started
    out = {
        "games": GAMES,
        "seed": SEED,
        "elapsed": elapsed,
        "rules": rules.to_dict(),
        "strats": STRATS,
        "results": cells,
    }
    dest = ROOT / "data/lab/set-ef-open-stage.json"
    dest.write_text(json.dumps(out, indent=2))
    md = ROOT / "data/lab/set-ef-open-stage.md"
    e_rate = cells["e_vs_f"]["win_rate_a"]
    f_rate = cells["f_vs_e"]["win_rate_a"]
    md.write_text(
        f"""# Carpet Set E vs Set F — Open Stage

Rule C (**Open Stage**): Rule B energy plus any Pokémon stage may enter play from hand.
Existing Rule B decks (A–T) remain selectable.

| Side | List | Strategy |
| --- | --- | --- |
| E | Walrein / Irida / dual Pikachu | `shock` |
| F | Quaquaval (no Quaxly) / Staraptor / Gengar | `carnival` |

## Results ({GAMES} games / ordered pair, seed `{SEED}`)

| Matchup | A win rate | first / second |
| --- | --- | --- |
| **E vs F** | **{e_rate:.1%}** | {cells['e_vs_f']['first']:.1%} / {cells['e_vs_f']['second']:.1%} |
| **F vs E** | **{f_rate:.1%}** | {cells['f_vs_e']['first']:.1%} / {cells['f_vs_e']['second']:.1%} |

Raw: `data/lab/set-ef-open-stage.json` (elapsed {elapsed:.1f}s).
"""
    )
    print(f"\nE vs F: {e_rate:.1%} · F vs E: {f_rate:.1%}")
    print(f"elapsed {elapsed:.1f}s -> {dest}")


if __name__ == "__main__":
    main()
