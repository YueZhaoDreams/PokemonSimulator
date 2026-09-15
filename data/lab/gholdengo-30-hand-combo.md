# 30th Celebration Gholdengo — exactly-30-hand combo research

Date: 2026-09-15
Rule to test: **s60** (60 cards, 6 prizes). Not Family Cup 30-card.
Status: card-text survey. No Monte Carlo yet. Engine does not implement Celebration / Crazy Code / Teleporter / Enriching Energy attach-draw.

Printed sentences on the cards win. Lab notes here are not engine effects.

---

## 中文结论（给下一轮）

**Celebration 是攻击，不是 Ability。** 要 1 个 Metal，手牌恰好 30，拿 2 奖，然后把手牌洗回牌库。同一回合只能攻击一次，所以不能先用 Gimmighoul / Pikachu ex / Jirachi ex 的攻击再 Celebration。

**30 卡 Family Cup 做不到手牌 30。** 牌组 30、奖 3、场上至少 1 只宝可梦，手牌理论上限约 26。这个 combo 只能在 60 卡（s60 / Standard / Expanded）里谈。

**目前 Standard（H/I/J，含 30th Celebration）没有找到真正的同回合无限循环。** 最接近的可重复引擎是：

`Enriching Energy（+4，必须从手牌贴上）→ Dudunsparce Run Away Draw（+3，自己+附属牌回库）→ Hilda（进化宝可梦 + 任意 Energy，含 Special）`

Hilda 是支援者，一回合一次，所以 Enriching Energy 一回合最多「手牌里那张 + Hilda 再拿回一次」= **两次贴牌**。Abra Teleporter 不需要进化，但 Abra 是基础宝可梦，**Hilda 搜不到它**；Energy 回库后要再进手牌，Standard 同样卡在「一回合一次的检索」。

**Porygon-Z Crazy Code + Speed Lightning Energy 是 Expanded，不是 Standard。** Speed Lightning Energy 只在贴到 **Lightning** 宝可梦时抽 2；Abra 是 Psychic，贴上去不抽牌。Enriching Energy 不限属性，比 Speed L 更适合 Abra。

**同回合再进化：** Forest of Vitality 只允许 Grass→Grass，且自己的第一回合不能用；Dudunsparce 是无色，吃不到。Grand Tree / Rare Candy 都写了「本回合刚上场的基础宝可梦不能进化」。Wally（Roaring Skies）**可以**对本回合上场的宝可梦进化，但是支援者、Expanded。Broken Time-Space 是 Platinum，只有 Unlimited。Forest of Giant Plants、Puzzle of Time、Scoop Up Net 在 Expanded **禁卡**。

**精确停在 30：** 先用大块（+3/+4），最后用 N's Zoroark Trade（净 +1）、多打 Item（−1）、Ultra Ball（丢 2）微调。不要用 Iono / Research / Lillie / Jirachi ex Wish Granter（抽到 7）去堆 30。

**备用赢法合法性：** Ambipom DRX 是 10×手牌（Expanded，30 张=300）。Ambipom PAR 是 20×手牌（G 标记，Standard 已轮换，Expanded 仍合法，30 张=600）。Meowstic BUS Hand Kinesis 是 10×手牌（Expanded）；Allure 抽 3 是另一个攻击，同一回合不能两发。Standard 里手牌×伤害的主力就是 Celebration 自己；Mega Froslass ex 算的是**对手**手牌，不是你的。

---

## Format split

| Format | 60-card 30-hand? | Crazy Code | Enriching Energy | Abra TWM | Dudunsparce | Forest of Vitality | Gholdengo ex Coin Bonus |
|---|---|---|---|---|---|---|---|
| Standard 2026 (H/I/J + 30th Celebration main set) | Yes, in principle | No (UNB) | Yes (ACE SPEC, H) | Yes (H) | Yes (H) | Yes (I, Grass only) | No (G, rotated) |
| Expanded (BW-on, minus ban list) | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Unlimited | Yes | Yes | Yes | Yes | Yes | Yes | Yes |
| Family Cup 30-card / Combo Cub presets b,c,s30 | **No** — not enough cards exist | household scan | household scan | household scan | already in engine | household scan | household scan |

30th Celebration **Classic Collection** reprints are not Standard-legal. Main-set Gholdengo (EN 108/128, JP 087/103, AR 142/128) is a new card and is the Celebration attacker.

---

## Verified printed pieces

