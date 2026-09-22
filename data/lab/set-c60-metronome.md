# C60 1-of Metronome Clefable

Date: 2026-09-22
Seed: `20260922`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_metronome.py`
Raw: `data/lab/set-c60-metronome.json`
Elapsed: 200s

Printed Metronome (CLC 014 and TWM 079): **Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack.** We pick the copy (KO prizes + Active damage + bench counters). Mime Jr. Mimed Games is the opponent's choice (min). Same printed name as Rebel Clash Prankish, so this is the 2-of Clefable slot, not a fifth copy.

The locked list keeps 2 Prankish. This trial swaps the second copy for CLC (`[C]`, Colorless, 70 HP) or TWM (`[CC]`, Psychic, 120 HP) and teaches party to Boss Dragapult Active, evolve, then copy Phantom Dive.

Foes: T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `g`.

`wComp` weights T60, Hedrick, and D60 by how often the 2-Prankish list loses that matchup.

## Head-to-head (C60 win rate)

| Variant | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **prankish2 (lock)** | **67.2%** | **64.7%** | **90.3%** | 76.1% | 99.5% | 71.5% | **68.5%** |
| clc1 | 65.5% | 64.2% | 89.2% | **76.3%** | **99.7%** | **73.2%** | 67.8% |
| twm1 | 66.0% | 63.2% | 88.2% | 76.2% | 99.5% | 71.3% | 67.6% |

Going first / second vs T60: lock 67.4 / 66.9, CLC 66.0 / 65.0, TWM 65.9 / 66.1. Vs Hedrick: lock 66.5 / 62.9, CLC 65.5 / 62.8, TWM 63.2 / 63.3. Vs D60: lock 79.7 / 72.4, CLC 79.6 / 73.1, TWM 80.1 / 71.9.

## The copy line does fire

Vs T60, games (out of 3,000) where C60 copied Phantom Dive / evolved Metronome / played Boss / bounced Prankish:

| Variant | copy Dive | Metronome evolve | Boss (A) | Prankish |
| --- | ---: | ---: | ---: | ---: |
| prankish2 | 0 | 0 | 201 | 656 |
| clc1 | **649** | 1052 | 496 | 307 |
| twm1 | 457 | 830 | 424 | 337 |

CLC is `[C]` so it evolves more often than TWM `[CC]`. Hedrick copies Dive in 486 (CLC) / 376 (TWM) games. Vs D60 the mix almost never copies (3 / 2 games) and still bounces Fighting ~280–300 times; Boss stays held for the close. That is the 1 Prankish we kept.

The loss vs Dragapult is the body, not the AI. Dive is 200 into 320 HP Dragapult ex (not a KO) plus 6 bench counters. After the copy, C60 is Active on 70 HP (CLC) or 120 HP (TWM). The opponent Dives back. Prankish is 110 HP and does not spend Boss or the Active slot on that chip.

Historical 2 CLC vs 2 Prankish (seed `20260911`, pre-Cage, no gust): T60 52.3 vs 53.6, Hedrick 60.6 vs 65.9. This run's 1-of with gust-and-copy still sits behind 2 Prankish on T60 / Hedrick / wComp.

## Lock

`SET_C60_NAMES` stays **2 Rebel Clash Prankish**. Do not put CLC or TWM in the 2-of slot unless a later plan can copy Dive without leaving a 70/120 HP Active into the next Dive.
