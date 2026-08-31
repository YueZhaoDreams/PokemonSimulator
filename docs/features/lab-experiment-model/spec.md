# Lab experiment model

Status: in_review

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

The Lab tab is a list of `simulations` rows. Trainers need a first-class **experiment** (question, cells, queries, results, lock, optional script text) owned by them and stored in the database — not in git `data/lab/`.

## Scope

- New `lab_experiments` table (or equivalent): `id`, `owner_id`, `question`, `cells_json`, `queries_json`, `games`, `seed`, `results_json`, `locked_cell_id`, `lock_reason`, `script_text` (nullable; **not executed** in this slice), `created_at`, `updated_at`.
- CRUD API scoped like decks: non-admin sees only own rows; admin may see all.
- Chat tool to list/get the current viewer’s experiments (do not return other trainers’ rows).
- `script_text` is stored as text only; size-capped; reject non-text / oversized blobs. No runner in this slice.
- Copying an official `data/lab/*.md` into an experiment, if implemented, writes a **new DB row** only.
- Existing `simulations` and `simulate_match` keep working.

## Non-Goals

- Running the matrix (`lab-run-cells`).
- Executing `script_text` (`lab-python-sandbox`).
- Fight dropdown for custom strategies (`user-owned-strategies`).
- Writing files under `data/lab/` or `app/`.

## Implementation Outline

1. Schema + migration-style `_ensure_*` in `app/db.py`.
2. `save_lab_experiment` / `get_lab_experiment` / `list_lab_experiments(owner_id=...)`.
3. FastAPI routes under `/api/lab/experiments`.
4. Owner checks matching `chat_visible` / deck visibility.
5. Tests: two users cannot read each other’s experiments; blob over size cap rejected.

## Data Model And API Impact

- New table `lab_experiments`.
- `GET/POST /api/lab/experiments`, `GET /api/lab/experiments/{id}`.
- Optional chat tools `list_lab_experiments` / `get_lab_experiment`.

## Acceptance Criteria

- [x] A logged-in trainer can create and fetch their experiment JSON (cells, queries, optional script text).
- [x] A second non-admin cannot GET the first trainer’s experiment.
- [x] Creating an experiment does not write `data/lab/` or `app/`.
- [x] Oversized or non-text `script_text` is rejected.
- [x] `simulate_match` / `simulations` still persist as today.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: owner isolation, size cap, no filesystem writes beside `data/app.db`
- Broader validation: `pytest -q`
- Manual review: none required beyond API tests

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
