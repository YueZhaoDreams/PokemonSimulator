# C60 Dimension Valley vs Battle Cage Bakeoff

Date: 2026-09-20
Seed: `20260911`
Rule: **s60** (60 cards, 4-of, 6 prizes, Pokémon are not Basic Energy)
Games: 3,000 / cell (C60 is always player A; who goes first is random)
Script: `data/lab/set_c60_dimension_valley.py`
Raw: `data/lab/set-c60-dimension-valley.json`

## Hypothesis & Rationale

**Hypothesis**: Can Dimension Valley (PHF 93) replace Battle Cage (ME02 85) in C60 (1, 2, or 3 copies) to accelerate attacks by 1 turn under the idea that "Clefairy needs 3 energy to attack after opening with Moon-Watching Party"?

### Mechanics & Text Clarifications

1. **Moon-Watching Party is an Ability, not an attack**:
   - Clefairy (LOR 62) text: *"Once during your turn, if this Pokémon is in the Active Spot, for each of your Benched Clefairy, you may search your deck for a Psychic Energy card and attach it to that Clefairy. Then, shuffle your deck."*
   - Abilities require **0 energy**. Clefairy opens Party on Turn 1 (going second) or Turn 2 (going first) completely free.
2. **What costs 3 energy is Clefairy's attack Wonder Storm**:
   - `Wonder Storm`: `[C][C][C]` for `20× Psychic Energy attached to all Pokémon`.
   - Dimension Valley text: *"The attacks of each Psychic Pokémon in play (both yours and your opponent's) cost [C] less."*
   - Under Dimension Valley, Wonder Storm costs `[C][C]` (2 energy instead of 3).
3. **Dimension Valley does NOT benefit C60's actual attackers**:
   - **Mewtwo ex (sv04-058)**: Tera **Lightning** type (not Psychic), and Photon Kinesis costs `[P][P]` (no `[C]`). **0 benefit**.
   - **Clefable ex (sv03-082)**: Wondrous Moon costs `[P][P][P]` (no `[C]`). **0 benefit**.
   - **Mega Clefable ex (me03-031)**: Shooting Moons costs `[P][P]` (no `[C]`). **0 benefit**.
   - Only 60 HP Clefairy (`[C][C][C]` → `[C][C]`) and 110 HP Clefable (`[P][C]` → `[P]`) have `[C]` in their attack costs.
4. **Why attacking with 60 HP Clefairy fails**:
   - Mewtwo ex has **230 HP** and deals `10 + 30× Energy` for 2 attachments.
   - Clefairy has only **60 HP** and deals `20× Energy` for 2 attachments under Valley.
   - Forcing Clefairy to attack turns it into a 60 HP prize gift. Empirical test: forcing Clefairy Wonder Storm under Dimension Valley drops win rates vs T60 from 52.8% to **25.8%**, and vs D60 Ogerpon from 74.6% to **8.0%**.
5. **The Battle Cage Factor (Stadium conflict & bench snipe)**:
   - Battle Cage protects both benches from damage counter placement.
   - Dragapult ex's Phantom Dive places 6 damage counters (60 damage) on the bench every turn, exactly enough to OHKO benched 60 HP Clefairies.
   - Stadium cards are mutually exclusive. Playing Dimension Valley immediately bumps your own Battle Cage, exposing the bench to Dragapult.

---

## 3,000 Games / Cell Matrix

| Variant | T60 Dragapult | Hedrick Worlds | UNL Pidgeot | D60 Ogerpon | Set G Carpet | S60 Floragato |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **3 Battle Cage / 0 DV (Locked)** | **69.1%** | **65.4%** | **89.5%** | **76.1%** | **88.1%** | **99.7%** |
| 2 Battle Cage / 1 DV | 61.2% | 60.9% | 86.9% | 76.7% | 88.5% | 99.6% |
| 1 Battle Cage / 2 DV | 55.5% | 58.2% | 85.0% | 76.9% | 87.6% | 99.6% |
| 0 Battle Cage / 3 DV | 52.6% | 58.4% | 82.1% | 76.2% | 87.5% | 99.6% |

### First vs Second Split vs Dragapults

| Variant | T60 (Going 1st) | T60 (Going 2nd) | Hedrick (1st) | Hedrick (2nd) |
| :--- | :---: | :---: | :---: | :---: |
| **3 Battle Cage / 0 DV** | **69.0%** | **69.2%** | **65.6%** | **65.1%** |
| 2 Battle Cage / 1 DV | 62.3% | 60.2% | 61.0% | 60.8% |
| 1 Battle Cage / 2 DV | 57.4% | 53.5% | 60.3% | 56.1% |
| 0 Battle Cage / 3 DV | 57.7% | 47.7% | 60.0% | 56.9% |

---

## Findings & Conclusion

1. **Severe Dragapult Matchup Regression**:
   - Cutting 1 Battle Cage for 1 Dimension Valley drops T60 win rate from **69.1% to 61.2%** (-7.9%).
   - Cutting all 3 Battle Cages drops T60 win rate to **52.6%** (-16.5%), and going second collapses to **47.7%** (-21.5%).
   - Worlds Hedrick Dragapult drops from **65.4% to 58.4%** (-7.0%).
   - UNL Dragapult drops from **89.5% to 82.1%** (-7.4%).
2. **Zero Gain in Non-Dragapult Matchups**:
   - Against D60 Cornerstone Ogerpon, Set G, and S60 Floragato, win rates are essentially flat (+0.1% to +0.8%, within statistical margin of error) because Dimension Valley does not discount Mewtwo ex, Clefable ex, or Mega Clefable ex.
3. **Recommendation**:
   - **Do NOT replace Battle Cage with Dimension Valley in C60.**
   - Keep C60 locked with **3 Battle Cage**.
