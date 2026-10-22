# Mill sleep wall vs Sisters 60

- **Seed**: `20261022`
- **Games per seat**: 250
- **Seats**: each Mill list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: loss-weighted from the Sisters 60, frozen. Harder Sisters matchups count more.
- **Weights**: t60 4.4%, hedrick 6.9%, unl 3.1%, d60 16.4%, s60 8.2%, g 14.1%, m 16.0%, starmie 11.1%, lucario 5.5%, thorns 4.4%, h 8.4%, g30 1.4%
- **Elapsed**: 150.8s

Printed Playground lets each player bench as many Basic Pokémon as they like, user first, then Pichu is Asleep. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Sleepy Lost puts the top card of the opponent's deck into the Lost Zone, then Mime Jr. is Asleep. Energy Antics moves an Energy from one of the opponent's Pokémon to another of theirs, then Smoochum is Asleep. Slumbering Forest makes an Asleep Pokémon flip 2 coins between turns and stay Asleep unless both are heads. Manaphy Wave Veil prevents damage done to the bench by attacks.

## Win-rate array

| Foe | Sisters A | Sisters B | Sisters | Sleep A | Sleep B | Sleep | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 70.4% | 78.4% | 74.4% | 30.8% | 30.8% | 30.8% | -43.6% |
| Hedrick Worlds Dragapult | 62.4% | 56.4% | 59.4% | 37.2% | 46.4% | 41.8% | -17.6% |
| Unlimited Dragapult | 82.0% | 82.0% | 82.0% | 52.4% | 52.8% | 52.6% | -29.4% |
| Cornerstone Ogerpon (D60) | 4.0% | 3.2% | 3.6% | 1.2% | 2.4% | 1.8% | -1.8% |
| Wo-Chien / Floragato (S60) | 49.2% | 54.4% | 51.8% | 66.8% | 65.6% | 66.2% | +14.4% |
| Gholdengo (G) | 14.8% | 19.2% | 17.0% | 15.6% | 21.2% | 18.4% | +1.4% |
| Set M (Mew ex) | 6.0% | 6.0% | 6.0% | 20.8% | 20.4% | 20.6% | +14.6% |
| Mega Starmie ex (Kudo) | 34.4% | 35.6% | 35.0% | 10.0% | 8.4% | 9.2% | -25.8% |
| Lucario Hariyama | 68.8% | 66.4% | 67.6% | 80.8% | 76.0% | 78.4% | +10.8% |
| Iron Thorns ex | 79.2% | 69.6% | 74.4% | 93.6% | 90.4% | 92.0% | +17.6% |
| Carpet Set H | 52.0% | 49.2% | 50.6% | 25.2% | 22.4% | 23.8% | -26.8% |
| Ambipom Hand Fling | 92.4% | 90.8% | 91.6% | 81.6% | 86.4% | 84.0% | -7.6% |
| Mean |  |  | 51.1% |  |  | 43.3% | -7.8% |
| Weighted |  |  | 34.5% |  |  | 30.1% | -4.5% |
| Worst |  |  | 3.6% |  |  | 1.8% | -1.8% |

## Head to head

Sleep wall win rate vs Sisters 60: 18.0% (as A 15.2%, as B 20.8%).

## Package use on the sleep wall

Means are per game across the 12 foes and both seats. Pichu, Mime Jr., Smoochum, Manaphy, and Slumbering Forest rows are the share of games in which that card entered play.

| Event | Per game |
| :--- | ---: |
| Playground | 2.94 |
| Sweet Sleeping Face blocks | 20.81 |
| Cards milled by an attack or Handiwork | 2.23 |
| Undersea Tunnel attacks | 1.92 |
| Sleepy Lost | 0.95 |
| Energy Antics | 0.62 |
| Slumbering Forest sleep checks | 6.54 |
| Pichu saw play | 97.5% |
| Mime Jr. saw play | 82.3% |
| Smoochum saw play | 71.9% |
| Manaphy saw play | 83.2% |
| Slumbering Forest entered play | 93.8% |

## Lists

Sisters 60 is frozen in `SISTERS_60`. Sleep wall is `build_mill_deck()`.

| Card | Sisters | Sleep |
| :--- | ---: | ---: |
| Boss's Orders | 1 | 0 |
| Buddy-Buddy Poffin | 4 | 4 |
| Colress's Tenacity | 4 | 3 |
| Counter Catcher | 2 | 0 |
| Crispin | 3 | 2 |
| Crushing Hammer | 4 | 2 |
| Double Turbo Energy | 4 | 2 |
| Fighting Energy | 2 | 0 |
| Ignition Energy | 4 | 4 |
| Level Ball | 3 | 2 |
| Manaphy | 0 | 1 |
| Mime Jr. | 0 | 4 |
| Miss Fortune Sisters | 2 | 2 |
| Nest Ball | 3 | 2 |
| Neutralization Zone | 1 | 1 |
| Pichu | 0 | 4 |
| Rescue Carrier | 4 | 2 |
| Reversal Energy | 4 | 3 |
| Slumbering Forest | 0 | 4 |
| Smoochum | 0 | 4 |
| Switch | 0 | 2 |
| Team Rocket's Handiwork | 2 | 2 |
| Victini | 1 | 1 |
| Water Energy | 4 | 1 |
| Wiglett | 4 | 4 |
| Wugtrio | 4 | 4 |

## Decision

Sleep wall mean 43.3% vs Sisters 51.1% (-7.8%). Weighted 34.5% → 30.1% (-4.5%). Head to head sleep wall 18.0%.
