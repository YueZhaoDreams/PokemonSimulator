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

The fifth RCL Clefable (and any Metronome printing as a fifth Clefable) is illegal. The 30th card returns to **1 Psychic Energy** — the last legal bakeoff winner versus a 4th Mega (3 prizes). Locked 30: 4 Clefairy / 2 Mewtwo ex / **4 Clefable** / 4 Clefable ex / 3 Mega / 3 Hop / 2 Nest / 3 Energy Search / Belt / Tool Box / Arven / Boss / **1 Psychic Energy**.


