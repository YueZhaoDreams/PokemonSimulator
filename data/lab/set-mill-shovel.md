# Mill, Cursed Shovel

Each step replaces one copy of one other card with one Cursed Shovel. The cut with the higher win rate under the 0-copy loss weights is kept. The next copy is measured on that list, through four copies, including when a copy lowers the rate. The kept count is the one whose gain over the starting list is the largest.

Printed sentence: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck."

The starting 60 is the locked Wiglett Mill, zero Cursed Shovel. Mill's picker already plays a Pokémon Tool when a Pokémon in play has an empty tool slot. It attaches that tool to the Active Pokémon when that slot is empty, otherwise to the first benched Pokémon without a tool. This search does not add a strategy branch. Cursed Shovel is an Item, so playing it does not use the Supporter for the turn.

- **Seed**: `20261118`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from this starting list's own losses. A foe it loses more often counts more.
- **Elapsed**: 13958.0s
- **Streams**: each cell starts with `random.Random(20261118)`. Two lists diverge after the first choice that consumes a different number of draws.

The weight of a foe is `max(1e-6, 1 - win rate)` divided by the sum of those values. The script divides. The Sisters weights in `data/lab/set-mill-sleep.md` are not this vector.

The active set is the weight prefix that first reaches 90%. Its cumulative weight is 92.06%. Later cells are played only against that set. A parked foe keeps its 0-copy win rate and its weight. It is not played again.

## 0-copy pass

Every live 60-card deck that is not archived. Card count is the registry length. Mega Starmie and Iron Thorns are included while they are not seed keys.

| Key | Deck | Cards | Strategy | A | B | Mean | Weight |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: | ---: |
| d60 | Set D Standard 60 (Charm Ogerpon) | 60 | demolish | 16.25% | 14.00% | 15.12% | 15.1090% (active) |
| m60 | Set M Standard 60 (Mew ex / Spiky Energy) | 60 | mew_baby | 30.50% | 31.75% | 31.13% | 12.2608% (active) |
| starmie | Mega Starmie ex (Kudo) | 60 | starmie | 34.50% | 35.75% | 35.12% | 11.5487% (active) |
| mill | Mill | 60 | mill | 50.25% | 49.75% | 50.00% | 8.9008% (active) |
| g | Carpet Set G (Clefairy / Ledian 60) | 60 | g | 51.00% | 51.25% | 51.12% | 8.7005% (active) |
| c60 | Set C Standard 60 (Clefairy / Mewtwo) | 60 | party | 50.75% | 56.00% | 53.37% | 8.3000% (active) |
| celebi | Celebi Mill | 60 | roast | 72.50% | 66.75% | 69.62% | 5.4072% (active) |
| two-forest | 二森林 | 60 | roast | 70.00% | 72.00% | 71.00% | 5.1624% (active) |
| t-meta | Worlds 2026 Hedrick Dragapult | 60 | phantom | 71.25% | 76.00% | 73.62% | 4.6951% (active) |
| h | Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | 60 | nuzzle | 77.50% | 75.25% | 76.38% | 4.2056% (active) |
| s60 | Set S Standard 60 (Floragato hunter) | 60 | slash | 76.50% | 79.00% | 77.75% | 3.9608% (active) |
| t60 | Set T Standard 60 (Dragapult ex) | 60 | phantom | 78.25% | 79.00% | 78.62% | 3.8051% (active) |
| t-unl | Unlimited Dragapult (Pidgeot / Rotom V) | 60 | phantom | 85.75% | 82.75% | 84.25% | 2.8037% (parked) |
| l60 | Chris Brewer Lucario Hariyama | 60 | aura | 84.25% | 86.50% | 85.38% | 2.6035% (parked) |
| thorns | Iron Thorns ex | 60 | thorns | 95.25% | 93.00% | 94.12% | 1.0458% (parked) |
| doll | Doll | 60 | doll | 95.75% | 95.50% | 95.62% | 0.7788% (parked) |
| g30 | Unlimited 60 (Ambipom Hand Fling) | 60 | celebration | 95.25% | 96.75% | 96.00% | 0.7121% (parked) |

Active set (92.06%): d60, m60, starmie, mill, g, c60, celebi, two-forest, t-meta, h, s60, t60.

Parked foes stay at the 0-copy rates below.

| Key | Deck | Weight | A | B | Mean |
| :--- | :--- | ---: | ---: | ---: | ---: |
| doll | Doll | 0.7788% | 95.75% | 95.50% | 95.62% |
| g30 | Unlimited 60 (Ambipom Hand Fling) | 0.7121% | 95.25% | 96.75% | 96.00% |
| l60 | Chris Brewer Lucario Hariyama | 2.6035% | 84.25% | 86.50% | 85.38% |
| t-unl | Unlimited Dragapult (Pidgeot / Rotom V) | 2.8037% | 85.75% | 82.75% | 84.25% |
| thorns | Iron Thorns ex | 1.0458% | 95.25% | 93.00% | 94.12% |

## Archived, no row

- Carpet Set A (Dondozo / Staraptor) (`a`, 30 cards)
- Carpet Set B (Walrein / Pikachu shock) (`b`, 30 cards)
- Set C (Clefairy / Mewtwo) (`c`, 30 cards)
- Set D (Charm Ogerpon) (`d`, 30 cards)
- Carpet Set E (Walrein / Iris) (`e`, 30 cards)
- Carpet Set F (Staraptor / Gengar) (`f`, 30 cards)
- Set S (Floragato hunter) (`s`, 30 cards)
- Spare Cards (`spare`, 4 cards)

## Not 60 cards, no row

- Set T (Dragapult ex) (`t`, 30 cards)

## Path

Delta start is against the 0-copy list. Delta step is against the previous count. Mill cards is `mill_opponent`. Shovel is `shovel_mill`. Attaches is `tool:Cursed Shovel`. Those two shovel keys are bumped for both players, so at zero copies they are the foe's tools, mostly Doll. The counters are weighted over every foe in the score, including a foe that mills.

| Copies | Cut | Weighted | ± | Mean | Worst | Delta start | Delta step | Mill cards | Shovel | Attaches |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 50.65% | 0.47% | 66.96% | 15.12% | +0.00% | +0.00% | 21.08 | 0.00 | 0.01 |
| 1 | Buddy-Buddy Poffin | 52.47% | 0.48% | 67.92% | 18.38% | +1.82% | +1.82% | 21.43 | 0.20 | 0.38 |
| 2 | Mime Jr. | 52.43% | 0.48% | 68.18% | 19.62% | +1.78% | -0.04% | 21.74 | 0.38 | 0.73 |
| 3 | Wally | 51.90% | 0.48% | 67.69% | 18.75% | +1.25% | -0.53% | 21.97 | 0.54 | 1.09 |
| 4 | Crushing Hammer | 52.47% | 0.48% | 68.11% | 20.00% | +1.82% | +0.57% | 21.99 | 0.68 | 1.41 |

## Decision

Kept count is 4 Cursed Shovel: weighted 52.47% against the start at 50.65% (+1.82%, gap SE 0.66%, 2.75 combined standard errors).

Copy 4 gains +1.82% over the start. Copy 1 gains +1.82%. The higher count gained more. Unrounded, copy 4 leads by +0.0048%.
Copy 4 gains +1.82% over the start. Copy 2 gains +1.78%. The higher count gained more.
Copy 4 gains +1.82% over the start. Copy 3 gains +1.25%. The higher count gained more.

The step from 3 to 4 is +0.57%, gap SE 0.67%, 0.85 combined standard errors. That step does not clear one combined standard error. The kept count is still the one with the largest gain over the start.

Each step took the best cut on this seed, so that path sits a little high. Continuing through a dip does not remove that.

This file records the sample. It does not assign `SET_MILL_NAMES`.

Counts on the kept list (4 Cursed Shovel):

- Pichu ×1
- Cleffa ×1
- Wiglett ×4
- Wugtrio ×4
- Victini ×1
- Slumbering Forest ×1
- Neutralization Zone ×1
- Buddy-Buddy Poffin ×3
- Level Ball ×4
- Rescue Carrier ×3
- Lillie's Poké Doll ×1
- Crushing Hammer ×3
- Miss Fortune Sisters ×2
- Wally ×1
- Igglybuff ×1
- Team Rocket's Handiwork ×2
- Colress's Tenacity ×4
- Double Turbo Energy ×4
- Water Energy ×3
- Ignition Energy ×2
- Reversal Energy ×4
- Hilda ×4
- Lillie's Determination ×2
- Cursed Shovel ×4

### 1 Cursed Shovel, cut Buddy-Buddy Poffin

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Buddy-Buddy Poffin: "Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the start, +1.82%, gap SE 0.66%, 2.74 combined standard errors. Against the previous count, +1.82%, gap SE 0.66%, 2.74 combined standard errors.

