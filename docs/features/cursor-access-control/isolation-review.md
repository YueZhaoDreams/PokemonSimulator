# Self-check: extensible vs Game/repo stay closed

Question: can engine v2 let customers add **new printings** and **new strategies** without those additions writing `app/engine/game.py` (or any product git), while still growing with future sets?

**Verdict:** the four-object split can do that **inside a frozen hook + Observation catalog**. It cannot do unlimited TCG without a Combo Cub version bump. Several sentences in the earlier design would have forced a git change for every new wording; those are closed below.

Related: [engine v2](./engine-v2-design.md), [strategy](./strategy-model.md), [spec](./spec.md).

## 1. What “won’t affect Game (repo)” must mean

Three different surfaces. Mixing them makes the design look safer than it is.

| Surface | Customer new card / strategy may touch? | Mechanism |
| --- | --- | --- |
| Git checkout (`app/`, `tests/`, shipped `data/lab/`, `.env`, `STRATEGY_LIBRARY`) | **Never** | Cursor deny list (`tools=["mcp"]`, no shell/edit) + no tool that writes those paths + overlays stored in DB |
| Process kernel (`Game` class, module globals, other tenants’ later sims) | **Never** | Overlay is a per-request JSON blob applied to a copy of card programs / Strategy; no monkeypatch; lab Python (later, gated) in a subprocess |
| This trainer’s next simulation | **Yes — that is the product** | Their deck row, their card AST overlay, their Strategy weights |

If a customer “inserts a card” by patching `parse_effects` or adding `if name ==` in `game.py`, isolation has failed even when git is clean on disk from chat — because the only legal path would be an operator PR. v2 must make the **legal** path the DB overlay.

Today: isolation already blocks chat from editing the checkout. `replace_deck_card` writes the trainer’s deck in the database (good). Strategy still lives in git `STRATEGY_LIBRARY`. Card AST overlay does not exist yet. This document is the contract for closing that gap, not a claim it has shipped.

## 2. Extensibility is real, and bounded

| Customer wants | Without git? | What happens |
| --- | --- | --- |
| Pin a known TCGDex id / swap Raichu printing | Yes | `replace_deck_card` → DB |
| Same hook, different numbers or wording (look 5, household translation) | Yes | Overlay **compiled AST** using only existing `kind`s + declared params. Parser catch-up is an **operator RFC**, not the customer path |
| New `you may` / `any number` on an existing hook | Yes | Card declares a **stable hook-level** decision id (`look_then_attach.how_many`, not `dondozo.swallow`). Strategy.decide already answers that id |
| New Strategy (aggro vs grind, go-for-it) | Yes | JSON: objective weights + when-clauses over **published Observation** + features of `ctx.legal` actions. Not a new Python class, not `STRATEGY_LIBRARY` |
| Effect kind the kernel has no hook for (Stance-style prevention, new timing) | **No** | `print_unresolved`; sim runs without that effect; RFC asks for a **new kernel version**. Fail closed. This is the safety bound, not a bug |
| New Observation field (“if opponent’s Ability would prevent this”) | **No** until trunk lists the field | Unknown predicates in when-clauses are ignored |

Unbounded “any new Pokémon Company sentence works tomorrow” would require customer Python on the card. That is how they **would** affect Game. We refuse it.

## 3. Holes found in the draft (and the fix)

### A. “New sentence, old hook → parser branch”

That is an **operator** change to `effects.py`. If it is the only door, every household translation waits for git. **Fix:** customer door is AST overlay constrained to the published kind catalog. Parser tests land later via revisement so the next household does not need the overlay.

### B. “Card-local handler”

A Python callable on a catalog_id in the DB is a virus and can patch how Game behaves for everyone if it is imported into the web process. **Fix:** customer programs are JSON AST only. Operator-shipped handlers, if any, live in git on trunk and still only call listed hooks. Product chat cannot upload callables.

### C. Per-card decision ids

`swallow.attach` vs `dondozo_sv04.attach` would force Strategy overlays to be rewritten per printing. **Fix:** decision ids are **hook-scoped** (`look_then_attach.how_many`, `distribute_counters`). The card program lists which ids it emits. A new Swallow-Up printing reuses the same id; Strategy keeps working.

### D. Strategy enums that grow like `swallow_look`

`swallow.attach: "leave_one_if_hand_energy"` as a one-off enum becomes another `StrategySpec` field in git. **Fix:** score `ctx.legal` with **action features** already implied by the payload (`attach_count`, `leaves_energy_in_deck`, `target_remaining_hp`, `is_closer`). Weights and when-clauses combine those features. New printings of the same hook do not need a new enum. New *features* of actions are a trunk version (same rule as Observation).

### E. Overlay that rewrites print

