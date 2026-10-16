# Set M, more search from one Sky Field and four Budew

Start list is the last row of `set-m-budew-policy.md`: the locked Set M (`SET_M60_NAMES`) with one Sky Field and four Budew,
played with the fixed Baby order (`tests/test_mew_baby_attacker.py`).
Each step may add one more copy of Sky Field, Budew, Igglybuff, Mime Jr. or Cleffa (4-of-a-name limit), and every card name
in the list except the added one is tried as the cut. A step is taken only if it beats the current list on the selection seed.
Every list on the path is then run on two fresh seeds and pooled, and Set M, the start list and the final list on a third.

- **Selection seed**: `20261007`; cuts screened on 300 games per foe, best 6 confirmed on 1000
- **Fresh seeds**: `20261015` with 2000 per foe, `20261022` with 3000
- **Clean seed**: `20261029` with 8000 per foe
- **Score**: loss-weighted win rate. Weights: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 13226s

## Path (selection seed)

| Step | Add | Cut | Weighted | ±1 SE | vs start | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Budew 4 (start) | — | — | 88.9% | 0.5% | +0.0% | 92.2% | 84.8% | 92.1% | 87.9% | 90.5% | 98.7% | 99.5% | 84.8% |
| Step 1: +Sky Field | Sky Field | Boss's Orders | 89.1% | 0.5% | +0.1% | 92.4% | 85.9% | 91.2% | 88.5% | 89.7% | 99.2% | 99.6% | 85.9% |
| Step 2: +Sky Field | Sky Field | Bravery Charm | 89.4% | 0.5% | +0.5% | 92.5% | 86.9% | 91.1% | 87.9% | 90.6% | 98.7% | 99.7% | 86.9% |
| Step 3: +Sky Field | Sky Field | Counter Catcher | 90.4% | 0.5% | +1.5% | 93.1% | 88.9% | 92.1% | 89.6% | 90.0% | 98.5% | 99.6% | 88.9% |

## Step 1: take Sky Field

Best candidate is Sky Field cutting Boss's Orders, +0.13% against the current list on the selection seed.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Babies | 8 Babies |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sky Field | Boss's Orders | 89.1% | 0.5% | 92.4% | 85.9% | 4.43 | 9.3% |
| Mime Jr. | Penny | 88.2% | 0.5% | 92.0% | 85.3% | 4.31 | 6.0% |
| Cleffa | Bravery Charm | 86.3% | 0.5% | 90.3% | 82.7% | 4.35 | 6.7% |

Confirmed cuts for Sky Field:

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Boss's Orders | 89.1% | 92.4% | 4.43 | 91.2% | 88.5% | 89.7% | 99.2% | 99.6% | 85.9% |
| 2 | Penny | 88.6% | 92.0% | 4.39 | 92.8% | 87.8% | 88.1% | 98.8% | 99.4% | 85.4% |
| 3 | Bursting Balloon | 88.4% | 91.8% | 4.39 | 91.1% | 87.1% | 88.5% | 99.1% | 98.9% | 85.9% |
| 4 | Budew | 88.3% | 91.7% | 4.29 | 91.1% | 85.4% | 89.0% | 98.7% | 99.0% | 86.8% |
| 5 | Nest Ball | 87.9% | 91.5% | 4.32 | 89.7% | 85.9% | 89.9% | 99.3% | 99.1% | 84.9% |
| 6 | Hero's Cape | 86.7% | 90.9% | 4.40 | 91.9% | 86.0% | 84.7% | 99.6% | 99.8% | 83.6% |

## Step 2: take Sky Field

Best candidate is Sky Field cutting Bravery Charm, +0.33% against the current list on the selection seed.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Babies | 8 Babies |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sky Field | Bravery Charm | 89.4% | 0.5% | 92.5% | 86.9% | 4.57 | 12.0% |
| Mime Jr. | Battle Cage | 88.8% | 0.5% | 92.2% | 87.1% | 4.52 | 10.4% |
| Cleffa | Penny | 87.2% | 0.5% | 91.0% | 83.8% | 4.60 | 12.7% |

Confirmed cuts for Sky Field:

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Bravery Charm | 89.4% | 92.5% | 4.57 | 91.1% | 87.9% | 90.6% | 98.7% | 99.7% | 86.9% |
| 2 | Night Stretcher | 89.4% | 92.4% | 4.56 | 90.7% | 85.4% | 91.8% | 99.2% | 99.2% | 88.2% |
| 3 | Rescue Carrier | 89.0% | 92.2% | 4.54 | 91.8% | 88.4% | 89.5% | 98.5% | 99.5% | 85.6% |
| 4 | Battle Cage | 89.0% | 92.1% | 4.57 | 89.7% | 86.5% | 91.5% | 99.0% | 99.2% | 86.6% |
| 5 | Counter Catcher | 88.9% | 92.2% | 4.51 | 91.1% | 87.2% | 90.1% | 99.0% | 99.5% | 86.3% |
| 6 | Ultra Ball | 88.6% | 92.0% | 4.57 | 91.2% | 85.2% | 90.2% | 98.9% | 99.7% | 86.9% |

## Step 3: take Sky Field

Best candidate is Sky Field cutting Counter Catcher, +1.00% against the current list on the selection seed.

| Add | Best cut | Weighted | ±1 SE | Mean | Worst | Babies | 8 Babies |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Sky Field | Counter Catcher | 90.4% | 0.5% | 93.1% | 88.9% | 4.69 | 15.3% |
| Mime Jr. | Ultra Ball | 90.1% | 0.5% | 93.1% | 87.8% | 4.68 | 14.5% |
| Cleffa | Battle Cage | 87.8% | 0.5% | 91.1% | 85.9% | 4.78 | 16.6% |

