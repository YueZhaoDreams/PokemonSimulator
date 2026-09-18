# C60 bench shields vs Dragapult (Battle Cage lock)

Date: 2026-09-18
Seed: `20260911`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / cell (C60 variant is always player A; who goes first is random)
Script: `data/lab/set_c60_bench_shield.py`
Raw: `data/lab/set-c60-bench-shield.json` (7-variant bakeoff),
`data/lab/set-c60-bench-shield-final.json` (locked 6-foe array)

Phantom Dive is 200 to the Active plus **6 damage counters** on the Bench — an
attack *effect*, not damage. So "prevent damage" shields (Manaphy, Shaymin) do
not stop the bench bleed; only attack-effect prevention (Rabsca) or
counter-placement prevention (Battle Cage) does. This lab implements that layer
split, then bakes off the three shield directions for C60.

## Engine work (printed text wins)

New parser branches in `parse_ability_effects`, each with a test using the
exact printed wording (`tests/test_bench_shields.py`):

| Card | Printed text (short) | Effect kind |
| --- | --- | --- |
| Rabsca TEF 24 Spherical Shield | Prevent all damage from and effects of attacks … done to your Benched Pokémon | `prevent_bench_damage_and_attack_effects` |
| Shaymin DRI 10 Flower Curtain | Prevent all damage done to your Benched Pokémon that don't have a Rule Box by attacks … | `prevent_bench_attack_damage_no_rulebox` |
| Battle Cage ME02 85 (Stadium) | Prevent all damage counters from being placed on Benched Pokémon (both yours and your opponent's) by effects of attacks and Abilities … (Damage from attacks is still taken.) | `stadium_prevent_bench_counters` |
| Manaphy BRS 41 Wave Veil | Prevent all damage done to your Benched Pokémon by attacks … | `prevent_bench_attack_damage` (unchanged) |

Layer fixes in `app/engine/game.py`:

- `_bench_damage_counters` (Dive, Hex Hurl): blocked by Rabsca and Battle Cage
  only. Manaphy/Shaymin no longer block counters (old `test_wave_veil_*`
  asserted the wrong interaction and now asserts counters land).
- `_damage_one_pokemon` (Cruel Arrow "does damage"): blocked by Rabsca/Manaphy
  for the whole bench, by Shaymin for non-Rule-Box bench only (ex bench still
  hittable). Battle Cage never blocks damage. A shielded bench pivots the hit
  to the Active instead of fizzling.
- `_move_damage_counters` (Adrena-Brain): Rabsca does not block Abilities.
  Under Battle Cage the attacker aims the Active; counters aimed at a bench
  vanish after leaving the donor (printed ruling).

Cards added to `app/seed_data.py`: Rellor TEF 23 (50 HP, Poffin-legal),
Rabsca TEF 24, Shaymin DRI 10, Battle Cage ME02 85.

AI: party benches Rellor/Shaymin vs phantom only (never opens on them),
evolves Rabsca first vs phantom, tutors the line via Nest/Poffin/Ultra/Jacq,
plays Battle Cage at 19 vs phantom (above Hop/Lillie 17, below Belt 21), and
keeps shield pieces out of Ultra Ball discards. Phantom bumps an enemy Cage
with Risky Ruins / Collapsed Stadium at 14. T60 runs no Stadium, so Cage
sticks all game there.

## Bakeoff (vs three Dragapults + Ogerpon)

Cuts tested: `-Hop -Iono`, `-Jacq -Energy Retrieval`, `-Iono`.

| C60 variant | T60 | Hedrick | UNL | D60 |
| --- | ---: | ---: | ---: | ---: |
| base (pre-shield) | 51.3% | 59.0% | 82.8% | 76.0% |
| cage2-hop-iono | 65.2% | 61.5% | 87.8% | 73.6% |
| **cage2-jacq-retr** | **67.1%** | **62.5%** | **88.8%** | **78.2%** |
| cage1-iono | 62.0% | 60.6% | 86.0% | 75.6% |
| rabsca-hop-iono | 52.5% | 57.3% | 83.2% | 73.6% |
| rabsca-jacq-retr | 51.4% | 58.5% | 84.7% | 78.0% |
| shaymin-iono | 50.6% | 57.4% | 82.7% | 74.8% |

Read:

- **Battle Cage is the whole story.** 2-of with `-Jacq -Retrieval` jumps T60
  **51.3 → 67.1 (+15.8)**, Hedrick +3.5, UNL +6.0, and even D60 +2.2. 1-of
  already gains +10.7 vs T60; the 2nd copy is worth ~+5 more.
- **Rabsca 1-1 does nothing** (+0-1 vs T60, flat-to-down elsewhere). It is not
  an AI bug: Spherical Shield blocks 0.73×/game vs Cage's 2.10×/game (400-game
  trace). A 1-1 Stage 1 that needs a turn to evolve, eats a bench slot, and
  dies to Boss on 50/70 HP bodies cannot cover Dive turns. Do not lock it.