### Win condition — Gholdengo (30th Celebration 108/142)

Metal Stage 1, 130 HP, evolves from Gimmighoul, retreat 2.

- **[M] Celebration** — If you have exactly 30 cards in your hand, take 2 Prize cards. If you do, shuffle your hand into your deck.
- **[M] Triple Smash 50×** — Flip 3 coins. This attack does 50 damage for each heads.

Implications:

- Hand size is checked when you **attack**, after all Ability / Item / Energy plays.
- You need a Metal Energy on the attacker (or Mew ex copying the attack; see below).
- After success the hand is empty except for the shuffle-back; this is not a lock, it is a reset.
- First player cannot attack on turn 1. Going second can attack on their first turn if a setup Gimmighoul evolves into Gholdengo.

### 30th Celebration cards that look like engines but fight Celebration

These are **attacks**. Using one of them spends the only attack of the turn.

| Card | Printed effect (summary) | vs 30-hand |
|---|---|---|
| Gimmighoul 30th | [C] coin flip: search any 1 card | Tutor, then you cannot Celebration |
| Pikachu ex (day) | Pika-Pika Parade: any number of Basics from deck to Bench | Setup attack, not Celebration |
| Pikachu ex (night) | Zip-Zap Frenzy: attach any number of **Basic** Energy from hand | Not Special Energy; not Crazy Code |
| Jirachi ex 30th #102 | **Wish Granter**: draw until you have 7 in hand; **Swift** 150 | Caps at 7. Useless for 30; does not shrink a bigger hand |
| Mew ex 30th | Ability **Memory Helix**: this Pokémon can use the attacks of any of your Benched Pokémon (still need the Energy). Attack Teleportation Burst: may switch to Bench | **Can copy benched Gholdengo’s Celebration** while Mew is Active. Mew needs [M] on **itself**. 0 retreat |
| Ditto 30th | Coin-flip attack: swap Ditto with a Pokémon from deck, **keep attached cards** | Opposite of energy recycle (energy stays, Ditto leaves) |

Legendary birds (Moltres / Articuno / Zapdos) each have a once-per-turn Ability to attach a Basic Energy of their type from hand if all three are in play. That is extra **Basic** attach, not Special-Energy draw.

### Porygon-Z UNB 157 — Crazy Code (Expanded)

> As often as you like during your turn (before your attack), you may attach a Special Energy card from your hand to 1 of your Pokémon.

Removes the one-Energy-per-turn rule for **Special** Energy only. Aurora Energy still makes you discard; type restrictions on the Energy still apply. Does not attach from deck. Does not trigger “when you attach from your hand” if the Energy never came from hand.

### Abra TWM 80 — Teleporter (Standard + Expanded)

> Once during your turn, if this Pokémon is in the Active Spot, you may shuffle it and all attached cards into your deck.

- Psychic Basic, 40 HP, retreat **1**, attack Beam 10.
- “Once during your turn” is per Pokémon in play. A new copy that comes into play the same turn **may** Teleporter. The card does **not** say “you can’t use more than 1 Teleporter Ability during your turn.”
- If it is your only Pokémon, Teleporter loses the game (no Pokémon left in play).
- Attached Special Energy, Tools, and damage all go to **deck**, not discard, not hand.
- Buddy-Buddy Poffin legal tutor (40 ≤ 70 HP). Nest Ball’s Paldea Evolved print is **G** and is **not** Standard; Expanded still has Nest Ball. Ultra Ball is reprinted with I.

**Same-turn re-deploy (the question in the brief):**

1. Keep at least one Benched Pokémon (second Abra, or a 0-retreat pivot).
2. Teleporter the Active Abra → Abra + Energy into deck.
3. Promote the Bench Pokémon.
4. Poffin / Ultra Ball / (Expanded) Nest Ball / Mysterious Treasure the next Abra onto the Bench (Poffin puts it on the Bench; Ultra Ball puts it in hand, then you play it).
5. Get that Abra Active: **Switch** (I reprint, Standard), or **Rescue Board** (TWM H, retreat −2) on the **pivot that stays in play**, not on the Abra you Teleporter (the Tool would be shuffled in). Abra’s own retreat is 1, not 0.
6. Repeat. Each new in-play Abra has a fresh “once during your turn.”

Bottleneck is not “finding Abra.” Bottleneck is **getting the Special Energy back into hand** so the next attach can trigger draw.

Hilda cannot search Abra (Abra is a Basic, not an Evolution Pokémon).

