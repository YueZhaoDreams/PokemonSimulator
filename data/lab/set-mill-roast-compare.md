# Celebi Mill, same-seed comparison

Two 60-card lists, both played by the current roast policy, 400 games per seat, both seats. A foe cell is the mean of the two seats. Weights are the frozen Sisters loss weights.

Kindling is the locked list in `SET_ROAST_NAMES`. Litwick is Lost Origin 24, Kindling Panic, HP 60. The printed sentence is: Discard the top card of your opponent's deck. The list has four Devolution Spray, four Rescue Scarf, three Evolution Incense, and zero Slumbering Forest.

Flicker is `best.list` in `set-mill-roast-forest.json`. That list is the locked 60 with one Rescue Scarf and one Evolution Incense replaced by Slumbering Forest. Litwick is Guardians Rising 11, Flickering Flames, HP 50. The printed sentence is: Your opponent's Active Pokémon is now Asleep. Four Devolution Spray stay in the list.

The 4-spray sample in `set-mill-roast-spray.md` is seed `20261031`, weighted 46.23% ± 0.46%. That sample was recorded before this branch's Litwick print and before Broken Time-Space was limited to a Pokémon that still has to evolve on the turn it was played. Seed `20261031` in the table below is that same seed, replayed on the current engine.

Seed `20261101` is the Slumbering Forest search seed. The flicker row on that seed matches `set-mill-roast-forest.json`. Seed `20261102` was not used to choose the Forest cuts or the Devolution Spray cuts.

The locked list is unchanged.

## Weighted win rate

| Seed | Role | Kindling | ± | Flicker | ± | Flicker − Kindling | ± of difference |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `20261102` | holdout | 45.47% | 0.46% | 45.30% | 0.48% | -0.17% | 0.66% |
| `20261101` | forest search seed | 46.54% | 0.46% | 46.28% | 0.49% | -0.26% | 0.67% |
| `20261031` | spray search seed, current engine | 45.81% | 0.47% | 45.51% | 0.48% | -0.30% | 0.67% |

The difference uses independent samples. Its standard error is the square root of the sum of the two squared standard errors.

## Exact weighted rates

| Seed | Kindling | Flicker | Flicker − Kindling |
| :--- | ---: | ---: | ---: |
| `20261102` | 0.4547209709709710 | 0.4530442942942943 | -0.0016766766766766 |
| `20261101` | 0.4653578578578578 | 0.4627802802802803 | -0.0025775775775775 |
| `20261031` | 0.4580630630630630 | 0.4550913413413413 | -0.0029717217217217 |

## Lists

| Card | Kindling | Flicker |
| :--- | ---: | ---: |
| Litwick (print differs) | 4 | 4 |
| Rescue Scarf | 4 | 3 |
| Evolution Incense | 3 | 2 |
| Slumbering Forest | 0 | 2 |

Litwick count is four in both lists. The prints differ, as described above.

## Seed 20261102

| List | Weighted | ± | Mean | Worst | Flicker | Kindling Panic | Sleep checks | Forest plays | Mill cards | Time Distortion | Spray | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 Spray, Kindling Panic | 45.47% | 0.46% | 57.09% | 14.37% | 0.00 | 0.00 | 0.00 | 0.00 | 19.91 | 5.77 | 1.00 | 91.26% |
| 2 Forest, Flickering Flames | 45.30% | 0.48% | 56.50% | 10.25% | 1.94 | 0.00 | 2.58 | 0.74 | 17.09 | 3.75 | 1.69 | 92.10% |

| Foe | Kindling A | Kindling B | Kindling | Flicker A | Flicker B | Flicker | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 39.00% | 44.00% | 41.50% | 52.00% | 44.25% | 48.12% | +6.62% |
| Hedrick Worlds Dragapult | 61.00% | 62.25% | 61.62% | 56.75% | 61.50% | 59.13% | -2.50% |
| Unlimited Dragapult | 62.75% | 64.50% | 63.62% | 63.25% | 64.25% | 63.75% | +0.12% |
| Cornerstone Ogerpon (D60) | 13.75% | 15.00% | 14.37% | 21.75% | 20.50% | 21.12% | +6.75% |
| Wo-Chien / Floragato (S60) | 72.25% | 70.75% | 71.50% | 71.50% | 68.00% | 69.75% | -1.75% |
| Gholdengo (G) | 50.75% | 47.75% | 49.25% | 48.00% | 46.50% | 47.25% | -2.00% |
| Clefairy / Mewtwo (C60) | 57.50% | 49.00% | 53.25% | 57.00% | 59.25% | 58.13% | +4.88% |
| Set M (Mew ex) | 15.75% | 15.75% | 15.75% | 16.00% | 15.00% | 15.50% | -0.25% |
| Mega Starmie ex (Kudo) | 16.50% | 17.00% | 16.75% | 8.50% | 12.00% | 10.25% | -6.50% |
| Lucario Hariyama | 72.50% | 68.00% | 70.25% | 73.25% | 75.00% | 74.12% | +3.87% |
| Iron Thorns ex | 91.25% | 92.25% | 91.75% | 92.25% | 91.75% | 92.00% | +0.25% |
| Carpet Set H | 95.25% | 97.00% | 96.12% | 81.00% | 85.75% | 83.38% | -12.75% |
| Ambipom Hand Fling | 95.75% | 97.00% | 96.38% | 92.75% | 91.25% | 92.00% | -4.38% |

