# Doll, one Black Market

Dark Market is Black Market ◇, Team Up 134. One copy. The Prism Star rule puts it in the Lost Zone instead of the discard pile. When a Darkness Pokémon with any Darkness Energy attached to it is Knocked Out by damage from an opponent's attack, that player takes 1 fewer Prize card. An Item or a Supporter cannot affect this Stadium. Another Stadium still replaces it.

The pilot plays it for Sableye once that Sableye has Darkness Energy, or can attach one this turn. Junk Hunt still costs Darkness, and the prize line does too, so the Energy stays. Life Dew stays off that Sableye. Battle Cage stays up against spread. Slumbering Forest stays up while a face is Asleep.

- **Seed**: `20261028`
- **Screen games per seat**: 40
- **Confirm games per seat**: 200
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 1316.5s

## Screen

| Cut | Copies | Weighted | Mean | Worst | Stadium plays | Prize cuts |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Switch | 2 | 30.8% | 41.4% | 1.2% | 0.10 | 0.05 |
| Life Dew | 1 | 30.2% | 41.0% | 2.5% | 0.10 | 0.04 |
| VS Seeker | 4 | 29.7% | 41.5% | 2.5% | 0.09 | 0.06 |
| Dark Patch | 1 | 29.6% | 39.7% | 2.5% | 0.08 | 0.04 |
| Cleffa | 4 | 29.5% | 41.0% | 1.2% | 0.08 | 0.03 |
| Rescue Carrier | 3 | 29.2% | 40.5% | 3.8% | 0.10 | 0.06 |
| Lillie's Poké Doll | 4 | 29.2% | 40.4% | 1.2% | 0.11 | 0.04 |
| Puzzle of Time | 4 | 29.2% | 40.4% | 0.0% | 0.10 | 0.05 |
| Robo Substitute Team Flare Gear | 4 | 29.2% | 40.4% | 1.2% | 0.11 | 0.04 |
| Level Ball | 2 | 29.1% | 40.0% | 0.0% | 0.09 | 0.04 |
| Manaphy | 1 | 29.0% | 40.6% | 2.5% | 0.10 | 0.04 |
| Mime Jr. | 2 | 28.6% | 40.0% | 5.0% | 0.10 | 0.05 |
| Nincada | 1 | 28.4% | 40.8% | 2.5% | 0.11 | 0.05 |
| Snorlax Doll | 2 | 28.3% | 39.7% | 2.5% | 0.10 | 0.06 |
| Crushing Hammer | 2 | 27.7% | 39.3% | 0.0% | 0.08 | 0.04 |
| Buddy-Buddy Poffin | 2 | 27.7% | 38.8% | 0.0% | 0.08 | 0.04 |
| Sableye | 2 | 27.6% | 37.6% | 2.5% | 0.07 | 0.03 |
| Field Blower | 1 | 27.6% | 39.6% | 2.5% | 0.10 | 0.05 |
| Slumbering Forest | 2 | 27.3% | 39.1% | 1.2% | 0.09 | 0.04 |
| Darkness Energy | 2 | 27.3% | 38.8% | 0.0% | 0.06 | 0.03 |
| Shedinja | 1 | 27.1% | 38.4% | 3.8% | 0.10 | 0.06 |
| Smoochum | 2 | 26.8% | 38.5% | 1.2% | 0.08 | 0.03 |
| Cursed Shovel | 3 | 26.1% | 38.6% | 0.0% | 0.10 | 0.05 |
| Battle Cage | 4 | 25.9% | 38.0% | 1.2% | 0.10 | 0.03 |
| — locked — | 0 | 25.9% | 38.9% | 2.5% | 0.00 | 0.00 |
| Team Rocket's Handiwork | 4 | 25.8% | 38.2% | 1.2% | 0.10 | 0.05 |

## Confirm

