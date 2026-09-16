# 30th Galarian Meowth Treasure Rush — 60-card Unlimited (G30 lab)

Date: 2026-09-16
Status: engine plays 30th Celebration Galarian Meowth Treasure Rush (Basic, no evolve) with Lopunny FLF Big Jump, Shaymin UL Celebration Wind recycling Speed Lightning Energy, Penny / Scoop Up Net to replay Shaymin, Iron Hands ex Amp extra prize + Speed L host, Draw Energy, and Rare Candy. Win-rate array vs household 60s is in `data/lab/gholdengo-30-array.json`. Crown Zenith Fasten Claws stays the catalog default for the name Galarian Meowth.

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

主循环仍是 **Lopunny FLF 85 Big Jump**：印刷 `Once during your turn (before your attack), you may return this Pokémon and all cards attached to it to your hand.` Jumpluff DRX 3 Leave It to the Wind 是同一句，但是 Stage 2，这副 60 用 Stage 1 Lopunny。Crazy Code 贴 Enriching（+3）→ Big Jump 把 Buneary+Lopunny+Enriching 回手（+3）→ 重放 Buneary −1 → BTS 进化 −1，净 **+4** / 圈。Draw Energy CEC 209 贴上摸 1，净 0。

**主攻仍是 30th Galarian Meowth（J 101/128, `me04-101`）。** Basic 钢 70 HP，**不用进化**。印刷 Pay Day `[C]` 10「Draw a card.」；Treasure Rush **`[M]`** 10×「This attack does 10 damage for each card in your hand.」钢能量符号不是无色星。无色能量付不了 Rush。Crown Zenith Fasten Claws（`swsh12.5-084`）仍是名字默认。70 HP 可 Poffin。1 奖身体。10× 打 Mewtwo 230 要 **23 张手牌**。Pay Day 不能在 Rush 能 KO 时抢走攻击。

**砍掉 2 Raikou V + 2 Forest Seal Stone。电系位改 3 Iron Hands ex（PAR 70, `sv04-070`）。** Lightning Basic ex 230 HP，退 4，不吃 Poffin，所以 Nest 1→2。**Arm Press** `[L][L][C]` 160；**Amp You Very Much** `[L][C][C][C]` 120，印刷「If your opponent's Pokémon is Knocked Out by damage from this attack, take 1 more Prize card.」对 Clefairy 60 Amp 拿 **2 奖**（1+1），Rush 只拿 1。160/120 秒不了 Mewtwo 230 / Ogerpon 210 / Dragapult 320，胖子仍靠 Meowth Rush。Speed Lightning Energy 贴 Hands 才抽 2。刷牌不靠 Fleet-Footed / Star Alchemy。场上最多 **1** 只 Hands（2 奖，Net 能捞 ex，keep-names 拦住；Penny 也别捞）。

**砍掉 Aipom / Ambipom / Sableye / Remoraid / Octillery / Porygon2 / Pikachu。** Rare Candy 仍跳 Porygon → Porygon-Z。Wally 只给 Buneary→Lopunny。场上最多 **1** 只 Meowth，给 Shaymin 留座位。

**刷牌：Shaymin UL 8 Celebration Wind + Penny。** Crazy Code 把 Speed L 贴到 Iron Hands（最多 +8），Enriching 贴大兔子（+4），手牌打出 Shaymin 把电系身上的特殊电挪到 Lopunny（钢能量留在 Meowth 上）。Hands 已经能付招并 KO 时不要 Wind。Big Jump 整叠回手后再贴。Scoop Up Net（物品，可连用）或 Penny（支援者，每回合 1 张）把 Shaymin 拿回手再打，Wind 再触发。不用 Shaymin-EX Set Up（摸到 6 就停）。Enriching 仍是唯一 ACE SPEC。不用苹果龙。

家庭组 3000 盘数组（seed 20260911）这版 **Shaymin Wind + Penny**：胜率 **2.2 / 6.8 / 8.0 / 17.2 / 5.2 / 11.5 / 30.1%** vs c60/t60/hedrick/unl/d60/s60/g。上一版无 Shaymin 的 `[M]` + 4 钢是 **2.6 / 6.9 / 9.6 / 17.0 / 2.8 / 10.4 / 24.7%**。Big Jump 大约翻倍；g 24.7→30.1，d60 2.8→5.2。Wind 只在约 9–28% 的对局里打出（要 Shaymin 上手 + Raikou + 大兔子）。c60 Photon 仍秒 70 HP。Goldfish 场上齐了能摸到 30。

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

## The 60 (Unlimited constructed, Treasure Rush)

Printings are the text this lab uses. Galarian Meowth in this 60 is **30th Celebration 101** (Pay Day / Treasure Rush), not Crown Zenith Fasten Claws. Iron Hands ex is Paradox Rift 70 (Arm Press / Amp You Very Much). Draw Energy is Cosmic Eclipse 209.