### Speed L Energy RCL 173 (Expanded)

> As long as this card is attached to a Pokémon, it provides Lightning Energy.
> When you attach this card from your hand to a Lightning Pokémon, draw 2 cards.

In hand / deck / discard it is **not** Lightning Energy. Magnezone Magnetic Circuit (“attach a Lightning Energy card from your hand”) cannot attach it. Flaaffy Dynamotor cannot. Crazy Code can, because it names Special Energy.

**Abra is not Lightning. Attaching Speed L Energy to Abra does not draw.**

Net if attached to a Lightning Pokémon: −1 from hand, +2 draw = **+1**, Energy now on the Pokémon.

### Enriching Energy SSP 191 (Standard + Expanded, ACE SPEC)

> You can’t have more than 1 ACE SPEC card in your deck.
> As long as this card is attached to a Pokémon, it provides [C] Energy.
> When you attach this card from your hand to a Pokémon, draw 4 cards.

- One copy per deck. Mutex with Scoop Up Cyclone, Grand Tree, Precious Trolley, Secret Box, Unfair Stamp, Prime Catcher, …
- Draw **only** on attach **from hand**. Archeops / Hilda-to-the-Pokémon / deck-attach does **not** draw.
- No type restriction. This is the Energy that belongs on Abra or Dudunsparce.
- Night Stretcher / Energy Retrieval / Super Rod / Ordinary Rod / Klara name **Basic** Energy. They **cannot** recover Enriching Energy from discard.
- Hilda **can** search it from deck (ruling: Hilda says “an Energy card,” not Basic).

Net on attach: −1 +4 = **+3**, Energy now attached.

Known Standard pairing (already on Limitless / pkmncards commentary): Enriching Energy + Dudunsparce, Hilda searches both.

### Draw Energy CEC 209 (Expanded)

Same attach-from-hand trigger, but draw **1**. Four copies allowed. Net **0** per attach. Cycle, not growth.

### Dudunsparce TEF 129 (Standard + Expanded)

> Once during your turn, you may draw 3 cards. If you drew any cards in this way, shuffle this Pokémon and all attached cards into your deck.

Colorless Stage 1, 140 HP, retreat 3, evolves from Dunsparce. Ability works from Active or Bench (no Active restriction). Does **not** need Forest of Vitality.

If the deck is empty you cannot draw, so you cannot use it to shuffle for free (same idea as Trade: the draw is the effect).

Net: −1 when you play the Stage 1 from hand, +3 draw = **+2**, and the whole line leaves play.

### Forest of Vitality MEG 117 (Standard)

> Each player’s [G] Pokémon can evolve into [G] Pokémon during the turn they play those Pokémon, except during their first turn.

Ruling (Mega Evolution FAQ): Bulbasaur → Ivysaur → Venusaur in one turn is allowed when it is not your first turn.

Does **not** help Dudunsparce, Abra, Gimmighoul, or Porygon. Grass self-shuffle Ability that also draws was not found in the current Standard pool; Butterfree 151 **Bye-Bye Flight** shuffles itself, but it is an **attack**, G-mark, and also shuffles an opponent’s Benched Pokémon.

Forest of Giant Plants (AOR 74) is the old unrestricted Grass version. **Banned in Expanded.** Unlimited only.

### Grand Tree SCR 136 (ACE SPEC Stadium)

Once per turn, search Stage 1 from a Basic then Stage 2 from that Stage 1, from **deck**. Explicitly: cannot evolve a Basic on the first turn or a Basic put into play this turn. Mutex with Enriching Energy.

### Rare Candy (I reprint, Standard)

Cannot use on the first turn or on a Basic put into play this turn. Broken Time-Space does **not** override that sentence (compendium).

### Wally ROS 94 (Expanded supporter)

> Search your deck for a Pokémon that evolves from 1 of your Pokémon (excluding Pokémon-EX) and put it onto that Pokémon. … You can use this card during your first turn or on a Pokémon that was put into play this turn.

This is the Expanded answer to “Dudunsparce came back; evolve it this turn.” **Once**, because it is a Supporter. Not a loop.

### Broken Time-Space (Platinum, Unlimited)

Stadium: players may evolve Pokémon they play during their turn. Pre-BW → Unlimited only. This is the historical “evolve every Basic you just played, every turn.”

### Hilda WHT 84 (Standard supporter)

