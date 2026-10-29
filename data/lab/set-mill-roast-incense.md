# Roast Evolution Incense greedy

Each step tries every other card as the one copy to replace with one Evolution Incense. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

The starting 60 is the locked list: one Hisuian Heavy Ball in place of one Switch, and zero Evolution Incense. Evolution Incense searches the deck for one Evolution Pokémon. Roast takes Chandelure once a Lampent is in hand or in play, and takes Lampent only while a Litwick still has no Stage 1.

- **Seed**: `20261027`
- **Games per seat**: 40
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 1064.6s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Incense | Chandelure | Lampent | Mill cards |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 34.5% | 1.4% | 45.2% | 3.8% | +0.0% | 0.00 | 0.00 | 0.00 | 15.78 |
| 1 Incense | 1 | Level Ball | 35.3% | 1.3% | 46.4% | 2.5% | +0.8% | 0.71 | 0.46 | 0.25 | 15.99 |
| 2 Incense | 2 | Cleffa | 35.9% | 1.4% | 47.8% | 5.0% | +1.4% | 1.19 | 0.85 | 0.35 | 16.52 |
| 3 Incense | 3 | Cleffa | 36.9% | 1.3% | 49.6% | 7.5% | +2.4% | 1.58 | 1.15 | 0.43 | 17.05 |

## Decision

Kept list is 3 Incense: 3 Evolution Incense, weighted 36.9% against the locked list at 34.5% (+2.4%).

Counts:

- Litwick ×4
- Lampent ×4
- Chandelure ×4
- Celebi ◇ ×1
- Pichu ×3
- Arven ×4
- Team Rocket's Petrel ×4
- Buddy-Buddy Poffin ×3
- Energy Search ×4
- Energy Retrieval ×2
- Rescue Scarf ×4
- Dawn ×4
- Level Ball ×2
- Ultra Ball ×1
- Switch ×1
- Broken Time-Space ×3
- Slumbering Forest ×1
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×3

## Step 1

List entering this step: weighted 34.5% ± 1.4%. Each row replaces one copy of that card with one Evolution Incense.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Incense | Chandelure | Lampent | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Level Ball | 3 | 35.3% | 1.3% | 46.4% | 2.5% | +0.8% | 0.71 | 0.46 | 0.25 | 15.99 |
| Broken Time-Space | 3 | 34.6% | 1.3% | 46.9% | 6.2% | +0.0% | 0.69 | 0.46 | 0.22 | 16.18 |
| Cleffa | 2 | 34.3% | 1.3% | 47.1% | 6.2% | -0.2% | 0.71 | 0.50 | 0.21 | 16.28 |
| Arven | 4 | 34.1% | 1.3% | 47.6% | 1.2% | -0.4% | 0.67 | 0.46 | 0.21 | 15.94 |
| Fire Energy | 7 | 34.0% | 1.3% | 44.9% | 3.8% | -0.5% | 0.70 | 0.48 | 0.22 | 15.94 |
| Chandelure | 4 | 33.8% | 1.3% | 45.4% | 3.8% | -0.7% | 0.66 | 0.44 | 0.22 | 15.38 |
| Slumbering Forest | 1 | 33.2% | 1.2% | 45.7% | 1.2% | -1.3% | 0.70 | 0.48 | 0.21 | 15.73 |
| Energy Search | 4 | 32.9% | 1.3% | 45.8% | 3.8% | -1.6% | 0.70 | 0.46 | 0.23 | 15.72 |
| Ultra Ball | 1 | 32.8% | 1.3% | 45.3% | 3.8% | -1.7% | 0.68 | 0.46 | 0.22 | 15.87 |
| Pichu | 3 | 32.7% | 1.3% | 45.3% | 1.2% | -1.8% | 0.72 | 0.48 | 0.23 | 15.91 |
| Switch | 1 | 32.5% | 1.3% | 44.6% | 2.5% | -2.0% | 0.71 | 0.48 | 0.23 | 16.08 |
| Rescue Scarf | 4 | 32.5% | 1.3% | 45.4% | 6.2% | -2.0% | 0.68 | 0.46 | 0.22 | 16.36 |
| Hisuian Heavy Ball | 1 | 32.2% | 1.3% | 43.4% | 5.0% | -2.3% | 0.71 | 0.50 | 0.22 | 15.41 |
| Buddy-Buddy Poffin | 3 | 32.1% | 1.2% | 45.6% | 1.2% | -2.4% | 0.68 | 0.45 | 0.22 | 15.56 |
| Team Rocket's Petrel | 4 | 31.9% | 1.3% | 43.8% | 3.8% | -2.6% | 0.68 | 0.47 | 0.21 | 15.46 |
| Energy Retrieval | 2 | 31.5% | 1.2% | 45.1% | 3.8% | -3.0% | 0.70 | 0.47 | 0.22 | 15.45 |
| Litwick | 4 | 31.1% | 1.2% | 43.7% | 2.5% | -3.4% | 0.66 | 0.47 | 0.20 | 15.03 |
| Lampent | 4 | 29.5% | 1.2% | 41.9% | 3.8% | -5.0% | 0.69 | 0.44 | 0.25 | 14.70 |
| Dawn | 4 | 28.8% | 1.2% | 41.3% | 2.5% | -5.7% | 0.71 | 0.47 | 0.24 | 14.89 |
| Celebi ◇ | 1 | 7.2% | 0.6% | 13.1% | 0.0% | -27.3% | 0.68 | 0.39 | 0.29 | 5.99 |

