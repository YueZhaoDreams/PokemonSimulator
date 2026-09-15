# Live G: 3 Boss's Orders before Friday

Date: 2026-09-15
Seed: `20260915`
Rule: s60
G always A; first player random
Script: `data/lab/set_g_boss_friday.py`
Raw: `data/lab/set-g-boss-friday.json`
Confirm: `data/lab/set-g-boss-friday-confirm.json` (3,000 games)

Source of truth: **combocub.com** `seed-g` for `dancedfire@gmail.com` on 2026-09-15 (password checked). Live G is not the repo G-plus lock.

## Live G vs repo seed-g

Repo `SET_G_NAMES` is still G-plus (Plusle for Trapinch). Production already moved two C60-shaped pieces in:

| | Repo G-plus | Live combocub G |
| --- | --- | --- |
| Mewtwo (sv07-059 Super Psy Bolt) | 1 | **0** |
| Emolga | 1 | **0** |
| Mega Clefable ex (me03-031, Stage 1 from Clefairy) | 0 | **1** |
| Tornadus (sv07-120) | 0 | **1** |
| Boss's Orders | 0 | **0** |
| Psychic Energy | 17 | 17 |

Mega is playable: printed `evolves_from = Clefairy`, 320 HP, Shooting Moons. Not a brick.

Live C60 on the same account is **behind** locked `SET_C60_NAMES`: Tool Box + 15 Psychic, no Telepathic. Destination for the rebuild is still the locked list (14 Psychic + 2 Telepathic, Belt + Arven, no Tool Box). Family Cup Set C (30) still matches the repo.

Household foes D60 / T60 / Hedrick / UNL / S60 match the repo seeds. H on combocub does not (1 Zapdos, 4 Wattrel); bakeoff still uses seed H as the Lightning stand-in.

## Friday question

Three Boss's Orders are arriving. Stay at 60. Keep the G engine (Party Clefairy, Ledian gust, Staraptor, Mega) until the rest of C60 shows up.

`g` plays Boss whenever the opponent has a bench (score +8), not only to close like `party`. Queries named `boss_orders` also count the **opponent's** Boss, so vs Dragapult that counter is mixed. Vs H (no Boss) the 3-Boss lists fire it in ~38% of games.

## 1-for-1 screen (1,500 games) — do not use as the cut

Add 1 Boss, cut one name. Weighted by live-G loss rate on t60 / Hedrick / D60 / UNL.

The top three were **Starly / Energy Switch / Kecleon**. That 3-for-3 (`auto_top3`) **lost** to baseline on the 2,000-game package field. Starly is a Staraptor body; Energy Switch is a C60 card G already has 1 of (C60 wants 2). Singleton ranking is noise plus "1 supporter ≠ 3 supporters".

Potion alone also looks bad (Hedrick 28.4% vs 31.7%). Potion is still in the locked 3-cut because the extra two Boss copies change the supporter math.

Do **not** cut: Darkness Energy, Munkidori, Psychic Energy, Mega Clefable ex, Energy Search as a 1-of replacement for a single Boss.

## 3-for-3 packages (2,000 games)

3 Boss in. Weighted-all uses every foe's baseline loss rate. Competitive = t60 + Hedrick + D60.

| List | Cuts | t60 | Hedrick | D60 | UNL | C60 | S60 | H | 竞争加权 | 全场加权 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **plusle** | Potion, Poké Ball, Plusle | **25.7** | **34.0** | 7.5 | **51.1** | **16.5** | 66.5 | 95.1 | **21.09** | **28.72** |
| junk | Potion, Poké Ball, Cramorant | 24.5 | 34.1 | 8.4 | 47.6 | 16.2 | 63.1 | 95.0 | 21.07 | 27.87 |
| line_thin | Ledian, Ledyba, Potion | 24.8 | 32.5 | 8.6 | 48.1 | 15.8 | 65.0 | 94.8 | 20.80 | 27.87 |
| tornadus | Tornadus, Potion, Poké Ball | 23.1 | 33.3 | 8.3 | 50.0 | 14.5 | 63.7 | 94.4 | 20.36 | 27.51 |
| ledian_junk | Ledian, Potion, Poké Ball | 23.9 | 32.9 | 7.7 | 49.5 | 16.4 | 63.1 | 95.8 | 20.26 | 27.74 |
| relicanth | Potion, Poké Ball, Relicanth | 24.0 | 32.9 | 7.5 | 50.2 | 15.2 | **66.8** | 93.6 | 20.25 | 27.88 |
| kecleon | Potion, Poké Ball, Kecleon | 22.8 | 33.3 | 8.0 | 50.8 | 14.1 | 62.6 | 94.4 | 20.11 | 27.29 |
| **baseline** | (live G, 0 Boss) | 22.8 | 31.4 | **8.8** | 44.2 | 14.4 | 64.7 | **96.0** | 19.85 | 26.51 |
| search | Energy Search, Poké Ball, Potion | 23.5 | 30.9 | 8.1 | 48.7 | 15.8 | 63.5 | 95.2 | 19.68 | 27.19 |
| ledian3 | Ledian ×3 | 23.6 | 29.5 | 8.8 | 47.4 | 14.5 | 62.2 | 94.3 | 19.62 | 26.61 |
| supporters | Tulip, Drayton, Iris | 23.2 | 30.9 | 7.5 | 49.1 | 13.7 | 61.7 | 94.0 | 19.39 | 26.50 |
| auto_top3 | Starly, Energy Switch, Kecleon | 23.0 | 31.1 | 7.2 | 49.5 | 12.4 | 63.4 | 95.0 | 19.28 | 26.36 |
| energy | Psychic Energy, Potion, Poké Ball | 21.9 | 31.9 | 7.3 | 48.7 | 15.8 | 64.8 | 95.4 | 19.21 | 27.04 |
| dark3 | Darkness ×3 | 18.4 | 26.7 | 5.8 | 43.8 | 13.7 | 60.1 | 93.2 | 15.90 | 23.65 |

