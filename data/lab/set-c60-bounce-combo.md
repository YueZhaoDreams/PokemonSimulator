# C60 bounce-slot swap matrix

Date: 2026-09-22
Seed: `20260922`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_bounce_combo.py`
Raw: `data/lab/set-c60-bounce-combo.json`
Elapsed: 875s for the full matrix. Rows that contain Seeker were re-run after the one-bench KO line (552s, same seed and game count). Rows without Seeker are the first run.

The engine can play Penny, Professor Turo's Scenario, Mr. Briney's Compassion, Seeker, AZ, and Cheren's Care from the printed sentences. Party also plays Seeker when the opponent has exactly one Benched Pokémon and the Active attack still KOs after the return: that Bench Pokémon goes back, then the KO leaves no Pokémon in play. This lab asks which of those cards, in the five slots a bounce package would spend, changes C60's win rate.

Those five indexes, on the measured package, are 2 Penny, 1 Turo, 1 Briney, 1 Seeker. On the cage list they are a second Hop, a second Lillie, a second Lillie's Determination, the last Iono, and a second Energy Switch. Every other card stays in the same index, so a cell is a swap.

Foes: T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `g` (`SET_G_NAMES`).

`wComp` weights T60, Hedrick, and D60 by how often the cage list loses that matchup. `wAll` does the same over all six foes.

## One card in Iono's slot

The other four slots stay Hop, Lillie, Lillie's Determination, and Energy Switch.

| Variant | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **cage** | **68.8%** | 63.8% | **90.7%** | **75.8%** | 99.5% | 71.9% | 68.7% |
| iono-penny | 66.3% | 63.7% | 90.2% | 73.5% | 99.6% | **74.5%** | 67.2% |
| iono-turo | 66.6% | 62.2% | 89.5% | 73.3% | 99.6% | 72.7% | 66.6% |
| iono-briney | 66.8% | **65.1%** | 89.7% | 74.4% | 99.4% | 73.8% | 68.1% |
| iono-seeker | 67.5% | 63.6% | 90.5% | **75.8%** | 99.4% | 74.3% | 68.2% |
| iono-az | 65.1% | 61.1% | 89.9% | 73.4% | 99.5% | 71.4% | 65.7% |
| iono-cheren | 66.7% | 61.5% | 90.6% | 74.7% | 99.3% | 73.5% | 66.8% |

Vs T60 the AI does play the one-of: Penny 35% of games, Turo 34%, Briney 29%, AZ 32%. Cheren's Care resolves in 0 games and fails in 34% (the line is Psychic; the printed sentence needs a damaged Colorless Pokémon). The supporter is still discarded. With the one-bench KO line in, C60's own Seeker return happens 560 times in 3,000 T60 games (18.7%).

Seeker-for-Iono, measured with that line: T60 67.5% (cage 68.8%), Hedrick 63.6% (63.8%), D60 tied at 75.8%, G 74.3% (71.9%), wComp 68.2% (68.7%). The cage list stays ahead on the weighted hard matchups. G is the matchup where the one Seeker is higher.

## Packages in the five slots

| Variant | Slots | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **cage** | Hop, Lillie, Determination, Iono, Energy Switch | **68.8%** | **63.8%** | **90.7%** | **75.8%** | **99.5%** | 71.9% | **68.7%** |
| penny2 | 2 Penny, Determination, Iono, Energy Switch | 63.5% | 58.9% | 89.1% | 71.5% | 99.3% | 71.6% | 63.8% |
| penny4 | 4 Penny, Energy Switch | 58.3% | 54.9% | 85.5% | 64.1% | 99.0% | 71.2% | 58.5% |
| live | 2 Penny, Turo, Briney, Seeker | 58.3% | 55.1% | 85.2% | 62.2% | 98.8% | 70.1% | 58.1% |
| no-penny | Turo, Briney, Seeker | 64.3% | 58.6% | 88.9% | 68.6% | 99.4% | 71.8% | 63.2% |
| no-turo | 2 Penny, Briney, Seeker | 63.1% | 60.0% | 88.4% | 68.4% | 99.1% | 72.5% | 63.3% |
| no-briney | 2 Penny, Turo, Seeker | 59.9% | 54.6% | 85.5% | 64.4% | 98.7% | 69.5% | 59.0% |
| no-seeker | 2 Penny, Turo, Briney | 56.5% | 54.5% | 86.1% | 62.8% | 98.7% | 69.4% | 57.4% |
| az-for-turo | 2 Penny, AZ, Briney, Seeker | 59.2% | 55.2% | 85.7% | 63.9% | 98.4% | 70.2% | 58.8% |
| cheren-for-turo | 2 Penny, Cheren, Briney, Seeker | 60.5% | 57.6% | 85.9% | 63.4% | 98.8% | 71.2% | 60.1% |
| turo-for-briney | 2 Penny, 2 Turo, Seeker | 57.4% | 54.6% | 84.4% | 64.0% | 98.1% | 67.8% | 58.0% |
| briney-for-turo | 2 Penny, 2 Briney, Seeker | 59.4% | 56.9% | 86.0% | 63.1% | 98.8% | 71.5% | 59.4% |

Penny count vs T60, with the rest of the cage list held: 0 copies 68.8%, 1 copy 66.3%, 2 copies 63.5%, 4 copies 58.3%. The same staircase shows up on Hedrick and D60. Vs T60, Penny fires in 35% / 56% / 76% of games at 1 / 2 / 4 copies, and a damaged Pokémon is replayed at full HP in 24% / 39% / 61%.

The live package vs T60 plays Penny in 52% of games, Turo in 36%, Briney in 29%, Seeker in 14%, and heals in 59%. It is 58.3% there (cage 68.8%) and 62.2% vs D60 (cage 75.8%). AZ in Turo's slot is T60 59.2% and D60 63.9%. Two Turo in place of Briney is the low weighted row (58.0%).

Going first and second move together. Cage vs T60 is 69.5% / 68.0%. The live package is 59.6% / 57.0%. Cage vs D60 is 78.0% / 73.6%. The live package is 65.1% / 59.2%.

## Lock

`SET_C60_NAMES` stays the cage list: 2 Hop, 2 Lillie, 2 Lillie's Determination, 1 Iono, 2 Energy Switch, 0 Penny, 0 Turo, 0 Briney, 0 Seeker.

On this seed the cage row is T60 68.8%, Hedrick 63.8%, UNL 90.7%, D60 75.8%, S60 99.5%, G 71.9%. The older Battle Cage array (seed `20260911`) was 69.1 / 64.6 / 89.5 / 76.1 / 99.7 on the first five. G here is strategy `g` on the current Telepathic list, so 71.9% is this matrix's G number.

Seeker-for-Iono is the cell to re-test if G becomes a matchup that matters. With the one-bench KO line measured, that swap is G 74.3% against the cage list's 71.9%, T60 67.5% against 68.8%, D60 tied at 75.8%, and wComp 68.2% against 68.7%. The lock stays Iono.
