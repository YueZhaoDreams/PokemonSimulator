# G → C60: this shipment stays in the box

Date: 2026-09-23
Seed: `20260923`
Rule: s60
Games: 3,000 / cell (trial list always A; first player random)
Script: `data/lab/set_g_c60_arrival.py`
Raw: `data/lab/set-g-c60-arrival.json`
Elapsed: 727s, plus 180s for the three Pad controls

Live G is `SET_G_NAMES` (Nest/Zone + 2 Telepathic). Strategy `g`. The cards that just arrived:

| Qty | Card | Printed text the engine played |
| ---: | --- | --- |
| 2 | Lillie (SM Ultra Prism) | Draw until you have 6. On your first turn, draw until you have 8. |
| 1 | Night Stretcher | Put 1 Pokémon or 1 Basic Energy from your discard pile into your hand. |
| 1 | Ultra Ball | Discard 2 cards. Search your deck for a Pokémon. G already has 1. |
| 2 | Poké Pad (ME03 081/088) | Search your deck for a Pokémon that doesn't have a Rule Box. |
| 2 | Clefable (Rebel Clash, holo) | Prankish: on evolve, you may put an Energy from the opponent's Active on top of their deck. 110 HP. |

Finished C60 wants 2 Lillie, 1 Stretcher, 2 Ultra Ball, 1 Pad, and 1 of these Clefable (the other Clefable name is CLC 014, which is not in the box). That count is a destination. It is not a reason to pull Drayton, Energy Retrieval, or a Darkness Energy out of G today.

`wComp` weights T60, Hedrick, and D60 by how often live G loses that matchup. Binomial SE is about 0.8 pp on a 30% cell and 0.4 pp on a 6% cell. Treat ±0.8 on T60 / Hedrick as noise.

## Head-to-head (G win rate)

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **live** | — | 28.0% | 38.9% | **53.5%** | 5.4% | 28.4% | 80.4% | 97.0% | 21.5% | 30.6% |
| lillie_iris | Iris → Lillie | **28.1%** | 39.4% | 52.6% | 5.7% | 29.6% | 80.3% | **97.6%** | 21.9% | 31.0% |
| lillie_drayton | Drayton → Lillie | 26.4% | 39.7% | 52.9% | 6.2% | 29.4% | 80.8% | 96.9% | 21.6% | 30.8% |
| lillie2 | Iris + Drayton → 2 Lillie | 26.8% | 39.5% | 53.6% | 5.5% | **30.7%** | 80.1% | 97.0% | 21.4% | 31.0% |
| stretcher | Retrieval → Night Stretcher | 27.3% | 36.7% | 51.3% | 5.2% | 25.2% | 78.2% | 96.6% | 20.7% | 29.1% |
| pad_ledian | Ledian → Poké Pad | 28.0% | 39.8% | 51.9% | **6.5%** | 29.7% | **80.9%** | 97.1% | **22.2%** | 31.2% |
| l2s_ultra | 2 Lillie + Stretcher + Ultra, −1 Darkness | 26.6% | 36.8% | 49.0% | 4.3% | 26.5% | 77.5% | 95.9% | 20.1% | 28.6% |
| l2s_prank | +1 Clefable, −1 Darkness | 25.3% | 36.4% | 51.6% | 4.6% | 25.8% | 77.4% | 96.1% | 19.7% | 28.6% |
| l2s_prank2 | +2 Clefable, −2 Darkness | 25.2% | 34.0% | 51.0% | 3.1% | 25.3% | 77.2% | 94.8% | 18.4% | 27.6% |
| l2s_pad2 | +2 Pad, −Darkness −Psychic | 24.4% | 36.2% | 49.7% | 4.4% | 25.5% | 76.6% | 95.7% | 19.2% | 28.0% |
| slice | C60's count of this box | 23.9% | 35.1% | 48.0% | 4.3% | 24.8% | 77.1% | 94.9% | 18.8% | 27.4% |

Lillie was played (about 900–1,700 games). Stretcher was played (731–983 on the 1-for-1). Prankish bounced an Energy (233 games vs T60 at 1 copy, 630 vs D60 at 2). The losses are not idle cards.

## The Pad row was a Ledian cut

