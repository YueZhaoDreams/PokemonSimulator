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

## 30-card, B cuts Lickilicky / Aipom (2026-08-20)

Set B swapped Colorless Lickilicky and Aipom for spare **Darkness Energy** and a second **Grass Energy**. Same seed, 3,000 games / cell. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 72.0% | 4.8% | 0.3% | 70.8% |
| **B** | 29.1% | — | 10.9% | 0.1% | 24.3% |
| **C** | **94.9%** | **88.6%** | — | **60.2%** | 77.4% |
| **D** | 99.9% | 99.8% | 42.0% | — | 33.8% |
| **S** | 28.8% | 74.6% | 22.4% | **67.0%** | — |

B did **not** improve until `shock` actually played Roselia. Vs A 29.2% → 29.1% (noise). Vs S 25.9% → 24.3%. Extra Grass sat unused: Thunder Shock already had a Colorless, and Roselia stayed in hand as fuel.

## 30-card, shock uses Roselia (2026-08-20)

`shock` now benches one Roselia. Extra Grass Energy pays **Soothing Scent [G]** when Thunder Shock is not ready; once Pikachu can Shock, it swaps in. Same seed, 3,000 games / cell. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 63.4% | 4.8% | 0.3% | 70.8% |
| **B** | **34.9%** | — | 15.0% | 0.4% | 25.5% |
| **C** | **94.9%** | 85.0% | — | **60.2%** | 77.4% |
| **D** | 99.9% | 99.6% | 42.0% | — | 33.8% |
| **S** | 28.8% | 76.1% | 22.4% | **67.0%** | — |

B vs A **29.1% → 34.9%**. Vs C 10.9% → 15.0%. Sleep-lock eats Hydro Splash turns. Vs D still ~0. Vs S ~flat.

## 30-card, shock uses Spinarak too (2026-08-20)

Darkness Energy pays **Poison Sting 10 + Poison**. Do not open the 50 HP bug into Hydro Splash; bench it, sting when Thunder Shock is not ready, poison ticks stack with paralysis. Same seed, 3,000 games / cell. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 70.0% | 4.8% | 0.3% | 70.8% |
| **B** | 31.9% | — | **18.6%** | 0.5% | 19.2% |
| **C** | **94.9%** | 81.6% | — | **60.2%** | 77.4% |
| **D** | 99.9% | 99.7% | 42.0% | — | 33.8% |
| **S** | 28.8% | 81.5% | 22.4% | **67.0%** | — |

Vs the last merged 30-card table (Wo-Chien S, B still Lickilicky/Aipom): B vs A 29.2% → **31.9%**, vs C 11.1% → **18.6%**, vs S 25.9% → 19.2%. Poison helps the Plusle race vs Clefairy/Mewtwo; 50 HP Spinarak is prize food vs Floragato. Vs Roselia-only, B vs A dropped 34.9% → 31.9% and vs C rose 15.0% → 18.6%.

## 30-card, Walrein line (2026-08-22)

Carpet Set B cut Fire / Darkness / Spinarak / Gimmighoul and added Surging Sparks **Spheal / Sealeo / Walrein**, two Water Energy, two extra Lightning Energy, one extra Grass Energy, and Trekking Shoes. `shock` evolves the water line; **Megaton Fall 170** KOs 160 HP Dondozo; Frigid Fangs locks ≤2 Energy. Thunder Shock still chips. Same seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | **54.7%** | 4.8% | 0.3% | 70.8% |
| **B** | **44.1%** | — | 13.9% | 1.1% | 21.3% |
| **C** | **94.9%** | 86.7% | — | **60.2%** | 77.4% |
| **D** | 99.9% | 98.6% | 42.0% | — | 33.8% |
| **S** | 29.4% | 78.5% | 22.4% | **67.0%** | — |

B vs A **31.9% → 44.1%**. Megaton Fall is a real Hydro Splash answer; A vs B fell 70.0% → 54.7%. Vs D still ~1% (140 Demolish vs a 170 HP Water that does not hit Fighting weakness). Vs C 18.6% → 13.9% without Poison Sting. Vs S ~flat (21.3%). Recoil is now parsed from printed "does N damage to itself" text (Megaton Fall 50, and any other card that already had that sentence).

## 30-card A, Staraptor + Boomerang + 2 Psychic Energy (2026-08-22)

