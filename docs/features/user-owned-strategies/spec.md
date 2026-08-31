# User-owned strategies

Status: ready

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

Locking a lab cell is useless if Fight and chat can only pick shipped `STRATEGY_LIBRARY` names. A trainer must save the winning `StrategySpec` overlay (and optionally apply a deck patch to a deck they own) and use it next game.

## Scope

- Persist per-owner strategies: id, owner_id, name, `spec_json` (`StrategySpec` overlay), timestamps.
- Lock experiment cell: record `locked_cell_id` + reason; create/update a user strategy from that cell’s spec; optional apply of a **data** deck patch to an owned deck.
- Fight `stratA` / `stratB` lists shipped strategies plus the current user’s saved ones.
- `simulate_match` / `run_lab` accept a user strategy id the viewer owns (or a spec dict).
- Non-admin cannot list or use another trainer’s saved strategies.
- Do not modify `STRATEGY_LIBRARY` in git.

## Non-Goals

- Changing `app/engine/game.py` lines for party/shock.
- Publishing strategies to other trainers.
- Operator promotion into shipped library (Desktop/git).

## Implementation Outline

1. `user_strategies` table + CRUD with owner scope.
2. Lock endpoint/tool: copy cell spec into `user_strategies`; set experiment lock fields.
3. `GET /api/strategies` includes user overlays for the viewer.
4. Fight UI: extra options for saved strategies.
5. Tests: two users; lock → Fight payload uses overlay; library names unchanged.

## Data Model And API Impact

- Table `user_strategies`.
- `POST /api/lab/experiments/{id}/lock`.
- `GET /api/strategies` response grows with user rows (id distinct from library names).
- Chat tools `save_strategy` / `lock_lab_cell`.

## Acceptance Criteria

- [ ] After lock, the trainer sees the saved strategy on Fight and a later simulate uses that overlay.
- [ ] Second trainer does not see it.
- [ ] Shipped strategy names in code/`STRATEGY_LIBRARY` are unchanged by lock.
- [ ] Lock does not write `data/lab/` or `app/`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: lock, visibility, simulate with user strategy id
- Broader validation: `pytest -q`
- Manual review: Fight dropdown at `http://127.0.0.1:8000` after lock

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
