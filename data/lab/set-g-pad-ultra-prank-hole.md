# Hold Pad and Ultra Ball until they have a hole

> Superseded by [set-g-pad-ultra-review.md](set-g-pad-ultra-review.md). The held Ultra Ball lost to the fixed order on fresh seeds and was reverted. Pad still waits for a hole.

Date: 2026-09-23
Seed: `20260923`
Rule: s60
Games: 3,000 / cell
Script: `data/lab/set_g_pad_ultra_prank.py`
Raw: `data/lab/set-g-pad-ultra-prank-hole.json`
Policy: `hole_ex`
Elapsed: 447.7s

Poké Pad and Ultra Ball stay in hand until the deck is missing one piece. Pad takes Clefairy while fewer than three are in hand or play, then Prankish when two Clefairy are out and the opponent's Active has an Energy, then Ledyba, Ledian, or Munkidori, ahead of Starly. Ultra Ball takes Clefable ex once any Clefairy is owned and Lunar Zone is missing, ahead of another Clefairy. Mega only after that ex is in play. Nest Ball and Poffin keep the previous list.

An earlier hold order put another Clefairy ahead of Clefable ex. On the untouched energy-lock list, ex tutors fell from about 500 games to about 150–270 and the C60 mirror fell with them. That run is `set-g-pad-ultra-prank-hole-clefairy.json`. It is not this table.

`wComp` weights T60, Hedrick, and D60 by this table's base loss rate. Binomial SE is about 0.8 pp on a 30% cell and 0.4 pp on a 6% cell.

## Head-to-head (G win rate)

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **base** | energy lock, this play | **30.1%** | 40.3% | 53.0% | 5.4% | 29.6% | 81.3% | **97.6%** | 22.4% | 31.3% |
| thin_energy | the three cuts → Psychic | **31.3%** | **43.4%** | **55.5%** | 4.5% | 32.1% | 82.0% | 96.1% | **23.2%** | **32.6%** |
| pad | Ledyba → Poké Pad | 28.8% | 41.5% | 54.4% | **6.3%** | **32.7%** | **83.3%** | 96.8% | 22.7% | 32.3% |
| ultra | Ledian → Ultra Ball | 27.7% | 37.5% | 54.2% | 4.9% | 30.8% | 82.1% | 96.6% | 20.7% | 30.7% |
| prank | Munkidori → Clefable | 28.4% | 40.7% | 53.4% | 4.4% | 30.0% | 80.4% | 96.5% | 21.5% | 30.8% |
| pad_ultra | Pad + Ultra | 27.5% | 40.5% | 51.3% | 5.9% | 29.7% | 83.1% | 97.0% | 21.9% | 30.8% |
| pad_prank | Pad + Prankish | 31.3% | 39.6% | 54.7% | 5.2% | 30.5% | 82.8% | 96.7% | 22.5% | 31.8% |
| ultra_prank | Ultra + Prankish | 27.5% | 38.1% | 50.7% | 5.2% | 28.4% | 80.1% | 95.3% | 20.9% | 29.8% |
| **full** | Pad + Ultra + Prankish | 28.6% | 38.4% | 53.7% | 4.7% | 29.7% | 80.8% | 95.7% | 21.1% | 30.6% |

The fixed-prefer base, where Ultra Ball is played whenever it is in hand, was T60 27.4%, Hedrick 40.6%, UNL 54.7%, D60 6.4%, C60 mirror 31.2%, S60 80.9% (`set-g-pad-ultra-prank.json`). This play moves that same 60 to T60 30.1% and the mirror 29.6%, D60 5.4%. Ex tutors on that list are about 430–570 games, against about 490–670 before. Ultra Ball fires a bit less often because it is held when the hole is filled.

## The three cards

`full` is wComp 21.1% against this base's 22.4%. T60 28.6% against 30.1%. Hedrick 38.4% against 40.3%. D60 4.7% against 5.4%. The Items are aimed: against T60, Pad resolves in 952 games and takes Clefairy in 388, Ledian in 90, Ledyba in 42, Munkidori in 31, Prankish in 56. Ultra Ball resolves in 1,565 and takes Clefable ex in 797, Clefairy in 413, Ledian in 132.

The second Ultra Ball alone is the drag. Hedrick 40.3% → 37.5%, D60 5.4% → 4.9%, wComp 20.7%. It does take Ledian (156 games vs T60, 223 vs the mirror) and Clefable ex (765–892). The printed cost is still discard 2.

Pad alone is wComp 22.7%, +0.3. T60 28.8% is under this base's 30.1%. Hedrick 41.5%, the mirror 32.7%, D60 6.3%, S60 83.3%. Most Pad hits are Clefairy (about 380–460), then Ledian (about 70–150).

`thin_energy` is the top of the table on wComp, T60, Hedrick, and UNL. D60 falls to 4.5%. The 60 stays at Ledian 3, Ledyba 4, Munkidori 2, Psychic 16.

## Lock

`SET_G_NAMES` stays the energy lock. Sleeve none of Poké Pad, the second Ultra Ball, or Rebel Clash Clefable. Holding the Item until the hole is real, and sending Ultra Ball back to Clefable ex, does not make the three-card swap win.
