# C60 vs Worlds-2026-shaped Dragapult

Date: 2026-09-11
Seed: `20260911`
Games: 3,000 (C60 always A; first player random)
Rule: s60
Script: `data/lab/set_c60_vs_hedrick.py`
Raw: `data/lab/set-c60-vs-hedrick.json`

## What “mainstream Unlimited Dragapult” is

On Limitless **Unlimited**, Dragapult ex is still deck #1 (~9% share). That bucket mixes years of lists: Pidgeot, Dusknoir, Lost Zone, Charizard, and the current Standard core.

The list people actually sleeve in 2026 is **Andrew Hedrick, 1st Worlds 2026** ([Limitless 28752](https://limitlesstcg.com/decks/list/28752)):

- 4 Dreepy / 4 Drakloak / 3 Dragapult ex
- 2 Munkidori / 2 Budew / 1 Dunsparce / 1 Dudunsparce / 1 Meowth ex / 1 Fezandipiti ex
- 4 Lillie's Determination / 3 Boss / 2 Crispin / 1 Rosa's Encouragement
- 4 Poké Pad / 4 Crushing Hammer / 4 Poffin / 3 Night Stretcher / 3 Ultra Ball
- 1 Unfair Stamp / 1 Special Red Card / 2 Risky Ruins
- 3 Fire / 3 Darkness / 3 Psychic (no Rare Candy)

Older Unlimited Pidgeot / Rotom V / Counter Catcher / Forest Seal Stone is **not** in this engine.

## What we actually simulated (`SET_T_META_NAMES`)

Printed cards missing from the fallback catalog: Dunsparce, Dudunsparce, Meowth ex, Rosa's Encouragement, Special Red Card, Risky Ruins. Those slots became Nest Ball, Rare Candy ×2, Judge, Iono, extra Ultra Ball, extra Night Stretcher. Munkidori **Adrena-Brain** is parsed from printed text (Darkness attached, move up to 3 damage counters).

Hedrick's real list has **zero** Rare Candy; this engine list has two so the existing phantom script can still Candy into Dive.

## Result

| | C60 win |
| --- | ---: |
| vs household T60 (4 Candy, 5 Fire / 4 Psychic) | **52.3%** |
| vs Hedrick-shaped Worlds list | **68.1%** (first 70.9% / second 65.3%) |

Household T60 is the meaner engine opponent: more Candy and a 5/4 Fire/Psychic split, so Dive lands earlier. Hedrick's 3/3/3 split plus 4 Hammers (coin) is slower in this AI. Adrena-Brain can snipe a 30-damage Clefairy, but Darkness often loses the attach race to Dive.

One traced game (seed `20260911`): C60 won on **deck-out** 18 turns, prizes 4–5, Photon ×5, Dive ×4, one Dragapult KO. Typical prize-race noise, not a claim that C60 beats a human Hedrick pilot.
