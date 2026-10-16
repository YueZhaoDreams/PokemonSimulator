# Set M with Sky Field and Budew, greedy

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
Baby order: an Active Baby whose attack only chips and locks Items gives way to a Benched Baby that out-damages it, in play and after a Knock Out (see tests/test_mew_baby_attacker.py). The earlier Budew run in set-m-sky-field.md used the old order, which put Budew in front whenever Mew ex could not attack.

- **Seed**: `20261007`
- **Games**: cuts screened on 300 per foe, best 6 confirmed on 1000 per foe
- **Score**: loss-weighted win rate. Weights are frozen from the zero-Sky-Field baseline.
- **Weights**: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 5556s

## Path

| Step | Sky Field | Budew | Cut | Weighted | ±1 SE | vs Set M | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 0 | 0 | — | 85.7% | 0.5% | +0.0% | 89.8% | 82.7% | 90.0% | 84.6% | 84.8% | 98.5% | 98.3% | 82.7% |
| Sky Field | 1 | 0 | Night Stretcher | 86.5% | 0.5% | +0.8% | 90.4% | 84.5% | 89.7% | 86.2% | 84.5% | 98.8% | 98.6% | 84.5% |
| Budew 1 | 1 | 1 | Bursting Balloon | 87.7% | 0.5% | +2.0% | 91.1% | 85.0% | 91.1% | 85.0% | 86.6% | 98.0% | 98.7% | 87.1% |
| Budew 2 | 1 | 2 | Night Stretcher | 88.4% | 0.5% | +2.7% | 91.7% | 86.8% | 90.4% | 86.8% | 88.3% | 98.3% | 99.5% | 86.8% |
| Budew 3 | 1 | 3 | Crushing Hammer | 88.8% | 0.5% | +3.1% | 92.1% | 85.6% | 91.0% | 88.6% | 88.9% | 99.0% | 99.7% | 85.6% |
| Budew 4 (best) | 1 | 4 | Night Stretcher | 88.9% | 0.5% | +3.2% | 92.2% | 84.8% | 92.1% | 87.9% | 90.5% | 98.7% | 99.5% | 84.8% |

## Holdout

The same lists on a fresh seed, `20261015`, 2000 games per foe. No list was chosen on this seed, so it is free of the selection bias in the path above. Weights are the same. The difference column uses the unpaired standard error of the two lists.

| Step | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | Babies | 8 Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.6% | 0.4% | +0.0% | 0.6% | 89.8% | 82.7% | 3.65 | 0.0% | 90.1% | 84.2% | 84.8% | 98.5% | 98.7% | 82.7% |
| Sky Field | 86.4% | 0.4% | +0.8% | 0.5% | 90.3% | 83.2% | 3.74 | 0.0% | 90.8% | 84.1% | 83.2% | 98.5% | 99.0% | 86.4% |
| Budew 1 | 87.2% | 0.4% | +1.6% | 0.5% | 91.0% | 83.9% | 3.94 | 0.0% | 91.5% | 86.2% | 86.8% | 98.5% | 99.3% | 83.9% |
| Budew 2 | 87.8% | 0.4% | +2.2% | 0.5% | 91.3% | 84.9% | 4.05 | 2.2% | 90.0% | 86.7% | 88.5% | 98.7% | 99.2% | 84.9% |
| Budew 3 | 87.4% | 0.4% | +1.8% | 0.5% | 91.1% | 84.2% | 4.15 | 4.2% | 90.8% | 85.2% | 88.5% | 98.9% | 99.1% | 84.2% |
| Budew 4 | 87.8% | 0.4% | +2.2% | 0.5% | 91.5% | 85.0% | 4.21 | 4.8% | 90.4% | 85.8% | 88.8% | 99.2% | 99.5% | 85.0% |

## Bench of 30 HP Pokémon

Babies is the mean number of Benched 30 HP Pokémon at the moment side A attacks.
The last three columns are the share of games with at least one attack at that many (6 Babies is 180, 7 is 210, 8 is 240).

