# Lab Python sandbox

Status: ready

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

Trainers should generate bakeoff Python like operator `data/lab/*.py`, but that code is untrusted: store it in the database, run it only in a game sandbox, and fail closed so Combo Cub does not become a virus library or a way to patch `game.py`.

## Scope

- Execute `lab_experiments.script_text` (and/or a `run_lab_script` tool that saves then runs) **only** if it passes a fail-closed gate: text-only, size cap, game-related.
- Sandbox may import/call an **allowlist** of engine APIs (`run_simulation`, `StrategySpec`, `Card`, family rules helpers, query dicts). It must not import `os`, `subprocess`, `socket`, `urllib`, `pathlib` writes, `importlib`, or similar.
- No network. No writes under the git checkout (`app/`, `tests/`, `data/lab/`, `.env`). Ephemeral scratch if needed is process-local and deleted.
- Must not mutate shared `Game` class / module globals so another user’s later match sees a monkeypatch.
- Hostile payloads are **not stored as executable** (reject on save and/or strip `executable` flag); legitimate bakeoffs still run.
- Results go back into the experiment’s `results_json` (and never into git).
- Tests for the documented hostile list in the epic gate `lab-python-safe`.

## Non-Goals

- Customers changing repository code.
- A general code host, pastebin, or package installer.
- Cloud agents.
- Auto-promoting scripts into `STRATEGY_LIBRARY` or git `data/lab/`.
- Sharing scripts between trainers.

## Implementation Outline

1. Restrict parse (AST allowlist or equivalent) before save-as-executable and before run.
2. Runner: subprocess or restricted exec with allowlisted globals; timeout; games cap; no inherited writable `ROOT`.
3. Isolate `Game` mutations (run in a subprocess so monkeypatches die with the child).
4. Chat/HTTP: save script to DB; run; return matrix or error; never write repo files.
5. Tests: each hostile case rejects/kills; a small legitimate `run_simulation` script succeeds; checkout paths unchanged.

## Data Model And API Impact

- Uses `script_text` on `lab_experiments`.
- `POST /api/lab/experiments/{id}/run-script` (or extend run with `mode=script`).
- Custom tool e.g. `run_lab_script`.

## Acceptance Criteria

- [ ] Legitimate bakeoff Python stored in DB runs and returns cell-like results.
- [ ] Documented hostile imports and filesystem/network/Git writes do not execute; script is not kept executable.
- [ ] Monkeypatching `Game` in a script does not affect a subsequent simulation in another request.
- [ ] No new files under `app/` or `data/lab/` after save or run.
- [ ] Other trainers cannot run or read this script.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: allowlist, each hostile case, subprocess isolation, owner checks
- Broader validation: `pytest -q` (engine tests still pass — printed text wins)
- Manual review: human signs the hostile checklist at gate `lab-python-safe`

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