- **Shaymin does nothing vs Dive** (50.6% vs 51.3%), as the wording predicts:
  Flower Curtain is damage-only, and Dive's bench output is counters. It only
  redirects Cruel Arrow onto the Active. Do not lock it.
- Cuts: `-Jacq -Retrieval` beats `-Hop -Iono` everywhere (D60 78.2 vs 73.6).
  Jacq/Retrieval are the two most marginal cards once the bench is safe.

Follow-up screening (3,000/cell): a 3rd Cage for `-Iono` beats cage2 on both
Candy Dragapults (T60 68.5 vs 67.1, Hedrick 66.4 vs 62.5 — re-establishes after
a Risky Ruins bump) at a small D60 cost (75.3 vs 78.2, still at base). A 3rd
Cage for `-Hop` instead is worse (T60 65.5). So the lock is 3 Cage.

## Locked C60 (`SET_C60_NAMES`)

`-Jacq -Energy Retrieval -1 Iono +3 Battle Cage` (60 cards, copy-legal):

4 Clefairy / 3 Mewtwo ex / 2 Clefable (RCL Prankish) / 3 Clefable ex /
2 Mega Clefable ex / 4 Nest / 4 Poffin / 2 Ultra / 2 Hop / 2 Lillie /
2 Lillie's Determination / 1 Arven / 3 Boss / **1 Iono** / 2 Switch /
2 Energy Switch / 1 Night Stretcher / 1 Maximum Belt / **3 Battle Cage** /
2 Telepathic Psychic Energy / 14 Psychic Energy.

C60 runs no bench-counter output of its own (Photon / Moon / Moons are all
Active damage), so Cage's symmetric text costs it nothing.

## Final win-rate array (locked C60, 3,000/cell)

| Foe | strat | Overall | C60 first | C60 second |
| --- | --- | ---: | ---: | ---: |
| Carpet Set G | carnival | **88.1%** | 89.9% | 86.4% |
| Charm Ogerpon 60 (D60) | demolish | **76.1%** | 79.4% | 72.9% |
| Dragapult 60 (T60) | phantom | **69.1%** | 69.0% | 69.2% |
| Worlds Hedrick Dragapult | phantom | **64.6%** | 65.3% | 63.8% |
| UNL Pidgeot/Rotom Dragapult | phantom | **89.5%** | 91.3% | 87.7% |
| Floragato hunter 60 (S60) | slash | **99.7%** | 99.8% | 99.5% |

Pre-shield base on the same seed: G 89.3 / D60 76.0 / T60 51.3 /
Hedrick 59.0 / UNL 82.8 / S60 99.5. Deltas: **T60 +17.8**, Hedrick +5.6,
UNL +6.7, D60 +0.1, G −1.2, S60 +0.2. Mean over the six: 76.3 → 81.2.
Cage erases the going-second gap vs T60 (base 53.9/48.7 → locked 69.0/69.2).

## What I would not do

- Do not lock Rabsca 1-1 (or Shaymin) for the Dragapult matchup; re-test only
  with a thicker line plus a Boss answer, and expect the bench slot to cost.
- Do not cut the 3rd Cage for a 2nd Iono: Hedrick/UNL bump the first Cage and
  the re-establish is worth more than the disruption.
- Do not cut Hop for shield slots; Hop trims lose T60 (cage3-hop 65.5).
- Do not play Cage late: party scores it 19 vs phantom so it lands before the
  first Dive; holding it for "value" just bleeds Clefairy.
