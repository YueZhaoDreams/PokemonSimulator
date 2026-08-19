# Clefairy / Mewtwo Baseline v1 — Family Cup

Date: 2026-08-19

This is the locked **28-card** Family Cup list vs Charm Ogerpon. Moon-Watching Party is LOR 62 (full-deck search, one Psychic Energy per benched Clefairy). **Maximum Belt is an ACE SPEC (one copy).** Tool Box tutors it from the top 7; Arven is the full-deck Tool + Item search.

Locked trainer package: **3 Hop / 2 Nest / 3 Energy Search / 1 Belt / 1 Tool Box / 1 Arven** — **54.1%** random (56.9% first, 50.8% second), 10k seed `20260818`. Earlier 4 Hop / no Tool Box sat at ~53.7% on the same seed.

Any later swap must beat this list in the same simulator before it replaces Baseline v1.

---

## Family Rule (Rule B)

- **28** cards
- Opening 7, 3 prizes (simulator defaults)
- **Every Pokémon card may be treated as a Basic Energy of its type** — in hand, deck, or discard, wherever the effect looks for that energy

Under this rule, Psychic Pokémon in the deck (Clefairy, both Clefable lines, Mega Clefable) are also **Basic Psychic Energy**. That is why Moon-Watching Party, Energy Search, and Transfer Charge all over-perform versus standard TCG.

---

## Locked 28 — vs Charm Ogerpon

| Qty | Card | HP | Type / stage | Role |
| --- | --- | --- | --- | --- |
| 4 | Clefairy — Lost Origin 62 | 60 | Basic / Psychic | Energy engine |
| 2 | Mewtwo ex — Paradox Rift 58 | 230 | Basic / Lightning | Closer / 230 HP tank |
| 4 | Clefable — Rebel Clash 75 | 110 | Stage 1 / Psychic | Prankish + Psychic fuel |
| 4 | Clefable ex — Obsidian Flames 82 | 260 | Stage 1 / Psychic | Lunar Zone |
| 3 | Mega Clefable ex | 320 | Stage 1 / Psychic | Wall / Plan B |
| 3 | Hop | — | Supporter | Draw 3 |
| 2 | Nest Ball | — | Item | Put Mewtwo on the bench |
| 3 | Energy Search | — | Item | Mewtwo / Psychic tutor |
| 1 | Maximum Belt | — | ACE SPEC Tool | +50 vs ex |
| 1 | Tool Box | — | Item | Top-7 Tool tutor |
| 1 | Arven | — | Supporter | 1 Tool + 1 Item |
| **28** | | | | |

Original v1 was 3 Poffin / 2 Switch / 3 Energy Search / Belt / Beach / Arven. After LOR 62 Party the 4 Hop list cleared 50%. **2026-08-19:** −1 Hop +1 Tool Box (ACE SPEC Belt stays at one copy).

Mewtwo is recorded here as **Lightning**, so it is **not** Psychic Energy under Rule B. Energy Search can still find it as Lightning Energy. Do not attach Mewtwo as fuel.

---

## vs Charm Ogerpon (hardest even matchup)

Documented claim (before this engine check):

| Going first | Going second | Random seat |
| --- | --- | --- |
| 68% | 74% | **71%** |

