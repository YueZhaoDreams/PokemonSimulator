# Set M with Sky Field and Budew, greedy

**Run before the gust fix.** Set M's Boss's Orders and Counter Catcher plays were changed afterwards (`set-m-gust-audit.md`), which moved Set M itself by about one point. Compare lists inside one report only. The best Sky Field and Budew list on the fixed engine is in `set-m-gust-search.md`.

**The Budew rows below were run before the Baby order fix.** That order put Budew in the Active Spot whenever Mew ex could not
attack, where it hits for 10 while Igglybuff's Bouncy Circle hits for 30 per Benched 30 HP Pokémon. The Set M and Sky Field rows
do not depend on it and are unchanged. The same greedy search on the fixed order is in `set-m-budew-policy.md`.

Starting 60 is the locked Set M list (`SET_M60_NAMES`). Step 1 adds one Sky Field and the Budew steps follow.
Each step cuts exactly one copy of one other card for the new card, and every distinct card is tried as the cut.
Sky Field: each player can have 8 Pokémon on the Bench. Bouncy Circle is 30 damage for each Benched Pokémon
with a maximum HP of 30, so 8 of them is 240. Set M has 6 such Pokémon (4 Igglybuff, 2 Mime Jr.).
Budew is a third 30 HP Basic, and each copy is one more body for the wider Bench.
The Sky Field step is taken even when it lowers the score. Budew runs to 4 copies, the 4-of-a-name limit.
Mew ex plays a Bench-raising Stadium before Buddy-Buddy Poffin when more 30 HP Basics are waiting than there are
open slots, and Battle Cage does not replace it while the Bench is past 5 (see `tests/test_mew_sky_field.py`).
Set M is re-measured here on the current engine. The 88.4% in `set-m-eco-arm-on-carrier.md` was measured on
2026-10-07, before later engine commits, and does not reproduce.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. Weights are frozen from the zero-Sky-Field baseline.
- **Weights**: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 7567s

## Path

| Step | Sky Field | Budew | Cut | Weighted | ±1 SE | vs Set M | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 0 | 0 | — | 85.7% | 0.5% | +0.0% | 89.8% | 82.7% | 90.0% | 84.6% | 84.8% | 98.5% | 98.3% | 82.7% |
| Sky Field (best) | 1 | 0 | Night Stretcher | 86.5% | 0.5% | +0.8% | 90.4% | 84.5% | 89.7% | 86.2% | 84.5% | 98.8% | 98.6% | 84.5% |
| Budew 1 | 1 | 1 | Boss's Orders | 84.7% | 0.6% | -1.0% | 88.1% | 81.7% | 88.5% | 83.5% | 81.7% | 98.7% | 92.1% | 84.4% |
| Budew 2 | 1 | 2 | Bravery Charm | 83.9% | 0.6% | -1.8% | 86.6% | 79.5% | 87.3% | 85.6% | 79.5% | 98.8% | 85.9% | 82.8% |
| Budew 3 | 1 | 3 | Counter Catcher | 83.1% | 0.6% | -2.6% | 84.7% | 75.4% | 88.7% | 82.7% | 80.1% | 99.1% | 75.4% | 82.4% |
| Budew 4 | 1 | 4 | Ultra Ball | 83.0% | 0.6% | -2.7% | 83.4% | 68.6% | 86.8% | 84.5% | 80.2% | 98.5% | 68.6% | 82.0% |

## Holdout

The same lists on a fresh seed, `20261015`, 2000 games per foe. No list was chosen on this seed, so it is free of the selection bias in the path above. Weights are the same. The difference column uses the unpaired standard error of the two lists.

