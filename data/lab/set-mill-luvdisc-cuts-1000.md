# Luvdisc vs every legal cut, 1000 games

One Luvdisc replaces one copy of a cuttable card on the locked Mill 60. The other 58 cards stay. Protected cards stay in the list: the babies, Manaphy, Wiglett, Wugtrio, Victini, Slumbering Forest, and Neutralization Zone. Paldea Evolved Luvdisc uses Matching and Water Pulse.

- **Seed**: `20261031`
- **Games per seat**: 1000
- **Seats**: Mill is player A and player B. A matchup cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 6959.4s

The ± column is one standard error of that list's weighted rate. Δ/SE is the gap divided by one standard error of the difference against the lock.

## Lists

| List | Left | Weighted | ± | Mean | Worst | Delta | Δ/SE | Matching | Supporters taken | Opponent Asleep | Luvdisc saw play | Undersea Tunnel |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | — | 42.52% | 0.30% | 57.32% | 7.85% | +0.00% | 0.00 | 0.000 | 0.000 | 0.002 | 0.0% | 3.308 |
| −Wally | 2 | 41.69% | 0.31% | 56.07% | 10.40% | -0.83% | -1.92 | 0.311 | 0.566 | 0.421 | 74.8% | 3.136 |
| −Level Ball | 3 | 41.41% | 0.31% | 55.97% | 10.90% | -1.11% | -2.57 | 0.304 | 0.549 | 0.425 | 72.8% | 3.139 |
| −Rescue Carrier | 2 | 41.36% | 0.30% | 55.95% | 9.50% | -1.16% | -2.69 | 0.301 | 0.540 | 0.404 | 74.6% | 3.161 |
| −Boss's Orders | 0 | 41.33% | 0.31% | 55.84% | 10.45% | -1.19% | -2.76 | 0.293 | 0.522 | 0.397 | 74.5% | 3.189 |
| −Lillie's Poké Doll | 0 | 41.07% | 0.30% | 55.67% | 9.30% | -1.45% | -3.37 | 0.293 | 0.532 | 0.413 | 74.5% | 3.189 |
| −Crushing Hammer | 3 | 41.06% | 0.30% | 55.58% | 10.45% | -1.46% | -3.38 | 0.303 | 0.547 | 0.404 | 74.9% | 3.166 |
| −Miss Fortune Sisters | 1 | 41.04% | 0.30% | 55.60% | 9.75% | -1.47% | -3.43 | 0.288 | 0.511 | 0.408 | 74.5% | 3.244 |
| −Buddy-Buddy Poffin | 3 | 40.81% | 0.31% | 55.15% | 9.65% | -1.71% | -3.96 | 0.293 | 0.526 | 0.393 | 71.2% | 3.136 |
| −Water Energy | 2 | 40.79% | 0.30% | 55.35% | 10.35% | -1.73% | -4.02 | 0.299 | 0.533 | 0.328 | 74.9% | 3.130 |
| −Team Rocket's Handiwork | 1 | 40.74% | 0.30% | 55.59% | 9.60% | -1.78% | -4.14 | 0.283 | 0.508 | 0.410 | 75.1% | 2.985 |
| −Counter Catcher | 1 | 40.74% | 0.30% | 55.30% | 10.85% | -1.78% | -4.14 | 0.287 | 0.520 | 0.407 | 74.1% | 3.163 |
| −Ignition Energy | 3 | 40.26% | 0.30% | 54.96% | 8.80% | -2.26% | -5.29 | 0.300 | 0.542 | 0.420 | 74.5% | 3.082 |
| −Colress's Tenacity | 3 | 39.96% | 0.30% | 54.57% | 9.75% | -2.56% | -5.98 | 0.292 | 0.527 | 0.370 | 73.9% | 3.099 |
| −Double Turbo Energy | 3 | 39.79% | 0.30% | 54.48% | 8.50% | -2.73% | -6.38 | 0.268 | 0.485 | 0.389 | 74.8% | 3.085 |
| −Reversal Energy | 3 | 39.44% | 0.30% | 54.33% | 7.80% | -3.08% | -7.22 | 0.280 | 0.506 | 0.391 | 74.9% | 3.077 |

