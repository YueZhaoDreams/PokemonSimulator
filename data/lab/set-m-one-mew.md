# Set M one-Mew bench

Same locked Penny list. Old board plays every Mew ex in hand.
one_mew leaves a second Mew ex in hand. Bouncy Circle does 30 damage for each
benched Pokémon with a printed maximum HP of 30. Mew ex retreats for 0.

- **Seed**: `20260929`
- **Games per cell**: 1000
- **Score**: loss-weighted win rate. Comparison weights are frozen from the old board.
- **Weights**: t60 27.6%, hedrick 50.5%, c60 14.3%, d60 4.9%, thorns 2.7%
- **one_mew better**: True
- **Elapsed**: 926.1s

| Board | Weighted | Mean | Babies on bench | Games with 2 Mew | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| old | 86.9% | 92.6% | 3.76 | 35.1% | 89.8% | 81.3% | 94.7% | 98.2% | 99.0% |
| one_mew | 87.1% | 92.4% | 3.93 | 0.0% | 89.2% | 82.7% | 92.1% | 98.9% | 99.2% |

## One Budew

Weights for this step are frozen from the one_mew list with zero Budew.
A swap is better only when the weighted win rate rises.

- **Budew weights**: t60 28.5%, hedrick 45.6%, c60 20.8%, d60 2.9%, thorns 2.1%
- **Accepted**: Bravery Charm

| Budew | Weighted | Mean | Babies | Itchy Pollen | Cut | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |
| ---: | ---: | ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: |
| 0 | 87.3% | 92.4% | 3.93 | 0.9% | — | 89.2% | 82.7% | 92.1% | 98.9% | 99.2% |
| 1 | 87.9% | 91.2% | 4.09 | 24.6% | Bravery Charm | 89.9% | 84.4% | 91.0% | 98.3% | 92.6% |

### Every cut for one Budew

| Rank | Cut | Weighted | Mean | Babies | Itchy Pollen | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Bravery Charm | 87.9% | 91.2% | 4.09 | 24.6% | 89.9% | 84.4% | 91.0% | 98.3% | 92.6% |
| 2 | Ultra Ball | 87.7% | 91.2% | 4.09 | 25.2% | 88.3% | 84.1% | 92.6% | 98.5% | 92.7% |
| 3 | Max Potion | 87.6% | 91.2% | 4.11 | 24.2% | 89.6% | 83.9% | 91.0% | 98.7% | 92.7% |
| 4 | Penny | 87.5% | 91.5% | 4.09 | 23.9% | 89.2% | 83.5% | 91.7% | 98.9% | 94.4% |
| 5 | Bursting Balloon | 87.4% | 91.1% | 4.11 | 24.7% | 89.7% | 83.5% | 90.8% | 99.4% | 92.1% |
| 6 | Iono | 87.0% | 90.5% | 4.05 | 23.9% | 86.8% | 84.2% | 91.4% | 98.1% | 91.8% |
| 7 | Night Stretcher | 87.0% | 90.8% | 4.10 | 24.8% | 89.8% | 82.6% | 90.5% | 98.2% | 92.9% |
| 8 | Buddy-Buddy Poffin | 86.9% | 90.5% | 3.98 | 25.0% | 88.5% | 83.8% | 89.3% | 99.0% | 91.9% |
| 9 | Spiky Energy | 86.9% | 90.2% | 4.11 | 24.8% | 87.8% | 83.9% | 90.1% | 98.3% | 90.9% |
| 10 | Boss's Orders | 86.7% | 90.9% | 4.13 | 24.0% | 89.4% | 82.5% | 89.8% | 99.0% | 93.7% |
| 11 | Counter Catcher | 86.7% | 90.8% | 4.08 | 25.1% | 89.1% | 82.0% | 91.3% | 98.6% | 93.0% |
| 12 | Nest Ball | 86.4% | 90.8% | 4.04 | 24.7% | 88.4% | 81.5% | 92.1% | 99.0% | 93.1% |
| 13 | Crushing Hammer | 86.4% | 89.9% | 4.09 | 24.8% | 87.4% | 83.0% | 90.4% | 98.3% | 90.4% |
| 14 | Igglybuff | 86.1% | 89.9% | 3.85 | 25.1% | 87.7% | 81.9% | 91.2% | 98.5% | 90.1% |
| 15 | Professor's Research | 85.7% | 89.6% | 4.02 | 25.8% | 87.6% | 82.7% | 87.5% | 98.6% | 91.6% |
| 16 | Battle Cage | 85.6% | 90.0% | 4.08 | 24.8% | 87.1% | 82.0% | 88.8% | 98.3% | 93.6% |
| 17 | Arven | 85.6% | 90.2% | 4.09 | 25.0% | 89.4% | 80.0% | 89.9% | 98.9% | 93.0% |
| 18 | Mew ex | 84.6% | 89.4% | 4.09 | 27.0% | 87.7% | 79.8% | 88.3% | 98.4% | 92.8% |
| 19 | Mime Jr. | 84.3% | 86.2% | 3.86 | 25.8% | 88.7% | 78.6% | 90.4% | 88.2% | 84.9% |
| 20 | Hero's Cape | 84.3% | 88.8% | 4.12 | 25.6% | 88.5% | 79.9% | 85.3% | 98.6% | 91.8% |
