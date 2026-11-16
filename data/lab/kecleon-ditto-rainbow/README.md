# Kecleon + Ditto ◇ adaptive rainbow toolbox

Research note for a 60-card deck with three jobs: Kecleon turns the types in hand into damage, Ditto ◇ becomes whichever Stage 1 the board wants, and Rescue Scarf puts the knocked-out Pokémon back in hand. The card pool is the physical Pokémon TCG. Pokémon TCG Pocket is not in the snapshot and is not used.

The tables live next to this note.

| File | What it is |
| --- | --- |
| `dual_type_pokemon.csv` | All 106 dual-type Pokémon entries in the snapshot, one row per printing |
| `basic_dual_type_pokemon.csv` | The 17 of those that are Basic |
| `stage1_toolbox.csv` | Dual-type Stage 1 and Mega Evolution cards, plus the single-type Stage 1 cards in the decks |
| `type_coverage_matrix.csv` | Smallest dual-type sets that cover the nine types other than Dragon and Colorless |
| `weakness_coverage_matrix.csv` | Deck attackers against the common weakness chart |
| `energy_compatibility_matrix.csv` | Whether one copy of each special Energy pays each attack |
| `decklists.csv` | Decks A, B, and C |
| `deck_standard.csv` | A Standard list. It is not one of the goldfish runs |
| `coverage_summary.json` | Counts from the dual-type scan |
| `simulation_results.json` | 100,000 goldfish games per deck and seat |
| `../../kecleon_ditto_rainbow.py` | Rules model and goldfish |
| `../build_kecleon_ditto_databases.py` | Rebuilds the CSVs from a local card dump at `/tmp/tcg` |

The snapshot is 177 English expansions through Delta Reign (released 6 November 2026). A dual-type row is a Pokémon card whose data has two or more printed types. Delta Species on its own is not enough: a δ card with one type is not in the database.

## Kecleon and Colorful Whip

The attack is on Kecleon from Delta Reign, a Basic Colorless Pokémon with 90 HP, Fighting weakness ×2, and a Retreat Cost of two Colorless. Regulation mark J. The common copy is 83/103. The illustration rare is 117/103 and has the same text.

Colorful Whip costs two Colorless and does 30×. The printed sentence is:

> Reveal any number of Pokémon from your hand, and this attack does 30 damage for each different type of Pokémon you revealed in this way.

"Any number" on an attack includes zero, so the attack can be used for no damage. Revealing an extra Pokémon cannot lower the count, so the damage ceiling is the number of different types among every Pokémon in hand. The Kecleon that is attacking is in play, not in hand, and does not count unless a second Kecleon, or another Colorless Pokémon, is in hand.

One Double Colorless Energy pays the attack. In Standard there is no Double Colorless Energy with a current regulation mark. Ignition Energy provides three Colorless only while attached to an Evolution Pokémon, and it is discarded at the end of the turn, so it does not stick on Kecleon. A Standard Kecleon needs two attachments.

### How a dual-type card is counted

The current rulebook's dual-type appendix says a dual-type Pokémon is both types at the same time, and that weakness applies if the defender is weak to either type. The same construction, "different types of Pokémon," is what older attacks use when they count Grass, Fire, and the rest, rather than species names. The rulings compendium's answer on Toxtricity's Loud Mix is the same idea: the attack counts types, and a Pokémon that is more than one type counts as each of those types.

No Colorful Whip question-and-answer was in the sources retrieved for this note. Delta Reign had been out for a week on 13 November 2026. The model therefore follows the rulebook and the Loud Mix ruling: Volcarona (Fire and Grass) plus Azumarill (Fairy and Water) is four types and 120 damage. Two Fire Pokémon are one type.

There are 11 types on physical cards: Grass, Fire, Water, Lightning, Psychic, Fighting, Darkness, Metal, Fairy, Dragon, and Colorless. Eleven different types is 330 damage. That is the printed ceiling. It is not a target the deck should chase with every hand.

## Dual-type census

The snapshot has 106 dual-type Pokémon printings and 86 distinct names. None of them is Dragon. Dragon Frontiers was checked on its own and also has none. A Dragon card in hand has to be a single-type Dragon. Druddigon from White Flare, 71/86, is the one these lists use: Basic, 120 HP, Dragon, regulation I, with Shred for one Colorless and 40 damage that is not affected by effects on the defending Pokémon.

