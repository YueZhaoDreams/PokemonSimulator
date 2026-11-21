# Kecleon stall line, Dual Ball at 0

The engine was put back on the old Kecleon-first line after this measurement. The locked list is 4 Dual Ball. This note is the stall sample only.

The locked `SET_KECLEON_NAMES` list is not edited. Dual Ball is 0. Latias ex stays at 2. Against Mill, Doll, and the roast mills the old line still leads Kecleon and swings a short Colorful Whip. Against every other current 60, a higher-HP Basic stays Active. Energy goes to the benched Kecleon. Retreat, including a free Skyliner retreat, happens when Colorful Whip, Cruel Arrow, or Hyperspace Fury Knocks Out. A short Whip passes.

The old cells are `start_cells` in `kecleon-dual-ball.json`. Seed 20261120. 400 games per seat. Both seats. Each cell starts a new `random.Random` at that seed. The two lines diverge after the first choice that consumes a different number of draws. Mill matchups share the old choices, so their win counts should match.

Elapsed 151s.

## Rates

Full field, 0-copy weights: old 53.11%, new 44.96%, -8.15 pp. Old SE 0.45%, new SE 0.45%, gap SE 0.63%.

Same weights, restricted to the old active set and divided by that set's weight: old 50.82%, new 42.68%, -8.15 pp.

Unweighted, all 18 foes: old 66.03%, new 57.33%, -8.70 pp.

A positive step is the stall line winning more often. The weight vector is the old loss rates, so a foe the old line already beat has a small weight.

| Foe | Strategy | Line | Old | New | Change | Whip / game | Stall pass | Stall KO | Stall wall |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Chris Brewer Lucario Hariyama | aura | stall | 60.25% | 26.12% | -34.13 pp | 4.23 → 0.95 | 0.82 | 0.52 | 0.60 |
| Iron Thorns | thorns | stall | 76.25% | 44.12% | -32.12 pp | 4.50 → 1.07 | 2.01 | 0.39 | 0.58 |
| Mega Starmie | starmie | stall | 56.50% | 30.12% | -26.37 pp | 3.54 → 1.10 | 0.58 | 0.61 | 0.39 |
| Set D Standard 60 (Charm Ogerpon) | demolish | stall | 88.38% | 69.75% | -18.63 pp | 1.95 → 0.69 | 0.73 | 0.57 | 0.44 |
| Unlimited Dragapult (Pidgeot / Rotom V) | phantom | stall | 67.50% | 54.00% | -13.50 pp | 5.10 → 1.65 | 0.68 | 1.16 | 0.74 |
| Worlds 2026 Hedrick Dragapult | phantom | stall | 53.25% | 43.50% | -9.75 pp | 4.00 → 1.80 | 0.36 | 1.05 | 0.62 |
| Set T Standard 60 (Dragapult ex) | phantom | stall | 44.00% | 34.50% | -9.50 pp | 3.64 → 1.36 | 0.55 | 0.94 | 0.63 |
| Set S Standard 60 (Floragato hunter) | slash | stall | 91.75% | 83.12% | -8.62 pp | 4.81 → 1.99 | 1.20 | 1.37 | 0.44 |
| Set C Standard 60 (Clefairy / Mewtwo) | party | stall | 54.50% | 51.00% | -3.50 pp | 3.78 → 2.79 | 0.47 | 1.49 | 0.28 |
| Carpet Set G (Clefairy / Ledian 60) | g | stall | 80.00% | 77.75% | -2.25 pp | 4.29 → 3.22 | 0.35 | 1.24 | 0.29 |
| Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | nuzzle | stall | 99.88% | 99.38% | -0.50 pp | 3.17 → 2.35 | 0.32 | 0.79 | 0.19 |
| Unlimited 60 (Ambipom Hand Fling) | celebration | stall | 99.25% | 99.12% | -0.13 pp | 4.71 → 3.10 | 0.57 | 0.92 | 0.20 |
| Mill | mill | old | 63.00% | 63.00% | 0.00 pp | 5.94 → 5.94 | 0.00 | 0.00 | 0.00 |
| Doll | doll | old | 48.50% | 48.50% | 0.00 pp | 9.95 → 9.95 | 0.00 | 0.00 | 0.00 |
| Celebi Mill | roast | old | 73.00% | 73.00% | 0.00 pp | 5.50 → 5.50 | 0.00 | 0.00 | 0.00 |
| 二森林 | roast | old | 68.12% | 68.12% | 0.00 pp | 5.57 → 5.57 | 0.00 | 0.00 | 0.00 |
| Kecleon | kecleon | stall | 50.00% | 50.00% | 0.00 pp | 8.58 → 5.51 | 0.67 | 1.40 | 0.23 |
| Set M Standard 60 (Mew ex / Spiky Energy) | mew_baby | stall | 14.50% | 16.88% | +2.38 pp | 2.15 → 1.28 | 0.28 | 0.91 | 0.31 |

Stall pass, stall KO, and stall wall are per subject seat per game. Colorful Whip has no seat, so a Kecleon mirror counts both players. Mill, Doll, Celebi Mill, and 二森林 stay on the old line; a stall counter above zero there is a bug.
