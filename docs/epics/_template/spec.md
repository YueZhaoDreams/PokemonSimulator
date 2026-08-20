# Epic Name

Status: draft

GitHub Issue: TBD

## Problem And Value

Describe the user, business, or operational outcome this epic delivers.

## Scope

-

## Non-Goals

-

## Acceptance Gates

Define where acceptance must be verified before dispatch continues or the epic can close. Tag each gate with **consumer** (who experiences the output) and **verifier** (who may sign off).

- **consumer:** `human` (UI/UX), `agent` (API/dispatch consumers), or `both`
- **verifier:** `agent-auto`, `agent-then-human`, or `human-required`

### Milestone: <short-id>

- **After features:** `<feature-slug-a>`, `<feature-slug-b>`
- **Consumer:** `agent` | `human` | `both`
- **Verifier:** `agent-auto` | `agent-then-human` | `human-required`
- **Verify:** concrete local app (`http://127.0.0.1:8000`) or data checks
- **Blocks dispatch until passed:** yes

### Epic exit

- **After features:** all child features done
- **Consumer:** `human`
- **Verifier:** `human-required`
- **Verify:** product-level checks on the running app at `http://127.0.0.1:8000` (or documented fixture set)
- **Blocks epic `done`:** yes

## Epic Validation

-

## Status Update Checklist

When the epic changes state, update the linked tracker with:

- current epic state,
- gate pass/fail notes,
- child feature progress summary,
- blockers,
- next human or agent action.
