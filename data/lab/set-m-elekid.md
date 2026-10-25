# Set M with Elekid

Elekid (Paradox Rift 59) is a 30 HP Basic with Retreat Cost 0. Crackling Shot costs no Energy and does 30 damage to 1 of the opponent's Pokémon, with no Weakness or Resistance on the Bench. It is one more Benched body for Bouncy Circle. The attack is a finisher: it is used only when the Knock Out wins the game, or it takes at least 2 prizes the Active attack cannot take this turn. Mew ex copies it and stays Active. Elekid itself goes Active only when Mew ex cannot use the attack and that Knock Out is extreme. The play, written before the search, is in `set-m-elekid-strategy.md`; the engine paths are in `tests/test_mew_elekid.py`.

Start list is the locked Set M: four Team Rocket's Petrel, one Junk Arm, three Sky Field, four Budew, no Ultra Ball, no Penny, no Boss's Orders. Each step adds one more Elekid, forced up to 4 copies, and every other card name is tried as the cut. Every list on the path is then run on two fresh seeds and pooled, and the start list, the final list and the best fresh-seed list go to the clean seed.

- **Selection seed**: `20261007`; cuts screened on 300 games per foe, best 6 confirmed on 1000
- **Fresh seeds**: `20261105` with 2000 per foe, `20261112` with 3000
- **Clean seed**: `20261029` with 8000 per foe
- **Score**: loss-weighted win rate, weights frozen from the locked list on the selection seed. Weights: t60 20.3%, hedrick 37.7%, c60 16.0%, d60 1.9%, thorns 0.8%, starmie 23.3%
- **Elapsed**: 17942s

## Path (selection seed)

| List | Cut | Weighted | ±1 SE | vs start | Mean | Worst | Elekid games | Elekid shots | Mew shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Start (no Elekid) | — | 90.1% | 0.5% | +0.0% | 93.8% | 85.9% | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.07 | 92.4% | 85.9% | 94.0% | 99.3% | 99.7% | 91.3% |
| 1 Elekid | Manaphy | 91.1% | 0.5% | +0.9% | 94.0% | 84.2% | 0.01 | 0.01 | 0.03 | 0.04 | 0.03 | 0.12 | 0.06 | 93.4% | 91.6% | 95.3% | 99.5% | 99.9% | 84.2% |
| 2 Elekid | Counter Catcher | 92.2% | 0.4% | +2.1% | 94.6% | 88.6% | 0.01 | 0.01 | 0.04 | 0.05 | 0.04 | 0.15 | 0.00 | 94.9% | 92.0% | 93.6% | 99.0% | 99.6% | 88.6% |
| 3 Elekid | Battle Cage | 91.8% | 0.5% | +1.7% | 94.5% | 87.1% | 0.01 | 0.01 | 0.03 | 0.04 | 0.04 | 0.20 | 0.00 | 94.2% | 91.2% | 95.8% | 99.6% | 99.3% | 87.1% |
| 4 Elekid | Mime Jr. | 91.8% | 0.5% | +1.6% | 93.8% | 86.9% | 0.02 | 0.02 | 0.04 | 0.05 | 0.04 | 0.23 | 0.00 | 93.5% | 91.7% | 95.9% | 95.5% | 99.3% | 86.9% |

Elekid games is the share of games in which an Elekid itself used Crackling Shot. Elekid shots and Mew shots are per game, averaged over the six foes. Mew ex is the one that copies the shot when it can. Snipe KOs count every Crackling Shot that Knocked something Out; Bench KOs are the ones on a Benched Pokémon. Boss + Catcher is per game.

## Step 1: 1 Elekid, cut Manaphy

+0.91% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Manaphy | 91.1% | 94.0% | 93.4% | 91.6% | 95.3% | 99.5% | 99.9% | 84.2% |
| 2 | Counter Catcher | 90.9% | 93.9% | 88.3% | 89.8% | 95.1% | 99.6% | 99.8% | 91.0% |
| 3 | Battle Cage | 90.2% | 93.4% | 88.8% | 88.5% | 93.3% | 99.3% | 99.7% | 90.9% |
| 4 | Sky Field | 90.2% | 93.6% | 91.0% | 87.5% | 94.7% | 99.3% | 99.4% | 89.6% |
| 5 | Rescue Carrier | 89.2% | 93.0% | 90.9% | 86.9% | 93.9% | 99.1% | 99.7% | 87.2% |
| 6 | Nest Ball | 89.0% | 92.8% | 90.5% | 86.2% | 93.4% | 99.1% | 99.7% | 87.9% |

