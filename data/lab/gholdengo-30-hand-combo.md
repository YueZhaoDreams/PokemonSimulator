# Ambipom PAR Hand Fling — 60-card Unlimited (G30 lab)

Date: 2026-09-15
Status: engine plays Ambipom PAR 146 Hand Fling with Lopunny FLF Big Jump, Raikou V Fleet-Footed + Forest Seal Stone Star Alchemy, Draw Energy, and Rare Candy. Win-rate array vs household 60s is in `data/lab/gholdengo-30-array.json`.

**This lab is Unlimited constructed. Not Standard. Not Expanded. Not Family Cup 30.**

Printed sentences on the cards win. This file is not an engine effect list.

---

## Format of record (do not mix)

| | |
|---|---|
| Card pool | **Unlimited** — any US-released expansion or promo. Latest printing’s wording. **No ban list.** |
| Deck | **Exactly 60 cards** |
| Copies | At most **4** of a name, except basic Energy (no cap). ACE SPEC still says 1 per deck. |
| Prizes | **6** |
| Turn 1 | First player skips draw and cannot attack. Going second may attack. |
| Combo Cub | Rules skeleton = preset **`s60`** (60 / 6 prizes / 4-of). Card pool = Unlimited list, not a rotated Standard 60. Family Cup 30-card presets **cannot** hold 30 cards in hand. |

Puzzle of Time, Scoop Up Net, Forest of Giant Plants, Broken Time-Space, Lysandre’s Trump Card, Shaymin-EX, Sableye DEX, Oranguru UPR, Archeops, and Crazy Code are all **legal here**. They are banned or rotated in Expanded/Standard; that does not apply to this pile.

---

## 中文结论

研究目标从一开始就是：**60 张牌组 + Unlimited 卡池 + 6 奖**。Standard / Expanded 的轮换和禁卡表只用来对照「离开 Unlimited 会丢掉哪些循环」，不是这副牌的规则。

主循环改成 **Lopunny FLF 85 Big Jump**：印刷 `Once during your turn (before your attack), you may return this Pokémon and all cards attached to it to your hand.` Jumpluff DRX 3 Leave It to the Wind 是同一句，但是 Stage 2（Hoppip→Skiploom→Jumpluff），这副 60 用 Stage 1 Lopunny。附着卡回**手牌**，不是洗回牌库（Abra Teleporter / Dudunsparce RAD），也不是进弃牌再 Puzzle（Scoop Up Net）。Crazy Code 贴 Enriching（+3）→ Big Jump 把 Buneary+Lopunny+Enriching 回手（+3）→ 重放 Buneary −1 → BTS 进化 −1，净 **+4** / 圈。Draw Energy CEC 209 贴上摸 1，净 0，Crazy Code 可以连贴，给 Ambipom 付无色。12 张手牌 = 240，够打家庭组常见 2 奖（Mewtwo 230 / Ogerpon 210 / Wo-Chien）；Dragapult 320 要 16 张。还是一回合一次攻击，6 奖至少 3 枪。

**电系位换成 Raikou V（BRS 48）**，不再用 Pikachu / Tynamo。Fleet-Footed：在场上前位时摸 1。Forest Seal Stone 贴在 V 上开 Star Alchemy，**从牌组找任意一张**（Rare Candy / Porygon-Z / Lopunny / Draw Energy），一局一次 VSTAR。Speed Lightning Energy 只有贴到雷宝可梦才抽 2，贴 Raikou V 才算。这版 Raikou / Seal / Nest 各留 1：Star Alchemy 一局一次，第二只 V 是 2 奖诱饵。

**砍掉 Sableye / Remoraid / Octillery / Porygon2 / Pikachu。** Rare Candy 比 Porygon2：跳过 Stage 1 直接 Porygon → Porygon-Z。印刷写明不能第一回合、不能对这回合放下的 Basic 用，Broken Time-Space **不能**覆盖这句。

同回合再进化 Stage 1（Aipom / Buneary）用 **Broken Time-Space**。Abra Teleporter 仍把 Energy 洗进牌库，不要当这副的宿主。

**Ambipom 不抗揍，走 2 换 1。** 100 HP 挡不住 Photon / Dive，但只给 1 奖。家庭组 closer 是 2 奖，Hand Fling 先 KO 再死 = 净 +1 奖。所以把线加厚成 **4 Aipom / 4 Ambipom**：大接手更容易抽出第二只，Wally / Ultra Ball 在场上已有一只 Ambipom 时仍会找备用。不换 Mew 墙，也不占 Enriching 的 ACE SPEC 位。

家庭组 3000 盘数组（seed 20260911）上一版 **2 Raikou V + 2 Forest Seal + 3/2 Aipom/Ambipom**：胜率 **3.5 / 5.2 / 6.1 / 20.5 / 5.5 / 28.0 / 26.5%** vs c60/t60/hedrick/unl/d60/s60/g。再上一版 Pikachu / Octillery / Sableye 是 **2.8 / 3.6 / 2.7 / 19.0 / 2.3 / 6.7 / 6.4%**。s60 / g 明显起来（Hand Fling 37.8% / 38.4%），c60 Photon 和 t60 Dive 还是先打掉 100 HP Ambipom。4/4 Ambipom 线的新数组见下面 Win-rate array。

