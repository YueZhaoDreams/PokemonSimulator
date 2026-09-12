# Deck KG metrics

Status: planned

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

Once the deck-induced KG exists, each node needs the numbers a deck builder actually compares: damage per energy for the attack you will take prizes with, how many turns it takes to warm up, whether the evolution line has enough bodies, whether the energy in the list can actually pay it, and whether the card is linked to anything at all. These are print + copy-count arithmetic, not a tier list.

## Scope

- `compute_metrics(deck_kg, rules) -> DeckMetrics` in `app/engine/fate/metrics.py`:
  - **Attack efficiency** per Pokémon: `lead_attack` (highest-damage attack by default; overridable per trainer), `dpe_lead`, `dpe_min`, `dpe_max` (variable damage such as Shooting Moons 120–280 → 60–140), `energy_lead`.
  - **Warm-up**: `energy_lead / attach_rate`, default attach rate 1; printed acceleration edges (`attaches_from_deck`, attach-from-hand abilities) lower the denominator with a documented cap. Evolution readiness reported separately; total readiness = `max(body_ready, energy_ready)`.
  - **Dependence** per evolution line: `bodies`, `evolutions`, `stage2`, `charges = min(evolutions, bodies)` (and the stage-2 analogue), `stranded = evolutions > bodies` (or stage2 > stage1). Rare Candy edges recorded as an alternate path, not counted as bodies.
  - **Reach** per node: P(at least one) at `effective_seen` (from `deck-copy-ceilings`) plus role-search edges that can find it (Jacq → Evolution Pokémon, Poké Ball / Ultra Ball → Pokémon, Energy Search → Basic Energy).
  - **Energy budget**: supply per energy type (Psychic 17, Darkness 3, Boomerang 1 …) vs drinkers per type; special Colorless does not satisfy a typed cost.
  - **Prize weight** from rules (1 / 2 / 3).
  - **Isolation / junk**: node with no non-generic edge to any other node in the deck (or in a supplied pool).
- Route `GET /api/decks/{id}/fate/metrics` and chat tool `deck_metrics`.

## Non-Goals

- Weighted scoring or swap ranking (`deck-fate-score`).
- Monte Carlo (`uncertainty-tiebreak`).
- Any change to `game.py` or `StrategySpec`.

## Implementation Outline

1. Attack efficiency from `Attack.cost` / `Attack.damage` / parsed bonus effects (per-discard, per-energy bonuses give min/max).
2. Line detection via `evolves_into` edges; count copies per stage; compute charges and stranded flags.
3. Energy budget: group Energy nodes by provided type (use `energy_provided`), attackers by typed cost.
4. Reach: call ceilings helper for hypergeometric part; union with role-search edges.
5. Isolation: degree over non-generic edges within the induced subgraph.
6. Tests: 50 vs 100 same-cost pair; Mega min/max DPE; Ledyba/Ledian 4/4, 3/4, 4/3 charges and stranded; Psychic vs Darkness/Boomerang budget; isolated fixture.

## Data Model And API Impact

- No schema change.
- New route `GET /api/decks/{id}/fate/metrics`.
- New chat tool `deck_metrics`.
- Optional per-trainer `lead_attack` override stored alongside the deck (JSON column already used for deck metadata if present; otherwise defer to `fate-report-ux`).

## Acceptance Criteria

- [ ] Same-cost 50 vs 100 pair reports `dpe_lead` 25 vs 50.
- [ ] Mega Clefable ex reports `dpe_min` 60, `dpe_max` 140, `warm_up_turns` 2.
- [ ] Ledyba/Ledian 4/4 → charges 4, not stranded; 3/4 → charges 3, stranded; 4/3 → charges 3, not stranded.
- [ ] Energy budget separates Psychic from Darkness / Boomerang; [P][P] not payable by Colorless special Energy.
- [ ] Isolated node flagged only when its sole edges are generic energy-pay.
- [ ] No name tables in `app/engine/game.py`.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_metrics.py`
- Broader validation: `.venv/bin/pytest -q`
- Manual review: metrics for Set G show Iron Boulder 170/2 as `dpe_lead` 85 with the printed condition attached, and Ledian charges 4.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
