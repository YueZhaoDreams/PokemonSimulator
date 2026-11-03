# Pad photo match

Status: in_review

Epic: poke-pad

Jira Issue: TBD

GitHub Issue: TBD

## Problem And Value

A photo of a Pokémon picture should open the same device entry as a text search. The photo may be the official artwork or a close animation still. A toy photo may only be close. A miss stays a miss. A card photo must keep going through card scan.

## Scope

- Pokémon mode has its own photo input. It posts to `POST /api/pad/photo`.
- Match uses the existing `dhash` / Hamming helpers against artwork hashes cached when a species entry is loaded.
- A clear winner returns `match: one` and the same entry as text search.
- Several close hashes and no clear winner return `match: many` and a short list.
- A distant image returns `match: none` and no invented species.
- The handler does not create a deck and does not call `/api/recognize`.
- `#findScan` in card mode still uses the card recognizer.

## Non-Goals

- A paid vision API, a web image search, or a toy-photo catalog.
- Hashing every national-dex image into git.
- Changing printed-card parsing.

## Implementation Outline

1. Remember an artwork dHash when a species entry is built.
2. Rank a query hash against that gallery.
3. Add the route and the Pokémon-mode photo control.
4. Test confident, ambiguous, and miss cases, and assert deck count does not change.

## Data Model And API Impact

`POST /api/pad/photo` multipart file, login required. Hash cache under `data/cache/pad/`.

## Acceptance Criteria

- [x] An image with the same dHash as cached species 25 returns that entry.
- [x] Two close hashes without a clear winner return `match: many` including the right id.
- [x] A distant hash returns `match: none`.
- [x] The photo route does not create a deck.
- [x] Card scan still uses the recognize path.

## Validation Plan

- Build/compile: `.venv/bin/python -m compileall -q app`
- Targeted tests: `.venv/bin/pytest -q tests/test_pad_photo.py`
- Broader validation: `tests/test_pad_species.py tests/test_ui.py`
- Manual review: upload the cached artwork in Pokémon mode and confirm the device fills.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
