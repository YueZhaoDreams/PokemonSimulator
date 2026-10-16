# Set M with more Sky Field, greedy

**Run before the gust fix.** Set M's Boss's Orders and Counter Catcher plays were changed afterwards (`set-m-gust-audit.md`), which moved Set M itself by about one point. Compare lists inside one report only. The best Sky Field and Budew list on the fixed engine is in `set-m-gust-search.md`.

Starting 60 is the locked Set M list (`SET_M60_NAMES`). Every step adds one more Sky Field, up to 4, and no Budew.
Each step cuts exactly one copy of one other card, and every distinct card is tried as the cut.
Sky Field: each player can have 8 Pokémon on the Bench. Set M has 6 Pokémon with a maximum HP of 30,
so Bouncy Circle tops out at 180 here. The question is whether a second, third, or fourth copy
puts the 8-slot Bench up often enough to pay for the card it replaces.
Mew ex plays a Bench-raising Stadium before Buddy-Buddy Poffin when more 30 HP Basics are waiting than there are
open slots, and Battle Cage does not replace it while the Bench is past 5 (see `tests/test_mew_sky_field.py`).
A second Sky Field is held while one is in play, so extra copies are replacements after the opponent's Stadium removes it.
Step 1 is the same swap as in `set-m-sky-field.md`, and its cells are the same.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. Weights are frozen from the zero-Sky-Field baseline.
- **Weights**: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 5956s

## Path

| Step | Sky Field | Cut | Weighted | ±1 SE | vs Set M | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 0 | — | 85.7% | 0.5% | +0.0% | 89.8% | 82.7% | 90.0% | 84.6% | 84.8% | 98.5% | 98.3% | 82.7% |
| Sky Field 1 | 1 | Night Stretcher | 86.5% | 0.5% | +0.8% | 90.4% | 84.5% | 89.7% | 86.2% | 84.5% | 98.8% | 98.6% | 84.5% |
| Sky Field 2 | 2 | Boss's Orders | 87.0% | 0.5% | +1.2% | 90.8% | 83.6% | 89.9% | 86.7% | 86.6% | 99.0% | 98.8% | 83.6% |
| Sky Field 3 (best) | 3 | Night Stretcher | 87.4% | 0.5% | +1.7% | 91.0% | 85.0% | 90.2% | 85.0% | 86.1% | 98.7% | 99.3% | 86.9% |
| Sky Field 4 | 4 | Night Stretcher | 86.7% | 0.5% | +0.9% | 90.5% | 82.0% | 88.2% | 88.4% | 86.6% | 98.7% | 99.0% | 82.0% |

## Fresh seeds

The same lists on two seeds that no list was chosen on: `20261015` with 2000 games per foe and `20261022` with 3000. Weights are the same. The pooled columns merge both seeds, and the difference uses the unpaired standard error of the two lists.

| Step | Seed 1 | Seed 2 | Pooled | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.6% | 85.6% | 85.6% | 0.2% | +0.0% | 0.3% | 89.9% | 82.9% | 90.6% | 84.1% | 84.3% | 98.7% | 98.8% | 82.9% |
| Sky Field 1 | 86.4% | 85.5% | 85.8% | 0.2% | +0.2% | 0.3% | 90.0% | 83.8% | 90.4% | 84.3% | 83.8% | 98.5% | 98.9% | 83.9% |
| Sky Field 2 (best) | 86.0% | 86.6% | 86.3% | 0.2% | +0.7% | 0.3% | 90.3% | 83.9% | 90.7% | 85.1% | 83.9% | 98.9% | 98.6% | 84.8% |
| Sky Field 3 | 85.6% | 85.5% | 85.5% | 0.2% | -0.1% | 0.3% | 89.6% | 83.7% | 88.1% | 84.7% | 84.0% | 98.6% | 98.5% | 83.7% |
| Sky Field 4 | 85.0% | 85.2% | 85.1% | 0.2% | -0.5% | 0.4% | 89.4% | 82.9% | 88.1% | 84.1% | 83.9% | 98.8% | 98.8% | 82.9% |

## Bench of 30 HP Pokémon

