#!/usr/bin/env python3
"""Set M versus the Aichi Open 2026-05-10 lightning and Regidrago cells.

Set M is the locked SET_M60_NAMES list and the mew_baby strategy. Nothing in
that list is rewritten here. Rules are Expanded. Seed 20260510.

The Raichu / Electrode cell is the requested 60. The Regidrago cell is a
control shell that keeps Battle Compressor, Kyurem's Trifrost, and Path to
the Peak. It is not a paste of a Limitless decklist.
"""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.engine.models import expanded_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import StrategySpec
from app.seed_data import SET_M60_NAMES, build_fallback_deck

SEED = 20260510
SMOKE_GAMES = 300
GAMES = 1000
WORKERS = 4

HOSODA = (
    ["Electrode-GX"] * 4
    + ["Voltorb"] * 4
    + ["Alolan Raichu"] * 3
    + ["Pikachu"] * 3
    + ["Tapu Koko ◇"]
    + ["Zeraora-GX"]
    + ["Switch"] * 4
    + ["Guzma"] * 4
    + ["Battle Compressor"] * 4
    + ["Acro Bike"] * 4
    + ["Ultra Ball"] * 3
    + ["Sky Field"] * 3
    + ["Thunder Mountain ◇"] * 2
    + ["Rescue Stretcher"] * 2
    + ["Special Charge"] * 2
    + ["Counter Gain"]
    + ["Field Blower"]
    + ["Energy Switch"]
    + ["Choice Band"]
    + ["Lightning Energy"] * 4
    + ["Counter Energy"] * 4
    + ["Reversal Energy"] * 4
)

# Control shell. Limitless rank 10 (list 26816) plays Parallel City, and rank
# 11 is a different player. This 60 keeps the three cards the cell has to show:
# Battle Compressor, Kyurem Trifrost, and Path to the Peak.
YOSHIOKA = (
    ["Regidrago V"] * 4
    + ["Regidrago VSTAR"] * 3
    + ["Kyurem"] * 2
    + ["Budew"] * 3
    + ["Battle Compressor"] * 4
    + ["Ultra Ball"] * 4
    + ["Nest Ball"] * 4
    + ["Switch"] * 4
    + ["Path to the Peak"] * 3
    + ["Professor's Research"] * 4
    + ["Iono"] * 4
    + ["Boss's Orders"] * 2
    + ["Guzma"] * 3
    + ["Rescue Stretcher"] * 2
    + ["Energy Switch"] * 2
    + ["Double Dragon Energy"] * 4
    + ["Grass Energy"] * 4
    + ["Fire Energy"] * 4
)

CELLS = (
    ("hosoda", "Aichi 4th-requested Raichu / Electrode", HOSODA, "electro_rain"),
    ("yoshioka", "Regidrago control (Trifrost, compressor, Path)", YOSHIOKA, "regidrago"),
)

QUERIES = [
    {"type": "event_sum", "prefix": "bench30_end_sum_a", "key": "bench_sum"},
    {"type": "event_sum", "prefix": "bench30_end_n_a", "key": "bench_n"},
    {"type": "event_sum", "prefix": "baby_ko_bench_a", "key": "baby_bench"},
    {"type": "event_sum", "prefix": "baby_ko_active_a", "key": "baby_active"},
    {"type": "event_sum", "prefix": "bursting_balloon_trigger", "key": "balloon"},
    {"type": "event_sum", "prefix": "sky_field_turns", "key": "sky"},
    {"type": "event_sum", "prefix": "sky_field_with_cage", "key": "sky_cage"},
    {"type": "event_sum", "prefix": "electro_rain_cards", "key": "rain_cards"},
    {"type": "event_sum", "prefix": "extra_energy_bomb", "key": "bomb"},
    {"type": "event_sum", "prefix": "attack:Alolan Raichu:Electro Rain", "key": "rain_attacks"},
    {"type": "event_sum", "prefix": "attack:Regidrago VSTAR:Apex Dragon", "key": "apex"},
    {"type": "event_sum", "prefix": "attack:Kyurem:Trifrost", "key": "trifrost"},
]

JSON_DEST = ROOT / "data/lab/set-m-vs-aichi.json"
MD_DEST = ROOT / "data/lab/set-m-vs-aichi.md"


