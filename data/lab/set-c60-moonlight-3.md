# C60: a third Moonlight Stadium in place of every other card

Date: 2026-09-28
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_moonlight_next.py`
Raw: `data/lab/set-c60-moonlight-3.json`
Elapsed: 1441s

The lock is the live list (`SET_C60_NAMES`): two Great Encounters Moonlight Stadium and no Ultra Ball. Every other row removes exactly one copy of one other printed name and adds a third Moonlight Stadium.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp.

## Win rate

Rows are sorted by `wComp`.

| Cut for a third Moonlight Stadium | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **lock** | 72.1% | **71.5%** | 91.4% | 77.6% | 99.2% | 64.6% | **73.4%** | 72.3% |
| Clefable CLC | 71.9% | 69.3% | **92.2%** | **79.7%** | 99.5% | 65.6% | 73.2% | **72.5%** |
| Seeker | 71.7% | 69.8% | 91.0% | 78.6% | **99.6%** | 63.8% | 73.0% | 71.8% |
| Iono | 70.8% | 71.4% | 91.0% | 77.3% | 99.3% | 65.5% | 72.9% | 72.2% |
| Boss's Orders | 71.4% | 70.8% | 90.8% | 77.1% | 99.5% | 66.0% | 72.8% | 72.3% |
| Energy Switch | 71.9% | 70.9% | 91.8% | 75.7% | 99.5% | 64.2% | 72.6% | 71.7% |
| Switch | 71.0% | 70.0% | 90.9% | 77.8% | 99.2% | 65.4% | 72.6% | 72.0% |
| Clefable (Prankish) | 71.1% | 70.5% | 90.8% | 76.9% | 99.3% | 64.5% | 72.5% | 71.7% |
| Nest Ball | 72.3% | 70.6% | 90.4% | 75.1% | 99.3% | 65.8% | 72.5% | 72.0% |
| Poké Pad | 71.6% | 70.4% | 91.0% | 75.9% | 99.3% | 64.5% | 72.4% | 71.6% |
| Night Stretcher | 71.4% | 70.4% | 91.6% | 75.4% | 99.5% | 63.5% | 72.2% | 71.2% |
| Battle Cage | 70.2% | 69.2% | 90.2% | 78.0% | 99.4% | 64.5% | 72.1% | 71.3% |
| Mewtwo ex | **72.5%** | 68.8% | 90.9% | 75.2% | 99.0% | **66.1%** | 71.9% | 71.8% |
| Lillie | 70.3% | 69.0% | 89.7% | 76.9% | 99.1% | 63.8% | 71.7% | 70.9% |
| Buddy-Buddy Poffin | 71.3% | 69.2% | 90.2% | 74.7% | 99.2% | **66.1%** | 71.5% | 71.4% |
| Clefable ex | 69.6% | 68.6% | 90.9% | 76.8% | 99.1% | 64.0% | 71.3% | 70.7% |
| Psychic Energy | 70.0% | 68.4% | 90.1% | 75.4% | 99.4% | 62.0% | 70.9% | 69.9% |
| Arven | 71.3% | 70.1% | 91.6% | 71.3% | 99.3% | 64.4% | 70.9% | 70.6% |
| Hop | 68.9% | 67.8% | 90.4% | 76.7% | 99.4% | 62.7% | 70.7% | 70.0% |
| Telepathic Psychic Energy | 68.5% | 67.9% | 91.0% | 73.5% | 99.4% | 62.5% | 69.7% | 69.3% |
| Lillie's Determination | 68.3% | 67.2% | 89.8% | 73.4% | 99.2% | 64.7% | 69.3% | 69.6% |
| Clefairy | 68.7% | 67.7% | 89.7% | 67.0% | 99.4% | 63.9% | 67.9% | 68.4% |
| Maximum Belt | 68.3% | 67.7% | 89.8% | 59.0% | 99.4% | 63.0% | 65.4% | 66.6% |

Going first / second. Same order.

| Cut | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| **lock** | 74.0/70.2 | 73.2/69.7 | 81.0/74.0 | 66.4/62.9 |
| Clefable CLC | 73.6/70.2 | 71.4/67.1 | 82.0/77.4 | 67.6/63.7 |
| Seeker | 75.3/68.0 | 71.2/68.4 | 81.0/76.2 | 67.7/60.2 |
| Iono | 73.0/68.7 | 73.5/69.3 | 79.6/75.0 | 66.7/64.4 |
| Boss's Orders | 73.0/69.7 | 72.3/69.3 | 80.9/73.1 | 69.3/62.8 |
| Energy Switch | 74.9/68.8 | 73.0/68.9 | 79.3/72.2 | 67.5/60.9 |
| Switch | 71.0/71.0 | 71.1/68.9 | 80.1/75.6 | 70.0/60.8 |
| Clefable (Prankish) | 71.8/70.4 | 69.8/71.1 | 79.2/74.4 | 66.6/62.5 |
| Nest Ball | 71.8/72.8 | 71.2/70.0 | 78.6/71.8 | 68.3/63.3 |
| Poké Pad | 74.7/68.5 | 71.3/69.6 | 79.3/72.4 | 67.4/61.5 |
| Night Stretcher | 73.0/69.8 | 70.8/69.9 | 79.3/71.7 | 65.8/61.3 |
| Battle Cage | 72.3/68.1 | 71.6/66.9 | 80.8/75.5 | 67.7/61.5 |
| Mewtwo ex | 74.2/70.6 | 69.8/67.8 | 77.1/73.3 | 68.2/64.2 |
| Lillie | 71.2/69.3 | 70.8/67.2 | 78.8/75.0 | 65.8/61.9 |
| Buddy-Buddy Poffin | 74.1/68.6 | 71.2/67.1 | 77.7/71.8 | 68.0/64.2 |
| Clefable ex | 70.0/69.1 | 70.6/66.6 | 80.7/72.8 | 67.6/60.6 |
| Psychic Energy | 70.0/68.4 | 72.0/64.5 | 78.1/72.6 | 63.6/60.3 |
| Arven | 72.9/69.6 | 71.0/69.2 | 75.0/67.7 | 66.5/62.3 |
| Hop | 70.3/67.5 | 69.4/66.3 | 81.1/72.3 | 65.5/59.8 |
| Telepathic Psychic Energy | 71.1/66.0 | 70.3/65.6 | 77.4/69.4 | 63.6/61.4 |
| Lillie's Determination | 69.6/67.0 | 69.3/65.0 | 77.7/69.3 | 67.3/62.0 |
| Clefairy | 72.0/65.5 | 67.8/67.7 | 71.6/62.4 | 67.9/60.3 |
| Maximum Belt | 70.1/66.5 | 68.5/66.8 | 66.1/51.7 | 64.7/61.3 |

## What the ranking says

The two-stadium lock is the best `wComp`, 73.4%. No cut is above it. The closest third copy replaces Clefable CLC and lands at 73.2% (−0.2). That row is the best `wAll` (72.5% against the lock's 72.3%) and the best D60 (79.7% against 77.6%, +2.1). Hedrick is 69.3% against the lock's 71.5% (−2.2). T60 is 71.9% against 72.1%.

No row is ahead of the lock on T60, Hedrick, and D60 at the same time. T60 72.5% is one Mewtwo ex. Hedrick 71.5% stays with two stadiums. G 66.1% is shared by one Mewtwo ex and one Buddy-Buddy Poffin.

On the three-stadium rows the stadium is played in about 1,500–2,300 games per foe. The two-stadium lock already plays it in 1,160–1,731 games per foe, and the Party pivot is 259 / 280 / 475 of 3,000 T60 / Hedrick / D60 games.

## Conclusion

A third Moonlight Stadium does not raise the weighted win rate. `SET_C60_NAMES` stays at two. The search stops here; a fourth copy was not run.
