# C60 Belt package vs 2 Telepathic + 1 card (keep Belt)

Date: 2026-09-15
Seed: `20260911`
Rule: s60
Games: 3,000 / cell (C60 always A; first player random)
Script: `data/lab/set_c60_belt_vs_telepathic.py`
Raw: `data/lab/set-c60-belt-vs-telepathic.json`

Photon Kinesis is `10 + 30 × Psychic Energy attached to all of your Pokémon`. **Telepathic Psychic Energy** (POR 88 / ME03 88) provides Psychic (+30). Attach from hand to a Psychic Pokémon, then bench up to 2 Basic Psychic; Party can then load two Basic Psychic (**+60**). Seed Mewtwo ex is Lightning, so that bench search fires on Clefairy / Clefable, not Mewtwo. **Maximum Belt** is ACE SPEC +50 vs Pokémon ex, and C60 spends **Tool Box + Arven** to find it.

Swap: **Maximum Belt + Tool Box + Arven → 2 Telepathic + 1 other**. Locked C60 already has 2 Telepathic in place of 2 Psychic, so `tele2_*` is **4 Telepathic**. `psy2_*` restores those 2 Psychic and spends the free slot on the third card (still 2 Telepathic). `energy3` is the control: the three slots become 3 Psychic Energy. Family Cup Set C stays 30 with Belt.

Field: every s60 60-card seed list except C60 itself. G uses dedicated `g`. H has no Zapdos script — `nuzzle` is the Lightning stand-in.

## 2 Telepathic + 1 card (4 Telepathic total)

| Foe | AI | **belt** | energy3 | **tele2_energy** | stretcher | boss | retrieval | eswitch | iono | stamp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | 49.6% | 51.9% | **53.2%** | 52.0% | 53.0% | 52.6% | 50.0% | 51.1% | 52.2% |
| Hedrick Dragapult | phantom | 58.5% | **63.4%** | 63.3% | 61.9% | 61.6% | 63.0% | 60.7% | 59.9% | 62.9% |
| UNL Pidgeot / Rotom | phantom | 83.6% | 85.8% | 85.1% | 85.0% | **86.1%** | 85.9% | 85.7% | 84.9% | 84.9% |
| D60 Charm Ogerpon | demolish | **77.7%** | 61.6% | 63.7% | 61.8% | 63.4% | 62.4% | 62.2% | 64.0% | 61.0% |
| S60 Floragato | slash | **99.7%** | 99.4% | **99.7%** | 99.5% | 99.5% | 99.3% | **99.7%** | **99.7%** | 99.6% |
| G carpet | g | 90.2% | 93.3% | 93.6% | 93.0% | 93.0% | **94.1%** | 93.4% | 92.9% | **94.1%** |
| H TR Zapdos | nuzzle | 96.8% | 96.8% | 97.3% | 97.1% | 97.1% | 97.1% | 96.9% | **97.4%** | 96.7% |
| **平均胜率** | — | **79.4%** | 78.9% | **79.4%** | 78.6% | 79.1% | 79.2% | 78.4% | 78.6% | 78.8% |
| **加权胜率** | — | 64.3% | 64.5% | **65.2%** | 64.0% | 64.7% | 64.8% | 63.1% | 63.5% | 64.3% |

加权：对手越弱权越低。权重固定为 locked belt C60 对该对手的败率 `1 − WR_belt`（T60 50.4%，Hedrick 41.5%，D60 22.3%，UNL 16.4%，G 9.8%，H 3.2%，S60 0.3%）。各列共用同一套权重。

## Restore 2 Psychic + 1 card (keep locked 2 Telepathic)

| Foe | **belt** | psy2_stretcher | psy2_boss | psy2_retrieval | psy2_eswitch | psy2_iono | psy2_stamp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T60 | 49.6% | 51.4% | 51.7% | 51.8% | 52.0% | 51.1% | **52.4%** |
| Hedrick | 58.5% | 62.0% | 61.0% | **63.0%** | 62.5% | 60.3% | 61.7% |
| UNL | 83.6% | 84.5% | 84.3% | 84.9% | 84.6% | **86.2%** | 85.1% |
| D60 | **77.7%** | 59.7% | 57.0% | 57.0% | 58.7% | 60.4% | 58.4% |
| **加权胜率** | 64.3% | 63.5% | 62.9% | 63.5% | 63.7% | 63.2% | 63.6% |

`psy2_energy` is `energy3` (3 Psychic in the three slots).

## Read

The +60 line is real: one Telepathic attach onto Clefairy benches two Party engines, then Party loads two Basic Psychic. That is better Photon math than Belt's +50 **when the energy is actually in play**. It does not replace the **Charm 260 breakpoint**.

Photon with 7 Psychic is 220. Belt vs ex makes **270**, which OHKOs Bravery Charm Ogerpon (260). Without Belt you need 9 Psychic (280). Extra Telepathic copies and extra basic Energy do not hit that line often enough: every cut-Belt cell dumps D60 by **13–21 points**, and going second vs D60 falls from belt 74.5% into the low 50s.

Dragapult likes the cut. Best trial is **tele2_energy** (4 Telepathic + 14 Psychic): T60 **53.2%** (+3.6), Hedrick **63.3%** (+4.8). Competitive pair mean 58.2% vs belt 54.0%. Weighted field even ticks up (65.2% vs 64.3%) because T60 / Hedrick outweigh D60. That is the same trap as Lillie's Clefairy ex: a Dragapult tweak that spends the Ogerpon race.

`energy3` (keep 2 Telepathic, fill the three slots with Psychic) already takes most of the Dragapult gain. The extra 2 Telepathic on top (`tele2_energy`) add a bit more T60 and save ~2 D60 points versus `energy3`, but D60 is still 14 points under Belt. Third-card extras (Stretcher, Boss, Retrieval, Stamp, Iono, Energy Switch) do not recover Charm.

3000-game noise on a 50% cell is about ±0.9 points. Blowouts (S60 / G / H) do not move.

Do not lock this swap. Keep **Maximum Belt + Tool Box + Arven** in C60. Keep the energy line at **13 Psychic + 2 Telepathic**. Do not spend trainer slots on a 3rd/4th Telepathic. Family Cup Set C stays 30 with Belt.