---

## Three Celebrations (6 prizes)

Celebration takes **2** prizes and then shuffles **the hand** into the deck. It does not win the game. Board, attached cards, and the discard pile stay.

| | |
|---|---|
| Prizes to win | 6 |
| Per Celebration | 2 |
| Attacks required | **3** (2+2+2). One attack per turn, so **3 of our attack turns** |
| Going second | Earliest calendar: our T1, T2, T3 if every attack is a Celebration |
| Going first | T1 cannot attack. Earliest: T2, T3, T4 (**4 of our turns**) |
| If Junk Hunt is needed between shots | Extra non-Celebration turns. 3 shots + 2 rebuilds = 5 of our turns |

After each successful Celebration the next turn starts at **hand = 1** (the draw). The +2 loop only restarts if Enriching Energy, Scoop Up Net, and two Puzzle of Time are reachable from **play + discard**, not from the vanished hand.

**End the loop like this, or the second shot dies:**

1. Leave Enriching Energy **attached** to Bench Abra (last action is attach, not Net). It is not in the 30-card hand, so Celebration does not shuffle it away.
2. Leave Metal attached to Mew / Gholdengo. Same reason.
3. Leave Porygon-Z and Octillery in play. Abyssal Hand is how turn 2 and turn 3 start.
4. Prefer Puzzle of Time / Scoop Up Net in the **discard** (play the last Puzzle pair retrieving other cards, not the last two Puzzles). Cards in hand get shuffled; cards in discard do not.
5. Do not Research / Iono / N yourself on a 30-hand.

**Turn after Celebration:**

1. Draw 1. Octillery **Abyssal Hand** → 5.
2. Need two Puzzle of Time in hand. They are Items in discard.
   - **Junk Arm** TM 87: discard **2**, put a Trainer (Item) from discard into hand. Cannot retrieve Junk Arm. From Octillery’s 5 this usually buys **one** Puzzle, not two.
   - **Sableye Junk Hunt** `[D]`: put **2** Items from discard into hand. Reliable, but **spends the attack**, so that turn is not a Celebration.
3. Scoop Up Net the Abra that still holds Enriching → Energy to discard, Abra to hand.
4. Replay Abra. Crazy Code attach. +2 loop back to 30. Celebration again.

Junk Hunt is the reliable retrieve and the reason the calendar is **3–4+ of our turns**, not 3 guaranteed Celebrations. Junk Arm tries to retrieve without spending the attack, so a going-second T1/T2/T3 triple Celebration stays possible if the 5-card Octillery hand contains Junk Arm / Net.

**On a Junk Hunt turn, do not pass with 30 in hand.** You already spent the attack. Loop only far enough to re-park Enriching on Bench Abra and Puzzle / Net in discard, then end small. Passing 30 invites N / Iono / Judge; the next turn would start at the wrong count.

Opponent gets a full turn after shot 1 and shot 2. Gust Porygon-Z or Octillery, or N / Judge, can stop the rebuild. N after our hand is already empty can accidentally refill us (draw equal to remaining prizes).

---

## The 60 (Unlimited constructed, Hand Fling)

Printings are the text this lab uses. Aipom is Paradox Rift 145 (Filch / Smack), not Lost Origin, so it evolves into Ambipom PAR 146. Raikou V is Brilliant Stars 48 (Fleet-Footed). Draw Energy is Cosmic Eclipse 209.