This is the matchup the list was optimized against. See [Matchups](#matchups) for why it is a race, and why Jungle Mr. Mime is a rules-level lock instead.

### Set D — Charm Cornerstone Ogerpon (28)

| Qty | Card | Role |
| ---: | --- | --- |
| 4 | Cornerstone Mask Ogerpon ex | Attacker / wall, 210 HP, Demolish 140 |
| 6 | Fighting Energy | `[F]` |
| 4 | Double Colorless Energy | One card pays `[CC]`; with Fighting that is `[FCC]` |
| 4 | Energy Search | Energy tutor (Rule B can also fetch Pokémon) |
| 4 | Nest Ball | Bench Ogerpon |
| 2 | Bravery Charm | Ogerpon 210 → **260 HP** |
| 2 | Acerola | Pick up a damaged Ogerpon and clear damage |
| 2 | Switch | Get Ogerpon Active |
| **28** | | |

Line: T1 Ogerpon + Fighting → T2 DCE → Demolish 140. Charm makes the body 260. Acerola punishes any hit that does not KO.

### Simulator check — 2026-08-19

Seed `20260818`, 10,000 games, strategies `party` vs `demolish`, engine `family-tcg-monte-carlo`. Set C is player A.

| Seat | Documented | Original (3 Poffin / 2 Switch) | Prior (4 Hop) | Locked (3 Hop + Tool Box) |
| --- | ---: | ---: | ---: | ---: |
| Clefairy first | 68% | 29.2% | 56.9% | **56.9%** |
| Clefairy second | 74% | 27.0% | 50.4% | **50.8%** |
| Random | 71% | 28.1% | 53.7% | **54.1%** |

ACE SPEC Belt stays at one. Details: `data/lab/clefairy-ogerpon-sim.md`.

---

## Card roles

### 1. Clefairy LOR ×4 — the engine

- HP 60, Psychic, Basic
- Ability **Moon-Watching Party** (LOR 62): once per turn, if Active, **for each benched Clefairy, search the deck for 1 Psychic Energy and attach it to that Clefairy**, then shuffle. There is no top-6 look.

Under Rule B the following are all Basic Psychic Energy when Party hits them:

- RCL Clefable ×4
- Clefable ex ×4
- Mega Clefable ex ×3
- leftover Clefairy still in the deck

Each extra benched Clefairy is one more full-deck energy tutor. Vs Ogerpon the engine caps at **3 Clefairy** (Active + 2 benched = 2 energy per Party) so a 4th 60 HP body does not feed prizes or block Mega.

Classic burst with three Clefairy (2 energy per Party):

1. A Active → Party onto B and C (2)
2. Switch → B Active → Party onto A and C (2)
3. Switch → C Active → Party onto A and B (2)

### 2. Mewtwo ex PAR ×2 — the closer

- HP 230, Lightning, Basic
- Not Psychic, so it cannot be attached as Psychic Energy

**Transfer Charge** — `[P]`  
Attach up to 2 Basic Psychic Energy from discard to your Psychic Pokémon.

Rule B combo (retreat cost is not actually lost):

1. Clefairy has 2 Energy
2. Pay 2 to retreat → those two Psychic Pokémon-Energy go to discard
3. Mewtwo Active
4. Hand-attach `[P]`
5. Transfer Charge returns both discarded cards

**Photon Kinesis** — `[P][P]`  
10 damage, then **+30 per Psychic Energy in play**.

| Psychic Energy in play | Damage |
| --- | --- |
| 5 | 160 |
| 6 | 190 |
| 7 | 220 |
| 8 | 250 |
| **9** | **280** |
| 10 | 310 |
| 11 | 340 |

The Charm Ogerpon line is **9 Psychic = 280**. That OHKOs 260 HP Ogerpon and skips Acerola.

### 3. RCL Clefable ×4 — the clock

- Clefable — Rebel Clash 75, HP 110, Psychic, Stage 1
- Ability **Prankish**: when you play this from hand to evolve, you may put 1 Energy from the opponent’s Active onto the top of their deck

This card does not exist for damage. It **buys one attachment tempo**.

Example vs Ogerpon:

- Their T1: attach F
- You evolve Clefairy → RCL Clefable, Prankish puts F on top
- They draw F back and re-attach, but they cannot also attach DCE that turn
- **Demolish is delayed one turn**

**When not to evolve.** If that Clefairy can still Party, do not Prankish on autopilot. RCL spends **one Party engine** to buy **one turn**. Press the button only when that turn lets Mewtwo go 7 → 9 Psychic, or finishes Mega / Mewtwo setup. Otherwise the card is just Psychic Energy — which is why it is so good under Rule B.

### 4. Clefable ex OBF ×4 — the lubricant

- HP 260, Psychic, Stage 1 / Pokémon ex
- Ability **Lunar Zone**: your Pokémon that have Psychic Energy attached have **Retreat Cost 0**

Without it, Clefairy rotation is Switch → Switch → Switch. With it, any Pokémon holding Psychic Energy retreats for free.

The Mega / Mewtwo line:

1. Mega eats damage
2. Lunar Zone
3. Free retreat
4. Mewtwo Active
5. Photon Kinesis 280

You do not need to discard Energy, Energy Switch, Switch, or Switch Cart.

260 HP also eats one Ogerpon 140 (260 → 120) and can wall for a turn.

### 5. Mega Clefable ex ×3 — two attack turns of HP

- HP 320

Vs Cornerstone Ogerpon, Demolish is 140:

| Hit | Mega HP |
| --- | --- |
| 0 | 320 |
| 1 | 180 |
| 2 | 40 |
| 3 | KO |

Mega is not “320 HP.” It is **two full construction turns** for the back-row Mewtwo / Clefairy. That is the going-second problem this list solved.

Typical line:

- Board: Mega Active; bench Clefairy / Clefairy / Mewtwo
- Ogerpon Demolish 140 → Mega 320 → 180
- Your turn: Party, Party, hand attach / search, keep building Mewtwo
- Ogerpon 140 again → Mega 180 → 40
- Your turn: if 9 Psychic + Mewtwo is payable, Lunar Zone free-retreats Mega, Mewtwo Photon Kinesis 280, Ogerpon KO

### 6. Nest Ball ×1 / Hop ×3 — find Mewtwo, see the deck

Poffin benches up to 2 Basics with 70 HP or less — in this 28, that is only Clefairy. That **increases** Party (one full-deck search per benched Clefairy). Nest Ball is still the Mewtwo fetch (Poffin cannot; Mewtwo is 230 HP). Earlier “cut Poffin for Hop” results assumed the fake top-6 Party.

Do not Hop when the deck is already thin (≤8); that is how this 28 decks out in ~9% of games.

### 7. Energy Search ×3 — Rule B tutor

Printed text: search the deck for 1 Basic Energy.

Under Rule B, Pokémon in the deck count as that type’s Basic Energy, so this is a **no-discard Pokémon/Energy search**:

| Need | Search as |
| --- | --- |
| Clefairy | Psychic Energy |
| RCL Clefable | Psychic Energy |
| Clefable ex | Psychic Energy |
| Mega Clefable | Psychic Energy |
| Mewtwo | Lightning Energy |

No Ultra Ball discard-2. That is why Ultra Ball left the list.

### 8. Switch ×1

Not just a swap. Each Switch is another Moon-Watching Party. v2 keeps **one** copy; a second Switch consistently lost to a third Hop in the simulator (opening congestion). Beach Court + Lunar Zone cover extra movement.

### 9. Maximum Belt ×1 / Beach Court ×1 / Arven ×1

- **Maximum Belt**: +50 attack (helps the closer vs ex)
- **Beach Court**: Retreat −1 before Lunar Zone is up
- **Arven**: 1 Tool + 1 Item (Belt, Switch, Poffin, Energy Search)

---

## Three phases

### Phase 1 — Burst energy

Do not attack yet. Goal board: **4 Clefairy + Mewtwo**. Move Psychic Energy from deck to field with Party (1 per benched Clefairy), Energy Search, and Switch.

### Phase 2 — Buy time (evolution toolbox)

Pick the Stage 1 that the board needs. There is no fixed evolution line.

| Situation | Evolve to | Why |
| --- | --- | --- |
| Opponent has not finished attack Energy | RCL Clefable | Prankish breaks their attach tempo |
| Need free rotation | Clefable ex | Lunar Zone |
| Mewtwo needs 1–2 more turns | Mega Clefable ex | 320 HP eats two 140s |

### Phase 3 — Mewtwo harvest

- Mewtwo payable
- 9 Psychic in play
- Photon Kinesis = **280** → Charm Ogerpon 260 OHKO

10 Psychic = 310, 11 = 340. Damage keeps scaling if the game goes long.

---

## Decision order vs Ogerpon

1. **Can Mewtwo 280 kill now?** Do it.
2. Else: **one turn short and Prankish actually delays Ogerpon?** RCL.
3. Else: **one or two turns short and Mega can evolve?** Mega walls.
4. In parallel: **Clefable ex if you can** — establish Lunar Zone.
5. Then: Mega walls → free retreat → Mewtwo 280.

Roles in that loop:

| Piece | Job |
| --- | --- |
| Clefairy | Create resources |
| RCL Clefable | Create time |
| Mega | Buy time with HP |
| Clefable ex | Delete movement cost |
| Mewtwo | Convert everything into 280+ once |

---

## Matchups

### Cornerstone Mask Ogerpon ex — strength counter (documented ~71%; simulator ~29%)

- HP 210; **260** with Bravery Charm
- Basic Pokémon ex (no evolution needed)
- Ability **Cornerstone Stance**: prevent attack damage from Pokémon that have an Ability
- Attack **Demolish** `[F][C][C]`: 140 damage; attack damage is not affected by effects on the opponent’s Pokémon

Why it races this deck: Basic → F + DCE reaches 140 fast; 260 HP survives ordinary hits.

Why this list still has a line: **Mewtwo ex has no Ability**, so Stance does not stop Photon Kinesis. 9 Psychic → 280 OHKOs Charm Ogerpon.

Race:

- Ogerpon: land 140 as soon as possible, keep swinging
- Clefairy: burst energy → Mega wall / Clefable ex free retreat → Mewtwo 280

### Jungle Mr. Mime — rules counter (hard lock)

Jungle Mr. Mime 6/64 / 22/64:

- HP 40, Basic
- Psychic Weakness ×2
- Pokémon Power **Invisible Wall**: if an attack would do **30 or more** after Weakness / Resistance, prevent all of that attack’s damage

Clefairy **Wonder Storm** is 20 × Psychic Energy in play. Minimum useful hit is 20. After Psychic Weakness: 40. Invisible Wall sees ≥30 and prevents **all** of it.

| Psychic Energy | Wonder Storm | After Weakness | Final |
| --- | --- | --- | --- |
| 1 | 20 | 40 | 0 |
| 2 | 40 | 80 | 0 |
| 3 | 60 | 120 | 0 |
| 5 | 100 | 200 | 0 |
| 9 | 180 | 360 | 0 |

Mewtwo is the same trap. Photon Kinesis is already 40+ as soon as the attack is payable (and 280 at 9 Psychic). ≥30 → Invisible Wall → 0.

Mega’s 320 HP still cannot punch through: any real attack is 30+ after math, then 0.

More energy makes the lock **stricter**, not weaker.

### Two kinds of counter

| Opponent | Kind | What it contests | This list’s answer |
| --- | --- | --- | --- |
| Cornerstone Ogerpon ex | Strength | HP, speed, stable 140 | Mega wall → Mewtwo 280 (Mewtwo has no Ability) |
| Jungle Mr. Mime | Rules | Invisible Wall + Psychic Weakness | None on the main attack lines. 40 HP is a dedicated anti-Clefairy card |

Mr. Mime is a **meta card**: excellent vs this engine, often weak vs decks that do not need a 30+ Psychic hit.

---

## Current meta shape (Rule B)

1. Clefairy Rule-B engine beats a large set of ordinary lists
2. Jungle Mr. Mime hard-counters that engine
3. Lists that do not rely on high Psychic damage then beat 40 HP Mr. Mime

---

## Baseline policy

**Do not change this 28 without a same-simulator proof that the new list is stronger.**

Frozen counts **v3**: **4 / 2 / 4 / 4 / 3** Pokémon, plus **2 Nest Ball / 1 Belt / 1 Tool Box / 3 Energy Search / 3 Hop / 1 Arven**.
