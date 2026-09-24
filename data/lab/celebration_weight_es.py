#!/usr/bin/env python3
"""Self-play pilot: tune the seven StrategySpec floats of `celebration` by evolution strategy.

Row is G30 (Ambipom PAR Hand Fling, strategy celebration) as player A against the
household 60s from data/lab/gholdengo-30-array.py. Only the floats move; every
`strat.name == "celebration"` branch in game.py still decides the rest. The question
is how much win rate is left in weights alone.

Search: (mu/mu_w, lambda) evolution strategy on [0, 1]^7 with a decaying step. Every
candidate in a generation, and the incumbent defaults, play the same seeds. The
final mean and the best candidate are re-run on held-out seeds with a 95% interval.
"""

from __future__ import annotations

import json
import math
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from app.engine.models import standard_60_rules
from app.engine.montecarlo import run_simulation
from app.engine.strategies import STRATEGY_LIBRARY, StrategySpec
from app.seed_data import (
    SET_C60_NAMES,
    SET_D60_NAMES,
    SET_G_NAMES,
    SET_S60_NAMES,
    SET_T60_NAMES,
    SET_T_META_NAMES,
    SET_T_UNL_NAMES,
    build_fallback_deck,
    build_g30_deck,
)

ROOT = Path(__file__).resolve().parents[2]
GAMES = int(os.environ.get("GAMES", "500"))
GENERATIONS = int(os.environ.get("GENERATIONS", "20"))
LAMBDA = int(os.environ.get("LAMBDA", "12"))
MU = int(os.environ.get("MU", "4"))
VAL_GAMES = int(os.environ.get("VAL_GAMES", "3000"))
WORKERS = int(os.environ.get("WORKERS", str(max(1, (os.cpu_count() or 2) - 1))))
SEED = 20260923
VAL_SEED = 20260924
SIGMA0 = 0.2
SIGMA_DECAY = 0.9
SIGMA_MIN = 0.03

PARAMS = (
    "prefer_damage",
    "prefer_status",
    "bench_fill",
    "evolve_asap",
    "attach_pokemon_as_energy",
    "item_spend",
    "self_preserve",
)
OPPONENTS = (
    ("c60", SET_C60_NAMES, "party"),
    ("t60", SET_T60_NAMES, "phantom"),
    ("hedrick", SET_T_META_NAMES, "phantom"),
    ("unl", SET_T_UNL_NAMES, "phantom"),
    ("d60", SET_D60_NAMES, "demolish"),
    ("s60", SET_S60_NAMES, "slash"),
    ("g", SET_G_NAMES, "carnival"),
)
FOE_KEYS = tuple(key for key, *_ in OPPONENTS)

_DECKS: dict[str, list] = {}


def _deck(key: str) -> list:
    if key not in _DECKS:
        if key == "g30":
            _DECKS[key] = build_g30_deck()
        else:
            names = next(n for k, n, _ in OPPONENTS if k == key)
            _DECKS[key] = build_fallback_deck(list(names))
    return _DECKS[key]


def _spec(values: tuple[float, ...]) -> StrategySpec:
    return StrategySpec.from_dict({"name": "celebration", **dict(zip(PARAMS, values))})


def _cell(values: tuple[float, ...], foe: str, games: int, seed: int) -> float:
    foe_strat = next(s for k, _, s in OPPONENTS if k == foe)
    rec = run_simulation(
        _deck("g30"),
        _deck(foe),
        standard_60_rules(),
        _spec(values),
        StrategySpec.from_dict(foe_strat),
        games=games,
        seed=seed,
        queries=[],
    )
    return float(rec["results"]["win_rate_a"])


def _evaluate(pool, candidates: list[tuple[float, ...]], games: int, seed: int) -> list[dict[str, float]]:
    """Win rate per foe for every candidate. Foe i always plays seed + i."""
    futs = {
        (c, foe): pool.submit(_cell, cand, foe, games, seed + i)
        for c, cand in enumerate(candidates)
        for i, foe in enumerate(FOE_KEYS)
    }
    out: list[dict[str, float]] = [{} for _ in candidates]
    for (c, foe), fut in futs.items():
        out[c][foe] = fut.result()
    return out


def _mean(rates: dict[str, float]) -> float:
    return sum(rates.values()) / len(rates)


def _mean_se(rates: dict[str, float], games: int) -> float:
    var = sum(p * (1 - p) / games for p in rates.values())
    return math.sqrt(var) / len(rates)


def _round(values) -> list[float]:
    return [round(float(v), 4) for v in values]