| Set | Dual-type printings |
| --- | ---: |
| Team Rocket Returns | 24 |
| Delta Species | 22 |
| Team Magma vs Team Aqua | 13 |
| Steam Siege | 12 |
| Holon Phantoms | 10 |
| HS—Unleashed | 6 |
| HS—Undaunted | 4 |
| HS—Triumphant | 4 |
| Hidden Legends | 3 |
| Crystal Guardians | 3 |
| 30th Celebration: Classic Collection | 3 |
| Celebrations: Classic Collection | 1 |
| XY Black Star Promos | 1 |

By stage: 46 Stage 1, 23 Stage 2, 17 Basic, 16 LEGEND halves (eight pairs, each pair stored as two cards), and 4 Mega Evolution Pokémon-EX. Team Magma vs Team Aqua and Team Rocket Returns pair the second type with Darkness. Most Delta Species, Holon Phantoms, and Crystal Guardians dual-types pair the second type with Metal. Steam Siege is the set that still matters in Expanded, because it is Black & White-onward and it has Fairy.

The 17 Basics are in `basic_dual_type_pokemon.csv`. Four of the printings are Volcanion-EX. The others are single-prize Basics such as Team Aqua's Kyogre, Team Magma's Groudon, Latias δ, and Jirachi. A Basic dual-type can sit in the opening hand and can be the Active Pokémon. It cannot be the card placed onto Ditto ◇, because Almighty Evolution asks for a Stage 1.

## Covering the types

Dragon and Colorless never appear on a dual-type card, so they each need their own card in hand. The other nine types have ten type-slots on five dual-type cards, which is enough for every one of those nine types with a single repeated type.

Several different five-card sets do that. The search in `type_coverage_matrix.csv` keeps one of them. Deck A uses this Stage 1 set, which also has exactly one repeated type:

| Card | Set | Types |
| --- | --- | --- |
| Volcarona | Steam Siege 15/114 | Fire, Grass |
| Azumarill | Steam Siege 77/114 | Fairy, Water |
| Marowak δ | Delta Species 10/113 | Fighting, Metal |
| Dark Magneton | Team Rocket Returns 39/109 | Lightning, Darkness |
| Dark Hypno | Team Rocket Returns 6/109 | Psychic, Darkness |

Darkness is the repeated type. Add Druddigon and a Kecleon in hand and the reveal is all 11 types: 330 damage. That package is seven Pokémon in hand. It is a ceiling, not the opening plan. Marowak δ, Dark Magneton, and Dark Hypno are EX-era cards, so this package is Unlimited only.

Expanded does not have a five-card set of playable Basics and Stage 1s, with no Rule Box, that covers those nine types. The Steam Siege cards that are actually playable as hand fuel are Volcarona, Azumarill, Galvantula (Lightning and Grass), and Bisharp (Darkness and Metal). They cover seven types. Psychic and Fighting are filled by single-type Stage 1s: Banette and Marowak. Shiftry is a Stage 2 Grass/Darkness card and only a Dawn target. Fairy still exists in Expanded because Azumarill is from Steam Siege.

Standard has no Fairy Pokémon with regulation mark H, I, or J. The scanned Fairy cards stop before those marks. The Standard ceiling is 10 types and 300 damage, and only if Dragon and Colorless are also in hand.

## Ditto ◇

Ditto ◇ is Lost Thunder 154/214. It is a Basic Colorless Prism Star with 40 HP, Fighting weakness, and one Colorless retreat. The Prism Star rule is printed on the card: only one copy of that name in the deck, and if the card would go to the discard pile it goes to the Lost Zone instead.

Almighty Evolution:

> Once during your turn (before your attack), you may put any Stage 1 card from your hand onto this Pokémon to evolve it. You can't use this Ability during your first turn or the turn this Pokémon was put into play.

The compendium answers used here are the two on Almighty Evolution: a Stage 1 placed this way can later evolve into its own Stage 2, and a different Stage 1 cannot be stacked on top unless Ditto ◇ is devolved first. The Ability is optional. It is an Ability, so an effect that turns Abilities off, including Path to the Peak while Ditto ◇ itself is in play, stops it.

"Any Stage 1 card" does not ask for a matching name. Aerodactyl from 151, which evolves from Antique Old Amber, can be placed onto Ditto ◇. A Stage 1 Pokémon ex can too. A Stage 2 cannot. Evosoda and similar "evolves from" searches do not find a Stage 1 for Ditto ◇, because those cards look at the name of the Pokémon in play. The Stage 1 has to be in hand. Dawn, Hilda, and Hyper Aroma are how it gets there.

An older Mega Evolution Pokémon-EX ends the turn when it evolves. Do not put M Steelix-EX or M Gardevoir-EX onto Ditto ◇ if the point is to attack that turn.