## Decision

No cut beat the lock by more than one standard error. The closest is −Wally at 41.69% (-0.83%, difference ±0.43%). SET_MILL_NAMES stays the current 60. Luvdisc stays at zero copies.

## Lock, both seats

| Matchup | Weight | A | B | Mean |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 72.50% | 73.00% | 72.75% |
| Hedrick Worlds Dragapult | 5.1% | 58.90% | 61.20% | 60.05% |
| Unlimited Dragapult | 2.2% | 85.70% | 85.50% | 85.60% |
| Cornerstone Ogerpon (D60) | 14.5% | 8.70% | 7.00% | 7.85% |
| Wo-Chien / Floragato (S60) | 7.0% | 68.30% | 75.20% | 71.75% |
| Gholdengo (G) | 11.7% | 31.60% | 31.10% | 31.35% |
| Clefairy / Mewtwo (C60) | 12.4% | 40.00% | 40.90% | 40.45% |
| Set M (Mew ex) | 14.5% | 23.20% | 22.90% | 23.05% |
| Mega Starmie ex (Kudo) | 10.6% | 36.60% | 39.10% | 37.85% |
| Lucario Hariyama | 5.1% | 79.50% | 82.80% | 81.15% |
| Iron Thorns ex | 4.1% | 91.00% | 91.60% | 91.30% |
| Carpet Set H | 7.6% | 46.40% | 45.20% | 45.80% |
| Ambipom Hand Fling | 1.1% | 96.20% | 96.20% | 96.20% |

## −Wally, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 62.30% | 61.20% | 61.75% | -11.00% |
| Hedrick Worlds Dragapult | 5.1% | 59.30% | 60.70% | 60.00% | -0.05% |
| Unlimited Dragapult | 2.2% | 84.50% | 83.70% | 84.10% | -1.50% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.70% | 11.10% | 10.40% | +2.55% |
| Wo-Chien / Floragato (S60) | 7.0% | 68.60% | 67.90% | 68.25% | -3.50% |
| Gholdengo (G) | 11.7% | 30.70% | 31.40% | 31.05% | -0.30% |
| Clefairy / Mewtwo (C60) | 12.4% | 39.40% | 37.30% | 38.35% | -2.10% |
| Set M (Mew ex) | 14.5% | 21.30% | 19.20% | 20.25% | -2.80% |
| Mega Starmie ex (Kudo) | 10.6% | 35.80% | 35.10% | 35.45% | -2.40% |
| Lucario Hariyama | 5.1% | 78.40% | 82.80% | 80.60% | -0.55% |
| Iron Thorns ex | 4.1% | 93.00% | 90.90% | 91.95% | +0.65% |
| Carpet Set H | 7.6% | 50.20% | 54.60% | 52.40% | +6.60% |
| Ambipom Hand Fling | 1.1% | 94.70% | 94.10% | 94.40% | -1.80% |

