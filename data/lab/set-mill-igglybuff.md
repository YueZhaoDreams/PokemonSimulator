# Mill, Sleepy Voice Igglybuff

Printed text: once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends. The sentence does not say the Active Spot, so a Benched Igglybuff can use it.

Undersea Tunnel, Sleepy Lost, Eeeeeeek, and the first Playground stay ahead of the coin. The coin replaces those attacks only when the hit ignores effects on the Active, as Demolish does. A turn with none of those attacks still flips when their hit would land. One Igglybuff is benched once a Wiglett is already in play or in hand. Poffin takes it after the wall and the first Wiglett. Level Ball still finds Wugtrio. Slumbering Forest is already in this list, so the wake check is two coins.

Each step tries every other card as the one copy to replace with one Sleepy Voice Igglybuff. The cut with the higher Sisters-weighted win rate is kept, and the next copy is tried the same way.

- **Seed**: `20261029`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen Sisters loss weights. The same weights as the Doll lock.
- **Plays**: every Igglybuff that entered play, including Set M's Bouncy Circle print. The locked row is not zero for that reason. Flips count only Sleepy Voice.
- **Elapsed**: 2862.4s

This sample is not the 1000-game holdout.

## Lock

The search's highest row cut Manaphy (44.9%, +3.4, about 5.0 SE). The locked 60 keeps Manaphy and replaces Boss's Orders. That row is 44.6% (+3.1, gap SE 0.69, about 4.5 SE). Mega Starmie is 36.4% → 40.8% on the Boss cut and 36.4% → 32.0% on the Manaphy cut. A second copy was measured only after the Manaphy cut, so this lock stops at one Igglybuff.

## Path

| Step | Copies | Cut | Weighted | ± | Mean | Worst | Delta | Flips | Heads | Plays | Mill cards |
| :--- | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| locked | 0 | — | 41.4% | 0.5% | 56.5% | 7.8% | +0.0% | 0.00 | 0.00 | 0.45 | 14.20 |
| 1 Igglybuff | 1 | Manaphy | 44.9% | 0.5% | 59.2% | 12.8% | +3.4% | 1.86 | 0.91 | 1.20 | 14.34 |

## Decision

The greedy step kept −Manaphy at 44.9% (+3.4%, 5.0 SE). The lock accepts the Boss's Orders row instead, so Wave Veil stays in the 60. The counts below are the Manaphy path the search measured, not the locked list.

Counts:

- Pichu ×1
- Mime Jr. ×1
- Cleffa ×1
- Wiglett ×4
- Wugtrio ×4
- Victini ×1
- Slumbering Forest ×1
- Neutralization Zone ×1
- Buddy-Buddy Poffin ×4
- Level Ball ×4
- Rescue Carrier ×3
- Lillie's Poké Doll ×1
- Crushing Hammer ×4
- Counter Catcher ×2
- Miss Fortune Sisters ×2
- Wally ×3
- Boss's Orders ×1
- Team Rocket's Handiwork ×2
- Colress's Tenacity ×4
- Double Turbo Energy ×4
- Water Energy ×3
- Ignition Energy ×4
- Reversal Energy ×4
- Igglybuff ×1

## Step 1

