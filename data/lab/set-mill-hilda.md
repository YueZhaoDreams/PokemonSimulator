# Mill Hilda greedy

Each step tries every other card as the one copy to replace with one Hilda. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

The starting 60 is the locked Wiglett Mill. Hilda's printed sentence searches the deck for an Evolution Pokémon and an Energy card. Mill takes Wugtrio and the Energy that pays Undersea Tunnel: Reversal Energy while more Prize cards remain, otherwise Ignition Energy, then Double Turbo Energy. Wally still evolves a Wiglett that can attack this turn, including one played this turn. Level Ball and Poffin stay ahead while no Wiglett is in play or in hand.

- **Seed**: `20261106`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 17767.0s

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Hilda | Evo | Energy | Mill cards | Wally |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 43.4% | 0.5% | 57.6% | 10.6% | +0.0% | 0.11 | 0.11 | 0.11 | 15.87 | 0.67 |
| 1 Hilda | 1 | Manaphy | 46.6% | 0.5% | 60.9% | 12.9% | +3.2% | 0.39 | 0.37 | 0.39 | 16.96 | 0.62 |
| 2 Hilda | 2 | Wally | 47.8% | 0.5% | 61.8% | 15.0% | +4.4% | 0.66 | 0.62 | 0.66 | 17.42 | 0.44 |
| 3 Hilda | 3 | Counter Catcher | 49.0% | 0.5% | 62.8% | 17.8% | +5.6% | 0.92 | 0.85 | 0.92 | 17.87 | 0.41 |
| 4 Hilda | 4 | Ignition Energy | 50.1% | 0.5% | 63.7% | 13.4% | +6.7% | 1.17 | 1.06 | 1.17 | 18.25 | 0.37 |

## Decision

Kept list is 4 Hilda: 4 Hilda, weighted 50.1% against the locked list at 43.4% (+6.7%, 9.45 combined standard errors).

The step keeps the best of the cuts on this seed, so that gain sits a little high.

Counts:

- Pichu ×1
- Mime Jr. ×1
- Cleffa ×1
- Wiglett ×4
- Wugtrio ×4
- Victini ×1
- Slumbering Forest ×1
- Neutralization Zone ×1
- Buddy-Buddy Poffin ×4
- Level Ball ×4
- Rescue Carrier ×3
- Lillie's Poké Doll ×1
- Crushing Hammer ×4
- Counter Catcher ×1
- Miss Fortune Sisters ×2
- Wally ×2
- Igglybuff ×1
- Team Rocket's Handiwork ×2
- Colress's Tenacity ×4
- Double Turbo Energy ×4
- Water Energy ×3
- Ignition Energy ×3
- Reversal Energy ×4
- Hilda ×4

## Step 1