def _check_lists() -> None:
    if len(SET_M60_NAMES) != 60:
        raise SystemExit(f"SET_M60_NAMES is {len(SET_M60_NAMES)}")
    if len(HOSODA) != 60:
        raise SystemExit(f"Hosoda list is {len(HOSODA)}")
    if len(YOSHIOKA) != 60:
        raise SystemExit(f"Yoshioka control is {len(YOSHIOKA)}")


def _run(label: str, games: int) -> dict:
    key, _title, names, strat = next(cell for cell in CELLS if cell[0] == label)
    rec = run_simulation(
        build_fallback_deck(list(SET_M60_NAMES)),
        build_fallback_deck(list(names)),
        expanded_60_rules(),
        StrategySpec.from_dict("mew_baby"),
        StrategySpec.from_dict(strat),
        games=games,
        seed=SEED,
        queries=QUERIES,
        deck_a_meta={"id": "set-m60", "name": "Set M"},
        deck_b_meta={"id": key, "name": key},
    )
    counts = rec["results"]["query_counts"]
    return {
        "games": games,
        "wins_a": rec["results"]["wins_a"],
        "wins_b": rec["results"]["wins_b"],
        "ties": rec["results"]["ties"],
        "win_rate_a": rec["results"]["win_rate_a"],
        "win_rate_b": rec["results"]["win_rate_b"],
        "tie_rate": rec["results"]["tie_rate"],
        "first": rec["results"]["win_rate_a_going_first"],
        "second": rec["results"]["win_rate_a_going_second"],
        "bench_sum": counts.get("bench_sum", 0),
        "bench_n": counts.get("bench_n", 0),
        "baby_bench": counts.get("baby_bench", 0),
        "baby_active": counts.get("baby_active", 0),
        "balloon": counts.get("balloon", 0),
        "sky": counts.get("sky", 0),
        "sky_cage": counts.get("sky_cage", 0),
        "rain_cards": counts.get("rain_cards", 0),
        "bomb": counts.get("bomb", 0),
        "rain_attacks": counts.get("rain_attacks", 0),
        "apex": counts.get("apex", 0),
        "trifrost": counts.get("trifrost", 0),
        "elapsed": rec["elapsed_seconds"],
    }


def _cell(row: dict) -> dict:
    bench_n = row["bench_n"] or 1
    games = row["games"] or 1
    return {
        **row,
        "bench30": row["bench_sum"] / bench_n,
        "baby_bench_per": row["baby_bench"] / games,
        "baby_active_per": row["baby_active"] / games,
        "balloon_per": row["balloon"] / games,
        "sky_per": row["sky"] / games,
    }


def _fmt(row: dict) -> str:
    shown = _cell(row)
    return (
        f"{shown['win_rate_a']:.1%}  bench30 {shown['bench30']:.2f}  "
        f"baby bench/active {shown['baby_bench']}/{shown['baby_active']}  "
        f"balloon {shown['balloon']}  sky {shown['sky']} cage {shown['sky_cage']}"
    )


