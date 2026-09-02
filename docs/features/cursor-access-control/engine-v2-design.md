# Engine v2: Card is the program, Cursor is the access control

This is the architecture for Combo Cub engine **v2**. It lives under Cursor access control because the product question is not “can the model write Python?” It is **what a Cursor product-chat agent is allowed to change**.

`coach-isolation` is the deny list. This document is the allow list.

Related: [spec](./spec.md), [set survey](./set-card-survey.md), [strategy](./strategy-model.md), [isolation review](./isolation-review.md).

## 1. Why v2

v1 compiles printed attack/ability text into a global effect list (`parse_effects` / `parse_ability_effects`) and then executes it inside `Game` with extra `if name ==` and `StrategySpec` fields. That works until:

- The Pokémon Company prints a new sentence, or a household translation is wrong, and the legal fix is “put it on **this** `catalog_id`”.
- Print says “any number” / “you may” / “in any way you like”, and the agent needs to answer that **this attack**, from public game state.
- Isolation forbids editing `game.py`, so a clamp like `min(look, strat.swallow_look)` cannot be undone in product chat.

v2 does not give the agent the kernel. It gives the agent a **Card object** with a frozen interface.

## 2. Objects

| Object | Identity | Owns | Must not own |
| --- | --- | --- | --- |
| Game (kernel) | runtime version (v2, …) | Turn loop, Rule B/C, hook dispatch, **legal sets** | Card names, look-N, whether to “go for it” |
| Card printing | `catalog_id` | Printed text, compiled program, param schema, **declared decision ids** | OS, objectives, aggro vs mill |
| Player | seat in this Game | Deck, prizes, hand; holds one Strategy | Kernel hooks |
| Strategy | strategy id | `decide(ctx) → legal choice` for game-steps **and** card holes | Printed params (`look: 5`) |
| Overlay | owner + card id and/or strategy id | Card params; Strategy weights / when-clauses | New hooks, rewritten English, `.py` on the card |

A Card is a program **plugged into** Game. A Player holds a Strategy that `decide`s every legal ask. The program is JSON AST, not a `.py`. Customers overlay parameters and Strategy weights onto **match copies**. Operators merge a printing’s parser/pin into trunk, not a fork of `game.py`.

The program language is the effect AST, not a Python file. Unrestricted Python per card is a virus library and is out of scope even for engine v2.

## 3. Four layers (fixed interface)

Later sets will invent sentences we have not seen. v2 does not need to guess them. It needs a door that stays the same.

1. **Hook (interface)** — kernel / runtime version. Examples already implied by the household: `on_attack`, `on_ability`, `on_play`, `on_attach`, `on_ko`, `look_then_attach`, `search`, `distribute_counters`, `move_energy`, `you_may`. **No new hook without a trunk version.** This is the security boundary.
2. **Implementation** — JSON AST on `catalog_id`. Prefer compile-from-print. If print does not parse, the customer overlay is still AST of existing kinds, never a Python callable. Operator-only handlers in git, if any, may only call listed hooks. Tests use the exact printed wording.
3. **Parameters** — fields the hook already named (`look: 5`, damage, counts). Overlay may change a value that is already in the schema. Overlay may not invent a field.
4. **Decision points** — named holes the print left open (`you may`, `any number`, `choose`, `up to`, `in any way you like`, coin). Strategy fills them **per resolution** via the same `decide()` as `game.attack`. The answer is logged. They must not be buried in `game.py`.

Inserting a card (two doors — do not mix them):

| Case | Customer (DB overlay, no git) | Operator (trunk) |
| --- | --- | --- |
| Print already parses | Pin `catalog_id` on their deck | Optional: add to `PREFERRED_IDS` |
| Same hook, wording/numbers wrong or parser miss | Overlay compiled AST + params using **existing** `kind`s | Parser test + pin so the next household drops the overlay |
| New sentence, old hook | Same AST overlay; card emits the **hook-level** decision id | Parser branch when convenient — not required for this chat’s sim |
| Truly new kind of effect | Store printing; effect stays `print_unresolved`; file RFC | New hook on a new runtime version, then this card’s AST |

Customers never add a Python handler. “Implementation on the card” means JSON AST on that `catalog_id`, not a callable in the web process.

