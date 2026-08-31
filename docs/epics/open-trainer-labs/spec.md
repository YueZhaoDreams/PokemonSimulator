# Open trainer labs

Status: in_delivery

GitHub Issue: TBD

## Problem And Value

Combo Cub chat is a Cursor local agent whose working directory is the product git checkout. The same session that answers “who wins?” can edit `app/`, read `.env`, run shell, and load project skills that know how to open PRs. That is acceptable for the operator’s desktop IDE. It is not acceptable once other trainers use the public chat.

**Customers must never change repository code.** Product chat, Lab UI, and any generated lab Python are untrusted. They must not write `app/`, `tests/`, shipped `data/lab/`, `.env`, or git. Isolation is a security property of agent options, storage, and the runner — not a polite system prompt.

Today there are also two different “labs” glued together:

- **Operator notebooks** in `data/lab/` (Python bakeoffs, markdown conclusions, JSON matrices). Cursor writes these into git. They are how the family actually changes lists and named play — energy swaps, `carnival` vs `party`, query rates, then a locked 30.
- **Product Lab** (`simulations` rows plus the Lab tab). `simulate_match` stores one matchup. Fight and chat only send a named strategy string. Queries are still hardcoded around Dondozo / Pikachu.

Other trainers need the **notebook loop**, including the same kind of bakeoff **Python** the operator uses, not a thinner log of win rates. Changing a strategy without a controlled comparison is guessing. The product outcome is: a trainer can ask a question, generate or author game-only lab Python and/or cells, run a same-seed comparison, lock the winning cell into **their** strategy (and/or their deck), and use that on Fight — while **none of that code ever lands in the product git repo**.

Generated lab Python is **data in the database**, scoped to that trainer, executed in a sandbox that can only talk to the match engine. Combo Cub is not a code host and must not become a virus library.

Operator `data/lab/` stays the published cookbook and the operator’s git notebook. It is not the multi-tenant store.

## Scope

### Hard invariant: customers cannot change repo code

- Product chat agents must not receive built-in `shell` / `edit` / `delete` / `task`. They use in-process Combo Cub tools only (SDK `tools=["mcp"]` plus existing custom tools). `setting_sources` for product chat is empty (no Harmonia / PR skills). Agent cwd is not the git worktree root.
- `FAMILY_CUP_BRIEF` does not tell the model to edit the checkout or run pytest against the repo. Adversarial prompts (“edit `game.py`”, “cat `.env`”, “git push”, “save this script under `data/lab/`”) must leave `app/`, `tests/`, `data/lab/`, `.env`, and git history unchanged.
- There is no power-user escape hatch in the web app that writes customer or agent output into the product repository. Promotion into `STRATEGY_LIBRARY` or official `data/lab/` is an **operator git change on Desktop**, never a chat or Lab side effect.

### Trainer lab Python (allowed — DB, game-only, sandboxed)

Customers **may** generate Python (and the coach may draft it) so bakeoffs can be as targeted as today’s operator scripts. That Python:

- is stored in the database (per `owner_id`), never as files in the git checkout;
- may run only inside a **sandbox** whose purpose is Family Cup experiments: decks, `StrategySpec` overlays, Monte Carlo, queries, printed-card event names;
- cannot import or call general OS, network, subprocess, filesystem, installer, or reflection APIs that could escape the engine;
- cannot mutate shared process state (`Game` class, other users’ rows, settings, `.env`);
- is size-capped and text-only; refuse binaries, encoded droppers, and payloads that are not a lab experiment;
- is time- and games-capped (existing Monte Carlo cap still applies);
- fails closed: if the script is not clearly game-related or cannot be shown safe, do not store it as executable and do not run it.

JSON cells (deck patch + strategy overlay + queries) remain a first-class, non-Python way to run the same loop. Python is for experiments that need a bakeoff script; it is not a second product.

### Lab experiment, strategies, ownership

- Persist per-owner experiments: question, cells and/or sandboxed script, games, seed, queries, matrix results, learning notes, and which cell was locked (and why). `simulate_match` remains the one-cell shortcut; it is not the whole Lab.
- Queries belong to the experiment (Party fired, named attack, KO of a named Pokémon), not a hardcoded Dondozo/Pikachu list for every run.
- A trainer can save a `StrategySpec` overlay. Fight and chat can select it. Locking a cell can save that overlay (and/or apply a deck patch to a deck they own).
- Experiments, saved strategies, saved scripts, and Lab UI/API are scoped by `owner_id`. Admins may see all. Non-admins never see another trainer’s experiments, strategies, or scripts.
- Shipped `data/lab/*.md` (and related JSON) may be offered as “copy into my experiment.” Copy means a **new DB row**, not a write to those paths.
- **Printed card text still wins.** Lab notes, locked cells, generated scripts, and strategy descriptions must not become a second rules engine. No hardcoded look-N in `app/engine/game.py` from a lab conclusion.

## Non-Goals

