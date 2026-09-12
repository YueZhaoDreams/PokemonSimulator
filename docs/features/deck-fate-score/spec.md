# Deck fate score and fast swap ranking

Status: planned

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

"Add Mega Clefable ex — cut which card?" should not need a throwaway script or a 10,000-game run per candidate. Given the Deck KG metrics, a weighted ecology score \(S(\text{Deck})\) and its delta \(\Delta S\) for every legal 1-for-1 cut give a ranked table in milliseconds, with a per-ecology explanation. It is a fast estimate that prunes candidates for Monte Carlo; it is not a win rate and never chooses an in-game action.

## Scope

- `score(metrics, weights) -> ScoreBreakdown` and `rank_swaps(deck, add, weights, rules) -> list[SwapRow]` in `app/engine/fate/score.py`.
- **Ecologies** (functions of metrics, each 0–N): early tempo (2-energy Basics that KO, conditional attacks kept live by print), main line (body copies, evolution charges, typed energy reach, role search), secondary closer lines, energy budget (supply − drinkers per type), control (force-opponent-active Boss-equivalent, status, ability lock), prize race (1-prize attackers vs 2/3-prize leak), consistency (search, stranded lines, 1-1 widows).
- **Boss-equivalent** computed from the parsed `force_opponent_active` hook: 1.0 per copy for a supporter; for an on-evolve ability, `hp_gate × supporter_free × charge_curve(min(evolution, body))`. All three factors live in the weights data.
- **Weights are data**: `data/fate/weights/<preset>.json` shipped defaults; trainer overlay stored in DB (owner-scoped) may override numbers only, never add an ecology.
- Copy-count curves (`fate` 0/1, 2-of line, 4-of engine, Party per-bench curve) are also data.
- `rank_swaps`: for each distinct name in the deck, remove one, add the candidate, recompute, emit `delta_s` and per-ecology deltas plus a one-line reason drawn from the largest movers (dependence, energy, closer loss).
- Route `POST /api/decks/{id}/fate/swaps` `{add: <name or catalog_id>, weights?: {...}}` and chat tool `rank_fate_swaps`. Response echoes weights used and is labelled `estimate: true`.

## Non-Goals

- Monte Carlo confirmation (`bounded-fate-search`).
- Weight fitting from match results (future; note only).
- Any coefficient in `app/engine/game.py` or `StrategySpec`.

## Implementation Outline

1. Weight schema + loader with validation (unknown ecology keys rejected).
2. Ecology functions over `DeckMetrics`; keep each pure and unit-tested.
3. `rank_swaps` with copy-cap and deck-size legality checks (reuse `app/engine/legality.py`).
4. Explanation builder: top-2 absolute ecology deltas → sentence templates citing metric names.
5. Route + chat tool; owner checks.
6. Tests on the Carpet Set G fixture: Ledian above Ledyba; Clefairy below Ledian; Iron Boulder near bottom at default early weight and its rank changes when the weight changes; Boss-equivalent for Boss's Orders = 1.0 per copy; Ledian 4/4 → 4/3 drops by one marginal charge; runtime under 2 s for all cuts.

## Data Model And API Impact

- New data files `data/fate/weights/*.json`.
- New table or JSON column for trainer weight overlays (owner-scoped), reusing the strategies/overlay pattern from `user-owned-strategies`.
- New route `POST /api/decks/{id}/fate/swaps`.
- New chat tool `rank_fate_swaps`.

## Acceptance Criteria

- [ ] All 1-for-1 cuts for Set G + Mega Clefable ex ranked with `delta_s` and per-ecology breakdown, no `run_simulation` call, < 2 s.
- [ ] Ledian ranks above Ledyba with a dependence reason; Clefairy ranks below Ledian.
- [ ] Changing `early_equal_hands` weight via request or overlay changes the conditional 170/2 attacker's rank; response echoes weights.
- [ ] Boss-equivalent: 1.0 per Boss's Orders copy; Ledian line value derived from `min(evolution, body)`; 4→3 charges drops by one marginal step.
- [ ] Response labelled as an estimate; no coefficient added to `app/engine/game.py`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_score.py`
- Broader validation: `.venv/bin/pytest -q`
- Manual review: read the Set G table in chat and confirm it matches the operator's hand-built ranking direction (Ledian / Mewtwo top, Iron Boulder bottom) under default weights.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