`pad_ledian` is the only shipment row above live. The control splits the two halves. Same seed, 3,000 games.

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| live | — | **28.0%** | 38.9% | 53.5% | 5.4% | 28.4% | 21.5% | 30.6% |
| pad_ledian | Ledian → Pad | **28.0%** | 39.8% | 51.9% | **6.5%** | 29.7% | **22.2%** | 31.2% |
| **ledian_energy** | Ledian → Psychic Energy | 27.4% | **40.6%** | **54.7%** | 6.4% | **31.2%** | **22.2%** | **31.8%** |
| iris_pad | Iris → Pad | 26.5% | 37.9% | 53.1% | 5.5% | 28.3% | 20.8% | 30.1% |
| psychic_pad | Psychic → Pad | 26.8% | 37.2% | 52.4% | 6.3% | 27.4% | 21.1% | 30.0% |

Cutting one Ledian for a 16th Psychic matches the Pad row on wComp and beats it on Hedrick, UNL, the C60 mirror, and the whole field. Pad in place of Iris or a Psychic loses T60 and Hedrick. Two Pads lose harder (wComp 19.2%). The card is not the upgrade.

## What each card did

**Lillie.** Replacing Iris is +0.4 wComp, inside noise, and UNL drops 0.9. Replacing Drayton drops T60 28.0 → 26.4. Drayton looks at the top 7 and may take a Pokémon and a Trainer. Lillie draws until 6, or 8 on the first turn, and does not find the evolution. Both copies together (Iris and Drayton out) leave T60 at 26.8 and wComp under live. On finished C60, cutting one Lillie is one of the worst swaps, because that list has no Drayton. G is not that list.

**Night Stretcher.** Energy Retrieval puts up to 2 Basic Energy into hand. Stretcher puts 1 Pokémon or 1 Energy. The 1-for-1 loses Hedrick 38.9 → 36.7 and the C60 mirror 28.4 → 25.2. G still recycles Psychic and Darkness. Stretcher's job on C60 is a KO'd Mewtwo. There is no Mewtwo in G.

**Ultra Ball.** The second copy, paid with a Darkness Energy, drops UNL 53.5 → 49.0 and D60 5.4 → 4.3. G already has 1 Ultra Ball, 4 Nest Ball, and 4 Buddy-Buddy Poffin. On C60 the second Ultra Ball was the redundant Item once Pad existed.

**Clefable.** One Prankish drops wComp to 19.7%. Two drop it to 18.4%, the bottom of the matrix, and D60 to 3.1%. The bounce fires. It still spends a Clefairy, and G has no Mewtwo to turn that turn into prizes. C60's own lock is 1 Rebel Clash Prankish, not 2: 2 Prankish is wComp 68.5 against 69.3 for 1 Prankish + 1 Pad ([set-c60-pad-clc-cuts.md](set-c60-pad-clc-cuts.md)).

**The whole box at C60's counts** (`slice`: 2 Lillie, 1 Stretcher, 2nd Ultra, 1 Pad, 1 Clefable) is wComp 18.8%. T60 23.9%. That is the "put the new cards in" list, and it is the wrong 60.

## Lock

This matrix played the Telepathic lock (4 Ledian). Sleeve **none** of this shipment. The Ledian count changed later; see the paragraph below.

- Both Lillie stay unsleeved until Hop and Lillie's Determination are here to re-measure the draw package. Do not cut Drayton for one.
- Night Stretcher stays unsleeved. Energy Retrieval stays.
- The new Ultra Ball stays unsleeved. G keeps the one it has.
- Both Poké Pad stay unsleeved. The reverse holo is the spare for C60's 1-of, later.
- Both Rebel Clash Clefable stay unsleeved. When the Photon line exists, sleeve 1, not 2.

The Ledian → Psychic control is a real bump (Hedrick +1.7, C60 mirror +2.8, D60 +1.0, UNL +1.2, T60 −0.6 inside noise) and it is not a card from this box. It was locked into `SET_G_NAMES` afterward (Ledian 3, Psychic Energy 16). The 4 Ledian count in [set-g-nest-zone.md](set-g-nest-zone.md) is the list this matrix was played on. The next sleeve, one Pad plus one extra Ultra Ball plus one Prankish, is [set-g-pad-ultra-prank.md](set-g-pad-ultra-prank.md).
