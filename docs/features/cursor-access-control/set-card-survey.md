# Household set survey (engine v2 backlog)

Source: unique names in `SET_A`–`SET_F`, `SET_S`, `SET_T`, `SET_SPARE` resolved through `FALLBACK_BY_NAME` (the engine’s current printed text), plus `PREFERRED_IDS`. Live TCGDex rows in a trainer DB may differ (two Pikachu prints, Rockruff Invite Out vs Double Draw). This survey is **what the kernel would compile today**, not a photo audit.

Related: [design](./engine-v2-design.md), [spec](./spec.md).

## Headline

| | Count |
| --- | --- |
| Unique names across A–F, S, T, spare | 98 |
| Pokémon | 56 |
| Trainers | 32 |
| Energy | 10 |
| Missing fallback | 0 |
| Attack lines that are pure damage (no text) | 48 |
| Attack/ability lines with print that **did not parse** | 10 |
| Print slots with decision language (`you may`, `any number`, `up to`, `choose`, `look`, `search`, `flip`, `if you do`, `instead`) | 34 |
| Pokémon abilities in the house | 7 (3 parse, 4 do not) |

v1 already has a useful hook vocabulary for **attacks**. The gaps that force engine v2 are: (1) decisions executed inside `game.py` instead of on the Card, (2) trainers dispatched by name, (3) a handful of unparsed sentences, (4) `StrategySpec.swallow_look`.

## Complexity mix (unique Pokémon)

Most of the 56 Pokémon are simple. The interesting remainder is the v2 interface test, not a reason to delay the interface.

| Bucket | What it means | Approx. unique Pokémon | v2 action |
| --- | --- | --- | --- |
| 0 | Damage only, no text | ~18 (Starly, Sprigatito, Floragato, Dreepy, …) | Identity + pay cost + damage hook |
| 1 | Fixed effect, no choice (heal, draw, recoil, Asleep, item lock) | ~12 (Roselia, Budew, Orthworm Punch and Draw, Aron recoil, …) | Params on the card |
| 2 | Parsed numeric / search (`up to N`, look N, × energy) | ~10 (Carbink, Emolga, Clefairy Storm, Mewtwo, Mega Shooting Moons, …) | Params + maybe a decision |
| 3 | Print leaves a choice (`any number`, `in any way you like`, `you may`) | Dondozo, Clefable ex, Mega Clefable ex, Dragapult, Flutter Mane, Drakloak, Clefable Prankish, Aipom, Trekking/Tool Box as trainers | **Named decision points** |
| 4 | Print present, parser missed | 10 slots (below) | Parser or card-local handler, same hooks |
| 5 | Trainers | all 32 | Move `_resolve_trainer` onto the card; `_pick_trainer` → `Strategy.decide(game.play_trainer)` |

We do not know how wild future sets get. The survey says **today’s house fits a small hook catalog**. New kinds wait for a trunk version.

## Parsed effect kinds (attacks + abilities)

These are the v2 hook backlog that already exist as AST `kind` values:

`status`, `times`, `draw_until_hand` (trainers), `recoil`, `bench_damage_counters`, `call_family`, `damage_one_pokemon`, `heal`, `lock_items`, `search_item`, `move_psychic_energy`, `psychic_energy_times`, `attach_energy_from_deck_per_benched`, `ignore_wr`, `ignore_active_effects`, `swallow_energy`, `look_top_put_hand`, `draw_if_ko_last_turn`, `discard_hand_energy_bonus`, `transfer_charge`, `psychic_energy_bonus`, `draw`, `deck_count_bonus`, `damage_counter_bonus`, `prevent_basic_damage`, `discard_energy`, `energy_attack_lock`.

Not in this household (do not invent them on cards): copy-attack Metronome, mill opponent, Fairy Zone, Invisible Wall — those parsers exist in `effects.py` for other lists.

## Decision language vs what the kernel actually asks

Regex on print is not the interface. Several sentences use “in any way you like”, which the survey regex did not treat as `choose`. They still need named decisions.