> Search your deck for an Evolution Pokémon and an Energy card, reveal them, and put them into your hand. Then, shuffle your deck.

Special Energy is legal. Abra is not. Dudunsparce / Gholdengo / Porygon-Z are.

### Precious Trolley SSP 185 (ACE SPEC)

> Search your deck for any number of Basic Pokémon and put them onto your Bench.

One-shot board dump (4 Dunsparce + Gimmighoul + Abra). Mutex with Enriching Energy. Does not draw.

### Scoop Up Cyclone TWM 162 (ACE SPEC)

> Put 1 of your Pokémon and all attached cards into your hand.

This is the clean “Energy returns to **hand**” card. Mutex with Enriching Energy, so you cannot pair the best draw Energy with the best scoop. Super Scoop Up (coin flip, same destination) has no current H/I/J print → Expanded only, not infinite.

### Expanded ban list that kills the “obvious” infinites

Puzzle of Time, Scoop Up Net, Forest of Giant Plants, Oranguru UPR (Resource Management), Sableye DEX, Shaymin-EX ROS, Lysandre’s Trump Card, Archeops (Primal Turbo prints), Chip-Chip Ice Axe, Reset Stamp, … — full list on Play! Pokémon / PokeGym Expanded list.

No Puzzle of Time item loop. No Scoop Up Net “Abra to hand, Energy to discard” loop.

---

## A. Pokémon that put themselves (and attachments) into the deck

| Pokémon | Kind | Draw? | Type | Active only? | Standard? | Same-turn return? |
|---|---|---|---|---|---|---|
| **Abra TWM Teleporter** | Ability, once per copy | No | Psychic | Yes | Yes | Play another Basic; no evolution required |
| **Dudunsparce TEF Run Away Draw** | Ability, once per copy | +3 then leave | Colorless | No | Yes | Need a Dunsparce that was **already** in play, or Wally (Expanded, once), or Forest (no, not Grass) |
| Suicune-GX Phantom Wind | Ability, once | No | Water | Bench only | No | GX, Expanded |
| Butterfree 151 Bye-Bye Flight | Attack | No | Grass | Must attack | No (G) | Spends the attack; also shuffles opponent |

Abra is the only Standard **Ability** that recycles attachments **without** being a Stage 1 that then cannot re-evolve.

Other “leaves play” cards (Turo, Super Scoop Up, Scoop Up Cyclone) send the Pokémon to **hand** and either discard attachments (Turo) or keep them (Scoop). Turo is a Supporter (once). Cyclone is ACE SPEC (once, mutex).

---

## B. Same-turn evolution — what actually repeats

| Card | Repeats in one turn? | Restriction | Format |
|---|---|---|---|
| Normal evolution | Each Pokémon once; not the turn it entered play | Always | All |
| Forest of Vitality | Yes, for Grass→Grass chains | Not your first turn | Standard |
| Forest of Giant Plants | Yes, Grass, including first turn | **Expanded banned** | Unlimited |
| Broken Time-Space | Yes, any type, the turn played | Platinum | Unlimited |
| Grand Tree | One chain per turn from deck | Not a Basic played this turn; ACE SPEC | Standard |
| Rare Candy | One skip to Stage 2 | Not a Basic played this turn | Standard |
| Wally ROS | One evolution from deck | **May** target a Pokémon played this turn | Expanded |
| Technical Machine: Evolution | Attack | Spends the attack; G print rotated from Standard | Expanded |
| Pikachu ex Pika-Pika Parade | Puts Basics in play, does not evolve | Attack | Standard 30th |

**Dudunsparce loop in Standard is therefore not “evolve, shuffle, Poffin, evolve again” on the same line in the same turn.** After Run Away Draw you can:

- Hilda Dudunsparce + Enriching Energy into hand,
- play a **new** Dunsparce,
- attach Enriching Energy again (+4),
- and **stop** (cannot evolve that Dunsparce).

Or start the turn with several Dunsparce **already in play** (previous turn / Precious Trolley last turn / Poffin last turn) and evolve all of them this turn, each Run Away Draw once. That is a burst, not a loop.

---

## C. Special Energy → Pokémon → draw → back to hand/deck → attach again

Must-haves for a real loop:

1. Attach **from hand** (Enriching / Speed L / Draw Energy text).
2. Unlimited extra attaches: **Crazy Code** (Expanded) or the single rule-attach (Standard: one Energy per turn unless a card says otherwise).
3. Return that Energy to **hand**, not merely to deck.

