# Roast Jacq greedy

Each step tries every other card as the one copy to replace with one Jacq. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

The starting 60 is the locked Hyper Aroma list: one Hyper Aroma in place of Ultra Ball, three Evolution Incense, zero Cleffa, zero Jacq. Jacq searches the deck for up to 2 Evolution Pokémon. Roast takes Lampent while uncovered Litwick remain, counting Litwick that Playground will bench, then Chandelure once a Lampent is in hand or in play.

An earlier search on the Heavy Ball list used 40 games per seat. Its best cut was one Litwick at 33.7%, below that list's 34.5%, so it kept zero Jacq. This table is the retry at 400 games per seat.

- **Seed**: `20261027`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 9761.9s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Jacq | Cards | Mill cards | Aroma | Incense | Dawn |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 38.5% | 0.4% | 51.0% | 10.4% | +0.0% | 0.00 | 0.00 | 18.00 | 0.67 | 1.36 | 1.19 |
| 1 Jacq | 1 | Switch | 39.7% | 0.4% | 52.0% | 9.5% | +1.2% | 0.28 | 0.54 | 18.27 | 0.63 | 1.31 | 1.16 |
| 2 Jacq | 2 | Energy Retrieval | 40.7% | 0.4% | 53.0% | 11.1% | +2.2% | 0.52 | 0.98 | 18.71 | 0.61 | 1.26 | 1.13 |
| 3 Jacq | 3 | Buddy-Buddy Poffin | 41.1% | 0.5% | 53.5% | 10.1% | +2.6% | 0.73 | 1.39 | 18.60 | 0.57 | 1.18 | 1.07 |

## Decision

Kept list is 3 Jacq: 3 Jacq, weighted 41.1% against the locked list at 38.5% (+2.6%).

Counts:

- Litwick ×4
- Lampent ×4
- Chandelure ×4
- Celebi ◇ ×1
- Pichu ×3
- Arven ×4
- Team Rocket's Petrel ×4
- Buddy-Buddy Poffin ×2
- Energy Search ×4
- Energy Retrieval ×1
- Rescue Scarf ×4
- Dawn ×4
- Level Ball ×2
- Broken Time-Space ×3
- Slumbering Forest ×1
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×3
- Hyper Aroma ×1
- Jacq ×3

## Step 1

