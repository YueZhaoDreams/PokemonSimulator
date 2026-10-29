# Doll losses

Locked 60: one Switch, one Black Market. Strategy `doll`. Product engine. Both seats. Doll goes first in either seat. The win rates are the Switch confirm in `set-doll-black-market.md`: same seed, same list, same games.

- **Seed**: `20261028`
- **Games per seat**: 200
- **Weights**: frozen Sisters loss weights, the same weights as the Doll lock.
- **Elapsed**: 111.3s

A reason is `GameResult.reason` from Doll's seat. `prizes` means the opponent took all 6 Prize cards. `empty` means Doll's Active was Knocked Out with an empty Bench, before the opponent had 6 Prizes. `decked` means Doll's deck ran out. `no_basic` means Doll still had no Basic after the mulligan cap. Knock Out counts use names that are not in that foe's deck. The counter itself is not side-specific.

## By foe

| Foe | Win | Prizes | Empty | Decked | No basic | Turn | Foe prizes when the board is empty |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 49.0% | 17.2% | 29.0% | 0.0% | 0.0% | 4.8% | 2.40 |
| Hedrick Worlds Dragapult | 26.8% | 19.0% | 43.8% | 0.0% | 0.0% | 10.5% | 2.60 |
| Unlimited Dragapult | 78.0% | 8.8% | 11.5% | 0.0% | 0.0% | 1.8% | 2.85 |
| Cornerstone Ogerpon (D60) | 0.8% | 0.0% | 98.8% | 0.0% | 0.0% | 0.5% | 2.01 |
| Wo-Chien / Floragato (S60) | 55.0% | 11.8% | 5.8% | 0.0% | 0.0% | 27.5% | 3.00 |
| Gholdengo (G) | 20.8% | 38.8% | 34.2% | 0.0% | 0.0% | 6.2% | 3.12 |
| Clefairy / Mewtwo (C60) | 48.0% | 17.5% | 29.5% | 0.0% | 0.0% | 5.0% | 2.41 |
| Set M (Mew ex) | 17.0% | 45.5% | 37.0% | 0.0% | 0.0% | 0.5% | 2.32 |
| Mega Starmie ex (Kudo) | 11.5% | 21.2% | 57.8% | 0.0% | 0.0% | 9.5% | 2.93 |
| Lucario Hariyama | 70.5% | 8.2% | 20.5% | 0.0% | 0.0% | 0.8% | 2.10 |
| Iron Thorns ex | 85.8% | 2.0% | 7.8% | 0.0% | 0.0% | 4.5% | 2.13 |
| Carpet Set H | 6.8% | 4.5% | 14.5% | 0.0% | 0.0% | 74.2% | 1.88 |
| Ambipom Hand Fling | 61.0% | 2.2% | 3.0% | 0.0% | 0.0% | 33.8% | 2.42 |

## Share of the weighted losses

Sisters-weighted loss rate: 70.6% of games.

| Reason | Weighted share of games | Share of weighted losses | Raw games |
| :--- | ---: | ---: | ---: |
| Opponent took 6 Prizes | 19.1% | 27.1% | 787 / 5200 |
| Doll's board emptied | 40.1% | 56.7% | 1572 / 5200 |
| Doll decked out | 0.0% | 0.0% | 0 / 5200 |
| Doll had no Basic | 0.0% | 0.0% | 0 / 5200 |
| Turn limit, fewer Prizes | 10.2% | 14.5% | 551 / 5200 |
| Turn limit, less HP | 1.2% | 1.7% | 167 / 5200 |
| Other | 0.0% | 0.0% | 0 / 5200 |

## Knock Outs when the opponent takes 6 Prizes

Mean Knock Outs of Doll-only names in those losses. A foe that shares the name is omitted.

| Foe | Games | Cleffa | Smoochum | Mime Jr. | Manaphy | Sableye | Nincada | Shedinja | Dolls | Turns | Market | Prize cut |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 69 | 1.78 | 0.86 | 1.25 | 0.80 | 1.49 | 0.20 | 0.00 | 3.09 | 25.5 | 3% | 0% |
| Hedrick Worlds Dragapult | 76 | 1.74 | 0.75 | 1.41 | 0.75 | 1.47 | 0.24 | 0.00 | 2.74 | 24.9 | 8% | 4% |
| Unlimited Dragapult | 35 | 1.97 | 0.69 | 1.29 | — | 1.60 | 0.26 | 0.00 | 3.11 | 22.1 | 6% | 6% |
| Wo-Chien / Floragato (S60) | 47 | 2.53 | 1.09 | 1.49 | 0.21 | 1.11 | 0.11 | 0.00 | 1.94 | 31.0 | 9% | 6% |
| Gholdengo (G) | 155 | 1.89 | 1.44 | 1.70 | 0.19 | 1.07 | 0.10 | 0.01 | 2.24 | 28.0 | 10% | 8% |
| Clefairy / Mewtwo (C60) | 70 | 2.26 | 1.13 | 1.81 | 0.11 | 1.09 | 0.01 | 0.00 | 0.76 | 24.4 | 16% | 6% |
| Set M (Mew ex) | 182 | 1.71 | 1.42 | — | — | 1.08 | 0.03 | 0.01 | 1.48 | 22.2 | 12% | 3% |
| Mega Starmie ex (Kudo) | 85 | 1.75 | 0.81 | 1.39 | 0.74 | 1.52 | 0.16 | 0.00 | 2.84 | 25.1 | 5% | 5% |
| Lucario Hariyama | 33 | 2.06 | 1.27 | 1.58 | 0.18 | 1.00 | 0.06 | 0.00 | 1.88 | 22.8 | 9% | 3% |
| Iron Thorns ex | 8 | 1.62 | 1.00 | 1.62 | 0.50 | 1.50 | 0.00 | 0.00 | 1.88 | 23.5 | 0% | 0% |
| Carpet Set H | 18 | 2.28 | 0.67 | 1.17 | 0.72 | 1.39 | 0.06 | 0.00 | 1.50 | 35.0 | 11% | 0% |
| Ambipom Hand Fling | 9 | 2.89 | 1.00 | 1.00 | 0.11 | 1.00 | 0.00 | 0.00 | 1.89 | 28.9 | 11% | 0% |

