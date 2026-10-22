# Set M greedy Team Rocket's Petrel

Petrel searches the deck for any Trainer. On this list the found Item, Tool, or Stadium
is played the same turn, and a Supporter is held for the next turn. The collapse uses
the scores those cards already have. Sky Field, and any Stadium whose printed sentence
raises the Bench, is taken before Buddy-Buddy Poffin when that sentence adds a waiting
30 HP Basic. Area Zero Underdepths is taken when a Tera Pokémon is in play and the burst
is ready. Battle Cage uses its own score. Then Max Potion, Hero's Cape, Counter Catcher,
Buddy-Buddy Poffin, Rescue Carrier, Bursting Balloon, Night Stretcher, and Nest Ball.
Boss's Orders is the next-turn Supporter when Catcher cannot be played. Penny is next
when Manaphy is Active. Arven is played instead when it can fetch that Item or Tool
and a second card. Arven cannot fetch a Stadium, so Petrel still takes that Stadium.
Boss's Orders is played instead when the gust is already in hand.

Starting 60 is the fresh-seed best from `set-m-gust-search`: Start (4 Sky Field, 4 Budew).
That list has four Sky Field, four Budew, and zero Team Rocket's Petrel.
An earlier pass measured the previous lock, which has zero Sky Field. Those numbers are withdrawn.
The list this search kept is locked as `SET_M60_NAMES`.
Each step cuts exactly one copy of one other card. Weights are frozen from the
0-Petrel measurement of this list on this engine.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. A copy is kept only when that score rises.
- **Weights**: t60 20.9%, hedrick 25.8%, c60 20.9%, d60 3.2%, thorns 1.1%, starmie 28.1%
- **Copies kept**: 4
- **Elapsed**: 6148s

## Path

| Petrel | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Poffin | Potion | Catcher | Cape | Boss | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 89.0% | 0.5% | +0.00% | — | 92.2% | 86.8% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 90.2% | 87.9% | 90.2% | 98.5% | 99.5% | 86.8% |
| 1 | Ultra Ball | 90.4% | 0.5% | +1.38% | 0.7% | 93.2% | 87.9% | 10.1% | 3.1% | 0.2% | 3.6% | 0.0% | 91.6% | 87.9% | 92.2% | 99.3% | 99.4% | 89.1% |
| 2 | Penny | 91.1% | 0.4% | +2.10% | 0.7% | 93.8% | 88.5% | 19.1% | 6.2% | 0.5% | 6.6% | 0.0% | 93.5% | 89.0% | 93.2% | 99.2% | 99.5% | 88.5% |
| 3 | Penny | 92.1% | 0.4% | +3.12% | 0.6% | 94.4% | 90.4% | 25.7% | 9.1% | 1.1% | 10.0% | 0.0% | 92.2% | 90.4% | 95.2% | 98.4% | 99.8% | 90.4% |
| 4 | Sky Field | 92.3% | 0.4% | +3.32% | 0.6% | 94.6% | 90.6% | 32.2% | 10.4% | 1.1% | 11.8% | 0.0% | 92.2% | 90.6% | 94.7% | 99.3% | 99.7% | 91.2% |

## Step 1