Carpet Set A is **30**: Dondozo plus Paldea Evolved **Starly / Staravia / Staraptor**, Twilight Masquerade **Boomerang Energy**, Gligar, Aipom, metal leftovers (Aron / Ferroseed / Galarian Meowth), and **two Psychic Energy** (Flutter Mane still pays Psychic). Clefairy and Trekking Shoes out. `thrifty` evolves the bird; **Power Blast 180** discards energy and Boomerang returns; **Tailspin Away** prevents damage from Basic Pokémon. Same seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S |
| --- | ---: | ---: | ---: | ---: | ---: |
| **A** | — | **67.3%** | 10.1% | 4.2% | 66.4% |
| **B** | 32.1% | — | 13.9% | 1.1% | 21.3% |
| **C** | 89.2% | 86.7% | — | **60.2%** | 77.4% |
| **D** | 95.5% | 98.6% | 42.0% | — | 33.8% |
| **S** | 33.7% | 78.5% | 22.4% | **67.0%** | — |

Vs the 28-card Staraptor table: A vs B 66.6% → **67.3%** (noise). A vs C 11.7% → 10.1% (extra Psychic is also Party fuel if C prizes it, but A holds it as Flutter Mane pay). A vs D 5.2% → 4.2%. B–C–D–S cells that do not touch A match the Walrein table.

## 30-card Set T, Dragapult ex (2026-08-23)

Set T is the official **30-card constructed** half-deck (max 2 copies except basic Energy, 3 prizes) compressed from August 2026 Standard **Dragapult ex**. Strategy `phantom`: Poffin Dreepy / Budew, Recon Directive from printed look-N, Rare Candy into Dragapult, Phantom Dive 200 + 6 bench counters. Budew Itchy Pollen locks Items. Same seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

Family Cup still allows Pokémon-as-energy; T holds the line and pays Fire / Psychic / Darkness Energy.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 67.3% | 10.1% | 4.2% | 66.4% | 45.8% |
| **B** | 32.1% | — | 13.9% | 1.1% | 21.3% | 50.1% |
| **C** | 89.2% | 86.7% | — | **60.2%** | 77.4% | 41.3% |
| **D** | 95.5% | 98.6% | 42.0% | — | 33.8% | **61.9%** |
| **S** | 33.7% | 78.5% | 22.4% | **67.0%** | — | **65.9%** |
| **T** | **55.9%** | 50.9% | **59.4%** | 40.0% | 35.0% | — |

T beats carpet A and Party C, splits shock B, and loses to Charm Ogerpon D (Demolish 140 into a slow Stage 2) and Floragato hunter S (Grass OHKO / Wo-Chien sponge). A–S cells that do not touch T match the Staraptor table.

## 30-card, ex = 2 prizes, Mega ex = 3 (2026-08-23)

Family Cup still puts **3** prize cards face-down. Knocking Out a Pokémon ex now takes **2**; Knocking Out a Mega ex takes **3** (one Mega KO wins). Same lists, strategies, seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 67.3% | 11.9% | 4.2% | 67.3% | 46.1% |
| **B** | 32.1% | — | 13.2% | 1.1% | 22.8% | 49.5% |
| **C** | 87.7% | 86.2% | — | 52.4% | 82.8% | 45.3% |
| **D** | 95.5% | 98.6% | 49.2% | — | 42.5% | **70.1%** |
| **S** | 31.1% | 76.3% | 17.4% | 57.9% | — | 60.4% |
| **T** | 52.9% | 50.2% | 55.4% | 30.6% | 41.8% | — |

Vs the previous 1-prize-per-KO table: C vs D **60.2% → 52.4%** (Ogerpon is 2 prizes; Mega Clefable is a 3-prize gift). D vs T **61.9% → 70.1%** (Dragapult ex is 2). S vs D **67.0% → 57.9%** because Wo-Chien ex also pays 2. T vs C **59.4% → 55.4%**; C vs T **41.3% → 45.3%**. Carpet A/B barely move — they are mostly non-ex.

## 30-card Set C, −1 Psychic Energy + Boss's Orders (2026-08-23)

Rule B already treats Clefable as Psychic Energy. Bakeoffs (`data/lab/set_c_energy_swap.py`, seed `20260823`, 1k/cell) showed 2× Switch and 2× Clefairy lose D+T. Locked swap: **one Boss's Orders, one Psychic Energy**. Same seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 67.3% | 14.0% | 4.2% | 67.3% | 46.1% |
| **B** | 32.1% | — | 15.2% | 1.1% | 22.8% | 49.5% |
| **C** | 85.4% | 85.9% | — | 48.3% | **85.4%** | 47.1% |
| **D** | 95.5% | 98.6% | 49.9% | — | 42.5% | 70.1% |
| **S** | 31.1% | 76.3% | 13.8% | 57.9% | — | 60.4% |
| **T** | 52.9% | 50.2% | 51.6% | 30.6% | 41.8% | — |

