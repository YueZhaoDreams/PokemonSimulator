# Mill sleep wall vs Sisters 60

Locked 2026-10-22. This file is that measurement. `SET_MILL_NAMES` later replaced this list's one Switch with one Lillie's Poké Doll (2026-10-24). Rabsca 1-1 and Battle Cage stay outside the lock.

- **Seed**: `20261022`
- **Games per seat**: 250
- **Seats**: each Mill list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: loss-weighted from the Sisters 60, frozen. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 108.9s

Printed Playground lets each player bench as many Basic Pokémon as they like, user first, then Pichu is Asleep. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Sleepy Lost puts the top card of the opponent's deck into the Lost Zone, then Mime Jr. is Asleep. Energy Antics moves an Energy from one of the opponent's Pokémon to another of theirs, then Smoochum is Asleep. Slumbering Forest makes an Asleep Pokémon flip 2 coins between turns and stay Asleep unless both are heads. Manaphy Wave Veil prevents damage done to the bench by attacks.

## Win-rate array

| Foe | Sisters A | Sisters B | Sisters | Sleep A | Sleep B | Sleep | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 71.2% | 76.0% | 73.6% | 73.6% | 65.6% | 69.6% | -4.0% |
| Hedrick Worlds Dragapult | 67.2% | 65.6% | 66.4% | 57.6% | 62.0% | 59.8% | -6.6% |
| Unlimited Dragapult | 84.4% | 86.8% | 85.6% | 82.4% | 87.2% | 84.8% | -0.8% |
| Cornerstone Ogerpon (D60) | 6.0% | 4.0% | 5.0% | 5.6% | 6.0% | 5.8% | +0.8% |
| Wo-Chien / Floragato (S60) | 52.8% | 55.6% | 54.2% | 65.6% | 63.6% | 64.6% | +10.4% |
| Gholdengo (G) | 27.6% | 19.2% | 23.4% | 25.6% | 24.0% | 24.8% | +1.4% |
| Clefairy / Mewtwo (C60) | 16.8% | 20.0% | 18.4% | 28.0% | 31.6% | 29.8% | +11.4% |
| Set M (Mew ex) | 3.2% | 6.4% | 4.8% | 12.8% | 12.0% | 12.4% | +7.6% |
| Mega Starmie ex (Kudo) | 28.8% | 31.6% | 30.2% | 30.4% | 28.8% | 29.6% | -0.6% |
| Lucario Hariyama | 68.8% | 64.0% | 66.4% | 78.0% | 81.2% | 79.6% | +13.2% |
| Iron Thorns ex | 71.2% | 74.4% | 72.8% | 90.0% | 92.4% | 91.2% | +18.4% |
| Carpet Set H | 48.4% | 51.6% | 50.0% | 46.4% | 46.4% | 46.4% | -3.6% |
| Ambipom Hand Fling | 93.6% | 92.0% | 92.8% | 96.0% | 94.8% | 95.4% | +2.6% |
| Mean |  |  | 49.5% |  |  | 53.4% | +3.9% |
| Weighted |  |  | 32.9% |  |  | 37.0% | +4.1% |
| Worst |  |  | 4.8% |  |  | 5.8% | +1.0% |

## Head to head

Sleep wall win rate vs Sisters 60: 44.6% (as A 48.0%, as B 41.2%).

## Package use on the sleep wall

Means are per game across the measured foes and both seats. Pichu, Mime Jr., Smoochum, Manaphy, and Slumbering Forest rows are the share of games in which that card entered play. Manaphy is not in this Mill list; a hit there is the opponent's Manaphy.

| Event | Per game |
| :--- | ---: |
| Playground | 1.63 |
| Sweet Sleeping Face blocks | 9.52 |
| Cards milled by an attack or Handiwork | 2.90 |
| Undersea Tunnel attacks | 2.76 |
| Sleepy Lost | 0.57 |
| Energy Antics | 0.00 |
| Slumbering Forest sleep checks | 1.05 |
| Pichu saw play | 51.1% |
| Mime Jr. saw play | 37.2% |
| Smoochum saw play | 0.0% |
| Manaphy saw play | 5.4% |
| Slumbering Forest entered play | 46.5% |

## Lists

Sisters 60 is frozen in `SISTERS_60`. Sleep wall is `build_mill_deck()`.

| Card | Sisters | Sleep |
| :--- | ---: | ---: |
| Boss's Orders | 1 | 1 |
| Buddy-Buddy Poffin | 4 | 4 |
| Colress's Tenacity | 4 | 4 |
| Counter Catcher | 2 | 2 |
| Crispin | 3 | 3 |
| Crushing Hammer | 4 | 4 |
| Double Turbo Energy | 4 | 4 |
| Fighting Energy | 2 | 0 |
| Ignition Energy | 4 | 4 |
| Level Ball | 3 | 3 |
| Mime Jr. | 0 | 1 |
| Miss Fortune Sisters | 2 | 2 |
| Nest Ball | 3 | 3 |
| Neutralization Zone | 1 | 1 |
| Pichu | 0 | 1 |
| Rescue Carrier | 4 | 3 |
| Reversal Energy | 4 | 4 |
| Slumbering Forest | 0 | 1 |
| Switch | 0 | 1 |
| Team Rocket's Handiwork | 2 | 2 |
| Victini | 1 | 1 |
| Water Energy | 4 | 3 |
| Wiglett | 4 | 4 |
| Wugtrio | 4 | 4 |

## Decision

Locked. Sleep wall mean 53.4% vs Sisters 49.5% (+3.9%). Weighted 32.9% → 37.0% (+4.1%). Head to head sleep wall 44.6%.

Rabsca 1-1 stays out. The C60 bench-shield bakeoff (seed 20260911, 3000 games) put that line at 51.4–52.5% vs T60 against a 51.3% base. One Battle Cage on that same bakeoff was 62.0% vs T60. Battle Cage stays out of this Mill lock because it replaces Neutralization Zone, and this 60 was not remeasured with that swap.
