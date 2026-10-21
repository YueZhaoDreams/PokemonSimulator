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

Starting 60 is the locked Set M list (`SET_M60_NAMES`), which has zero Team Rocket's Petrel.
Each step cuts exactly one copy of one other card. Weights are frozen from the
0-Petrel measurement on this engine.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. A copy is kept only when that score rises.
- **Weights**: t60 18.3%, hedrick 26.6%, c60 25.7%, d60 2.7%, thorns 2.5%, starmie 24.1%
- **Copies kept**: 4
- **Elapsed**: 6722s

## Path

| Petrel | Cut | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | Poffin | Potion | Catcher | Cape | Boss | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 87.3% | 0.5% | +0.00% | — | 90.8% | 85.3% | 0.0% | 0.0% | 0.0% | 0.0% | 0.0% | 89.9% | 85.3% | 85.8% | 98.5% | 98.6% | 86.7% |
| 1 | Penny | 89.0% | 0.5% | +1.66% | 0.7% | 92.0% | 85.5% | 8.1% | 4.0% | 0.6% | 4.1% | 0.4% | 91.9% | 87.9% | 89.2% | 99.0% | 98.7% | 85.5% |
| 2 | Rescue Carrier | 89.4% | 0.5% | +2.07% | 0.7% | 92.4% | 86.9% | 16.3% | 7.0% | 0.6% | 7.8% | 1.1% | 91.9% | 86.9% | 89.0% | 98.9% | 98.9% | 88.5% |
| 3 | Crushing Hammer | 89.9% | 0.5% | +2.58% | 0.7% | 92.7% | 88.0% | 22.4% | 9.0% | 1.4% | 10.5% | 1.7% | 92.3% | 88.1% | 89.9% | 99.0% | 99.1% | 88.0% |
| 4 | Max Potion | 90.3% | 0.5% | +3.04% | 0.7% | 93.0% | 87.3% | 27.7% | 11.2% | 1.6% | 12.8% | 1.7% | 92.1% | 88.8% | 91.8% | 98.9% | 98.8% | 87.3% |

## Step 1

Current weighted rate 87.3%. Accepted cut is Penny at 89.0%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Penny | 89.0% | 92.0% | 85.5% | 31.1% | 91.9% | 87.9% | 89.2% | 99.0% | 98.7% | 85.5% |
| 2 | Bursting Balloon | 88.5% | 91.8% | 86.0% | 30.2% | 92.0% | 86.9% | 88.1% | 98.7% | 98.8% | 86.0% |
| 3 | Ultra Ball | 88.4% | 91.8% | 84.4% | 34.1% | 93.2% | 84.4% | 88.6% | 98.7% | 98.8% | 86.8% |
| 4 | Rescue Carrier | 88.3% | 91.6% | 86.3% | 30.8% | 91.5% | 86.4% | 86.3% | 98.5% | 98.8% | 88.0% |
| 5 | Crushing Hammer | 87.9% | 91.4% | 84.6% | 30.4% | 91.2% | 85.0% | 89.3% | 99.2% | 99.0% | 84.6% |
| 6 | Counter Catcher | 87.9% | 91.4% | 84.9% | 30.4% | 93.1% | 85.4% | 87.2% | 99.2% | 98.7% | 84.9% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Crushing Hammer | 89.3% | 92.3% | 85.3% |
| 2 | Rescue Carrier | 89.2% | 92.0% | 86.7% |
| 3 | Ultra Ball | 89.0% | 92.1% | 84.7% |
| 4 | Counter Catcher | 88.6% | 92.0% | 84.7% |
| 5 | Penny | 88.4% | 91.7% | 83.7% |
| 6 | Bursting Balloon | 88.4% | 91.8% | 85.7% |
| 7 | Night Stretcher | 88.1% | 91.3% | 86.7% |
| 8 | Arven | 87.9% | 91.3% | 86.0% |
| 9 | Spiky Energy | 87.7% | 91.4% | 84.3% |
| 10 | Boss's Orders | 87.6% | 91.2% | 81.7% |
| 11 | Bravery Charm | 87.3% | 91.3% | 83.3% |
| 12 | Buddy-Buddy Poffin | 87.3% | 90.8% | 82.0% |
| 13 | Max Potion | 87.2% | 90.8% | 85.0% |
| 14 | Professor's Research | 87.0% | 90.8% | 81.7% |
| 15 | Mew ex | 86.8% | 90.6% | 83.7% |
| 16 | Battle Cage | 86.6% | 90.6% | 81.3% |
| 17 | Iono | 86.3% | 90.4% | 80.3% |
| 18 | Hero's Cape | 86.1% | 90.3% | 82.3% |
| 19 | Manaphy | 85.9% | 90.1% | 72.0% |
| 20 | Nest Ball | 85.9% | 89.8% | 79.7% |
| 21 | Igglybuff | 84.9% | 89.0% | 80.7% |
| 22 | Mime Jr. | 84.0% | 86.4% | 79.3% |