| Step | Babies | Games with Sky Field | 6 Babies | 7 Babies | 8 Babies | Itchy Pollen |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 3.66 | 0.0% | 0.0% | 0.0% | 0.0% | 0.9% |
| Sky Field | 3.73 | 13.3% | 7.4% | 0.0% | 0.0% | 0.7% |
| Budew 1 | 3.92 | 18.2% | 9.7% | 6.2% | 0.0% | 3.9% |
| Budew 2 | 4.08 | 21.2% | 8.2% | 10.7% | 2.3% | 5.2% |
| Budew 3 | 4.16 | 23.0% | 8.0% | 12.0% | 3.5% | 6.3% |
| Budew 4 | 4.24 | 25.0% | 8.4% | 13.1% | 5.7% | 6.8% |

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

Chosen cut is Bursting Balloon. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Bursting Balloon | 87.7% | 91.1% | 3.92 | 91.1% | 85.0% | 86.6% | 98.0% | 98.7% | 87.1% |
| 2 | Ultra Ball | 87.3% | 91.2% | 3.92 | 91.8% | 86.0% | 86.7% | 98.8% | 99.5% | 84.3% |
| 3 | Boss's Orders | 87.1% | 90.9% | 3.93 | 89.9% | 86.4% | 86.4% | 98.8% | 99.2% | 84.5% |
| 4 | Night Stretcher | 86.7% | 90.7% | 3.91 | 90.7% | 86.0% | 85.8% | 99.0% | 99.2% | 83.4% |
| 5 | Rescue Carrier | 86.5% | 90.4% | 3.91 | 90.4% | 85.0% | 85.0% | 98.6% | 98.7% | 84.5% |
| 6 | Iono | 85.8% | 90.1% | 3.87 | 90.6% | 86.7% | 83.9% | 99.0% | 98.9% | 81.5% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Boss's Orders | 88.3% | 91.7% |
| 2 | Bursting Balloon | 88.2% | 91.2% |
| 3 | Ultra Ball | 87.9% | 91.7% |
| 4 | Rescue Carrier | 87.8% | 91.3% |
| 5 | Night Stretcher | 87.7% | 91.3% |
| 6 | Iono | 87.0% | 90.5% |
| 7 | Crushing Hammer | 86.8% | 90.6% |
| 8 | Spiky Energy | 86.6% | 90.7% |
| 9 | Bravery Charm | 86.4% | 90.4% |
| 10 | Buddy-Buddy Poffin | 85.8% | 89.6% |
| 11 | Counter Catcher | 85.8% | 89.9% |
| 12 | Battle Cage | 85.6% | 89.9% |
| 13 | Max Potion | 85.5% | 89.8% |
| 14 | Igglybuff | 85.3% | 89.3% |
| 15 | Mew ex | 85.1% | 89.6% |
| 16 | Professor's Research | 85.0% | 89.2% |
| 17 | Arven | 84.9% | 89.6% |
| 18 | Penny | 84.8% | 89.4% |
| 19 | Nest Ball | 84.7% | 89.2% |
| 20 | Manaphy | 84.3% | 89.2% |
| 21 | Hero's Cape | 83.9% | 88.5% |
| 22 | Mime Jr. | 83.2% | 86.5% |

## Step 3: add Budew 2, every cut

