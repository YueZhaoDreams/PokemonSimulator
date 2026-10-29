# Mill greedy Luvdisc

Paldea Evolved Luvdisc. Matching searches the deck for up to 2 Supporter cards. Water Pulse does 20 and the opponent's Active is Asleep. Slumbering Forest flips 2 coins between turns and the Pokémon stays Asleep unless both are heads. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Forest and Sweet Sleeping Face are the two protections.

- **Seed**: `20261030`
- **Screen games per seat**: 30
- **Confirm games per seat**: 80
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 399.8s

The ± column is one standard error of that list's weighted rate, measured on the confirm sample. A step keeps the confirm only when the weighted rate rises.

## Greedy path

| Step | Add | Cut | Luvdisc | Weighted | ± | Mean | Worst | Delta | Matching | Asleep | Forest checks | Face blocks | Mill attacks |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | — | — | 0 | 44.8% | 1.1% | 58.8% | 10.6% | +0.0% | 0.00 | 0.00 | 0.86 | 9.07 | 3.31 |

## Decision

No confirm beat the lock. The closest is −Lillie's Poké Doll at 43.8% (-1.1%, difference ±1.6%). Matching averaged 0.21 per game and the opponent fell Asleep 0.09 times per game. Luvdisc saw play in 54% of games. The gap is not a gain, so SET_MILL_NAMES stays the current 60.

Counts on the best sample:

- Luvdisc saw play: 0.00 per game
- Slumbering Forest entered play: 0.52 per game

## Step 1

Screen leader −Rescue Carrier at 44.3%. The list entering this step screened at 44.2%. The top 3 cuts were confirmed at 80 games per seat.

Every legal cut, on the short sample:

| Cut | Screen | Mean | Worst | Delta | Matching | Asleep | Luvdisc | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rescue Carrier | 44.3% | 57.9% | 10.0% | +0.1% | 0.22 | 0.09 | 0.53 | 3.24 |
| Lillie's Poké Doll | 43.9% | 58.1% | 8.3% | -0.3% | 0.22 | 0.11 | 0.53 | 3.30 |
| Level Ball | 43.8% | 57.6% | 6.7% | -0.4% | 0.25 | 0.14 | 0.52 | 3.25 |
| Miss Fortune Sisters | 43.6% | 59.4% | 8.3% | -0.6% | 0.24 | 0.12 | 0.54 | 3.43 |
| Crushing Hammer | 43.0% | 57.8% | 1.7% | -1.2% | 0.27 | 0.13 | 0.56 | 3.26 |
| Counter Catcher | 41.8% | 55.6% | 5.0% | -2.4% | 0.26 | 0.12 | 0.55 | 3.16 |
| Colress's Tenacity | 41.5% | 55.3% | 5.0% | -2.7% | 0.23 | 0.09 | 0.54 | 3.16 |
| Reversal Energy | 41.4% | 57.2% | 8.3% | -2.9% | 0.17 | 0.10 | 0.52 | 3.24 |
| Double Turbo Energy | 41.2% | 54.9% | 11.7% | -3.1% | 0.23 | 0.12 | 0.52 | 3.17 |
| Ignition Energy | 40.6% | 55.9% | 3.3% | -3.7% | 0.20 | 0.10 | 0.53 | 3.24 |
| Buddy-Buddy Poffin | 40.5% | 55.5% | 5.0% | -3.7% | 0.25 | 0.11 | 0.50 | 3.15 |
| Wally | 40.4% | 54.5% | 8.3% | -3.8% | 0.24 | 0.11 | 0.57 | 3.21 |
| Boss's Orders | 39.9% | 54.5% | 5.0% | -4.3% | 0.21 | 0.09 | 0.54 | 3.29 |
| Water Energy | 39.6% | 54.5% | 11.7% | -4.7% | 0.24 | 0.06 | 0.55 | 3.26 |
| Team Rocket's Handiwork | 38.3% | 53.5% | 3.3% | -5.9% | 0.24 | 0.11 | 0.53 | 2.88 |