Kept −Level Ball at 35.3% (+0.8%).

## Step 2

List entering this step: weighted 35.3% ± 1.3%. Each row replaces one copy of that card with one Evolution Incense.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Incense | Chandelure | Lampent | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cleffa | 2 | 35.9% | 1.4% | 47.8% | 5.0% | +0.7% | 1.19 | 0.85 | 0.35 | 16.52 |
| Ultra Ball | 1 | 35.0% | 1.3% | 48.1% | 5.0% | -0.3% | 1.21 | 0.88 | 0.33 | 16.46 |
| Pichu | 3 | 34.3% | 1.3% | 46.1% | 6.2% | -0.9% | 1.20 | 0.85 | 0.35 | 15.94 |
| Energy Retrieval | 2 | 33.7% | 1.3% | 46.5% | 7.5% | -1.6% | 1.18 | 0.85 | 0.33 | 15.89 |
| Energy Search | 4 | 33.6% | 1.3% | 45.4% | 5.0% | -1.6% | 1.18 | 0.85 | 0.33 | 15.77 |
| Rescue Scarf | 4 | 33.5% | 1.3% | 46.0% | 2.5% | -1.7% | 1.25 | 0.90 | 0.35 | 16.13 |
| Buddy-Buddy Poffin | 3 | 33.5% | 1.3% | 47.4% | 2.5% | -1.8% | 1.18 | 0.87 | 0.32 | 15.91 |
| Switch | 1 | 33.3% | 1.3% | 45.7% | 3.8% | -2.0% | 1.24 | 0.88 | 0.36 | 15.97 |
| Arven | 4 | 33.1% | 1.3% | 45.6% | 6.2% | -2.2% | 1.12 | 0.80 | 0.32 | 15.99 |
| Slumbering Forest | 1 | 32.8% | 1.3% | 44.9% | 2.5% | -2.5% | 1.22 | 0.84 | 0.37 | 15.91 |
| Dawn | 4 | 32.6% | 1.3% | 43.5% | 2.5% | -2.6% | 1.25 | 0.88 | 0.36 | 15.27 |
| Broken Time-Space | 3 | 32.4% | 1.2% | 44.6% | 3.8% | -2.9% | 1.21 | 0.85 | 0.36 | 15.97 |
| Hisuian Heavy Ball | 1 | 32.0% | 1.4% | 43.7% | 8.8% | -3.3% | 1.27 | 0.91 | 0.36 | 14.93 |
| Team Rocket's Petrel | 4 | 31.9% | 1.3% | 43.8% | 5.0% | -3.3% | 1.18 | 0.87 | 0.31 | 15.42 |
| Litwick | 4 | 31.9% | 1.2% | 44.7% | 1.2% | -3.4% | 1.18 | 0.84 | 0.33 | 15.38 |
| Level Ball | 2 | 31.6% | 1.3% | 43.2% | 3.8% | -3.7% | 1.22 | 0.84 | 0.38 | 15.33 |
| Chandelure | 4 | 31.5% | 1.3% | 44.5% | 3.8% | -3.8% | 1.13 | 0.78 | 0.35 | 15.61 |
| Fire Energy | 7 | 29.5% | 1.2% | 43.5% | 0.0% | -5.7% | 1.18 | 0.82 | 0.35 | 15.52 |
| Lampent | 4 | 28.9% | 1.2% | 41.5% | 3.8% | -6.4% | 1.19 | 0.79 | 0.40 | 14.66 |
| Celebi ◇ | 1 | 7.7% | 0.7% | 13.7% | 0.0% | -27.5% | 1.19 | 0.75 | 0.45 | 5.89 |

