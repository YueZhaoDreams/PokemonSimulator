# Celebi ◇ Chandelure roast

Celebi ◇ uses Time Distortion: devolve any number of benched Pokémon as many times as you like, and put each Evolution card removed this way into the hand. The measured line devolves each benched Chandelure once, leaving Lampent.

Chandelure's Mountain Roasting says the top 3 cards are discarded when you play that Pokémon from your hand to evolve. One evolution mills 3. Three mill 9. Four mill 12. Dawn puts one Basic, one Stage 1, and one Stage 2 into the hand. Playing Chandelure from that hand mills.

Broken Time-Space says each player may evolve a Pokémon that he or she just played or evolved during that turn. With it in play, a Litwick played this turn can evolve into Lampent and then into Chandelure before the attack. Both players may use that stadium.

Pichu is HeartGold & SoulSilver Playground. Each player may bench as many Basic Pokémon as they like, this player first. Roast benches Litwick until four lines are in play, then Celebi ◇. Dawn searches the deck for a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon. It takes Pichu, Litwick, or Celebi ◇ for the Basic, Lampent for the Stage 1, and Chandelure for the Stage 2. Under Broken Time-Space a Litwick played this turn can evolve twice before the attack. Celebi ◇ uses Time Distortion and puts that Chandelure back into the hand. Level Ball finds a Pokémon with 90 HP or less and does not find Chandelure. When this turn will play Playground, Level Ball searches a Stage 1, so Litwick stays in the deck for that attack.

Hisuian Heavy Ball looks at the face-down Prize cards. It may reveal a Basic Pokémon, put that Pokémon into the hand, and put this card in its place as a face-down Prize card. If it does not reveal a Basic, this card goes to the discard pile. Then the face-down prizes are shuffled. When more than one Basic is there, roast reveals Celebi ◇ before Litwick, then a Pichu or Cleffa the deck no longer has. The roast list has one copy. That copy replaced one Switch: every other card was measured as the cut, this swap had the higher weighted win rate, and a second copy did not raise it. See data/lab/set-mill-roast-heavy.md.

Jacq searches the deck for up to 2 Evolution Pokémon. An earlier search on the Heavy Ball list at 40 games per seat kept zero; its best cut was one Litwick at 33.7%, below 34.5%. The same search on the Hyper Aroma list at 400 games per seat kept three copies: one Switch, then one Energy Retrieval, then one Buddy-Buddy Poffin. The path is 38.5%, 39.7%, 40.7%, 41.1%. The fourth copy's best cut, one Broken Time-Space, is 41.1% and is not higher. The third copy's gain is inside one standard error, and the best of about twenty cuts sits a little high. See data/lab/set-mill-roast-jacq.md.

Evolution Incense searches the deck for one Evolution Pokémon. Roast takes Chandelure once a Lampent is in hand or in play, and takes Lampent only while a Litwick still has no Stage 1. Three copies replaced one Level Ball and both Cleffa. A fourth copy did not raise the weighted win rate. See data/lab/set-mill-roast-incense.md. That search was 40 games per seat. The same list at 400 games per seat is 34.4%.

Hyper Aroma searches the deck for up to 3 Stage 1 Pokémon. Roast takes Lampent and stops once four Lampent are in hand or in play. The printed count is the parser's search_stage1 count. One copy replaces Ultra Ball. At 400 games per seat that swap is 38.5% against the 34.4% list. See data/lab/set-mill-roast-aroma.md.

Lampent is Plasma Storm Freefloating. With no Energy attached, its retreat cost is 0. Fire Energy stays on Celebi ◇.

Rescue Scarf puts the Pokémon into the hand when an attack Knocks it Out, and discards the cards attached to it. Celebi ◇ therefore does not go to the discard pile, and the Prism Star rule does not put it in the Lost Zone. Energy Retrieval takes that Fire Energy back. Arven can find an Item and the scarf. When Celebi ◇ or a needed Litwick or Pichu is in the prizes and Hisuian Heavy Ball is still in the deck, Arven takes that ball. Team Rocket's Petrel searches the deck for a Trainer card. It takes Hisuian Heavy Ball before Broken Time-Space when that prize is Celebi ◇, a stuck Pichu, or a Litwick with almost none of the line outside the prizes. A spare Litwick waits until after Dawn. Petrel does not search a Pokémon or an Energy card.

Cleffa was tried again on the Hyper Aroma list at 400 games per seat. Each step would replace one other card with one Cleffa. The highest first cut, one Switch, is 38.1%, below 38.5%, so the list keeps zero Cleffa. When one Cleffa is in the deck it enters play about 0.41 times per game and Eeeeeeek fires about 0.02 times. It is a backup wall behind Pichu. See data/lab/set-mill-roast-cleffa.md. Pichu is the Playground attacker. Sweet Sleeping Face prevents attack damage while that Pokémon is Asleep. Slumbering Forest makes the between-turns sleep check two coins, and the Pokémon stays Asleep unless both are heads. Asleep blocks retreat. This list has no Switch.

