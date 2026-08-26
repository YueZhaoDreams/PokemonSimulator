# Set C: cut one Psychic Energy

Date: 2026-08-23
Seed (bakeoff): `20260823` · 1,000 games / cell
Engine: `family-tcg-monte-carlo` with Family Cup **ex = 2 / Mega ex = 3**

Set C is 30. The two dedicated Psychic Energy are redundant under Rule B (Clefairy / Clefable are Psychic Energy) but still help Photon density vs D. Replacing **both** with Switch or extra Clefairy lost the D/T race. The locked swap is **−1 Psychic Energy, +1 Boss's Orders**.

## Bakeoff (C is row, party vs foe)

D+T = mean of vs D and vs T. Baseline `energy2` is the old 2× Psychic Energy list.

| package | A | B | D | S | T | mean | D+T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **energy1 + Boss** (locked) | 86.0% | 84.6% | 49.6% | 86.6% | **51.2%** | **71.6%** | **50.4%** |
| energy2 (old) | 88.9% | 87.1% | **54.0%** | 82.5% | 44.0% | 71.3% | 49.0% |
| 2× Boss | 84.2% | 85.9% | 46.4% | 86.8% | 51.3% | 70.9% | 48.9% |
| 1 energy + 1 Switch | 90.0% | 93.8% | 50.3% | 77.4% | 43.2% | 70.9% | 46.8% |
| 2× Switch | 91.5% | 94.4% | 45.8% | 72.4% | 44.1% | 69.6% | 45.0% |
| 2× Clefairy | 85.3% | 85.0% | 57.6% | 77.5% | 39.5% | 69.0% | 48.5% |

Switch helps vs carpet A/B (rotate Party) and loses vs D (Ogerpon does not care about your Active) and vs T (Dive still prizes 60 HP Clefairy). Extra Clefairy helps vs D and feeds T. Boss pulls Budew / a weak Dragapult into Photon; vs T that flips C over 50% in the 1k screen.

Locked 30: 4 Clefairy / 2 Mewtwo ex / 4 Clefable / 4 Clefable ex / 3 Mega Clefable ex / 3 Hop / 2 Nest / 3 Energy Search / 1 Belt / 1 Tool Box / 1 Arven / **1 Boss's Orders / 1 Psychic Energy**.

Full A–T matrix (3,000 / cell, seed `20260819`) after this lock: C vs T **47.1%** (was 45.3% on 2 energy), C vs D **48.3%** (was 52.4%), C vs S **85.4%** (was 82.8%). The 1k T screen (51.2%) was high; 3k is the number.

## Last energy → which Clefable (2026-08-23)

Rule B: a Clefable **is** a Psychic Energy. 3,000 games / cell, seed `20260819`, Boss kept. The dedicated energy is noise against Rebel Clash Clefable; Mega is a 3-prize gift vs D.

| package | A | B | D | S | T | mean | D+T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **1 energy + Boss** (locked) | 86.8% | 85.1% | 49.3% | 85.7% | 48.1% | 71.0% | 48.7% |
| 5th Clefable + Boss (**illegal 5-of**) | 86.7% | 85.8% | 48.9% | 85.0% | 47.9% | 70.9% | 48.4% |
| 5th Clefable ex + Boss (**illegal 5-of**) | 86.8% | 84.7% | 49.1% | 86.0% | 47.3% | 70.8% | 48.2% |
| 4th Mega + Boss (legal name) | 86.5% | 85.1% | 47.5% | 85.4% | 47.8% | 70.5% | 47.7% |

The 5th Clefable / 5th Clefable ex break the 4-of same-name cap. **Locked 30 is the energy row:** 4 Clefairy / 2 Mewtwo ex / **4 Clefable** / 4 Clefable ex / 3 Mega / 3 Hop / 2 Nest / 3 Energy Search / Belt / Tool Box / Arven / Boss / **1 Psychic Energy**.

Full A–T matrix after restoring energy (3,000 / cell, seed `20260819`): C vs A 85.4%, B 85.9%, D 48.3%, S 85.4%, T 47.1%.

## Metronome Clefable (TWM 79 / CLC 014) — not locked (2026-08-23)

