# Ledyba and Iris's Fighting Spirit in the same 60

Date: 2026-09-23
Seeds: `20260928`, `20260929` (3,000 games each, 6,000 per cell)

**Lock:** live `SET_G_NAMES` is `ledyba_energy` from this matrix. One Ledyba became Psychic Energy (Psychic 20, Ledyba 2). Iris's Fighting Spirit stays. The table below still uses the four-Psychic list as `base`.
Rule: s60
Script: `data/lab/set_g_ledyba_lillie.py`
Raw: `data/lab/set-g-ledyba-lillie.json`
Elapsed: 455s

`base` in the table is the four-Psychic list this matrix started from: Psychic 19, Telepathic 2, Ledian 2, Ledyba 3, Munkidori 1, one Iris's Fighting Spirit. Strategy `g`, on the engine that plays Lillie at `17 + (cards drawn − 3)`, ahead of Iris (discard, then draw until 6) and Drayton (top 7).

The two swaps below were previously scored on separate lists, on the engine from before that Lillie priority. This run puts them in one 60.

| Variant | Swap |
| --- | --- |
| base | live four-Psychic list |
| lillie_iris | Iris's Fighting Spirit → Lillie |
| ledyba_energy | one Ledyba → Psychic Energy |
| both | both of those swaps |
| both_energy | one Ledyba → Psychic, and Iris → Psychic |

wComp weights T60, Hedrick, and D60 by how often this base loses. Difference SE on wComp is about 0.39 pp. A 30% cell's difference SE is about 0.84 pp.

## Head-to-head (G win rate)

| Variant | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| base | 30.2% | 42.0% | 55.5% | 4.8% | 32.5% | 82.3% | 96.5% | 22.4% | 32.2% |
| lillie_iris | 31.1% | 40.9% | 55.2% | 4.8% | 33.5% | 82.5% | 96.6% | 22.4% | 32.3% |
| **ledyba_energy** | 32.0% | 43.6% | 57.2% | 5.1% | 35.6% | 84.2% | 96.1% | **23.6%** | **33.8%** |
| both | 31.6% | 42.3% | 57.4% | 4.9% | 34.1% | 84.8% | 96.0% | 23.0% | 33.2% |
| both_energy | 30.3% | 42.7% | 57.3% | 5.2% | 33.6% | 83.9% | 96.1% | 22.8% | 32.9% |

## Contrasts (wComp)

| Contrast | Δ wComp | z |
| --- | ---: | ---: |
| both − base | +0.56 | +1.4 |
| both − lillie_iris | +0.58 | +1.5 |
| both − ledyba_energy | −0.55 | −1.4 |
| both − both_energy | +0.21 | +0.5 |
| lillie_iris − base | −0.01 | −0.0 |
| ledyba_energy − base | +1.11 | +2.8 |

## What to sleeve

**One Ledyba becomes Psychic Energy. Iris's Fighting Spirit stays.** That single cut is wComp 23.6%, +1.11 over the live list (z +2.8). Both seeds are up on T60 (30.9 / 33.0 against 29.2 / 31.3), Hedrick (43.5 / 43.8 against 42.1 / 41.9), and D60 (5.0 / 5.3 against 4.6 / 5.0).

**Doing both swaps in one list sits under that cut.** Ledyba → Psychic plus Iris → Lillie is wComp 23.0%. It is +0.56 over the live list (z +1.4) and −0.55 under Ledyba → Psychic alone (z −1.4). Hedrick is lower on both seeds (41.2 / 43.4 against 43.5 / 43.8). The C60 mirror is lower on both seeds (34.1 / 34.0 against 36.0 / 35.3).

**Lillie ties the card it replaces, and ties a Psychic in that slot once the Ledyba is already gone.** Iris → Lillie alone is −0.01 wComp (z −0.0). On the Ledyba-cut list, Lillie against Iris → Psychic is +0.21 (z +0.5). Lillie resolves in about 1,850–2,500 of 6,000 games. Printed text: Lillie draws until 6, or until 8 on the first turn. Iris discards another card, then draws until 6.

Live `SET_G_NAMES` is the Ledyba → Psychic row. Iris's Fighting Spirit stays. The earlier shipment note that sleeved one Lillie was scored before G was taught to play Lillie ahead of Iris.