## −Level Ball, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 62.00% | 63.50% | 62.75% | -10.00% |
| Hedrick Worlds Dragapult | 5.1% | 61.60% | 57.00% | 59.30% | -0.75% |
| Unlimited Dragapult | 2.2% | 86.70% | 86.70% | 86.70% | +1.10% |
| Cornerstone Ogerpon (D60) | 14.5% | 11.70% | 10.10% | 10.90% | +3.05% |
| Wo-Chien / Floragato (S60) | 7.0% | 68.30% | 69.40% | 68.85% | -2.90% |
| Gholdengo (G) | 11.7% | 30.80% | 29.30% | 30.05% | -1.30% |
| Clefairy / Mewtwo (C60) | 12.4% | 33.50% | 37.30% | 35.40% | -5.05% |
| Set M (Mew ex) | 14.5% | 20.90% | 23.70% | 22.30% | -0.75% |
| Mega Starmie ex (Kudo) | 10.6% | 35.40% | 33.10% | 34.25% | -3.60% |
| Lucario Hariyama | 5.1% | 79.80% | 80.30% | 80.05% | -1.10% |
| Iron Thorns ex | 4.1% | 90.60% | 92.30% | 91.45% | +0.15% |
| Carpet Set H | 7.6% | 52.70% | 49.50% | 51.10% | +5.30% |
| Ambipom Hand Fling | 1.1% | 94.60% | 94.40% | 94.50% | -1.70% |

## −Rescue Carrier, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 62.80% | 64.50% | 63.65% | -9.10% |
| Hedrick Worlds Dragapult | 5.1% | 59.80% | 62.00% | 60.90% | +0.85% |
| Unlimited Dragapult | 2.2% | 85.50% | 84.00% | 84.75% | -0.85% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.50% | 9.50% | 9.50% | +1.65% |
| Wo-Chien / Floragato (S60) | 7.0% | 67.20% | 66.40% | 66.80% | -4.95% |
| Gholdengo (G) | 11.7% | 29.30% | 29.20% | 29.25% | -2.10% |
| Clefairy / Mewtwo (C60) | 12.4% | 38.50% | 36.30% | 37.40% | -3.05% |
| Set M (Mew ex) | 14.5% | 22.90% | 20.70% | 21.80% | -1.25% |
| Mega Starmie ex (Kudo) | 10.6% | 36.80% | 34.70% | 35.75% | -2.10% |
| Lucario Hariyama | 5.1% | 80.30% | 79.40% | 79.85% | -1.30% |
| Iron Thorns ex | 4.1% | 90.90% | 91.90% | 91.40% | +0.10% |
| Carpet Set H | 7.6% | 51.10% | 50.70% | 50.90% | +5.10% |
| Ambipom Hand Fling | 1.1% | 95.90% | 95.00% | 95.45% | -0.75% |

## −Boss's Orders, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 61.90% | 63.70% | 62.80% | -9.95% |
| Hedrick Worlds Dragapult | 5.1% | 60.30% | 61.10% | 60.70% | +0.65% |
| Unlimited Dragapult | 2.2% | 84.70% | 84.50% | 84.60% | -1.00% |
| Cornerstone Ogerpon (D60) | 14.5% | 10.10% | 10.80% | 10.45% | +2.60% |
| Wo-Chien / Floragato (S60) | 7.0% | 67.40% | 68.60% | 68.00% | -3.75% |
| Gholdengo (G) | 11.7% | 31.20% | 29.80% | 30.50% | -0.85% |
| Clefairy / Mewtwo (C60) | 12.4% | 35.70% | 35.80% | 35.75% | -4.70% |
| Set M (Mew ex) | 14.5% | 22.30% | 21.60% | 21.95% | -1.10% |
| Mega Starmie ex (Kudo) | 10.6% | 34.20% | 34.00% | 34.10% | -3.75% |
| Lucario Hariyama | 5.1% | 81.20% | 81.60% | 81.40% | +0.25% |
| Iron Thorns ex | 4.1% | 89.20% | 92.20% | 90.70% | -0.60% |
| Carpet Set H | 7.6% | 49.60% | 51.30% | 50.45% | +4.65% |
| Ambipom Hand Fling | 1.1% | 96.40% | 92.70% | 94.55% | -1.65% |