Param overlay could set `look: 99` and mill the deck without touching git — it would still “change Game” for that match in a rules-illegal way. **Fix:** parsed params from printed text are authoritative. Overlay may (1) fill `print_unresolved` with an AST of existing kinds, or (2) disable a **kernel leak** (stop applying `swallow_look`), not raise look above print. Overlay that disagrees with a successfully parsed sentence is rejected unless it is an explicit RFC-tagged correction waiting for operator pin.

### F. Shared mutable Game

Applying an overlay by mutating `FALLBACK_BY_NAME` or `Game._swallow_energy` would leak into the next user’s Fight. **Fix:** compile overlay onto the match’s card copies only. `Game` class stays immutable for the process. Lab sandbox (later) is a subprocess so monkeypatches die.

### G. Trainers and static abilities (honest lag)

Until `_resolve_trainer` is a card program, a **new trainer name** still no-ops or needs git. Stance / Lunar Zone need new hooks. **Fix:** ship order keeps those as trunk work. Customer can still store the printing in DB; the effect stays `print_unresolved` until the hook exists. Do not pretend Set C/D abilities are customer-extensible today.

### H. Lab Python (not this slice, still a threat)

The sandbox spec allows importing engine APIs. If `Game` or card callables leak into that allowlist, a “strategy script” becomes a kernel patch. **Fix when that slice is built:** subprocess; no assignment to `Game`; Strategy/Card inputs are JSON; script may call `run_simulation(..., overlay=)`.

## 4. What product chat may write (allow list)

JSON only, owner-scoped DB or request body:

- Deck printing identity (`catalog_id` in their 30).
- Card overlay: `{catalog_id: {program: AST, params?: }}` validated against published kinds/params.
- Strategy overlay: `{weights, when: [{if: ObservationPredicate, prefer: ActionFeatureMatch}]}`.
- Lab cells that point at those overlays.
- Revisement row (data): “parser missed this sentence; AST I used; please add a test.”

Never: files under the checkout, `STRATEGY_LIBRARY` keys, new hook names, Python.

## 5. Invariants (test these when implementing)

1. After any product-chat or Lab overlay, `git status` is clean for `app/`, `tests/`, `data/lab/`, `.env`.
2. `Game` bytecode / class dict is unchanged after a request that used a hostile overlay.
3. A second user simulating the same seed without the overlay matches the un-overlaid engine.
4. Overlay AST with `kind` not in the published catalog is rejected; the match does not run a guessed effect.
5. Overlay cannot set `look` above the parsed print when parse succeeded.
6. Strategy.decide return not in `ctx.legal` is dropped; default is pass / attach 0.
7. Product chat agent options still deny shell/edit/delete/task.

## 6. A scan loop does not complete Game

A scheduled ingest (TCGDex / photo OCR → pin `catalog_id` → run `parse_effects` / `parse_ability_effects`) is useful. It is **not** how Game becomes complete.

| What the loop fills | What it does not fill |
| --- | --- |
| Identity: name, HP, attack text, art, `catalog_id` | New hooks (Stance, ACE SPEC timing, copy-attack, …) |
| Coverage report: parsed vs `print_unresolved` vs “needs new kind” | Strategy.decide / Observation fields |
| RFC backlog: exact printed sentences the parser missed | Legal play (unresolved cards still no-op that clause) |
| Regression fixtures for operator parser PRs | Pocket vs paper ranking — ingest must fail closed on identity, not “first search hit” |

“Most of the TCG” is tens of thousands of printings. Completeness for Combo Cub is: **household 30s + the Standard cards you actually simulate**, with a high parse rate **on the hook catalog you already have**. Sweeping everything first creates a catalog of silent no-ops (Relicanth empty text, Prankish, Invite Out) and looks finished.

The loop should write a **DB coverage table** (not git): `catalog_id`, text hash, AST kinds, unresolved spans, suggested hook. Operator then adds the missing **kind** once and every scanned card that used that sentence shape starts working. That is how scan and Game compose: ingest measures the gap; trunk closes kinds; cards stay plugins.

Do not let the job write `PREFERRED_IDS` or `game.py`. Do not auto-promote Pocket ids. Rate-limit TCGDex. Prefer: (1) every unique name already in sets A–F/S/T, (2) Standard rotation used by Set T, (3) then the rest as a report, not as fake completeness.

## 7. Conclusion

- **Extensible:** yes for new printings and strategies that fit the current hook + Observation + action-feature catalog. That catalog grows only with a Combo Cub runtime version (operator git).
- **Repo / kernel closed:** yes if customer data is JSON overlays on copies, not parsers, not callables, not module patches. The earlier “parser branch” / “card-local handler” wording would have broken that; it is not the customer path.
- **Customer role:** find mismatches (parser, kernel, agent), overlay this match, RFC with evidence. That is how parser and Game improve. They never write the checkout.