Chosen cut is Night Stretcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 88.4% | 91.7% | 4.08 | 90.4% | 86.8% | 88.3% | 98.3% | 99.5% | 86.8% |
| 2 | Bravery Charm | 88.0% | 91.6% | 4.07 | 91.9% | 86.6% | 87.6% | 99.3% | 99.3% | 85.1% |
| 3 | Ultra Ball | 87.9% | 91.5% | 4.04 | 90.7% | 86.5% | 87.8% | 99.0% | 99.2% | 85.6% |
| 4 | Bursting Balloon | 87.8% | 91.5% | 4.05 | 92.2% | 84.3% | 89.6% | 98.4% | 99.7% | 84.7% |
| 5 | Penny | 87.4% | 91.1% | 4.05 | 91.1% | 85.8% | 86.4% | 98.8% | 99.1% | 85.6% |
| 6 | Nest Ball | 86.9% | 90.8% | 3.99 | 90.7% | 86.5% | 85.8% | 99.1% | 99.1% | 83.8% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Ultra Ball | 89.3% | 92.5% |
| 2 | Night Stretcher | 88.8% | 92.1% |
| 3 | Nest Ball | 88.3% | 91.6% |
| 4 | Penny | 88.0% | 91.7% |
| 5 | Bursting Balloon | 87.9% | 91.8% |
| 6 | Bravery Charm | 87.9% | 91.4% |
| 7 | Counter Catcher | 87.8% | 91.5% |
| 8 | Igglybuff | 87.2% | 90.6% |
| 9 | Mew ex | 87.1% | 91.1% |
| 10 | Battle Cage | 87.1% | 90.8% |
| 11 | Professor's Research | 87.0% | 91.1% |
| 12 | Boss's Orders | 86.8% | 90.7% |
| 13 | Mime Jr. | 86.8% | 89.3% |
| 14 | Buddy-Buddy Poffin | 86.4% | 90.6% |
| 15 | Max Potion | 86.3% | 90.6% |
| 16 | Crushing Hammer | 86.0% | 90.0% |
| 17 | Iono | 85.8% | 90.0% |
| 18 | Arven | 85.5% | 90.0% |
| 19 | Rescue Carrier | 85.5% | 89.9% |
| 20 | Spiky Energy | 85.3% | 89.9% |
| 21 | Manaphy | 84.5% | 89.6% |
| 22 | Hero's Cape | 83.1% | 88.7% |

## Step 4: add Budew 3, every cut

Chosen cut is Crushing Hammer. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Crushing Hammer | 88.8% | 92.1% | 4.16 | 91.0% | 88.6% | 88.9% | 99.0% | 99.7% | 85.6% |
| 2 | Night Stretcher | 88.7% | 92.3% | 4.15 | 92.8% | 87.3% | 90.1% | 99.5% | 99.6% | 84.5% |
| 3 | Boss's Orders | 88.4% | 91.9% | 4.17 | 92.9% | 86.4% | 86.8% | 99.0% | 99.5% | 87.0% |
| 4 | Bursting Balloon | 88.2% | 91.7% | 4.15 | 91.8% | 85.5% | 88.0% | 98.9% | 99.4% | 86.6% |
| 5 | Spiky Energy | 88.1% | 91.8% | 4.16 | 93.0% | 86.4% | 88.2% | 98.9% | 99.3% | 84.8% |
| 6 | Battle Cage | 87.9% | 91.4% | 4.16 | 89.3% | 86.1% | 88.3% | 99.3% | 99.1% | 86.1% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Crushing Hammer | 89.9% | 92.9% |
| 2 | Bursting Balloon | 89.3% | 92.5% |
| 3 | Battle Cage | 89.3% | 92.2% |
| 4 | Night Stretcher | 88.6% | 92.2% |
| 5 | Boss's Orders | 88.5% | 91.8% |
| 6 | Spiky Energy | 88.3% | 91.7% |
| 7 | Counter Catcher | 88.2% | 91.6% |
| 8 | Iono | 88.2% | 91.6% |
| 9 | Nest Ball | 87.8% | 91.6% |
| 10 | Ultra Ball | 87.7% | 91.4% |
| 11 | Rescue Carrier | 87.5% | 91.3% |
| 12 | Professor's Research | 87.4% | 91.0% |
| 13 | Bravery Charm | 87.2% | 90.8% |
| 14 | Mew ex | 87.2% | 91.1% |
| 15 | Penny | 87.1% | 90.6% |
| 16 | Max Potion | 87.1% | 91.1% |
| 17 | Manaphy | 86.5% | 91.0% |
| 18 | Mime Jr. | 86.4% | 89.3% |
| 19 | Hero's Cape | 86.1% | 90.3% |
| 20 | Arven | 85.8% | 89.9% |
| 21 | Buddy-Buddy Poffin | 85.7% | 89.9% |
| 22 | Igglybuff | 85.2% | 89.4% |

## Step 5: add Budew 4, every cut