## −Lillie's Poké Doll, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 64.60% | 62.00% | 63.30% | -9.45% |
| Hedrick Worlds Dragapult | 5.1% | 57.50% | 61.40% | 59.45% | -0.60% |
| Unlimited Dragapult | 2.2% | 84.00% | 85.10% | 84.55% | -1.05% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.50% | 9.10% | 9.30% | +1.45% |
| Wo-Chien / Floragato (S60) | 7.0% | 68.30% | 66.10% | 67.20% | -4.55% |
| Gholdengo (G) | 11.7% | 29.10% | 29.60% | 29.35% | -2.00% |
| Clefairy / Mewtwo (C60) | 12.4% | 37.10% | 34.70% | 35.90% | -4.55% |
| Set M (Mew ex) | 14.5% | 17.90% | 21.20% | 19.55% | -3.50% |
| Mega Starmie ex (Kudo) | 10.6% | 39.50% | 35.20% | 37.35% | -0.50% |
| Lucario Hariyama | 5.1% | 78.50% | 76.10% | 77.30% | -3.85% |
| Iron Thorns ex | 4.1% | 90.40% | 90.60% | 90.50% | -0.80% |
| Carpet Set H | 7.6% | 55.00% | 54.90% | 54.95% | +9.15% |
| Ambipom Hand Fling | 1.1% | 95.50% | 94.40% | 94.95% | -1.25% |

## −Crushing Hammer, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 60.40% | 63.20% | 61.80% | -10.95% |
| Hedrick Worlds Dragapult | 5.1% | 57.10% | 58.80% | 57.95% | -2.10% |
| Unlimited Dragapult | 2.2% | 85.10% | 85.00% | 85.05% | -0.55% |
| Cornerstone Ogerpon (D60) | 14.5% | 10.30% | 10.60% | 10.45% | +2.60% |
| Wo-Chien / Floragato (S60) | 7.0% | 66.40% | 67.70% | 67.05% | -4.70% |
| Gholdengo (G) | 11.7% | 31.30% | 29.10% | 30.20% | -1.15% |
| Clefairy / Mewtwo (C60) | 12.4% | 35.70% | 34.30% | 35.00% | -5.45% |
| Set M (Mew ex) | 14.5% | 20.70% | 21.00% | 20.85% | -2.20% |
| Mega Starmie ex (Kudo) | 10.6% | 37.00% | 34.50% | 35.75% | -2.10% |
| Lucario Hariyama | 5.1% | 79.70% | 79.20% | 79.45% | -1.70% |
| Iron Thorns ex | 4.1% | 91.00% | 90.90% | 90.95% | -0.35% |
| Carpet Set H | 7.6% | 52.80% | 52.40% | 52.60% | +6.80% |
| Ambipom Hand Fling | 1.1% | 95.00% | 95.80% | 95.40% | -0.80% |

## −Miss Fortune Sisters, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 63.10% | 61.40% | 62.25% | -10.50% |
| Hedrick Worlds Dragapult | 5.1% | 62.30% | 60.70% | 61.50% | +1.45% |
| Unlimited Dragapult | 2.2% | 81.80% | 84.50% | 83.15% | -2.45% |
| Cornerstone Ogerpon (D60) | 14.5% | 8.90% | 10.60% | 9.75% | +1.90% |
| Wo-Chien / Floragato (S60) | 7.0% | 66.00% | 66.40% | 66.20% | -5.55% |
| Gholdengo (G) | 11.7% | 31.20% | 29.40% | 30.30% | -1.05% |
| Clefairy / Mewtwo (C60) | 12.4% | 34.60% | 37.10% | 35.85% | -4.60% |
| Set M (Mew ex) | 14.5% | 19.70% | 20.40% | 20.05% | -3.00% |
| Mega Starmie ex (Kudo) | 10.6% | 34.90% | 35.10% | 35.00% | -2.85% |
| Lucario Hariyama | 5.1% | 81.10% | 78.10% | 79.60% | -1.55% |
| Iron Thorns ex | 4.1% | 91.50% | 91.20% | 91.35% | +0.05% |
| Carpet Set H | 7.6% | 55.60% | 50.90% | 53.25% | +7.45% |
| Ambipom Hand Fling | 1.1% | 95.10% | 94.10% | 94.60% | -1.60% |

