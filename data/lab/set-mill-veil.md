# Mill draw package

Level Ball finds any Pokémon with 90 HP or less, including Wugtrio. Nest Ball finds a Basic and benches it. HeartGold & SoulSilver Cleffa uses Eeeeeeek: shuffle the hand into the deck, draw 6, then Cleffa is Asleep. Sweet Sleeping Face prevents attack damage while it is Asleep. Survival Brace is the Twilight Masquerade ACE SPEC. A full-HP Pokémon that would be Knocked Out by attack damage is left at 10 HP, then the tool is discarded. Demolish ignores effects on the defending Pokémon, so Brace does not stop that attack. Junk Arm discards 2 cards from the hand and takes a Trainer from the discard, never another Junk Arm.

The machine needs an evolution and an Energy after the basics are out. Eeeeeeek is used when the hand has neither. Brace attaches only to a full-HP Wugtrio. Junk Arm discards Nest Ball and Poffin once a Wiglett and a Sweet Sleeping Face are in play.

Manaphy Wave Veil prevents damage done to benched Pokémon by attacks. Phantom Dive and Spooky Balloon place damage counters, and Wave Veil does not stop those, so Cleffa stays in the deck in those matches. Against bench damage, Poffin benches Manaphy and then Cleffa. Level Ball still searches for Wugtrio.

- **Seed**: `20261029`
- **Games per seat**: 400
- **Seats**: each list is player A and player B. A foe cell is the mean of those two win rates.
- **Weights**: frozen from the Sisters 60. Harder Sisters matchups count more.
- **Weights**: t60 4.0%, hedrick 5.1%, unl 2.2%, d60 14.5%, s60 7.0%, g 11.7%, c60 12.4%, m 14.5%, starmie 10.6%, lucario 5.1%, thorns 4.1%, h 7.6%, g30 1.1%
- **Elapsed**: 324.0s

The ± column is one standard error of that list's weighted rate. Delta is against the lock measured in this same run.

## Lists

| List | Swap | Weighted | ± | Mean | Worst | Delta | Eeeeeeek | Cleffa | Manaphy | Attacks |
| :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| veil | Manaphy and HGSS Cleffa replace two Nest Ball. Level Ball stays ×3. Poffin stays ×4. | 41.7% | 0.5% | 56.8% | 7.3% | +3.0% | 0.42 | 0.64 | 0.54 | 3.30 |
| lock | Wally lock. Level Ball ×3, Nest Ball ×3, Neutralization Zone | 38.7% | 0.4% | 55.0% | 5.9% | — | 0.00 | 0.00 | 0.05 | 3.13 |

Highest weighted list in this run: `veil` at 41.7%.

## Foes

| Foe | Lock | veil |
| :--- | ---: | ---: |
| Dragapult ex (T60) | 74.6% | +0.1% |
| Hedrick Worlds Dragapult | 60.1% | +0.5% |
| Unlimited Dragapult | 87.6% | -2.7% |
| Cornerstone Ogerpon (D60) | 5.9% | +1.4% |
| Wo-Chien / Floragato (S60) | 70.6% | -0.1% |
| Gholdengo (G) | 26.1% | +4.5% |
| Clefairy / Mewtwo (C60) | 35.1% | +3.9% |
| Set M (Mew ex) | 13.1% | +7.7% |
| Mega Starmie ex (Kudo) | 29.2% | +10.1% |
| Lucario Hariyama | 77.6% | +2.0% |
| Iron Thorns ex | 91.5% | -0.6% |
| Carpet Set H | 49.5% | -6.5% |
| Ambipom Hand Fling | 93.4% | +3.6% |

## Decision

`SET_MILL_NAMES` is the veil 60. Two Nest Ball leave. One Manaphy and one HeartGold & SoulSilver Cleffa come in. Level Ball stays at three. Poffin stays at four.

Seed `20261029`, 400 games each seat, both seats, Sisters loss weights. Weighted 38.729% → 41.719% (+2.990 points, difference ±0.654, 4.57 SE). Mean 54.962% → 56.798%. Worst remains D60, 5.88% → 7.25%.

Cleffa enters play 0.64 times a game. Eeeeeeek resolves 0.42 times a game. Undersea attacks move from 3.13 to 3.30 a game.

Cleffa enters the wall matches (D60 1.07, G 0.91, C60 0.91, Set M 0.99) and Mega Starmie (0.76) once Wave Veil is in play. Dragapult Cleffa entries stay at 0.08–0.09. Phantom Dive places damage counters, and Wave Veil does not stop that sentence. Carpet Set H is −6.5 points. Drifblim Spooky Balloon is the same kind of counter, so Cleffa stays in the deck there (0.10). Manaphy still comes out against Kecleon's Lick Whip and Fezandipiti's Cruel Arrow, which do damage.

Starmie is +10.1 points. Set M is +7.7. Gholdengo is +4.5. Clefairy is +3.9. Those gains carry the weighted rate.
