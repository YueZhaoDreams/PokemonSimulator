# Feature Specs

This directory contains delivery slice specs (typically one PR each). Large outcomes belong in `docs/epics/`; link slices with `Epic: <epic-slug>` or `Epic: none` when standalone.

Draft new slices from `docs/features/_template/spec.md`. Draft epics from `docs/epics/_template/spec.md`.

`cursor-access-control` is the engine-v2 allow list for product chat (Card programs and decision points). Status: `in_review` on `feature/open-trainer-labs/cursor-access-control`. Do not start `lab-python-sandbox` until `lab-is-an-experiment` is in `passed_gates`.

## Status Values

- `planned`: desired but not ready for implementation.
- `ready`: spec is clear enough for an AI or human to implement.
- `in_progress`: implementation has started.
- `blocked`: waiting on a decision, dependency, access, or external review.
- `in_review`: implementation is in PR review.
- `done`: shipped or intentionally completed.
