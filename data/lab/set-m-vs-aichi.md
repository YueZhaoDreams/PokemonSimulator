# Set M vs Aichi Open 2026-05-10

Set M is the current `SET_M60_NAMES` list and the `mew_baby` strategy. No card in that list was changed.
Rules are Expanded (`expanded_60_rules`). Seed `20260510`.
Bench HP 30 is the count of side A's benched Pokémon whose printed maximum HP is 30, sampled after every turn.
Baby KOs are side A's printed-HP-30 Pokémon, split by where they were when Knocked Out.
Balloon is the number of times Bursting Balloon's sentence resolved, not the damage-counter total.
Sky Field and Battle Cage cannot be in play together: a new Stadium replaces the old one.

## 细田周 Raichu / Electrode

Requested 60 (16 Pokémon / 32 Trainer / 12 Energy). Electrode-GX ×4, Voltorb ×4, Alolan Raichu ×3,
Pikachu ×3, Tapu Koko ◇ ×1, Zeraora-GX ×1, and the trainer and energy counts named in the request.
Zeraora is Lost Thunder Zeraora-GX. Battle Compressor is the existing Team Flare Gear sentence.
Thunder Mountain ◇ is listed ×2 because the request says ×2.
This is not Limitless list 26812.

## 吉冈 Regidrago control

Same Set M. The control is a 60 that contains Battle Compressor, Kyurem's Trifrost, and Path to the Peak,
plus a Regidrago V / VSTAR, Double Dragon Energy, Grass, and Fire shell.
Limitless tournament 566 rank 10 is a different 20-Pokémon Regidrago list and plays Parallel City.
Rank 11 is a different player. This cell keeps Path to the Peak because the request asked for 颠峰之径.
It is a control, not a verbatim Limitless paste. Set M is the same list in both cells.

## Smoke (300)

| Cell | M win rate | Bench HP 30 | Baby KO bench | Baby KO active | Balloon triggers | Sky Field turns | Sky Field with Battle Cage |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hosoda Raichu / Electrode | 98.3% | 3.362 | 127 | 24 | 14 | 542 | 0 |
| Regidrago control (Trifrost, compressor, Path) | 81.7% | 3.304 | 646 | 146 | 37 | 0 | 0 |

## 1000 games

| Cell | M wins | M win rate | Going first | Going second | Bench HP 30 | Baby KO bench | Baby KO active | Balloon triggers | Sky Field turns | Sky Field with Battle Cage |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Hosoda Raichu / Electrode | 982/1000 | 98.2% | 97.6% | 98.8% | 3.441 | 396 (0.40/game) | 74 (0.07/game) | 47 (0.05/game) | 1701 (1.70/game) | 0 |
| Regidrago control (Trifrost, compressor, Path) | 815/1000 | 81.5% | 75.0% | 88.0% | 3.268 | 2141 (2.14/game) | 518 (0.52/game) | 148 (0.15/game) | 0 (0.00/game) | 0 |

Bench HP 30 is `bench30_end_sum_a / bench30_end_n_a` (mean Pokémon, not a sum across the match).

| Cell | Electro Rain attacks | Energy cards discarded by Electro Rain | Extra Energy Bomb attaches | Apex Dragon | Trifrost |
| :--- | ---: | ---: | ---: | ---: | ---: |
| Hosoda Raichu / Electrode | 212 | 461 | 986 | 0 | 0 |
| Regidrago control (Trifrost, compressor, Path) | 0 | 0 | 0 | 557 | 0 |

Apex Dragon copies Trifrost from the discard, so those hits are counted on Apex Dragon.
The Trifrost column is Kyurem using the attack on its own card.

Elapsed smoke 27.5s, 1000-game cells 88.6s.
