---
name: greed
description: Run a one-card greedy search on a 60-card list. Each comparison is 400 games per seat on one shared seed, 30-card decks are left out, and every kept win-rate change gets a written reason from the printed text, the foe table, the effect counters, and the end reasons. Use when the user invokes /greed, asks for a greedy swap, or wants to try cards one copy at a time.
---

# Greed

Measure one copy in and one copy out. Keep the swap only when its Sisters-weighted win rate is higher than the list already kept. Record the sample. Do not edit a locked list.

Follow the one-card loop in `data/lab/set_mill_hilda.py` and `data/lab/set-mill-hilda.md`: same shape of path, both seats, and the same standard-error formula. `data/lab/set_igglybuff_greedy.py` is that loop on a second list. `data/lab/set_doll_losses.py` supplies the end-reason buckets. `data/lab/set-mill-sleep.md` supplies the frozen Sisters weights. `data/lab/set_mill_doll.py` screens at 40 games and confirms at 120. This skill measures every cut at 400 and leaves that screen unused.

## Before measuring

Read those labs. Then name three things, and stop if any one is missing:

- The starting list. A locked `SET_*_NAMES` of 60 cards, or a 60 the user wrote down. A 30-card list is not a start.
- The card coming in, or the exact pair when the user already chose both the card that comes in and the card that leaves.
- The subject's strategy name. Use the strategy that already plays this list. Do not add a `strat.name ==` branch, and do not hardcode a look size into `app/engine/game.py`.

If the engine does not execute the printed sentence of the card coming in, stop before the first game. A win rate from an ignored sentence is not a result. A new sentence needs a parser branch and a test that uses the exact printed wording. That work is not this search.

Quote the printed sentence from the catalog or the card text. A lab note, a memory of the line, or a strategy comment does not choose the cut.

## No 30-card decks

Neither seat is a 30-card list, and the rules are `standard_60_rules()` (60 cards, 6 prizes, 4 of a name except basic Energy). Leave out every 30-card preset, including Carpet Sets A, B, C, D, S, and T, `SET_G30_NAMES`, seed-g30, and Ambipom Hand Fling. Do not call `build_g30_deck()`. Do not import the `g30` row from an older lab script. Those scripts still contain it; this search deletes that row instead of copying the tuple.

The foe field is these twelve 60s, with the strategy each older lab already uses:

| Key | List | Names | Strategy |
| :--- | :--- | :--- | :--- |
| t60 | Dragapult ex (T60) | `SET_T60_NAMES` | phantom |
| hedrick | Hedrick Worlds Dragapult | `SET_T_META_NAMES` | phantom |
| unl | Unlimited Dragapult | `SET_T_UNL_NAMES` | phantom |
| d60 | Cornerstone Ogerpon (D60) | `SET_D60_NAMES` | demolish |
| s60 | Wo-Chien / Floragato (S60) | `SET_S60_NAMES` | slash |
| g | Gholdengo (G) | `SET_G_NAMES` | g |
| c60 | Clefairy / Mewtwo (C60) | `SET_C60_NAMES` | party |
| m | Set M (Mew ex) | `SET_M60_NAMES` | mew_baby |
| starmie | Mega Starmie ex (Kudo) | `SET_STARMIE60_NAMES` | starmie |
| lucario | Lucario Hariyama | `SET_L60_NAMES` | aura |
| thorns | Iron Thorns ex | `IRON_THORNS_NAMES` | thorns |
| h | Carpet Set H | `SET_H_NAMES` | nuzzle |

Build each foe with `build_fallback_deck`. Check `len(cards) == 60` for the subject and for every foe before the first game.

## Weights

Use the frozen Sisters loss weights from `data/lab/set-mill-sleep.md`, and drop g30's 1.1%. The raw numbers are:

| t60 | hedrick | unl | d60 | s60 | g | c60 | m | starmie | lucario | thorns | h |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.040 | 0.051 | 0.022 | 0.145 | 0.070 | 0.117 | 0.124 | 0.145 | 0.106 | 0.051 | 0.041 | 0.076 |

Divide each raw number by the sum of these twelve. Do that division in the script. Do not type a pre-rounded weight into the score. If the user removes another foe, drop that foe's raw number, divide by the new sum, and write which foe left. Do not invent a new weight.

A foe cell is the mean of the two seats. The score is the weighted sum of those twelve cells. Also report the unweighted mean and the worst foe.

The standard error of a list is the same formula as Hilda. For each foe, each seat contributes `p * (1 - p) / 400`, the two seats are averaged, and the foe variances combine with the squared weights:

```text
variance += weight^2 * (seat_var_a + seat_var_b) / 4
se = sqrt(variance)
gap_se = sqrt(se_before^2 + se_after^2)
```

Report a gap as the rate difference and as `gap / gap_se` combined standard errors.

## One seed, 400 games

One comparison is one list, one foe, and one seat, and that cell is 400 games. The other seat is its own 400, from the same seed. A 20-game or 40-game run is a smoke. Label it smoke, and leave it out of the keep rule.

One integer seed covers the whole search: the baseline, every cut, both seats, and every later copy. Write that integer into the script before the first game. If the user names a seed, use it. If they do not, use a `YYYYMMDD` integer and do not change it later.

