# Deck as fate

Status: draft

GitHub Issue: TBD

## Problem And Value

Combo Cub already answers “how often does this name appear in N cards?” and “who wins 10,000 games?” Those tools measure **luck after the list is frozen**: random draws, mulligans, and the opponent’s line. They do not yet treat the **60-card list itself** as the main object of design.

The operator’s claim (keep this wording as the outcome, not as engine flavor text):

- In a 60-card deck the most important job is **reducing uncertainty**.
- The **4-of-a-name** rule puts a **probability ceiling** on any one card.
- Cards with search, draw, attach, and evolve links form a **network**. In a game that network is how you keep converting the next unknown card into a known setup.
- There really are **good cards and bad cards**. Same energy cost can print **50 damage or 100**. A card with **no links to other cards** is junk for list-building: it does not sit on the graph.
- That network is a **Knowledge Graph (KG)**: nodes are printings (stats, costs, roles); edges are printed links. **Building the 60 uses the KG** — pick efficient, connected nodes; do not fill slots with isolated weak printings.
- Anything still unknown is potential risk. The same expected output with **less uncertainty is strictly better**.
- The 60 cards are **fate (命)**. Draws and the opponent’s board are **luck (运)**. Raising win rate is first **changing fate** — designing the list — not guessing better on the table.
- The catalog is large, but a 60-card list under format rules is a **finite** space. A **relatively optimal** list can be searched; a unique global optimum need not be claimed.

**Value:** trainers (and the household operator) can compare and search lists on *how much of the game is still a guess*, on **print-derived card quality**, and on **whether a card is actually in the graph**. Chat and Lab should talk about copy ceilings, KG edges, isolated junk, and variance — without inventing numbers, tier-list vibes, or turning this philosophy into printed card text.

Today `/api/probability` is hypergeometric on a **single name**. Monte Carlo is matchup luck. Trade search is a one-for-one household swap. Catalog rows have HP and attacks, but nothing scores **damage per energy** against **graph degree**. None of that is “this 60 is a tighter, higher-quality KG than that 60.”

## Scope

Format of record: **Standard 60 cards, 4 of a name (`s60`)**. The same measurements should reuse `GET /api/rule-presets` so 30-card Family Cup lists can be scored with their own size and copy cap; do not hardcode 60 or 4 in `app/engine/game.py`.

### Fate vs luck (vocabulary)

| Term | Meaning in product | Not this |
| --- | --- | --- |
| Fate / 命 | The frozen list: names, copy counts, roles, and legal links between cards | A new rules engine, a look-N, or a lab note that overrides print |
| Luck / 运 | Shuffle, opening hand, prize order, opponent’s list and decisions | Something the deck builder “solves away” |
| Copy ceiling | Hypergeometric (and sequential-draw) upper bound given copies ≤ format max | A guarantee the card is in hand |
| Network / KG | Directed **Knowledge Graph**: nodes = printings (and roles); edges = printed search/draw/attach/evolve/energy-pay links | A strategy comment, Limitless scrape, or operator memory of “top 6” |
| Node quality | Printed efficiency: attack damage vs energy cost, HP, prize count, and roles the parse already exposes | A human “tier list” or chat opinion with no catalog numbers |
| Isolated / junk | A candidate with **no named or role link** to other cards in the pool or the current 60 (no evolve line, no tutor/search partner, no printed “this card / that card” combo). Paying generic Basic Energy of its type is **not** enough to stop being junk | A one-of tech the trainer **chooses** to keep after the KG flags it |
| Uncertainty | Residual chance a needed node is missing, a chain breaks, or two lines with similar mean prize/damage differ in spread | A vibe; a made-up win rate |

### What to build (outcome, not slice list)

- **Copy-ceiling report** for a saved deck under the active rules: for each name (and for named *roles* such as “Basic Energy of type T”, “search that finds Energy”), show copies, legal max, P(at least one) for documented draws (opening hand, plus optional extra draw counts from **printed** draw cards if those cards are in the list). Single-name `/api/probability` remains valid; this epic wraps it for a whole list.
- **Knowledge Graph** from catalog + printed effect parse (the network, named as a KG so deck search can query it):
  - **Nodes:** a printing (set + number or stable catalog id), with attributes taken from the card: type, HP, stage, attacks (damage, energy cost), abilities, trainer/energy class, prize count under active rules.
  - **Edges:** only when printed text (or engine-parse of that text) can fetch, attach, evolve into, or pay for the target. Missing print → no edge. Lab markdown, chat memory, and this spec must not add edges.
  - **Node quality:** comparable printings (same energy cost for an attack, or same role) must be rankable from those attributes — e.g. 100 damage vs 50 damage at the same cost is a real quality gap, not a vibe.
  - **Isolated / junk:** unlabeled if the only edges are generic energy-pay. Junk = no evolve line, no tutor/search that finds this card or its role, no printed partner with another node in the pool/60. List-building default is **do not add junk**; the trainer may override a flagged one-of.