Printed text (both): *Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack.* Pay **Metronome's** cost; resolve the copied attack's damage and effects. Do not recurse into another Metronome.

| printing | type | HP | Metronome | other | Family Cup energy |
| --- | --- | --- | --- | --- | --- |
| Rebel Clash Clefable (locked) | Psychic | 110 | — | Moon Kick 60, Prankish | Psychic |
| TWM 79 | Psychic | 120 | **[C][C]** | Magical Shot 100 | Psychic |
| CLC/CMC 014 | Colorless | 70 | **[C]** | Minimize | Colorless, not Psychic |

The T2 “copy a huge attack” line is real in isolation (CLC copies Hydro Splash 180 into 160 HP Dondozo on one energy; CLC has no Ability so copied Demolish is 140 through Stance). It is not a KO into Charm Ogerpon (~270) or Dragapult ex (320). Boss-gusting Budew then Metronome copies Itchy Pollen, not Phantom Dive.

3,000 games / cell, seed `20260819`, Boss kept. Fifth slot (or fifth+sixth as TWM+CLC):

| package | A | B | D | S | T | mean | D+T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **5× RCL** (illegal 5-of) | 86.4% | 83.9% | **48.6%** | 83.7% | 46.3% | 69.8% | **47.5%** |
| 4× RCL + TWM | 87.0% | 85.3% | 46.7% | 84.9% | 46.0% | 70.0% | 46.4% |
| 4× RCL + CLC | 85.2% | 85.3% | 44.3% | 84.0% | 47.7% | 69.3% | 46.0% |
| 3× RCL + TWM + CLC | 85.7% | 85.6% | 41.9% | 84.9% | **49.9%** | 69.6% | 45.9% |

CLC density helps vs T and costs vs D. Those packages are also illegal as extra **Clefable** copies of the same name.

## Same-name cap: 5× Clefable is illegal (2026-08-23)

Family Cup uses Standard constructed copies: **at most 4 of the same name**, basic Energy unlimited. TWM 79 and CLC 014 are still named **Clefable**, so they share the cap with Rebel Clash. Clefable / Clefable ex / Mega Clefable ex are different names (4 each). Official 30-card constructed's 2-of rule is only how Set T was imported; A–S are household 30s with the 4-of cap.

The fifth RCL Clefable (and any Metronome printing as a fifth Clefable) is illegal.

## 30th card: 4th Mega, four Clefable stay Rebel Clash (2026-08-23)

If the last slot must be a Clefable-line Pokémon (Rule B, no dedicated Energy), the only legal add is **Mega Clefable ex** (a different name; the list had 3). Hop / Nest / Energy Search / Psychic Energy are also legal, but they are not that line. Replacing one of the four **Clefable** with TWM/CLC is legal and worse.

3,000 games / cell, seed `20260819`, Boss kept:

| package | A | B | D | S | T | mean | D+T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4× RCL + energy | 87.0% | 86.0% | 49.1% | 85.5% | **47.0%** | **70.9%** | **48.0%** |
| **4× RCL + 4th Mega** (locked) | 86.1% | 85.1% | **49.7%** | 85.3% | 45.6% | 70.3% | 47.6% |
| 3× RCL + TWM + 4th Mega | 86.4% | 85.2% | 46.9% | 85.6% | 45.6% | 69.9% | 46.3% |
| 3× RCL + CLC + 4th Mega | 86.7% | 85.8% | 45.2% | 85.8% | 47.0% | 70.1% | 46.1% |

Rebel Clash is the Clefable printing: Prankish + Psychic type for Party/Photon. TWM still Psychic but no Prankish and steals a name slot. CLC is Colorless 70 HP, not Psychic fuel.

Locked 30: 4 Clefairy / 2 Mewtwo ex / **4 Rebel Clash Clefable** / 4 Clefable ex / **4 Mega Clefable ex** / 3 Hop / 2 Nest / 3 Energy Search / Belt / Tool Box / Arven / Boss. **Zero dedicated Energy.**

## Mulligan bonus draws (2026-08-23)

