# Mill draw package

Level Ball finds any Pokémon with 90 HP or less, including Wugtrio. Nest Ball finds a Basic and benches it. HeartGold & SoulSilver Cleffa uses Eeeeeeek: shuffle the hand into the deck, draw 6, then Cleffa is Asleep. Sweet Sleeping Face prevents attack damage while it is Asleep. Survival Brace is the Twilight Masquerade ACE SPEC. A full-HP Pokémon that would be Knocked Out by attack damage is left at 10 HP, then the tool is discarded. Demolish ignores effects on the defending Pokémon, so Brace does not stop that attack. Junk Arm discards 2 cards from the hand and takes a Trainer from the discard, never another Junk Arm.

The machine needs an evolution and an Energy after the basics are out. Eeeeeeek is used when the hand has neither. Brace attaches only to a full-HP Wugtrio. Junk Arm discards Nest Ball and Poffin once a Wiglett and a Sweet Sleeping Face are in play.

- **Seed**: `20261028`
- **Games per seat**: 800
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 837.2s

The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in this same run.

## Lists

| List | Swap | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Junk | Brace | Attacks |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| level4 | Level Ball ×4, Nest Ball ×2 | 40.2% | 0.3% | 55.9% | 8.0% | +0.3% | 0.00 | 0.02 | 0.00 | 3.18 |
| cleffa | One HGSS Cleffa replaces one Nest Ball | 40.0% | 0.3% | 55.5% | 8.1% | +0.2% | 0.15 | 0.02 | 0.00 | 3.19 |
| lock | Wally lock. Level Ball ×3, Nest Ball ×3, Neutralization Zone | 39.8% | 0.3% | 55.7% | 9.4% | — | 0.00 | 0.02 | 0.00 | 3.16 |

Highest weighted list in this run: `level4` at 40.2%.

## Foes

| Foe | Lock | level4 | cleffa |
| :--- | ---: | ---: | ---: |
| Dragapult ex (T60) | 76.2% | -1.6% | -3.2% |
| Hedrick Worlds Dragapult | 62.1% | +1.9% | -0.4% |
| Unlimited Dragapult | 85.6% | +0.4% | -1.4% |
| Cornerstone Ogerpon (D60) | 9.4% | -1.4% | -1.3% |
| Wo-Chien / Floragato (S60) | 70.1% | -0.1% | +0.7% |
| Gholdengo (G) | 27.7% | +2.9% | +2.8% |
| Clefairy / Mewtwo (C60) | 32.9% | +0.3% | +3.7% |
| Set M (Mew ex) | 16.2% | +0.4% | -0.4% |
| Mega Starmie ex (Kudo) | 30.6% | +1.1% | +1.6% |
| Lucario Hariyama | 80.4% | -0.6% | -3.1% |
| Iron Thorns ex | 91.4% | -0.4% | -0.6% |
| Carpet Set H | 47.9% | +0.1% | -3.1% |
| Ambipom Hand Fling | 94.2% | -0.3% | +1.2% |

## Decision

The lock stays at Level Ball ×3 and Nest Ball ×3. No Cleffa.

This run is 800 games per seat after the play-order fix. Nest Ball had been scored as a search for Manaphy, which this 60 does not contain, so it was played before Level Ball. Both lists here play Level Ball first while Wugtrio is in the deck.

Level Ball ×4 is +0.337 points, 0.73 SE. Cleffa for one Nest Ball is +0.175 points, 0.38 SE. Eeeeeeek resolves 0.15 times per game. Mill attacks stay at 3.16 to 3.19 per game.