- **Uncertainty score** for a list (and optionally a matchup): brick/chain-break rates, variance of a documented output (prizes taken, energy attached by turn N, “can attack with named attack”), not only the mean. Ranking rule: if two lists have statistically similar mean output, **prefer the lower-uncertainty one**.
- **Bounded fate search on the KG**: neighborhood search (copy tweaks within the 4-of cap, one-for-one swaps from the trainer’s scanned pool or a documented seed catalog), not exhaustive C(catalog, 60). Neighbors should prefer **higher node quality** and **higher connectivity** (replace isolated 50-damage attackers with linked 100-damage ones when print and the copy cap allow). Output is a **relatively better** list plus why (ceiling, missing edge, junk isolation, quality delta, variance), with Monte Carlo used to estimate luck *after* the candidate fate is chosen.
- **Coach/Lab language**: answers about “why this 60?” or “is this card junk?” must cite the in-process KG/report (ceilings, node attributes, edges, isolation, uncertainty, sim id). Never invent a win rate, a look size, or a tier without numbers.

Printed card text still wins. A new tutor ability still needs a parser branch and a test with the exact printed sentence. Clefairy LOR 62 remains a full-deck search (one Psychic Energy per benched Clefairy), not a top-N look.

## Non-Goals

- Enumerating every legal 60-card combination from the full catalog, or claiming a unique global optimum.
- Encoding this philosophy as match rules, look-N, attach counts, or search widths in `app/engine/game.py`.
- Letting lab notes, strategy comments, or this spec attach, search, or look-N.
- Replacing Monte Carlo matchups or `StrategySpec` play; those remain luck-and-decision tools once fate is fixed.
- Auto-writing the operator’s git `data/lab/` or promoting a searched list into shipped seeds without a human.
- Changing Family Cup defaults (30-card presets) or prize counts.
- A general-purpose solver that ignores the 4-of (or preset copy) cap.
- An external or community Knowledge Graph (Limitless, Reddit, operator memory) as the source of edges or “good/bad.” Our KG is catalog + printed parse only.
- A handwritten global tier list in git. Quality is computed from print (and graph degree), then shown; humans may disagree and keep a flagged card.
- Customer or product-chat writes to `app/`, `tests/`, or shipped `data/lab/` (still `open-trainer-labs`).

## Acceptance Gates

Define where acceptance must be verified before dispatch continues or the epic can close. Tag each gate with **consumer** (who experiences the output) and **verifier** (who may sign off).

- **consumer:** `human` (UI/UX), `agent` (API/dispatch consumers), or `both`
- **verifier:** `agent-auto`, `agent-then-human`, or `human-required`

Child feature slugs are **not** named here. After this spec is stable, run `create-features-for-epic` and fill **After features** on each gate. Human: edit verify steps if the shipped endpoints differ.

### Milestone: `copy-ceilings`

- **After features:** (breakdown)
- **Consumer:** `agent`
- **Verifier:** `agent-auto`
- **Verify:**
  - For a documented `s60` fixture list, an in-process API or lab tool returns per-name copy count, format copy cap (4 under `s60`), and hypergeometric P(at least one) for opening hand size from the active rules — matching the existing `draw_probability` math, not a new invented formula.
  - A name at 4 copies shows a higher ceiling than the same name at 1 copy; a name at 0 copies is absent or P=0.
  - The response does not hardcode deck size 60 or cap 4 when the active preset is a 30-card rule; those numbers come from rules.
- **Blocks dispatch until passed:** yes — do not rank lists until ceilings are real numbers from the engine.

### Milestone: `network-from-print`

