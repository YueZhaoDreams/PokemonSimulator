# C60 greedy Wondrous Patch

- **Seed**: `20261002`
- **Games per cell**: 1000
- **Score**: loss-weighted win rate. Weights are frozen from the 0-Patch list.
- **Weights**: t60 21.2%, hedrick 27.2%, unl 5.5%, d60 23.5%, s60 0.1%, g 22.5%
- **Copies**: 2
- **Cuts**: Boss's Orders, Clefable CLC
- **Elapsed**: 5285.9s

Printed text: Attach a Basic Psychic Energy card from your discard pile to 1 of your Benched Psychic Pokémon.

Turn 2, when the Active Clefairy already has one Energy: attach one more, retreat, and discard those two. The Benched Clefairy that has two Psychic Energy comes up and uses Moon-Watching Party. Wonder Storm is 20 for each Psychic Energy on your Pokémon, so one other Clefairy is 80 and more Clefairies add more. The Patch is played while its target is still Benched. If the discard is empty, those two discarded Energy are the fuel: retreat into a different Bench Pokémon, Patch, then Switch the fueled Clefairy Active. Later copies can fuel Clefable ex or Mega Clefable ex.

## Weighted win-rate array

| Patch | Weighted | Mean | Cut this step | vs T60 | vs Hedrick | vs UNL | vs D60 | vs S60 | vs G |
| ---: | ---: | ---: | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 77.6% | 83.6% | — | 79.1% | 73.2% | 94.6% | 76.9% | 99.9% | 77.8% |
| 1 | 79.1% | 84.3% | Boss's Orders | 80.5% | 75.2% | 92.4% | 80.6% | 99.5% | 77.4% |
| 2 | 79.3% | 84.6% | Clefable CLC | 79.6% | 75.4% | 93.9% | 81.0% | 99.6% | 78.2% |

## Next swap, not taken

Best cut `Night Stretcher` weighted 79.0% does not beat 79.3% at 2 copies.
