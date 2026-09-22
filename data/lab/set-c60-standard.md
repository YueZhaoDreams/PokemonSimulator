# Set C → Standard 60 (Pokémon are not energy)

Date: 2026-09-11
Seed: `20260911`
Engine: `family-tcg-monte-carlo`
Rule: **s60** — 60 cards, 4 of a name, 6 prizes, Pokémon are not Basic Energy
Games: 3,000 / cell (C60 is always player A; who goes first is random)
Script: `data/lab/set_c60_standard.py`
Raw: `data/lab/set-c60-standard.json`

Family Cup **Set C stays 30 cards** (`SET_C_NAMES`). That list has **no dedicated Energy** because Rule B treats the Clefable line as Psychic. This file is the constructed rewrite for real Standard 60.

## How the 30-card list changes

The 30-card identity is LOR 62 Moon-Watching Party → load Psychic onto benched Clefairy → Photon Kinesis on Mewtwo ex, with Clefable / Clefable ex / Mega as the wall. Under s60 that engine **needs Psychic Energy cards in the deck**. Party searches Energy, not Pokémon.

| 30-card Set C (Rule B) | Standard 60 rewrite |
| --- | --- |
| 4 Clefairy / 2 Mewtwo ex / 4 Clefable / 4 Clefable ex / 4 Mega | 4 Clefairy / **3** Mewtwo ex / **2 Rebel Clash Prankish Clefable** / **3** Clefable ex / **2** Mega |
| 0 Energy (Pokémon pay Party) | **14 Psychic Energy + 2 Telepathic Psychic Energy** |
| 2 Nest, 0 Poffin, 0 Switch | 4 Nest, **4 Poffin** (Clefairy is 60 HP), **2 Switch** (Party is Active-only) |
| 1 Boss | **3 Boss** (6-prize race) |
| 2 Hop / 1 Lillie | 1 Hop / 1 Lillie / 1 Lillie's Determination / Penny / Turo / Briney / Seeker |
| Arven + Belt | kept (ACE SPEC Belt still 1; Tool Box cut for a 14th Psychic) |
| — | **3 Battle Cage** (−Jacq −Energy Retrieval −1 Iono; see [bench shields](set-c60-bench-shield.md)) |

Thinned Stage 1 pile: four Mega in a 6-prize format is three-prize suicide. Two Mega sponge Phantom Dive / Demolish; three Clefable ex keep Lunar Zone. Third Mewtwo is a second closer after the first 2-prize KO.

Locked C60 list (`SET_C60_NAMES`):

| Qty | Card | Role |
| ---: | --- | --- |
| 4 | Clefairy (LOR 62) | Party engine |
| 3 | Mewtwo ex | Photon closer / 230 HP tank |
| 2 | Clefable (RCL 75 Prankish) | On evolve, bounce an Energy off the opponent's Active; 110 HP sponge |
| 3 | Clefable ex | Lunar Zone + Wondrous Moon 170 |
| 2 | Mega Clefable ex | 320 HP sponge / Shooting Moons |
| 4 | Nest Ball | Bench Mewtwo / Clefairy |
| 4 | Buddy-Buddy Poffin | Bench two 60 HP Clefairy |
| 2 | Ultra Ball | Pokémon tutor |
| 1 | Hop | Draw 3 |
| 1 | Lillie | Draw until 6 (8 on first turn) |
| 1 | Lillie's Determination | Shuffle draw 6 / 8 |
| 1 | Arven | Belt + Item |
| 3 | Boss's Orders | Pull a prize |
| 2 | Penny | Basic + all attached cards to hand. Second Party after Telepathic; full HP on replay |
| 1 | Professor Turo's Scenario | Any Pokémon to hand; discard attachments. Evolved bounce / ex heal |
| 1 | Mr. Briney's Compassion | Non-ex Pokémon + attachments to hand. Double Prankish |
| 1 | Seeker | Each player returns 1 Bench Pokémon + attachments. Opponent bench |
| 2 | Switch | Rotate Party Active; Seeker needs the Clefable on the bench |
| 1 | Energy Switch | Party Energy → Mewtwo |
| 1 | Night Stretcher | Recycle Pokémon or Energy |
| 1 | Maximum Belt | ACE SPEC +50 vs ex |
| 3 | Battle Cage | Stadium: both benches ignore opp counter placement (Dive) |
| 2 | Telepathic Psychic Energy | From-hand attach benches up to 2 Basic Psychic; then Party |
| 14 | Psychic Energy | Pays Party / Photon / Zone |

