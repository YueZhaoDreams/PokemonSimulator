# Doll

Locked 60. Seed id `seed-doll`. The pilot is strategy `doll`. The deck does not select that spec by itself.

Cleffa is HeartGold & SoulSilver 17, Eeeeeeek. Mime Jr. is Call of Legends 47, Sleepy Lost. Robo Substitute Team Flare Gear is the full Phantom Forces 102 name. Life Dew is one Plasma Freeze tool. Lillie's Poké Doll uses the ASCII apostrophe already registered for that print.

Item dolls are Trainers. A Pokémon search does not find them. They are played from the hand. One Snorlax Doll is benched while setting up. The two search Items are Level Ball. Its sentence takes a Pokémon with 90 HP or less into the hand, so it can find Shedinja. Nest Ball is not in this 60.

## Holdout

The rates below are the fight-script holdout, seed 20261025, 1000 games each seat, 13 weighted foes. They are not games played by this engine. The 100-game selection on seed 20261024 was sisters-weighted 31.4% and self-weighted 31.7%. The holdout stayed inside that sample's noise.

| Weight | Baseline | Holdout |
| --- | --- | --- |
| Sisters-loss weights | 26.9% | 30.1% |
| Frozen self weights | 23.6% | 30.2% |

| Foe | Win rate | Seat A | Seat B | Foe prizes |
| --- | --- | --- | --- | --- |
| T60 | 55.9% | 57.6% | 54.2% | 2.74 |
| Hedrick | 31.1% | 31.3% | 30.8% | 2.69 |
| Unlimited Dragapult | 78.9% | 78.6% | 79.1% | 1.90 |
| D60 | 2.1% | 1.9% | 2.2% | 1.48 |
| S60 | 52.9% | 52.7% | 53.1% | 2.58 |
| G | 19.8% | 18.9% | 20.7% | 4.02 |
| C60 | 46.8% | 47.6% | 45.9% | 3.20 |
| M | 19.9% | 19.8% | 20.0% | 3.99 |
| Starmie | 11.4% | 10.6% | 12.1% | 3.05 |
| Lucario | 73.1% | 74.0% | 72.2% | 2.18 |
| Thorns | 87.9% | 87.3% | 88.5% | 1.55 |
| H | 4.6% | 4.6% | 4.5% | 3.02 |
| g30 | 55.3% | 55.8% | 54.7% | 0.92 |

D60's 2.1% includes mulligan-cap wins plus a few real deck-outs. Against Carpet H, Battle Cage's average was 0. An empty board after the Active Pokémon is Knocked Out still loses, including when the prize count is already low. That residual is part of this lock.

## Level Ball

The holdout above is the Nest Ball list on the fight script. The swap was measured on the product engine, strategy `doll`, seed 20261026, 1000 games each seat, the same 13 foes. Nest Ball is the locked list with those two cards put back. Level Ball is this 60.

| List | Sisters-weighted | Self-weighted |
| --- | --- | --- |
| Nest Ball | 28.9% | 28.6% |
| Level Ball | 28.8% | 28.9% |

Level Ball tutored Shedinja, and Vessel of Life fired more often. The weighted rates stayed inside the noise of this sample. These games are not the fight-script holdout.

## Black Market

The Black Market 60 cuts one of the two Switches for one Black Market ◇ (Team Up 134). The confirm is the product engine, strategy `doll`, seed 20261028, 200 games each seat. Sisters-weighted 27.6% on the two-Switch list, 29.4% after the cut. The gap's standard error is about 0.81 points. The Stadium is played about once every ten games, and the prize line fires less often, because Battle Cage stays up against spread. Darkness Energy still has to be attached before that line applies. Life Dew stays off Sableye when Black Market is in play. This confirm is not the 1000-game holdout above. Its loss reasons are in "Why the Black Market 60 loses", and in `data/lab/set-doll-losses.md`.

## Arven and Petrel