List entering this step: weighted 43.4% ± 0.5%. Each row replaces one copy of that card with one Hilda.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Hilda | Evo | Energy | Mill cards | Wally |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Manaphy | 1 | 46.6% | 0.5% | 60.9% | 12.9% | +3.2% | 0.39 | 0.37 | 0.39 | 16.96 | 0.62 |
| Double Turbo Energy | 4 | 46.6% | 0.5% | 60.7% | 13.5% | +3.2% | 0.42 | 0.39 | 0.41 | 16.56 | 0.63 |
| Wally | 3 | 45.6% | 0.5% | 59.8% | 13.2% | +2.2% | 0.41 | 0.39 | 0.40 | 16.59 | 0.47 |
| Colress's Tenacity | 4 | 45.5% | 0.5% | 59.6% | 13.0% | +2.1% | 0.40 | 0.38 | 0.40 | 16.34 | 0.62 |
| Pichu | 1 | 45.3% | 0.5% | 59.1% | 13.0% | +1.8% | 0.40 | 0.38 | 0.39 | 16.50 | 0.62 |
| Level Ball | 4 | 45.2% | 0.5% | 59.2% | 11.6% | +1.8% | 0.40 | 0.38 | 0.39 | 16.56 | 0.64 |
| Miss Fortune Sisters | 2 | 45.1% | 0.5% | 59.7% | 12.2% | +1.7% | 0.40 | 0.38 | 0.39 | 17.01 | 0.64 |
| Mime Jr. | 1 | 45.0% | 0.5% | 59.3% | 12.1% | +1.6% | 0.39 | 0.37 | 0.39 | 16.93 | 0.62 |
| Wugtrio | 4 | 44.9% | 0.5% | 59.2% | 12.6% | +1.5% | 0.40 | 0.35 | 0.39 | 16.42 | 0.62 |
| Counter Catcher | 2 | 44.8% | 0.5% | 58.7% | 12.9% | +1.4% | 0.40 | 0.38 | 0.39 | 16.74 | 0.63 |
| Team Rocket's Handiwork | 2 | 44.8% | 0.5% | 59.6% | 12.5% | +1.4% | 0.40 | 0.38 | 0.40 | 16.37 | 0.64 |
| Crushing Hammer | 4 | 44.8% | 0.5% | 59.3% | 9.1% | +1.3% | 0.41 | 0.39 | 0.40 | 16.68 | 0.63 |
| Lillie's Poké Doll | 1 | 44.7% | 0.5% | 59.3% | 12.6% | +1.3% | 0.40 | 0.37 | 0.39 | 16.72 | 0.63 |
| Reversal Energy | 4 | 44.5% | 0.5% | 58.9% | 11.9% | +1.1% | 0.40 | 0.38 | 0.40 | 16.32 | 0.62 |
| Water Energy | 3 | 44.4% | 0.5% | 58.5% | 12.8% | +1.0% | 0.41 | 0.39 | 0.41 | 16.38 | 0.64 |
| Igglybuff | 1 | 44.3% | 0.5% | 58.8% | 8.0% | +0.9% | 0.39 | 0.37 | 0.39 | 16.70 | 0.63 |
| Slumbering Forest | 1 | 44.1% | 0.5% | 59.1% | 8.5% | +0.7% | 0.39 | 0.37 | 0.39 | 16.72 | 0.62 |
| Wiglett | 4 | 44.1% | 0.5% | 58.4% | 12.4% | +0.6% | 0.40 | 0.38 | 0.39 | 16.05 | 0.58 |
| Cleffa | 1 | 44.0% | 0.5% | 58.8% | 11.8% | +0.6% | 0.39 | 0.36 | 0.38 | 16.32 | 0.62 |
| Ignition Energy | 4 | 44.0% | 0.5% | 58.4% | 9.6% | +0.5% | 0.41 | 0.39 | 0.40 | 16.20 | 0.61 |
| Buddy-Buddy Poffin | 4 | 43.8% | 0.5% | 58.1% | 11.8% | +0.3% | 0.40 | 0.38 | 0.39 | 16.36 | 0.60 |
| Rescue Carrier | 3 | 43.6% | 0.5% | 58.5% | 10.4% | +0.1% | 0.41 | 0.39 | 0.41 | 16.36 | 0.65 |
| Victini | 1 | 43.2% | 0.5% | 58.0% | 9.9% | -0.2% | 0.39 | 0.37 | 0.39 | 15.91 | 0.65 |
| Neutralization Zone | 1 | 42.7% | 0.5% | 55.2% | 17.2% | -0.8% | 0.39 | 0.37 | 0.39 | 16.17 | 0.62 |

Kept −Manaphy at 46.6% (+3.2%, 4.60 combined standard errors).

## Step 2