- **Customers (or product chat) changing repository code** — no writes, commits, PRs, or checkouts of `app/`, `tests/`, shipped `data/lab/`, `.env`, git config, or secrets. This epic will not add a later “just let them patch the engine” path.
- **A general code host / pastebin / virus library.** Do not store or run malware, unrelated programs, package installs, network clients, or “scripts” whose purpose is not a Family Cup experiment. If we cannot keep it a game sandbox, we do not ship execution.
- Lab Python that reaches the network, the host filesystem (beyond an ephemeral scratch the runner controls), other tenants, or the live web process.
- Cloud Cursor agents for Combo Cub chat.
- Auto-merging a trainer’s locked cell or script into `STRATEGY_LIBRARY` or git `data/lab/`.
- Sharing, forking, or publishing labs between trainers (can follow later).
- Replacing the operator desktop workflow: the operator may still write `data/lab/` from Cursor Desktop.

## Acceptance Gates

Define where acceptance must be verified before dispatch continues or the epic can close. Tag each gate with **consumer** (who experiences the output) and **verifier** (who may sign off).

- **consumer:** `human` (UI/UX), `agent` (API/dispatch consumers), or `both`
- **verifier:** `agent-auto`, `agent-then-human`, or `human-required`

Child slices: `coach-isolation`, `lab-experiment-model`, `lab-run-cells`, `lab-python-sandbox`, `user-owned-strategies`.

### Milestone: `coach-isolated`

- **After features:** `coach-isolation`
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - Product chat agent options: built-in tools are MCP/custom only; `shell`, `edit`, `delete`, and `task` are not offered; `setting_sources` is empty; cwd is not the repository root.
  - After chat prompts equivalent to “edit `app/engine/game.py`”, “print `.env`”, “git push”, and “write a file under `data/lab/`”, the product checkout has no new diffs under those paths (running app at `http://127.0.0.1:8000` or a documented agent-create fixture).
  - A generated lab script, if any, exists only as a DB row for that user, not as a new file in the checkout.
  - A normal lab-style question still gets numbers from in-process tools (not invented win rates).
- **Blocks dispatch until passed:** yes — do not invite non-operator trainers to chat until this gate passes.

### Milestone: `lab-is-an-experiment`

- **After features:** `lab-experiment-model`, `lab-run-cells`
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - API (and chat tool) can create/run an experiment with at least two cells that differ by one deck patch **or** one strategy overlay, same seed and games cap, and custom queries; response includes a per-cell win rate and query rates.
  - A trainer can store a game-related Python bakeoff in the database and run it; the checkout still has no new `data/lab/` or `app/` files.
  - Lab tab at `http://127.0.0.1:8000` shows the matrix for that experiment, not only a single simulation row.
  - Two registered non-admin accounts cannot read each other’s experiments or scripts.
- **Blocks dispatch until passed:** yes

### Milestone: `lab-python-safe`

- **After features:** `lab-python-sandbox`
- **Consumer:** `both`
- **Verifier:** `agent-then-human` (human signs the threat checklist)
- **Verify:** Documented hostile payloads **do not run** and **are not kept as executable lab scripts** (human may extend the list): `import os` / `subprocess` / `socket` / `urllib`; reading `.env` or `app/engine/game.py` from disk; writing anywhere under the git checkout; downloading or decoding a binary; mutating `Game` so a later request from another user sees the patch. Each case: runner rejects or sandbox-kills; no repo file change; no network; other users’ later sims still match a clean engine. A legitimate bakeoff (cells, `run_simulation`, `StrategySpec`, event queries) still runs. Human: confirm we are not storing arbitrary blobs as “labs.”
- **Blocks dispatch until passed:** yes — no public lab-Python until this gate passes.

### Milestone: `strategy-lock`

- **After features:** `user-owned-strategies`
- **Consumer:** `human`
- **Verifier:** `agent-then-human`
- **Verify:**
  - After locking a winning cell, that trainer has a saved strategy (and/or updated owned deck) they can select on Fight (`stratA` / `stratB`) and that chat will use on a later simulate.
  - Official `STRATEGY_LIBRARY` names are unchanged unless an operator changed git.
  - A second trainer does not see the first trainer’s saved strategy.
- **Blocks dispatch until passed:** yes

### Epic exit

- **After features:** all child features done
- **Consumer:** `human`
- **Verifier:** `human-required`
- **Verify:** On `http://127.0.0.1:8000`, an operator and a second trainer account: second trainer authors or copies a comparison (example: Set F `carnival` vs `party` vs an energy-type patch, including a DB-stored Python bakeoff if that path shipped), reads which cell won and whether Party/attack queries fired, locks one cell, plays Fight with that locked strategy. Operator confirms the git worktree has **no** product-chat or trainer-script writes to `app/` or `data/lab/`. Operator still can add a notebook under `data/lab/` from Desktop. Human re-runs the `lab-python-safe` hostile list on the running app. Human may edit this checklist if the shipped cell vocabulary differs.
- **Blocks epic `done`:** yes

## Epic Validation

- Isolation is a property of agent options, database storage, and the sandbox — not of the system prompt alone.
- Untrusted Python is data. The product git tree is not a place customer or chat code is saved.
- Allowlist / sandbox must fail closed. Prefer refusing a clever script over “it might be a lab.”
- `StrategySpec` overlays and engine APIs are how scripts change play; they must not persist monkeypatches onto `Game` for other requests.
- Games-per-run remain capped (existing Monte Carlo cap). Experiments with many cells must stay within a documented budget (human: confirm per-cell games default before invite).
- Printed card text wins over lab markdown, generated scripts, and locked conclusions.

## Status Update Checklist

When the epic changes state, update the linked tracker with:

- current epic state,
- gate pass/fail notes,
- child feature progress summary,
- blockers,
- next human or agent action.
