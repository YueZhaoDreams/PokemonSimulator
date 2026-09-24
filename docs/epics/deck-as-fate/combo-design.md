# Relations, combos, and deck plans: model and flow design

Status: draft for operator review

Related: [epic spec](./spec.md), [strategy model](../../features/cursor-access-control/strategy-model.md), [engine v2](../../features/cursor-access-control/engine-v2-design.md)

This document proposes how cards relate to each other, how a deck's strategy is modelled as combos built on those relations, how search cards become **superposed** cards inside a deck, and how combos are searched, shared, and revised. It is the design behind operator notes from 2026-09-23:

- Nest Ball is a superposition of every Pokémon it can fetch. Drawing it is drawing all of those possibilities at once.
- Strategy should travel with the deck.
- Several cards together form a combo. Combos should be searchable and shareable, and they should reference each other. A strategy is the deck's big combo, not a named branch in code.
- A combo describes a relationship between cards. Nest Ball relates to every Basic; Mew ex's copied attacks relate to every Pokémon. A combo is a best practice someone found on top of those relationships, but it is not absolute.

Requirements: **reusable** (one relation or combo serves many decks), **extensible** (new cards, new decks, and new combos arrive as data, not as code).

## 1. Why the current shape does not scale

`app/engine/game.py` has 100 `strat.name == "..."` branches today, across `party`, `g`, `celebration`, `phantom`, `slash`, `shock`, `carnival`, `thrifty`, `demolish`, `crunch`, `invisible`. Most pair a strategy name with a card name (`strat.name == "g" and name == "ledyba"`). Three consequences:

1. A new deck idea needs a new strategy name and a new set of branches in the kernel.
2. The same idea is rewritten per name. Returning a Pokémon to hand is `_party_bounce_combo` (Seeker, Boss, double Prankish, Penny, heal-bounce in a fixed order) for `party`, and a separate bench cap table for `celebration` (one Buneary, one Porygon, one Aipom, one Raikou V).
3. Lab results end as code or constant edits (`SET_C60_NAMES`, fixed sleeve indexes) instead of a new version of the deck and its plan.

The branches also mix two different kinds of knowledge. "Nest Ball can fetch Clefairy" is a fact from print. "Bench Clefairy before Mewtwo on turn 1" is advice that held in some labs. Code treats both as the same `if`, so advice can never be tested, weakened, or dropped without an edit.

`strategy-model.md` already fixed the decision interface: Strategy is `decide(ctx) → legal choice`, driven by objective weights and Observation, with no subclass per deck. It does not say what the cards can do for each other, or what this deck is trying to assemble. Relations and combos are the missing objects.

## 2. Principles

1. **Print is the only source of what a card does.** Relations come from parsed print. A combo can name cards and prefer legal actions. It cannot add an effect, a look size, an attach count, or a search width.
2. **Relations are facts; combos are hypotheses.** A relation holds whenever the print says so, in every deck. A combo is a found best practice: a chosen part of the relation graph, with copy counts and a preferred line, claimed under stated conditions and backed by evidence. It can be supported, weakened, or refuted.
3. **A combo never forbids a legal action.** It adds a preference to the score. When the position clearly calls for something else, `decide` deviates, and the deviation is logged as evidence about the combo.
4. **The kernel never reads a strategy name or a combo id.** It computes legal actions, runs hooks, and asks `decide(ctx)`. Operator decision, 2026-09-23: the ~100 `strat.name ==` branches come out. A new line of play arrives as combo and plan data. The engine gets smarter by composing those, by weighing them with evidence, and by search, not by another hardcoded name. Rules and the parser stay code; deck-specific choices do not.
5. **Combos are matched, not named.** Which combos a player pursues is decided by matching the library against the deck list and the board, scoring the matches, and selecting. No code path picks a combo because of a strategy name, and a deck does not need a hand-written plan to play its combos. Identity of a combo is `id@version`, not a name string.
6. **A combo in play is an instance with memory.** Many combos span turns. Once selected, a combo becomes an instance that remembers which cards it bound and which steps are done, carries that across turn boundaries, and is re-evaluated, continued, or abandoned as the board changes.
7. **Reuse is by reference.** A combo includes another combo by pinned reference and binds its parameters. It does not copy it.
8. **Cards are addressed by selectors over printed attributes.** A literal name or `catalog_id` is allowed when print names the card or a human pins it.
9. **Everything a trainer adds is data, validated against a published vocabulary.** Unknown keys, unknown decision ids, or cycles fail at save time. Nothing fails open at play time.

## 3. Model

### 3.1 Layers

```
Catalog printing ──parse_effects / parse_ability_effects──▶ Effects (kinds + params)
        │                                                        │
        └──────────── attributes ────────▶ Selector vocabulary ◀─┘
                                                 │
Relation graph (hard, from print): source capability ─▶ target selector, per scope
        │  instantiated per deck (and against the opponent's board)
        ▼
Combo (soft, data): a chosen subgraph · slots | refs · context · line · keep · evidence → strength
        │  refs are pinned id@version, acyclic
        ▼
Deck match (per deck version): library combos whose slots resolve in this list → candidates
        │  Plan (optional): weights, pins, exclusions, priorities on top of the candidates
        ▼
Board match (each decision): feasible candidates → score → select → combo instances (with step memory, across turns)
        │
Strategy.decide(ctx): objectives + Σ instance value × advance − keep penalties
        │
Game kernel: legal(state, deck, rules), hooks, applies the chosen action
```

Only the bottom box and the parser are code. The relation graph is computed from print; combos and plans are data.

### 3.2 Printing and capabilities

Unchanged object: a printing with `catalog_id`, printed text, attributes (category, stage, types, HP, Rule Box, `evolves_from`, energy type, trainer kind, attacks, prize weight under rules), and the effects the parser already emits.

A **capability** is an emitted effect kind with its params, e.g. `call_family {count: 1}`, `search_pokemon_no_rule_box`, `return_self_to_hand {once_per_turn}`, `attach_special_energy_from_hand {as_often_as_you_like}`, `hand_count_times {per: 20}`, `attach_energy_from_deck_per_benched`, `gust_low_hp_on_evolve {max_remaining: 90}`, `copy_benched_attacks`, `copy_active_attack`. Capabilities are derived. Nobody hand-tags a card.

### 3.3 Selector

A selector is a JSON predicate over a printing's attributes and capabilities. It is how relations name their targets, how combos stay generic, and how new cards join existing relations and combos without edits.

Vocabulary (versioned, small):

| Key | Matches |
| --- | --- |
| `category`, `stage`, `types`, `trainer_kind`, `energy_type`, `basic_energy` | printed attributes |
| `rule_box` | true / false |
| `hp_lte`, `hp_gte`, `prize_weight` | printed HP, prizes under active rules |
| `evolves_from`, `evolves_into` | a name or another selector |
| `has_kind` | an effect kind, optionally with param filters |
| `attack` | `{cost_lte, damage_gte, has_kind}` on any printed attack |
| `name`, `catalog_id` | literal pin |
| `all`, `any`, `not` | combinators |

Examples:

```json
{"all": [{"category": "Pokemon"}, {"stage": "Basic"}]}
{"all": [{"category": "Pokemon"}, {"rule_box": false}]}
{"any": [{"has_kind": "return_self_to_hand"}, {"has_kind": "return_pokemon_to_hand"}]}
{"attack": {"has_kind": "hand_count_times"}}
```

### 3.4 Relations: the hard layer

A **relation** is a typed, directed, usually one-to-many link from one printing's capability to every printing a selector matches. It is the epic's catalog knowledge graph (`card-kg-from-print`), stated as an object.

