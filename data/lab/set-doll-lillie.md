# Doll, one Lillie's Determination

Printed text: shuffle your hand into your deck, then draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead. Doll plays that Supporter when the deck still has a replayable doll, the hand has fewer than two, and at most two are in play. A doll, Life Dew, Cursed Shovel, the Stadiums, Arven, and Petrel outrank it. Handiwork yields on that turn. One Supporter is played each turn. The redraw is not a search.

- **Seed**: `20261029`
- **Screen games per seat**: 40
- **Confirm games per seat**: 200
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 1553.5s

The baseline is the current Doll 60, including the Eeeeeeek pilot. A cut is locked only when its confirm is higher by about two standard errors of the gap. This sample is not the 1000-game holdout.

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Determination | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 42.7% | 1.48% | +0.0% | 53.9% | 8.8% | 0.00 | 4.13 |
| Crushing Hammer | 47.3% | 1.50% | +4.6% | 58.3% | 12.5% | 0.39 | 4.34 |
| Darkness Energy | 46.5% | 1.53% | +3.8% | 54.7% | 8.8% | 0.40 | 4.33 |
| Battle Cage | 45.8% | 1.55% | +3.1% | 56.0% | 7.5% | 0.39 | 4.29 |
| Slumbering Forest | 45.8% | 1.46% | +3.1% | 58.1% | 6.2% | 0.40 | 4.48 |
| Buddy-Buddy Poffin | 45.7% | 1.49% | +3.0% | 56.6% | 8.8% | 0.40 | 4.50 |
| Shedinja | 45.4% | 1.53% | +2.7% | 56.8% | 11.2% | 0.41 | 4.18 |
| Switch | 45.4% | 1.54% | +2.7% | 56.1% | 8.8% | 0.40 | 4.29 |
| Cleffa | 45.1% | 1.50% | +2.4% | 55.6% | 6.2% | 0.35 | 4.16 |
| Smoochum | 45.1% | 1.50% | +2.4% | 56.0% | 10.0% | 0.38 | 4.35 |
| Rescue Carrier | 44.8% | 1.50% | +2.1% | 55.8% | 15.0% | 0.39 | 4.27 |
| Black Market | 44.7% | 1.42% | +2.0% | 56.2% | 6.2% | 0.38 | 4.34 |
| Robo Substitute Team Flare Gear | 44.7% | 1.42% | +2.0% | 55.3% | 11.2% | 0.39 | 3.98 |
| Field Blower | 44.7% | 1.50% | +2.0% | 55.7% | 8.8% | 0.40 | 4.30 |
| Dark Patch | 44.7% | 1.46% | +1.9% | 55.2% | 8.8% | 0.36 | 4.35 |
| Snorlax Doll | 44.6% | 1.56% | +1.9% | 54.3% | 12.5% | 0.37 | 4.30 |
| Sableye | 44.5% | 1.51% | +1.8% | 54.5% | 7.5% | 0.34 | 4.22 |
| Team Rocket's Petrel | 43.9% | 1.47% | +1.2% | 55.3% | 10.0% | 0.42 | 4.13 |
| Lillie's Poké Doll | 43.9% | 1.51% | +1.2% | 55.4% | 10.0% | 0.40 | 3.95 |
| Nincada | 43.8% | 1.50% | +1.1% | 55.4% | 11.2% | 0.39 | 4.38 |
| Arven | 43.7% | 1.45% | +1.0% | 56.0% | 5.0% | 0.43 | 4.05 |
| Puzzle of Time | 43.6% | 1.48% | +0.9% | 53.9% | 6.2% | 0.38 | 4.28 |
| Manaphy | 43.1% | 1.45% | +0.4% | 54.4% | 10.0% | 0.36 | 4.54 |
| Cursed Shovel | 42.9% | 1.54% | +0.2% | 53.8% | 12.5% | 0.38 | 4.36 |
| Level Ball | 42.2% | 1.42% | -0.6% | 54.5% | 3.8% | 0.40 | 4.31 |
| Mime Jr. | 41.8% | 1.48% | -0.9% | 53.1% | 6.2% | 0.38 | 4.30 |
| Team Rocket's Handiwork | 41.6% | 1.46% | -1.1% | 52.8% | 5.0% | 0.37 | 4.45 |
| VS Seeker | 40.3% | 1.47% | -2.4% | 52.7% | 8.8% | 0.40 | 4.35 |
| Life Dew | 39.7% | 1.48% | -3.0% | 51.1% | 10.0% | 0.37 | 4.25 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Determination | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 43.5% | 0.68% | +0.0% | 54.4% | 10.5% | 0.00 | 4.15 |
| Slumbering Forest | 44.8% | 0.67% | +1.3% | 56.0% | 10.5% | 0.39 | 4.32 |
| Switch | 44.5% | 0.68% | +1.0% | 54.9% | 9.0% | 0.39 | 4.30 |
| Darkness Energy | 44.5% | 0.67% | +0.9% | 54.8% | 7.5% | 0.40 | 4.23 |
| Crushing Hammer | 44.3% | 0.66% | +0.8% | 55.1% | 7.3% | 0.39 | 4.34 |
| Battle Cage | 44.0% | 0.67% | +0.5% | 54.8% | 8.0% | 0.39 | 4.28 |
| Shedinja | 43.8% | 0.68% | +0.3% | 55.1% | 9.5% | 0.40 | 4.21 |
| Buddy-Buddy Poffin | 43.5% | 0.67% | -0.0% | 54.3% | 8.2% | 0.38 | 4.33 |

