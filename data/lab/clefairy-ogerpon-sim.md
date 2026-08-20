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
| 3 | Hop | swsh1-165 | Draw 3 |
| 2 | Nest Ball | sv01-181 | Fetch Mewtwo |
| 3 | Energy Search | sv01-172 | Mewtwo / Psychic fuel |
| 1 | Maximum Belt | sv05-154 | ACE SPEC +50 vs ex |
| 1 | Tool Box | sv01-196 | Top-7 Tool tutor |
| 1 | Arven | sv01-166 | Belt + Item |
| **28** | | | |

No Poffin, Switch, or Beach Court. **Maximum Belt is ACE SPEC (one copy).** Tool Box + Arven dig for it. Diff vs the prior 4 Hop lock: −1 Hop, +1 Tool Box.

## Play

- Cap Clefairy at **3** (two benched for Party; a 4th 60 HP body is prize fodder and blocks Mega).
- Nest Ball / Energy Search hunt Mewtwo first. Play Mewtwo even if Clefairy is not out yet.
- Never end turn on 60 HP Clefairy if Ogerpon has energy.
- Transfer Charge to load Mewtwo whenever Ogerpon threatens, not only when Photon already KOs.
- Do not Mega while Mewtwo can still eat one 140.
- Lunar Zone if Mewtwo is tanking and two Party engines remain.
- Skip Hop when the deck has ≤8 cards.

## 10,000 games (seed `20260818`, random seat)

| Seat | Original (3 Poffin / 2 Switch) | Prior (4 Hop) | Locked (3 Hop + Tool Box) |
| --- | ---: | ---: | ---: |
| Clefairy first | 29.2% | 56.9% | **56.9%** |
| Clefairy second | 27.0% | 50.4% | **50.8%** |
| Random | 28.1% | 53.7% | **54.1%** |

Photon still equals the win. ACE SPEC stays at one Belt — a second Belt is illegal.

## 30-card Family Cup (2026-08-20)

Family Cup is now 30. This list added **2 Psychic Energy** (Party's printed search). Pokémon line and ACE SPEC Belt are unchanged.

3,000 games, seed `20260819`, `party` vs `demolish`: **60.2%** random (62.1% first, 58.3% second). The 28-card Tool Box lock was 54.9% on this seed.

## What was tried

Poffin does **not** empty a top-6 window. It does make Party stronger, and it still loses this matchup because extra Clefairy are Demolish prizes. 3 Hop + 2 Nest + Beach sat at 49.8%. Two Maximum Belts are illegal ACE SPEC. Orthworm Charm lines lost this race (~11%).