The locked 60 cuts two Cleffa for one Arven and one Team Rocket's Petrel. The confirm is the product engine, strategy `doll`, seed 20261029, 200 games each seat. The Arven step starts from the Black Market 60. Its highest confirm is 31.2% against 29.5% (+1.7 points; the gap's standard error is 0.84 points). Cleffa, VS Seeker, Switch, and Crushing Hammer sit within 0.2 points of one another, inside that standard error. The point estimate cuts Cleffa, and the Petrel step is that list. Petrel's highest confirm cuts a second Cleffa: 33.8% against 31.2% (+2.6 points; the gap's standard error is 0.86 points). Switch is next, 0.8 points lower. Lillie's Poké Doll and Robo Substitute stay at four. Doll plays rise from 2.86 to 3.39 a game. Arven resolves about 0.49 times a game and Petrel about 0.47. One Supporter is played each turn. When the hand has no doll, the search takes Lillie's Poké Doll or Robo Substitute. This confirm is not the 1000-game holdout. Detail is `data/lab/set-doll-arven-petrel.md`.

## Eeeeeeek when the dolls run out

The locked 60 is unchanged. Cleffa is still HeartGold & SoulSilver 17: shuffle the hand into the deck, draw 6, and Cleffa is now Asleep. The strict hand check almost never used that attack, so dolls stayed in the deck while the board emptied. The pilot now uses it when the hand has fewer than two replayable dolls, at most two are in play, and the deck still has one. Life Dew prefers that Cleffa. Item dolls can't retreat. Switch swaps one for Cleffa. Otherwise the Active doll is put on the bottom of the deck, or discarded, by its own sentence, and Cleffa is promoted, only while another Pokémon remains benched. Junk Hunt stays ahead of that.