Kept −Cleffa at 35.9% (+0.7%).

## Step 3

List entering this step: weighted 35.9% ± 1.4%. Each row replaces one copy of that card with one Evolution Incense.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Incense | Chandelure | Lampent | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Cleffa | 1 | 36.9% | 1.3% | 49.6% | 7.5% | +0.9% | 1.58 | 1.15 | 0.43 | 17.05 |
| Arven | 4 | 36.2% | 1.4% | 47.8% | 10.0% | +0.3% | 1.48 | 1.07 | 0.41 | 16.29 |
| Broken Time-Space | 3 | 35.9% | 1.4% | 47.5% | 6.2% | -0.1% | 1.58 | 1.14 | 0.44 | 16.39 |
| Energy Search | 4 | 35.2% | 1.3% | 48.5% | 6.2% | -0.8% | 1.61 | 1.15 | 0.46 | 16.85 |
| Level Ball | 2 | 34.9% | 1.3% | 46.9% | 7.5% | -1.1% | 1.59 | 1.14 | 0.44 | 16.35 |
| Slumbering Forest | 1 | 34.7% | 1.3% | 47.6% | 6.2% | -1.3% | 1.61 | 1.16 | 0.45 | 16.87 |
| Switch | 1 | 34.3% | 1.3% | 46.1% | 7.5% | -1.7% | 1.64 | 1.16 | 0.48 | 16.25 |
| Hisuian Heavy Ball | 1 | 34.2% | 1.3% | 46.3% | 5.0% | -1.7% | 1.68 | 1.22 | 0.46 | 15.71 |
| Lampent | 4 | 33.6% | 1.4% | 44.8% | 7.5% | -2.3% | 1.56 | 1.11 | 0.45 | 15.24 |
| Rescue Scarf | 4 | 33.2% | 1.3% | 45.6% | 3.8% | -2.8% | 1.58 | 1.12 | 0.47 | 16.26 |
| Team Rocket's Petrel | 4 | 33.0% | 1.3% | 46.4% | 5.0% | -2.9% | 1.53 | 1.12 | 0.41 | 16.10 |
| Ultra Ball | 1 | 33.0% | 1.2% | 46.2% | 2.5% | -3.0% | 1.60 | 1.14 | 0.46 | 16.41 |
| Fire Energy | 7 | 32.8% | 1.3% | 45.1% | 7.5% | -3.2% | 1.54 | 1.11 | 0.43 | 16.39 |
| Buddy-Buddy Poffin | 3 | 32.8% | 1.3% | 44.5% | 6.2% | -3.2% | 1.55 | 1.10 | 0.44 | 15.66 |
| Dawn | 4 | 32.8% | 1.3% | 45.5% | 5.0% | -3.2% | 1.66 | 1.14 | 0.51 | 15.57 |
| Litwick | 4 | 32.7% | 1.3% | 45.3% | 3.8% | -3.3% | 1.56 | 1.14 | 0.41 | 15.89 |
| Pichu | 3 | 32.1% | 1.3% | 44.6% | 6.2% | -3.9% | 1.60 | 1.15 | 0.45 | 16.09 |
| Energy Retrieval | 2 | 32.0% | 1.2% | 45.1% | 3.8% | -4.0% | 1.57 | 1.12 | 0.45 | 15.75 |
| Chandelure | 4 | 29.9% | 1.2% | 43.3% | 1.2% | -6.1% | 1.51 | 1.01 | 0.50 | 15.64 |
| Celebi ◇ | 1 | 7.7% | 0.7% | 14.6% | 0.0% | -28.3% | 1.59 | 0.97 | 0.62 | 6.09 |

Kept −Cleffa at 36.9% (+0.9%).

## Step 4