Current weighted rate 89.0%. Accepted cut is Ultra Ball at 90.4%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Ultra Ball | 90.4% | 93.2% | 87.9% | 32.0% | 91.6% | 87.9% | 92.2% | 99.3% | 99.4% | 89.1% |
| 2 | Iono | 89.9% | 92.8% | 88.5% | 30.6% | 90.6% | 88.5% | 90.6% | 98.8% | 99.6% | 88.7% |
| 3 | Rescue Carrier | 89.9% | 92.9% | 88.0% | 31.8% | 90.9% | 88.3% | 91.4% | 98.8% | 99.8% | 88.0% |
| 4 | Bursting Balloon | 89.7% | 92.7% | 87.6% | 31.5% | 91.0% | 87.6% | 91.8% | 98.2% | 99.7% | 87.9% |
| 5 | Mew ex | 89.6% | 92.7% | 86.8% | 30.5% | 90.8% | 86.8% | 90.6% | 99.5% | 99.3% | 89.0% |
| 6 | Manaphy | 89.1% | 92.6% | 81.0% | 29.2% | 93.4% | 89.7% | 92.8% | 98.8% | 99.7% | 81.0% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Manaphy | 90.9% | 93.8% | 83.0% |
| 2 | Rescue Carrier | 90.6% | 93.5% | 87.3% |
| 3 | Ultra Ball | 90.4% | 93.3% | 87.0% |
| 4 | Iono | 90.2% | 93.1% | 87.7% |
| 5 | Bursting Balloon | 90.1% | 93.1% | 88.0% |
| 6 | Mew ex | 90.0% | 92.6% | 88.3% |
| 7 | Battle Cage | 89.9% | 92.6% | 87.3% |
| 8 | Budew | 89.9% | 92.9% | 86.0% |
| 9 | Crushing Hammer | 89.8% | 92.7% | 86.0% |
| 10 | Bravery Charm | 89.8% | 92.9% | 88.7% |
| 11 | Sky Field | 89.7% | 92.9% | 87.7% |
| 12 | Arven | 89.7% | 92.8% | 85.3% |
| 13 | Counter Catcher | 89.6% | 92.6% | 87.0% |
| 14 | Night Stretcher | 89.5% | 92.8% | 83.7% |
| 15 | Spiky Energy | 89.3% | 92.4% | 86.7% |
| 16 | Penny | 89.2% | 92.4% | 86.3% |
| 17 | Nest Ball | 89.2% | 92.4% | 86.3% |
| 18 | Mime Jr. | 88.9% | 91.2% | 85.0% |
| 19 | Buddy-Buddy Poffin | 88.9% | 92.1% | 85.3% |
| 20 | Professor's Research | 88.7% | 92.3% | 84.3% |
| 21 | Igglybuff | 88.5% | 91.9% | 86.0% |
| 22 | Hero's Cape | 87.9% | 91.4% | 86.3% |
| 23 | Max Potion | 87.9% | 91.6% | 85.7% |

## Step 2

Current weighted rate 90.4%. Accepted cut is Penny at 91.1%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Penny | 91.1% | 93.8% | 88.5% | 52.0% | 93.5% | 89.0% | 93.2% | 99.2% | 99.5% | 88.5% |
| 2 | Battle Cage | 90.6% | 93.5% | 88.3% | 51.9% | 91.8% | 88.6% | 93.3% | 99.4% | 99.5% | 88.3% |
| 3 | Spiky Energy | 90.3% | 93.3% | 88.4% | 52.0% | 91.6% | 88.4% | 91.9% | 99.1% | 99.9% | 88.7% |
| 4 | Bravery Charm | 90.3% | 93.2% | 88.0% | 51.0% | 91.6% | 88.0% | 91.7% | 99.0% | 99.8% | 88.9% |
| 5 | Mew ex | 89.8% | 92.9% | 87.1% | 51.5% | 91.5% | 87.4% | 92.6% | 98.9% | 99.9% | 87.1% |
| 6 | Nest Ball | 89.7% | 92.8% | 87.8% | 51.9% | 91.4% | 87.8% | 90.5% | 99.0% | 99.7% | 88.3% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Mew ex | 91.3% | 93.9% | 87.0% |
| 2 | Penny | 91.1% | 93.7% | 88.3% |
| 3 | Bravery Charm | 90.8% | 93.6% | 88.7% |
| 4 | Spiky Energy | 90.7% | 93.5% | 88.0% |
| 5 | Nest Ball | 90.6% | 93.3% | 87.3% |
| 6 | Battle Cage | 90.6% | 93.6% | 87.3% |
| 7 | Mime Jr. | 90.4% | 92.2% | 89.0% |
| 8 | Counter Catcher | 90.4% | 93.4% | 88.7% |
| 9 | Rescue Carrier | 90.4% | 93.2% | 86.3% |
| 10 | Bursting Balloon | 90.3% | 93.0% | 87.7% |
| 11 | Sky Field | 90.3% | 93.1% | 87.3% |
| 12 | Iono | 90.2% | 93.0% | 87.0% |
| 13 | Buddy-Buddy Poffin | 90.1% | 93.2% | 87.3% |
| 14 | Max Potion | 90.1% | 93.1% | 87.0% |
| 15 | Ultra Ball | 90.1% | 92.9% | 87.3% |
| 16 | Crushing Hammer | 89.8% | 92.9% | 86.0% |
| 17 | Manaphy | 89.7% | 93.3% | 80.7% |
| 18 | Professor's Research | 89.6% | 92.7% | 85.7% |
| 19 | Arven | 89.5% | 92.8% | 85.7% |
| 20 | Budew | 89.0% | 92.3% | 87.3% |
| 21 | Igglybuff | 88.4% | 91.8% | 85.7% |
| 22 | Night Stretcher | 88.1% | 91.6% | 86.3% |
| 23 | Hero's Cape | 86.8% | 90.7% | 85.7% |

## Step 3