| Path | Energy destination | Repeatable in one turn? |
|---|---|---|
| Abra Teleporter / Dudunsparce RAD | **Deck** | Repeat attach only if you **search or draw** the Energy into hand again |
| Hilda | Deck → hand, Energy + Evolution | **Once** (Supporter) |
| Pidgeot ex Quick Search | Deck → hand, any 1 card | **Once** per turn, all Pidgeot; G, Expanded only |
| Scoop Up Cyclone | **Hand** (Pokémon + attachments) | Once, ACE SPEC, mutex with Enriching |
| Super Scoop Up | Hand on heads | 4 copies, 50%, Expanded |
| Professor Turo’s Scenario | Pokémon to hand, attachments **discarded** | Once; Special Energy stuck unless a non-Basic retrieval exists |
| Special Charge (FCO) | Special Energy discard → **deck** | Item; still need a search to hand |
| Night Stretcher / Energy Retrieval / Super Rod | Basic Energy only | **Cannot** touch Enriching / Speed L / Draw Energy |

**Standard ceiling:** at most **two** Enriching Energy attaches in one turn (copy started in hand, Hilda once). Crazy Code is illegal, so the second attach also needs a card that extra-attaches Special Energy. **There is no Standard Crazy Code.** The second Enriching Energy can use the one legal Energy attach of the turn if you did not already attach; if you already attached a Metal for Celebration, you **cannot** attach Enriching a second time in Standard.

That last sentence is the Standard killer:

- Celebration needs [M] on Gholdengo or Mew.
- Enriching Energy provides [C], not [M].
- One Energy attach per turn without Crazy Code.
- If Enriching is sitting on Dudunsparce and then shuffles away, Gholdengo still needs a Metal from somewhere (previous turn, Crispin, bird Ability, Jet Energy rotated, …).

Expanded Crazy Code ignores the one-attach rule and can dump Enriching / Speed L / Draw Energy all turn.

---

## D. Hand-size deltas (for stopping on 30)

Growth (all “once” unless noted):

| Net | Source | Limit |
|---|---|---|
| +4 raw / **+3 net** | Enriching Energy attach from hand | 1 copy; Standard 1 attach/turn without Crazy Code |
| +3 | Dudunsparce Run Away Draw | Once per Dudunsparce in play; then it leaves |
| +3 | Fezandipiti ex Flip the Script | Only if a KO happened on the opponent’s last turn; one Flip the Script per turn |
| +2 | Gholdengo ex Coin Bonus while Active | Once per Gholdengo ex; G rotated |
| +1 | Gholdengo ex Coin Bonus while Benched | Same |
| **+1 net** | N’s Zoroark ex Trade (discard 1, draw 2) | Once per Zoroark; discard is a cost; cannot use if deck is empty |
| +1 net | Speed L Energy on a Lightning Pokémon | Expanded; 4 copies |
| 0 net | Draw Energy | Expanded; 4 copies |
| +3 net | Carmine (play −1, discard −1, draw 5) | Supporter, once; TWM H |
| to 7 | Professor’s Research; Jirachi ex Wish Granter | **Destroys** a large hand or does nothing if already ≥7 |
| to remaining prizes | Iono | Usually shrinks |
| shuffle → 8 or 6 | Lillie’s Determination | Destroys a stacked hand |

Shrink / spend (to correct an overshoot):

| Net | Source |
|---|---|
| −1 | Play Switch, Poffin, Boss, Stadium, Rescue Board, extra Item |
| −1 | Attach a non-draw Energy (the Metal for Celebration, after drawing) |
| −1 | Play a Basic from hand onto the Bench |
| −2 from hand, +1 Pokémon | Ultra Ball (net −1 if you needed that Pokémon) |
| −1 +2 Basic Energy | Earthen Vessel (net +0 or +1 depending on the discard) |

**Do not** Iono / Research / Lillie as the last action before Celebration.

If a hypothetical loop were **+3 net** per cycle, stop at 27 then one more cycle, or stop at 28/29 and use Trade (+1) / one Item (−1) / Speed L (+1). If the loop is **+2 net** (Dudunsparce: −1 evo +3), stop at 28 or 30.

---

## Loop math that survived the card text

### Standard — not infinite

Optimistic **Turn N** burst (not turn-2 casual):

