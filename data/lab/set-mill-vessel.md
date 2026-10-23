# Mill Vessel of Life pairs

- **Confirm seed**: `20261023`
- **Holdout seed**: `20261024`
- **Screen**: 32 games per seat, both seats, top 4 confirmed
- **Confirm**: 80 games per seat
- **Holdout**: 120 games per seat
- **Score**: mean of the two seat win rates, then loss-weighted. Weights are frozen from the sleep wall on the confirm seed.
- **Step**: one Nincada and one Shedinja replace two cards. A step is kept only when the confirmed weighted rate beats the current list by more than the combined standard error.
- **Weights**: t60 5.0%, hedrick 6.2%, unl 2.3%, d60 15.6%, s60 6.0%, g 11.5%, c60 11.4%, m 13.7%, starmie 11.6%, lucario 3.8%, thorns 2.0%, h 10.0%, g30 0.8%
- **Elapsed**: 1626s

Dig prevents effects of attacks, including damage, on heads during the opponent's next turn. Vessel of Life discards the cards attached to Shedinja, including the Nincada under it, and attaches Shedinja as a Tool. The Tool makes that Knock Out worth 1 fewer Prize. On a 1-Prize Wugtrio that is 0 Prizes. The line is worth about one extra Undersea Tunnel only when the Tool is actually knocked out. Handiwork and Miss Fortune Sisters still mill on the same turn as the attack, so the slots have to win the match, not the card-count comparison.

## Baseline

Sleep wall weighted 34.8% (SE 1.0%), mean 52.4%, worst 3.1%.

| Foe | Win rate |
| :--- | ---: |
| Dragapult ex (T60) | 68.8% |
| Hedrick Worlds Dragapult | 61.9% |
| Unlimited Dragapult | 85.6% |
| Cornerstone Ogerpon (D60) | 3.1% |
| Wo-Chien / Floragato (S60) | 63.1% |
| Gholdengo (G) | 28.7% |
| Clefairy / Mewtwo (C60) | 29.4% |
| Set M (Mew ex) | 15.0% |
| Mega Starmie ex (Kudo) | 28.1% |
| Lucario Hariyama | 76.2% |
| Iron Thorns ex | 87.5% |
| Carpet Set H | 38.1% |
| Ambipom Hand Fling | 95.0% |

## Path

### 1 pair, cut Counter Catcher + Miss Fortune Sisters

Weighted 34.8% → 35.6% (+0.8%, combined SE 1.4%). Mean 52.5%, worst 6.2%. Vessel 0.13/game, prizes denied 0.06, Nincada KO 0.04.

| Confirm rank | Cut | Weighted | Mean | Worst | Vessel | Nincada KO |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher + Miss Fortune Sisters | 35.6% | 52.5% | 6.2% | 0.13 | 0.04 |
| 2 | Switch + Wiglett | 34.5% | 51.6% | 3.8% | 0.15 | 0.07 |
| 3 | Crispin + Level Ball | 33.9% | 51.2% | 3.1% | 0.09 | 0.06 |
| 4 | Colress's Tenacity + Miss Fortune Sisters | 33.6% | 50.4% | 6.2% | 0.12 | 0.05 |

| Screen rank | Cut | Weighted | Mean | Worst |
| ---: | :--- | ---: | ---: | ---: |
| 1 | Counter Catcher + Miss Fortune Sisters | 37.0% | 52.8% | 7.8% |
| 2 | Colress's Tenacity + Miss Fortune Sisters | 36.8% | 52.4% | 6.2% |
| 3 | Switch + Wiglett | 36.6% | 53.2% | 4.7% |
| 4 | Crispin + Level Ball | 36.1% | 53.6% | 0.0% |
| 5 | Crushing Hammer x2 | 35.8% | 51.4% | 10.9% |
| 6 | Crispin + Team Rocket's Handiwork | 35.7% | 53.1% | 4.7% |
| 7 | Nest Ball + Reversal Energy | 35.6% | 52.5% | 6.2% |
| 8 | Miss Fortune Sisters + Nest Ball | 35.6% | 51.8% | 9.4% |

## Holdout

No finalist. The sleep wall stays the lock.

## Counts

| Card | Sleep | Finalist |
| :--- | ---: | ---: |
| — | same list | |

## Decision

No Nincada + Shedinja pair beat the sleep wall by more than the confirm noise. SET_MILL_NAMES stays the sleep wall.