## Stage 1 toolbox and weakness

Weakness is ×2, applied to the attack's damage when the attacking Pokémon is either of the types the defender is weak to. The chart in `weakness_coverage_matrix.csv` is the common chart used since Sword & Shield. It is a comparison tool. Older cards, and Dragon cards from before Fairy, do not all use it. Kecleon is Colorless, so Colorful Whip is not doubled by the defender's weakness to some other type. Kecleon's own weakness is Fighting.

The attacks worth building around are the ones one attachment can pay:

| Pokémon | Attack used | Cost | Base | What it is for |
| --- | --- | --- | --- | --- |
| Azumarill | Play Rough | CC | 30+ | Fairy and Water in one card. Coin flip for +30. |
| Bisharp | Retaliate | C | 30+ | +60 if an attack KO'd a friendly Pokémon last turn. Mach Claw is Darkness plus Colorless for 60 and ignores Resistance. |
| Galvantula | Double Thread | C | 30 to two Pokémon | Spread. Weakness applies to the Bench as well. It is not a one-shot attacker. |
| Volcarona | Power Hurricane | CCC | 120 | Discards all Energy from Volcarona. Triple Acceleration Energy or Ignition Energy is the clean way to pay it, because those cards leave at the end of the turn anyway. |
| Banette | Puppet Pull | Psychic | 80 | Searches any card. Needs a Psychic Energy. Double Colorless does not pay it. |
| Marowak | Bone Vengeance | CC | 60+ | The +120 needs a damaged Cubone on the Bench. These lists do not play Cubone, so plan on 60. |
| Seaking | Rapid Draw | C | 60 | Draws 2. Festival Lead does nothing without Festival Grounds. |
| Aerodactyl | Devolution Ray | CC | 100 | Devolves the defending Evolution. Legal on Ditto ◇. Regulation G, so Expanded, not Standard. |
| Druddigon | Shred | C | 40 | Does not need Ditto ◇. The Dragon type if the other copy stays in hand. |
| Marowak δ | Metal Crusher | Fighting CC | 50 | 90 if the defender is Metal. One Double Colorless Energy does not pay the Fighting. Keep it in hand in Deck A. |
| Dark Magneton | Magnetic Lines | Lightning C | 20 | A Lightning/Darkness card for the hand, not a knockout attack. |
| Dark Hypno | Dark Link | C | — | Copies another Dark attack. The card is Psychic/Darkness hand fuel. It has 70 HP. |

## Rescue Scarf

Rescue Scarf is Dragons Exalted 115/124, a Pokémon Tool.

> If the Pokémon this card is attached to is Knocked Out by damage from an attack, put that Pokémon into your hand. (Discard all cards attached to that Pokémon.)

The Japanese reprint says the same thing more tightly: the Pokémon is returned to the hand instead of being discarded, and every card other than a Pokémon card is discarded.

What follows from that sentence and from the compendium entries for this card:

1. The Knock Out has to be damage from an attack. Poison between turns, damage counters from an Ability, and an effect that Knocks a Pokémon Out without attack damage do not use the Tool.
2. The English sentence does not say the attack has to be the opponent's. Damage from an attack is the printed condition.
3. An evolved Pokémon sends every Pokémon card in the stack to hand, not only the top card. Compendium entry 1151.
4. A Prism Star that would be discarded goes to the Lost Zone. Rescue Scarf sends the Pokémon cards to hand, so they are not discarded. The compendium's Volcanion Prism Star answer is that the Prism Star returns to hand. The same routing is what this deck relies on for Ditto ◇. Entry 1150.
5. Energy and Tools on that Pokémon are discarded, including the Scarf. The Energy investment is not preserved. Night Stretcher can pick up a Pokémon or a Basic Energy afterward. It cannot pick up Double Colorless Energy, Counter Energy, or the Scarf.
6. Another recovery card can be played later. Rescue Stretcher takes a Pokémon from the discard, which is where a Stage 1 goes when the Scarf was not attached or the Knock Out was not from an attack. It cannot take a Prism Star out of the Lost Zone.

Three copies are in each goldfish list. The scripted Knock Out hits whichever Pokémon just attacked. Kecleon is that Pokémon in most games, so the pilot puts the first Scarf on Kecleon and the next one on Ditto ◇. A Scarf on a benched Ditto ◇ does not trigger while Kecleon is the one being Knocked Out. A Scarf on Kecleon returns Kecleon to hand, where it counts as Colorless for the next Colorful Whip. A Scarf on an evolved Ditto ◇ returns both the Stage 1 and Ditto ◇. The Tool does not belong on a disposable Basic.