## Empty board

Foe Prize cards already taken when Doll's Bench was empty. The count is games, both seats.

| Foe | Games | Prize cards | Doll Knock Outs | Prize-body Knock Outs | Turns | Market played |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 116 | 0:9 1:30 2:27 3:21 4:14 5:15 | 1.57 | 2.69 | 14.2 | 2% |
| Hedrick Worlds Dragapult | 175 | 0:9 1:49 2:30 3:29 4:31 5:27 | 1.67 | 2.91 | 16.5 | 4% |
| Unlimited Dragapult | 46 | 0:3 1:10 2:5 3:10 4:9 5:9 | 1.78 | 2.57 | 12.1 | 0% |
| Cornerstone Ogerpon (D60) | 395 | 0:30 1:105 2:135 3:88 4:32 5:5 | 2.90 | 2.30 | 14.6 | 4% |
| Wo-Chien / Floragato (S60) | 23 | 1:4 2:6 3:5 4:2 5:6 | 2.52 | 3.78 | 19.3 | 4% |
| Gholdengo (G) | 137 | 0:5 1:21 2:21 3:27 4:32 5:31 | 2.29 | 3.57 | 19.2 | 5% |
| Clefairy / Mewtwo (C60) | 118 | 0:5 1:34 2:25 3:27 4:16 5:11 | 1.61 | 2.70 | 13.3 | 3% |
| Set M (Mew ex) | 148 | 0:4 1:48 2:34 3:35 4:13 5:14 | 1.26 | 1.74 | 8.3 | 1% |
| Mega Starmie ex (Kudo) | 231 | 0:10 1:45 2:38 3:43 4:48 5:47 | 1.95 | 3.25 | 13.4 | 3% |
| Lucario Hariyama | 82 | 0:4 1:29 2:20 3:16 4:10 5:3 | 1.57 | 2.32 | 10.2 | 1% |
| Iron Thorns ex | 31 | 0:4 1:8 2:6 3:8 4:3 5:2 | 1.87 | 2.52 | 15.7 | 0% |
| Carpet Set H | 58 | 0:6 1:24 2:10 3:11 4:3 5:4 | 1.14 | 2.17 | 13.5 | 0% |
| Ambipom Hand Fling | 12 | 1:5 2:1 3:3 4:2 5:1 | 1.33 | 2.58 | 16.2 | 8% |

## Turn limit

The game stops after 40 turns. Doll loses this way when the opponent has more Prize cards, or the same number and more remaining HP. The Prize column is how many the opponent had already taken.

| Foe | Fewer Prizes | Their Prizes | Less HP |
| :--- | ---: | :--- | ---: |
| Hedrick Worlds Dragapult | 33 | 1:7 2:8 3:9 4:4 5:5 | 9 |
| Wo-Chien / Floragato (S60) | 99 | 1:26 2:20 3:26 4:9 5:18 | 11 |
| Gholdengo (G) | 23 | 2:4 3:5 4:6 5:8 | 2 |
| Clefairy / Mewtwo (C60) | 19 | 1:3 2:3 3:7 4:3 5:3 | 1 |
| Mega Starmie ex (Kudo) | 26 | 1:3 2:8 3:3 4:8 5:4 | 12 |
| Carpet Set H | 294 | 1:13 2:50 3:97 4:83 5:51 | 3 |
| Ambipom Hand Fling | 19 | 1:11 2:1 3:3 4:2 5:2 | 116 |

Shared names are left out of the Knock Out columns: Unlimited Dragapult shares Manaphy; Set M (Mew ex) shares Mime Jr., Manaphy.

## How the wins happen

| Foe | Foe decked | Foe board empty | Foe had no Basic | Doll took 6 |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 49.0% | 0.0% | 0.0% | 0.0% |
| Hedrick Worlds Dragapult | 26.8% | 0.0% | 0.0% | 0.0% |
| Unlimited Dragapult | 78.0% | 0.0% | 0.0% | 0.0% |
| Cornerstone Ogerpon (D60) | 0.0% | 0.0% | 0.8% | 0.0% |
| Wo-Chien / Floragato (S60) | 55.0% | 0.0% | 0.0% | 0.0% |
| Gholdengo (G) | 20.8% | 0.0% | 0.0% | 0.0% |
| Clefairy / Mewtwo (C60) | 48.0% | 0.0% | 0.0% | 0.0% |
| Set M (Mew ex) | 16.8% | 0.0% | 0.0% | 0.0% |
| Mega Starmie ex (Kudo) | 11.5% | 0.0% | 0.0% | 0.0% |
| Lucario Hariyama | 70.2% | 0.2% | 0.0% | 0.0% |
| Iron Thorns ex | 85.0% | 0.0% | 0.8% | 0.0% |
| Carpet Set H | 6.5% | 0.0% | 0.0% | 0.0% |
| Ambipom Hand Fling | 61.0% | 0.0% | 0.0% | 0.0% |

