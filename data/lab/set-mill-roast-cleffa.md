# Roast Cleffa greedy

Each step tries every other card as the one copy to replace with one Cleffa. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way. Stop at four, or when the next copy does not raise the score.

The starting 60 is the list locked after the Hyper Aroma search. Cleffa is HeartGold & SoulSilver Eeeeeeek. The kept cut at each step is the maximum of about twenty tries, so it is biased upward. Read the gain next to the standard error.

- **Seed**: `20261027`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 2709.2s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Cleffa played | Mill cards |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 38.5% | 0.4% | 51.0% | 10.4% | +0.0% | 0.00 | 0.00 | 18.00 |

## Decision

Kept list is locked: 0 Cleffa, weighted 38.5% against the starting list at 38.5% (+0.0%).

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
- Switch ×1
- Broken Time-Space ×3
- Slumbering Forest ×1
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×3
- Hyper Aroma ×1

## Step 1

List entering this step: weighted 38.5% ± 0.4%. Each row replaces one copy of that card with one Cleffa.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Cleffa played | Mill | Aroma | Incense | Dawn | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Switch | 1 | 38.1% | 0.4% | 49.9% | 10.2% | -0.4% | 0.02 | 0.41 | 17.60 | 0.67 | 1.38 | 1.22 | 0.906 |
| Energy Retrieval | 2 | 37.9% | 0.4% | 50.4% | 9.5% | -0.6% | 0.02 | 0.42 | 17.81 | 0.67 | 1.37 | 1.21 | 0.907 |
| Slumbering Forest | 1 | 37.7% | 0.4% | 50.1% | 8.5% | -0.8% | 0.02 | 0.42 | 17.73 | 0.67 | 1.35 | 1.22 | 0.904 |
| Level Ball | 2 | 37.3% | 0.4% | 49.2% | 7.3% | -1.2% | 0.02 | 0.40 | 17.39 | 0.68 | 1.35 | 1.21 | 0.899 |
| Team Rocket's Petrel | 4 | 37.0% | 0.4% | 49.3% | 9.0% | -1.5% | 0.02 | 0.41 | 17.49 | 0.65 | 1.30 | 1.21 | 0.903 |
| Broken Time-Space | 3 | 36.7% | 0.4% | 49.1% | 8.8% | -1.8% | 0.02 | 0.42 | 17.42 | 0.66 | 1.36 | 1.21 | 0.901 |
| Buddy-Buddy Poffin | 3 | 36.7% | 0.4% | 49.5% | 9.2% | -1.8% | 0.02 | 0.40 | 17.33 | 0.66 | 1.36 | 1.20 | 0.890 |
| Fire Energy | 7 | 36.6% | 0.4% | 48.6% | 9.1% | -1.9% | 0.02 | 0.43 | 17.45 | 0.66 | 1.33 | 1.22 | 0.906 |
| Evolution Incense | 3 | 36.6% | 0.4% | 48.9% | 8.4% | -1.9% | 0.02 | 0.42 | 17.23 | 0.68 | 1.03 | 1.25 | 0.899 |
| Energy Search | 4 | 36.6% | 0.4% | 49.0% | 9.0% | -1.9% | 0.02 | 0.42 | 17.54 | 0.67 | 1.36 | 1.22 | 0.905 |
| Pichu | 3 | 36.3% | 0.4% | 48.6% | 8.9% | -2.2% | 0.03 | 0.49 | 17.01 | 0.66 | 1.34 | 1.20 | 0.888 |
| Chandelure | 4 | 36.0% | 0.4% | 48.2% | 8.1% | -2.5% | 0.03 | 0.41 | 17.00 | 0.67 | 1.24 | 1.18 | 0.902 |
| Rescue Scarf | 4 | 35.8% | 0.4% | 48.5% | 7.6% | -2.7% | 0.02 | 0.41 | 17.32 | 0.65 | 1.37 | 1.22 | 0.901 |
| Dawn | 4 | 35.4% | 0.4% | 47.6% | 8.5% | -3.1% | 0.02 | 0.39 | 16.70 | 0.68 | 1.41 | 0.96 | 0.891 |
| Arven | 4 | 35.0% | 0.4% | 47.5% | 7.9% | -3.5% | 0.02 | 0.42 | 16.98 | 0.63 | 1.27 | 1.20 | 0.897 |
| Hisuian Heavy Ball | 1 | 34.7% | 0.4% | 46.3% | 7.9% | -3.8% | 0.02 | 0.42 | 16.53 | 0.72 | 1.43 | 1.21 | 0.897 |
| Hyper Aroma | 1 | 34.3% | 0.4% | 46.8% | 6.6% | -4.2% | 0.01 | 0.42 | 16.53 | 0.00 | 1.62 | 1.32 | 0.894 |
| Lampent | 4 | 34.2% | 0.4% | 46.2% | 7.4% | -4.3% | 0.02 | 0.42 | 16.40 | 0.57 | 1.36 | 1.24 | 0.896 |
| Litwick | 4 | 33.5% | 0.4% | 45.9% | 6.4% | -5.0% | 0.02 | 0.44 | 16.36 | 0.67 | 1.35 | 1.22 | 0.880 |
| Celebi ◇ | 1 | 7.1% | 0.2% | 13.8% | 0.0% | -31.4% | 0.02 | 0.63 | 6.41 | 0.68 | 1.30 | 1.35 | 0.900 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 32.2% | 31.8% | 32.0% | +0.0% |
| Hedrick Worlds Dragapult | 54.2% | 50.2% | 52.2% | +0.0% |
| Unlimited Dragapult | 64.2% | 60.2% | 62.3% | +0.0% |
| Cornerstone Ogerpon (D60) | 13.0% | 10.5% | 11.8% | +0.0% |
| Wo-Chien / Floragato (S60) | 64.8% | 63.2% | 64.0% | +0.0% |
| Gholdengo (G) | 33.8% | 36.8% | 35.2% | +0.0% |
| Clefairy / Mewtwo (C60) | 32.8% | 44.0% | 38.4% | +0.0% |
| Set M (Mew ex) | 12.5% | 8.2% | 10.4% | +0.0% |
| Mega Starmie ex (Kudo) | 14.8% | 12.2% | 13.5% | +0.0% |
| Lucario Hariyama | 66.5% | 69.2% | 67.9% | +0.0% |
| Iron Thorns ex | 91.2% | 89.8% | 90.5% | +0.0% |
| Carpet Set H | 91.2% | 91.8% | 91.5% | +0.0% |
| Ambipom Hand Fling | 93.0% | 92.5% | 92.8% | +0.0% |