A Litwick played on the turn Dawn finds Lampent stays unevolved until Broken Time-Space is in play. The stadium also lets that Lampent take Chandelure the same turn.

- **List**: Litwick ×4, Lampent ×4, Chandelure ×4, Celebi ◇ ×1, Pichu ×3, Arven ×4, Team Rocket's Petrel ×4, Buddy-Buddy Poffin ×2, Energy Search ×4, Energy Retrieval ×1, Rescue Scarf ×4, Dawn ×4, Level Ball ×2, Broken Time-Space ×3, Slumbering Forest ×1, Fire Energy ×7, Hisuian Heavy Ball ×1, Evolution Incense ×3, Hyper Aroma ×1, Jacq ×3
- **Seed**: `20261027`
- **Games per seat**: 400
- **Seats**: roast is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 122.9s

Weighted win rate **41.1%** (± 0.5%). Games in which Mountain Roasting fired: **87.4%**. Hand-evolve turns per game: 3.22. Cards milled by those turns per game: 17.02. Dawn plays per game: 1.04. Evolution Incense plays per game: 1.16. Hyper Aroma plays per game: 0.57. Lampent found by Hyper Aroma per game: 1.34. Jacq plays per game: 0.70. Evolution Pokémon found by Jacq per game: 1.34. Hisuian Heavy Ball swaps per game: 0.33. Broken Time-Space plays per game: 0.95. Time Distortion devolves per game: 4.97. Rescue Scarf returns per game: 0.75. Celebi ◇ sent to the Lost Zone per game: 0.38. Playground attacks per game: 0.82. Pichu entered play per game: 1.80. Eeeeeeek per game: 0.00. Cleffa entered play per game: 0.00. Mill turns of 9 or more: 20.6%. A shorter row can be one Lampent taking one Chandelure from the hand, or the opponent's deck running out.

## Wave

Each row is how often a turn's from-hand Chandelure evolutions milled that many cards. One Chandelure mills 3. Dawn itself is not in this histogram. A short last row can be the opponent's deck running out.

| Cards milled that turn | Turns per game |
| ---: | ---: |
| 1 | 0.035 |
| 2 | 0.036 |
| 3 | 1.403 |
| 4 | 0.033 |
| 5 | 0.031 |
| 6 | 0.967 |
| 7 | 0.026 |
| 8 | 0.028 |
| 9 | 0.587 |
| 10 | 0.004 |
| 11 | 0.004 |
| 12 | 0.071 |

## Foes

| Foe | Win rate | A | B | Fired | Mill turns | Mill cards | Scarf | Lost Zone |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 38.2% | 36.8% | 39.8% | 94.0% | 3.35 | 15.82 | 0.67 | 0.29 |
| Hedrick Worlds Dragapult | 57.8% | 58.2% | 57.2% | 95.5% | 3.73 | 18.29 | 0.47 | 0.20 |
| Unlimited Dragapult | 63.7% | 62.3% | 65.2% | 96.2% | 3.42 | 16.57 | 0.50 | 0.23 |
| Cornerstone Ogerpon (D60) | 14.0% | 13.0% | 15.0% | 90.2% | 3.18 | 17.18 | 1.03 | 0.59 |
| Wo-Chien / Floragato (S60) | 70.8% | 68.2% | 73.2% | 96.6% | 4.48 | 25.84 | 0.74 | 0.32 |
| Gholdengo (G) | 40.4% | 40.2% | 40.5% | 94.4% | 3.60 | 19.86 | 0.86 | 0.52 |
| Clefairy / Mewtwo (C60) | 44.9% | 41.2% | 48.5% | 90.0% | 2.89 | 14.42 | 0.89 | 0.50 |
| Set M (Mew ex) | 10.1% | 8.2% | 12.0% | 63.9% | 1.80 | 9.04 | 0.70 | 0.45 |
| Mega Starmie ex (Kudo) | 13.9% | 15.0% | 12.8% | 79.8% | 2.20 | 10.48 | 0.60 | 0.32 |
| Lucario Hariyama | 67.6% | 67.5% | 67.8% | 87.5% | 2.76 | 12.83 | 0.50 | 0.26 |
| Iron Thorns ex | 90.4% | 89.5% | 91.2% | 96.0% | 4.14 | 20.98 | 0.65 | 0.13 |
| Carpet Set H | 88.6% | 88.0% | 89.2% | 96.6% | 5.37 | 31.72 | 0.73 | 0.08 |
| Ambipom Hand Fling | 95.2% | 95.2% | 95.2% | 99.5% | 5.00 | 28.80 | 0.15 | 0.07 |
