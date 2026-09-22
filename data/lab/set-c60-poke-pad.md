# C60 1 Prankish Clefable → Poké Pad (trial)

Date: 2026-09-22
Seed: `20260922`
Rule: s60
Games: 3,000 / cell (C60 variant is always A; who goes first is random)
Script: `data/lab/set_c60_poke_pad.py`
Raw: `data/lab/set-c60-poke-pad.json`
Elapsed: 129s

**Poké Pad** (ME02.5 198): *Search your deck for a Pokémon that doesn't have a Rule Box.* In this list that is Clefairy or Rebel Clash Prankish Clefable — never Clefable ex, Mega, or Mewtwo. Party treats the Item as that superposition: fetch the Party engine when short, or the Prankish evo once a Clefairy is already in play. Phantom still hunts Dreepy / Drakloak / Budew.

Swap: **1 of 2 Prankish Clefable → 1 Poké Pad**. Locked C60 stays 2 Clefable / 0 Pad. Family Cup Set C stays 30 with 0 Pad.

`wComp` weights T60, Hedrick, and D60 by how often the 2-Clefable list loses that matchup. `wAll` does the same over all six foes.

## Head-to-head

| Foe | AI | **clefable2** | **pad** | Pad hits | Clefable / Clefairy | Prankish (2 / 1) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| T60 (Candy Dragapult) | phantom | 67.7% | **68.0%** | 1068 | 919 / 149 | 634 / 555 |
| Hedrick Dragapult | phantom | 64.2% | **65.0%** | 1081 | 900 / 181 | 466 / 405 |
| UNL Pidgeot / Rotom | phantom | **90.3%** | 89.8% | 1263 | 1072 / 191 | 592 / 466 |
| D60 Charm Ogerpon | demolish | 76.1% | **77.6%** | 943 | 811 / 132 | 491 / 440 |
| S60 Floragato | slash | 99.5% | **99.7%** | 1418 | 1235 / 183 | 0 / 0 |
| G Nest/Zone | g | 71.5% | **72.2%** | 1361 | 1137 / 224 | 0 / 0 |
| **平均胜率** | — | 78.2% | **78.7%** | — | — | — |
| **加权胜率** | — | 70.9% | **71.6%** | — | — | — |
| **竞争加权** | — | 68.5% | **69.3%** | — | — | — |

Going first / second:

| Foe | clefable2 1st / 2nd | pad 1st / 2nd |
| --- | ---: | ---: |
| T60 | 69.9% / 65.4% | **70.1% / 66.1%** |
| Hedrick | **67.9%** / 60.5% | 65.4% / **64.5%** |
| D60 | 79.7% / 72.4% | **80.2% / 75.0%** |

## Read

The Item is doing the superposition job. Vs T60 it resolves in **36%** of games; **86%** of those hits are Prankish Clefable, **14%** Clefairy. Nest / Poffin still bench the engine. Pad is the Stage 1 tutor those Items cannot be.

Win rate: D60 **+1.5** (outside 3000-game noise of ~±0.9 on a 50% cell). Hedrick **+0.8**. T60 **+0.3** (noise). UNL **−0.5** (noise). Competitive weighted **68.5 → 69.3**. First and second move together on T60 and D60.

Hedrick going first is the spend: **67.9 → 65.4 (−2.5)**. Going second is **60.5 → 64.5 (+4.0)**. One fewer Clefable in the opening 60 hurts the scripted first-player bounce; Pad repairs after prizes and KOs, which is the second-player game. Prankish evolutions drop with the copy (T60 634 → 555) and the list still wins more games.

Do **not** lock this into `SET_C60_NAMES` yet. The weighted field likes Pad, but Hedrick going first is a real dip, and T60 is inside noise. This is the run. Family Cup Set C stays 30 with 0 Pad.