List entering this step: weighted 36.9% ± 1.3%. Each row replaces one copy of that card with one Evolution Incense.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Incense | Chandelure | Lampent | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Broken Time-Space | 3 | 36.8% | 1.3% | 49.7% | 7.5% | -0.1% | 1.89 | 1.41 | 0.48 | 17.00 |
| Team Rocket's Petrel | 4 | 36.4% | 1.3% | 49.2% | 6.2% | -0.5% | 1.85 | 1.34 | 0.51 | 17.36 |
| Arven | 4 | 36.3% | 1.3% | 50.1% | 7.5% | -0.6% | 1.84 | 1.32 | 0.52 | 16.93 |
| Slumbering Forest | 1 | 36.0% | 1.3% | 48.9% | 7.5% | -0.9% | 1.92 | 1.39 | 0.53 | 17.00 |
| Fire Energy | 7 | 36.0% | 1.4% | 48.0% | 7.5% | -0.9% | 1.97 | 1.42 | 0.55 | 16.90 |
| Ultra Ball | 1 | 34.8% | 1.3% | 48.0% | 7.5% | -2.1% | 1.94 | 1.40 | 0.54 | 16.94 |
| Chandelure | 4 | 34.8% | 1.4% | 46.6% | 8.8% | -2.1% | 1.76 | 1.18 | 0.58 | 16.83 |
| Switch | 1 | 34.7% | 1.3% | 48.2% | 6.2% | -2.2% | 1.89 | 1.33 | 0.56 | 16.96 |
| Level Ball | 2 | 34.2% | 1.3% | 47.3% | 7.5% | -2.7% | 1.93 | 1.38 | 0.55 | 16.84 |
| Energy Search | 4 | 34.1% | 1.3% | 47.2% | 2.5% | -2.8% | 1.94 | 1.40 | 0.54 | 16.99 |
| Hisuian Heavy Ball | 1 | 34.1% | 1.3% | 46.1% | 7.5% | -2.8% | 2.00 | 1.44 | 0.55 | 16.10 |
| Pichu | 3 | 33.5% | 1.2% | 47.5% | 0.0% | -3.4% | 1.89 | 1.39 | 0.50 | 16.33 |
| Buddy-Buddy Poffin | 3 | 33.0% | 1.2% | 46.6% | 3.8% | -3.9% | 1.89 | 1.37 | 0.52 | 16.73 |
| Litwick | 4 | 33.0% | 1.3% | 46.2% | 3.8% | -3.9% | 1.86 | 1.40 | 0.47 | 15.73 |
| Rescue Scarf | 4 | 32.8% | 1.2% | 46.4% | 3.8% | -4.1% | 1.93 | 1.42 | 0.51 | 17.00 |
| Energy Retrieval | 2 | 32.5% | 1.2% | 45.3% | 3.8% | -4.4% | 1.91 | 1.38 | 0.53 | 16.63 |
| Dawn | 4 | 31.8% | 1.3% | 44.1% | 6.2% | -5.1% | 1.95 | 1.38 | 0.57 | 15.83 |
| Lampent | 4 | 30.1% | 1.2% | 41.9% | 2.5% | -6.7% | 1.87 | 1.32 | 0.55 | 15.63 |
| Celebi ◇ | 1 | 7.0% | 0.6% | 13.8% | 0.0% | -29.9% | 1.81 | 1.12 | 0.68 | 6.11 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 35.0% | 32.5% | 33.8% | -6.2% |
| Hedrick Worlds Dragapult | 47.5% | 40.0% | 43.8% | +1.3% |
| Unlimited Dragapult | 60.0% | 62.5% | 61.3% | +18.8% |
| Cornerstone Ogerpon (D60) | 7.5% | 7.5% | 7.5% | -1.2% |
| Wo-Chien / Floragato (S60) | 65.0% | 52.5% | 58.8% | +7.5% |
| Gholdengo (G) | 32.5% | 30.0% | 31.2% | -2.5% |
| Clefairy / Mewtwo (C60) | 47.5% | 47.5% | 47.5% | +11.2% |
| Set M (Mew ex) | 10.0% | 10.0% | 10.0% | -5.0% |
| Mega Starmie ex (Kudo) | 7.5% | 7.5% | 7.5% | +3.7% |
| Lucario Hariyama | 60.0% | 62.5% | 61.3% | +6.2% |
| Iron Thorns ex | 90.0% | 95.0% | 92.5% | +12.5% |
| Carpet Set H | 87.5% | 95.0% | 91.2% | +1.2% |
| Ambipom Hand Fling | 100.0% | 97.5% | 98.8% | +10.0% |