- Going second, opening 7 + draw 1 = **8**.
- 4 Dunsparce already in play from earlier turns (Poffin / Trolley last turn).
- Evolve 4 Dudunsparce: −4 from hand, +12 from Run Away Draw = **+8**, all four lines in the deck.
- One Enriching Energy attach before the first RAD: **+3 net**, Energy shuffles in with that Dudunsparce.
- Hilda: −1, Dudunsparce + Enriching to hand. Play Dunsparce −1. Attach Enriching **only if** you still have the Energy attach of the turn → often you do **not**, because Enriching was already the attach.
- 2–4 N’s Zoroark already in play: +1 each.

A clean count from 8: +8 (four RAD) +3 (Enriching) −1 (Hilda) +2 (two Trade) ≈ **20**, not 30, before other one-of draws (Carmine, Fez, Earthen Vessel, Pidgeot rotated). Hitting 30 in Standard requires drawing a large fraction of a 60-card deck with **stacked once-per-Pokémon Abilities plus Item tutors**, not a closed loop. It is not free. It is also not disproven for a dedicated 60-card pile that opens with Research/Carmine and then only uses +1/+3 engines — it is **unreliable**, not a combo in the infinite sense.

**Turn 2 (going second, first turn):** Forest of Vitality is off (first turn). You may evolve a **setup** Gimmighoul. You do not have four Dunsparce in play unless the opening hand + Poffin dumped them during setup (setup only places Basics; you can Poffin on turn 1). Four RAD on turn 1 going second is possible if four Dunsparce are in play and four Dudunsparce are in hand. That is a high-roll, still ~+8, plus Enriching +3, still far from +22.

### Expanded — Crazy Code, still not infinite without a banned card

Crazy Code lets you attach Enriching / Speed L / Draw Energy as often as they are in **hand**.

Per Enriching cycle with Abra Teleporter:

1. Crazy Code attach Enriching to Abra: **+3 net**.
2. Teleporter: Energy + Abra to deck. Hand unchanged. Must promote a Bench Pokémon.
3. Poffin Abra: **−1**, Abra on Bench; Switch **−1** to make it Active (or Rescue Board on a staying pivot, retreat 0).
4. Energy is in the deck. First cycle started with Energy in hand; later cycles need Hilda (once) or Pidgeot ex Quick Search (once) or a lucky draw.

**Hard cap on Enriching attaches in one Expanded turn:** copies in hand at the start of the attach sequence. With 1 ACE SPEC that is: 1 (started in hand) + 1 (Hilda) + 1 (Pidgeot ex) = **3** if both search Pokémon are already in play. Draw 4×3 = +12 raw, −3 Energy from hand, net **+9** from Enriching, minus Poffin/Switch per Teleporter.

Add four pre-built Dudunsparce RAD (+8 net) and four Trade (+4) and you can **cross 30**, then spend Items to land on 30, then attach Metal (Crazy Code cannot attach Basic Metal — need the rule attach or Magnezone for Basic Lightning, not Metal). Ultra Prism Magnezone attaches **Metal** Energy from hand as often as you like; that is Basic Metal, which can be the Celebration cost, and it does not draw.

Plausible Expanded **Turn N** kill:

1. Board already has Porygon-Z, Pidgeot ex, 2 Abra or a pivot, Gholdengo or Mew, maybe Zoroarks / leftover Dunsparce.
2. Crazy Code Enriching → Teleporter → Poffin → Switch → Hilda Enriching back → Crazy Code again → Teleporter → Pidgeot Enriching back → Crazy Code third time.
3. RAD / Trade until ≥30.
4. Spend Items or attach Magnezone Metals until **exactly 30**.
5. Attack Celebration (or Mew Memory Helix copy).

That is a **setup turn + combo turn**, not a turn-2 goldfish from nothing. It is also **not** an infinite: three Enriching attaches then the searches are gone.

Speed L version: need a **Lightning** Teleporter-equivalent. Abra does not qualify. Without a Lightning self-shuffle Ability, Speed L wants Scoop Up Cyclone (mutex) or Super Scoop Up (coins) to return to hand. Weaker than Enriching on Abra.

### Unlimited

Broken Time-Space + Forest of Giant Plants + Puzzle of Time + Lysandre’s Trump Card / VS Seeker restore true infinites. That is a different game than Standard 2026. Not required for Celebration to be interesting, and not the format Combo Cub simulates by default.

---

## Backup attackers (hand × damage) — reprint check

