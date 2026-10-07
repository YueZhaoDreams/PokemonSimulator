# Set M greedy Eco Arm on the two Rescue Carrier list

Starting 60 is the locked Set M list: two Rescue Carrier, two Spiky Energy, three Max Potion, one Boss's Orders.
Ancient Origins Eco Arm shuffles 3 Pokémon Tool cards from the discard pile into the deck.
The sentence does not say "up to", so the Item stays in hand when fewer than 3 Tools are in the discard.
Set M recovers Hero's Cape first, then Bursting Balloon, then Bravery Charm.
Battle Cage is a Stadium. It is not a Tool, and Eco Arm leaves it in the discard.
Arven can search the Tools again after they return to the deck.
The earlier table in `data/lab/set-m-eco-arm.md` searched the pre-carrier Manaphy 60.

- **Seed**: `20261007`
- **Games per new cell**: 1000
- **Score**: loss-weighted win rate. Weights are frozen from the 0-copy list.
- **0-copy cells**: reused from the locked two Rescue Carrier list, seed 20261007, 1000 games.
- **Weights**: t60 16.7%, hedrick 24.3%, c60 23.1%, d60 3.6%, thorns 2.6%, starmie 29.8%
- **Copies**: 0
- **Cuts**: (none)
- **Elapsed**: 2028.0s

| Eco Arm | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie |
| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 88.4% | 91.6% | — | 91.6% | 87.8% | 88.4% | 98.2% | 98.7% | 85.0% |

## Step 1, every cut

Current weighted rate 88.4%. Best cut is not taken: Boss's Orders.

| Rank | Cut | Weighted | Mean | vs T60 | vs Hedrick | vs C60 | vs D60 | vs Thorns | vs Starmie | Eco Arm | Cape | Balloon | Charm |
| ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Boss's Orders | 87.9% | 91.5% | 92.3% | 84.3% | 89.3% | 99.1% | 98.6% | 85.1% | 6.9% | 2.5% | 6.9% | 5.1% |
| 2 | Rescue Carrier | 87.8% | 91.2% | 91.7% | 85.2% | 88.4% | 98.1% | 99.1% | 85.0% | 6.0% | 2.1% | 6.0% | 4.3% |
| 3 | Bursting Balloon | 87.8% | 91.3% | 91.7% | 85.3% | 88.1% | 98.5% | 99.4% | 85.0% | 2.9% | 1.4% | 2.7% | 2.9% |
| 4 | Penny | 87.7% | 91.3% | 91.1% | 86.5% | 87.7% | 99.2% | 98.9% | 84.5% | 6.8% | 2.3% | 6.7% | 5.1% |
| 5 | Counter Catcher | 87.7% | 91.2% | 91.6% | 84.1% | 87.0% | 98.5% | 99.1% | 86.7% | 6.7% | 2.5% | 6.7% | 5.0% |
| 6 | Battle Cage | 87.5% | 91.1% | 91.8% | 83.5% | 88.8% | 98.5% | 98.6% | 85.2% | 6.0% | 2.0% | 6.0% | 4.5% |
| 7 | Night Stretcher | 87.5% | 91.1% | 90.9% | 86.7% | 88.8% | 97.9% | 99.1% | 83.1% | 6.0% | 1.9% | 6.0% | 4.5% |
| 8 | Bravery Charm | 87.3% | 90.8% | 89.4% | 84.7% | 87.0% | 98.7% | 99.0% | 86.0% | 5.4% | 2.3% | 5.4% | 3.6% |
| 9 | Mew ex | 86.9% | 90.6% | 90.0% | 85.0% | 87.1% | 99.1% | 98.6% | 84.0% | 6.6% | 2.4% | 6.6% | 4.8% |
| 10 | Ultra Ball | 86.8% | 90.6% | 90.7% | 84.9% | 87.8% | 98.5% | 98.9% | 83.0% | 6.5% | 2.3% | 6.5% | 4.8% |
| 11 | Arven | 86.6% | 90.5% | 91.0% | 85.5% | 85.5% | 98.6% | 99.0% | 83.5% | 5.4% | 1.8% | 5.4% | 4.0% |
| 12 | Max Potion | 86.6% | 90.4% | 90.4% | 84.1% | 87.5% | 98.6% | 98.7% | 83.3% | 5.9% | 2.2% | 5.9% | 4.4% |
| 13 | Nest Ball | 86.5% | 90.3% | 89.0% | 86.1% | 86.1% | 98.8% | 98.7% | 83.3% | 7.1% | 2.6% | 7.0% | 4.9% |
| 14 | Crushing Hammer | 86.4% | 90.4% | 91.0% | 82.5% | 87.5% | 99.1% | 98.4% | 83.6% | 6.3% | 2.1% | 6.2% | 4.7% |
| 15 | Spiky Energy | 85.7% | 89.9% | 91.0% | 84.8% | 86.6% | 98.7% | 98.1% | 80.0% | 6.2% | 2.3% | 6.2% | 4.4% |
| 16 | Professor's Research | 85.5% | 89.7% | 89.3% | 81.0% | 87.2% | 98.8% | 99.0% | 82.8% | 4.3% | 1.4% | 4.3% | 3.2% |
| 17 | Iono | 85.4% | 89.5% | 89.3% | 83.1% | 87.2% | 97.8% | 98.5% | 81.2% | 5.4% | 1.9% | 5.3% | 3.9% |
| 18 | Hero's Cape | 84.8% | 89.0% | 88.5% | 84.1% | 81.2% | 98.5% | 98.5% | 83.1% | 5.8% | 0.0% | 5.8% | 5.8% |
| 19 | Igglybuff | 84.2% | 88.6% | 90.3% | 81.4% | 83.8% | 98.6% | 97.3% | 80.4% | 6.6% | 2.3% | 6.6% | 4.8% |
| 20 | Buddy-Buddy Poffin | 84.1% | 88.8% | 90.2% | 83.1% | 84.1% | 98.4% | 98.6% | 78.6% | 6.9% | 2.4% | 6.9% | 5.0% |
| 21 | Mime Jr. | 83.4% | 86.3% | 89.7% | 80.9% | 83.1% | 89.4% | 93.9% | 80.6% | 6.9% | 2.6% | 6.8% | 4.8% |
| 22 | Manaphy | 83.0% | 88.8% | 93.9% | 87.5% | 87.8% | 98.3% | 99.1% | 66.3% | 4.9% | 1.6% | 4.9% | 3.7% |

Stopped at 0 Eco Arm. The next copy, cutting Boss's Orders, is 87.93% against the current 88.39%.
