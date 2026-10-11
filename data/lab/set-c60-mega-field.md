# Household 60s vs the Mega C60

- **Seed**: `20261011`
- **Games per cell**: 1000
- **Seat**: the named deck is player A. C60 is player B. Who goes first is random.
- **Score**: C60's loss-weighted win rate. Weights are frozen from the old C60.
- **Weights**: m 41.1%, starmie 17.9%, mill 10.2%, lucario 7.8%, thorns 9.6%, g 11.1%, h 1.7%, g30 0.6%
- **Weighted**: old 49.1%, new 51.3%.
- **Old C60**: one Rebel Clash Prankish Clefable, zero Mega Clefable ex (`c60_names_before_mega`).
- **New C60**: that Prankish Clefable is one Mega Clefable ex. Seeker stays.
- **Elapsed**: 299.8s

The table's win rates are player A's. C60's win rate in that cell is the complement when there are no ties. Shooting Moons is recorded for either player. Carpet Set G also attacks with Mega Clefable ex, so that cell's shooting rate includes both.

| Deck | Strategy | Weight | A vs old | A vs new | C60 old | C60 new | Moons | Shooting |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M (Mew ex) | mew_baby | 41.1% | 87.3% | 85.7% | 12.7% | 14.3% | 0.009 | 0.109 |
| Mega Starmie ex (Kudo) | starmie | 17.9% | 38.1% | 37.3% | 61.9% | 62.7% | 0.005 | 0.118 |
| Wugtrio mill | mill | 10.2% | 21.7% | 19.3% | 78.3% | 80.7% | 0.000 | 0.084 |
| Lucario Hariyama | aura | 7.8% | 16.5% | 17.1% | 83.5% | 82.9% | 0.032 | 0.367 |
| Iron Thorns ex | thorns | 9.6% | 20.4% | 15.8% | 79.6% | 84.2% | 0.003 | 0.041 |
| Carpet Set G | g | 11.1% | 23.6% | 17.1% | 76.4% | 82.9% | 0.004 | 0.308 |
| Carpet Set H | nuzzle | 1.7% | 3.6% | 2.9% | 96.4% | 97.1% | 0.000 | 0.065 |
| Ambipom Hand Fling | celebration | 0.6% | 1.2% | 0.7% | 98.8% | 99.3% | 0.003 | 0.137 |

## Decision

C60's loss-weighted win rate is 49.1% on the old list and 51.3% on the Mega list. Unweighted mean 73.5% → 75.5%.
