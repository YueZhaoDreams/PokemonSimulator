---
name: greedy
description: Run a one-card greedy search on a 60-card list. Every current 60-card deck that is not archived is a foe, each cell is 400 games on one shared seed, weights are the 0-copy loss rates, and a higher copy count can gain more than a lower one. Each kept win-rate change gets a written reason from the printed text, the foe table, the effect counters, and the end reasons. Use when the user invokes /greedy, asks for a greedy swap, or wants to try cards one copy at a time.
---

# Greedy

Measure one copy in and one copy out. Record every count up to the cap, then keep the count whose gain over the starting list is the largest. A later count can raise the rate by more than an earlier count. Record the sample. Do not edit a locked list.

Follow the one-card loop in `data/lab/set_mill_hilda.py` and `data/lab/set-mill-hilda.md`: same shape of path, both seats, and the same standard-error formula. `data/lab/set_igglybuff_greedy.py` is that loop on a second list. `data/lab/set_doll_losses.py` supplies the end-reason buckets. `data/lab/set-mill-sleep.md` is one past weight vector, not the vector for this run. `data/lab/set_mill_doll.py` screens at 40 games and confirms at 120. This skill measures every cut at 400 and leaves that screen unused. Those older scripts also stop when the next copy fails to beat the list already kept, and they play a fixed foe list. This skill does neither.

## Before measuring

Read those labs. Then name three things, and stop if any one is missing:

- The starting list. A locked `SET_*_NAMES` of 60 cards, or a 60 the user wrote down. A 30-card list is not a start. An archived list is not a start either. The same `archived` check used for foes applies to the subject.
- The card coming in, or the exact pair when the user already chose both the card that comes in and the card that leaves.
- The subject's strategy name. Use the strategy that already plays this list. Do not add a `strat.name ==` branch, and do not hardcode a look size into `app/engine/game.py`.

If the engine does not execute the printed sentence of the card coming in, stop before the first game. A win rate from an ignored sentence is not a result. A new sentence needs a parser branch and a test that uses the exact printed wording. That work is not this search.

Quote the printed sentence from the catalog or the card text. A lab note, a memory of the line, or a strategy comment does not choose the cut.

## Every 60-card deck

Build the foe field at the start of the run from the live registry, `LIST_KEYS` and `load_seed_payload()`. A foe is every entry whose kind is a list, whose card count is 60, and which is not archived. Decks get added. The next run tests the new ones too. A live 60 with no row in this note was not tested.

An archived deck is not a foe. Read `archived` on the deck record when the record has it. When it does not, use `deck_archived_for_presets(default_rule_presets_for(deck_id))` in `app/engine/models.py`. That is the app's check: a deck whose presets are only the retired `b` and `c` rules is archived. Carpet sets A–F and S, and Spare Cards, are archived today. A deck archived later, including a 60, drops out of the next run. Name the skipped archived decks in the note. They get no row and no weight.

Judge the field by `len(cards) == 60`. A 30-card list stays out even when it is not archived. Set T is Standard 30 (`s30`) and is not archived, and it is still not a foe. `seed-g30` is 60 cards now, so it is in the field. Build it with `build_g30_deck()`, because that list's Aipom is the Paradox Rift print. Build Mill, Doll, Celebi Mill, and 二森林 with their own builders. Build the rest with `build_fallback_deck`.

Also test a 60-card list that the current labs already play and that is not a seed key yet, unless that list is archived. Today that is Mega Starmie (`SET_STARMIE60_NAMES`, strategy `starmie`) and Iron Thorns (`IRON_THORNS_NAMES`, strategy `thorns`). When one of those is registered as a seed, the registry row replaces the extra row. If that seed is archived, the row goes away.

The strategies that already play today's 60s:

| Key | Strategy |
| :--- | :--- |
| g | g |
| h | nuzzle |
| c60 | party |
| d60 | demolish |
| s60 | slash |
| t60, t-meta, t-unl | phantom |
| g30 | celebration |
| m60 | mew_baby |
| l60 | aura |
| mill | mill |
| doll | doll |
| celebi, two-forest | roast |
| starmie | starmie |
| thorns | thorns |

A 60 that is not in this table still gets a row. Use the strategy that already plays that locked list. If no strategy plays it, stop and name the deck. Skipping it means it was not tested. Do not invent a strategy.

Foes are the locked lists as they stand when the search starts. The candidate being edited is not written into the foe field. A mirror against the subject's own lock uses that locked list.

Check `len(cards) == 60` for the subject and for every foe before the first game. Rules are `standard_60_rules()` (60 cards, 6 prizes, 4 of a name except basic Energy).

