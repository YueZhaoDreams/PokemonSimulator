# C60: a second Moonlight Stadium in place of every other card

Date: 2026-09-28
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_moonlight_second.py`
Raw: `data/lab/set-c60-moonlight-second.json`
Elapsed: 1558s

The lock is the live list (`SET_C60_NAMES`): one Great Encounters Moonlight Stadium and one Ultra Ball. Every other row removes exactly one copy of one other printed name and adds a second Moonlight Stadium.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp.

## Win rate

Rows are sorted by `wComp`.

| Cut for a second Moonlight Stadium | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ultra Ball | **74.3%** | **70.0%** | 91.7% | 78.3% | 99.3% | 64.6% | **73.7%** | **72.3%** |
| Clefable CLC | 73.3% | 69.4% | **91.9%** | 77.8% | **99.7%** | 63.8% | 73.0% | 71.6% |
| Switch | 73.4% | 69.7% | 90.9% | 76.5% | 99.5% | 63.0% | 72.8% | 71.2% |
| **lock** | 71.9% | 69.1% | 91.5% | **79.1%** | 99.6% | 63.2% | 72.7% | 71.2% |
| Seeker | 72.0% | 69.2% | 90.8% | 78.5% | 99.5% | 62.0% | 72.6% | 70.8% |
| Boss's Orders | 71.0% | 69.7% | 90.4% | 77.3% | 99.4% | 63.2% | 72.1% | 70.8% |
| Poké Pad | 70.8% | 69.2% | 90.4% | 78.2% | 99.5% | 64.2% | 72.1% | 71.1% |
| Mewtwo ex | 71.7% | 69.9% | 91.3% | 75.4% | 99.1% | 64.7% | 72.0% | 71.2% |
| Clefable (Prankish) | 70.4% | 68.8% | 90.5% | 78.4% | 99.6% | 64.0% | 71.9% | 70.9% |
| Lillie | 70.6% | 68.4% | 90.9% | 77.5% | 99.5% | 63.0% | 71.6% | 70.4% |
| Energy Switch | 72.1% | 67.1% | 91.7% | 76.6% | 99.4% | 62.4% | 71.3% | 70.2% |
| Night Stretcher | 70.3% | 68.0% | 91.7% | 77.5% | 99.4% | 61.9% | 71.3% | 70.0% |
| Nest Ball | 70.0% | 69.7% | 90.6% | 74.9% | 99.5% | 65.7% | 71.2% | 71.0% |
| Iono | 69.6% | 68.7% | 90.6% | 76.7% | 99.5% | 66.2% | 71.1% | 71.1% |
| Battle Cage | 68.4% | 69.1% | 89.5% | 77.4% | 99.6% | 64.6% | 71.0% | 70.5% |
| Clefable ex | 69.2% | 68.0% | 90.3% | 77.5% | 99.6% | **66.7%** | 70.9% | 71.1% |
| Buddy-Buddy Poffin | 70.2% | 68.3% | 90.4% | 74.5% | 99.5% | 63.9% | 70.6% | 70.0% |
| Arven | 70.3% | 69.8% | 90.8% | 71.4% | 99.4% | 63.6% | 70.4% | 69.9% |
| Hop | 68.8% | 67.7% | 90.1% | 75.0% | 99.3% | 63.2% | 70.0% | 69.4% |
| Psychic Energy | 68.4% | 66.5% | 90.7% | 75.1% | 99.4% | 61.9% | 69.4% | 68.7% |
| Telepathic Psychic Energy | 68.9% | 65.5% | 89.8% | 75.0% | 99.6% | 61.7% | 69.2% | 68.5% |
| Lillie's Determination | 68.5% | 65.7% | 90.9% | 73.3% | 99.5% | 62.9% | 68.7% | 68.6% |
| Clefairy | 69.5% | 65.4% | 89.8% | 67.2% | 99.3% | 63.1% | 67.3% | 67.7% |
| Maximum Belt | 69.3% | 64.5% | 89.2% | 58.1% | 99.5% | 61.8% | 64.5% | 65.5% |

Going first / second. Same order.

| Cut | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| Ultra Ball | 75.8/72.6 | 72.6/67.4 | 82.4/74.3 | 65.3/63.9 |
| Clefable CLC | 74.8/71.7 | 70.6/68.2 | 81.4/74.2 | 64.8/62.9 |
| Switch | 74.5/72.3 | 70.0/69.5 | 80.4/72.2 | 64.5/61.5 |
| **lock** | 74.0/69.8 | 70.4/67.9 | 82.3/75.7 | 64.3/62.0 |
| Seeker | 74.3/69.6 | 70.2/68.2 | 83.0/74.0 | 63.7/60.2 |
| Boss's Orders | 72.0/70.0 | 72.6/66.7 | 80.7/73.6 | 64.2/62.1 |
| Poké Pad | 73.2/68.5 | 69.8/68.7 | 79.6/76.7 | 65.0/63.4 |
| Mewtwo ex | 73.9/69.4 | 70.1/69.8 | 78.3/72.6 | 66.2/63.3 |
| Clefable (Prankish) | 73.4/67.5 | 70.2/67.6 | 81.5/75.4 | 66.7/61.5 |
| Lillie | 72.9/68.5 | 68.9/68.0 | 81.5/73.5 | 65.1/61.0 |
| Energy Switch | 73.0/71.1 | 68.8/65.5 | 80.3/72.5 | 64.2/60.4 |
| Night Stretcher | 71.9/68.7 | 69.2/66.9 | 81.1/74.0 | 63.6/60.3 |
| Nest Ball | 71.7/68.3 | 71.0/68.4 | 79.6/70.0 | 68.8/62.8 |
| Iono | 71.8/67.4 | 69.2/68.2 | 80.5/72.9 | 68.3/64.2 |
| Battle Cage | 69.7/67.1 | 70.5/67.6 | 80.9/74.0 | 67.6/61.7 |
| Clefable ex | 70.4/68.0 | 69.4/66.6 | 80.6/74.1 | 68.9/64.4 |
| Buddy-Buddy Poffin | 72.8/67.6 | 68.7/67.9 | 77.4/71.8 | 66.0/61.9 |
| Arven | 72.8/67.9 | 70.2/69.4 | 76.3/66.4 | 64.5/62.8 |
| Hop | 71.3/66.1 | 69.5/65.8 | 78.1/71.9 | 63.6/62.8 |
| Psychic Energy | 69.6/67.2 | 67.3/65.7 | 79.5/70.8 | 63.8/60.0 |
| Telepathic Psychic Energy | 70.7/67.2 | 65.2/65.8 | 79.1/70.9 | 61.4/61.9 |
| Lillie's Determination | 68.6/68.3 | 67.6/63.7 | 78.2/68.5 | 65.3/60.6 |
| Clefairy | 71.5/67.5 | 68.1/62.8 | 70.2/64.1 | 64.9/61.2 |
| Maximum Belt | 71.5/67.1 | 65.0/64.0 | 65.7/50.4 | 62.7/61.0 |

## What the ranking says

Cutting the remaining Ultra Ball is the best `wComp` (73.7% against the lock's 72.7%, +1.0) and the best `wAll` (72.3% against 71.2%, +1.0). It is also the best T60 (74.3% against 71.9%, +2.4) and the best Hedrick (70.0% against 69.1%, +0.9). D60 is 78.3% against the lock's 79.1% (−0.8). Going first against T60 is 75.8% against the lock's 74.0%, and going second is 72.6% against 69.8%. G is 64.6% against 63.2% (+1.4). UNL is 91.7% against 91.5%. S60 is 99.3% against 99.6%.

No row is ahead of the lock on T60, Hedrick, and D60 at the same time. D60 79.1% stays with the one-stadium list. The next rows, one Clefable CLC (`wComp` 73.0%) and one Switch (`wComp` 72.8%), also give T60 back and give D60 away.

On the two-stadium rows the stadium is played in about 1,100–1,900 games per foe. On the Ultra Ball row the Party pivot is 232 of 3,000 T60 games, 265 of 3,000 Hedrick games, and 472 of 3,000 D60 games, against 109, 114, and 226 on the one-stadium lock.

## Conclusion

The second copy that raises the weighted win rate replaces the remaining Ultra Ball. `SET_C60_NAMES` stays at one Moonlight Stadium until that swap is locked.

