# C60 1 Prankish + Metronome + Poké Pad

Date: 2026-09-22
Seed: `20260922`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (C60 always player A; who goes first is random)
Script: `data/lab/set_c60_pad_metronome.py`
Raw: `data/lab/set-c60-pad-metronome.json`
Elapsed: 250s

The 2-of Clefable slot is not a 1-for-1 Metronome swap. **One Prankish stays.** CLC 014 Metronome (`[C]`, 70 HP) is the other Clefable print. Poké Pad (ME02.5 198) searches a Pokémon without a Rule Box, so with both prints in the deck it is a **3-way superposition**: Clefairy, Prankish, or Metronome — never Clefable ex / Mega / Mewtwo. Pad takes a Hop so the list stays 60.

Printed Metronome: choose 1 of the opponent's Active attacks (we pick). Mime Jr. Mimed Games is their choice.

Foes: T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `g`.

`wComp` weights T60, Hedrick, and D60 by how often the 2-Prankish list loses that matchup.

## Head-to-head (C60 win rate)

| Variant | List | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **prankish2 (lock)** | 2 Prankish | 67.7% | 64.2% | **90.3%** | 76.1% | 99.5% | 71.5% | 68.5% |
| clc1 | 1 Prankish + 1 CLC | 65.8% | 63.0% | 89.2% | 76.3% | **99.7%** | **73.2%** | 67.5% |
| **pad** | 1 Prankish + 1 Pad | **68.0%** | **65.0%** | 89.8% | **77.6%** | **99.7%** | **72.2%** | **69.3%** |
| pad_clc | 1 Prankish + 1 CLC + 1 Pad −1 Hop | 63.9% | 61.6% | 87.6% | 75.7% | 99.3% | 70.4% | 66.1% |

Going first / second vs T60: lock 69.9 / 65.4, CLC 66.7 / 64.9, Pad 70.1 / 66.1, Pad+CLC 64.7 / 63.2. Vs Hedrick: lock 67.9 / 60.5, CLC 63.1 / 62.9, Pad 65.4 / 64.5, Pad+CLC 62.3 / 60.9. Vs D60: lock 79.7 / 72.4, CLC 79.6 / 73.1, Pad 80.2 / 75.0, Pad+CLC 79.4 / 72.1.

## The 3-way Pad does fetch the right print

Vs T60, games (out of 3,000) where C60's Pad hit / fetched Metronome / fetched Prankish / copied Dive:

| Variant | Pad hit | Pad → Metro | Pad → Prankish | copy Dive | Prankish bounce |
| --- | ---: | ---: | ---: | ---: | ---: |
| prankish2 | 0 | 0 | 0 | 0 | 634 |
| clc1 | 0 | 0 | 0 | 672 | 287 |
| pad | 1068 | 0 | 919 | 0 | 555 |
| pad_clc | 1267 | **812** | 375 | 699 | 314 |

Vs D60, Pad+CLC still prefers Prankish (845 Pad→Prankish vs 133 Pad→Metro) and bounces 423 times. The hunt is matchup-correct.

The combined list still loses. Pad fetches CLC, party Bosses Dragapult, Metronome copies Dive 200 into 320 HP — then C60 is Active on **70 HP**. Cutting Hop to pay for Pad makes that worse than CLC-only (T60 65.8 → 63.9). Pad-only (no Metronome, Pad instead of the second Clefable) is the only row above the lock, same shape as [set-c60-poke-pad.md](set-c60-poke-pad.md).

## Lock

`SET_C60_NAMES` stays **2 Rebel Clash Prankish**, 0 Pad, 0 Metronome. Do not add CLC just because Pad can tutor it. Pad-alone is a separate 1-for-1 that is slightly ahead and is not locked from this run either.