| Qty | Card | Set | Why |
|---:|---|---|---|
| 3 | Buneary | FLF 84 | 60 HP → Poffin. Big Jump stack. |
| 2 | Lopunny | FLF 85 | **Big Jump**: this Pokémon + attachments to **hand**. Sitdown Bounce is not the closer. |
| 3 | Porygon | UNB 154 | 50 HP → Poffin. Rare Candy into Porygon-Z. |
| 2 | Porygon-Z | UNB 157 | Crazy Code. |
| 4 | Aipom | PAR 145 | BTS into Ambipom. 60 HP → Poffin. Filch draws 1. Spare Basic after the first closer dies. |
| 4 | Ambipom | PAR 146 | **Hand Fling** 20×hand, `[C][C][C]`. Collect draws 2. No Ability (Stance does not block). 100 HP, **1 prize**. Second copy is the 2-for-1 race. |
| 1 | Raikou V | BRS 48 | Lightning host for Speed L draw 2. **Fleet-Footed** draws 1 if Active. Pokémon V for Forest Seal Stone. 200 HP, 2 prizes — do not open on it. Star Alchemy is once per game. |
| 4 | Puzzle of Time | BKP 109 | Discard retrieve backup. |
| 2 | Scoop Up Net | RCL 165 | Backup if Big Jump is not in play. Cannot Net Raikou V. Do **not** Net Ambipom / Lopunny. |
| 3 | Broken Time-Space | PL 104 | Same-turn Stage 1 evo. Does **not** override Rare Candy. |
| 1 | Nest Ball | any | Raikou V is 200 HP — Poffin cannot fetch it. One copy: only one V left. |
| 3 | Buddy-Buddy Poffin | TEF 144 | Buneary / Porygon / Aipom. |
| 3 | Ultra Ball | any | |
| 3 | VS Seeker | PHF 109 | |
| 2 | Wally | ROS 94 | Buneary→Lopunny, Aipom→Ambipom. Cannot skip to Porygon-Z. |
| 1 | Professor's Research | any | Setup only. |
| 1 | Battle Compressor | FCO / UNB | |
| 1 | Switch | any | Into Ambipom when Hand Fling is still lethal after −1 card. |
| 4 | Rare Candy | PAF 89 | Skip Porygon → Porygon-Z. Not first turn; not a Basic played this turn. |
| 1 | Forest Seal Stone | SIT 156 | Tool on Raikou V. **Star Alchemy**: search any one card, one VSTAR Power per game. |
| 1 | Enriching Energy | SSP 191 | ACE SPEC. Loop on Lopunny (Big Jump). |
| 4 | Speed Lightning Energy | RCL 173 | Draw 2 only on Lightning. Extra copies stay on Raikou V; reserve 3 Colorless for Ambipom. |
| 3 | Lightning Energy | any | Pays Colorless on Ambipom. Once-per-turn attach. |
| 4 | Draw Energy | CEC 209 | Colorless; attach from hand, draw 1. Net 0. Crazy Code can spam it. |

**19 Pokémon + 29 Trainers + 12 Energy = 60.**

Cut Sableye, Remoraid, Octillery, Pikachu, Porygon2, Junk Arm, Darkness. Jumpluff DRX 3 is the same bounce sentence but Stage 2 — not in this 60. Cut the second Raikou V / Forest Seal / Nest for two extra Ambipom and one extra Aipom.

Goldfish (board already up, going second): Rare Candy Porygon into Z, BTS into Ambipom + Lopunny, Nest Raikou V. Forest Seal Stone on Raikou → Star Alchemy. Crazy Code Speed L onto Raikou (draw 2), Enriching onto Lopunny (draw 4), Draw Energy onto Ambipom / bounce host. Big Jump returns Buneary + Lopunny + Enriching. Replay Buneary, BTS evolve, attach again. Fleet-Footed if Raikou is Active on a setup turn. After the first Ambipom is in play, Nest / Wally / Ultra Ball still fetch a spare Aipom → Ambipom. Hand Fling when `20 × (hand − pay − Switch)` KOs.

---

## The previous 60 (Gholdengo Celebration)

Recorded for comparison. This closer needed exactly 30 cards and shuffled the hand; the household array below is **not** this list.

| Qty | Card | Set | Why |
|---:|---|---|---|
| 3 | Abra | TWM 80 | Enriching host. 40 HP → Poffin. |
| 3 | Porygon | UNB 154 | 50 HP → Poffin. |
| 2 | Porygon2 | UNB 156 | BTS into Porygon-Z. |
| 2 | Porygon-Z | UNB 157 | Crazy Code. Must survive all three shots. |
| 2 | Remoraid | BKT 32 | 60 HP → Poffin. |
| 2 | Octillery | BKT 33 | **Abyssal Hand**: every post-Celebration turn, 1 card → 5. Bench, stays in play. One copy is enough; two for prizes / KO. |
| 2 | Sableye | DEX 62 | 70 HP → Poffin. **Junk Hunt** `[D]`: 2 Items from discard to hand. Rebuild turn when Junk Arm misses. |
| 3 | Gimmighoul | 30th Celebration 81 | BTS into Gholdengo. |
| 2 | Gholdengo | 30th Celebration 108 | Celebration. Two copies because the attacker must live three turns. |
| 1 | Mew ex | 30th Celebration 66 | Active copy of Celebration. 0 retreat. Metal stays attached between shots. |
| 4 | Puzzle of Time | BKP 109 | Loop recycle. Park in discard before Celebration. |
| 4 | Scoop Up Net | RCL 165 | Park in discard before Celebration. |
| 4 | Junk Arm | TM 87 | Discard 2, one Item from discard (not Junk Arm). Helps a Celebration restart if the Octillery 5 already has fuel. |
| 3 | Broken Time-Space | PL 104 | Same-turn evo. After the board is built, keep it or lose re-evolve if something is KO’d. |
| 3 | Nest Ball | any | |
| 3 | Buddy-Buddy Poffin | TEF 144 | Abra, Porygon, Gimmighoul, Remoraid, Sableye all ≤70. |
| 3 | Ultra Ball | any | |
| 4 | VS Seeker | PHF 109 | |
| 2 | Wally | ROS 94 | |
| 1 | Professor's Research | any | Setup only. |
| 1 | Battle Compressor | FCO / UNB | Mill Puzzle into discard. |
| 1 | Switch | any | Sableye Active for Junk Hunt ↔ Mew Active for Celebration. |
| 1 | Enriching Energy | SSP 191 | ACE SPEC. Leave **attached** through Celebration. |
| 3 | Basic Metal Energy | any | Attach to Mew / Gholdengo on the first combo turn; leave it there. |
| 1 | Basic Darkness Energy | any | Junk Hunt cost on a Sableye turn. |

