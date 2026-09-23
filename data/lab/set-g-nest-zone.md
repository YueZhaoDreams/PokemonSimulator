# G: 4 Nest Ball, 3 Clefable ex, 1 Energy Switch, 2 Switch arrive

Date: 2026-09-21
Seed: `20260921`
Rule: s60
G-side always A; first player random
Script: `data/lab/set_g_nest_zone.py`
Raw: `data/lab/set-g-nest-zone.json`

Base is frozen Poffin-lock `SET_G_POFFIN_NAMES` (4 Poffin, 1 Mega, 0 Nest, 0 Clefable ex, 0 Switch, 1 Energy Switch).
Ten cards in, ten cards out. Strategy `g` evolves one Clefable ex onto a bench Clefairy once two Clefairy are out (Lunar Zone; the Active stays Party), Nest Ball fetches Munkidori / Flutter Mane after the first Clefairy, and Switch rotates only when a bench attacker should be Active.

## Headline

**−1 Starly −1 Staravia −1 Staraptor −Surfer −Kecleon −Boomerang Energy −Flutter Mane −Energy Search −Trekking Shoes −Tulip.**

Bird line stays 1-1-1. Ledian stays 4/4. Munkidori, 3 Darkness, 17 Psychic, Mega, Ultra Ball, Poffin, Boss, Drayton, Iris, Energy Retrieval stay. Energy Switch goes 1 → 2.

Confirm, 3,000 games. Win rates are G's:

| | t60 | Hedrick | D60 | UNL | C60 | S60 | H | 竞争加权 | 全场加权 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Poffin lock | 20.9 | 29.8 | **5.6** | 44.5 | 21.7 | 69.8 | 95.8 | 0.1754 | 0.2661 |
| **bird_thin** | **23.9** | **34.6** | 5.4 | **49.3** | **22.2** | **74.8** | **96.4** | **0.1982** | **0.2906** |
| Δ | +2.9 | +4.8 | −0.1 | +4.8 | +0.4 | +5.0 | +0.6 | +2.3pp | +2.5pp |

D60 is flat. The mirror (C60) is flat at 3,000 games (the 2,000-game pass had bird_thin behind, 21.3 vs 23.1). The gain is Hedrick, household Candy Dragapult, Unlimited Dragapult, and the Grass hunter.

## Why these ten

Nest Ball does the job Poffin cannot (Munkidori 110 / Flutter Mane 90) and Switch replaces Surfer without spending the supporter. The duplicate bird line was the Pokémon cut: one Staraptor closer stays, the second 1-1-1 was the bench clog. Flutter Mane, Kecleon, Boomerang, Energy Search, Trekking Shoes, and Tulip were the other flex slots. Keeping Flutter (`keep_flutter`) was one of the worst lists. Cutting 3 Psychic (`psychic3`) was the worst. Cutting Munkidori + 3 Darkness (`dark_out`) drops D60 to 2.0%.

Thinning Ledian to 2/2 (`ledian_thin`) is the only other list that beat the Poffin lock on both weights. It loses to `bird_thin` on every foe except D60 (6.5 vs 6.0 at 2,000 games). Gust stays a 4-of.

## Packages (2,000 games)

| List | t60 | Hedrick | D60 | UNL | C60 | S60 | H | 竞争加权 | 全场加权 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **bird_thin** | **24.1** | **33.7** | 6.0 | **48.4** | 21.3 | **74.6** | **96.2** | **0.1982** | **0.2889** |
| ledian_thin | 21.9 | 32.7 | **6.5** | 45.5 | 20.5 | 74.4 | 95.1 | 0.1900 | 0.2782 |
| baseline | 21.1 | 29.8 | 5.1 | 43.7 | **23.1** | 69.8 | 95.3 | 0.1738 | 0.2675 |
| dark_out | 20.8 | 27.7 | 2.0 | 48.1 | 20.8 | 69.7 | 92.5 | 0.1547 | 0.2578 |
| keep_draw | 21.6 | 27.9 | 5.4 | 44.8 | 17.6 | 68.8 | 94.2 | 0.1709 | 0.2563 |
| keep_search | 21.6 | 28.5 | 6.2 | 43.6 | 17.2 | 67.5 | 93.5 | 0.1759 | 0.2558 |
| flex_out | 20.5 | 28.7 | 6.0 | 44.4 | 16.0 | 66.2 | 93.2 | 0.1722 | 0.2514 |
| keep_flutter | 19.1 | 27.5 | 4.7 | 45.1 | 16.0 | 62.2 | 92.5 | 0.1592 | 0.2417 |
| psychic3 | 17.9 | 27.1 | 4.3 | 42.0 | 16.7 | 62.5 | 92.2 | 0.1529 | 0.2352 |

`flex_out` is the "cut every non-C60 one-of, keep both lines" list. It loses the back half (C60 16.0, S60 66.2) because the second bird line is still in the way and Flutter / the search items were not the expensive cards.

## Lock

Applied to `SET_G_NEST_ZONE_NAMES`. Live `SET_G_NAMES` later swapped 2 Psychic for 2 Telepathic (see [set-g-c60-telepathic.md](set-g-c60-telepathic.md)), then 2 Ledian, 1 Ledyba, and 1 Munkidori for 4 Psychic (see [set-g-four-psychic.md](set-g-four-psychic.md)). Poffin list stays `SET_G_POFFIN_NAMES`.

Still not C60: no Mewtwo ex, no Prankish Clefable, no second Mega, no Hop / Lillie / Iono / Arven / Belt / Battle Cage. Telepathic is in live G as a 2-of. Next arrivals are the draw core and the Photon line.
