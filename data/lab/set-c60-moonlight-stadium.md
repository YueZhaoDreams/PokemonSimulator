# C60: one Moonlight Stadium in place of every distinct card

Date: 2026-09-27
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_moonlight_stadium.py`
Raw: `data/lab/set-c60-moonlight-stadium.json`
Elapsed: 1609s

The lock is the live list (`SET_C60_NAMES`). Every other row removes exactly one copy of one printed name and adds one Moonlight Stadium (Lost Thunder 188).

Printed text: "The Retreat Cost of each Pokémon in play (both yours and your opponent's) that has any Psychic or Darkness Energy attached to it is Colorless less."

Clefairy retreats for 2. With one Psychic or Darkness Energy already attached, that cost is 1. Party uses it this way: Party, pay the one energy to retreat, promote a benched Clefairy that just received one Psychic, Party again, then attach this turn's energy to the Clefairy that came up. Switch is not spent on that retreat. Versus Dragapult, Floragato, or a ready Demolish, the pivot only happens when a Switch is still in hand, so the 60 HP body can hide afterward. Battle Cage is not played over an early Moonlight Stadium, and Moonlight Stadium is not played over a Battle Cage that is already in play. Once six Psychic Energy are in play against Dragapult, Cage replaces Moonlight Stadium.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp.

## Win rate

The lock is the first row. Every other row is one copy swapped for Moonlight Stadium, sorted by `wComp`.

| Cut for Moonlight Stadium | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **lock** | **73.4%** | 66.8% | 91.2% | 78.0% | 99.5% | **63.3%** | **72.0%** | **70.9%** |
| Boss's Orders | 71.4% | 67.8% | **91.7%** | 78.3% | **99.7%** | 61.0% | 71.8% | 70.2% |
| Night Stretcher | 72.1% | 67.7% | 91.6% | 76.2% | 99.6% | 61.7% | 71.4% | 70.1% |
| Ultra Ball | 70.8% | 67.3% | 91.3% | 78.0% | 99.6% | 63.2% | 71.3% | 70.5% |
| Clefable ex | 71.2% | 66.7% | 90.1% | 78.0% | 99.5% | 62.6% | 71.2% | 70.2% |
| Seeker | 71.0% | 66.4% | 90.8% | **78.6%** | 99.5% | 61.0% | 71.2% | 69.7% |
| Clefable CLC | 71.1% | 66.6% | 91.4% | 78.0% | **99.7%** | 60.3% | 71.1% | 69.5% |
| Poké Pad | 70.0% | 67.7% | 91.5% | 77.6% | 99.5% | 60.7% | 71.1% | 69.7% |
| Mewtwo ex | 71.8% | **68.3%** | 91.5% | 73.0% | 99.6% | 60.9% | 70.7% | 69.4% |
| Clefable (Prankish) | 70.3% | 66.4% | 90.9% | 77.5% | 99.6% | 62.3% | 70.7% | 69.8% |
| Iono | 70.0% | 66.9% | 90.6% | 76.8% | 99.6% | **63.3%** | 70.6% | 70.0% |
| Switch | 71.5% | 66.4% | 91.6% | 75.4% | 99.5% | 61.5% | 70.5% | 69.5% |
| Battle Cage | 68.4% | 66.9% | 89.7% | 77.8% | 99.6% | 62.5% | 70.3% | 69.5% |
| Buddy-Buddy Poffin | 71.1% | 66.8% | 89.8% | 74.7% | **99.7%** | 62.3% | 70.3% | 69.5% |
| Nest Ball | 71.2% | 65.0% | 90.7% | 76.0% | 99.5% | 61.2% | 70.0% | 69.0% |
| Psychic Energy | 69.4% | 64.4% | 90.4% | 76.8% | 99.5% | 60.4% | 69.4% | 68.4% |
| Lillie | 70.1% | 65.2% | 90.9% | 74.4% | 99.6% | 59.7% | 69.3% | 68.1% |
| Energy Switch | 69.6% | 63.9% | 89.9% | 76.7% | **99.7%** | 60.4% | 69.2% | 68.2% |
| Hop | 69.0% | 64.1% | 89.0% | 74.9% | **99.7%** | 59.7% | 68.6% | 67.6% |
| Arven | 70.3% | 65.6% | 89.8% | 71.0% | 99.3% | 61.7% | 68.6% | 68.2% |
| Telepathic Psychic Energy | 69.1% | 63.4% | 90.0% | 73.8% | 99.3% | 58.8% | 68.1% | 67.0% |
| Lillie's Determination | 67.6% | 63.7% | 89.5% | 74.5% | **99.7%** | 58.8% | 67.9% | 66.9% |
| Clefairy | 69.0% | 64.6% | 89.6% | 65.9% | 99.4% | 59.9% | 66.4% | 66.3% |
| Maximum Belt | 69.4% | 65.1% | 89.3% | 56.1% | 99.6% | 58.6% | 64.1% | 64.4% |

Going first / second. The lock is the first row.

| Cut | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| **lock** | 74.6/72.2 | 68.8/64.8 | 79.8/76.1 | 64.2/62.4 |
| Boss's Orders | 73.5/69.3 | 67.3/68.2 | 80.9/75.8 | 62.2/59.6 |
| Night Stretcher | 73.8/70.3 | 69.4/65.8 | 79.2/73.1 | 62.7/60.7 |
| Ultra Ball | 72.4/69.2 | 67.3/67.2 | 82.1/73.8 | 64.9/61.6 |
| Clefable ex | 73.7/68.5 | 66.2/67.2 | 81.3/75.0 | 63.0/62.2 |
| Seeker | 73.6/68.2 | 66.8/66.0 | 81.2/76.0 | 60.5/61.5 |
| Clefable CLC | 73.4/68.6 | 69.8/63.2 | 80.4/75.7 | 60.7/59.9 |
| Poké Pad | 72.1/68.0 | 69.2/66.2 | 79.8/75.4 | 63.2/58.2 |
| Mewtwo ex | 73.8/69.8 | 69.4/67.2 | 77.0/69.3 | 60.9/60.8 |
| Clefable (Prankish) | 72.6/68.0 | 67.2/65.6 | 79.6/75.3 | 62.1/62.4 |
| Iono | 72.0/68.1 | 67.1/66.7 | 79.4/74.2 | 63.0/63.6 |
| Switch | 71.8/71.1 | 66.3/66.6 | 78.8/72.0 | 64.4/58.6 |
| Battle Cage | 69.1/67.7 | 68.8/65.0 | 80.9/74.6 | 65.9/59.1 |
| Buddy-Buddy Poffin | 72.4/69.7 | 66.4/67.2 | 77.1/72.4 | 63.7/60.8 |
| Nest Ball | 72.2/70.2 | 65.5/64.5 | 79.3/72.7 | 61.1/61.4 |
| Psychic Energy | 70.7/68.3 | 66.6/62.2 | 80.2/73.3 | 61.9/58.7 |
| Lillie | 71.8/68.3 | 65.4/65.0 | 78.3/70.6 | 61.2/58.2 |
| Energy Switch | 70.6/68.7 | 65.3/62.4 | 79.6/73.9 | 60.8/59.9 |
| Hop | 69.4/68.7 | 65.2/63.2 | 78.1/71.7 | 60.6/58.8 |
| Arven | 70.3/70.4 | 65.3/65.9 | 75.8/66.6 | 62.0/61.4 |
| Telepathic Psychic Energy | 70.2/68.1 | 63.2/63.6 | 77.2/70.4 | 59.9/57.7 |
| Lillie's Determination | 70.5/64.7 | 63.5/64.0 | 78.0/70.9 | 60.1/57.5 |
| Clefairy | 70.8/67.3 | 64.2/65.0 | 67.6/64.1 | 61.9/58.0 |
| Maximum Belt | 71.4/67.3 | 65.8/64.4 | 62.2/49.8 | 60.9/56.3 |

## What the ranking says

No cut beats the lock. `wComp` 72.0% and `wAll` 70.9% are both the best numbers in the matrix. T60 73.4% and G 63.3% are also the best cells in those columns. No row is ahead of the lock on T60, Hedrick, and D60 at the same time.

The closest row cuts one Boss's Orders: `wComp` 71.8% (−0.2). Hedrick is 67.8% (+1.0) and D60 is 78.3% (+0.3). T60 is 71.4% (−2.0), and going second against T60 is 69.3% against the lock's 72.2%. G is 61.0% (−2.3). That is not a swap.

Cutting one Battle Cage for the stadium drops T60 from 73.4% to 68.4% (−5.0) and UNL from 91.2% to 89.7%. Cutting Maximum Belt drops D60 from 78.0% to 56.1%. Cutting Clefairy drops D60 to 65.9%. Cutting Switch, which the pivot is supposed to leave in hand, drops D60 to 75.4% and `wComp` to 70.5%.

On the rows that include the stadium, the Party pivot shows up in about 40–70 of 3,000 Dragapult games and about 90–170 of 3,000 D60 games. Against G it shows up in about 500–680 games. The stadium itself is played in roughly 700–1,100 games per foe. The pivot is real, and it is too rare against Dive to pay for a card.

The printed gate is why. Retreat drops only after a Psychic or Darkness Energy is already attached. An empty Active Clefairy still retreats for 2, so the first turn cannot Party, retreat, and Party again before the manual attachment. The second Party needs that energy to already be there. Against Dragapult the pivot also keeps a Switch so the 60 HP Clefairy does not stay Active. Dragapult ex retreats for 1, and a Psychic Energy on it makes that 0 under the same stadium, so the opponent's line gets the discount too.

## Conclusion

Do not put Moonlight Stadium into C60. Keep the live list. The card and the Party pivot stay in the engine for any list that actually includes the stadium.