| Cut | Weighted | SE | vs locked | Mean | Worst | Stadium plays | Prize cuts | Junk Hunt |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — locked — | 27.6% | 0.56% | +0.0% | 39.8% | 1.0% | 0.00 | 0.00 | 2.33 |
| Switch | 29.4% | 0.59% | +1.7% | 40.8% | 0.8% | 0.09 | 0.04 | 2.28 |
| Dark Patch | 29.3% | 0.58% | +1.6% | 40.9% | 1.5% | 0.09 | 0.04 | 2.13 |
| Cleffa | 29.1% | 0.59% | +1.5% | 40.6% | 2.2% | 0.08 | 0.04 | 2.20 |
| Rescue Carrier | 29.0% | 0.58% | +1.4% | 40.7% | 2.2% | 0.09 | 0.04 | 2.23 |
| Life Dew | 28.7% | 0.57% | +1.0% | 40.3% | 1.5% | 0.09 | 0.05 | 2.27 |
| VS Seeker | 27.8% | 0.58% | +0.2% | 39.3% | 2.8% | 0.10 | 0.05 | 2.37 |
| Lillie's Poké Doll | 27.8% | 0.58% | +0.2% | 38.9% | 1.5% | 0.09 | 0.04 | 2.24 |

## Decision

The highest confirm cuts one Switch for one Black Market. Weighted 29.4% vs the two-Switch Doll at 27.6% (+1.7%; SE 0.59% on the swap and 0.56% on the two-Switch list, so the gap's SE is about 0.81%). The Stadium comes down about once every ten games, and the prize line fires less often than that, because Battle Cage stays up against spread. That cut is now SET_DOLL_NAMES: one Switch, one Black Market. This sample is not the 1000-game holdout.

## Foes on the confirm

| Foe | Locked | Switch | Dark Patch | Cleffa | Rescue Carrier | Life Dew | VS Seeker | Lillie's Poké Doll |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 50.8% | 49.0% | 49.5% | 45.0% | 49.2% | 45.2% | 48.0% | 47.0% |
| Hedrick Worlds Dragapult | 26.2% | 26.8% | 26.5% | 29.2% | 24.5% | 29.2% | 25.5% | 26.0% |
| Unlimited Dragapult | 75.2% | 78.0% | 76.0% | 78.5% | 74.5% | 75.2% | 76.0% | 72.2% |
| Cornerstone Ogerpon (D60) | 1.0% | 0.8% | 1.5% | 2.2% | 2.2% | 1.5% | 2.8% | 1.5% |
| Wo-Chien / Floragato (S60) | 52.5% | 55.0% | 53.8% | 56.0% | 55.0% | 55.2% | 50.8% | 48.5% |
| Gholdengo (G) | 16.5% | 20.8% | 23.2% | 18.0% | 16.2% | 17.2% | 18.0% | 21.8% |
| Clefairy / Mewtwo (C60) | 43.5% | 48.0% | 45.8% | 47.0% | 47.0% | 48.8% | 45.0% | 44.5% |
| Set M (Mew ex) | 14.5% | 17.0% | 14.5% | 18.0% | 17.8% | 13.2% | 14.8% | 15.2% |
| Mega Starmie ex (Kudo) | 9.2% | 11.5% | 13.2% | 10.2% | 13.2% | 12.8% | 10.8% | 10.8% |
| Lucario Hariyama | 70.5% | 70.5% | 72.2% | 68.2% | 71.0% | 69.2% | 66.5% | 67.8% |
| Iron Thorns ex | 87.5% | 85.8% | 87.2% | 86.5% | 88.8% | 86.8% | 86.5% | 83.0% |
| Carpet Set H | 6.2% | 6.8% | 5.0% | 6.5% | 3.8% | 6.0% | 5.3% | 5.5% |
| Ambipom Hand Fling | 64.2% | 61.0% | 63.7% | 62.0% | 65.5% | 64.0% | 60.7% | 62.5% |
