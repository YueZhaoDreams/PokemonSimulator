# Kecleon, three one-copy swaps

One step removes one copy of one other card and adds one copy of the named card. The list stays 60. The locked `SET_KECLEON_NAMES` list is not assigned and is not changed. The mirror plays that locked list.

The starting 60 is the lock with one Battle Compressor and one Boss's Orders removed and two Latias ex added. Latias ex says: "Skyliner: Your Basic Pokémon in play have no Retreat Cost. Eon Blade: During your next turn, this Pokémon can't attack."

The three rounds add one copy each, in this order: Counter Catcher, Penny, Jirachi-EX. A second copy of the same card is not tried. The request names three rounds, not a walk to the 4-copy cap. Every other name still in the list is a cut. Nothing is protected. The step keeps the highest 0-copy weighted rate, then the higher worst active foe, then the cut that had more copies, then the name. A dip is kept.

Seed 20261116. 400 games per seat. Both seats. Each cell starts a new `random.Random` at that seed and plays its games on that generator. The foe, the seat, and the step are not mixed into the seed. Two lists diverge after the first choice that consumes a different number of draws.

Rules are standard 60. Weights are `max(1e-6, 1 - win rate)` on the starting list, divided by the sum. A tie is not a win, so it sits on the loss side of that formula. The same vector scores every later list. Parked foes keep their 0-copy win rate and are not replayed. Gap standard error is summed on the active set only.

Elapsed 295s.

## Field

0-copy foes:

