# Roast Hisuian Heavy Ball greedy

Each step tries every other card as the one copy to replace with one Hisuian Heavy Ball. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

Hisuian Heavy Ball looks at the face-down Prize cards and may reveal a Basic Pokémon, put it into the hand, and leave this card in that prize.

- **Seed**: `20261027`
- **Games per seat**: 40
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 551.7s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Heavy Ball | Mill cards | Dawn | Playground |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dawn | 0 | — | 30.3% | 1.2% | 41.2% | 2.5% | +0.0% | 0.00 | 14.90 | 1.64 | 0.81 |
| 1 Heavy Ball | 1 | Switch | 34.5% | 1.4% | 45.2% | 3.8% | +4.2% | 0.34 | 15.78 | 1.62 | 0.81 |

## Decision

Kept list is 1 Heavy Ball: 1 Hisuian Heavy Ball, weighted 34.5% against the Dawn list at 30.3% (+4.2%).

Counts:

- Litwick ×4
- Lampent ×4
- Chandelure ×4
- Celebi ◇ ×1
- Pichu ×3
- Cleffa ×2
- Arven ×4
- Team Rocket's Petrel ×4
- Buddy-Buddy Poffin ×3
- Energy Search ×4
- Energy Retrieval ×2
- Rescue Scarf ×4
- Dawn ×4
- Level Ball ×3
- Ultra Ball ×1
- Switch ×1
- Broken Time-Space ×3
- Slumbering Forest ×1
- Fire Energy ×7
- Hisuian Heavy Ball ×1

## Step 1

List entering this step: weighted 30.3% ± 1.2%. Each row replaces one copy of that card with one Hisuian Heavy Ball.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Heavy Ball | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Switch | 2 | 34.5% | 1.4% | 45.2% | 3.8% | +4.2% | 0.34 | 15.78 |
| Cleffa | 2 | 33.9% | 1.3% | 45.4% | 6.2% | +3.7% | 0.33 | 15.66 |
| Buddy-Buddy Poffin | 3 | 33.1% | 1.3% | 45.7% | 7.5% | +2.8% | 0.35 | 15.54 |
| Fire Energy | 7 | 32.9% | 1.3% | 43.8% | 3.8% | +2.7% | 0.36 | 15.27 |
| Slumbering Forest | 1 | 32.9% | 1.3% | 45.8% | 3.8% | +2.7% | 0.33 | 15.70 |
| Broken Time-Space | 3 | 32.0% | 1.2% | 45.1% | 2.5% | +1.8% | 0.35 | 15.88 |
| Pichu | 3 | 31.9% | 1.3% | 43.2% | 1.2% | +1.7% | 0.36 | 15.07 |
| Energy Search | 4 | 31.9% | 1.2% | 44.2% | 2.5% | +1.6% | 0.36 | 15.49 |
| Energy Retrieval | 2 | 31.5% | 1.3% | 42.5% | 5.0% | +1.3% | 0.34 | 15.36 |
| Arven | 4 | 30.8% | 1.2% | 43.2% | 0.0% | +0.5% | 0.33 | 15.27 |
| Litwick | 4 | 30.6% | 1.2% | 43.8% | 5.0% | +0.3% | 0.31 | 15.05 |
| Rescue Scarf | 4 | 30.5% | 1.3% | 42.7% | 1.2% | +0.3% | 0.36 | 15.29 |
| Team Rocket's Petrel | 4 | 29.9% | 1.2% | 43.0% | 5.0% | -0.3% | 0.34 | 14.99 |
| Chandelure | 4 | 29.9% | 1.3% | 41.3% | 7.5% | -0.4% | 0.36 | 15.10 |
| Ultra Ball | 1 | 29.8% | 1.2% | 41.7% | 3.8% | -0.5% | 0.33 | 15.07 |
| Dawn | 4 | 29.6% | 1.2% | 42.1% | 2.5% | -0.7% | 0.34 | 14.60 |
| Level Ball | 3 | 28.8% | 1.2% | 41.5% | 0.0% | -1.4% | 0.33 | 15.06 |
| Lampent | 4 | 27.3% | 1.1% | 40.2% | 2.5% | -2.9% | 0.33 | 14.36 |
| Celebi ◇ | 1 | 7.3% | 0.6% | 13.7% | 0.0% | -22.9% | 0.37 | 5.81 |