| Field | Meaning |
| --- | --- |
| `source` | printing (`catalog_id`) and the capability that creates the relation |
| `kind` | relation class: `fetches`, `evolves_into`, `attaches`, `returns_to_hand`, `copies_attack`, `forces_active`, `draws`, `pays_energy`, `zone_feed` (one card's effect puts cards into a zone, another's takes matching cards out), … |
| `target` | a selector, not a list of names |
| `scope` | where targets live: own deck, own hand, own bench, own discard, opponent's Active, opponent's bench |
| `limits` | printed count, trigger, and filters (Nest Ball 1 to Bench; Glittering Star Pattern on evolve, remaining HP ≤ 90) |
| `print` | the sentence that produced it |

One table lives in code, in the fate layer: **capability kind → relation kind, target selector, scope**. `call_family` without a name maps to `fetches` / Basic Pokémon / own deck; `call_family {name}` to that name; `search_pokemon_no_rule_box` to Pokémon without a Rule Box; `copy_benched_attacks` to `copies_attack` / Pokémon with an attack / own bench; `copy_active_attack` to `copies_attack` / the opponent's Active. The table is keyed by effect kind, never by card name. It grows only when the parser adds a kind.

In a given deck, a relation is **instantiated**: its targets are the cards in that 60 (or on the opponent's board) that the selector matches. The instance has a **value** computed from the targets' print, never typed in:

- `fetches`: how many targets, and which slots they fill (section 3.5).
- `copies_attack`: the best damage per energy among the targets the copier can pay for. Mew ex with a bench of 30 HP babies and Mew ex with a benched Gholdengo are the same relation with very different values.
- `forces_active`: how many charges the list can produce (`charges = min(evolution, body)` for an evolve trigger).

A value can be a **condition on the target against itself**. For `copies_attack` into the opponent's Active, where our side chooses the attack, the relation is **lethal** against a target \(X\) when some attack \(a\) of \(X\), resolved as if our copier used it, does at least \(X\)'s remaining HP. The copied damage takes weakness and resistance from the copier's type, runs "for each" terms on the copier's state, applies our Tools, and puts self-effects (discard, recoil) on the copier. Remaining HP makes it dynamic: a damaged target can become lethal.

**Who chooses** is part of the relation (`chooser`: self, opponent, each player for their own side). When we choose, the relation is worth its best option. When the opponent chooses, it is worth the option best for them. When the opponent's option set has exactly one member, their choice is **forced**, and the relation is worth that member. This is superposition on the opponent's side: a choice with a basis of one has already collapsed.

Metronome Clefable prints "choose 1 of your opponent's Active Pokémon's attacks": we choose, so every lethal attack is available. Mime Jr.'s Mimed Games lets the opponent choose; the engine's opponent already avoids an attack that would knock out its own Active. Same `copies_attack`, opposite chooser, and the lethal value disappears. Seeker ("Each player returns 1 of his or her Benched Pokémon and all cards attached to it to his or her hand. (You return your Pokémon first.)") lets each player choose their own: against a bench of two it is the opponent's pick; against a bench of one it is forced.

Lethal-to-self is also a **risk** on our own list: each of our Pokémon with an attack at or above its own HP is exposed to any opponent that runs a `copies_attack` relation with us choosing. It is a cross-deck edge and belongs in the fate score's risk term.

**Relations through zones.** Some relations do not link two cards directly; one card puts cards into a zone and another takes them out. Ultra Ball ("Discard 2 cards from your hand. Search your deck for a Pokémon.") has a cost that **produces** into our discard pile, with `discard.which` as our choice. Mewtwo ex's Transfer Charge ("Attach up to 2 Basic Psychic Energy cards from your discard pile to your Pokémon in any way you like.") **consumes** Basic Psychic Energy from our discard pile. The relation Ultra Ball → Transfer Charge exists because the producer's output can match the consumer's selector in the same zone. The zone is also where progress waits between turns (section 3.9).

Scope matters for fate and luck. A relation into the opponent's board (`copy_active_attack`, `forces_active`) has a value that depends on the opponent's list and play: part of the relation is luck, not fate. Its instance is evaluated against the league of opponents, not against one deck.

Relations are never overridden by a combo, a plan, or a lab note. A missing relation is a parser gap, fixed with a parser branch and an exact-wording test.

### 3.5 Superposition (叠加态): fetch relations over the deck

In a deck \(D\), a searcher \(s\) whose `fetches` relation targets selector \(\sigma\) in scope "own deck" is a **superposed card**.

- **Basis** \(B(s, D) = \{c \in D : \sigma(c)\}\). Same Nest Ball, different deck, different basis. The basis is computed, not saved.
- **Collapse** happens when the card resolves. Print fixes how many members it picks (Nest Ball 1; "up to 2" → 2) and where they go (Bench for Nest Ball). Which member is a decision point, `search.which`, answered by `decide()`.
- **Exclusive.** One resolution yields its printed count, not one of each basis member. Every searcher in the deck draws from the same shrinking deck: a Basic fetched or prized is gone for all of them.
- **Universal searchers** (Forest Seal Stone Star Alchemy, `search_any_card`) have the whole deck as basis. They are flagged `universal` so they do not flood the metrics.

Metrics per slot a combo needs:

- `reach(slot, n)`: P(at least one card that fills the slot, **or** a live searcher whose basis meets the slot, within \(n\) seen cards). The exact value comes from a draw-only sampler (shuffle, open, draw, no game). The hypergeometric on the union count is reported as an upper bound only.
- `shared_searchers`: searchers whose basis meets two or more slots. Two slots that lean on the same 4 Nest Ball do not both get 4 Nest Ball of reach.
- `basis` listing, so a trainer can read "Nest Ball here = these 7 Basics".

A Basic that Nest Ball can fetch is not isolated for lack of a tutor: the fetch relation is its edge.

### 3.6 Combo: a found best practice

A combo picks part of the relation graph and says: in this context, with about these copies, playing along this line has worked. It is versioned, owned, and revisable.

```json
{
  "id": "cmb_bounce_host",
  "version": 1,
  "owner": "user_…",
  "visibility": "private",
  "title": "Bounce host",
  "summary": "Put a Pokémon and its attachments back in hand, then replay it.",
  "params": {
    "host": {"selector": {"category": "Pokemon"}, "doc": "Pokémon that goes back to hand"},
    "bouncer": {"selector": {"any": [{"has_kind": "return_self_to_hand"}, {"has_kind": "return_pokemon_to_hand"}]}}
  },
  "parts": [
    {"slot": "host", "selector": {"param": "host"}, "copies": {"min": 1, "target": 2}},
    {"slot": "bouncer", "selector": {"param": "bouncer"}, "copies": {"min": 1, "target": 2}}
  ],
  "uses_relations": [{"kind": "returns_to_hand", "from": "bouncer", "to": "host"}],
  "context": {"rule_presets": ["s60"], "when": {"turn_gte": 2}},
  "line": [
    {"prefer": {"decision": "game.use_ability", "source": {"slot": "bouncer"}, "kind": "return_self_to_hand"}},
    {"prefer": {"decision": "game.bench", "card": {"slot": "host"}}, "after": 0}
  ],
  "goal": {"observe": "slot_in_hand", "slot": "host"},
  "keep": [],
  "evidence": [],
  "derived_from": []
}
```

Fields:

| Field | Meaning | Must not |
| --- | --- | --- |
| `params` | Typed holes with a default selector. A parent binds them. | Carry a probability or a weight |
| `parts` | Either a **slot** (`selector`, `copies {min, target, max}`) or a **ref** (`ref: "cmb_x@2"`, `as`, `bind`) | Exceed the rule preset's copy cap |
| `uses_relations` | Which relation instances between slots the combo relies on. Validation fails if print does not provide them. | Declare a relation print does not have |
| `context` | Where the claim is made: rule presets, turn window, own-board or opponent-capability conditions (`opponent_has_kind`). Outside its context a combo contributes nothing. | Name the opponent's strategy |
| `line` | Preferred action patterns: decision id, source slot, effect kind, target slot, optional `when`, optional `after` (indexes of earlier patterns; a partial order), optional `repeat: "until_goal"` | Name an action the kernel did not publish, or forbid one |
| `goal` | A published Observation predicate (`slot_in_play`, `slot_evolved`, `energy_ready`, `hand_count_gte`, `can_ko_active`, `opponent_no_pokemon_after_ko`, …) | Invent an Observation field |
| `horizon` | How many of our turns the combo may take from its first step to its goal. A one-turn combo has horizon 1. | Promise a turn count the rules cannot give (first turn no attack) |
| `keep` | Soft invariants the scorer penalises breaking: "fuel stays attached", "Puzzle of Time parked in discard" | Forbid a legal action outright |
| `evidence` | Links to simulation ids, lab experiments, deck versions, with the measured comparison each one supports | Hold a hand-typed win rate |
| `derived_from` | Decks, lab experiments, or self-play runs the combo was mined from | — |

**Strength** is computed, not typed. For each evidence item the engine has, or can run, a paired comparison: the same deck and seeds with the combo's preference on and off. Strength is the lower end of the confidence interval on that difference, per context, shrunk toward 0 when evidence is thin.

**Status** follows from strength: `untested` (no evidence), `supported` (interval above 0), `mixed` (interval spans 0), `refuted` (interval below 0). A refuted combo stays in the library with its evidence, so nobody rediscovers it blindly, but contributes nothing to play.

Loops are `repeat` on a line pattern, not a self-reference. The Hand Fling loop repeats "bounce host → replay → evolve → attach" until the closer's damage KOs.

### 3.7 References and binding

- A `ref` pins `id@version`. An imported or referenced combo never floats to a newer version. Upgrading is explicit and shows the diff.
- `bind` maps the referenced combo's params to the parent's slots or to narrower selectors. A bound slot is **one** slot: cards shared through a binding are counted once.
- Resolution flattens the tree into a **slot table**: concrete cards in this deck, copies, and the combo path that needs each one (provenance).
- References must be acyclic. Depth is capped (proposal: 6) so resolution stays bounded.
- If two independent slots match the same printing, their `min` copies add up and the slot table reports the contention. If two parts put conflicting `keep` rules on one card, validation warns and the parent sets priority.
- A parent's strength is measured on its own; it is not the product of its children's. A combo can be supported inside one deck and mixed inside another.

### 3.8 Plan: what travels with the deck

A deck plays its combos without a plan. The default candidate set comes from **deck match** (section 3.9): every library combo whose slots resolve in this list and whose status is not refuted. A plan is what a trainer or a tuner adds on top.

```json
{
  "id": "plan_g",
  "version": 4,
  "deck_id": "seed-g",
  "deck_version": "sha256:…",
  "candidates": "auto",
  "pin": ["cmb_g_root@4"],
  "exclude": ["cmb_bench_out@1"],
  "weights": {"win_now": 0.6, "equity": 0.8, "setup": 0.9, "self_preserve": 0.5, "clock": 0.1, "plan": 1.0, "keep": 0.7},
  "priorities": [
    {"when": {"turn_lte": 2}, "prefer": ["cmb_party_engine"]},
    {"when": {"opponent_has_kind": "bench_damage_counters"}, "prefer": ["cmb_bench_shield"]}
  ]
}
```

- `candidates: "auto"` means deck match. `pin` adds combos (a root combo written for this deck is just a pin). `exclude` removes matched combos that this deck should not pursue. No `name` field is read by any code path.
- `weights` are the objective weights from `strategy-model.md` plus the plan and keep weights of section 3.9. These are what self-play tunes.
- `priorities` multiply a combo's selection score under a board condition. They never select a combo on their own; a combo that does not match the board stays unselected whatever its priority.
- A plan binds to a **deck version** (hash of the list). Editing the list re-resolves the plan. A slot with no card left is reported as "combo broken by list change", not silently ignored.
- The deck row carries `plan_id`. Sharing a deck shares the list, the plan, and every referenced combo pinned by version.
- Monte Carlo loads each seat's plan from its deck. A strategy dropdown becomes an override, not a requirement.
- Matchup behaviour is a priority clause keyed on the opponent's capabilities, not on the opponent's strategy name.
- A plan has its own evidence: paired runs of the deck with the plan against the same deck with `candidates: "auto"` alone.

### 3.9 Match, score, select, continue

This is the core of play. No step reads a strategy name. The kernel interface stays `decide(ctx)`.

**Step 1: deck match (once per deck version).** For every library combo in the rule preset, resolve its slots against the list, with superposition: a slot is filled by a card that matches the selector, or reachable through a searcher whose basis meets it. A combo whose every `min` is met is a **candidate**. Near misses ("missing 1 Ledyba") are kept for deckbuilding search, not for play. The plan then applies `pin` and `exclude`. The result is cached with the deck version.

**Step 2: board match (at the start of each of our turns, and whenever a decision is asked).** For each candidate whose `context` holds on the current board, and for each live instance (step 4):

- **Feasibility** \(P_c\): the probability of reaching the goal within the remaining `horizon`, from the current zones. Cards already in hand, in play, attached, or in the discard count as present. The rest comes from the draw-only sampler over our hidden deck order, with searcher bases, and with the rules' turn limits (no attack on the first turn going first, one Supporter per turn, one manual attach).
- **Value** \(V_c\): what the goal is worth in objective terms on this board. `can_ko_active` is worth the prizes of the opponent's Active; `opponent_no_pokemon_after_ko` is worth the game. The same combo is worth more against a two-prize Active than a one-prize one.
- **Remaining cost** \(C_c\): what the remaining steps spend and expose: an attack spent for 0 damage, a two-prize Pokémon benched early, Energy discarded, the Supporter for the turn.

**Step 3: score and select.**

\[
\text{sel}(c) = p_c \, s_c \, P_c \, V_c - C_c
\]

\(s_c\) is the combo's strength in context (section 3.6) and \(p_c\) the plan priority, 1 by default. The player selects combos greedily by \(\text{sel}\), skipping any combo that conflicts with one already selected (both need the same scarce resource: the one card, the Supporter this turn, the attack this turn). Usually one combo is primary and one or two small ones run alongside. A combo with \(\text{sel} \le 0\) is not selected.

**Step 4: combo instances.** Selecting a combo creates an **instance**, stored per game and per player, beside the board:

```json
{
  "instance": "ci_3f2a",
  "combo": "cmb_discard_fuel@1",
  "status": "active",
  "bindings": {"fuel": ["card#41", "card#17"], "attacker": ["card#08"]},
  "done": [0],
  "open": [1],
  "started_turn": 3,
  "last_advanced_turn": 3,
  "horizon_end_turn": 7,
  "history": [{"turn": 3, "pattern": 0, "decision": "discard.which"}]
}
```

- `bindings` are card instance ids, not printings: *this* Mewtwo ex, *these* two Energy. A bound card that leaves the zone the combo needs it in is unbound. If another card matches the slot, it rebinds; if none can, the instance is **broken**.
- `done` and `open` are indexes into `line`. A pattern is done when a logged action matched it. `after` makes the order partial, so progress is a set, not a single counter; "which step" is the set of done patterns.
- The instance survives turn boundaries and opponent turns. It is part of our side of the Observation and is hidden from the opponent's seat.
- Status: `active` → `completed` (goal holds) | `abandoned` | `broken` | `expired` (past `horizon_end_turn`). Every transition is logged with its reason.

**Step 5: continue or abandon.** At the start of each of our turns, and after the opponent disrupts one of our zones, each active instance is scored again with step 2, from the board as it is now. Progress needs no special bonus: fuel already in the discard, or a body already on the bench, raises \(P_c\) and lowers \(C_c\), so an instance halfway done naturally outscores starting something new. An instance is abandoned when another selection beats it by more than a margin \(m\) (a plan weight, so choices do not flip on sampler noise), or when \(P_c\) drops to near 0. Abandoning frees its bindings.

**Where progress waits.** A multi-turn combo parks progress in a zone, and zones differ in how well they keep it across the opponent's turn:

| Zone | Survives the opponent's turn unless the opponent has |
| --- | --- |
| Discard pile | A relation that removes cards from our discard |
| In play, attached | A knock out, gust, bench damage, or energy removal relation |
| Hand | Hand disruption (shuffle-and-draw Supporters, hand bounce into deck) |
| Deck | Nothing keeps order; any shuffle resets it |

These are the opponent's relations into our zones (scope "opponent's side"), evaluated against the league, so \(P_c\) already prices the risk. Parking a key card in the discard for a later recovery, like Celebration's Puzzle of Time, is a combo choosing a safe zone.

**Step 6: score each legal action \(a\)** against the selected instances:

\[
\text{score}(a) = \sum_{o} w_o f_o(a) + w_{\text{plan}} \sum_{i} \text{sel}(i) \cdot \text{advance}_i(a) - w_{\text{keep}} \cdot \text{breaks}(a)
\]

The first term is the existing objective scorer. \(\text{advance}_i(a)\) is positive when \(a\) matches an open pattern of instance \(i\) with its bindings, collapses a superposition into one of its missing slots, or draws toward it. \(\text{breaks}(a)\) counts `keep` rules of live instances that \(a\) would violate, such as recovering the fuel into hand before its consumer runs.

**Step 7: pick and log.** Pick the best action among `ctx.legal`. Log the decision id, the instance id, the pattern, the top features, and whether the pick **deviated** from the best instance move (a different action outscored it). An action that matches a line pattern's first step of an unselected candidate does not start an instance; instances start only from selection, so the log says which combo the player was trying.

Deviation is expected, not an error. Taking the last prizes this turn outscores the next step of a setup combo because `win_now` is larger. Deviations are grouped per combo and context; a combo that is often deviated from in games that are then won is a candidate for a narrower context or a lower strength.

No candidates, or every instance broken or at zero value, falls back to the objective scorer alone. That is how an unknown scanned deck still plays.

Decision points this needs from the kernel, in the same `DecisionContext` form as `look_then_attach.how_many`: `search.which` (which basis member a search collapses into), `discard.which` (which cards pay a discard cost such as Ultra Ball's), `copy.which` (which target attack a copier uses), `gust.which` (which opponent's Benched Pokémon a gust brings in), `bounce.which` (which of our own Pokémon a bounce returns), `attach.distribute` (how "in any way you like" splits Energy), `game.bench`, `game.use_ability`, `game.play_trainer`, `game.evolve`, `game.attach`, `game.attack`. These are hook-level ids published once; no deck adds one.

### 3.10 Fate metrics

Relations and combos give the epic's fate score something concrete to measure:

- **Relation value per deck**: fetch bases, copy targets' best damage per energy, gust charges.
- **Completion probability by turn \(t\)** for each combo, from the draw-only sampler: slot reach through superposition, dependence (evolutions need bodies; a slot with more Stage 1s than Basics is stranded), copy caps from rules.
- **Monte Carlo per combo**, from instance logs: how often it was selected, completed, abandoned (and for what), broken (and by what), expired; turns from start to goal; deviation rate. Win rate is still luck given fate.
- **Junk**: a card with no relation to any other card in the 60 (the epic's isolated flag). **Unused**: a card with relations but in no slot of the resolved plan; it is a candidate cut, not junk.
- **Contention**: slots competing for the same searchers or the same copies.
- **Consistency and flexibility**: the two deck-level axes computed on the knowledge graph (section 3.11).

### 3.11 One knowledge graph: cards, relations, combos

The epic's output is a graph. The spec's catalog knowledge graph and deck knowledge graph have printings as nodes and printed links as edges. This design adds combos to the same graph, so one structure answers "what can these cards do for each other" (print) and "what has worked" (evidence).

**Nodes**

| Type | Is | Attributes |
| --- | --- | --- |
| `printing` | One catalog printing | Printed attributes, capabilities, node quality from the spec (damage per energy, HP, prize weight) |
| `role` | A selector that relations and slots point at: "Basic Pokémon", "Basic Psychic Energy", "Pokémon with an attack" | Selector JSON; which printings it matches |
| `zone` | Our discard, our hand, our bench, opponent's bench | Durability against the league (section 3.9) |
| `combo` | One combo version | Strength and status per context, `horizon` |
| `goal` | A goal predicate: `energy_ready`, `can_ko_active`, `opponent_no_pokemon_after_ko`, … | Objective value |

**Edges**

| Type | From → to | Hard or soft | Carries |
| --- | --- | --- | --- |
| relation (`fetches`, `copies_attack`, `forces_active`, …) | printing → role or printing | hard | The printed sentence, scope, chooser, limits |
| `produces` / `consumes` | printing → zone / zone → printing | hard | The printed sentence; together they form a `zone_feed` |
| `matches` | role → printing | hard | Derived from the selector |
| `slot` | combo → role or printing | soft | Slot name, copies `min` and `target` |
| `uses` | combo → relation edge | soft | Which printed link the combo leans on |
| `ref` | combo → combo | soft | Pinned version, bindings |
| `achieves` | combo → goal | soft | Strength in context |

A combo links many cards at once, so it is a hyperedge. The graph stores it as a node with `slot` edges (the usual way to store a hypergraph as a plain graph), which also lets combos point at each other with `ref`.

Hard and soft edges never mix meanings. The spec's isolated/junk flag reads hard edges only: a card that sits in a combo but has no printed link to anything is still junk, and a combo cannot rescue it. Soft edges give weight and routes; hard edges decide what exists.

**Three levels**

1. **Catalog graph**: every printing, role, zone, and relation. Recomputed per catalog and parser version.
2. **Library layer**: combo and goal nodes with their soft edges, filtered by what the viewer may see.
3. **Deck graph**: the induced subgraph for one deck version: printings in the 60 with copy counts, roles restricted to cards in the 60, matched combos (section 3.9 step 1), and per-deck numbers on edges (reach, completion probability by turn). Computed per deck version, cached, never hand-edited.

**What makes a deck good: two axes**

A deck can be good in two ways, and the graph measures both.

*Consistency (C)*: the deck does its main thing, often and early.

- \(P_\gamma(t)\): probability that goal \(\gamma\) is reached by turn \(t\) through its best route (a combo that achieves it), from the draw-only sampler.
- \(C = \sum_\gamma v_\gamma P_\gamma(t_\gamma)\), with the goal values \(v_\gamma\) and target turns \(t_\gamma\) as plan or preset weights.
- Node quality from the spec (damage per energy, warm-up turns, prize weight) enters through \(v_\gamma\): a route to a 280-damage closer is worth more than a route to a 60-damage one.

*Flexibility (F)*: the deck still has good moves when the draw, the prizes, or the opponent take something away.

| Metric | Definition | Reads as |
| --- | --- | --- |
| Routes per goal | \(N_\gamma\): number of matched, non-refuted combos that achieve \(\gamma\) with \(P \ge p_{\min}\) by \(t_\gamma\) | "3 ways to power an attacker" |
| Cut size | \(\kappa_\gamma\): the fewest card names whose loss (every copy prized or discarded) drops \(P_\gamma(t_\gamma)\) below \(p_{\min}\) | \(\kappa = 1\) is a single point of failure |
| Load-bearing cards | The names that appear in the smallest cuts | "Lose Mewtwo ex and nothing else attacks" |
| Versatility of a card | \(v(c)\): number of distinct goals whose routes use \(c\), weighted by route strength. Deck versatility is the copy-weighted mean | Nest Ball and Ultra Ball score high; a card with one job scores 1 |
| Superposition breadth | For each searcher, the nominal basis size and the effective size \(e^{H}\), where \(H\) is the entropy of which member it actually collapsed into in simulations | A searcher with 7 targets that always fetches the same one is less flexible than it looks |
| Live options | From simulations: mean number of candidates with \(\text{sel} > 0\) at the start of our turn, and P(at least one goal-reaching instance is live) per turn | How often the deck has a real choice, and how often it has none |
| Disruption drop | \(P_\gamma\) against the league's disruption relations minus \(P_\gamma\) without them | Progress parked in fragile zones |

Flexibility counts only routes that are real. A route needs a supported or untested combo, completion above \(p_{\min}\), and cards with hard edges. Adding a thin one-of for a fourth route barely moves \(N_\gamma\) if its completion is low, and it lowers \(C\) by taking a slot, so the graph does not reward piling up techs.

**No single number.** C and F trade against each other in 60 cards: a linear deck buys consistency with redundancy of one route; a toolbox deck buys flexibility with many thin routes. The deck graph reports both. The spec's fate score \(S\) can combine them with preset or plan weights, and bounded fate search (flow 4.8) shows neighbours on the C–F plane and marks the Pareto front (no neighbour is better on both). A trainer picks a point on the front; the engine does not pick the style.

**Queries the graph answers**

- Why are these two cards linked? The printed sentence on the hard edge, plus the combos whose slots join them.
- Which routes reach `can_attack` in this 60, and which of its requirements has no route?

A goal is a board predicate, and it splits into requirements. `can_attack` is not "an attacker exists". It is: a body that can attack is in play, that body is in the Active Spot, and its printed cost is payable. Each requirement lists every legal route, including a rule (retreat) and a card this deck does not run. A missing route is a review gap, not a silent omission.

For `can_attack` the Active-Spot routes are the same `switches` relation on three sources: Switch (Item, free), Surfer (Supporter: switch, then draw until 5), and retreat (pay the printed retreat cost; an ability such as Lunar Zone can zero it). The energy routes are separate: one manual attach a turn, Energy Switch (move 1 Basic Energy), and any `moves_energy` or `transfer_charge` relation. Moon-Watching Party attaches to the benched Clefairy, so the fueled body is often not the Active one, and a switch route or Energy Switch is what makes that energy usable.
- What breaks if I cut this card? The goals whose cut sets contain it, and the new \(P_\gamma\).
- Which card in my pool adds a route to my weakest goal? A candidate for fate search.
- Which cards are in the 60 but on no route? Unused (soft) or junk (no hard edge).

**Export.** The deck graph serialises as `{nodes, edges}` JSON with the types above, so the same object feeds the API, a canvas view, and the lab report. Rendering: card nodes sized by copies and coloured by quality; hard edges solid, soft edges dashed with width by strength; combo nodes as diamonds; goal nodes on the right; load-bearing cards outlined.

### 3.12 Library, search, and sharing

Storage (database, not git):

| Table | Holds |
| --- | --- |
| `combos` | `id`, `version`, `owner_id`, `visibility`, `title`, `body_json`, `forked_from`, timestamps |
| `combo_refs` | parent `id@version` → child `id@version` |
| `combo_evidence` | combo `id@version`, context, simulation ids, paired difference and interval, computed strength and status |
| `combo_index` | per combo version: `catalog_id`, capability kinds, relation kinds, selector hashes, goal predicates |
| `plans` | `id`, `version`, `deck_id`, `deck_version`, `body_json` |

The relation graph is not stored per user. It is recomputed from the catalog and parser version and cached by that version.

Shipped combos and plans for seed decks live in operator git (`data/combos/*.json`) the way presets do.

Search:

- **By card**: which relations this printing takes part in, and which combos use it, directly or because a selector matches it.
- **By relation**: combos that use a `copies_attack` or `forces_active` relation.
- **By deck or pool**: which combos this 60 (or this trainer's collection) can run now, and near misses ("missing 1 Ledyba").
- **By capability or goal**: combos whose closer has `hand_count_times`, combos whose goal is `can_ko_active`.
- **By reference**: which combos include `cmb_bounce_host`.
- **By source**: combos mined from a deck, lab experiment, or self-play run.

Results rank by status and strength in the searcher's context, then by completion probability in the searcher's own deck. Refuted combos are shown last and labelled.

Sharing:

- **Export** is a bundle: the combo, every transitive ref pinned by version, its evidence summary, and for each literal pin its `catalog_id` plus a hash of the printed text.
- **Import** validates against the local catalog and parser. A printing that does not parse locally imports as `print_unresolved` and its line does not run. Imported evidence is shown but not trusted: strength is recomputed locally before the combo affects play.
- **Visibility**: private, household, public. **Fork** makes a new id with `forked_from`.

## 4. Flows

### 4.1 A new printing arrives

1. Scan or catalog import adds the printing.
2. The parser emits effects. If the sentence is new, add a parser branch and a test with the exact printed wording. This is the only code change in the whole design.
3. Capabilities and relations are derived. Existing selectors pick the card up: a new Basic joins every Nest Ball basis; a new Pokémon with a strong attack raises the value of every `copies_attack` relation that can reach it.
4. Existing combos can use the card where their selectors match. Their strength for the new card is untested until evidence arrives.

### 4.2 Mine combos from relations, decks, labs, and self-play

1. Input: the relation graph, saved decks, lab experiments with results, and self-play traces (section 5).
2. A candidate is a set of cards connected by relations that co-occurs with similar copy counts across decks, or appears as a repeated action sequence in winning traces.
3. Output is a **draft** combo with generalised selectors, `uses_relations`, a proposed `context`, and `derived_from`. Its status is `untested`.
4. A human names it, edits slots and line, and saves it. Mined combos are never auto-published or auto-bound to a deck.

### 4.3 Author or edit a combo (chat or UI)

1. Draft.
2. Validate: schema, selector vocabulary, relations used exist in print, decision ids, Observation predicates, acyclic refs, depth cap, copy caps under the active preset.
3. Dry-run on a chosen deck: resolved slot table, relation values, superposition bases, completion probability, contention.
4. Save as a new version. Share if wanted.

### 4.4 Test a combo (evidence)

1. Pick a deck that can run the combo and a league of opponents.
2. Run paired simulations: the same seeds with the combo's preference on and off.
3. Store the difference, interval, and simulation ids per context. Strength and status update.
4. A result that holds against some opponents and not others narrows `context` in a new version rather than averaging the two away.

### 4.5 Match a deck, optionally add a plan

1. Save the deck. Deck match runs and lists the candidates, each with its completion probability by turn and its status.
2. Optional: pin combos written for this deck, exclude candidates, set weights and priority clauses.
3. Save the plan version; the deck row points to it. Without a plan the deck plays its candidates with default weights.

### 4.6 Play and simulate

1. Load both seats' deck, candidates, and plan if any.
2. At each of our turns, board match scores the candidates and live instances, selects, and continues or abandons instances (section 3.9).
3. The kernel computes legal actions and asks `decide(ctx)`; Strategy scores against the live instances; every decision is logged with its instance id and whether it deviated.
4. Results include per-combo instance outcomes (section 3.10) next to the win rate, with the simulation id.

### 4.7 Lab experiment

1. A cell is (deck version, plan version, variant).
2. Variant operators: swap a card, change copies, swap a referenced combo for another with the same goal, change weights or priorities, turn one combo's preference off.
3. Results are stored with simulation ids and feed combo evidence.
4. **Lock** saves a new deck version and plan version. Promoting it into a shipped seed is an operator git step. No `SET_*_NAMES` edit or kernel branch is needed to lock a result.

### 4.8 Bounded fate search

Neighbour moves become relation- and combo-aware: add a card that fills a missing slot, cut an unused or junk card, raise a thin slot toward `target`, swap a sub-combo for an alternative with the same goal, add a target that raises a relation's value (a better attack for a copier), add a second route to a goal whose cut size is 1. \(\Delta S\) prunes; a capped Monte Carlo confirms. Each surviving neighbour is placed on the consistency–flexibility plane (section 3.11) with its deck graph diff: edges gained, edges lost, routes gained or broken.

### 4.9 Generate and read the graph

1. The catalog graph rebuilds when the catalog or the parser version changes. The library layer updates when a combo version or its evidence changes.
2. Saving a deck builds its deck graph: induced subgraph, copy counts, matched combos, reach and \(P_\gamma(t)\) from the draw-only sampler, cut sizes, versatility, superposition breadth.
3. Simulation adds the metrics that need play: live options per turn, effective basis size, disruption drop.
4. The graph is served as `{nodes, edges}` JSON with the deck version and the sampler seed, and rendered in the deck view. Chat and Lab answers about "why this card" or "what breaks if I cut it" cite graph nodes and edges, not memory.

### 4.10 Migrate off strategy names

1. **Inventory** the 100 `strat.name ==` branches. Classify each as:
   - a relation the parser does not yet expose (a parser gap),
   - combo or plan data (card roles, bench caps, orders of play), which starts as `untested` and is ported with the old lab results as its first evidence,
   - a missing Observation field or decision id the kernel must publish,
   - a generic heuristic that belongs in the objective scorer without a name.
2. **Port one deck at a time**: write its shipped plan and combos, then run a parity check on fixed seeds against its lab matrix. The ported plan must match the old strategy's win rates within a documented tolerance before its branches are deleted.
3. **Order**: `celebration` (one deck, self-contained), then `g`, then `party` (largest), then `phantom` and the rest.
4. During migration `StrategySpec.from_dict("party")` resolves to the shipped plan as an alias, so old lab cells keep running.

## 5. Self-play: tuning and learning the scorer

The engine gets stronger by playing itself, not by more branches. Three stages, each useful alone. None of them changes rules, printed effects, relations, or legality: a learner only writes plan weights, combo evidence, or a versioned model file, and only picks among `ctx.legal`.

### 5.1 Prerequisite

Every choice for the deck under training goes through `decide(ctx)`, and every number in the score is plan data (section 3.9). While a choice still lives in a `strat.name ==` branch, no tuner can reach it. Tuning before migration only measures how much the remaining floats matter.

### 5.2 Stage 1: tune plan weights by self-play

- **Parameters**: objective weights, \(w_{\text{plan}}\), \(w_{\text{keep}}\), combo priorities. Roughly 10–30 numbers per plan.
- **Opponents**: a league, not one deck: the household decks with their own plans, plus earlier versions of the plan being tuned. One fixed opponent teaches exploits of that opponent; two sides tuning in turn chase each other.
- **Search**: an evolution strategy (CMA-ES or a simpler \((\mu/\mu, \lambda)\) variant). Each generation samples \(\lambda\) weight vectors, plays each against the league, and moves the mean toward the best.
- **Noise control**: every candidate in a generation plays the same seeds (common random numbers). A result is accepted only after a re-run on held-out seeds shows a gain beyond the confidence interval. Policies that roll `rng` to decide (for example `bench_fill` today) shift later draws, so seed pairing reduces noise but does not remove it.
- **Budget**: the G30 array ran 21,000 games in 71.9 s on 7 processes (about 290 games/s). One candidate at 6 opponents × 2,000 games is about 40 s; a generation of 12 is about 8 minutes; 30 generations fit in one night.
- **Output**: a new plan version whose evidence is the simulation ids. A human locks it, as with lab locks today.

### 5.3 Stage 2: learn a value function

1. **Log** every `decide`: the features of the state after each legal action, and the final result.
2. **Features are name-free**: HP, damage, energy on board, prizes, hand size, relation values in play (fetch bases left, best attack a copier can reach), which combo slots are filled and which line patterns an action advances, the progress of each live combo instance and the zones its progress waits in, whether a superposition can still collapse into a missing slot. A feature like "is this Ledian" is a hardcoded name in disguise and does not transfer to a new deck.
3. **Model**: logistic regression or gradient-boosted trees first; a small MLP only if the simpler model plateaus. Combo features let the model learn how much each combo is worth in each position, which is the learned form of "best practice, not absolute".
4. **Decide**: for each legal action, apply it to a copy of the state and score the copy. The engine has no state clone today; this stage needs one.
5. **Loop**: games from the new scorer become training data for the next one. Repeated winning sequences over relations are proposed as draft combos (section 4.2).

### 5.4 Stage 3: search

Monte Carlo tree search over the learned value. Unlike chess, the opponent's hand, both prize piles, and deck order are hidden. Sample the hidden cards consistent with public information, search each sample, and average (information-set Monte Carlo tree search). This is the most expensive stage in Python and waits until stage 2 shows headroom.

### 5.5 Pilot before migration

`data/lab/celebration_weight_es.py` runs stage 1 on the seven `StrategySpec` floats of `celebration` against the household 60s. It answers one question: how much win rate is left in weights alone while the name branches still decide the rest.

Result (2026-09-23, [`data/lab/celebration-weight-es.md`](../../../data/lab/celebration-weight-es.md)): none. On held-out seeds at 3,000 games per foe, the tuned mean is −0.6 points against the defaults (95% CI −1.2 to 0.0). The training-time gains were selection noise, and a parameter with no effect on this deck drifted freely. Stage 1 needs the migration first.

## 6. Extension points

| New thing | Where it goes | Code change |
| --- | --- | --- |
| New card whose sentence already parses | catalog; relations recompute | none |
| New printed sentence | parser branch + exact-wording test | parser only |
| New capability kind → relation | fate-layer table keyed by effect kind | one row |
| New combo, plan, deck, or shared bundle | database (or `data/combos/` for shipped) | none |
| New evidence for a combo | `combo_evidence` from paired simulations | none |
| New selector attribute | selector vocabulary, versioned | small |
| New goal predicate or Observation field | Observation, versioned | small |
| New decision point | kernel publishes a hook-level id | versioned kernel |

No row says "new strategy name".

## 7. Worked examples

### 7.1 Nest Ball and Poké Pad in one 60

Nest Ball's print, "Search your deck for a Basic Pokémon and put it onto your Bench", parses to `call_family {count: 1}`: a `fetches` relation to `{"all": [{"category": "Pokemon"}, {"stage": "Basic"}]}` in the own deck. Its basis is every Basic in that list.

Poké Pad's print parses to `search_pokemon_no_rule_box`: a `fetches` relation to `{"all": [{"category": "Pokemon"}, {"rule_box": false}]}`. In C60 the `party` strategy description hand-lists this basis today ("Clefairy, Prankish Clefable, or Metronome Clefable … never Clefable ex / Mega / Mewtwo"). Under this design the basis is computed from print and the list, and the text goes away.

The two bases overlap on Clefairy. `shared_searchers` reports that the Party engine's Clefairy slot leans on both.

### 7.2 One copy relation, two combos

Mew ex's Memory Helix ("can use the attacks of any of your Benched Pokémon") parses to `copy_benched_attacks`: a `copies_attack` relation from Mew ex to every Pokémon with an attack on its own bench. The relation is the same in every deck. Two combos in the house use it differently:

- **Mew and babies** (strategy `mew_baby` today): bench 30 HP Baby Pokémon and copy their zero-cost attacks from the Active Mew ex, Igglybuff's Bouncy Circle for damage and Budew's Itchy Pollen for Item lock.
- **Mew and Celebration** (the Gholdengo pass in `data/lab/gholdengo-30-hand-combo.md`): Mew ex in the Active copies a benched Gholdengo's Celebration, with Metal Energy on Mew.

Neither combo is the relation's "right" use. Each is a best practice in its own list, with its own evidence and strength. A new Pokémon with a stronger attack raises the relation's value in any deck that can bench it, before anyone writes a combo for it.

Metronome Clefable ("choose 1 of your opponent's Active Pokémon's attacks and use it as this attack") parses to `copy_active_attack`: a `copies_attack` relation whose scope is the opponent's Active. Its value is set by the opponent's list, so it is measured against the league. The C60 plan's Boss-then-copy-Phantom-Dive line versus Dragapult is a combo with context `opponent_has_kind: bench_damage_counters`; against a deck without a strong Active attack the same relation is worth little, and the combo is out of context.

Metronome is **lethal** against any Pokémon whose own attack reaches its own HP. In the seed decks (2026-09-23, base printed damage against full printed HP, before weakness, resistance, and Tools), 8 of 101 Pokémon printings qualify:

| Pokémon | HP | Attack | Damage | Seed decks |
| --- | ---: | --- | ---: | --- |
| Staraptor | 150 | Power Blast | 180 | A, F, G |
| Dondozo | 160 | Hydro Splash | 180 | A |
| Pikachu | 60 | Volt Tackle | 70 | B, E, H |
| Zekrom | 130 | Raging Thunder | 130 | H |
| Walrein | 170 | Megaton Fall | 170 | B, E |
| Staravia | 80 | Speed Dive | 80 | A, F |
| Flutter Mane | 90 | Hex Hurl | 90 | A |
| Floragato | 90 | Slashing Claw | 90 | S, S60 |

This list is computed from print, not written into a combo. The combo on top of it is short: a `forces_active` relation (Boss's Orders, or Ledian's evolve trigger when the target has 90 HP or less remaining) brings a lethal target into the Active, then Metronome copies. Its goal is the lethal predicate; it does not name which Pokémon satisfy it. The same table, read from the other side, is the risk list for A, F, and G's Staraptor line against any deck that runs Metronome.

Today `_copy_would_ko` in `game.py` already resolves copied damage from the copier's side, but it is reached through `card.name.lower() == "clefable"`. After migration the same computation hangs off the `copies_attack` relation, so any future printing with the same sentence gets it.

### 7.3 One bounce combo, two decks

`cmb_bounce_host` (section 3.6) is referenced by:

- **Hand Fling loop** (Unlimited 60). Binds `bouncer` to Lopunny FLF Big Jump (`return_self_to_hand`) and `host` to the Buneary → Lopunny line. It also references `cmb_special_energy_spam` (slot: `has_kind: attach_special_energy_from_hand`, Porygon-Z Crazy Code), `cmb_same_turn_evolve` (Broken Time-Space), and a closer slot `{"attack": {"has_kind": "hand_count_times"}}` (Ambipom Hand Fling). Goal `can_ko_active`, line `repeat: "until_goal"`, `keep`: Enriching Energy returns to hand with the host, not to the discard.
- **C60 return package**. Binds `bouncer` to Supporters with `return_pokemon_to_hand` (Penny, Professor Turo's Scenario, Mr. Briney's Compassion, Seeker) and `host` to a damaged Clefairy line. Goal: replay at full HP and use Moon-Watching Party again.

The same combo, the same scorer, different bindings. `_party_bounce_combo`'s fixed order becomes priority clauses on the C60 plan.

The C60 return package is also a worked case of "not absolute". The 2026-09-22 bounce matrix (`data/lab/set-c60-bounce-combo.md`) measured Penny counts against the cage list. Vs T60: 68.8% at 0 copies, 66.3% at 1, 63.5% at 2, 58.3% at 4, with the same staircase on Hedrick and D60. The full live package (2 Penny, Turo, Briney, Seeker) was below the cage list against every foe, including G (70.1% against 71.9%). But a single Penny in Iono's slot scored 74.5% against G. As evidence, the five-card package is `refuted` in C60 against that league; a one-copy version with context "vs G" is a separate, narrower claim worth testing. Meanwhile the Hand Fling loop is built on the same `cmb_bounce_host`. One relation, one combo, different decks and contexts, different statuses.

### 7.4 Party engine and the gust slot

- `cmb_party_engine`: Clefairy bodies (slot `name: Clefairy`, copies up to cap), Moon-Watching Party (`attach_energy_from_deck_per_benched`, full deck, one Psychic Energy per benched Clefairy, no look-N), Nest Ball superposition into the Clefairy slot, a Basic Psychic Energy supply slot.
- `cmb_gust`: one slot with any `forces_active` relation. Ledian's Glittering Star Pattern already parses to `gust_low_hp_on_evolve {max_remaining: 90}`, so the Ledyba → Ledian line fills it with dependence on Ledyba bodies. Boss's Orders fills the same slot once its Trainer program exposes the same capability.
- The Mega Clefable ex plan for Carpet Set G references both and sets priorities. The epic's "cut which card for Mega Clefable ex" question becomes: which cut breaks or thins which slot of which referenced combo, and how strong those combos are in G's context.

### 7.5 Gust, Seeker, knock out: winning on an empty board

Three relations and one rule:

1. `forces_active` (Ledian's Glittering Star Pattern, we choose): an opponent's Benched Pokémon with 90 HP or less remaining comes to the Active; their old Active goes to the Bench.
2. `returns_to_hand` (Seeker, each player chooses their own, we return first).
3. An attack that knocks out the new Active.
4. Rule: a player with no Pokémon in play loses, whatever the prize count.

The combo `cmb_bench_out` has a line of gust → Seeker → attack and the goal `opponent_no_pokemon_after_ko`. Its context is an Observation condition: the opponent has **exactly one** Benched Pokémon, it has 90 HP or less remaining, and our Active can knock it out. Then the gust swaps it in, Seeker's opponent-side choice is forced onto their old Active, the bench is empty, and the knockout wins the game. Without Ledian the same combo needs the opponent's current Active to be knocked out directly; the gust widens the condition to "the Active is too big, but the only Benched Pokémon is small".

Seeker also makes us return one of our own Benched Pokémon first. `bounce.which` can pick our evolved Ledian: Ledyba and Ledian return to hand, and replaying Ledyba then evolving next turn is another Glittering Star Pattern. That is `cmb_bounce_host` bound to the Ledyba → Ledian line, referenced from `cmb_bench_out`.

Today the pieces exist but do not meet. `_seeker_wipe_pending` (Seeker when the opponent has exactly one Benched Pokémon and the Active KO still lands) is reached only from `_party_bounce_combo`, so only strategy `party` plays it. `_gust_low_hp_bench` picks Ledian's target by prize count and a hardcoded list of "snack" names, not by whether the gust sets up a bench-out. After migration, `gust.which` is scored by the plan, and a gust that makes `opponent_no_pokemon_after_ko` reachable this turn outscores any prize-count pick.

### 7.6 Discard fuel now, recover it later: a combo across turns

Printed text (Mewtwo ex `sv04-058`, 230 HP; in this catalog Transfer Charge is an **attack**, not an Ability):

- Ultra Ball: "Discard 2 cards from your hand. Search your deck for a Pokémon."
- Transfer Charge [P], 0 damage: "Attach up to 2 Basic Psychic Energy cards from your discard pile to your Pokémon in any way you like."
- Photon Kinesis [P][P]: 10 damage plus 30 for each Psychic Energy attached to all of your Pokémon.

Relations: Ultra Ball `fetches` any Pokémon (Mewtwo ex is in its basis); Ultra Ball's cost **produces** into our discard (`discard.which`); Transfer Charge **consumes** Basic Psychic Energy from our discard (`attach.distribute`); Photon Kinesis scales with Psychic Energy in play. The combo is the choice that makes these line up: pay Ultra Ball's cost with Energy on purpose.

```json
{
  "id": "cmb_discard_fuel",
  "version": 1,
  "title": "Discard fuel, recover it with an attack",
  "params": {
    "payer": {"selector": {"has_kind": "discard_from_hand_cost"}},
    "recoverer": {"selector": {"attack": {"has_kind": "transfer_charge"}}},
    "fuel": {"selector": {"all": [{"basic_energy": true}, {"energy_type": "Psychic"}]}}
  },
  "parts": [
    {"slot": "payer", "selector": {"param": "payer"}, "copies": {"min": 1}},
    {"slot": "recoverer", "selector": {"param": "recoverer"}, "copies": {"min": 1}},
    {"slot": "fuel", "selector": {"param": "fuel"}, "copies": {"min": 2}}
  ],
  "uses_relations": [{"kind": "zone_feed", "zone": "own_discard", "from": "payer", "to": "recoverer", "cards": "fuel"}],
  "horizon": 3,
  "line": [
    {"prefer": {"decision": "discard.which", "source": {"slot": "payer"}, "card": {"slot": "fuel"}, "count": 2}},
    {"prefer": {"decision": "game.attack", "source": {"slot": "recoverer"}, "kind": "transfer_charge"}, "after": [0]},
    {"prefer": {"decision": "attach.distribute", "card": {"slot": "fuel"}, "target": {"slot": "recoverer"}}, "after": [1]}
  ],
  "goal": {"observe": "energy_ready", "slot": "recoverer", "attack": "strongest"},
  "keep": [{"zone": "own_discard", "slot": "fuel", "until_pattern": 1}]
}
```

The combo names no card. Any Pokémon whose printed attack parses to `transfer_charge` fills `recoverer`, and any card with a discard-from-hand cost fills `payer`. The closer (Photon Kinesis) belongs to a parent combo that references this one; the fuel combo only promises Energy on the board.

One game, going first:

| Our turn | Board match | Instance after the turn |
| --- | --- | --- |
| 1 | Ultra Ball and 2 Basic Psychic Energy in hand; Mewtwo ex in deck (in Ultra Ball's basis). \(P\) is high; \(C\) is 2 Energy that are not lost, only parked. Selected. `discard.which` picks the 2 Psychic; `search.which` collapses Ultra Ball into Mewtwo ex; it goes to the Bench. No attack on turn 1. | `done: [0]`, fuel bound to the 2 discarded cards, Mewtwo bound. Fuel sits in the discard: durable. Mewtwo on the Bench: exposed to bench damage and gust. |
| Opponent | They attack our Active; Mewtwo survives. | Unchanged. |
| 2 | Re-scored: fuel is already in the discard, so \(P\) is higher than on turn 1. Continue. Retreat or switch Mewtwo to the Active, attach 1 Psychic from hand, attack with Transfer Charge; `attach.distribute` puts both on Mewtwo. | `done: [0, 1, 2]`; goal holds (3 Energy on Mewtwo). `completed`. |
| 3 | The parent combo's closer: Photon Kinesis for 10 + 30 × Psychic in play. | — |

If the opponent knocks out the benched Mewtwo on their turn, the `recoverer` binding breaks. A second Mewtwo ex in hand or in the deck rebinds it and the instance stays active, with the fuel still waiting in the discard; with none left, the instance is `broken` and the log records the knockout as the reason. If Energy Retrieval would pull the fuel back into hand before Transfer Charge runs, the `keep` rule makes that action score lower, because it moves progress from a durable zone into the hand.

One parser gap first: the kernel resolves Ultra Ball by name (`elif name == "ultra ball"` in `game.py`), and no trainer effect kind describes its cost. `payer` needs a trainer parser branch that emits `discard_from_hand_cost {count: 2}` from "Discard 2 cards from your hand.", with a test on that exact wording. Until then the combo validates as `print_unresolved` on the payer slot.

Today the engine cannot play this line on purpose. `_discard_for_ultra_ball` scores discards by card name: outside a `strat.name == "g"` branch, every Energy card gets a small penalty, so it avoids discarding Psychic fuel. `_transfer_charge` picks its target through `_main_mewtwo`, by name. Nothing remembers across turns that the discard was deliberate. After migration, `discard.which` is scored against the live instance, and the step memory is the instance record, not a strategy flag.

## 8. Out of scope

- Combos adding effects, look sizes, attach counts, or search widths. Lines only prefer among legal actions.
- Combos as hard constraints. A combo never forbids a legal action and never overrides a relation.
- Win rates typed into a combo. Evidence is a link to a simulation id; strength is computed.
- Python inside combos or plans. Customers still never write `app/`, `tests/`, or shipped `data/lab/`.
- Auto-publishing mined combos or auto-binding them to a deck.
- Claiming a global optimum deck.

## 9. Open questions for the operator

1. **Epic placement.** Deleting the strategy-name branches is decided (2026-09-23). Still open: the deck-as-fate spec currently says Choice and Decision are unchanged and `game.py` gains nothing. Relations, combo modelling, superposition, and combo search can stay in that spec; plan-driven `decide` plus the migration may be the same epic or a sibling. The work happens either way.
2. **Share scope.** Household only, or public?
3. **One plan per deck, or several?** Proposal: one plan with matchup priority clauses.
4. **Strength formula.** Proposal: lower end of the 95% interval on the paired difference, shrunk toward 0 below a minimum game count. The minimum count is open.
5. **Parity tolerance** for deleting a ported strategy's branches (proposal: within the 95% interval of the old lab matrix at the same seed and game count).
6. **Live instances at once.** Proposal: at most one primary and two small non-conflicting instances per player, with the abandon margin \(m\) as a plan weight that self-play tunes.
7. **Default thresholds for flexibility.** \(p_{\min}\) (proposal 0.3) and target turns \(t_\gamma\) per goal (proposal: setup goals turn 2, `can_ko_active` turn 3) per rule preset, and whether \(S\) combines C and F by default or only shows the front.
8. **Spec update.** The spec's deck knowledge graph has print edges only. Adding the combo layer, C and F, and the graph export is a spec change for the operator to accept.