| Step | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | Babies | 8 Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.6% | 0.4% | +0.0% | 0.6% | 89.8% | 82.7% | 3.65 | 0.0% | 90.1% | 84.2% | 84.8% | 98.5% | 98.7% | 82.7% |
| Sky Field | 86.4% | 0.4% | +0.8% | 0.5% | 90.3% | 83.2% | 3.74 | 0.0% | 90.8% | 84.1% | 83.2% | 98.5% | 99.0% | 86.4% |
| Budew 1 | 84.3% | 0.4% | -1.3% | 0.6% | 88.4% | 81.5% | 3.96 | 0.0% | 89.1% | 83.8% | 81.5% | 98.7% | 95.0% | 82.2% |
| Budew 2 | 82.4% | 0.4% | -3.2% | 0.6% | 85.6% | 78.5% | 4.11 | 2.0% | 86.8% | 83.1% | 78.5% | 98.9% | 85.4% | 80.9% |
| Budew 3 | 83.1% | 0.4% | -2.6% | 0.6% | 84.5% | 74.9% | 4.24 | 4.5% | 87.9% | 83.5% | 79.6% | 98.7% | 74.9% | 82.4% |
| Budew 4 | 82.4% | 0.4% | -3.2% | 0.6% | 83.0% | 68.4% | 4.37 | 6.2% | 86.6% | 83.5% | 78.0% | 98.6% | 68.4% | 82.9% |

## Bench of 30 HP Pokémon

Babies is the mean number of Benched 30 HP Pokémon at the moment side A attacks.
The last three columns are the share of games with at least one attack at that many (6 Babies is 180, 7 is 210, 8 is 240).

| Step | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies | Itchy Pollen |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 3.66 | 0.0% | 0.0% | 0.0% | 0.0% | 0.9% |
| Sky Field | 3.73 | 13.3% | 7.4% | 0.0% | 0.0% | 0.7% |
| Budew 1 | 3.97 | 19.3% | 9.9% | 7.2% | 0.0% | 23.9% |
| Budew 2 | 4.14 | 24.5% | 10.8% | 10.8% | 2.2% | 29.8% |
| Budew 3 | 4.26 | 25.8% | 9.4% | 12.7% | 4.5% | 32.3% |
| Budew 4 | 4.37 | 28.4% | 10.6% | 15.2% | 6.3% | 34.9% |

## Step 1: add Sky Field, every cut

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

## Step 2: add Budew 1, every cut

Chosen cut is Boss's Orders. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Boss's Orders | 84.7% | 88.1% | 3.97 | 88.5% | 83.5% | 81.7% | 98.7% | 92.1% | 84.4% |
| 2 | Penny | 84.0% | 87.6% | 3.95 | 87.3% | 84.0% | 82.7% | 98.0% | 92.7% | 81.0% |
| 3 | Rescue Carrier | 83.8% | 87.8% | 3.95 | 88.8% | 85.4% | 80.7% | 98.4% | 93.5% | 80.0% |
| 4 | Ultra Ball | 83.3% | 87.5% | 3.93 | 88.9% | 85.0% | 79.4% | 98.7% | 93.3% | 79.7% |
| 5 | Bursting Balloon | 83.2% | 87.4% | 3.94 | 88.1% | 83.8% | 80.5% | 98.7% | 93.6% | 79.8% |
| 6 | Bravery Charm | 82.8% | 86.8% | 3.94 | 86.6% | 84.0% | 78.9% | 98.6% | 92.0% | 80.7% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Rescue Carrier | 85.5% | 89.1% |
| 2 | Penny | 84.2% | 87.9% |
| 3 | Ultra Ball | 83.9% | 87.9% |
| 4 | Bravery Charm | 83.9% | 87.6% |
| 5 | Boss's Orders | 83.5% | 87.2% |
| 6 | Bursting Balloon | 83.4% | 87.3% |
| 7 | Night Stretcher | 83.3% | 87.4% |
| 8 | Counter Catcher | 83.2% | 87.3% |
| 9 | Battle Cage | 83.1% | 87.3% |
| 10 | Nest Ball | 82.7% | 86.8% |
| 11 | Spiky Energy | 82.6% | 86.7% |
| 12 | Iono | 82.2% | 86.4% |
| 13 | Buddy-Buddy Poffin | 82.1% | 86.6% |
| 14 | Mew ex | 82.0% | 86.6% |
| 15 | Crushing Hammer | 81.9% | 86.3% |
| 16 | Max Potion | 81.8% | 86.7% |
| 17 | Professor's Research | 81.6% | 86.3% |
| 18 | Igglybuff | 81.2% | 85.8% |
| 19 | Arven | 81.1% | 85.6% |
| 20 | Manaphy | 81.0% | 86.9% |
| 21 | Mime Jr. | 80.2% | 83.0% |
| 22 | Hero's Cape | 78.5% | 84.4% |

## Step 3: add Budew 2, every cut

