# G: 4 Buddy-Buddy Poffin arrive, which 4 come out

Date: 2026-09-17
Seed: `20260915`
Rule: s60
G-side always A; first player random
Script: `data/lab/set_g_poffin_c60.py` + `data/lab/set_g_poffin_followup.py`
Raw: `data/lab/set-g-poffin-c60.json`, `data/lab/set-g-poffin-followup.json`

Base is frozen Friday-lock `SET_G_FRIDAY_NAMES` (3 Boss, Mega, Tornadus, 0 Poffin, 0 Mewtwo).
Mewtwo ex is not arriving; the earlier Mewtwo engine work was reverted.
Poffin is printed "Search your deck for up to 2 Basic Pokémon with 70 HP or
less and put them onto your Bench" — engine already plays exactly that.
G targets: Clefairy / Ledyba / Starly / Kecleon (11 cards).

## Headline

No 4-cut beats baseline on the competitive field (t60 / Hedrick / d60).
Poffin **loses ~2.5pp on household Candy Dragapult (t60) in every list and
every stage**, and gains +1–4pp on Hedrick / UNL / C60 / S60 / H.
All-field winner: **−Tornadus −Hop's Cramorant −Relicanth −Indeedee, +4 Poffin**
(`tech_keep_kec`, all-field 0.2847 vs baseline 0.2703).

If t60 is the matchup that matters, the data says keep baseline and sleeve
fewer than 4 — 2 Poffin loses t60 by the same ~3pp (dose-independent).

## Why Poffin loses t60

Poffin floods the bench with 60 HP basics (Party 673 → 1031 games, gust
892 → 1097 on tech vs t60). Phantom Dive does 200 to Active plus 6 bench
counters = exactly a KO on every Poffin target. The engine counts go up,
wins go down: Dragapult farms the extra bench faster than Wonder Storm
converts the extra energy. Every 1-for-1 screen swap (25/25) loses t60 vs
baseline 23.0%, and all four 2–4 Poffin lists lose t60 in both 2000-game
packages and 3000-game confirms.

## 1-for-1 screen (1,500 games) — do not use as the cut

Top singletons were Ledyba / Mega / Ultra Ball / Ledian. That auto top4
(`auto_top4`: −Ledyba −Mega −Ultra Ball −Ledian) **loses to baseline** on the
package field (all 0.2516 vs 0.2703) and collapses vs C60 (10.8%) and S60
(60.2%) — cutting the only Mega and the only Ultra Ball. Same lesson as the
Boss Friday screen: singleton ranking is noise plus "1 Poffin ≠ 4 Poffin".

Screen also says: cutting Tornadus is the worst t60 single (18.9%),
Munkidori / Trekking Shoes / Energy Search / Darkness are bad singles.
Do not cut: Munkidori, Darkness Energy, Mega, Ultra Ball, Energy Switch.

## 4-for-4 packages (2,000 games)

4 Poffin in. Weighted-all uses every foe's baseline loss rate.
Competitive = t60 + Hedrick + D60.

| List | Cuts | t60 | Hedrick | D60 | UNL | C60 | S60 | H | 竞争加权 | 全场加权 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **tech_keep_kec** | Tornadus, Cramorant, Relicanth, Indeedee | 21.2 | 33.5 | 7.0 | 46.5 | **21.6** | **69.5** | 96.1 | 0.1921 | **0.2847** |
| **keep_torn4** | Cramorant, Relicanth, Indeedee, Kecleon | 22.1 | 33.4 | 7.2 | 44.0 | 20.8 | 67.5 | 96.2 | **0.1951** | 0.2797 |
| bird_thin | Staraptor, Staravia, Starly, Cramorant | **22.9** | **33.6** | 5.3 | **46.9** | 19.6 | 68.2 | **97.0** | 0.1908 | 0.2795 |
| flutter_junk | Flutter Mane, Tornadus, Cramorant, Kecleon | 21.3 | 32.4 | **8.1** | 45.0 | 19.7 | 68.5 | 96.0 | 0.1930 | 0.2784 |
| junk4 | Tornadus, Cramorant, Kecleon, Relicanth | 20.9 | 32.6 | 7.0 | 45.8 | 18.8 | 67.0 | 96.9 | 0.1884 | 0.2741 |
| **baseline** | (Friday G, 0 Poffin) | **23.8** | 31.1 | 6.3 | 44.6 | 17.5 | 66.0 | 94.4 | 0.1909 | 0.2703 |
| ledian_thin | Ledian ×2, Ledyba, Cramorant | 19.8 | 30.8 | 6.7 | 43.9 | 20.6 | 67.8 | 96.8 | 0.1780 | 0.2697 |
| boom_search | Boomerang, Energy Search, Tornadus, Cramorant | 20.2 | 29.8 | 5.5 | 44.7 | 19.0 | 65.1 | 96.5 | 0.1721 | 0.2621 |
| search_swap | Energy Search, Trekking, Tornadus, Cramorant | 19.7 | 30.3 | 5.4 | 44.1 | 18.9 | 65.0 | 96.2 | 0.1713 | 0.2606 |
| supporters | Tulip, Drayton, Iris, Trekking | 20.0 | 30.0 | 6.6 | 46.2 | 16.4 | 64.5 | 95.2 | 0.1759 | 0.2602 |
| energy | Psychic ×3, Cramorant | 20.9 | 27.9 | 6.2 | 44.2 | 17.3 | 63.1 | 95.7 | 0.1716 | 0.2562 |
| auto_top4 | Ledyba, Mega, Ultra Ball, Ledian | 21.1 | 32.2 | 6.7 | 45.7 | 10.8 | 60.2 | 96.5 | 0.1866 | 0.2516 |
| poffin2 | Ledyba, Mega + 2 Poffin (bad cuts) | 22.0 | 31.2 | 7.4 | 43.2 | 8.7 | 57.0 | 95.3 | 0.1896 | 0.2430 |
| dark3cram | Darkness ×3, Cramorant | 16.8 | 26.2 | 4.5 | 41.5 | 17.1 | 63.9 | 95.5 | 0.1468 | 0.2385 |