After both players have a Basic and prizes are set, each side **always** draws one card per opponent mulligan. Extra cards stay in hand (not benched during setup). First-hand miss: C 17%, D 32%, S 6%, T 32%.

Full A–T matrix after this rule (3,000 / cell, seed `20260819`):

|  | A | B | C | D | S | T |
| --- | --- | --- | --- | --- | --- | --- |
| A | — | 68.3% | 14.4% | 4.2% | 67.7% | 47.2% |
| B | 32.3% | — | 15.9% | 1.2% | 23.2% | 50.3% |
| C | 85.8% | 84.3% | — | **51.7%** | 84.9% | 46.5% |
| D | 95.7% | 98.7% | 46.6% | — | 39.1% | 70.5% |
| S | 31.1% | 75.5% | 14.2% | **60.9%** | — | 59.0% |
| T | 52.8% | 49.4% | 53.0% | 30.9% | 39.8% | — |

Vs the same 4 Mega list without bonus draws: C vs D 49.9% → **51.7%**, D vs C 51.0% → 46.6%, S vs D 57.9% → **60.9%**. C vs T 48.1% → 46.5% (T vs C 50.9% → 53.0%); T’s extra Poffin/Candy from C’s rarer mulligans still matter.

## Belt-then-Hop trainer order (2026-08-25)

`party` plays Arven before Tool Box, Hop before Energy Search / Nest. Same 30-card lists, seed `20260819`, 3,000 / cell. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | --- | --- | --- | --- | --- | --- |
| A | — | 68.3% | 15.1% | 4.2% | 67.7% | 47.2% |
| B | 32.3% | — | 14.8% | 1.2% | 23.2% | 50.3% |
| C | 85.7% | 84.1% | — | **52.3%** | **88.5%** | 45.9% |
| D | 95.7% | 98.7% | 47.6% | — | 39.1% | 70.5% |
| S | 31.1% | 75.5% | 11.8% | **60.9%** | — | 59.0% |
| T | 52.8% | 49.4% | 53.6% | 30.9% | 39.8% | — |

Non-C cells match the mulligan table. C vs S 84.9% → **88.5%**. C vs D 51.7% → 52.3%. C vs T 46.5% → 45.9%.

## 2 Hop + 1 SM Lillie (2026-08-25)

Printed: until 6, until 8 on **your first turn**. First player cannot play a Supporter on turn 1, so 8 is going second. Screened vs 3 Hop, seed `20260819`, 3,000 / cell. C avg **72.6%** beats 3 Hop 71.8% (B 85.6% → **88.7%**, D 52.3% → 51.3%). Locked 30 is 2 Hop / 1 Lillie. Raw: `data/lab/c-sm-lillie-hop.json`.

Boss prize-close (same list): C avg **72.7%**. D stays 51.3%. A 90.7%, T 52.5%, S 80.2%.


## 151 Invitation Clefairy instead of Party (2026-08-25)

Locked C still has **no Switch**. Replacing 1–2 LOR 62 with MEW 035 (`Moon-Viewing Invitation`, bench up to 3 Clefairy) was retested after the engine learned the attack. Seed `20260819`, 3,000 / cell. Full writeup: [set-c-moon-view.md](set-c-moon-view.md).

| package | A | B | D | S | T | mean | D+T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **4 party** (locked) | 87.0% | 84.3% | **51.7%** | 84.9% | 46.5% | **70.9%** | **49.1%** |
| 3 party + 1 invite | 87.0% | 85.9% | 38.3% | 88.5% | 47.1% | 69.4% | 42.7% |
| 2 party + 2 invite | 84.9% | 85.1% | 28.3% | 91.6% | 47.0% | 67.4% | 37.6% |

The dump costs the attack and leaves 60 HP Active. Without Switch you cannot Party-then-tank the same turn, so vs D it is still a turn short. Cutting Party engines is the rest of the hole (−13 then −10 vs D) even when Invitation almost never fires (~2% vs D). Vs S it helps a winning matchup; that does not buy the D race. Stay on 4× LOR 62.

## Going-first 2+2+Prankish+ex (2026-08-26)

Human line vs D, going first, when the board is **2 Clefairy + 2 Mewtwo + Rebel Clash Clefable + Clefable ex + Belt** (not 4+1, not 3+2):

