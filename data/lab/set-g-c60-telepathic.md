# G → C60: 4 Telepathic arriving, sleeve 2

Date: 2026-09-22
Seed: `20260922`
Rule: s60
Games: 3,000 / cell (trial list always A; first player random)
Script: `data/lab/set_g_c60_telepathic.py`
Raw: `data/lab/set-g-c60-telepathic.json`

Four **Telepathic Psychic Energy** (POR 88 / ME03 88) are arriving while G is rebuilt toward C60. Locked C60 is already **14 Psychic + 2 Telepathic**; 3 and 4 are legal. Swap is **N Telepathic for N Psychic Energy**. Family Cup Set C stays 30 with 0 Telepathic.

Printed: attach from hand to a Psychic Pokémon, then search up to 2 Basic Psychic onto the Bench. Party cannot search it from the deck. Energy Switch cannot move it. `g` now attaches it before Party the same way `party` does, or the new engines miss this turn's search.

Base G is frozen Nest/Zone `SET_G_NEST_ZONE_NAMES` (17 Psychic, 0 Telepathic). Destination C60 is current Battle Cage `SET_C60_NAMES` (the Sep 14 energy-count lab was pre-Cage).

## Headline

**Sleeve 2. Keep C60 at 2. Do not play 3 or 4.**

The jump is 0 → 2 on G. Copies 3 and 4 do not pay the competitive field (t60 / Hedrick / D60). C60's extra copies still dump Hedrick and T60 going second.

On G vs t60, Party games go 1802 → 2212 once Telepathic is in, and the attach search fires in 1409 / 3000 games. That is the engine the 4 cards are for. Two copies already find the attach.

## Destination C60 (party)

Weights fixed from locked tele2 C60 loss rate. Competitive = t60 + Hedrick + D60.

| Foe | AI | tele0 | **tele2** | tele3 | tele4 |
| --- | --- | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | 66.8% | 67.2% | 67.7% | **67.9%** |
| Hedrick Dragapult | phantom | 64.2% | **64.7%** | 64.1% | 62.8% |
| UNL Pidgeot / Rotom | phantom | 89.9% | 89.7% | **90.4%** | 90.4% |
| D60 Charm Ogerpon | demolish | 74.6% | 76.1% | 77.2% | **77.5%** |
| S60 Floragato | slash | 99.2% | 99.5% | **99.7%** | 99.6% |
| G Nest/Zone | g | 77.7% | **79.2%** | 77.0% | 78.0% |
| H TR Zapdos | nuzzle | 96.7% | 96.8% | 96.1% | **97.1%** |
| **平均胜率** | — | 81.3% | 81.9% | 81.7% | **81.9%** |
| **加权胜率** | — | 72.1% | **72.8%** | 72.7% | 72.6% |
| **竞争加权** | — | 67.8% | 68.5% | **68.8%** | 68.5% |

T60 going second: tele2 **66.9%**, tele3 66.4%, tele4 **65.0%**. Hedrick: tele2 **64.7%**, tele4 **62.8%** (−1.9, outside 3000-game noise). D60 likes extra specials (+1.4 at tele4) the same way the pre-Cage lab did. Competitive tele3 over tele2 is 0.24pp — noise. Keep **2**.

Battle Cage moved the Candy matchup from a coin flip into the high 60s. The ranking did not change: 2 still wins the weighted field; 4 still spends Hedrick / T60 second for Ogerpon and T60 first.

## Live G Nest/Zone (`g`)

Weights fixed from tele0 G loss rate.

| Foe | AI | **tele0** | **tele2** | tele3 | tele4 |
| --- | --- | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | 24.3% | 29.1% | **29.7%** | 29.3% |
| Hedrick Dragapult | phantom | 34.2% | **40.3%** | 39.6% | 39.7% |
| UNL Pidgeot / Rotom | phantom | 47.6% | 52.9% | 54.2% | **54.8%** |
| D60 Charm Ogerpon | demolish | 5.9% | 6.1% | **6.4%** | 5.7% |
| C60 (locked 2 Telepathic) | party | 22.4% | 27.5% | 29.1% | **32.7%** |
| S60 Floragato | slash | 76.4% | 80.6% | 81.4% | **82.6%** |
| H TR Zapdos | nuzzle | 96.6% | 97.0% | 97.2% | **97.9%** |
| **平均胜率** | — | 43.9% | 47.6% | 48.2% | **49.0%** |
| **加权胜率** | — | 28.1% | 32.0% | 32.6% | **33.3%** |
| **竞争加权** | — | 19.7% | 23.0% | **23.2%** | 22.8% |

0 → 2 is the real swap: T60 **+4.7**, Hedrick **+6.1**, UNL **+5.3**, C60 **+5.1**, S60 **+4.2**. D60 is flat.

Copies 3 and 4 buy the C60 mirror and S60. They do not buy Dragapult: Hedrick peaks at tele2, D60 is worst at tele4 (5.7%), competitive tele3 vs tele2 is 0.13pp. All-field tele4 is the same trap as Lillie's Clefairy ex / the Belt cut — a back-half bump that spends Charm.

Vs t60, Telepathic attach games: tele2 1409, tele3 1719, tele4 2062. Extra copies attach more often; Wonder Storm does not convert the extras into prizes against Dive.

## Lock

**G at this bakeoff: −2 Psychic Energy, +2 Telepathic Psychic Energy.** Energy line in the historical tele2 list is **15 Psychic + 2 Telepathic**. Nest/Zone list stays `SET_G_NEST_ZONE_NAMES`. Live `SET_G_NAMES` later replaced 2 Ledian, 1 Ledyba, and 1 Munkidori with 4 Psychic Energy (see [set-g-four-psychic.md](set-g-four-psychic.md)).

**C60 stays 14 Psychic + 2 Telepathic.** Do not go to 3 or 4 on the destination list either.

Of the 4 cards arriving, sleeve **2**. The other 2 stay unsleeved (extras / spare) until a later C60 piece actually wants them. Do not cut trainers for copies 3 and 4.

Still not C60: no Mewtwo ex, no Prankish Clefable, no second Mega, no Hop / Lillie / Iono / Arven / Belt / Battle Cage. Next arrivals are the draw core and the Photon line.

3000-game noise on a 50% cell is about ±0.9 points. G's 0→2 gaps are outside that. C60's tele2 vs tele4 Hedrick gap is outside that. Blowouts (S60 / H) do not move the lock.
