# C60: one Seeker in place of every distinct card

Date: 2026-09-26
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_seeker_cuts.py`
Raw: `data/lab/set-c60-seeker-cuts.json`
Elapsed: 1546s

The live lock is `SET_C60_NAMES`. Each row removes exactly one copy of one printed name and adds one Seeker. The other 59 cards stay. The Iono row and the Clefable ex row match [set-c60-seeker-lines.md](set-c60-seeker-lines.md) on this seed.

Party plays the same five Seeker lines (save a damaged benched ex, reline a full Bench, double Prankish from two Benched Clefairies, knock out the Active when the opponent has one Bench Pokémon, fuel Shooting Moons from Bench Energy). The opponent chooses their own Bench Pokémon.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 68% has a binomial SE of about 0.8 pp.

## Win rate

The lock is the first row. Every other row is one copy swapped for Seeker, sorted by `wComp`. Energy Switch (68.46%) and Arven (68.45%) print as 68.5% and sit just under the lock (68.55%).

| Cut for Seeker | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **lock** | 68.3% | 63.5% | 89.8% | 76.8% | **99.9%** | 65.8% | 68.5% | 69.5% |
| Mega Clefable ex | **72.4%** | 66.6% | 90.8% | 77.8% | 99.5% | 61.0% | **71.5%** | 70.3% |
| Ultra Ball | 71.3% | **66.8%** | 90.0% | 77.7% | 99.8% | 66.4% | 71.1% | 71.4% |
| Clefable CLC | 72.1% | 65.2% | **91.1%** | 77.7% | 99.5% | 67.2% | 70.8% | **71.4%** |
| Mewtwo ex | 71.2% | 65.2% | 90.5% | 76.0% | 99.2% | 68.6% | 70.0% | 71.2% |
| Boss's Orders | 67.3% | 66.6% | 89.9% | 77.7% | 99.4% | 65.7% | 69.7% | 70.2% |
| Clefable (Prankish) | 68.9% | 64.3% | 90.7% | **78.7%** | 99.5% | 65.5% | 69.6% | 70.1% |
| Poké Pad | 69.2% | 65.0% | 89.5% | 77.2% | 99.6% | 66.2% | 69.5% | 70.2% |
| Night Stretcher | 68.7% | 65.5% | 89.1% | 76.4% | 99.5% | 68.1% | 69.4% | 70.6% |
| Iono | 68.8% | 65.5% | 89.5% | 74.6% | 99.6% | **69.0%** | 68.9% | 70.5% |
| Lillie | 68.9% | 64.6% | 89.2% | 75.6% | 99.6% | 64.3% | 68.9% | 69.3% |
| Buddy-Buddy Poffin | 69.6% | 63.3% | 89.6% | 75.6% | 99.6% | 65.7% | 68.6% | 69.5% |
| Energy Switch | 68.0% | 63.9% | 90.0% | 76.2% | 99.6% | 68.2% | 68.5% | 70.0% |
| Arven | 69.2% | 65.3% | 89.2% | 72.4% | 99.7% | 66.9% | 68.5% | 69.6% |
| Clefable ex | 67.4% | 62.8% | 89.9% | 78.6% | 99.6% | 65.9% | 68.4% | 69.4% |
| Psychic Energy | 68.5% | 63.5% | 89.5% | 75.7% | 99.5% | 63.9% | 68.3% | 68.8% |
| Nest Ball | 68.4% | 63.5% | 90.5% | 75.2% | 99.1% | 66.9% | 68.1% | 69.5% |
| Battle Cage | 66.3% | 63.8% | 88.5% | 76.6% | 99.7% | 66.4% | 67.9% | 69.1% |
| Switch | 68.0% | 63.6% | 90.1% | 73.6% | 99.5% | 64.9% | 67.7% | 68.7% |
| Lillie's Determination | 66.4% | 63.5% | 89.3% | 75.8% | 99.4% | 63.1% | 67.6% | 68.1% |
| Hop | 67.1% | 62.5% | 89.0% | 75.0% | 99.2% | 64.6% | 67.3% | 68.3% |
| Telepathic Psychic Energy | 66.9% | 62.6% | 88.8% | 74.5% | 99.6% | 64.4% | 67.1% | 68.1% |
| Clefairy | 68.1% | 64.3% | 89.5% | 67.2% | 99.5% | 64.1% | 66.4% | 67.5% |
| Maximum Belt | 66.8% | 64.8% | 88.5% | 57.0% | 99.5% | 63.3% | 63.5% | 65.3% |

Going first / second. The lock is the first row.

| Cut | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| **lock** | 69.5/67.2 | 65.6/61.4 | 79.1/74.4 | 68.0/63.7 |
| Mega Clefable ex | 73.8/71.0 | 66.7/66.5 | 80.6/75.1 | 62.6/59.3 |
| Ultra Ball | 72.2/70.4 | 66.8/66.9 | 78.7/76.8 | 68.5/64.4 |
| Clefable CLC | 73.3/71.0 | 65.8/64.6 | 79.8/75.5 | 69.6/64.8 |
| Mewtwo ex | 71.8/70.5 | 66.4/64.0 | 77.9/74.3 | 70.1/67.1 |

## What the ranking says

Mega Clefable ex is the highest `wComp` (+2.9, to 71.5%). T60 is 72.4% and Hedrick is 66.6%. G is 61.0%, down 4.8 from the lock, and G is outside `wComp`. Shooting Moons fuel is 0 on this row because the Mega was the card removed. That row is the hard-three list, and the mirror is the cost.

Ultra Ball is +2.6 `wComp` (71.1%) and +1.9 `wAll` (71.4%). T60, Hedrick, D60, and G are all above the lock (71.3, 66.8, 77.7, 66.4). The second Ultra Ball is the copy the scripted lines can spare: Seeker fires in 3,282 games across the six foes, the most of any row.

Clefable CLC (Metronome) is +2.2 `wComp` (70.8%) and the highest `wAll` (71.42%, against Ultra Ball's 71.38%). T60 is 72.1%, UNL is 91.1%, G is 67.2%. Hedrick is +1.7. Both of these rows move every matchup that the earlier Iono cut had to trade off.

Mewtwo ex is +1.5 `wComp`. G is the best non-Iono mirror in the matrix (68.6%). D60 dips to 76.0%.

The earlier two cuts stay where they were. Iono is +0.4 `wComp`, with Hedrick +2.0 and G +3.2 paid for by D60 −2.2. One Clefable ex is −0.1 `wComp`, with D60 +1.8 and T60 −1.0. Both are inside a point of the lock on the weighted score.

Cutting the only Prankish zeroes double Prankish. That row still beats the lock on `wComp` (69.6%) through the ex save and the one-bench KO, and D60 is the best Demolish cell (78.7%). G is flat.

## Lines that stay rare

Counts are games with at least one success, summed over the six foes (18,000 games).

| Cut | Seeker | One-bench KO | Save ex | Double Prankish | Reline | Moons fuel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **lock** | 0 | 0 | 0 | 0 | 0 | 0 |
| Ultra Ball | 3282 | 1295 | 1135 | 851 | 18 | 5 |
| Clefable CLC | 2988 | 1099 | 1067 | 829 | 9 | 4 |
| Iono | 2884 | 1147 | 980 | 760 | 18 | 8 |
| Mega Clefable ex | 2767 | 1056 | 923 | 804 | 4 | 0 |
| Mewtwo ex | 2658 | 1063 | 903 | 692 | 6 | 6 |
| Clefable (Prankish) | 2268 | 1174 | 1106 | 0 | 0 | 4 |

Reline stays under 21 games on every cut. Four Clefairy still means an open Bench, or another Clefairy, is the usual way onto ex or Mega. Shooting Moons fuel stays in single digits. The line is in the script; the turn where Mega can pay and still needs Bench Energy almost never has Seeker left to spend.

## Floor

Maximum Belt is the bottom row. D60 falls to 57.0% (first 62.5 / second 51.5). The Belt is the Demolish card.

Clefairy (4 → 3) is the other clear loss: D60 67.2%, `wComp` 66.4%. Hop, Lillie's Determination, and Telepathic Psychic Energy each cost more than a point of `wComp`.

## Lock

`SET_C60_NAMES` stays the live list. Mega is the highest hard-three weight, and G falls to 61.0%. Ultra Ball and the one Metronome Clefable are the cuts that rise on T60, Hedrick, D60, and G together. This note records the matrix. It does not change the 60.
