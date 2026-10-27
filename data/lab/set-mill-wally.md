# Mill Wally lock

Crispin searches for up to two Basic Energy cards of different types, puts one into the hand, and attaches the other. This 60 has only Water as a Basic Energy, so Crispin put that Water into the hand and did not attach it. Traces showed the Water landing on Wiglett while Wugtrio was still in the deck.

Wally's printed text searches the deck for a card that evolves from a Pokémon in play and puts it onto that Pokémon. It can be used on the first turn and on a Pokémon that was played this turn. Three Wally replace three Crispin. The same run also aims Level Ball at Wugtrio once a Wiglett is in play. That search change is in both rows. The gap below is the three Wally.

- **Seed**: `20261026`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Elapsed**: 296.7s
- **Source**: `data/lab/set-mill-wally.json`

The ± column is one standard error of that list's weighted rate. Delta is against the Crispin 60 measured in this same run.

| List | Weighted | ± | Mean | Worst | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Wally ×3 | 39.415% | 0.463% | 55.221% | 7.38% D60 | +1.404% |
| Crispin ×3 | 38.011% | 0.453% | 53.885% | 7.25% D60 | — |

Gap +1.404 points, difference ±0.647, 2.17 standard errors. Mean mill effects per game 2.965 → 3.166. The count rose against every foe.

| Foe | Weight | Crispin | Wally | Delta | Crispin mill | Wally mill |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| t60 | 4.0% | 72.9% | 75.1% | +2.2% | 3.31 | 3.39 |
| hedrick | 5.1% | 56.0% | 60.8% | +4.7% | 2.63 | 2.95 |
| unl | 2.2% | 82.0% | 85.0% | +3.0% | 3.44 | 3.58 |
| d60 | 14.5% | 7.3% | 7.4% | +0.1% | 2.36 | 2.67 |
| s60 | 7.0% | 70.0% | 66.5% | -3.5% | 4.15 | 4.30 |
| g | 11.7% | 27.2% | 29.2% | +2.0% | 2.56 | 2.87 |
| c60 | 12.4% | 30.0% | 32.0% | +2.0% | 1.84 | 2.06 |
| m | 14.5% | 15.0% | 17.2% | +2.2% | 1.56 | 1.71 |
| starmie | 10.6% | 28.7% | 31.1% | +2.4% | 2.42 | 2.60 |
| lucario | 5.1% | 79.8% | 80.9% | +1.1% | 2.57 | 2.67 |
| thorns | 4.1% | 92.2% | 90.0% | -2.2% | 3.44 | 3.58 |
| h | 7.6% | 45.1% | 47.8% | +2.6% | 3.80 | 4.04 |
| g30 | 1.1% | 94.2% | 94.9% | +0.6% | 4.45 | 4.75 |

`SET_MILL_NAMES` is this Wally 60.

A 160-game screen of three Great Ball in place of Crispin was 40.19% against a 38.64% Crispin row (+1.56 points, 1.52 SE). The registered Great Ball sentence is "Search your deck for a Pokémon." The printed Great Ball flips a coin and searches for a Basic. That row was not confirmed.

Broken Time-Space was played about 0.4 times a game and did not add evolutions. Opening Wiglett stay on `played_turn` 0, so the stadium does not evolve them.
