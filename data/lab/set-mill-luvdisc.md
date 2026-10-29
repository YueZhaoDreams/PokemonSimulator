# Mill greedy Luvdisc

Paldea Evolved Luvdisc. Matching searches the deck for up to 2 Supporter cards. Water Pulse does 20 and the opponent's Active is Asleep. Slumbering Forest flips 2 coins between turns and the Pokémon stays Asleep unless both are heads. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Forest and Sweet Sleeping Face are the two protections. Water Pulse comes up in a spread match while Forest is in play and the opponent is awake, and in a wall match when the Active would be Knocked Out. A paid Wugtrio mills once that Pokémon is Asleep. Retreat discards Energy, so a paid Wugtrio stays unless Undersea would still be paid or that Active would be Knocked Out.

- **Seed**: `20261031`
- **Screen games per seat**: 400
- **Confirm games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 3559.0s

The ± column is one standard error of that list's weighted rate, measured on the confirm sample. A step keeps the confirm only when the gain is larger than one standard error of the difference.

## Greedy path

| Step | Add | Cut | Luvdisc | Weighted | ± | Mean | Worst | Delta | Matching | Asleep | Forest checks | Face blocks | Mill attacks |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | — | — | 0 | 42.6% | 0.5% | 57.4% | 8.4% | +0.0% | 0.00 | 0.00 | 0.94 | 10.30 | 3.30 |

## Decision

No confirm beat the lock by more than one standard error. The closest is −Wally at 42.6% (+0.1%, difference ±0.7%). Matching averaged 0.30 per game and the opponent fell Asleep 0.41 times per game. Luvdisc saw play in 75% of games. SET_MILL_NAMES stays the current 60.

Counts on the best sample:

- Luvdisc saw play: 0.00 per game
- Slumbering Forest entered play: 0.52 per game

## Step 1

Screen leader −Wally at 42.6%. The list entering this step screened at 42.6%. The top 3 cuts were confirmed at 400 games per seat.

Every legal cut:

| Cut | Screen | Mean | Worst | Delta | Matching | Asleep | Luvdisc | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wally | 42.6% | 56.9% | 11.0% | +0.1% | 0.30 | 0.41 | 0.75 | 3.16 |
| Level Ball | 41.8% | 56.2% | 10.5% | -0.8% | 0.30 | 0.43 | 0.73 | 3.14 |
| Boss's Orders | 41.5% | 55.9% | 10.4% | -1.0% | 0.29 | 0.40 | 0.75 | 3.18 |
| Buddy-Buddy Poffin | 41.4% | 55.7% | 11.1% | -1.2% | 0.29 | 0.38 | 0.71 | 3.16 |
| Rescue Carrier | 41.3% | 56.1% | 9.2% | -1.3% | 0.30 | 0.40 | 0.75 | 3.17 |
| Team Rocket's Handiwork | 41.2% | 55.8% | 10.0% | -1.4% | 0.28 | 0.41 | 0.74 | 2.98 |
| Crushing Hammer | 41.0% | 55.4% | 9.9% | -1.6% | 0.30 | 0.39 | 0.75 | 3.15 |
| Counter Catcher | 40.9% | 55.1% | 11.1% | -1.7% | 0.28 | 0.39 | 0.74 | 3.16 |
| Colress's Tenacity | 40.8% | 55.1% | 11.1% | -1.8% | 0.29 | 0.38 | 0.74 | 3.11 |
| Ignition Energy | 40.7% | 55.3% | 9.1% | -1.9% | 0.30 | 0.43 | 0.75 | 3.08 |
| Water Energy | 40.7% | 55.6% | 9.9% | -1.9% | 0.30 | 0.32 | 0.75 | 3.13 |
| Miss Fortune Sisters | 40.2% | 55.0% | 9.5% | -2.4% | 0.28 | 0.40 | 0.74 | 3.24 |
| Lillie's Poké Doll | 40.1% | 55.1% | 7.8% | -2.5% | 0.29 | 0.40 | 0.74 | 3.20 |
| Double Turbo Energy | 39.9% | 54.6% | 8.6% | -2.7% | 0.27 | 0.38 | 0.75 | 3.09 |
| Reversal Energy | 39.4% | 54.2% | 7.5% | -3.1% | 0.28 | 0.40 | 0.75 | 3.07 |