- g — Carpet Set G (Clefairy / Ledian 60) — g — 60 cards
- h — Carpet Set H (Team Rocket's Zapdos / Pikachu 60) — nuzzle — 60 cards
- c60 — Set C Standard 60 (Clefairy / Mewtwo) — party — 60 cards
- d60 — Set D Standard 60 (Charm Ogerpon) — demolish — 60 cards
- m60 — Set M Standard 60 (Mew ex / Spiky Energy) — mew_baby — 60 cards
- s60 — Set S Standard 60 (Floragato hunter) — slash — 60 cards
- t60 — Set T Standard 60 (Dragapult ex) — phantom — 60 cards
- t-meta — Worlds 2026 Hedrick Dragapult — phantom — 60 cards
- t-unl — Unlimited Dragapult (Pidgeot / Rotom V) — phantom — 60 cards
- g30 — Unlimited 60 (Ambipom Hand Fling) — celebration — 60 cards
- l60 — Chris Brewer Lucario Hariyama — aura — 60 cards
- mill — Mill — mill — 60 cards
- doll — Doll — doll — 60 cards
- celebi — Celebi Mill — roast — 60 cards
- two-forest — 二森林 — roast — 60 cards
- kecleon — Kecleon — kecleon — 60 cards
- starmie — Mega Starmie — starmie — 60 cards
- thorns — Iron Thorns — thorns — 60 cards

Archived, no row:

- a — Carpet Set A (Dondozo / Staraptor) — 30 cards — presets b
- b — Carpet Set B (Walrein / Pikachu shock) — 30 cards — presets b
- c — Set C (Clefairy / Mewtwo) — 30 cards — presets b
- d — Set D (Charm Ogerpon) — 30 cards — presets b
- e — Carpet Set E (Walrein / Iris) — 30 cards — presets c
- f — Carpet Set F (Staraptor / Gengar) — 30 cards — presets c
- s — Set S (Floragato hunter) — 30 cards — presets b

Not 60 cards, no row:

- t — Set T (Dragapult ex) — 30 cards — presets s30

Not a list, no row:

- spare — Spare Cards — kind spare — 4 cards — archived True

## 0-copy weights

Active set cumulative weight 92.00%.

| Foe | Weight | Win rate | Seat A | Seat B |
| :--- | ---: | ---: | ---: | ---: |
| Set M Standard 60 (Mew ex / Spiky Energy) (active) | 12.60% | 14.00% | 13.75% | 14.25% |
| Set T Standard 60 (Dragapult ex) (active) | 9.49% | 35.25% | 37.50% | 33.00% |
| Worlds 2026 Hedrick Dragapult (active) | 8.19% | 44.12% | 45.50% | 42.75% |
| Doll (active) | 7.91% | 46.00% | 47.25% | 44.75% |
| Set C Standard 60 (Clefairy / Mewtwo) (active) | 7.56% | 48.38% | 51.25% | 45.50% |
| Mega Starmie (active) | 7.12% | 51.38% | 51.25% | 51.50% |
| Kecleon (active) | 6.98% | 52.38% | 50.50% | 54.25% |
| Chris Brewer Lucario Hariyama (active) | 6.90% | 52.88% | 53.50% | 52.25% |
| Unlimited Dragapult (Pidgeot / Rotom V) (active) | 6.03% | 58.88% | 60.50% | 57.25% |
| Mill (active) | 5.40% | 63.12% | 66.00% | 60.25% |
| 二森林 (active) | 5.11% | 65.12% | 66.25% | 64.00% |
| Celebi Mill (active) | 4.67% | 68.12% | 66.25% | 70.00% |
| Iron Thorns (active) | 4.03% | 72.50% | 74.00% | 71.00% |
| Carpet Set G (Clefairy / Ledian 60) (parked) | 3.90% | 73.38% | 71.25% | 75.50% |
| Set D Standard 60 (Charm Ogerpon) (parked) | 2.16% | 85.25% | 85.50% | 85.00% |
| Set S Standard 60 (Floragato hunter) (parked) | 1.61% | 89.00% | 89.00% | 89.00% |
| Unlimited 60 (Ambipom Hand Fling) (parked) | 0.22% | 98.50% | 99.00% | 98.00% |
| Carpet Set H (Team Rocket's Zapdos / Pikachu 60) (parked) | 0.11% | 99.25% | 99.50% | 99.00% |

Unweighted mean of every live 60: 62.08%. Unweighted mean of the active set: 51.70%. Worst active foe: Set M Standard 60 (Mew ex / Spiky Energy) 14.00%.

Parked foes stay at the win rate in that table.

## Path

| Step | Card in | Cut | Weighted | SE | Unweighted | Worst | Δ start | Δ previous | Catcher | Penny | Jirachi | Whip |
| :--- | :--- | :--- | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | — | — | 49.84% | 0.44% | 51.70% | Set M Standard 60 (Mew ex / Spiky Energy) 14.00% | 0.00 pp | 0.00 pp | 0.000 | 0.000 | 0.000 | 4.845 |

## Decision

0-copy weighted rate 49.84% (SE 0.44%). Active Set M Standard 60 (Mew ex / Spiky Energy), Set T Standard 60 (Dragapult ex), Worlds 2026 Hedrick Dragapult, Doll, Set C Standard 60 (Clefairy / Mewtwo), Mega Starmie, Kecleon, Chris Brewer Lucario Hariyama, Unlimited Dragapult (Pidgeot / Rotom V), Mill, 二森林, Celebi Mill, Iron Thorns.

Each step took the best cut on this one seed, so the path sits a little high. There is no second seed.

## Foe table at the kept list

start

| Foe | Weight | A | B | Mean | Δ start |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Set M Standard 60 (Mew ex / Spiky Energy) | 12.60% | 13.75% | 14.25% | 14.00% | 0.00 pp |
| Set T Standard 60 (Dragapult ex) | 9.49% | 37.50% | 33.00% | 35.25% | 0.00 pp |
| Worlds 2026 Hedrick Dragapult | 8.19% | 45.50% | 42.75% | 44.12% | 0.00 pp |
| Doll | 7.91% | 47.25% | 44.75% | 46.00% | 0.00 pp |
| Set C Standard 60 (Clefairy / Mewtwo) | 7.56% | 51.25% | 45.50% | 48.38% | 0.00 pp |
| Mega Starmie | 7.12% | 51.25% | 51.50% | 51.38% | 0.00 pp |
| Kecleon | 6.98% | 50.50% | 54.25% | 52.38% | 0.00 pp |
| Chris Brewer Lucario Hariyama | 6.90% | 53.50% | 52.25% | 52.88% | 0.00 pp |
| Unlimited Dragapult (Pidgeot / Rotom V) | 6.03% | 60.50% | 57.25% | 58.88% | 0.00 pp |
| Mill | 5.40% | 66.00% | 60.25% | 63.12% | 0.00 pp |
| 二森林 | 5.11% | 66.25% | 64.00% | 65.12% | 0.00 pp |
| Celebi Mill | 4.67% | 66.25% | 70.00% | 68.12% | 0.00 pp |
| Iron Thorns | 4.03% | 74.00% | 71.00% | 72.50% | 0.00 pp |
| Carpet Set G (Clefairy / Ledian 60) | 3.90% | 71.25% | 75.50% | 73.38% | 0.00 pp |
| Set D Standard 60 (Charm Ogerpon) | 2.16% | 85.50% | 85.00% | 85.25% | 0.00 pp |
| Set S Standard 60 (Floragato hunter) | 1.61% | 89.00% | 89.00% | 89.00% | 0.00 pp |
| Unlimited 60 (Ambipom Hand Fling) | 0.22% | 99.00% | 98.00% | 98.50% | 0.00 pp |
| Carpet Set H (Team Rocket's Zapdos / Pikachu 60) | 0.11% | 99.50% | 99.00% | 99.25% | 0.00 pp |

`complete` is false.
