# Celebi Mill, Slumbering Forest

The four Litwick are Guardians Rising Flickering Flames. The printed sentence is: Your opponent's Active Pokémon is now Asleep. Roast uses that attack when the opponent's Active Pokémon is not Asleep and a Litwick can pay it. Time Distortion waits until that Active is Asleep, or until Flickering Flames cannot be paid.

Printed stadium sentence: If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep.

Roast plays Slumbering Forest when this turn does not need Broken Time-Space. Broken Time-Space is played when a Pokémon played this turn still has to evolve. One stadium replaces the other.

Each step tries every other card as the one copy to replace with one Slumbering Forest. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way. The Litwick print is not one of the swaps.

- **Seed**: `20261101`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen Sisters loss weights. The same weights as the Celebi Mill lock.
- **Elapsed**: 10461.8s

This sample is not the 1000-game holdout. This script does not edit the locked list.

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 Forest | 0 | — | 44.0% | 0.5% | 54.9% | 10.5% | +0.0% | 2.18 | 0.00 | 0.00 | 17.04 | 3.84 | 91.4% |
| 1 Forest | 1 | Rescue Scarf | 45.0% | 0.5% | 55.9% | 10.4% | +1.0% | 2.01 | 1.46 | 0.45 | 17.11 | 3.79 | 92.0% |
| 2 Forest | 2 | Evolution Incense | 46.3% | 0.5% | 57.3% | 12.6% | +2.3% | 1.98 | 2.62 | 0.75 | 17.03 | 3.73 | 91.7% |

## Decision

The search kept 2 Slumbering Forest. Weighted win rate 46.3% against the zero-Forest list at 44.0% (+2.3%, ± 0.5%).

The locked Celebi Mill list is not changed by this search.

Counts on the kept list:

- Litwick ×4
- Lampent ×4
- Chandelure ×4
- Celebi ◇ ×1
- Pichu ×3
- Arven ×4
- Team Rocket's Petrel ×2
- Buddy-Buddy Poffin ×2
- Energy Search ×3
- Rescue Scarf ×3
- Dawn ×4
- Level Ball ×2
- Broken Time-Space ×2
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×2
- Hyper Aroma ×1
- Jacq ×1
- Hop ×4
- Devolution Spray ×4
- Slumbering Forest ×2

## Step 1