| Cut | Screen | Confirmed | ± | Mean | Worst | Delta | Matching | Asleep | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wally | 42.6% | 42.6% | 0.5% | 56.9% | 11.0% | +0.1% | 0.30 | 0.41 | 3.16 |
| Level Ball | 41.8% | 41.8% | 0.5% | 56.2% | 10.5% | -0.8% | 0.30 | 0.43 | 3.14 |
| Boss's Orders | 41.5% | 41.5% | 0.5% | 55.9% | 10.4% | -1.0% | 0.29 | 0.40 | 3.18 |

No confirm cleared one standard error over the list already kept. The search stopped.

Confirmed matchups. Each cell is the mean of the two seats, then the delta against the lock.

| Foe | Lock | −Wally | −Level Ball | −Boss's Orders |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 73.6% | 64.8% (-8.9%) | 63.0% (-10.6%) | 62.5% (-11.1%) |
| Hedrick Worlds Dragapult | 60.4% | 60.5% (+0.1%) | 59.9% (-0.5%) | 57.4% (-3.0%) |
| Unlimited Dragapult | 86.2% | 84.9% (-1.4%) | 86.6% (+0.4%) | 85.6% (-0.6%) |
| Cornerstone Ogerpon (D60) | 8.4% | 11.0% (+2.6%) | 10.5% (+2.1%) | 10.4% (+2.0%) |
| Wo-Chien / Floragato (S60) | 71.9% | 68.9% (-3.0%) | 66.5% (-5.4%) | 67.8% (-4.1%) |
| Gholdengo (G) | 30.2% | 31.4% (+1.1%) | 33.4% (+3.1%) | 29.4% (-0.9%) |
| Clefairy / Mewtwo (C60) | 41.6% | 40.0% (-1.6%) | 36.5% (-5.1%) | 34.0% (-7.6%) |
| Set M (Mew ex) | 24.4% | 22.0% (-2.4%) | 22.7% (-1.6%) | 23.8% (-0.6%) |
| Mega Starmie ex (Kudo) | 35.5% | 37.6% (+2.1%) | 34.0% (-1.5%) | 37.6% (+2.1%) |
| Lucario Hariyama | 82.1% | 79.9% (-2.3%) | 79.4% (-2.8%) | 81.0% (-1.1%) |
| Iron Thorns ex | 90.3% | 92.6% (+2.4%) | 91.9% (+1.6%) | 90.8% (+0.5%) |
| Carpet Set H | 45.1% | 51.4% (+6.2%) | 51.6% (+6.5%) | 52.2% (+7.1%) |
| Ambipom Hand Fling | 96.1% | 95.2% (-0.9%) | 94.2% (-1.9%) | 94.6% (-1.5%) |

## Foes at the best sample

| Foe | A | B | Mean | Delta vs lock |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 73.2% | 74.0% | 73.6% | +0.0% |
| Hedrick Worlds Dragapult | 62.0% | 58.8% | 60.4% | +0.0% |
| Unlimited Dragapult | 86.8% | 85.8% | 86.2% | +0.0% |
| Cornerstone Ogerpon (D60) | 9.5% | 7.2% | 8.4% | +0.0% |
| Wo-Chien / Floragato (S60) | 69.8% | 74.0% | 71.9% | +0.0% |
| Gholdengo (G) | 33.5% | 27.0% | 30.2% | +0.0% |
| Clefairy / Mewtwo (C60) | 40.0% | 43.2% | 41.6% | +0.0% |
| Set M (Mew ex) | 24.5% | 24.2% | 24.4% | +0.0% |
| Mega Starmie ex (Kudo) | 33.5% | 37.5% | 35.5% | +0.0% |
| Lucario Hariyama | 81.2% | 83.0% | 82.1% | +0.0% |
| Iron Thorns ex | 89.5% | 91.0% | 90.3% | +0.0% |
| Carpet Set H | 46.2% | 44.0% | 45.1% | +0.0% |
| Ambipom Hand Fling | 95.8% | 96.5% | 96.1% | +0.0% |