## Seed 20261101

| List | Weighted | ± | Mean | Worst | Flicker | Kindling Panic | Sleep checks | Forest plays | Mill cards | Time Distortion | Spray | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 Spray, Kindling Panic | 46.54% | 0.46% | 57.89% | 15.00% | 0.00 | 0.00 | 0.00 | 0.00 | 20.04 | 5.83 | 1.00 | 91.02% |
| 2 Forest, Flickering Flames | 46.28% | 0.49% | 57.28% | 12.62% | 1.98 | 0.00 | 2.62 | 0.75 | 17.03 | 3.73 | 1.68 | 91.72% |

| Foe | Kindling A | Kindling B | Kindling | Flicker A | Flicker B | Flicker | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 44.25% | 34.75% | 39.50% | 43.25% | 48.75% | 46.00% | +6.50% |
| Hedrick Worlds Dragapult | 60.50% | 60.25% | 60.38% | 62.00% | 58.25% | 60.13% | -0.25% |
| Unlimited Dragapult | 64.25% | 63.75% | 64.00% | 66.25% | 67.25% | 66.75% | +2.75% |
| Cornerstone Ogerpon (D60) | 15.50% | 15.75% | 15.62% | 22.75% | 26.25% | 24.50% | +8.88% |
| Wo-Chien / Floragato (S60) | 71.50% | 74.75% | 73.12% | 66.25% | 69.50% | 67.88% | -5.25% |
| Gholdengo (G) | 50.25% | 55.00% | 52.62% | 48.75% | 45.00% | 46.88% | -5.75% |
| Clefairy / Mewtwo (C60) | 56.75% | 58.75% | 57.75% | 54.75% | 62.50% | 58.62% | +0.87% |
| Set M (Mew ex) | 11.50% | 18.50% | 15.00% | 16.50% | 17.75% | 17.12% | +2.13% |
| Mega Starmie ex (Kudo) | 17.00% | 15.00% | 16.00% | 14.00% | 11.25% | 12.62% | -3.38% |
| Lucario Hariyama | 72.50% | 72.25% | 72.38% | 74.50% | 79.25% | 76.88% | +4.50% |
| Iron Thorns ex | 90.50% | 93.00% | 91.75% | 93.75% | 94.25% | 94.00% | +2.25% |
| Carpet Set H | 96.25% | 96.25% | 96.25% | 80.00% | 83.00% | 81.50% | -14.75% |
| Ambipom Hand Fling | 98.25% | 98.25% | 98.25% | 90.25% | 93.25% | 91.75% | -6.50% |

## Seed 20261031

| List | Weighted | ± | Mean | Worst | Flicker | Kindling Panic | Sleep checks | Forest plays | Mill cards | Time Distortion | Spray | Fired |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 4 Spray, Kindling Panic | 45.81% | 0.47% | 57.13% | 16.00% | 0.00 | 0.00 | 0.00 | 0.00 | 19.86 | 5.78 | 0.98 | 90.79% |
| 2 Forest, Flickering Flames | 45.51% | 0.48% | 56.41% | 12.25% | 1.97 | 0.00 | 2.57 | 0.74 | 17.12 | 3.75 | 1.69 | 92.15% |

| Foe | Kindling A | Kindling B | Kindling | Flicker A | Flicker B | Flicker | Delta |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 40.00% | 39.00% | 39.50% | 46.50% | 42.50% | 44.50% | +5.00% |
| Hedrick Worlds Dragapult | 56.25% | 59.00% | 57.62% | 62.50% | 59.00% | 60.75% | +3.12% |
| Unlimited Dragapult | 61.00% | 65.50% | 63.25% | 61.75% | 64.50% | 63.13% | -0.12% |
| Cornerstone Ogerpon (D60) | 15.25% | 17.00% | 16.12% | 26.75% | 22.00% | 24.38% | +8.25% |
| Wo-Chien / Floragato (S60) | 70.00% | 71.50% | 70.75% | 65.25% | 68.75% | 67.00% | -3.75% |
| Gholdengo (G) | 47.25% | 51.00% | 49.12% | 45.25% | 46.25% | 45.75% | -3.37% |
| Clefairy / Mewtwo (C60) | 53.75% | 55.75% | 54.75% | 55.75% | 55.25% | 55.50% | +0.75% |
| Set M (Mew ex) | 17.75% | 16.00% | 16.88% | 18.75% | 14.75% | 16.75% | -0.13% |
| Mega Starmie ex (Kudo) | 17.00% | 15.00% | 16.00% | 14.50% | 10.00% | 12.25% | -3.75% |
| Lucario Hariyama | 72.50% | 71.50% | 72.00% | 77.75% | 70.25% | 74.00% | +2.00% |
| Iron Thorns ex | 94.25% | 92.25% | 93.25% | 93.25% | 93.75% | 93.50% | +0.25% |
| Carpet Set H | 96.00% | 96.50% | 96.25% | 83.25% | 85.00% | 84.12% | -12.12% |
| Ambipom Hand Fling | 96.75% | 97.75% | 97.25% | 91.75% | 91.75% | 91.75% | -5.50% |

Elapsed 910.9s. Games per seat: 400. Workers recorded the cells in `set-mill-roast-compare.json`.