Current weighted rate 91.1%. Accepted cut is Penny at 92.1%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Penny | 92.1% | 94.4% | 90.4% | 64.8% | 92.2% | 90.4% | 95.2% | 98.4% | 99.8% | 90.4% |
| 2 | Max Potion | 91.8% | 94.2% | 89.7% | 64.6% | 92.1% | 89.7% | 93.8% | 99.4% | 99.5% | 90.9% |
| 3 | Bravery Charm | 91.4% | 94.0% | 88.1% | 64.3% | 91.8% | 88.1% | 93.9% | 99.3% | 99.7% | 91.1% |
| 4 | Counter Catcher | 91.0% | 93.8% | 88.5% | 65.3% | 91.1% | 88.5% | 93.7% | 99.4% | 99.8% | 90.0% |
| 5 | Night Stretcher | 90.9% | 93.6% | 87.7% | 64.3% | 91.4% | 87.7% | 94.1% | 99.3% | 99.5% | 89.8% |
| 6 | Professor's Research | 90.7% | 93.6% | 88.0% | 63.9% | 92.8% | 88.4% | 93.3% | 99.4% | 99.8% | 88.0% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Penny | 92.3% | 94.5% | 90.7% |
| 2 | Professor's Research | 92.2% | 94.7% | 87.7% |
| 3 | Max Potion | 92.0% | 94.4% | 89.7% |
| 4 | Bravery Charm | 91.9% | 94.3% | 90.0% |
| 5 | Night Stretcher | 91.6% | 94.1% | 88.3% |
| 6 | Counter Catcher | 91.5% | 94.1% | 88.7% |
| 7 | Crushing Hammer | 91.3% | 93.7% | 88.7% |
| 8 | Budew | 91.2% | 93.9% | 89.3% |
| 9 | Spiky Energy | 91.2% | 93.9% | 89.3% |
| 10 | Bursting Balloon | 91.2% | 93.9% | 88.7% |
| 11 | Igglybuff | 91.1% | 93.8% | 88.3% |
| 12 | Battle Cage | 91.1% | 94.0% | 85.7% |
| 13 | Mew ex | 91.0% | 93.8% | 86.7% |
| 14 | Buddy-Buddy Poffin | 91.0% | 93.6% | 86.7% |
| 15 | Mime Jr. | 91.0% | 92.7% | 88.3% |
| 16 | Iono | 90.8% | 93.4% | 88.0% |
| 17 | Nest Ball | 90.8% | 93.6% | 88.0% |
| 18 | Arven | 90.6% | 93.3% | 87.0% |
| 19 | Ultra Ball | 90.5% | 93.4% | 88.0% |
| 20 | Sky Field | 90.5% | 93.5% | 85.7% |
| 21 | Rescue Carrier | 90.5% | 93.3% | 86.7% |
| 22 | Manaphy | 89.7% | 93.1% | 80.3% |
| 23 | Hero's Cape | 88.4% | 91.9% | 85.7% |

## Step 4

Current weighted rate 92.1%. Accepted cut is Sky Field at 92.3%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Sky Field | 92.3% | 94.6% | 90.6% | 73.4% | 92.2% | 90.6% | 94.7% | 99.3% | 99.7% | 91.2% |
| 2 | Counter Catcher | 92.3% | 94.5% | 91.3% | 72.7% | 91.9% | 91.3% | 93.5% | 99.0% | 100.0% | 91.6% |
| 3 | Spiky Energy | 91.9% | 94.5% | 88.8% | 73.0% | 92.8% | 88.8% | 95.6% | 99.6% | 99.9% | 90.2% |
| 4 | Bursting Balloon | 91.9% | 94.2% | 89.8% | 74.5% | 93.7% | 89.9% | 94.0% | 98.8% | 99.3% | 89.8% |
| 5 | Rescue Carrier | 91.8% | 94.2% | 89.7% | 73.4% | 92.8% | 89.7% | 93.9% | 98.8% | 99.7% | 90.4% |
| 6 | Bravery Charm | 91.7% | 94.3% | 89.4% | 72.0% | 92.7% | 89.8% | 94.8% | 99.2% | 99.8% | 89.4% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Counter Catcher | 92.9% | 94.8% | 89.0% |
| 2 | Bravery Charm | 92.6% | 94.8% | 90.3% |
| 3 | Bursting Balloon | 92.4% | 94.5% | 87.7% |
| 4 | Sky Field | 92.3% | 94.8% | 89.3% |
| 5 | Rescue Carrier | 92.3% | 94.4% | 90.7% |
| 6 | Spiky Energy | 92.3% | 94.7% | 90.3% |
| 7 | Max Potion | 92.2% | 94.7% | 90.0% |
| 8 | Crushing Hammer | 92.0% | 94.2% | 89.7% |
| 9 | Iono | 91.9% | 94.4% | 89.7% |
| 10 | Battle Cage | 91.9% | 94.3% | 90.7% |
| 11 | Night Stretcher | 91.5% | 93.9% | 89.0% |
| 12 | Budew | 91.2% | 93.8% | 87.7% |
| 13 | Manaphy | 91.2% | 93.8% | 85.3% |
| 14 | Mime Jr. | 91.0% | 92.3% | 88.7% |
| 15 | Arven | 91.0% | 93.6% | 85.3% |
| 16 | Ultra Ball | 90.9% | 93.6% | 87.3% |
| 17 | Igglybuff | 90.7% | 93.4% | 88.3% |
| 18 | Professor's Research | 90.3% | 93.1% | 87.7% |
| 19 | Mew ex | 90.3% | 93.4% | 87.3% |
| 20 | Nest Ball | 90.2% | 93.3% | 83.7% |
| 21 | Hero's Cape | 89.6% | 92.8% | 87.0% |
| 22 | Buddy-Buddy Poffin | 89.3% | 92.5% | 87.0% |

