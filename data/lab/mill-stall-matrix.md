# Mill stall vs household 60s

Date: 2026-10-06
Seed: `20261006`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (mill is always player A; who goes first is random)
Script: `data/lab/mill_stall_matrix.py`
Raw: `data/lab/mill-stall-matrix.json`
Elapsed: 368.1s

List is `SET_MILL60_NAMES`, strategy `mill`. Great Tusk, Latias ex, Meowth ex, one Radiant Tsareena, Professor Sada's Vitality, Explorer's Guidance, Lively Stadium, Ancient Booster Energy Capsule, Hero's Cape, Earthen Vessel, Stone Fighting Energy. The card-by-card note is [mill-stall-deck.md](mill-stall-deck.md).

30-card Family Cup lists (A, B, C, D, E, F, S, T) are a different deck size and rule preset, so they are not in this array. G30 is the 60-card Ambipom list already used in the household bakeoff.

Mill did not deck itself out in any of the 33,000 games.

## Mill win rate

| Foe | Strategy | Overall | Mill first | Mill second | Deck-outs | Cards milled, average | Max |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Carpet Set H | nuzzle | **96.5%** | 96.3% | 96.6% | 41 | 7.9 | 29 |
| G30 Ambipom | celebration | **93.7%** | 93.2% | 94.1% | 502 | 6.8 | 28 |
| S60 Floragato | slash | **89.7%** | 90.3% | 89.1% | 2,535 | 18.6 | 28 |
| UNL Dragapult | phantom | **60.8%** | 60.4% | 61.2% | 1,727 | 9.8 | 27 |
| L60 Lucario Hariyama | aura | **44.2%** | 44.8% | 43.6% | 1,189 | 6.6 | 23 |
| Hedrick Worlds Dragapult | phantom | **41.6%** | 43.0% | 40.2% | 1,055 | 7.0 | 25 |
| T60 Dragapult | phantom | **28.5%** | 29.9% | 27.1% | 740 | 7.2 | 22 |
| C60 Clefairy / Mewtwo | party | **13.8%** | 14.3% | 13.3% | 151 | 4.2 | 23 |
| Carpet Set G | g | **13.5%** | 13.8% | 13.2% | 85 | 6.0 | 27 |
| D60 Charm Ogerpon | demolish | **3.1%** | 2.9% | 3.2% | 63 | 10.2 | 29 |
| M60 Mew ex baby box | mew_baby | **0.8%** | 0.7% | 0.9% | 20 | 3.0 | 30 |

## How a mill win ended

Counts are mill's wins only, out of 3,000.

| Foe | Deck-out | Prize cards | Empty board | Turn limit |
| --- | ---: | ---: | ---: | ---: |
| Carpet Set H | 41 | 630 | 2,082 | 141 |
| G30 Ambipom | 502 | 1,394 | 885 | 29 |
| S60 Floragato | 2,535 | 7 | 52 | 97 |
| UNL Dragapult | 1,727 | 29 | 69 | 0 |
| L60 Lucario Hariyama | 1,189 | 48 | 89 | 0 |
| Hedrick Worlds Dragapult | 1,055 | 99 | 92 | 3 |
| T60 Dragapult | 740 | 21 | 95 | 0 |
| C60 Clefairy / Mewtwo | 151 | 221 | 42 | 1 |
| Carpet Set G | 85 | 85 | 221 | 14 |
| D60 Charm Ogerpon | 63 | 0 | 0 | 1 |
| M60 Mew ex baby box | 20 | 1 | 2 | 0 |

Prize cards here includes "took all prize cards" and "more prizes at turn limit". Turn limit in that table is "more remaining HP at turn limit". D60's other 28 wins are openings where D60 had no Basic Pokémon.

Carpet H and G30 are wins. The end of those games is a Knock Out race or an empty board. Giant Tusk was used 8,628 times against H and 10,886 times against G30. Floragato is the deck-out: 2,535 of 2,691 wins are the opponent failing to draw, average 18.6 cards milled, average 31.4 turns. UNL Dragapult, Lucario, and the Hedrick list follow the same shape, with fewer of the games lasting long enough. T60 Dragapult is 740 deck-outs and 856 wins; the other 2,144 games are 1,282 prize losses and 859 empty boards.

Mew ex baby box is 23 wins. Twenty of those are deck-outs. The losses are 1,560 prize games and 1,410 empty boards. Ogerpon is 92 wins, and Giant Tusk was not used. Ogerpon still takes 5.18 prizes a game on average.

Radiant Tsareena reached play in roughly a third to a half of games (943 against C60, 1,199 against T60, 1,041 against Mew ex). Nest Ball does not search a Radiant. Elegant Heal resolved in 1,121 T60 games and 752 Mew games, and in 0 G30 games. Max Potion resolved in 567 T60 games, 254 Mew games, and 10 Floragato games.

Latias ex and Meowth ex remain two-prize gust targets. Going first and going second stay within about three points in every cell.
