# Celebi Mill, Devolution Spray

Printed sentence: Devolve 1 of your evolved Pokémon and put the highest Stage Evolution card on it into your hand. (That Pokémon can't evolve this turn.)

Roast plays it on a Chandelure that Time Distortion will not devolve. That includes a Chandelure in the Active Spot, and a benched Chandelure on a turn Celebi ◇ cannot attack. The sprayed Pokémon cannot evolve on that turn, so the card is replayed on a later turn. Broken Time-Space does not override that sentence.

Each step tries every other card as the one copy to replace with one Devolution Spray. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

- **Seed**: `20261031`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen Sisters loss weights. The same weights as the Celebi Mill lock.
- **Elapsed**: 10884.5s

This sample is not the 1000-game holdout.

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Sprays | Mill cards | Time Distortion | Fired |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 44.7% | 0.5% | 56.6% | 14.4% | +0.0% | 0.00 | 19.68 | 6.38 | 91.9% |
| 1 Devolution Spray | 1 | Broken Time-Space | 45.5% | 0.5% | 57.1% | 14.5% | +0.8% | 0.37 | 20.00 | 6.28 | 92.0% |
| 2 Devolution Spray | 2 | Team Rocket's Petrel | 45.5% | 0.5% | 56.9% | 14.1% | +0.8% | 0.61 | 19.96 | 6.05 | 91.9% |
| 3 Devolution Spray | 3 | Jacq | 45.9% | 0.5% | 57.3% | 16.4% | +1.2% | 0.82 | 19.88 | 5.89 | 91.2% |
| 4 Devolution Spray | 4 | Energy Retrieval | 46.2% | 0.5% | 58.0% | 13.8% | +1.5% | 1.02 | 20.04 | 5.79 | 91.3% |

## Decision

The search kept 4 Devolution Spray. Weighted win rate 46.2% against the locked list at 44.7% (+1.5%, ± 0.5%).

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
- Rescue Scarf ×4
- Dawn ×4
- Level Ball ×2
- Broken Time-Space ×2
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×3
- Hyper Aroma ×1
- Jacq ×1
- Hop ×4
- Devolution Spray ×4

## Step 1

List entering this step: weighted 44.7% ± 0.5%. Each row replaces one copy of that card with one Devolution Spray.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Sprays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Broken Time-Space | 3 | 45.5% | 0.5% | 57.1% | 14.5% | +0.8% | 0.37 | 20.00 | 6.28 | 92.0% |
| Energy Search | 3 | 45.2% | 0.5% | 57.4% | 13.4% | +0.5% | 0.39 | 19.94 | 6.17 | 92.3% |
| Team Rocket's Petrel | 3 | 45.2% | 0.5% | 57.0% | 14.6% | +0.5% | 0.36 | 19.92 | 6.20 | 92.3% |
| Jacq | 2 | 45.2% | 0.5% | 57.0% | 14.3% | +0.5% | 0.38 | 19.87 | 6.19 | 92.3% |
| Dawn | 4 | 45.1% | 0.5% | 56.6% | 14.8% | +0.4% | 0.38 | 19.60 | 6.10 | 91.2% |
| Energy Retrieval | 1 | 45.0% | 0.5% | 56.8% | 14.0% | +0.3% | 0.39 | 19.95 | 6.17 | 91.8% |
| Evolution Incense | 3 | 44.4% | 0.5% | 56.4% | 13.2% | -0.3% | 0.38 | 19.76 | 6.15 | 92.0% |
| Level Ball | 2 | 44.2% | 0.5% | 56.2% | 11.0% | -0.5% | 0.38 | 19.60 | 6.07 | 91.3% |
| Rescue Scarf | 4 | 44.1% | 0.5% | 56.3% | 13.9% | -0.6% | 0.39 | 19.76 | 6.06 | 92.0% |
| Fire Energy | 7 | 43.9% | 0.5% | 56.0% | 13.2% | -0.8% | 0.40 | 19.71 | 6.08 | 91.9% |
| Buddy-Buddy Poffin | 2 | 43.7% | 0.5% | 55.9% | 13.0% | -1.0% | 0.37 | 19.47 | 6.08 | 90.5% |
| Hop | 4 | 43.6% | 0.5% | 56.0% | 13.4% | -1.1% | 0.38 | 19.71 | 6.10 | 91.5% |
| Arven | 4 | 43.6% | 0.5% | 55.8% | 13.4% | -1.1% | 0.36 | 19.79 | 6.11 | 91.8% |
| Pichu | 3 | 42.7% | 0.5% | 55.0% | 12.4% | -2.0% | 0.38 | 19.14 | 5.94 | 90.1% |
| Chandelure | 4 | 42.5% | 0.5% | 54.8% | 12.4% | -2.2% | 0.40 | 19.35 | 5.92 | 92.3% |
| Hyper Aroma | 1 | 41.8% | 0.4% | 54.3% | 10.5% | -2.9% | 0.40 | 19.05 | 5.86 | 91.7% |
| Hisuian Heavy Ball | 1 | 41.4% | 0.5% | 53.3% | 10.5% | -3.3% | 0.42 | 18.89 | 5.68 | 91.3% |
| Lampent | 4 | 40.1% | 0.4% | 52.0% | 8.9% | -4.6% | 0.40 | 18.42 | 5.60 | 91.2% |
| Litwick | 4 | 39.6% | 0.4% | 52.2% | 10.9% | -5.1% | 0.37 | 18.37 | 5.68 | 89.9% |
| Celebi ◇ | 1 | 8.9% | 0.2% | 17.4% | 0.0% | -35.8% | 0.71 | 8.35 | 0.00 | 91.4% |

Kept −Broken Time-Space at 45.5% (+0.8%).

## Step 2

List entering this step: weighted 45.5% ± 0.5%. Each row replaces one copy of that card with one Devolution Spray.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Sprays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Team Rocket's Petrel | 3 | 45.5% | 0.5% | 56.9% | 14.1% | +0.1% | 0.61 | 19.96 | 6.05 | 91.9% |
| Energy Retrieval | 1 | 45.4% | 0.5% | 57.4% | 14.6% | -0.1% | 0.65 | 19.96 | 6.05 | 91.6% |
| Buddy-Buddy Poffin | 2 | 45.3% | 0.5% | 57.2% | 15.1% | -0.2% | 0.62 | 19.69 | 5.98 | 90.3% |
| Fire Energy | 7 | 45.3% | 0.5% | 56.9% | 14.4% | -0.2% | 0.67 | 19.87 | 5.98 | 91.9% |
| Energy Search | 3 | 45.2% | 0.5% | 57.2% | 14.8% | -0.2% | 0.65 | 19.93 | 6.01 | 92.0% |
| Broken Time-Space | 2 | 45.2% | 0.5% | 57.0% | 13.5% | -0.3% | 0.63 | 19.88 | 6.02 | 91.8% |
| Jacq | 2 | 44.8% | 0.5% | 56.4% | 14.9% | -0.7% | 0.64 | 19.88 | 6.00 | 92.2% |
| Level Ball | 2 | 44.5% | 0.5% | 56.1% | 14.5% | -1.0% | 0.63 | 19.67 | 5.98 | 91.0% |
| Evolution Incense | 3 | 44.4% | 0.5% | 56.6% | 13.4% | -1.1% | 0.64 | 19.88 | 6.00 | 92.2% |
| Rescue Scarf | 4 | 44.3% | 0.5% | 56.5% | 12.4% | -1.2% | 0.66 | 19.94 | 5.94 | 92.4% |
| Arven | 4 | 44.2% | 0.5% | 56.4% | 13.5% | -1.3% | 0.62 | 19.81 | 5.95 | 91.8% |
| Dawn | 4 | 44.1% | 0.5% | 55.9% | 11.9% | -1.4% | 0.64 | 19.50 | 5.92 | 90.8% |
| Hop | 4 | 44.0% | 0.5% | 56.1% | 13.4% | -1.5% | 0.62 | 19.70 | 5.92 | 91.9% |
| Chandelure | 4 | 43.8% | 0.5% | 55.5% | 12.2% | -1.6% | 0.66 | 19.37 | 5.77 | 92.1% |
| Pichu | 3 | 42.9% | 0.5% | 55.4% | 13.5% | -2.6% | 0.65 | 19.36 | 5.86 | 90.4% |
| Hisuian Heavy Ball | 1 | 42.7% | 0.5% | 54.5% | 14.1% | -2.7% | 0.70 | 19.12 | 5.60 | 91.2% |
| Hyper Aroma | 1 | 41.2% | 0.4% | 53.4% | 10.2% | -4.3% | 0.68 | 18.82 | 5.59 | 90.9% |
| Litwick | 4 | 40.3% | 0.4% | 52.9% | 9.8% | -5.1% | 0.62 | 18.45 | 5.60 | 89.5% |
| Lampent | 4 | 40.2% | 0.4% | 52.3% | 9.4% | -5.2% | 0.67 | 18.55 | 5.50 | 90.9% |
| Celebi ◇ | 1 | 10.6% | 0.2% | 20.2% | 0.0% | -34.9% | 1.30 | 9.33 | 0.00 | 91.3% |

Kept −Team Rocket's Petrel at 45.5% (+0.1%).

## Step 3

List entering this step: weighted 45.5% ± 0.5%. Each row replaces one copy of that card with one Devolution Spray.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Sprays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Jacq | 2 | 45.9% | 0.5% | 57.3% | 16.4% | +0.3% | 0.82 | 19.88 | 5.89 | 91.2% |
| Team Rocket's Petrel | 2 | 45.8% | 0.5% | 57.5% | 13.2% | +0.3% | 0.78 | 20.02 | 6.00 | 91.4% |
| Broken Time-Space | 2 | 45.8% | 0.5% | 57.2% | 14.4% | +0.2% | 0.79 | 20.05 | 5.99 | 91.2% |
| Energy Search | 3 | 45.8% | 0.5% | 57.6% | 13.8% | +0.2% | 0.84 | 20.07 | 5.94 | 91.4% |
| Energy Retrieval | 1 | 45.7% | 0.5% | 57.6% | 15.0% | +0.2% | 0.83 | 20.23 | 5.98 | 91.6% |
| Fire Energy | 7 | 45.6% | 0.5% | 56.9% | 16.2% | +0.1% | 0.86 | 19.89 | 5.83 | 91.5% |
| Buddy-Buddy Poffin | 2 | 45.6% | 0.5% | 57.2% | 14.4% | +0.0% | 0.80 | 19.84 | 5.94 | 90.5% |
| Level Ball | 2 | 45.4% | 0.5% | 57.3% | 15.2% | -0.1% | 0.82 | 19.83 | 5.88 | 90.5% |
| Hop | 4 | 44.8% | 0.5% | 56.8% | 13.8% | -0.7% | 0.79 | 19.73 | 5.85 | 91.1% |
| Evolution Incense | 3 | 44.8% | 0.5% | 56.9% | 13.1% | -0.7% | 0.81 | 19.75 | 5.88 | 91.1% |
| Rescue Scarf | 4 | 44.7% | 0.5% | 56.7% | 13.6% | -0.8% | 0.86 | 20.05 | 5.86 | 91.8% |
| Arven | 4 | 44.6% | 0.5% | 56.5% | 14.0% | -0.9% | 0.81 | 19.91 | 5.86 | 91.5% |
| Chandelure | 4 | 44.3% | 0.5% | 56.4% | 13.8% | -1.2% | 0.84 | 19.44 | 5.69 | 91.2% |
| Dawn | 4 | 44.2% | 0.5% | 55.8% | 12.0% | -1.3% | 0.80 | 19.40 | 5.75 | 89.9% |
| Pichu | 3 | 44.0% | 0.5% | 55.8% | 12.6% | -1.5% | 0.81 | 19.27 | 5.74 | 89.3% |
| Hyper Aroma | 1 | 42.6% | 0.5% | 54.5% | 11.9% | -2.9% | 0.86 | 19.04 | 5.58 | 90.5% |
| Lampent | 4 | 41.9% | 0.5% | 53.7% | 12.0% | -3.6% | 0.88 | 18.72 | 5.41 | 90.7% |
| Hisuian Heavy Ball | 1 | 41.8% | 0.5% | 53.7% | 13.1% | -3.7% | 0.92 | 19.12 | 5.41 | 90.5% |
| Litwick | 4 | 40.9% | 0.4% | 53.2% | 10.1% | -4.6% | 0.79 | 18.62 | 5.55 | 89.5% |
| Celebi ◇ | 1 | 11.7% | 0.2% | 22.1% | 0.1% | -33.8% | 1.75 | 10.21 | 0.00 | 91.0% |

Kept −Jacq at 45.9% (+0.3%).

## Step 4

List entering this step: weighted 45.9% ± 0.5%. Each row replaces one copy of that card with one Devolution Spray.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Sprays | Mill cards | Time Distortion | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Energy Retrieval | 1 | 46.2% | 0.5% | 58.0% | 13.8% | +0.4% | 1.02 | 20.04 | 5.79 | 91.3% |
| Energy Search | 3 | 46.2% | 0.5% | 57.6% | 15.0% | +0.3% | 1.01 | 20.10 | 5.82 | 91.9% |
| Level Ball | 2 | 45.9% | 0.5% | 57.2% | 13.6% | +0.0% | 0.99 | 19.77 | 5.75 | 90.7% |
| Team Rocket's Petrel | 2 | 45.8% | 0.5% | 57.6% | 15.6% | -0.0% | 0.97 | 20.09 | 5.86 | 91.5% |
| Broken Time-Space | 2 | 45.6% | 0.5% | 57.2% | 12.8% | -0.2% | 0.99 | 19.77 | 5.74 | 91.0% |
| Jacq | 1 | 45.4% | 0.5% | 57.2% | 12.0% | -0.4% | 1.00 | 19.90 | 5.78 | 91.7% |
| Buddy-Buddy Poffin | 2 | 45.4% | 0.5% | 57.0% | 15.2% | -0.4% | 0.99 | 19.78 | 5.77 | 90.1% |
| Fire Energy | 7 | 45.1% | 0.5% | 56.6% | 12.5% | -0.8% | 1.04 | 19.85 | 5.69 | 91.8% |
| Evolution Incense | 3 | 44.8% | 0.5% | 56.7% | 13.9% | -1.1% | 1.00 | 19.71 | 5.70 | 91.5% |
| Arven | 4 | 44.6% | 0.5% | 56.5% | 14.9% | -1.3% | 0.98 | 19.78 | 5.72 | 91.0% |
| Hop | 4 | 44.5% | 0.5% | 56.1% | 13.5% | -1.3% | 0.97 | 19.50 | 5.62 | 91.3% |
| Rescue Scarf | 4 | 44.5% | 0.5% | 56.4% | 13.4% | -1.3% | 1.05 | 19.90 | 5.66 | 91.6% |
| Dawn | 4 | 44.4% | 0.5% | 56.1% | 13.1% | -1.4% | 0.99 | 19.35 | 5.60 | 90.2% |
| Pichu | 3 | 43.5% | 0.5% | 55.6% | 12.2% | -2.4% | 1.01 | 19.29 | 5.56 | 89.4% |
| Chandelure | 4 | 43.3% | 0.5% | 55.5% | 10.9% | -2.5% | 1.04 | 19.54 | 5.54 | 91.4% |
| Hisuian Heavy Ball | 1 | 42.7% | 0.5% | 54.6% | 12.4% | -3.2% | 1.12 | 19.13 | 5.30 | 90.4% |
| Hyper Aroma | 1 | 42.6% | 0.4% | 55.0% | 12.0% | -3.3% | 1.05 | 19.04 | 5.40 | 90.8% |
| Lampent | 4 | 41.9% | 0.4% | 53.7% | 10.9% | -4.0% | 1.05 | 18.65 | 5.23 | 90.6% |
| Litwick | 4 | 40.6% | 0.4% | 52.8% | 9.6% | -5.3% | 0.96 | 18.56 | 5.37 | 89.4% |
| Celebi ◇ | 1 | 12.9% | 0.3% | 24.1% | 0.4% | -32.9% | 2.16 | 10.79 | 0.00 | 90.8% |

Kept −Energy Retrieval at 46.2% (+0.4%).

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 42.2% | 40.2% | 41.2% | -0.5% |
| Hedrick Worlds Dragapult | 65.2% | 63.7% | 64.5% | +3.6% |
| Unlimited Dragapult | 65.8% | 65.8% | 65.8% | -0.2% |
| Cornerstone Ogerpon (D60) | 13.5% | 14.0% | 13.8% | -0.6% |
| Wo-Chien / Floragato (S60) | 71.2% | 75.8% | 73.5% | +0.5% |
| Gholdengo (G) | 54.5% | 50.7% | 52.6% | +5.0% |
| Clefairy / Mewtwo (C60) | 53.8% | 55.8% | 54.8% | +3.5% |
| Set M (Mew ex) | 14.2% | 16.2% | 15.2% | -0.4% |
| Mega Starmie ex (Kudo) | 17.2% | 13.2% | 15.2% | -0.6% |
| Lucario Hariyama | 72.0% | 72.8% | 72.4% | +4.9% |
| Iron Thorns ex | 91.0% | 92.2% | 91.6% | -0.1% |
| Carpet Set H | 97.2% | 97.0% | 97.1% | +3.9% |
| Ambipom Hand Fling | 95.2% | 97.0% | 96.1% | -0.9% |

