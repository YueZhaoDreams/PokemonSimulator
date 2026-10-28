# Roast Hyper Aroma greedy

One step tries every other card as the single copy to replace with Hyper Aroma. The cut is kept only when its Sisters-weighted win rate is strictly higher. Hyper Aroma is an ACE SPEC, so the search stops at one copy.

The starting 60 is the locked three-Incense list: zero Cleffa and zero Hyper Aroma. Hyper Aroma searches the deck for up to 3 Stage 1 Pokémon. Roast takes Lampent and stops once four Lampent are in hand or in play.

The kept cut is the maximum of about twenty tries, so it is biased upward. Read the gain next to the standard error.

- **Seed**: `20261027`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 2726.3s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Aroma | Cards | Lampent | Mill cards |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 34.4% | 0.4% | 47.3% | 7.4% | +0.0% | 0.00 | 0.00 | 0.00 | 16.63 |
| 1 Hyper Aroma | 1 | Ultra Ball | 38.5% | 0.4% | 51.0% | 10.4% | +4.1% | 0.67 | 1.63 | 1.63 | 18.00 |

## Decision

Kept list is 1 Hyper Aroma: 1 Hyper Aroma, weighted 38.5% against the locked list at 34.4% (+4.1%).

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

List entering this step: weighted 34.4% ± 0.4%. Each row replaces one copy of that card with one Hyper Aroma.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Aroma | Cards | Lampent | Mill | Incense | Dawn | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ultra Ball | 1 | 38.5% | 0.4% | 51.0% | 10.4% | +4.1% | 0.67 | 1.63 | 1.63 | 18.00 | 1.36 | 1.19 | 0.910 |
| Energy Retrieval | 2 | 37.8% | 0.4% | 50.6% | 10.1% | +3.4% | 0.66 | 1.60 | 1.60 | 17.89 | 1.34 | 1.18 | 0.915 |
| Slumbering Forest | 1 | 37.8% | 0.4% | 50.7% | 7.8% | +3.4% | 0.66 | 1.59 | 1.59 | 17.88 | 1.33 | 1.19 | 0.910 |
| Energy Search | 4 | 37.5% | 0.4% | 50.2% | 9.0% | +3.2% | 0.67 | 1.63 | 1.63 | 17.84 | 1.34 | 1.18 | 0.916 |
| Broken Time-Space | 3 | 37.2% | 0.4% | 50.1% | 7.4% | +2.9% | 0.66 | 1.61 | 1.61 | 17.78 | 1.33 | 1.18 | 0.916 |
| Switch | 1 | 37.1% | 0.4% | 49.8% | 8.8% | +2.7% | 0.67 | 1.63 | 1.63 | 17.80 | 1.38 | 1.18 | 0.916 |
| Level Ball | 2 | 36.9% | 0.4% | 49.7% | 7.1% | +2.5% | 0.67 | 1.64 | 1.64 | 17.63 | 1.34 | 1.17 | 0.904 |
| Pichu | 3 | 36.9% | 0.4% | 49.9% | 7.4% | +2.5% | 0.66 | 1.60 | 1.60 | 17.38 | 1.34 | 1.16 | 0.899 |
| Buddy-Buddy Poffin | 3 | 36.9% | 0.4% | 49.8% | 10.0% | +2.5% | 0.65 | 1.57 | 1.57 | 17.56 | 1.34 | 1.18 | 0.906 |
| Rescue Scarf | 4 | 36.9% | 0.4% | 49.7% | 7.5% | +2.5% | 0.66 | 1.60 | 1.60 | 17.66 | 1.35 | 1.17 | 0.913 |
| Evolution Incense | 3 | 36.8% | 0.4% | 49.4% | 8.0% | +2.4% | 0.66 | 1.62 | 1.62 | 17.40 | 1.03 | 1.21 | 0.908 |
| Team Rocket's Petrel | 4 | 36.7% | 0.4% | 49.4% | 7.5% | +2.3% | 0.64 | 1.54 | 1.54 | 17.61 | 1.31 | 1.17 | 0.911 |
| Fire Energy | 7 | 36.4% | 0.4% | 49.4% | 8.6% | +2.0% | 0.66 | 1.60 | 1.60 | 17.60 | 1.34 | 1.18 | 0.914 |
| Arven | 4 | 36.0% | 0.4% | 49.0% | 8.0% | +1.7% | 0.62 | 1.52 | 1.52 | 17.43 | 1.28 | 1.18 | 0.911 |
| Dawn | 4 | 35.8% | 0.4% | 48.8% | 6.5% | +1.4% | 0.68 | 1.67 | 1.67 | 16.97 | 1.39 | 0.92 | 0.893 |
| Chandelure | 4 | 35.8% | 0.4% | 48.4% | 9.5% | +1.4% | 0.65 | 1.59 | 1.59 | 17.18 | 1.24 | 1.14 | 0.907 |
| Hisuian Heavy Ball | 1 | 35.1% | 0.4% | 47.5% | 8.6% | +0.7% | 0.71 | 1.73 | 1.73 | 16.92 | 1.40 | 1.18 | 0.908 |
| Lampent | 4 | 34.2% | 0.4% | 47.0% | 7.8% | -0.2% | 0.57 | 1.18 | 1.18 | 16.67 | 1.34 | 1.19 | 0.903 |
| Litwick | 4 | 33.8% | 0.4% | 46.6% | 4.4% | -0.5% | 0.69 | 1.66 | 1.66 | 16.47 | 1.34 | 1.17 | 0.892 |
| Celebi ◇ | 1 | 7.3% | 0.2% | 14.3% | 0.0% | -27.1% | 0.67 | 1.64 | 1.64 | 6.45 | 1.27 | 1.34 | 0.913 |

Kept −Ultra Ball at 38.5% (+4.1%).

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 32.2% | 31.8% | 32.0% | +1.4% |
| Hedrick Worlds Dragapult | 54.2% | 50.2% | 52.2% | +3.1% |
| Unlimited Dragapult | 64.2% | 60.2% | 62.3% | +4.0% |
| Cornerstone Ogerpon (D60) | 13.0% | 10.5% | 11.8% | +4.0% |
| Wo-Chien / Floragato (S60) | 64.8% | 63.2% | 64.0% | +4.5% |
| Gholdengo (G) | 33.8% | 36.8% | 35.2% | +9.4% |
| Clefairy / Mewtwo (C60) | 32.8% | 44.0% | 38.4% | +4.0% |
| Set M (Mew ex) | 12.5% | 8.2% | 10.4% | +3.0% |
| Mega Starmie ex (Kudo) | 14.8% | 12.2% | 13.5% | +2.5% |
| Lucario Hariyama | 66.5% | 69.2% | 67.9% | +3.7% |
| Iron Thorns ex | 91.2% | 89.8% | 90.5% | +4.9% |
| Carpet Set H | 91.2% | 91.8% | 91.5% | +3.5% |
| Ambipom Hand Fling | 93.0% | 92.5% | 92.8% | -0.9% |