Unknown future complexity is expected. The kernel does not grow an `if Dondozo`. The card grows a JSON program that still fits the published hook catalog. A kind that is not in the catalog does not run. See [isolation-review.md](./isolation-review.md).

## 4. Access control (Cursor product chat)

Map Cursor agent options to Combo Cub objects:

| Cursor control | Combo Cub meaning |
| --- | --- |
| `tools=["mcp"]` | Only in-process tools (list decks, simulate, overlay, lab). |
| No `shell` / `edit` / `delete` / `task` | Cannot patch `game.py` or the hook set. |
| Empty `setting_sources` | No Harmonia / PR skills in product chat. |
| cwd = `data/coach-sandbox/` | Working tree is not the git checkout. |
| Tool schema for overlays | The **allow list**: `{catalog_id: {params, decisions}}` validated against the card’s declared schema. |

What product chat **may** do in v2:

- Pin or replace a printing in the trainer’s DB deck (`replace_deck_card` already exists).
- Overlay params on a `catalog_id` for this chat’s next simulation (compiled AST of existing kinds, or disable a kernel leak such as `swallow_look`). Cannot raise a parsed `look` above print.
- Attach a Strategy overlay (weights / when-clauses) or a decision policy bound to a **hook-level** id (`look_then_attach.how_many`, not a Dondozo-only id).
- File a revisement request (data) so an operator can merge the printing into trunk.

What it **must not** do:

- Add a hook.
- Rewrite printed English.
- Set `StrategySpec.swallow_look` (that field is a v1 leak; v2 deletes it).
- Store or run a `.py` as the card program or as Strategy.
- Mutate `Game`, `FALLBACK_BY_NAME`, or `STRATEGY_LIBRARY` for other requests.
- Write `app/`, `tests/`, shipped `data/lab/`, `.env`, or git.

Strategy remains a separate object: when to Hydro Splash, whether to bench Orthworm, whether to go for last prizes now. It answers every `DecisionContext`. It does not own `look`. See [strategy-model.md](./strategy-model.md).

## 5. Decision point contract

A decision is a named callback the kernel must call when a hook needs a choice.

```
DecisionPoint {
  id: "look_then_attach.how_many"  # hook-scoped, not Dondozo-specific
  legal: 0..len(candidates)      # kernel computes from public state + print
  observe: {deck_len, hand_attachable, can_pay, prizes, ...}
  return: subset of candidates   # Strategy.decide
}
```

Rules:

- The card **declares** the id. The kernel **asks**. Strategy **answers** (same `decide()` as `game.attack`).
- Legal range comes from print + physics (deck shorter than 5 → look 3 is not a policy).
- Every answer is traceable (trace line + query key).
- A policy may use hand energy, remaining deck, prizes. It may not change `look`.

Worked example — Paradox Rift Dondozo `sv04-055`, Supplemental Swallow-Up:

- Param: `look: 5` (print).
- Physics: `look = min(5, len(deck))`.
- Decision `look_then_attach.how_many`: among Basic Energy in the looked cards, attach 0..N.
- Policy the household already wants: take fewer when the deck is thin; take one fewer when the hand already has an attachable Energy.

v1 does the opposite: `thrifty.swallow_look = 3` then `min(printed, 3)`, then greedy attach until `item_spend < 0.75`. That is a leaked decision, not a card program.

Same pattern already in the household (see survey):

| Print | Declared decision (v2) | v1 leak |
| --- | --- | --- |
| Swallow-Up “any number” | `swallow.attach` | `swallow_look` + greedy |
| Phantom Dive / Hex Hurl “in any way you like” | `distribute_counters` | dump all on lowest-HP bench |
| Wondrous Moon “any amount … in any way” | `move_energy` | keep 3 on Clefable, rest to Mewtwo |
| Transfer Charge “up to 2 … in any way” | `attach_from_discard.targets` | always the “main Mewtwo” |
| Shooting Moons “you may discard up to 4” | `discard_hand_energy.count` | not a per-state policy |
| Trekking Shoes / Tool Box “you may” | `look.keep` | strategy score, not a named id |
| Boss’s Orders “1 of your opponent’s Benched” | `boss.target` | lowest remaining HP |
| Drakloak Recon “put 1 of them into your hand” | `look.which` | parser has look 2; choice still implicit |