List entering this step: weighted 38.5% ± 0.4%. Each row replaces one copy of that card with one Jacq.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Cards | Mill cards | Aroma | Incense | Dawn |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Switch | 1 | 39.7% | 0.4% | 52.0% | 9.5% | +1.2% | 0.28 | 0.54 | 18.27 | 0.63 | 1.31 | 1.16 |
| Slumbering Forest | 1 | 39.1% | 0.4% | 51.7% | 9.2% | +0.6% | 0.28 | 0.55 | 18.42 | 0.63 | 1.29 | 1.14 |
| Energy Retrieval | 2 | 39.1% | 0.4% | 51.8% | 8.6% | +0.6% | 0.28 | 0.54 | 18.38 | 0.64 | 1.30 | 1.14 |
| Energy Search | 4 | 39.0% | 0.4% | 51.6% | 9.9% | +0.5% | 0.29 | 0.55 | 18.32 | 0.63 | 1.30 | 1.14 |
| Broken Time-Space | 3 | 38.9% | 0.4% | 51.6% | 9.4% | +0.4% | 0.28 | 0.54 | 18.25 | 0.62 | 1.28 | 1.14 |
| Fire Energy | 7 | 38.7% | 0.4% | 51.2% | 9.5% | +0.2% | 0.29 | 0.54 | 18.12 | 0.63 | 1.29 | 1.14 |
| Buddy-Buddy Poffin | 3 | 38.6% | 0.4% | 51.1% | 9.6% | +0.1% | 0.27 | 0.52 | 18.15 | 0.63 | 1.29 | 1.15 |
| Arven | 4 | 38.5% | 0.4% | 51.1% | 9.8% | -0.0% | 0.29 | 0.55 | 18.09 | 0.59 | 1.22 | 1.15 |
| Rescue Scarf | 4 | 38.4% | 0.4% | 51.0% | 9.8% | -0.1% | 0.28 | 0.52 | 18.26 | 0.64 | 1.30 | 1.14 |
| Evolution Incense | 3 | 38.2% | 0.4% | 50.5% | 8.5% | -0.3% | 0.30 | 0.58 | 18.06 | 0.64 | 0.99 | 1.17 |
| Team Rocket's Petrel | 4 | 38.1% | 0.4% | 50.8% | 9.5% | -0.4% | 0.28 | 0.52 | 18.03 | 0.61 | 1.24 | 1.14 |
| Level Ball | 2 | 38.0% | 0.4% | 50.8% | 9.5% | -0.5% | 0.27 | 0.52 | 17.85 | 0.64 | 1.27 | 1.13 |
| Pichu | 3 | 37.7% | 0.4% | 50.2% | 9.4% | -0.8% | 0.28 | 0.54 | 17.67 | 0.63 | 1.28 | 1.11 |
| Dawn | 4 | 37.3% | 0.4% | 50.3% | 8.1% | -1.2% | 0.29 | 0.55 | 17.66 | 0.66 | 1.33 | 0.90 |
| Chandelure | 4 | 37.2% | 0.4% | 49.9% | 9.0% | -1.3% | 0.25 | 0.46 | 17.60 | 0.62 | 1.17 | 1.10 |
| Hisuian Heavy Ball | 1 | 37.1% | 0.4% | 49.2% | 8.6% | -1.4% | 0.28 | 0.54 | 17.45 | 0.68 | 1.37 | 1.15 |
| Hyper Aroma | 1 | 35.9% | 0.4% | 48.8% | 7.4% | -2.6% | 0.32 | 0.62 | 17.26 | 0.00 | 1.56 | 1.22 |
| Litwick | 4 | 35.3% | 0.4% | 48.5% | 5.4% | -3.2% | 0.27 | 0.52 | 16.99 | 0.65 | 1.29 | 1.14 |
| Lampent | 4 | 35.0% | 0.4% | 47.5% | 8.1% | -3.5% | 0.27 | 0.52 | 16.95 | 0.53 | 1.29 | 1.15 |
| Celebi ◇ | 1 | 7.3% | 0.2% | 14.6% | 0.0% | -31.2% | 0.26 | 0.49 | 6.59 | 0.64 | 1.23 | 1.32 |

Kept −Switch at 39.7% (+1.2%).

## Step 2

