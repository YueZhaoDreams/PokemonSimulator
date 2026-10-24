# Lillie's Poké Doll, long sample

Only this card. Every legal cut is measured at the full game count. A step keeps the cut with the higher loss-weighted win rate.

- **Seed**: `20261023`
- **Games per seat**: 1000
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Games played**: 832000
- **Elapsed**: 11898.0s

The ± column is one standard error of that list's weighted rate. A foe rate uses both seats.

## Greedy path

| Step | Add | Cut | Weighted | ± | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | — | — | 37.9% | 0.3% | 54.1% | 6.5% | +0.0% | 0.00 | 0.00 | 0.00 | 0.00 | 2.90 |
| step 1 | Lillie's Poké Doll | Switch | 38.8% | 0.3% | 54.8% | 7.0% | +0.9% | 0.22 | 0.10 | 0.19 | 0.12 | 2.90 |

## Decision

Best list is step 1: weighted 38.8% vs the locked Mill at 37.9% (+0.9%, ±0.4%). Mean 54.8% (+0.7%). Locked 2026-10-24: `SET_MILL_NAMES` is this list, one Lillie's Poké Doll in place of the one Switch. The 120-game pass kept a Buddy-Buddy Poffin cut. On this sample that cut is flat.

Counts on that list:

- Lillie's Poké Doll: 1

## Step 1 cuts

List entering this step: weighted 37.9% ± 0.3%. Each row replaces one card with one Lillie's Poké Doll.

| Cut | Weighted | ± | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Switch | 38.8% | 0.3% | 54.8% | 7.0% | +0.9% | 0.22 | 0.10 | 0.19 | 0.12 | 2.90 |
| Boss's Orders | 38.5% | 0.3% | 54.4% | 7.3% | +0.6% | 0.22 | 0.10 | 0.20 | 0.13 | 2.91 |
| Nest Ball | 38.4% | 0.3% | 54.3% | 6.3% | +0.5% | 0.22 | 0.10 | 0.20 | 0.13 | 2.89 |
| Team Rocket's Handiwork | 38.1% | 0.3% | 54.2% | 6.2% | +0.2% | 0.22 | 0.10 | 0.20 | 0.13 | 2.73 |
| Crispin | 38.0% | 0.3% | 54.1% | 7.0% | +0.1% | 0.23 | 0.10 | 0.21 | 0.13 | 2.88 |
| Buddy-Buddy Poffin | 38.0% | 0.3% | 53.9% | 6.9% | +0.1% | 0.22 | 0.10 | 0.20 | 0.12 | 2.89 |
| Miss Fortune Sisters | 37.9% | 0.3% | 54.2% | 6.8% | +0.1% | 0.23 | 0.10 | 0.20 | 0.13 | 2.95 |
| Counter Catcher | 37.9% | 0.3% | 53.7% | 7.0% | -0.0% | 0.22 | 0.10 | 0.20 | 0.13 | 2.89 |
| Crushing Hammer | 37.9% | 0.3% | 53.8% | 5.1% | -0.0% | 0.23 | 0.10 | 0.19 | 0.13 | 2.90 |
| Double Turbo Energy | 37.8% | 0.3% | 53.9% | 6.2% | -0.1% | 0.22 | 0.10 | 0.19 | 0.13 | 2.85 |
| Reversal Energy | 37.6% | 0.3% | 53.8% | 6.2% | -0.2% | 0.23 | 0.10 | 0.20 | 0.13 | 2.83 |
| Rescue Carrier | 37.5% | 0.3% | 53.8% | 5.7% | -0.3% | 0.22 | 0.10 | 0.21 | 0.13 | 2.86 |
| Ignition Energy | 37.4% | 0.3% | 53.7% | 5.5% | -0.5% | 0.23 | 0.10 | 0.21 | 0.13 | 2.84 |
| Water Energy | 37.4% | 0.3% | 53.4% | 7.0% | -0.5% | 0.23 | 0.10 | 0.20 | 0.13 | 2.87 |
| Colress's Tenacity | 37.3% | 0.3% | 53.3% | 5.9% | -0.6% | 0.23 | 0.10 | 0.20 | 0.13 | 2.82 |
| Level Ball | 36.7% | 0.3% | 52.8% | 5.8% | -1.2% | 0.23 | 0.10 | 0.21 | 0.13 | 2.78 |

