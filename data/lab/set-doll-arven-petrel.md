# Doll, Arven then Petrel

One Supporter is played each turn. Arven searches the deck for an Item and a Pokémon Tool. When the hand has no doll, the Item is Lillie's Poké Doll or Robo Substitute, and the Tool is Cursed Shovel, then Life Dew. Team Rocket's Petrel searches for one Trainer: a doll if the hand has none, otherwise Battle Cage, Slumbering Forest, Team Rocket's Handiwork, or that Tool. The Supporter that was not played stays in hand.

- **Seed**: `20261029`
- **Screen games per seat**: 40
- **Confirm games per seat**: 200
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 2498.1s

The Arven step starts from the Black Market 60. The Petrel step starts from the Arven list because that confirm is higher. The two Cleffa cuts are now SET_DOLL_NAMES: one Arven and one Team Rocket's Petrel. Lillie's Poké Doll and Robo Substitute stay at four. This sample is not the 1000-game holdout.

## Arven

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Arven | Petrel | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 29.3% | 1.30% | +0.0% | 40.7% | 3.8% | 0.00 | 0.00 | 2.88 |
| VS Seeker | 33.7% | 1.34% | +4.4% | 45.4% | 1.2% | 0.49 | 0.00 | 3.17 |
| Cleffa | 33.3% | 1.38% | +4.0% | 45.3% | 1.2% | 0.52 | 0.00 | 3.21 |
| Crushing Hammer | 32.9% | 1.33% | +3.5% | 43.4% | 0.0% | 0.50 | 0.00 | 3.16 |
| Nincada | 32.3% | 1.31% | +3.0% | 43.8% | 0.0% | 0.49 | 0.00 | 3.18 |
| Switch | 31.8% | 1.32% | +2.5% | 43.3% | 1.2% | 0.47 | 0.00 | 3.17 |
| Smoochum | 31.5% | 1.38% | +2.2% | 42.5% | 3.8% | 0.50 | 0.00 | 3.16 |
| Shedinja | 31.3% | 1.35% | +2.0% | 42.1% | 5.0% | 0.46 | 0.00 | 3.02 |
| Buddy-Buddy Poffin | 31.3% | 1.33% | +2.0% | 42.0% | 5.0% | 0.49 | 0.00 | 3.15 |
| Sableye | 31.3% | 1.32% | +2.0% | 42.1% | 1.2% | 0.48 | 0.00 | 3.04 |
| Puzzle of Time | 31.2% | 1.30% | +1.9% | 43.7% | 3.8% | 0.43 | 0.00 | 3.10 |
| Robo Substitute Team Flare Gear | 31.1% | 1.31% | +1.8% | 42.5% | 1.2% | 0.48 | 0.00 | 2.84 |
| Rescue Carrier | 30.9% | 1.30% | +1.6% | 42.2% | 3.8% | 0.52 | 0.00 | 3.12 |
| Lillie's Poké Doll | 30.3% | 1.33% | +1.0% | 42.3% | 2.5% | 0.46 | 0.00 | 2.82 |
| Level Ball | 30.3% | 1.28% | +1.0% | 42.1% | 2.5% | 0.51 | 0.00 | 3.14 |
| Manaphy | 30.2% | 1.27% | +0.9% | 42.3% | 0.0% | 0.47 | 0.00 | 3.16 |
| Battle Cage | 30.1% | 1.33% | +0.8% | 41.8% | 1.2% | 0.47 | 0.00 | 3.12 |
| Field Blower | 30.0% | 1.28% | +0.7% | 41.6% | 1.2% | 0.48 | 0.00 | 3.12 |
| Life Dew | 29.9% | 1.33% | +0.6% | 41.0% | 3.8% | 0.45 | 0.00 | 3.04 |
| Dark Patch | 29.6% | 1.31% | +0.3% | 41.1% | 0.0% | 0.51 | 0.00 | 3.13 |
| Cursed Shovel | 29.4% | 1.30% | +0.1% | 41.1% | 2.5% | 0.48 | 0.00 | 3.06 |
| Darkness Energy | 29.2% | 1.23% | -0.2% | 40.5% | 0.0% | 0.46 | 0.00 | 3.07 |
| Black Market | 29.1% | 1.24% | -0.2% | 41.8% | 0.0% | 0.46 | 0.00 | 3.15 |
| Mime Jr. | 29.1% | 1.29% | -0.2% | 40.9% | 1.2% | 0.47 | 0.00 | 3.10 |
| Team Rocket's Handiwork | 28.6% | 1.26% | -0.7% | 40.4% | 0.0% | 0.53 | 0.00 | 3.17 |
| Slumbering Forest | 28.3% | 1.27% | -1.0% | 40.9% | 0.0% | 0.53 | 0.00 | 3.15 |
| Snorlax Doll | 27.8% | 1.28% | -1.5% | 39.7% | 0.0% | 0.45 | 0.00 | 3.10 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Arven | Petrel | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 29.5% | 0.58% | +0.0% | 41.2% | 1.8% | 0.00 | 0.00 | 2.86 |
| Cleffa | 31.2% | 0.60% | +1.7% | 42.5% | 2.0% | 0.48 | 0.00 | 3.14 |
| VS Seeker | 31.1% | 0.60% | +1.6% | 42.9% | 2.2% | 0.48 | 0.00 | 3.16 |
| Switch | 31.1% | 0.59% | +1.5% | 42.8% | 1.0% | 0.47 | 0.00 | 3.16 |
| Crushing Hammer | 31.1% | 0.59% | +1.5% | 42.4% | 1.8% | 0.49 | 0.00 | 3.16 |
| Nincada | 30.9% | 0.60% | +1.4% | 42.6% | 1.5% | 0.47 | 0.00 | 3.16 |
| Smoochum | 30.4% | 0.60% | +0.9% | 41.4% | 2.0% | 0.49 | 0.00 | 3.13 |
| Shedinja | 30.4% | 0.60% | +0.9% | 41.3% | 2.0% | 0.46 | 0.00 | 3.08 |

