# Set C: 151 Moon-Viewing Invitation vs 4× Party

Date: 2026-08-25
Seed: `20260819` · 3,000 games / cell
Engine: `family-tcg-monte-carlo` with Family Cup **ex = 2 / Mega ex = 3**

Locked Set C has **no Switch**. Moon-Watching Party (LOR 62) only fires from Active, so the question is whether **MEW 035 / 151 035 Clefairy** (`Moon-Viewing Invitation`: search the deck for up to 3 Clefairy and bench them, cost `[P]`) can replace 1–2 Party engines as a one-attack board dump.

Same-name cap: both prints are **Clefairy**. 3+1 and 2+2 are legal. Invitation has **no Ability**, retreat 1, and does 0 damage (Smack 20 is the other attack).

## Bakeoff (C is row, party vs foe)

D+T = mean of vs D and vs T. Baseline is locked **4× LOR 62**.

| package | A | B | D | S | T | mean | D+T | invite vs D |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **4 party** (locked) | 87.0% | 84.3% | **51.7%** | 84.9% | 46.5% | **70.9%** | **49.1%** | 0.0% |
| 3 party + 1 invite | 87.0% | 85.9% | 38.3% | 88.5% | 47.1% | 69.4% | 42.7% | 1.9% |
| 2 party + 2 invite | 84.9% | 85.1% | 28.3% | 91.6% | 47.0% | 67.4% | 37.6% | 3.2% |

Vs D first / second: 4 party **55.4% / 47.9%**; 3+1 42.2% / 34.3%; 2+2 30.5% / 26.0%.

Invitation actually fires vs D in **~2%** of games (1 copy) and **~3%** (2 copies). Vs T/S it fires much more (11–25%) because those games are not a T2 Demolish race.

## Why it does not catch 4 Party without Switch

The old “not enough turns” read still holds, and cutting Party engines makes it worse.

1. **Invitation is an attack.** Going first cannot dump on T1. Going second, Ogerpon already attached Fighting on T1; after the dump you stay on 60 HP and T2 Demolish prizes it. There is no Switch to Party-then-tank on the same turn.
2. **Party still needs a later Active engine.** The dump puts bodies in play; it does not attach energy. Next turn you retreat (now no energy on the Invitation that just paid `[P]`) into a Party Clefairy and *then* search energy. That is the extra turn the matchup does not have.
3. **Each cut is a lost Party.** Even when Invitation never attacks, 4→3 Party is about **−13 pts vs D**; 3→2 is another **−10**. Fewer Active abilities per game, and Nest Ball already benches engines without spending the attack.
4. **Vs S it looks good** (+3.6 / +6.7) because Floragato does not Demolish a 60 HP Active on curve and Invitation’s fire rate is real. That matchup is already 85%+; it does not pay for the D hole.

Keep **4× LOR 62**. Script: `data/lab/set_c_invitation.py`.
