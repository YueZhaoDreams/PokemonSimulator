# Family Cup play record — 2026-08-18

Carpet Set A (Dondozo / Staraptor, 28) vs Carpet Set B (Walrein / two Pikachu prints, 30).
Family rules: 30 cards, opening 7, 3 prizes, Pokémon in hand may be attached as matching Basic Energy.

2026-08-20: carpet lists moved to 30. Set A cut Tool Box and added Metal / Water / Psychic Energy (still one Clefairy). Set B added Lightning Energy and Fire Energy (no Clefairy), then later cut Lickilicky / Aipom for Darkness Energy and a second Grass Energy. Constructed C / D / S each gained two typed energy of their line. Set E was already folded into C.

2026-08-22: Set B rebuilt around Surging Sparks Spheal / Sealeo / Walrein. Fire, Darkness, Spinarak, and Gimmighoul left the 30. Four Lightning Energy, three Grass, two Water, Trekking Shoes in. Megaton Fall 170 is the Dondozo KO; Thunder Shock still chips.

2026-08-22: Set A rebuilt as a **28-card** carpet: Paldea Evolved Starly / Staravia / Staraptor, Twilight Masquerade Boomerang Energy, Gligar, Aipom, and the metal leftovers (Aron / Ferroseed / Galarian Meowth). Clefairy, Psychic Energy, Trekking Shoes, and the ghost line left. Tailspin Away prevents Basic damage; Power Blast 180 discards energy and Boomerang returns. These names come from the new floor photos, not from `data/samples/set-a.jpg` / `set-b.jpg` (those files are the older carpets).

## What was wrong

1. **Dumping the bench burned the energy.** A Pokémon that is Active or benched cannot later pay Hydro Splash or Volt Tackle. Early AI filled five bench slots at the start.
2. **Set B never took the knockout.** `control` scored Nuzzle (0 damage + paralysis) higher than Volt Tackle, even when Volt Tackle was payable. Dondozo is weak to Lightning: Volt Tackle is 140, not 70.
3. **One Pokémon in play ended the game.** Hydro Splash is 180. Pikachu is 60 HP. Empty bench + one attack = "opponent has no Pokémon in play."
4. **The second Pikachu was locked.** `protect=["Pikachu"]` refused to attach extra copies as Lightning once one was attacking.
5. **Grass Energy stole the attach.** Set B's Grass Energy was attached before Electrike, so Pikachu often never paid Lightning.

## Strategies that shipped

| Side | Name | How it plays |
| --- | --- | --- |
| A | `thrifty` | Dondozo Hydro Splash. One Starly → Staravia → Staraptor. Boomerang Energy pays Colorless and returns after Power Blast. Tailspin Away walls Basic attackers. Water / Metal Basics stay as energy. Orthworm is KO insurance. Swallow-Up looks at 3; balls hunt Dondozo. |
| B | `shock` (default) | One Spheal → Sealeo → Walrein. Water Energy pays Megaton Fall 170 (KO on 160 HP Dondozo). Frigid Fangs locks ≤2 Energy. Thunder Shock Pikachu / Electrike chip + paralyze while the line evolves. Nuzzle Pikachu stays as Lightning. Plusle leftover closer. One Roselia. Two Fighting sponges. Energy Search / Retrieval / Trekking Shoes. |
| B | `nuzzle` | One Volt Tackle Pikachu. Hits 140 then stalls at 20 HP. Kept as a named alternative. |

## Iteration (10k unless noted)

| Step | A | B | A wins | What changed |
| --- | --- | --- | --- | --- |
| 0 | balanced | control | ~50% | Both dumped the bench. Fake even matchup. |
| 1 | thrifty, empty bench | control | 73.5% | A held energy. B still played like a standard TCG AI. |
| 2 | thrifty | nuzzle, 0 sponges | 73.2% (2k) | B used Volt Tackle / Nuzzle correctly, but Hydro Splash still wiped 60 HP Pikachu. |
| 3 | thrifty + 1 sponge | nuzzle + 2 sponges | 69.1% then 67.5% after Plusle math | Honest prize fights. Seed `20260818`. |
| 4 | thrifty | **shock** (chip + Plusle) | **66.6%** | B 33.4%. Electrike in opening → B 55%. Plusle finishes the 20 HP Volt Tackle cannot. |

## Final 10,000 games (shock, default B)

- Seed `20260818`, engine `family-tcg-monte-carlo`
- **A 6,658 (66.6%) · B 3,342 (33.4%) · ties 0**
- Average 16.5 turns
- Plusle reached play 50%; Plus Damage fired 18%
- Electrike in opening 7 → B wins 55.1%
- B going first 33.5%; going second 33.3%
- Dondozo Knocked Out 26.6% (vs 23.5% on the nuzzle plan)

Nuzzle / Volt Tackle on the same seed: A 67.5% / B 32.5%. The remaining gap is still the cards: Hydro Splash 180 vs 60 HP, and Set B has no balls.
