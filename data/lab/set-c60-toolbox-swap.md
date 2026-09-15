# C60 Tool Box 1-for-1 (keep Belt + Arven)

Date: 2026-09-15
Seed: `20260911`
Rule: s60
Games: 3,000 / cell (C60 always A; first player random)
Script: `data/lab/set_c60_toolbox_swap.py`
Raw: `data/lab/set-c60-toolbox-swap.json`

**Tool Box** is printed top 7, any Tools into hand. **Arven** is still the full-deck Tool + Item search, so Maximum Belt (ACE SPEC +50 vs ex) stays findable. This is not the three-slot Belt cut: Charm Ogerpon's Photon 7 + Belt = 270 OHKO on 260 Charm remains.

Swap: **1 Tool Box → 1 other**. Locked C60 stays 13 Psychic + 2 Telepathic + Belt + Arven. Family Cup Set C stays 30 with Tool Box.

Field: every s60 60-card seed list except C60 itself. G uses dedicated `g`. H has no Zapdos script — `nuzzle` is the Lightning stand-in.

| Foe | AI | **toolbox** | **energy** | tele | stretcher | boss | retrieval | eswitch | iono | hop |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | 49.6% | 50.5% | 49.4% | 48.6% | 47.7% | **50.6%** | 48.5% | 47.5% | 49.3% |
| Hedrick Dragapult | phantom | 58.5% | 60.7% | **60.9%** | 60.2% | 58.0% | 59.9% | 59.6% | 58.6% | 60.0% |
| UNL Pidgeot / Rotom | phantom | 83.6% | **86.4%** | 85.3% | 83.7% | 84.5% | 84.4% | 84.2% | 84.9% | **86.4%** |
| D60 Charm Ogerpon | demolish | 77.7% | **78.9%** | 77.2% | 75.9% | 77.2% | 76.3% | 76.9% | 78.3% | 78.0% |
| S60 Floragato | slash | 99.7% | 99.6% | 99.7% | 99.5% | 99.7% | 99.4% | **99.8%** | 99.6% | **99.8%** |
| G carpet | g | 90.2% | **91.7%** | 91.6% | 90.4% | 90.3% | **91.7%** | 91.6% | 90.3% | 91.4% |
| H TR Zapdos | nuzzle | 96.8% | 97.1% | 97.6% | 97.5% | 97.1% | 97.1% | 97.1% | 97.6% | **97.7%** |
| **平均胜率** | — | 79.4% | **80.7%** | 80.2% | 79.4% | 79.2% | 79.9% | 79.7% | 79.6% | 80.4% |
| **加权胜率** | — | 64.3% | **65.9%** | 65.2% | 64.2% | 63.6% | 65.1% | 64.3% | 63.9% | 65.1% |

加权：对手越弱权越低。权重固定为 locked Tool Box C60 对该对手的败率 `1 − WR_toolbox`（T60 50.4%，Hedrick 41.5%，D60 22.3%，UNL 16.4%，G 9.8%，H 3.2%，S60 0.3%）。各列共用同一套权重。

Competitive pair (T60 + Hedrick): toolbox 54.0%, **energy 55.6%**, retrieval 55.2%, tele 55.2%. Include D60: toolbox 61.9%, **energy 63.4%**.

## Read

Top-7 Tool Box is the weak Belt tutor. Cutting it does **not** dump Charm, because Arven still searches Belt. The three-slot Belt cut lost 14 D60 points; this 1-for-1 does not.

**Psychic Energy** is the only replacement that is up on T60, Hedrick, UNL, **and** D60 (T60 +0.9, Hedrick +2.3, UNL +2.8, D60 +1.3). T60 going second stays 48.6%. Weighted **65.9%** vs toolbox 64.3%.

A 3rd Telepathic in that slot is the trap from the energy-count lab in a milder form: Hedrick likes it (+2.5) but T60 going second falls to **46.4%** (toolbox 48.6%). Do not go to 3 Telepathic here either.

4th Boss and 3rd Iono lose T60 (−2.0 / −2.2). 2nd Stretcher loses T60 and D60. 2nd Retrieval is a wash on T60 (+0.9) and spends D60 (−1.4). Extra Hop / Energy Switch do not beat the 14th Psychic.

3000-game noise on a 50% cell is about ±0.9 points. Energy's Hedrick / UNL gaps are outside that; T60 is on the edge and every competitive cell moves the same way.

If Tool Box is cut, the slot is a **14th Psychic Energy** (14 Psychic + 2 Telepathic, Belt + Arven kept). Do not put a 3rd Telepathic there. Family Cup Set C stays 30 with Tool Box. Locked C60 is unchanged until that 14th Psychic is accepted as a lock.