| Cut | Screen | Confirmed | ± | Mean | Worst | Delta | Matching | Asleep | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Lillie's Poké Doll | 43.9% | 43.8% | 1.1% | 58.8% | 9.4% | -1.1% | 0.21 | 0.09 | 3.31 |
| Rescue Carrier | 44.3% | 43.2% | 1.1% | 57.5% | 6.9% | -1.7% | 0.23 | 0.11 | 3.27 |
| Level Ball | 43.8% | 40.5% | 1.1% | 55.4% | 4.4% | -4.4% | 0.23 | 0.12 | 3.21 |

No confirm in this step was higher than the list already kept. The search stopped.

Confirmed matchups. Each cell is the mean of the two seats, then the delta against the lock.

| Foe | Lock | −Lillie's Poké Doll | −Rescue Carrier | −Level Ball |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 70.6% | 76.2% (+5.6%) | 72.5% (+1.9%) | 73.1% (+2.5%) |
| Hedrick Worlds Dragapult | 64.4% | 66.2% (+1.9%) | 60.0% (-4.4%) | 58.1% (-6.2%) |
| Unlimited Dragapult | 86.2% | 86.2% (+0.0%) | 90.6% (+4.4%) | 86.2% (+0.0%) |
| Cornerstone Ogerpon (D60) | 10.6% | 9.4% (-1.3%) | 6.9% (-3.8%) | 4.4% (-6.3%) |
| Wo-Chien / Floragato (S60) | 66.9% | 66.9% (+0.0%) | 65.0% (-1.9%) | 62.5% (-4.4%) |
| Gholdengo (G) | 41.2% | 38.7% (-2.5%) | 35.0% (-6.2%) | 28.7% (-12.5%) |
| Clefairy / Mewtwo (C60) | 45.6% | 34.4% (-11.2%) | 44.4% (-1.3%) | 42.5% (-3.1%) |
| Set M (Mew ex) | 25.6% | 22.5% (-3.1%) | 24.4% (-1.2%) | 25.6% (+0.0%) |
| Mega Starmie ex (Kudo) | 38.1% | 40.6% (+2.5%) | 43.8% (+5.6%) | 31.2% (-6.9%) |
| Lucario Hariyama | 80.0% | 81.9% (+1.9%) | 78.1% (-1.9%) | 77.5% (-2.5%) |
| Iron Thorns ex | 94.4% | 90.6% (-3.7%) | 87.5% (-6.9%) | 90.6% (-3.7%) |
| Carpet Set H | 43.8% | 53.1% (+9.4%) | 42.5% (-1.2%) | 42.5% (-1.3%) |
| Ambipom Hand Fling | 96.2% | 97.5% (+1.3%) | 97.5% (+1.3%) | 97.5% (+1.3%) |

## Foes at the best sample

| Foe | A | B | Mean | Delta vs lock |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 66.2% | 75.0% | 70.6% | +0.0% |
| Hedrick Worlds Dragapult | 70.0% | 58.8% | 64.4% | +0.0% |
| Unlimited Dragapult | 87.5% | 85.0% | 86.2% | +0.0% |
| Cornerstone Ogerpon (D60) | 11.2% | 10.0% | 10.6% | +0.0% |
| Wo-Chien / Floragato (S60) | 66.2% | 67.5% | 66.9% | +0.0% |
| Gholdengo (G) | 36.2% | 46.2% | 41.2% | +0.0% |
| Clefairy / Mewtwo (C60) | 40.0% | 51.2% | 45.6% | +0.0% |
| Set M (Mew ex) | 25.0% | 26.2% | 25.6% | +0.0% |
| Mega Starmie ex (Kudo) | 38.8% | 37.5% | 38.1% | +0.0% |
| Lucario Hariyama | 81.2% | 78.8% | 80.0% | +0.0% |
| Iron Thorns ex | 93.8% | 95.0% | 94.4% | +0.0% |
| Carpet Set H | 41.2% | 46.2% | 43.8% | +0.0% |
| Ambipom Hand Fling | 97.5% | 95.0% | 96.2% | +0.0% |
