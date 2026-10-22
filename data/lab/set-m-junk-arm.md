# Set M greedy Junk Arm

Junk Arm discards 2 cards from the hand, then puts a Trainer from the discard pile into the hand.
It cannot choose Junk Arm. An Item, a Tool, or a Stadium found that way is played the same turn,
and a Supporter is held. The Trainer is the one this list would play next and does not already hold:
Counter Catcher, Hero's Cape, Bursting Balloon, then the rest of that line.
The 2 discarded cards are Pokémon whose printed HP a Rescue Carrier can take back,
or any other Pokémon a Night Stretcher can take back.

Starting 60 is the locked Set M list: Set M (4 Petrel, 3 Sky Field, 4 Budew).
That list has four Team Rocket's Petrel, three Sky Field, four Budew, and zero Junk Arm.
Each step cuts exactly one copy of one other card. Weights are frozen from the
0-Junk-Arm measurement of this list on this engine.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. A copy is kept only when that score rises.
- **Weights**: t60 23.4%, hedrick 31.1%, c60 15.2%, d60 2.9%, thorns 0.3%, starmie 27.1%
- **Copies kept**: 1
- **Elapsed**: 3945s

## Path

| Junk Arm | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Poffin | Potion | Catcher | Cape | Balloon | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 90.6% | 0.5% | +0.00% | — | 93.7% | 88.3% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 91.2% | 88.3% | 94.3% | 98.9% | 99.9% | 89.8% |
| 1 | Ultra Ball | 91.9% | 0.4% | +1.25% | 0.6% | 94.6% | 90.0% | 1.1% | 0.4% | 0.1% | 0.1% | 2.8% | 92.6% | 90.2% | 96.1% | 99.1% | 99.8% | 90.0% |

## Step 1

Current weighted rate 90.6%. Accepted cut is Ultra Ball at 91.9%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Junk Arm played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Ultra Ball | 91.9% | 94.6% | 90.0% | 7.4% | 92.6% | 90.2% | 96.1% | 99.1% | 99.8% | 90.0% |
| 2 | Bursting Balloon | 91.7% | 94.3% | 89.8% | 6.3% | 92.7% | 90.5% | 94.4% | 98.6% | 99.6% | 89.8% |
| 3 | Sky Field | 91.3% | 94.1% | 89.6% | 8.5% | 92.2% | 90.2% | 93.7% | 99.0% | 99.7% | 89.6% |
| 4 | Night Stretcher | 91.1% | 94.0% | 89.1% | 4.7% | 92.1% | 89.7% | 94.0% | 99.4% | 99.7% | 89.1% |
| 5 | Manaphy | 90.5% | 93.5% | 83.2% | 4.9% | 93.2% | 92.2% | 94.0% | 99.0% | 99.6% | 83.2% |
| 6 | Team Rocket's Petrel | 90.3% | 93.4% | 88.6% | 6.9% | 90.7% | 88.8% | 94.1% | 98.5% | 99.8% | 88.6% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Ultra Ball | 92.7% | 95.2% | 90.0% |
| 2 | Night Stretcher | 91.8% | 94.4% | 89.0% |
| 3 | Bursting Balloon | 91.6% | 94.2% | 89.7% |
| 4 | Sky Field | 91.5% | 93.9% | 88.7% |
| 5 | Manaphy | 91.3% | 94.4% | 85.7% |
| 6 | Team Rocket's Petrel | 91.2% | 93.6% | 90.3% |
| 7 | Igglybuff | 91.2% | 93.5% | 89.3% |
| 8 | Crushing Hammer | 91.2% | 94.0% | 88.0% |
| 9 | Professor's Research | 91.0% | 94.0% | 88.7% |
| 10 | Bravery Charm | 91.0% | 93.8% | 89.0% |
| 11 | Counter Catcher | 90.7% | 93.8% | 87.3% |
| 12 | Arven | 90.4% | 93.6% | 88.7% |
| 13 | Spiky Energy | 90.3% | 93.4% | 88.0% |
| 14 | Rescue Carrier | 90.2% | 93.6% | 85.3% |
| 15 | Battle Cage | 90.2% | 93.6% | 88.0% |
| 16 | Max Potion | 90.1% | 93.3% | 86.7% |
| 17 | Mime Jr. | 89.9% | 92.2% | 85.3% |
| 18 | Budew | 89.9% | 93.3% | 86.3% |
| 19 | Buddy-Buddy Poffin | 89.9% | 93.1% | 87.0% |
| 20 | Mew ex | 89.7% | 93.3% | 86.7% |
| 21 | Iono | 89.0% | 92.6% | 87.3% |
| 22 | Nest Ball | 88.8% | 92.7% | 84.3% |
| 23 | Hero's Cape | 88.7% | 92.2% | 87.7% |

## Step 2