List entering this step: weighted 46.6% ± 0.5%. Each row replaces one copy of that card with one Hilda.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Hilda | Evo | Energy | Mill cards | Wally |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wally | 3 | 47.8% | 0.5% | 61.8% | 15.0% | +1.2% | 0.66 | 0.62 | 0.66 | 17.42 | 0.44 |
| Miss Fortune Sisters | 2 | 47.7% | 0.5% | 61.9% | 13.8% | +1.0% | 0.66 | 0.61 | 0.66 | 17.81 | 0.58 |
| Rescue Carrier | 3 | 47.4% | 0.5% | 61.2% | 14.6% | +0.8% | 0.66 | 0.61 | 0.66 | 17.28 | 0.58 |
| Crushing Hammer | 4 | 47.1% | 0.5% | 61.3% | 13.1% | +0.4% | 0.65 | 0.61 | 0.65 | 17.38 | 0.60 |
| Double Turbo Energy | 4 | 47.0% | 0.5% | 61.1% | 13.9% | +0.4% | 0.67 | 0.62 | 0.67 | 17.11 | 0.59 |
| Team Rocket's Handiwork | 2 | 46.9% | 0.5% | 61.2% | 11.5% | +0.3% | 0.66 | 0.62 | 0.66 | 17.25 | 0.61 |
| Counter Catcher | 2 | 46.8% | 0.5% | 61.0% | 13.1% | +0.2% | 0.65 | 0.60 | 0.65 | 17.52 | 0.58 |
| Level Ball | 4 | 46.8% | 0.5% | 60.8% | 13.0% | +0.1% | 0.65 | 0.61 | 0.65 | 17.23 | 0.59 |
| Ignition Energy | 4 | 46.6% | 0.5% | 61.2% | 12.5% | -0.0% | 0.65 | 0.61 | 0.65 | 17.20 | 0.58 |
| Water Energy | 3 | 46.5% | 0.5% | 60.8% | 13.1% | -0.2% | 0.67 | 0.62 | 0.66 | 17.14 | 0.58 |
| Wugtrio | 4 | 46.4% | 0.5% | 60.8% | 13.4% | -0.2% | 0.65 | 0.55 | 0.64 | 17.06 | 0.57 |
| Colress's Tenacity | 4 | 46.2% | 0.5% | 60.7% | 13.2% | -0.4% | 0.65 | 0.61 | 0.65 | 17.20 | 0.59 |
| Mime Jr. | 1 | 46.1% | 0.5% | 60.6% | 11.8% | -0.5% | 0.66 | 0.60 | 0.65 | 17.50 | 0.58 |
| Lillie's Poké Doll | 1 | 46.1% | 0.5% | 60.6% | 11.6% | -0.5% | 0.64 | 0.60 | 0.63 | 17.52 | 0.57 |
| Buddy-Buddy Poffin | 4 | 46.0% | 0.5% | 60.2% | 13.2% | -0.6% | 0.64 | 0.60 | 0.64 | 17.10 | 0.57 |
| Cleffa | 1 | 46.0% | 0.5% | 60.4% | 14.4% | -0.6% | 0.62 | 0.58 | 0.62 | 17.11 | 0.56 |
| Reversal Energy | 4 | 46.0% | 0.5% | 60.3% | 10.6% | -0.7% | 0.66 | 0.61 | 0.66 | 17.16 | 0.59 |
| Igglybuff | 1 | 45.9% | 0.5% | 59.8% | 9.2% | -0.7% | 0.63 | 0.58 | 0.62 | 17.55 | 0.59 |
| Slumbering Forest | 1 | 45.7% | 0.5% | 60.9% | 7.0% | -0.9% | 0.64 | 0.59 | 0.64 | 17.77 | 0.59 |
| Wiglett | 4 | 45.6% | 0.5% | 60.0% | 11.9% | -1.0% | 0.66 | 0.61 | 0.66 | 16.75 | 0.52 |
| Pichu | 1 | 45.5% | 0.5% | 59.9% | 14.1% | -1.2% | 0.65 | 0.60 | 0.65 | 17.31 | 0.57 |
| Neutralization Zone | 1 | 44.5% | 0.5% | 56.7% | 17.9% | -2.2% | 0.65 | 0.60 | 0.64 | 16.97 | 0.58 |
| Victini | 1 | 44.1% | 0.5% | 59.2% | 10.2% | -2.6% | 0.64 | 0.59 | 0.64 | 16.71 | 0.60 |

Kept −Wally at 47.8% (+1.2%, 1.64 combined standard errors).

## Step 3