The goldfish does not measure how often real opponents Knock Out with poison. It is given an input: 80 percent of the scripted Knock Outs are attack damage. The recovery rates below are the result of that input plus the draw and attach rules, not a survey of tournament games.

## Energy

| Energy | Printing used | What one card provides here | Legal where |
| --- | --- | --- | --- |
| Double Colorless Energy | Fates Collide 114/124 | Two Colorless. Pays Colorful Whip by itself. | Expanded and Unlimited. No H/I/J printing in the snapshot, so not Standard. |
| Counter Energy | Crimson Invasion 100/111 | One Colorless. Two of any type if you have more Prize cards left than your opponent and the Pokémon is not a Pokémon-GX or Pokémon-EX. | Expanded and Unlimited. |
| Reversal Energy | Paldea Evolved 192/193 | One Colorless. Three of any type if you are behind on Prizes and it is attached to an Evolution Pokémon that does not have a Rule Box. Regulation G. | Expanded and Unlimited. Not Standard after the 2026 rotation. |
| Triple Acceleration Energy | Unbroken Bonds 190/214 | Three Colorless on an Evolution, and only then. Discarded at the end of the turn. Cannot be attached to Kecleon. | Expanded and Unlimited. |
| Ignition Energy | White Flare 86/86 | Three Colorless on an Evolution, one Colorless on a Basic. Discarded at the end of the turn. Regulation I. | Standard, Expanded, and Unlimited. |
| Basic Energy | any printing | One of its type. Two of them pay Colorful Whip. | Every format. |

Counter Energy does not mention a Rule Box. On the printed text, Ditto ◇ and a non-GX, non-EX Stage 1 on top of it still get the two-Energy bonus while you are behind. Reversal Energy does mention a Rule Box. Ditto ◇ has one. This model treats the evolved Pokémon as still having that Rule Box, so Reversal Energy stays at one Colorless. That is the conservative reading. The sources retrieved for this note do not include a TPCi answer that says it in those words. Reversal Energy is left out of the lists for that reason. Counter Energy, Double Colorless Energy, and Triple Acceleration Energy are the shared engine. Banette is the attack that still wants a Basic Psychic Energy.

The full pay/fail table is `energy_compatibility_matrix.csv`.

## Trainers

Dawn, Phantasmal Flames 87/94, regulation I, is a Supporter, not an ACE SPEC:

> Search your deck for a Basic Pokémon, a Stage 1 Pokémon, and a Stage 2 Pokémon, reveal them, and put them into your hand. Then, shuffle your deck.

The sentence does not say "up to." The goldfish takes one of each when the deck has them. Shiftry is the only Stage 2 in Decks A, B, and C, so Dawn is also the way Shiftry enters hand as a Grass/Darkness card. There is no Nuzleaf, so Shiftry is not evolved.

Hilda, White Flare 84/86, regulation I:

> Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck.

Hyper Aroma, Twilight Masquerade 152/167, regulation H, is the Stage 1 ACE SPEC:

> Search your deck for up to 3 Stage 1 Pokémon, reveal them, and put them into your hand. Then, shuffle your deck.

"Up to" means the player may stop at one or two. One ACE SPEC per deck, so the lists play one copy.

The rest of the engine in Decks A–C is Ultra Ball (any Pokémon, discard two other cards), Nest Ball (a Basic to the Bench), Buddy-Buddy Poffin (up to two Basics with 70 HP or less; Ditto ◇ has 40 HP and Kecleon has 90, so Poffin finds Ditto ◇ and not Kecleon), Rescue Scarf, Night Stretcher, Rescue Stretcher, Switch, and Boss's Orders. Deck C also plays Professor's Research. Research discards the hand. The pilot uses it only when the hand is showing two or fewer types, because a large hand is the damage resource.

Nest Ball's printings in the snapshot are regulation G or unmarked. Professor's Research is the same. Both are Expanded-legal and are not Standard-legal under the 2026 H/I/J rotation. The Standard list replaces them with Ultra Ball, Night Stretcher, and Judge.

## Hand, Bench, and the Scarf

Keep one Pokémon of a missing type in hand. Play the spare copy. The practical order:

