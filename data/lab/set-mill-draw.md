# Mill draw package

Level Ball finds any Pokémon with 90 HP or less, including Wugtrio. Nest Ball finds a Basic and benches it. HeartGold & SoulSilver Cleffa uses Eeeeeeek: shuffle the hand into the deck, draw 6, then Cleffa is Asleep. Sweet Sleeping Face prevents attack damage while it is Asleep. Survival Brace is the Twilight Masquerade ACE SPEC. A full-HP Pokémon that would be Knocked Out by attack damage is left at 10 HP, then the tool is discarded. Demolish ignores effects on the defending Pokémon, so Brace does not stop that attack. Junk Arm discards 2 cards from the hand and takes a Trainer from the discard, never another Junk Arm.

The machine needs an evolution and an Energy after the basics are out. Eeeeeeek is used when the hand has neither. Brace attaches only to a full-HP Wugtrio. Junk Arm discards Nest Ball and Poffin once a Wiglett and a Sweet Sleeping Face are in play.

- **Seed**: `20261027`
- **Games per seat**: 160
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 101.6s

The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in this same run.

## Lists

| List | Swap | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Junk | Brace | Attacks |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| cleffa | One HGSS Cleffa replaces one Nest Ball | 40.4% | 0.7% | 56.6% | 10.3% | +0.7% | 0.15 | 0.02 | 0.00 | 3.25 |
| level4 | Level Ball ×4, Nest Ball ×2 | 40.0% | 0.7% | 55.9% | 11.9% | +0.3% | 0.00 | 0.02 | 0.00 | 3.23 |
| lock | Wally lock. Level Ball ×3, Nest Ball ×3, Neutralization Zone | 39.7% | 0.7% | 55.6% | 10.3% | — | 0.00 | 0.02 | 0.00 | 3.12 |
| junk2 | Junk Arm ×2 replaces two Nest Ball | 37.8% | 0.7% | 54.0% | 7.8% | -1.9% | 0.00 | 0.08 | 0.00 | 3.06 |
| brace | Survival Brace replaces Neutralization Zone | 36.6% | 0.7% | 51.2% | 8.1% | -3.1% | 0.00 | 0.02 | 0.10 | 3.05 |
| pack | Level ×4, Cleffa, Brace, Junk ×2. Cut three Nest, one Hammer, Zone | 36.0% | 0.7% | 50.0% | 6.6% | -3.7% | 0.14 | 0.06 | 0.10 | 3.08 |
| wake | Same package, Forest out and one Nest back, so sleep is one coin | 34.6% | 0.7% | 48.4% | 7.2% | -5.1% | 0.14 | 0.08 | 0.10 | 3.04 |

Highest weighted list in this run: `cleffa` at 40.4%.

## Foes

| Foe | Lock | cleffa | level4 | junk2 | brace | pack | wake |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Dragapult ex (T60) | 70.6% | +3.1% | +2.8% | +3.4% | -29.1% | -25.9% | -32.8% |
| Hedrick Worlds Dragapult | 63.1% | +0.0% | +1.3% | -1.9% | -8.1% | -11.9% | -11.2% |
| Unlimited Dragapult | 89.1% | -1.2% | -5.0% | -1.6% | -8.4% | -17.8% | -17.5% |
| Cornerstone Ogerpon (D60) | 10.3% | -0.0% | +1.6% | -2.5% | -2.2% | -3.8% | -3.1% |
| Wo-Chien / Floragato (S60) | 68.1% | +6.6% | +1.2% | -5.6% | +0.9% | +3.1% | +0.0% |
| Gholdengo (G) | 24.4% | +6.6% | +3.1% | -0.3% | +4.1% | +9.7% | +5.0% |
| Clefairy / Mewtwo (C60) | 31.2% | -1.6% | -0.9% | +0.0% | +0.9% | +4.1% | +5.6% |
| Set M (Mew ex) | 15.0% | -1.9% | +1.3% | -3.1% | -3.8% | -3.8% | -4.7% |
| Mega Starmie ex (Kudo) | 37.2% | -3.1% | -6.9% | -2.8% | -10.9% | -20.3% | -20.3% |
| Lucario Hariyama | 79.1% | +2.5% | +5.3% | +0.9% | +0.0% | -5.9% | -9.7% |
| Iron Thorns ex | 91.6% | +0.3% | -0.9% | -4.7% | -0.9% | -4.1% | -2.5% |
| Carpet Set H | 48.8% | +0.3% | -0.0% | -3.1% | +1.9% | +2.8% | -3.1% |
| Ambipom Hand Fling | 95.0% | +1.3% | +0.6% | +0.3% | -2.5% | +0.0% | -0.3% |

## Decision

The lock stays. Nothing here cleared two standard errors.

Cleffa for one Nest Ball is +0.71 points, 0.69 SE. Level Ball ×4 is +0.32 points, 0.31 SE. Junk Arm ×2 is −1.92 points. Survival Brace in place of Neutralization Zone is −3.05 points, 2.99 SE below the lock. The combined package is −3.68 points. Cutting Slumbering Forest as well is −5.12 points.

Brace is the loss. T60 has no Stadium, so Neutralization Zone is not replaced. That matchup falls 29.1 points, and Brace triggers 0.05 times per game. Starmie plays Gravity Mountain and Surfing Beach and still falls 10.9 points. Demolish ignores effects on the defending Pokémon, so Brace triggers 0 times against D60.

Eeeeeeek resolves 0.15 times per game. The attack leaves Cleffa Asleep, and Slumbering Forest makes the wake check two coins, so the draw does not become another Undersea on the next turn. Mill attacks move from 3.12 to 3.25.

Junk Arm resolves about 0.06 times per game beyond Junk Arm already played by Set M. The two discarded cards have to still be in hand. A Poffin or Nest Ball that was already played is in the discard, so it cannot pay that cost.