## Foes (household Standard 60, not Limitless meta)

The engine does not have a full 2026 Limitless field (Gardevoir, Charizard, etc.). The bakeoff uses lists the simulator already plays:

| Key | List | Strategy |
| --- | --- | --- |
| G | Carpet Set G (already 60: Clefairy / Ledian / Staraptor) | `carnival` |
| D60 | Set D Charm Ogerpon stretched to 60 (4 Ogerpon, 14 Fighting, 4 DCE, 4 Charm) | `demolish` |
| T60 | Set T Dragapult stretched to 60 (4 Dreepy / 3 Drakloak / 3 Dragapult, Rare Candy 4) | `phantom` |
| T meta | Worlds 2026 Hedrick Dragapult (printed 60) | `phantom` |
| T UNL | Unlimited-shaped Pidgeot / Rotom Dragapult 60 | `phantom` |
| S60 | Set S Floragato hunter stretched to 60 | `slash` |

G's AI is the Staraptor carnival script, not a dedicated Ledian/Party hybrid, so C60 vs G overstates a tuned bird list.

## Head-to-head (C60 win rate)

| Foe | Overall | C60 first | C60 second |
| --- | ---: | ---: | ---: |
| Charm Ogerpon 60 (D60) | **75.3%** | 76.8% | 73.8% |
| Carpet Set G | **98.0%** | 98.2% | 97.8% |
| Dragapult 60 (T60) | **54.3%** | 56.1% | 52.5% |
| Floragato hunter 60 (S60) | **99.6%** | 99.7% | 99.4% |

`pokemon_as_energy_per_game` is 0 on s60 (Party attaches **cards** named Psychic Energy).

Full pairwise matrix including Hedrick and the Unlimited-shaped Pidgeot/Rotom 60: [set-c60-unl-matrix.md](set-c60-unl-matrix.md). On this branch C60 vs T60 is **48.7%** (printed 0-cost Itchy Pollen).

Lock update 2026-09-18: **3 Battle Cage** (−Jacq −Retrieval −1 Iono) moves T60
51.3 → **69.1**, Hedrick 59.0 → **64.6**, UNL 82.8 → **89.5**, D60 holds 76.1.
Full bakeoff + locked array: [set-c60-bench-shield.md](set-c60-bench-shield.md).

Lock update 2026-09-22: bounce package replaces 1 Hop, 1 Lillie, 1 Lillie's Determination, the last Iono, and 1 Energy Switch.

- **Penny** (SVI 183): `Put 1 of your Basic Pokémon and all attached cards into your hand.` Attach Telepathic to the Active Clefairy (bench up to 2), Party, Penny that Basic, promote, Party again. Mewtwo ex is Basic, so the same sentence also picks up a chipped Mewtwo and its Energy.
- **Professor Turo's Scenario** (PAR 171): `Put 1 of your Pokémon into your hand. (Discard all attached cards.)` Any Pokémon, including Clefable / Clefable ex / Mega. Attachments are discarded.
- **Mr. Briney's Compassion** (DR 87): `Choose 1 of your Pokémon in play (excluding Pokémon-ex). Return that Pokémon and all cards attached to it to your hand.` This is the Prankish bounce that keeps Energy cards.
- **Seeker** (UD 85): `Each player returns 1 of his or her Benched Pokémon and all cards attached to it to his or her hand. (You return your Pokémon first.)` The Clefable has to be on the Bench (Switch first). The opponent also returns a Bench Pokémon.
- **AZ** is the same effect as Turo and is not in the 60. **Cheren's Care** is `Put 1 of your Colorless Pokémon that has any damage counters on it and all attached cards into your hand.` This line is Psychic, so Cheren cannot target it.