## 6. Trainers and tools

Pokémon attacks/abilities already go through parsers. Trainers mostly do **not**: `_resolve_trainer` and `_pick_trainer` are name switches in the kernel. v2 treats a Trainer the same as a Pokémon: `catalog_id` → program → hooks (`search`, `draw_until`, `switch`, `look_top`, `stadium`, `tool_stat`).

`_pick_trainer` scores become `Strategy.decide(game.play_trainer)`. `_resolve_trainer` bodies move onto the card program.

## 7. Versioning

| Git idea | Product object |
| --- | --- |
| Trunk | Runtime version + pins + shipped strategies (operator git) |
| Working tree | This chat’s overlay (seconds) |
| File | One printing’s program |
| Branch commit | Saved overlay / lab cell (DB) |
| PR | Master revisement for that `catalog_id` |
| Pull | Customer upgrades runtime; rebase overlays |

Conflict when syncing: if trunk now matches print, drop that overlay field; keep Strategy weights. Overlay that would change printed text is rejected.

## 8. Customer role: find where it ran wrong

Customers (and Combo Cub chat as their instrument) do not own Game or the parser. They **observe** a mismatch, **correct this match** with an overlay, and **report** enough for an operator to improve trunk.

| They noticed | Overlay this chat | Trunk gets better |
| --- | --- | --- |
| Print did not compile / wrong kind (`print_unresolved`, Swallow-Up look clamped) | AST of existing kinds, or disable the kernel leak | Parser test with the **exact printed sentence**; delete the leak |
| Effect compiled but resolved wrong (all 6 Phantom Dive counters on one bench) | Policy on the hook-level decision id | Kernel asks `decide()` instead of a greedy helper |
| Agent legal but wrong (Hop on 7 cards; did not take last prizes) | Strategy weights / when-clause | Optional preset in `STRATEGY_LIBRARY`; Observation field if the condition could not be expressed |
| Brand-new kind of effect | Store printing; effect stays unresolved | New hook on a new runtime version |

Evidence on the revisement row: `catalog_id`, printed text, trunk version, sim id / trace, expected vs actual, overlay used. That is how many households make **parser and Game** better without any of them writing `app/`. Scan jobs can add the same kind of row automatically (`print_unresolved` clusters). Humans still merge git.

## 9. What we are unsure about

Future printings may need hooks we do not have (attach to opponent, copy an attack that is not Metronome, stadium replacement effects, ACE SPEC timing, Poké-Power-style between-turns). v2’s answer is not a bigger `game.py`. It is: **fail closed** (do not invent an effect), surface `print_unresolved` on the Card, and require a trunk hook for a new kind.

The [set survey](./set-card-survey.md) is the backlog of kinds and decisions we **already** have in the house. It is not a claim that the interface is complete.

## 10. Ship order (inside this access-control story)

Isolation already shipped. Do not wait for sandbox Python.

0. Isolation + labs + Rule C overlay (main).
1. **This slice:** card-program overlay on simulate, keyed by `catalog_id`; kernel stops shrinking printed look; named decisions for Swallow-Up at minimum.
2. Lift `distribute_counters`, `move_energy`, `attach_from_discard` off greedy kernel helpers (same interface, household already prints them).
3. Trainer programs: replace `_resolve_trainer` name switch with card programs (same hooks).
4. Persist overlays; Fight picker (`user-owned-strategies`, still gated).
5. Simulation record stores trunk version + overlay diff.
6. Revisement queue. Sandbox Python remains a later, separately gated slice.

## 11. Invariants

- Printed card text wins. Parsers read the sentence. Lab notes and strategy blurbs do not invent look-N.
- Product chat never writes `app/`, `tests/`, shipped `data/lab/`, `.env`, or git.
- New hook = new kernel version. New card = new program on an id.
- Decision points are named, legal-ranged, logged, and answered by Strategy — including “take 0”.
- Strategy is condition → decision. Aggro / mill / “go for it” are objective weights, not subclasses per deck. See [strategy-model.md](./strategy-model.md).
- Customers report mismatches; they do not write `app/`. Evidence on a revisement makes parser tests and hooks better for everyone.
