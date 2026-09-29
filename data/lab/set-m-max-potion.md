# Set M greedy Max Potion

- **Seed**: `20260929`
- **Games per cell**: 1000
- **Foes**: equal-weight mean of T60, Hedrick, C60, D60
- **Copies**: 4
- **Cuts**: Cleffa, Cleffa, Maximum Belt, Ultra Ball
- **Elapsed**: 618.2s
- **Stop**: the mean was still rising at 4 copies. A fifth Max Potion is not legal.

## Win-rate array

Index is the number of Max Potion copies. Each step after 0 swaps exactly one card.

| Max Potion | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 |
| ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 0 | 83.1% | — | 79.5% | 77.4% | 78.4% | 97.1% |
| 1 | 84.3% | Cleffa | 81.6% | 78.0% | 81.6% | 96.1% |
| 2 | 85.2% | Cleffa | 81.5% | 79.0% | 83.2% | 97.0% |
| 3 | 88.0% | Maximum Belt | 86.4% | 81.2% | 86.3% | 98.2% |
| 4 | 89.0% | Ultra Ball | 88.8% | 83.1% | 86.3% | 97.8% |