| Qty | Card | Set | Why |
|---:|---|---|---|
| 3 | Buneary | FLF 84 | 60 HP → Poffin. Big Jump stack. |
| 2 | Lopunny | FLF 85 | **Big Jump**: this Pokémon + attachments to **hand**. Sitdown Bounce is not the closer. |
| 3 | Porygon | UNB 154 | 50 HP → Poffin. Rare Candy into Porygon-Z. |
| 2 | Porygon-Z | UNB 157 | Crazy Code. |
| 4 | Galarian Meowth | 30th 101 | **Treasure Rush** 10×hand, **`[M]`**. Pay Day `[C]` draws 1 when neither closer would KO. Basic, 70 HP → Poffin. **1 prize**. Cap **1** in play (bench seat for Shaymin). Hunt still wants a spare in hand. Fat 210–320 HP still needs Rush. |
| 3 | Iron Hands ex | PAR 70 | Lightning host for Speed L draw 2. **Amp You Very Much** 120 + printed extra prize on KO. **Arm Press** 160. 230 HP, **2 prizes** — do not open on it. Cap **1** in play. Nest-legal, not Poffin. Retreat 4 → Switch. Net *can* scoop ex; keep-names block it. |
| 4 | Shaymin | UL 8 | **Celebration Wind**: when put from **hand** onto the Bench, move any Energy to Lopunny. Not from Nest/Poffin. 70 HP → Poffin-legal, but the engine holds it in hand until Speed L is on Hands, and skips Wind if Hands can already pay+KO. |
| 4 | Puzzle of Time | BKP 109 | Discard retrieve backup. |
| 2 | Scoop Up Net | RCL 165 | Replay Shaymin the same turn (Item). Do **not** Net Meowth / Lopunny / Iron Hands. |
| 3 | Broken Time-Space | PL 104 | Same-turn Stage 1 evo (Lopunny). Does **not** override Rare Candy. |
| 2 | Nest Ball | any | Iron Hands is 230 HP — Poffin cannot fetch it. |
| 3 | Buddy-Buddy Poffin | TEF 144 | Buneary / Porygon / Galarian Meowth / Shaymin (70). |
| 2 | Ultra Ball | any | |
| 2 | VS Seeker | PHF 109 | Recycle Penny / Wally. |
| 1 | Wally | ROS 94 | Buneary→Lopunny. Meowth does not evolve. Cannot skip to Porygon-Z. |
| 2 | Penny | SVI 183 | **Put 1 of your Basic Pokémon and all attached cards into your hand.** Shaymin only here. Supporter, 1/turn. Cannot Penny Lopunny or Iron Hands. |
| 1 | Switch | any | Into Hands when Amp takes more prizes; into Meowth when Treasure Rush is still lethal after −1 card. Do not retreat Hands (cost 4 dumps Speed L). |
| 4 | Rare Candy | PAF 89 | Skip Porygon → Porygon-Z. Not first turn; not a Basic played this turn. |
| 1 | Enriching Energy | SSP 191 | ACE SPEC. Loop on Lopunny (Big Jump). |
| 4 | Speed Lightning Energy | RCL 173 | Draw 2 only on Lightning. Attach to Iron Hands ex, Wind onto Lopunny, Big Jump recycles. Do not spend on Metal Meowth. |
| 4 | Metal Energy | any | Pays Treasure Rush `[M]`. Once-per-turn attach. Colorless cannot pay Metal. Stay on Meowth through Wind. |
| 4 | Draw Energy | CEC 209 | Colorless; attach from hand, draw 1. Net 0. Crazy Code can spam it. Does **not** pay Rush. Pays Amp Colorless if Hands is still unpaid. |

**21 Pokémon + 26 Trainers + 13 Energy = 60.**

Cut Aipom, Ambipom, Sableye, Remoraid, Octillery, Pikachu, Porygon2, Junk Arm, Darkness, Lightning Energy, Professor's Research, Battle Compressor, Raikou V, Forest Seal Stone. The 8 Aipom/Ambipom slots plus trainer cuts become 4 Meowth + 3 Iron Hands + Nest + 4 Shaymin + 2 Penny.

Goldfish (board already up, going second): Rare Candy Porygon into Z, BTS into Lopunny, Nest Iron Hands ex, Meowth is already Basic. Attach one Metal to Meowth. Crazy Code Speed L onto Hands (draw 2 each, up to +8), Enriching onto Lopunny (draw 4), Draw Energy onto bounce host (or Hands if Amp is unpaid). Play Shaymin from hand: Celebration Wind moves Speed L (not Metal) onto Lopunny — skip Wind if Amp already KOs. Big Jump returns Buneary + Lopunny + Speed L + Enriching. Replay Buneary, BTS evolve, Net or Penny Shaymin, attach again. Amp Clefairy for 2 prizes. Treasure Rush when `10 × hand` KOs (23 vs Mewtwo 230) and `[M]` is attached.

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

