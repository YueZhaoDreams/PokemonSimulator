# C60 Pad + Metronome: cut something other than Hop

Date: 2026-09-22
Seed: `20260922`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (C60 always player A; who goes first is random)
Script: `data/lab/set_c60_pad_clc_cuts.py`
Raw: `data/lab/set-c60-pad-clc-cuts.json`
Elapsed: 1088s

The previous combined list paid for CLC 014 with a Hop and lost ([set-c60-pad-metronome.md](set-c60-pad-metronome.md)). Hop looked more valuable than the 70 HP copy body. This matrix keeps **1 Rebel Clash Prankish + 1 Poké Pad** and slots **Clefable CLC** by cutting Clefable ex, a Psychic Energy, or another trainer / Stage 1 — with the Hop cut as the known floor.

Construction: `pad_list()` (lock −1 Prankish + Pad), then `remove(X)` + `Clefable CLC`. Printed Pad text is unchanged (Pokémon without a Rule Box). Do not lock.

Foes: T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `g`.

`wComp` weights T60, Hedrick, and D60 by how often the 2-Prankish list loses that matchup.

Binomial SE on a 68% cell at 3,000 games is about **0.8 pp**. Treat ±0.5 as noise.

## Head-to-head (C60 win rate)

| Variant | Cut for CLC | T60 | Hedrick | UNL | D60 | S60 | G | wComp |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **pad** | *(no CLC)* | 68.0% | 65.0% | 89.8% | 77.6% | **99.7%** | 72.2% | 69.3% |
| mega | Mega Clefable ex | 66.9% | **66.5%** | 89.5% | **78.0%** | **99.7%** | 71.7% | **69.6%** |
| ultra | Ultra Ball | **68.5%** | 64.5% | **90.3%** | 77.6% | 99.6% | **74.3%** | 69.3% |
| **prankish2 (lock)** | — | 67.7% | 64.2% | **90.3%** | 76.1% | 99.5% | 71.5% | 68.5% |
| nest | Nest Ball | 67.1% | 64.6% | 89.9% | 76.0% | 99.6% | **74.3%** | 68.4% |
| switch | Switch | 67.1% | 63.1% | 88.7% | 75.9% | 99.4% | 72.3% | 67.8% |
| stretcher | Night Stretcher | 67.1% | 62.3% | 89.3% | 75.9% | 99.7% | 72.6% | 67.6% |
| ex | Clefable ex | 65.0% | 62.9% | 87.9% | 77.0% | 99.5% | 73.4% | 67.3% |
| poffin | Buddy-Buddy Poffin | 65.8% | 63.6% | 89.1% | 74.7% | 99.5% | 72.1% | 67.3% |
| iono | Iono | 65.8% | 63.2% | 88.9% | 75.2% | 99.4% | 74.5% | 67.2% |
| eswitch | Energy Switch | 64.9% | 62.7% | 89.1% | 76.6% | 99.6% | 72.4% | 67.1% |
| energy | Psychic Energy | 65.0% | 63.4% | 87.9% | 75.3% | 99.5% | 70.0% | 67.1% |
| cage | Battle Cage | 64.1% | 62.6% | 88.1% | 76.6% | 99.7% | 73.7% | 66.8% |
| hop | Hop | 64.3% | 62.8% | 88.4% | 74.2% | 99.5% | 70.3% | 66.3% |
| arven | Arven | 66.3% | 64.0% | 88.5% | 68.6% | 99.6% | 71.2% | 66.0% |
| tele | Telepathic Psychic Energy | 63.9% | 61.8% | 88.2% | 73.5% | 99.7% | 70.8% | 65.6% |
| lillie | Lillie | 64.4% | 60.5% | 88.0% | 74.2% | 99.7% | 71.9% | 65.4% |
| det | Lillie's Determination | 63.2% | 60.6% | 88.1% | 73.7% | **99.9%** | 70.6% | 64.9% |

Going first / second vs T60: pad 70.1 / 66.1, mega 69.2 / 64.6, ultra 68.9 / 68.0, lock 69.9 / 65.4, ex 68.4 / 61.7, energy 65.4 / 64.6, hop 66.6 / 61.9.

The hop row is the same 60 as the earlier `pad_clc` list (Counter equality). Cell percents differ by a point because card order changed (CLC appended vs Pad appended) and the shuffle is order-sensitive. Both are well below pad-only.

## Named cuts: Hop, Clefable ex, energy

Vs pad-only (no CLC), paying for Metronome with those three:

| Cut | T60 | Hedrick | D60 | wComp vs pad |
| --- | ---: | ---: | ---: | ---: |
| Hop | −3.7 | −2.1 | −3.3 | **−3.0** |
| Clefable ex | −3.0 | −2.0 | −0.5 | **−2.0** |
| Psychic Energy | −3.1 | −1.5 | −2.3 | **−2.3** |

Hop is still the expensive slot. Clefable ex and a 14th Psychic are also more valuable than CLC. Draw (Lillie / Determination / Telepathic) is worse than Hop.

## The copy line still fires

Vs T60, games (out of 3,000) where Pad fetched Metronome and Metronome copied Phantom Dive:

| Variant | Pad hit | Pad → Metro | copy Dive |
| --- | ---: | ---: | ---: |
| pad | 1068 | 0 | 0 |
| hop | 1286 | 843 | 734 |
| ex | 1303 | 819 | 749 |
| energy | 1272 | 776 | 717 |
| ultra | 1302 | 844 | **782** |
| mega | 1317 | 820 | 747 |

Vs D60 the Pad still prefers Prankish (800–860 Pad→Prankish vs ~130–170 Pad→Metro) and copy Dive is 0. The 3-way hunt is matchup-correct on every cut. The problem is still the **70 HP Active after a 200-into-320 Dive**.

## Two cuts that do not clearly lose

**Ultra Ball.** Pad already tutors a non-Rule-Box Pokémon, so the second ball is the most redundant Item. T60 68.5 is the best Dragapult cell in the matrix (lock 67.7, pad 68.0). Hedrick −0.5 vs pad. wComp ties pad at 69.3. Within noise of pad-only; not a lock.

**Mega Clefable ex.** Highest wComp (69.6) because Hedrick +1.6 and D60 +0.4 vs pad. T60 **drops** 68.0 → 66.9 (below the lock). Mega is the 320 HP / 3-prize sponge: cutting it helps when the opponent is taking that third prize, and hurts when Dive needs a body that is not a 70 HP Clefable. Do not lock a T60 regression for a Hedrick bump inside one SE.

Every other cut, including Clefable ex and energy, is below both pad-only and the 2-Prankish lock on wComp.

## Lock

Designer lock after this matrix: **1 Rebel Clash Prankish + 1 CLC 014 + 1 Poké Pad**, paid by cutting the second Mega. `SET_C60_NAMES` is that 60. Hop / Clefable ex / energy still lose; this is the Mega row (wComp 69.6). Cage-lock 2 Prankish / 2 Mega is frozen as `C60_CAGE_LOCK_NAMES` for historical bakeoffs.
