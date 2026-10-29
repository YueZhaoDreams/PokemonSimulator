# Doll losses

Locked 60: two Cleffa, one Switch, one Black Market, one Arven, one Team Rocket's Petrel. Lillie's Poké Doll and Robo Substitute stay at four. Strategy `doll`. Product engine. Both seats. Doll goes first in either seat. Seed 20261029 and 200 games per seat are the Petrel confirm in `set-doll-arven-petrel.md`. `set-doll-losses.md` is the earlier Black Market 60.

- **Seed**: `20261029`
- **Games per seat**: 200
- **Weights**: frozen Sisters loss weights, the same weights as the Doll lock.
- **Elapsed**: 99.6s

A reason is `GameResult.reason` from Doll's seat. `prizes` means the opponent took all 6 Prize cards. `empty` means Doll's Active was Knocked Out with an empty Bench, before the opponent had 6 Prizes. `decked` means Doll's deck ran out. `no_basic` means Doll still had no Basic after the mulligan cap. Knock Out counts use names that are not in that foe's deck. The counter itself is not side-specific.

## By foe

| Foe | Win | Prizes | Empty | Decked | No basic | Turn | Foe prizes when the board is empty |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 53.5% | 10.0% | 32.5% | 0.0% | 0.0% | 4.0% | 2.62 |
| Hedrick Worlds Dragapult | 32.2% | 13.2% | 43.0% | 0.0% | 0.0% | 11.5% | 2.58 |
| Unlimited Dragapult | 79.2% | 5.5% | 13.8% | 0.0% | 0.0% | 1.5% | 2.62 |
| Cornerstone Ogerpon (D60) | 1.0% | 0.0% | 98.5% | 0.0% | 0.0% | 0.5% | 1.81 |
| Wo-Chien / Floragato (S60) | 61.3% | 6.0% | 5.0% | 0.0% | 0.0% | 27.8% | 2.55 |
| Gholdengo (G) | 23.5% | 28.0% | 37.8% | 0.0% | 0.0% | 10.8% | 2.70 |
| Clefairy / Mewtwo (C60) | 56.8% | 9.5% | 28.7% | 0.0% | 0.0% | 5.0% | 1.96 |
| Set M (Mew ex) | 28.2% | 34.8% | 36.5% | 0.0% | 0.0% | 0.5% | 2.39 |
| Mega Starmie ex (Kudo) | 11.5% | 18.0% | 62.5% | 0.0% | 0.0% | 8.0% | 2.63 |
| Lucario Hariyama | 75.0% | 3.2% | 20.5% | 0.0% | 0.0% | 1.2% | 2.22 |
| Iron Thorns ex | 88.5% | 1.5% | 4.2% | 0.0% | 0.0% | 5.8% | 1.88 |
| Carpet Set H | 6.2% | 2.2% | 10.2% | 0.0% | 0.0% | 81.2% | 1.85 |
| Ambipom Hand Fling | 69.5% | 2.0% | 4.5% | 0.0% | 0.0% | 24.0% | 2.44 |

## Share of the weighted losses

Sisters-weighted loss rate: 66.2% of games.

| Reason | Weighted share of games | Share of weighted losses | Raw games |
| :--- | ---: | ---: | ---: |
| Opponent took 6 Prizes | 13.5% | 20.3% | 536 / 5200 |
| Doll's board emptied | 40.4% | 61.0% | 1591 / 5200 |
| Doll decked out | 0.0% | 0.0% | 0 / 5200 |
| Doll had no Basic | 0.0% | 0.0% | 0 / 5200 |
| Turn limit, fewer Prizes | 11.1% | 16.8% | 585 / 5200 |
| Turn limit, less HP | 1.2% | 1.8% | 142 / 5200 |
| Other | 0.0% | 0.0% | 0 / 5200 |

## Knock Outs when the opponent takes 6 Prizes

Mean Knock Outs of Doll-only names in those losses. A foe that shares the name is omitted.

| Foe | Games | Cleffa | Smoochum | Mime Jr. | Manaphy | Sableye | Nincada | Shedinja | Dolls | Turns | Market | Prize cut |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 40 | 1.25 | 0.95 | 1.55 | 0.80 | 1.65 | 0.23 | 0.00 | 2.92 | 23.8 | 2% | 2% |
| Hedrick Worlds Dragapult | 53 | 1.13 | 0.98 | 1.53 | 0.98 | 1.34 | 0.45 | 0.00 | 2.92 | 23.5 | 15% | 4% |
| Unlimited Dragapult | 22 | 1.27 | 0.91 | 1.77 | — | 2.00 | 0.18 | 0.00 | 3.82 | 22.4 | 9% | 9% |
| Wo-Chien / Floragato (S60) | 24 | 1.71 | 1.25 | 1.54 | 0.33 | 1.42 | 0.04 | 0.04 | 2.54 | 30.4 | 4% | 0% |
| Gholdengo (G) | 112 | 1.20 | 1.53 | 2.09 | 0.28 | 1.23 | 0.11 | 0.01 | 2.43 | 28.2 | 12% | 10% |
| Clefairy / Mewtwo (C60) | 38 | 1.16 | 1.47 | 2.03 | 0.13 | 1.47 | 0.05 | 0.00 | 1.63 | 26.5 | 11% | 0% |
| Set M (Mew ex) | 139 | 1.01 | 1.63 | — | — | 1.14 | 0.08 | 0.00 | 2.19 | 23.8 | 14% | 1% |
| Mega Starmie ex (Kudo) | 72 | 1.01 | 1.03 | 1.71 | 0.90 | 1.56 | 0.18 | 0.00 | 3.26 | 24.3 | 0% | 0% |
| Lucario Hariyama | 13 | 1.46 | 1.38 | 1.62 | 0.31 | 1.23 | 0.00 | 0.00 | 2.00 | 20.2 | 8% | 0% |
| Iron Thorns ex | 6 | 1.33 | 1.67 | 2.17 | 0.17 | 1.00 | 0.17 | 0.00 | 3.00 | 30.0 | 0% | 0% |
| Carpet Set H | 9 | 1.67 | 0.56 | 1.89 | 0.78 | 1.44 | 0.00 | 0.00 | 3.11 | 34.7 | 0% | 0% |
| Ambipom Hand Fling | 8 | 1.25 | 1.25 | 1.38 | 0.00 | 2.62 | 0.00 | 0.00 | 0.75 | 30.2 | 25% | 12% |

