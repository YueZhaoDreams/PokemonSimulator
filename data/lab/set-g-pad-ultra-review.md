# Review: Pad, second Ultra Ball, Prankish on energy-lock G

Date: 2026-09-23
Seeds: `20260924`, `20260925` (3,000 games each, 6,000 per cell)
Rule: s60
Script: `data/lab/set_g_pad_ultra_review.py`
Raw: `data/lab/set-g-pad-ultra-review.json` (policy `ultra_fixed`)
Elapsed: 905s

This supersedes the sleeve reading of [set-g-pad-ultra-prank.md](set-g-pad-ultra-prank.md) and [set-g-pad-ultra-prank-hole.md](set-g-pad-ultra-prank-hole.md).

## What the review changed

1. **Noise.** `run_simulation` draws every game from one `Random(seed)`. Two lists never replay the same games, so two cells are independent samples. At 3,000 games the difference of two 30% cells has SE 1.2 pp, not 0.8. The earlier write-ups read 1–2 pp single-cell moves as results. This matrix uses 6,000 games per cell (difference SE about 0.84 pp at 30%, 0.40 pp on wComp).
2. **Fresh seeds.** The hold-until-hole order was tuned while looking at seed `20260923`. This matrix uses two seeds that were not used for tuning.
3. **Ultra Ball legality.** Printed: "Discard 2 cards from your hand. Search your deck for a Pokémon." About 5% of G's Ultra Ball plays had fewer than 2 other cards; the engine discarded the Ball and one card and searched nothing. Ultra Ball now needs 2 other cards in hand.
4. **Ultra Ball fodder.** Boss's Orders was the second most common discard (102 of 334 plays in a 900-game sample). G now discards a spare Basic Energy first; Energy Retrieval returns 2. Boss discards fell to 26.
5. **Ultra Ball order.** Holding Ultra Ball for a hole made the base list worse on the fresh seeds: T60 27.0% vs 28.1%, Hedrick 38.7% vs 40.0%, D60 5.2% vs 5.7%, C60 mirror 28.8% vs 30.7%. That run is `set-g-pad-ultra-review-ultrahole.json`. Ultra Ball is back on the fixed search order. Poké Pad still waits for a hole.
6. **Slot controls.** Each card is measured against the same cut paid with a Psychic Energy, so the card and its cut are separated.

## Head-to-head (G win rate, 6,000 games per cell)

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **base** | energy lock | 27.3% | 40.1% | 52.8% | 5.5% | 30.2% | 81.4% | 97.2% | 21.6% | 30.9% |
| pad | Ledyba → Poké Pad | 28.5% | 39.7% | 52.8% | 5.2% | 29.6% | 81.8% | 97.3% | 21.8% | 30.9% |
| ledyba_energy | Ledyba → Psychic | 28.5% | 40.6% | 53.1% | 6.2% | 31.0% | 82.2% | 96.9% | 22.4% | 31.6% |
| ultra | Ledian → Ultra Ball | 24.5% | 37.2% | 50.1% | 4.9% | 28.9% | 80.6% | 96.6% | 19.7% | 29.1% |
| ledian_energy | Ledian → Psychic | 28.6% | 40.1% | 52.2% | 5.5% | 30.0% | 82.2% | 96.9% | 22.0% | 31.1% |
| prank | Munkidori → Clefable | 27.5% | 38.5% | 53.3% | 4.8% | 29.8% | 80.3% | 96.2% | 20.9% | 30.4% |
| munk_energy | Munkidori → Psychic | 29.8% | 40.9% | 53.4% | 4.4% | 32.0% | 82.0% | 96.4% | 22.2% | 31.7% |
| **full** | Pad + Ultra + Prankish | 26.6% | 37.6% | 52.9% | 3.9% | 29.1% | 82.2% | 95.8% | 20.0% | 29.8% |
| thin_energy | the three cuts → Psychic | 29.5% | 41.6% | 55.9% | 4.9% | 32.9% | 83.7% | 95.9% | 22.5% | 32.4% |

## Contrasts (wComp, ± 1 SE)

| Contrast | Δ wComp | z |
| --- | ---: | ---: |
| pad − base | +0.17 ± 0.39 | +0.4 |
| pad − ledyba_energy | −0.67 ± 0.40 | −1.7 |
| ultra − base | −1.88 ± 0.39 | −4.9 |
| ultra − ledian_energy | −2.33 ± 0.39 | −6.0 |
| prank − base | −0.64 ± 0.39 | −1.7 |
| prank − munk_energy | −1.20 ± 0.39 | −3.1 |
| full − base | −1.56 ± 0.38 | −4.1 |
| thin_energy − base | +0.86 ± 0.39 | +2.2 |

**Poké Pad** ties the Ledyba it replaces. Across all six Pad matrices (four on seed `20260923` under different search orders, the ultra-hole review, and this one) Pad − base is +0.73, +0.32, +1.25, +0.31, +0.77, +0.17. It is never below the base. Pad resolves in about 1,900–2,100 of 6,000 games.

**The second Ultra Ball** is the loss in the package. Every matrix has it under the base, with or without the hold, with or without the legality and fodder fixes. The printed discard of 2 is paid every time it resolves (about 3,200–3,650 of 6,000 games with two copies, against about 2,000–2,350 with one).

**Prankish** bounces (about 530–760 of 6,000 games) and still leans negative against the base and clearly under a Psychic in the same slot. Moon-Watching Party attaches "for each of your Benched Clefairy". Evolving a bench Clefairy into Clefable removes one of those targets for the rest of the game.

**Energy.** Every single-Pokémon-to-Psychic control is at or above the base (+0.84, +0.44, +0.56), and `thin_energy` is +0.86. This is the fifth matrix where the three-Psychic row beats the base.

## Lock

`SET_G_NAMES` is unchanged (energy lock). Pad for Ledyba is a tie and may be sleeved for the C60 transition. The second Ultra Ball stays out. Prankish stays out until the Photon line exists.
