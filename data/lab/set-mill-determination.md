# Mill, Lillie's Determination

Each step replaces one copy of one other card with one Lillie's Determination. The cut with the higher win rate under the 0-copy loss weights is kept. The next copy is measured on that list, through four copies, including when a copy lowers the rate. The kept count is the one whose gain over the starting list is the largest.

Printed sentence: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead."

The starting 60 is the Wiglett Mill before this card, four Hilda and zero Lillie's Determination. Mill's strategy already plays a Supporter the picker selects. This search does not add a strategy branch. The lock written after the sample is the three-copy list.

- **Seed**: `20261116`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from this starting list's own losses. A foe it loses more often counts more.
- **Elapsed**: 14793.1s
- **Streams**: each cell starts with `random.Random(20261116)`. Two lists diverge after the first choice that consumes a different number of draws.

The weight of a foe is `max(1e-6, 1 - win rate)` divided by the sum of those values. The script divides. The Sisters weights in `data/lab/set-mill-sleep.md` are not this vector.

The active set is the weight prefix that first reaches 90%. Its cumulative weight is 91.77%. Later cells are played only against that set. A parked foe keeps its 0-copy win rate and its weight. It is not played again.

## 0-copy pass

Every live 60-card deck that is not archived. Card count is the registry length. Mega Starmie and Iron Thorns are included while they are not seed keys.

| Key | Deck | Cards | Strategy | A | B | Mean | Weight |
| :--- | :--- | ---: | :--- | ---: | ---: | ---: | ---: |
| d60 | Set D Standard 60 (Charm Ogerpon) | 60 | demolish | 13.50% | 13.50% | 13.50% | 14.7485% (active) |
| m60 | Set M Standard 60 (Mew ex / Spiky Energy) | 60 | mew_baby | 29.00% | 31.25% | 30.12% | 11.9139% (active) |
| starmie | Mega Starmie ex (Kudo) | 60 | starmie | 41.50% | 32.75% | 37.12% | 10.7204% (active) |
| g | Carpet Set G (Clefairy / Ledian 60) | 60 | g | 42.50% | 48.25% | 45.38% | 9.3137% (active) |
| c60 | Set C Standard 60 (Clefairy / Mewtwo) | 60 | party | 49.75% | 47.00% | 48.38% | 8.8022% (active) |
| mill | Mill | 60 | mill | 53.75% | 46.25% | 50.00% | 8.5251% (active) |
| h | Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | 60 | nuzzle | 66.25% | 64.25% | 65.25% | 5.9250% (active) |
| t-meta | Worlds 2026 Hedrick Dragapult | 60 | phantom | 67.75% | 67.50% | 67.62% | 5.5200% (active) |
| celebi | Celebi Mill | 60 | roast | 75.75% | 73.75% | 74.75% | 4.3052% (active) |
| two-forest | 二森林 | 60 | roast | 74.00% | 75.50% | 74.75% | 4.3052% (active) |
| t60 | Set T Standard 60 (Dragapult ex) | 60 | phantom | 75.50% | 78.50% | 77.00% | 3.9216% (active) |
| s60 | Set S Standard 60 (Floragato hunter) | 60 | slash | 76.25% | 79.50% | 77.88% | 3.7724% (active) |
| l60 | Chris Brewer Lucario Hariyama | 60 | aura | 83.00% | 82.75% | 82.88% | 2.9199% (parked) |
| t-unl | Unlimited Dragapult (Pidgeot / Rotom V) | 60 | phantom | 85.25% | 85.75% | 85.50% | 2.4723% (parked) |
| thorns | Iron Thorns ex | 60 | thorns | 95.25% | 89.25% | 92.25% | 1.3214% (parked) |
| doll | Doll | 60 | doll | 94.75% | 95.75% | 95.25% | 0.8099% (parked) |
| g30 | Unlimited 60 (Ambipom Hand Fling) | 60 | celebration | 96.50% | 95.25% | 95.88% | 0.7033% (parked) |

Active set (91.77%): d60, m60, starmie, g, c60, mill, h, t-meta, celebi, two-forest, t60, s60.

Parked foes stay at the 0-copy rates below.

| Key | Deck | Weight | A | B | Mean |
| :--- | :--- | ---: | ---: | ---: | ---: |
| doll | Doll | 0.8099% | 94.75% | 95.75% | 95.25% |
| g30 | Unlimited 60 (Ambipom Hand Fling) | 0.7033% | 96.50% | 95.25% | 95.88% |
| l60 | Chris Brewer Lucario Hariyama | 2.9199% | 83.00% | 82.75% | 82.88% |
| t-unl | Unlimited Dragapult (Pidgeot / Rotom V) | 2.4723% | 85.25% | 85.75% | 85.50% |
| thorns | Iron Thorns ex | 1.3214% | 95.25% | 89.25% | 92.25% |

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

Delta start is against the 0-copy list. Delta step is against the previous count. Mill cards is `mill_opponent`. Mill has no counter for Lillie's Determination, so that sentence is not a column. The counters are weighted over every foe in the score, including a foe that mills or plays Hilda.

| Copies | Cut | Weighted | ± | Mean | Worst | Delta start | Delta step | Mill cards | Mill attacks | Hilda | Wally | Eeeeeeek |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | 49.50% | 0.46% | 65.50% | 13.50% | +0.00% | +0.00% | 20.43 | 4.36 | 1.27 | 0.35 | 0.29 |
| 1 | Ignition Energy | 51.57% | 0.46% | 67.00% | 16.00% | +2.08% | +2.08% | 20.62 | 4.38 | 1.32 | 0.34 | 0.29 |
| 2 | Pichu | 52.89% | 0.47% | 68.17% | 18.25% | +3.39% | +1.32% | 20.85 | 4.41 | 1.32 | 0.32 | 0.35 |
| 3 | Counter Catcher | 55.00% | 0.47% | 69.39% | 23.12% | +5.50% | +2.10% | 21.32 | 4.51 | 1.36 | 0.33 | 0.34 |
| 4 | Wugtrio | 55.29% | 0.47% | 69.64% | 20.75% | +5.79% | +0.29% | 21.17 | 4.48 | 1.40 | 0.33 | 0.37 |

## Decision

Kept count is 4 Lillie's Determination: weighted 55.29% against the start at 49.50% (+5.79%, gap SE 0.65%, 8.87 combined standard errors).

Copy 4 gains +5.79% over the start. Copy 1 gains +2.08%. The higher count gained more.
Copy 4 gains +5.79% over the start. Copy 2 gains +3.39%. The higher count gained more.
Copy 4 gains +5.79% over the start. Copy 3 gains +5.50%. The higher count gained more.

The step from 3 to 4 is +0.29%, gap SE 0.66%, 0.44 combined standard errors. That step does not clear one combined standard error. The kept count is still the one with the largest gain over the start.

Each step took the best cut on this seed, so that path sits a little high. Continuing through a dip does not remove that.

This file records the sample. It does not assign `SET_MILL_NAMES`.

The lock is that three-copy list: one Ignition Energy, Pichu, and Counter Catcher. Wugtrio stays at four. The fourth copy stays out of the lock.

Counts on the locked list:

- Mime Jr. ×1
- Cleffa ×1
- Wiglett ×4
- Wugtrio ×4
- Victini ×1
- Slumbering Forest ×1
- Neutralization Zone ×1
- Buddy-Buddy Poffin ×4
- Level Ball ×4
- Rescue Carrier ×3
- Lillie's Poké Doll ×1
- Crushing Hammer ×4
- Miss Fortune Sisters ×2
- Wally ×2
- Igglybuff ×1
- Team Rocket's Handiwork ×2
- Colress's Tenacity ×4
- Double Turbo Energy ×4
- Water Energy ×3
- Ignition Energy ×2
- Reversal Energy ×4
- Hilda ×4
- Lillie's Determination ×3

Counts on the four-copy sample list:

- Mime Jr. ×1
- Cleffa ×1
- Wiglett ×4
- Wugtrio ×3
- Victini ×1
- Slumbering Forest ×1
- Neutralization Zone ×1
- Buddy-Buddy Poffin ×4
- Level Ball ×4
- Rescue Carrier ×3
- Lillie's Poké Doll ×1
- Crushing Hammer ×4
- Miss Fortune Sisters ×2
- Wally ×2
- Igglybuff ×1
- Team Rocket's Handiwork ×2
- Colress's Tenacity ×4
- Double Turbo Energy ×4
- Water Energy ×3
- Ignition Energy ×2
- Reversal Energy ×4
- Hilda ×4
- Lillie's Determination ×4

### 1 Lillie's Determination, cut Ignition Energy

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the start, +2.08%, gap SE 0.65%, 3.20 combined standard errors. Against the previous count, +2.08%, gap SE 0.65%, 3.20 combined standard errors.

Against the previous count, the weighted move is Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.53% of the weighted rate; Carpet Set G (Clefairy / Ledian 60) +0.52% of the weighted rate; Set D Standard 60 (Charm Ogerpon) +0.37% of the weighted rate; 二森林 -0.12% of the weighted rate.

The unweighted mean is 67.00% against 65.50% on the previous count and 65.50% on the start. The keeper is the 0-copy loss weights.

The sample has no counter for Lillie's Determination on Mill. The engine bumps doll_determination only when the strategy is doll.
The sample has no counter for Ignition Energy.
Line counters, on the same weights: mill_opponent 20.43 → 20.62, mill_attack 4.36 → 4.38, hilda 1.27 → 1.32, wally 0.35 → 0.34, eeeeeeek_shuffle 0.29 → 0.29.