## Step 2

Current weighted rate 89.0%. Accepted cut is Rescue Carrier at 89.4%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Rescue Carrier | 89.4% | 92.4% | 86.9% | 50.9% | 91.9% | 86.9% | 89.0% | 98.9% | 98.9% | 88.5% |
| 2 | Night Stretcher | 89.3% | 92.3% | 86.5% | 50.6% | 93.3% | 86.8% | 89.7% | 98.8% | 98.8% | 86.5% |
| 3 | Counter Catcher | 89.1% | 92.2% | 86.6% | 51.0% | 92.7% | 86.6% | 89.0% | 98.7% | 99.0% | 87.2% |
| 4 | Spiky Energy | 88.9% | 92.1% | 85.7% | 50.1% | 93.5% | 86.5% | 89.0% | 98.6% | 99.2% | 85.7% |
| 5 | Bursting Balloon | 88.8% | 92.0% | 86.9% | 50.8% | 92.0% | 87.4% | 87.7% | 98.6% | 99.1% | 86.9% |
| 6 | Battle Cage | 88.7% | 91.8% | 85.0% | 50.9% | 91.4% | 85.0% | 91.3% | 98.7% | 98.6% | 85.8% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Rescue Carrier | 89.9% | 92.8% | 87.0% |
| 2 | Counter Catcher | 89.4% | 92.4% | 87.3% |
| 3 | Spiky Energy | 89.2% | 92.3% | 85.0% |
| 4 | Night Stretcher | 89.2% | 92.5% | 86.3% |
| 5 | Bursting Balloon | 89.1% | 92.1% | 86.7% |
| 6 | Battle Cage | 89.0% | 92.2% | 84.7% |
| 7 | Iono | 88.7% | 92.0% | 85.7% |
| 8 | Arven | 88.7% | 91.7% | 85.3% |
| 9 | Nest Ball | 88.4% | 91.6% | 85.0% |
| 10 | Crushing Hammer | 88.2% | 91.3% | 85.7% |
| 11 | Mew ex | 88.2% | 91.5% | 85.0% |
| 12 | Max Potion | 88.0% | 91.3% | 83.7% |
| 13 | Professor's Research | 87.9% | 91.2% | 80.7% |
| 14 | Bravery Charm | 87.8% | 91.3% | 85.3% |
| 15 | Buddy-Buddy Poffin | 87.8% | 91.3% | 83.7% |
| 16 | Hero's Cape | 87.8% | 91.3% | 86.0% |
| 17 | Boss's Orders | 87.8% | 91.2% | 82.0% |
| 18 | Manaphy | 87.7% | 91.3% | 71.3% |
| 19 | Igglybuff | 87.5% | 90.9% | 81.7% |
| 20 | Ultra Ball | 87.5% | 91.1% | 84.7% |
| 21 | Penny | 87.2% | 90.9% | 83.3% |
| 22 | Mime Jr. | 84.7% | 86.8% | 81.7% |

## Step 3