Kept −Switch at 34.5% (+4.2%).

## Step 2

List entering this step: weighted 34.5% ± 1.4%. Each row replaces one copy of that card with one Hisuian Heavy Ball.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Heavy Ball | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pichu | 3 | 34.0% | 1.3% | 46.4% | 5.0% | -0.5% | 0.52 | 15.90 |
| Cleffa | 2 | 33.0% | 1.3% | 45.5% | 8.8% | -1.5% | 0.49 | 15.98 |
| Fire Energy | 7 | 32.9% | 1.3% | 45.4% | 5.0% | -1.6% | 0.44 | 15.66 |
| Buddy-Buddy Poffin | 3 | 32.8% | 1.3% | 45.4% | 2.5% | -1.7% | 0.43 | 15.72 |
| Slumbering Forest | 1 | 32.4% | 1.2% | 45.3% | 2.5% | -2.1% | 0.47 | 15.74 |
| Lampent | 4 | 32.3% | 1.3% | 42.7% | 3.8% | -2.3% | 0.46 | 15.18 |
| Broken Time-Space | 3 | 32.0% | 1.3% | 44.0% | 6.2% | -2.5% | 0.44 | 15.57 |
| Energy Search | 4 | 31.8% | 1.2% | 44.4% | 5.0% | -2.7% | 0.44 | 15.35 |
| Switch | 1 | 31.4% | 1.3% | 43.3% | 3.8% | -3.1% | 0.47 | 15.89 |
| Energy Retrieval | 2 | 31.3% | 1.2% | 43.8% | 7.5% | -3.2% | 0.44 | 15.73 |
| Ultra Ball | 1 | 31.2% | 1.2% | 43.4% | 5.0% | -3.3% | 0.47 | 15.45 |
| Level Ball | 3 | 31.0% | 1.2% | 44.4% | 3.8% | -3.5% | 0.44 | 15.31 |
| Team Rocket's Petrel | 4 | 30.7% | 1.2% | 43.2% | 1.2% | -3.8% | 0.45 | 15.12 |
| Dawn | 4 | 30.6% | 1.2% | 43.2% | 1.2% | -3.9% | 0.48 | 14.97 |
| Arven | 4 | 30.4% | 1.3% | 42.8% | 7.5% | -4.2% | 0.42 | 15.48 |
| Chandelure | 4 | 29.9% | 1.2% | 43.4% | 2.5% | -4.6% | 0.43 | 15.14 |
| Litwick | 4 | 29.7% | 1.2% | 41.6% | 2.5% | -4.8% | 0.38 | 14.77 |
| Rescue Scarf | 4 | 29.7% | 1.2% | 43.2% | 2.5% | -4.8% | 0.44 | 15.32 |
| Celebi ◇ | 1 | 6.2% | 0.5% | 12.4% | 0.0% | -28.3% | 0.47 | 5.90 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs Dawn |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 42.5% | 37.5% | 40.0% | +6.2% |
| Hedrick Worlds Dragapult | 50.0% | 35.0% | 42.5% | -7.5% |
| Unlimited Dragapult | 35.0% | 50.0% | 42.5% | +1.3% |
| Cornerstone Ogerpon (D60) | 7.5% | 10.0% | 8.8% | +6.2% |
| Wo-Chien / Floragato (S60) | 55.0% | 47.5% | 51.2% | -12.5% |
| Gholdengo (G) | 37.5% | 30.0% | 33.8% | +12.5% |
| Clefairy / Mewtwo (C60) | 35.0% | 37.5% | 36.2% | -1.3% |
| Set M (Mew ex) | 5.0% | 25.0% | 15.0% | +11.2% |
| Mega Starmie ex (Kudo) | 5.0% | 2.5% | 3.8% | +1.3% |
| Lucario Hariyama | 52.5% | 57.5% | 55.0% | +0.0% |
| Iron Thorns ex | 85.0% | 75.0% | 80.0% | +7.5% |
| Carpet Set H | 87.5% | 92.5% | 90.0% | +10.0% |
| Ambipom Hand Fling | 92.5% | 85.0% | 88.8% | +16.2% |