List entering this step: weighted 47.8% ± 0.5%. Each row replaces one copy of that card with one Hilda.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Hilda | Evo | Energy | Mill cards | Wally |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter Catcher | 2 | 49.0% | 0.5% | 62.8% | 17.8% | +1.2% | 0.92 | 0.85 | 0.92 | 17.87 | 0.41 |
| Mime Jr. | 1 | 48.7% | 0.5% | 62.7% | 14.3% | +0.9% | 0.91 | 0.83 | 0.91 | 18.01 | 0.41 |
| Crushing Hammer | 4 | 48.2% | 0.5% | 62.3% | 12.5% | +0.4% | 0.92 | 0.85 | 0.92 | 17.89 | 0.42 |
| Double Turbo Energy | 4 | 48.2% | 0.5% | 62.1% | 13.4% | +0.4% | 0.94 | 0.86 | 0.93 | 17.49 | 0.42 |
| Lillie's Poké Doll | 1 | 48.0% | 0.5% | 62.2% | 14.6% | +0.2% | 0.90 | 0.84 | 0.90 | 17.87 | 0.42 |
| Miss Fortune Sisters | 2 | 48.0% | 0.5% | 62.1% | 13.2% | +0.2% | 0.94 | 0.87 | 0.94 | 18.15 | 0.43 |
| Water Energy | 3 | 47.9% | 0.5% | 62.0% | 14.0% | +0.1% | 0.92 | 0.85 | 0.92 | 17.66 | 0.41 |
| Reversal Energy | 4 | 47.7% | 0.5% | 61.7% | 14.9% | -0.1% | 0.95 | 0.87 | 0.95 | 17.61 | 0.41 |
| Level Ball | 4 | 47.7% | 0.5% | 61.7% | 12.2% | -0.1% | 0.94 | 0.87 | 0.93 | 17.50 | 0.42 |
| Wugtrio | 4 | 47.5% | 0.5% | 61.6% | 12.8% | -0.3% | 0.92 | 0.77 | 0.92 | 17.54 | 0.41 |
| Wally | 2 | 47.5% | 0.5% | 61.5% | 14.6% | -0.3% | 0.93 | 0.86 | 0.92 | 17.75 | 0.26 |
| Pichu | 1 | 47.5% | 0.5% | 61.4% | 15.8% | -0.3% | 0.89 | 0.83 | 0.89 | 17.62 | 0.41 |
| Buddy-Buddy Poffin | 4 | 47.4% | 0.5% | 61.4% | 14.1% | -0.4% | 0.90 | 0.83 | 0.89 | 17.39 | 0.40 |
| Ignition Energy | 4 | 47.4% | 0.5% | 61.6% | 15.0% | -0.4% | 0.94 | 0.86 | 0.93 | 17.65 | 0.40 |
| Colress's Tenacity | 4 | 47.3% | 0.5% | 61.4% | 15.4% | -0.5% | 0.93 | 0.86 | 0.92 | 17.51 | 0.42 |
| Rescue Carrier | 3 | 47.3% | 0.5% | 61.5% | 12.0% | -0.5% | 0.90 | 0.83 | 0.90 | 17.63 | 0.42 |
| Team Rocket's Handiwork | 2 | 47.2% | 0.5% | 61.4% | 13.0% | -0.6% | 0.93 | 0.86 | 0.93 | 17.42 | 0.42 |
| Igglybuff | 1 | 46.8% | 0.5% | 61.1% | 11.9% | -1.0% | 0.90 | 0.83 | 0.90 | 18.02 | 0.42 |
| Wiglett | 4 | 46.7% | 0.5% | 61.2% | 12.8% | -1.1% | 0.93 | 0.85 | 0.93 | 17.48 | 0.37 |
| Cleffa | 1 | 46.6% | 0.5% | 61.2% | 14.3% | -1.2% | 0.87 | 0.81 | 0.87 | 17.46 | 0.40 |
| Slumbering Forest | 1 | 46.4% | 0.5% | 61.3% | 8.8% | -1.4% | 0.91 | 0.84 | 0.90 | 17.87 | 0.41 |
| Victini | 1 | 46.1% | 0.5% | 60.6% | 11.5% | -1.7% | 0.92 | 0.85 | 0.92 | 17.04 | 0.42 |
| Neutralization Zone | 1 | 45.5% | 0.5% | 57.6% | 18.5% | -2.3% | 0.90 | 0.83 | 0.90 | 17.10 | 0.42 |

Kept −Counter Catcher at 49.0% (+1.2%, 1.74 combined standard errors).

## Step 4