Current weighted rate 89.4%. Accepted cut is Crushing Hammer at 89.9%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Crushing Hammer | 89.9% | 92.7% | 88.0% | 63.4% | 92.3% | 88.1% | 89.9% | 99.0% | 99.1% | 88.0% |
| 2 | Ultra Ball | 89.5% | 92.5% | 87.2% | 66.5% | 91.9% | 87.6% | 90.1% | 98.6% | 99.5% | 87.2% |
| 3 | Mew ex | 89.5% | 92.5% | 86.4% | 62.3% | 92.4% | 87.8% | 90.2% | 99.1% | 99.2% | 86.4% |
| 4 | Rescue Carrier | 89.4% | 92.3% | 86.4% | 63.4% | 92.2% | 86.4% | 90.9% | 98.3% | 99.1% | 86.9% |
| 5 | Spiky Energy | 89.0% | 92.2% | 85.9% | 62.5% | 92.5% | 86.4% | 90.1% | 99.1% | 99.2% | 85.9% |
| 6 | Night Stretcher | 88.8% | 92.0% | 85.1% | 63.1% | 92.3% | 85.1% | 87.6% | 98.3% | 99.6% | 89.1% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Ultra Ball | 90.5% | 93.2% | 86.7% |
| 2 | Mew ex | 90.3% | 93.0% | 87.0% |
| 3 | Night Stretcher | 90.1% | 93.1% | 87.3% |
| 4 | Crushing Hammer | 90.0% | 92.7% | 87.3% |
| 5 | Rescue Carrier | 89.9% | 92.7% | 85.7% |
| 6 | Spiky Energy | 89.8% | 92.6% | 88.0% |
| 7 | Battle Cage | 89.6% | 92.5% | 88.7% |
| 8 | Nest Ball | 89.4% | 92.3% | 86.7% |
| 9 | Penny | 89.3% | 92.3% | 83.7% |
| 10 | Counter Catcher | 89.1% | 92.4% | 84.7% |
| 11 | Bursting Balloon | 89.0% | 92.2% | 85.7% |
| 12 | Boss's Orders | 89.0% | 92.1% | 85.7% |
| 13 | Igglybuff | 88.8% | 91.9% | 85.0% |
| 14 | Bravery Charm | 88.8% | 92.1% | 85.0% |
| 15 | Professor's Research | 88.8% | 91.8% | 84.0% |
| 16 | Max Potion | 88.3% | 91.8% | 84.3% |
| 17 | Iono | 88.1% | 91.3% | 85.7% |
| 18 | Buddy-Buddy Poffin | 88.0% | 91.5% | 84.0% |
| 19 | Arven | 87.1% | 90.7% | 83.7% |
| 20 | Manaphy | 86.9% | 90.8% | 69.0% |
| 21 | Mime Jr. | 85.8% | 87.7% | 82.7% |
| 22 | Hero's Cape | 84.6% | 89.0% | 79.0% |

## Step 4

Current weighted rate 89.9%. Accepted cut is Max Potion at 90.3%.

### Confirmed

| Rank | Cut | Weighted | Mean | Worst | Petrel played | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Max Potion | 90.3% | 93.0% | 87.3% | 70.1% | 92.1% | 88.8% | 91.8% | 98.9% | 98.8% | 87.3% |
| 2 | Spiky Energy | 90.0% | 93.0% | 85.7% | 71.2% | 94.2% | 88.4% | 90.7% | 99.2% | 99.5% | 85.7% |
| 3 | Rescue Carrier | 89.9% | 92.7% | 87.8% | 72.0% | 92.5% | 87.8% | 89.7% | 98.4% | 99.2% | 88.7% |
| 4 | Bursting Balloon | 89.4% | 92.4% | 86.3% | 71.2% | 93.6% | 86.3% | 90.4% | 98.4% | 99.0% | 86.6% |
| 5 | Mew ex | 89.4% | 92.4% | 86.1% | 70.5% | 92.8% | 86.5% | 90.9% | 98.7% | 99.6% | 86.1% |
| 6 | Arven | 89.1% | 92.2% | 85.8% | 73.0% | 92.9% | 86.9% | 89.8% | 98.7% | 98.9% | 85.8% |

### Screen

| Rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Spiky Energy | 90.8% | 93.4% | 84.0% |
| 2 | Mew ex | 90.7% | 93.3% | 87.7% |
| 3 | Bursting Balloon | 90.4% | 92.7% | 85.7% |
| 4 | Max Potion | 90.3% | 92.9% | 87.0% |
| 5 | Rescue Carrier | 90.2% | 92.9% | 87.0% |
| 6 | Arven | 89.8% | 92.7% | 87.7% |
| 7 | Battle Cage | 89.5% | 92.4% | 86.3% |
| 8 | Bravery Charm | 89.5% | 92.7% | 86.0% |
| 9 | Crushing Hammer | 89.4% | 92.2% | 85.3% |
| 10 | Penny | 89.4% | 92.6% | 85.3% |
| 11 | Counter Catcher | 89.2% | 92.1% | 85.7% |
| 12 | Iono | 89.0% | 92.3% | 85.0% |
| 13 | Ultra Ball | 88.9% | 91.8% | 82.7% |
| 14 | Boss's Orders | 88.9% | 91.9% | 86.0% |
| 15 | Nest Ball | 88.7% | 92.0% | 84.3% |
| 16 | Night Stretcher | 88.5% | 91.7% | 82.3% |
| 17 | Professor's Research | 87.4% | 91.0% | 82.7% |
| 18 | Buddy-Buddy Poffin | 87.2% | 91.0% | 81.3% |
| 19 | Igglybuff | 86.8% | 90.8% | 80.7% |
| 20 | Manaphy | 86.8% | 90.6% | 70.0% |
| 21 | Mime Jr. | 86.7% | 88.0% | 82.3% |
| 22 | Hero's Cape | 84.5% | 89.3% | 81.3% |

## Holdout

The same lists on seed `20261015`, 1000 games per foe. Nothing was chosen on this seed. Weights are unchanged.

| Petrel | Weighted | ±1 SE | vs 0 | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 88.3% | 0.5% | +0.00% | — | 91.6% | 85.2% | 91.0% | 86.9% | 88.7% | 98.8% | 98.8% | 85.2% |
| 1 | 88.9% | 0.5% | +0.58% | 0.7% | 92.1% | 86.6% | 92.8% | 86.6% | 88.4% | 98.4% | 99.3% | 86.9% |
| 2 | 88.7% | 0.5% | +0.36% | 0.7% | 91.9% | 85.1% | 92.4% | 85.6% | 90.5% | 98.8% | 99.1% | 85.1% |
| 3 | 89.4% | 0.5% | +1.11% | 0.7% | 92.3% | 85.6% | 92.5% | 85.6% | 90.8% | 98.5% | 98.7% | 87.9% |
| 4 | 90.2% | 0.5% | +1.85% | 0.7% | 92.9% | 86.8% | 94.1% | 87.3% | 91.8% | 98.3% | 99.1% | 86.8% |

## Result

The selection seed keeps a copy at every step and stops at 4, cutting Penny, then Rescue Carrier, then Crushing Hammer, then Max Potion. Weighted win rate 87.3% → 90.3% (+3.04 pp). That seed keeps the best of many cuts, so the gain is biased upward.

The same lists on seed `20261015`, 1000 games per foe, same weights:

| Petrel | vs 0 | Standard errors |
| ---: | ---: | ---: |
| 1 | +0.58 pp | 0.84 |
| 2 | +0.36 pp | 0.51 |
| 3 | +1.11 pp | 1.61 |
| 4 | +1.85 pp | 2.72 |

Four copies against zero is +1.8507 pp, unpaired standard error 0.679 pp, 2.72 standard errors. This repo treats a fresh-seed difference under 2 standard errors as not separating the lists. 2.72 does separate them, so `SET_M60_NAMES` is this 4-copy list. One, two, and three copies do not clear that line, and the holdout path is not monotone. Hedrick, the heaviest weight, is 86.9% → 87.3%. The weighted gain is T60 91.0% → 94.1% and C60 88.7% → 91.8%.

On the selection seed at 4 copies, Petrel resolves about 0.70 times a game. The collapses per game are Buddy-Buddy Poffin 0.28, Bursting Balloon 0.16, Battle Cage 0.15, Hero's Cape 0.13, and Max Potion 0.11. Sky Field and Area Zero Underdepths are scored the same way and are not in this 60, so those rates are 0. Battle Cage is the Stadium this list can collapse into.