Same seed 20261029, 200 games each seat, Sisters weights, product engine, strategy `doll`. Weighted win rate 43.5% against the Petrel confirm 33.8% (+9.7 points; the gap's standard error is 0.91 points, about 10.6 standard errors). Eeeeeeek resolves 1.83 times a game. Life Dew is attached 0.56 times a game. Sisters-weighted empty boards fall from 40.4% of games to 26.7%. D60 goes from 1.0% to 10.5%, and its empty games from 98.5% to 70.5%. Starmie goes from 11.5% to 24.2% (empty 62.5% to 41.0%). G goes from 23.5% to 41.0% (empty 37.8% to 18.2%). Every foe in the thirteen is higher. This confirm is not the 1000-game holdout. Detail is `data/lab/set-doll-eeeeeeek.md`.

## Lillie's Determination

The locked 60 has four Lillie's Determination. Each copy replaced one card, and the next copy was measured on that new list. Printed text: shuffle your hand into your deck, then draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead. Doll plays it when the deck still has a replayable doll, the hand has fewer than two, and at most two are in play. A doll, Life Dew, Cursed Shovel, the Stadiums, Arven, and Petrel outrank it. Handiwork yields on that turn. One Darkness Energy remains. Dark Patch is out. Cleffa and Smoochum are one each.

The decision sample is seed 20261029, 400 games each seat, Sisters weights, product engine, strategy `doll`. The screen is 40 games. A confirm higher than its own baseline is the next list. Four is the maximum.

| Copy | Cut | Baseline | Confirm | Gap | Gap SE |
| --- | --- | ---: | ---: | ---: | ---: |
| 1 | Darkness Energy | 43.7% | 45.0% | +1.3 | 0.67 |
| 2 | Dark Patch | 45.0% | 46.8% | +1.7 | 0.67 |
| 3 | Cleffa | 46.8% | 49.5% | +2.7 | 0.66 |
| 4 | Smoochum | 49.5% | 51.5% | +2.0 | 0.66 |

Lillie's Determination resolves 0.40, 0.81, 1.15, then 1.51 times a game. This confirm is not the 1000-game holdout. Detail is `data/lab/set-doll-lillie.md`.

## Why the strict Eeeeeeek 60 loses

This sample is the Arven and Petrel lock before Cleffa was sent up to draw, seed 20261029, 200 games each seat, the same games as the Petrel confirm. Sisters-weighted win rate is 33.8%. The weighted losses are an empty board 61.0%, the opponent taking all 6 Prize cards 20.3%, and the 40-turn limit 18.6% (16.8% because the opponent had more Prizes, 1.8% because they had more remaining HP). The empty board is 40.4% of games, the same band as the Black Market 60. The six-Prize losses are what shrank. Doll did not deck out, and Doll did not fail to find a Basic. A win is the opponent decking out. Two D60 games and eight Iron Thorns games are the opponent still having no Basic after the mulligan cap. One Starmie game is Doll having more Prizes at the turn limit. The detail is `data/lab/set-doll-arven-petrel-losses.md`.

The weighted losses sit on five foes: D60 21.7% (394 of 400 games end with an empty board; the opponent has taken 1.81 Prizes; about 3.7 dolls and 2.2 prize bodies, at 16.1 turns), Set M 15.7% (139 games are 6 Prizes, 146 end empty at a mean of 9.3 turns), Starmie 14.2% (250 empty at 14.0 turns, 72 are 6 Prizes), G 13.5% (151 empty, 112 are 6 Prizes), and Carpet H 10.8% (323 games reach the turn limit with H ahead on Prizes: 43 at 1, 69 at 2, 108 at 3, 73 at 4, 30 at 5). S60's mill wins 61.3%, and 27.8% of those games hit the turn limit.

## Why the Black Market 60 loses

This sample is the Black Market 60, before Arven and Petrel. Sisters-weighted win rate on this sample is 29.4%. The weighted losses are an empty board 56.7%, the opponent taking all 6 Prize cards 27.1%, and the 40-turn limit 16.2% (14.5% because the opponent had more Prizes, 1.7% because they had more remaining HP). Doll did not deck out in these 5200 games, and Doll did not fail to find a Basic. A win is the opponent decking out. D60's three wins, and three of Iron Thorns' wins, are the opponent still having no Basic after the mulligan cap. One Lucario win is an empty opposing board. One game against M and one against H win on remaining HP at the turn limit. The detail is `data/lab/set-doll-losses.md`.

Black Market was in play in 7.1% of the losses, and its prize line fired in 2.9%. Against spread and Demolish the pilot keeps Battle Cage, so the Stadium is usually not the card in play when the game is lost.

The weighted losses sit on five foes:

| Foe | Share of weighted losses | What happens |
| --- | ---: | --- |
| D60 | 20.4% | 395 of 400 games end with an empty board. The opponent has taken 2.01 Prizes. The other 3 games are the opponent still having no Basic after the mulligan cap. |
| M | 17.1% | 182 games the opponent takes 6 Prizes. 148 end with an empty board, at a mean of 8.3 turns. |
| Starmie | 13.3% | 231 games end with an empty board, at a mean of 13.4 turns. 85 are 6 Prizes. |
| G | 13.1% | 155 games are 6 Prizes. 137 are an empty board. |
| H | 10.0% | 294 games reach the turn limit with H ahead on Prizes: 97 at 3, 83 at 4, 51 at 5. The mill finishes in 6.5% of games. |

Demolish does 140, and that damage is not affected by any effects on the opponent's Active Pokémon. Sweet Sleeping Face does not stop it. The pilot does not play those faces into Demolish. Lillie's Poké Doll and Robo Substitute award no Prize and have 30 HP, so Ogerpon can Knock them Out without taking a Prize. The game ends when the Active is Knocked Out and the Bench is empty. In those games Doll has lost about 2.9 dolls and 2.3 prize bodies.

Sweet Sleeping Face prevents attack damage only while that Pokémon is Asleep. Between turns its owner flips 1 coin. Under Slumbering Forest the flip is 2 coins, and Asleep ends only when every coin is heads. Against Dragapult, Starmie, and Carpet H the pilot keeps Battle Cage, so the check stays 1 coin. Damage counters are not attack damage. Phantom Dive places its counters on one Benched Pokémon, and Battle Cage is what stops that placement. A 30 HP doll is Knocked Out by those counters. Sableye has no Sweet Sleeping Face. Where the opponent takes 6 Prizes, the Knock Outs are Cleffa, Smoochum, Mime Jr., and Sableye. Shedinja is not among them. Set M also plays Mime Jr. and Manaphy, so those two names are not separated in that matchup.

Carpet H's Wicked Thunder does 60. An Asleep face in the Active Spot does not take that attack damage. Over 40 turns H still leaves with 3, 4, or 5 Prizes, and Doll's mill has not finished. S60 is the same shape at a smaller weight: the mill wins 55%, and 27.5% of games hit the turn limit. Ambipom's non-mill losses are the turn limit on remaining HP, 116 games. Its Sisters weight is 1.1%.