**22 Pokémon + 33 Trainers + 5 Energy = 60.**

This is **not** the one-shot 60 from the previous pass. The rebuild package is 2 Remoraid, 2 Octillery, 2 Sableye, 4 Junk Arm (+10). Paid for by −1 Abra, −1 Porygon, −1 Gimmighoul, −1 Gholdengo, −1 Broken Time-Space, −1 Nest, −1 Poffin, −1 Ultra Ball, −1 Research, −1 Battle Compressor (−10). Metal 4→3; +1 Darkness for Junk Hunt. Net Pokémon 20→22, Trainers 35→33, Energy 5.

| | One-shot 60 (previous commit) | Three-shot 60 (this list) |
|---|---|---|
| Win condition | First 30-hand Celebration | **Three** Celebrations (or 2 + one KO — still 3 attacks) |
| After Celebration | Lab stopped | Engine still on board + discard |
| Persistent draw | None | Octillery Abyssal Hand → 5 |
| Puzzle / Net retrieve | None | Junk Arm (Item turn) and/or Sableye Junk Hunt (attack turn) |
| Stadium | 4 Broken Time-Space | 3 Broken Time-Space |
| Combo Cub stop | First Celebration | Third Celebration / 6 prizes taken |

Not in this 60: Forest of Vitality, Speed L Energy, Dudunsparce, Shaymin-EX (Set Up caps at 6; GX so Net cannot bounce it), Dedenne-GX (discards the 30-hand), Iono / N as our own closer.

**Ambipom backup (swap 4):** −1 Gholdengo, −1 Porygon2, −1 Nest, −1 Poffin, +2 Aipom PAR, +2 Ambipom PAR 146. Does **not** reduce the number of attacks: 600 damage is still one attack. At best 2 Celebrations (4 prizes) + one Ambipom KO of a 2-prize Pokémon (2) = still **3 attacks**.

Goldfish (going second, board already up):

1. BTS, build Porygon-Z, Gholdengo, Octillery, Abra. Mew Active. Metal on Mew.
2. Loop to 30. **Stop with Enriching on Abra and Puzzle/Net in discard.** Celebration. 6→4 prizes. Hand gone.
3. Opponent’s turn.
4. Draw 1. Octillery to 5. If that 5 can Junk Arm a Net and still assemble two Puzzle, scoop Abra and Celebration the same turn (4→2 prizes). If not, Switch Sableye Active, Junk Hunt 2 Puzzle, **skip Celebration**.
5. Opponent’s turn.
6. Repeat until three Celebrations. 2→0 prizes.

Honest calendar: **3 Celebration attacks** is the prize floor. **3 of our turns** only if every post-reset hand restarts without Junk Hunt. **4 of our turns** if we go first, or if one rebuild spends Sableye. **5** if both rebuilds need Junk Hunt.

---

## Win-rate array

G30 (`celebration` strategy, Ambipom PAR Hand Fling + Lopunny FLF Big Jump + 4/4 Aipom/Ambipom + 1 Raikou V) as player A vs the household 60s. Not a full NxN remake of `set-c60-unl-matrix`. Rules preset `s60` (60 / 6 prizes / 4-of). First player random. **3,000 games / cell, seed 20260911**. Elapsed **81.7s** on the previous 2 Raikou / 3+2 Aipom list; 4/4 rerun pending in `gholdengo-30-array.json`.

Script: `data/lab/gholdengo-30-array.py`. Numbers: `data/lab/gholdengo-30-array.json`.