| Card | Print (short) | Parsed? | v2 decision id | What v1 does |
| --- | --- | --- | --- | --- |
| Dondozo Swallow-Up | look 5, attach **any number** of Basic Energy | `swallow_energy` look 5 | `swallow.attach` | `min(look, swallow_look=3)` then greedy |
| Clefable ex Wondrous Moon | **you may** move **any amount** of Psychic **in any way you like** | `move_psychic_energy` | `move_energy` | Keep 3 on the attacker, dump rest on Mewtwo |
| Mewtwo Transfer Charge | attach **up to 2** from discard **in any way you like** | `transfer_charge` | `attach_from_discard` | Always “main Mewtwo”, take 2 if present |
| Mega Clefable ex Shooting Moons | **you may** discard **up to 4** Energy from hand | `discard_hand_energy_bonus` | `discard_hand.count` | Not a per-state policy |
| Dragapult Phantom Dive | 6 counters on benched **in any way you like** | `bench_damage_counters` 6 | `distribute_counters` | All 60 damage on lowest-HP bench |
| Flutter Mane Hex Hurl | 2 counters **in any way you like** | `bench_damage_counters` 2 | `distribute_counters` (same hook) | Same dump |
| Drakloak Recon Directive | look 2, **you may** put **1** in hand | `look_top_put_hand` | `look.which` | Implicit |
| Clefairy Moon-Watching Party | **you may** search 1 Psychic per benched Clefairy | `attach_energy_from_deck_per_benched` | `search.attach` per copy | Parser is correct (full deck, not top 6) |
| Clefable Prankish | **you may** put an Energy from opponent Active on top of deck | **unparsed** | `on_evolve.you_may` | Ability does nothing |
| Fezandipiti Flip the Script | **you may** draw 3 if KO last turn | `draw_if_ko_last_turn` | mostly param; once-per-turn is a constraint | Parsed |
| Trekking Shoes | look 1, **you may** hand or discard+draw | trainer name | `look.keep` | Heuristic in `_pick_trainer` / resolve |
| Tool Box | look 7, **you may** take Tools | trainer name | `look.take_matching` | Name dispatch |
| Boss’s Orders | switch **1** opponent bench | trainer name | `boss.target` | Lowest remaining HP |
| Iris’s Fighting Spirit | discard **another card**, then draw-until 6 | trainer + `draw_until_hand` | `discard.which` | `_iris_discard_choice` |
| Crispin | **up to 2** different Basic Energy, 1 hand / 1 attach | trainer name | `crispin.split` | Name dispatch |
| Aipom Mischievous Tail | look opponent top, **you may** shuffle | **unparsed** | `you_may` mill/shuffle | Attack is a stub |
| Gastly Astonish | **choose** a random card from opponent hand | **unparsed** | random is physics; still a hook | Stub |
| Crushing Hammer / coins | flip | trainer / status / `times` | `coin` (kernel RNG is fine; “which energy” is not) | Coin ok; Hammer target not asked |

The agent example you gave (Swallow-Up 1–5 depending on thin deck and hand Energy) is bucket 3. Phantom Dive spreading 6 counters is the same bucket and already in Set T.

## Unparsed print (parser miss, not missing cards)

These have English on the fallback card and **no** AST kind. v2 still puts the handler on the card; several can reuse existing hooks.

| Name | Slot | Sets | Text (truncated) | Likely hook |
| --- | --- | --- | --- | --- |
| Aipom | Mischievous Tail | A | Look at opponent’s top card. You may shuffle their deck. | `look` + `you_may` |
| Clefable | ability Prankish | C | On evolve, you may put an Energy from opponent Active on top of their deck | `on_evolve` + `you_may` |
| Clefable ex | ability Lunar Zone | C | Psychic-attached Pokémon have no Retreat Cost | static modifier (new hook or `on_retreat_cost`) |
| Cornerstone Mask Ogerpon ex | ability Cornerstone Stance | D | Prevent damage from opponent Pokémon that have an Ability | prevention filter (new hook) |
| Galarian Meowth | Fasten Claws | A | Flip: +20 | `times` / coin bonus (parser gap: “more damage” without “for each”) |
| Gastly | Astonish | F | Choose a random card from opponent hand, shuffle into deck | `hand_disrupt` |
| Haunter | Pain Amplifier | F | 2 counters on each opponent Pokémon that already has counters | `damage_counters` filter (not “in any way”) |
| Mega Clefable ex | ability Luminous Wing | C | Prevent effects of opponent Abilities on this Pokémon | prevention filter |
| Rockruff | Invite Out | A (fallback); B photo may be Double Draw | Flip: switch opponent bench with Active | `gust` + coin |
| Sudowoodo | Impound | B, E | Can’t retreat next turn | `lock_retreat` |

