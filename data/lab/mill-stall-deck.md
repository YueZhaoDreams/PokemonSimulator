# Mill stall 60

Great Tusk is the body that gives up one prize. Meowth ex searches a Supporter only when it is played from the hand. Latias ex stays on the bench: Skyliner makes every Basic retreat for free. Mew ex is not in this list.

## The 60

- Pokémon 9: Great Tusk ×4, Latias ex ×2, Meowth ex ×2, Radiant Tsareena ×1
- Supporters 6: Professor Sada's Vitality ×4, Explorer's Guidance ×2
- Stadiums and items 25: Ancient Booster Energy Capsule ×4, Hero's Cape ×1, Lively Stadium ×4, Night Stretcher ×4, Nest Ball ×4, Earthen Vessel ×4, Energy Retrieval ×2, Max Potion ×2
- Energy 20: Double Colorless Energy ×4, Stone Fighting Energy ×4, Fighting Energy ×12

One Double Colorless Energy pays Land Collapse. Fighting Energy is the Basic Energy Professor Sada's Vitality can attach from the discard pile. Double Colorless Energy is Special Energy, so Sada cannot attach it.

## Printed extras

Lively Stadium: each Basic Pokémon in play, yours and your opponent's, gets +30 HP. Evolutions do not. Great Tusk, Latias ex, and Meowth ex are all Basic. Radiant Tsareena is not Basic, so the stadium does not add 30 to it, and Nest Ball does not search it. It is played from the hand.

Radiant Tsareena (Silver Tempest 16), one copy. Elegant Heal: once during your turn, heal 20 damage from each of your Pokémon. The opponent's Pokémon are not healed. Aroma Shot is Grass and is not the mill attack. One prize.

Ancient Booster Energy Capsule: the Ancient Pokémon it is attached to gets +60 HP, recovers from Special Conditions, and cannot be affected by them. On a non-Ancient Pokémon the +60 does not apply. Great Tusk is 140 + 60 + 30 = 230 HP, and it is still one prize.

Earthen Vessel discards 1 card from your hand, then searches the deck for up to 2 Basic Energy cards. It finds Fighting Energy. Double Colorless Energy is Special Energy, so the Vessel does not find it. The discard is a spare Nest Ball or a spare Fighting Energy. Professor Sada's Vitality, Great Tusk, and Double Colorless Energy stay in hand.

Night Stretcher puts one Pokémon or one Basic Energy from the discard pile into the hand. After Great Tusk is Knocked Out, the stretcher picks that body back up.

Hero's Cape is one ACE SPEC. The Pokémon it is attached to gets +100 HP and can't be affected by any Special Conditions. It goes on Great Tusk. With the capsule the tool slot is one card, so the cape takes the Active Tusk and a capsule waits for another Tusk. Cape plus Lively Stadium is 140 + 100 + 30 = 270 HP, still one prize.

Stone Fighting Energy (Vivid Voltage 164) provides Fighting Energy. The Fighting Pokémon it is attached to takes 20 less damage from attacks, after Weakness and Resistance. Each copy adds its own 20. It does not reduce damage on Latias ex or Meowth ex. It is Special Energy, so Sada, Earthen Vessel, Night Stretcher, and Energy Retrieval do not find it. One Stone plus one Fighting, or one Double Colorless Energy, pays Land Collapse.

Max Potion heals all damage from one Pokémon. If it healed, it discards all Energy from that Pokémon. On this list it heals Great Tusk. A Tusk with no Energy is healed once it has at least 20 damage. A Tusk that still has Energy is healed only when 160 or less HP remains and a Double Colorless Energy is in hand, because trainers resolve before the energy attachment. Professor Sada's Vitality does not attach (and therefore does not draw 3) when that hand Energy already finishes Land Collapse.

## One round

After setup the opponent has about 47 cards left.

1. Great Tusk is Active. Latias ex is benched, so retreat costs nothing.
2. Earthen Vessel discards a spare card and puts up to 2 Fighting Energy into the hand. Attach Double Colorless Energy, or two Fighting Energy, plus the capsule and Lively Stadium.
3. Meowth ex comes from the hand and searches Professor Sada's Vitality, if that card is not already in hand.
4. Play Sada. Choosing zero Ancient Pokémon does not draw. The Ancient flag is that the Supporter was played.
5. Land Collapse discards 1, then 3 more. That is 4.
6. They draw 1 on their turn.

Net is about 5 cards a round, about 9 or 10 attack turns, if a Great Tusk is in the Active Spot and can pay the attack. They take one prize for each Great Tusk they Knock Out. Six prizes is six of those Knock Outs. The stretcher puts the Tusk back into the hand so the next one can be played.

Explorer's Guidance looks at the top 6, keeps 2, and discards the other 4. Use it only while Great Tusk is still missing.

## What still takes two prizes

Latias ex and Meowth ex are two-prize Basics. Boss's Orders can gust them. Lively Stadium also gives the opponent's Basic Pokémon +30 HP.

## Formal matrix

Standard 60, seed `20261006`, 3,000 games a cell, this list as player A. Who goes first is random. Script `data/lab/mill_stall_matrix.py`. The table and the win reasons are in [mill-stall-matrix.md](mill-stall-matrix.md).

| Foe | Wins | Deck-outs | Cards milled, average | Max |
| :--- | ---: | ---: | ---: | ---: |
| Carpet Set H | 2,894/3,000 | 41 | 7.9 | 29 |
| G30 Ambipom | 2,810/3,000 | 502 | 6.8 | 28 |
| S60 Floragato | 2,691/3,000 | 2,535 | 18.6 | 28 |
| UNL Dragapult | 1,825/3,000 | 1,727 | 9.8 | 27 |
| L60 Lucario | 1,326/3,000 | 1,189 | 6.6 | 23 |
| Hedrick Dragapult | 1,249/3,000 | 1,055 | 7.0 | 25 |
| T60 Dragapult | 856/3,000 | 740 | 7.2 | 22 |
| C60 Clefairy / Mewtwo | 415/3,000 | 151 | 4.2 | 23 |
| Carpet Set G | 405/3,000 | 85 | 6.0 | 27 |
| D60 Charm Ogerpon | 92/3,000 | 63 | 10.2 | 29 |
| M60 Mew ex | 23/3,000 | 20 | 3.0 | 30 |

Floragato, UNL Dragapult, Lucario, and the Hedrick list are deck-outs. Carpet H and G30 win by Knock Out or an empty board. Mew ex and Ogerpon take the prizes. Mill did not deck itself out.