| A \\ B | c60 | t60 | hedrick | unl | d60 | s60 | g |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| g30 win | 3.5% | 5.2% | 6.1% | 20.5% | 5.5% | 28.0% | 26.5% |
| first | 3.5% | 4.5% | 5.9% | 19.3% | 5.0% | 28.3% | 24.4% |
| second | 3.5% | 5.9% | 6.3% | 21.6% | 6.1% | 27.6% | 28.6% |
| Crazy Code | 45.4% | 22.5% | 32.1% | 34.8% | 23.4% | 60.8% | 58.1% |
| Puzzle pair | 6.5% | 3.4% | 6.4% | 6.4% | 3.9% | 8.0% | 7.0% |
| Speed L draw | 31.9% | 15.3% | 21.8% | 25.9% | 18.2% | 50.2% | 40.1% |
| Big Jump | 20.3% | 8.7% | 12.0% | 16.6% | 8.3% | 27.9% | 18.3% |
| Hand Fling | 22.9% | 9.4% | 15.8% | 14.6% | 4.3% | 37.8% | 38.4% |
| Draw Energy | 86.6% | 80.0% | 79.2% | 87.1% | 80.0% | 93.8% | 89.4% |
| Rare Candy | 66.6% | 69.7% | 44.8% | 94.0% | 47.8% | 76.9% | 71.2% |
| Fleet-Footed | 61.7% | 58.2% | 53.0% | 56.0% | 63.6% | 58.5% | 55.6% |
| Star Alchemy | 55.6% | 37.7% | 41.6% | 87.3% | 41.1% | 70.0% | 61.6% |
| Celebration | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Same seed, 2 Raikou V / 3 Aipom / 2 Ambipom (before the 4/4 prize-race thicken): g30 win **3.5 / 5.2 / 6.1 / 20.5 / 5.5 / 28.0 / 26.5%**, Hand Fling **22.9 / 9.4 / 15.8 / 14.6 / 4.3 / 37.8 / 38.4%**.

Same seed, previous Pikachu / Octillery / Sableye 60 (play-script fix): g30 win **2.8 / 3.6 / 2.7 / 19.0 / 2.3 / 6.7 / 6.4%**. Raikou V + Draw Energy + Candy + Forest Seal Stone lifts s60 and g the most (Hand Fling 10% → 38%). c60 Photon and t60 Dive still KO 100 HP Ambipom before three prize shots.

Same seed, Abra-era search script (Buneary not tutored): g30 win **2.7 / 3.2 / 2.7 / 18.4 / 1.6 / 6.8 / 7.6%**, Big Jump **9.3 / 4.2 / 5.6 / 8.5 / 2.2 / 11.4 / 8.3%**.

Previous Abra + Net closer (same seed): g30 win **2.5 / 4.6 / 3.6 / 16.5 / 1.1 / 5.8 / 7.1%**. Celebration 30-hand was **3.3 / 3.9 / 2.9 / 18.1 / 0.9 / 1.7 / 1.0%**.

Goldfish from a ready board still grows the hand (Big Jump returns Buneary + Lopunny + Enriching; Draw Energy is net 0; Speed L on Raikou V is +2) and Hand Fling KOs Mewtwo at 12 cards. Live vs household 60s Draw Energy / Candy / Star Alchemy actually fire. Three prize shots still lose the race to Photon / Dive on the fast 60s.

Household 60s also kill the board first. C60 Photon Kinesis KOs 100 HP Ambipom for one prize and 90 HP Lopunny / 130 HP Porygon-Z for one; Raikou V is 200 HP but **two prizes**. d60 Dive / Ogerpon is faster than assembling `[C][C][C]` plus a 12-card hand.

---

## Win condition

**Current closer — Ambipom PAR 146.** Colorless Stage 1, 100 HP, evolves from Aipom PAR 145, no Ability.

- **[C] Collect** — Draw 2 cards.
- **[C][C][C] Hand Fling** — This attack does 20 damage for each card in your hand.

12 cards = 240 (Mewtwo 230 / Wo-Chien 230). 11 = 220 (Ogerpon 210). 16 = 320 (Dragapult). Hand stays after the attack. Six prizes still need three KOs of 2-prize Pokémon. Ambipom itself is 1 prize, so a post-attack death is a 2-for-1 if a spare Aipom → Ambipom is already on the bench.

**Recycle — Lopunny FLF 85 Big Jump.** Same printed sentence as Jumpluff DRX Leave It to the Wind. Returns this Pokémon **and all cards attached to it** (including Buneary underneath) to the hand.

**Previous closer — Gholdengo** (30th Celebration 108 / AR 142) — Metal Stage 1, 130 HP, evolves from Gimmighoul, retreat 2.

- **[M] Celebration** — If you have exactly 30 cards in your hand, take 2 Prize cards. If you do, shuffle your hand into your deck.
- **[M] Triple Smash 50×** — Flip 3 coins. 50 damage for each heads.

Celebration is an **attack**. Hand size is checked when you attack. Same turn you cannot also attack with Gimmighoul’s coin-search, Pikachu ex Parade / Zip-Zap, or Jirachi ex Wish Granter (draw until 7 — the wrong direction).

Going second, turn 1: a setup Gimmighoul may evolve (Broken Time-Space does not have a “not your first turn” clause). First player still cannot attack on turn 1.

Mew ex (30th) **Memory Helix** copies a benched Gholdengo’s Celebration. Metal Energy must be on **Mew**. 0 retreat.

---

## The Unlimited pieces that Standard/Expanded strip out

### Porygon-Z UNB 157 — Crazy Code

> As often as you like during your turn (before your attack), you may attach a Special Energy card from your hand to 1 of your Pokémon.

Unlimited: legal. This is the extra-attach rule. Aurora Energy still discards. Type lines on the Energy still apply.

### Enriching Energy SSP 191 — ACE SPEC

