# Bounded fate search

Status: ready

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

The 60-card space is finite but not enumerable. A trainer wants "a relatively better 60 from what I own", with the reason. The search walks 1-for-1 (and copy-count) neighbors of a seed list inside a bounded pool, prunes with \(\Delta S\), and confirms survivors with a capped Monte Carlo. Output is labelled relative, never "the best deck".

## Scope

- `search(seed_deck, pool, rules, weights, budget) -> SearchResult` in `app/engine/fate/search.py`:
  - neighbors: swap one copy of X for one copy of Y (Y from pool, copy cap respected), and ±1 copy moves within the cap;
  - prune: keep top-K by `delta_s`;
  - confirm: capped Monte Carlo (existing games cap) vs a chosen opponent deck or the seed itself, using `uncertainty-tiebreak` to break near-ties;
  - locks: trainer may lock names that must not be cut.
- Budget is data: `max_candidates`, `top_k`, `games_per_candidate`; enforced and echoed.
- Route `POST /api/decks/{id}/fate/search` and chat tool `search_fate` (owner-scoped; pool defaults to the trainer's scanned cards).
- Result rows show `delta_s`, confirming win rate + `sim_id`, and a written reason from the KG metrics.

## Non-Goals

- Exhaustive or global optimisation.
- Writing results into `data/lab/` or shipped seeds (a trainer may save the list as their own deck via existing deck routes).
- Multi-step search beyond a documented depth (start at depth 1; depth is data).

## Implementation Outline

1. Neighbor generator with legality checks (`app/engine/legality.py`).
2. Prune via `rank_swaps` / `score`.
3. Confirm via `run_simulation` under the cap; attach uncertainty.
4. Locks and pool handling; default pool = owner's cards.
5. Tests: fixture pool containing a linked 100-damage same-cost substitute for an isolated 50-damage attacker → that swap ranks first; budget enforced; locked card never cut; result labelled relative.

## Data Model And API Impact

- New route `POST /api/decks/{id}/fate/search`.
- New chat tool `search_fate`.
- Budget defaults in `data/fate/search.json`.

## Acceptance Criteria

- [ ] Returns ≥ 1 legal neighbor with a reason from Set G + fixture pool.
- [ ] Linked higher-quality substitute for an isolated weaker attacker outranks keeping it unless locked.
- [ ] `delta_s` and confirming win rate shown side by side; pruned rows carry `delta_s` only.
- [ ] Budget enforced; no full-catalog enumeration.
- [ ] Output labelled a relative improvement.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_search.py`
- Broader validation: `.venv/bin/pytest -q`
- Manual review: run a search from chat with a small budget and read the table.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
