# C60 bounce-slot swap matrix

Date: 2026-09-22
Seed: `20260922`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_bounce_combo.py`
Raw: `data/lab/set-c60-bounce-combo.json`
Elapsed: 875s

The engine can play Penny, Professor Turo's Scenario, Mr. Briney's Compassion, Seeker, AZ, and Cheren's Care from the printed sentences. This lab asks which of those cards, in the five slots a bounce package would spend, changes C60's win rate.

Those five indexes, on the measured package, are 2 Penny, 1 Turo, 1 Briney, 1 Seeker. On the cage list they are a second Hop, a second Lillie, a second Lillie's Determination, the last Iono, and a second Energy Switch. Every other card stays in the same index, so a cell is a swap.

Foes: T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `g` (`SET_G_NAMES`).

`wComp` weights T60, Hedrick, and D60 by how often the cage list loses that matchup. `wAll` does the same over all six foes.

## One card in Iono's slot

The other four slots stay Hop, Lillie, Lillie's Determination, and Energy Switch.

| Variant | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **cage** | **68.8%** | 63.8% | **90.7%** | **75.8%** | 99.5% | 71.9% | 68.7% |
| iono-penny | 66.3% | 63.7% | 90.2% | 73.5% | 99.6% | 74.5% | 67.2% |
| iono-turo | 66.6% | 62.2% | 89.5% | 73.3% | 99.6% | 72.7% | 66.6% |
| iono-briney | 66.8% | **65.1%** | 89.7% | 74.4% | 99.4% | 73.8% | 68.1% |
| iono-seeker | **68.8%** | **65.1%** | 90.3% | 74.8% | 99.4% | **75.5%** | **68.9%** |
| iono-az | 65.1% | 61.1% | 89.9% | 73.4% | 99.5% | 71.4% | 65.7% |
| iono-cheren | 66.7% | 61.5% | 90.6% | 74.7% | 99.3% | 73.5% | 66.8% |

Vs T60 the AI does play the one-of: Penny 35% of games, Turo 34%, Briney 29%, Seeker 32%, AZ 32%. Cheren's Care resolves in 0 games and fails in 34% (the line is Psychic; the printed sentence needs a damaged Colorless Pokémon). The supporter is still discarded.

Seeker-for-Iono is the only row whose weighted T60/Hedrick/D60 score is above the cage list, by 0.2. T60 is flat (68.8%), Hedrick is +1.3, D60 is −0.9, G is +3.6. A 3,000-game cell at these rates moves about a point from noise. That is a wash on the matchups that decide the lock, plus a real G bump.

## Packages in the five slots

| Variant | Slots | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **cage** | Hop, Lillie, Determination, Iono, Energy Switch | **68.8%** | **63.8%** | **90.7%** | **75.8%** | **99.5%** | 71.9% | **68.7%** |
| penny2 | 2 Penny, Determination, Iono, Energy Switch | 63.5% | 58.9% | 89.1% | 71.5% | 99.3% | 71.6% | 63.8% |
| penny4 | 4 Penny, Energy Switch | 58.3% | 54.9% | 85.5% | 64.1% | 99.0% | 71.2% | 58.5% |
| live | 2 Penny, Turo, Briney, Seeker | 57.7% | 57.2% | 85.6% | 62.7% | 99.0% | 71.4% | 58.9% |
| no-penny | Turo, Briney, Seeker | 62.6% | 59.9% | 88.3% | 68.3% | 99.1% | 72.0% | 63.1% |
| no-turo | 2 Penny, Briney, Seeker | 64.2% | 59.7% | 88.3% | 67.2% | 99.0% | 73.3% | 63.2% |
| no-briney | 2 Penny, Turo, Seeker | 58.9% | 55.6% | 87.4% | 65.7% | 98.8% | 70.9% | 59.4% |
| no-seeker | 2 Penny, Turo, Briney | 56.5% | 54.5% | 86.1% | 62.8% | 98.7% | 69.4% | 57.4% |
| az-for-turo | 2 Penny, AZ, Briney, Seeker | 57.8% | 55.8% | 85.3% | 62.1% | 98.9% | 70.6% | 58.1% |
| cheren-for-turo | 2 Penny, Cheren, Briney, Seeker | 60.8% | 56.7% | 87.1% | 61.7% | 98.8% | 72.8% | 59.4% |
| turo-for-briney | 2 Penny, 2 Turo, Seeker | 58.0% | 53.7% | 85.1% | 63.0% | 98.5% | 68.6% | 57.6% |
| briney-for-turo | 2 Penny, 2 Briney, Seeker | 60.1% | 57.6% | 86.5% | 60.9% | 98.8% | 72.5% | 59.3% |

Penny count vs T60, with the rest of the cage list held: 0 copies 68.8%, 1 copy 66.3%, 2 copies 63.5%, 4 copies 58.3%. The same staircase shows up on Hedrick and D60. Vs T60, Penny fires in 35% / 56% / 76% of games at 1 / 2 / 4 copies, and a damaged Pokémon is replayed at full HP in 24% / 39% / 61%.

The live package vs T60 plays Penny in 52% of games, Turo in 37%, Briney in 30%, Seeker in 34%, and heals in 61%. It still loses 11.1 points to the cage list there and 13.1 points vs D60 (75.8% → 62.7%). AZ in Turo's slot copies that loss (T60 57.8%, D60 62.1%). A second Turo instead of Briney is the low weighted row (57.6%).

Going first and second move together. Cage vs T60 is 69.5% / 68.0%. The live package is 57.4% / 58.0%. Cage vs D60 is 78.0% / 73.6%. The live package is 64.4% / 61.0%.

## Lock

`SET_C60_NAMES` stays the cage list: 2 Hop, 2 Lillie, 2 Lillie's Determination, 1 Iono, 2 Energy Switch, 0 Penny, 0 Turo, 0 Briney, 0 Seeker.

On this seed the cage row is T60 68.8%, Hedrick 63.8%, UNL 90.7%, D60 75.8%, S60 99.5%, G 71.9%. The older Battle Cage array (seed `20260911`) was 69.1 / 64.6 / 89.5 / 76.1 / 99.7 on the first five. G here is strategy `g` on the current Telepathic list, so 71.9% is this matrix's G number.

Seeker-for-Iono is the swap to re-test if G becomes a matchup that matters. It is the one cell with a G gain (+3.6) and a flat T60. It gives back 0.9 on D60, and the weighted hard-matchup edge is 0.2.