> When you attach this card from your hand to a Pokémon, draw 4 cards.

One copy. Mutex with Scoop Up Cyclone, Grand Tree, Precious Trolley, Computer Search, Dowsing Machine. Draw only from **hand** attach. Net **+3** on attach (−1 Energy, +4 cards). No type lock. Night Stretcher / Energy Retrieval / Super Rod cannot retrieve it (they say Basic Energy).

### Puzzle of Time BKP 109

> You may play 2 Puzzle of Time cards at once.
> • If you played 1 card, look at the top 3 cards of your deck and put them back in any order.
> • If you played 2 cards, put 2 cards from your discard pile into your hand.

The two-card mode is **any two cards**, not Items only. Four copies recycle the other two Puzzles, or Scoop Up Net + Enriching Energy, forever. Expanded-banned; Unlimited-legal.

### Scoop Up Net RCL 165

> Put 1 of your Pokémon that isn’t a Pokémon V or a Pokémon-GX into your hand. (Discard all attached cards.)

Expanded-banned **because** it scoops Rule Box Pokémon that are not V/GX, including Pokémon ex. Unlimited-legal.

Legal hosts for this loop: Abra, Dudunsparce, 30th Gholdengo, Gholdengo ex, N’s Zoroark ex, Mew ex. Illegal hosts: anything V or GX (Shaymin-EX cannot be Netted).

Energy attached to the scooped Pokémon goes to **discard**, which is what Puzzle of Time wants.

### Broken Time-Space PL 104

> Each player may evolve a Pokémon that he or she just played or evolved during that turn.

Unlimited-only (Platinum). No first-turn exception. Stage 2 the turn the Basic hits play.

### Forest of Giant Plants AOR 74

> Each player’s [G] Pokémon can evolve during his or her first turn or the turn he or she plays those Pokémon.

Expanded-banned. Unlimited-legal. Grass only, including turn 1. For this pile **Broken Time-Space is the stadium** (Porygon-Z and Gholdengo are not Grass). Do not pair two stadiums.

### Wally ROS 94 (backup if BTS is not in play)

> … You can use this card during your first turn or on a Pokémon that was put into play this turn.

Supporter, once. VS Seeker PHF 109 returns a Supporter from discard to hand, even one played this turn — you still only **play** one Supporter unless a card says otherwise.

### Lysandre’s Trump Card PHF 118

> Each player shuffles all cards in his or her discard pile into his or her deck (except for Lysandre’s Trump Card).

Unlimited-legal. With VS Seeker, the discard pile never stays empty. Recycles Puzzle / Net / Energy into the **deck**, not into hand. Secondary, not the +2 loop.

### Abra TWM 80 — Teleporter

> Once during your turn, if this Pokémon is in the Active Spot, you may shuffle it and all attached cards into your deck.

Psychic Basic, 40 HP, retreat 1. New in-play copy may Teleporter again. Must keep a Bench Pokémon or you lose.

Teleporter puts Enriching Energy in the **deck**. Puzzle of Time cannot see the deck. In Unlimited, **prefer Scoop Up Net over Teleporter** for the Energy loop. Teleporter is still the answer if Energy must return to the deck (Lysandre’s Trump Card / search).

Buddy-Buddy Poffin (40 ≤ 70) and Nest Ball both tutor Abra in Unlimited.

### Dudunsparce TEF 129 — Run Away Draw

> Once during your turn, you may draw 3 cards. If you drew any cards in this way, shuffle this Pokémon and all attached cards into your deck.

With Broken Time-Space: play Dunsparce → evolve → RAD → Nest Ball the Basic again → repeat.

Without Puzzle recycling the tutor, each cycle is Nest −1, evolve −1, RAD +3 = **+1**, and the next Dudunsparce must be in the +3 or you spend Evolution Incense and the loop nets 0. Enriching Energy attached before RAD goes to the **deck**, so Enriching + RAD is the wrong recycle path (use Net + Puzzle instead).

### Speed L Energy RCL 173

Draw 2 only if attached from hand to a **Lightning** Pokémon. Abra is Psychic: **no draw**. Crazy Code can attach it. Magnezone Magnetic Circuit cannot (it is not Lightning Energy while in hand).

Net on a Lightning host: +1 per attach. After Scoop Up Net (−1) and replaying the host (−1) and Puzzle (0), a Speed L recycle is **net 0**. Do not use it as the growth loop. Four Speed L attached and left on a Lightning Pokémon is a finite **+4**.

### Draw Energy CEC 209

Attach from hand, draw 1. Net **0** per attach. Four copies, no ACE SPEC. Cycle, not growth.

---

## A. Self-recycle Pokémon (Unlimited)

