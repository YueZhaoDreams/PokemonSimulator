# Set M greedy Bursting Balloon

Starting 60 is the Hero's Cape / four Max Potion list (two Budew, three Ultra Ball, no Maximum Belt, no Cleffa).

- **Seed**: `20260929`
- **Games per cell**: 1000
- **Score**: loss-weighted win rate. Weights are frozen from that starting list.
- **Weights**: T60 27.4%, Hedrick 45.6%, C60 23.9%, D60 3.1%
- **Copies**: 1
- **Cut**: Ultra Ball (3 → 2)
- **Elapsed**: 380.0s

Index is the number of Bursting Balloon copies. The weighted column is the decision score.

| Balloon | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 |
| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: |
| 0 | 85.7% | 89.5% | — | 88.5% | 80.9% | 90.0% | 98.7% |
| 1 | 87.2% | 90.4% | Ultra Ball | 89.2% | 83.4% | 90.5% | 98.6% |

## Step 1, every cut

Current weighted rate 85.7%. Accepted cut is Ultra Ball.

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Ultra Ball | 87.2% | 90.4% | 89.2% | 83.4% | 90.5% | 98.6% |
| 2 | Night Stretcher | 86.8% | 90.3% | 88.4% | 82.0% | 92.4% | 98.5% |
| 3 | Budew | 86.6% | 90.2% | 88.4% | 82.5% | 91.0% | 98.7% |
| 4 | Switch | 86.6% | 90.2% | 88.2% | 81.6% | 93.0% | 98.2% |
| 5 | Igglybuff | 86.4% | 89.9% | 88.2% | 82.6% | 90.2% | 98.7% |
| 6 | Mew ex | 86.4% | 89.7% | 88.6% | 82.9% | 89.2% | 98.1% |
| 7 | Iono | 86.4% | 89.9% | 88.1% | 82.0% | 91.5% | 98.0% |
| 8 | Mime Jr. | 86.4% | 87.6% | 89.5% | 82.2% | 90.6% | 88.0% |
| 9 | Boss's Orders | 86.1% | 89.7% | 89.7% | 80.9% | 90.4% | 97.9% |
| 10 | Nest Ball | 86.1% | 89.4% | 86.2% | 82.9% | 90.5% | 98.0% |
| 11 | Bravery Charm | 85.8% | 89.6% | 88.5% | 79.9% | 92.5% | 97.3% |
| 12 | Counter Catcher | 85.6% | 89.5% | 87.6% | 81.1% | 90.3% | 98.9% |
| 13 | Battle Cage | 85.3% | 89.0% | 85.8% | 80.9% | 91.5% | 98.0% |
| 14 | Arven | 85.0% | 88.8% | 88.6% | 79.5% | 89.5% | 97.8% |
| 15 | Max Potion | 84.9% | 88.7% | 85.3% | 81.1% | 90.0% | 98.4% |
| 16 | Buddy-Buddy Poffin | 84.7% | 88.7% | 88.8% | 78.5% | 90.2% | 97.4% |
| 17 | Professor's Research | 84.2% | 88.3% | 86.6% | 79.4% | 88.6% | 98.6% |
| 18 | Crushing Hammer | 84.1% | 88.2% | 85.4% | 79.5% | 89.6% | 98.1% |
| 19 | Hero's Cape | 83.6% | 87.6% | 86.4% | 79.4% | 86.6% | 98.1% |

## Step 2, every cut, not taken

Current weighted rate 87.2% with one balloon. Best cut Counter Catcher is 86.8% and does not rise.

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Counter Catcher | 86.8% | 90.1% | 88.4% | 82.8% | 91.0% | 98.3% |
| 2 | Mime Jr. | 86.3% | 86.8% | 88.3% | 83.4% | 89.8% | 85.6% |
| 3 | Ultra Ball | 86.2% | 89.7% | 88.1% | 82.4% | 89.8% | 98.4% |
| 4 | Switch | 86.2% | 89.7% | 88.3% | 81.7% | 90.9% | 98.0% |
| 5 | Night Stretcher | 86.2% | 89.4% | 86.8% | 82.8% | 90.4% | 97.5% |
| 6 | Boss's Orders | 85.6% | 89.6% | 88.4% | 79.9% | 91.6% | 98.6% |
| 7 | Budew | 85.5% | 89.5% | 88.2% | 79.6% | 91.8% | 98.5% |
| 8 | Buddy-Buddy Poffin | 85.4% | 89.2% | 87.1% | 81.1% | 90.1% | 98.3% |
| 9 | Bravery Charm | 85.2% | 88.8% | 86.3% | 81.6% | 89.1% | 98.4% |
| 10 | Iono | 84.9% | 89.1% | 88.2% | 79.3% | 90.2% | 98.6% |
| 11 | Max Potion | 84.9% | 89.1% | 86.6% | 79.1% | 92.3% | 98.3% |
| 12 | Professor's Research | 84.6% | 88.6% | 86.6% | 80.2% | 88.8% | 98.6% |
| 13 | Arven | 84.5% | 88.7% | 88.0% | 78.5% | 90.3% | 98.1% |
| 14 | Igglybuff | 84.4% | 88.6% | 86.8% | 79.1% | 90.2% | 98.1% |
| 15 | Crushing Hammer | 84.3% | 88.4% | 86.3% | 79.3% | 89.6% | 98.2% |
| 16 | Mew ex | 84.1% | 88.2% | 87.4% | 79.2% | 87.9% | 98.2% |
| 17 | Battle Cage | 83.9% | 88.2% | 85.8% | 78.8% | 89.6% | 98.7% |
| 18 | Nest Ball | 83.6% | 88.0% | 86.0% | 78.0% | 89.8% | 98.1% |
| 19 | Hero's Cape | 83.0% | 87.4% | 87.0% | 78.3% | 85.4% | 98.8% |