## −Buddy-Buddy Poffin, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 61.10% | 63.30% | 62.20% | -10.55% |
| Hedrick Worlds Dragapult | 5.1% | 60.40% | 58.40% | 59.40% | -0.65% |
| Unlimited Dragapult | 2.2% | 84.80% | 83.50% | 84.15% | -1.45% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.40% | 9.90% | 9.65% | +1.80% |
| Wo-Chien / Floragato (S60) | 7.0% | 67.20% | 65.30% | 66.25% | -5.50% |
| Gholdengo (G) | 11.7% | 31.70% | 31.80% | 31.75% | +0.40% |
| Clefairy / Mewtwo (C60) | 12.4% | 36.10% | 35.70% | 35.90% | -4.55% |
| Set M (Mew ex) | 14.5% | 23.00% | 19.70% | 21.35% | -1.70% |
| Mega Starmie ex (Kudo) | 10.6% | 33.90% | 34.40% | 34.15% | -3.70% |
| Lucario Hariyama | 5.1% | 77.70% | 78.40% | 78.05% | -3.10% |
| Iron Thorns ex | 4.1% | 90.00% | 89.50% | 89.75% | -1.55% |
| Carpet Set H | 7.6% | 49.20% | 50.40% | 49.80% | +4.00% |
| Ambipom Hand Fling | 1.1% | 94.80% | 94.20% | 94.50% | -1.70% |

## −Water Energy, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 61.20% | 61.20% | 61.20% | -11.55% |
| Hedrick Worlds Dragapult | 5.1% | 61.10% | 59.70% | 60.40% | +0.35% |
| Unlimited Dragapult | 2.2% | 86.30% | 85.30% | 85.80% | +0.20% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.20% | 11.50% | 10.35% | +2.50% |
| Wo-Chien / Floragato (S60) | 7.0% | 63.50% | 68.20% | 65.85% | -5.90% |
| Gholdengo (G) | 11.7% | 27.20% | 30.00% | 28.60% | -2.75% |
| Clefairy / Mewtwo (C60) | 12.4% | 37.50% | 36.20% | 36.85% | -3.60% |
| Set M (Mew ex) | 14.5% | 22.70% | 20.40% | 21.55% | -1.50% |
| Mega Starmie ex (Kudo) | 10.6% | 35.70% | 31.70% | 33.70% | -4.15% |
| Lucario Hariyama | 5.1% | 80.10% | 80.60% | 80.35% | -0.80% |
| Iron Thorns ex | 4.1% | 90.10% | 92.10% | 91.10% | -0.20% |
| Carpet Set H | 7.6% | 50.40% | 47.90% | 49.15% | +3.35% |
| Ambipom Hand Fling | 1.1% | 94.30% | 94.90% | 94.60% | -1.60% |

## −Team Rocket's Handiwork, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 64.40% | 62.60% | 63.50% | -9.25% |
| Hedrick Worlds Dragapult | 5.1% | 60.30% | 58.80% | 59.55% | -0.50% |
| Unlimited Dragapult | 2.2% | 84.30% | 85.80% | 85.05% | -0.55% |
| Cornerstone Ogerpon (D60) | 14.5% | 10.30% | 8.90% | 9.60% | +1.75% |
| Wo-Chien / Floragato (S60) | 7.0% | 63.40% | 64.00% | 63.70% | -8.05% |
| Gholdengo (G) | 11.7% | 27.90% | 31.40% | 29.65% | -1.70% |
| Clefairy / Mewtwo (C60) | 12.4% | 34.30% | 34.30% | 34.30% | -6.15% |
| Set M (Mew ex) | 14.5% | 19.60% | 19.50% | 19.55% | -3.50% |
| Mega Starmie ex (Kudo) | 10.6% | 35.60% | 35.70% | 35.65% | -2.20% |
| Lucario Hariyama | 5.1% | 81.70% | 79.90% | 80.80% | -0.35% |
| Iron Thorns ex | 4.1% | 91.30% | 92.10% | 91.70% | +0.40% |
| Carpet Set H | 7.6% | 54.70% | 54.20% | 54.45% | +8.65% |
| Ambipom Hand Fling | 1.1% | 95.30% | 95.10% | 95.20% | -1.00% |