## Step 2: 2 Elekid, cut Counter Catcher

+1.19% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher | 92.2% | 94.6% | 94.9% | 92.0% | 93.6% | 99.0% | 99.6% | 88.6% |
| 2 | Night Stretcher | 91.5% | 94.2% | 95.4% | 91.5% | 93.6% | 98.9% | 99.8% | 85.8% |
| 3 | Rescue Carrier | 91.3% | 94.0% | 95.2% | 91.3% | 93.0% | 99.1% | 99.8% | 85.6% |
| 4 | Battle Cage | 91.3% | 94.1% | 95.2% | 91.1% | 94.3% | 99.5% | 99.5% | 85.0% |
| 5 | Bravery Charm | 90.4% | 93.5% | 92.9% | 90.4% | 93.4% | 99.5% | 99.6% | 85.3% |
| 6 | Hero's Cape | 88.8% | 92.5% | 93.7% | 87.9% | 90.6% | 99.6% | 99.7% | 83.3% |

## Step 3: 3 Elekid, cut Battle Cage

-0.43% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Battle Cage | 91.8% | 94.5% | 94.2% | 91.2% | 95.8% | 99.6% | 99.3% | 87.1% |
| 2 | Mime Jr. | 91.4% | 93.4% | 95.0% | 91.5% | 94.4% | 94.5% | 99.4% | 85.6% |
| 3 | Spiky Energy | 91.2% | 94.1% | 92.8% | 91.1% | 95.2% | 99.5% | 99.4% | 86.4% |
| 4 | Sky Field | 91.2% | 94.0% | 95.1% | 91.5% | 93.4% | 99.6% | 99.5% | 84.8% |
| 5 | Iono | 91.0% | 93.9% | 95.1% | 91.1% | 94.4% | 99.5% | 99.3% | 84.1% |
| 6 | Bursting Balloon | 91.0% | 93.9% | 94.6% | 90.5% | 94.1% | 99.4% | 99.4% | 85.5% |

## Step 4: 4 Elekid, cut Mime Jr.

-0.06% against the list before on the selection seed.

Confirmed cuts:

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Mime Jr. | 91.8% | 93.8% | 93.5% | 91.7% | 95.9% | 95.5% | 99.3% | 86.9% |
| 2 | Junk Arm | 91.7% | 94.4% | 94.0% | 90.5% | 94.6% | 99.6% | 99.3% | 88.6% |
| 3 | Arven | 91.5% | 94.1% | 93.4% | 91.2% | 94.4% | 99.3% | 99.0% | 87.5% |
| 4 | Bursting Balloon | 91.4% | 94.1% | 94.0% | 91.7% | 95.2% | 99.3% | 99.2% | 85.2% |
| 5 | Max Potion | 91.1% | 94.0% | 93.0% | 90.2% | 94.7% | 99.1% | 99.8% | 87.5% |
| 6 | Night Stretcher | 91.0% | 94.0% | 94.0% | 89.9% | 93.6% | 99.4% | 99.7% | 87.2% |

## Fresh seeds

No list was chosen on these seeds. The pooled columns merge both, and differences use the unpaired standard error.

