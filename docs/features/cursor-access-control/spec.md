# Cursor access control

Status: in_review

Epic: open-trainer-labs

Jira Issue: TBD

Related: [coach-isolation](../coach-isolation/spec.md) (deny list, shipped), [engine v2 design](./engine-v2-design.md), [strategy](./strategy-model.md), [isolation review](./isolation-review.md), [set card survey](./set-card-survey.md)

## Problem And Value

`coach-isolation` shipped the **deny list**: product chat is a Cursor local agent with `tools=["mcp"]`, empty `setting_sources`, and cwd under `data/coach-sandbox/`. It cannot edit `app/`, read `.env`, or run git.

That is not enough. Isolation without an **allow list** means the only way to insert a new printing, fix a household translation, or answer “any number of Basic Energy” is to change `game.py` — which the agent is forbidden to touch. Customers then wait for a master release, which is slower than ChatGPT inventing a house rule.

Engine **v2** is the allow list. Cards plugin into Game. A Player plays with a **Strategy**. Customers do not maintain `game.py`. Their long-term job is to **find where a sim ran wrong** — parser miss, kernel leak, or agent decision — overlay this chat, and file a revisement so trunk parser/hooks/presets get better. Product chat may overlay card AST and Strategy weights. It may not add hooks or put Python on a card.

## Scope

- Card object is the unit of access control for **print**: program, params, decision ids live on the card, not in `StrategySpec` or `game.py` name branches.
- Strategy object is the unit of access control for **choice**: objective weights + when-clauses; never printed look-N. Same `decide()` for `game.attack` and `look_then_attach.how_many`. See [strategy-model.md](./strategy-model.md).
- Fixed hook interface on the kernel. New *kinds* of effect require a trunk version. New *printings* of existing kinds do not.
- Product-chat tools may apply a catalog_id-keyed overlay (params + compiled AST of published kinds) to a simulation. They still must not receive `shell` / `edit` / `delete` / `task`.
- Survey of every unique name in household sets A–F, S, T, and spare, mapped to parsed kinds vs unparsed print vs leaked kernel decisions. See [set-card-survey.md](./set-card-survey.md).

This slice ships the overlay path and the Swallow-Up named decision. It does not rewrite `_resolve_trainer` or freeze every trainer hook.

## Non-Goals

- Starting `lab-python-sandbox` or `user-owned-strategies` from this spec. Those remain gated by `lab-is-an-experiment`.
- A `.py` file per card, or customer Python as the card program (virus library).
- Giving product chat a git worktree of `app/`.
- Auto-appending `lab-is-an-experiment` to `passed_gates`.
- Hardcoding look-N (or any other printed number) into `app/engine/game.py`. Printed text still wins via `parse_effects` / `parse_ability_effects`.

## Implementation Outline

Design is in [engine-v2-design.md](./engine-v2-design.md). This slice:

1. Publish the existing attack-effect `kind` catalog as the overlay allow list (trainer name-dispatch stays trunk work).
2. Apply a catalog_id-keyed JSON overlay to **match copies** on `simulate_match` / `POST /api/simulate` / lab cells. Unknown kinds and look-above-print fail closed.
3. Swallow-Up looks at printed N, then `decide(look_then_attach.how_many)` logs the attach count. No `StrategySpec.swallow_look`. No `min(printed, strat.swallow_look)` in `game.py`.
4. Product chat brief documents `card_overlay`. Agent options stay MCP-only.
5. Parser tests stay exact printed wording. Customer new cards: pin + AST overlay of existing kinds, or RFC. Never a callable on the card.

## Data Model And API Impact

- Card (runtime): `catalog_id`, printed text, compiled program (effect AST), param schema, decision-point schema.
- Overlay (DB / request, not git): keyed by `catalog_id`, typed params and named policies only.
- Chat tools stay MCP-only. New tool fields are schema-validated overlays, not free Python.
- Simulation records should store trunk version + overlay diff (may land with this slice or a follow-on).

## Acceptance Criteria

- [x] Design reviewed: Card owns JSON AST / params / hook-level decision ids; Strategy owns `decide(ctx)`; kernel owns hooks and legal sets; customer overlays never write git or mutate `Game`.
- [x] Isolation review: customer path is AST/weight JSON; parser/new hooks are operator-only. See [isolation-review.md](./isolation-review.md).
- [x] Household set survey attached and used as the v2 hook+decision backlog (not a second rules engine).
- [x] When implemented: product chat can overlay Dondozo `look_then_attach.how_many` without editing `game.py`; look remains 5 from print unless overlay lowers it on the match copy.
- [x] When implemented: agent options still deny shell/edit/delete/task; overlay cannot invent a hook the trunk does not list.
- [x] Printed text still wins. Overlay cannot rewrite the English sentence.

## Validation Plan

- Build/compile: `python -m compileall app tests` (when code exists)
- Targeted tests: overlay schema; Swallow-Up look 5 + per-attack attach count; isolation options unchanged
- Broader validation: `pytest -q`
- Manual review: product chat overlay on `http://127.0.0.1:8000` vs adversarial “edit game.py”

## Status Update Checklist

When work starts or changes state, update the linked issue with:

- current state,
- completed work,
- validation run,
- blockers,
- next action.

**Human:** `cursor-access-control` is in `docs/epics/open-trainer-labs/breakdown.json`. Operator approved implementation. Do not start `lab-python-sandbox` or auto-pass `lab-is-an-experiment`.
