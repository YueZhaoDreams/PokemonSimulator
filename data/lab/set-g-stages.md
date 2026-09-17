# G staged run: Mega / Boss / Poffin on one seed and one bake

Date: 2026-09-17
Seed: `20260915`
Rule: s60. G always A; first player random.
Script: `data/lab/set_g_stages.py`
Raw: `data/lab/set-g-stages.json` (3000 games/cell, 4 stages x 7 foes)

## Why

The three PR-descs were baked on different engine states, so their absolute
numbers are not comparable stage-over-stage. Proof: re-running the
Boss-Friday baseline cell (identical list, seed 20260915, 2000 games) on the
current tree gives t60 **17.3%**, not the recorded **22.8%** — while the
later Poffin bakeoff's Friday baseline (t60 23.9 / Hedrick 31.2 / D60 6.4 /
UNL 44.6 / C60 17.6 / S60 66.0 / H 94.4 @2000) still reproduces on this tree
(s2 row below, within sampling noise). This run re-bakes all four stages on
the same code, seed, foes, and strategies so only the list changes.

## Stages (60 cards each, copy-legal)

| Stage | Mega | Boss | Poffin | List |
| --- | ---: | ---: | ---: | --- |
| s0_none | 0 | 0 | 0 | Friday minus Mega/Boss; Emolga + Potion / Poke Ball / Plusle back in the printed slots |
| s1_mega | 1 | 0 | 0 | s0 minus Emolga plus Mega Clefable ex (= Boss-Friday live G, verified identical) |
| s2_boss | 1 | 3 | 0 | s1 minus Potion / Poke Ball / Plusle plus 3 Boss's Orders (= `SET_G_FRIDAY_NAMES`) |
| s3_poffin | 1 | 3 | 4 | s2 minus Tornadus / Hop's Cramorant / Relicanth / Indeedee plus 4 Buddy-Buddy Poffin (= `SET_G_NAMES` lock) |

## Win rates (3000 games/cell)

| Stage | T60 | Hedrick | D60 | UNL | C60 | S60 | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| s0_none | 18.7 | 28.2 | 7.7 | 40.1 | 7.8 | 54.1 | 96.1 |
| s1_mega | 17.5 | 28.2 | 7.7 | 41.2 | 13.5 | 62.5 | 95.9 |
| s2_boss | 23.6 | 31.7 | 6.8 | 45.6 | 16.8 | 66.3 | 94.9 |
| s3_poffin | 20.5 | 33.0 | 6.6 | 45.4 | 21.0 | 68.4 | 96.3 |

Stage-over-stage deltas (pp):

| Step | T60 | Hedrick | D60 | UNL | C60 | S60 | H |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| +Mega (s1-s0) | -1.2 | 0.0 | 0.0 | +1.1 | +5.7 | +8.5 | -0.2 |
| +Boss (s2-s1) | +6.1 | +3.4 | -1.0 | +4.5 | +3.3 | +3.7 | -1.0 |
| +Poffin (s3-s2) | -3.1 | +1.3 | -0.2 | -0.2 | +4.2 | +2.1 | +1.4 |
| total (s3-s0) | +1.8 | +4.8 | -1.1 | +5.3 | +13.2 | +14.3 | +0.2 |

Loss-weighted vs s0 (all 7 foes): 0.2290 -> 0.2486 -> 0.2797 -> **0.2865**.
Loss-weighted vs s0 (competitive t60/Hedrick/D60): 0.1736 -> 0.1697 -> 0.1963 -> 0.1892.

## Read

- Mega is a slow-matchup card: C60 +5.7, S60 +8.5 (320 HP Shooting Moons
  wall); fast Dragapult is flat (t60 -1.2 is noise-level on one cell).
- Boss is the Dragapult fix: T60 +6.1, Hedrick +3.4, UNL +4.5. D60 -1.0:
  Charm Ogerpon still does not want the swap, same sign as the Friday bake.
- Poffin is consistency: C60 +4.2, S60 +2.1, H +1.4, Hedrick +1.3; t60
  -3.1 (bench flood feeds Phantom Dive, same known tradeoff, slightly
  larger on this bake than the -2.5pp in #104).
- Net s0 -> s3: every foe up except D60 (-1.1). C60/S60 roughly double
  (+13.2/+14.3pp); T60 nets only +1.8pp because Poffin gives back half
  the Boss gain there.