End reasons, weighted with the 0-copy vector, from Mill's seat: foe_decked 49.15% → 51.06% (+1.91%); empty 16.12% → 14.67% (-1.45%); prizes 26.97% → 26.45% (-0.52%).

Replacing one Ignition Energy with Lillie's Determination leaves the weighted rate higher (+2.08%), with the largest piece on Carpet Set H (Team Rocket's Zapdos / Pikachu 60), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Team Rocket's Handiwork (+1.89%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Team Rocket's Handiwork: "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.89%, gap SE 0.65%, 2.90 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.53%, Set C Standard 60 (Clefairy / Mewtwo) +0.40%, Celebi Mill -0.10%, Mega Starmie ex (Kudo) -0.08%.
Unweighted mean 66.84% against the entering list at 65.50%.
Team Rocket's Handiwork counters: handiwork 0.71 → 0.43, handiwork_tails 0.18 → 0.11.
End reasons: foe_decked 49.15% → 51.08% (+1.93%); empty 16.12% → 14.79% (-1.33%); prizes 26.97% → 26.52% (-0.45%).
Replacing one Team Rocket's Handiwork with Lillie's Determination leaves the weighted rate higher (+1.89%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wally (+1.49%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the list entering the step, +1.49%, gap SE 0.65%, 2.30 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.52%, Set D Standard 60 (Charm Ogerpon) +0.35%, Set M Standard 60 (Mew ex / Spiky Energy) -0.22%, 二森林 -0.15%.
Unweighted mean 66.60% against the entering list at 65.50%.
Wally counters: wally 0.35 → 0.22.
End reasons: empty 16.12% → 14.75% (-1.36%); foe_decked 49.15% → 50.49% (+1.34%); turn_prizes 0.94% → 0.74% (-0.20%).
Replacing one Wally with Lillie's Determination leaves the weighted rate higher (+1.49%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Mime Jr. (+1.44%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Mime Jr.: "Sweet Sleeping Face: As long as Mime Jr. is Asleep, prevent all damage done to Mime Jr. by attacks. Sleepy Lost: Put the top card of your opponent's deck in the Lost Zone. Mime Jr. is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.44%, gap SE 0.65%, 2.22 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.48%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.39%, Set M Standard 60 (Mew ex / Spiky Energy) -0.49%, Celebi Mill -0.03%.
Unweighted mean 66.67% against the entering list at 65.50%.
Mime Jr. counters: sleepy_lost 0.31 → 0.06, sleepy_lost_miss 0.00 → 0.00.
End reasons: foe_decked 49.15% → 50.56% (+1.41%); empty 16.12% → 15.22% (-0.89%); prizes 26.97% → 26.60% (-0.37%).
Replacing one Mime Jr. with Lillie's Determination leaves the weighted rate higher (+1.44%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Miss Fortune Sisters (+1.40%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Miss Fortune Sisters: "Look at the top 5 cards of your opponent's deck and discard any number of Item cards you find there. Your opponent shuffles the other cards back into their deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.40%, gap SE 0.65%, 2.15 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.53%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.41%, 二森林 -0.20%, Set M Standard 60 (Mew ex / Spiky Energy) -0.16%.
Unweighted mean 66.57% against the entering list at 65.50%.
Miss Fortune Sisters counters: sisters_item 1.11 → 0.68, sisters_miss 0.13 → 0.08.
End reasons: empty 16.12% → 14.36% (-1.76%); foe_decked 49.15% → 50.56% (+1.41%); prizes 26.97% → 27.39% (+0.42%); turn_prizes 0.94% → 0.74% (-0.21%).
Replacing one Miss Fortune Sisters with Lillie's Determination leaves the weighted rate higher (+1.40%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Pichu (+1.38%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.38%, gap SE 0.65%, 2.13 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.53%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.35%, Set M Standard 60 (Mew ex / Spiky Energy) -0.37%, Mega Starmie ex (Kudo) -0.29%.
Unweighted mean 66.89% against the entering list at 65.50%.
Pichu counters: playground 1.66 → 0.59.
End reasons: prizes 26.97% → 22.29% (-4.68%); empty 16.12% → 19.97% (+3.85%); foe_decked 49.15% → 50.46% (+1.31%); turn_prizes 0.94% → 0.65% (-0.30%).
Replacing one Pichu with Lillie's Determination leaves the weighted rate higher (+1.38%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Hilda (+1.24%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.24%, gap SE 0.65%, 1.91 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.42%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.37%, Set M Standard 60 (Mew ex / Spiky Energy) -0.10%, 二森林 -0.06%.
Unweighted mean 66.44% against the entering list at 65.50%.
Hilda counters: hilda 1.27 → 1.08, evo_from_hilda 1.13 → 0.98, energy_from_hilda 1.26 → 1.07.
End reasons: foe_decked 49.15% → 50.39% (+1.24%); empty 16.12% → 14.88% (-1.24%).
Replacing one Hilda with Lillie's Determination leaves the weighted rate higher (+1.24%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Rescue Carrier (+1.21%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Rescue Carrier: "Put up to 2 Pokémon, each with 90 HP or less, from your discard pile into your hand."

The score uses the 0-copy loss weights. Against the list entering the step, +1.21%, gap SE 0.65%, 1.85 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.40%, Set D Standard 60 (Charm Ogerpon) +0.24%, 二森林 -0.18%, Mill -0.10%.
Unweighted mean 66.37% against the entering list at 65.50%.
Rescue Carrier counters: rescue_carrier 1.51 → 1.22.
End reasons: prizes 26.97% → 25.51% (-1.46%); foe_decked 49.15% → 50.38% (+1.23%); decked 6.45% → 6.67% (+0.23%).
Replacing one Rescue Carrier with Lillie's Determination leaves the weighted rate higher (+1.21%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Water Energy (+1.18%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, +1.18%, gap SE 0.65%, 1.81 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.61%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.36%, Celebi Mill -0.23%, Mega Starmie ex (Kudo) -0.19%.
Unweighted mean 66.26% against the entering list at 65.50%.
The sample has no counter for Water Energy.
End reasons: empty 16.12% → 14.94% (-1.18%); foe_decked 49.15% → 50.30% (+1.15%); decked 6.45% → 6.75% (+0.30%); turn_prizes 0.94% → 0.70% (-0.25%).
Replacing one Water Energy with Lillie's Determination leaves the weighted rate higher (+1.18%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Cleffa (+1.15%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.15%, gap SE 0.65%, 1.76 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.68%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.61%, Set M Standard 60 (Mew ex / Spiky Energy) -0.57%, 二森林 -0.15%.
Unweighted mean 66.56% against the entering list at 65.50%.
Cleffa counters: eeeeeeek_shuffle 0.29 → 0.03.
End reasons: foe_decked 49.15% → 50.30% (+1.15%); prizes 26.97% → 25.90% (-1.07%); turn_prizes 0.94% → 0.72% (-0.22%).
Replacing one Cleffa with Lillie's Determination leaves the weighted rate higher (+1.15%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Colress's Tenacity (+0.90%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.90%, gap SE 0.65%, 1.39 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.42%, Set C Standard 60 (Clefairy / Mewtwo) +0.41%, Set M Standard 60 (Mew ex / Spiky Energy) -0.22%, Mill -0.19%.
Unweighted mean 66.10% against the entering list at 65.50%.
Colress's Tenacity counters: colress 1.35 → 1.11.
End reasons: empty 16.12% → 14.86% (-1.25%); foe_decked 49.15% → 50.04% (+0.89%); decked 6.45% → 6.86% (+0.41%).
Replacing one Colress's Tenacity with Lillie's Determination leaves the weighted rate higher (+0.90%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Level Ball (+0.87%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.87%, gap SE 0.65%, 1.34 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.56%, Set C Standard 60 (Clefairy / Mewtwo) +0.32%, Mega Starmie ex (Kudo) -0.47%, 二森林 -0.19%.
Unweighted mean 66.14% against the entering list at 65.50%.
Level Ball counters: level_ball 1.16 → 1.00.
End reasons: prizes 26.97% → 25.62% (-1.35%); foe_decked 49.15% → 50.06% (+0.91%); decked 6.45% → 6.81% (+0.37%); empty 16.12% → 16.32% (+0.20%).
Replacing one Level Ball with Lillie's Determination leaves the weighted rate higher (+0.87%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Counter Catcher (+0.72%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Counter Catcher: "You can use this card only if you have more Prize cards remaining than your opponent.

Switch in 1 of your opponent's Benched Pokémon to the Active Spot."

The score uses the 0-copy loss weights. Against the list entering the step, +0.72%, gap SE 0.65%, 1.11 combined standard errors.

Weighted contributions: Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.49%, Carpet Set G (Clefairy / Ledian 60) +0.38%, Set C Standard 60 (Clefairy / Mewtwo) -0.22%, 二森林 -0.19%.
Unweighted mean 66.06% against the entering list at 65.50%.
Counter Catcher counters: counter_catcher 0.16 → 0.01, counter_catcher_fail 0.00 → 0.00.
End reasons: foe_decked 49.15% → 49.87% (+0.72%); empty 16.12% → 15.41% (-0.71%); turn_prizes 0.94% → 0.74% (-0.20%).
Replacing one Counter Catcher with Lillie's Determination leaves the weighted rate higher (+0.72%), with the largest piece on Carpet Set H (Team Rocket's Zapdos / Pikachu 60), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Reversal Energy (+0.69%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Reversal Energy: "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy but provides only 3 Energy at a time."

The score uses the 0-copy loss weights. Against the list entering the step, +0.69%, gap SE 0.65%, 1.06 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.35%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.30%, Mega Starmie ex (Kudo) -0.23%, Celebi Mill -0.09%.
Unweighted mean 65.99% against the entering list at 65.50%.
The sample has no counter for Reversal Energy.
End reasons: empty 16.12% → 15.06% (-1.05%); foe_decked 49.15% → 49.78% (+0.63%); decked 6.45% → 6.71% (+0.27%).
Replacing one Reversal Energy with Lillie's Determination leaves the weighted rate higher (+0.69%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Igglybuff (+0.67%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, +0.67%, gap SE 0.65%, 1.03 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.50%, Set D Standard 60 (Charm Ogerpon) +0.31%, Set M Standard 60 (Mew ex / Spiky Energy) -0.51%, Mega Starmie ex (Kudo) -0.20%.
Unweighted mean 66.18% against the entering list at 65.50%.
Igglybuff counters: sleepy_flip 1.58 → 0.06, sleepy_heads 0.78 → 0.03.
End reasons: empty 16.12% → 19.12% (+3.00%); prizes 26.97% → 24.19% (-2.78%); turn_prizes 0.94% → 0.25% (-0.69%); foe_decked 49.15% → 49.67% (+0.52%).
Replacing one Igglybuff with Lillie's Determination leaves the weighted rate higher (+0.67%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Victini (-1.08%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -1.08%, gap SE 0.64%, -1.67 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.28%, Set T Standard 60 (Dragapult ex) +0.19%, Set M Standard 60 (Mew ex / Spiky Energy) -0.94%, Mill -0.40%.
Unweighted mean 64.83% against the entering list at 65.50%.
Victini counters: victory_star_reflip 0.97 → 0.18.
End reasons: empty 16.12% → 17.80% (+1.68%); prizes 26.97% → 25.77% (-1.19%); foe_decked 49.15% → 48.06% (-1.09%); decked 6.45% → 7.32% (+0.87%).
Replacing one Victini with Lillie's Determination leaves the weighted rate lower (-1.08%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

### 2 Lillie's Determination, cut Pichu

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Pichu: "Sweet Sleeping Face: As long as Pichu is Asleep, prevent all damage done to Pichu by attacks. Playground: Each player may search his or her deck for as many Basic Pokémon as he or she likes, put them onto his or her Bench, and shuffle his or her deck afterward. (You put your Pokémon on the Bench first.) Pichu is now Asleep."

The score uses the 0-copy loss weights. Against the start, +3.39%, gap SE 0.65%, 5.21 combined standard errors. Against the previous count, +1.32%, gap SE 0.65%, 2.02 combined standard errors.
Copy 2 gains +3.39% over the start. Copy 1 gains +2.08%. The higher count gained more.

Against the previous count, the weighted move is Set D Standard 60 (Charm Ogerpon) +0.33% of the weighted rate; Carpet Set G (Clefairy / Ledian 60) +0.27% of the weighted rate; Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.27% of the weighted rate; Set M Standard 60 (Mew ex / Spiky Energy) -0.16% of the weighted rate; Worlds 2026 Hedrick Dragapult -0.13% of the weighted rate; Mill -0.06% of the weighted rate.

The unweighted mean is 68.17% against 67.00% on the previous count and 65.50% on the start. The keeper is the 0-copy loss weights.

The sample has no counter for Lillie's Determination on Mill. The engine bumps doll_determination only when the strategy is doll.
Pichu counters: playground 1.63 → 0.59.
Line counters, on the same weights: mill_opponent 20.62 → 20.85, mill_attack 4.38 → 4.41, hilda 1.32 → 1.32, wally 0.34 → 0.32, eeeeeeek_shuffle 0.29 → 0.35.

End reasons, weighted with the 0-copy vector, from Mill's seat: prizes 26.45% → 22.14% (-4.31%); empty 14.67% → 17.85% (+3.17%); foe_decked 51.06% → 52.44% (+1.38%); turn_prizes 0.77% → 0.53% (-0.24%).

Replacing one Pichu with Lillie's Determination leaves the weighted rate higher (+1.32%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Rescue Carrier (+1.28%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Rescue Carrier: "Put up to 2 Pokémon, each with 90 HP or less, from your discard pile into your hand."

The score uses the 0-copy loss weights. Against the list entering the step, +1.28%, gap SE 0.65%, 1.97 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.66%, Carpet Set G (Clefairy / Ledian 60) +0.23%, Celebi Mill -0.11%, Set D Standard 60 (Charm Ogerpon) -0.06%.
Unweighted mean 68.03% against the entering list at 67.00%.
Rescue Carrier counters: rescue_carrier 1.64 → 1.30.
End reasons: foe_decked 51.06% → 52.44% (+1.38%); empty 14.67% → 14.02% (-0.66%); prizes 26.45% → 25.92% (-0.52%); turn_prizes 0.77% → 0.53% (-0.24%).
Replacing one Rescue Carrier with Lillie's Determination leaves the weighted rate higher (+1.28%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Colress's Tenacity (+1.10%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.10%, gap SE 0.66%, 1.68 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.51%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.35%, Mill -0.32%, Worlds 2026 Hedrick Dragapult -0.13%.
Unweighted mean 67.64% against the entering list at 67.00%.
Colress's Tenacity counters: colress 1.39 → 1.13.
End reasons: empty 14.67% → 13.13% (-1.54%); foe_decked 51.06% → 52.24% (+1.18%); decked 6.53% → 6.98% (+0.46%).
Replacing one Colress's Tenacity with Lillie's Determination leaves the weighted rate higher (+1.10%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wally (+0.89%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the list entering the step, +0.89%, gap SE 0.65%, 1.36 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.48%, Set D Standard 60 (Charm Ogerpon) +0.20%, Celebi Mill -0.16%, 二森林 -0.12%.
Unweighted mean 67.60% against the entering list at 67.00%.
Wally counters: wally 0.34 → 0.20.
End reasons: foe_decked 51.06% → 52.13% (+1.07%); empty 14.67% → 13.70% (-0.97%); decked 6.53% → 6.98% (+0.45%); prizes 26.45% → 26.23% (-0.22%).
Replacing one Wally with Lillie's Determination leaves the weighted rate higher (+0.89%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Crushing Hammer (+0.87%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, +0.87%, gap SE 0.65%, 1.34 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.34%, Carpet Set G (Clefairy / Ledian 60) +0.33%, Worlds 2026 Hedrick Dragapult -0.23%, Celebi Mill -0.13%.
Unweighted mean 67.59% against the entering list at 67.00%.
Crushing Hammer counters: crushing_hammer_heads 0.73 → 0.63, crushing_hammer_tails 0.75 → 0.64.
End reasons: foe_decked 51.06% → 52.04% (+0.98%); empty 14.67% → 14.00% (-0.68%); turn_prizes 0.77% → 0.47% (-0.31%).
Replacing one Crushing Hammer with Lillie's Determination leaves the weighted rate higher (+0.87%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Ignition Energy (+0.86%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, +0.86%, gap SE 0.65%, 1.33 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.38%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.30%, Set D Standard 60 (Charm Ogerpon) -0.28%, Celebi Mill -0.06%.
Unweighted mean 67.95% against the entering list at 67.00%.
The sample has no counter for Ignition Energy.
End reasons: empty 14.67% → 13.47% (-1.21%); foe_decked 51.06% → 52.14% (+1.08%); prizes 26.45% → 26.84% (+0.39%).
Replacing one Ignition Energy with Lillie's Determination leaves the weighted rate higher (+0.86%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Lillie's Poké Doll (+0.82%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Lillie's Poké Doll: "Play this card as if it were a 30-HP Colorless Basic Pokémon. At any time during your turn (before your attack), if this Pokémon is your Active Pokémon, you may discard all cards from it and put it on the bottom of your deck. This card can't retreat. If this card is Knocked Out, your opponent can't take any Prize cards for it."

The score uses the 0-copy loss weights. Against the list entering the step, +0.82%, gap SE 0.65%, 1.26 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.34%, Carpet Set G (Clefairy / Ledian 60) +0.29%, Set M Standard 60 (Mew ex / Spiky Energy) -0.34%, Mill -0.27%.
Unweighted mean 67.70% against the entering list at 67.00%.
The sample has no counter for Lillie's Poké Doll.
End reasons: foe_decked 51.06% → 51.98% (+0.92%); empty 14.67% → 13.79% (-0.88%); decked 6.53% → 6.89% (+0.37%); turn_prizes 0.77% → 0.51% (-0.26%).
Replacing one Lillie's Poké Doll with Lillie's Determination leaves the weighted rate higher (+0.82%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Level Ball (+0.77%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.77%, gap SE 0.65%, 1.17 combined standard errors.

Weighted contributions: Set T Standard 60 (Dragapult ex) +0.22%, Set D Standard 60 (Charm Ogerpon) +0.18%, Celebi Mill -0.21%, Mega Starmie ex (Kudo) -0.12%.
Unweighted mean 67.56% against the entering list at 67.00%.
Level Ball counters: level_ball 1.27 → 1.06.
End reasons: foe_decked 51.06% → 51.87% (+0.81%); prizes 26.45% → 25.78% (-0.67%); decked 6.53% → 6.73% (+0.21%).
Replacing one Level Ball with Lillie's Determination leaves the weighted rate higher (+0.77%), with the largest piece on Set T Standard 60 (Dragapult ex), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Water Energy (+0.68%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, +0.68%, gap SE 0.65%, 1.04 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.24%, Set D Standard 60 (Charm Ogerpon) +0.22%, Mill -0.21%, Worlds 2026 Hedrick Dragapult -0.07%.
Unweighted mean 67.44% against the entering list at 67.00%.
The sample has no counter for Water Energy.
End reasons: empty 14.67% → 12.88% (-1.79%); foe_decked 51.06% → 51.99% (+0.93%); prizes 26.45% → 27.21% (+0.76%); decked 6.53% → 7.05% (+0.52%).
Replacing one Water Energy with Lillie's Determination leaves the weighted rate higher (+0.68%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Hilda (-0.73%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.73%, gap SE 0.65%, -1.12 combined standard errors.

Weighted contributions: Set T Standard 60 (Dragapult ex) +0.18%, Carpet Set G (Clefairy / Ledian 60) +0.10%, Mill -0.36%, Set M Standard 60 (Mew ex / Spiky Energy) -0.18%.
Unweighted mean 66.54% against the entering list at 67.00%.
Hilda counters: hilda 1.32 → 1.12, evo_from_hilda 1.18 → 1.01, energy_from_hilda 1.32 → 1.11.
End reasons: empty 14.67% → 13.26% (-1.41%); prizes 26.45% → 27.86% (+1.41%); decked 6.53% → 7.27% (+0.74%); foe_decked 51.06% → 50.44% (-0.62%).
Replacing one Hilda with Lillie's Determination leaves the weighted rate lower (-0.73%), with the largest piece on Mill, and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Neutralization Zone (-1.03%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -1.03%, gap SE 0.66%, -1.56 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +1.81%, Carpet Set G (Clefairy / Ledian 60) +0.41%, Mega Starmie ex (Kudo) -1.23%, Set T Standard 60 (Dragapult ex) -1.11%.
Unweighted mean 65.24% against the entering list at 67.00%.
Neutralization Zone counters: neutralization_zone 8.23 → 0.25.
End reasons: empty 14.67% → 15.67% (+1.00%); foe_decked 51.06% → 50.08% (-0.98%); decked 6.53% → 6.82% (+0.29%); prizes 26.45% → 26.17% (-0.28%).
Replacing one Neutralization Zone with Lillie's Determination leaves the weighted rate lower (-1.03%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Igglybuff (-1.39%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, -1.39%, gap SE 0.65%, -2.14 combined standard errors.

Weighted contributions: Set S Standard 60 (Floragato hunter) +0.18%, Set T Standard 60 (Dragapult ex) +0.09%, Carpet Set G (Clefairy / Ledian 60) -0.41%, Celebi Mill -0.31%.
Unweighted mean 65.96% against the entering list at 67.00%.
Igglybuff counters: sleepy_flip 1.59 → 0.06, sleepy_heads 0.79 → 0.03.
End reasons: empty 14.67% → 16.84% (+2.17%); foe_decked 51.06% → 49.62% (-1.44%); prizes 26.45% → 25.39% (-1.06%); decked 6.53% → 7.31% (+0.78%).
Replacing one Igglybuff with Lillie's Determination leaves the weighted rate lower (-1.39%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Victini (-1.78%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -1.78%, gap SE 0.65%, -2.74 combined standard errors.

Weighted contributions: Set T Standard 60 (Dragapult ex) +0.20%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.05%, Mill -0.64%, Set M Standard 60 (Mew ex / Spiky Energy) -0.42%.
Unweighted mean 65.87% against the entering list at 67.00%.
Victini counters: victory_star_reflip 1.04 → 0.19.
End reasons: empty 14.67% → 16.38% (+1.71%); foe_decked 51.06% → 49.49% (-1.57%); decked 6.53% → 7.74% (+1.21%); prizes 26.45% → 25.57% (-0.88%).
Replacing one Victini with Lillie's Determination leaves the weighted rate lower (-1.78%), with the largest piece on Mill, and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

### 3 Lillie's Determination, cut Counter Catcher

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Counter Catcher: "You can use this card only if you have more Prize cards remaining than your opponent.

Switch in 1 of your opponent's Benched Pokémon to the Active Spot."

The score uses the 0-copy loss weights. Against the start, +5.50%, gap SE 0.66%, 8.39 combined standard errors. Against the previous count, +2.10%, gap SE 0.66%, 3.19 combined standard errors.
Copy 3 gains +5.50% over the start. Copy 1 gains +2.08%. The higher count gained more.
The step gain at copy 3 is +2.10%. The step gain at copy 1 is +2.08%. The later step gained more.

Against the previous count, the weighted move is Set D Standard 60 (Charm Ogerpon) +0.72% of the weighted rate; Carpet Set G (Clefairy / Ledian 60) +0.38% of the weighted rate; Set C Standard 60 (Clefairy / Mewtwo) +0.33% of the weighted rate; 二森林 -0.13% of the weighted rate; Set S Standard 60 (Floragato hunter) -0.04% of the weighted rate; Celebi Mill -0.03% of the weighted rate.

The unweighted mean is 69.39% against 68.17% on the previous count and 65.50% on the start. The keeper is the 0-copy loss weights.

The sample has no counter for Lillie's Determination on Mill. The engine bumps doll_determination only when the strategy is doll.
Counter Catcher counters: counter_catcher 0.18 → 0.01, counter_catcher_fail 0.00 → 0.00.
Line counters, on the same weights: mill_opponent 20.85 → 21.32, mill_attack 4.41 → 4.51, hilda 1.32 → 1.36, wally 0.32 → 0.33, eeeeeeek_shuffle 0.35 → 0.34.

End reasons, weighted with the 0-copy vector, from Mill's seat: empty 17.85% → 15.40% (-2.45%); foe_decked 52.44% → 54.61% (+2.16%); prizes 22.14% → 22.52% (+0.38%).

Replacing one Counter Catcher with Lillie's Determination leaves the weighted rate higher (+2.10%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Colress's Tenacity (+1.78%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Colress's Tenacity: "Search your deck for a Stadium card and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.78%, gap SE 0.66%, 2.71 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.35%, Carpet Set G (Clefairy / Ledian 60) +0.33%, 二森林 -0.11%, Celebi Mill -0.05%.
Unweighted mean 69.26% against the entering list at 68.17%.
Colress's Tenacity counters: colress 1.38 → 1.12.
End reasons: empty 17.85% → 15.26% (-2.58%); foe_decked 52.44% → 54.28% (+1.84%); prizes 22.14% → 23.07% (+0.93%).
Replacing one Colress's Tenacity with Lillie's Determination leaves the weighted rate higher (+1.78%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Cleffa (+1.41%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Cleffa: "Sweet Sleeping Face: As long as Cleffa is Asleep, prevent all damage done to Cleffa by attacks. Eeeeeeek: Shuffle your hand into your deck, then draw 6 cards. Cleffa is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, +1.41%, gap SE 0.66%, 2.14 combined standard errors.

Weighted contributions: Mill +0.35%, Set D Standard 60 (Charm Ogerpon) +0.35%, 二森林 -0.16%, Set M Standard 60 (Mew ex / Spiky Energy) -0.13%.
Unweighted mean 69.01% against the entering list at 68.17%.
Cleffa counters: eeeeeeek_shuffle 0.35 → 0.03.
End reasons: prizes 22.14% → 19.45% (-2.68%); empty 17.85% → 19.27% (+1.43%); foe_decked 52.44% → 53.86% (+1.42%).
Replacing one Cleffa with Lillie's Determination leaves the weighted rate higher (+1.41%), with the largest piece on Mill, and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Ignition Energy (+1.40%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Ignition Energy: "If this card is attached to 1 of your Pokémon, discard it at the end of your turn. As long as this card is attached to a Pokémon, it provides Colorless Energy. If this card is attached to an Evolution Pokémon, it provides Colorless Colorless Colorless Energy instead."

The score uses the 0-copy loss weights. Against the list entering the step, +1.40%, gap SE 0.66%, 2.14 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.61%, Mill +0.48%, Celebi Mill -0.18%, Set M Standard 60 (Mew ex / Spiky Energy) -0.18%.
Unweighted mean 68.95% against the entering list at 68.17%.
The sample has no counter for Ignition Energy.
End reasons: empty 17.85% → 15.19% (-2.66%); foe_decked 52.44% → 54.00% (+1.56%); prizes 22.14% → 23.42% (+1.28%).
Replacing one Ignition Energy with Lillie's Determination leaves the weighted rate higher (+1.40%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wally (+1.38%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wally: "Search your deck for a card that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. (This counts as evolving that Pokémon.) Shuffle your deck afterward. You can use this card during your first turn or on a Pokémon that was put into play this turn."

The score uses the 0-copy loss weights. Against the list entering the step, +1.38%, gap SE 0.65%, 2.11 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.57%, Mega Starmie ex (Kudo) +0.34%, Celebi Mill -0.07%, 二森林 -0.06%.
Unweighted mean 69.00% against the entering list at 68.17%.
Wally counters: wally 0.32 → 0.21.
End reasons: empty 17.85% → 15.59% (-2.26%); foe_decked 52.44% → 53.86% (+1.42%); prizes 22.14% → 22.99% (+0.86%).
Replacing one Wally with Lillie's Determination leaves the weighted rate higher (+1.38%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Level Ball (+1.36%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +1.36%, gap SE 0.65%, 2.09 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.31%, Set C Standard 60 (Clefairy / Mewtwo) +0.30%, Set D Standard 60 (Charm Ogerpon) -0.15%, Set S Standard 60 (Floragato hunter) -0.12%.
Unweighted mean 69.20% against the entering list at 68.17%.
Level Ball counters: level_ball 1.31 → 1.10.
End reasons: empty 17.85% → 15.89% (-1.95%); foe_decked 52.44% → 53.80% (+1.36%); prizes 22.14% → 23.06% (+0.92%); turn_prizes 0.53% → 0.31% (-0.22%).
Replacing one Level Ball with Lillie's Determination leaves the weighted rate higher (+1.36%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Rescue Carrier (+1.31%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Rescue Carrier: "Put up to 2 Pokémon, each with 90 HP or less, from your discard pile into your hand."

The score uses the 0-copy loss weights. Against the list entering the step, +1.31%, gap SE 0.65%, 2.00 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.35%, Mega Starmie ex (Kudo) +0.31%, Celebi Mill -0.18%, 二森林 -0.09%.
Unweighted mean 68.99% against the entering list at 68.17%.
Rescue Carrier counters: rescue_carrier 1.66 → 1.30.
End reasons: foe_decked 52.44% → 53.81% (+1.37%); prizes 22.14% → 21.10% (-1.04%); empty 17.85% → 17.41% (-0.44%); decked 6.58% → 6.82% (+0.24%).
Replacing one Rescue Carrier with Lillie's Determination leaves the weighted rate higher (+1.31%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Water Energy (+1.25%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Water Energy: ""

The score uses the 0-copy loss weights. Against the list entering the step, +1.25%, gap SE 0.65%, 1.91 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.42%, Carpet Set G (Clefairy / Ledian 60) +0.35%, Set D Standard 60 (Charm Ogerpon) -0.13%, Celebi Mill -0.07%.
Unweighted mean 69.01% against the entering list at 68.17%.
The sample has no counter for Water Energy.
End reasons: empty 17.85% → 15.94% (-1.91%); foe_decked 52.44% → 53.77% (+1.33%); prizes 22.14% → 22.93% (+0.79%).
Replacing one Water Energy with Lillie's Determination leaves the weighted rate higher (+1.25%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Lillie's Poké Doll (+0.88%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Lillie's Poké Doll: "Play this card as if it were a 30-HP Colorless Basic Pokémon. At any time during your turn (before your attack), if this Pokémon is your Active Pokémon, you may discard all cards from it and put it on the bottom of your deck. This card can't retreat. If this card is Knocked Out, your opponent can't take any Prize cards for it."

The score uses the 0-copy loss weights. Against the list entering the step, +0.88%, gap SE 0.65%, 1.34 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.47%, Carpet Set G (Clefairy / Ledian 60) +0.31%, Set M Standard 60 (Mew ex / Spiky Energy) -0.45%, Celebi Mill -0.11%.
Unweighted mean 68.79% against the entering list at 68.17%.
The sample has no counter for Lillie's Poké Doll.
End reasons: empty 17.85% → 16.45% (-1.40%); foe_decked 52.44% → 53.39% (+0.95%); prizes 22.14% → 22.86% (+0.73%); turn_prizes 0.53% → 0.31% (-0.22%).
Replacing one Lillie's Poké Doll with Lillie's Determination leaves the weighted rate higher (+0.88%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Hilda (+0.83%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.83%, gap SE 0.65%, 1.26 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.26%, Carpet Set G (Clefairy / Ledian 60) +0.24%, 二森林 -0.15%, Set M Standard 60 (Mew ex / Spiky Energy) -0.04%.
Unweighted mean 68.68% against the entering list at 68.17%.
Hilda counters: hilda 1.32 → 1.14, evo_from_hilda 1.17 → 1.01, energy_from_hilda 1.32 → 1.13.
End reasons: empty 17.85% → 15.15% (-2.69%); prizes 22.14% → 23.72% (+1.59%); foe_decked 52.44% → 53.36% (+0.92%); decked 6.58% → 6.86% (+0.28%).
Replacing one Hilda with Lillie's Determination leaves the weighted rate higher (+0.83%), with the largest piece on Worlds 2026 Hedrick Dragapult, and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wugtrio (+0.73%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wugtrio: "Undersea Tunnel: Flip 3 coins. For each heads, discard the top 3 cards of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, +0.73%, gap SE 0.65%, 1.12 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.52%, Worlds 2026 Hedrick Dragapult +0.14%, 二森林 -0.15%, Celebi Mill -0.13%.
Unweighted mean 68.54% against the entering list at 68.17%.
The sample has no counter for Wugtrio.
End reasons: empty 17.85% → 15.88% (-1.97%); prizes 22.14% → 23.11% (+0.98%); foe_decked 52.44% → 53.36% (+0.92%); decked 6.58% → 6.86% (+0.28%).
Replacing one Wugtrio with Lillie's Determination leaves the weighted rate higher (+0.73%), with the largest piece on Carpet Set G (Clefairy / Ledian 60), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Crushing Hammer (+0.69%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, +0.69%, gap SE 0.66%, 1.05 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.34%, Mega Starmie ex (Kudo) +0.23%, Mill -0.13%, Celebi Mill -0.12%.
Unweighted mean 68.52% against the entering list at 68.17%.
Crushing Hammer counters: crushing_hammer_heads 0.76 → 0.67, crushing_hammer_tails 0.78 → 0.66.
End reasons: empty 17.85% → 15.82% (-2.03%); prizes 22.14% → 23.26% (+1.12%); foe_decked 52.44% → 53.22% (+0.78%); decked 6.58% → 6.98% (+0.41%).
Replacing one Crushing Hammer with Lillie's Determination leaves the weighted rate higher (+0.69%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Slumbering Forest (-0.65%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Slumbering Forest: "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -0.65%, gap SE 0.64%, -1.02 combined standard errors.

Weighted contributions: Carpet Set G (Clefairy / Ledian 60) +0.22%, Worlds 2026 Hedrick Dragapult +0.19%, Set D Standard 60 (Charm Ogerpon) -1.25%, Set M Standard 60 (Mew ex / Spiky Energy) -0.19%.
Unweighted mean 68.23% against the entering list at 68.17%.
Slumbering Forest counters: slumbering_forest 1.80 → 0.41.
End reasons: prizes 22.14% → 25.40% (+3.26%); empty 17.85% → 15.69% (-2.15%); foe_decked 52.44% → 51.84% (-0.60%); decked 6.58% → 6.22% (-0.36%).
Replacing one Slumbering Forest with Lillie's Determination leaves the weighted rate lower (-0.65%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wiglett (-0.66%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wiglett: "Twisting Strike: Flip a coin. If heads, during your opponent's next turn, prevent all damage from and effects of attacks done to this Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -0.66%, gap SE 0.65%, -1.01 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.25%, Mill +0.25%, Set D Standard 60 (Charm Ogerpon) -0.28%, Set C Standard 60 (Clefairy / Mewtwo) -0.21%.
Unweighted mean 67.60% against the entering list at 68.17%.
The sample has no counter for Wiglett.
End reasons: empty 17.85% → 18.93% (+1.08%); prizes 22.14% → 21.51% (-0.62%); foe_decked 52.44% → 51.87% (-0.57%).
Replacing one Wiglett with Lillie's Determination leaves the weighted rate lower (-0.66%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Victini (-2.34%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -2.34%, gap SE 0.65%, -3.61 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.24%, Worlds 2026 Hedrick Dragapult +0.15%, Set M Standard 60 (Mew ex / Spiky Energy) -0.76%, Mill -0.48%.
Unweighted mean 66.45% against the entering list at 68.17%.
Victini counters: victory_star_reflip 1.06 → 0.16.
End reasons: foe_decked 52.44% → 50.07% (-2.37%); decked 6.58% → 7.86% (+1.28%); empty 17.85% → 19.13% (+1.28%).
Replacing one Victini with Lillie's Determination leaves the weighted rate lower (-2.34%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

### 4 Lillie's Determination, cut Wugtrio

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wugtrio: "Undersea Tunnel: Flip 3 coins. For each heads, discard the top 3 cards of your opponent's deck."

The score uses the 0-copy loss weights. Against the start, +5.79%, gap SE 0.65%, 8.87 combined standard errors. Against the previous count, +0.29%, gap SE 0.66%, 0.44 combined standard errors.
Copy 4 gains +5.79% over the start. Copy 1 gains +2.08%. The higher count gained more.

Against the previous count, the weighted move is Set C Standard 60 (Clefairy / Mewtwo) +0.41% of the weighted rate; Mega Starmie ex (Kudo) +0.17% of the weighted rate; Mill +0.16% of the weighted rate; Set D Standard 60 (Charm Ogerpon) -0.35% of the weighted rate; Celebi Mill -0.11% of the weighted rate; Carpet Set G (Clefairy / Ledian 60) -0.08% of the weighted rate.

The unweighted mean is 69.64% against 69.39% on the previous count and 65.50% on the start. The keeper is the 0-copy loss weights.

The sample has no counter for Lillie's Determination on Mill. The engine bumps doll_determination only when the strategy is doll.
The sample has no counter for Wugtrio.
Line counters, on the same weights: mill_opponent 21.32 → 21.17, mill_attack 4.51 → 4.48, hilda 1.36 → 1.40, wally 0.33 → 0.33, eeeeeeek_shuffle 0.34 → 0.37.
Those counters moved, and the weighted win rate did not clear one combined standard error.

End reasons, weighted with the 0-copy vector, from Mill's seat: empty 15.40% → 13.93% (-1.47%); prizes 22.52% → 23.66% (+1.14%); foe_decked 54.61% → 54.91% (+0.31%).

Replacing one Wugtrio with Lillie's Determination leaves the weighted rate higher (+0.29%), with the largest piece on Set C Standard 60 (Clefairy / Mewtwo), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Level Ball (-0.72%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Level Ball: "Search your deck for a Pokémon with 90 HP or less, reveal it, and put it into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.72%, gap SE 0.66%, -1.10 combined standard errors.

Weighted contributions: 二森林 +0.13%, Mega Starmie ex (Kudo) +0.09%, Set D Standard 60 (Charm Ogerpon) -0.66%, Carpet Set G (Clefairy / Ledian 60) -0.19%.
Unweighted mean 69.20% against the entering list at 69.39%.
Level Ball counters: level_ball 1.40 → 1.15.
End reasons: foe_decked 54.61% → 53.89% (-0.72%); empty 15.40% → 15.95% (+0.56%); decked 6.67% → 7.02% (+0.35%).
Replacing one Level Ball with Lillie's Determination leaves the weighted rate lower (-0.72%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Team Rocket's Handiwork (-0.74%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Team Rocket's Handiwork: "Flip 2 coins. For each heads, discard 2 cards from the top of your opponent's deck."

The score uses the 0-copy loss weights. Against the list entering the step, -0.74%, gap SE 0.66%, -1.12 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.17%, Mill +0.15%, Set D Standard 60 (Charm Ogerpon) -0.68%, Celebi Mill -0.32%.
Unweighted mean 68.82% against the entering list at 69.39%.
Team Rocket's Handiwork counters: handiwork 0.77 → 0.48, handiwork_tails 0.19 → 0.12.
End reasons: prizes 22.52% → 24.27% (+1.75%); empty 15.40% → 13.72% (-1.68%); foe_decked 54.61% → 53.81% (-0.79%); decked 6.67% → 7.42% (+0.76%).
Replacing one Team Rocket's Handiwork with Lillie's Determination leaves the weighted rate lower (-0.74%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Mime Jr. (-0.94%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Mime Jr.: "Sweet Sleeping Face: As long as Mime Jr. is Asleep, prevent all damage done to Mime Jr. by attacks. Sleepy Lost: Put the top card of your opponent's deck in the Lost Zone. Mime Jr. is now Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -0.94%, gap SE 0.65%, -1.43 combined standard errors.

Weighted contributions: Mega Starmie ex (Kudo) +0.20%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.20%, Set M Standard 60 (Mew ex / Spiky Energy) -0.97%, Set D Standard 60 (Charm Ogerpon) -0.37%.
Unweighted mean 69.24% against the entering list at 69.39%.
Mime Jr. counters: sleepy_lost 0.46 → 0.06, sleepy_lost_miss 0.01 → 0.00.
End reasons: empty 15.40% → 16.72% (+1.32%); foe_decked 54.61% → 53.72% (-0.89%).
Replacing one Mime Jr. with Lillie's Determination leaves the weighted rate lower (-0.94%), with the largest piece on Set M Standard 60 (Mew ex / Spiky Energy), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Igglybuff (-1.05%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Igglybuff: "Sleepy Voice: Once during your turn (before your attack), you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep. If you use this Ability, your turn ends."

The score uses the 0-copy loss weights. Against the list entering the step, -1.05%, gap SE 0.66%, -1.58 combined standard errors.

Weighted contributions: Mill +0.17%, Set M Standard 60 (Mew ex / Spiky Energy) +0.07%, Set D Standard 60 (Charm Ogerpon) -0.46%, Carpet Set G (Clefairy / Ledian 60) -0.42%.
Unweighted mean 68.73% against the entering list at 69.39%.
Igglybuff counters: sleepy_flip 1.50 → 0.06, sleepy_heads 0.74 → 0.03.
End reasons: empty 15.40% → 18.68% (+3.28%); prizes 22.52% → 20.71% (-1.81%); foe_decked 54.61% → 53.48% (-1.13%); turn_prizes 0.41% → 0.16% (-0.25%).
Replacing one Igglybuff with Lillie's Determination leaves the weighted rate lower (-1.05%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Crushing Hammer (-1.21%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Crushing Hammer: "Flip a coin. If heads, discard an Energy from 1 of your opponent's Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -1.21%, gap SE 0.66%, -1.84 combined standard errors.

Weighted contributions: Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.16%, Set M Standard 60 (Mew ex / Spiky Energy) +0.13%, Set D Standard 60 (Charm Ogerpon) -0.88%, Celebi Mill -0.26%.
Unweighted mean 68.58% against the entering list at 69.39%.
Crushing Hammer counters: crushing_hammer_heads 0.84 → 0.71, crushing_hammer_tails 0.83 → 0.70.
End reasons: prizes 22.52% → 23.69% (+1.17%); foe_decked 54.61% → 53.52% (-1.08%); decked 6.67% → 7.37% (+0.70%); empty 15.40% → 14.93% (-0.47%).
Replacing one Crushing Hammer with Lillie's Determination leaves the weighted rate lower (-1.21%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Hilda (-1.24%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Hilda: "Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.24%, gap SE 0.66%, -1.88 combined standard errors.

Weighted contributions: Set C Standard 60 (Clefairy / Mewtwo) +0.19%, Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.10%, Set D Standard 60 (Charm Ogerpon) -0.63%, Mill -0.48%.
Unweighted mean 68.62% against the entering list at 69.39%.
Hilda counters: hilda 1.36 → 1.15, evo_from_hilda 1.20 → 1.02, energy_from_hilda 1.35 → 1.14.
End reasons: prizes 22.52% → 24.03% (+1.51%); foe_decked 54.61% → 53.30% (-1.31%); empty 15.40% → 14.27% (-1.13%); decked 6.67% → 7.64% (+0.97%).
Replacing one Hilda with Lillie's Determination leaves the weighted rate lower (-1.24%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Reversal Energy (-1.36%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Reversal Energy: "As long as this card is attached to a Pokémon, it provides Colorless Energy. If you have more Prize cards remaining than your opponent, and if this card is attached to an Evolution Pokémon that doesn't have a Rule Box (Pokémon ex, Pokémon V, etc. have Rule Boxes), this card provides every type of Energy but provides only 3 Energy at a time."

The score uses the 0-copy loss weights. Against the list entering the step, -1.36%, gap SE 0.66%, -2.07 combined standard errors.

Weighted contributions: Carpet Set H (Team Rocket's Zapdos / Pikachu 60) +0.06%, Set T Standard 60 (Dragapult ex) +0.05%, Set D Standard 60 (Charm Ogerpon) -0.35%, Set C Standard 60 (Clefairy / Mewtwo) -0.32%.
Unweighted mean 68.60% against the entering list at 69.39%.
The sample has no counter for Reversal Energy.
End reasons: prizes 22.52% → 24.41% (+1.89%); foe_decked 54.61% → 53.23% (-1.37%); empty 15.40% → 14.54% (-0.86%); decked 6.67% → 7.10% (+0.43%).
Replacing one Reversal Energy with Lillie's Determination leaves the weighted rate lower (-1.36%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Slumbering Forest (-1.46%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Slumbering Forest: "If a Pokémon is Asleep, its owner flips 2 coins instead of 1 for that Special Condition between turns. If either of them is tails, that Pokémon is still Asleep."

The score uses the 0-copy loss weights. Against the list entering the step, -1.46%, gap SE 0.65%, -2.25 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.46%, 二森林 +0.16%, Set D Standard 60 (Charm Ogerpon) -1.77%, Set C Standard 60 (Clefairy / Mewtwo) -0.24%.
Unweighted mean 68.91% against the entering list at 69.39%.
Slumbering Forest counters: slumbering_forest 1.85 → 0.39.
End reasons: prizes 22.52% → 25.52% (+3.00%); foe_decked 54.61% → 53.23% (-1.38%); empty 15.40% → 14.28% (-1.12%); decked 6.67% → 6.35% (-0.32%).
Replacing one Slumbering Forest with Lillie's Determination leaves the weighted rate lower (-1.46%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at prizes. Lillie's Determination itself has no Mill counter in this sample.

#### Also Buddy-Buddy Poffin (-1.80%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Buddy-Buddy Poffin: "Search your deck for up to 2 Basic Pokémon with 70 HP or less and put them onto your Bench. Then, shuffle your deck."

The score uses the 0-copy loss weights. Against the list entering the step, -1.80%, gap SE 0.66%, -2.74 combined standard errors.

Weighted contributions: Set M Standard 60 (Mew ex / Spiky Energy) +0.12%, Set S Standard 60 (Floragato hunter) +0.08%, Set D Standard 60 (Charm Ogerpon) -0.81%, Carpet Set G (Clefairy / Ledian 60) -0.59%.
Unweighted mean 68.22% against the entering list at 69.39%.
The sample has no counter for Buddy-Buddy Poffin.
End reasons: foe_decked 54.61% → 52.78% (-1.82%); empty 15.40% → 16.69% (+1.29%); decked 6.67% → 7.13% (+0.46%).
Replacing one Buddy-Buddy Poffin with Lillie's Determination leaves the weighted rate lower (-1.80%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Neutralization Zone (-2.04%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Neutralization Zone: "Prevent all damage done to Pokémon that don't have a Rule Box (both yours and your opponent's) by attacks from the opponent's Pokémon ex and Pokémon V. (Pokémon ex, Pokémon V, etc. have Rule Boxes.)

This card can't be put into your hand or deck from the discard pile."

The score uses the 0-copy loss weights. Against the list entering the step, -2.04%, gap SE 0.67%, -3.06 combined standard errors.

Weighted contributions: Set D Standard 60 (Charm Ogerpon) +0.66%, Set C Standard 60 (Clefairy / Mewtwo) +0.15%, Mega Starmie ex (Kudo) -1.01%, Set T Standard 60 (Dragapult ex) -0.93%.
Unweighted mean 67.11% against the entering list at 69.39%.
Neutralization Zone counters: neutralization_zone 7.97 → 0.25.
End reasons: foe_decked 54.61% → 52.51% (-2.10%); empty 15.40% → 16.87% (+1.47%); decked 6.67% → 7.22% (+0.55%).
Replacing one Neutralization Zone with Lillie's Determination leaves the weighted rate lower (-2.04%), with the largest piece on Mega Starmie ex (Kudo), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

#### Also Wiglett (-2.25%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Wiglett: "Twisting Strike: Flip a coin. If heads, during your opponent's next turn, prevent all damage from and effects of attacks done to this Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -2.25%, gap SE 0.66%, -3.40 combined standard errors.

Weighted contributions: 二森林 +0.05%, Mill +0.05%, Set D Standard 60 (Charm Ogerpon) -0.76%, Set C Standard 60 (Clefairy / Mewtwo) -0.56%.
Unweighted mean 67.88% against the entering list at 69.39%.
The sample has no counter for Wiglett.
End reasons: empty 15.40% → 17.64% (+2.25%); foe_decked 54.61% → 52.38% (-2.23%); decked 6.67% → 6.95% (+0.28%); prizes 22.52% → 22.27% (-0.25%).
Replacing one Wiglett with Lillie's Determination leaves the weighted rate lower (-2.25%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at empty. Lillie's Determination itself has no Mill counter in this sample.

#### Also Victini (-3.58%)

Lillie's Determination: "Shuffle your hand into your deck. Then, draw 6 cards. If you have exactly 6 Prize cards remaining, draw 8 cards instead." Victini: "Victory Star: Once during your turn, after you flip any coins for an attack, you may ignore all effects of those coin flips and begin flipping those coins again. You can’t use more than 1 Victory Star Ability each turn. Stored Power: Move all Energy attached to this Pokémon to 1 of your Benched Pokémon."

The score uses the 0-copy loss weights. Against the list entering the step, -3.58%, gap SE 0.65%, -5.48 combined standard errors.

Weighted contributions: Worlds 2026 Hedrick Dragapult +0.14%, 二森林 +0.01%, Set D Standard 60 (Charm Ogerpon) -1.07%, Mill -0.58%.
Unweighted mean 67.10% against the entering list at 69.39%.
Victini counters: victory_star_reflip 1.11 → 0.16.
End reasons: foe_decked 54.61% → 50.97% (-3.64%); empty 15.40% → 18.19% (+2.79%); decked 6.67% → 7.98% (+1.31%); prizes 22.52% → 22.15% (-0.37%).
Replacing one Victini with Lillie's Determination leaves the weighted rate lower (-3.58%), with the largest piece on Set D Standard 60 (Charm Ogerpon), and the end-reason mix moves at foe_decked. Lillie's Determination itself has no Mill counter in this sample.

## Step 1

List entering this step: weighted 49.50%. Each row replaces one copy of that card with one Lillie's Determination. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Ignition Energy | 3 | 51.57% | 0.46% | 67.00% | 16.00% | +2.08% | +2.08% | 20.62 |
| Team Rocket's Handiwork | 2 | 51.39% | 0.47% | 66.84% | 17.12% | +1.89% | +1.89% | 20.56 |
| Wally | 2 | 50.99% | 0.46% | 66.60% | 15.88% | +1.49% | +1.49% | 20.71 |
| Mime Jr. | 1 | 50.94% | 0.46% | 66.67% | 15.00% | +1.44% | +1.44% | 21.10 |
| Miss Fortune Sisters | 2 | 50.90% | 0.46% | 66.57% | 17.12% | +1.40% | +1.40% | 21.17 |
| Pichu | 1 | 50.88% | 0.46% | 66.89% | 17.12% | +1.38% | +1.38% | 20.50 |
| Hilda | 4 | 50.74% | 0.46% | 66.44% | 16.00% | +1.24% | +1.24% | 20.72 |
| Rescue Carrier | 3 | 50.70% | 0.46% | 66.37% | 15.12% | +1.21% | +1.21% | 20.81 |
| Water Energy | 3 | 50.67% | 0.47% | 66.26% | 17.62% | +1.18% | +1.18% | 20.73 |
| Cleffa | 1 | 50.64% | 0.46% | 66.56% | 18.12% | +1.15% | +1.15% | 20.69 |
| Colress's Tenacity | 4 | 50.40% | 0.46% | 66.10% | 16.38% | +0.90% | +0.90% | 20.81 |
| Level Ball | 4 | 50.36% | 0.46% | 66.14% | 15.25% | +0.87% | +0.87% | 20.81 |
| Counter Catcher | 1 | 50.22% | 0.46% | 66.06% | 14.75% | +0.72% | +0.72% | 20.88 |
| Reversal Energy | 4 | 50.18% | 0.46% | 65.99% | 15.00% | +0.69% | +0.69% | 20.63 |
| Igglybuff | 1 | 50.16% | 0.46% | 66.18% | 15.62% | +0.67% | +0.67% | 21.47 |
| Wiglett | 4 | 50.02% | 0.46% | 65.99% | 13.75% | +0.52% | +0.52% | 20.37 |
| Crushing Hammer | 4 | 50.01% | 0.46% | 65.97% | 16.75% | +0.51% | +0.51% | 20.70 |
| Wugtrio | 4 | 49.97% | 0.46% | 65.99% | 13.00% | +0.47% | +0.47% | 20.48 |
| Lillie's Poké Doll | 1 | 49.95% | 0.46% | 66.01% | 16.50% | +0.45% | +0.45% | 20.85 |
| Buddy-Buddy Poffin | 4 | 49.87% | 0.47% | 65.65% | 16.50% | +0.38% | +0.38% | 20.43 |
| Slumbering Forest | 1 | 49.77% | 0.44% | 66.55% | 7.75% | +0.27% | +0.27% | 20.73 |
| Double Turbo Energy | 4 | 49.73% | 0.46% | 65.88% | 15.75% | +0.23% | +0.23% | 20.46 |
| Neutralization Zone | 1 | 49.04% | 0.47% | 64.19% | 23.50% | -0.46% | -0.46% | 20.58 |
| Victini | 1 | 48.42% | 0.46% | 64.83% | 15.38% | -1.08% | -1.08% | 20.35 |

Kept −Ignition Energy at 51.57% (+2.08%, gap SE 0.65%, 3.20 combined standard errors).

The unweighted mean keeps the same cut.

## Step 2

List entering this step: weighted 51.57%. Each row replaces one copy of that card with one Lillie's Determination. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Pichu | 1 | 52.89% | 0.47% | 68.17% | 18.25% | +1.32% | +3.39% | 20.85 |
| Rescue Carrier | 3 | 52.86% | 0.46% | 68.03% | 15.62% | +1.28% | +3.36% | 21.02 |
| Colress's Tenacity | 4 | 52.68% | 0.47% | 67.64% | 18.12% | +1.10% | +3.18% | 20.98 |
| Wally | 2 | 52.46% | 0.47% | 67.60% | 17.38% | +0.89% | +2.96% | 20.94 |
| Crushing Hammer | 4 | 52.45% | 0.46% | 67.59% | 16.75% | +0.87% | +2.95% | 20.95 |
| Ignition Energy | 2 | 52.44% | 0.46% | 67.95% | 14.12% | +0.86% | +2.94% | 20.93 |
| Lillie's Poké Doll | 1 | 52.40% | 0.46% | 67.70% | 17.75% | +0.82% | +2.90% | 21.12 |
| Level Ball | 4 | 52.34% | 0.47% | 67.56% | 17.25% | +0.77% | +2.84% | 20.84 |
| Water Energy | 3 | 52.25% | 0.47% | 67.44% | 17.50% | +0.68% | +2.76% | 20.92 |
| Mime Jr. | 1 | 52.21% | 0.46% | 67.52% | 17.38% | +0.64% | +2.71% | 21.25 |
| Counter Catcher | 1 | 52.11% | 0.47% | 67.49% | 17.38% | +0.54% | +2.61% | 20.97 |
| Wiglett | 4 | 52.05% | 0.46% | 67.46% | 17.38% | +0.48% | +2.55% | 20.63 |
| Cleffa | 1 | 52.02% | 0.47% | 67.33% | 18.75% | +0.44% | +2.52% | 20.94 |
| Team Rocket's Handiwork | 2 | 52.01% | 0.46% | 67.18% | 14.62% | +0.43% | +2.51% | 20.79 |
| Miss Fortune Sisters | 2 | 51.92% | 0.46% | 67.24% | 16.38% | +0.35% | +2.43% | 21.42 |
| Double Turbo Energy | 4 | 51.80% | 0.46% | 67.01% | 14.88% | +0.22% | +2.30% | 20.91 |
| Wugtrio | 4 | 51.55% | 0.46% | 67.03% | 15.75% | -0.02% | +2.05% | 20.83 |
| Slumbering Forest | 1 | 51.53% | 0.45% | 67.50% | 10.50% | -0.05% | +2.03% | 20.98 |
| Buddy-Buddy Poffin | 4 | 51.40% | 0.46% | 66.84% | 16.88% | -0.18% | +1.90% | 20.70 |
| Reversal Energy | 4 | 51.16% | 0.46% | 67.00% | 14.62% | -0.41% | +1.67% | 20.83 |
| Hilda | 4 | 50.84% | 0.46% | 66.54% | 15.50% | -0.73% | +1.34% | 20.65 |
| Neutralization Zone | 1 | 50.55% | 0.47% | 65.24% | 23.50% | -1.03% | +1.05% | 20.70 |
| Igglybuff | 1 | 50.18% | 0.46% | 65.96% | 14.75% | -1.39% | +0.68% | 21.58 |
| Victini | 1 | 49.80% | 0.46% | 65.87% | 15.12% | -1.78% | +0.30% | 20.43 |

Kept −Pichu at 52.89% (+1.32%, gap SE 0.65%, 2.02 combined standard errors).

The unweighted mean keeps the same cut.

## Step 3

List entering this step: weighted 52.89%. Each row replaces one copy of that card with one Lillie's Determination. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Counter Catcher | 1 | 55.00% | 0.47% | 69.39% | 23.12% | +2.10% | +5.50% | 21.32 |
| Colress's Tenacity | 4 | 54.67% | 0.47% | 69.26% | 19.88% | +1.78% | +5.17% | 21.09 |
| Cleffa | 1 | 54.30% | 0.47% | 69.01% | 20.62% | +1.41% | +4.80% | 20.95 |
| Ignition Energy | 2 | 54.30% | 0.47% | 68.95% | 19.88% | +1.40% | +4.80% | 21.00 |
| Wally | 2 | 54.27% | 0.47% | 69.00% | 18.88% | +1.38% | +4.77% | 21.17 |
| Level Ball | 4 | 54.25% | 0.46% | 69.20% | 17.25% | +1.36% | +4.75% | 20.96 |
| Rescue Carrier | 3 | 54.20% | 0.47% | 68.99% | 18.13% | +1.31% | +4.70% | 20.95 |
| Water Energy | 3 | 54.14% | 0.46% | 69.01% | 17.38% | +1.25% | +4.64% | 21.03 |
| Lillie's Poké Doll | 1 | 53.77% | 0.46% | 68.79% | 18.25% | +0.88% | +4.27% | 21.19 |
| Hilda | 4 | 53.72% | 0.47% | 68.68% | 19.38% | +0.83% | +4.22% | 20.97 |
| Wugtrio | 4 | 53.62% | 0.47% | 68.54% | 18.38% | +0.73% | +4.13% | 21.03 |
| Crushing Hammer | 4 | 53.58% | 0.47% | 68.52% | 18.87% | +0.69% | +4.08% | 21.07 |
| Miss Fortune Sisters | 2 | 53.41% | 0.46% | 68.49% | 15.12% | +0.52% | +3.91% | 21.39 |
| Mime Jr. | 1 | 53.30% | 0.46% | 68.56% | 16.75% | +0.41% | +3.80% | 21.10 |
| Double Turbo Energy | 4 | 53.13% | 0.46% | 68.18% | 16.38% | +0.24% | +3.63% | 20.78 |
| Reversal Energy | 4 | 52.96% | 0.46% | 68.10% | 20.00% | +0.07% | +3.47% | 20.87 |
| Team Rocket's Handiwork | 2 | 52.92% | 0.46% | 68.17% | 15.62% | +0.03% | +3.43% | 20.78 |
| Buddy-Buddy Poffin | 4 | 52.75% | 0.46% | 68.01% | 17.12% | -0.14% | +3.25% | 20.89 |
| Igglybuff | 1 | 52.73% | 0.47% | 67.72% | 18.75% | -0.16% | +3.24% | 21.75 |
| Slumbering Forest | 1 | 52.24% | 0.44% | 68.23% | 9.75% | -0.65% | +2.74% | 20.84 |
| Wiglett | 4 | 52.24% | 0.46% | 67.60% | 16.38% | -0.66% | +2.74% | 20.38 |
| Neutralization Zone | 1 | 52.24% | 0.47% | 66.65% | 25.00% | -0.66% | +2.74% | 20.86 |
| Victini | 1 | 50.55% | 0.46% | 66.45% | 15.38% | -2.34% | +1.05% | 20.38 |

Kept −Counter Catcher at 55.00% (+2.10%, gap SE 0.66%, 3.19 combined standard errors).

The unweighted mean keeps the same cut.

## Step 4

List entering this step: weighted 55.00%. Each row replaces one copy of that card with one Lillie's Determination. Sorted by the 0-copy weighted rate, then the worst foe, then how many copies the cut had, then the name.

| Cut | Copies before | Weighted | ± | Mean | Worst | Delta step | Delta start | Mill cards |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Wugtrio | 4 | 55.29% | 0.47% | 69.64% | 20.75% | +0.29% | +5.79% | 21.17 |
| Water Energy | 3 | 54.95% | 0.47% | 69.39% | 21.25% | -0.04% | +5.45% | 21.32 |
| Lillie's Poké Doll | 1 | 54.94% | 0.47% | 69.40% | 21.62% | -0.06% | +5.44% | 21.53 |
| Cleffa | 1 | 54.88% | 0.46% | 69.60% | 17.75% | -0.12% | +5.38% | 21.05 |
| Ignition Energy | 2 | 54.71% | 0.47% | 69.32% | 19.62% | -0.29% | +5.21% | 21.27 |
| Rescue Carrier | 3 | 54.66% | 0.47% | 69.28% | 18.88% | -0.34% | +5.16% | 21.25 |
| Double Turbo Energy | 4 | 54.64% | 0.46% | 69.32% | 18.75% | -0.36% | +5.14% | 21.18 |
| Wally | 2 | 54.52% | 0.47% | 69.03% | 18.38% | -0.47% | +5.02% | 21.30 |
| Colress's Tenacity | 4 | 54.48% | 0.47% | 69.10% | 19.88% | -0.51% | +4.99% | 21.28 |
| Miss Fortune Sisters | 2 | 54.45% | 0.46% | 69.23% | 17.62% | -0.55% | +4.95% | 21.74 |
| Level Ball | 4 | 54.27% | 0.46% | 69.20% | 18.62% | -0.72% | +4.78% | 21.02 |
| Team Rocket's Handiwork | 2 | 54.25% | 0.47% | 68.82% | 18.50% | -0.74% | +4.76% | 21.08 |
| Mime Jr. | 1 | 54.06% | 0.46% | 69.24% | 20.62% | -0.94% | +4.56% | 21.63 |
| Igglybuff | 1 | 53.95% | 0.47% | 68.73% | 20.00% | -1.05% | +4.45% | 22.05 |
| Crushing Hammer | 4 | 53.79% | 0.46% | 68.58% | 17.12% | -1.21% | +4.29% | 21.26 |
| Hilda | 4 | 53.76% | 0.46% | 68.62% | 18.88% | -1.24% | +4.26% | 21.13 |
| Reversal Energy | 4 | 53.63% | 0.47% | 68.60% | 20.75% | -1.36% | +4.13% | 21.10 |
| Slumbering Forest | 1 | 53.54% | 0.45% | 68.91% | 11.12% | -1.46% | +4.04% | 21.23 |
| Buddy-Buddy Poffin | 4 | 53.19% | 0.47% | 68.22% | 17.62% | -1.80% | +3.69% | 20.85 |
| Neutralization Zone | 1 | 52.96% | 0.47% | 67.11% | 26.38% | -2.04% | +3.46% | 20.94 |
| Wiglett | 4 | 52.75% | 0.47% | 67.88% | 18.00% | -2.25% | +3.25% | 20.67 |
| Victini | 1 | 51.42% | 0.46% | 67.10% | 15.88% | -3.58% | +1.92% | 20.49 |

Kept −Wugtrio at 55.29% (+0.29%, gap SE 0.66%, 0.44 combined standard errors).

The unweighted mean keeps the same cut.

## Unweighted mean across counts

The unweighted mean also keeps 4 copies at 69.64%. The keeper stays the 0-copy loss weights.

## Foes at the kept list

A parked foe repeats its 0-copy rate. Delta is against the start.

| Foe | Weight | A | B | Mean | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Set D Standard 60 (Charm Ogerpon) | 14.7485% | 18.75% | 22.75% | 20.75% | +7.25% |
| Set M Standard 60 (Mew ex / Spiky Energy) | 11.9139% | 29.50% | 30.50% | 30.00% | -0.13% |
| Mega Starmie ex (Kudo) | 10.7204% | 43.00% | 40.25% | 41.62% | +4.50% |
| Carpet Set G (Clefairy / Ledian 60) | 9.3137% | 57.00% | 57.25% | 57.12% | +11.75% |
| Set C Standard 60 (Clefairy / Mewtwo) | 8.8022% | 62.75% | 62.50% | 62.62% | +14.25% |
| Mill | 8.5251% | 53.50% | 54.00% | 53.75% | +3.75% |
| Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | 5.9250% | 81.50% | 81.75% | 81.62% | +16.37% |
| Worlds 2026 Hedrick Dragapult | 5.5200% | 75.50% | 78.00% | 76.75% | +9.13% |
| Celebi Mill | 4.3052% | 73.00% | 72.00% | 72.50% | -2.25% |
| 二森林 | 4.3052% | 69.75% | 72.75% | 71.25% | -3.50% |
| Set T Standard 60 (Dragapult ex) | 3.9216% | 84.50% | 83.50% | 84.00% | +7.00% |
| Set S Standard 60 (Floragato hunter) | 3.7724% | 78.00% | 82.25% | 80.12% | +2.25% |
| Chris Brewer Lucario Hariyama | 2.9199% | 83.00% | 82.75% | 82.88% | +0.00% |
| Unlimited Dragapult (Pidgeot / Rotom V) | 2.4723% | 85.25% | 85.75% | 85.50% | +0.00% |
| Iron Thorns ex | 1.3214% | 95.25% | 89.25% | 92.25% | +0.00% |
| Doll | 0.8099% | 94.75% | 95.75% | 95.25% | +0.00% |
| Unlimited 60 (Ambipom Hand Fling) | 0.7033% | 96.50% | 95.25% | 95.88% | +0.00% |