List entering this step: weighted 41.4% ± 0.5%. Each row replaces one copy of that card with one Igglybuff.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flips | Heads | Plays | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Manaphy | 1 | 44.9% | 0.5% | 59.2% | 12.8% | +3.4% | 1.86 | 0.91 | 1.20 | 14.34 |
| Boss's Orders | 1 | 44.6% | 0.5% | 58.6% | 12.5% | +3.1% | 1.88 | 0.94 | 1.19 | 14.26 |
| Counter Catcher | 2 | 44.0% | 0.5% | 58.2% | 12.4% | +2.6% | 1.88 | 0.93 | 1.19 | 14.24 |
| Wugtrio | 4 | 43.8% | 0.5% | 58.3% | 11.0% | +2.4% | 1.86 | 0.92 | 1.18 | 13.93 |
| Rescue Carrier | 3 | 43.8% | 0.5% | 58.3% | 11.1% | +2.3% | 1.85 | 0.92 | 1.17 | 14.00 |
| Team Rocket's Handiwork | 2 | 43.6% | 0.5% | 58.2% | 10.6% | +2.2% | 1.86 | 0.93 | 1.19 | 13.83 |
| Mime Jr. | 1 | 43.6% | 0.5% | 58.7% | 10.9% | +2.2% | 1.92 | 0.95 | 1.20 | 14.18 |
| Water Energy | 3 | 43.4% | 0.5% | 57.8% | 10.8% | +2.0% | 1.89 | 0.93 | 1.19 | 13.86 |
| Wally | 3 | 43.3% | 0.5% | 57.8% | 9.6% | +1.8% | 1.90 | 0.95 | 1.19 | 13.93 |
| Colress's Tenacity | 4 | 43.2% | 0.5% | 57.2% | 12.1% | +1.8% | 1.91 | 0.96 | 1.18 | 13.87 |
| Crushing Hammer | 4 | 43.2% | 0.5% | 57.9% | 9.6% | +1.7% | 1.88 | 0.93 | 1.19 | 13.97 |
| Lillie's Poké Doll | 1 | 42.9% | 0.5% | 57.6% | 9.8% | +1.5% | 1.78 | 0.89 | 1.19 | 14.22 |
| Slumbering Forest | 1 | 42.8% | 0.5% | 57.9% | 7.0% | +1.4% | 1.91 | 0.95 | 1.18 | 14.17 |
| Double Turbo Energy | 4 | 42.8% | 0.5% | 57.4% | 10.5% | +1.4% | 1.92 | 0.95 | 1.20 | 13.71 |
| Miss Fortune Sisters | 2 | 42.6% | 0.5% | 57.6% | 9.8% | +1.2% | 1.83 | 0.90 | 1.19 | 14.28 |
| Level Ball | 4 | 42.5% | 0.5% | 57.3% | 9.8% | +1.0% | 1.82 | 0.92 | 1.16 | 13.67 |
| Wiglett | 4 | 42.4% | 0.5% | 57.0% | 10.4% | +1.0% | 1.98 | 0.99 | 1.20 | 13.37 |
| Cleffa | 1 | 42.4% | 0.5% | 57.2% | 12.9% | +0.9% | 1.94 | 0.98 | 1.20 | 13.54 |
| Pichu | 1 | 42.3% | 0.5% | 57.2% | 10.8% | +0.9% | 1.84 | 0.93 | 1.15 | 13.74 |
| Neutralization Zone | 1 | 42.2% | 0.5% | 54.7% | 17.5% | +0.8% | 1.86 | 0.93 | 1.15 | 13.97 |
| Reversal Energy | 4 | 41.9% | 0.5% | 56.9% | 11.1% | +0.4% | 1.95 | 0.97 | 1.18 | 13.53 |
| Ignition Energy | 4 | 41.9% | 0.5% | 56.9% | 8.6% | +0.4% | 1.90 | 0.94 | 1.19 | 13.57 |
| Buddy-Buddy Poffin | 4 | 41.7% | 0.5% | 56.5% | 8.1% | +0.2% | 1.73 | 0.86 | 1.13 | 13.54 |
| Victini | 1 | 41.0% | 0.5% | 56.3% | 8.9% | -0.4% | 1.97 | 0.98 | 1.23 | 13.31 |

Kept −Manaphy at 44.9% (+3.4%, 5.0 SE). Sleepy Voice flips 1.86 times a game and lands heads 0.91 times.

| Foe | Baseline | Kept | Delta |
| :--- | ---: | ---: | ---: |
| Dragapult ex (T60) | 73.1% | 74.6% | +1.5% |
| Hedrick Worlds Dragapult | 58.6% | 61.9% | +3.2% |
| Unlimited Dragapult | 84.2% | 86.9% | +2.6% |
| Cornerstone Ogerpon (D60) | 7.8% | 12.8% | +5.0% |
| Wo-Chien / Floragato (S60) | 71.0% | 72.0% | +1.0% |
| Gholdengo (G) | 30.1% | 43.1% | +13.0% |
| Clefairy / Mewtwo (C60) | 39.2% | 40.4% | +1.1% |
| Set M (Mew ex) | 21.1% | 23.9% | +2.8% |
| Mega Starmie ex (Kudo) | 36.4% | 32.0% | -4.4% |
| Lucario Hariyama | 82.2% | 82.5% | +0.2% |
| Iron Thorns ex | 91.0% | 92.8% | +1.7% |
| Carpet Set H | 42.5% | 51.2% | +8.7% |
| Ambipom Hand Fling | 97.1% | 96.1% | -1.0% |