Vs the 2-energy prize table: C vs T 45.3% → **47.1%**, C vs S 82.8% → **85.4%**, C vs D 52.4% → **48.3%**. Cells that do not touch C match.

## 30-card Set C, fifth Clefable instead of energy (2026-08-23)

The last Psychic Energy is now a fifth Rebel Clash **Clefable** (Prankish, 1 prize, Rule B Psychic). 3k bakeoff vs Clefable ex / Mega: RCL Clefable matches dedicated energy; Mega loses vs D. Same seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 67.3% | 15.9% | 4.2% | 67.3% | 46.1% |
| **B** | 32.1% | — | 15.1% | 1.1% | 22.8% | 49.5% |
| **C** | **86.8%** | 83.9% | — | 48.6% | 83.7% | 46.3% |
| **D** | 95.5% | 98.6% | 50.9% | — | 42.5% | 70.1% |
| **S** | 31.1% | 76.3% | 14.5% | 57.9% | — | 60.4% |
| **T** | 52.9% | 50.2% | 51.6% | 30.6% | 41.8% | — |

Vs the 1-energy+Boss table: D/T are noise (48.3/47.1 → 48.6/46.3). C vs A 85.4% → **86.8%**. Dedicated Energy is gone from Set C.

## 30-card Set C, Belt-then-Hop trainer order (2026-08-25)

`party` now hunts Maximum Belt (Arven before Tool Box), then Hop, then Energy Search / Nest Ball. Same lists, seed `20260819`, 3,000 games / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 15.1% | 4.2% | 67.7% | 47.2% |
| **B** | 32.3% | — | 14.8% | 1.2% | 23.2% | 50.3% |
| **C** | 85.7% | 84.1% | — | **52.3%** | **88.5%** | 45.9% |
| **D** | 95.7% | 98.7% | 47.6% | — | 39.1% | 70.5% |
| **S** | 31.1% | 75.5% | 11.8% | 60.9% | — | 59.0% |
| **T** | 52.8% | 49.4% | 53.6% | 30.9% | 39.8% | — |

Vs the mulligan-bonus table (previous json): cells that do not touch C are unchanged. C vs S 84.9% → **88.5%** (S vs C 14.2% → 11.8%). C vs D 51.7% → 52.3%. C vs T 46.5% → 45.9%. A/B vs C are noise (±1%).

## 2 Hop + 1 SM Lillie (2026-08-25)

Printed UPR 125: draw until 6, or until 8 on **your first turn** (not “went first all game”). Family Cup still blocks the first player’s turn-1 Supporter, so the 8-card draw is the second player’s first turn.

`party` plays Lillie over Hop when it would draw more. Same seed `20260819`, 3,000 / C-cell. Raw: `data/lab/c-sm-lillie-hop.json`; C cells copied into `data/lab/family-cup-30-matrix.json`.

| list | vs A | vs B | vs D | vs S | vs T | T vs C | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 Hop | 88.0% | 85.6% | **52.3%** | 82.0% | 51.2% | 50.2% | 71.8% |
| **2 Hop + 1 Lillie** | **89.2%** | **88.7%** | 51.3% | **82.3%** | **51.3%** | **48.8%** | **72.6%** |

B is the big gain. D dips about 1 point. Set C locks 2 Hop / 1 Lillie.

## Boss only closes the game (2026-08-25)

`party` plays Boss's Orders only if the pulled Active is a KO that covers remaining prizes (e.g. 6P+Belt = 240 snipe uncharmed 210, not Charm 260). Same 2 Hop + 1 Lillie list, seed `20260819`, 3,000 / C-cell.

| Boss | vs A | vs B | vs D | vs S | vs T | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| any bench | 89.2% | 88.7% | 51.3% | **82.3%** | 51.3% | 72.6% |
| last prize(s) only | **90.7%** | 88.7% | 51.3% | 80.2% | **52.5%** | **72.7%** |

D does not move. A/T pick up a bit. S drops ~2 points (early Boss vs 60 HP cats is gone).

## Rotate dying walls; Photon last hit (2026-08-25)

Vs D: keep Mega / Clefable ex in front, pay retreat, swap a dying sponge to the next body that survives 140. Mewtwo only for Photon finish (or if no sponge is left). Same lists, seed `20260819`, 3,000 / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 9.5% | 4.2% | 67.7% | 47.5% |
| **B** | 32.3% | — | 11.1% | 1.2% | 23.2% | 50.4% |
| **C** | 90.6% | 88.4% | — | 51.0% | **86.2%** | 51.6% |
| **D** | 95.7% | 98.7% | 48.0% | — | 39.1% | 70.4% |
| **S** | 31.1% | 75.5% | 14.8% | 60.9% | — | 59.7% |
| **T** | 51.7% | 49.6% | 47.9% | 31.0% | 41.1% | — |