Babies is the mean number of Benched 30 HP Pokémon at the moment side A attacks.
The attack columns are the share of games with at least one attack at that many (5 is the old limit, 6 is 180, 7 is 210, 8 is 240).
Sky Field is the share of games where one was played. The table is the selection seed.

| Step | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Set M | 3.66 | 0.0% | 0.0% | 0.0% | 0.0% |
| Sky Field 1 | 3.73 | 13.3% | 7.4% | 0.0% | 0.0% |
| Sky Field 2 | 3.82 | 24.2% | 14.9% | 0.0% | 0.0% |
| Sky Field 3 | 3.84 | 30.5% | 19.0% | 0.0% | 0.0% |
| Sky Field 4 | 3.88 | 36.3% | 23.3% | 0.0% | 0.0% |

## Step 1: add Sky Field 1, every cut

Chosen cut is Night Stretcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 86.5% | 90.4% | 3.73 | 89.7% | 86.2% | 84.5% | 98.8% | 98.6% | 84.5% |
| 2 | Rescue Carrier | 86.4% | 90.4% | 3.73 | 89.7% | 85.9% | 85.4% | 98.6% | 98.8% | 83.7% |
| 3 | Boss's Orders | 86.4% | 90.1% | 3.75 | 90.5% | 85.4% | 85.0% | 98.2% | 97.8% | 83.9% |
| 4 | Arven | 86.1% | 90.2% | 3.74 | 90.5% | 86.3% | 82.3% | 99.1% | 98.7% | 84.4% |
| 5 | Battle Cage | 85.7% | 89.8% | 3.73 | 90.3% | 82.0% | 85.3% | 98.3% | 98.3% | 84.4% |
| 6 | Ultra Ball | 85.6% | 89.8% | 3.69 | 91.0% | 83.5% | 85.4% | 98.0% | 98.8% | 82.0% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Rescue Carrier | 87.9% | 91.4% |
| 2 | Night Stretcher | 87.5% | 91.1% |
| 3 | Boss's Orders | 87.4% | 91.2% |
| 4 | Arven | 87.1% | 91.1% |
| 5 | Ultra Ball | 87.1% | 90.8% |
| 6 | Battle Cage | 86.8% | 90.6% |
| 7 | Counter Catcher | 86.7% | 90.2% |
| 8 | Bursting Balloon | 86.5% | 90.2% |
| 9 | Mew ex | 86.4% | 90.7% |
| 10 | Buddy-Buddy Poffin | 85.5% | 89.6% |
| 11 | Iono | 85.4% | 89.6% |
| 12 | Nest Ball | 85.1% | 89.6% |
| 13 | Spiky Energy | 84.8% | 89.3% |
| 14 | Bravery Charm | 84.5% | 88.7% |
| 15 | Max Potion | 84.5% | 88.6% |
| 16 | Crushing Hammer | 84.2% | 88.7% |
| 17 | Professor's Research | 83.8% | 88.3% |
| 18 | Penny | 83.5% | 88.5% |
| 19 | Mime Jr. | 83.1% | 86.1% |
| 20 | Manaphy | 83.0% | 88.6% |
| 21 | Hero's Cape | 82.1% | 87.4% |
| 22 | Igglybuff | 81.1% | 86.3% |

## Step 2: add Sky Field 2, every cut

