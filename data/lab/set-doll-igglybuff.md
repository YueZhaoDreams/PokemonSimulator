# Doll, Sleepy Voice Igglybuff

Printed text: once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends. The sentence does not say the Active Spot, so a Benched Igglybuff can use it. Doll spends that attack on the coin only when the hit ignores effects on the Active, as Demolish does. Eeeeeeek, Energy Antics, Sleepy Lost, and Junk Hunt stay ahead of the coin against every other deck. A turn with no attack still flips when their hit would land. Slumbering Forest is the wake check that is already in the list.

An earlier sample used the coin whenever the Active was awake. That confirm cut Cleffa and landed at 50.1% against its own 53.0% baseline. D60 rose from 6.0% to 20.0%, and the ended turn cost the other foes. This sample is the benefit rule.

- **Seed**: `20261029`
- **Screen games per seat**: 40
- **Confirm games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates. Doll goes first in either seat.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Elapsed**: 11206.8s

Each step adds one Sleepy Voice Igglybuff. The confirm is 400 games per seat. A cut higher than that step's baseline is the next list. Four is the maximum. This sample is not the 1000-game holdout.

## Copy 1

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 53.0% | 1.47% | +0.0% | 62.2% | 6.2% | 0.00 | 0.00 | 4.60 |
| Smoochum | 59.2% | 1.55% | +6.2% | 67.4% | 8.8% | 3.36 | 1.64 | 4.70 |
| Arven | 58.9% | 1.57% | +5.9% | 65.8% | 11.2% | 2.75 | 1.40 | 4.15 |
| Switch | 57.3% | 1.51% | +4.2% | 65.6% | 8.8% | 2.80 | 1.42 | 4.39 |
| Black Market | 57.0% | 1.55% | +4.0% | 65.4% | 15.0% | 2.71 | 1.33 | 4.37 |
| Snorlax Doll | 57.0% | 1.54% | +3.9% | 65.4% | 13.8% | 2.77 | 1.37 | 4.40 |
| Lillie's Poké Doll | 56.9% | 1.54% | +3.9% | 65.2% | 10.0% | 2.75 | 1.37 | 4.05 |
| Nincada | 56.7% | 1.49% | +3.6% | 65.6% | 7.5% | 2.88 | 1.45 | 4.45 |
| Cleffa | 56.4% | 1.57% | +3.4% | 63.7% | 16.2% | 2.59 | 1.29 | 4.11 |
| Mime Jr. | 56.2% | 1.58% | +3.2% | 63.6% | 8.8% | 3.00 | 1.49 | 4.49 |
| Shedinja | 56.1% | 1.54% | +3.1% | 64.7% | 6.2% | 2.73 | 1.35 | 4.26 |
| Crushing Hammer | 56.1% | 1.57% | +3.1% | 64.2% | 13.8% | 2.88 | 1.41 | 4.40 |
| Level Ball | 55.8% | 1.54% | +2.8% | 63.7% | 7.5% | 2.68 | 1.32 | 4.31 |
| Field Blower | 55.8% | 1.52% | +2.8% | 64.8% | 15.0% | 2.77 | 1.38 | 4.43 |
| Robo Substitute Team Flare Gear | 55.5% | 1.52% | +2.5% | 64.9% | 13.8% | 2.64 | 1.30 | 4.02 |
| Lillie's Determination | 55.3% | 1.56% | +2.3% | 63.7% | 16.2% | 2.71 | 1.39 | 4.10 |
| VS Seeker | 55.2% | 1.57% | +2.2% | 63.2% | 12.5% | 2.87 | 1.39 | 4.35 |
| Sableye | 54.8% | 1.56% | +1.7% | 63.8% | 3.8% | 2.71 | 1.34 | 4.33 |
| Darkness Energy | 54.3% | 1.51% | +1.3% | 63.6% | 3.8% | 2.77 | 1.34 | 4.27 |
| Manaphy | 54.3% | 1.43% | +1.3% | 63.6% | 8.8% | 2.70 | 1.32 | 4.50 |
| Rescue Carrier | 54.1% | 1.59% | +1.1% | 63.4% | 13.8% | 2.86 | 1.41 | 4.39 |
| Battle Cage | 54.1% | 1.52% | +1.1% | 62.6% | 7.5% | 2.78 | 1.40 | 4.34 |
| Team Rocket's Petrel | 53.9% | 1.53% | +0.9% | 63.1% | 6.2% | 2.68 | 1.34 | 4.13 |
| Puzzle of Time | 53.6% | 1.55% | +0.6% | 62.3% | 11.2% | 2.74 | 1.34 | 4.40 |
| Life Dew | 53.5% | 1.52% | +0.4% | 62.8% | 8.8% | 2.83 | 1.38 | 4.27 |
| Cursed Shovel | 53.0% | 1.54% | -0.0% | 62.2% | 6.2% | 2.86 | 1.42 | 4.37 |
| Slumbering Forest | 52.9% | 1.54% | -0.2% | 62.2% | 5.0% | 2.85 | 1.43 | 4.41 |
| Buddy-Buddy Poffin | 51.6% | 1.54% | -1.4% | 61.2% | 5.0% | 2.88 | 1.46 | 4.54 |
| Team Rocket's Handiwork | 51.6% | 1.53% | -1.4% | 60.6% | 2.5% | 2.97 | 1.50 | 4.40 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 53.0% | 0.47% | +0.0% | 61.9% | 6.0% | 0.00 | 0.00 | 4.64 |
| Black Market | 57.7% | 0.50% | +4.7% | 65.7% | 11.2% | 2.81 | 1.40 | 4.35 |
| Smoochum | 57.5% | 0.49% | +4.5% | 65.5% | 10.4% | 3.11 | 1.55 | 4.55 |
| Nincada | 57.1% | 0.50% | +4.1% | 65.6% | 12.6% | 2.76 | 1.38 | 4.40 |
| Switch | 56.7% | 0.50% | +3.7% | 64.7% | 11.0% | 2.84 | 1.43 | 4.39 |
| Snorlax Doll | 56.6% | 0.50% | +3.6% | 64.9% | 12.2% | 2.81 | 1.40 | 4.36 |
| Arven | 56.1% | 0.49% | +3.1% | 64.1% | 12.1% | 2.70 | 1.35 | 4.17 |
| Lillie's Poké Doll | 55.9% | 0.49% | +2.9% | 64.5% | 11.9% | 2.63 | 1.32 | 4.00 |