| List | Seed 1 | Seed 2 | Pooled | ±1 SE | vs start | ±1 SE of diff | Mean | Worst | Elekid games | Elekid shots | Mew shots | Snipe KOs | Bench KOs | Elekid KO'd | Boss + Catcher | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Start (no Elekid) | 89.7% | 90.2% | 90.0% | 0.2% | +0.0% | 0.3% | 93.5% | 87.3% | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.06 | 90.3% | 87.3% | 94.3% | 99.3% | 99.7% | 90.0% |
| 1 Elekid | 90.2% | 91.2% | 90.8% | 0.2% | +0.9% | 0.3% | 93.8% | 84.6% | 0.01 | 0.01 | 0.03 | 0.04 | 0.03 | 0.12 | 0.07 | 93.9% | 90.8% | 94.6% | 99.2% | 99.6% | 84.6% |
| 2 Elekid | 90.9% | 91.4% | 91.2% | 0.2% | +1.3% | 0.3% | 94.0% | 85.7% | 0.01 | 0.01 | 0.03 | 0.05 | 0.04 | 0.16 | 0.00 | 94.1% | 91.2% | 94.2% | 99.3% | 99.5% | 85.7% |
| 3 Elekid | 91.1% | 91.4% | 91.2% | 0.2% | +1.3% | 0.3% | 94.1% | 86.3% | 0.01 | 0.01 | 0.04 | 0.05 | 0.04 | 0.19 | 0.00 | 93.7% | 90.8% | 94.9% | 99.4% | 99.5% | 86.3% |
| 4 Elekid | 91.3% | 91.4% | 91.3% | 0.2% | +1.4% | 0.3% | 93.5% | 87.0% | 0.01 | 0.01 | 0.04 | 0.05 | 0.04 | 0.23 | 0.00 | 94.2% | 90.7% | 94.7% | 95.5% | 99.2% | 87.0% |

## Clean seed `20261029`

8000 games per foe per list. The first row is the locked list. The last two columns merge this seed with both fresh seeds.

| List | Weighted | ±1 SE | vs locked | ±1 SE of diff | Mean | Worst | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Three seeds | vs locked |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Start (no Elekid) | 89.8% | 0.2% | +0.00% | 0.3% | 93.4% | 86.7% | 90.8% | 86.7% | 94.2% | 99.1% | 99.8% | 90.0% | 89.9% | +0.00% |
| 4 Elekid | 91.1% | 0.2% | +1.27% | 0.2% | 93.3% | 86.6% | 93.5% | 90.6% | 94.9% | 95.0% | 99.2% | 86.6% | 91.2% | +1.30% |

## Result

- Locked Set M, no Elekid: 90.1% on the selection seed, 90.0% on the two fresh seeds pooled, 89.8% on the clean seed.
- 1 Elekid (cut Manaphy): 91.1% on the selection seed (+0.9% against the start list); two fresh seeds pooled 90.8% (+0.9%, +2.7 standard errors).
- 2 Elekid (cut Counter Catcher): 92.2% on the selection seed (+2.1% against the start list); two fresh seeds pooled 91.2% (+1.3%, +4.1 standard errors).
- 3 Elekid (cut Battle Cage): 91.8% on the selection seed (+1.7% against the start list); two fresh seeds pooled 91.2% (+1.3%, +4.1 standard errors).
- 4 Elekid (cut Mime Jr.): 91.8% on the selection seed (+1.6% against the start list); two fresh seeds pooled 91.3% (+1.4%, +4.4 standard errors).
- 1 Elekid against Start (no Elekid) on the two fresh seeds: +0.85% (+2.7 standard errors).
- 2 Elekid against 1 Elekid on the two fresh seeds: +0.41% (+1.4 standard errors).
- 3 Elekid against 2 Elekid on the two fresh seeds: +0.02% (+0.1 standard errors).
- 4 Elekid against 3 Elekid on the two fresh seeds: +0.08% (+0.3 standard errors).
- 4 Elekid against the start list: clean seed +1.27% (+5.2 standard errors); all three seeds +1.30% (+6.8 standard errors).

4 Elekid is the best list on the two fresh seeds, and it is better than the start list on all three seeds. The selection seed keeps the best of many cuts at every step, so its gains are biased upward and the fresh seeds decide.

Best list on the two fresh seeds (4 Elekid); the clean seed above was not used to pick it:

```
4 Arven
3 Battle Cage
2 Bravery Charm
4 Buddy-Buddy Poffin
4 Budew
1 Bursting Balloon
3 Crushing Hammer
4 Elekid
1 Hero's Cape
4 Igglybuff
4 Iono
1 Junk Arm
3 Max Potion
3 Mew ex
1 Mime Jr.
4 Nest Ball
1 Night Stretcher
2 Professor's Research
2 Rescue Carrier
3 Sky Field
2 Spiky Energy
4 Team Rocket's Petrel
```
