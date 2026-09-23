# Energy-lock G: Pad, Ultra Ball, and Prankish stay out

Date: 2026-09-23
Seed: `20260923`
Rule: s60
Games: 3,000 / cell (trial list always A; first player random)
Script: `data/lab/set_g_pad_ultra_prank.py`
Raw: `data/lab/set-g-pad-ultra-prank.json`
Elapsed: 446.5s

Base is live `SET_G_NAMES`: Nest/Zone, 2 Telepathic Psychic Energy, and the Ledian → Psychic Energy swap already locked (Ledian 3, Ledyba 4, Munkidori 2, Psychic 16, Ultra Ball 1). Strategy `g`, shipped search order. Clefairy comes first while fewer than three are in play. Prankish Clefable is inserted next when that print is in the deck and missing from hand and play. Poké Pad cannot take a Rule Box. Ultra Ball can, and the list already has one.

The package under test replaces one Ledyba with Poké Pad, one Ledian with a second Ultra Ball, and one Munkidori with Rebel Clash Clefable (swsh2-75, Prankish). `thin_energy` pays those same three cuts with Psychic Energy.

`wComp` weights T60, Hedrick, and D60 by how often the base loses that matchup. D60 is the heavy weight. Binomial SE is about 0.8 pp on a 30% cell and 0.4 pp on a 6% cell. Treat ±0.8 on T60 / Hedrick as noise.

## Head-to-head (G win rate)

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **base** | energy lock | 27.4% | 40.6% | 54.7% | **6.4%** | 31.2% | 80.9% | **96.9%** | 22.1% | 31.7% |
| thin_energy | the three cuts → Psychic | **29.6%** | 41.2% | **56.7%** | 5.2% | **32.9%** | **83.9%** | 96.5% | **22.5%** | **32.7%** |
| pad | Ledyba → Poké Pad | 28.4% | **41.3%** | 54.8% | 5.9% | 31.0% | 82.0% | 96.6% | **22.5%** | 31.9% |
| ultra | Ledian → Ultra Ball | 27.4% | 37.9% | 52.3% | 6.0% | 27.9% | 82.1% | 96.4% | 21.3% | 30.3% |
| prank | Munkidori → Clefable | 27.8% | 40.4% | 53.4% | 5.6% | 30.7% | 80.7% | 96.7% | 21.9% | 31.2% |
| pad_ultra | Pad + Ultra | 27.1% | 39.1% | 52.0% | 6.4% | 30.6% | 82.4% | 95.9% | 21.7% | 31.0% |
| pad_prank | Pad + Prankish | 28.3% | 39.6% | 51.5% | 5.4% | 30.4% | 82.1% | 95.8% | 21.8% | 31.0% |
| ultra_prank | Ultra + Prankish | 26.2% | 36.7% | 50.8% | 5.3% | 28.2% | 80.0% | 95.8% | 20.3% | 29.4% |
| **full** | Pad + Ultra + Prankish | 26.9% | 39.1% | 52.3% | 4.9% | 29.3% | 82.8% | 95.7% | 21.0% | 30.4% |

The base row matches the earlier Ledian → Psychic control (T60 27.4, Hedrick 40.6, UNL 54.7, D60 6.4, C60 mirror 31.2, S60 80.9). That is the list these cards are being asked to beat.

## The three cards together

`full` is wComp 21.0% against 22.1%. Hedrick 40.6 → 39.1, UNL 54.7 → 52.3, D60 6.4 → 4.9, the C60 mirror 31.2 → 29.3. T60 27.4 → 26.9 sits inside noise. S60 80.9 → 82.8 is the cell that rises. The cards are being played. Against T60, Pad resolves in 825 games, Prankish bounces in 282, and Ultra Ball resolves in 1,630. Pad takes the Prankish Clefable in 170 of those games. Ultra Ball takes Clefable ex in 886 and the Prankish print in 212.

## What each card did alone

**Poké Pad.** One copy for a Ledyba is wComp 22.5% (+0.4) and T60 28.4% (+1.0). Hedrick +0.7 is inside noise. D60 falls 6.4 → 5.9. Pad resolves in about 840–1,320 games. With no Prankish in the deck the named pulls are small: Clefairy about 50, Ledyba about 50, Ledian about 50, Munkidori under 10. The shipped order asks for Clefairy while the play count is under three, then the bird line and the evolutions. The rest of the Pad hits are that line.

**Ultra Ball.** The second copy, paid with a Ledian, leaves T60 flat at 27.4% and drops Hedrick 40.6 → 37.9 and the mirror 31.2 → 27.9. wComp 21.3%. The copy already in the deck takes Clefable ex in about 470–670 games per matchup. Two copies take it in about 810–1,140, and Mega Clefable ex rises with them (about 160–320). That is the Pokémon the search asks for once a Clefairy is the first miss.

**Prankish.** One Clefable for a Munkidori is wComp 21.9%. T60 27.8% and Hedrick 40.4% are noise. UNL 54.7 → 53.4 and D60 6.4 → 5.6. The bounce fires (232 games vs T60, 384 vs D60). Stacking it onto Pad (`pad_prank`) makes Pad take the Prankish print in 172–268 games, the largest named Pad pull in that row, and wComp is still 21.8%. UNL falls to 51.5%.

`ultra_prank` is the bottom of the matrix, wComp 20.3%.

## Same three cuts, three Psychic

`thin_energy` is the control for "the cuts were the upgrade." T60 29.6%, UNL 56.7%, the mirror 32.9%, S60 83.9%. D60 falls to 5.2%. wComp is 22.5%, +0.4 on the base, the same wComp as Pad alone and inside the noise of a score that leans on D60. The 60 stays at Ledian 3, Ledyba 4, Munkidori 2, Psychic 16.

## The on-demand order

A hole picker (Clefairy under two copies in hand or play, Prankish when an Energy can be bounced, otherwise the missing gust piece) was measured on this same seed and is stored in `set-g-pad-ultra-prank-ondemand.json`. It is not the sleeve decision. On that policy the energy-lock list itself fell to Hedrick 36.3% and S60 71.9% (wComp 20.3%). The three-card package was 19.8% under its own weakened base. Search shipped here is the fixed order above.

## Lock

`SET_G_NAMES` stays the energy lock. Sleeve none of Poké Pad, the second Ultra Ball, or Rebel Clash Clefable.

- The three together lose Hedrick, UNL, D60, and the mirror.
- Pad alone is a +0.4 wComp, inside noise, and the same seats filled with Psychic win T60, UNL, the mirror, and S60 by more.
- The second Ultra Ball spends its searches on Clefable ex and Mega.
- One Prankish bounces an Energy and still loses UNL and D60. Pad does take it when both are in the list. That pair loses too.
