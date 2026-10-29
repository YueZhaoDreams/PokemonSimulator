# Doll, Sleepy Voice Igglybuff

Printed text: once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends. The sentence does not say the Active Spot, so a Benched Igglybuff can use it. Doll uses it when that Active is not already Asleep. The turn then has no attack. Slumbering Forest is the wake check that is already in the list.

- **Seed**: `20261029`
- **Screen games per seat**: 40
- **Confirm games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 1542.8s

Each step adds one Sleepy Voice Igglybuff. The confirm is 400 games per seat. A cut higher than that step's baseline is the next list. Four is the maximum. This sample is not the 1000-game holdout.

## Copy 1

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 53.0% | 1.47% | +0.0% | 62.2% | 6.2% | 0.00 | 0.00 | 4.60 |
| Lillie's Poké Doll | 50.5% | 1.62% | -2.5% | 57.9% | 2.5% | 9.19 | 4.62 | 4.09 |
| Cleffa | 50.2% | 1.56% | -2.8% | 58.5% | 5.0% | 8.99 | 4.46 | 4.26 |
| Rescue Carrier | 49.5% | 1.63% | -3.5% | 57.5% | 7.5% | 9.22 | 4.66 | 4.43 |
| Snorlax Doll | 49.5% | 1.60% | -3.5% | 57.3% | 1.2% | 9.13 | 4.57 | 4.46 |
| Level Ball | 49.2% | 1.63% | -3.9% | 56.3% | 10.0% | 8.43 | 4.28 | 4.27 |
| Slumbering Forest | 49.0% | 1.59% | -4.0% | 56.3% | 6.2% | 9.24 | 4.56 | 4.45 |
| Switch | 49.0% | 1.59% | -4.1% | 56.7% | 6.2% | 8.96 | 4.44 | 4.44 |
| Nincada | 48.6% | 1.58% | -4.4% | 57.4% | 2.5% | 9.00 | 4.45 | 4.39 |
| Sableye | 48.5% | 1.61% | -4.6% | 56.4% | 6.2% | 8.99 | 4.50 | 4.35 |
| Darkness Energy | 48.2% | 1.57% | -4.8% | 56.2% | 3.8% | 9.51 | 4.73 | 4.40 |
| Black Market | 47.6% | 1.61% | -5.4% | 56.3% | 3.8% | 9.09 | 4.55 | 4.44 |
| Cursed Shovel | 47.4% | 1.55% | -5.6% | 56.2% | 2.5% | 9.33 | 4.62 | 4.43 |
| Mime Jr. | 47.4% | 1.55% | -5.6% | 55.4% | 2.5% | 9.29 | 4.70 | 4.57 |
| Field Blower | 47.0% | 1.54% | -6.0% | 54.4% | 6.2% | 9.45 | 4.70 | 4.48 |
| Team Rocket's Petrel | 47.0% | 1.61% | -6.1% | 55.0% | 3.8% | 9.03 | 4.51 | 4.22 |
| Crushing Hammer | 46.5% | 1.59% | -6.5% | 54.8% | 6.2% | 9.58 | 4.82 | 4.41 |
| Shedinja | 46.4% | 1.55% | -6.6% | 55.4% | 6.2% | 9.09 | 4.48 | 4.28 |
| Smoochum | 46.4% | 1.57% | -6.6% | 55.1% | 5.0% | 9.01 | 4.51 | 4.48 |
| Battle Cage | 46.1% | 1.60% | -6.9% | 54.8% | 5.0% | 8.87 | 4.38 | 4.39 |
| VS Seeker | 45.8% | 1.52% | -7.3% | 54.0% | 0.0% | 9.22 | 4.63 | 4.40 |
| Manaphy | 45.4% | 1.54% | -7.6% | 54.5% | 8.8% | 9.00 | 4.43 | 4.46 |
| Arven | 44.6% | 1.51% | -8.5% | 53.7% | 5.0% | 8.90 | 4.41 | 4.13 |
| Lillie's Determination | 44.5% | 1.59% | -8.5% | 53.3% | 2.5% | 8.84 | 4.36 | 4.17 |
| Robo Substitute Team Flare Gear | 44.3% | 1.58% | -8.8% | 52.6% | 1.2% | 9.26 | 4.60 | 4.14 |
| Puzzle of Time | 43.8% | 1.57% | -9.2% | 53.0% | 3.8% | 9.14 | 4.53 | 4.33 |
| Buddy-Buddy Poffin | 43.5% | 1.57% | -9.5% | 53.4% | 2.5% | 8.41 | 4.20 | 4.45 |
| Life Dew | 42.5% | 1.57% | -10.6% | 51.9% | 2.5% | 8.65 | 4.32 | 4.27 |
| Team Rocket's Handiwork | 41.8% | 1.53% | -11.2% | 51.0% | 1.2% | 9.35 | 4.65 | 4.50 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 53.0% | 0.47% | +0.0% | 61.9% | 6.0% | 0.00 | 0.00 | 4.64 |
| Cleffa | 50.1% | 0.51% | -2.9% | 58.3% | 5.1% | 8.87 | 4.42 | 4.26 |
| Lillie's Poké Doll | 45.7% | 0.50% | -7.3% | 54.6% | 3.9% | 8.97 | 4.47 | 3.99 |

No confirm beat this baseline. Best confirm is Cleffa: weighted 50.1% vs 53.0% (-2.9%; the gap's SE is about 0.69%). The list stays at 0 copies.

| Foe | Baseline | Cleffa | Lillie's Poké Doll |
| :--- | ---: | ---: | ---: |
| Dragapult ex (T60) | 81.2% | 79.6% | 78.6% |
| Hedrick Worlds Dragapult | 55.5% | 61.0% | 53.9% |
| Unlimited Dragapult | 92.1% | 90.1% | 86.9% |
| Cornerstone Ogerpon (D60) | 6.0% | 20.0% | 19.0% |
| Wo-Chien / Floragato (S60) | 70.6% | 60.6% | 57.0% |
| Gholdengo (G) | 54.6% | 48.0% | 45.5% |
| Clefairy / Mewtwo (C60) | 82.9% | 72.6% | 66.3% |
| Set M (Mew ex) | 57.4% | 50.1% | 37.9% |
| Mega Starmie ex (Kudo) | 37.6% | 33.0% | 30.8% |
| Lucario Hariyama | 88.6% | 86.0% | 81.9% |
| Iron Thorns ex | 94.4% | 92.8% | 91.6% |
| Carpet Set H | 11.5% | 5.1% | 3.9% |
| Ambipom Hand Fling | 72.6% | 59.5% | 56.1% |
