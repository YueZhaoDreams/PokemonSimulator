# C60 + Telepathic Psychic Energy (locked 2)

Date: 2026-09-14
Seed: `20260911`
Rule: s60
Games: 3,000 / cell (C60 always A; first player random)
Script: `data/lab/set_c60_telepathic_energy.py`
Raw: `data/lab/set-c60-telepathic-energy.json`

**Telepathic Psychic Energy** (POR 88 / ME03 88): Special Energy. Attach from hand to a Psychic Pokémon, then search up to 2 Basic Psychic onto the Bench. Party cannot search it from the deck. Energy Switch cannot move it. Seed Mewtwo ex is Lightning, so the bench search fires on Clefairy / Clefable, not Mewtwo.

Swap: **N Telepathic for N Psychic Energy**. Locked C60 is **14 Psychic + 2 Telepathic** (Tool Box later cut for the 14th Psychic). Family Cup Set C stays 30 with 0 Telepathic.

Field: every s60 60-card seed list except C60 itself. G uses dedicated `g` (not carnival). H has no Zapdos script — `nuzzle` is the Lightning stand-in.

| Foe | AI | 15 Psychic | tele1 | **tele2** | tele3 | tele4 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | **48.7%** | 47.5% | 49.6% | 47.7% | 47.5% |
| Hedrick Dragapult | phantom | 58.2% | 58.2% | 58.5% | **59.3%** | 58.0% |
| UNL Pidgeot / Rotom | phantom | **84.4%** | 84.6% | 83.6% | 82.8% | 84.1% |
| D60 Charm Ogerpon | demolish | 74.2% | 74.8% | 77.7% | 77.0% | **79.6%** |
| S60 Floragato | slash | 99.5% | **99.8%** | 99.7% | 99.4% | 99.5% |
| G carpet | g | 90.0% | 89.8% | 90.2% | **91.1%** | 90.8% |
| H TR Zapdos | nuzzle | 97.2% | 97.3% | 96.8% | 97.2% | **97.4%** |
| **平均胜率** | — | 78.9% | 78.9% | 79.4% | 79.2% | **79.6%** |
| **加权胜率** | — | 63.5% | 63.2% | **64.4%** | 63.8% | 64.0% |

加权：对手越弱权越低。权重固定为 15-Psychic C60 对该对手的败率 `1 − WR_15P`（T60 34.7%，Hedrick 28.3%，D60 17.5%，UNL 10.6%，G 6.7%，H 1.9%，S60 0.3%）。各列共用同一套权重。

3000-game noise on a 50% cell is about ±0.9 points. Blowouts (S60 / G / H, already 90%+) do not move. UNL is already 84% and slightly prefers fewer specials.

Competitive pair (T60 + Hedrick) mean: 15-Psychic 53.5%, tele2 **54.1%**, tele3 53.5%, tele1 52.9%, tele4 52.8%. Include D60: tele2 61.9%, tele4 61.7%, 15-Psychic 60.4%.

tele2 is the only count that does not lose T60. tele4 is a D60 specialist (empty Clefairy is already the 1-prize chump; extra Party outruns Demolish) and collapses T60 going second (43.6% vs 15-Psychic 46.8%).

Lock **2 Telepathic Psychic Energy** into C60 (`SET_C60_NAMES`). Do not go to 3 or 4. Family Cup Set C stays 30 with 0. The field ranking does not change: coin vs Candy Dragapult, favorite vs Hedrick, crush vs UNL / Ogerpon / Floragato / G / H.

Do not spend the Belt package (Maximum Belt + Tool Box + Arven) on a 3rd/4th Telepathic either. That swap helps Dragapult and dumps Charm Ogerpon (see [set-c60-belt-vs-telepathic.md](set-c60-belt-vs-telepathic.md)).
