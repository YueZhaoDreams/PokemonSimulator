# Chris Brewer Lucario Hariyama vs household 60s

Date: 2026-09-26
Seed: `20260925`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (Lucario is always player A; who goes first is random)
Script: `data/lab/lucario_brewer_matrix.py`
Raw: `data/lab/lucario-brewer-matrix.json`
Elapsed: 69.1s

List is the public Chris Brewer 60 (Limitless, Surge's TCG Vault): 3 Riolu MEG 76, 3 Mega Lucario ex MEG 77, 3 Solrock, 2-2 Makuhita/Hariyama, 2 Lunatone, 1 Meowth ex, 4 Fighting Gong, 4 Premium Power Pro, 4 Poké Pad, 11 Fighting Energy. Baltimore Regional 2026 records him on Lucario Hariyama and does not publish counts. `SET_L60_NAMES`, strategy `aura`.

Mega Lucario ex may evolve the turn Riolu is played. Aura Jab attaches up to 3 Basic Fighting Energy from discard onto the bench. Lunatone's Lunar Cycle discards one Basic Fighting Energy to draw 3 while Solrock is in play. Premium Power Pro is +30 for Fighting attacks this turn. Gravity Mountain is −30 HP on every Stage 2.

30-card Family Cup lists (A, B, C, D, E, F, S, T) are a different deck size and rule preset, so they are not in this array. Their 60-card stretches that already exist (C60, D60, S60, and Carpet G/H) are.

## Lucario win rate

| Foe | Strategy | Overall | Lucario first | Lucario second |
| --- | --- | ---: | ---: | ---: |
| D60 Charm Ogerpon | demolish | **83.1%** | 85.1% | 81.1% |
| Carpet Set H | nuzzle | **74.9%** | 77.0% | 72.9% |
| S60 Floragato | slash | **69.9%** | 72.0% | 67.7% |
| G30 Ambipom | celebration | **69.1%** | 70.7% | 67.4% |
| UNL Dragapult | phantom | **50.3%** | 52.9% | 47.7% |
| Hedrick Worlds Dragapult | phantom | **44.1%** | 45.0% | 43.0% |
| T60 Dragapult | phantom | **43.5%** | 45.6% | 41.4% |
| Carpet Set G | g | **33.2%** | 34.3% | 32.2% |
| C60 Clefairy / Mewtwo | party | **14.3%** | 13.5% | 15.1% |
| M Mew ex baby box | mew_baby | **8.3%** | 6.7% | 9.9% |

Rerun on 2026-09-26, same seed, after Premium Power Pro clears at the end of the turn and Makuhita / Hariyama pay their printed attack costs. The 2026-09-25 table was D60 84.7, H 73.2, T60 44.7, M 9.9. C60 stays 14.3 (428 wins, was 430).

Startup is real, and it is not enough against the decks that already beat Dragapult. Mega Brave is 270 for two Fighting Energy, and a Knocked Out Mega Lucario ex gives three prizes. Candy Dragapult and the Hedrick list both take that trade. M's Budew line item-locks Gong, Poké Pad, Ultra Ball, and Premium Power Pro, then attacks for no energy; Lucario wins 248 of 3,000 there.

Ogerpon is the other way around. Mega Lucario ex has no Ability, so Cornerstone Stance does not block Mega Brave, and 270 is a knockout on 210 HP.

## C60 closer vs Lucario

Photon Kinesis is Lightning, and Mewtwo ex is Fighting-weak, so Mega Brave 270 is 540. In this matchup `party` does not play Mewtwo, does not Nest Ball for it, and does not attach to it. The closer is Clefable ex: Wondrous Moon is 170 Psychic, weakness makes that 340, and 340 KOs Mega Lucario ex for 3 prizes. Mega Clefable ex is the second attacker (Shooting Moons, 320 HP so one unboosted Mega Brave does not KO it). Mewtwo is promoted only when Photon actually KOs.

The instrumented C60 run on 2026-09-25, same seed, was 430 wins (14.3%). Average prizes 1.89 / 4.74. Attacks: Wondrous Moon 3625, Shooting Moons 2320, Photon Kinesis 415. Mega Lucario ex was Knocked Out 2672 times. The 2026-09-26 rerun is 428 wins.