Leaving play removes damage counters. The card comes back, and the next time it is played it is a new Pokémon at full HP. A Basic played that turn cannot evolve. Double Prankish needs two Clefairy that were already in play: evolve one, bounce the Clefable, promote the other, Party, evolve that Clefable onto it.

### Read

- **Vs Ogerpon:** 30-card Rule B C vs D sat near 50%. With real Energy + Switch + three Boss, Photon still outraces Demolish 140. Charm 260 is 2 prizes; empty Clefairy is 1. Overall **75.3%**.
- **Vs Dragapult:** After Party, C60 Photons and Moons for whatever they pay. Clefable is **Prankish** (110 HP). Energy Search is gone: s60 Search is a delayed energy that Budew can lock, so the slot is a **15th Psychic Energy**. Same seed: **54.3%** vs household T60 (first 56.1% / second 52.5%).
- **Vs Worlds Hedrick Dragapult:** Printed Worlds 2026 60 is `SET_T_META_NAMES`. Same seed: **62.9%** (first 63.8% / second 61.9%). Household T60 (4 Candy) remains harder. Write-up: `data/lab/set-c60-vs-hedrick.md`.
- **Vs G / Floragato:** Carnival and slash do not assemble a 6-prize closer before Photon. Those cells are blowouts, not a claim that C60 is a tournament deck.

## How C60 loses to Dragapult

Same seed family, 1,500 extra traced games (C60 still 28.8%). Almost every Dragapult win is a **prize race**, not a deck-out or Budew lock.

| In a C60 loss | Rate / count |
| --- | --- |
| Dragapult took all 6 prizes | **96%** of losses |
| Phantom Dive fired | **99.6%** of losses (**3.89** Dives / loss vs 0.51 / win) |
| At least one Clefairy KO | **95%** (1.81 Clefairy KOs / loss) |
| At least one Mewtwo ex KO | **95%** (1.31 / loss; 2 prizes each) |
| Mega Clefable ex KO (3 prizes) | **37%** of losses |
| Dragapult ex itself KO'd | **0.03** / loss |
| Photon Kinesis fired | 70% of losses, **1.33** Photons / loss vs **3.09** / win |
| Itchy Pollen item lock | **15%** of losses — not the main line |
| Mean length | 16.1 turns (wins are shorter: 13.9) |

Prize split when C60 loses: most often **0–2 prizes for C60, 6 for Dragapult**. C60's KOs in those games are mostly **Budew** (1 prize) and leftover Dreepy / Fez, not the 3-prize Dragapult.

**Why Dive wins the math.** Phantom Dive does 200 to Active and puts 6 damage counters on the bench. Clefairy is 60 HP, so one Dive KOs the Active snack **and** a benched Party engine (60 = 6 counters). Mewtwo is 230, so a second Dive or a Boss into a chipped body takes 2 prizes. Mega is 320 / 3 prizes: Boss + two Dives, or one Dive into a 120 HP leftover Mega, ends the game.

Typical 12-turn loss (C60 never Photoned): Boss Mewtwo → Budew chip → Candy Dragapult → Boss Clefable ex → Dive 200 (2 prizes) → Dive Mega → Boss Mewtwo → Dive (2) → Dive leftover Mega (3). That's 6+ prizes without C60 attacking.

C60's wins look the opposite: Photon fires ~3 times, Dragapult dies (~0.45 KO / win), and C60 often wins by **clearing the board** (Budew / Dreepy / Fez) before Candy, not only by taking 6 prizes.

The 30-card Family Cup matchup hid this: 3 prizes and a half-list Dragapult. Standard 60 gives Dragapult Rare Candy ×4 and six prizes to spend on the Party board.

## Prankish vs CLC

Rebel Clash **Clefable** (`swsh2-75`): Psychic, 110 HP, Prankish — when you evolve, you may put an Energy attached to the opponent's Active on top of their deck. Moon Kick `[P][C]` 60.

