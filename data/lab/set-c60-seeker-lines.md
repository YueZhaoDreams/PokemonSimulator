# C60: one Seeker, from Iono or from one Clefable ex

Date: 2026-09-26
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_seeker_lines.py`
Raw: `data/lab/set-c60-seeker-lines.json`
Elapsed: 222s

The live lock is `SET_C60_NAMES` (1 Prankish, 1 Metronome Clefable, 1 Poké Pad, 1 Mega, 3 Clefable ex, 1 Iono). `iono-seeker` replaces Iono and keeps 3 Clefable ex. `ex-seeker` keeps Iono and drops Clefable ex from 3 to 2. Every other card stays.

Party now plays Seeker for five lines, from the printed sentence (each player returns one Benched Pokémon and everything attached to it; you return yours first; a player with no Bench returns nothing):

1. A damaged benched ex that the opponent can knock out, including by Boss's Orders, goes back to hand and stays there. The body is full HP and is not a gust target.
2. The Bench is full, Prankish is sitting on the only Clefairy, and Clefable ex or Mega Clefable ex is in hand. Seeker returns that stack and replays the Clefairy.
3. Two Clefairies can evolve. Seeker is Bench-only, so the first evolution is a Benched Clefairy. Prankish puts one Energy from the opponent's Active on top of their deck, Seeker returns that Clefable, and the same Prankish evolves the other Clefairy.
4. The opponent has exactly one Benched Pokémon and the Active attack still knocks out after both returns. That is the win on an empty board.
5. Mega Clefable ex is Active, Shooting Moons can be paid, and Energy attached to a Benched Pokémon is what turns the attack into a knockout. Seeker puts that Energy into hand, then the attack discards it.

The opponent chooses their own Bench Pokémon. One Bench Pokémon is forced. Otherwise they save a damaged Pokémon we could knock out, or they return their least valuable one.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes.

## Win rate

| Variant | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **lock** | 68.3% | 63.5% | 89.8% | 76.8% | **99.9%** | 65.8% | 68.5% | 69.5% |
| iono-seeker | **68.8%** | **65.5%** | 89.5% | 74.6% | 99.6% | **69.0%** | **68.9%** | **70.5%** |
| ex-seeker | 67.4% | 62.8% | **89.9%** | **78.6%** | 99.6% | 65.9% | 68.4% | 69.4% |

Going first / second for ex-seeker: T60 68.9/65.8, Hedrick 63.8/61.9, D60 81.9/75.2, G 65.4/66.4. The lock on those four is 69.5/67.2, 65.6/61.4, 79.1/74.4, 68.0/63.7.

## One Clefable ex for Seeker

wComp is 68.4% against the lock's 68.5%. D60 is +1.8 (78.6% against 76.8%). T60 is −1.0 and Hedrick is −0.7. G is flat (65.9% against 65.8%). Keeping Iono gives the D60 row back the 2 points the Iono cut lost, and gives up the Hedrick and G gains from that cut.

Seeker still fires. Out of 3,000:

| Foe | Seeker played | Save ex | Double Prankish | One-bench KO | Reline | Moons fuel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T60 | 489 | 270 | 67 | 163 | 0 | 0 |
| Hedrick | 407 | 224 | 81 | 102 | 4 | 0 |
| UNL | 312 | 125 | 86 | 96 | 7 | 0 |
| D60 | 287 | 287 | 0 | 0 | 0 | 0 |
| S60 | 658 | 1 | 186 | 470 | 0 | 2 |
| G | 696 | 107 | 395 | 198 | 0 | 0 |

On D60 every Seeker is still the ex save (287 games). With Iono still in the list, that line sits on top of the shuffle instead of replacing it, and the matchup goes up. Two Clefable ex is enough Lunar Zone for the Demolish wall. The third copy was the card the phantom matchups were using: T60 and Hedrick both drop about a point.

## How often each line fires (Iono → Seeker)

Counts are games with at least one success, out of 3,000.

| Foe | Seeker played | Save ex | Double Prankish | One-bench KO | Reline | Moons fuel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| T60 | 517 | 263 | 75 | 182 | 4 | 1 |
| Hedrick | 366 | 205 | 67 | 98 | 2 | 0 |
| UNL | 345 | 127 | 80 | 128 | 12 | 0 |
| D60 | 293 | 293 | 0 | 0 | 0 | 0 |
| S60 | 667 | 3 | 169 | 493 | 0 | 6 |
| G | 696 | 89 | 369 | 246 | 0 | 1 |

Hedrick (+2.0) and G (+3.2) are the matchups that move. On G, double Prankish happens in 369 games and the one-bench KO in 246. On Hedrick the save and the one-bench KO are the common lines. T60 is +0.4, inside a 3,000-game wobble. S60 and UNL stay on the ceiling.

D60 is −2.2. Every Seeker there is the save (293 games, nothing else). Ogerpon's threat is Demolish from the Active, not Boss's Orders. Picking the ex up denies the prize and also takes the wall off the board. Iono's shuffle was worth more in that matchup.

Reline is 18 games across all six foes. A full Bench whose only Clefairy is underneath Prankish, with ex or Mega already in hand, almost never comes up: the list plays four Clefairy, and an open Bench spot is the usual way onto ex or Mega.

Shooting Moons fuel is 8 games. On G the Mega attacks with Shooting Moons in 746 games, and Seeker is in hand on a turn Mega can pay in 84. In 79 of those the hand already knocks out. In 10 the Energy on the Bench still does not reach. The printed bonus is Energy cards from hand, so a Benched Pokémon helps only when it has Energy attached. This one Seeker is usually already used, or not drawn, on the turn Mega swings.

## Lock

`SET_C60_NAMES` stays the live list: 3 Clefable ex, 1 Iono, 0 Seeker. Iono → Seeker is wComp 68.9%. One Clefable ex → Seeker is wComp 68.4%, against the lock's 68.5%. The ex cut is the D60 list. The Iono cut is the Hedrick and G list. Neither replaces the lock.