G30 (`celebration` strategy, 30th Galarian Meowth Treasure Rush `[M]` + 4 Metal Energy + Lopunny FLF Big Jump + Shaymin UL Celebration Wind + Penny + 4 Meowth + 2 Raikou V) as player A vs the household 60s. Not a full NxN remake of `set-c60-unl-matrix`. Rules preset `s60` (60 / 6 prizes / 4-of). First player random. **3,000 games / cell, seed 20260911**. Elapsed **80.4s**.

Script: `data/lab/gholdengo-30-array.py`. Numbers: `data/lab/gholdengo-30-array.json`.

| A \\ B | c60 | t60 | hedrick | unl | d60 | s60 | g |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| g30 win | 2.2% | 6.8% | 8.0% | 17.2% | 5.2% | 11.5% | 30.1% |
| first | 1.9% | 7.5% | 8.5% | 17.5% | 5.4% | 10.4% | 29.5% |
| second | 2.6% | 6.1% | 7.6% | 16.9% | 5.0% | 12.6% | 30.7% |
| Crazy Code | 40.0% | 21.7% | 32.6% | 35.8% | 21.1% | 59.8% | 38.9% |
| Puzzle pair | 3.5% | 2.1% | 5.3% | 4.1% | 2.0% | 5.7% | 3.4% |
| Speed L draw | 31.8% | 16.7% | 26.5% | 28.5% | 14.9% | 52.7% | 32.2% |
| Big Jump | 41.3% | 29.6% | 34.9% | 45.1% | 28.0% | 62.0% | 33.9% |
| Treasure Rush | 29.6% | 27.0% | 33.5% | 18.2% | 4.1% | 32.5% | 49.3% |
| Draw Energy | 71.8% | 59.8% | 64.4% | 70.2% | 60.8% | 84.8% | 71.1% |
| Rare Candy | 48.5% | 67.3% | 38.1% | 92.5% | 30.4% | 65.9% | 45.3% |
| Fleet-Footed | 55.6% | 51.2% | 47.5% | 50.1% | 55.1% | 54.3% | 48.8% |
| Star Alchemy | 43.5% | 30.4% | 37.1% | 84.5% | 32.5% | 62.4% | 42.1% |
| Celebration Wind | 14.4% | 8.8% | 14.8% | 15.5% | 7.4% | 27.9% | 14.0% |
| Penny | 17.5% | 10.8% | 16.7% | 16.1% | 11.6% | 26.0% | 16.9% |
| Scoop Up Net | 20.0% | 12.1% | 19.4% | 18.7% | 12.8% | 31.4% | 19.0% |

Same seed, previous **`[M]` + 4 Metal, no Shaymin/Penny**: g30 win **2.6 / 6.9 / 9.6 / 17.0 / 2.8 / 10.4 / 24.7%**, Treasure Rush **25.5 / 27.4 / 32.6 / 13.8 / 1.9 / 22.7 / 45.5%**, Big Jump **18.3 / 10.9 / 15.5 / 17.9 / 8.0 / 35.6 / 14.9%**. Wind recycle roughly **doubles Big Jump** (c60 18→41, s60 36→62, g 15→34). Wins move most on **g** (24.7→30.1) and **d60** (2.8→5.2); s60 10.4→11.5; unl 17.0→17.2. Hedrick 9.6→8.0 and c60 2.6→2.2: Photon / Dive still KO 70 HP before three 2-prize shots, and Wind only fires in ~9–28% of games (need Shaymin in hand plus Raikou + Lopunny). Goldfish with the board already up still reaches 30.

Same seed, previous **wrong `[C][C]` cost + 4 Lightning Energy**: g30 win **2.5 / 7.0 / 8.5 / 17.3 / 5.3 / 15.2 / 28.9%**, Treasure Rush **30.1 / 25.2 / 32.2 / 18.5 / 4.2 / 33.9 / 50.1%**. Printed `[M]` is easier to *count* (one energy) but harder to *pay*: Crazy Code cannot dump Colorless onto a Metal cost, and once-per-turn attach waits for a Metal from a 4-of.