List entering this step: weighted 44.0% ± 0.5%. Each row replaces one copy of that card with one Slumbering Forest.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rescue Scarf | 4 | 45.0% | 0.5% | 55.9% | 10.4% | +1.0% | 2.01 | 1.46 | 0.45 | 17.11 | 3.79 | 92.0% |
| Energy Search | 3 | 44.7% | 0.5% | 55.7% | 11.5% | +0.7% | 2.05 | 1.53 | 0.45 | 17.01 | 3.70 | 91.9% |
| Broken Time-Space | 2 | 44.6% | 0.5% | 55.6% | 9.5% | +0.6% | 2.00 | 1.50 | 0.45 | 17.03 | 3.81 | 91.8% |
| Devolution Spray | 4 | 44.5% | 0.5% | 55.2% | 11.6% | +0.5% | 2.09 | 1.51 | 0.45 | 16.70 | 3.93 | 92.1% |
| Evolution Incense | 3 | 44.3% | 0.5% | 55.1% | 11.8% | +0.3% | 2.03 | 1.55 | 0.45 | 16.92 | 3.77 | 91.3% |
| Fire Energy | 7 | 44.3% | 0.5% | 55.5% | 10.9% | +0.3% | 1.91 | 1.36 | 0.43 | 17.11 | 3.78 | 91.5% |
| Team Rocket's Petrel | 2 | 44.2% | 0.5% | 55.2% | 10.9% | +0.2% | 2.05 | 1.45 | 0.43 | 16.90 | 3.79 | 91.9% |
| Dawn | 4 | 44.2% | 0.5% | 54.7% | 10.6% | +0.2% | 2.09 | 1.53 | 0.44 | 16.74 | 3.69 | 91.0% |
| Level Ball | 2 | 44.1% | 0.5% | 55.4% | 10.5% | +0.1% | 2.06 | 1.43 | 0.43 | 16.80 | 3.74 | 90.6% |
| Jacq | 1 | 44.1% | 0.5% | 55.3% | 10.0% | +0.1% | 2.08 | 1.49 | 0.44 | 16.86 | 3.75 | 91.8% |
| Buddy-Buddy Poffin | 2 | 44.0% | 0.5% | 55.2% | 11.0% | -0.0% | 1.98 | 1.46 | 0.44 | 16.71 | 3.71 | 90.3% |
| Arven | 4 | 43.9% | 0.5% | 54.6% | 9.0% | -0.1% | 2.06 | 1.55 | 0.45 | 16.88 | 3.74 | 91.7% |
| Chandelure | 4 | 43.6% | 0.5% | 54.7% | 8.8% | -0.3% | 2.04 | 1.51 | 0.44 | 16.84 | 3.70 | 91.8% |
| Hop | 4 | 43.6% | 0.5% | 54.5% | 11.6% | -0.4% | 2.04 | 1.48 | 0.42 | 16.76 | 3.73 | 91.9% |
| Pichu | 3 | 42.0% | 0.5% | 53.7% | 10.5% | -1.9% | 2.06 | 1.44 | 0.44 | 16.25 | 3.53 | 90.2% |
| Hyper Aroma | 1 | 41.4% | 0.5% | 52.8% | 8.5% | -2.5% | 2.45 | 1.76 | 0.45 | 15.82 | 3.21 | 91.4% |
| Lampent | 4 | 40.9% | 0.5% | 52.1% | 9.6% | -3.0% | 2.84 | 2.18 | 0.46 | 15.51 | 2.91 | 91.3% |
| Hisuian Heavy Ball | 1 | 40.6% | 0.5% | 51.8% | 9.1% | -3.4% | 1.79 | 1.38 | 0.45 | 16.38 | 3.54 | 90.4% |
| Litwick | 4 | 36.8% | 0.4% | 48.8% | 7.6% | -7.2% | 1.43 | 1.04 | 0.43 | 15.39 | 3.63 | 88.3% |
| Celebi ◇ | 1 | 17.7% | 0.3% | 30.7% | 1.6% | -26.3% | 2.44 | 1.67 | 0.49 | 11.54 | 0.00 | 91.7% |

Kept −Rescue Scarf at 45.0% (+1.0%).

## Step 2