The highest confirm cuts one Slumbering Forest and is higher by +1.3%, but the gap's SE is about 0.95% (1.3 SE). That is noise against this baseline. The 60 stays unchanged. Lillie's Determination on that cut resolves 0.39 times a game on the Sisters weights.

| Foe | Baseline | Slumbering Forest | Switch | Darkness Energy | Crushing Hammer | Battle Cage | Shedinja | Buddy-Buddy Poffin |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 68.8% | 75.0% | 74.2% | 71.2% | 72.5% | 71.0% | 72.8% | 70.0% |
| Hedrick Worlds Dragapult | 47.0% | 45.0% | 47.0% | 50.8% | 49.5% | 47.0% | 53.2% | 46.0% |
| Unlimited Dragapult | 85.5% | 90.0% | 86.0% | 87.5% | 84.7% | 86.5% | 86.8% | 86.8% |
| Cornerstone Ogerpon (D60) | 10.5% | 10.5% | 9.0% | 7.5% | 7.3% | 8.0% | 9.5% | 8.2% |
| Wo-Chien / Floragato (S60) | 66.5% | 72.2% | 64.0% | 64.0% | 66.3% | 65.3% | 65.3% | 64.2% |
| Gholdengo (G) | 41.0% | 41.8% | 43.5% | 44.0% | 44.0% | 42.8% | 45.5% | 44.0% |
| Clefairy / Mewtwo (C60) | 69.0% | 72.2% | 67.2% | 72.0% | 73.2% | 70.5% | 66.3% | 71.2% |
| Set M (Mew ex) | 30.5% | 30.2% | 34.0% | 35.0% | 30.0% | 31.5% | 29.0% | 29.8% |
| Mega Starmie ex (Kudo) | 24.2% | 24.2% | 28.5% | 25.5% | 26.0% | 27.0% | 24.0% | 23.5% |
| Lucario Hariyama | 83.0% | 84.5% | 84.7% | 82.7% | 82.5% | 84.5% | 85.2% | 83.0% |
| Iron Thorns ex | 93.8% | 92.5% | 95.0% | 93.2% | 94.0% | 94.0% | 92.8% | 94.2% |
| Carpet Set H | 13.5% | 15.2% | 13.8% | 11.0% | 13.8% | 12.0% | 14.0% | 13.5% |
| Ambipom Hand Fling | 73.5% | 74.2% | 67.0% | 67.5% | 72.8% | 73.0% | 72.0% | 71.0% |