Chosen cut is Boss's Orders. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Boss's Orders | 87.0% | 90.8% | 3.82 | 89.9% | 86.7% | 86.6% | 99.0% | 98.8% | 83.6% |
| 2 | Battle Cage | 86.3% | 90.3% | 3.79 | 89.5% | 85.0% | 86.3% | 98.5% | 98.9% | 83.4% |
| 3 | Bravery Charm | 86.0% | 89.9% | 3.80 | 89.0% | 84.5% | 84.5% | 98.1% | 98.5% | 84.8% |
| 4 | Ultra Ball | 85.4% | 89.7% | 3.77 | 89.8% | 84.7% | 84.4% | 98.9% | 98.5% | 81.8% |
| 5 | Mew ex | 85.2% | 89.6% | 3.77 | 88.9% | 83.0% | 84.5% | 99.1% | 98.6% | 83.2% |
| 6 | Penny | 84.5% | 89.1% | 3.78 | 89.3% | 82.8% | 83.8% | 98.6% | 98.9% | 81.3% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Ultra Ball | 87.1% | 90.9% |
| 2 | Boss's Orders | 87.1% | 91.1% |
| 3 | Battle Cage | 86.9% | 90.7% |
| 4 | Bravery Charm | 86.8% | 90.6% |
| 5 | Mew ex | 86.3% | 90.1% |
| 6 | Penny | 86.2% | 90.4% |
| 7 | Max Potion | 85.6% | 89.8% |
| 8 | Crushing Hammer | 85.5% | 89.6% |
| 9 | Nest Ball | 85.2% | 89.5% |
| 10 | Spiky Energy | 85.0% | 89.3% |
| 11 | Counter Catcher | 84.7% | 89.1% |
| 12 | Professor's Research | 84.5% | 89.1% |
| 13 | Iono | 84.3% | 88.9% |
| 14 | Night Stretcher | 84.3% | 88.9% |
| 15 | Rescue Carrier | 84.1% | 88.6% |
| 16 | Buddy-Buddy Poffin | 83.8% | 88.7% |
| 17 | Bursting Balloon | 83.4% | 88.7% |
| 18 | Igglybuff | 83.3% | 87.6% |
| 19 | Arven | 82.9% | 88.0% |
| 20 | Hero's Cape | 82.9% | 87.6% |
| 21 | Mime Jr. | 82.2% | 85.3% |
| 22 | Manaphy | 81.7% | 88.0% |

## Step 3: add Sky Field 3, every cut

Chosen cut is Night Stretcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 87.4% | 91.0% | 3.84 | 90.2% | 85.0% | 86.1% | 98.7% | 99.3% | 86.9% |
| 2 | Rescue Carrier | 86.1% | 90.2% | 3.85 | 89.5% | 85.2% | 84.9% | 98.6% | 99.0% | 83.8% |
| 3 | Penny | 86.1% | 90.1% | 3.86 | 91.4% | 85.1% | 84.2% | 98.7% | 98.0% | 83.4% |
| 4 | Spiky Energy | 85.9% | 90.0% | 3.85 | 90.0% | 83.8% | 85.1% | 98.6% | 98.7% | 83.6% |
| 5 | Iono | 85.5% | 89.6% | 3.80 | 88.6% | 85.2% | 84.3% | 98.6% | 98.4% | 82.6% |
| 6 | Bravery Charm | 85.1% | 89.4% | 3.85 | 89.4% | 82.7% | 83.3% | 98.8% | 98.4% | 83.7% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Night Stretcher | 86.8% | 90.8% |
| 2 | Rescue Carrier | 86.6% | 90.8% |
| 3 | Penny | 86.4% | 90.6% |
| 4 | Spiky Energy | 86.2% | 90.3% |
| 5 | Bravery Charm | 86.0% | 90.2% |
| 6 | Iono | 85.9% | 90.2% |
| 7 | Ultra Ball | 85.8% | 89.9% |
| 8 | Bursting Balloon | 85.2% | 89.2% |
| 9 | Crushing Hammer | 85.1% | 89.3% |
| 10 | Mew ex | 84.9% | 89.2% |
| 11 | Counter Catcher | 84.8% | 89.0% |
| 12 | Max Potion | 84.8% | 89.1% |
| 13 | Battle Cage | 84.6% | 88.9% |
| 14 | Buddy-Buddy Poffin | 84.4% | 88.9% |
| 15 | Nest Ball | 83.8% | 88.8% |
| 16 | Manaphy | 82.9% | 88.7% |
| 17 | Professor's Research | 82.7% | 87.7% |
| 18 | Hero's Cape | 82.7% | 88.1% |
| 19 | Arven | 82.5% | 87.8% |
| 20 | Mime Jr. | 82.4% | 85.9% |
| 21 | Igglybuff | 81.4% | 86.5% |

## Step 4: add Sky Field 4, every cut

