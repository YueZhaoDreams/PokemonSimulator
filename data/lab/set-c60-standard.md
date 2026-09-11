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
| 4 Clefairy / 2 Mewtwo ex / 4 Clefable / 4 Clefable ex / 4 Mega | 4 Clefairy / **3** Mewtwo ex / **2 CLC Metronome Clefable** / **3** Clefable ex / **2** Mega |
| 0 Energy (Pokémon pay Party) | **14 Psychic Energy** |
| 2 Nest, 0 Poffin, 0 Switch | 4 Nest, **4 Poffin** (Clefairy is 60 HP), **2 Switch** (Party is Active-only) |
| 1 Boss | **3 Boss** (6-prize race) |
| 2 Hop / 1 Lillie | 2 Hop / 2 Lillie / 2 Lillie's Determination / 2 Iono |
| Arven + Belt + Tool Box | kept (ACE SPEC Belt still 1) |

Thinned Stage 1 pile: four Mega in a 6-prize format is three-prize suicide. Two Mega sponge Phantom Dive / Demolish; three Clefable ex keep Lunar Zone. Third Mewtwo is a second closer after the first 2-prize KO.

Locked C60 list (`SET_C60_NAMES`):

| Qty | Card | Role |
| ---: | --- | --- |
| 4 | Clefairy (LOR 62) | Party engine |
| 3 | Mewtwo ex | Photon closer / 230 HP tank |
| 2 | Clefable (CLC 014 Metronome `[C]`) | Copy Phantom Dive / other Active attacks |
| 3 | Clefable ex | Lunar Zone + Wondrous Moon 170 |
| 2 | Mega Clefable ex | 320 HP sponge / Shooting Moons |
| 4 | Nest Ball | Bench Mewtwo / Clefairy |
| 4 | Buddy-Buddy Poffin | Bench two 60 HP Clefairy |
| 2 | Ultra Ball | Pokémon tutor |
| 2 | Hop | Draw 3 |
| 2 | Lillie | Draw until 6 (8 on first turn) |
| 2 | Lillie's Determination | Shuffle draw 6 / 8 |
| 1 | Arven | Belt + Item |
| 1 | Jacq | Evolution tutor |
| 3 | Boss's Orders | Pull a prize |
| 2 | Iono | Hand disruption |
| 2 | Switch | Rotate Party Active |
| 2 | Energy Switch | Party Energy → Mewtwo |
| 1 | Energy Retrieval | Hand fuel for Shooting Moons |
| 1 | Energy Search | Psychic tutor |
| 1 | Night Stretcher | Recycle Pokémon or Energy |
| 1 | Maximum Belt | ACE SPEC +50 vs ex |
| 1 | Tool Box | Top-7 Tool |
| 14 | Psychic Energy | Pays Party / Photon / Zone |

## Foes (household Standard 60, not Limitless meta)

The engine does not have a full 2026 Limitless field (Gardevoir, Charizard, etc.). The bakeoff uses lists the simulator already plays:

| Key | List | Strategy |
| --- | --- | --- |
| G | Carpet Set G (already 60: Clefairy / Ledian / Staraptor) | `carnival` |
| D60 | Set D Charm Ogerpon stretched to 60 (4 Ogerpon, 14 Fighting, 4 DCE, 4 Charm) | `demolish` |
| T60 | Set T Dragapult stretched to 60 (4 Dreepy / 3 Drakloak / 3 Dragapult, Rare Candy 4) | `phantom` |
| S60 | Set S Floragato hunter stretched to 60 | `slash` |

G's AI is the Staraptor carnival script, not a dedicated Ledian/Party hybrid, so C60 vs G overstates a tuned bird list.

## Head-to-head (C60 win rate)

| Foe | Overall | C60 first | C60 second |
| --- | ---: | ---: | ---: |
| Charm Ogerpon 60 (D60) | **72.5%** | 72.6% | 72.3% |
| Carpet Set G | **97.7%** | 97.5% | 97.9% |
| Dragapult 60 (T60) | **34.7%** | 37.6% | 31.9% |
| Floragato hunter 60 (S60) | **99.4%** | 99.4% | 99.4% |

`pokemon_as_energy_per_game` is 0 on s60 (Party attaches **cards** named Psychic Energy).

### Read

- **Vs Ogerpon:** 30-card Rule B C vs D sat near 50%. With real Energy + Switch + three Boss, Photon still outraces Demolish 140. Charm 260 is 2 prizes; empty Clefairy is 1. Overall **72.5%**.
- **Vs Dragapult:** Still the Standard problem, but CLC Metronome is a real chip. Same seed, Rebel Clash Clefable sat at **29.0%**; two CLC 014 (`[C]` Metronome) plus copying Dive even when it is not a KO reach **34.7%** (Dragapult **65.3%**). 800-game screen: Metronome copied Phantom Dive in **15.6%** of games. See [How C60 loses to Dragapult](#how-c60-loses-to-dragapult) and [CLC Metronome](#clc-metronome).
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

## CLC Metronome

Classic **CLC 014** Clefable: Colorless, 70 HP, Metronome costs **one Colorless**. Printed text is still *Choose 1 of your opponent's Active Pokémon's attacks and use it as this attack.* TWM 79 is the same text at `[C][C]` — too slow for a 1-attach surprise.

The 30-card Family Cup bakeoff did not lock Metronome: TWM/CLC share the **Clefable** name with Rebel Clash, so they cannot be a fifth copy. Here the two RCL Prankish copies **are** the two CLC prints (legal 2-of).

Party used to evolve Metronome only when the copy **KOs**. Phantom Dive 200 does not KO 320 HP Dragapult, so CLC never came down. The s60 script now copies Dive whenever Dragapult is Active (200 + 6 bench counters), then Photon takes the 120 leftover. It still refuses Budew (Itchy Pollen).

800-game same-seed screen vs the previous 2× RCL C60:

| Package | vs Dragapult | vs Ogerpon | vs G | vs Floragato |
| --- | ---: | ---: | ---: | ---: |
| 2× RCL Prankish | 29.9% | 70.9% | 98.0% | 99.6% |
| **2× CLC Metronome** | **34.6%** | 72.9% | 97.8% | 99.4% |

Locked 3,000-game table uses CLC. It is not an upset: Dragapult still wins ~2 of 3. It is the only household 60 that C60 loses, and Metronome is the only lever that moved that cell.

## What I would not do

- Do not keep 4/4/4 Clefable / ex / Mega. Copy-cap legal, but the deck becomes 18 Stage 1s and bricky under real Energy.
- Do not leave 0 Switch. Moon-Watching Party only fires from Active; the 30-card list leaned on Rule B chump sequences.
- Do not add TWM Metronome (`[C][C]`) instead of CLC. The surprise is the single attach.
- Do not evolve CLC onto Budew — Metronome then copies Itchy Pollen, not Dive.
- Do not treat this as a replacement for Family Cup Set C. Rule B Clefable-as-energy is a different game.