`keep_torn4` and `poffin2_sane` are from the follow-up script (same seed).
`poffin2` inherited the noisy screen's Mega cut and is uninformative about
count — `poffin2_sane` (−Tornadus −Cramorant, +2 Poffin) is the real dose
check: t60 20.5 / Hedrick 33.0 / UNL 47.5 / C60 18.0.

## Confirm (3,000 games, t60 / Hedrick / D60 / UNL)

| List | t60 | Hedrick | D60 | UNL | 竞争加权 |
| --- | ---: | ---: | ---: | ---: | ---: |
| **baseline** | **23.6** | 31.7 | 6.8 | 45.6 | **0.1932** |
| tech_keep_kec | 21.4 | **33.8** | 6.9 | **46.5** | 0.1925 |
| keep_torn4 | 21.8 | 32.6 | **7.2** | 43.5 | 0.1917 |
| flutter_junk | 21.2 | 31.8 | **7.9** | 45.5 | 0.1907 |
| poffin2_sane | 20.2 | 32.7 | 7.5 | **47.0** | 0.1880 |

Nothing beats baseline on competitive at 3000 games. tech_keep_kec is
within 0.001 (noise); its edge is entirely the back half (C60 / S60 / H),
which the confirm field excludes.

## Lock (applied to `SET_G_NAMES` / `seed-g`)

**−1 Tornadus −1 Hop's Cramorant −1 Relicanth −1 Indeedee, +4 Buddy-Buddy Poffin.**

- Keeps Kecleon as the 11th Poffin target (junk4, which cuts Kecleon instead
  of Indeedee, is worse on both weights).
- Keeps the bird line, 4/4 Ledian, 3 Darkness, 17 Psychic, Mega, Ultra Ball,
  Energy Switch, and all 4 supporters.
- Those four cuts are not in C60; Poffin ×4 is exactly the C60 playset.

If t60 is the priority matchup: sleeve 2, not 4 (cuts Tornadus + Cramorant
still lose t60 ~3pp — there is no free lunch vs Candy Dive). Revisit after
Switch / Nest arrive and the bench plan changes.

Do **not**: cut Mega / Ultra Ball / Ledian line (auto_top4), cut 3 Darkness
(Adrena-Brain goes to 0, Hedrick −5pp), cut 3+ Psychic (Hedrick 27.9%),
cut Tulip/Drayton/Iris as a group, or thin the bird line for D60 (5.3%).

## After this (still not C60)

Poffin is the setup, not the closer. G still has no Photon plan (Mewtwo is
out), 1 Ultra Ball, 0 Nest, and Surfer as the only rotate. Next arrivals:

1. Nest Ball — Poffin only finds ≤70 HP; Nest finds Munkidori / Tornadus /
   anything prized.
2. Switch ×2 — Party is Active-only; Surfer is the current rotate.
3. Clefable ex / Prankish Clefable / 2nd Mega — wall + Lunar Zone.
4. Draw core (Hop / Lillie / Iono / Arven / Belt) + Telepathic.

Repo `SET_G_NAMES` / `seed-g` is this Poffin lock; the Friday list is frozen
as `SET_G_FRIDAY_NAMES` so the boss-friday and poffin labs stay reproducible.
