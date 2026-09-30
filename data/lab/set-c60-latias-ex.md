# C60: Latias ex in place of two Moonlight Stadium

Date: 2026-09-30
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_latias_ex.py`
Raw: `data/lab/set-c60-latias-ex.json`
Elapsed: 377s

The lock is the live list (`SET_C60_NAMES`): two Great Encounters Moonlight Stadium and no Ultra Ball. `latias2` replaces both stadiums with Surging Sparks 76 Latias ex. `latias_ultra` replaces them with one Latias ex and one Ultra Ball.

Printed ability, Skyliner: "Your Basic Pokémon in play have no Retreat Cost."
Printed attack, Eon Blade, [P][P][C] 200: "During your next turn, this Pokémon can't attack."

Latias ex is a Basic, so Nest Ball and Ultra Ball can find it. Buddy-Buddy Poffin cannot: 210 HP is over 70. Poké Pad cannot: it is a Pokémon ex. Telepathic Psychic Energy, attached from hand to a Psychic Pokémon, searches up to 2 Basic Psychic Pokémon. Mewtwo ex is Lightning, so Telepathic never takes it.

Summon order, lowest tier first. A copy already in hand counts as obtained when the search looks at the deck:

1. First Clefairy
2. Second Clefairy
3. Latias ex
4. Third Clefairy
5. First Mewtwo ex
6. Fourth Clefairy
7. Second Mewtwo ex, only while the Mewtwo cap allows it

The second Clefairy comes before Latias because Skyliner's free retreat needs a Clefairy to pivot into before the next Party can fire. The third Clefairy doubles Party again. The first Mewtwo comes before the fourth Clefairy because Photon Kinesis is 10 plus 30 damage for each Psychic Energy on your Pokémon, and Wonder Storm is 20 for each. The live list has no Latias, so its ladder is three Clefairy, then Mewtwo, then the fourth Clefairy. This run's lock row is that ladder. It is a different policy from `data/lab/set-c60-moonlight-3.md`, where every Clefairy under the cap came down before Mewtwo.

The Party plan benches one Latias ex, does not open on it, and does not attach to it ahead of Mewtwo. Eon Blade is legal if Latias ex is forced Active. It is not the closer.

Skyliner is only your Basics, and only while that Pokémon is in play. Clefairy and Mewtwo ex retreat for 0. Clefable, Clefable ex, and Mega Clefable ex still pay their printed Retreat Cost. The opponent's Pokémon do not. Moonlight Stadium zeros Retreat Cost for every Psychic and Darkness Pokémon on both sides, including evolutions, and it does not take a bench slot or give up two prizes.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp.

## Win rate

| List | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2 Latias ex | 79.0% | **74.7%** | 91.5% | 68.4% | **99.6%** | 73.8% | **74.0%** | 75.5% |
| 1 Latias ex + Ultra Ball | **79.4%** | 71.5% | **93.1%** | 70.0% | 99.4% | **74.9%** | 73.5% | **75.6%** |
| **lock** | 73.2% | 69.3% | 90.2% | **72.4%** | 98.9% | 67.1% | 71.5% | 72.1% |

Going first / second. Same order.

| List | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| 2 Latias ex | 79.2/78.9 | 76.5/72.7 | 70.3/66.3 | 76.5/71.0 |
| 1 Latias ex + Ultra Ball | 80.7/78.1 | 72.0/71.0 | 71.9/68.2 | 77.5/72.2 |
| **lock** | 75.4/71.0 | 70.0/68.6 | 76.9/68.3 | 68.1/66.1 |

## What the ranking says

Two Latias ex leads `wComp` at 74.0% against the lock's 71.5% (+2.5) and against one Latias ex plus Ultra Ball at 73.5% (+0.5). Hedrick is the cell that does it: 74.7% against 71.5% for one copy (+3.2) and against 69.3% for the lock (+5.4). T60 is 79.0% against 73.2% (+5.8). D60 is 68.4% against 72.4% (−4.0).

One Latias ex plus one Ultra Ball leads `wAll` at 75.6% against 75.5% for two copies. That gap is 0.06 pp. T60 is 79.4% against 73.2% (+6.2). Going first against T60 is 80.7% against 75.4%, and going second is 78.1% against 71.0%. Hedrick is 71.5% against 69.3% (+2.2). UNL is 93.1% against 90.2% (+2.9). G is 74.9% against 67.1% (+7.8). D60 is 70.0% against 72.4% (−2.3). `wComp` is 73.5% against 71.5% (+2.0). `wAll` is 75.6% against 72.1% (+3.5).

The lock is the best D60 list in this run. Putting the first Mewtwo ahead of the fourth Clefairy is the change on that list: D60 is 72.4% here, and `set-c60-moonlight-3.md` recorded 77.6% when the fourth Clefairy came first. G on the same lock moved the other way, 67.1% here against 64.6% in that note.

Nest Ball benched Latias ex in 834–998 of 3,000 games on the one-copy list, and in 785–940 on two copies. The card saw play in 2,037–2,274 games with one copy and in 2,280–2,389 with two. The Skyliner pivot showed up in 763 of 3,000 T60 games on the one-copy list (lock Moonlight pivot: 275) and in 2,507 of 3,000 G games (lock: 1,206). Eon Blade connected in 10 of 3,000 T60 games on that list, 5 Hedrick, 0 D60, 14 G. On two copies the attack connected in 14 T60 games and 0 D60 games.

## Conclusion

`wComp` prefers two Surging Sparks Latias ex (`sv08-076`) in the Moonlight Stadium slots. `wAll` prefers one Latias ex and one Ultra Ball, by a margin inside the noise of a 3,000-game cell. D60 still prefers the two stadiums. `SET_C60_NAMES` stays the two-stadium list.
