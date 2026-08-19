# Set C vs Set D — Clefairy / Mewtwo vs Charm Ogerpon

Date: 2026-08-18
Seed: `20260818`
Engine: `family-tcg-monte-carlo`
Strategies: `party` (Set C) vs `demolish` (Set D)
Games: 10,000, random seat

Moon-Watching Party is LOR 62: **for each benched Clefairy, search the deck for 1 Psychic Energy and attach it to that Clefairy.** There is no top-6 look.

## Set C locked 28 (vs Ogerpon)

Original 3 Poffin / 2 Switch retest after the LOR 62 fix: **28.1%** random (29.2% first, 27.0% second). Below 50%, so the trainer package was rebuilt. Pokémon line is unchanged.

| Qty | Card | ID | Notes |
| ---: | --- | --- | --- |
| 4 | Clefairy | swsh11-062 | Psychic, HP60, Basic |
| 2 | Mewtwo ex | sv04-058 | Lightning, HP230, Basic |
| 4 | Clefable | swsh2-75 | Psychic, HP110, Stage 1 |
| 4 | Clefable ex | sv03-082 | Psychic, HP260, Stage 1 |
| 3 | Mega Clefable ex | me03-031 | Psychic, HP320, Stage 1 |
| 4 | Hop | swsh1-165 | Draw 3 |
| 2 | Nest Ball | sv01-181 | Fetch Mewtwo |
| 3 | Energy Search | sv01-172 | Mewtwo / Psychic fuel |
| 1 | Maximum Belt | sv05-154 | +50 vs ex |
| 1 | Arven | sv01-166 | Belt + Item |
| **28** | | | |

No Poffin, Switch, or Beach Court. The 4th Hop beat Beach; Arven stayed so Belt is searchable.

## Play

- Cap Clefairy at **3** (two benched for Party; a 4th 60 HP body is prize fodder and blocks Mega).
- Nest Ball / Energy Search hunt Mewtwo first. Play Mewtwo even if Clefairy is not out yet.
- Never end turn on 60 HP Clefairy if Ogerpon has energy.
- Transfer Charge to load Mewtwo whenever Ogerpon threatens, not only when Photon already KOs.
- Do not Mega while Mewtwo can still eat one 140.
- Lunar Zone if Mewtwo is tanking and two Party engines remain.
- Skip Hop when the deck has ≤8 cards.

## 10,000 games (seed `20260818`, random seat)

| Seat | Original (3 Poffin / 2 Switch) | Locked (4 Hop / 2 Nest) |
| --- | ---: | ---: |
| Clefairy first | 29.2% | **57.9%** |
| Clefairy second | 27.0% | **51.4%** |
| Random | 28.1% | **54.6%** |

Photon still equals the win. Locked list: 7P 19.5%; Mewtwo tanked one 140 in 58.7%; Party energy 1.82/game; deck-out 7.1%. Original Poffin list attached **3.51** Party energy/game but lost on 60 HP prize fodder (Photon 28.1%).

## What was tried

Poffin does **not** empty a top-6 window. It does make Party stronger, and it still loses this matchup because extra Clefairy are Demolish prizes. 3 Hop + 2 Nest + Beach sat at 49.8%. Keeping Beach instead of a 4th Hop, or dropping Arven for Beach, both lost to **4 Hop + 2 Nest + 3 Energy Search + Belt + Arven**.
