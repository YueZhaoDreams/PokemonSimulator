# Set E vs Set D — Ogerpon hunter

Date: 2026-08-19
Seed: `20260818`
Engine: `family-tcg-monte-carlo`
Strategies: `party` (Set E) vs `demolish` (Set D)
Games: 10,000

Set E is the specialized **counter to Set D** Charm Ogerpon. Cornerstone Stance
blocks Pokémon that have an Ability; **Mewtwo ex has no Ability**, so Photon Kinesis
connects. Charm Ogerpon is 260 HP — 9 Psychic = 280 OHKO, or **7 Psychic + Maximum Belt = 270**.

## Locked 28

| Qty | Card | Role |
| ---: | --- | --- |
| 4 | Clefairy | Moon-Watching Party engine (LOR 62 full-deck search) |
| 2 | Mewtwo ex | Closer / 230 HP tank (no Ability) |
| 4 | Clefable | Prankish tempo + Psychic fuel |
| 3 | Clefable ex | Lunar Zone |
| 3 | Mega Clefable ex | Wall (two Demolishs of construction time) |
| 4 | Hop | Draw 3 |
| 2 | Nest Ball | Fetch Mewtwo |
| 3 | Energy Search | Mewtwo / Psychic tutor under Rule B |
| 2 | Maximum Belt | +50 vs ex (7P line) |
| 1 | Arven | Belt + Item |
| **28** | | |

Diff vs Set C baseline: **−1 Clefable ex, +1 Maximum Belt**. The second Belt is the
seat-stable upgrade for the Ogerpon race.

## 10,000 games (seed `20260818`)

| Seat | Set E (2 Belt) | Set C baseline (1 Belt) |
| --- | ---: | ---: |
| E/C first | **68.5%** | 56.9% |
| E/C second | **61.5%** | 50.4% |
| Random | **65.0%** | 53.7% |

Average turns (random): 9.7.

## Why it beats Ogerpon

1. Nest Ball / Energy Search → Mewtwo Active as a 230 HP Demolish sponge.
2. Party loads Psychic Energy onto benched Clefairy (Rule B: Clefable lines are Psychic Energy).
3. Transfer Charge + Belt when short of 9 Psychic.
4. Photon Kinesis 270–280 takes Charm Ogerpon in one hit — Acerola never fires.

## Tried and rejected (same seed, 2k–3k)

| List | Random vs D |
| --- | ---: |
| Orthworm Charm / thin-deck Crunch | ~11% |
| 3 Mewtwo / 4 Nest / −Mega | ~38% |
| Set C + Switch (−1 Hop) | ~49% |
| Set C + Bravery Charm (−1 Hop) | ~44% |
| Set C locked (1 Belt) | ~53% |
| **Set E (2 Belt)** | **~65%** |