- Ditto ◇ goes to the Bench as soon as it is found. It does not attack, and it has to wait a turn before Almighty Evolution.
- One Kecleon becomes the Active attacker when it can. A second Kecleon stays in hand so Colorless is part of the reveal. A third copy may Bench as a spare body.
- One Druddigon stays in hand. The other may Bench if both are drawn. A single Druddigon is not Benched, because there is no other Dragon.
- A Stage 1 stays in hand until Ditto ◇ can evolve and the attack is payable without giving away the last copy of a type. If Colorful Whip is already at 180 or more, the pilot does not spend a unique type on a smaller attack.
- After a Scarf Knock Out, Kecleon is in hand again and counts on the next reveal. Ditto ◇ is in hand again and has to be played, then it has to wait a turn before it evolves.
- Switch is the pivot. Retreating Kecleon would discard the Double Colorless Energy that is paying Colorful Whip.

The failure mode is a hand full of types and an empty Bench, or a Bench full of types and a Whip for 30. Rescue Scarf is the card that moves a body back to the hand without a Supporter. Professor Turo's Scenario does that too, and its printing is regulation G, so it is not in the Standard list.

## Deck A — Rainbow Kecleon

Unlimited. The five-card Stage 1 package above, plus the Dragon and the Colorless, with a few extra Stage 1s so Dawn and Hyper Aroma have more than one target.

Pokémon, 20

| Count | Card | Number |
| ---: | --- | --- |
| 4 | Kecleon | Delta Reign 83/103 |
| 1 | Ditto ◇ | Lost Thunder 154/214 |
| 2 | Volcarona | Steam Siege 15/114 |
| 2 | Azumarill | Steam Siege 77/114 |
| 2 | Marowak δ | Delta Species 10/113 |
| 2 | Dark Magneton | Team Rocket Returns 39/109 |
| 2 | Dark Hypno | Team Rocket Returns 6/109 |
| 2 | Druddigon | White Flare 71/86 |
| 1 | Galvantula | Steam Siege 42/114 |
| 1 | Bisharp | Steam Siege 64/114 |
| 1 | Shiftry | Steam Siege 11/114 |

Trainers, 28: 4 Dawn, 3 Hilda, 1 Hyper Aroma, 4 Ultra Ball, 3 Nest Ball, 2 Buddy-Buddy Poffin, 3 Rescue Scarf, 2 Night Stretcher, 2 Rescue Stretcher, 2 Switch, 2 Boss's Orders.

Energy, 12: 4 Double Colorless Energy, 4 Counter Energy, 2 Triple Acceleration Energy, 2 Fighting Energy.

Open on Kecleon if it is in the first hand, Bench Ditto ◇, and leave the Dragon and the last copy of each dual-type in hand. Attach Double Colorless Energy to Kecleon. Use Triple Acceleration Energy only under an evolved Ditto ◇ that needs three Colorless, which is Volcarona. The first Rescue Scarf goes on Kecleon.

The risk is the EX-era cards. They are real attackers only in a narrow case, and they are not Expanded-legal. The deck is the 330-damage build.

## Deck B — Kecleon + Ditto ◇ hybrid

The Expanded version of the same idea. Psychic and Fighting are Banette and Marowak. Fairy remains Azumarill. Reversal Energy is still omitted.

Pokémon, 20

| Count | Card | Number |
| ---: | --- | --- |
| 4 | Kecleon | Delta Reign 83/103 |
| 1 | Ditto ◇ | Lost Thunder 154/214 |
| 2 | Azumarill | Steam Siege 77/114 |
| 2 | Galvantula | Steam Siege 42/114 |
| 2 | Bisharp | Steam Siege 64/114 |
| 2 | Volcarona | Steam Siege 15/114 |
| 2 | Marowak | Stellar Crown 73/142 |
| 2 | Banette | Pitch Black 34/84 |
| 2 | Druddigon | White Flare 71/86 |
| 1 | Shiftry | Steam Siege 11/114 |

Trainers, 28, and Energy, 12, match Deck A except the Basic Energy is Psychic Energy, Crown Zenith 156/159, for Puppet Pull.

This is the list to play in Expanded once Kecleon is legal. Banette is the search attack. Bisharp is the attack that gets larger after a Knock Out. Volcarona is the 120. Kecleon is still the card that goes to 180 and beyond when the hand cooperates.

## Deck C — Adaptive toolbox

Less of the Whip package, more attackers that function on one Colorless.

Pokémon, 17

| Count | Card | Number |
| ---: | --- | --- |
| 3 | Kecleon | Delta Reign 83/103 |
| 1 | Ditto ◇ | Lost Thunder 154/214 |
| 2 | Bisharp | Steam Siege 64/114 |
| 2 | Galvantula | Steam Siege 42/114 |
| 2 | Seaking | Prismatic Evolutions 21/131 |
| 2 | Banette | Pitch Black 34/84 |
| 2 | Druddigon | White Flare 71/86 |
| 1 | Marowak | Stellar Crown 73/142 |
| 1 | Aerodactyl | 151 142/165 |
| 1 | Shiftry | Steam Siege 11/114 |