The highest confirm cuts one Cleffa for one Arven. Weighted 31.2% vs 29.5% (+1.7%; SE 0.60% on the swap and 0.58% on the baseline, so the gap's SE is about 0.84%). Cleffa, VS Seeker, Switch, and Crushing Hammer sit within 0.2 points. That spread is inside the gap's standard error, so the point estimate is Cleffa and the Petrel step uses that list.

| Foe | Baseline | Cleffa | VS Seeker | Switch | Crushing Hammer | Nincada | Smoochum | Shedinja |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 50.5% | 51.2% | 53.0% | 56.5% | 55.8% | 51.8% | 44.2% | 46.8% |
| Hedrick Worlds Dragapult | 31.2% | 26.2% | 30.2% | 27.0% | 25.8% | 29.8% | 31.0% | 27.8% |
| Unlimited Dragapult | 72.0% | 80.8% | 80.8% | 77.8% | 74.0% | 78.5% | 76.5% | 76.5% |
| Cornerstone Ogerpon (D60) | 1.8% | 2.0% | 2.2% | 1.0% | 1.8% | 1.5% | 2.0% | 2.0% |
| Wo-Chien / Floragato (S60) | 53.8% | 59.7% | 57.8% | 56.5% | 60.2% | 54.8% | 58.7% | 52.0% |
| Gholdengo (G) | 19.5% | 25.0% | 16.8% | 23.8% | 24.0% | 21.5% | 21.0% | 20.8% |
| Clefairy / Mewtwo (C60) | 48.8% | 50.5% | 49.5% | 51.8% | 51.0% | 51.8% | 48.5% | 54.2% |
| Set M (Mew ex) | 15.8% | 20.8% | 25.0% | 14.8% | 19.5% | 19.0% | 21.8% | 18.5% |
| Mega Starmie ex (Kudo) | 11.5% | 9.0% | 10.8% | 16.2% | 9.2% | 13.0% | 11.0% | 12.8% |
| Lucario Hariyama | 72.8% | 72.8% | 73.0% | 72.8% | 74.8% | 72.8% | 68.0% | 71.5% |
| Iron Thorns ex | 87.8% | 85.8% | 87.5% | 87.8% | 86.5% | 88.0% | 86.8% | 86.0% |
| Carpet Set H | 5.5% | 6.0% | 5.0% | 6.8% | 5.0% | 5.8% | 6.2% | 5.3% |
| Ambipom Hand Fling | 65.5% | 62.5% | 65.8% | 64.2% | 64.0% | 66.0% | 62.5% | 63.3% |

## Team Rocket's Petrel

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Arven | Petrel | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 33.3% | 1.38% | +0.0% | 45.3% | 1.2% | 0.52 | 0.00 | 3.21 |
| Cleffa | 34.8% | 1.39% | +1.5% | 46.2% | 1.2% | 0.47 | 0.50 | 3.39 |
| Battle Cage | 34.0% | 1.39% | +0.7% | 44.2% | 1.2% | 0.53 | 0.45 | 3.41 |
| Switch | 33.5% | 1.37% | +0.2% | 44.8% | 5.0% | 0.46 | 0.46 | 3.45 |
| Field Blower | 33.4% | 1.35% | +0.1% | 44.3% | 0.0% | 0.48 | 0.48 | 3.39 |
| Robo Substitute Team Flare Gear | 33.3% | 1.38% | -0.1% | 44.8% | 3.8% | 0.46 | 0.49 | 3.05 |
| Nincada | 32.9% | 1.32% | -0.5% | 45.0% | 2.5% | 0.46 | 0.48 | 3.35 |
| Dark Patch | 32.8% | 1.34% | -0.5% | 44.4% | 2.5% | 0.44 | 0.46 | 3.32 |
| Slumbering Forest | 32.7% | 1.35% | -0.6% | 44.2% | 2.5% | 0.51 | 0.49 | 3.41 |
| Sableye | 32.6% | 1.31% | -0.7% | 45.6% | 0.0% | 0.45 | 0.45 | 3.39 |
| Manaphy | 32.6% | 1.35% | -0.8% | 44.0% | 1.2% | 0.47 | 0.46 | 3.40 |
| Cursed Shovel | 32.4% | 1.35% | -0.9% | 44.5% | 1.2% | 0.51 | 0.50 | 3.44 |
| Crushing Hammer | 32.3% | 1.33% | -1.1% | 42.6% | 1.2% | 0.52 | 0.46 | 3.37 |
| Lillie's Poké Doll | 31.9% | 1.36% | -1.4% | 42.9% | 1.2% | 0.51 | 0.44 | 3.04 |
| VS Seeker | 31.9% | 1.36% | -1.4% | 42.8% | 2.5% | 0.48 | 0.42 | 3.41 |
| Darkness Energy | 31.6% | 1.30% | -1.7% | 43.5% | 0.0% | 0.43 | 0.43 | 3.23 |
| Arven | 31.6% | 1.31% | -1.7% | 44.6% | 1.2% | 0.00 | 0.47 | 3.08 |
| Puzzle of Time | 31.6% | 1.31% | -1.8% | 43.8% | 1.2% | 0.43 | 0.45 | 3.28 |
| Buddy-Buddy Poffin | 31.5% | 1.34% | -1.8% | 42.5% | 1.2% | 0.53 | 0.43 | 3.46 |
| Shedinja | 31.5% | 1.30% | -1.9% | 43.7% | 1.2% | 0.50 | 0.46 | 3.33 |
| Level Ball | 31.4% | 1.32% | -2.0% | 43.8% | 1.2% | 0.51 | 0.45 | 3.37 |
| Smoochum | 31.2% | 1.32% | -2.1% | 43.0% | 1.2% | 0.48 | 0.47 | 3.37 |
| Rescue Carrier | 30.6% | 1.32% | -2.8% | 42.0% | 1.2% | 0.47 | 0.48 | 3.38 |
| Team Rocket's Handiwork | 30.0% | 1.31% | -3.4% | 41.2% | 1.2% | 0.48 | 0.50 | 3.47 |
| Snorlax Doll | 29.7% | 1.27% | -3.6% | 42.3% | 0.0% | 0.50 | 0.47 | 3.29 |
| Life Dew | 29.7% | 1.32% | -3.7% | 42.9% | 1.2% | 0.46 | 0.49 | 3.36 |
| Black Market | 29.6% | 1.28% | -3.8% | 41.4% | 0.0% | 0.51 | 0.47 | 3.35 |
| Mime Jr. | 29.5% | 1.34% | -3.9% | 40.9% | 2.5% | 0.49 | 0.46 | 3.50 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Arven | Petrel | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 31.2% | 0.60% | +0.0% | 42.5% | 2.0% | 0.48 | 0.00 | 3.14 |
| Cleffa | 33.8% | 0.61% | +2.6% | 45.1% | 1.0% | 0.49 | 0.47 | 3.39 |
| Switch | 33.0% | 0.60% | +1.8% | 44.6% | 2.0% | 0.47 | 0.47 | 3.41 |
| Dark Patch | 32.9% | 0.59% | +1.7% | 44.8% | 1.5% | 0.48 | 0.47 | 3.36 |
| Battle Cage | 32.7% | 0.61% | +1.5% | 43.6% | 1.0% | 0.49 | 0.46 | 3.33 |
| Field Blower | 32.2% | 0.60% | +1.0% | 44.0% | 1.0% | 0.49 | 0.46 | 3.37 |
| Robo Substitute Team Flare Gear | 31.8% | 0.61% | +0.6% | 43.8% | 2.2% | 0.47 | 0.44 | 3.04 |
| Nincada | 31.7% | 0.60% | +0.5% | 43.4% | 2.2% | 0.48 | 0.48 | 3.36 |

The highest confirm cuts one Cleffa for one Team Rocket's Petrel. Weighted 33.8% vs 31.2% (+2.6%; SE 0.61% on the swap and 0.60% on the baseline, so the gap's SE is about 0.86%). Switch is the next confirm, 0.8 points lower. Lillie's Poké Doll and Robo Substitute stay at four. These two cuts are the Doll lock.

