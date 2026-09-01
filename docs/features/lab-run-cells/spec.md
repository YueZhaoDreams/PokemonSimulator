# Lab run cells

Status: in_review

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

Operator bakeoffs compare several cells at one seed. Product chat only runs one `simulate_match` with hardcoded Dondozo/Pikachu queries. Trainers need `run_lab`: a matrix of deck patches and `StrategySpec` overlays plus custom queries, shown on the Lab tab.

## Scope

- Run an experiment’s `cells` with shared `games`, `seed`, `queries`; persist per-cell results into `results_json`.
- A cell names a deck the viewer can use (or a small **data** patch: energy-type swap, drop/add named cards from their deck) plus a named strategy or `StrategySpec` overlay dict.
- Chat tool `run_lab` (and HTTP POST run) call the existing Monte Carlo helper; do not invent win rates.
- `simulate_match` accepts caller `queries` instead of always using the Dondozo/Pikachu default (keep that default when queries omitted).
- Lab tab lists experiments and opens a **matrix** (cell id, title, win rates, query rates), not only simulation cards.
- Games remain capped by existing Monte Carlo max; cap cell count (document in code, e.g. ≤12 cells).
- No writes to git `data/lab/` or `app/`.

## Non-Goals

- Executing stored Python (`lab-python-sandbox`).
- Saving a locked cell as a reusable Fight strategy (`user-owned-strategies` may add lock-apply; this slice may store `locked_cell_id` + reason only).
- Arbitrary deck-file formats or monkeypatching `Game`.
- Sharing experiments between trainers.

## Implementation Outline

1. Cell runner: resolve deck + patch → `Card` lists; `StrategySpec.from_dict`; `run_simulation` per cell with experiment queries/seed.
2. Persist matrix into the experiment row.
3. Wire `run_lab` custom tool and POST `/api/lab/experiments/{id}/run`.
4. Lab UI: experiment list + matrix detail.
5. Tests: two-cell energy or strategy overlay comparison; owner isolation on run; no `data/lab/` files created.

## Data Model And API Impact

- Uses `lab_experiments` from `lab-experiment-model`.
- `POST /api/lab/experiments/{id}/run`.
- Custom tool `run_lab`.
- Lab tab reads experiments API in addition to `/api/simulations`.

## Acceptance Criteria

- [x] Two-cell run returns per-cell win rates and query rates at the requested seed.
- [x] Custom queries are used (not only the hardcoded Dondozo/Pikachu list).
- [x] Lab tab shows the matrix for that experiment.
- [x] Non-admin cannot run or view another trainer’s experiment.
- [x] Run does not create or modify files under `data/lab/` or `app/`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: matrix run with small `games`; query override; isolation
- Broader validation: `pytest -q`
- Manual review: Lab tab at `http://127.0.0.1:8000` shows a two-cell matrix

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
