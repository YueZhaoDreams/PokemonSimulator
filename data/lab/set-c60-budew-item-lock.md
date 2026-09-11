# C60 + Budew Item lock (rejected)

Date: 2026-09-11
Seed: `20260911`
Rule: s60
Games: 1,500 / cell
Script: `data/lab/set_c60_budew_item_lock.py`
Raw: `data/lab/set-c60-budew-item-lock.json`

Printed **Item** lock is **Budew** PRE 4, Itchy Pollen `[]` 10: “During your opponent's next turn, they can't play any Item cards from their hand.” That is Nest / Poffin / Ultra / Candy / Switch / Hammer. It does **not** lock Supporters (Boss, Iono, Tulip, Hop).

Swap: **1 Budew for 1 Psychic Energy** on locked C60 (still 15−1 Energy). Family Cup Set C stays 30 and still has no Budew.

The 1,500-game cells used a temporary party path: Moon-Watching Party from Active Clefairy, then Switch onto Budew to Pollen, and skip Pollen when Photon / Moon can KO or Dive is paid. That path is **not** in locked `party` — C60 has no Budew, and sitting a 30 HP Grass body still lost even when the AI tried to use it.

| Foe | Locked C60 (3,000) | C60 + Budew − 1 Psychic (1,500) |
| --- | ---: | ---: |
| T60 | 54.3% | **45.3%** |
| Hedrick | 62.9% | **55.9%** |
| D60 | 75.3% | **69.0%** |

Do not lock Budew into C60. Party needs Clefairy Active to fire; Pollen needs Budew Active to attack. The Switch tax plus a 30 HP Dive / Demolish snack is worse than the 15th Psychic. Phantom already plays Budew — giving them a 1-prize snack helps T60 more than locking their Items helps us.
