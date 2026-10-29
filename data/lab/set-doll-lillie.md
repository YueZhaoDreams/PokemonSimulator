# Doll, one Lillie's Determination

Printed text: shuffle your hand into your deck, then draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead. Doll plays that Supporter when the deck still has a replayable doll, the hand has fewer than two, and at most two are in play. A doll, Life Dew, Cursed Shovel, the Stadiums, Arven, and Petrel outrank it. Handiwork yields on that turn. One Supporter is played each turn. The redraw is not a search.

- **Seed**: `20261029`
- **Screen games per seat**: 40
- **Confirm games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 1791.4s

The baseline is the current Doll 60, including the Eeeeeeek pilot. The confirm is 400 games per seat. A cut higher than that baseline is the list. This sample is not the 1000-game holdout.

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
| — baseline — | 43.7% | 0.47% | +0.0% | 54.8% | 8.2% | 0.00 | 4.12 |
| Darkness Energy | 45.0% | 0.48% | +1.3% | 55.2% | 8.6% | 0.40 | 4.21 |
| Slumbering Forest | 44.7% | 0.48% | +1.0% | 55.9% | 9.8% | 0.39 | 4.31 |
| Crushing Hammer | 44.3% | 0.47% | +0.7% | 55.1% | 8.4% | 0.39 | 4.34 |
| Battle Cage | 44.3% | 0.48% | +0.6% | 54.9% | 9.9% | 0.39 | 4.27 |
| Switch | 44.2% | 0.48% | +0.6% | 55.1% | 8.2% | 0.39 | 4.29 |
| Shedinja | 44.0% | 0.47% | +0.3% | 55.3% | 9.5% | 0.40 | 4.19 |
| Buddy-Buddy Poffin | 43.9% | 0.48% | +0.2% | 54.5% | 10.6% | 0.38 | 4.33 |

The confirm cuts one Darkness Energy for one Lillie's Determination. Weighted 45.0% vs 43.7% (+1.3%; SE 0.48% on the swap and 0.47% on the baseline, so the gap's SE is about 0.67%, 2.0 SE). Lillie's Determination resolves 0.40 times a game on the Sisters weights.

| Foe | Baseline | Darkness Energy | Slumbering Forest | Crushing Hammer | Battle Cage | Switch | Shedinja | Buddy-Buddy Poffin |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 69.4% | 71.6% | 73.2% | 72.8% | 71.1% | 73.0% | 75.5% | 71.5% |
| Hedrick Worlds Dragapult | 48.9% | 50.4% | 49.5% | 50.0% | 47.1% | 48.9% | 54.9% | 46.6% |
| Unlimited Dragapult | 87.4% | 88.0% | 87.5% | 85.0% | 86.4% | 85.5% | 86.0% | 87.2% |
| Cornerstone Ogerpon (D60) | 8.2% | 8.6% | 9.8% | 8.4% | 9.9% | 8.2% | 9.5% | 10.6% |
| Wo-Chien / Floragato (S60) | 69.0% | 63.3% | 71.1% | 64.6% | 65.4% | 66.9% | 65.5% | 65.4% |
| Gholdengo (G) | 41.4% | 45.0% | 43.6% | 42.8% | 42.2% | 42.6% | 42.8% | 42.0% |
| Clefairy / Mewtwo (C60) | 69.2% | 73.9% | 68.6% | 73.5% | 72.2% | 66.6% | 68.8% | 70.6% |
| Set M (Mew ex) | 30.4% | 34.4% | 30.9% | 30.9% | 31.2% | 32.8% | 28.1% | 32.0% |
| Mega Starmie ex (Kudo) | 24.2% | 26.2% | 24.6% | 26.4% | 26.9% | 26.6% | 24.1% | 24.1% |
| Lucario Hariyama | 84.1% | 82.5% | 84.9% | 81.6% | 83.9% | 85.1% | 86.0% | 81.9% |
| Iron Thorns ex | 92.8% | 94.6% | 93.4% | 94.0% | 93.6% | 95.1% | 93.9% | 93.9% |
| Carpet Set H | 14.9% | 12.0% | 15.8% | 13.4% | 12.0% | 15.8% | 14.0% | 11.9% |
| Ambipom Hand Fling | 72.4% | 67.6% | 74.0% | 73.5% | 71.1% | 69.0% | 70.2% | 71.4% |