Current weighted rate 91.9%. Best cut Budew at 91.5% does not rise. Stop.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Junk Arm played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Budew | 91.5% | 94.3% | 89.5% | 10.3% | 90.4% | 91.4% | 95.6% | 99.2% | 99.8% | 89.5% |
| 2 | Counter Catcher | 91.5% | 94.2% | 89.8% | 12.0% | 92.6% | 90.0% | 94.2% | 99.0% | 99.8% | 89.8% |
| 3 | Arven | 91.4% | 94.3% | 89.7% | 11.5% | 92.2% | 89.7% | 94.9% | 99.2% | 99.8% | 89.8% |
| 4 | Night Stretcher | 91.2% | 94.1% | 87.4% | 7.6% | 94.3% | 87.4% | 94.6% | 98.8% | 99.5% | 89.9% |
| 5 | Iono | 90.9% | 93.9% | 88.6% | 12.0% | 91.8% | 90.2% | 93.2% | 99.5% | 99.9% | 88.6% |
| 6 | Team Rocket's Petrel | 90.3% | 93.3% | 88.7% | 12.9% | 91.0% | 89.5% | 92.1% | 98.9% | 99.4% | 88.7% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Iono | 92.6% | 94.9% | 91.3% |
| 2 | Counter Catcher | 92.5% | 95.0% | 90.0% |
| 3 | Arven | 92.4% | 94.9% | 89.7% |
| 4 | Budew | 92.2% | 94.6% | 90.3% |
| 5 | Night Stretcher | 92.2% | 94.8% | 86.7% |
| 6 | Team Rocket's Petrel | 91.9% | 94.2% | 89.3% |
| 7 | Bravery Charm | 91.5% | 94.3% | 89.3% |
| 8 | Igglybuff | 91.5% | 94.4% | 86.0% |
| 9 | Crushing Hammer | 91.4% | 94.1% | 89.7% |
| 10 | Spiky Energy | 91.2% | 94.1% | 88.7% |
| 11 | Battle Cage | 91.0% | 93.9% | 89.0% |
| 12 | Max Potion | 90.9% | 94.0% | 85.3% |
| 13 | Bursting Balloon | 90.8% | 94.1% | 88.3% |
| 14 | Rescue Carrier | 90.7% | 94.1% | 86.7% |
| 15 | Mew ex | 90.6% | 93.9% | 87.0% |
| 16 | Sky Field | 90.6% | 93.6% | 88.7% |
| 17 | Manaphy | 90.3% | 93.6% | 78.3% |
| 18 | Professor's Research | 90.2% | 93.4% | 88.3% |
| 19 | Buddy-Buddy Poffin | 90.0% | 93.2% | 87.3% |
| 20 | Mime Jr. | 89.8% | 92.7% | 86.0% |
| 21 | Hero's Cape | 89.7% | 93.1% | 86.3% |
| 22 | Nest Ball | 89.6% | 92.9% | 86.3% |

## Holdout

The same lists on seed `20261015`, 1000 games per foe. Nothing was chosen on this seed. Weights are unchanged.

| Junk Arm | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 91.1% | 0.5% | +0.00% | — | 93.9% | 89.5% | 91.9% | 89.5% | 93.7% | 98.7% | 99.9% | 89.9% |
| 1 | 91.2% | 0.5% | +0.12% | 0.6% | 94.0% | 89.8% | 91.7% | 90.1% | 93.7% | 99.0% | 99.5% | 89.8% |

Stopped at 1. The next copy, cutting Budew, is 91.54% against 91.89%.


## Result

The selection seed keeps a copy when the loss-weighted rate rises. It picks the best of many cuts, so that gain is biased upward. The holdout seed is the one no list was chosen on. A difference under 2 standard errors does not separate two lists.

- 1 copy, cut Ultra Ball: 91.9% (+1.25% against the previous list, 1.93 standard errors).

The last copy's 300-game screen ranks Iono first at 92.6%. The 1000-game confirm ranks Budew first at 91.5% and Counter Catcher second at 91.5%.

Holdout seed `20261015`, 1000 games per foe, same weights. Unpaired difference against zero copies:

- 1 copy: +0.12% (0.19 standard errors, ±1 SE of the difference 0.6%).

Junk Arm finds a discarded Trainer. On the selection seed at 1 copy the finds per game are Hero's Cape 0.001, Bursting Balloon 0.028, Counter Catcher 0.001, Rescue Carrier 0.001, Night Stretcher 0.000. On the holdout those five are 0.001, 0.026, 0.000, 0.001, 0.001.

`SET_M60_NAMES` stays the locked four-Petrel list. This report starts from that list.

Copies at or above 2 standard errors against zero: none. Copies under 2 standard errors against zero: 1. The search kept 1.
1 copy against 0 copies is 0.19 standard errors, and that step cuts Ultra Ball.

The list the search kept:

```
4 Arven
4 Battle Cage
2 Bravery Charm
4 Buddy-Buddy Poffin
4 Budew
1 Bursting Balloon
1 Counter Catcher
3 Crushing Hammer
1 Hero's Cape
4 Igglybuff
4 Iono
1 Junk Arm
1 Manaphy
3 Max Potion
3 Mew ex
2 Mime Jr.
4 Nest Ball
1 Night Stretcher
2 Professor's Research
2 Rescue Carrier
3 Sky Field
2 Spiky Energy
4 Team Rocket's Petrel
```

