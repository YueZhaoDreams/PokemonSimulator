# C60: one Moonlight Stadium in place of every distinct card

Date: 2026-09-28
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_moonlight_stadium.py`
Raw: `data/lab/set-c60-moonlight-stadium.json`
Elapsed: 1617s

The lock is the live list (`SET_C60_NAMES`). Every other row removes exactly one copy of one printed name and adds one Moonlight Stadium (Great Encounters 100, `dp4-100`).

Printed text: "The Retreat Cost for each Psychic and Darkness Pokémon (both yours and your opponent's) is 0."

Clefairy is Psychic and retreats for 2. Under this stadium that cost is 0 even with no Energy attached. Party uses it this way: Party, retreat for free (no Energy discarded, Switch stays in hand), promote a benched Clefairy that just received one Psychic, Party again, then attach this turn's energy to the Clefairy that came up. Versus Dragapult, Floragato, or a ready Demolish, the pivot only happens when a Switch is still in hand, so the 60 HP body can hide afterward. Battle Cage is not played over an early Moonlight Stadium, and Moonlight Stadium is not played over a Battle Cage that is already in play. Once six Psychic Energy are in play against Dragapult, Cage replaces Moonlight Stadium.

The discount follows the Pokémon's type, for both players. Mewtwo ex is Lightning, so Psychic Energy on it does not change its retreat. Dragapult ex is Dragon, so its retreat stays 1. A Darkness Pokémon such as Fezandipiti ex retreats for 0. Lost Thunder 188 (Colorless less, and only while Psychic or Darkness Energy is attached) is a different card and is not this row.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp.

## Win rate

Rows are one copy swapped for Moonlight Stadium, sorted by `wComp`. The lock is fourth.

| Cut for Moonlight Stadium | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ultra Ball | 72.6% | 69.1% | 90.7% | 78.1% | 99.6% | 64.0% | **72.7%** | 71.6% |
| Mewtwo ex | 72.7% | **69.9%** | 90.7% | 76.4% | 99.5% | 64.7% | 72.5% | **71.7%** |
| Seeker | 70.3% | 68.4% | 91.6% | **79.5%** | 99.4% | 62.9% | 72.0% | 70.9% |
| **lock** | **73.4%** | 66.8% | 91.2% | 78.0% | 99.5% | 63.3% | 72.0% | 70.9% |
| Clefable CLC | 71.8% | 68.4% | **92.1%** | 77.2% | **99.7%** | 63.0% | 71.9% | 70.8% |
| Boss's Orders | 72.0% | 68.5% | 91.0% | 76.2% | 99.6% | 62.9% | 71.7% | 70.6% |
| Energy Switch | 71.1% | 67.8% | 90.5% | 77.6% | **99.7%** | 60.8% | 71.5% | 69.9% |
| Clefable (Prankish) | 71.1% | 68.0% | 91.2% | 77.1% | **99.7%** | 62.8% | 71.5% | 70.4% |
| Night Stretcher | 71.8% | 68.0% | 90.9% | 76.0% | 99.5% | 61.7% | 71.4% | 70.1% |
| Buddy-Buddy Poffin | 71.2% | 66.8% | 90.2% | 76.4% | **99.7%** | 62.1% | 70.8% | 69.8% |
| Iono | 71.2% | 66.7% | 90.9% | 76.4% | 99.6% | **65.0%** | 70.8% | 70.6% |
| Poké Pad | 71.8% | 66.4% | 89.8% | 75.7% | 99.5% | 62.0% | 70.7% | 69.6% |
| Switch | 70.5% | 67.0% | 90.5% | 76.4% | 99.6% | 62.7% | 70.7% | 69.9% |
| Psychic Energy | 70.2% | 67.8% | 90.1% | 75.2% | 99.4% | 61.5% | 70.6% | 69.4% |
| Nest Ball | 71.3% | 67.7% | 91.0% | 73.8% | 99.3% | 64.0% | 70.5% | 70.1% |
| Battle Cage | 70.2% | 65.9% | 89.5% | 77.3% | 99.4% | 62.9% | 70.4% | 69.7% |
| Clefable ex | 71.4% | 65.2% | 91.3% | 76.1% | 99.5% | 62.9% | 70.1% | 69.6% |
| Hop | 70.1% | 64.5% | 90.2% | 76.4% | **99.7%** | 60.5% | 69.5% | 68.5% |
| Lillie | 69.5% | 65.5% | 91.0% | 75.2% | 99.5% | 61.9% | 69.4% | 68.9% |
| Arven | 71.3% | 66.3% | 89.8% | 71.3% | **99.7%** | 61.3% | 69.3% | 68.5% |
| Lillie's Determination | 68.0% | 66.0% | 90.1% | 74.2% | **99.7%** | 61.2% | 68.9% | 68.2% |
| Telepathic Psychic Energy | 66.8% | 65.8% | 90.7% | 74.9% | **99.7%** | 59.3% | 68.6% | 67.6% |
| Clefairy | 69.2% | 64.9% | 89.5% | 65.7% | 99.2% | 61.4% | 66.5% | 66.7% |
| Maximum Belt | 68.8% | 65.2% | 90.6% | 57.8% | 99.6% | 59.0% | 64.4% | 64.8% |

Going first / second. Same order.

| Cut | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| Ultra Ball | 74.0/71.3 | 70.5/67.8 | 80.7/75.6 | 65.1/63.0 |
| Mewtwo ex | 72.3/73.0 | 70.4/69.4 | 80.0/72.6 | 66.0/63.5 |
| Seeker | 71.5/69.0 | 68.7/68.1 | 82.6/76.4 | 64.3/61.6 |
| **lock** | 74.6/72.2 | 68.8/64.8 | 79.8/76.1 | 64.2/62.4 |
| Clefable CLC | 71.8/71.7 | 70.0/66.7 | 79.3/75.0 | 65.4/60.5 |
| Boss's Orders | 74.1/69.9 | 67.1/69.9 | 79.7/72.7 | 67.2/58.7 |
| Energy Switch | 73.1/69.2 | 67.4/68.3 | 79.2/76.0 | 63.4/58.2 |
| Clefable (Prankish) | 72.9/69.2 | 66.9/69.1 | 79.2/74.9 | 64.2/61.5 |
| Night Stretcher | 74.5/69.0 | 69.0/67.0 | 79.3/72.4 | 62.2/61.3 |
| Buddy-Buddy Poffin | 72.1/70.3 | 67.7/65.8 | 79.3/73.6 | 63.9/60.3 |
| Iono | 72.5/69.7 | 66.4/67.0 | 79.1/73.7 | 67.6/62.4 |
| Poké Pad | 73.8/69.8 | 67.8/65.1 | 79.2/72.2 | 63.0/61.1 |
| Switch | 70.9/70.1 | 67.5/66.5 | 79.1/73.7 | 63.5/61.9 |
| Psychic Energy | 71.3/69.1 | 68.2/67.4 | 78.2/72.2 | 63.0/59.9 |
| Nest Ball | 72.6/70.0 | 68.2/67.1 | 76.7/70.8 | 65.3/62.6 |
| Battle Cage | 71.7/68.7 | 66.0/65.8 | 80.3/74.1 | 65.5/60.3 |
| Clefable ex | 71.6/71.1 | 65.3/65.0 | 78.6/73.7 | 65.6/60.2 |
| Hop | 70.1/70.0 | 66.1/62.8 | 78.1/74.6 | 62.5/58.5 |
| Lillie | 70.6/68.4 | 67.0/63.9 | 78.6/71.6 | 64.6/59.2 |
| Arven | 72.9/69.7 | 67.1/65.5 | 74.7/67.8 | 63.0/59.7 |
| Lillie's Determination | 70.5/65.5 | 66.8/65.2 | 78.3/70.1 | 60.5/61.9 |
| Telepathic Psychic Energy | 67.1/66.5 | 65.6/66.1 | 78.2/71.6 | 60.2/58.5 |
| Clefairy | 72.6/65.4 | 65.0/64.8 | 69.7/61.6 | 62.7/60.1 |
| Maximum Belt | 70.5/67.1 | 65.7/64.6 | 63.5/52.4 | 60.3/57.6 |

## What the ranking says

No row is ahead of the lock on T60, Hedrick, and D60 at the same time. T60 73.4% stays with the lock. The best `wComp` is one Ultra Ball, 72.7% against the lock's 72.0% (+0.7). A single cell near 70% has an SE of about 0.8 pp, so that weighted edge is inside the noise. Hedrick is 69.1% (+2.3) and D60 is 78.1% (+0.2). T60 is 72.6% (−0.8). Going first against T60 is 74.0% against the lock's 74.6%, and going second is 71.3% against 72.2%. G is 64.0% (+0.7). That is not a swap.

Cutting one Mewtwo ex is the best `wAll`, 71.7% against 70.9% (+0.8). Hedrick is 69.9% (+3.1) and G is 64.7% (+1.4). T60 is 72.7% (−0.8) and D60 is 76.4% (−1.6). The Hedrick games are bought by giving up a closer against Demolish.

Cutting Seeker ties the lock on the displayed `wComp` (72.0%) and raises D60 to 79.5% (+1.6). T60 falls to 70.3% (−3.2).

Cutting one Battle Cage drops T60 from 73.4% to 70.2% (−3.2). Cutting Maximum Belt drops D60 from 78.0% to 57.8%. Cutting Clefairy drops D60 to 65.7%. Cutting Switch, which the pivot leaves in hand, drops `wComp` to 70.7% and is the rarest Dragapult pivot in the matrix (70 of 3,000 T60 games).

On the rows that include the stadium, the Party pivot shows up in 70–149 of 3,000 Dragapult games (T60, Hedrick, or UNL), 189–273 of 3,000 D60 games, and 650–841 of 3,000 G games. The stadium itself is played in about 640–1,170 games per foe. Versus Dive the pivot still waits for a Switch, so the 60 HP Clefairy can hide. The retreat itself does not spend that Switch.

## Conclusion

Keep the live C60 list. Moonlight Stadium stays available for any list that actually includes the stadium. It does not earn a slot in `SET_C60_NAMES`.