List entering this step: weighted 39.7% ± 0.4%. Each row replaces one copy of that card with one Jacq.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Cards | Mill cards | Aroma | Incense | Dawn |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Energy Retrieval | 2 | 40.7% | 0.4% | 53.0% | 11.1% | +0.9% | 0.52 | 0.98 | 18.71 | 0.61 | 1.26 | 1.13 |
| Slumbering Forest | 1 | 40.0% | 0.4% | 52.6% | 9.9% | +0.3% | 0.52 | 0.99 | 18.67 | 0.62 | 1.26 | 1.11 |
| Fire Energy | 7 | 40.0% | 0.4% | 52.2% | 9.9% | +0.3% | 0.52 | 1.00 | 18.54 | 0.62 | 1.26 | 1.12 |
| Team Rocket's Petrel | 4 | 39.9% | 0.4% | 52.5% | 8.5% | +0.2% | 0.52 | 0.99 | 18.35 | 0.59 | 1.22 | 1.11 |
| Broken Time-Space | 3 | 39.9% | 0.4% | 52.2% | 10.0% | +0.1% | 0.52 | 0.99 | 18.54 | 0.61 | 1.25 | 1.12 |
| Rescue Scarf | 4 | 39.7% | 0.4% | 52.5% | 10.2% | -0.0% | 0.51 | 0.98 | 18.55 | 0.61 | 1.25 | 1.13 |
| Level Ball | 2 | 39.7% | 0.4% | 51.8% | 9.1% | -0.1% | 0.51 | 0.98 | 18.37 | 0.61 | 1.26 | 1.12 |
| Energy Search | 4 | 39.6% | 0.4% | 52.2% | 11.2% | -0.1% | 0.52 | 1.00 | 18.55 | 0.61 | 1.26 | 1.11 |
| Evolution Incense | 3 | 39.6% | 0.4% | 52.1% | 9.9% | -0.1% | 0.54 | 1.02 | 18.35 | 0.62 | 0.97 | 1.12 |
| Buddy-Buddy Poffin | 3 | 39.6% | 0.4% | 52.1% | 9.6% | -0.2% | 0.52 | 0.99 | 18.34 | 0.61 | 1.25 | 1.10 |
| Pichu | 3 | 39.3% | 0.5% | 51.7% | 10.6% | -0.4% | 0.51 | 0.97 | 17.98 | 0.61 | 1.23 | 1.09 |
| Dawn | 4 | 39.0% | 0.4% | 51.3% | 9.5% | -0.8% | 0.54 | 1.02 | 18.09 | 0.62 | 1.29 | 0.87 |
| Arven | 4 | 38.7% | 0.4% | 51.6% | 9.0% | -1.0% | 0.53 | 1.00 | 18.21 | 0.57 | 1.17 | 1.12 |
| Chandelure | 4 | 38.7% | 0.4% | 51.4% | 9.0% | -1.1% | 0.47 | 0.88 | 17.99 | 0.60 | 1.10 | 1.09 |
| Hyper Aroma | 1 | 37.0% | 0.4% | 49.6% | 8.5% | -2.7% | 0.57 | 1.09 | 17.56 | 0.00 | 1.50 | 1.18 |
| Hisuian Heavy Ball | 1 | 36.9% | 0.4% | 49.3% | 7.4% | -2.8% | 0.50 | 0.96 | 17.54 | 0.66 | 1.30 | 1.11 |
| Lampent | 4 | 35.9% | 0.4% | 48.4% | 8.0% | -3.8% | 0.51 | 0.98 | 17.19 | 0.49 | 1.23 | 1.13 |
| Litwick | 4 | 35.8% | 0.4% | 48.9% | 6.4% | -3.9% | 0.50 | 0.96 | 17.27 | 0.64 | 1.23 | 1.12 |
| Celebi ◇ | 1 | 7.7% | 0.2% | 15.2% | 0.0% | -32.0% | 0.47 | 0.91 | 6.79 | 0.60 | 1.16 | 1.27 |

Kept −Energy Retrieval at 40.7% (+0.9%).

## Step 3

