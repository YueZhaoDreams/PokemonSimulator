# C60 vs Unlimited-shaped Dragapult

Date: 2026-09-11
Seed: `20260911`
Games: 3,000 (C60 always A; first player random)
Rule: s60
Script: `data/lab/set_c60_vs_unl.py`
Raw: `data/lab/set-c60-vs-unl.json`

## List

`SET_T_UNL_NAMES` is a 60 with the printed Unlimited extras that were missing before: Pidgeot line (OBF Gust Pidgey, not 151 Call for Family), Rotom V, Lumineon V, Manaphy, Counter Catcher, Forest Seal Stone, Professor Turo's Scenario, Collapsed Stadium, plus 4 Candy / 4 Nest / 4 Poffin / 4 Arven / 4 Iono.

| Card | Printed effect used |
| --- | --- |
| Pidgeot ex OBF 164 | Quick Search: any one card, once per turn |
| Rotom V LOR | Instant Charge: draw 3, then the turn ends |
| Lumineon V BRS | Luminous Sign: play from hand onto Bench, search a Supporter |
| Manaphy BRS 41 | Wave Veil: no attack damage to your Bench |
| Counter Catcher | More prizes remaining → gust |
| Forest Seal Stone | Star Alchemy on a Pokémon V, one VSTAR Power per game |
| Collapsed Stadium | Bench limit 4; opponent discards first |
| Professor Turo's Scenario | Return 1 in-play Pokémon and attachments to hand |

Pokémon V take 2 prizes. Scrap Short puts Tools in the Lost Zone.

## Result

| Opponent | C60 win |
| --- | ---: |
| Household T60 (4 Candy, 5 Fire / 4 Psychic) | **52.3%** |
| Printed Hedrick 60 (no Candy) | **60.6%** |
| **Unlimited-shaped Pidgeot/Rotom 60** | **83.2%** (first 85.2% / second 81.2%) |

This UNL shape is easier for C60 in the phantom AI than Hedrick or household T60: 2 Drakloak instead of 4, Instant Charge spends whole turns drawing, and Wave Veil only protects *Pult's* bench (C60 Metronome Dive still hits C60's own bench when they copy it). Candy is in the list; the engine still has to find Pidgeot and pay Dive.