**Identity notes, not parser notes:**

- Set B lists two `Pikachu`. Fallback is one print (`sm3-40` Tail Whap / Thunder Shock). The second household print is Cosmic Eclipse Nuzzle (`sm12-66`) via `EXTRA_PRINT_IDS`. v2 identity is `catalog_id`, never the English name.
- Set A Rockruff is Crown Zenith Invite Out; Set B is Lost Origin Double Draw. Fallback is Invite Out for both names.
- Relicanth `Into the Deep` is registered with **empty text** (damage 0). Treat as `print_unresolved`.
- Several trainers/Pokémon still use slug ids (`energy-switch`, `oddish`, `plusle`, `relicanth`, `lickilicky`) instead of TCGDex pins.

## Abilities in the house

| Pokémon | Ability | Parsed kind | Sets |
| --- | --- | --- | --- |
| Clefairy | Moon-Watching Party | `attach_energy_from_deck_per_benched` | C |
| Drakloak | Recon Directive | `look_top_put_hand` | T |
| Fezandipiti ex | Flip the Script | `draw_if_ko_last_turn` | T |
| Clefable | Prankish | none | C |
| Clefable ex | Lunar Zone | none | C |
| Mega Clefable ex | Luminous Wing | none | C |
| Cornerstone Mask Ogerpon ex | Cornerstone Stance | none | D |

Stance / Lunar Zone / Luminous Wing are **static modifiers**. They probably need one new hook family (`on_damage_to_self`, `on_retreat_cost`, `on_ability_effect`) on trunk — the first “new kind” v2 should budget for, because they are already in C and D.

## Trainers: name switch is the kernel leak

All 32 trainers resolve through `_resolve_trainer` / `_pick_trainer` on `card.name`. Lillie and Iris are the only ones that reuse `parse_draw_until_hand(card.text)`. v2: compile trainer text to the same hook list; Strategy.decide keeps “whether to play Hop this turn”.

Household trainer hooks (from print, not from Python names): draw N, draw-until, shuffle-draw, search (Pokémon / Item / Tool / Energy / no Rule Box), bench Basic, switch, Boss gust, look-top (1 or 7), stadium, tool stats (Belt, Charm), Ultra Ball discard cost, coin hammer, recycle from discard, Iono/Judge/Unfair Stamp hand reset, Crispin split energy, Rare Candy evolve.

## Special Energy

| Name | Sets | Program on the card |
| --- | --- | --- |
| Double Colorless Energy | D | Provides Colorless×2 |
| Boomerang Energy | A | Provides Colorless; **on discard by that Pokémon’s attack**, reattach | needs `on_discard_by_attack` (Staraptor Power Blast already `discard_energy`) |

Basic Energy are params (type only).

## Per-set unique names

Counts: A 30/29 unique, B 30/23, C 30/13, D 30/8, E 30/20, F 30/18, S 30/13, T 30/19, spare 4/4.

### Set A (Rule B carpet — Dondozo / Starly)

| Name | n | Role |
| --- | --- | --- |
| Dondozo | 1 | Swallow-Up + Hydro Splash 180 — **v2 poster child** |
| Starly / Staravia / Staraptor | 1 each | Flap; Wing/Speed; Tailspin Away + Power Blast (Boomerang) |
| Orthworm | 1 | Draw 2; +150 if deck ≤3 |
| Flutter Mane | 1 | Hex Hurl distribute 2 counters |
| Carbink | 1 | Lucky Find up to 2 Items |
| Gligar | 1 | Toxic + extra poison counters |
| Aipom | 1 | Mischievous Tail unparsed |
| Galarian Meowth | 1 | Fasten Claws coin +20 unparsed |
| Rockruff | 1 | Invite Out unparsed |
| Metang | 1 | Bullet Punch coin × |
| Aron | 1 | Recoil 10 |
| Poliwhirl | 1 | Double Smash coin × |
| Baltoy, Bronzor, Corphish, Ferroseed, Oddish, Roselia | 1 | Simple / status |
| Tulip, Ultra Ball, Poké Ball, Energy Switch, Lake Acuity | 1 | Trainers |
| Water / Psychic×2 / Metal / Boomerang Energy | — | Energy |

