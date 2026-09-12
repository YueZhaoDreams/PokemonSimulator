# Card Knowledge Graph from print

Status: planned

Epic: deck-as-fate

Jira Issue: TBD

## Problem And Value

Cards relate to each other only through what is printed: evolves-from, search by role, energy pay by type, force-opponent-active, draw, attach-from-deck. Deck building needs those relations as a graph so that "is this card linked to anything?" and "which cards reach this one?" are queries, not chat opinions. The graph must be derived from `parse_effects` / `parse_ability_effects`; lab notes and strategy comments never add an edge.

## Scope

- `build_catalog_kg(cards) -> KG` in `app/engine/fate/kg.py`: nodes keyed by `catalog_id` with printed attributes (name, category, stage, types, HP, attacks with cost + damage, abilities, trainer kind, energy type, prize weight under rules); edges typed and sourced:
  - `evolves_into` (from `evolves_from`),
  - `searches_role` (Basic Pokémon, Evolution Pokémon, Pokémon, Item, Tool, Basic Energy of type T, named card),
  - `pays_energy` (energy type → attackers whose cost includes it; generic Colorless pay is stored but flagged `generic=True` so junk detection can ignore it),
  - `draws` (operator with amount),
  - `attaches_from_deck` (Moon-Watching Party: full deck, per benched Clefairy — no look-N),
  - `force_opponent_active` (Boss's Orders; Ledian Glittering Star Pattern with `trigger=on_evolve`, `max_remaining_hp=90`),
  - `named_partner` when printed text names another card.
- Every edge carries the printed sentence (or effect dict) that produced it.
- Parser branch in `parse_ability_effects` for the Glittering Star Pattern sentence emitting the same hook kind used for Boss's Orders; test with the exact printed wording. Match-time resolution of that hook inside `Game` is **not** in scope.
- Deck-induced subgraph helper `induce(kg, names_with_counts)`.

## Non-Goals

- Per-node quality metrics, dependence balance, energy budget (`deck-kg-metrics`).
- Executing the new ability hook in live matches.
- Community / external card graphs.
- Any look-N or attach count invented outside print.

## Implementation Outline

1. Define `KGNode`, `KGEdge`, `KG` dataclasses (JSON-serialisable).
2. Edge extractors keyed on effect `kind`s already emitted by the parser; add one extractor per kind, no name tables.
3. Parser: add `force_opponent_active` for "switch in 1 of your opponent's Benched Pokémon" (trainer) and the on-evolve / HP-limited variant (ability). Keep Boss's Orders behaviour in `game.py` unchanged.
4. `induce()` for a deck; `explain_edge()` returns the printed source.
5. Tests: Clefairy edge has no look attribute; Ledian sentence → same kind as Boss with trigger and HP filter; unrelated fixture card has zero non-energy edges; adding a markdown note changes nothing.
6. Route `GET /api/decks/{id}/fate/kg` and chat tool `deck_kg` (owner-scoped).

## Data Model And API Impact

- No schema change.
- New route `GET /api/decks/{id}/fate/kg`.
- New chat tool `deck_kg`.
- New effect kind emitted by the parser (`force_opponent_active`), listed in `app/engine/overlay.py` allowed kinds.

## Acceptance Criteria

- [ ] Catalog KG built from shipped fallback cards without errors; nodes carry printed attributes.
- [ ] Edges exist only where an effect kind or `evolves_from` supports them and each carries its printed source.
- [ ] Ledian and Boss's Orders share the hook kind; Ledian's edge has `trigger=on_evolve`, `max_remaining_hp=90`.
- [ ] Moon-Watching Party edge is full-deck, per benched Clefairy, no look-N.
- [ ] Generic energy-pay edges are flagged and excluded from "linked" counts.
- [ ] `app/engine/game.py` behaviour unchanged (full suite green).

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: `tests/test_fate_kg.py`, parser tests in `tests/test_printings.py` style using exact printed sentences
- Broader validation: `.venv/bin/pytest -q`
- Manual review: query the KG route for Set G and check a Ledian → opponent-active edge and a Clefairy → Psychic Energy edge.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
