# Coach isolation

Status: done

Epic: open-trainer-labs

Jira Issue: TBD

## Problem And Value

Product chat is a Cursor local agent pointed at the git checkout. Other trainers must be able to talk to Combo Cub without that agent editing `app/`, reading `.env`, or loading Harmonia skills. Isolation is options and workspace, not a prompt.

## Scope

- Product chat `AgentOptions`: `tools=["mcp"]` so only in-process custom tools run; do not offer `shell`, `edit`, `delete`, or `task`.
- `setting_sources` for product chat is empty (ignore `CURSOR_SETTING_SOURCES=project` for this path, or default that env to empty).
- Local `cwd` and `AsyncClient.launch_bridge` workspace are a dedicated directory under `data/` (for example `data/coach-sandbox/`), not `ROOT`.
- Rewrite `FAMILY_CUP_BRIEF`: no “edit files”, no pytest against the repo, no writing `data/lab/`. Numbers come from custom tools.
- Unit tests that inspect the options builder without a live Cursor key: tools list, empty setting sources, cwd not equal to `ROOT`.
- Keep existing custom tools (`list_decks`, `simulate_match`, …) working.

## Non-Goals

- Lab experiment tables, sandbox Python execution, or user-owned strategies (later slices).
- Cloud Cursor agents.
- Changing operator Cursor Desktop / Harmonia skills for the git checkout.
- A power-user web path that writes the product repo.

## Implementation Outline

1. Extract a `product_chat_agent_options()` (or equivalent) used by create/resume.
2. Point local cwd + bridge workspace at `DATA_DIR / "coach-sandbox"` (mkdir).
3. Pass `tools=["mcp"]`; deny `shell`/`edit`/`delete`/`task` if the SDK allows both.
4. Stop loading project setting sources for product chat.
5. Update `FAMILY_CUP_BRIEF`.
6. Tests for the options helper and cwd/workspace paths.

## Data Model And API Impact

- No schema change. Config/default for `CURSOR_SETTING_SOURCES` may become empty for the app server.
- Chat HTTP API unchanged.

## Acceptance Criteria

- [ ] Product chat agent options do not include built-in shell/edit/delete/task.
- [ ] Product chat `setting_sources` is empty.
- [ ] Product chat cwd and bridge workspace are not the repository root.
- [ ] Brief no longer instructs file edits or repo pytest.
- [ ] Tests fail if options are pointed back at `ROOT` or full toolset.

## Validation Plan

- Build/compile: `python -m compileall app tests`
- Targeted tests: new tests on `product_chat_agent_options` / cwd; existing chat tests still pass
- Broader validation: `pytest -q`
- Manual review: confirm `.env` is not under the sandbox cwd

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.
