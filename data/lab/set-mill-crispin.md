# Mill Crispin swaps

Printed Crispin searches for up to two Basic Energy cards of different types, puts one into the hand, and attaches the other. The locked Mill has three Crispin and only Water Energy as a Basic Energy. With one type, Crispin puts that Water Energy into the hand and does not attach it. The Supporter is still used.

Wiglett's Twisting Strike costs Water. Undersea Tunnel costs three Colorless. Double Turbo, Ignition, and Reversal are already at four copies, and Crispin cannot search a Special Energy.

- **Seed**: `20261026`
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%

The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in the same run.

## Screen, 160 games per seat

Every row is one swap off the lock. Elapsed 184.6s after the later lists joined the same cache.

| List | Swap | Weighted | ± | Mean | Worst | Delta | D60 | M | G | C60 | Starmie |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| lock | Three Crispin, three Water Energy, no second Basic type. | 39.3% | 0.7% | 55.2% | 7.2% | — | 7.2% | 16.6% | 27.5% | 33.4% | 29.4% |
| water3 | Cut all three Crispin for Water Energy. | 39.1% | 0.7% | 54.8% | 5.6% | -0.2% | 5.6% | 21.2% | 25.3% | 27.8% | 30.9% |
| split3 | Keep three Crispin. Cut both Counter Catcher for Fighting Energy. | 38.8% | 0.7% | 54.6% | 5.3% | -0.5% | 5.3% | 18.1% | 27.2% | 33.1% | 28.7% |
| carrier | Cut one Crispin for a fourth Rescue Carrier. | 38.8% | 0.7% | 55.1% | 7.2% | -0.5% | 7.2% | 16.6% | 23.1% | 33.8% | 27.8% |
| split1 | Cut two Crispin for Fighting Energy. One Crispin keeps both types. | 38.8% | 0.7% | 54.3% | 8.4% | -0.5% | 8.4% | 16.9% | 26.9% | 35.3% | 28.1% |
| types | Turn one Water Energy into Fighting Energy. Three Crispin stay. | 38.7% | 0.7% | 54.5% | 10.6% | -0.6% | 10.6% | 17.8% | 22.8% | 34.7% | 25.6% |
| dce3 | Cut all three Crispin for Double Colorless Energy. | 38.7% | 0.7% | 54.3% | 9.4% | -0.6% | 9.4% | 20.6% | 25.6% | 31.6% | 30.9% |
| water2 | Cut two Crispin for Water Energy. One Crispin stays. | 38.4% | 0.7% | 54.6% | 9.1% | -0.9% | 9.1% | 14.4% | 23.8% | 28.4% | 30.0% |
| handi2 | Cut two Crispin for two Team Rocket's Handiwork. | 37.9% | 0.7% | 53.8% | 7.5% | -1.4% | 7.5% | 15.0% | 22.8% | 33.1% | 30.9% |
| handi | Cut all three Crispin for two Handiwork and one Water Energy. | 37.8% | 0.7% | 53.9% | 5.3% | -1.4% | 5.3% | 17.2% | 20.9% | 35.3% | 29.1% |
| types2 | Turn two Water Energy into Fighting Energy. One Water stays. | 37.5% | 0.7% | 53.5% | 4.7% | -1.8% | 4.7% | 16.9% | 24.7% | 31.2% | 30.3% |
| manaphy | Cut one Crispin for Manaphy. | 37.4% | 0.7% | 52.9% | 9.1% | -1.9% | 9.1% | 16.2% | 19.4% | 32.2% | 30.3% |
| sisters | Cut two Crispin for two Miss Fortune Sisters. | 37.0% | 0.7% | 53.1% | 9.1% | -2.3% | 9.1% | 15.9% | 20.9% | 28.4% | 30.3% |

Handiwork, Sisters, Manaphy, and the fourth Rescue Carrier are below the lock by more than the noise of this sample. Double Colorless Energy is not, but Carpet Set H fell 11.9% on the 160-game pass because that energy does not pay Twisting Strike.

## Confirm, 400 games per seat

The three lists still inside the screen noise. Elapsed 458.3s. Same seed.

| List | Weighted | ± | Mean | Worst | Delta | SE of the gap |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| water3 | 39.0% | 0.5% | 54.5% | 6.0% | +0.1% | 0.15 |
| lock | 38.9% | 0.5% | 55.0% | 6.1% | — | — |
| types | 38.1% | 0.5% | 54.1% | 8.0% | -0.8% | 1.31 |

Three Water Energy instead of three Crispin does not separate from the lock. Giving Crispin a second Basic type, by turning one Water into Fighting, is lower.