## −Counter Catcher, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 63.10% | 63.00% | 63.05% | -9.70% |
| Hedrick Worlds Dragapult | 5.1% | 57.60% | 58.30% | 57.95% | -2.10% |
| Unlimited Dragapult | 2.2% | 86.20% | 84.10% | 85.15% | -0.45% |
| Cornerstone Ogerpon (D60) | 14.5% | 10.60% | 11.10% | 10.85% | +3.00% |
| Wo-Chien / Floragato (S60) | 7.0% | 63.80% | 65.00% | 64.40% | -7.35% |
| Gholdengo (G) | 11.7% | 27.60% | 28.60% | 28.10% | -3.25% |
| Clefairy / Mewtwo (C60) | 12.4% | 35.40% | 35.30% | 35.35% | -5.10% |
| Set M (Mew ex) | 14.5% | 19.50% | 20.70% | 20.10% | -2.95% |
| Mega Starmie ex (Kudo) | 10.6% | 35.40% | 33.90% | 34.65% | -3.20% |
| Lucario Hariyama | 5.1% | 79.60% | 78.80% | 79.20% | -1.95% |
| Iron Thorns ex | 4.1% | 91.80% | 92.40% | 92.10% | +0.80% |
| Carpet Set H | 7.6% | 56.00% | 53.60% | 54.80% | +9.00% |
| Ambipom Hand Fling | 1.1% | 93.80% | 92.60% | 93.20% | -3.00% |

## −Ignition Energy, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 62.80% | 62.20% | 62.50% | -10.25% |
| Hedrick Worlds Dragapult | 5.1% | 58.20% | 59.40% | 58.80% | -1.25% |
| Unlimited Dragapult | 2.2% | 82.60% | 84.10% | 83.35% | -2.25% |
| Cornerstone Ogerpon (D60) | 14.5% | 9.20% | 8.40% | 8.80% | +0.95% |
| Wo-Chien / Floragato (S60) | 7.0% | 64.80% | 64.60% | 64.70% | -7.05% |
| Gholdengo (G) | 11.7% | 28.40% | 30.20% | 29.30% | -2.05% |
| Clefairy / Mewtwo (C60) | 12.4% | 33.10% | 33.60% | 33.35% | -7.10% |
| Set M (Mew ex) | 14.5% | 19.90% | 18.90% | 19.40% | -3.65% |
| Mega Starmie ex (Kudo) | 10.6% | 36.00% | 34.90% | 35.45% | -2.40% |
| Lucario Hariyama | 5.1% | 80.20% | 80.60% | 80.40% | -0.75% |
| Iron Thorns ex | 4.1% | 89.70% | 90.00% | 89.85% | -1.45% |
| Carpet Set H | 7.6% | 54.20% | 54.30% | 54.25% | +8.45% |
| Ambipom Hand Fling | 1.1% | 94.20% | 94.50% | 94.35% | -1.85% |