List entering this step: weighted 45.0% ± 0.5%. Each row replaces one copy of that card with one Slumbering Forest.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Evolution Incense | 3 | 46.3% | 0.5% | 57.3% | 12.6% | +1.3% | 1.98 | 2.62 | 0.75 | 17.03 | 3.73 | 91.7% |
| Broken Time-Space | 2 | 46.1% | 0.5% | 56.9% | 10.8% | +1.1% | 1.96 | 2.69 | 0.74 | 17.16 | 3.77 | 91.7% |
| Buddy-Buddy Poffin | 2 | 45.7% | 0.5% | 56.7% | 11.0% | +0.7% | 1.91 | 2.51 | 0.74 | 16.93 | 3.74 | 90.8% |
| Level Ball | 2 | 45.6% | 0.5% | 56.6% | 10.2% | +0.7% | 1.97 | 2.67 | 0.75 | 16.99 | 3.72 | 91.2% |
| Team Rocket's Petrel | 2 | 45.6% | 0.5% | 56.8% | 8.8% | +0.6% | 1.99 | 2.70 | 0.74 | 17.06 | 3.79 | 91.8% |
| Energy Search | 3 | 45.2% | 0.5% | 56.6% | 11.2% | +0.2% | 1.91 | 2.57 | 0.75 | 17.12 | 3.73 | 91.6% |
| Arven | 4 | 45.1% | 0.5% | 56.3% | 10.8% | +0.2% | 1.98 | 2.65 | 0.75 | 16.87 | 3.70 | 91.3% |
| Fire Energy | 7 | 45.0% | 0.5% | 56.2% | 11.1% | +0.0% | 1.83 | 2.44 | 0.75 | 17.08 | 3.71 | 92.0% |
| Rescue Scarf | 3 | 45.0% | 0.5% | 56.2% | 11.4% | +0.0% | 1.94 | 2.67 | 0.75 | 17.32 | 3.75 | 91.8% |
| Jacq | 1 | 44.8% | 0.5% | 55.9% | 10.9% | -0.2% | 1.98 | 2.71 | 0.75 | 16.96 | 3.72 | 91.7% |
| Dawn | 4 | 44.7% | 0.5% | 56.0% | 9.9% | -0.2% | 1.98 | 2.62 | 0.75 | 16.82 | 3.67 | 91.1% |
| Chandelure | 4 | 44.5% | 0.5% | 55.5% | 11.0% | -0.5% | 1.97 | 2.60 | 0.76 | 16.80 | 3.58 | 92.1% |
| Devolution Spray | 4 | 44.4% | 0.5% | 55.3% | 11.5% | -0.5% | 1.97 | 2.69 | 0.76 | 16.69 | 3.90 | 91.9% |
| Pichu | 3 | 43.7% | 0.5% | 55.0% | 11.8% | -1.2% | 1.94 | 2.58 | 0.75 | 16.57 | 3.60 | 90.4% |
| Hop | 4 | 42.7% | 0.5% | 54.5% | 8.6% | -2.2% | 1.97 | 2.57 | 0.73 | 16.83 | 3.64 | 91.7% |
| Hyper Aroma | 1 | 42.7% | 0.5% | 54.5% | 7.1% | -2.3% | 2.30 | 2.99 | 0.76 | 16.13 | 3.29 | 91.9% |
| Lampent | 4 | 42.1% | 0.5% | 53.0% | 8.4% | -2.9% | 2.70 | 3.83 | 0.77 | 15.58 | 2.87 | 91.4% |
| Hisuian Heavy Ball | 1 | 40.9% | 0.5% | 52.2% | 9.0% | -4.0% | 1.73 | 2.36 | 0.75 | 16.27 | 3.43 | 90.8% |
| Litwick | 4 | 36.8% | 0.4% | 48.8% | 7.9% | -8.2% | 1.38 | 1.89 | 0.74 | 15.48 | 3.61 | 88.6% |
| Celebi ◇ | 1 | 19.0% | 0.3% | 32.2% | 2.8% | -26.0% | 2.33 | 2.88 | 0.81 | 11.77 | 0.00 | 92.6% |

Kept −Evolution Incense at 46.3% (+1.3%).

## Step 3

