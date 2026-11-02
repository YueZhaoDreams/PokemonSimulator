# 二森林

Locked 60. Seed id `seed-two-forest`. Display name 二森林. Aliases `two-forest`, `二森林`, and `24`. The pilot is strategy `roast`. The deck does not select that spec by itself.

Celebi Mill stays `seed-celebi` (`SET_ROAST_NAMES`): zero Slumbering Forest, four Rescue Scarf, three Evolution Incense. On the current engine that seed's Litwick is Guardians Rising Flickering Flames. 二森林 is the list kept by `data/lab/set-mill-roast-forest.json`: one Rescue Scarf and one Evolution Incense from that 60, replaced by Slumbering Forest.

Litwick is Guardians Rising 11, Flickering Flames, HP 50. The printed sentence is: Your opponent's Active Pokémon is now Asleep. `fallback_named("Litwick")` stays Lost Origin Kindling Panic. Lampent is Plasma Storm 22, Freefloating. Pichu is HeartGold & SoulSilver Playground. Four Devolution Spray stay.

## Sample

Same foes and frozen Sisters weights as the Celebi Mill lock. 400 games per seat, both seats. A foe cell is the mean of the two seats.

| Seed | Role | Weighted | Exact |
| :--- | :--- | ---: | ---: |
| `20261101` | forest search seed | 46.28% ± 0.49% | 0.4627802802802803 |
| `20261102` | holdout | 45.30% ± 0.48% | 0.4530442942942943 |

Holdout `20261102` against the Kindling Panic zero-Forest list on that same seed is 45.30% versus 45.47%. See `data/lab/set-mill-roast-compare.md`.

Holdout engine, per game: Flickering Flames 1.94, sleep checks 2.58, Forest plays 0.74, mill cards 17.09, Time Distortion 3.75, Devolution Spray 1.69, Mountain Roasting fired 92.1%.

## List

- Litwick ×4
- Lampent ×4
- Chandelure ×4
- Celebi ◇ ×1
- Pichu ×3
- Arven ×4
- Team Rocket's Petrel ×2
- Buddy-Buddy Poffin ×2
- Energy Search ×3
- Rescue Scarf ×3
- Dawn ×4
- Level Ball ×2
- Broken Time-Space ×2
- Fire Energy ×7
- Hisuian Heavy Ball ×1
- Evolution Incense ×2
- Hyper Aroma ×1
- Jacq ×1
- Hop ×4
- Devolution Spray ×4
- Slumbering Forest ×2

Pokémon 16, trainers 37, Fire Energy 7.