List entering this step: weighted 40.7% ± 0.4%. Each row replaces one copy of that card with one Jacq.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Cards | Mill cards | Aroma | Incense | Dawn |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Buddy-Buddy Poffin | 3 | 41.1% | 0.5% | 53.5% | 10.1% | +0.4% | 0.73 | 1.39 | 18.60 | 0.57 | 1.18 | 1.07 |
| Broken Time-Space | 3 | 40.9% | 0.4% | 53.3% | 10.6% | +0.2% | 0.75 | 1.42 | 18.85 | 0.58 | 1.18 | 1.07 |
| Evolution Incense | 3 | 40.3% | 0.4% | 53.0% | 9.8% | -0.3% | 0.76 | 1.45 | 18.65 | 0.59 | 0.92 | 1.09 |
| Energy Search | 4 | 40.3% | 0.4% | 52.7% | 10.2% | -0.4% | 0.73 | 1.40 | 18.84 | 0.57 | 1.19 | 1.08 |
| Level Ball | 2 | 40.3% | 0.5% | 52.5% | 10.8% | -0.4% | 0.73 | 1.39 | 18.59 | 0.58 | 1.18 | 1.08 |
| Team Rocket's Petrel | 4 | 40.3% | 0.4% | 53.0% | 9.4% | -0.4% | 0.73 | 1.38 | 18.77 | 0.57 | 1.15 | 1.06 |
| Energy Retrieval | 1 | 40.2% | 0.4% | 53.0% | 9.8% | -0.5% | 0.72 | 1.37 | 18.95 | 0.58 | 1.20 | 1.09 |
| Slumbering Forest | 1 | 40.2% | 0.4% | 52.7% | 9.9% | -0.5% | 0.74 | 1.40 | 18.87 | 0.58 | 1.19 | 1.07 |
| Fire Energy | 7 | 40.1% | 0.4% | 52.4% | 8.0% | -0.5% | 0.74 | 1.40 | 18.75 | 0.58 | 1.19 | 1.08 |
| Rescue Scarf | 4 | 39.8% | 0.4% | 52.8% | 9.0% | -0.9% | 0.73 | 1.40 | 18.85 | 0.59 | 1.18 | 1.10 |
| Dawn | 4 | 39.7% | 0.4% | 52.2% | 10.4% | -0.9% | 0.75 | 1.43 | 18.41 | 0.59 | 1.24 | 0.86 |
| Pichu | 3 | 39.6% | 0.4% | 52.1% | 8.2% | -1.1% | 0.72 | 1.37 | 18.18 | 0.58 | 1.17 | 1.06 |
| Arven | 4 | 39.3% | 0.4% | 52.0% | 9.5% | -1.4% | 0.75 | 1.42 | 18.58 | 0.54 | 1.13 | 1.08 |
| Hyper Aroma | 1 | 38.2% | 0.4% | 51.0% | 7.6% | -2.5% | 0.80 | 1.52 | 18.07 | 0.00 | 1.46 | 1.13 |
| Hisuian Heavy Ball | 1 | 37.9% | 0.4% | 50.2% | 8.5% | -2.7% | 0.71 | 1.36 | 17.95 | 0.62 | 1.22 | 1.08 |
| Chandelure | 4 | 37.8% | 0.4% | 50.8% | 8.6% | -2.8% | 0.65 | 1.21 | 18.23 | 0.58 | 1.05 | 1.06 |
| Lampent | 4 | 37.1% | 0.4% | 49.4% | 9.2% | -3.5% | 0.71 | 1.35 | 17.57 | 0.46 | 1.18 | 1.11 |
| Litwick | 4 | 36.7% | 0.4% | 49.8% | 7.4% | -3.9% | 0.71 | 1.34 | 17.48 | 0.60 | 1.18 | 1.09 |
| Celebi ◇ | 1 | 7.4% | 0.2% | 14.8% | 0.0% | -33.3% | 0.67 | 1.29 | 6.95 | 0.57 | 1.11 | 1.25 |

Kept −Buddy-Buddy Poffin at 41.1% (+0.4%).

## Step 4

