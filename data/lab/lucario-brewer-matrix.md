# Chris Brewer Lucario Hariyama vs household 60s

Date: 2026-09-25
Seed: `20260925`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (Lucario is always player A; who goes first is random)
Script: `data/lab/lucario_brewer_matrix.py`
Raw: `data/lab/lucario-brewer-matrix.json`
Elapsed: 74.8s

List is the public Chris Brewer 60 (Limitless, Surge's TCG Vault): 3 Riolu MEG 76, 3 Mega Lucario ex MEG 77, 3 Solrock, 2-2 Makuhita/Hariyama, 2 Lunatone, 1 Meowth ex, 4 Fighting Gong, 4 Premium Power Pro, 4 Poké Pad, 11 Fighting Energy. Baltimore Regional 2026 records him on Lucario Hariyama and does not publish counts. `SET_L60_NAMES`, strategy `aura`.

Mega Lucario ex may evolve the turn Riolu is played. Aura Jab attaches up to 3 Basic Fighting Energy from discard onto the bench. Lunatone's Lunar Cycle discards one Basic Fighting Energy to draw 3 while Solrock is in play. Premium Power Pro is +30 for Fighting attacks this turn. Gravity Mountain is −30 HP on every Stage 2.

30-card Family Cup lists (A, B, C, D, E, F, S, T) are a different deck size and rule preset, so they are not in this array. Their 60-card stretches that already exist (C60, D60, S60, and Carpet G/H) are.

## Lucario win rate

| Foe | Strategy | Overall | Lucario first | Lucario second |
| --- | --- | ---: | ---: | ---: |
| D60 Charm Ogerpon | demolish | **84.7%** | 86.3% | 83.1% |
| Carpet Set H | nuzzle | **73.2%** | 74.6% | 71.8% |
| S60 Floragato | slash | **69.8%** | 71.1% | 68.5% |
| G30 Ambipom | celebration | **69.2%** | 71.4% | 67.1% |
| UNL Dragapult | phantom | **50.2%** | 51.0% | 49.5% |
| T60 Dragapult | phantom | **44.7%** | 44.7% | 44.7% |
| Hedrick Worlds Dragapult | phantom | **43.6%** | 44.9% | 42.2% |
| Carpet Set G | g | **33.3%** | 33.9% | 32.7% |
| C60 Clefairy / Mewtwo | party | **14.3%** | 14.5% | 14.2% |
| M Mew ex baby box | mew_baby | **9.9%** | 7.6% | 12.2% |

The C60 cell was remeasured after `party` stopped using Mewtwo as the closer against Mega Lucario. Same seed, 3,000 games. The other rows are the original run.

Startup is real, and it is not enough against the decks that already beat Dragapult. Mega Brave is 270 for two Fighting Energy, and a Knocked Out Mega Lucario ex gives three prizes. Candy Dragapult and the Hedrick list both take that trade. M's Budew line item-locks Gong, Poké Pad, Ultra Ball, and Premium Power Pro, then attacks for no energy; Lucario wins 296 of 3,000 there.

Ogerpon is the other way around. Mega Lucario ex has no Ability, so Cornerstone Stance does not block Mega Brave, and 270 is a knockout on 210 HP.

## C60 closer vs Lucario

Photon Kinesis is Lightning, and Mewtwo ex is Fighting-weak, so Mega Brave 270 is 540. In this matchup `party` does not play Mewtwo, does not Nest Ball for it, and does not attach to it. The closer is Clefable ex: Wondrous Moon is 170 Psychic, weakness makes that 340, and 340 KOs Mega Lucario ex for 3 prizes. Mega Clefable ex is the second attacker (Shooting Moons, 320 HP so one unboosted Mega Brave does not KO it). Mewtwo is promoted only when Photon actually KOs.

3000 games, seed `20260925`, Lucario as player A: Lucario wins 430 (14.3%). Average prizes 1.89 / 4.74. Attacks: Wondrous Moon 3625, Shooting Moons 2320, Photon Kinesis 415. Mega Lucario ex was Knocked Out 2672 times.

Smoke on the same seed, 400 games, left the other scripts alone: T60 42.8% (published 44.7%), D60 84.5% (published 84.7%).