## Weights

The decision weights come from the 0-copy list. That is the starting 60, before any copy of the incoming card is added. Measure it first, on the same seed and the same foes as every later count.

A foe cell is the mean of the two seats. The raw weight is how often that list loses the cell. This is `_weights` in `data/lab/set_mill_sleep.py`, the same rule that froze the Sisters 60's own losses:

```text
raw[foe] = max(1e-6, 1 - win_rate_at_0_copies)
weight[foe] = raw[foe] / sum(raw)
```

A foe the 0-copy list loses more often counts more. A foe it beats in every game still gets the `1e-6` floor before the division, so the weight is never exactly zero. Divide in the script. Do not type a pre-rounded weight into the score.

Freeze that vector for the rest of this search. Copy 1, copy 2, and copy 4 all use the 0-copy weights. Do not recompute the weights from a later count. The Sisters numbers in `data/lab/set-mill-sleep.md` are the losses of that old list. They are not the weights for a new starting 60.

The weights change when the 0-copy measurement changes. A different starting list, a deck added to the field, or a deck archived out of it, produces a new set of losses and a new vector. Store the per-foe cells, so a later vector can re-score them without new games and without a new seed. The kept list for this run is the one scored with the 0-copy weights.

An archived deck is not in the field, so it has no loss and no weight. A new live 60 is in the 0-copy measurement, so it has a weight. Leaving any other live 60 out of that measurement leaves it out of the score.

Write each foe's 0-copy win rate and its weight in the note. Also report the unweighted mean and the worst foe. Those two columns do not choose the cut. If the user names a different vector, re-score the stored cells and say whether the kept count changes. The keeper stays the 0-copy weights unless the user says to keep the other vector.

The standard error uses the vector of the score being quoted. For each foe, each seat contributes `p * (1 - p) / 400`, the two seats are averaged, and the foe variances combine with the squared weights:

```text
variance += weight^2 * (seat_var_a + seat_var_b) / 4
se = sqrt(variance)
gap_se = sqrt(se_before^2 + se_after^2)
```

Report a gap as the rate difference and as `gap / gap_se` combined standard errors. Two vectors mean two standard errors.

## One seed, 400 games

One comparison is one list, one foe, and one seat, and that cell is 400 games. The other seat is its own 400, from the same seed. A 20-game or 40-game run is a smoke. Label it smoke, and leave it out of the keep rule.

One integer seed covers the whole search: the baseline, every cut, both seats, every foe, and every later copy. Write that integer into the script before the first game. If the user names a seed, use it. If they do not, use a `YYYYMMDD` integer and do not change it later.

Each cell starts with `random.Random(SEED)` and then plays its 400 games on that generator, as `set_mill_hilda.py` does. Do not add the foe index, the seat, or the step to the seed. Do not continue one generator from one foe into the next. Two lists still diverge after the first choice that consumes a different number of random draws. Say that in the note. Do not claim the streams stayed identical.

The cache key is `seed|400|seat|foe|full list`. A cell from another seed, another game count, or a 30-card foe is not reusable. Append each finished cell to a partial jsonl and resume from it. A foe that joined the registry after this sample is unmeasured. The next run plays it. Do not reuse a score from a run that lacked that foe.

## One card at a time

Three requests use this same measurement:

- A named swap. The user chose the card coming in and the card leaving. Measure that one list against the starting list.
- A greedy search on one incoming card. Each step tries every other name still in the list as the one copy to cut, then the next copy is tried the same way, through the cap.
- A sequence of named swaps. Apply them one copy at a time. Each one is measured against the list so far, on the same seed.

A step removes one copy and appends one copy. The list stays 60 cards. `copy_violations` against `standard_60_rules()` must be empty. The cap is 4 of the incoming name, or the legal maximum when that is lower. Basic Energy keeps the printed exception to that cap. Skip a cut that is not in the list.

Every other name is a legal cut, unless the user named cards that stay. Do not copy the Doll `PROTECT` set on your own. Do not cut the incoming card below the count this step is building.

Sort the step by the decision-vector rate, then worst foe, then how many copies the cut had before, then the name. Take that best cut and continue, including when its rate is below the count before it and below the start. A dip is a row. The search stops at the cap.

After the last count, keep the count whose rate under the decision vector is highest against the starting list. If the start is higher than every count, keep the start. A count of 3 or 4 can be the keeper when its gain over the start is larger than the gain at 1 or 2. The path is one line: the next copy is built on the list that just added a copy, not on a second branch from an earlier count.