Confirmed cuts for Sky Field:

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher | 90.4% | 93.1% | 4.69 | 92.1% | 89.6% | 90.0% | 98.5% | 99.6% | 88.9% |
| 2 | Night Stretcher | 90.2% | 93.0% | 4.68 | 91.8% | 88.3% | 90.4% | 99.2% | 99.5% | 89.0% |
| 3 | Ultra Ball | 90.0% | 92.8% | 4.69 | 90.6% | 89.1% | 92.0% | 99.1% | 99.3% | 86.9% |
| 4 | Spiky Energy | 89.7% | 92.7% | 4.70 | 90.7% | 87.5% | 90.2% | 99.4% | 99.4% | 88.9% |
| 5 | Manaphy | 88.5% | 92.2% | 4.99 | 93.2% | 91.0% | 91.2% | 99.0% | 99.7% | 79.1% |
| 6 | Max Potion | 88.3% | 91.7% | 4.68 | 91.3% | 86.0% | 88.9% | 98.6% | 99.4% | 86.2% |

## Fresh seeds

No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.

| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.6% | 85.6% | 85.6% | 0.2% | +0.0% | 0.3% | 89.9% | 82.9% | 90.6% | 84.1% | 84.3% | 98.7% | 98.8% | 82.9% |
| Sky Field | 86.4% | 85.5% | 85.8% | 0.2% | +0.2% | 0.3% | 90.0% | 83.8% | 90.4% | 84.3% | 83.8% | 98.5% | 98.9% | 83.9% |
| Budew 4 (start) | 87.8% | 88.1% | 88.0% | 0.2% | +2.3% | 0.3% | 91.6% | 84.9% | 90.7% | 86.3% | 89.0% | 99.0% | 99.5% | 84.9% |
| Step 1: +Sky Field | 88.8% | 88.8% | 88.8% | 0.2% | +3.1% | 0.3% | 92.1% | 86.7% | 90.8% | 86.7% | 89.7% | 99.2% | 99.6% | 86.7% |
| Step 2: +Sky Field | 89.1% | 88.9% | 89.0% | 0.2% | +3.3% | 0.3% | 92.2% | 86.8% | 91.4% | 86.9% | 89.8% | 98.7% | 99.7% | 86.8% |
| Step 3: +Sky Field | 88.9% | 89.4% | 89.2% | 0.2% | +3.6% | 0.3% | 92.4% | 86.8% | 91.2% | 87.7% | 90.2% | 99.0% | 99.3% | 86.8% |

## Clean seed `20261029`

8000 games per foe per list. The last two columns merge this seed with both fresh seeds.

| List | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs Set M |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.9% | 0.2% | +0.00% | 0.3% | 90.0% | 83.5% | 90.9% | 84.7% | 83.5% | 98.7% | 98.6% | 83.7% | 85.8% | +0.00% |
| Budew 4 (start) | 87.6% | 0.2% | +1.71% | 0.3% | 91.4% | 84.8% | 91.3% | 85.7% | 87.9% | 99.0% | 99.5% | 84.8% | 87.7% | +1.95% |
| Step 3: +Sky Field | 89.6% | 0.2% | +3.70% | 0.3% | 92.6% | 87.5% | 91.3% | 87.8% | 90.5% | 99.1% | 99.4% | 87.5% | 89.5% | +3.67% |

## Bench of 30 HP Pokémon (selection seed)

| List | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies | Itchy Pollen |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Budew 4 (start) | 4.24 | 25.0% | 8.4% | 13.1% | 5.7% | 6.8% |
| Step 1: +Sky Field | 4.43 | 39.2% | 13.5% | 21.2% | 9.3% | 6.6% |
| Step 2: +Sky Field | 4.57 | 50.1% | 18.4% | 27.6% | 12.0% | 6.9% |
| Step 3: +Sky Field | 4.69 | 57.9% | 21.9% | 32.0% | 15.3% | 6.7% |

## Result

- Start list (Budew 4 (start)): 88.9% on the selection seed, 88.0% on the two fresh seeds pooled, 87.6% on the clean seed.
- Step 1: +Sky Field (cut Boss's Orders): 89.1% on the selection seed (+0.1% against the start list); two fresh seeds pooled 88.8% (+0.8%, +2.6 standard errors).
- Step 2: +Sky Field (cut Bravery Charm): 89.4% on the selection seed (+0.5% against the start list); two fresh seeds pooled 89.0% (+1.0%, +3.2 standard errors).
- Step 3: +Sky Field (cut Counter Catcher): 90.4% on the selection seed (+1.5% against the start list); two fresh seeds pooled 89.2% (+1.3%, +4.1 standard errors).
- The search stopped: reached 3 steps.
- Budew 4 (start) against Set M: clean seed +1.71% (+6.4 standard errors); all three fresh seeds +1.95% (+9.3).
- Step 3: +Sky Field against Set M: clean seed +3.70% (+14.4 standard errors); all three fresh seeds +3.67% (+18.1).
- Step 3: +Sky Field against the start list: clean seed +2.00% (+8.0 standard errors); all three fresh seeds +1.72% (+8.8).

The final list is better than the start list on the three fresh seeds. The selection seed keeps the best of many cuts at every step, so its gain is biased upward and the fresh seeds decide.

Final list (Step 3: +Sky Field):

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
