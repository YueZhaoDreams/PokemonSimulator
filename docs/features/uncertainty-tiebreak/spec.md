# Uncertainty tie-break

Status: ready

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

Two lists with the same expected output are not equal: the one that bricks less and whose prize count varies less is the better fate. Monte Carlo already reports a mean win rate; it needs to also report spread and brick / chain-break rates so that a ranking can prefer the lower-uncertainty list when means are within tolerance.

## Scope

- Extend the Monte Carlo result (`app/engine/montecarlo.py`) with per-run distributions for documented outputs: prizes taken, turn of first attack with the lead attack, energy attached by turn N, mulligan count, "no attacker by turn 3" (brick), and evolution-line break (evolution in hand with no body in play) when the KG line exists.
- `uncertainty(result) -> {mean, variance, brick_rate, chain_break_rate, sim_id}` helper in `app/engine/fate/uncertainty.py`.
- `compare_lists(a, b, tolerance)` returning the preferred list and the reason; tolerance is data (per preset) and echoed.
- Chat tool `compare_fates` and route `POST /api/fate/compare` (owner-scoped decks, games cap respected).

## Non-Goals

- Changing how the engine plays (`Strategy`).
- Weighted score (`deck-fate-score`).
- Any invented number: every figure carries a simulation id.

## Implementation Outline

1. Add event counters to the existing per-game log path (reuse query mechanism from `lab-run-cells` where possible).
2. Aggregate to variance / rates; attach `sim_id`.
3. `compare_lists`: if `|mean_a − mean_b| < tol` prefer lower variance / brick; else prefer higher mean; always explain.
4. Tests with two seeded fixture lists (e.g. Set G vs Set G with 3 Psychic Energy swapped for a 1-1 line) at a small games count and fixed seed.

## Data Model And API Impact

- Simulation result JSON gains an `uncertainty` block (backward compatible).
- New route `POST /api/fate/compare`.
- New chat tool `compare_fates`.

## Acceptance Criteria

- [ ] Monte Carlo result exposes variance, brick rate, chain-break rate with the simulation id.
- [ ] For two fixture lists within tolerance on mean, the lower-uncertainty list is preferred and the reason says so.
- [ ] For two lists outside tolerance, the higher mean wins and the reason says so.
- [ ] No number without a `sim_id`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_uncertainty.py`
- Broader validation: `.venv/bin/pytest -q`
- Manual review: run compare in chat; explanation reads as ceiling / broken chain / variance.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