Trainers, 31: the Deck B trainer line, plus a third Night Stretcher and 2 Professor's Research (Paldean Fates 87/91).

Energy, 12: 4 Double Colorless Energy, 4 Counter Energy, 2 Triple Acceleration Energy, 2 Psychic Energy.

Use this when the game is about devolving, drawing, or copying a search, and a 240-damage Whip is less important than having an attack every turn. It is still an Expanded list, not a Standard list. Aerodactyl is regulation G.

## Goldfish

`kecleon_ditto_rainbow.py` plays 100,000 games of each deck going first and 100,000 going second. Seed 20261113. It is a goldfish. There is no opposing deck. A scripted defender has one type, chosen uniformly from the 11 types and known from our second turn. The common weakness chart is used only for the toolbox comparison.

Other rules the program actually applies:

- Mulligan until a Basic is in the opening 7. Six Prizes. A draw at the start of every turn, including the first.
- The first player does not attack or play a Supporter on their first turn. Almighty Evolution is refused on the player's first turn and on the turn Ditto ◇ was played, for either seat.
- Searches take a card when that category is in the deck and the pilot wants it. Dawn and Hilda take the Stage 1 even when it does not add a new type, because those cards do not say "up to."
- Colorful Whip counts every printed type in hand, and a dual-type card contributes both.
- Triple Acceleration Energy and Ignition Energy are discarded at the end of the turn.
- Power Hurricane discards Volcarona's Energy.
- The opponent Knocks Out the Active Pokémon at the start of our next turn if it attacked. Eighty percent of those Knock Outs are attack damage. A prize is taken for 110 or more damage. One prize, not two: these attackers are not Rule Box attackers. Being "behind" for Counter Energy is having more Prize cards remaining than the opponent.
- The pilot will not evolve Ditto ◇ into an attack it cannot pay, and it will not spend the last copy of a type while Colorful Whip is already at 180 or more.

The measured rates are in `simulation_results.json`. They are not match win rates.

### Results, 100,000 games each

Going second is the seat that attacks first. Rates are the share of games in which the event happened at least once, except the rows marked as averages.

| | Deck A rainbow | Deck B hybrid | Deck C toolbox |
| --- | ---: | ---: | ---: |
| At least one mulligan | 40.2% | 40.0% | 45.8% |
| Kecleon in the opening 7 | 66.3% | 66.4% | 58.0% |
| Kecleon seen by turn 3 | 97.1% | 96.9% | 96.3% |
| Kecleon attacks | 78.3% | 78.3% | 77.3% |
| Average Colorful Whip damage | 204 | 189 | 166 |
| Average types on that attack | 6.8 | 6.3 | 5.5 |
| Whip reaches 180 at least once | 59.5% | 54.4% | 46.4% |
| 240 | 36.4% | 30.0% | 17.5% |
| 270 | 25.3% | 18.9% | 5.9% |
| 300 | 14.7% | 9.6% | 0% |
| 330 | 5.5% | 3.0% | 0% |
| Ditto ◇ in the opening 7 | 19.4% | 19.3% | 21.5% |
| Ditto ◇ seen by search or draw | 79.9% | 80.1% | 82.7% |
| Ditto ◇ evolves | 72.6% | 76.8% | 80.2% |
| The evolution attacks | 28.7% | 27.9% | 28.3% |
| Both engines attack in one game | 26.4% | 25.7% | 26.3% |
| A weakness attack lands | 10.9% | 11.4% | 7.8% |
| Rescue Scarf in the opening 7 | 29.0% | 29.1% | 28.9% |
| Scarf attached to Kecleon | 55.7% | 55.4% | 57.9% |
| Scarf attached to Ditto ◇ | 15.8% | 15.7% | 18.4% |
| Kecleon returned to hand | 24.0% | 24.0% | 25.6% |
| Ditto ◇ returned to hand | 3.5% | 3.4% | 4.0% |
| Ditto ◇ sent to the Lost Zone | 23.3% | 22.9% | 22.3% |
| Extra attacks after a Scarf return | 0.10 | 0.10 | 0.12 |
| Some attacker used | 80.6% | 80.5% | 79.3% |
| Average turn of the first attack | 3.66 | 3.63 | 3.94 |
| Game lost inside 12 turns | 29.7% | 30.3% | 27.1% |

