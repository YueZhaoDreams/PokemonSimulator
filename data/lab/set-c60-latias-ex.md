# C60: Latias ex in place of two Moonlight Stadium

Date: 2026-09-30
Seed: `20260926`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (the C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_latias_ex.py`
Raw: `data/lab/set-c60-latias-ex.json`
Elapsed: 344s

The lock is the live list (`SET_C60_NAMES`): two Great Encounters Moonlight Stadium and no Ultra Ball. `latias2` replaces both stadiums with Surging Sparks 76 Latias ex. `latias_ultra` replaces them with one Latias ex and one Ultra Ball.

Printed ability, Skyliner: "Your Basic Pokémon in play have no Retreat Cost."
Printed attack, Eon Blade, [P][P][C] 200: "During your next turn, this Pokémon can't attack."

Latias ex is a Basic, so Nest Ball and Ultra Ball can find it. Buddy-Buddy Poffin cannot: 210 HP is over 70. Poké Pad cannot: it is a Pokémon ex. Telepathic Psychic Energy, attached from hand to a Psychic Pokémon, searches up to 2 Basic Psychic Pokémon. Mewtwo ex is Lightning, so Telepathic never takes it.

Summon split:

- Nest Ball takes Latias ex once one Clefairy is in play, then can take Mewtwo. Poffin keeps taking Clefairy.
- Clefairy in hand are played before Mewtwo. Vs Demolish the Clefairy cap is four, so the 4+1 chump line still gets its bodies before the closer has to stand in front.
- Telepathic's two slots, once one Clefairy is already obtained, are the second Clefairy and Latias ex. With none out, both slots are Clefairy. With two and no Latias ex, Latias ex then another Clefairy.

The Party plan benches one Latias ex, does not open on it, and does not attach to it ahead of Mewtwo. Eon Blade is legal if Latias ex is forced Active. It is not the closer.

Skyliner is only your Basics, and only while that Pokémon is in play. Clefairy and Mewtwo ex retreat for 0. Clefable, Clefable ex, and Mega Clefable ex still pay their printed Retreat Cost. The opponent's Pokémon do not. Moonlight Stadium zeros Retreat Cost for every Psychic and Darkness Pokémon on both sides, including evolutions, and it does not take a bench slot or give up two prizes.

`wComp` weights T60, Hedrick, and D60 by how often the lock loses that matchup. `wAll` does the same over all six foes. A single cell near 70% has a binomial SE of about 0.8 pp. The lock row matches `data/lab/set-c60-moonlight-3.md` on this seed.

## Win rate

| List | T60 | Hedrick | UNL | D60 | S60 | G | wComp | wAll |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 Latias ex + Ultra Ball | **79.1%** | **75.4%** | **93.9%** | 76.7% | 99.5% | 75.2% | **77.1%** | 77.8% |
| 2 Latias ex | 78.7% | 74.9% | 93.3% | 75.4% | **99.8%** | **77.0%** | 76.4% | **77.9%** |
| **lock** | 72.1% | 71.5% | 91.4% | **77.6%** | 99.2% | 64.6% | 73.4% | 72.3% |

Going first / second. Same order.

| List | T60 | Hedrick | D60 | G |
| --- | --- | --- | --- | --- |
| 1 Latias ex + Ultra Ball | 81.4/76.9 | 77.8/73.0 | 78.5/74.9 | 76.3/74.1 |
| 2 Latias ex | 79.6/77.8 | 74.5/75.4 | 77.1/73.8 | 77.6/76.5 |
| **lock** | 74.0/70.2 | 73.2/69.7 | 81.0/74.0 | 66.4/62.9 |

## What the ranking says

One Latias ex plus one Ultra Ball leads `wComp` at 77.1% against the lock's 73.4% (+3.7) and against two Latias ex at 76.4% (+0.7). Hedrick is 75.4% against 71.5% (+3.9). T60 is 79.1% against 72.1% (+7.0). Going first against T60 is 81.4% against 74.0%, and going second is 76.9% against 70.2%. UNL is 93.9% against 91.4% (+2.4). G is 75.2% against 64.6% (+10.5). D60 is 76.7% against 77.6% (−0.9), about one SE. `wAll` is 77.8% against 72.3% (+5.5).

Two Latias ex leads `wAll` at 77.9% against 77.8% for one copy. That gap is 0.08 pp. G is 77.0% against 75.2% for one copy and against 64.6% for the lock (+12.4). D60 is 75.4% against 77.6% (−2.2).

Putting Mewtwo ahead of the fourth Clefairy, and holding Nest Ball's Latias ex until the second Clefairy, was measured separately on this seed. That order took one-copy D60 from 78.5% to 70.0% and `wComp` from 76.9% to 73.5%. This run puts Nest Ball back on Latias ex after the first Clefairy and puts hand Clefairy back in front of Mewtwo. The lock's D60 is 77.6% again. Telepathic still spends its second slot on Latias ex once one Clefairy is out. Hedrick on the one-copy list is 75.4%, against 73.2% when Telepathic only fetched Clefairy.

Nest Ball benched Latias ex in 1,198–1,321 of 3,000 games on the one-copy list, and in 1,047–1,253 on two copies. The card saw play in 2,289–2,445 games with one copy and in 2,497–2,576 with two. The Skyliner pivot showed up in 697 of 3,000 T60 games on the one-copy list (lock Moonlight pivot: 259) and in 2,462 of 3,000 G games (lock: 1,150). Eon Blade connected in 12 of 3,000 T60 games on that list, 1 Hedrick, 0 D60, 18 G. On two copies the attack connected in 17 T60 games and 0 D60 games.

## Conclusion

`wComp` prefers one Surging Sparks Latias ex (`sv08-076`) and one Ultra Ball in the two Moonlight Stadium slots. `wAll` prefers two Latias ex, by a margin inside the noise of a 3,000-game cell. D60 still prefers the two stadiums, by about one SE against the one-copy list. `SET_C60_NAMES` stays the two-stadium list.
