# Set M greedy Colress

Plasma Storm Colress shuffles your hand into your deck, then draws a number of cards equal to
the number of Benched Pokémon (both yours and your opponent's).
Professor's Research discards the hand and draws 7. The shuffled cards are not discarded.
Sky Field lets each Bench reach 8, and this list already fills its Bench, so the draw is often
near that 7 once both boards are out.

Starting 60 is the locked Set M list (`SET_M60_NAMES`): three Sky Field, four Budew, one Junk Arm,
two Professor's Research, four Iono, and zero Colress.
Each step cuts exactly one copy of one other card. Weights are frozen from the 0-Colress list.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. A copy is kept only when that score rises.
- **Weights**: t60 22.6%, hedrick 29.4%, c60 18.3%, d60 2.1%, thorns 0.9%, starmie 26.6%
- **Copies kept**: 3
- **Elapsed**: 8498s

## Path

| Colress | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 92.1% | 0.4% | +0.00% | — | 94.5% | 90.4% | 0.00 | 0.0 | 92.6% | 90.4% | 94.0% | 99.3% | 99.7% | 91.3% |
| 1 | Crushing Hammer | 92.4% | 0.4% | +0.29% | 0.6% | 94.7% | 90.6% | 0.26 | 8.2 | 91.7% | 90.6% | 94.8% | 99.3% | 99.4% | 92.4% |
| 2 | Sky Field | 92.8% | 0.4% | +0.78% | 0.6% | 95.1% | 90.9% | 0.49 | 8.3 | 93.3% | 90.9% | 95.6% | 98.8% | 99.9% | 92.0% |
| 3 | Bravery Charm | 93.0% | 0.4% | +0.88% | 0.6% | 95.1% | 91.0% | 0.70 | 8.4 | 94.2% | 92.4% | 94.1% | 99.1% | 99.8% | 91.0% |

## Step 1

Current weighted rate 92.1%. Accepted cut is Crushing Hammer at 92.4%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Crushing Hammer | 92.4% | 94.7% | 90.6% | 0.26 | 8.2 | 91.7% | 90.6% | 94.8% | 99.3% | 99.4% | 92.4% |
| 2 | Battle Cage | 92.2% | 94.6% | 90.7% | 0.25 | 8.3 | 92.8% | 91.0% | 94.5% | 98.8% | 99.9% | 90.7% |
| 3 | Rescue Carrier | 92.1% | 94.5% | 90.5% | 0.25 | 8.3 | 93.0% | 90.5% | 94.2% | 98.6% | 99.8% | 90.8% |
| 4 | Counter Catcher | 92.1% | 94.6% | 89.3% | 0.25 | 8.3 | 92.6% | 89.3% | 94.9% | 99.5% | 99.6% | 91.9% |
| 5 | Sky Field | 92.1% | 94.7% | 89.8% | 0.25 | 8.2 | 92.7% | 89.8% | 95.1% | 99.7% | 99.7% | 91.1% |
| 6 | Budew | 91.9% | 94.4% | 89.9% | 0.26 | 8.2 | 92.8% | 89.9% | 92.5% | 99.2% | 99.7% | 92.2% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Crushing Hammer | 93.0% | 95.1% | 91.7% |
| 2 | Sky Field | 92.9% | 95.3% | 91.0% |
| 3 | Battle Cage | 92.9% | 95.1% | 90.0% |
| 4 | Rescue Carrier | 92.5% | 94.6% | 91.7% |
| 5 | Budew | 92.2% | 94.5% | 90.7% |
| 6 | Counter Catcher | 92.0% | 94.7% | 87.3% |
| 7 | Junk Arm | 91.9% | 94.6% | 89.7% |
| 8 | Igglybuff | 91.8% | 94.2% | 90.3% |
| 9 | Team Rocket's Petrel | 91.7% | 94.3% | 89.0% |
| 10 | Mew ex | 91.7% | 94.3% | 88.0% |
| 11 | Nest Ball | 91.7% | 94.3% | 88.3% |
| 12 | Bravery Charm | 91.6% | 94.2% | 89.0% |
| 13 | Professor's Research | 91.5% | 93.9% | 89.7% |
| 14 | Manaphy | 91.3% | 94.1% | 83.3% |
| 15 | Iono | 91.2% | 93.8% | 89.3% |
| 16 | Night Stretcher | 90.9% | 93.6% | 87.0% |
| 17 | Bursting Balloon | 90.8% | 93.7% | 88.7% |
| 18 | Hero's Cape | 90.8% | 93.7% | 88.3% |
| 19 | Arven | 90.7% | 93.8% | 87.3% |
| 20 | Buddy-Buddy Poffin | 90.6% | 93.6% | 87.7% |
| 21 | Max Potion | 90.5% | 93.8% | 87.3% |
| 22 | Spiky Energy | 90.5% | 93.7% | 88.3% |
| 23 | Mime Jr. | 89.3% | 92.1% | 84.7% |

## Step 2

Current weighted rate 92.4%. Accepted cut is Sky Field at 92.8%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Sky Field | 92.8% | 95.1% | 90.9% | 0.49 | 8.3 | 93.3% | 90.9% | 95.6% | 98.8% | 99.9% | 92.0% |
| 2 | Night Stretcher | 92.5% | 94.9% | 90.0% | 0.49 | 8.4 | 94.0% | 90.0% | 94.7% | 99.2% | 99.5% | 91.8% |
| 3 | Junk Arm | 92.5% | 94.9% | 90.0% | 0.48 | 8.4 | 94.1% | 90.6% | 95.9% | 99.4% | 99.6% | 90.0% |
| 4 | Bravery Charm | 92.3% | 94.6% | 91.4% | 0.48 | 8.5 | 91.9% | 91.4% | 93.8% | 98.9% | 99.9% | 91.9% |
| 5 | Counter Catcher | 91.9% | 94.3% | 90.5% | 0.50 | 8.3 | 92.2% | 90.5% | 93.9% | 98.9% | 99.6% | 90.9% |
| 6 | Mew ex | 91.7% | 94.4% | 89.7% | 0.49 | 8.4 | 91.6% | 89.7% | 94.7% | 99.3% | 99.8% | 91.1% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Sky Field | 94.4% | 96.1% | 93.3% |
| 2 | Bravery Charm | 92.9% | 95.1% | 91.3% |
| 3 | Mew ex | 92.8% | 95.3% | 89.0% |
| 4 | Night Stretcher | 92.6% | 94.9% | 88.7% |
| 5 | Counter Catcher | 92.5% | 94.8% | 91.7% |
| 6 | Junk Arm | 92.4% | 95.0% | 90.0% |
| 7 | Manaphy | 92.3% | 94.7% | 85.3% |
| 8 | Spiky Energy | 92.2% | 94.7% | 90.3% |
| 9 | Bursting Balloon | 92.1% | 94.7% | 88.3% |
| 10 | Professor's Research | 92.0% | 94.6% | 90.0% |
| 11 | Buddy-Buddy Poffin | 92.0% | 94.4% | 90.0% |
| 12 | Arven | 91.9% | 94.7% | 89.3% |
| 13 | Battle Cage | 91.8% | 94.4% | 89.3% |
| 14 | Max Potion | 91.7% | 94.3% | 89.7% |
| 15 | Rescue Carrier | 91.6% | 94.3% | 89.0% |
| 16 | Crushing Hammer | 91.5% | 94.3% | 87.0% |
| 17 | Iono | 91.5% | 94.0% | 90.3% |
| 18 | Team Rocket's Petrel | 91.4% | 94.2% | 89.3% |
| 19 | Nest Ball | 91.2% | 94.1% | 88.0% |
| 20 | Budew | 91.1% | 94.0% | 89.0% |
| 21 | Mime Jr. | 91.0% | 92.7% | 87.7% |
| 22 | Igglybuff | 90.6% | 93.6% | 88.7% |
| 23 | Hero's Cape | 90.0% | 93.3% | 87.3% |

## Step 3

Current weighted rate 92.8%. Accepted cut is Bravery Charm at 93.0%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Bravery Charm | 93.0% | 95.1% | 91.0% | 0.70 | 8.4 | 94.2% | 92.4% | 94.1% | 99.1% | 99.8% | 91.0% |
| 2 | Junk Arm | 92.9% | 95.0% | 91.3% | 0.70 | 8.4 | 92.5% | 91.3% | 94.4% | 99.0% | 99.7% | 93.3% |
| 3 | Team Rocket's Petrel | 92.4% | 94.8% | 90.8% | 0.73 | 8.3 | 92.2% | 90.8% | 94.9% | 99.1% | 99.7% | 92.0% |
| 4 | Night Stretcher | 92.4% | 94.8% | 90.4% | 0.70 | 8.3 | 93.6% | 90.4% | 94.4% | 98.8% | 99.9% | 91.4% |
| 5 | Mime Jr. | 92.2% | 93.6% | 90.3% | 0.73 | 8.2 | 93.4% | 91.5% | 94.4% | 92.6% | 99.5% | 90.3% |
| 6 | Battle Cage | 92.2% | 94.6% | 89.5% | 0.70 | 8.4 | 92.4% | 89.5% | 94.7% | 98.9% | 99.7% | 92.3% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Bravery Charm | 93.4% | 95.2% | 89.7% |
| 2 | Battle Cage | 93.3% | 95.3% | 91.3% |
| 3 | Mime Jr. | 93.2% | 94.3% | 92.0% |
| 4 | Junk Arm | 93.2% | 95.3% | 90.7% |
| 5 | Team Rocket's Petrel | 93.1% | 95.2% | 91.3% |
| 6 | Night Stretcher | 92.7% | 94.9% | 89.7% |
| 7 | Mew ex | 92.6% | 95.0% | 90.3% |
| 8 | Spiky Energy | 92.6% | 94.8% | 91.3% |
| 9 | Bursting Balloon | 92.2% | 94.7% | 90.0% |
| 10 | Professor's Research | 92.2% | 94.7% | 88.7% |
| 11 | Crushing Hammer | 92.1% | 94.6% | 88.7% |
| 12 | Budew | 92.0% | 94.6% | 90.0% |
| 13 | Arven | 92.0% | 94.6% | 89.0% |
| 14 | Sky Field | 92.0% | 94.4% | 89.3% |
| 15 | Counter Catcher | 92.0% | 94.6% | 87.0% |
| 16 | Nest Ball | 91.8% | 94.4% | 88.3% |
| 17 | Rescue Carrier | 91.7% | 94.3% | 89.3% |
| 18 | Iono | 91.4% | 94.2% | 87.7% |
| 19 | Igglybuff | 91.4% | 93.9% | 89.7% |
| 20 | Buddy-Buddy Poffin | 90.7% | 93.4% | 87.0% |
| 21 | Max Potion | 90.5% | 93.7% | 86.7% |
| 22 | Manaphy | 90.4% | 93.6% | 80.7% |
| 23 | Hero's Cape | 90.4% | 93.6% | 85.7% |

## Step 4

Current weighted rate 93.0%. Best cut Sky Field at 92.7% does not rise. Stop.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Sky Field | 92.7% | 94.9% | 91.1% | 0.92 | 8.2 | 93.5% | 91.1% | 94.2% | 98.9% | 99.5% | 92.2% |
| 2 | Counter Catcher | 92.7% | 95.0% | 90.3% | 0.88 | 8.5 | 93.0% | 92.3% | 95.2% | 99.6% | 99.6% | 90.3% |
| 3 | Arven | 92.3% | 94.7% | 90.6% | 0.92 | 8.4 | 92.2% | 90.6% | 94.9% | 99.0% | 99.7% | 91.8% |
| 4 | Team Rocket's Petrel | 92.3% | 94.6% | 90.2% | 0.94 | 8.4 | 92.9% | 90.2% | 94.3% | 98.7% | 99.7% | 91.8% |
| 5 | Manaphy | 92.2% | 94.7% | 86.7% | 0.82 | 8.2 | 94.6% | 92.3% | 95.9% | 99.2% | 99.8% | 86.7% |
| 6 | Nest Ball | 91.7% | 94.2% | 89.7% | 0.89 | 8.5 | 91.4% | 89.7% | 94.2% | 98.6% | 99.6% | 91.6% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Arven | 93.6% | 95.6% | 92.3% |
| 2 | Nest Ball | 93.2% | 95.1% | 90.7% |
| 3 | Counter Catcher | 93.2% | 95.3% | 89.7% |
| 4 | Sky Field | 93.2% | 95.2% | 92.0% |
| 5 | Manaphy | 93.1% | 95.2% | 90.0% |
| 6 | Team Rocket's Petrel | 93.0% | 95.1% | 90.3% |
| 7 | Igglybuff | 92.7% | 94.7% | 91.7% |
| 8 | Professor's Research | 92.5% | 94.7% | 91.7% |
| 9 | Max Potion | 92.4% | 94.8% | 90.7% |
| 10 | Rescue Carrier | 92.4% | 94.9% | 89.7% |
| 11 | Mime Jr. | 92.4% | 93.8% | 90.7% |
| 12 | Junk Arm | 92.3% | 94.9% | 90.3% |
| 13 | Bursting Balloon | 92.1% | 94.6% | 90.3% |
| 14 | Bravery Charm | 92.1% | 94.7% | 90.7% |
| 15 | Spiky Energy | 92.0% | 94.4% | 90.3% |
| 16 | Mew ex | 91.9% | 94.3% | 91.0% |
| 17 | Iono | 91.8% | 94.2% | 89.7% |
| 18 | Battle Cage | 91.6% | 94.1% | 89.3% |
| 19 | Budew | 91.5% | 94.3% | 87.7% |
| 20 | Crushing Hammer | 91.3% | 93.9% | 89.7% |
| 21 | Buddy-Buddy Poffin | 90.7% | 93.8% | 87.7% |
| 22 | Night Stretcher | 90.6% | 93.3% | 89.0% |
| 23 | Hero's Cape | 90.6% | 93.6% | 86.7% |

## Holdout

The same lists on seed `20261015`, 1000 games per foe. Nothing was chosen on this seed. Weights are unchanged.

| Colress | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Plays | Drawn | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 92.2% | 0.4% | +0.00% | — | 94.7% | 90.3% | 0.00 | 0.0 | 92.8% | 91.1% | 94.5% | 99.3% | 99.9% | 90.3% |
| 1 | 91.2% | 0.5% | -1.00% | 0.6% | 94.0% | 89.1% | 0.26 | 8.3 | 91.9% | 89.1% | 95.0% | 99.0% | 99.7% | 89.2% |
| 2 | 92.5% | 0.4% | +0.34% | 0.6% | 94.9% | 90.8% | 0.48 | 8.3 | 93.3% | 90.8% | 94.8% | 99.2% | 99.8% | 91.3% |
| 3 | 92.9% | 0.4% | +0.74% | 0.6% | 95.0% | 91.6% | 0.69 | 8.4 | 92.2% | 91.6% | 94.9% | 99.2% | 99.6% | 92.8% |

Stopped at 3. The next copy, cutting Sky Field, is 92.75% against 92.96%.


## Result

The selection seed keeps a copy when the loss-weighted rate rises. It picks the best of many cuts, so that gain is biased upward. The holdout seed is the one no list was chosen on. A difference under 2 standard errors does not separate two lists.

- 1 copy, cut Crushing Hammer: 92.4% (+0.29% against the previous list, 0.48 standard errors).
- 2 copies, cut Sky Field: 92.8% (+0.48% against the previous list, 0.82 standard errors).
- 3 copies, cut Bravery Charm: 93.0% (+0.11% against the previous list, 0.19 standard errors).

Holdout seed `20261015`, 1000 games per foe, same weights. Unpaired difference against zero copies:

- 1 copy: -1.00% (-1.60 standard errors, ±1 SE of the difference 0.6%).
- 2 copies: +0.34% (0.57 standard errors, ±1 SE of the difference 0.6%).
- 3 copies: +0.74% (1.26 standard errors, ±1 SE of the difference 0.6%).

The selection seed kept 3.
That path cuts Crushing Hammer, then Sky Field, then Bravery Charm.

On the holdout, 2 against 1 is +1.34% (2.17 standard errors); 3 against 2 is +0.40% (0.68 standard errors); 3 against 1 is +1.74% (2.86 standard errors).
On the first screen, Professor's Research is rank 13 at 91.5%; Iono is rank 15 at 91.2%.
At 3 copies on the selection seed, Colress is played 0.70 times a game and draws 8.4 cards when it is played. The rest of the hand is shuffled into the deck. Professor's Research discards the hand and draws 7.
No holdout count is 2 standard errors above zero copies. 3 copies against zero is +0.74% (1.26 standard errors). 1 copy is -1.00% (-1.60 standard errors), below the starting 60. `SET_M60_NAMES` stays the starting 60.
2 and 3 against 1 clear 2 standard errors. That 1-copy list is below zero copies.

The list at the end of the search:

```
4 Arven
4 Battle Cage
1 Bravery Charm
4 Buddy-Buddy Poffin
4 Budew
1 Bursting Balloon
3 Colress
1 Counter Catcher
2 Crushing Hammer
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
2 Sky Field
2 Spiky Energy
4 Team Rocket's Petrel
```