| Pokémon | Kind | Energy goes | Same-turn return |
|---|---|---|---|
| **Lopunny FLF Big Jump** | Ability, any slot, once per copy | **Hand** | Replay Buneary, BTS into Lopunny. **This 60.** |
| **Jumpluff DRX Leave It to the Wind** | Same sentence as Big Jump | **Hand** | Stage 2: Hoppip → Skiploom → Jumpluff. Same net, more pieces. |
| Scoop Up Net host | Item, not V/GX | **Discard** (attachments) | Replay Basic. Puzzle to take Energy back. Net +2. |
| Abra Teleporter | Ability, Active, once per copy | **Deck** | Worse than Big Jump. Do not use. |
| Dudunsparce RAD | Ability, any slot, +3 then leave | **Deck** | BTS re-evolve a new Dunsparce |
| Suicune-GX Phantom Wind | Ability, Bench | Deck | GX (Scoop Up Net cannot target it) |

---

## B. Same-turn evolution (Unlimited)

| Card | Repeats? | Notes |
|---|---|---|
| **Broken Time-Space** | Yes, any type, including the Pokémon you just evolved | **The stadium for this combo** |
| Forest of Giant Plants | Yes, Grass, including first turn | Wrong types for Porygon-Z / Gholdengo |
| Forest of Vitality | Grass→Grass, not first turn | Strictly worse here |
| Wally ROS | One evolution from deck, may target a Pokémon played this turn | Supporter |
| Rare Candy | No on a Basic played this turn; BTS does not override Candy’s sentence | Skip on the fresh Basic |
| Grand Tree | ACE SPEC, not a Basic played this turn | Mutex with Enriching Energy |

---

## C. Special Energy hand ⇄ Pokémon ⇄ hand

1. Attach **from hand** (Enriching / Speed L / Draw Energy text).
2. Extra attaches: **Crazy Code**.
3. Return Energy to **hand** (Puzzle of Time after it hits discard, or Super Scoop Up / Scoop Up Cyclone keeping it attached).

| Path | Energy lands | Unlimited repeatable? |
|---|---|---|
| Scoop Up Net → Puzzle of Time ×2 | Discard → hand | **Yes, infinite** |
| Super Scoop Up (heads) | Hand with the Pokémon | 4 copies, 50% |
| Scoop Up Cyclone | Hand with the Pokémon | Once, ACE SPEC, mutex with Enriching |
| Abra Teleporter / RAD | Deck | Only if you search it back (Hilda once, Pidgeot ex once, Computer Search ACE mutex) |
| Lysandre’s Trump Card | Discard → deck | Then still need a search to hand |
| Night Stretcher / Energy Retrieval | Basic Energy only | **No** Special Energy |

---

## D. Hand deltas (stop on 30)

| Net | Source | Unlimited note |
|---|---|---|
| **+4 per loop** | Enriching + Big Jump + replay Buneary + BTS evolve | **The infinite for this 60.** Attachments stay in hand. |
| **+3** per attach | Enriching Energy | 1 copy; Crazy Code reattaches it each loop |
| **+2 per loop** | Enriching + Net + Puzzle + replay host | Discard path. Backup if Lopunny is not in play. |
| +3 then leave | Dudunsparce RAD | BTS re-evolve; tutor cost can eat the +3 |
| +1 per attach | Speed L on Lightning | Recycle nets 0 |
| +1 each, once | N’s Zoroark Trade | Scoop-and-replay Trade is net 0 (filter, not growth) |
| +2 / +1 | Gholdengo ex Coin Bonus Active / Bench | Once per copy until scooped and replayed |
| +3 net | Carmine | One Supporter |
| to 7 | Research / Jirachi Wish Granter | Destroys a 30-hand |
| to prize count | Iono / N | Destroys a 30-hand |
| −1 | Extra Item, Switch, playing a Basic | Fine-tune |

Trade after the loop is the **+1** trim. An extra Poffin/Switch is the **−1** trim. Do not Iono at the end.

---

## Loop math (Unlimited)

### Primary infinite — Lopunny Big Jump (net +4 / cycle)

Board: Porygon-Z, Lopunny (Buneary underneath), a pivot so the board is not empty after Big Jump, Broken Time-Space.

1. Crazy Code: attach Enriching Energy. Hand **−1 +4 = +3**. Energy on Lopunny.
2. Big Jump: Buneary + Lopunny + Enriching to **hand** (**+3**). No Item.
3. Play Buneary. Hand **−1**.
4. BTS evolve Lopunny. Hand **−1**.

**Cycle net: +4.** Jumpluff DRX is the same sentence; the cycle spends Hoppip + Skiploom + Jumpluff (−3) and bounces those three plus Enriching (+4), still +4, but three evolution cards have to come back every lap.

Scoop Up Net + Puzzle is **+2** and sends Energy to discard. Abra Teleporter / RAD send Energy to the **deck**. Big Jump is strictly better for Enriching.

### Same-turn setup (going second, turn 1)

Broken Time-Space in play:

- Porygon → Porygon2 → Porygon-Z
- Buneary → Lopunny (nest a same-turn Buneary if the opener was played_turn 0)
- Aipom → Ambipom
- Then the +4 loop, then Hand Fling when 20×hand KOs