Going first does not change the shape. The first attack moves from about turn 3.6 to about turn 4.1, because that player cannot attack on turn 1. Rainbow's average Whip goes from 204 to 200. Hybrid's goes from 189 to 185. Ditto ◇ evolves a little more often, because the extra setup turn is legal for Almighty Evolution. The 330 rate stays 5.3% for rainbow and 3.1% for hybrid.

What those numbers mean:

- The lists find Kecleon. Four copies plus Dawn, Nest Ball, and Ultra Ball put it in reach by turn 3 in about 97% of games, and it attacks in about 78%.
- A Whip hit is usually six or seven types, around 180–210, not 330. The ceiling shows up in a minority of games. Deck C never reaches 300, because that list does not carry the Fairy pair and the compact nine-type package.
- Ditto ◇ evolves in roughly three games out of four and attacks in fewer than one in three. The pilot refuses to spend the last copy of a type once Whip is already at 180. That is the hand-versus-board tradeoff, measured.
- The mulligan rate is the consistency cost. Decks A and B have seven Basics. About 40% of games mulligan at least once, and the opponent may draw for each one. Deck C has six Basics and mulligans in 46% of games.
- Rescue Scarf on Kecleon returns Kecleon in about 24% of games. Ditto ◇ still goes to the Lost Zone in about 23%, because the first Scarf is on the attacker and a second Scarf reaches Ditto ◇ in only about 16% of games. The return adds about a tenth of an attack per game under this KO clock. It keeps the one Colorless attacker in the list. It does not turn one attack into two on a regular basis.
- A weakness attack is about 11% of hybrid games. The toolbox is a second plan, not the plan that shows up every game.
- The empty-hand count stays low on Decks A and B (about 0.10 turns per game). The types are usually still in hand when Whip is used.

## Format legality

Checked against the 9 January 2026 Play! Pokémon rotation announcement and the Tournament Handbook section on reprinted cards. Standard is regulation marks H, I, and J. G rotated out on 10 April 2026 for in-person events. Expanded is Black & White onward, using the same reprint rule: an older printing is legal when a printing with the same name and functionally identical text is legal. Unlimited has no ban list. New sets become legal on the second Friday after the US release.

Delta Reign's US release in this snapshot is 6 November 2026, a Friday. The second Friday after that is 20 November 2026. On 13 November 2026, Kecleon from Delta Reign is not yet legal in a sanctioned event. Every list in this note includes it.

| Card | Standard | Expanded | Unlimited |
| --- | --- | --- | --- |
| Kecleon, Delta Reign | Legal from 20 November 2026 | Same | Yes |
| Druddigon, Banette, Dawn, Hilda, Ultra Ball, Switch, Boss's Orders, Ignition Energy | Yes, once their own sets are legal | Yes | Yes |
| Hyper Aroma, Buddy-Buddy Poffin, Night Stretcher, Seaking, Marowak (Stellar Crown), Boltund, Forretress | Yes, marks H or I | Yes | Yes |
| Judge, Perfect Order | Yes, mark J | Yes | Yes |
| Nest Ball, Professor's Research, Reversal Energy, Aerodactyl (151) | No current mark | Yes | Yes |
| Ditto ◇, Rescue Scarf, Double Colorless Energy, Counter Energy, Triple Acceleration Energy, Steam Siege dual-types | No | Yes | Yes |
| Marowak δ, Dark Magneton, Dark Hypno, and the other EX-era dual-types | No | No | Yes |
| Fairy Pokémon | No H/I/J card exists | Azumarill and other Expanded Fairy cards | Yes |

The Expanded ban list published by Play! Pokémon does not name Kecleon, Ditto ◇, Rescue Scarf, Double Colorless Energy, Counter Energy, Triple Acceleration Energy, or the Steam Siege attackers in these lists. It does ban two Unown from the same Lost Thunder set as Ditto ◇ (90/214 and 91/214), and it bans Flapple, so those are not substitutes for a Dragon or a Grass card. Recheck the list before an event. Prism Star is a one-per-name rule, not a format ban. ACE SPEC is one per deck. Both restrictions are already how the lists are built.

## Standard list

This list is not in the 100,000-game run. It is the same Whip idea inside H/I/J, without Ditto ◇ and without Rescue Scarf, because those cards are not Standard. Ten types are available. Fairy is the one that is missing, so 300 is the ceiling.

Pokémon, 20: 4 Kecleon, 2 Druddigon, 2 Simisear (White Flare 15/86), 2 Vespiquen (Delta Reign 7/103), 2 Seaking, 2 Boltund (Temporal Forces 59/162), 2 Banette, 2 Marowak, 1 Ariados (Delta Reign 59/103), 1 Forretress (Temporal Forces 110/162).