1. T1 Party + hand attach.
2. T3 Party, evolve **Prankish** on the empty Active Clefairy — bounce T2 Fighting so Demolish cannot land T4.
3. T5 another attach. T6 Demolish KOs Clefable (1 prize); the Clefairy underneath and Clefable hit discard. Promote the **support** Mewtwo.
4. T7 Transfer Charge +2 onto the Belted closer, stay to tank.
5. T8 support (230 HP) eats 140 and lives.
6. T9 evolve Lunar Zone, attach, free-retreat onto the full-HP closer, Photon for 2 prizes.

The engine now plays this Charge combo at 2 Party engines going first; going second still wants 3 Clefairy. This does not replace locked 4× LOR 62.

## Going-first 2+1+Mega+ex+tool (2026-08-26)

Human line vs D, going first, when the board is **2 Clefairy + 1 Mewtwo + Mega Clefable ex + Clefable ex + Maximum Belt** (second Mewtwo not in hand):

1. T1 Party + hand attach (D cannot Demolish yet).
2. T3 Party, evolve **Mega** on the empty Active Clefairy (320 HP). Mega evolves from Clefairy.
3. T4 Demolish (180 HP left). T5 attach, evolve Lunar Zone on the leftover Clefairy.
4. T6 Demolish (40 HP left). T7 attach a retreat payer, swap to Clefable ex (260).
5. T8 Demolish on the ex. T9 attach, swap to the full-HP Belted Mewtwo, Photon.

If the second Mewtwo is already in hand, the 2+2 Charge line still takes priority. This does not replace locked 4× LOR 62.

## Going-second 3+1+Mega+ex+tool (2026-08-26)

Human line vs D, going second, when the board is **3 Clefairy + 1 Mewtwo + Mega Clefable ex + Clefable ex + Maximum Belt** (fourth Clefairy not still in hand/deck; second Mewtwo not for 3+2):

1. T2 Party +3 (two benched engines + hand attach). Empty Active Clefairy is the chump.
2. T3 Demolish takes that Clefairy (1 prize).
3. T4 Party +2, evolve **Mega** on the Active Clefairy (320 HP).
4. T5 Demolish (180 left). T6 +1 on Mewtwo. T7 Demolish (40 left).
5. T8 +1 retreat payer, evolve **Lunar Zone**, switch onto Clefable ex (260).
6. T9 Demolish on the ex. T10 +1, switch to the full-HP Belted Mewtwo, Photon.

If a fourth Clefairy can still come down, keep assembling 4+1. This does not replace locked 4× LOR 62.

## A–T matrix after 2+2 / 2+1 scripts (2026-08-26)

First pass locked Clefairy at 2 whenever Mega/Prankish pieces were in hand. That stole
PR #33's going-first 4+1 / 3+2: C vs D **57.5% → 52.8%** (first **58.2% → 48.2%**).

Fix: 2+2 / 2+1 only start when no more Clefairy are in hand or deck. Cap stays 4 (or 3
with both Mewtwo). Seed `20260819`, 3,000 / cell. Raw: `data/lab/family-cup-30-matrix.json`.

|  | A | B | C | D | S | T |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **A** | — | 68.3% | 11.3% | 4.2% | 67.7% | 47.5% |
| **B** | 32.3% | — | 10.4% | 1.2% | 23.2% | 50.4% |
| **C** | **88.2%** | **89.6%** | — | **57.9%** | 78.2% | **54.5%** |
| **D** | 95.7% | 98.7% | 40.7% | — | 39.1% | 70.4% |
| **S** | 31.1% | 75.5% | 20.8% | **60.9%** | — | 59.7% |
| **T** | 51.7% | 49.6% | 44.6% | 31.0% | 41.1% | — |

C vs D **57.9%** (first **58.7%** / second **57.1%**), at or above PR #33's 57.5% / 58.2% / 56.8%. C vs T **54.5%**. C vs S 78.2% is the same as PR #33 (that drop was the D scripts vs Floragato, not the 2-engine lock). C mean vs A/B/D/S/T **73.7%**.