| Card | Formula | 30 cards | Format 2026 |
|---|---|---|---|
| Ambipom DRX 100 Hand Fling | 10 × cards in your hand, [C][C] | 300 | Expanded (BW) |
| Ambipom PAR 146 Hand Fling | 20 × cards in your hand, [C][C][C]; other attack Collect draw 2 | 600 | **Standard no** (G). Expanded yes |
| Meowstic BUS 60 Hand Kinesis | 10 × cards in your hand, [C][C]; Allure [P] draw 3 is a **different** attack | 300 | Expanded (SM). Standard no |
| Golurk BRS Big Hand | 30 + 10 × cards in your hand | 330 | Rotated from Standard |
| Mega Froslass ex Resentful Refrain | 50 × **opponent’s** hand | — | Standard, wrong axis |
| Gholdengo 30th Celebration | exactly 30 → 2 prizes | win | Standard |

No Standard reprint of Hand Fling / Hand Kinesis was found that is H/I/J. If the 30-hand pile misses Celebration (wrong count, no Metal, first-player turn 1), Expanded still converts the pile into 300–600 damage; Standard does not.

Meowstic cannot Allure and Hand Kinesis the same turn. Draw 3 first would be a previous turn.

---

## ACE SPEC mutex (pick one)

| ACE SPEC | Role in this pile |
|---|---|
| **Enriching Energy** | Best attach-draw. Default for the engine |
| Scoop Up Cyclone | Best Energy-to-hand; cannot coexist with Enriching |
| Grand Tree | Same-turn Stage 2 from deck; cannot evo a Basic played this turn |
| Precious Trolley | Dump every Basic onto the Bench; setup card, not the combo turn |
| Secret Box / Unfair Stamp / Prime Catcher / Hero’s Cape / … | Generally worse than Enriching for this win condition |

---

## Recommended lines to keep studying

1. **Standard 60 — Dudunsparce + Hilda + Enriching Energy + N’s Zoroark + Gholdengo / Mew ex**, Precious Trolley **or** Enriching (not both). Treat it as a **finite burst** that tries to land on 30, not an infinite. Carmine / Trade are the fine-tune. Do not play Iono at the end.
2. **Expanded 60 — Porygon-Z Crazy Code + Enriching Energy + Abra Teleporter + Hilda + Pidgeot ex**, Magnezone UPR for extra Basic Metal, Celebration. Count three Enriching attaches as the Energy cap, then RAD/Trade/Items to 30.
3. **Do not** build Speed L Energy on Abra. If Speed L is used, the host must be Lightning and must return the Energy to **hand**.
4. **Do not** expect Forest of Vitality to re-evolve Dudunsparce.
5. **Combo Cub:** use rule preset **s60**. A 30-card scan cannot hold 30 cards in hand. Engine work (separate feature) needs parser branches + tests that quote the printed sentences: Celebration, Teleporter, Crazy Code, Enriching Energy “from your hand”, Run Away Draw (already parsed).

---

## Engine gap (do not implement from this note)

`parse_ability_effects` already understands Dudunsparce-style “draw then shuffle this Pokémon into your deck.” It must not grow a “look 6” or a hardcoded Enriching draw from this file. A later feature should add tests with the exact English sentences above, then parser branches, then a s60 lab script.

---

## Sources

- Bulbapedia / Pokémon.com / Limitless / Serebii for Gholdengo 30th, Enriching Energy SSP 191, Speed L Energy RCL 173, Abra TWM 80, Dudunsparce TEF 129, Porygon-Z UNB 157, Forest of Vitality MEG 117, Grand Tree SCR 136, Hilda WHT, Precious Trolley SSP 185, Scoop Up Cyclone TWM 162, Gholdengo ex PAR 139, N’s Zoroark ex JTG, Draw Energy CEC, Wally ROS 94, Mew ex 30th, Jirachi ex 30th #102, Ambipom DRX 100, Ambipom PAR 146, Meowstic BUS 60.
- Pokémon Rulings Compendium: Forest of Vitality chain evo; Rare Candy vs Broken Time-Space; Hilda Special Energy; N’s Zoroark Trade vs empty deck.
- Play! Pokémon / PokeGym: 2026 Standard = H/I/J (G rotated 2026-04-10 in-person); Expanded ban list including Puzzle of Time, Scoop Up Net, Forest of Giant Plants.
- Pokémon.com: 30th Celebration Classic Collection is not Standard-legal; main set worldwide 2026-09-16 (TCG Live 2026-09-15).
