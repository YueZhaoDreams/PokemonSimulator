# Family Cup play record — 2026-08-18

Carpet Set A (吃吼霸 / Dondozo) vs Carpet Set B (two Pikachu prints).
Family rules: 28 cards, opening 7, 3 prizes, Pokémon in hand may be attached as matching Basic Energy.

This note is the experience log from iterating **both** sides until the engine stopped making obvious family-play mistakes. Perfect play is not 50/50 — the cards still favor A.

## What was wrong

1. **Dumping the bench burned the energy.** A Pokémon that is Active or benched cannot later pay Hydro Splash or Volt Tackle. Early AI filled five bench slots at the start.
2. **Set B never took the knockout.** `control` scored Nuzzle (0 damage + paralysis) higher than Volt Tackle, even when Volt Tackle was payable. Dondozo is weak to Lightning: Volt Tackle is 140, not 70.
3. **One Pokémon in play ended the game.** Hydro Splash is 180. Pikachu is 60 HP. Empty bench + one attack = "opponent has no Pokémon in play."
4. **The second Pikachu was locked.** `protect=["Pikachu"]` refused to attach extra copies as Lightning once one was attacking.
5. **Grass Energy stole the attach.** Set B's Grass Energy was attached before Electrike, so Pikachu often never paid Lightning.

## Strategies that shipped

| Side | Name | How it plays |
| --- | --- | --- |
| A | `thrifty` | One Dondozo. Water Basics stay in hand as energy. Balls hunt Dondozo only. Swallow-Up looks at 3 and stops when Hydro Splash is payable. After Dondozo is out, bench one non-Water Pokémon (Orthworm first) as KO insurance. If Dondozo is prized, Orthworm / Flutter Mane becomes the attacker. |
| B | `nuzzle` | One Pikachu (prefer the Volt Tackle print). Lightning Basics stay in hand as energy. Nuzzle / Thunder Shock while charging; Volt Tackle once it is payable. After Pikachu is out, bench **two** non-Lightning Pokémon (Wailmer first) so Hydro Splash cannot wipe the board. Call for Family only fetches Pikachu. Extra Pikachu pays Lightning. |

## Iteration (10k unless noted)

| Step | A | B | A wins | What changed |
| --- | --- | --- | --- | --- |
| 0 | balanced | control | ~50% | Both dumped the bench. Fake even matchup. |
| 1 | thrifty, empty bench | control | 73.5% | A held energy. B still played like a standard TCG AI. |
| 2 | thrifty | nuzzle, 0 sponges | 73.2% (2k) | B used Volt Tackle / Nuzzle correctly, but Hydro Splash still wiped 60 HP Pikachu. |
| 3 | thrifty + 1 sponge | nuzzle + 2 sponges | **69.1%** | Honest prize fights. Seed `20260818`. Lab id `490cda4b-092b-49d7-b73e-cc19fdc12963`. |

## Final 10,000 games

- Seed `20260818`, 8.0s, engine `family-tcg-monte-carlo`
- **A 6,905 (69.1%) · B 3,095 (30.9%) · ties 0**
- Average 15.5 turns
- Dondozo reached play 85%; tutored 44% (Ultra Ball 34%, Poké Ball 10%)
- Dondozo in opening 7 → A wins 81.7%; Dondozo prized → A still 60.1%
- Pikachu in opening (at least one of two) → B wins **46.6%**; Pikachu prized → B 24.3%
- Hydro Splash used in 59% of games; Volt Tackle in 17%; Pikachu paralyzed Dondozo in 26%
- Wins by: 6,806 prize, 1,924 no Pokémon left, 1,201 A decked out, 69 B decked out

The remaining gap is the cards, not the AI: 180 damage vs 60 HP, and Set B has Energy Search / Call for Family but no Poké Ball or Ultra Ball.
