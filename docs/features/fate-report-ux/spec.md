# Fate report UX

Status: planned

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

The numbers from ceilings, KG, metrics, score, and search need one readable place. A trainer opening a deck should see its fate: copy ceilings and effective seen cards, links and junk flags, why one attacker is stronger than another at the same cost, a "cut which card for Y?" table with per-ecology deltas and the weights used, a two-list uncertainty comparison, and a bounded-search suggestion they can accept (save as their deck) or reject. Chat answers must cite the same data.

## Scope

- Deck view (Fight or Lab tab, decided by human during `fast-swap-score` review) gains a **Fate** panel with sections: Ceilings, Links, Quality, Swap table, Compare, Search.
- Chat: the coach uses `deck_ceilings`, `deck_kg`, `deck_metrics`, `rank_fate_swaps`, `compare_fates`, `search_fate` and phrases answers with the returned numbers; the `FAMILY_CUP_BRIEF` gains one line that these tools exist and that win rate still comes only from simulation.
- Accept a search suggestion → creates a new owned deck (existing deck save path), never edits shipped seeds.
- Weight overlay editor (numbers only) for the trainer, stored owner-scoped.
- Labels: "fast estimate" on score tables; "luck given this fate" on the Monte Carlo confirm.

## Non-Goals

- New engine behaviour.
- Editing weights' ecology set from the UI.
- Public sharing of fate reports between trainers.

## Implementation Outline

1. Frontend panel in `app/static/app.js` using the new routes; owner-scoped like existing deck views.
2. Chat tool descriptions and brief line; local coach intents for "what should I cut for X" and "is X junk".
3. Accept flow → `POST /api/decks` (or existing save) with the suggested list.
4. Tests: UI string tests as in `tests/test_ui.py`; coach intent tests; accept flow creates an owned deck and leaves `data/lab/` untouched.

## Data Model And API Impact

- No new tables beyond the weight overlay from `deck-fate-score`.
- No new routes; consumes the fate routes.

## Acceptance Criteria

- [ ] Fate panel shows all six sections for a seeded `s60` deck.
- [ ] Chat "what do I cut for Mega Clefable ex?" returns the same table as the panel, with weights echoed.
- [ ] Accepting a search suggestion creates an owned deck; no writes under `data/lab/` or `app/`.
- [ ] Second trainer cannot see the first trainer's fate overlays or saved decks.
- [ ] Labels present: estimate vs simulated.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_ui.py` additions, `tests/test_coach.py` additions
- Broader validation: `.venv/bin/pytest -q`
- Manual review: epic exit checklist on `http://127.0.0.1:8000`.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