def _markdown(payload: dict) -> str:
    lines = [
        "# Set M vs Aichi Open 2026-05-10",
        "",
        "Set M is the current `SET_M60_NAMES` list and the `mew_baby` strategy. No card in that list was changed.",
        "Rules are Expanded (`expanded_60_rules`). Seed `20260510`.",
        "Bench HP 30 is the count of side A's benched Pokémon whose printed maximum HP is 30, sampled after every turn.",
        "Baby KOs are side A's printed-HP-30 Pokémon, split by where they were when Knocked Out.",
        "Balloon is the number of times Bursting Balloon's sentence resolved, not the damage-counter total.",
        "Sky Field and Battle Cage cannot be in play together: a new Stadium replaces the old one.",
        "",
        "## 细田周 Raichu / Electrode",
        "",
        "Requested 60 (16 Pokémon / 32 Trainer / 12 Energy). Electrode-GX ×4, Voltorb ×4, Alolan Raichu ×3,",
        "Pikachu ×3, Tapu Koko ◇ ×1, Zeraora-GX ×1, and the trainer and energy counts named in the request.",
        "Zeraora is Lost Thunder Zeraora-GX. Battle Compressor is the existing Team Flare Gear sentence.",
        "Thunder Mountain ◇ is listed ×2 because the request says ×2.",
        "This is not Limitless list 26812.",
        "",
        "## 吉冈 Regidrago control",
        "",
        "Same Set M. The control is a 60 that contains Battle Compressor, Kyurem's Trifrost, and Path to the Peak,",
        "plus a Regidrago V / VSTAR, Double Dragon Energy, Grass, and Fire shell.",
        "Limitless tournament 566 rank 10 is a different 20-Pokémon Regidrago list and plays Parallel City.",
        "Rank 11 is a different player. This cell keeps Path to the Peak because the request asked for 颠峰之径.",
        "It is a control, not a verbatim Limitless paste. Set M is the same list in both cells.",
        "",
        "## Smoke (300)",
        "",
        "| Cell | M win rate | Bench HP 30 | Baby KO bench | Baby KO active | Balloon triggers | Sky Field turns | Sky Field with Battle Cage |",
        "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for key, title, *_ in CELLS:
        row = _cell(payload["smoke"][key])
        lines.append(
            f"| {title} | {row['win_rate_a']:.1%} | {row['bench30']:.3f} | {row['baby_bench']} | "
            f"{row['baby_active']} | {row['balloon']} | {row['sky']} | {row['sky_cage']} |"
        )
    lines.extend(
        [
            "",
            "## 1000 games",
            "",
            "| Cell | M wins | M win rate | Going first | Going second | Bench HP 30 | Baby KO bench | Baby KO active | Balloon triggers | Sky Field turns | Sky Field with Battle Cage |",
            "| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, title, *_ in CELLS:
        row = _cell(payload["full"][key])
        lines.append(
            f"| {title} | {row['wins_a']}/{row['games']} | {row['win_rate_a']:.1%} | {row['first']:.1%} | "
            f"{row['second']:.1%} | {row['bench30']:.3f} | {row['baby_bench']} ({row['baby_bench_per']:.2f}/game) | "
            f"{row['baby_active']} ({row['baby_active_per']:.2f}/game) | {row['balloon']} ({row['balloon_per']:.2f}/game) | "
            f"{row['sky']} ({row['sky_per']:.2f}/game) | {row['sky_cage']} |"
        )
    lines.extend(
        [
            "",
            "Bench HP 30 is `bench30_end_sum_a / bench30_end_n_a` (mean Pokémon, not a sum across the match).",
            "",
            "| Cell | Electro Rain attacks | Energy cards discarded by Electro Rain | Extra Energy Bomb attaches | Apex Dragon | Trifrost |",
            "| :--- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for key, title, *_ in CELLS:
        row = payload["full"][key]
        lines.append(
            f"| {title} | {row['rain_attacks']} | {row['rain_cards']} | {row['bomb']} | {row['apex']} | {row['trifrost']} |"
        )
    lines.extend(
        [
            "",
            f"Elapsed smoke {payload['smoke_elapsed']:.1f}s, 1000-game cells {payload['full_elapsed']:.1f}s.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    _check_lists()
    started = time.perf_counter()
    smoke: dict[str, dict] = {}
    full: dict[str, dict] = {}
    jobs = [(key, games) for games in (SMOKE_GAMES, GAMES) for key, *_ in CELLS]
    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        futs = {pool.submit(_run, key, games): (key, games) for key, games in jobs}
        for fut in as_completed(futs):
            key, games = futs[fut]
            row = fut.result()
            if games == SMOKE_GAMES:
                smoke[key] = row
            else:
                full[key] = row
            print(f"  {key} x{games}: {_fmt(row)}", flush=True)
    smoke_elapsed = sum(smoke[key]["elapsed"] for key, *_ in CELLS)
    full_elapsed = sum(full[key]["elapsed"] for key, *_ in CELLS)
    payload = {
        "seed": SEED,
        "smoke_games": SMOKE_GAMES,
        "games": GAMES,
        "set_m": list(SET_M60_NAMES),
        "hosoda": list(HOSODA),
        "yoshioka_control": list(YOSHIOKA),
        "smoke": smoke,
        "full": full,
        "smoke_elapsed": smoke_elapsed,
        "full_elapsed": full_elapsed,
        "wall_seconds": round(time.perf_counter() - started, 3),
    }
    JSON_DEST.write_text(json.dumps(payload, indent=2) + "\n")
    MD_DEST.write_text(_markdown(payload))
    print(f"wrote {MD_DEST}", flush=True)


if __name__ == "__main__":
    main()
