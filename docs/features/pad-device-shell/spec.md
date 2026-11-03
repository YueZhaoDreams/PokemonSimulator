# Pad device shell

Status: in_progress

Epic: poke-pad

Jira Issue: TBD

GitHub Issue: TBD

## Problem And Value

The Cards screen is a catalog form. On an iPad it needs to be the handheld drawn on Poké Pad (Perfect Order 081/088, same art as Ascended Heroes 198/217): blue field, red upper shell, white lower shell, glass screen with a ball and pulse, and a play triangle.

## Scope

- Bottom nav label and the `#view-cards` title say Pad. `data-view="cards"` stays.
- `#padDevice` fills the Cards view. Default `data-mode="pokemon"`.
- Landscape CSS (iPad-sized) makes that device the page. Portrait keeps the same device, scaled.
- Idle screen shows the ball and the pulse line. The play control `#padSpeak` has accessible name 朗读. It does not have to speak yet.
- A Card / Pokémon toggle sets `data-mode`. Card mode shows the existing `#cardsHost` finder (`#findPanel`, `#addName`, `#findScan`, `#ownedGrid`). Pokémon mode hides that finder.
- `parkCardsPanel` still moves `#findPanel` between `#cardsHost` and the card sheet. Sets → Add a card still works.
- Do not paste the Studio Bora scan. Do not render Item / TRAINER / 081/088 chrome.

## Non-Goals

- PokéAPI calls, species readout, speech playback, cry, or photo match.
- A new `me03-081` catalog row.
- Fight, Lab, or the match engine.

## Implementation Outline

1. Rebuild `#view-cards` around the device and keep the finder ids inside `#cardsHost`.
2. Add the shell CSS, including a landscape rule.
3. Add `setPadMode` in `app.js`.
4. Lock the structure in `tests/test_pad_shell.py` and update the Cards copy assertion in `tests/test_ui.py`.

## Data Model And API Impact

None.

## Acceptance Criteria

- [ ] Nav and title say Pad. View ids for cards, decks, fight, and lab remain.
- [ ] `#padDevice[data-mode="pokemon"]` shows the idle screen and hides `#cardsHost`.
- [ ] `#padDevice[data-mode="card"]` shows `#cardsHost` with the existing finder.
- [ ] CSS includes the red shell, white shell, idle ball, pulse, and a landscape rule for `.pad-device`.
- [ ] `#padSpeak` accessible name is 朗读.

## Validation Plan

- Build/compile: `.venv/bin/python -m compileall -q app`
- Targeted tests: `.venv/bin/pytest -q tests/test_pad_shell.py tests/test_ui.py`
- Broader validation: same tests, plus a quick read that `parkCardsPanel` is unchanged in behavior.
- Manual review: iPad-width landscape screenshot of the idle device.

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