The path table has two deltas for each count: against the start, and against the previous count. The decision names the count with the largest gain over the start, and it says when a higher count gained more than a lower one. The step gain of a later copy can be larger than the step gain of an earlier copy. Report that when it happens.

Write the json and the markdown after every count, with `complete` still false until the cap is done.

Each step took the best cut on this seed, so that path sits a little high. Say so in the decision. Continuing through a dip does not remove that. A second seed is a holdout, and only when the user asks. The holdout is still 400 games, the same foes, and a new seed. Label it holdout. It does not replace the search seed, and it does not choose a different cut.

## Why the rate moved

Write the reason in prose beside the path table. After each count, and in the decision, that prose uses only the measurements below. For a named swap, write it for that swap. Also write it for any other cut in the same step whose move under the decision vector is at least one combined standard error, so a cut that lost for a different reason is visible.

Each reason has these parts, in this order:

1. The printed sentence of the card that came in, and the printed sentence of the card that left. Quote the text the engine parsed.
2. The 0-copy loss weights. The delta against the start and the delta against the previous count, with both standard errors, the combined standard error, and the ratio. When a higher count gained more than a lower count, say both gains.
3. The foes that carry the move. For each foe, contribution is `weight * (new cell − old cell)` under the vector being quoted. Name the largest contributions in both directions. A foe that did not move does not explain the rate. If a higher count wins because a different foe moved, say that. If it wins because the same foe moved further, say that.
4. The unweighted mean. If it would keep another cut or another count, name that list and the foes that flip the order. The keeper is still the 0-copy loss weights.
5. The counters for those two sentences, before and after, on the same weights as the quoted score. Use the event key the engine already bumps for that sentence (`event_sum` or the key passed to `_bump`). Count how often the sentence resolved, and how often the line it feeds resolved: the attack, the mill, the search, the evolve. If the engine bumps no event for that sentence, say the sample has no counter for it. Do not invent a rate, and do not add a look size to `app/engine/game.py` to manufacture one.
6. The end reasons, tallied for all 400 games from the subject's seat. Use the buckets in `set_doll_losses.py` `_kind`, read from `GameResult.reason`:

| Bucket | `GameResult.reason` |
| :--- | :--- |
| prizes | `took all prize cards` |
| empty / foe empty | `opponent has no Pokémon in play` |
| decked / foe decked | `{seat} decked out` |
| no basic / foe no basic | `{seat} had no Basic Pokémon` or `had no playable Pokémon` |
| turn prizes | `more prizes at turn limit` |
| turn hp | `more remaining HP at turn limit` |
| tie | `turn limit` |

Weight those shares with the same vector as the score being quoted. Report the change. A rise that is the opponent decking out is a different reason from a rise that is taking all six Prizes, or from a loss that is an empty board.

7. One sentence that ties the printed text to the foes and the end reasons that actually moved. If the counters did not move, say the sample does not show that sentence firing. If the counters moved and the win rate did not, say that too. The counters and the reasons win over the story.

The six sample traces from `run_simulation` are not this tally. Count every game in the cell. Hilda's worker already loops `play_game`; add the reason buckets and the sentence counters there.

## What to write

Write three files under `data/lab/`:

- `<slug>.py` runs the search.
- `<slug>.json` stores the seed, the games, the foe keys actually tested and each one's card count, the archived decks that were skipped, the 0-copy win rate and weight of each foe, the per-foe cells, every count through the cap, the path, the rounds, the best list, and `complete`.
- `<slug>.md` is the note a person reads.

The note starts the way `data/lab/set-mill-hilda.md` starts: what one step does, the printed sentence, the seed, 400 games per seat, both seats, the decks tested, the archived decks skipped, the 0-copy weights, and the elapsed time. Then the path table (count, cut, weighted rate, standard error, unweighted mean, worst, delta against the start, delta against the previous count, and the sentence counters), the decision, the counts, each step's full cut table, the reason paragraphs, and the foe table at the kept list (A, B, mean, delta against the start).

The script records the sample. It does not assign `SET_*_NAMES` and it does not change a lock. Say that in the note.

## Done

The search is done when every 60-card deck in this checkout's registry that is not archived has a row, the path runs through the copy cap, and the kept count is the one with the largest gain over the start under the weights taken from the 0-copy losses. The note names the archived decks it skipped. It has the foe table and a reason paragraph for every count that cites the printed sentences, the weighted contributions, the counters, and the end-reason mix. The same seed and 400 games appear on every row. A 30-card deck has no row, and an archived deck has no row. The stored cells can be re-scored with a new vector without new games.