List entering this step: weighted 49.0% ± 0.5%. Each row replaces one copy of that card with one Hilda.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Hilda | Evo | Energy | Mill cards | Wally |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ignition Energy | 4 | 50.1% | 0.5% | 63.7% | 13.4% | +1.0% | 1.17 | 1.06 | 1.17 | 18.25 | 0.37 |
| Water Energy | 3 | 49.9% | 0.5% | 63.3% | 14.5% | +0.9% | 1.19 | 1.07 | 1.18 | 18.15 | 0.39 |
| Double Turbo Energy | 4 | 49.7% | 0.5% | 63.4% | 15.4% | +0.7% | 1.18 | 1.06 | 1.17 | 18.01 | 0.39 |
| Mime Jr. | 1 | 49.6% | 0.5% | 63.5% | 11.9% | +0.6% | 1.15 | 1.03 | 1.15 | 18.59 | 0.39 |
| Miss Fortune Sisters | 2 | 49.2% | 0.5% | 62.8% | 14.0% | +0.2% | 1.17 | 1.06 | 1.17 | 18.57 | 0.40 |
| Team Rocket's Handiwork | 2 | 49.1% | 0.5% | 63.0% | 14.8% | +0.1% | 1.19 | 1.07 | 1.18 | 18.01 | 0.40 |
| Wally | 2 | 49.1% | 0.5% | 62.9% | 14.9% | +0.1% | 1.20 | 1.10 | 1.19 | 18.20 | 0.24 |
| Counter Catcher | 1 | 49.0% | 0.5% | 62.6% | 15.8% | -0.0% | 1.16 | 1.05 | 1.16 | 18.19 | 0.40 |
| Reversal Energy | 4 | 49.0% | 0.5% | 62.3% | 14.9% | -0.1% | 1.19 | 1.07 | 1.19 | 17.97 | 0.39 |
| Lillie's Poké Doll | 1 | 49.0% | 0.5% | 62.9% | 15.4% | -0.1% | 1.13 | 1.03 | 1.13 | 18.39 | 0.39 |
| Wugtrio | 4 | 48.5% | 0.5% | 62.6% | 14.4% | -0.6% | 1.18 | 0.95 | 1.18 | 18.05 | 0.39 |
| Rescue Carrier | 3 | 48.4% | 0.5% | 62.6% | 12.1% | -0.7% | 1.17 | 1.05 | 1.17 | 17.96 | 0.40 |
| Level Ball | 4 | 48.4% | 0.5% | 62.1% | 16.0% | -0.7% | 1.16 | 1.06 | 1.15 | 17.95 | 0.40 |
| Crushing Hammer | 4 | 48.2% | 0.5% | 62.3% | 13.8% | -0.8% | 1.17 | 1.06 | 1.17 | 18.22 | 0.40 |
| Buddy-Buddy Poffin | 4 | 48.2% | 0.5% | 62.0% | 17.0% | -0.8% | 1.14 | 1.04 | 1.14 | 18.00 | 0.40 |
| Cleffa | 1 | 48.0% | 0.5% | 62.4% | 15.4% | -1.0% | 1.11 | 1.00 | 1.10 | 18.10 | 0.38 |
| Colress's Tenacity | 4 | 48.0% | 0.5% | 61.4% | 15.4% | -1.0% | 1.18 | 1.08 | 1.18 | 17.92 | 0.39 |
| Slumbering Forest | 1 | 47.8% | 0.5% | 62.3% | 8.4% | -1.2% | 1.14 | 1.04 | 1.14 | 18.39 | 0.39 |
| Igglybuff | 1 | 47.7% | 0.5% | 61.7% | 13.6% | -1.4% | 1.13 | 1.02 | 1.12 | 18.47 | 0.39 |
| Pichu | 1 | 47.4% | 0.5% | 61.5% | 12.4% | -1.6% | 1.14 | 1.04 | 1.14 | 18.11 | 0.38 |
| Wiglett | 4 | 47.2% | 0.5% | 61.2% | 11.5% | -1.8% | 1.17 | 1.06 | 1.17 | 17.51 | 0.36 |
| Neutralization Zone | 1 | 46.9% | 0.5% | 58.8% | 21.9% | -2.2% | 1.16 | 1.05 | 1.16 | 17.70 | 0.38 |
| Victini | 1 | 46.2% | 0.5% | 60.8% | 10.6% | -2.9% | 1.17 | 1.05 | 1.17 | 17.61 | 0.40 |

Kept −Ignition Energy at 50.1% (+1.0%, 1.45 combined standard errors).

## Foes at the kept list

| Foe | A | B | Mean | Delta vs locked |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 79.0% | 80.5% | 79.8% | +5.8% |
| Hedrick Worlds Dragapult | 70.0% | 69.8% | 69.9% | +10.4% |
| Unlimited Dragapult | 87.8% | 85.2% | 86.5% | +2.0% |
| Cornerstone Ogerpon (D60) | 12.2% | 14.5% | 13.4% | +2.7% |
| Wo-Chien / Floragato (S60) | 80.2% | 76.2% | 78.2% | +7.3% |
| Gholdengo (G) | 43.8% | 48.2% | 46.0% | +10.9% |
| Clefairy / Mewtwo (C60) | 48.2% | 50.0% | 49.1% | +9.5% |
| Set M (Mew ex) | 33.8% | 30.8% | 32.2% | +5.5% |
| Mega Starmie ex (Kudo) | 34.0% | 34.8% | 34.4% | -0.3% |
| Lucario Hariyama | 80.0% | 81.8% | 80.9% | -0.2% |
| Iron Thorns ex | 93.5% | 93.2% | 93.4% | +2.4% |
| Carpet Set H | 69.0% | 66.5% | 67.8% | +21.4% |
| Ambipom Hand Fling | 96.0% | 97.0% | 96.5% | +1.4% |