Chosen cut is Night Stretcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 86.7% | 90.5% | 3.88 | 88.2% | 88.4% | 86.6% | 98.7% | 99.0% | 82.0% |
| 2 | Bursting Balloon | 86.0% | 89.8% | 3.89 | 87.7% | 84.2% | 86.2% | 97.7% | 98.7% | 84.3% |
| 3 | Rescue Carrier | 86.0% | 90.0% | 3.88 | 89.2% | 84.2% | 87.1% | 98.4% | 98.7% | 82.3% |
| 4 | Counter Catcher | 85.3% | 89.5% | 3.85 | 87.6% | 85.2% | 82.7% | 98.5% | 99.2% | 83.9% |
| 5 | Arven | 85.2% | 89.2% | 3.85 | 88.3% | 83.2% | 84.3% | 98.1% | 97.8% | 83.7% |
| 6 | Crushing Hammer | 85.0% | 89.3% | 3.88 | 88.0% | 84.3% | 85.7% | 98.7% | 98.5% | 80.7% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Rescue Carrier | 87.1% | 90.9% |
| 2 | Night Stretcher | 86.5% | 90.3% |
| 3 | Counter Catcher | 86.1% | 89.9% |
| 4 | Arven | 85.7% | 89.6% |
| 5 | Crushing Hammer | 85.7% | 90.1% |
| 6 | Bursting Balloon | 85.4% | 89.5% |
| 7 | Bravery Charm | 85.4% | 89.3% |
| 8 | Professor's Research | 85.4% | 89.6% |
| 9 | Max Potion | 85.2% | 89.1% |
| 10 | Ultra Ball | 85.2% | 89.4% |
| 11 | Buddy-Buddy Poffin | 85.0% | 89.1% |
| 12 | Spiky Energy | 84.9% | 89.2% |
| 13 | Penny | 84.4% | 88.9% |
| 14 | Battle Cage | 83.9% | 88.6% |
| 15 | Mew ex | 83.8% | 88.0% |
| 16 | Iono | 83.7% | 88.1% |
| 17 | Manaphy | 82.7% | 88.5% |
| 18 | Hero's Cape | 82.4% | 87.6% |
| 19 | Nest Ball | 82.1% | 87.5% |
| 20 | Mime Jr. | 81.5% | 84.8% |
| 21 | Igglybuff | 81.4% | 86.5% |

## Result

- Set M, re-measured on the current engine: 85.7% weighted (±0.5%) on the selection seed; 85.6% (±0.2%) on the two fresh seeds pooled.
- Sky Field 1 (cut Night Stretcher): selection seed 86.5% (+0.8% against Set M); fresh seeds pooled 85.8% (+0.2% against Set M, +0.6 standard errors).
- Sky Field 2 (cut Boss's Orders): selection seed 87.0% (+1.2% against Set M); fresh seeds pooled 86.3% (+0.7% against Set M, +2.1 standard errors); +0.5% against one Sky Field (+1.5).
- Sky Field 3 (cut Night Stretcher): selection seed 87.4% (+1.7% against Set M); fresh seeds pooled 85.5% (-0.1% against Set M, -0.2 standard errors); -0.3% against one Sky Field (-0.8).
- Sky Field 4 (cut Night Stretcher): selection seed 86.7% (+0.9% against Set M); fresh seeds pooled 85.1% (-0.5% against Set M, -1.5 standard errors); -0.7% against one Sky Field (-2.0).

The selection seed picks Sky Field 3 and the pooled fresh seeds pick Sky Field 2. The greedy step chooses the best of six confirmed cuts on the selection seed, so its gains are biased upward, and a gain that the fresh seeds do not repeat is selection noise. No extra copy beats one Sky Field by 2 standard errors on the pooled fresh seeds. Sky Field 2 is the best of 4 lists compared with Set M on these same games, so its gain is also biased upward. The pooled rates neither rise nor fall steadily with the number of copies.

Best list on the pooled fresh seeds (Sky Field 2):

```
4 Arven
4 Battle Cage
3 Bravery Charm
4 Buddy-Buddy Poffin
2 Bursting Balloon
2 Counter Catcher
4 Crushing Hammer
1 Hero's Cape
4 Igglybuff
4 Iono
1 Manaphy
3 Max Potion
3 Mew ex
2 Mime Jr.
4 Nest Ball
3 Night Stretcher
2 Penny
2 Professor's Research
2 Rescue Carrier
2 Sky Field
2 Spiky Energy
2 Ultra Ball
```
