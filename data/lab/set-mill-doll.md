# Mill no-Prize dolls

Items played as a Pokémon. A Knock Out awards no Prize. Each greedy step screens every legal cut, confirms the best cut of each card, and keeps the confirm with the higher loss-weighted win rate.

- **Seed**: `20261023`
- **Screen games per seat**: 40
- **Confirm games per seat**: 120
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Elapsed**: 2065.5s

## Cards

Kept: the printed sentence awards no Prize.

| Card | HP | Play | When it leaves |
| :--- | ---: | :--- | :--- |
| Lillie's Poké Doll | 30 | during the turn | Active: discard attached cards, put it on the bottom of the deck |
| Robo Substitute | 30 | during the turn | discard from play |
| Snorlax Doll | 120 | setup only | discard from play; immune to Special Conditions |
| Clefairy Doll | 10 | during the turn | discard; Asleep, Confused, Paralyzed, and Poisoned do not apply |
| Mysterious Fossil | 50 | during the turn | discard; immune to Special Conditions |
| Root Fossil | 40 | during the turn | discard; immune to Special Conditions |
| Claw Fossil | 40 | during the turn | discard; immune to Special Conditions |

Left out, because a Knock Out still awards a Prize: Unidentified Fossil, Rare Fossil, the Antique fossils, and Helix Fossil, Dome Fossil, Old Amber, Armor Fossil, and Skull Fossil from Diamond & Pearl and Platinum. The XY fossils that look at the bottom 7 cards are not played as Pokémon. A lower-HP reprint of the same name, such as Mysterious Fossil at 10 HP, does not raise the four-copy cap.

## Greedy path

| Step | Add | Cut | Weighted | Mean | Worst | Doll plays | Holds | Tucks | No-Prize KOs | Mill attacks |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | — | — | 37.9% | 53.9% | 9.2% | 0.00 | 0.00 | 0.00 | 0.00 | 2.87 |
| step 1 | Lillie's Poké Doll | Buddy-Buddy Poffin | 39.7% | 55.4% | 7.1% | 0.22 | 0.20 | 0.03 | 0.12 | 2.95 |

## Decision

Best confirmed list is step 1: weighted 39.7% vs the locked Mill at 37.9% (+1.8%). Mean 55.4% (+1.5%). SET_MILL_NAMES stays the sleep-wall 60. The worst foe on this swap is still Cornerstone Ogerpon.

Counts on that list:

- Lillie's Poké Doll: 1
- Robo Substitute: 0
- Snorlax Doll: 0
- Mysterious Fossil: 0
- Root Fossil: 0
- Claw Fossil: 0
- Clefairy Doll: 0

## Step 1 confirms

Screen leader +Mysterious Fossil −Colress's Tenacity at 40.4%. The list entering this step screened at 37.5%. Each row is that card's best cut, confirmed at 120 games per seat.

| Card | Cut | Screen | Confirmed | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mysterious Fossil | Colress's Tenacity | 40.4% | 37.4% | 53.5% | 4.2% | -0.5% | 0.22 | 0.11 | 0.18 | 0.12 | 2.84 |
| Snorlax Doll | Nest Ball | 40.2% | 39.5% | 55.4% | 8.8% | +1.6% | 0.00 | 0.05 | 0.13 | 0.05 | 2.91 |
| Root Fossil | Colress's Tenacity | 39.9% | 37.8% | 53.6% | 5.0% | -0.1% | 0.23 | 0.11 | 0.20 | 0.13 | 2.84 |
| Claw Fossil | Colress's Tenacity | 39.9% | 37.8% | 53.6% | 5.0% | -0.1% | 0.23 | 0.11 | 0.20 | 0.13 | 2.84 |
| Robo Substitute | Colress's Tenacity | 39.9% | 37.0% | 53.1% | 6.2% | -0.9% | 0.22 | 0.10 | 0.20 | 0.12 | 2.85 |
| Lillie's Poké Doll | Buddy-Buddy Poffin | 39.7% | 39.7% | 55.4% | 7.1% | +1.8% | 0.22 | 0.10 | 0.20 | 0.12 | 2.95 |
| Clefairy Doll | Miss Fortune Sisters | 39.4% | 37.8% | 54.1% | 6.2% | -0.1% | 0.23 | 0.09 | 0.18 | 0.13 | 2.92 |

Kept +Lillie's Poké Doll −Buddy-Buddy Poffin at 39.7% (+1.8%).

## Step 2 confirms

Screen leader +Mysterious Fossil −Crushing Hammer at 41.6%. The list entering this step screened at 39.7%. Each row is that card's best cut, confirmed at 120 games per seat.

| Card | Cut | Screen | Confirmed | Mean | Worst | Delta | Plays | Stalls | Holds | No-Prize KOs | Mill attacks |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mysterious Fossil | Crushing Hammer | 41.6% | 39.5% | 54.8% | 7.5% | -0.2% | 0.42 | 0.20 | 0.35 | 0.24 | 2.90 |
| Lillie's Poké Doll | Switch | 40.7% | 39.5% | 54.9% | 5.8% | -0.2% | 0.40 | 0.20 | 0.36 | 0.23 | 2.96 |
| Snorlax Doll | Counter Catcher | 40.3% | 37.5% | 52.7% | 7.5% | -2.2% | 0.23 | 0.16 | 0.35 | 0.19 | 2.91 |
| Clefairy Doll | Miss Fortune Sisters | 40.0% | 38.6% | 54.2% | 5.0% | -1.0% | 0.43 | 0.19 | 0.39 | 0.26 | 2.97 |
| Robo Substitute | Crispin | 39.8% | 38.3% | 54.6% | 7.5% | -1.3% | 0.43 | 0.20 | 0.37 | 0.25 | 2.92 |
| Root Fossil | Crushing Hammer | 39.6% | 37.8% | 53.1% | 5.8% | -1.9% | 0.41 | 0.19 | 0.36 | 0.23 | 2.85 |
| Claw Fossil | Crushing Hammer | 39.6% | 37.8% | 53.1% | 5.8% | -1.9% | 0.41 | 0.19 | 0.36 | 0.23 | 2.85 |

No confirm in this step was higher than the list already kept. The search stopped.

## Foes at the best list

| Foe | A | B | Mean | Delta vs lock |
| :--- | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 75.8% | 70.8% | 73.3% | +3.3% |
| Hedrick Worlds Dragapult | 52.5% | 56.7% | 54.6% | -1.7% |
| Unlimited Dragapult | 83.3% | 89.2% | 86.2% | +2.5% |
| Cornerstone Ogerpon (D60) | 6.7% | 7.5% | 7.1% | -2.1% |
| Wo-Chien / Floragato (S60) | 68.3% | 81.7% | 75.0% | +8.7% |
| Gholdengo (G) | 25.8% | 25.8% | 25.8% | +0.8% |
| Clefairy / Mewtwo (C60) | 24.2% | 35.0% | 29.6% | +3.7% |
| Set M (Mew ex) | 15.8% | 24.2% | 20.0% | +5.0% |
| Mega Starmie ex (Kudo) | 31.7% | 35.8% | 33.8% | +0.0% |
| Lucario Hariyama | 80.0% | 86.7% | 83.3% | +2.5% |
| Iron Thorns ex | 93.3% | 91.7% | 92.5% | +0.4% |
| Carpet Set H | 48.3% | 43.3% | 45.8% | -0.4% |
| Ambipom Hand Fling | 94.2% | 93.3% | 93.8% | -2.9% |