def main() -> None:
    started = time.perf_counter()
    base_spec = STRATEGY_LIBRARY["celebration"]
    baseline = tuple(float(getattr(base_spec, p)) for p in PARAMS)
    rng = np.random.default_rng(SEED)
    dim = len(PARAMS)
    mean = np.array(baseline)
    sigma = SIGMA0
    ranks = np.log(MU + 0.5) - np.log(np.arange(1, MU + 1))
    weights = ranks / ranks.sum()

    best = {"values": baseline, "delta": 0.0, "generation": -1, "rates": {}}
    history = []
    print(f"workers={WORKERS} games/foe={GAMES} lambda={LAMBDA} mu={MU} generations={GENERATIONS}", flush=True)
    print(f"baseline {dict(zip(PARAMS, baseline))}", flush=True)

    with ProcessPoolExecutor(max_workers=WORKERS) as pool:
        for gen in range(GENERATIONS):
            gen_started = time.perf_counter()
            samples = np.clip(mean + sigma * rng.standard_normal((LAMBDA, dim)), 0.0, 1.0)
            candidates = [baseline, *[tuple(float(x) for x in row) for row in samples]]
            seed = SEED + 1000 * (gen + 1)
            rates = _evaluate(pool, candidates, GAMES, seed)
            base_score = _mean(rates[0])
            scores = [_mean(r) for r in rates[1:]]
            order = np.argsort(scores)[::-1]
            elite = samples[order[:MU]]
            mean = np.clip(weights @ elite, 0.0, 1.0)
            top = int(order[0])
            delta = scores[top] - base_score
            if delta > best["delta"]:
                best = {
                    "values": candidates[top + 1],
                    "delta": delta,
                    "generation": gen,
                    "rates": rates[top + 1],
                }
            history.append(
                {
                    "generation": gen,
                    "seed": seed,
                    "sigma": round(sigma, 4),
                    "baseline_mean": round(base_score, 4),
                    "best_mean": round(scores[top], 4),
                    "best_delta": round(delta, 4),
                    "median_delta": round(float(np.median(scores)) - base_score, 4),
                    "best_values": _round(candidates[top + 1]),
                    "new_mean": _round(mean),
                    "elapsed": round(time.perf_counter() - gen_started, 1),
                }
            )
            print(
                f"gen {gen:2d} sigma {sigma:.3f} baseline {base_score:.1%} best {scores[top]:.1%} "
                f"(delta {delta:+.1%}, median {history[-1]['median_delta']:+.1%}) "
                f"{time.perf_counter() - gen_started:.0f}s",
                flush=True,
            )
            sigma = max(SIGMA_MIN, sigma * SIGMA_DECAY)

        final_mean = tuple(float(x) for x in mean)
        finalists = {"baseline": baseline, "final_mean": final_mean, "best_seen": tuple(best["values"])}
        val = _evaluate(pool, list(finalists.values()), VAL_GAMES, VAL_SEED)

    validation = {}
    base_val = val[0]
    for (label, values), rates in zip(finalists.items(), val):
        diff = _mean(rates) - _mean(base_val)
        se = math.sqrt(_mean_se(rates, VAL_GAMES) ** 2 + _mean_se(base_val, VAL_GAMES) ** 2)
        validation[label] = {
            "values": dict(zip(PARAMS, _round(values))),
            "mean": round(_mean(rates), 4),
            "per_foe": {k: round(v, 4) for k, v in rates.items()},
            "delta_vs_baseline": round(diff, 4),
            "ci95": [round(diff - 1.96 * se, 4), round(diff + 1.96 * se, 4)] if label != "baseline" else None,
        }

    elapsed = time.perf_counter() - started
    out = {
        "question": "How much win rate is left in celebration's StrategySpec floats while name branches decide the rest?",
        "rule_preset": "s60",
        "row": "g30 player A win rate; first player random; objective = unweighted mean over foes",
        "opponents": {k: s for k, _, s in OPPONENTS},
        "params": list(PARAMS),
        "search": {
            "method": "(mu/mu_w, lambda) evolution strategy, clipped to [0, 1], decaying step",
            "lambda": LAMBDA,
            "mu": MU,
            "generations": GENERATIONS,
            "games_per_foe": GAMES,
            "sigma0": SIGMA0,
            "sigma_decay": SIGMA_DECAY,
            "seed": SEED,
            "common_random_numbers": "all candidates in a generation, and the baseline, play seed + foe index",
        },
        "history": history,
        "validation": {"games_per_foe": VAL_GAMES, "seed": VAL_SEED, "results": validation},
        "elapsed": round(elapsed, 1),
    }
    dest = ROOT / "data/lab/celebration-weight-es.json"
    dest.write_text(json.dumps(out, indent=2))
    print(f"\nelapsed {elapsed:.1f}s -> {dest}")
    for label, row in validation.items():
        ci = row["ci95"]
        ci_txt = f" 95% CI [{ci[0]:+.1%}, {ci[1]:+.1%}]" if ci else ""
        print(f"{label:11s} mean {row['mean']:.1%} delta {row['delta_vs_baseline']:+.1%}{ci_txt}")
        print("   " + " ".join(f"{k} {v:.1%}" for k, v in row["per_foe"].items()))
        print("   " + " ".join(f"{k}={v}" for k, v in row["values"].items()))


if __name__ == "__main__":
    main()