## Empty board

Foe Prize cards already taken when Doll's Bench was empty. The count is games, both seats.

| Foe | Games | Prize cards | Doll Knock Outs | Prize-body Knock Outs | Turns | Market played |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 130 | 0:6 1:31 2:25 3:31 4:19 5:18 | 2.23 | 3.03 | 16.6 | 2% |
| Hedrick Worlds Dragapult | 172 | 0:8 1:46 2:33 3:34 4:25 5:26 | 1.98 | 2.95 | 17.1 | 5% |
| Unlimited Dragapult | 55 | 0:4 1:10 2:12 3:13 4:9 5:7 | 2.36 | 2.71 | 13.6 | 2% |
| Cornerstone Ogerpon (D60) | 394 | 0:32 1:138 2:126 3:76 4:14 5:8 | 3.69 | 2.24 | 16.1 | 6% |
| Wo-Chien / Floragato (S60) | 20 | 0:1 1:4 2:4 3:6 4:4 5:1 | 3.00 | 3.10 | 19.4 | 15% |
| Gholdengo (G) | 151 | 0:12 1:25 2:27 3:38 4:30 5:19 | 2.79 | 3.17 | 18.9 | 2% |
| Clefairy / Mewtwo (C60) | 115 | 0:11 1:41 2:27 3:19 4:12 5:5 | 2.08 | 2.30 | 13.3 | 3% |
| Set M (Mew ex) | 146 | 0:4 1:48 2:32 3:27 4:19 5:16 | 1.75 | 1.58 | 9.3 | 1% |
| Mega Starmie ex (Kudo) | 250 | 0:10 1:62 2:51 3:50 4:41 5:36 | 2.51 | 3.04 | 14.0 | 1% |
| Lucario Hariyama | 82 | 0:6 1:23 2:21 3:18 4:7 5:7 | 1.91 | 2.49 | 11.0 | 0% |
| Iron Thorns ex | 17 | 0:1 1:7 2:3 3:5 4:1 | 1.76 | 2.24 | 15.6 | 6% |
| Carpet Set H | 41 | 0:5 1:18 2:5 3:7 4:3 5:3 | 1.49 | 2.22 | 15.6 | 0% |
| Ambipom Hand Fling | 18 | 0:1 1:6 2:3 3:2 4:4 5:2 | 2.56 | 2.89 | 20.7 | 17% |

## Turn limit

The game stops after 40 turns. Doll loses this way when the opponent has more Prize cards, or the same number and more remaining HP. The Prize column is how many the opponent had already taken.

| Foe | Fewer Prizes | Their Prizes | Less HP |
| :--- | ---: | :--- | ---: |
| Hedrick Worlds Dragapult | 36 | 1:7 2:6 3:14 4:6 5:3 | 10 |
| Wo-Chien / Floragato (S60) | 85 | 1:28 2:17 3:15 4:14 5:11 | 26 |
| Gholdengo (G) | 42 | 1:2 2:11 3:11 4:7 5:11 | 1 |
| Clefairy / Mewtwo (C60) | 19 | 1:3 2:5 3:6 4:4 5:1 | 1 |
| Mega Starmie ex (Kudo) | 26 | 1:3 2:3 3:5 4:8 5:7 | 6 |
| Iron Thorns ex | 13 | 1:4 2:6 3:2 5:1 | 10 |
| Carpet Set H | 323 | 1:43 2:69 3:108 4:73 5:30 | 2 |
| Ambipom Hand Fling | 15 | 1:6 2:3 3:1 4:4 5:1 | 81 |

Shared names are left out of the Knock Out columns: Unlimited Dragapult shares Manaphy; Set M (Mew ex) shares Mime Jr., Manaphy.

## How the wins happen

| Foe | Foe decked | Foe board empty | Foe had no Basic | Doll took 6 |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 53.5% | 0.0% | 0.0% | 0.0% |
| Hedrick Worlds Dragapult | 32.2% | 0.0% | 0.0% | 0.0% |
| Unlimited Dragapult | 79.2% | 0.0% | 0.0% | 0.0% |
| Cornerstone Ogerpon (D60) | 0.5% | 0.0% | 0.5% | 0.0% |
| Wo-Chien / Floragato (S60) | 61.3% | 0.0% | 0.0% | 0.0% |
| Gholdengo (G) | 23.5% | 0.0% | 0.0% | 0.0% |
| Clefairy / Mewtwo (C60) | 56.8% | 0.0% | 0.0% | 0.0% |
| Set M (Mew ex) | 28.2% | 0.0% | 0.0% | 0.0% |
| Mega Starmie ex (Kudo) | 11.2% | 0.0% | 0.0% | 0.0% |
| Lucario Hariyama | 75.0% | 0.0% | 0.0% | 0.0% |
| Iron Thorns ex | 86.5% | 0.0% | 2.0% | 0.0% |
| Carpet Set H | 6.2% | 0.0% | 0.0% | 0.0% |
| Ambipom Hand Fling | 69.5% | 0.0% | 0.0% | 0.0% |