Chosen cut is Bravery Charm. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Bravery Charm | 83.9% | 86.6% | 4.14 | 87.3% | 85.6% | 79.5% | 98.8% | 85.9% | 82.8% |
| 2 | Counter Catcher | 82.7% | 85.8% | 4.13 | 88.7% | 83.0% | 78.7% | 98.3% | 84.7% | 81.1% |
| 3 | Nest Ball | 82.7% | 85.7% | 4.06 | 87.5% | 82.7% | 77.8% | 98.6% | 85.1% | 82.5% |
| 4 | Mime Jr. | 82.2% | 82.9% | 3.94 | 86.9% | 83.5% | 75.7% | 89.0% | 78.8% | 83.7% |
| 5 | Night Stretcher | 82.0% | 85.3% | 4.11 | 86.8% | 83.4% | 77.8% | 98.7% | 85.2% | 79.8% |
| 6 | Professor's Research | 81.6% | 85.0% | 4.06 | 86.0% | 82.8% | 77.7% | 98.4% | 85.9% | 79.4% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Bravery Charm | 85.0% | 87.2% |
| 2 | Professor's Research | 83.7% | 87.2% |
| 3 | Nest Ball | 83.4% | 85.7% |
| 4 | Night Stretcher | 83.4% | 86.3% |
| 5 | Mime Jr. | 83.2% | 84.3% |
| 6 | Counter Catcher | 83.1% | 86.4% |
| 7 | Ultra Ball | 83.0% | 86.4% |
| 8 | Manaphy | 82.9% | 86.4% |
| 9 | Spiky Energy | 82.9% | 86.4% |
| 10 | Iono | 82.9% | 85.9% |
| 11 | Max Potion | 82.4% | 85.4% |
| 12 | Bursting Balloon | 82.4% | 85.6% |
| 13 | Battle Cage | 82.2% | 84.7% |
| 14 | Crushing Hammer | 81.9% | 84.8% |
| 15 | Penny | 81.8% | 84.9% |
| 16 | Igglybuff | 81.8% | 84.4% |
| 17 | Rescue Carrier | 81.7% | 85.2% |
| 18 | Buddy-Buddy Poffin | 80.8% | 84.4% |
| 19 | Arven | 80.3% | 83.9% |
| 20 | Mew ex | 79.0% | 82.8% |
| 21 | Hero's Cape | 78.9% | 84.1% |

## Step 4: add Budew 3, every cut

Chosen cut is Counter Catcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher | 83.1% | 84.7% | 4.26 | 88.7% | 82.7% | 80.1% | 99.1% | 75.4% | 82.4% |
| 2 | Bravery Charm | 82.9% | 84.5% | 4.26 | 87.8% | 85.6% | 78.5% | 98.6% | 75.6% | 80.9% |
| 3 | Iono | 82.7% | 84.4% | 4.20 | 87.4% | 84.1% | 80.1% | 97.9% | 76.3% | 80.3% |
| 4 | Mime Jr. | 82.5% | 81.8% | 4.16 | 86.8% | 82.1% | 78.7% | 89.4% | 69.1% | 84.4% |
| 5 | Rescue Carrier | 82.0% | 83.9% | 4.25 | 86.5% | 82.8% | 77.4% | 97.6% | 77.0% | 82.0% |
| 6 | Battle Cage | 81.8% | 83.3% | 4.27 | 86.7% | 82.4% | 77.4% | 98.4% | 73.4% | 81.7% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Rescue Carrier | 83.7% | 84.9% |
| 2 | Battle Cage | 83.3% | 84.3% |
| 3 | Mime Jr. | 83.1% | 81.9% |
| 4 | Counter Catcher | 83.0% | 84.6% |
| 5 | Iono | 82.9% | 84.4% |
| 6 | Bravery Charm | 82.8% | 84.4% |
| 7 | Max Potion | 82.6% | 84.3% |
| 8 | Penny | 82.6% | 84.3% |
| 9 | Buddy-Buddy Poffin | 82.5% | 83.6% |
| 10 | Spiky Energy | 82.2% | 84.4% |
| 11 | Bursting Balloon | 82.1% | 84.0% |
| 12 | Night Stretcher | 82.1% | 83.9% |
| 13 | Nest Ball | 81.8% | 83.5% |
| 14 | Ultra Ball | 81.7% | 83.7% |
| 15 | Arven | 80.3% | 82.5% |
| 16 | Professor's Research | 80.1% | 82.8% |
| 17 | Crushing Hammer | 79.5% | 82.0% |
| 18 | Manaphy | 79.4% | 82.6% |
| 19 | Mew ex | 79.3% | 81.9% |
| 20 | Igglybuff | 79.2% | 81.4% |
| 21 | Hero's Cape | 75.7% | 79.4% |