C-row vs the Boss-close lock (same seed / 3k):

|  | vs A | vs B | vs D | vs S | vs T | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Boss last prize | 90.7% | 88.7% | **51.3%** | 80.2% | **52.5%** | 72.7% |
| wall rotate | 90.6% | 88.4% | 51.0% | **86.2%** | 51.6% | **73.6%** |

D does not move (noise). The C-row lift is vs S (80.2% → 86.2%); S vs C 21.1% → 14.8%.

## Going-first/second D scripts (2026-08-26)

`party` vs D uses the 4+1 and 3+2 lines only when the board is assembled; otherwise it keeps the Mega / Clefable ex wall. Going first: one empty Clefairy chump, or Clefable/ex Charge fodder + Zone. Going second: two empty Clefairy chumps while Party keeps firing, or support Transfer Charge then free-retreat onto the Belted closer. Same lists, seed `20260819`, 3,000 / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 11.3% | 4.2% | 67.7% | 47.5% |
| **B** | 32.3% | — | 10.4% | 1.2% | 23.2% | 50.4% |
| **C** | 88.2% | 89.6% | — | **57.5%** | 78.2% | **54.5%** |
| **D** | 95.7% | 98.7% | **41.4%** | — | 39.1% | 70.4% |
| **S** | 31.1% | 75.5% | 20.8% | 60.9% | — | 59.7% |
| **T** | 51.7% | 49.6% | 44.6% | 31.0% | 41.1% | — |

C-row vs the wall-rotate table (same seed / 3k):

|  | vs A | vs B | vs D | vs S | vs T | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| wall rotate | 90.6% | 88.4% | 51.0% | **86.2%** | 51.6% | 73.6% |
| D scripts | 88.2% | **89.6%** | **57.5%** | 78.2% | **54.5%** | 73.6% |

C vs D is first 58.2% / second 56.8%. The vs-D lift is paid for vs S (86.2% → 78.2%); S vs C 14.8% → 20.8%. D vs C 48.0% → 41.4%.

## Party vs Floragato (2026-08-26)

`party` branches on the opponent: D scripts stay vs Ogerpon; vs Floragato open Mewtwo, Party once, hide on Mega / Clefable ex / Mewtwo, Photon when it finishes. Same seed `20260819`, 3,000 / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 11.3% | 4.2% | 67.7% | 47.5% |
| **B** | 32.3% | — | 10.4% | 1.2% | 23.2% | 50.4% |
| **C** | 88.2% | 89.6% | — | **58.1%** | **90.6%** | 54.5% |
| **D** | 95.7% | 98.7% | 41.8% | — | 39.1% | 70.4% |
| **S** | 31.1% | 75.5% | **9.7%** | 60.9% | — | 59.7% |
| **T** | 51.7% | 49.6% | 44.6% | 31.0% | 41.1% | — |

C-row vs the D-script table (same seed / 3k):

|  | vs A | vs B | vs D | vs S | vs T | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| D scripts | 88.2% | 89.6% | 57.5% | 78.2% | 54.5% | 73.6% |
| vs Floragato branch | 88.2% | 89.6% | **58.1%** | **90.6%** | 54.5% | **76.2%** |

C vs S is first 85.5% / second 95.8%. C vs D stays 58.1% (first 59.4 / second 56.9).

## Party vs Dragapult (2026-08-26)

`party` branches on the opponent: D scripts stay vs Ogerpon; vs Floragato hide from Claw; vs Dragapult Party once, hide from Phantom Dive 200, Moon when it takes prizes, Photon as the closer. Same seed `20260819`, 3,000 / ordered pair. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 11.3% | 4.2% | 67.7% | 47.5% |
| **B** | 32.3% | — | 10.4% | 1.2% | 23.2% | 50.4% |
| **C** | 88.2% | 89.6% | — | **58.1%** | **90.6%** | **62.4%** |
| **D** | 95.7% | 98.7% | 41.8% | — | 39.1% | 70.4% |
| **S** | 31.1% | 75.5% | **9.7%** | 60.9% | — | 59.7% |
| **T** | 51.7% | 49.6% | **37.1%** | 31.0% | 41.1% | — |

C-row vs the Floragato-branch table (same seed / 3k):

|  | vs A | vs B | vs D | vs S | vs T | C avg |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vs Floragato branch | 88.2% | 89.6% | 58.1% | 90.6% | 54.5% | 76.2% |
| vs Dragapult branch | 88.2% | 89.6% | **58.1%** | **90.6%** | **62.4%** | **77.8%** |

C vs T is first 63.0% / second 61.8%. C vs D and C vs S are unchanged.


