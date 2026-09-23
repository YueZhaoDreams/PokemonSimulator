# C60 s60 win-rate matrix (three Dragapult 60s included)

Date: 2026-09-23
Seed: `20260911`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / directed cell (row is player A; who goes first is random)
Elapsed: 499.3s (official table + same seed with bonus draws off)
Script: `data/lab/set_c60_unl_matrix.py`
Raw: `data/lab/set-c60-unl-matrix.json`

Diagonal skipped. A vs B and B vs A are separate runs, so they need not sum to 100%.

Opening: draw 7, mulligan until a Basic Pokémon, set 6 prizes, then the opponent **always** draws one card per mulligan. Extra cards stay in hand (not benched during setup). That is the official table below. The script also stores `cells_no_bonus` at the same seed so the delta is not mixed up with later list locks.

## Decks

| Key | List | Strategy |
| --- | --- | --- |
| C60 | Locked Set C Standard 60 (1 Prankish + 1 CLC Metronome + 1 Poké Pad) | `party` |
| T60 | Household Set T stretched to 60 (4 Candy) | `phantom` |
| Hedrick | Printed Worlds 2026 Andrew Hedrick Dragapult | `phantom` |
| UNL | Unlimited-shaped Pidgeot / Rotom V / Counter Catcher Dragapult | `phantom` |
| D60 | Charm Ogerpon 60 | `demolish` |
| S60 | Floragato hunter 60 | `slash` |
| G | Carpet Set G 60 | `carnival` |

T60 / Hedrick / UNL are the three Dragapult 60s the engine can actually play. UNL is a card-pool package (Pidgeot ex, Rotom V, Lumineon V, Manaphy, Forest Seal Stone), not Unlimited copy rules.

## First-hand miss (no Basic in the opening 7)

Same seed, 3,000 openings / list. A miss is at least one mulligan.

| List | Miss | Avg mulligans | Basics in 60 (approx.) |
| --- | ---: | ---: | --- |
| C60 | 39.2% | 0.66 | 4 Clefairy + 3 Mewtwo ex |
| T60 | 34.3% | 0.53 | Dreepy line + Budew + Fez |
| Hedrick | 21.7% | 0.28 | thicker Basic suite |
| UNL | 25.5% | 0.34 | Dreepy + extra Basics |
| D60 | **59.9%** | **1.46** | 4 Charm Ogerpon |
| S60 | 31.0% | 0.44 | 4 Sprigatito + Tangela / Wo-Chien |
| G | 21.3% | 0.27 | Starly / Relicanth suite |

D60 bricks most. Whoever sits across from it draws the extra cards. C60 also misses often (~40%); T60 is close behind.

## Row win rate (official: opponent draws one per mulligan)

| A \\ B | C60 | T60 | Hedrick | UNL | D60 | S60 | G |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **C60** | — | **69.2%** | 63.7% | 90.3% | **77.2%** | 99.7% | 88.3% |
| **T60** | 30.7% | — | 54.8% | 74.2% | 80.7% | 84.5% | 86.3% |
| **Hedrick** | 35.3% | 44.7% | — | 69.1% | 71.9% | 78.5% | 82.4% |
| **UNL** | 11.1% | 25.7% | 30.9% | — | 56.5% | 66.7% | 61.7% |
| **D60** | 22.6% | 19.5% | 28.4% | 44.6% | — | 72.2% | 96.6% |
| **S60** | 0.6% | 16.7% | 21.3% | 32.8% | 28.7% | — | 27.4% |
| **G** | 11.4% | 13.7% | 16.8% | 39.1% | 4.0% | 73.3% | — |

## Same seed without bonus draws

| A \\ B | C60 | T60 | Hedrick | UNL | D60 | S60 | G |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **C60** | — | 68.9% | 64.8% | 90.2% | 71.9% | 99.8% | 89.2% |
| **T60** | 29.6% | — | 56.1% | 73.5% | 77.9% | 83.4% | 86.7% |
| **Hedrick** | 35.1% | 43.5% | — | 69.7% | 65.9% | 79.6% | 82.5% |
| **UNL** | 9.9% | 24.8% | 32.1% | — | 52.7% | 67.0% | 60.7% |
| **D60** | 26.3% | 21.4% | 32.6% | 46.5% | — | 75.1% | 96.5% |
| **S60** | 0.4% | 16.6% | 22.1% | 32.4% | 26.7% | — | 27.3% |
| **G** | 11.6% | 14.5% | 18.1% | 39.6% | 3.8% | 72.4% | — |

## Delta (bonus minus no-bonus, player A percentage points)

Binomial SE on a 70% cell at 3,000 games is about **0.8 pp**. Treat ±1.0 as noise.

| A \\ B | C60 | T60 | Hedrick | UNL | D60 | S60 | G |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **C60** | — | +0.3 | −1.0 | +0.1 | **+5.3** | −0.2 | −0.9 |
| **T60** | +1.1 | — | −1.3 | +0.7 | **+2.8** | +1.1 | −0.4 |
| **Hedrick** | +0.2 | +1.2 | — | −0.6 | **+6.0** | −1.1 | −0.1 |
| **UNL** | +1.2 | +0.9 | −1.2 | — | **+3.7** | −0.3 | +1.1 |
| **D60** | **−3.7** | −2.0 | **−4.2** | −1.9 | — | −2.9 | +0.1 |
| **S60** | +0.2 | +0.2 | −0.8 | +0.4 | +2.0 | — | +0.1 |
| **G** | −0.2 | −0.8 | −1.3 | −0.5 | +0.2 | +1.0 | — |

The rule mainly punishes **D60**. Charm Ogerpon keeps only four Basics, so the opponent sees ~1.5 extra cards per game and Demolish drops several points from both seats. C60 vs D60 71.9% → **77.2%**; D60 vs C60 26.3% → **22.6%**. Hedrick vs D60 +6.0 is the same story.

C60 vs T60 is **+0.3** (68.9 → 69.2). Both lists miss often (39% / 34%), so extra cards mostly cancel. Dragapult-internal cells and S60 / G stay inside noise.

## Vs the 2026-09-12 table (same seed, older lists)

That table already drew one per mulligan. The jump is the **Pad + CLC lock** (and later G / Dragapult list work), not this rule.

| C60 as A | 2026-09-12 | 2026-09-23 | Δ |
| --- | ---: | ---: | ---: |
| vs T60 | 48.7% | **69.2%** | +20.5 |
| vs Hedrick | 58.2% | 63.7% | +5.5 |
| vs UNL | 84.4% | 90.3% | +5.9 |
| vs D60 | 74.2% | 77.2% | +3.0 |
| vs S60 | 99.5% | 99.7% | +0.2 |
| vs G | 97.9% | 88.3% | −9.6 |

C60 vs T60 is no longer even: Party + Pad/Metronome is a favorite. G is no longer free food (Nest / Zone / Telepathic work after that lock). D60 is still last among real threats, and the mulligan bonus makes that worse.

## Read

Locked **C60** beats every household 60 in this array. T60 is the closest Dragapult at 30.7% from T60's seat (C60 69.2% from Party's seat). Hedrick without Candy stays a C60 favorite. UNL remains a blowout.

Among Dragapults, T60 still beats Hedrick (54.8%) and UNL (74.2%). Hedrick still beats UNL (69.1%).

D60 still loses to every Dragapult and to C60; the bonus draws are the one rule change that moves it. S60 stays Party food. G takes ~12% off C60, not the old 2%.