Each cell starts with `random.Random(SEED)` and then plays its 400 games on that generator, as `set_mill_hilda.py` does. Do not add the foe index, the seat, or the step to the seed. Do not continue one generator from one foe into the next. Two lists still diverge after the first choice that consumes a different number of random draws. Say that in the note. Do not claim the streams stayed identical.

The cache key is `seed|400|seat|foe|full list`. A cell from another seed, another game count, or a 30-card foe is not reusable. Append each finished cell to a partial jsonl and resume from it.

## One card at a time

Three requests use this same measurement:

- A named swap. The user chose the card coming in and the card leaving. Measure that one list against the starting list.
- A greedy search on one incoming card. Each step tries every other name still in the list as the one copy to cut. Keep the cut with the higher weighted rate, then try the next copy the same way.
- A sequence of named swaps. Apply them one copy at a time. Each one is measured against the list kept so far, on the same seed.

A step removes one copy and appends one copy. The list stays 60 cards. `copy_violations` against `standard_60_rules()` must be empty. Stop adding at 4 of the incoming name. Basic Energy keeps the printed exception to that cap. Skip a cut that is not in the list.

Every other name is a legal cut, unless the user named cards that stay. Do not copy the Doll `PROTECT` set on your own. Do not cut the incoming card below the count this step is building.

Sort the step by weighted rate, then worst foe, then how many copies the cut had before, then the name. Keep the first row only when its weighted rate is strictly higher than the list already kept. An equal rate does not keep. Stop when this step has no such row, or at 4 copies.

Write the json and the markdown after every step, with `complete` still false until the search stops.

The step keeps the best cut on this seed, so that gain sits a little high. Say so in the decision. A second seed is a holdout, and only when the user asks. The holdout is still 400 games, the same twelve foes, and a new seed. Label it holdout. It does not replace the search seed, and it does not choose a different cut.

## Why the rate moved

Write the reason in prose beside the path table. After each kept step, and in the decision, that prose uses only the measurements below. For a named swap, write it for that swap. Also write it for any other cut in the same step whose weighted move is at least one combined standard error, so a cut that lost for a different reason is visible.

Each reason has these parts, in this order:

1. The printed sentence of the card that came in, and the printed sentence of the card that left. Quote the text the engine parsed.
2. The weighted delta, both standard errors, the combined standard error, and the ratio.
3. The foes that carry the move. For each foe, contribution is `weight * (new cell − old cell)`. Name the largest contributions in both directions. A foe that did not move does not explain the rate.
4. The counters for those two sentences, before and after, on the same weights. Use the event key the engine already bumps for that sentence (`event_sum` or the key passed to `_bump`). Count how often the sentence resolved, and how often the line it feeds resolved: the attack, the mill, the search, the evolve. If the engine bumps no event for that sentence, say the sample has no counter for it. Do not invent a rate, and do not add a look size to `app/engine/game.py` to manufacture one.
5. The end reasons, tallied for all 400 games from the subject's seat. Use the buckets in `set_doll_losses.py` `_kind`, read from `GameResult.reason`:

| Bucket | `GameResult.reason` |
| :--- | :--- |
| prizes | `took all prize cards` |
| empty / foe empty | `opponent has no Pokémon in play` |
| decked / foe decked | `{seat} decked out` |
| no basic / foe no basic | `{seat} had no Basic Pokémon` or `had no playable Pokémon` |
| turn prizes | `more prizes at turn limit` |
| turn hp | `more remaining HP at turn limit` |
| tie | `turn limit` |

Weight those shares the same way as the win rate. Report the change. A rise that is the opponent decking out is a different reason from a rise that is taking all six Prizes, or from a loss that is an empty board.

6. One sentence that ties the printed text to the foes and the end reasons that actually moved. If the counters did not move, say the sample does not show that sentence firing. If the counters moved and the win rate did not, say that too. The counters and the reasons win over the story.

The six sample traces from `run_simulation` are not this tally. Count every game in the cell. Hilda's worker already loops `play_game`; add the reason buckets and the sentence counters there.

## What to write

Write three files under `data/lab/`:

- `<slug>.py` runs the search.
- `<slug>.json` stores the seed, the games, the raw weights, the renormalized weights, the path, the rounds, the best list, and `complete`.
- `<slug>.md` is the note a person reads.

The note starts the way `data/lab/set-mill-hilda.md` starts: what one step does, the printed sentence, the seed, 400 games per seat, both seats, the weights with g30 left out, and the elapsed time. Then the path table (step, copies, cut, weighted, standard error, mean, worst, delta, and the sentence counters), the decision, the counts, each step's full cut table, the reason paragraphs, and the foe table at the kept list (A, B, mean, delta against the start).

The script records the sample. It does not assign `SET_*_NAMES` and it does not change a lock. Say that in the note.

## Done

The search is done when the note has the path, the kept or rejected decision, the foe table, and a reason paragraph for every kept step that cites the printed sentences, the weighted contributions, the counters, and the end-reason mix. The same seed and 400 games appear on every row. No 30-card deck appears in a seat, a weight, or a table.