Against the previous count, the weighted move is Set D Standard 60 (Charm Ogerpon) +0.49% of the weighted rate; Set M Standard 60 (Mew ex / Spiky Energy) +0.34% of the weighted rate; Mega Starmie ex (Kudo) +0.33% of the weighted rate; Worlds 2026 Hedrick Dragapult -0.15% of the weighted rate; Carpet Set H (Team Rocket's Zapdos / Pikachu 60) -0.05% of the weighted rate; Set S Standard 60 (Floragato hunter) -0.04% of the weighted rate.

The unweighted mean is 67.92% against 66.96% on the previous count and 66.96% on the start. The keeper is the 0-copy loss weights.

Cursed Shovel counters: shovel_mill 0.00 → 0.20, tool:Cursed Shovel 0.01 → 0.38.
The sample has no counter for Buddy-Buddy Poffin.
Line counters, on the same weights: mill_opponent 21.08 → 21.43, mill_attack 4.53 → 4.70, shovel_mill 0.00 → 0.20, tool:Cursed Shovel 0.01 → 0.38, hilda 1.35 → 1.34, wally 0.34 → 0.32, eeeeeeek_shuffle 0.26 → 0.27.

End reasons, weighted with the 0-copy vector, from Mill's seat: prizes 27.49% → 24.74% (-2.76%); foe_decked 50.26% → 52.16% (+1.91%); empty 13.74% → 15.20% (+1.46%); decked 7.73% → 7.16% (-0.56%).

Replacing one Buddy-Buddy Poffin with Cursed Shovel leaves the weighted rate higher (+1.82%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.20 a game, counting both players.

#### Also Crushing Hammer (+1.52%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, +1.52%, gap SE 0.66%, 2.31 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.64%, Celebi Mill +0.24%, Mill -0.06%, Set S Standard 60 (Floragato hunter) -0.01%.
Unweighted mean 68.02% against the entering list at 66.96%.
Crushing Hammer counters: crushing_hammer_heads 0.79 → 0.66, crushing_hammer_tails 0.78 → 0.64.
End reasons: foe_decked 50.26% → 51.79% (+1.54%); prizes 27.49% → 26.55% (-0.94%); decked 7.73% → 7.41% (-0.32%); empty 13.74% → 13.51% (-0.23%).
Replacing one Crushing Hammer with Cursed Shovel leaves the weighted rate higher (+1.52%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.20 a game, counting both players.

#### Also Colress's Tenacity (+1.49%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.49%, gap SE 0.66%, 2.27 combined standard errors.

Weighted contributions: Mill +0.37%, Set M Standard 60 (Mew ex / Spiky Energy) +0.34%, Set T Standard 60 (Dragapult ex) -0.07%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) -0.05%.
Unweighted mean 67.84% against the entering list at 66.96%.
Colress's Tenacity counters: colress 1.40 → 1.12.
End reasons: foe_decked 50.26% → 51.81% (+1.55%); empty 13.74% → 12.68% (-1.06%); decked 7.73% → 7.20% (-0.53%).
Replacing one Colress's Tenacity with Cursed Shovel leaves the weighted rate higher (+1.49%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.20 a game, counting both players.

#### Also Cleffa (+1.45%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.45%, gap SE 0.66%, 2.20 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.65%, Set D Standard 60 (Charm Ogerpon) +0.45%, Set M Standard 60 (Mew ex / Spiky Energy) -0.41%, Set C Standard 60 (Clefairy / Mewtwo) -0.24%.
Unweighted mean 68.18% against the entering list at 66.96%.
Cleffa counters: eeeeeeek_shuffle 0.26 → 0.03.
End reasons: foe_decked 50.26% → 51.80% (+1.54%); prizes 27.49% → 26.09% (-1.40%); decked 7.73% → 6.86% (-0.86%); empty 13.74% → 14.56% (+0.83%).
Replacing one Cleffa with Cursed Shovel leaves the weighted rate higher (+1.45%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.19 a game, counting both players.

#### Also Wally (+1.44%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the list entering the step, +1.44%, gap SE 0.66%, 2.17 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.76%, Carpet Set G (Clefairy / Ledian 60) +0.22%, Mill -0.07%, Set C Standard 60 (Clefairy / Mewtwo) -0.01%.
Unweighted mean 67.85% against the entering list at 66.96%.
Wally counters: wally 0.34 → 0.21.
End reasons: foe_decked 50.26% → 51.75% (+1.49%); prizes 27.49% → 26.02% (-1.47%).
Replacing one Wally with Cursed Shovel leaves the weighted rate higher (+1.44%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.20 a game, counting both players.

#### Also Water Energy (+1.44%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, +1.44%, gap SE 0.66%, 2.18 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.53%, Set M Standard 60 (Mew ex / Spiky Energy) +0.26%, Worlds 2026 Hedrick Dragapult -0.20%.
Unweighted mean 67.87% against the entering list at 66.96%.
The sample has no counter for Water Energy.
End reasons: foe_decked 50.26% → 51.78% (+1.53%); prizes 27.49% → 26.37% (-1.12%).
Replacing one Water Energy with Cursed Shovel leaves the weighted rate higher (+1.44%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.19 a game, counting both players.

#### Also Ignition Energy (+1.40%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, +1.40%, gap SE 0.66%, 2.12 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.43%, Mill +0.38%, Worlds 2026 Hedrick Dragapult -0.18%, Set T Standard 60 (Dragapult ex) -0.01%.
Unweighted mean 67.76% against the entering list at 66.96%.
The sample has no counter for Ignition Energy.
End reasons: foe_decked 50.26% → 51.66% (+1.41%); prizes 27.49% → 26.69% (-0.80%); decked 7.73% → 7.07% (-0.66%).
Replacing one Ignition Energy with Cursed Shovel leaves the weighted rate higher (+1.40%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.21 a game, counting both players.

#### Also Pichu (+1.35%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.35%, gap SE 0.66%, 2.07 combined standard errors.

Weighted contributions: Mill +0.27%, Set D Standard 60 (Charm Ogerpon) +0.25%, Worlds 2026 Hedrick Dragapult -0.15%, Set M Standard 60 (Mew ex / Spiky Energy) -0.05%.
Unweighted mean 68.19% against the entering list at 66.96%.
Pichu counters: playground 1.61 → 0.67.
End reasons: prizes 27.49% → 23.41% (-4.08%); empty 13.74% → 17.07% (+3.33%); foe_decked 50.26% → 51.78% (+1.53%); decked 7.73% → 7.08% (-0.65%).
Replacing one Pichu with Cursed Shovel leaves the weighted rate higher (+1.35%), with the largest piece on Mill, and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.20 a game, counting both players.

#### Also Miss Fortune Sisters (+1.27%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Miss Fortune Sisters: "Look at the top 5 cards of your opponent's deck and discard any number of Item cards you find there. Your opponent shuffles the other cards back into their deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.27%, gap SE 0.66%, 1.92 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.34%, Mega Starmie ex (Kudo) +0.29%, Mill -0.11%, Carpet Set G (Clefairy / Ledian 60) -0.04%.
Unweighted mean 68.04% against the entering list at 66.96%.
Miss Fortune Sisters counters: sisters_item 1.24 → 0.77, sisters_miss 0.15 → 0.08.
End reasons: foe_decked 50.26% → 51.56% (+1.30%); empty 13.74% → 12.69% (-1.05%); prizes 27.49% → 27.17% (-0.32%).
Replacing one Miss Fortune Sisters with Cursed Shovel leaves the weighted rate higher (+1.27%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.21 a game, counting both players.

#### Also Level Ball (+1.00%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.00%, gap SE 0.66%, 1.51 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.57%, Carpet Set G (Clefairy / Ledian 60) +0.28%, Mega Starmie ex (Kudo) -0.26%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) -0.08%.
Unweighted mean 67.59% against the entering list at 66.96%.
Level Ball counters: level_ball 1.39 → 1.08.
End reasons: prizes 27.49% → 25.39% (-2.10%); empty 13.74% → 14.90% (+1.17%); foe_decked 50.26% → 51.19% (+0.93%).
Replacing one Level Ball with Cursed Shovel leaves the weighted rate higher (+1.00%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.19 a game, counting both players.

#### Also Reversal Energy (+0.84%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Reversal Energy: "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy but provides only 3 Energy at a time."

The score uses the 0-copy loss weights. Against the list entering the step, +0.84%, gap SE 0.66%, 1.27 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.64%, Set C Standard 60 (Clefairy / Mewtwo) +0.18%, Set M Standard 60 (Mew ex / Spiky Energy) -0.25%, 二森林 -0.16%.
Unweighted mean 67.51% against the entering list at 66.96%.
The sample has no counter for Reversal Energy.
End reasons: empty 13.74% → 12.97% (-0.77%); foe_decked 50.26% → 50.97% (+0.71%).
Replacing one Reversal Energy with Cursed Shovel leaves the weighted rate higher (+0.84%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.20 a game, counting both players.

#### Also Team Rocket's Handiwork (+0.68%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Team Rocket's Handiwork: "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.68%, gap SE 0.66%, 1.03 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.18%, Celebi Mill +0.17%, Mill -0.10%, Worlds 2026 Hedrick Dragapult -0.07%.
Unweighted mean 67.59% against the entering list at 66.96%.
Team Rocket's Handiwork counters: handiwork 0.76 → 0.46, handiwork_tails 0.20 → 0.11.
End reasons: empty 13.74% → 12.92% (-0.82%); foe_decked 50.26% → 50.96% (+0.70%).
Replacing one Team Rocket's Handiwork with Cursed Shovel leaves the weighted rate higher (+0.68%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.38 a game and shovel mills move +0.21 a game, counting both players.

#### Also Mime Jr. (+0.67%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Mime Jr.: "Sweet Sleeping Face: As long as Mime Jr. is Asleep, prevent all damage done to Mime Jr. by attacks. Sleepy Lost: Put the top card of your opponent's deck in the Lost Zone. Mime Jr. is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +0.67%, gap SE 0.66%, 1.01 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.55%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.16%, Mill -0.28%, Set M Standard 60 (Mew ex / Spiky Energy) -0.15%.
Unweighted mean 67.65% against the entering list at 66.96%.
Mime Jr. counters: sleepy_lost 0.27 → 0.05, sleepy_lost_miss 0.00 → 0.00.
End reasons: prizes 27.49% → 26.16% (-1.33%); foe_decked 50.26% → 51.00% (+0.75%); empty 13.74% → 14.26% (+0.53%).
Replacing one Mime Jr. with Cursed Shovel leaves the weighted rate higher (+0.67%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.20 a game, counting both players.

#### Also Neutralization Zone (-0.74%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -0.74%, gap SE 0.66%, -1.12 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +1.68%, Set C Standard 60 (Clefairy / Mewtwo) +0.29%, Mega Starmie ex (Kudo) -1.05%, Set T Standard 60 (Dragapult ex) -1.01%.
Unweighted mean 65.34% against the entering list at 66.96%.
Neutralization Zone counters: neutralization_zone 7.92 → 0.26.
End reasons: empty 13.74% → 15.82% (+2.09%); prizes 27.49% → 26.23% (-1.26%); foe_decked 50.26% → 49.56% (-0.70%).
Replacing one Neutralization Zone with Cursed Shovel leaves the weighted rate lower (-0.74%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.20 a game, counting both players.

#### Also Victini (-1.52%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -1.52%, gap SE 0.65%, -2.34 combined standard errors.

Weighted contributions: Set T Standard 60 (Dragapult ex) +0.15%, Set S Standard 60 (Floragato hunter) +0.09%, Set M Standard 60 (Mew ex / Spiky Energy) -0.75%, Carpet Set G (Clefairy / Ledian 60) -0.30%.
Unweighted mean 66.23% against the entering list at 66.96%.
Victini counters: victory_star_reflip 1.06 → 0.20.
End reasons: empty 13.74% → 16.48% (+2.74%); prizes 27.49% → 26.05% (-1.44%); foe_decked 50.26% → 48.86% (-1.40%).
Replacing one Victini with Cursed Shovel leaves the weighted rate lower (-1.52%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.21 a game, counting both players.

### 2 Cursed Shovel, cut Mime Jr.

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Mime Jr.: "Sweet Sleeping Face: As long as Mime Jr. is Asleep, prevent all damage done to Mime Jr. by attacks. Sleepy Lost: Put the top card of your opponent's deck in the Lost Zone. Mime Jr. is now Asleep."

The score uses the 0-copy loss weights. Against the start, +1.78%, gap SE 0.66%, 2.68 combined standard errors. Against the previous count, -0.04%, gap SE 0.67%, -0.06 combined standard errors.

Against the previous count, the weighted move is Set D Standard 60 (Charm Ogerpon) +0.19% of the weighted rate; Set S Standard 60 (Floragato hunter) +0.13% of the weighted rate; 二森林 +0.10% of the weighted rate; Set M Standard 60 (Mew ex / Spiky Energy) -0.26% of the weighted rate; Set C Standard 60 (Clefairy / Mewtwo) -0.24% of the weighted rate; Mill -0.14% of the weighted rate.

The unweighted mean is 68.18% against 67.92% on the previous count and 66.96% on the start. The keeper is the 0-copy loss weights.

Cursed Shovel counters: shovel_mill 0.20 → 0.38, tool:Cursed Shovel 0.38 → 0.73.
Mime Jr. counters: sleepy_lost 0.28 → 0.05, sleepy_lost_miss 0.00 → 0.00.
Line counters, on the same weights: mill_opponent 21.43 → 21.74, mill_attack 4.70 → 4.87, shovel_mill 0.20 → 0.38, tool:Cursed Shovel 0.38 → 0.73, hilda 1.34 → 1.32, wally 0.32 → 0.32, eeeeeeek_shuffle 0.27 → 0.29.
Those counters moved, and the weighted win rate did not clear one combined standard error.

End reasons, weighted with the 0-copy vector, from Mill's seat: empty 15.20% → 15.81% (+0.61%); prizes 24.74% → 24.21% (-0.53%).

Replacing one Mime Jr. with Cursed Shovel leaves the weighted rate lower (-0.04%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Cleffa (-0.67%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -0.67%, gap SE 0.67%, -1.00 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.36%, Set S Standard 60 (Floragato hunter) +0.15%, Set M Standard 60 (Mew ex / Spiky Energy) -0.63%, Mega Starmie ex (Kudo) -0.30%.
Unweighted mean 67.64% against the entering list at 67.92%.
Cleffa counters: eeeeeeek_shuffle 0.27 → 0.03.
End reasons: empty 15.20% → 16.92% (+1.72%); prizes 24.74% → 23.80% (-0.94%); foe_decked 52.16% → 51.39% (-0.77%).
Replacing one Cleffa with Cursed Shovel leaves the weighted rate lower (-0.67%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.18 a game, counting both players.

#### Also Hilda (-0.76%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.76%, gap SE 0.67%, -1.14 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.14%, Set D Standard 60 (Charm Ogerpon) +0.13%, Mega Starmie ex (Kudo) -0.36%, Carpet Set G (Clefairy / Ledian 60) -0.36%.
Unweighted mean 67.64% against the entering list at 67.92%.
Hilda counters: hilda 1.34 → 1.09, evo_from_hilda 1.20 → 0.99, energy_from_hilda 1.33 → 1.08.
End reasons: foe_decked 52.16% → 51.41% (-0.76%); prizes 24.74% → 25.14% (+0.40%); decked 7.16% → 7.47% (+0.30%).
Replacing one Hilda with Cursed Shovel leaves the weighted rate lower (-0.76%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.18 a game, counting both players.

#### Also Wally (-0.82%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the list entering the step, -0.82%, gap SE 0.67%, -1.22 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.12%, Set D Standard 60 (Charm Ogerpon) +0.11%, Mill -0.52%, Mega Starmie ex (Kudo) -0.25%.
Unweighted mean 67.25% against the entering list at 67.92%.
Wally counters: wally 0.32 → 0.20.
End reasons: foe_decked 52.16% → 51.19% (-0.97%); decked 7.16% → 7.73% (+0.57%); empty 15.20% → 15.47% (+0.28%).
Replacing one Wally with Cursed Shovel leaves the weighted rate lower (-0.82%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Crushing Hammer (-0.96%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -0.96%, gap SE 0.67%, -1.44 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.13%, Set S Standard 60 (Floragato hunter) +0.10%, Mega Starmie ex (Kudo) -0.69%, Mill -0.45%.
Unweighted mean 67.41% against the entering list at 67.92%.
Crushing Hammer counters: crushing_hammer_heads 0.78 → 0.64, crushing_hammer_tails 0.78 → 0.65.
End reasons: foe_decked 52.16% → 51.19% (-0.97%); empty 15.20% → 16.01% (+0.81%); decked 7.16% → 7.72% (+0.56%); prizes 24.74% → 24.38% (-0.36%).
Replacing one Crushing Hammer with Cursed Shovel leaves the weighted rate lower (-0.96%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Miss Fortune Sisters (-0.99%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Miss Fortune Sisters: "Look at the top 5 cards of your opponent's deck and discard any number of Item cards you find there. Your opponent shuffles the other cards back into their deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.99%, gap SE 0.66%, -1.50 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.12%, Worlds 2026 Hedrick Dragapult +0.10%, Carpet Set G (Clefairy / Ledian 60) -0.51%, Set M Standard 60 (Mew ex / Spiky Energy) -0.40%.
Unweighted mean 67.59% against the entering list at 67.92%.
Miss Fortune Sisters counters: sisters_item 1.21 → 0.73, sisters_miss 0.15 → 0.07.
End reasons: foe_decked 52.16% → 51.11% (-1.05%); prizes 24.74% → 25.43% (+0.69%); empty 15.20% → 15.49% (+0.29%).
Replacing one Miss Fortune Sisters with Cursed Shovel leaves the weighted rate lower (-0.99%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Lillie's Poké Doll (-1.12%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Lillie's Poké Doll: "Play this card as if it were a 30-HP Colorless Basic Pokémon. At any time during your turn (before your attack), if this Pokémon is your Active Pokémon, you may discard all cards from it and put it on the bottom of your deck. This card can't retreat. If this card is Knocked Out, your opponent can't take any Prize cards for it."

The score uses the 0-copy loss weights. Against the list entering the step, -1.12%, gap SE 0.67%, -1.68 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.19%, Set S Standard 60 (Floragato hunter) +0.13%, Set M Standard 60 (Mew ex / Spiky Energy) -0.58%, Mega Starmie ex (Kudo) -0.27%.
Unweighted mean 67.36% against the entering list at 67.92%.
The sample has no counter for Lillie's Poké Doll.
End reasons: empty 15.20% → 16.56% (+1.36%); foe_decked 52.16% → 50.96% (-1.20%); prizes 24.74% → 24.25% (-0.49%); decked 7.16% → 7.58% (+0.41%).
Replacing one Lillie's Poké Doll with Cursed Shovel leaves the weighted rate lower (-1.12%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.17 a game, counting both players.

#### Also Ignition Energy (-1.17%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, -1.17%, gap SE 0.67%, -1.76 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.08%, Worlds 2026 Hedrick Dragapult +0.05%, Mega Starmie ex (Kudo) -0.55%, Set M Standard 60 (Mew ex / Spiky Energy) -0.46%.
Unweighted mean 67.38% against the entering list at 67.92%.
The sample has no counter for Ignition Energy.
End reasons: foe_decked 52.16% → 51.00% (-1.17%); empty 15.20% → 16.14% (+0.94%); decked 7.16% → 7.45% (+0.29%).
Replacing one Ignition Energy with Cursed Shovel leaves the weighted rate lower (-1.17%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.19 a game, counting both players.

#### Also Double Turbo Energy (-1.48%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Double Turbo Energy: "As long as this card is attached to a Pokémon, it provides Colorless Colorless Energy. The attacks of the Pokémon this card is attached to do 20 less damage to your opponent's Active Pokémon (before applying Weakness and Resistance)."

The score uses the 0-copy loss weights. Against the list entering the step, -1.48%, gap SE 0.67%, -2.22 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.21%, Worlds 2026 Hedrick Dragapult +0.16%, Mill -0.57%, Mega Starmie ex (Kudo) -0.49%.
Unweighted mean 67.02% against the entering list at 67.92%.
The sample has no counter for Double Turbo Energy.
End reasons: foe_decked 52.16% → 50.71% (-1.45%); decked 7.16% → 7.92% (+0.75%); empty 15.20% → 15.79% (+0.59%).
Replacing one Double Turbo Energy with Cursed Shovel leaves the weighted rate lower (-1.48%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Igglybuff (-1.49%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, -1.49%, gap SE 0.67%, -2.24 combined standard errors.

Weighted contributions: Celebi Mill +0.31%, Set S Standard 60 (Floragato hunter) +0.17%, Carpet Set G (Clefairy / Ledian 60) -0.55%, Mill -0.48%.
Unweighted mean 66.93% against the entering list at 67.92%.
Igglybuff counters: sleepy_flip 1.36 → 0.06, sleepy_heads 0.68 → 0.03.
End reasons: empty 15.20% → 19.63% (+4.43%); prizes 24.74% → 21.90% (-2.83%); foe_decked 52.16% → 50.53% (-1.63%); turn_prizes 0.41% → 0.20% (-0.21%).
Replacing one Igglybuff with Cursed Shovel leaves the weighted rate lower (-1.49%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.17 a game, counting both players.

#### Also Level Ball (-1.62%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.62%, gap SE 0.67%, -2.43 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.13%, Set D Standard 60 (Charm Ogerpon) +0.08%, Mega Starmie ex (Kudo) -0.72%, Carpet Set G (Clefairy / Ledian 60) -0.40%.
Unweighted mean 66.94% against the entering list at 67.92%.
Level Ball counters: level_ball 1.35 → 1.08.
End reasons: empty 15.20% → 17.53% (+2.33%); foe_decked 52.16% → 50.52% (-1.64%); prizes 24.74% → 23.62% (-1.12%); decked 7.16% → 7.61% (+0.44%).
Replacing one Level Ball with Cursed Shovel leaves the weighted rate lower (-1.62%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.17 a game, counting both players.

#### Also Slumbering Forest (-1.89%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Slumbering Forest: "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.89%, gap SE 0.66%, -2.86 combined standard errors.

Weighted contributions: Celebi Mill +0.21%, Set T Standard 60 (Dragapult ex) +0.14%, Set D Standard 60 (Charm Ogerpon) -0.66%, Carpet Set G (Clefairy / Ledian 60) -0.63%.
Unweighted mean 67.19% against the entering list at 67.92%.
Slumbering Forest counters: slumbering_forest 1.96 → 0.44.
End reasons: foe_decked 52.16% → 50.18% (-1.98%); prizes 24.74% → 25.88% (+1.15%); empty 15.20% → 16.00% (+0.80%).
Replacing one Slumbering Forest with Cursed Shovel leaves the weighted rate lower (-1.89%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.18 a game, counting both players.

#### Also Buddy-Buddy Poffin (-1.93%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Buddy-Buddy Poffin: "Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.93%, gap SE 0.67%, -2.90 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.01%, Set M Standard 60 (Mew ex / Spiky Energy) -0.48%, Mill -0.27%.
Unweighted mean 66.40% against the entering list at 67.92%.
The sample has no counter for Buddy-Buddy Poffin.
End reasons: empty 15.20% → 18.98% (+3.78%); prizes 24.74% → 22.21% (-2.52%); foe_decked 52.16% → 50.19% (-1.97%); decked 7.16% → 7.86% (+0.69%).
Replacing one Buddy-Buddy Poffin with Cursed Shovel leaves the weighted rate lower (-1.93%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.17 a game, counting both players.

#### Also Pichu (-1.98%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.98%, gap SE 0.66%, -3.00 combined standard errors.

Weighted contributions: Celebi Mill +0.24%, 二森林 +0.22%, Set M Standard 60 (Mew ex / Spiky Energy) -0.66%, Mega Starmie ex (Kudo) -0.51%.
Unweighted mean 67.16% against the entering list at 67.92%.
Pichu counters: playground 1.71 → 0.70.
End reasons: empty 15.20% → 21.69% (+6.49%); prizes 24.74% → 20.31% (-4.42%); foe_decked 52.16% → 50.26% (-1.90%).
Replacing one Pichu with Cursed Shovel leaves the weighted rate lower (-1.98%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Reversal Energy (-2.03%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Reversal Energy: "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy but provides only 3 Energy at a time."

The score uses the 0-copy loss weights. Against the list entering the step, -2.03%, gap SE 0.66%, -3.05 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.11%, Celebi Mill +0.05%, Mega Starmie ex (Kudo) -0.74%, Set M Standard 60 (Mew ex / Spiky Energy) -0.54%.
Unweighted mean 66.80% against the entering list at 67.92%.
The sample has no counter for Reversal Energy.
End reasons: foe_decked 52.16% → 49.97% (-2.19%); prizes 24.74% → 25.96% (+1.22%); decked 7.16% → 7.61% (+0.45%); empty 15.20% → 15.51% (+0.31%).
Replacing one Reversal Energy with Cursed Shovel leaves the weighted rate lower (-2.03%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.19 a game, counting both players.

#### Also Water Energy (-2.07%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, -2.07%, gap SE 0.66%, -3.12 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.13%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.05%, Mill -0.60%, Mega Starmie ex (Kudo) -0.55%.
Unweighted mean 66.80% against the entering list at 67.92%.
The sample has no counter for Water Energy.
End reasons: foe_decked 52.16% → 50.10% (-2.06%); empty 15.20% → 16.46% (+1.26%); decked 7.16% → 7.82% (+0.66%); prizes 24.74% → 24.97% (+0.23%).
Replacing one Water Energy with Cursed Shovel leaves the weighted rate lower (-2.07%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.18 a game, counting both players.

#### Also Team Rocket's Handiwork (-2.34%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Team Rocket's Handiwork: "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, -2.34%, gap SE 0.66%, -3.53 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.06%, Worlds 2026 Hedrick Dragapult +0.04%, Mega Starmie ex (Kudo) -0.72%, Set M Standard 60 (Mew ex / Spiky Energy) -0.72%.
Unweighted mean 66.60% against the entering list at 67.92%.
Team Rocket's Handiwork counters: handiwork 0.74 → 0.44, handiwork_tails 0.19 → 0.11.
End reasons: foe_decked 52.16% → 49.80% (-2.36%); empty 15.20% → 16.40% (+1.20%); prizes 24.74% → 25.41% (+0.67%); decked 7.16% → 7.60% (+0.44%).
Replacing one Team Rocket's Handiwork with Cursed Shovel leaves the weighted rate lower (-2.34%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.18 a game, counting both players.

#### Also Colress's Tenacity (-2.58%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -2.58%, gap SE 0.66%, -3.87 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.09%, Set S Standard 60 (Floragato hunter) +0.04%, Mega Starmie ex (Kudo) -0.84%, Set M Standard 60 (Mew ex / Spiky Energy) -0.55%.
Unweighted mean 66.32% against the entering list at 67.92%.
Colress's Tenacity counters: colress 1.38 → 1.10.
End reasons: foe_decked 52.16% → 49.45% (-2.71%); empty 15.20% → 16.87% (+1.67%); decked 7.16% → 7.87% (+0.71%); prizes 24.74% → 25.02% (+0.28%).
Replacing one Colress's Tenacity with Cursed Shovel leaves the weighted rate lower (-2.58%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.17 a game, counting both players.

#### Also Lillie's Determination (-2.58%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead."

The score uses the 0-copy loss weights. Against the list entering the step, -2.58%, gap SE 0.66%, -3.90 combined standard errors.

Weighted contributions: Celebi Mill +0.18%, Set S Standard 60 (Floragato hunter) +0.12%, Set M Standard 60 (Mew ex / Spiky Energy) -0.55%, Carpet Set G (Clefairy / Ledian 60) -0.53%.
Unweighted mean 66.32% against the entering list at 67.92%.
The sample has no counter for Lillie's Determination.
End reasons: foe_decked 52.16% → 49.53% (-2.63%); empty 15.20% → 17.63% (+2.43%); decked 7.16% → 7.44% (+0.28%).
Replacing one Lillie's Determination with Cursed Shovel leaves the weighted rate lower (-2.58%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.29 a game and shovel mills move +0.16 a game, counting both players.

#### Also Neutralization Zone (-3.06%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -3.06%, gap SE 0.67%, -4.59 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +1.15%, Set S Standard 60 (Floragato hunter) +0.22%, Mega Starmie ex (Kudo) -1.86%, Set T Standard 60 (Dragapult ex) -1.01%.
Unweighted mean 65.05% against the entering list at 67.92%.
Neutralization Zone counters: neutralization_zone 7.71 → 0.26.
End reasons: empty 15.20% → 18.88% (+3.69%); foe_decked 52.16% → 49.17% (-2.99%); prizes 24.74% → 23.79% (-0.94%); decked 7.16% → 7.56% (+0.40%).
Replacing one Neutralization Zone with Cursed Shovel leaves the weighted rate lower (-3.06%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.18 a game, counting both players.

#### Also Wiglett (-3.10%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wiglett: "Twisting Strike: Flip a coin. If heads, during your opponent's next turn, prevent all damage from and effects of attacks done to this Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -3.10%, gap SE 0.66%, -4.68 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.17%, Celebi Mill +0.02%, Set M Standard 60 (Mew ex / Spiky Energy) -0.66%, Mill -0.55%.
Unweighted mean 65.89% against the entering list at 67.92%.
The sample has no counter for Wiglett.
End reasons: empty 15.20% → 18.51% (+3.31%); foe_decked 52.16% → 48.95% (-3.21%); prizes 24.74% → 23.91% (-0.83%); decked 7.16% → 7.71% (+0.55%).
Replacing one Wiglett with Cursed Shovel leaves the weighted rate lower (-3.10%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.19 a game, counting both players.

#### Also Victini (-4.20%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -4.20%, gap SE 0.66%, -6.39 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.08%, Set M Standard 60 (Mew ex / Spiky Energy) -0.80%, Mega Starmie ex (Kudo) -0.78%.
Unweighted mean 65.36% against the entering list at 67.92%.
Victini counters: victory_star_reflip 1.09 → 0.19.
End reasons: foe_decked 52.16% → 48.12% (-4.04%); empty 15.20% → 18.85% (+3.65%); decked 7.16% → 8.23% (+1.07%); prizes 24.74% → 24.28% (-0.45%).
Replacing one Victini with Cursed Shovel leaves the weighted rate lower (-4.20%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.19 a game, counting both players.

### 3 Cursed Shovel, cut Wally

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the start, +1.25%, gap SE 0.66%, 1.89 combined standard errors. Against the previous count, -0.53%, gap SE 0.67%, -0.79 combined standard errors.

Against the previous count, the weighted move is Set C Standard 60 (Clefairy / Mewtwo) +0.22% of the weighted rate; Worlds 2026 Hedrick Dragapult +0.22% of the weighted rate; Set M Standard 60 (Mew ex / Spiky Energy) +0.21% of the weighted rate; Mill -0.42% of the weighted rate; 二森林 -0.31% of the weighted rate; Set D Standard 60 (Charm Ogerpon) -0.13% of the weighted rate.

The unweighted mean is 67.69% against 68.18% on the previous count and 66.96% on the start. The keeper is the 0-copy loss weights.

Cursed Shovel counters: shovel_mill 0.38 → 0.54, tool:Cursed Shovel 0.73 → 1.09.
Wally counters: wally 0.32 → 0.20.
Line counters, on the same weights: mill_opponent 21.74 → 21.97, mill_attack 4.87 → 5.01, shovel_mill 0.38 → 0.54, tool:Cursed Shovel 0.73 → 1.09, hilda 1.32 → 1.36, wally 0.32 → 0.20, eeeeeeek_shuffle 0.29 → 0.30.
Those counters moved, and the weighted win rate did not clear one combined standard error.

End reasons, weighted with the 0-copy vector, from Mill's seat: decked 7.21% → 7.93% (+0.72%); foe_decked 52.11% → 51.52% (-0.59%); prizes 24.21% → 23.88% (-0.33%).

Replacing one Wally with Cursed Shovel leaves the weighted rate lower (-0.53%), with the largest piece on Mill, and the end-reason mix moves at decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.16 a game, counting both players.

#### Also Rescue Carrier (-0.69%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Rescue Carrier: "Put up to 2 Pokémon, each with 90 HP or less, from your discard pile into your hand."

The score uses the 0-copy loss weights. Against the list entering the step, -0.69%, gap SE 0.67%, -1.02 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.32%, Mega Starmie ex (Kudo) +0.04%, 二森林 -0.23%, Mill -0.21%.
Unweighted mean 67.31% against the entering list at 68.18%.
Rescue Carrier counters: rescue_carrier 1.66 → 1.25.
End reasons: prizes 24.21% → 23.03% (-1.18%); empty 15.81% → 16.93% (+1.11%); decked 7.21% → 7.94% (+0.73%); foe_decked 52.11% → 51.39% (-0.72%).
Replacing one Rescue Carrier with Cursed Shovel leaves the weighted rate lower (-0.69%), with the largest piece on 二森林, and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Ignition Energy (-0.72%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, -0.72%, gap SE 0.67%, -1.08 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.25%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.04%, Mega Starmie ex (Kudo) -0.36%, Set M Standard 60 (Mew ex / Spiky Energy) -0.35%.
Unweighted mean 67.68% against the entering list at 68.18%.
The sample has no counter for Ignition Energy.
End reasons: foe_decked 52.11% → 51.46% (-0.65%); prizes 24.21% → 24.77% (+0.56%).
Replacing one Ignition Energy with Cursed Shovel leaves the weighted rate lower (-0.72%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Level Ball (-0.74%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.74%, gap SE 0.67%, -1.11 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.14%, Set C Standard 60 (Clefairy / Mewtwo) +0.12%, Mega Starmie ex (Kudo) -0.36%, Celebi Mill -0.33%.
Unweighted mean 67.32% against the entering list at 68.18%.
Level Ball counters: level_ball 1.32 → 1.04.
End reasons: empty 15.81% → 17.26% (+1.45%); prizes 24.21% → 23.10% (-1.11%); foe_decked 52.11% → 51.13% (-0.97%); decked 7.21% → 7.63% (+0.42%).
Replacing one Level Ball with Cursed Shovel leaves the weighted rate lower (-0.74%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.15 a game, counting both players.

#### Also Miss Fortune Sisters (-0.78%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Miss Fortune Sisters: "Look at the top 5 cards of your opponent's deck and discard any number of Item cards you find there. Your opponent shuffles the other cards back into their deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.78%, gap SE 0.67%, -1.17 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.18%, Set C Standard 60 (Clefairy / Mewtwo) +0.08%, Set M Standard 60 (Mew ex / Spiky Energy) -0.35%, 二森林 -0.17%.
Unweighted mean 67.59% against the entering list at 68.18%.
Miss Fortune Sisters counters: sisters_item 1.20 → 0.71, sisters_miss 0.15 → 0.08.
End reasons: foe_decked 52.11% → 51.26% (-0.85%); decked 7.21% → 7.51% (+0.30%); prizes 24.21% → 24.50% (+0.29%).
Replacing one Miss Fortune Sisters with Cursed Shovel leaves the weighted rate lower (-0.78%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Lillie's Poké Doll (-0.94%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Lillie's Poké Doll: "Play this card as if it were a 30-HP Colorless Basic Pokémon. At any time during your turn (before your attack), if this Pokémon is your Active Pokémon, you may discard all cards from it and put it on the bottom of your deck. This card can't retreat. If this card is Knocked Out, your opponent can't take any Prize cards for it."

The score uses the 0-copy loss weights. Against the list entering the step, -0.94%, gap SE 0.66%, -1.41 combined standard errors.

Weighted contributions: Mill +0.14%, Worlds 2026 Hedrick Dragapult +0.12%, Set D Standard 60 (Charm Ogerpon) -0.28%, Set M Standard 60 (Mew ex / Spiky Energy) -0.28%.
Unweighted mean 67.61% against the entering list at 68.18%.
The sample has no counter for Lillie's Poké Doll.
End reasons: empty 15.81% → 17.01% (+1.20%); foe_decked 52.11% → 51.14% (-0.97%); prizes 24.21% → 23.90% (-0.31%).
Replacing one Lillie's Poké Doll with Cursed Shovel leaves the weighted rate lower (-0.94%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.17 a game, counting both players.

#### Also Igglybuff (-1.02%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, -1.02%, gap SE 0.67%, -1.52 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.23%, Worlds 2026 Hedrick Dragapult +0.09%, Carpet Set G (Clefairy / Ledian 60) -0.41%, Set M Standard 60 (Mew ex / Spiky Energy) -0.35%.
Unweighted mean 67.26% against the entering list at 68.18%.
Igglybuff counters: sleepy_flip 1.45 → 0.06, sleepy_heads 0.73 → 0.03.
End reasons: empty 15.81% → 19.31% (+3.50%); prizes 24.21% → 21.64% (-2.57%); foe_decked 52.11% → 51.02% (-1.09%); decked 7.21% → 7.42% (+0.22%).
Replacing one Igglybuff with Cursed Shovel leaves the weighted rate lower (-1.02%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.29 a game and shovel mills move +0.15 a game, counting both players.

#### Also Hilda (-1.03%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.03%, gap SE 0.67%, -1.54 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.12%, Set M Standard 60 (Mew ex / Spiky Energy) +0.05%, Carpet Set G (Clefairy / Ledian 60) -0.32%, Mill -0.27%.
Unweighted mean 67.38% against the entering list at 68.18%.
Hilda counters: hilda 1.32 → 1.12, evo_from_hilda 1.16 → 1.00, energy_from_hilda 1.32 → 1.11.
End reasons: foe_decked 52.11% → 51.01% (-1.10%); prizes 24.21% → 24.82% (+0.61%); decked 7.21% → 7.63% (+0.42%).
Replacing one Hilda with Cursed Shovel leaves the weighted rate lower (-1.03%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.37 a game and shovel mills move +0.18 a game, counting both players.

#### Also Crushing Hammer (-1.08%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -1.08%, gap SE 0.66%, -1.62 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.17%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.15%, Set D Standard 60 (Charm Ogerpon) -0.51%, Mill -0.30%.
Unweighted mean 67.55% against the entering list at 68.18%.
Crushing Hammer counters: crushing_hammer_heads 0.77 → 0.62, crushing_hammer_tails 0.79 → 0.64.
End reasons: foe_decked 52.11% → 51.04% (-1.07%); empty 15.81% → 16.47% (+0.65%); decked 7.21% → 7.61% (+0.40%).
Replacing one Crushing Hammer with Cursed Shovel leaves the weighted rate lower (-1.08%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.15 a game, counting both players.

#### Also Buddy-Buddy Poffin (-1.25%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Buddy-Buddy Poffin: "Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.25%, gap SE 0.67%, -1.88 combined standard errors.

Weighted contributions: Celebi Mill +0.07%, Set D Standard 60 (Charm Ogerpon) +0.02%, Mega Starmie ex (Kudo) -0.32%, Set C Standard 60 (Clefairy / Mewtwo) -0.22%.
Unweighted mean 67.19% against the entering list at 68.18%.
The sample has no counter for Buddy-Buddy Poffin.
End reasons: empty 15.81% → 18.95% (+3.14%); prizes 24.21% → 22.22% (-1.99%); foe_decked 52.11% → 50.84% (-1.27%).
Replacing one Buddy-Buddy Poffin with Cursed Shovel leaves the weighted rate lower (-1.25%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.15 a game, counting both players.

#### Also Team Rocket's Handiwork (-1.26%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Team Rocket's Handiwork: "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.26%, gap SE 0.67%, -1.89 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.05%, Mill -0.23%, Mega Starmie ex (Kudo) -0.22%.
Unweighted mean 67.27% against the entering list at 68.18%.
Team Rocket's Handiwork counters: handiwork 0.75 → 0.44, handiwork_tails 0.18 → 0.11.
End reasons: foe_decked 52.11% → 50.82% (-1.29%); decked 7.21% → 7.69% (+0.49%); prizes 24.21% → 24.64% (+0.43%); empty 15.81% → 16.20% (+0.39%).
Replacing one Team Rocket's Handiwork with Cursed Shovel leaves the weighted rate lower (-1.26%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.16 a game, counting both players.

#### Also Water Energy (-1.26%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, -1.26%, gap SE 0.67%, -1.89 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.15%, Set C Standard 60 (Clefairy / Mewtwo) +0.10%, Mega Starmie ex (Kudo) -0.51%, Carpet Set G (Clefairy / Ledian 60) -0.34%.
Unweighted mean 67.35% against the entering list at 68.18%.
The sample has no counter for Water Energy.
End reasons: foe_decked 52.11% → 50.91% (-1.19%); empty 15.81% → 16.46% (+0.65%); prizes 24.21% → 24.50% (+0.29%); decked 7.21% → 7.43% (+0.22%).
Replacing one Water Energy with Cursed Shovel leaves the weighted rate lower (-1.26%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.17 a game, counting both players.

#### Also Colress's Tenacity (-1.36%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.36%, gap SE 0.67%, -2.03 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.37%, Carpet Set G (Clefairy / Ledian 60) -0.37%, Mega Starmie ex (Kudo) -0.27%.
Unweighted mean 67.06% against the entering list at 68.18%.
Colress's Tenacity counters: colress 1.37 → 1.10.
End reasons: foe_decked 52.11% → 50.68% (-1.43%); empty 15.81% → 16.54% (+0.73%); decked 7.21% → 7.55% (+0.35%).
Replacing one Colress's Tenacity with Cursed Shovel leaves the weighted rate lower (-1.36%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.16 a game, counting both players.

#### Also Wugtrio (-1.36%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wugtrio: "Undersea Tunnel: Flip 3 coins. For each heads, discard the top 3 cards of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.36%, gap SE 0.67%, -2.04 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.05%, Mill +0.01%, Mega Starmie ex (Kudo) -0.33%, Carpet Set G (Clefairy / Ledian 60) -0.27%.
Unweighted mean 67.08% against the entering list at 68.18%.
The sample has no counter for Wugtrio.
End reasons: foe_decked 52.11% → 50.75% (-1.35%); prizes 24.21% → 24.82% (+0.61%); empty 15.81% → 16.21% (+0.40%); decked 7.21% → 7.43% (+0.22%).
Replacing one Wugtrio with Cursed Shovel leaves the weighted rate lower (-1.36%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Slumbering Forest (-1.40%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Slumbering Forest: "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.40%, gap SE 0.65%, -2.16 combined standard errors.

Weighted contributions: Celebi Mill +0.24%, 二森林 +0.19%, Set D Standard 60 (Charm Ogerpon) -1.45%, Carpet Set G (Clefairy / Ledian 60) -0.45%.
Unweighted mean 68.05% against the entering list at 68.18%.
Slumbering Forest counters: slumbering_forest 1.79 → 0.42.
End reasons: prizes 24.21% → 26.18% (+1.97%); foe_decked 52.11% → 50.69% (-1.42%); decked 7.21% → 6.64% (-0.56%).
Replacing one Slumbering Forest with Cursed Shovel leaves the weighted rate lower (-1.40%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.16 a game, counting both players.

#### Also Lillie's Determination (-1.57%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead."

The score uses the 0-copy loss weights. Against the list entering the step, -1.57%, gap SE 0.67%, -2.36 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.23%, 二森林 +0.06%, Set D Standard 60 (Charm Ogerpon) -0.38%, Set C Standard 60 (Clefairy / Mewtwo) -0.36%.
Unweighted mean 66.91% against the entering list at 68.18%.
The sample has no counter for Lillie's Determination.
End reasons: empty 15.81% → 17.42% (+1.60%); foe_decked 52.11% → 50.57% (-1.54%).
Replacing one Lillie's Determination with Cursed Shovel leaves the weighted rate lower (-1.57%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.25 a game and shovel mills move +0.14 a game, counting both players.

#### Also Reversal Energy (-1.71%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Reversal Energy: "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy but provides only 3 Energy at a time."

The score uses the 0-copy loss weights. Against the list entering the step, -1.71%, gap SE 0.67%, -2.56 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.20%, Set D Standard 60 (Charm Ogerpon) +0.13%, Mill -0.69%, Mega Starmie ex (Kudo) -0.35%.
Unweighted mean 66.91% against the entering list at 68.18%.
The sample has no counter for Reversal Energy.
End reasons: foe_decked 52.11% → 50.32% (-1.79%); decked 7.21% → 8.05% (+0.84%); prizes 24.21% → 24.95% (+0.74%).
Replacing one Reversal Energy with Cursed Shovel leaves the weighted rate lower (-1.71%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Cleffa (-1.89%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.89%, gap SE 0.66%, -2.85 combined standard errors.

Weighted contributions: Celebi Mill +0.09%, Set T Standard 60 (Dragapult ex) +0.09%, Set M Standard 60 (Mew ex / Spiky Energy) -0.69%, Set C Standard 60 (Clefairy / Mewtwo) -0.56%.
Unweighted mean 67.10% against the entering list at 68.18%.
Cleffa counters: eeeeeeek_shuffle 0.29 → 0.03.
End reasons: empty 15.81% → 19.01% (+3.19%); foe_decked 52.11% → 50.28% (-1.83%); prizes 24.21% → 23.14% (-1.07%); decked 7.21% → 7.00% (-0.21%).
Replacing one Cleffa with Cursed Shovel leaves the weighted rate lower (-1.89%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.27 a game and shovel mills move +0.16 a game, counting both players.

#### Also Neutralization Zone (-1.95%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -1.95%, gap SE 0.67%, -2.90 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +1.49%, Set C Standard 60 (Clefairy / Mewtwo) +0.25%, Mega Starmie ex (Kudo) -1.49%, Set T Standard 60 (Dragapult ex) -1.22%.
Unweighted mean 65.48% against the entering list at 68.18%.
Neutralization Zone counters: neutralization_zone 7.91 → 0.26.
End reasons: empty 15.81% → 18.95% (+3.14%); foe_decked 52.11% → 50.14% (-1.97%); prizes 24.21% → 22.47% (-1.74%); decked 7.21% → 7.75% (+0.54%).
Replacing one Neutralization Zone with Cursed Shovel leaves the weighted rate lower (-1.95%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.17 a game, counting both players.

#### Also Pichu (-2.13%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -2.13%, gap SE 0.66%, -3.22 combined standard errors.

Weighted contributions: Celebi Mill +0.26%, 二森林 +0.19%, Set M Standard 60 (Mew ex / Spiky Energy) -1.04%, Carpet Set G (Clefairy / Ledian 60) -0.74%.
Unweighted mean 66.96% against the entering list at 68.18%.
Pichu counters: playground 1.84 → 0.69.
End reasons: empty 15.81% → 23.14% (+7.33%); prizes 24.21% → 19.33% (-4.88%); foe_decked 52.11% → 49.95% (-2.16%); decked 7.21% → 6.81% (-0.40%).
Replacing one Pichu with Cursed Shovel leaves the weighted rate lower (-2.13%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.16 a game, counting both players.

#### Also Double Turbo Energy (-2.30%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Double Turbo Energy: "As long as this card is attached to a Pokémon, it provides Colorless Colorless Energy. The attacks of the Pokémon this card is attached to do 20 less damage to your opponent's Active Pokémon (before applying Weakness and Resistance)."

The score uses the 0-copy loss weights. Against the list entering the step, -2.30%, gap SE 0.66%, -3.47 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.22%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.06%, Mega Starmie ex (Kudo) -0.87%, Carpet Set G (Clefairy / Ledian 60) -0.38%.
Unweighted mean 66.75% against the entering list at 68.18%.
The sample has no counter for Double Turbo Energy.
End reasons: foe_decked 52.11% → 49.70% (-2.41%); empty 15.81% → 17.00% (+1.19%); decked 7.21% → 8.01% (+0.80%); prizes 24.21% → 24.55% (+0.34%).
Replacing one Double Turbo Energy with Cursed Shovel leaves the weighted rate lower (-2.30%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.16 a game, counting both players.

#### Also Wiglett (-2.40%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wiglett: "Twisting Strike: Flip a coin. If heads, during your opponent's next turn, prevent all damage from and effects of attacks done to this Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -2.40%, gap SE 0.67%, -3.60 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) -0.48%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) -0.29%.
Unweighted mean 66.13% against the entering list at 68.18%.
The sample has no counter for Wiglett.
End reasons: empty 15.81% → 18.93% (+3.11%); foe_decked 52.11% → 49.60% (-2.51%); prizes 24.21% → 22.67% (-1.54%); decked 7.21% → 7.87% (+0.66%).
Replacing one Wiglett with Cursed Shovel leaves the weighted rate lower (-2.40%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.18 a game, counting both players.

#### Also Victini (-2.86%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -2.86%, gap SE 0.67%, -4.28 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.09%, Carpet Set G (Clefairy / Ledian 60) -0.65%, Set M Standard 60 (Mew ex / Spiky Energy) -0.55%.
Unweighted mean 65.87% against the entering list at 68.18%.
Victini counters: victory_star_reflip 1.07 → 0.20.
End reasons: empty 15.81% → 19.10% (+3.29%); foe_decked 52.11% → 49.21% (-2.90%); prizes 24.21% → 22.72% (-1.49%); decked 7.21% → 8.18% (+0.97%).
Replacing one Victini with Cursed Shovel leaves the weighted rate lower (-2.86%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.18 a game, counting both players.

### 4 Cursed Shovel, cut Crushing Hammer

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the start, +1.82%, gap SE 0.66%, 2.75 combined standard errors. Against the previous count, +0.57%, gap SE 0.67%, 0.85 combined standard errors.
Copy 4 gains +1.82% over the start. Copy 1 gains +1.82%. The higher count gained more. Unrounded, copy 4 leads by +0.0048%.
The step gain at copy 4 is +0.57%. The step gain at copy 2 is -0.04%. The later step gained more.

Against the previous count, the weighted move is Mill +0.39% of the weighted rate; 二森林 +0.25% of the weighted rate; Set D Standard 60 (Charm Ogerpon) +0.19% of the weighted rate; Worlds 2026 Hedrick Dragapult -0.26% of the weighted rate; Set M Standard 60 (Mew ex / Spiky Energy) -0.14% of the weighted rate; Celebi Mill -0.10% of the weighted rate.

The unweighted mean is 68.11% against 67.69% on the previous count and 66.96% on the start. The keeper is the 0-copy loss weights.

Cursed Shovel counters: shovel_mill 0.54 → 0.68, tool:Cursed Shovel 1.09 → 1.41.
Crushing Hammer counters: crushing_hammer_heads 0.79 → 0.62, crushing_hammer_tails 0.77 → 0.64.
Line counters, on the same weights: mill_opponent 21.97 → 21.99, mill_attack 5.01 → 5.11, shovel_mill 0.54 → 0.68, tool:Cursed Shovel 1.09 → 1.41, hilda 1.36 → 1.32, wally 0.20 → 0.19, eeeeeeek_shuffle 0.30 → 0.29.
Those counters moved, and the weighted win rate did not clear one combined standard error.

End reasons, weighted with the 0-copy vector, from Mill's seat: foe_decked 51.52% → 52.13% (+0.61%); decked 7.93% → 7.41% (-0.52%); empty 15.92% → 16.13% (+0.21%); prizes 23.88% → 23.67% (-0.21%).

Replacing one Crushing Hammer with Cursed Shovel leaves the weighted rate higher (+0.57%), with the largest piece on Mill, and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.15 a game, counting both players.

#### Also Wiglett (-0.76%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Wiglett: "Twisting Strike: Flip a coin. If heads, during your opponent's next turn, prevent all damage from and effects of attacks done to this Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -0.76%, gap SE 0.67%, -1.14 combined standard errors.

Weighted contributions: Mill +0.30%, 二森林 +0.23%, Set C Standard 60 (Clefairy / Mewtwo) -0.35%, Set M Standard 60 (Mew ex / Spiky Energy) -0.31%.
Unweighted mean 67.09% against the entering list at 67.69%.
The sample has no counter for Wiglett.
End reasons: empty 15.92% → 18.01% (+2.09%); prizes 23.88% → 22.79% (-1.09%); foe_decked 51.52% → 50.83% (-0.69%); decked 7.93% → 7.66% (-0.27%).
Replacing one Wiglett with Cursed Shovel leaves the weighted rate lower (-0.76%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.33 a game and shovel mills move +0.17 a game, counting both players.

#### Also Neutralization Zone (-0.83%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -0.83%, gap SE 0.67%, -1.24 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +1.74%, Mill +0.51%, Mega Starmie ex (Kudo) -1.46%, Set T Standard 60 (Dragapult ex) -1.13%.
Unweighted mean 65.82% against the entering list at 67.69%.
Neutralization Zone counters: neutralization_zone 7.85 → 0.26.
End reasons: empty 15.92% → 17.91% (+1.99%); foe_decked 51.52% → 50.77% (-0.74%); decked 7.93% → 7.30% (-0.63%); prizes 23.88% → 23.36% (-0.52%).
Replacing one Neutralization Zone with Cursed Shovel leaves the weighted rate lower (-0.83%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.19 a game, counting both players.

#### Also Double Turbo Energy (-0.86%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Double Turbo Energy: "As long as this card is attached to a Pokémon, it provides Colorless Colorless Energy. The attacks of the Pokémon this card is attached to do 20 less damage to your opponent's Active Pokémon (before applying Weakness and Resistance)."

The score uses the 0-copy loss weights. Against the list entering the step, -0.86%, gap SE 0.67%, -1.29 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.20%, Set M Standard 60 (Mew ex / Spiky Energy) +0.08%, Mega Starmie ex (Kudo) -0.46%, Worlds 2026 Hedrick Dragapult -0.30%.
Unweighted mean 67.03% against the entering list at 67.69%.
The sample has no counter for Double Turbo Energy.
End reasons: foe_decked 51.52% → 50.65% (-0.87%); decked 7.93% → 8.33% (+0.40%); prizes 23.88% → 24.14% (+0.26%); empty 15.92% → 16.14% (+0.23%).
Replacing one Double Turbo Energy with Cursed Shovel leaves the weighted rate lower (-0.86%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.36 a game and shovel mills move +0.17 a game, counting both players.

#### Also Ignition Energy (-0.87%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, -0.87%, gap SE 0.67%, -1.30 combined standard errors.

Weighted contributions: Mill +0.12%, Set T Standard 60 (Dragapult ex) +0.08%, Set M Standard 60 (Mew ex / Spiky Energy) -0.49%, Worlds 2026 Hedrick Dragapult -0.30%.
Unweighted mean 67.02% against the entering list at 67.69%.
The sample has no counter for Ignition Energy.
End reasons: foe_decked 51.52% → 50.74% (-0.77%); prizes 23.88% → 24.38% (+0.50%); empty 15.92% → 16.38% (+0.46%).
Replacing one Ignition Energy with Cursed Shovel leaves the weighted rate lower (-0.87%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.35 a game and shovel mills move +0.17 a game, counting both players.

#### Also Pichu (-1.25%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.25%, gap SE 0.66%, -1.88 combined standard errors.

Weighted contributions: Mill +0.39%, 二森林 +0.30%, Set M Standard 60 (Mew ex / Spiky Energy) -0.95%, Set C Standard 60 (Clefairy / Mewtwo) -0.68%.
Unweighted mean 67.21% against the entering list at 67.69%.
Pichu counters: playground 1.87 → 0.67.
End reasons: empty 15.92% → 23.25% (+7.33%); prizes 23.88% → 18.46% (-5.42%); foe_decked 51.52% → 50.23% (-1.28%); decked 7.93% → 7.29% (-0.64%).
Replacing one Pichu with Cursed Shovel leaves the weighted rate lower (-1.25%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.32 a game and shovel mills move +0.16 a game, counting both players.

#### Also Igglybuff (-1.32%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, -1.32%, gap SE 0.66%, -1.99 combined standard errors.

Weighted contributions: Mill +0.29%, 二森林 +0.13%, Set M Standard 60 (Mew ex / Spiky Energy) -0.69%, Worlds 2026 Hedrick Dragapult -0.40%.
Unweighted mean 66.74% against the entering list at 67.69%.
Igglybuff counters: sleepy_flip 1.40 → 0.06, sleepy_heads 0.69 → 0.03.
End reasons: empty 15.92% → 20.54% (+4.62%); prizes 23.88% → 21.20% (-2.68%); foe_decked 51.52% → 50.14% (-1.38%); decked 7.93% → 7.40% (-0.53%).
Replacing one Igglybuff with Cursed Shovel leaves the weighted rate lower (-1.32%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.26 a game and shovel mills move +0.16 a game, counting both players.

#### Also Lillie's Determination (-1.89%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead."

The score uses the 0-copy loss weights. Against the list entering the step, -1.89%, gap SE 0.67%, -2.84 combined standard errors.

Weighted contributions: 二森林 +0.26%, Mill +0.06%, Carpet Set G (Clefairy / Ledian 60) -0.59%, Mega Starmie ex (Kudo) -0.58%.
Unweighted mean 66.23% against the entering list at 67.69%.
The sample has no counter for Lillie's Determination.
End reasons: empty 15.92% → 18.00% (+2.08%); foe_decked 51.52% → 49.66% (-1.85%); decked 7.93% → 7.65% (-0.28%).
Replacing one Lillie's Determination with Cursed Shovel leaves the weighted rate lower (-1.89%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.21 a game and shovel mills move +0.13 a game, counting both players.

#### Also Cleffa (-2.20%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -2.20%, gap SE 0.66%, -3.33 combined standard errors.

Weighted contributions: Mill +0.28%, 二森林 +0.16%, Set M Standard 60 (Mew ex / Spiky Energy) -1.18%, Set C Standard 60 (Clefairy / Mewtwo) -0.70%.
Unweighted mean 66.40% against the entering list at 67.69%.
Cleffa counters: eeeeeeek_shuffle 0.30 → 0.03.
End reasons: foe_decked 51.52% → 49.38% (-2.14%); empty 15.92% → 17.80% (+1.89%); prizes 23.88% → 24.59% (+0.71%); decked 7.93% → 7.52% (-0.41%).
Replacing one Cleffa with Cursed Shovel leaves the weighted rate lower (-2.20%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. The printed Knock Out mills 2. On these weights, attaches move +0.26 a game and shovel mills move +0.17 a game, counting both players.

#### Also Victini (-2.45%)

Cursed Shovel: "If the Pokémon this card is attached to is Knocked Out by damage from an opponent's attack, discard the top 2 cards of your opponent's deck." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -2.45%, gap SE 0.66%, -3.70 combined standard errors.

Weighted contributions: 二森林 +0.09%, Set S Standard 60 (Floragato hunter) +0.07%, Set M Standard 60 (Mew ex / Spiky Energy) -0.86%, Worlds 2026 Hedrick Dragapult -0.38%.
Unweighted mean 66.07% against the entering list at 67.69%.
Victini counters: victory_star_reflip 1.08 → 0.20.
End reasons: empty 15.92% → 19.70% (+3.78%); foe_decked 51.52% → 49.15% (-2.36%); prizes 23.88% → 22.22% (-1.66%); decked 7.93% → 8.24% (+0.31%).
Replacing one Victini with Cursed Shovel leaves the weighted rate lower (-2.45%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. The printed Knock Out mills 2. On these weights, attaches move +0.34 a game and shovel mills move +0.19 a game, counting both players.

## Step 1

List entering this step: weighted 50.65%. Each row replaces one copy of that card with one Cursed Shovel. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards | Shovel | Attaches |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Buddy-Buddy Poffin | 4 | 52.47% | 0.48% | 67.92% | 18.38% | +1.82% | +1.82% | 21.43 | 0.20 | 0.38 |
| Crushing Hammer | 4 | 52.18% | 0.47% | 68.02% | 16.12% | +1.52% | +1.52% | 21.66 | 0.20 | 0.37 |
| Colress's Tenacity | 4 | 52.15% | 0.47% | 67.84% | 16.62% | +1.49% | +1.49% | 21.34 | 0.20 | 0.38 |
| Cleffa | 1 | 52.10% | 0.47% | 68.18% | 18.12% | +1.45% | +1.45% | 21.35 | 0.19 | 0.35 |
| Wally | 2 | 52.10% | 0.48% | 67.85% | 20.12% | +1.44% | +1.44% | 21.35 | 0.20 | 0.37 |
| Water Energy | 3 | 52.09% | 0.47% | 67.87% | 18.62% | +1.44% | +1.44% | 21.42 | 0.19 | 0.37 |
| Ignition Energy | 2 | 52.06% | 0.47% | 67.76% | 18.00% | +1.40% | +1.40% | 21.28 | 0.21 | 0.38 |
| Pichu | 1 | 52.01% | 0.47% | 68.19% | 16.75% | +1.35% | +1.35% | 21.25 | 0.20 | 0.37 |
| Miss Fortune Sisters | 2 | 51.92% | 0.47% | 68.04% | 16.75% | +1.27% | +1.27% | 21.78 | 0.21 | 0.38 |
| Level Ball | 4 | 51.65% | 0.47% | 67.59% | 18.88% | +1.00% | +1.00% | 21.21 | 0.19 | 0.36 |
| Reversal Energy | 4 | 51.49% | 0.47% | 67.51% | 19.38% | +0.84% | +0.84% | 21.27 | 0.20 | 0.37 |
| Team Rocket's Handiwork | 2 | 51.33% | 0.47% | 67.59% | 15.75% | +0.68% | +0.68% | 21.24 | 0.21 | 0.39 |
| Mime Jr. | 1 | 51.32% | 0.47% | 67.65% | 18.75% | +0.67% | +0.67% | 21.57 | 0.20 | 0.37 |
| Lillie's Poké Doll | 1 | 51.24% | 0.47% | 67.46% | 18.25% | +0.58% | +0.58% | 21.39 | 0.20 | 0.37 |
| Double Turbo Energy | 4 | 51.23% | 0.47% | 67.23% | 17.25% | +0.58% | +0.58% | 21.15 | 0.20 | 0.38 |
| Slumbering Forest | 1 | 51.19% | 0.46% | 67.80% | 11.50% | +0.54% | +0.54% | 21.50 | 0.20 | 0.37 |
| Rescue Carrier | 3 | 51.19% | 0.47% | 67.24% | 17.75% | +0.53% | +0.53% | 21.40 | 0.20 | 0.37 |
| Igglybuff | 1 | 50.97% | 0.47% | 67.21% | 16.50% | +0.32% | +0.32% | 21.96 | 0.19 | 0.35 |
| Lillie's Determination | 2 | 50.88% | 0.47% | 67.11% | 16.50% | +0.22% | +0.22% | 21.09 | 0.18 | 0.34 |
| Hilda | 4 | 50.87% | 0.48% | 66.86% | 19.37% | +0.21% | +0.21% | 21.27 | 0.20 | 0.38 |
| Wiglett | 4 | 50.84% | 0.47% | 67.29% | 16.62% | +0.19% | +0.19% | 20.78 | 0.20 | 0.38 |
| Wugtrio | 4 | 50.72% | 0.47% | 67.04% | 17.00% | +0.07% | +0.07% | 21.22 | 0.20 | 0.38 |
| Neutralization Zone | 1 | 49.92% | 0.48% | 65.34% | 25.87% | -0.74% | -0.74% | 21.16 | 0.20 | 0.38 |
| Victini | 1 | 49.13% | 0.46% | 66.23% | 15.00% | -1.52% | -1.52% | 20.83 | 0.21 | 0.38 |

Kept −Buddy-Buddy Poffin at 52.47% (+1.82%, gap SE 0.66%, 2.74 combined standard errors).

The unweighted mean would keep Pichu at 68.19% instead of Buddy-Buddy Poffin at 67.92%. The foes ahead on that cut are Set S Standard 60 (Floragato hunter) +3.75%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +3.12%, Set T Standard 60 (Dragapult ex) +2.37%, Celebi Mill +1.88%.

## Step 2

List entering this step: weighted 52.47%. Each row replaces one copy of that card with one Cursed Shovel. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards | Shovel | Attaches |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Mime Jr. | 1 | 52.43% | 0.48% | 68.18% | 19.62% | -0.04% | +1.78% | 21.74 | 0.38 | 0.73 |
| Wugtrio | 4 | 52.09% | 0.47% | 67.86% | 19.88% | -0.38% | +1.43% | 21.33 | 0.37 | 0.73 |
| Rescue Carrier | 3 | 51.95% | 0.47% | 68.02% | 16.38% | -0.52% | +1.30% | 21.32 | 0.38 | 0.73 |
| Cleffa | 1 | 51.80% | 0.47% | 67.64% | 20.75% | -0.67% | +1.15% | 21.35 | 0.37 | 0.70 |
| Hilda | 4 | 51.71% | 0.47% | 67.64% | 19.25% | -0.76% | +1.05% | 21.27 | 0.38 | 0.73 |
| Wally | 2 | 51.65% | 0.48% | 67.25% | 19.12% | -0.82% | +1.00% | 21.43 | 0.38 | 0.73 |
| Crushing Hammer | 4 | 51.51% | 0.47% | 67.41% | 18.00% | -0.96% | +0.86% | 21.51 | 0.38 | 0.73 |
| Miss Fortune Sisters | 2 | 51.48% | 0.47% | 67.59% | 17.50% | -0.99% | +0.82% | 21.76 | 0.38 | 0.73 |
| Lillie's Poké Doll | 1 | 51.35% | 0.47% | 67.36% | 19.62% | -1.12% | +0.70% | 21.45 | 0.37 | 0.72 |
| Ignition Energy | 2 | 51.30% | 0.47% | 67.38% | 18.62% | -1.17% | +0.64% | 21.28 | 0.38 | 0.74 |
| Double Turbo Energy | 4 | 50.99% | 0.47% | 67.02% | 19.75% | -1.48% | +0.34% | 21.34 | 0.38 | 0.73 |
| Igglybuff | 1 | 50.98% | 0.47% | 66.93% | 16.88% | -1.49% | +0.33% | 22.06 | 0.37 | 0.70 |
| Level Ball | 4 | 50.85% | 0.47% | 66.94% | 18.88% | -1.62% | +0.19% | 21.11 | 0.37 | 0.71 |
| Slumbering Forest | 1 | 50.58% | 0.46% | 67.19% | 14.00% | -1.89% | -0.07% | 21.42 | 0.37 | 0.72 |
| Buddy-Buddy Poffin | 3 | 50.54% | 0.47% | 66.40% | 17.50% | -1.93% | -0.12% | 21.05 | 0.36 | 0.71 |
| Pichu | 1 | 50.49% | 0.46% | 67.16% | 16.00% | -1.98% | -0.16% | 20.81 | 0.37 | 0.72 |
| Reversal Energy | 4 | 50.44% | 0.47% | 66.80% | 18.38% | -2.03% | -0.21% | 21.08 | 0.38 | 0.73 |
| Water Energy | 3 | 50.40% | 0.47% | 66.80% | 17.38% | -2.07% | -0.26% | 21.27 | 0.38 | 0.73 |
| Team Rocket's Handiwork | 2 | 50.13% | 0.47% | 66.60% | 16.88% | -2.34% | -0.52% | 21.04 | 0.38 | 0.74 |
| Colress's Tenacity | 4 | 49.89% | 0.47% | 66.32% | 19.00% | -2.58% | -0.76% | 21.15 | 0.37 | 0.71 |
| Lillie's Determination | 2 | 49.89% | 0.47% | 66.32% | 16.12% | -2.58% | -0.76% | 21.18 | 0.36 | 0.67 |
| Neutralization Zone | 1 | 49.41% | 0.47% | 65.05% | 21.88% | -3.06% | -1.25% | 21.26 | 0.38 | 0.71 |
| Wiglett | 4 | 49.37% | 0.47% | 65.89% | 16.25% | -3.10% | -1.29% | 20.73 | 0.38 | 0.72 |
| Victini | 1 | 48.27% | 0.46% | 65.36% | 14.25% | -4.20% | -2.38% | 20.79 | 0.39 | 0.72 |

Kept −Mime Jr. at 52.43% (-0.04%, gap SE 0.67%, -0.06 combined standard errors).

The unweighted mean keeps the same cut.

## Step 3

List entering this step: weighted 52.43%. Each row replaces one copy of that card with one Cursed Shovel. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards | Shovel | Attaches |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wally | 2 | 51.90% | 0.48% | 67.69% | 18.75% | -0.53% | +1.25% | 21.97 | 0.54 | 1.09 |
| Rescue Carrier | 3 | 51.74% | 0.48% | 67.31% | 21.75% | -0.69% | +1.09% | 21.91 | 0.55 | 1.08 |
| Ignition Energy | 2 | 51.71% | 0.47% | 67.68% | 19.62% | -0.72% | +1.06% | 21.78 | 0.55 | 1.08 |
| Level Ball | 4 | 51.69% | 0.48% | 67.32% | 20.00% | -0.74% | +1.03% | 21.60 | 0.53 | 1.06 |
| Miss Fortune Sisters | 2 | 51.65% | 0.47% | 67.59% | 19.00% | -0.78% | +0.99% | 22.11 | 0.55 | 1.08 |
| Lillie's Poké Doll | 1 | 51.50% | 0.47% | 67.61% | 17.75% | -0.94% | +0.84% | 21.90 | 0.54 | 1.06 |
| Igglybuff | 1 | 51.41% | 0.47% | 67.26% | 19.75% | -1.02% | +0.76% | 22.58 | 0.53 | 1.02 |
| Hilda | 4 | 51.40% | 0.48% | 67.38% | 19.50% | -1.03% | +0.74% | 21.56 | 0.56 | 1.10 |
| Crushing Hammer | 4 | 51.35% | 0.47% | 67.55% | 16.25% | -1.08% | +0.70% | 21.88 | 0.52 | 1.05 |
| Buddy-Buddy Poffin | 3 | 51.18% | 0.47% | 67.19% | 19.75% | -1.25% | +0.52% | 21.53 | 0.53 | 1.06 |
| Team Rocket's Handiwork | 2 | 51.17% | 0.47% | 67.27% | 18.88% | -1.26% | +0.52% | 21.54 | 0.54 | 1.06 |
| Water Energy | 3 | 51.17% | 0.47% | 67.35% | 19.75% | -1.26% | +0.52% | 21.61 | 0.55 | 1.09 |
| Colress's Tenacity | 4 | 51.08% | 0.47% | 67.06% | 18.50% | -1.36% | +0.42% | 21.66 | 0.53 | 1.07 |
| Wugtrio | 4 | 51.07% | 0.47% | 67.08% | 18.50% | -1.36% | +0.42% | 21.47 | 0.54 | 1.08 |
| Slumbering Forest | 1 | 51.03% | 0.45% | 68.05% | 10.00% | -1.40% | +0.37% | 21.66 | 0.54 | 1.06 |
| Lillie's Determination | 2 | 50.86% | 0.47% | 66.91% | 17.12% | -1.57% | +0.21% | 21.52 | 0.52 | 0.98 |
| Reversal Energy | 4 | 50.72% | 0.47% | 66.91% | 20.50% | -1.71% | +0.07% | 21.47 | 0.55 | 1.08 |
| Cleffa | 1 | 50.54% | 0.47% | 67.10% | 19.25% | -1.89% | -0.11% | 21.66 | 0.53 | 1.00 |
| Neutralization Zone | 1 | 50.48% | 0.48% | 65.48% | 24.75% | -1.95% | -0.17% | 21.49 | 0.55 | 1.06 |
| Pichu | 1 | 50.30% | 0.46% | 66.96% | 18.38% | -2.13% | -0.35% | 21.28 | 0.54 | 1.05 |
| Double Turbo Energy | 4 | 50.14% | 0.47% | 66.75% | 17.12% | -2.30% | -0.52% | 21.43 | 0.54 | 1.08 |
| Wiglett | 4 | 50.03% | 0.47% | 66.13% | 18.12% | -2.40% | -0.62% | 21.23 | 0.56 | 1.07 |
| Victini | 1 | 49.57% | 0.47% | 65.87% | 20.25% | -2.86% | -1.08% | 21.34 | 0.56 | 1.07 |

Kept −Wally at 51.90% (-0.53%, gap SE 0.67%, -0.79 combined standard errors).

The unweighted mean would keep Slumbering Forest at 68.05% instead of Wally at 67.69%. The foes ahead on that cut are 二森林 +9.75%, Set T Standard 60 (Dragapult ex) +4.88%, Celebi Mill +4.88%, Mill +4.75%.

## Step 4

List entering this step: weighted 51.90%. Each row replaces one copy of that card with one Cursed Shovel. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards | Shovel | Attaches |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Crushing Hammer | 4 | 52.47% | 0.48% | 68.11% | 20.00% | +0.57% | +1.82% | 21.99 | 0.68 | 1.41 |
| Miss Fortune Sisters | 2 | 52.44% | 0.48% | 68.04% | 20.75% | +0.54% | +1.79% | 22.41 | 0.69 | 1.42 |
| Rescue Carrier | 3 | 52.36% | 0.48% | 68.02% | 18.75% | +0.45% | +1.70% | 21.81 | 0.70 | 1.43 |
| Water Energy | 3 | 52.29% | 0.48% | 67.79% | 23.00% | +0.39% | +1.64% | 21.89 | 0.69 | 1.44 |
| Lillie's Poké Doll | 1 | 52.13% | 0.48% | 67.71% | 20.12% | +0.23% | +1.48% | 22.12 | 0.68 | 1.39 |
| Reversal Energy | 4 | 51.75% | 0.48% | 67.39% | 21.50% | -0.15% | +1.10% | 21.87 | 0.70 | 1.44 |
| Colress's Tenacity | 4 | 51.66% | 0.48% | 67.33% | 20.38% | -0.25% | +1.00% | 21.87 | 0.70 | 1.44 |
| Wugtrio | 4 | 51.60% | 0.47% | 67.52% | 17.62% | -0.30% | +0.95% | 21.80 | 0.71 | 1.45 |
| Slumbering Forest | 1 | 51.57% | 0.46% | 68.08% | 13.50% | -0.33% | +0.92% | 22.00 | 0.70 | 1.40 |
| Wally | 1 | 51.56% | 0.48% | 67.21% | 19.88% | -0.34% | +0.91% | 21.88 | 0.70 | 1.44 |
| Hilda | 4 | 51.52% | 0.47% | 67.49% | 18.50% | -0.38% | +0.87% | 21.72 | 0.71 | 1.43 |
| Team Rocket's Handiwork | 2 | 51.49% | 0.47% | 67.46% | 18.38% | -0.41% | +0.84% | 21.72 | 0.70 | 1.44 |
| Level Ball | 4 | 51.41% | 0.48% | 67.21% | 20.88% | -0.49% | +0.76% | 21.72 | 0.70 | 1.41 |
| Buddy-Buddy Poffin | 3 | 51.27% | 0.47% | 67.15% | 18.62% | -0.64% | +0.61% | 21.71 | 0.69 | 1.39 |
| Wiglett | 4 | 51.14% | 0.47% | 67.09% | 18.88% | -0.76% | +0.49% | 21.46 | 0.71 | 1.42 |
| Neutralization Zone | 1 | 51.07% | 0.48% | 65.82% | 24.00% | -0.83% | +0.42% | 21.85 | 0.72 | 1.42 |
| Double Turbo Energy | 4 | 51.04% | 0.47% | 67.03% | 18.25% | -0.86% | +0.39% | 21.63 | 0.71 | 1.45 |
| Ignition Energy | 2 | 51.04% | 0.47% | 67.02% | 18.75% | -0.87% | +0.38% | 21.80 | 0.70 | 1.44 |
| Pichu | 1 | 50.66% | 0.47% | 67.21% | 19.88% | -1.25% | +0.00% | 21.68 | 0.70 | 1.40 |
| Igglybuff | 1 | 50.58% | 0.47% | 66.74% | 19.00% | -1.32% | -0.07% | 22.46 | 0.70 | 1.35 |
| Lillie's Determination | 2 | 50.01% | 0.47% | 66.23% | 19.00% | -1.89% | -0.64% | 21.40 | 0.66 | 1.30 |
| Cleffa | 1 | 49.70% | 0.47% | 66.40% | 19.25% | -2.20% | -0.95% | 21.80 | 0.70 | 1.34 |
| Victini | 1 | 49.46% | 0.47% | 66.07% | 16.88% | -2.45% | -1.20% | 21.30 | 0.72 | 1.43 |

Kept −Crushing Hammer at 52.47% (+0.57%, gap SE 0.67%, 0.85 combined standard errors).

The unweighted mean keeps the same cut.

## Unweighted mean across counts

The unweighted mean would keep 2 copies at 68.18% instead of 4 copies at 68.11%. The keeper stays the 0-copy loss weights.
The foes ahead on the mean's count are Celebi Mill +2.38%, Mega Starmie ex (Kudo) +1.87%, 二森林 +1.13%, Set T Standard 60 (Dragapult ex) +0.88%, Worlds 2026 Hedrick Dragapult +0.88%.

## Foes at the kept list

A parked foe repeats its 0-copy rate. Delta is against the start.

| Foe | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Set D Standard 60 (Charm Ogerpon) | 15.1090% | 20.50% | 19.50% | 20.00% | +4.88% |
| Set M Standard 60 (Mew ex / Spiky Energy) | 12.2608% | 33.50% | 31.25% | 32.38% | +1.25% |
| Mega Starmie ex (Kudo) | 11.5487% | 36.75% | 34.75% | 35.75% | +0.63% |
| Mill | 8.9008% | 50.50% | 52.50% | 51.50% | +1.50% |
| Carpet Set G (Clefairy / Ledian 60) | 8.7005% | 56.00% | 52.50% | 54.25% | +3.12% |
| Set C Standard 60 (Clefairy / Mewtwo) | 8.3000% | 55.75% | 56.00% | 55.88% | +2.50% |
| Celebi Mill | 5.4072% | 72.00% | 70.75% | 71.38% | +1.75% |
| 二森林 | 5.1624% | 74.50% | 70.50% | 72.50% | +1.50% |
| Worlds 2026 Hedrick Dragapult | 4.6951% | 70.00% | 71.25% | 70.62% | -3.00% |
| Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | 4.2056% | 77.75% | 75.00% | 76.38% | +0.00% |
| Set S Standard 60 (Floragato hunter) | 3.9608% | 81.00% | 80.75% | 80.88% | +3.12% |
| Set T Standard 60 (Dragapult ex) | 3.8051% | 79.75% | 82.25% | 81.00% | +2.38% |
| Unlimited Dragapult (Pidgeot / Rotom V) | 2.8037% | 85.75% | 82.75% | 84.25% | +0.00% |
| Chris Brewer Lucario Hariyama | 2.6035% | 84.25% | 86.50% | 85.38% | +0.00% |
| Iron Thorns ex | 1.0458% | 95.25% | 93.00% | 94.12% | +0.00% |
| Doll | 0.7788% | 95.75% | 95.50% | 95.62% | +0.00% |
| Unlimited 60 (Ambipom Hand Fling) | 0.7121% | 95.25% | 96.75% | 96.00% | +0.00% |
