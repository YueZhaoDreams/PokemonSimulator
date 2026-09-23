# This shipment on four-Psychic G

Date: 2026-09-23
Seeds: `20260926`, `20260927` (3,000 games each, 6,000 per cell)
Rule: s60
Script: `data/lab/set_g_four_psychic_arrival.py`
Raw: `data/lab/set-g-four-psychic-arrival.json`
Iris / Drayton energy controls: `data/lab/set-g-four-psychic-arrival-controls.json`
Elapsed: 1047s, plus the two controls

Base is live `SET_G_NAMES`: Psychic 19, Telepathic 2, Ledian 2, Ledyba 3, Munkidori 1. Strategy `g`. The cards that just arrived:

| Qty | Card | Printed text |
| ---: | --- | --- |
| 2 | Lillie (SM Ultra Prism) | Draw until you have 6. On your first turn, draw until you have 8. |
| 1 | Night Stretcher | Put a Pokémon or a Basic Energy from your discard pile into your hand. |
| 1 | Ultra Ball | Discard 2 cards. Search your deck for a Pokémon. G already has 1. |
| 2 | Poké Pad (ME03 081/088) | Search your deck for a Pokémon that doesn't have a Rule Box. |
| 2 | Clefable (Rebel Clash) | Prankish: on evolve, you may put an Energy from the opponent's Active on top of their deck. |

wComp weights T60, Hedrick, and D60 by how often this base loses. Difference SE on wComp is about 0.39 pp. A 30% cell's difference SE is about 0.84 pp.

## Head-to-head (G win rate)

| Variant | Swap | T60 | Hedrick | UNL | D60 | C60 | S60 | H | wComp | wAll |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **base** | four Psychic | 29.0% | 41.8% | 55.3% | 4.9% | 33.7% | 83.3% | 96.4% | 22.1% | 32.1% |
| lillie_iris | Iris → Lillie | 30.9% | 42.3% | 55.5% | 5.4% | 32.9% | 83.0% | 96.7% | 23.1% | 32.5% |
| iris_energy | Iris → Psychic | 30.4% | 40.5% | 56.0% | 5.2% | 32.2% | 81.4% | 95.4% | 22.3% | 31.9% |
| lillie_drayton | Drayton → Lillie | 30.3% | 42.0% | 56.6% | 4.8% | 32.9% | 82.5% | 95.9% | 22.5% | 32.3% |
| drayton_energy | Drayton → Psychic | 30.6% | 41.2% | 54.6% | 5.0% | 31.8% | 82.2% | 96.1% | 22.5% | 31.8% |
| lillie2 | Iris + Drayton → 2 Lillie | 31.4% | 42.6% | 55.5% | 5.4% | 33.4% | 82.4% | 96.2% | 23.3% | 32.7% |
| stretcher | Retrieval → Night Stretcher | 29.8% | 42.4% | 55.4% | 4.8% | 32.9% | 82.9% | 96.1% | 22.5% | 32.1% |
| pad | Ledyba → Poké Pad | 31.3% | 42.4% | 58.1% | 5.8% | 33.9% | 83.6% | 96.3% | 23.4% | 33.2% |
| ledyba_energy | Ledyba → Psychic | 32.2% | 43.7% | 57.9% | 5.6% | 34.9% | 84.5% | 96.0% | **23.9%** | **33.8%** |
| ultra | Ledian → Ultra Ball | 29.0% | 40.6% | 52.6% | 5.2% | 31.5% | 83.4% | 95.4% | 21.9% | 31.2% |
| ledian_energy | Ledian → Psychic | 30.1% | 42.0% | 55.3% | 4.7% | 33.3% | 84.3% | 96.2% | 22.4% | 32.2% |
| prank | Munkidori → Clefable | 29.2% | 39.6% | 55.8% | 1.5% | 34.8% | 82.0% | 94.8% | 20.1% | 31.0% |
| munk_energy | Munkidori → Psychic | 31.7% | 42.2% | 58.5% | 1.6% | 34.9% | 79.8% | 94.8% | 21.7% | 32.2% |
| slice | C60's count of this box | 26.9% | 37.9% | 52.4% | 4.4% | 29.1% | 84.6% | 95.4% | 20.2% | 29.7% |

## Contrasts (wComp)

| Contrast | Δ wComp | z |
| --- | ---: | ---: |
| lillie_iris − base | +0.94 | +2.4 |
| lillie_iris − iris_energy | +0.72 | +1.8 |
| lillie2 − lillie_iris | +0.24 | +0.6 |
| lillie_drayton − drayton_energy | +0.01 | +0.0 |
| stretcher − base | +0.34 | +0.9 |
| pad − ledyba_energy | −0.57 | −1.4 |
| ledyba_energy − base | +1.79 | +4.5 |
| ultra − ledian_energy | −0.50 | −1.3 |
| prank − base | −2.00 | −5.3 |
| prank − munk_energy | −1.54 | −4.2 |
| slice − base | −1.91 | −5.0 |

## What to sleeve

**One Lillie, paid by Iris's Fighting Spirit.** Iris discards another card, then draws until 6. Lillie draws until 6 with no discard, and until 8 on the first turn. The same cut paid with a Psychic Energy is only +0.21 wComp. Lillie's edge over that energy is Hedrick +1.8 (z +2.0) and S60 +1.6 (z +2.3). Both seeds have Lillie above the base on T60 (30.7 / 31.2 against 29.1 / 29.0).

**The second Lillie stays out.** Adding it by cutting Drayton is +0.24 wComp over the one-Lillie list (z +0.6). Drayton → Lillie ties Drayton → Psychic. Drayton looks at the top 7 and may take a Pokémon and a Trainer. Keep it.

**Night Stretcher stays out.** Energy Retrieval puts up to 2 Basic Energy into hand. Stretcher puts 1 Pokémon or 1 Energy. +0.34 wComp is inside noise. G has no Mewtwo for the stretcher to pick up.

**Both Poké Pads stay out.** Ledyba → Pad is +1.22 wComp over the base, and Pad resolves in about 1,850–2,500 of 6,000 games. Ledyba → Psychic in that same slot is +1.79 (z +4.5) and beats the Pad on T60, Hedrick, and the C60 mirror. The bump is the cut, not the Pad.

**The new Ultra Ball stays out.** The second copy loses UNL 55.3 → 52.6 and the C60 mirror 33.7 → 31.5. Printed cost is discard 2, paid on every resolution. G already has 1 Ultra Ball, 4 Nest Ball, and 4 Buddy-Buddy Poffin.

**Both Prankish Clefable stay out.** Evolving a benched Clefairy removes a Moon-Watching Party target. The bounce fires (about 500 games vs T60, about 1,400 vs D60) and D60 falls 4.9 → 1.5. Cutting the last Munkidori for a Psychic also drops D60 to 1.6, and Prankish is still 1.5 pp of wComp under that energy.

**The destination count of this box loses.** 2 Lillie, 1 Stretcher, a second Ultra Ball, 1 Pad, 1 Prankish is wComp 20.2% and T60 26.9%. That is not the next 60.

`SET_G_NAMES` is unchanged. The one Lillie swap is the only card from this box that beats both the card it replaces and a Psychic in that slot.
