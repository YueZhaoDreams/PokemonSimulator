# Tool Box vs Muscle Band — lab result

Date: 2026-08-19
Seed: `20260818`
Engine: `family-tcg-monte-carlo`
Matchup: Set C line vs Set D (`party` vs `demolish`)

**Maximum Belt is ACE SPEC (one copy).** The open trainer slot was compared as Tool Box vs Muscle Band.

## Locked Set C keeps Tool Box

| Qty | Card |
| ---: | --- |
| 4 | Clefairy |
| 2 | Mewtwo ex |
| 4 | Clefable |
| 4 | Clefable ex |
| 3 | Mega Clefable ex |
| 3 | Hop |
| 2 | Nest Ball |
| 3 | Energy Search |
| 1 | Maximum Belt (ACE SPEC) |
| 1 | **Tool Box** |
| 1 | Arven |

## Head-to-head (5,000 games)

| List | Random | First | Second |
| --- | ---: | ---: | ---: |
| **Tool Box** (locked) | **54.7%** | 57.6% | 51.8% |
| Muscle Band instead of Tool Box | 50.4% | 55.7% | 45.1% |
| Prior 4 Hop / no Tool Box | 53.8% | 56.8% | 50.8% |

### Why Tool Box wins

Mewtwo can hold only **one** Tool. Muscle Band is +20 to all attacks; Maximum Belt is +50 vs Pokémon ex. Against Charm Ogerpon, attaching Muscle Band instead of Belt loses the 7 Psychic Photon line (270). Tool Box / Arven dig for the single ACE SPEC Belt; they do not compete for the Tool slot on Mewtwo.

Muscle Band remains in the engine (printed +20) for other lists, but **does not replace Tool Box in Set C**.

## Family Cup win-rate matrix (3,000 games / cell)

Strategies: A `thrifty`, B `shock`, C `party`, D `demolish`. Cell = **row player's win rate** vs column. Diagonal is —.

|  | A | B | C | D |
| --- | ---: | ---: | ---: | ---: |
| **A** | — | 64.2% | 29.8% | 0.2% |
| **B** | 35.1% | — | 49.0% | 0.1% |
| **C** | 70.6% | 52.7% | — | **54.9%** |
| **D** | 99.7% | 99.8% | 47.2% | — |

Notes:

- A vs B ≈ documented carpet matchup (~66% A in the older 10k shock log).
- D (Charm Ogerpon) hard-crushes A and B; C is the only list that stays above 50% vs D.
- C vs D ≈ 55% matches the locked Tool Box list.
