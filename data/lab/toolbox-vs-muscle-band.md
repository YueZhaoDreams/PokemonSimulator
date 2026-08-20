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

Date: 2026-08-19 · Seed: `20260819`
Engine: `family-tcg-monte-carlo`
Strategies: A `thrifty`, B `shock`, C `party`, D `demolish`, S `slash`.
Cell = **row player's win rate** vs column. Diagonal is —. Random seat.

`party` vs A/B: open on **Mewtwo**, Clefairy mostly as energy (cap **1** vs thrifty, **0** vs shock). Vs D: Party ramp (cap 3) → Photon / Belt.
`slash` is the Set S Floragato hunter: tank on a 230 HP Basic with no Ability, OHKO Charm Ogerpon with Slashing Claw + Belt (280). The 28-card and first 30-card tables below still used Paradox Rift Lightning Mewtwo as that sponge (it cannot pay Photon in a Grass list). Current S uses Wo-Chien ex.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 64.5% | 7.7% | 0.2% | 71.4% |
| **B** | 37.9% | — | 9.2% | 0.3% | 19.5% |
| **C** | **92.3%** | **91.1%** | — | 54.9% | 69.0% |
| **D** | 99.8% | 99.8% | 45.0% | — | 32.9% |
| **S** | 26.7% | 80.4% | 30.5% | **66.0%** | — |

Notes:

- A–D cells re-ran unchanged on this seed.
- C vs A/B were previously inflated by C deck-outs while Active Clefairy died to Hydro Splash / Thunder Shock.
- S is specialized vs D (66.0%). It also beats B (80.4%) because Mewtwo tanks Thunder Shock. It loses to A (26.7%) and C (30.5%): Hydro Splash / Photon win the prize race while Floragato only swings on an OHKO, and Belt does not help vs non-ex Dondozo.

## 30-card Family Cup (2026-08-20)

Rule is **30**. Carpet A dropped Tool Box and added Metal / Water / Psychic Energy (still one Clefairy). Carpet B added Lightning Energy and Fire Energy. Constructed C / D / S each gained two typed energy of their line. Set E stays folded into C; S is the fifth list.

Same engine, seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 71.4% | 4.8% | 0.3% | 73.6% |
| **B** | 29.2% | — | 11.1% | 0.2% | 28.8% |
| **C** | **94.9%** | **88.2%** | — | **60.2%** | 76.6% |
| **D** | 99.9% | 99.6% | 42.0% | — | 33.4% |
| **S** | 27.7% | 71.7% | 24.2% | **67.6%** | — |

Moves vs the 28-card table: A vs B +6.9 (Water Energy pays Hydro Splash). C vs D +5.3 (real Psychic Energy for Party). S vs D +1.6 (Grass Energy for Slashing Claw). B vs S +9.3 (Lightning Energy pays Thunder Shock / Volt Tackle). D still tables A/B. That S still had Lightning Mewtwo as a sponge; Floragato did the KOs.

## 30-card, Wo-Chien tank (2026-08-20)

Paradox Rift Mewtwo ex is Lightning; Photon costs Psychic. Set S is Grass, so that tank could not attack D. Current S is 3× Wo-Chien ex (`sv02-027`): Grass, no Ability, Forest Blast 220 ×2 = 440. Same seed, 3,000 games / cell.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 71.4% | 4.8% | 0.3% | 70.8% |
| **B** | 29.2% | — | 11.1% | 0.2% | 25.9% |
| **C** | **94.9%** | **88.2%** | — | **60.2%** | 77.4% |
| **D** | 99.9% | 99.6% | 42.0% | — | 33.8% |
| **S** | 28.8% | 74.6% | 22.4% | **67.0%** | — |

S vs D is **67.0%** (Floragato 280 / Forest Blast 440). A–D cells are unchanged.