List entering this step: weighted 41.1% ± 0.5%. Each row replaces one copy of that card with one Jacq.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Cards | Mill cards | Aroma | Incense | Dawn |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Broken Time-Space | 3 | 41.1% | 0.4% | 53.6% | 11.8% | -0.0% | 0.91 | 1.73 | 18.85 | 0.55 | 1.13 | 1.04 |
| Team Rocket's Petrel | 4 | 41.0% | 0.5% | 53.3% | 10.8% | -0.1% | 0.92 | 1.75 | 18.88 | 0.55 | 1.09 | 1.04 |
| Rescue Scarf | 4 | 41.0% | 0.5% | 53.4% | 10.5% | -0.1% | 0.91 | 1.73 | 18.92 | 0.55 | 1.14 | 1.05 |
| Slumbering Forest | 1 | 40.8% | 0.4% | 53.4% | 10.4% | -0.2% | 0.92 | 1.75 | 18.84 | 0.54 | 1.13 | 1.05 |
| Energy Retrieval | 1 | 40.8% | 0.5% | 53.4% | 11.1% | -0.3% | 0.91 | 1.73 | 18.85 | 0.55 | 1.14 | 1.05 |
| Evolution Incense | 3 | 40.7% | 0.4% | 53.2% | 10.5% | -0.4% | 0.94 | 1.80 | 18.83 | 0.56 | 0.88 | 1.07 |
| Energy Search | 4 | 40.5% | 0.4% | 52.9% | 10.8% | -0.6% | 0.92 | 1.74 | 18.63 | 0.54 | 1.13 | 1.05 |
| Dawn | 4 | 40.4% | 0.5% | 52.6% | 10.2% | -0.7% | 0.95 | 1.80 | 18.40 | 0.57 | 1.16 | 0.83 |
| Level Ball | 2 | 40.2% | 0.5% | 52.5% | 10.8% | -0.9% | 0.91 | 1.74 | 18.41 | 0.57 | 1.12 | 1.05 |
| Buddy-Buddy Poffin | 2 | 40.0% | 0.4% | 52.4% | 10.8% | -1.1% | 0.91 | 1.74 | 18.57 | 0.55 | 1.13 | 1.05 |
| Fire Energy | 7 | 40.0% | 0.4% | 52.9% | 10.0% | -1.1% | 0.92 | 1.75 | 18.65 | 0.55 | 1.14 | 1.05 |
| Arven | 4 | 39.5% | 0.4% | 52.2% | 10.2% | -1.6% | 0.92 | 1.75 | 18.60 | 0.52 | 1.07 | 1.06 |
| Chandelure | 4 | 39.4% | 0.4% | 52.1% | 10.6% | -1.6% | 0.82 | 1.53 | 18.44 | 0.55 | 1.00 | 1.01 |
| Pichu | 3 | 39.1% | 0.4% | 51.7% | 9.1% | -1.9% | 0.90 | 1.72 | 18.24 | 0.56 | 1.10 | 1.01 |
| Hyper Aroma | 1 | 38.5% | 0.4% | 51.7% | 6.8% | -2.5% | 0.99 | 1.89 | 18.16 | 0.00 | 1.36 | 1.11 |
| Hisuian Heavy Ball | 1 | 38.0% | 0.4% | 50.0% | 8.9% | -3.1% | 0.90 | 1.71 | 17.84 | 0.59 | 1.16 | 1.06 |
| Litwick | 4 | 36.4% | 0.4% | 49.4% | 5.0% | -4.6% | 0.90 | 1.71 | 17.46 | 0.59 | 1.12 | 1.06 |
| Lampent | 4 | 36.1% | 0.4% | 48.6% | 7.6% | -4.9% | 0.88 | 1.68 | 17.35 | 0.43 | 1.12 | 1.07 |
| Celebi ◇ | 1 | 7.9% | 0.2% | 15.4% | 0.0% | -33.2% | 0.84 | 1.60 | 6.96 | 0.55 | 1.06 | 1.21 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 36.8% | 39.8% | 38.2% | +6.2% |
| Hedrick Worlds Dragapult | 58.2% | 57.2% | 57.8% | +5.5% |
| Unlimited Dragapult | 62.3% | 65.2% | 63.7% | +1.5% |
| Cornerstone Ogerpon (D60) | 13.0% | 15.0% | 14.0% | +2.3% |
| Wo-Chien / Floragato (S60) | 68.2% | 73.2% | 70.8% | +6.8% |
| Gholdengo (G) | 40.2% | 40.5% | 40.4% | +5.1% |
| Clefairy / Mewtwo (C60) | 41.2% | 48.5% | 44.9% | +6.5% |
| Set M (Mew ex) | 8.2% | 12.0% | 10.1% | -0.3% |
| Mega Starmie ex (Kudo) | 15.0% | 12.8% | 13.9% | +0.4% |
| Lucario Hariyama | 67.5% | 67.8% | 67.6% | -0.2% |
| Iron Thorns ex | 89.5% | 91.2% | 90.4% | -0.1% |
| Carpet Set H | 88.0% | 89.2% | 88.6% | -2.9% |
| Ambipom Hand Fling | 95.2% | 95.2% | 95.2% | +2.5% |