Same seed, previous **4 Aipom / 4 Ambipom / 1 Raikou**: g30 win **3.7 / 4.9 / 6.7 / 22.1 / 4.2 / 28.5 / 30.4%**, Hand Fling **23.7 / 11.4 / 17.6 / 15.0 / 3.4 / 37.8 / 42.5%**. Skipping evolve lifts t60 vs Ambipom (4.9→6.9) and hedrick (6.7→9.6); 2 Raikou lifts Speed L / Fleet-Footed / Star Alchemy. c60 stays ~2.5: Photon still KOs, and 70 HP Meowth dies even faster. s60 drops hard (28.5→10.4): 10× needs ~23 cards vs 20× at 12, `[M]` is once-per-turn, and 70 HP does not survive the prize race the way 100 HP Ambipom did. unl 22.1→17.0, g 30.4→24.7.

Same seed, 2 Raikou V / 3 Aipom / 2 Ambipom (before the 4/4 prize-race thicken): g30 win **3.5 / 5.2 / 6.1 / 20.5 / 5.5 / 28.0 / 26.5%**, Hand Fling **22.9 / 9.4 / 15.8 / 14.6 / 4.3 / 37.8 / 38.4%**.

Same seed, previous Pikachu / Octillery / Sableye 60 (play-script fix): g30 win **2.8 / 3.6 / 2.7 / 19.0 / 2.3 / 6.7 / 6.4%**. Raikou V + Draw Energy + Candy + Forest Seal Stone lifts s60 and g the most (Hand Fling 10% → 38%). c60 Photon and t60 Dive still KO 100 HP Ambipom before three prize shots.

Same seed, Abra-era search script (Buneary not tutored): g30 win **2.7 / 3.2 / 2.7 / 18.4 / 1.6 / 6.8 / 7.6%**, Big Jump **9.3 / 4.2 / 5.6 / 8.5 / 2.2 / 11.4 / 8.3%**.

Previous Abra + Net closer (same seed): g30 win **2.5 / 4.6 / 3.6 / 16.5 / 1.1 / 5.8 / 7.1%**. Celebration 30-hand was **3.3 / 3.9 / 2.9 / 18.1 / 0.9 / 1.7 / 1.0%**.

Goldfish from a ready board still grows the hand (Big Jump returns Buneary + Lopunny + Enriching; Draw Energy is net 0; Speed L on Raikou V is +2) and Treasure Rush KOs Mewtwo at 23 cards **if one Metal is already attached**. Live vs household 60s Draw Energy / Candy / Star Alchemy still fire, but Draw Energy does not pay Rush, so the once-per-turn attach has to find Metal. Three prize shots still lose the race to Photon / Dive on the fast 60s; 70 HP makes that race worse than 100 HP Ambipom except against slower Dragapult piles.

Household 60s also kill the board first. C60 Photon Kinesis KOs 70 HP Meowth for one prize and 90 HP Lopunny / 130 HP Porygon-Z for one; Raikou V is 200 HP but **two prizes**. d60 Dive / Ogerpon is faster than assembling `[M]` plus a 23-card hand.

---

## Win condition

**Current closer — 30th Galarian Meowth 101.** Metal Basic, 70 HP, Fire ×2, Grass −30. No evolve. Catalog alias `galarian meowth 30th` / `me04-101`. Set A Fasten Claws (`swsh12.5-084`) stays the name default.

- **[C] Pay Day 10** — Draw a card. Must not steal the attack when Treasure Rush would KO.
- **[M] Treasure Rush 10×** — This attack does 10 damage for each card in your hand. One Metal Energy. Colorless specials do not pay this cost.

23 cards = 230 (Mewtwo). 21 = 210 (Ogerpon). 32 = 320 (Dragapult). Hand stays after the attack. Six prizes still need three KOs of 2-prize Pokémon. Meowth itself is 1 prize, so a post-attack death is a 2-for-1 if a spare Meowth is already on the bench. 70 HP dies to almost every household attack; that is the cost of skipping Aipom→Ambipom.

**Lightning closer — Iron Hands ex PAR 70.** Lightning Basic ex, 230 HP, Fighting ×2, retreat 4, **2 prizes**. Catalog `sv04-070`. Speed L host. Do not open on it.

- **[L][L][C] Arm Press 160** — Pays with Speed L. Misses Mewtwo 230 / Ogerpon 210 / Dragapult 320.
- **[L][C][C][C] Amp You Very Much 120** — If your opponent's Pokémon is Knocked Out by damage from this attack, take 1 more Prize card. vs Clefairy 60: **2 prizes** (1+1). Prefer Amp over Rush when both KO a 1-prize body. Prefer Rush when 10× actually KOs a tank.

**Previous closer — Ambipom PAR 146.** Colorless Stage 1, 100 HP, evolves from Aipom PAR 145, no Ability.

- **[C] Collect** — Draw 2 cards.
- **[C][C][C] Hand Fling** — This attack does 20 damage for each card in your hand.

12 cards = 240 (Mewtwo 230 / Wo-Chien 230). 11 = 220 (Ogerpon 210). 16 = 320 (Dragapult).

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