Trainers, 25: 4 Dawn, 4 Hilda, 1 Hyper Aroma, 4 Ultra Ball, 4 Night Stretcher, 3 Switch, 3 Boss's Orders, 2 Judge (Perfect Order 76/88).

Energy, 15: 4 Ignition Energy, 6 Psychic Energy, 5 Metal Energy. The Psychic Energy pays Banette and, as Colorless, pays Kecleon. Ignition Energy is for an Evolution that needs three Colorless, not for Kecleon.

The full row-by-row list is `deck_standard.csv`. Judge shuffles the type hand away, so it is a two-of for a hand that is already empty of Pokémon.

## Recommended list

Deck B is the list to build. Going second, its average Colorful Whip is 189 against Deck A's 204, and it still reaches 180 in 54% of games against Deck A's 59%. It gives up about two points of the 330 rate (3.0% against 5.5%) and it stays inside Expanded once Kecleon is legal. Deck A is the Unlimited ceiling. Deck C never reaches 300 in the goldfish, because it does not carry the compact type package. The Standard list is a different deck: no Ditto ◇, no Scarf, and no Fairy, so its ceiling is 300.

Play Deck B as written. Put the first Rescue Scarf on the Kecleon that is attacking. Put the next one on Ditto ◇. Do not add Reversal Energy unless a ruling is published that a Stage 1 on Ditto ◇ does not have a Rule Box.

## Sources

Card text for Kecleon was checked against the Pokémon TCG card database:

- [Kecleon, Delta Reign 83/103](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/me06/83)
- [Kecleon, Delta Reign 117/103](https://www.pokemon.com/us/pokemon-tcg/pokemon-cards/series/me06/117)

The other printed attacks, Abilities, and Trainer text in this note were read from the physical-card JSON snapshot (set files through `me6`, Delta Reign). The same sentences for the cards below are also published at:

- [Ditto ◇, Lost Thunder 154](https://bulbapedia.bulbagarden.net/wiki/Ditto_%E2%99%A2_(Lost_Thunder_154)), including Almighty Evolution and the Prism Star rule
- [Reversal Energy, Paldea Evolved 192](https://bulbapedia.bulbagarden.net/wiki/Reversal_Energy_(Paldea_Evolved_192))
- [Rescue Scarf, Japanese reprint](https://www.pokemon-card.com/card-search/details.php/card/27969/regu/DP), which states that non-Pokémon cards are discarded and the Pokémon returns to hand

Rules and rulings:

- [2026 Standard rotation announcement, 9 January 2026](https://www.pokemon.com/us/news/2026-pokemon-tcg-standard-format-rotation-announcement). G leaves Standard. H, I, and J stay. Expanded stays Black & White onward. In-person rotation date 10 April 2026.
- [Play! Pokémon TCG Tournament Handbook](https://www.pokemon.com/static-assets/content-assets/cms2/pdf/play-pokemon/rules/play-pokemon-tcg-tournament-handbook-en.pdf), sections 4.1 through 4.2. Reprint rule, Expanded set list, and the Unlimited ban note.
- [Pokémon TCG banned card list](https://www.pokemon.com/us/play-pokemon/about/pokemon-tcg-banned-card-list). Expanded bans checked against the list retrieved on 13 November 2026. Unlimited has no banned cards.
- [Pokémon TCG rules resources](https://play.pokemon.com/en-us/resources/rules/)
- Delta Reign rulebook PDF, appendix on dual-type Pokémon and the section on "up to" versus "any number": [dlr_rulebook_en.pdf](https://media.pocketmonsters.net/pdf/TCG/dlr_rulebook_en.pdf)
- [Rescue Scarf rulings](https://compendium.pokegym.net/category/5-trainers/rescue-scarf/), including [the evolved-stack answer](https://compendium.pokegym.net/ruling/1151/) and [the Volcanion Prism Star answer](https://compendium.pokegym.net/ruling/1150/)
- [Almighty Evolution rulings](https://compendium.pokegym.net/category/4-abilities/almighty-evolution/)
- [Rule Box ruling of 18 March 2021](https://compendium.pokegym.net/ruling/1508/). Prism Star is a Rule Box. Original EX-era Pokémon-ex are not.
- [Double Type / Loud Mix ruling](https://compendium.pokegym.net/category/4-abilities/double-type/). A multi-type Pokémon counts as each of its types when an attack counts types.

The goldfish assumptions that are not printed rules are listed in `ASSUMPTIONS` inside `kecleon_ditto_rainbow.py` and in `simulation_results.json`.