Kept −Switch at 38.8% (+0.9%).

## Step 2 cuts

List entering this step: weighted 38.8% ± 0.3%. Each row replaces one card with one Lillie's Poké Doll.

| Cut | Weighted | ± | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter Catcher | 38.6% | 0.3% | 54.4% | 7.3% | -0.1% | 0.42 | 0.21 | 0.36 | 0.24 | 2.90 |
| Boss's Orders | 38.3% | 0.3% | 54.4% | 6.2% | -0.4% | 0.42 | 0.21 | 0.36 | 0.24 | 2.92 |
| Ignition Energy | 38.2% | 0.3% | 54.3% | 7.0% | -0.6% | 0.42 | 0.21 | 0.37 | 0.24 | 2.85 |
| Miss Fortune Sisters | 38.1% | 0.3% | 54.1% | 5.5% | -0.6% | 0.42 | 0.20 | 0.36 | 0.24 | 2.93 |
| Nest Ball | 38.0% | 0.3% | 54.2% | 6.8% | -0.8% | 0.42 | 0.20 | 0.36 | 0.24 | 2.89 |
| Buddy-Buddy Poffin | 38.0% | 0.3% | 54.0% | 6.7% | -0.8% | 0.42 | 0.20 | 0.36 | 0.24 | 2.87 |
| Crushing Hammer | 37.9% | 0.3% | 54.0% | 5.8% | -0.9% | 0.42 | 0.20 | 0.36 | 0.24 | 2.90 |
| Crispin | 37.8% | 0.3% | 53.8% | 6.6% | -1.0% | 0.42 | 0.20 | 0.37 | 0.24 | 2.88 |
| Rescue Carrier | 37.8% | 0.3% | 54.0% | 6.8% | -1.0% | 0.42 | 0.21 | 0.37 | 0.25 | 2.86 |
| Double Turbo Energy | 37.6% | 0.3% | 53.8% | 6.2% | -1.1% | 0.42 | 0.21 | 0.37 | 0.24 | 2.84 |
| Water Energy | 37.4% | 0.3% | 53.5% | 6.2% | -1.3% | 0.42 | 0.21 | 0.37 | 0.24 | 2.85 |
| Team Rocket's Handiwork | 37.3% | 0.3% | 53.6% | 7.4% | -1.5% | 0.42 | 0.21 | 0.36 | 0.24 | 2.70 |
| Level Ball | 37.1% | 0.3% | 52.9% | 5.9% | -1.7% | 0.43 | 0.21 | 0.38 | 0.25 | 2.78 |
| Reversal Energy | 37.0% | 0.3% | 53.3% | 6.0% | -1.7% | 0.42 | 0.20 | 0.36 | 0.24 | 2.82 |
| Colress's Tenacity | 37.0% | 0.3% | 53.0% | 5.9% | -1.8% | 0.42 | 0.21 | 0.36 | 0.24 | 2.81 |

No cut in this step was higher than the list already kept. The search stopped.

## Foes at the best list

| Foe | A | B | Mean | Delta vs lock |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 72.1% | 74.8% | 73.4% | +0.6% |
| Hedrick Worlds Dragapult | 60.9% | 60.4% | 60.7% | +1.2% |
| Unlimited Dragapult | 85.5% | 85.1% | 85.3% | +1.2% |
| Cornerstone Ogerpon (D60) | 7.1% | 6.8% | 7.0% | +0.5% |
| Wo-Chien / Floragato (S60) | 68.6% | 70.0% | 69.3% | +0.4% |
| Gholdengo (G) | 27.3% | 27.5% | 27.4% | +2.1% |
| Clefairy / Mewtwo (C60) | 33.0% | 30.8% | 31.9% | +2.3% |
| Set M (Mew ex) | 16.7% | 14.6% | 15.7% | +1.0% |
| Mega Starmie ex (Kudo) | 32.0% | 29.9% | 30.9% | -0.1% |
| Lucario Hariyama | 81.7% | 81.1% | 81.4% | +2.9% |
| Iron Thorns ex | 92.0% | 92.1% | 92.1% | +0.5% |
| Carpet Set H | 45.0% | 41.9% | 43.5% | -1.5% |
| Ambipom Hand Fling | 92.5% | 94.8% | 93.7% | -1.8% |
