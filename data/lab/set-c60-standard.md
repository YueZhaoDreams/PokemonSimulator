# Set C → Standard 60 (Pokémon are not energy)

Date: 2026-09-11
Seed: `20260911`
Engine: `family-tcg-monte-carlo`
Rule: **s60** — 60 cards, 4 of a name, 6 prizes, Pokémon are not Basic Energy
Games: 3,000 / cell (C60 is player A, random seat)
Script: `data/lab/set_c60_standard.py`
Raw: `data/lab/set-c60-standard.json`

Family Cup **Set C stays 30 cards** (`SET_C_NAMES`). That list has **no dedicated Energy** because Rule B treats the Clefable line as Psychic. This file is the constructed rewrite for real Standard 60.

## How the 30-card list changes

The 30-card identity is LOR 62 Moon-Watching Party → load Psychic onto benched Clefairy → Photon Kinesis on Mewtwo ex, with Clefable / Clefable ex / Mega as the wall. Under s60 that engine **needs Psychic Energy cards in the deck**. Party searches Energy, not Pokémon.

| 30-card Set C (Rule B) | Standard 60 rewrite |
| --- | --- |
| 4 Clefairy / 2 Mewtwo ex / 4 Clefable / 4 Clefable ex / 4 Mega | 4 Clefairy / **3** Mewtwo ex / **2** Clefable / **3** Clefable ex / **2** Mega |
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
| 2 | Clefable | Prankish bounce |
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

| Foe | Random | First | Second |
| --- | ---: | ---: | ---: |
| Charm Ogerpon 60 (D60) | **72.5%** | 75.5% | 69.4% |
| Carpet Set G | **97.8%** | 98.1% | 97.5% |
| Dragapult 60 (T60) | **29.0%** | 31.5% | 26.5% |
| Floragato hunter 60 (S60) | **99.4%** | 99.4% | 99.3% |

`pokemon_as_energy_per_game` is 0 on s60 (Party attaches **cards** named Psychic Energy).

### Read

- **Vs Ogerpon:** 30-card Rule B C vs D sat near 50%. With real Energy + Switch + three Boss, Photon still outraces Demolish 140. Charm 260 is 2 prizes; empty Clefairy is 1. Random **72.5%**.
- **Vs Dragapult:** This is the Standard problem. Phantom Dive 200 plus 6 bench counters farms 60 HP Clefairy and still KOs a damaged Mewtwo. C60 **29.0%** (Dragapult **71.0%**). The 30-card Family Cup pair was close (~46–52%); six prizes and a full candy line blow the race open.
- **Vs G / Floragato:** Carnival and slash do not assemble a 6-prize closer before Photon. Those cells are blowouts, not a claim that C60 is a tournament deck.

## What I would not do

- Do not keep 4/4/4 Clefable / ex / Mega. Copy-cap legal, but the deck becomes 18 Stage 1s and bricky under real Energy.
- Do not leave 0 Switch. Moon-Watching Party only fires from Active; the 30-card list leaned on Rule B chump sequences.
- Do not treat this as a replacement for Family Cup Set C. Rule B Clefable-as-energy is a different game.