## Holdout

The same lists on seed `20261015`, 1000 games per foe. Nothing was chosen on this seed. Weights are unchanged.

| Petrel | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 90.0% | 0.5% | +0.00% | — | 93.0% | 87.5% | 91.9% | 87.5% | 89.4% | 99.1% | 99.7% | 90.1% |
| 1 | 89.2% | 0.5% | -0.83% | 0.7% | 92.5% | 86.7% | 90.3% | 86.7% | 92.3% | 99.2% | 99.8% | 86.9% |
| 2 | 91.0% | 0.4% | +0.96% | 0.6% | 93.8% | 88.9% | 92.0% | 89.6% | 92.9% | 99.3% | 99.8% | 88.9% |
| 3 | 91.0% | 0.5% | +0.93% | 0.6% | 93.8% | 88.2% | 92.3% | 89.2% | 93.8% | 99.7% | 99.9% | 88.2% |
| 4 | 91.8% | 0.4% | +1.73% | 0.6% | 94.1% | 89.8% | 92.2% | 89.8% | 93.0% | 98.5% | 99.8% | 91.3% |

## Result

The selection seed keeps a copy when the loss-weighted rate rises. It picks the best of many cuts, so that gain is biased upward. The holdout seed is the one no list was chosen on. A difference under 2 standard errors does not separate two lists.

- 1 copy, cut Ultra Ball: 90.4% (+1.38% against the previous list, 2.06 standard errors).
- 2 copies, cut Penny: 91.1% (+0.72% against the previous list, 1.12 standard errors).
- 3 copies, cut Penny: 92.1% (+1.02% against the previous list, 1.66 standard errors).
- 4 copies, cut Sky Field: 92.3% (+0.20% against the previous list, 0.34 standard errors).

The last copy's 300-game screen ranks Counter Catcher first at 92.9%. The 1000-game confirm ranks Sky Field first at 92.3% and Counter Catcher second at 92.3%.

Holdout seed `20261015`, 1000 games per foe, same weights. Unpaired difference against zero copies:

- 1 copy: -0.83% (-1.23 standard errors, ±1 SE of the difference 0.7%).
- 2 copies: +0.96% (1.49 standard errors, ±1 SE of the difference 0.6%).
- 3 copies: +0.93% (1.43 standard errors, ±1 SE of the difference 0.6%).
- 4 copies: +1.73% (2.73 standard errors, ±1 SE of the difference 0.6%).

On the same seed, 2 against 1 is +1.79% (2.71 standard errors); 3 against 2 is -0.04% (-0.06 standard errors); 4 against 3 is +0.80% (1.29 standard errors); 4 against 2 is +0.76% (1.23 standard errors).

Sky Field is fetched. On the selection seed it is 0.071 finds per game at 1 copy, with four Sky Field still in the deck, and 0.265 finds per game at 4 copies, with 3 Sky Field left. On the holdout those rates are 0.075 and 0.266. At 4 copies on the selection seed the other finds per game are Buddy-Buddy Poffin 0.322, Hero's Cape 0.118, Battle Cage 0.113, Max Potion 0.104. Area Zero Underdepths is 0.000.

`SET_M60_NAMES` is the list this search kept. The starting 60 is the fresh-seed best of `set-m-gust-search`, four Sky Field and four Budew.

Copies at or above 2 standard errors against zero: 4. Copies under 2 standard errors against zero: 1, 2, 3. The search kept 4.
4 copies against 3 copies is 1.29 standard errors, and that step cuts Sky Field.

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
1 Ultra Ball
```

