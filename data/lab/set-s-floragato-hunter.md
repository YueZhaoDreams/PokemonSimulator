# Set S — Floragato hunter vs Charm Ogerpon

Date: 2026-08-20
Seed: `20260819`
Engine: `family-tcg-monte-carlo`
Strategies: `slash` (Set S) vs `demolish` (Set D)
Games: 3,000, random seat

Forget A/B/C. This list is built only to beat Charm Ogerpon. Family Cup is 30.

Ogerpon is Grass-weak. Floragato has **no Ability**, so Cornerstone Stance does not block. Slashing Claw 90 + Maximum Belt 50 = 140, ×2 Weakness = **280**, which OHKOs 260 Charm Ogerpon so Acerola cannot reset. **Wo-Chien ex** (Grass, 230 HP, no Ability) is the Demolish sponge; Forest Blast 220 ×2 = **440** is the backup KO. ACE SPEC stays one Belt.

## Why Paradox Rift Mewtwo was wrong

`sv04-058` Mewtwo ex is **Lightning**. Photon Kinesis costs **[P][P]**. Set S is a Grass list: no Psychic Energy, no Party, no Transfer Charge fuel. That Mewtwo could sit as a 230 HP sponge, but it could not Photon vs D. The tank has to be Grass if it is going to attack through Stance.

## Locked 30

| Qty | Card | ID | Notes |
| ---: | --- | --- | --- |
| 4 | Sprigatito | sv01-013 | Paldea Evolved; extras are Grass energy |
| 4 | Floragato | sv01-014 | Engine: Slashing Claw 90 for [G][C] (no Ability). Picture is Paldea Evolved. |
| 3 | Wo-Chien ex | sv02-027 | Grass, 230 HP, Retreat 4, no Ability; Forest Blast 220 |
| 4 | Nest Ball | sv01-181 | Fetch Wo-Chien, then one Sprigatito |
| 3 | Energy Search | sv01-172 | Wo-Chien / Grass fuel |
| 3 | Switch | sv01-194 | Wo-Chien Retreat 4; swing only when a Grass attack KOs |
| 1 | Jacq | sv01-175 | Up to 2 Evolution Pokémon (Floragato) |
| 1 | Maximum Belt | sv05-154 | ACE SPEC +50 vs ex |
| 1 | Tool Box | swsh11-168 | Printed top-7 Tool tutor |
| 1 | Arven | sv01-166 | Belt + Item |
| 1 | Hop | swsh1-165 | Draw 3 |
| 2 | Tangela | swsh12.5-004 | Grass energy |
| 2 | Grass Energy | swsh12.5-152 | Pays [G][C] / Forest Blast |
| **30** | | | |

No Muscle Band. Band is +20 (110×2 = 220), which does not KO Charm 260 and occupies the only Tool slot Belt needs.

## Play

- Open on Wo-Chien when it is in the opening 7. Nest it if it is still in the deck.
- One Sprigatito in play to evolve; extras and Tangela pay [G][C], then Forest Blast.
- Hold Maximum Belt in hand until Floragato is in play. Never park it on Wo-Chien.
- Stay on Wo-Chien until Slashing Claw or Forest Blast KOs this turn, then Switch in if needed.
- Do not chip 180 into Acerola. Do not Nest Tangela.
- Skip Hop when the deck has ≤10 cards.

## 3,000 games vs D (seed `20260819`, Wo-Chien tank)

| Seat | Set S win rate |
| --- | ---: |
| S first | 67.6% |
| S second | 66.4% |
| **Random** | **67.0%** |

Full table: `data/lab/family-cup-30-matrix.json`.

## Family Cup matrix (3,000 games / cell, same seed)

Row = that set's win rate. Strategies: A `thrifty`, B `shock`, C `party`, D `demolish`, S `slash`.

### 28-card (Lightning Mewtwo tank, historical)

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 64.5% | 7.7% | 0.2% | 71.4% |
| **B** | 37.9% | — | 9.2% | 0.3% | 19.5% |
| **C** | 92.3% | 91.1% | — | 54.9% | 69.0% |
| **D** | 99.8% | 99.8% | 45.0% | — | 32.9% |
| **S** | 26.7% | 80.4% | 30.5% | **66.0%** | — |

### 30-card, Lightning Mewtwo still in S (historical, +2 Grass Energy)

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 71.4% | 4.8% | 0.3% | 73.6% |
| **B** | 29.2% | — | 11.1% | 0.2% | 28.8% |
| **C** | 94.9% | 88.2% | — | 60.2% | 76.6% |
| **D** | 99.9% | 99.6% | 42.0% | — | 33.4% |
| **S** | 27.7% | 71.7% | 24.2% | **67.6%** | — |

That 67.6% vs D was Floragato + Belt. Mewtwo never Photoned.

### 30-card, Wo-Chien ex tank (current)

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 71.4% | 4.8% | 0.3% | 70.8% |
| **B** | 29.2% | — | 11.1% | 0.2% | 25.9% |
| **C** | 94.9% | 88.2% | — | 60.2% | 77.4% |
| **D** | 99.9% | 99.6% | 42.0% | — | 33.8% |
| **S** | 28.8% | 74.6% | 22.4% | **67.0%** | — |

S vs D is **67.0%**. The tank is now Grass and can Forest Blast through Stance. Vs B the 230 HP sponge still eats Thunder Shock. Vs A and C it still sits until an OHKO that Belt cannot provide against non-ex Dondozo.
