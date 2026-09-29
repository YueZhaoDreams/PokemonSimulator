# C60: Latias ex in place of two Moonlight Stadium

Date: 2026-09-29
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_latias_ex.py`
Raw: `data/lab/set-c60-latias-ex.json`
Elapsed: 309s

The lock is the live list (`SET_C60_NAMES`): two Great Encounters Moonlight Stadium and no Ultra Ball. `latias2` replaces both stadiums with Surging Sparks 76 Latias ex. `latias_ultra` replaces them with one Latias ex and one Ultra Ball.

Printed ability, Skyliner: "Your Basic Pokémon in play have no Retreat Cost."
Printed attack, Eon Blade, [P][P][C] 200: "During your next turn, this Pokémon can't attack."

Latias ex is a Basic, so Nest Ball can bench it. Buddy-Buddy Poffin cannot: 210 HP is over 70. Poké Pad cannot: it is a Pokémon ex. The Party plan benches one copy after a Clefairy is out, does not open on it, and does not attach to it ahead of Mewtwo. Eon Blade is legal if Latias ex is forced Active. It is not the closer.

Skyliner is only your Basics, and only while that Pokémon is in play. Clefairy and Mewtwo ex retreat for 0. Clefable, Clefable ex, and Mega Clefable ex still pay their printed Retreat Cost. The opponent's Pokémon do not. Moonlight Stadium zeros Retreat Cost for every Psychic and Darkness Pokémon on both sides, including evolutions, and it does not take a bench slot or give up two prizes.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp. The lock row matches `data/lab/set-c60-moonlight-3.md` on this seed.

## Win rate

| List | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Latias ex + Ultra Ball | **79.5%** | 73.2% | 93.2% | **78.5%** | 99.6% | **76.7%** | **76.9%** | **78.1%** |
| 2 Latias ex | 79.1% | **74.3%** | **93.5%** | 74.1% | **99.7%** | **76.7%** | 75.9% | 77.5% |
| **lock** | 72.1% | 71.5% | 91.4% | 77.6% | 99.2% | 64.6% | 73.4% | 72.3% |

Going first / second. Same order.

| List | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| 1 Latias ex + Ultra Ball | 79.9/79.1 | 73.5/72.8 | 79.9/77.1 | 78.3/75.1 |
| 2 Latias ex | 80.1/78.1 | 74.4/74.1 | 76.6/71.6 | 79.4/74.2 |
| **lock** | 74.0/70.2 | 73.2/69.7 | 81.0/74.0 | 66.4/62.9 |

## What the ranking says

One Latias ex plus one Ultra Ball is ahead of the lock on T60, Hedrick, and D60 at the same time. `wComp` is 76.9% against 73.4% (+3.5). `wAll` is 78.1% against 72.3% (+5.8). T60 is 79.5% against 72.1% (+7.4). Going first against T60 is 79.9% against 74.0%, and going second is 79.1% against 70.2%. Hedrick is 73.2% against 71.5% (+1.7). D60 is 78.5% against 77.6% (+0.9), about one SE. G is 76.7% against 64.6% (+12.1). UNL is 93.2% against 91.4% (+1.8).

Two Latias ex is the best Hedrick (74.3%, +2.8) and the best UNL (93.5%, +2.1). T60 is 79.1% (+7.0). D60 is 74.1% against 77.6% (−3.5). G ties the one-copy row at 76.7%. The second copy is the card that gives D60 away.

Nest Ball benched Latias ex in 1,120–1,379 of 3,000 games. The card saw play in 2,395–2,682 games. The Skyliner pivot showed up in 637 of 3,000 T60 games on the one-copy list (lock Moonlight pivot: 259) and in 2,367 of 3,000 G games (lock: 1,150). Eon Blade connected in 7 of 3,000 T60 games on that list, 6 Hedrick, 0 D60, 15 G. On two copies the attack connected in 16 T60 games and 0 D60 games.

## Conclusion

The measured winner is one Surging Sparks Latias ex (`sv08-076`) and one Ultra Ball in the two Moonlight Stadium slots. `SET_C60_NAMES` is still the two-stadium list.
