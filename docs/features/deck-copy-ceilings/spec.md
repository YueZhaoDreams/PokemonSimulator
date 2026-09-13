# Deck copy ceilings

Status: in_progress

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

`/api/probability` answers one name at a time. Deck building needs the whole list: for every name, how many copies, what the format allows, and how likely at least one shows up in the cards you will actually see. The 4-of cap is the probability ceiling on any single card; a printed draw card raises the number of cards seen, not a flat "+3/60 for everything".

## Scope

- `compute_ceilings(names, rules)` in a new deck-building module (e.g. `app/engine/fate/ceilings.py`) returning, per distinct name: `copies`, `copy_cap` (from the active rule preset; basic Energy uncapped where the preset says so), `p_opening` (P(at least one) at the preset opening hand), and `p_seen` at `effective_seen`.
- `effective_seen = opening_hand + Σ printed draw operators present in the list` where a draw operator is an effect already emitted by `parse_effects` / `parse_ability_effects` (`draw` with an amount). Search / shuffle-draw supporters are **not** added here (they are role operators, handled in `card-kg-from-print`).
- Reuse `hypergeometric_at_least_one` / `hypergeometric_exact`. No new probability formula.
- Route `GET /api/decks/{id}/fate/ceilings` (owner-scoped like other deck routes) and an in-process chat tool `deck_ceilings`.
- Works for any preset: 30-card Family Cup and `s60` both pull `deck_size`, `opening_hand`, `copy_cap` from rules.

## Non-Goals

- Graph edges, quality, junk flags (`card-kg-from-print`, `deck-kg-metrics`).
- Mulligan correction (a later refinement; document that P is pre-mulligan).
- Any change to `app/engine/game.py`.

## Implementation Outline

1. Add `app/engine/fate/__init__.py` and `ceilings.py`; import `draw_probability` helpers from `app/engine/probability.py`.
2. Read `deck_size`, `opening_hand`, copy cap from the rules object / preset registry; do not hardcode 60 or 4.
3. Collect draw operators from parsed effects of Trainer cards in the list; sum amounts into `effective_seen`.
4. Route + chat tool; register the tool in `app/ai/tools.py` with the same owner checks as `list_decks`.
5. Tests: Carpet Set G fixture equality with `draw_probability`; 30-card preset numbers; +3 draw operator delta (1-of ≈ 3/60, 4-of > 3/60).

## Data Model And API Impact

- No schema change.
- New route `GET /api/decks/{id}/fate/ceilings`.
- New chat tool `deck_ceilings`.

## Acceptance Criteria

- [ ] Per-name copies, cap, `p_opening`, `p_seen`, `effective_seen` for a saved deck under the active rules.
- [ ] Numbers equal `draw_probability` for the same name and draw count.
- [ ] Preset switch changes deck size / cap / opening hand in the response without code change.
- [ ] Draw operator raises `effective_seen`; the 1-of vs 4-of delta behaves as the epic gate states.
- [ ] No edits under `app/engine/game.py`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_ceilings.py` (fixture Set G, preset s60 and a 30-card preset, draw-operator delta)
- Broader validation: `.venv/bin/pytest -q`
- Manual review: hit the route for a seeded deck and eyeball one 4-of and one 1-of.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
