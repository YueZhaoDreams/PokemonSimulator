# C60 s60 win-rate matrix (three Dragapult 60s included)

Date: 2026-09-12
Seed: `20260911`
Rule: s60 (60 cards, 4-of, 6 prizes, Pokémon are not energy)
Games: 3,000 / directed cell (row is player A; who goes first is random)
Script: `data/lab/set_c60_unl_matrix.py`
Raw: `data/lab/set-c60-unl-matrix.json`

Diagonal skipped. A vs B and B vs A are separate runs, so they need not sum to 100%.

## Decks

| Key | List | Strategy |
| --- | --- | --- |
| C60 | Locked Set C Standard 60 (15 Psychic, Prankish, no Search) | `party` |
| T60 | Household Set T stretched to 60 (4 Candy) | `phantom` |
| Hedrick | Printed Worlds 2026 Andrew Hedrick Dragapult | `phantom` |
| UNL | Unlimited-shaped Pidgeot / Rotom V / Counter Catcher Dragapult | `phantom` |
| D60 | Charm Ogerpon 60 | `demolish` |
| S60 | Floragato hunter 60 | `slash` |
| G | Carpet Set G 60 | `carnival` |

T60 / Hedrick / UNL are the three Dragapult 60s the engine can actually play. UNL is a card-pool package (Pidgeot ex, Rotom V, Lumineon V, Manaphy, Forest Seal Stone), not Unlimited copy rules.

## Row win rate

| A \\ B | C60 | T60 | Hedrick | UNL | D60 | S60 | G |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **C60** | — | 48.7% | 58.2% | 84.4% | 74.2% | 99.5% | 97.9% |
| **T60** | 51.7% | — | 56.0% | 68.2% | 81.5% | 80.5% | 84.4% |
| **Hedrick** | 42.1% | 45.6% | — | 64.2% | 71.4% | 74.9% | 83.8% |
| **UNL** | 15.7% | 32.3% | 34.9% | — | 52.2% | 62.6% | 75.0% |
| **D60** | 27.1% | 19.5% | 30.2% | 46.4% | — | 71.9% | 93.2% |
| **S60** | 0.5% | 20.5% | 23.9% | 36.6% | 28.8% | — | 66.8% |
| **G** | 2.6% | 14.8% | 15.5% | 24.3% | 7.0% | 32.4% | — |

## Read

Household **T60** (4 Candy) is the only Dragapult that is even with C60. Hedrick (no Candy) is a C60 favorite. UNL Pidgeot/Rotom is a blowout for C60: Instant Charge eats turns, 2 Drakloak, Wave Veil only shields *Pult's* bench.

Among Dragapults, T60 beats Hedrick (56.0%) and UNL (68.2%). Hedrick beats UNL (64.2%). Candy + 5 Fire / 4 Psychic still pays Dive faster than the Unlimited extras in this AI.

D60 still loses to every Dragapult and to C60. S60 / G remain Party food.

C60 vs T60 on this branch is **48.7%**, under the older 54.3% lock, because opponent Budew Itchy Pollen is a printed 0-cost attack. Both seats see that.