## Step 2

List entering this step: weighted 44.9% ± 0.5%. Each row replaces one copy of that card with one Igglybuff.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta | Flips | Heads | Plays | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pichu | 1 | 44.3% | 0.5% | 58.7% | 13.5% | -0.5% | 2.28 | 1.14 | 1.35 | 14.08 |
| Lillie's Poké Doll | 1 | 44.2% | 0.5% | 59.5% | 12.9% | -0.6% | 2.18 | 1.08 | 1.36 | 14.34 |
| Water Energy | 3 | 44.1% | 0.5% | 58.4% | 12.1% | -0.7% | 2.32 | 1.16 | 1.36 | 13.93 |
| Boss's Orders | 1 | 44.0% | 0.5% | 58.6% | 12.4% | -0.9% | 2.26 | 1.10 | 1.38 | 14.36 |
| Crushing Hammer | 4 | 43.9% | 0.5% | 58.7% | 9.8% | -1.0% | 2.30 | 1.15 | 1.37 | 14.29 |
| Double Turbo Energy | 4 | 43.9% | 0.5% | 58.2% | 11.2% | -1.0% | 2.32 | 1.15 | 1.39 | 13.91 |
| Wally | 3 | 43.8% | 0.5% | 58.6% | 13.0% | -1.0% | 2.36 | 1.19 | 1.38 | 13.97 |
| Rescue Carrier | 3 | 43.6% | 0.5% | 58.7% | 10.2% | -1.3% | 2.29 | 1.14 | 1.37 | 14.01 |
| Miss Fortune Sisters | 2 | 43.5% | 0.5% | 58.6% | 9.0% | -1.3% | 2.33 | 1.16 | 1.38 | 14.45 |
| Buddy-Buddy Poffin | 4 | 43.3% | 0.5% | 58.0% | 11.0% | -1.5% | 2.19 | 1.10 | 1.35 | 13.81 |
| Counter Catcher | 2 | 43.3% | 0.5% | 58.1% | 9.9% | -1.5% | 2.29 | 1.14 | 1.39 | 14.20 |
| Level Ball | 4 | 43.3% | 0.5% | 58.1% | 11.9% | -1.6% | 2.28 | 1.13 | 1.37 | 13.82 |
| Team Rocket's Handiwork | 2 | 43.2% | 0.5% | 57.9% | 14.1% | -1.7% | 2.34 | 1.17 | 1.38 | 13.79 |
| Colress's Tenacity | 4 | 43.1% | 0.5% | 57.8% | 13.2% | -1.7% | 2.34 | 1.16 | 1.38 | 13.97 |
| Slumbering Forest | 1 | 42.9% | 0.5% | 58.1% | 4.9% | -1.9% | 2.31 | 1.15 | 1.36 | 14.25 |
| Reversal Energy | 4 | 42.9% | 0.5% | 57.7% | 13.1% | -2.0% | 2.36 | 1.18 | 1.37 | 13.63 |
| Wugtrio | 4 | 42.9% | 0.5% | 57.9% | 10.4% | -2.0% | 2.39 | 1.18 | 1.39 | 13.79 |
| Ignition Energy | 4 | 42.9% | 0.5% | 58.1% | 12.5% | -2.0% | 2.34 | 1.16 | 1.38 | 13.75 |
| Mime Jr. | 1 | 42.9% | 0.5% | 57.7% | 10.0% | -2.0% | 2.37 | 1.18 | 1.38 | 14.26 |
| Wiglett | 4 | 42.7% | 0.5% | 57.5% | 12.5% | -2.2% | 2.39 | 1.18 | 1.41 | 13.52 |
| Cleffa | 1 | 42.4% | 0.5% | 57.5% | 10.9% | -2.5% | 2.28 | 1.14 | 1.36 | 13.79 |
| Neutralization Zone | 1 | 41.8% | 0.5% | 54.8% | 17.1% | -3.0% | 2.25 | 1.13 | 1.34 | 13.99 |
| Victini | 1 | 41.4% | 0.5% | 56.9% | 8.6% | -3.5% | 2.35 | 1.18 | 1.41 | 13.41 |

No cut beat this list. Best cut is Pichu: weighted 44.3% vs 44.9% (-0.5%).