This is a **consistency** problem (opening 8 cards plus tutors), not a **rules** problem. Shaymin-EX Set Up draws **until 6** — useless once the hand is already large; do not play it during the loop. Dedenne-GX Dedechange discards the hand — setup only, never at 20+ cards.

### Dudunsparce + BTS (secondary, weaker)

Nest Ball −1, evolve −1, RAD +3 = **+1** if the next Dudunsparce is in the +3. Puzzle recycles Nest Ball from discard. If you also spend Evolution Incense every lap, net goes to 0. Do not put Enriching on Dudunsparce if you want Puzzle to see it — RAD hides it in the deck.

### What is not infinite even in Unlimited

- Hilda / Pidgeot ex Quick Search: still once per turn.
- Coin Bonus / Trade without Net: once per in-play copy.
- Speed L + Net + Puzzle: net 0.
- Draw Energy: net 0.
- Forest of Vitality without Grass draw-and-shuffle: wrong stadium.

---

## Backup attackers (all Unlimited-legal)

| Card | Formula | At 30 cards |
|---|---|---|
| **Ambipom PAR 146 Hand Fling** | 20 × your hand, [C][C][C] | **600** |
| Ambipom DRX 100 Hand Fling | 10 × your hand, [C][C] | 300 |
| Meowstic BUS 60 Hand Kinesis | 10 × your hand, [C][C] | 300 |
| Golurk BRS Big Hand | 30 + 10 × your hand | 330 |
| Gholdengo 30th Celebration | exactly 30 → 2 of 6 prizes | main win |

Meowstic Allure (draw 3) is a different attack; you cannot Allure and Hand Kinesis the same turn. Prefer Ambipom PAR if Celebration is bricked (wrong count, no Metal, first-player turn 1).

Mega Froslass ex counts the **opponent’s** hand. Wrong axis.

---

## ACE SPEC (still 1 per Unlimited deck)

Pick **Enriching Energy**. Scoop Up Cyclone would return Energy to hand without Puzzle, but you cannot run both. Precious Trolley / Grand Tree / Computer Search are the wrong one-of for this win condition.

---

## Combo Cub

- Simulate on **`s60`** (60 cards, 6 prizes, 4-of). That is the Unlimited constructed skeleton.
- The list must include Unlimited cards (Lopunny FLF Big Jump, Puzzle of Time, Scoop Up Net, Broken Time-Space, Porygon-Z, Enriching Energy, Ambipom PAR, Speed Lightning Energy, Octillery, Sableye Junk Hunt, Junk Arm). A Standard-rotated 60 is the wrong pool.
- Do not test this win condition on Family Cup 30-card presets.
- Goldfish stop: Hand Fling lethal vs a household 2-prizer (12 cards vs Mewtwo 230 / 16 vs Dragapult 320), not exactly 30. Six prizes still need **three** attacks.
- Engine parses those printed sentences (`tests/test_gholdengo_celebration.py`). Puzzle of Time look-N comes from print, not a hardcoded top-6 in `app/engine/game.py`. The household array is in `data/lab/gholdengo-30-array.json`.

---

## Appendix — what you lose if the pool shrinks

Kept only as a warning. **Not the format of this lab.**

| Leave Unlimited for… | The +2 loop dies because… |
|---|---|
| Expanded | Puzzle of Time, Scoop Up Net, Forest of Giant Plants, Lysandre’s Trump Card, Shaymin-EX, Sableye, Oranguru UPR are banned. Crazy Code and Broken Time-Space: BTS is pre-BW so it was never Expanded. |
| Standard 2026 (H/I/J) | Crazy Code, Puzzle, Net, BTS, Speed L, Gholdengo ex, Ambipom PAR, Meowstic BUS all gone. Hilda once per turn is the Enriching cap. |

---

## Sources

- Play! Pokémon: Unlimited constructed = 60 cards, 4-of except basic Energy, 6 prizes, no banned cards; latest printing.
- Pokémon.com / Serebii / pkmncards / Limitless: Gholdengo 30th Celebration, Enriching Energy SSP 191, Porygon-Z UNB 157, Puzzle of Time BKP 109, Scoop Up Net RCL 165, Broken Time-Space PL 104, Forest of Giant Plants AOR 74, Abra TWM 80, Lopunny FLF 85 Big Jump, Jumpluff DRX 3 Leave It to the Wind, Dudunsparce TEF 129, Speed L Energy RCL 173, Wally ROS 94, VS Seeker PHF 109, Lysandre’s Trump Card PHF 118, Ambipom PAR 146 / DRX 100, Meowstic BUS 60, Mew ex 30th, Jirachi ex 30th.
- Pokémon Rulings Compendium: VS Seeker same-turn Supporter; Rare Candy wording vs Broken Time-Space; Hilda may search Special Energy; N’s Zoroark Trade vs empty deck.
- PokeBeach / TPCi Expanded ban note: Scoop Up Net scoops Pokémon ex (not V/GX).