## Confirm (3,000 games, competitive four)

| List | t60 | Hedrick | D60 | UNL | weighted |
| --- | ---: | ---: | ---: | ---: | ---: |
| **plusle** | **25.3** | **34.5** | 6.9 | **50.5** | **0.264** |
| 2 Boss (Potion + Poké Ball) | 23.6 | 32.6 | **9.0** | 48.1 | 0.258 |
| junk (Cramorant instead of Plusle) | 24.0 | 33.0 | 8.0 | 47.7 | 0.256 |
| 1 Boss for Kecleon | 22.6 | 31.6 | 8.1 | 46.3 | 0.247 |
| live G | 22.7 | 31.4 | 8.7 | 45.1 | 0.246 |

plusle vs live G: T60 **+2.6**, Hedrick **+3.1**, UNL **+5.4**, D60 **−1.8**. Charm Ogerpon does not want this swap; Dragapult does.

## Lock (Friday)

**−1 Potion −1 Poké Ball −1 Plusle, +3 Boss's Orders.**

Those three cuts are not in C60. Keep Mega, Tornadus, Energy Switch, Ultra Ball, Darkness, Munkidori, the 4/4 Ledian line, and 17 Psychic.

If the mail is late:

- **2 Boss:** Potion + Poké Ball (keep Plusle). Still up vs live G.
- **1 Boss:** almost a wash. Do not bother; wait for the other two.

Do **not**: dump 3 Ledian, dump 3 Darkness, cut Energy Switch, cut Starly, or replace Tulip/Drayton/Iris yet.

## After Friday (G → C60, cards arriving later)

Set C (30) already holds Mewtwo ex ×2, Clefable ×4, Clefable ex ×4, Mega ×4, Nest ×2, Hop ×2, Lillie, Belt, Tool Box, Arven, Boss ×1. Do not cannibalize that 30 until Family Cup is done unless those copies are extras.

When C60 pieces actually arrive, next slots that did **not** win as Friday Boss-cuts:

1. **Nest Ball / Poffin** — G has no reliable Pokémon search (Poké Ball is a coin, Ultra Ball is 1). C60 is 4 Nest + 4 Poffin.
2. **Switch ×2** — Party is Active-only; Surfer is the current rotate. Replace Surfer after Switch is in.
3. **Mewtwo ex** — Photon closer. Cut Tornadus / Staraptor line after the ex is in play, not before.
4. **Clefable ex ×3 / Clefable ×2 / 2nd Mega** — wall + Lunar Zone. Mega is already 1.
5. **Hop / Lillie / Iono / Arven / Jacq** — only after the Pokémon search and Switch are real.
6. Energy count 17 → 14 Psychic + 2 Telepathic. **Do not** spend a Psychic slot on a 4th Boss (toolbox lab: 4th Boss lost T60).

Ledian gust is still this 60's printed Boss-like hook until the 3 supporters are in hand often enough. Thin that line **after** Mewtwo ex, one copy at a time (`ledian3` lost Hedrick).

## Read

Live G vs Dragapult is still a losing matchup. Three Boss copies buy about three points vs household T60 and Hedrick, and they are exactly the C60 gust package. Potion never heals a 6-prize race. Coin Poké Ball is worse than Ultra Ball. Plusle's Plus Damage almost never fires in this 60 (`g-plus` already saw 0 Plusle games on several cells). Hop's Cramorant is the next 1-of to cut when the fourth C60 card arrives; it was the runner-up 3-cut.

Repo `SET_G_NAMES` is left as G-plus so historical C60-vs-G cells stay comparable. Apply the Friday list on combocub `seed-g` by hand (upsert does not overwrite `cards_json`).