The confirm cuts one Black Market for copy 1. Weighted 57.7% vs 53.0% (+4.7%; SE 0.50% on the swap and 0.47% on the baseline, so the gap's SE is about 0.68%, 6.9 SE). Sleepy Voice flips 3.36 times a game and lands heads 1.69 times, on the Sisters weights.

| Foe | Baseline | Black Market | Smoochum | Nincada | Switch | Snorlax Doll | Arven | Lillie's Poké Doll |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 81.2% | 85.2% | 83.2% | 85.5% | 85.9% | 85.2% | 82.8% | 85.8% |
| Hedrick Worlds Dragapult | 55.5% | 67.5% | 68.8% | 71.1% | 66.5% | 68.6% | 70.0% | 67.6% |
| Unlimited Dragapult | 92.1% | 94.8% | 94.0% | 94.2% | 93.1% | 94.2% | 92.3% | 93.8% |
| Cornerstone Ogerpon (D60) | 6.0% | 23.6% | 21.8% | 24.2% | 21.3% | 20.8% | 20.9% | 18.2% |
| Wo-Chien / Floragato (S60) | 70.6% | 68.9% | 74.0% | 72.0% | 67.0% | 70.9% | 68.9% | 68.6% |
| Gholdengo (G) | 54.6% | 61.4% | 63.4% | 56.8% | 59.6% | 55.2% | 57.2% | 60.9% |
| Clefairy / Mewtwo (C60) | 82.9% | 84.5% | 81.0% | 85.5% | 82.9% | 84.8% | 83.8% | 84.0% |
| Set M (Mew ex) | 57.4% | 55.9% | 60.9% | 55.0% | 58.5% | 54.0% | 56.2% | 53.8% |
| Mega Starmie ex (Kudo) | 37.6% | 42.8% | 36.6% | 36.5% | 39.8% | 45.5% | 37.4% | 37.9% |
| Lucario Hariyama | 88.6% | 90.9% | 89.5% | 91.6% | 90.2% | 86.4% | 88.8% | 89.2% |
| Iron Thorns ex | 94.4% | 94.4% | 95.0% | 94.2% | 93.6% | 94.5% | 94.6% | 94.6% |
| Carpet Set H | 11.5% | 11.2% | 10.4% | 12.6% | 11.0% | 12.2% | 12.1% | 11.9% |
| Ambipom Hand Fling | 72.6% | 72.6% | 72.8% | 72.9% | 71.2% | 71.8% | 68.2% | 72.0% |

## Copy 2

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 57.0% | 1.55% | +0.0% | 65.4% | 15.0% | 2.71 | 1.33 | 4.37 |
| Field Blower | 59.3% | 1.57% | +2.3% | 66.3% | 11.2% | 3.28 | 1.66 | 4.35 |
| Nincada | 59.0% | 1.60% | +1.9% | 66.4% | 10.0% | 3.16 | 1.60 | 4.36 |
| Snorlax Doll | 58.9% | 1.56% | +1.9% | 66.2% | 12.5% | 3.23 | 1.58 | 4.40 |
| VS Seeker | 58.8% | 1.52% | +1.8% | 66.6% | 6.2% | 3.35 | 1.68 | 4.36 |
| Puzzle of Time | 58.6% | 1.52% | +1.5% | 65.9% | 11.2% | 3.22 | 1.59 | 4.26 |
| Sableye | 58.4% | 1.56% | +1.4% | 66.3% | 7.5% | 3.20 | 1.55 | 4.44 |
| Rescue Carrier | 58.3% | 1.56% | +1.3% | 66.2% | 8.8% | 3.46 | 1.69 | 4.48 |
| Level Ball | 58.3% | 1.57% | +1.3% | 66.3% | 10.0% | 3.21 | 1.58 | 4.37 |
| Shedinja | 58.2% | 1.63% | +1.2% | 65.1% | 10.0% | 3.20 | 1.61 | 4.25 |
| Crushing Hammer | 58.1% | 1.56% | +1.0% | 65.4% | 10.0% | 3.26 | 1.61 | 4.36 |
| Buddy-Buddy Poffin | 58.0% | 1.56% | +1.0% | 65.4% | 10.0% | 3.34 | 1.68 | 4.52 |
| Battle Cage | 57.5% | 1.59% | +0.5% | 65.7% | 11.2% | 3.22 | 1.58 | 4.34 |
| Lillie's Determination | 57.1% | 1.55% | +0.1% | 65.4% | 7.5% | 3.18 | 1.55 | 4.29 |
| Smoochum | 57.0% | 1.60% | -0.0% | 64.3% | 11.2% | 3.66 | 1.77 | 4.60 |
| Arven | 57.0% | 1.59% | -0.1% | 65.7% | 11.2% | 3.12 | 1.49 | 4.10 |
| Darkness Energy | 56.8% | 1.53% | -0.3% | 64.3% | 3.8% | 3.28 | 1.64 | 4.29 |
| Team Rocket's Petrel | 56.6% | 1.58% | -0.4% | 64.4% | 6.2% | 3.30 | 1.65 | 4.15 |
| Switch | 56.4% | 1.56% | -0.6% | 64.5% | 6.2% | 3.42 | 1.68 | 4.53 |
| Cleffa | 56.4% | 1.54% | -0.6% | 65.0% | 7.5% | 3.31 | 1.66 | 4.12 |
| Life Dew | 56.4% | 1.57% | -0.6% | 64.9% | 5.0% | 3.08 | 1.52 | 4.28 |
| Lillie's Poké Doll | 55.8% | 1.48% | -1.2% | 65.2% | 6.2% | 3.08 | 1.55 | 3.92 |
| Mime Jr. | 55.1% | 1.52% | -1.9% | 63.1% | 0.0% | 3.62 | 1.80 | 4.59 |
| Manaphy | 55.0% | 1.44% | -2.0% | 63.7% | 7.5% | 3.06 | 1.52 | 4.57 |
| Cursed Shovel | 55.0% | 1.43% | -2.0% | 64.5% | 11.2% | 3.30 | 1.70 | 4.44 |
| Slumbering Forest | 54.3% | 1.58% | -2.7% | 63.0% | 15.0% | 3.32 | 1.67 | 4.35 |
| Team Rocket's Handiwork | 52.0% | 1.59% | -5.0% | 60.9% | 7.5% | 3.37 | 1.67 | 4.33 |
| Robo Substitute Team Flare Gear | 51.7% | 1.49% | -5.3% | 62.2% | 7.5% | 3.05 | 1.59 | 3.99 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 57.7% | 0.50% | +0.0% | 65.7% | 11.2% | 2.81 | 1.40 | 4.35 |
| Rescue Carrier | 58.2% | 0.50% | +0.5% | 66.1% | 9.8% | 3.34 | 1.66 | 4.38 |
| Field Blower | 57.9% | 0.49% | +0.3% | 65.9% | 12.5% | 3.28 | 1.65 | 4.33 |
| Sableye | 57.7% | 0.49% | -0.0% | 65.6% | 9.4% | 3.17 | 1.57 | 4.39 |
| Nincada | 57.7% | 0.50% | -0.0% | 66.0% | 12.5% | 3.21 | 1.60 | 4.35 |
| Snorlax Doll | 57.6% | 0.50% | -0.1% | 65.4% | 11.9% | 3.24 | 1.61 | 4.36 |
| Puzzle of Time | 56.5% | 0.49% | -1.2% | 64.9% | 9.8% | 3.32 | 1.67 | 4.30 |
| VS Seeker | 56.1% | 0.49% | -1.6% | 64.4% | 8.0% | 3.32 | 1.66 | 4.37 |

The confirm cuts one Rescue Carrier for copy 2. Weighted 58.2% vs 57.7% (+0.5%; SE 0.50% on the swap and 0.50% on the baseline, so the gap's SE is about 0.70%, 0.7 SE). Sleepy Voice flips 3.96 times a game and lands heads 1.96 times, on the Sisters weights.

| Foe | Baseline | Rescue Carrier | Field Blower | Sableye | Nincada | Snorlax Doll | Puzzle of Time | VS Seeker |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 85.2% | 87.6% | 88.4% | 87.5% | 87.8% | 87.6% | 88.2% | 86.1% |
| Hedrick Worlds Dragapult | 67.5% | 71.0% | 70.0% | 72.9% | 73.0% | 66.6% | 71.9% | 69.1% |
| Unlimited Dragapult | 94.8% | 95.8% | 93.2% | 94.4% | 93.6% | 93.1% | 94.4% | 93.1% |
| Cornerstone Ogerpon (D60) | 23.6% | 26.2% | 23.8% | 21.9% | 24.0% | 23.9% | 20.5% | 18.8% |
| Wo-Chien / Floragato (S60) | 68.9% | 67.8% | 70.5% | 66.3% | 70.0% | 65.9% | 65.0% | 64.9% |
| Gholdengo (G) | 61.4% | 61.5% | 61.1% | 60.9% | 56.5% | 60.4% | 57.8% | 55.5% |
| Clefairy / Mewtwo (C60) | 84.5% | 85.6% | 85.8% | 85.4% | 84.4% | 83.0% | 82.5% | 84.6% |
| Set M (Mew ex) | 55.9% | 58.0% | 56.5% | 58.5% | 57.4% | 58.0% | 58.1% | 59.5% |
| Mega Starmie ex (Kudo) | 42.8% | 38.5% | 39.4% | 41.4% | 40.0% | 42.2% | 39.1% | 39.9% |
| Lucario Hariyama | 90.9% | 90.5% | 90.8% | 90.2% | 90.6% | 90.8% | 91.9% | 90.4% |
| Iron Thorns ex | 94.4% | 95.6% | 93.8% | 94.1% | 96.5% | 96.2% | 95.8% | 96.0% |
| Carpet Set H | 11.2% | 9.8% | 12.5% | 9.4% | 12.5% | 11.9% | 9.8% | 8.0% |
| Ambipom Hand Fling | 72.6% | 70.9% | 70.8% | 70.5% | 71.5% | 70.5% | 68.6% | 71.4% |

## Copy 3

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 58.3% | 1.56% | +0.0% | 66.2% | 8.8% | 3.46 | 1.69 | 4.48 |
| Nincada | 60.7% | 1.54% | +2.4% | 67.5% | 10.0% | 3.37 | 1.73 | 4.50 |
| Field Blower | 60.6% | 1.55% | +2.3% | 67.6% | 11.2% | 3.55 | 1.77 | 4.48 |
| Battle Cage | 59.9% | 1.57% | +1.6% | 67.9% | 10.0% | 3.53 | 1.71 | 4.43 |
| Crushing Hammer | 59.5% | 1.48% | +1.1% | 67.6% | 5.0% | 3.60 | 1.72 | 4.46 |
| Buddy-Buddy Poffin | 59.2% | 1.55% | +0.9% | 66.1% | 6.2% | 3.56 | 1.75 | 4.51 |
| Switch | 59.1% | 1.55% | +0.7% | 66.9% | 11.2% | 3.42 | 1.73 | 4.41 |
| Sableye | 58.8% | 1.51% | +0.4% | 66.2% | 3.8% | 3.55 | 1.75 | 4.57 |
| Smoochum | 58.5% | 1.48% | +0.2% | 66.9% | 10.0% | 3.87 | 1.93 | 4.47 |
| Manaphy | 58.3% | 1.54% | -0.0% | 65.6% | 12.5% | 3.38 | 1.67 | 4.62 |
| Level Ball | 58.3% | 1.53% | -0.1% | 64.8% | 11.2% | 3.37 | 1.58 | 4.43 |
| Puzzle of Time | 57.7% | 1.60% | -0.6% | 65.9% | 15.0% | 3.53 | 1.80 | 4.30 |
| Cleffa | 57.5% | 1.56% | -0.9% | 65.2% | 10.0% | 3.70 | 1.87 | 4.20 |
| Rescue Carrier | 57.4% | 1.56% | -0.9% | 65.6% | 7.5% | 3.49 | 1.72 | 4.37 |
| Robo Substitute Team Flare Gear | 57.4% | 1.55% | -0.9% | 65.7% | 11.2% | 3.16 | 1.57 | 4.12 |
| Team Rocket's Petrel | 57.1% | 1.54% | -1.2% | 64.6% | 6.2% | 3.51 | 1.81 | 4.27 |
| Lillie's Poké Doll | 56.9% | 1.48% | -1.4% | 64.9% | 10.0% | 3.45 | 1.73 | 4.12 |
| Cursed Shovel | 56.8% | 1.55% | -1.5% | 65.0% | 6.2% | 3.51 | 1.67 | 4.32 |
| Shedinja | 56.7% | 1.58% | -1.6% | 65.0% | 6.2% | 3.48 | 1.76 | 4.31 |
| Team Rocket's Handiwork | 56.7% | 1.56% | -1.7% | 65.3% | 11.2% | 3.66 | 1.84 | 4.52 |
| Arven | 56.6% | 1.55% | -1.8% | 65.2% | 17.5% | 3.44 | 1.71 | 4.18 |
| Slumbering Forest | 56.3% | 1.56% | -2.0% | 64.3% | 8.8% | 3.63 | 1.75 | 4.39 |
| VS Seeker | 55.9% | 1.53% | -2.5% | 64.5% | 8.8% | 3.53 | 1.80 | 4.36 |
| Snorlax Doll | 55.7% | 1.55% | -2.6% | 64.3% | 11.2% | 3.42 | 1.73 | 4.35 |
| Darkness Energy | 55.7% | 1.52% | -2.6% | 64.8% | 2.5% | 3.73 | 1.86 | 4.29 |
| Lillie's Determination | 55.6% | 1.60% | -2.7% | 64.1% | 7.5% | 3.57 | 1.79 | 4.29 |
| Mime Jr. | 54.7% | 1.50% | -3.7% | 62.8% | 13.8% | 3.77 | 1.84 | 4.53 |
| Life Dew | 54.1% | 1.48% | -4.2% | 63.3% | 8.8% | 3.58 | 1.79 | 4.38 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 58.2% | 0.50% | +0.0% | 66.1% | 9.8% | 3.34 | 1.66 | 4.38 |
| Battle Cage | 59.6% | 0.50% | +1.4% | 67.1% | 10.4% | 3.49 | 1.73 | 4.40 |
| Field Blower | 59.1% | 0.49% | +0.9% | 66.9% | 10.8% | 3.56 | 1.79 | 4.41 |
| Sableye | 59.0% | 0.49% | +0.8% | 66.7% | 10.5% | 3.41 | 1.70 | 4.44 |
| Switch | 58.9% | 0.49% | +0.7% | 66.6% | 10.0% | 3.53 | 1.77 | 4.42 |
| Crushing Hammer | 58.4% | 0.49% | +0.2% | 66.2% | 9.0% | 3.55 | 1.76 | 4.41 |
| Nincada | 58.3% | 0.49% | +0.1% | 66.7% | 12.0% | 3.48 | 1.75 | 4.44 |
| Buddy-Buddy Poffin | 57.9% | 0.50% | -0.3% | 65.5% | 9.1% | 3.48 | 1.72 | 4.49 |

The confirm cuts one Battle Cage for copy 3. Weighted 59.6% vs 58.2% (+1.4%; SE 0.50% on the swap and 0.50% on the baseline, so the gap's SE is about 0.70%, 2.0 SE). Sleepy Voice flips 4.14 times a game and lands heads 2.06 times, on the Sisters weights.

| Foe | Baseline | Battle Cage | Field Blower | Sableye | Switch | Crushing Hammer | Nincada | Buddy-Buddy Poffin |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 87.6% | 88.8% | 89.2% | 91.0% | 87.9% | 89.0% | 90.9% | 86.9% |
| Hedrick Worlds Dragapult | 71.0% | 69.5% | 72.1% | 70.1% | 73.6% | 71.1% | 72.8% | 69.6% |
| Unlimited Dragapult | 95.8% | 92.9% | 93.6% | 92.9% | 95.6% | 93.0% | 94.1% | 93.0% |
| Cornerstone Ogerpon (D60) | 26.2% | 27.6% | 22.6% | 22.4% | 22.6% | 23.5% | 23.2% | 24.8% |
| Wo-Chien / Floragato (S60) | 67.8% | 69.0% | 72.4% | 70.2% | 65.4% | 67.6% | 69.4% | 69.2% |
| Gholdengo (G) | 61.5% | 61.7% | 60.1% | 61.4% | 63.2% | 58.0% | 60.6% | 59.5% |
| Clefairy / Mewtwo (C60) | 85.6% | 83.2% | 85.5% | 84.9% | 84.5% | 83.5% | 86.0% | 83.6% |
| Set M (Mew ex) | 58.0% | 61.9% | 60.0% | 61.4% | 63.7% | 63.5% | 56.2% | 59.2% |
| Mega Starmie ex (Kudo) | 38.5% | 45.4% | 46.4% | 45.2% | 40.6% | 43.9% | 41.8% | 41.6% |
| Lucario Hariyama | 90.5% | 93.0% | 90.6% | 90.9% | 92.8% | 91.4% | 90.8% | 90.5% |
| Iron Thorns ex | 95.6% | 95.5% | 95.2% | 95.0% | 94.8% | 93.6% | 95.9% | 95.2% |
| Carpet Set H | 9.8% | 10.4% | 10.8% | 10.5% | 10.0% | 9.0% | 12.0% | 9.1% |
| Ambipom Hand Fling | 70.9% | 73.9% | 71.2% | 71.4% | 70.6% | 73.2% | 74.0% | 69.5% |

## Copy 4

### Screen

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 59.9% | 1.57% | +0.0% | 67.9% | 10.0% | 3.53 | 1.71 | 4.43 |
| Rescue Carrier | 61.8% | 1.56% | +1.9% | 68.8% | 13.8% | 3.79 | 1.92 | 4.53 |
| Lillie's Determination | 60.4% | 1.55% | +0.5% | 67.8% | 12.5% | 3.51 | 1.77 | 4.36 |
| Snorlax Doll | 59.9% | 1.58% | -0.0% | 66.8% | 8.8% | 3.55 | 1.75 | 4.44 |
| Smoochum | 59.2% | 1.55% | -0.8% | 67.0% | 10.0% | 4.10 | 2.04 | 4.66 |
| Team Rocket's Petrel | 59.1% | 1.60% | -0.8% | 65.7% | 11.2% | 3.48 | 1.72 | 4.15 |
| Battle Cage | 59.0% | 1.60% | -1.0% | 66.3% | 12.5% | 3.69 | 1.88 | 4.51 |
| Puzzle of Time | 58.6% | 1.54% | -1.3% | 67.3% | 13.8% | 3.55 | 1.77 | 4.43 |
| Switch | 58.5% | 1.59% | -1.4% | 66.7% | 6.2% | 3.50 | 1.79 | 4.29 |
| Slumbering Forest | 58.5% | 1.49% | -1.4% | 66.8% | 8.8% | 3.58 | 1.73 | 4.46 |
| Field Blower | 58.5% | 1.57% | -1.5% | 64.8% | 11.2% | 3.63 | 1.82 | 4.47 |
| Sableye | 58.3% | 1.48% | -1.6% | 66.5% | 10.0% | 3.59 | 1.75 | 4.56 |
| Crushing Hammer | 58.3% | 1.57% | -1.6% | 65.9% | 8.8% | 3.72 | 1.84 | 4.46 |
| Cursed Shovel | 58.2% | 1.52% | -1.8% | 66.0% | 8.8% | 3.50 | 1.78 | 4.29 |
| VS Seeker | 57.9% | 1.56% | -2.0% | 65.3% | 5.0% | 3.61 | 1.79 | 4.47 |
| Shedinja | 57.8% | 1.55% | -2.1% | 65.7% | 7.5% | 3.66 | 1.78 | 4.33 |
| Arven | 57.8% | 1.60% | -2.1% | 64.8% | 7.5% | 3.57 | 1.76 | 4.26 |
| Darkness Energy | 57.4% | 1.59% | -2.5% | 65.5% | 3.8% | 3.68 | 1.87 | 4.25 |
| Level Ball | 56.8% | 1.56% | -3.2% | 65.4% | 13.8% | 3.48 | 1.74 | 4.37 |
| Cleffa | 56.2% | 1.50% | -3.8% | 64.8% | 12.5% | 3.68 | 1.90 | 4.20 |
| Lillie's Poké Doll | 56.1% | 1.58% | -3.8% | 64.5% | 10.0% | 3.40 | 1.67 | 4.04 |
| Buddy-Buddy Poffin | 56.1% | 1.56% | -3.9% | 63.7% | 6.2% | 3.71 | 1.86 | 4.57 |
| Life Dew | 55.8% | 1.61% | -4.1% | 64.2% | 7.5% | 3.58 | 1.76 | 4.42 |
| Nincada | 55.6% | 1.54% | -4.3% | 64.1% | 11.2% | 3.54 | 1.76 | 4.39 |
| Mime Jr. | 55.6% | 1.59% | -4.3% | 63.0% | 12.5% | 3.98 | 2.00 | 4.68 |
| Robo Substitute Team Flare Gear | 55.0% | 1.58% | -4.9% | 64.2% | 13.8% | 3.36 | 1.68 | 3.96 |
| Team Rocket's Handiwork | 54.9% | 1.56% | -5.1% | 62.8% | 7.5% | 3.77 | 1.91 | 4.47 |
| Manaphy | 54.5% | 1.53% | -5.4% | 62.7% | 5.0% | 3.56 | 1.79 | 4.65 |

### Confirm

| Cut | Weighted | SE | vs baseline | Mean | Worst | Flips | Heads | Doll plays |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| — baseline — | 59.6% | 0.50% | +0.0% | 67.1% | 10.4% | 3.49 | 1.73 | 4.40 |
| Smoochum | 59.7% | 0.49% | +0.0% | 67.0% | 11.9% | 3.97 | 1.98 | 4.60 |
| Rescue Carrier | 59.0% | 0.49% | -0.6% | 66.6% | 10.4% | 3.68 | 1.82 | 4.44 |
| Snorlax Doll | 58.7% | 0.49% | -0.9% | 66.4% | 12.0% | 3.58 | 1.79 | 4.44 |
| Battle Cage | 58.7% | 0.50% | -1.0% | 65.9% | 11.6% | 3.59 | 1.80 | 4.39 |
| Team Rocket's Petrel | 58.2% | 0.50% | -1.5% | 65.6% | 9.1% | 3.46 | 1.73 | 4.22 |
| Lillie's Determination | 57.3% | 0.49% | -2.3% | 65.2% | 9.6% | 3.51 | 1.75 | 4.25 |

The confirm cuts one Smoochum for copy 4. Weighted 59.7% vs 59.6% (+0.0%; SE 0.49% on the swap and 0.50% on the baseline, so the gap's SE is about 0.70%, 0.1 SE). Sleepy Voice flips 4.60 times a game and lands heads 2.29 times, on the Sisters weights.

| Foe | Baseline | Smoochum | Rescue Carrier | Snorlax Doll | Battle Cage | Team Rocket's Petrel | Lillie's Determination |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 88.8% | 88.1% | 89.4% | 89.2% | 83.7% | 87.9% | 85.2% |
| Hedrick Worlds Dragapult | 69.5% | 68.6% | 69.6% | 68.1% | 69.1% | 67.0% | 69.5% |
| Unlimited Dragapult | 92.9% | 93.4% | 92.9% | 94.4% | 89.9% | 92.1% | 92.0% |
| Cornerstone Ogerpon (D60) | 27.6% | 24.9% | 23.6% | 25.6% | 26.5% | 26.1% | 22.5% |
| Wo-Chien / Floragato (S60) | 69.0% | 72.1% | 66.9% | 69.2% | 70.4% | 68.6% | 69.1% |
| Gholdengo (G) | 61.7% | 63.6% | 62.7% | 58.4% | 58.9% | 59.9% | 59.9% |
| Clefairy / Mewtwo (C60) | 83.2% | 85.2% | 84.7% | 87.0% | 85.4% | 84.9% | 82.9% |
| Set M (Mew ex) | 61.9% | 62.9% | 60.2% | 59.0% | 61.3% | 58.4% | 59.4% |
| Mega Starmie ex (Kudo) | 45.4% | 42.1% | 45.5% | 41.8% | 40.6% | 42.4% | 39.8% |
| Lucario Hariyama | 93.0% | 92.5% | 92.9% | 92.8% | 92.6% | 91.8% | 90.0% |
| Iron Thorns ex | 95.5% | 94.5% | 95.8% | 95.6% | 95.9% | 95.5% | 95.5% |
| Carpet Set H | 10.4% | 11.9% | 10.4% | 12.0% | 11.6% | 9.1% | 9.6% |
| Ambipom Hand Fling | 73.9% | 71.4% | 71.5% | 70.0% | 70.5% | 69.8% | 72.8% |