## −Colress's Tenacity, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 60.90% | 61.10% | 61.00% | -11.75% |
| Hedrick Worlds Dragapult | 5.1% | 59.20% | 57.00% | 58.10% | -1.95% |
| Unlimited Dragapult | 2.2% | 81.60% | 83.60% | 82.60% | -3.00% |
| Cornerstone Ogerpon (D60) | 14.5% | 10.80% | 8.70% | 9.75% | +1.90% |
| Wo-Chien / Floragato (S60) | 7.0% | 63.20% | 65.50% | 64.35% | -7.40% |
| Gholdengo (G) | 11.7% | 29.10% | 26.00% | 27.55% | -3.80% |
| Clefairy / Mewtwo (C60) | 12.4% | 35.80% | 36.40% | 36.10% | -4.35% |
| Set M (Mew ex) | 14.5% | 18.70% | 18.50% | 18.60% | -4.45% |
| Mega Starmie ex (Kudo) | 10.6% | 33.00% | 32.90% | 32.95% | -4.90% |
| Lucario Hariyama | 5.1% | 79.80% | 78.40% | 79.10% | -2.05% |
| Iron Thorns ex | 4.1% | 90.90% | 91.70% | 91.30% | +0.00% |
| Carpet Set H | 7.6% | 55.40% | 51.90% | 53.65% | +7.85% |
| Ambipom Hand Fling | 1.1% | 93.80% | 94.90% | 94.35% | -1.85% |

## −Double Turbo Energy, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 60.50% | 60.40% | 60.45% | -12.30% |
| Hedrick Worlds Dragapult | 5.1% | 58.90% | 56.00% | 57.45% | -2.60% |
| Unlimited Dragapult | 2.2% | 84.90% | 84.50% | 84.70% | -0.90% |
| Cornerstone Ogerpon (D60) | 14.5% | 8.50% | 8.50% | 8.50% | +0.65% |
| Wo-Chien / Floragato (S60) | 7.0% | 65.20% | 64.60% | 64.90% | -6.85% |
| Gholdengo (G) | 11.7% | 25.90% | 28.80% | 27.35% | -4.00% |
| Clefairy / Mewtwo (C60) | 12.4% | 34.30% | 33.80% | 34.05% | -6.40% |
| Set M (Mew ex) | 14.5% | 20.20% | 22.00% | 21.10% | -1.95% |
| Mega Starmie ex (Kudo) | 10.6% | 33.50% | 33.10% | 33.30% | -4.55% |
| Lucario Hariyama | 5.1% | 79.50% | 78.90% | 79.20% | -1.95% |
| Iron Thorns ex | 4.1% | 92.40% | 91.60% | 92.00% | +0.70% |
| Carpet Set H | 7.6% | 50.10% | 52.80% | 51.45% | +5.65% |
| Ambipom Hand Fling | 1.1% | 94.40% | 93.20% | 93.80% | -2.40% |

## −Reversal Energy, both seats

Delta is the two-seat mean against the lock.

| Matchup | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 4.0% | 63.20% | 60.80% | 62.00% | -10.75% |
| Hedrick Worlds Dragapult | 5.1% | 60.20% | 58.80% | 59.50% | -0.55% |
| Unlimited Dragapult | 2.2% | 82.70% | 85.30% | 84.00% | -1.60% |
| Cornerstone Ogerpon (D60) | 14.5% | 7.40% | 8.20% | 7.80% | -0.05% |
| Wo-Chien / Floragato (S60) | 7.0% | 65.30% | 64.20% | 64.75% | -7.00% |
| Gholdengo (G) | 11.7% | 25.90% | 27.30% | 26.60% | -4.75% |
| Clefairy / Mewtwo (C60) | 12.4% | 34.30% | 33.60% | 33.95% | -6.50% |
| Set M (Mew ex) | 14.5% | 19.30% | 21.00% | 20.15% | -2.90% |
| Mega Starmie ex (Kudo) | 10.6% | 33.90% | 33.80% | 33.85% | -4.00% |
| Lucario Hariyama | 5.1% | 78.70% | 77.40% | 78.05% | -3.10% |
| Iron Thorns ex | 4.1% | 91.60% | 91.20% | 91.40% | +0.10% |
| Carpet Set H | 7.6% | 51.10% | 48.30% | 49.70% | +3.90% |
| Ambipom Hand Fling | 1.1% | 94.30% | 94.70% | 94.50% | -1.70% |