## Step 5: add Budew 4, every cut

Chosen cut is Ultra Ball. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Ultra Ball | 83.0% | 83.4% | 4.37 | 86.8% | 84.5% | 80.2% | 98.5% | 68.6% | 82.0% |
| 2 | Rescue Carrier | 82.1% | 82.8% | 4.35 | 85.8% | 84.0% | 77.7% | 98.4% | 69.4% | 81.8% |
| 3 | Manaphy | 82.0% | 82.7% | 4.69 | 90.8% | 88.4% | 79.8% | 99.1% | 64.9% | 73.3% |
| 4 | Nest Ball | 81.5% | 82.6% | 4.29 | 86.0% | 82.9% | 77.6% | 97.6% | 70.8% | 80.8% |
| 5 | Igglybuff | 81.5% | 81.9% | 4.26 | 87.9% | 81.8% | 77.7% | 98.5% | 64.5% | 81.1% |
| 6 | Buddy-Buddy Poffin | 81.3% | 82.0% | 4.26 | 86.2% | 83.3% | 77.8% | 98.6% | 66.6% | 79.6% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Ultra Ball | 83.2% | 83.7% |
| 2 | Nest Ball | 83.1% | 83.8% |
| 3 | Manaphy | 82.2% | 82.7% |
| 4 | Rescue Carrier | 82.2% | 83.1% |
| 5 | Igglybuff | 82.1% | 82.3% |
| 6 | Buddy-Buddy Poffin | 82.0% | 82.2% |
| 7 | Iono | 81.9% | 82.2% |
| 8 | Counter Catcher | 81.8% | 82.9% |
| 9 | Spiky Energy | 81.7% | 82.6% |
| 10 | Night Stretcher | 81.6% | 81.7% |
| 11 | Penny | 81.5% | 82.6% |
| 12 | Mime Jr. | 81.2% | 79.9% |
| 13 | Bravery Charm | 81.2% | 81.9% |
| 14 | Battle Cage | 81.1% | 82.4% |
| 15 | Crushing Hammer | 81.0% | 81.9% |
| 16 | Mew ex | 80.8% | 81.7% |
| 17 | Professor's Research | 80.8% | 82.0% |
| 18 | Bursting Balloon | 80.5% | 81.5% |
| 19 | Arven | 80.1% | 81.8% |
| 20 | Max Potion | 79.8% | 81.2% |
| 21 | Hero's Cape | 77.2% | 79.8% |

## Result

- Set M, re-measured on the current engine: 85.7% weighted (±0.5%); 85.6% on the fresh seed.
- One Sky Field, cutting Night Stretcher: 86.5% (+0.8%); 86.4% on the fresh seed (+0.8%, ±0.5% of the difference).
- Best Budew step on the path: Budew 1 at 84.7%, -1.8% against the Sky Field-only list; on the fresh seed the best is Budew 1 at 84.3%, -2.1%.
- With 4 Budew the worst foe is Iron Thorns ex (Crushing Thorn) at 68.6% (Set M 98.3%). The loss weights are frozen from Set M, so a foe that Set M nearly always beats carries a small weight and a collapse there moves the weighted score little.
- With 4 Budew the Bench holds 8 Babies (240) in 6.3% of games, and Sky Field is in play in 28.4%.

Only the Sky Field step is above Set M: +0.8% on the selection seed (1.0 standard errors) and +0.8% on the fresh seed (1.4). Both are under 2 standard errors, so the gain is small and not settled. Every Budew step is below the Sky Field-only list on both seeds, so the best list on the path is Set M with one Sky Field and no Budew.

Best list on the path:

```
4 Arven
4 Battle Cage
1 Boss's Orders
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
1 Sky Field
2 Spiky Energy
2 Ultra Ball
```
