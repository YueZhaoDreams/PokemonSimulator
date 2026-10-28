# Roast Jacq greedy

Each step tries every other card as the one copy to replace with one Jacq. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

The starting 60 is the locked list: one Hisuian Heavy Ball in place of one Switch. Jacq searches the deck for up to 2 Evolution Pokémon. Roast takes Lampent while uncovered Litwick remain, counting Litwick that Playground will bench, then Chandelure once a Lampent is in hand or in play.

- **Seed**: `20261027`
- **Games per seat**: 40
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 286.2s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Jacq | Mill cards | Dawn | Heavy Ball | Playground |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 34.5% | 1.4% | 45.2% | 3.8% | +0.0% | 0.00 | 15.78 | 1.62 | 0.34 | 0.81 |

## Decision

Kept list is locked: 0 Jacq, weighted 34.5% against the locked list at 34.5% (+0.0%).

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

List entering this step: weighted 34.5% ± 1.4%. Each row replaces one copy of that card with one Jacq.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Jacq | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Litwick | 4 | 33.7% | 1.3% | 45.7% | 3.8% | -0.8% | 0.49 | 15.24 |
| Switch | 1 | 33.3% | 1.3% | 46.7% | 3.8% | -1.2% | 0.51 | 16.03 |
| Energy Search | 4 | 33.2% | 1.3% | 45.1% | 2.5% | -1.4% | 0.49 | 15.63 |
| Broken Time-Space | 3 | 32.8% | 1.3% | 45.2% | 3.8% | -1.7% | 0.47 | 15.48 |
| Cleffa | 2 | 32.5% | 1.2% | 44.7% | 3.8% | -2.0% | 0.50 | 15.86 |
| Pichu | 3 | 32.1% | 1.2% | 44.7% | 3.8% | -2.4% | 0.47 | 15.34 |
| Hisuian Heavy Ball | 1 | 31.9% | 1.3% | 44.2% | 2.5% | -2.6% | 0.51 | 15.03 |
| Team Rocket's Petrel | 4 | 31.7% | 1.2% | 44.9% | 2.5% | -2.8% | 0.45 | 15.66 |
| Slumbering Forest | 1 | 31.7% | 1.2% | 44.9% | 2.5% | -2.8% | 0.50 | 16.01 |
| Buddy-Buddy Poffin | 3 | 31.7% | 1.3% | 44.9% | 5.0% | -2.9% | 0.44 | 15.42 |
| Rescue Scarf | 4 | 31.4% | 1.2% | 44.0% | 3.8% | -3.1% | 0.49 | 15.46 |
| Ultra Ball | 1 | 31.1% | 1.2% | 44.1% | 3.8% | -3.4% | 0.50 | 15.72 |
| Dawn | 4 | 30.8% | 1.2% | 42.6% | 1.2% | -3.7% | 0.50 | 14.84 |
| Fire Energy | 7 | 30.7% | 1.3% | 41.7% | 3.8% | -3.8% | 0.53 | 14.97 |
| Arven | 4 | 30.5% | 1.2% | 42.8% | 2.5% | -4.0% | 0.50 | 15.02 |
| Energy Retrieval | 2 | 30.5% | 1.2% | 43.9% | 6.2% | -4.0% | 0.47 | 15.60 |
| Level Ball | 3 | 30.4% | 1.2% | 43.2% | 5.0% | -4.1% | 0.49 | 15.28 |
| Chandelure | 4 | 29.7% | 1.2% | 41.3% | 5.0% | -4.8% | 0.44 | 14.90 |
| Lampent | 4 | 29.5% | 1.3% | 42.2% | 6.2% | -5.0% | 0.49 | 14.85 |
| Celebi ◇ | 1 | 5.9% | 0.5% | 12.7% | 0.0% | -28.6% | 0.51 | 5.95 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 42.5% | 37.5% | 40.0% | +0.0% |
| Hedrick Worlds Dragapult | 50.0% | 35.0% | 42.5% | +0.0% |
| Unlimited Dragapult | 35.0% | 50.0% | 42.5% | +0.0% |
| Cornerstone Ogerpon (D60) | 7.5% | 10.0% | 8.8% | +0.0% |
| Wo-Chien / Floragato (S60) | 55.0% | 47.5% | 51.2% | +0.0% |
| Gholdengo (G) | 37.5% | 30.0% | 33.8% | +0.0% |
| Clefairy / Mewtwo (C60) | 35.0% | 37.5% | 36.2% | +0.0% |
| Set M (Mew ex) | 5.0% | 25.0% | 15.0% | +0.0% |
| Mega Starmie ex (Kudo) | 5.0% | 2.5% | 3.8% | +0.0% |
| Lucario Hariyama | 52.5% | 57.5% | 55.0% | +0.0% |
| Iron Thorns ex | 85.0% | 75.0% | 80.0% | +0.0% |
| Carpet Set H | 87.5% | 92.5% | 90.0% | +0.0% |
| Ambipom Hand Fling | 92.5% | 85.0% | 88.8% | +0.0% |
