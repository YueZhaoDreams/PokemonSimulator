# Set M greedy Max Potion

- **Seed**: `20260929`
- **Games per cell**: 1000
- **Score**: loss-weighted win rate. Weights are frozen from the 0-potion list.
- **Weights**: t60 30.3%, hedrick 33.4%, c60 32.0%, d60 4.3%
- **Copies**: 4
- **Cuts**: Cleffa, Cleffa, Maximum Belt, Ultra Ball
- **Elapsed**: 618.2s

## Weighted win-rate array

Index is the number of Max Potion copies. Each step after 0 swaps exactly one card.
The weighted column is the decision score. Mean is the equal-weight average of the same four foes.

| Max Potion | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 |
| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 0 | 79.2% | 83.1% | — | 79.5% | 77.4% | 78.4% | 97.1% |
| 1 | 81.0% | 84.3% | Cleffa | 81.6% | 78.0% | 81.6% | 96.1% |
| 2 | 81.9% | 85.2% | Cleffa | 81.5% | 79.0% | 83.2% | 97.0% |
| 3 | 85.1% | 88.0% | Maximum Belt | 86.4% | 81.2% | 86.3% | 98.2% |
| 4 | 86.5% | 89.0% | Ultra Ball | 88.8% | 83.1% | 86.3% | 97.8% |

The weighted score was still rising at 4 copies. A fifth Max Potion is not legal.