### Set B (Rule B carpet — Pikachu / Spheal)

Two Pikachu **names**, one fallback print. Spheal line: Powder Snow Asleep → Sealeo damage → Walrein Frigid Fangs (energy attack lock) + Megaton Fall recoil. Emolga Call for Family. Plusle scales on damage counters. Sudowoodo Impound unparsed. Relicanth Into the Deep unresolved. Trekking Shoes look-1 you-may. 4 Lightning, 3 Grass, 2 Water.

### Set C (Clefairy party, no dedicated Energy)

4 Clefairy (Moon-Watching Party + Wonder Storm), 4 Clefable (Prankish unparsed), 4 Clefable ex (Lunar Zone unparsed + Wondrous Moon any-amount move), 4 Mega Clefable ex (Luminous Wing unparsed + Shooting Moons you-may discard up to 4), 2 Mewtwo ex (Transfer Charge + Photon). Trainers: Hop, SM Lillie draw-until, Nest, Energy Search, Maximum Belt, Tool Box, Arven, Boss. **Highest density of unparsed abilities.**

### Set D (Charm Ogerpon)

4 Cornerstone Mask Ogerpon ex (Stance unparsed + Demolish ignore W/R and effects), 8 Fighting, 4 DCE, Energy Search, Nest, Bravery Charm, Acerola, Switch. Stance is the prevention hook we do not have yet.

### Set E (Rule C carpet — Pikachu / Spheal, dedicated Energy)

Overlaps B’s electric/water line plus Hippopotas, Gengar Poltergeist, Surfer (if-you-do draw-until 5), Iris’s Fighting Spirit (discard then draw-until 6), Lake Acuity, 5 Water / 4 Lightning / 3 Fighting. Rule C: Pokémon are not energy.

### Set F (Rule C carpet — Staraptor / ghosts)

Starly line ×, Gastly Astonish unparsed, 2 Haunter Pain Amplifier unparsed, Gengar, Scream Tail Roaring Scream (20× counters to one Pokémon), Orthworm, Skwovet, Wailmer, Iono, Switch Cart, Nest, Ultra Ball, Energy Search, 6 Psychic / 3 Water / 3 Metal.

### Set S (Floragato hunter)

4 Sprigatito, 4 Floragato (Slashing Claw 90 only), 3 Wo-Chien ex (Covetous Ivy × prizes taken; Forest Blast 220), Tangela×2, Grass×2, Nest, Search, Switch, Jacq, Belt, Tool Box, Arven, Hop. Almost no decisions on the Pokémon; playstyle is “when to Switch into the cat”.

### Set T (Dragapult 30)

Dreepy / Drakloak (Recon look-2) / Dragapult ex (Phantom Dive **distribute 6**), Fezandipiti (Flip the Script + Cruel Arrow one target), Budew Itchy Pollen item lock. Trainers: Lillie’s Determination, Boss×2, Crispin, Ultra Ball, Poffin, Poké Pad, Crushing Hammer, Night Stretcher, Rare Candy, Unfair Stamp, Judge. This list is why `distribute_counters` cannot be Dondozo-specific.

### Spare

Gimmighoul Call for Family, Lickilicky damage, Tool Box, Fighting Energy.

## Kernel leaks to delete in v2 (from this survey)

1. `StrategySpec.swallow_look` and `min(printed, swallow_look)` in `game.py`.
2. `_bench_damage_counters` dumping every counter on one Pokémon.
3. `_move_psychic_energy` / `_transfer_charge` hard-wired to Mewtwo.
4. `_resolve_trainer` / most of `_pick_trainer` name tables (pick scores → Strategy.decide; resolve → card program).
5. Ability stubs that silently no-op (Prankish, Stance, Lunar Zone, Luminous Wing).

Strategy name tables (`if strat.name == "party"`) are a separate cleanup. They are not card programs. v2 Strategy is condition → decision; it must not steal card params. See [strategy-model.md](./strategy-model.md).

## Suggested first overlay (same chat, no git)

`sv04-055` Supplemental Swallow-Up: keep parsed `look: 5`; expose `swallow.attach`; drop the thrifty cap. That is the smallest proof that access control has an allow list. Phantom Dive `distribute_counters` is the second proof (Set T already prints it).