Chosen cut is Night Stretcher. Screen is 300 games per foe; the confirmed table is 1000 games per foe.

### Confirmed

| Rank | Cut | Weighted | Mean | Babies | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 88.9% | 92.2% | 4.24 | 92.1% | 87.9% | 90.5% | 98.7% | 99.5% | 84.8% |
| 2 | Boss's Orders | 88.6% | 92.0% | 4.23 | 90.6% | 86.5% | 89.2% | 99.0% | 99.8% | 86.7% |
| 3 | Counter Catcher | 88.4% | 92.0% | 4.20 | 92.1% | 86.6% | 89.0% | 99.3% | 99.8% | 85.3% |
| 4 | Crushing Hammer | 87.8% | 91.4% | 4.23 | 90.6% | 85.4% | 88.3% | 99.0% | 99.5% | 85.7% |
| 5 | Ultra Ball | 87.8% | 91.5% | 4.21 | 90.6% | 87.3% | 87.7% | 99.0% | 99.8% | 84.5% |
| 6 | Bursting Balloon | 87.8% | 91.3% | 4.21 | 90.8% | 86.2% | 87.8% | 98.9% | 99.1% | 85.3% |

### Screen

| Rank | Cut | Weighted | Mean |
| ---: | :--- | ---: | ---: |
| 1 | Bursting Balloon | 89.1% | 92.4% |
| 2 | Night Stretcher | 89.1% | 92.5% |
| 3 | Counter Catcher | 89.0% | 92.4% |
| 4 | Ultra Ball | 88.6% | 92.1% |
| 5 | Boss's Orders | 88.3% | 91.8% |
| 6 | Crushing Hammer | 88.2% | 91.9% |
| 7 | Penny | 88.2% | 91.9% |
| 8 | Battle Cage | 88.2% | 91.9% |
| 9 | Arven | 88.1% | 91.7% |
| 10 | Rescue Carrier | 87.9% | 91.7% |
| 11 | Nest Ball | 87.8% | 91.3% |
| 12 | Spiky Energy | 87.5% | 91.4% |
| 13 | Iono | 87.1% | 91.1% |
| 14 | Mew ex | 86.9% | 90.7% |
| 15 | Max Potion | 86.8% | 90.6% |
| 16 | Professor's Research | 86.5% | 90.5% |
| 17 | Mime Jr. | 86.5% | 89.7% |
| 18 | Igglybuff | 86.4% | 90.1% |
| 19 | Buddy-Buddy Poffin | 86.2% | 90.3% |
| 20 | Bravery Charm | 86.0% | 90.3% |
| 21 | Manaphy | 85.2% | 90.2% |
| 22 | Hero's Cape | 84.5% | 89.4% |

## Result

- Set M, re-measured on the current engine: 85.7% weighted (±0.5%); 85.6% on the fresh seed.
- One Sky Field, cutting Night Stretcher: 86.5% (+0.8%); 86.4% on the fresh seed (+0.8%, ±0.5% of the difference).
- Best Budew step on the path: Budew 4 at 88.9%, +2.4% against the Sky Field-only list; on the fresh seed the best is Budew 2 at 87.8%, +1.5%.
- With 4 Budew the worst foe is Mega Starmie ex (Kudo) at 84.8% (Set M 82.7%). The loss weights are frozen from Set M, so a foe that Set M nearly always beats carries a small weight and a collapse there moves the weighted score little.
- With 4 Budew the Bench holds 8 Babies (240) in 5.7% of games, and Sky Field is in play in 25.0%.

The best list on the selection seed is Budew 4: +3.2% against Set M there, and +2.2% on the fresh seed (4.1 standard errors). The fresh seed picks Budew 2. Each step keeps the best of several cuts on the selection seed, so that seed's gain is biased upward and the fresh seed is the unbiased check.

Best list on the path:

```
4 Arven
4 Battle Cage
1 Boss's Orders
3 Bravery Charm
4 Buddy-Buddy Poffin
4 Budew
1 Bursting Balloon
2 Counter Catcher
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
1 Sky Field
2 Spiky Energy
2 Ultra Ball
```