List entering this step: weighted 46.3% ± 0.5%. Each row replaces one copy of that card with one Slumbering Forest.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flicker | Sleep checks | Forest plays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Fire Energy | 7 | 46.2% | 0.5% | 57.1% | 10.6% | -0.1% | 1.75 | 3.31 | 0.97 | 17.08 | 3.71 | 91.6% |
| Energy Search | 3 | 46.2% | 0.5% | 56.9% | 11.9% | -0.1% | 1.83 | 3.41 | 0.97 | 16.94 | 3.66 | 91.8% |
| Broken Time-Space | 2 | 46.2% | 0.5% | 57.1% | 11.2% | -0.1% | 1.88 | 3.59 | 0.97 | 17.02 | 3.71 | 91.8% |
| Level Ball | 2 | 46.1% | 0.5% | 57.0% | 10.9% | -0.1% | 1.88 | 3.53 | 0.97 | 16.92 | 3.75 | 90.6% |
| Jacq | 1 | 46.0% | 0.5% | 56.7% | 11.1% | -0.3% | 1.92 | 3.49 | 0.99 | 17.03 | 3.69 | 92.2% |
| Evolution Incense | 2 | 45.9% | 0.5% | 56.6% | 12.9% | -0.3% | 1.92 | 3.55 | 0.98 | 17.07 | 3.71 | 92.9% |
| Rescue Scarf | 3 | 45.7% | 0.5% | 56.7% | 11.8% | -0.6% | 1.84 | 3.49 | 0.98 | 17.24 | 3.72 | 92.4% |
| Team Rocket's Petrel | 2 | 45.7% | 0.5% | 56.9% | 10.2% | -0.6% | 1.94 | 3.51 | 0.97 | 17.00 | 3.74 | 92.0% |
| Arven | 4 | 45.6% | 0.5% | 56.2% | 12.8% | -0.7% | 1.93 | 3.53 | 0.98 | 16.96 | 3.68 | 92.2% |
| Hop | 4 | 45.3% | 0.5% | 56.1% | 9.6% | -0.9% | 1.88 | 3.34 | 0.92 | 16.75 | 3.66 | 91.2% |
| Buddy-Buddy Poffin | 2 | 44.8% | 0.5% | 56.0% | 11.1% | -1.4% | 1.85 | 3.50 | 0.96 | 16.74 | 3.62 | 90.6% |
| Chandelure | 4 | 44.4% | 0.5% | 55.2% | 10.0% | -1.9% | 1.88 | 3.50 | 0.97 | 16.63 | 3.52 | 91.4% |
| Devolution Spray | 4 | 44.2% | 0.5% | 55.3% | 8.8% | -2.0% | 1.89 | 3.45 | 0.99 | 16.54 | 3.85 | 92.1% |
| Hyper Aroma | 1 | 44.0% | 0.5% | 55.5% | 8.4% | -2.3% | 2.27 | 4.06 | 0.97 | 16.01 | 3.24 | 91.6% |
| Dawn | 4 | 44.0% | 0.5% | 55.0% | 11.5% | -2.3% | 1.95 | 3.62 | 0.97 | 16.61 | 3.59 | 90.5% |
| Pichu | 3 | 43.5% | 0.5% | 55.0% | 11.8% | -2.8% | 1.89 | 3.43 | 0.98 | 16.25 | 3.50 | 89.8% |
| Lampent | 4 | 43.3% | 0.5% | 53.8% | 9.4% | -3.0% | 2.65 | 4.91 | 0.98 | 15.62 | 2.87 | 91.7% |
| Hisuian Heavy Ball | 1 | 42.0% | 0.5% | 53.2% | 10.6% | -4.3% | 1.73 | 3.27 | 0.97 | 16.23 | 3.43 | 90.5% |
| Litwick | 4 | 38.0% | 0.4% | 49.4% | 9.6% | -8.3% | 1.37 | 2.57 | 0.96 | 15.57 | 3.61 | 89.1% |
| Celebi ◇ | 1 | 20.0% | 0.3% | 32.9% | 3.8% | -26.3% | 2.28 | 3.94 | 1.03 | 11.69 | 0.00 | 92.1% |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs zero Forest |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 43.2% | 48.8% | 46.0% | +1.2% |
| Hedrick Worlds Dragapult | 62.0% | 58.2% | 60.1% | +2.8% |
| Unlimited Dragapult | 66.2% | 67.2% | 66.8% | +7.7% |
| Cornerstone Ogerpon (D60) | 22.8% | 26.2% | 24.5% | +4.6% |
| Wo-Chien / Floragato (S60) | 66.2% | 69.5% | 67.9% | +0.7% |
| Gholdengo (G) | 48.8% | 45.0% | 46.9% | +6.0% |
| Clefairy / Mewtwo (C60) | 54.8% | 62.5% | 58.6% | +2.0% |
| Set M (Mew ex) | 16.5% | 17.8% | 17.1% | -0.4% |
| Mega Starmie ex (Kudo) | 14.0% | 11.2% | 12.6% | +2.1% |
| Lucario Hariyama | 74.5% | 79.2% | 76.9% | +5.1% |
| Iron Thorns ex | 93.8% | 94.2% | 94.0% | +0.6% |
| Carpet Set H | 80.0% | 83.0% | 81.5% | -2.9% |
| Ambipom Hand Fling | 90.2% | 93.2% | 91.8% | +1.2% |