Classic **CLC 014** is still in the catalog (`Clefable CLC`) for Metronome tests. It is Colorless 70 HP, Metronome `[C]`. Same printed name as RCL, so it cannot sit beside Prankish as extra copies.

s60 does not treat Pokémon as energy, so Prankish is not Party fuel. The remaining edge is **110 HP** plus bouncing an attach (Fighting vs Demolish; Fire/Psychic can delay Dive). CLC's edge is copying Dive when Dragapult is Active; the 70 HP body is a Munkidori / Risky Ruins snack.

Same seed `20260911`, 3,000 games, C60 otherwise as then locked (14 Psychic + Energy Search):

| 2-of Clefable | vs T60 | vs Hedrick | vs D60 |
| --- | ---: | ---: | ---: |
| CLC Metronome | 52.3% | 60.6% | 72.5% |
| Prankish | 53.6% | 65.9% | 72.5% |

## Energy Search → 15th Psychic

s60 Energy Search only finds a Basic Energy and does not attach it. Budew can lock the Item. The slot is now a **15th Psychic Energy**.

Same seed, 3,000 games, Prankish C60:

| Foe | 14 Psychic + Search | **15 Psychic (this lock)** |
| --- | ---: | ---: |
| T60 | 53.6% | **54.3%** |
| Hedrick | 65.9% | **62.9%** |
| D60 | 72.5% | **75.3%** |

Household Candy Dragapult and Ogerpon go up; Hedrick (Munkidori / Risky Ruins, slower Dive) likes the extra trainer more than the extra brick.

## What I would not do

- Do not keep 4/4/4 Clefable / ex / Mega. Copy-cap legal, but the deck becomes 18 Stage 1s and bricky under real Energy.
- Do not leave 0 Switch. Moon-Watching Party only fires from Active; the 30-card list leaned on Rule B chump sequences.
- Do not put CLC Metronome back in this 2-of slot unless the plan is specifically to copy Dive on a 70 HP body.
- Do not put Energy Search back unless you want the Hedrick cell more than T60 / D60.
- Do not add Budew for Item lock. Itchy Pollen is Items only; 1-of for 1 Psychic lost T60 / Hedrick / D60 even with a sit-and-Pollen party path (see [set-c60-budew-item-lock.md](set-c60-budew-item-lock.md)).
- Do not swap Night Stretcher for Tulip. 1-for-1 is a wash / Stretcher slightly better vs Hedrick (see [set-c60-tulip-vs-stretcher.md](set-c60-tulip-vs-stretcher.md)). 2 Tulip −2 Hop already lost T60.
- Do not cut a Psychic Energy for Lillie's Clefairy ex. Fairy Zone helps T60 / Hedrick a little and costs ~5 points vs D60 (see [set-c60-lillie-clefairy-ex.md](set-c60-lillie-clefairy-ex.md)).
- Energy line is **14 Psychic + 2 Telepathic Psychic Energy**. Do not go to 3 or 4 Telepathic. Pre-Cage T60 going second collapsed (see [set-c60-telepathic-energy.md](set-c60-telepathic-energy.md)). Battle Cage C60 re-checked 2026-09-22: tele4 still dumps Hedrick (−1.9) and T60 second (see [set-g-c60-telepathic.md](set-g-c60-telepathic.md)).
- Do not cut Maximum Belt + Arven for 2 more Telepathic plus a free slot. Dragapult rises ~3–5 points; Charm Ogerpon drops ~14 because Photon 7 + Belt is the 270 OHKO on 260 Charm (see [set-c60-belt-vs-telepathic.md](set-c60-belt-vs-telepathic.md)).
- Tool Box is out: the 1-for-1 is a **14th Psychic Energy**, not a 3rd Telepathic (T60 going second 46.4% with the extra special; see [set-c60-toolbox-swap.md](set-c60-toolbox-swap.md)). 4th Boss / 3rd Iono also lose T60. Arven still searches Belt.
- Do not treat this as a replacement for Family Cup Set C. Rule B Clefable-as-energy is a different game.