| Foe | Lock | Water | Delta | Types | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 73.4% | 73.4% | +0.0% | 71.2% | -2.1% |
| Hedrick Worlds Dragapult | 62.0% | 55.2% | -6.8% | 60.9% | -1.1% |
| Unlimited Dragapult | 86.6% | 83.6% | -3.0% | 85.8% | -0.9% |
| Cornerstone Ogerpon (D60) | 6.1% | 6.0% | -0.1% | 8.0% | +1.9% |
| Wo-Chien / Floragato (S60) | 67.5% | 68.8% | +1.2% | 68.6% | +1.1% |
| Gholdengo (G) | 26.9% | 26.1% | -0.8% | 23.4% | -3.5% |
| Clefairy / Mewtwo (C60) | 31.5% | 33.5% | +2.0% | 33.8% | +2.3% |
| Set M (Mew ex) | 17.5% | 20.0% | +2.5% | 15.9% | -1.6% |
| Mega Starmie ex (Kudo) | 30.1% | 29.2% | -0.9% | 26.2% | -3.9% |
| Lucario Hariyama | 80.6% | 78.4% | -2.2% | 80.4% | -0.2% |
| Iron Thorns ex | 92.8% | 90.3% | -2.5% | 90.9% | -1.9% |
| Carpet Set H | 46.5% | 49.4% | +2.9% | 44.4% | -2.1% |
| Ambipom Hand Fling | 94.0% | 94.8% | +0.8% | 93.9% | -0.1% |

Water instead of Crispin picks up about two points against Mew ex and Carpet Set H, and gives them back against Hedrick's Dragapult. The Fighting split picks up Ogerpon and gives it back against Gholdengo and Starmie. Attack counts do not move. Ogerpon stays at 2.34 mill attacks a game on the lock and 2.26 on three Water.

## How the hard games end

Shares are both seats of the 400-game confirm. Prize losses are the opponent taking all six Prize cards. Deckout wins are the opponent decking out. Board losses are Mill with no Pokémon left in play.

| Foe | List | Foe prizes | Mill deckout | Mill board loss | Mill attacks | Turns |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: |
| D60 | lock | 77.2% | 5.2% | 16.6% | 2.34 | 15.6 |
| D60 | water3 | 75.0% | 4.6% | 19.0% | 2.26 | 15.3 |
| M | lock | 58.0% | 17.5% | 24.5% | 1.63 | 15.3 |
| M | water3 | 59.2% | 20.0% | 20.5% | 1.66 | 16.3 |
| G | lock | 56.8% | 26.6% | 16.0% | 2.52 | 20.5 |
| G | water3 | 57.0% | 26.1% | 16.5% | 2.41 | 20.0 |
| C60 | lock | 41.6% | 31.4% | 26.8% | 1.87 | 18.6 |
| C60 | water3 | 40.8% | 33.4% | 25.2% | 1.92 | 18.4 |
| Starmie | lock | 17.4% | 30.1% | 52.1% | 2.44 | 14.3 |
| Starmie | water3 | 16.0% | 29.1% | 54.2% | 2.42 | 14.0 |
| H | lock | 9.5% | 40.8% | 30.8% | 3.93 | 27.4 |
| H | water3 | 8.9% | 40.1% | 30.0% | 3.87 | 26.7 |

Ogerpon and Mew end by taking the prizes, or by clearing the board, after about two mill attacks. Starmie ends by clearing the board. Carpet H is the long game, and that is where a Water search still shows up. Extra energy does not buy the missing attacks, because the Pokémon is Knocked Out before a third Undersea Tunnel.

## Decision

`SET_MILL_NAMES` stays the locked 60. Three Crispin stay.

The best swap on the long sample is three Water Energy in their place: weighted 38.9% → 39.0% (+0.10 points, 0.15 standard errors). That is not a new list. Turning one Water into Fighting so Crispin can attach is 38.1% (−0.84 points, 1.31 standard errors).

Crispin does not do the printed attach in this deck. A 25-game trace against Ogerpon played it 34 times and attached zero times. It still finds one of the three Water Energy, and Twisting Strike is the card that needs that Water. Cutting the search for a second type, for Double Colorless Energy, or for another mill Supporter spends that Water and does not slow the prize race.

A play-order trial, not kept, scored one-type Crispin behind Handiwork, Miss Fortune Sisters, and Colress's Tenacity. Same seed, 160 games per seat. Weighted 39.3% → 39.2%. Mew and Starmie rose, Wo-Chien and Unlimited Dragapult fell. The Supporter order is not where the weighted rate moves.
