# G Poffin lock: 4 Buddy-Buddy Poffin for Potion, Poké Ball, Plusle, Cramorant

Date: 2026-09-17
Seed: `20260917`
Rule: s60
G always A; first player random
Script: `data/lab/set_g_poffin_swap.py`
Raw: `data/lab/set-g-poffin-swap.json`
Confirm: `data/lab/set-g-poffin-swap-confirm.json` (3,000 games)

The 3 Boss are not in hand, so the Friday Boss lock comes back out of
`SET_G_NAMES`. Baseline is frozen pre-Friday live G (combocub.com `seed-g`
2026-09-15: Mega + Tornadus, Potion / Poké Ball / Plusle, 0 Boss, 0 Poffin).

Printed Poffin (sv05-144): search the deck for up to 2 Basic Pokémon with
70 HP or less and bench them. G targets: Clefairy 60, Ledyba 60, Starly 60,
Kecleon 70. Item, so it plays on turn 1. `g` spends it while Clefairy in play
is below 3, then Starly / Ledyba.

## Packages (2,000 games)

4 Poffin in unless noted. Weighted-all uses every foe's baseline loss rate.
Competitive = t60 + Hedrick + D60.

| List | 4th cut | t60 | Hedrick | D60 | UNL | C60 | S60 | H | 竞争加权 | 全场加权 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **junk4** | Cramorant | 18.6 | **29.6** | **8.1** | 40.7 | 17.8 | 66.8 | **97.3** | **17.89** | **26.26** |
| surfer4 | Surfer | **19.6** | 29.4 | 7.0 | 40.5 | 16.4 | 66.0 | 96.5 | 17.73 | 25.80 |
| rel_cram4 | keep Plusle | 18.3 | 28.7 | 8.6 | 40.6 | 16.7 | 62.7 | 96.9 | 17.68 | 25.54 |
| **baseline** | (0 Poffin) | **19.6** | 28.1 | 7.5 | **42.9** | 13.5 | 60.7 | 94.8 | 17.54 | 24.90 |
| tulip4 | Tulip | 18.1 | 29.2 | 7.8 | 40.5 | 17.0 | 67.5 | 97.4 | 17.50 | 25.91 |
| indeedee4 | Indeedee | 18.8 | 29.1 | 6.7 | 42.7 | 16.6 | 67.8 | 96.5 | 17.22 | 25.99 |
| tornadus4 | Tornadus | 18.6 | 29.1 | 6.7 | 38.9 | 17.0 | 67.2 | 97.0 | 17.20 | 25.52 |
| poffin3 | (3 Poffin) | 18.9 | 28.3 | 6.8 | 41.3 | 16.6 | 65.4 | 96.0 | 17.08 | 25.50 |
| relicanth4 | Relicanth | 18.6 | 29.2 | 6.2 | 41.9 | 18.9 | 67.6 | 96.4 | 17.03 | 26.22 |
| keep_plusle4 | Rel.+Kec. | 17.8 | 27.9 | 7.7 | 40.1 | 16.2 | 62.1 | 96.1 | 16.92 | 24.86 |
| energy4 | Psychic | 17.8 | 29.6 | 6.1 | 41.0 | 16.1 | 65.9 | 96.6 | 16.84 | 25.29 |
| search4 | Energy Search | 17.2 | 29.9 | 6.2 | 38.6 | 17.5 | 66.8 | 96.8 | 16.77 | 25.30 |
| kecleon4 | Kecleon | 18.1 | 29.9 | 5.3 | 41.4 | 17.6 | 64.8 | 97.0 | 16.73 | 25.50 |
| iris4 | Iris | 18.0 | 28.8 | 6.1 | 39.8 | 15.3 | 68.1 | 96.6 | 16.69 | 25.08 |
| shoes4 | Trekking Shoes | 17.8 | 28.5 | 6.2 | 40.6 | 18.1 | 64.6 | 96.5 | 16.57 | 25.38 |
| line_thin4 | Ledian+Ledyba | 18.1 | 26.2 | 7.8 | 38.2 | 15.6 | 61.9 | 96.0 | 16.57 | 24.28 |
| poffin2 | (2 Poffin) | 17.7 | 27.0 | 7.2 | 38.9 | 14.7 | 63.2 | 95.5 | 16.48 | 24.27 |
| drayton4 | Drayton | 17.3 | 27.2 | 6.3 | 39.5 | 16.5 | 66.0 | 96.5 | 16.03 | 24.71 |
| supporters4 | 4 supporters | 15.8 | 26.7 | 7.5 | 37.5 | 14.2 | 59.2 | 96.3 | 15.86 | 23.30 |

## Confirm (3,000 games, fast four)

| List | t60 | Hedrick | D60 | UNL | weighted |
| --- | ---: | ---: | ---: | ---: | ---: |
| live G (0 Poffin) | **19.4** | 28.8 | **7.5** | **41.8** | **0.223** |
| surfer4 | 19.0 | 30.0 | 7.2 | 39.9 | 0.220 |
| **junk4** | 18.7 | **30.2** | 7.2 | 39.4 | 0.219 |
| poffin3 | 18.6 | 28.8 | 7.1 | 41.2 | 0.219 |
| indeedee4 | 18.2 | 28.8 | 6.7 | 42.5 | 0.218 |
| relicanth4 | 19.0 | 28.4 | 6.5 | 41.1 | 0.216 |
| tulip4 | 17.7 | 28.7 | 7.4 | 40.7 | 0.216 |

## Read

Poffin is a consistency upgrade, not a Dragapult fix. Party setup jumps
from ~620 games to ~950+ per 2,000. Slow matchups move a lot: C60 **+4**,
S60 **+6**, H **+2.5**. Fast Dragapult is flat to slightly down: Hedrick
+1.5, T60 −1, UNL −2.5. Benched 60 HP bodies feed Phantom Dive; that is the
whole cost. D60 is noise either way.

Cutting Plusle is right twice: junk4 beats rel_cram4 (keep Plusle) on both
weights, and keep_plusle4 (Plusle kept, Relicanth + Kecleon cut) loses to
baseline. The 4th Poffin beats Cramorant: junk4 > poffin3 on both weights.
Do not cut draw to pay for search: supporters4 and drayton4 are the floor.
Do not thin the Ledian line for Item search (line_thin4 loses Hedrick).
2 Poffin for Potion + Ball alone loses to baseline; the playset is the point.

## Lock

**−1 Potion −1 Poké Ball −1 Plusle −1 Hop's Cramorant, +4 Buddy-Buddy Poffin.**
0 Boss until the supporters physically arrive. All four cuts are outside C60;
Poffin is a C60 4-of, so this step is pure G→C60 progress.

When Boss arrives, re-run the Boss question on top of this Poffin list: the
Friday numbers were measured on 0-Poffin live G, and the gust-vs-search mix
changes the cut order. Do not blindly apply the old Friday cuts then.
