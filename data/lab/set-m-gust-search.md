# Set M, Boss's Orders and Counter Catcher after the gust fix

Set M used to play Boss's Orders and Counter Catcher whenever the opponent had a Bench, and pulled the lowest-HP Benched Pokémon.
Counter Catcher also needs more Prize cards remaining than the opponent, as printed. In 300 games per foe on the locked Set M,
36% of Boss's Orders plays took no prize that turn, and in 15% (Counter Catcher 23%) the Active Pokémon could already have been
Knocked Out for the same prizes or more. A gust is now played only when the pulled Pokémon's Knock Out takes more prizes this turn than
the Active Spot already would, and the pull is the Knock Out that takes the most prizes (`tests/test_mew_gust.py`).

Start list is the best list of `set-m-best-search.md` (four Sky Field, four Budew, no Boss's Orders, one Counter Catcher).
Each step may add one more copy of Boss's Orders or Counter Catcher (4-of-a-name limit), and every other card name is tried as the cut.
A step is taken only if it beats the current list on the selection seed. Every list on the path is then run on two fresh seeds and pooled,
and Set M, the start list, the final list and the best fresh-seed list on the clean seed.

- **Selection seed**: `20261007`; cuts screened on 300 games per foe, best 6 confirmed on 1000
- **Fresh seeds**: `20261105` with 2000 per foe, `20261112` with 3000
- **Clean seed**: `20261029` with 8000 per foe (the clean seed of `set-m-best-search.md`)
- **Score**: loss-weighted win rate. Weights: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 12011s

## Path (selection seed)

| Step | Add | Cut | Weighted | ±1 SE | vs start | Mean | Worst | Boss | Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Start (4 Sky Field, 4 Budew) | — | — | 89.1% | 0.5% | +0.0% | 92.2% | 86.8% | 0.01 | 0.01 | 90.2% | 87.9% | 90.2% | 98.5% | 99.5% | 86.8% |
| Step 1: +Boss's Orders | Boss's Orders | Battle Cage | 90.3% | 0.5% | +1.2% | 93.1% | 87.1% | 0.14 | 0.01 | 92.6% | 87.1% | 91.7% | 98.6% | 99.7% | 89.0% |
| Step 2: +Counter Catcher | Counter Catcher | Crushing Hammer | 90.5% | 0.5% | +1.4% | 93.2% | 89.4% | 0.14 | 0.03 | 90.2% | 89.6% | 90.9% | 99.0% | 99.8% | 89.4% |

Boss and Catcher are plays per game, averaged over the six foes.

## Step 1: take +Boss's Orders

Best candidate is Boss's Orders cutting Battle Cage, +1.20% against the current list on the selection seed.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Boss | Catcher |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Boss's Orders | Battle Cage | 90.3% | 0.5% | 93.1% | 87.1% | 0.14 | 0.01 |
| Counter Catcher | Ultra Ball | 90.2% | 0.5% | 93.0% | 87.9% | 0.03 | 0.03 |

Confirmed cuts for Boss's Orders:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Battle Cage | 90.3% | 93.1% | 92.6% | 87.1% | 91.7% | 98.6% | 99.7% | 89.0% |
| 2 | Counter Catcher | 89.9% | 92.8% | 91.2% | 88.3% | 91.3% | 98.9% | 99.4% | 87.5% |
| 3 | Bursting Balloon | 89.6% | 92.6% | 90.0% | 88.2% | 91.4% | 99.3% | 99.4% | 87.1% |
| 4 | Penny | 89.5% | 92.6% | 92.1% | 86.2% | 91.7% | 98.8% | 99.4% | 87.2% |
| 5 | Budew | 89.5% | 92.2% | 87.7% | 88.8% | 91.3% | 98.8% | 98.9% | 87.7% |
| 6 | Arven | 89.0% | 92.1% | 89.3% | 86.9% | 91.3% | 99.1% | 99.4% | 86.7% |

## Step 2: take +Counter Catcher

Best candidate is Counter Catcher cutting Crushing Hammer, +0.16% against the current list on the selection seed.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Boss | Catcher |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter Catcher | Crushing Hammer | 90.5% | 0.5% | 93.2% | 89.4% | 0.14 | 0.03 |
| Boss's Orders | Night Stretcher | 90.3% | 0.5% | 93.1% | 88.1% | 0.24 | 0.02 |

Confirmed cuts for Counter Catcher:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Crushing Hammer | 90.5% | 93.2% | 90.2% | 89.6% | 90.9% | 99.0% | 99.8% | 89.4% |
| 2 | Bursting Balloon | 89.9% | 92.8% | 90.9% | 88.6% | 92.6% | 99.0% | 99.7% | 86.3% |
| 3 | Battle Cage | 89.9% | 92.7% | 89.3% | 87.7% | 90.8% | 99.3% | 99.4% | 89.5% |
| 4 | Bravery Charm | 89.6% | 92.5% | 90.2% | 86.8% | 91.0% | 98.8% | 99.1% | 88.8% |
| 5 | Penny | 89.6% | 92.7% | 90.6% | 88.8% | 92.0% | 99.3% | 99.5% | 85.7% |
| 6 | Spiky Energy | 89.5% | 92.5% | 90.0% | 86.5% | 91.5% | 98.8% | 99.7% | 88.3% |

## Step 3: stop

Best candidate is Boss's Orders cutting Counter Catcher, -0.37% against the current list on the selection seed, so the search stops.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Boss | Catcher |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Boss's Orders | Counter Catcher | 90.1% | 0.5% | 92.8% | 88.1% | 0.23 | 0.01 |
| Counter Catcher | Penny | 90.0% | 0.5% | 92.8% | 88.7% | 0.15 | 0.04 |

Confirmed cuts for Boss's Orders:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher | 90.1% | 92.8% | 89.7% | 88.1% | 92.1% | 98.8% | 99.5% | 88.7% |
| 2 | Night Stretcher | 90.0% | 92.7% | 89.0% | 88.8% | 91.9% | 99.1% | 99.2% | 88.4% |
| 3 | Bursting Balloon | 89.9% | 92.7% | 90.2% | 87.5% | 91.8% | 99.0% | 99.3% | 88.5% |
| 4 | Max Potion | 89.5% | 92.6% | 89.9% | 89.2% | 92.3% | 99.2% | 99.7% | 85.2% |
| 5 | Spiky Energy | 89.4% | 92.3% | 88.6% | 88.0% | 91.8% | 98.7% | 99.7% | 87.2% |
| 6 | Arven | 89.4% | 92.3% | 89.3% | 87.4% | 92.9% | 99.1% | 99.1% | 86.2% |

## Fresh seeds

No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.

| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | Boss | Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 87.7% | 87.1% | 87.4% | 0.2% | +0.0% | 0.3% | 91.1% | 84.9% | 0.16 | 0.03 | 91.2% | 85.7% | 86.9% | 98.8% | 99.0% | 84.9% |
| Start (4 Sky Field, 4 Budew) | 89.7% | 89.9% | 89.9% | 0.2% | +2.5% | 0.3% | 92.8% | 87.9% | 0.01 | 0.01 | 90.7% | 88.8% | 90.6% | 99.0% | 99.6% | 87.9% |
| Step 1: +Boss's Orders | 89.0% | 90.1% | 89.7% | 0.2% | +2.3% | 0.3% | 92.6% | 87.2% | 0.13 | 0.01 | 90.1% | 87.2% | 91.6% | 99.0% | 99.7% | 88.2% |
| Step 2: +Counter Catcher | 89.4% | 90.0% | 89.7% | 0.2% | +2.4% | 0.3% | 92.7% | 87.4% | 0.14 | 0.03 | 89.8% | 87.4% | 91.8% | 99.2% | 99.5% | 88.3% |

## Clean seed `20261029`

8000 games per foe per list. The last two columns merge this seed with both fresh seeds.

| List | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs Set M |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 87.0% | 0.2% | +0.00% | 0.3% | 90.7% | 84.8% | 90.7% | 85.5% | 86.1% | 98.7% | 98.8% | 84.8% | 87.1% | +0.00% |
| Start (4 Sky Field, 4 Budew) | 89.6% | 0.2% | +2.62% | 0.3% | 92.6% | 87.3% | 91.0% | 87.3% | 90.8% | 99.1% | 99.5% | 88.0% | 89.7% | +2.58% |
| Step 2: +Counter Catcher | 89.5% | 0.2% | +2.57% | 0.3% | 92.5% | 87.4% | 89.6% | 87.4% | 91.3% | 99.1% | 99.4% | 88.1% | 89.6% | +2.50% |

## The gust fix alone, clean seed `20261029`

The same two lists, the same seed and game count, before and after the gust fix. The foes' decks and play are unchanged.

| List | Before | After | Change | ±1 SE of diff | Boss's Orders per game | Counter Catcher per game |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.9% | 87.0% | +1.09% | 0.3% | 0.16 | 0.03 |
| Start (4 Sky Field, 4 Budew) | 89.6% | 89.6% | +0.01% | 0.2% | 0.01 | 0.01 |

## Result

- Start list (Start (4 Sky Field, 4 Budew)): 89.1% on the selection seed, 89.9% on the two fresh seeds pooled, 89.6% on the clean seed.
- Step 1: +Boss's Orders (cut Battle Cage): 90.3% on the selection seed (+1.2% against the start list); two fresh seeds pooled 89.7% (-0.2%, -0.5 standard errors).
- Step 2: +Counter Catcher (cut Crushing Hammer): 90.5% on the selection seed (+1.4% against the start list); two fresh seeds pooled 89.7% (-0.1%, -0.4 standard errors).
- The search stopped: step 3: no candidate beats the current list on the selection seed.
- Start (4 Sky Field, 4 Budew) against Set M: clean seed +2.62% (+10.4 standard errors); all three fresh seeds +2.58% (+13.1).
- Step 2: +Counter Catcher against Set M: clean seed +2.57% (+10.2 standard errors); all three fresh seeds +2.50% (+12.7).
- Step 2: +Counter Catcher against the start list: clean seed -0.06% (-0.2 standard errors); all three fresh seeds -0.08% (-0.4).
- Step 2: +Counter Catcher against Start (4 Sky Field, 4 Budew), the best list on the two fresh seeds: clean seed -0.06% (-0.2 standard errors).

The final list is not clearly different from the start list on the three fresh seeds. The selection seed keeps the best of many cuts at every step, so its gain is biased upward and the fresh seeds decide.

Best list on the two fresh seeds (Start (4 Sky Field, 4 Budew)); the clean seed above was not used to pick it:

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
2 Penny
2 Professor's Research
2 Rescue Carrier
4 Sky Field
2 Spiky Energy
2 Ultra Ball
```
