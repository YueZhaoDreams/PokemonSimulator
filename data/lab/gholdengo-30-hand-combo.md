# 30th Celebration Gholdengo — 60-card Unlimited, exactly 30 in hand

Date: 2026-09-15 (format restated 2026-09-15)
Status: card-text survey. No Monte Carlo yet.

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

在这个规则下，**同回合无限循环是存在的**。

主循环（净 **+2** 手牌 / 圈，可停在恰好 30）：

`Enriching Energy 从手牌贴上（+4）`
`→ Porygon-Z Crazy Code（Unlimited 任意次贴 Special Energy）`
`→ Scoop Up Net（非 V/GX 的宝可梦回手，附属牌进弃牌；官方点名可以捞 Pokémon ex）`
`→ Puzzle of Time 打出 2 张（从弃牌拿回任意 2 张牌，含 Special Energy 和 Scoop Up Net）`
`→ 再把 Abra / 宿主打出 → 再贴`

停手：手牌 28 再转一圈到 30，或 29 时用 Trade +1 / 多打一张 Item −1。然后 **[M] Celebration** 拿 2 奖，手牌洗回库。

**考虑了：2 奖 / 枪，Unlimited 6 奖，不是一轮杀。** 6 ÷ 2 = **至少 3 次 Celebration**（一回合一次攻击）。后手最早 T1/T2/T3；先手 T1 不能攻击，最早 T2/T3/T4（**4 个我方回合**）。Ambipom 600 也占一次攻击，替不掉枪数。上一版 60 只写了第一枪；这版把 Octillery / Junk Arm / Sableye 写进 60，专门接第二、第三枪。见 **Three Celebrations**。

同回合再进化用 **Broken Time-Space**（Platinum 体育场）：本回合刚打出或刚进化的宝可梦可以再进化。Porygon → Porygon2 → Porygon-Z、Gimmighoul → Gholdengo、Dunsparce → Dudunsparce 都可以在同一回合完成。Wally ROS 是一次性支援者备份。Forest of Vitality 在 Unlimited 里比 Forest of Giant Plants / BTS 弱，不是这副的体育场。

Abra Teleporter 把 Energy 洗进 **牌库**，不如 Scoop Up Net 把 Energy 送进 **弃牌** 再被 Puzzle of Time 拿回手。Speed Lightning Energy 贴 Abra（Psychic）不抽牌；Speed L 循环在付完 Scoop/重放成本后净 **0**，不要当增长引擎。

备用赢法在 Unlimited 全合法：Ambipom PAR Hand Fling **20×手牌**（30 张 = 600），Ambipom DRX / Meowstic BUS 是 **10×**（300）。

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

## The 60 (Unlimited constructed, three-shot)

Built to fire Celebration **three times**, not once. Printings are the text this lab uses.

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

## Win condition

**Gholdengo** (30th Celebration 108 / AR 142) — Metal Stage 1, 130 HP, evolves from Gimmighoul, retreat 2.

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
| Abra Teleporter | Ability, Active, once per copy | **Deck** | Play another Basic (Poffin / Nest). No evolution. |
| Dudunsparce RAD | Ability, any slot, +3 then leave | **Deck** | Broken Time-Space evolve a new Dunsparce |
| Suicune-GX Phantom Wind | Ability, Bench | Deck | GX (Scoop Up Net cannot target it) |
| Scoop Up Net host | Item, not V/GX | **Discard** (attachments) | Replay from hand. This is the Unlimited Energy path. |

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
| **+3** per attach | Enriching Energy | 1 copy; Crazy Code reattaches it each loop |
| **+2 per loop** | Enriching + Net + Puzzle + replay host | **The infinite.** Stop at 28, one more loop → 30 |
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

### Primary infinite — Enriching Energy (net +2 / cycle)

Board: Porygon-Z, a non-V/GX host (Abra is enough), Bench not empty after Net (keep a pivot).

1. Crazy Code: attach Enriching Energy. Hand **−1 +4 = +3**. Energy on the host.
2. Scoop Up Net. Hand **−1**, host **+1**. Energy to discard. Net 0 this step.
3. Play the host. Hand **−1**.
4. Play 2 Puzzle of Time. Hand **−2**, take Enriching Energy + Scoop Up Net (**+2**). Net 0. The two Puzzles hit discard.
5. Play the other 2 Puzzle of Time. Take the first 2 Puzzles back. Net 0.

**Cycle net: +2.** Repeat until 28 or 30. Attach a Basic Metal (one rule-attach, or Magnezone UPR Magnetic Circuit as often as you like from hand) onto Gholdengo or Mew. Attack Celebration.

Scoop Up Net on Abra does **not** require Abra to be Active. Teleporter does. Net is the better recycle.

If the opening hand already has Enriching + Net + 2 Puzzle, the first attach does not need Puzzle yet. Puzzle comes online the moment Energy hits discard.

### Same-turn setup (going second, turn 1)

Broken Time-Space in play:

- Porygon → Porygon2 → Porygon-Z
- Gimmighoul → Gholdengo (or Mew in Active, Gholdengo on Bench)
- Abra to Bench/Active as the Enriching host
- Then the +2 loop to 30, then Celebration

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
- The list must include Unlimited cards (Puzzle of Time, Scoop Up Net, Broken Time-Space, Porygon-Z, Enriching Energy, 30th Gholdengo, Octillery, Sableye Junk Hunt, Junk Arm). A Standard-rotated 60 is the wrong pool.
- Do not test this win condition on Family Cup 30-card presets.
- **Do not stop the goldfish at the first Celebration.** Two stop conditions: (a) time-to-first-30 / first Celebration, (b) turns until **three** Celebrations / 6 prizes, including the Octillery → Junk Arm / Junk Hunt rebuild. Report how often the second and third shots spend a Sableye attack (that is the 3-turn vs 4-turn vs 5-turn split).
- Engine today already parses Dudunsparce-style “draw then shuffle this Pokémon into your deck.” It does not parse Celebration, Crazy Code, Teleporter, Enriching Energy attach-from-hand, Puzzle of Time’s two-card discard search, Scoop Up Net, Octillery Abyssal Hand, Sableye Junk Hunt, or Junk Arm. A later feature needs tests that quote those printed sentences. Do not hardcode a look size from Puzzle of Time’s single-card mode.

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
- Pokémon.com / Serebii / pkmncards / Limitless: Gholdengo 30th Celebration, Enriching Energy SSP 191, Porygon-Z UNB 157, Puzzle of Time BKP 109, Scoop Up Net RCL 165, Broken Time-Space PL 104, Forest of Giant Plants AOR 74, Abra TWM 80, Dudunsparce TEF 129, Speed L Energy RCL 173, Wally ROS 94, VS Seeker PHF 109, Lysandre’s Trump Card PHF 118, Ambipom PAR 146 / DRX 100, Meowstic BUS 60, Mew ex 30th, Jirachi ex 30th.
- Pokémon Rulings Compendium: VS Seeker same-turn Supporter; Rare Candy wording vs Broken Time-Space; Hilda may search Special Energy; N’s Zoroark Trade vs empty deck.
- PokeBeach / TPCi Expanded ban note: Scoop Up Net scoops Pokémon ex (not V/GX).