| Foe | Baseline | Cleffa | Switch | Dark Patch | Battle Cage | Field Blower | Robo Substitute Team Flare Gear | Nincada |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 51.2% | 53.5% | 56.2% | 57.5% | 52.0% | 54.2% | 53.5% | 55.2% |
| Hedrick Worlds Dragapult | 26.2% | 32.2% | 26.5% | 30.0% | 26.2% | 27.7% | 31.5% | 29.0% |
| Unlimited Dragapult | 80.8% | 79.2% | 80.2% | 83.0% | 78.0% | 81.5% | 79.8% | 80.5% |
| Cornerstone Ogerpon (D60) | 2.0% | 1.0% | 2.0% | 1.5% | 1.0% | 1.0% | 2.2% | 2.2% |
| Wo-Chien / Floragato (S60) | 59.7% | 61.3% | 56.5% | 61.5% | 57.0% | 59.5% | 58.5% | 55.2% |
| Gholdengo (G) | 25.0% | 23.5% | 28.5% | 19.0% | 22.8% | 21.5% | 26.0% | 20.0% |
| Clefairy / Mewtwo (C60) | 50.5% | 56.8% | 58.5% | 58.5% | 56.2% | 54.8% | 50.2% | 55.2% |
| Set M (Mew ex) | 20.8% | 28.2% | 18.5% | 23.8% | 23.0% | 22.2% | 17.0% | 20.8% |
| Mega Starmie ex (Kudo) | 9.0% | 11.5% | 12.0% | 11.5% | 17.0% | 13.5% | 15.2% | 12.0% |
| Lucario Hariyama | 72.8% | 75.0% | 78.0% | 75.2% | 73.5% | 75.0% | 69.8% | 72.5% |
| Iron Thorns ex | 85.8% | 88.5% | 90.8% | 90.0% | 91.3% | 89.0% | 90.8% | 91.0% |
| Carpet Set H | 6.0% | 6.2% | 4.2% | 3.2% | 6.0% | 4.0% | 6.5% | 4.8% |
| Ambipom Hand Fling | 62.5% | 69.5% | 68.2% | 68.2% | 62.3% | 67.5% | 68.8% | 66.3% |
