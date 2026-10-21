# Set M with Elekid

Elekid (Paradox Rift 59) is a 30 HP Basic with Retreat Cost 0. Crackling Shot costs no Energy and does 30 damage to 1 of the opponent's Pokémon, with no Weakness or Resistance on the Bench. It is one more Benched body for Bouncy Circle, and it Knocks Out a Pokémon with 30 HP or less left without a gust. Mew ex copies it. The play, written before the search, is in `set-m-elekid-strategy.md`; the engine paths are in `tests/test_mew_elekid.py`.

Start list is the best list of `set-m-gust-search.md` (four Sky Field, four Budew, one Counter Catcher, no Boss's Orders). Each step adds one more Elekid, forced up to 4 copies, and every other card name is tried as the cut. Every list on the path is then run on two fresh seeds and pooled, and Set M, the start list, the final list and the best fresh-seed list on the clean seed.

- **Selection seed**: `20261007`; cuts screened on 300 games per foe, best 6 confirmed on 1000
- **Fresh seeds**: `20261105` with 2000 per foe, `20261112` with 3000
- **Clean seed**: `20261029` with 8000 per foe (the clean seed of `set-m-gust-search.md`)
- **Score**: loss-weighted win rate. Weights: t60 16.4%, hedrick 25.2%, c60 24.9%, d60 2.5%, thorns 2.8%, starmie 28.3%
- **Elapsed**: 13264s

## Path (selection seed)

| List | Cut | Weighted | ±1 SE | vs start | Mean | Worst | Games with a shot | Shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Start (no Elekid) | — | 87.6% | 0.5% | +0.0% | 91.0% | 83.9% | 0.00 | 0.00 | 0.01 | 0.01 | 0.00 | 0.03 | 87.2% | 83.9% | 90.2% | 98.5% | 99.5% | 86.8% |
| 1 Elekid | Penny | 88.8% | 0.5% | +1.2% | 92.0% | 86.9% | 0.21 | 0.34 | 0.20 | 0.17 | 0.12 | 0.03 | 88.7% | 87.1% | 90.7% | 99.3% | 99.4% | 86.9% |
| 2 Elekid | Iono | 89.1% | 0.5% | +1.5% | 92.2% | 86.6% | 0.25 | 0.43 | 0.24 | 0.20 | 0.17 | 0.03 | 90.5% | 87.6% | 90.4% | 98.8% | 99.6% | 86.6% |
| 3 Elekid | Penny | 89.3% | 0.5% | +1.6% | 92.5% | 85.5% | 0.26 | 0.49 | 0.25 | 0.20 | 0.19 | 0.02 | 91.7% | 88.2% | 90.9% | 99.3% | 99.4% | 85.5% |
| 4 Elekid | Night Stretcher | 89.6% | 0.5% | +2.0% | 92.5% | 85.7% | 0.29 | 0.58 | 0.28 | 0.22 | 0.22 | 0.03 | 90.6% | 85.7% | 92.6% | 99.1% | 99.3% | 88.0% |

Games with a shot is the share of games in which an Elekid used Crackling Shot. Shots, Snipe KOs, Bench KOs, Elekid KO'd and Boss + Catcher are per game, averaged over the six foes. Snipe KOs count every single-target hit that Knocked something Out, including Mew ex's copies; Bench KOs are the ones on a Benched Pokémon.

## Step 1: 1 Elekid, cut Penny

+1.22% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Penny | 88.8% | 92.0% | 88.7% | 87.1% | 90.7% | 99.3% | 99.4% | 86.9% |
| 2 | Sky Field | 88.8% | 92.0% | 90.3% | 85.0% | 92.0% | 99.2% | 99.2% | 86.6% |
| 3 | Ultra Ball | 88.8% | 92.1% | 90.5% | 87.2% | 91.9% | 98.9% | 99.6% | 84.6% |
| 4 | Mime Jr. | 88.6% | 91.0% | 89.1% | 83.6% | 92.3% | 93.3% | 99.5% | 88.0% |
| 5 | Night Stretcher | 88.4% | 91.8% | 90.0% | 85.1% | 90.5% | 99.0% | 99.4% | 86.7% |
| 6 | Bursting Balloon | 88.4% | 91.8% | 89.8% | 85.4% | 91.2% | 99.0% | 99.4% | 85.8% |

## Step 2: 2 Elekid, cut Iono

+0.25% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Iono | 89.1% | 92.2% | 90.5% | 87.6% | 90.4% | 98.8% | 99.6% | 86.6% |
| 2 | Bursting Balloon | 89.1% | 92.2% | 90.1% | 85.5% | 92.1% | 99.1% | 99.2% | 87.1% |
| 3 | Counter Catcher | 89.0% | 92.2% | 91.4% | 84.3% | 92.6% | 98.8% | 99.3% | 86.6% |
| 4 | Battle Cage | 88.9% | 92.2% | 90.6% | 84.8% | 91.0% | 99.2% | 99.5% | 87.9% |
| 5 | Bravery Charm | 88.8% | 92.0% | 90.2% | 84.7% | 91.0% | 99.1% | 99.6% | 87.6% |
| 6 | Mime Jr. | 88.3% | 90.8% | 90.9% | 85.3% | 91.9% | 92.3% | 99.2% | 85.0% |

## Step 3: 3 Elekid, cut Penny

+0.17% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Penny | 89.3% | 92.5% | 91.7% | 88.2% | 90.9% | 99.3% | 99.4% | 85.5% |
| 2 | Crushing Hammer | 89.1% | 92.2% | 89.9% | 86.7% | 90.8% | 99.4% | 99.3% | 87.4% |
| 3 | Bursting Balloon | 88.9% | 92.1% | 89.9% | 85.6% | 91.0% | 99.5% | 99.3% | 87.3% |
| 4 | Spiky Energy | 88.8% | 92.0% | 89.7% | 85.0% | 91.6% | 99.5% | 99.0% | 87.3% |
| 5 | Mime Jr. | 88.6% | 91.0% | 90.8% | 85.9% | 91.2% | 93.2% | 99.0% | 86.1% |
| 6 | Ultra Ball | 88.4% | 91.8% | 89.8% | 85.6% | 89.8% | 99.0% | 99.7% | 86.8% |

## Step 4: 4 Elekid, cut Night Stretcher

+0.31% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Night Stretcher | 89.6% | 92.5% | 90.6% | 85.7% | 92.6% | 99.1% | 99.3% | 88.0% |
| 2 | Bravery Charm | 89.2% | 92.3% | 90.2% | 87.0% | 90.9% | 98.7% | 99.4% | 87.4% |
| 3 | Nest Ball | 88.7% | 92.0% | 90.5% | 85.4% | 90.9% | 98.9% | 99.3% | 86.9% |
| 4 | Crushing Hammer | 88.5% | 91.8% | 90.2% | 85.6% | 90.9% | 99.1% | 99.3% | 86.0% |
| 5 | Ultra Ball | 88.4% | 91.9% | 90.5% | 85.9% | 89.6% | 99.6% | 99.7% | 86.2% |
| 6 | Iono | 88.1% | 91.7% | 90.8% | 86.1% | 89.8% | 99.2% | 99.6% | 84.8% |

## Fresh seeds

No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.

| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs start | ±1 SE of diff | Mean | Worst | Games with a shot | Shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 86.0% | 84.6% | 85.1% | 0.2% | -3.4% | 0.3% | 89.5% | 78.5% | 0.00 | 0.00 | 0.02 | 0.01 | 0.00 | 0.20 | 88.6% | 78.5% | 86.9% | 98.8% | 99.0% | 84.9% |
| Start (no Elekid) | 88.3% | 88.6% | 88.5% | 0.2% | +0.0% | 0.3% | 91.8% | 84.5% | 0.00 | 0.00 | 0.01 | 0.01 | 0.00 | 0.03 | 89.1% | 84.5% | 90.6% | 99.0% | 99.6% | 87.9% |
| 1 Elekid | 88.5% | 88.6% | 88.5% | 0.2% | +0.0% | 0.3% | 91.8% | 85.4% | 0.21 | 0.35 | 0.20 | 0.17 | 0.13 | 0.03 | 89.6% | 85.4% | 90.9% | 98.6% | 99.5% | 86.7% |
| 2 Elekid | 88.2% | 88.6% | 88.5% | 0.2% | -0.0% | 0.3% | 91.9% | 85.4% | 0.25 | 0.45 | 0.24 | 0.20 | 0.17 | 0.03 | 90.7% | 85.4% | 90.6% | 99.1% | 99.4% | 86.0% |
| 3 Elekid | 88.2% | 88.7% | 88.5% | 0.2% | +0.0% | 0.3% | 91.9% | 85.7% | 0.27 | 0.51 | 0.26 | 0.21 | 0.20 | 0.03 | 90.2% | 85.7% | 91.3% | 99.0% | 99.3% | 85.7% |
| 4 Elekid | 88.3% | 88.4% | 88.4% | 0.2% | -0.1% | 0.3% | 91.8% | 85.5% | 0.29 | 0.57 | 0.28 | 0.22 | 0.23 | 0.03 | 90.3% | 85.5% | 90.1% | 99.2% | 99.6% | 86.3% |

## Clean seed `20261029`

8000 games per foe per list. The last two columns merge this seed with both fresh seeds.

| List | Weighted | ±1 SE | vs Set M | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs Set M |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Set M | 85.1% | 0.2% | +0.00% | 0.3% | 89.4% | 79.8% | 88.2% | 79.8% | 86.1% | 98.7% | 98.8% | 84.8% | 85.1% | +0.00% |
| Start (no Elekid) | 88.6% | 0.2% | +3.42% | 0.3% | 91.7% | 85.1% | 88.0% | 85.1% | 90.8% | 99.1% | 99.5% | 88.0% | 88.5% | +3.40% |
| 3 Elekid | 88.2% | 0.2% | +3.02% | 0.3% | 91.6% | 85.2% | 89.7% | 85.2% | 90.8% | 99.1% | 99.3% | 85.6% | 88.3% | +3.16% |
| 4 Elekid | 88.3% | 0.2% | +3.19% | 0.3% | 91.7% | 85.0% | 89.7% | 85.0% | 91.2% | 99.3% | 99.3% | 86.0% | 88.3% | +3.21% |

## The engine changes alone, clean seed `20261029`

Set M and the start list, same seed and game count as `set-m-gust-search.md`, before and after this change. Neither list plays Elekid. The change is that a single-target hit (Cruel Arrow, also copied by Mime Jr.'s Mimed Games) takes the Knock Out with the most prizes, and that a "1 of your opponent's Pokémon" sentence is one hit, not two (Fezandipiti ex's Cruel Arrow used to land twice).

| List | Before | After | Change | ±1 SE of diff |
| :--- | ---: | ---: | ---: | ---: |
| Set M | 87.0% | 85.1% | -1.84% | 0.3% |
| Start (no Elekid) | 89.6% | 88.6% | -1.04% | 0.2% |

## Result

- Start list: 87.6% on the selection seed, 88.5% on the two fresh seeds pooled, 88.6% on the clean seed.
- 1 Elekid (cut Penny): 88.8% on the selection seed (+1.2% against the start list); two fresh seeds pooled 88.5% (+0.0%, +0.1 standard errors).
- 2 Elekid (cut Iono): 89.1% on the selection seed (+1.5% against the start list); two fresh seeds pooled 88.5% (-0.0%, -0.1 standard errors).
- 3 Elekid (cut Penny): 89.3% on the selection seed (+1.6% against the start list); two fresh seeds pooled 88.5% (+0.0%, +0.1 standard errors).
- 4 Elekid (cut Night Stretcher): 89.6% on the selection seed (+2.0% against the start list); two fresh seeds pooled 88.4% (-0.1%, -0.4 standard errors).
- Start (no Elekid) against Set M: clean seed +3.42% (+13.0 standard errors); all three seeds +3.40% (+16.5).
- 3 Elekid against Set M: clean seed +3.02% (+11.4 standard errors); all three seeds +3.16% (+15.2).
- 4 Elekid against Set M: clean seed +3.19% (+12.1 standard errors); all three seeds +3.21% (+15.5).
- 3 Elekid against the start list: clean seed -0.40% (-1.6 standard errors); all three seeds -0.24% (-1.2).
- 4 Elekid against 3 Elekid, the best list on the two fresh seeds: clean seed +0.17% (+0.7 standard errors).

No Elekid count separates from the start list. On the two fresh seeds the highest is 3 Elekid at +0.02% (+0.1 standard errors). On the clean seed it is -0.40% (-1.6 standard errors), and on all three seeds -0.24% (-1.2). The selection seed keeps the best of many cuts at every step, so its climb is biased upward. The start list, with no Elekid, stays the one to play.

Highest list on the two fresh seeds (3 Elekid). The clean seed was not used to pick it, and the paragraph above is what decides whether to play it:

```
4 Arven
4 Battle Cage
2 Bravery Charm
4 Buddy-Buddy Poffin
4 Budew
1 Bursting Balloon
1 Counter Catcher
3 Crushing Hammer
3 Elekid
1 Hero's Cape
4 Igglybuff
3 Iono
1 Manaphy
3 Max Potion
3 Mew ex
2 Mime Jr.
4 Nest Ball
1 Night Stretcher
2 Professor's Research
2 Rescue Carrier
4 Sky Field
2 Spiky Energy
2 Ultra Ball
```