- **After features:** (breakdown)
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - For a fixture that includes Clefairy LOR 62 Moon-Watching Party, the KG records a **full-deck** Energy search edge (one Psychic Energy per benched Clefairy), not a look-6 or look-N invented here.
  - An edge exists only when printed parse supports it; a card with no search/draw/tutor text does not gain a tutor edge from this spec or from `data/lab/*.md`.
  - Human: on `http://127.0.0.1:8000`, a trainer can see or ask why two cards are linked and the answer cites print, not a lab story.
- **Blocks dispatch until passed:** yes — do not search “better networks” until edges are print-derived.

### Milestone: `kg-card-quality`

- **After features:** (breakdown)
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - A documented pair of Pokémon printings that share the same attack energy cost (fixture: one attack dealing 50, one dealing 100, or the closest shipped catalog pair) receive node attributes from the catalog; the 100-damage printing ranks as the higher-quality attacker on that cost, without a hardcoded name table in `game.py`.
  - A documented printing with **no** named/role KG links to any other card in a small fixture pool is labeled isolated/junk even if it can attach generic Basic Energy of its type; a printing on an evolve line or with a printed tutor/partner is not.
  - Chat/Lab “is this a junk card?” cites those attributes and degree, not an invented tier.
  - Human: on `http://127.0.0.1:8000`, the good/bad explanation is readable (cost, damage, links). Mark for human edit if the surface is chat-only.
- **Blocks dispatch until passed:** yes — do not swap cards in fate search until quality and isolation are computed from print + KG.

### Milestone: `prefer-less-uncertainty`

- **After features:** (breakdown)
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - A documented pair of lists (same format, similar mean on a named output in a capped Monte Carlo) is ranked; the higher-variance / higher brick-or-chain-break list is not preferred when means are within a documented tolerance.
  - Chat/Lab must not invent the means or variances; they come from the tool/simulation id.
  - Human: the ranking explanation is readable (ceiling, broken chain, variance), not a raw matrix dump. Mark this step for human edit if the UI surface is Fight vs Lab vs chat only.
- **Blocks dispatch until passed:** yes

### Milestone: `bounded-fate-search`

- **After features:** (breakdown)
- **Consumer:** `both`
- **Verifier:** `agent-then-human`
- **Verify:**
  - A search from a documented seed `s60` list plus a bounded pool (trainer set or fixture catalog) returns at least one neighbor that respects the copy cap and 60-card size, with a written reason (ceiling, KG edge, isolation/junk, node quality, or uncertainty).
  - When the pool contains a higher-quality linked substitute for an isolated weaker attacker (same role / comparable energy cost), the search prefers that swap over keeping the junk node (unless the trainer locked the junk card).
  - The search does not enumerate the full catalog combinatorially; a documented budget (candidates × games) is respected.
  - Human: the suggested list is a **relative** improvement, labeled as such, not “the best 60 in the game.”
- **Blocks dispatch until passed:** yes — do not advertise “optimal deck” until this gate’s labeling is signed.

### Epic exit

- **After features:** all child features done
- **Consumer:** `human`
- **Verifier:** `human-required`
- **Verify:** On `http://127.0.0.1:8000`, with rule preset `s60`, a trainer (or operator) can: load or scan a 60, see copy ceilings, see KG links and isolated/junk flags, see why one printing is stronger than another at the same energy cost, compare two neighbors, and accept or reject a bounded search suggestion. A 10k-game (or capped) matchup is still available as **luck given that fate**. Human confirms no look-N was hardcoded into `game.py` from this epic. Human may edit this checklist if the shipped UI tab differs.
- **Blocks epic `done`:** yes

## Epic Validation

- Fate is the list; luck is the shuffle and the opponent. Product copy should not collapse those.
- Same expected output, less uncertainty, is the ranking tie-break — not a license to ignore mean win rate when means differ.
- Finite space ≠ we will brute-force it. Relatively optimal means bounded search + human lock.
- Printed parse is the only source of KG edges. Node quality is catalog math (damage, cost, HP, prizes, degree), not a vibe. Operator chat in this epic is intent, not a card ruling.
- Isolated/junk is a default against filling the 60 with unlinked cards; it is not a ban on a human-locked tech.
- Reuse rule presets and existing hypergeometric helpers; do not fork a second probability story.
- Isolation and “customers cannot change repo code” from `open-trainer-labs` still apply.

## Status Update Checklist

When the epic changes state, update the linked tracker with:

- current epic state,
- gate pass/fail notes,
- child feature progress summary,
- blockers,
- next human or agent action.
