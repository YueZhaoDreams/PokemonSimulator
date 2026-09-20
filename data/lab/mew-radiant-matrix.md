# Radiant Charizard & 1-5 Colorless Tech Attackers: Monte Carlo Optimization Matrix

**Date**: 2026-09-20 09:52 UTC
**Sample Size**: 1,000 games per cell × 6 variants × 4 opponents = **24,000 games total**

## Executive Summary

- **Champion Variant**: **Phase 1 Champion: V5 Hybrid Baseline (Pure Baby)**
- **Peak Overall Win Rate**: **35.9%** (vs Phase 1 Baseline: 35.9%, **+0.0% net change**)
- **Best Matchup**: vs t60 (45.6%)

## Full Win-Rate Matrix

| Rank | Candidate Variant | Overall WR | vs Dragapult (T60) | vs Hedrick Worlds | vs Clefable/Mewtwo (C60) | vs Cornerstone (D60) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | **Phase 1 Champion: V5 Hybrid Baseline (Pure Baby)** | **35.9%** | 45.6% | 42.3% | 31.7% | 24.1% |
| 2 | RC-V5: 2-Fire Heavy Charizard Finisher | 23.5% | 32.6% | 27.4% | 19.6% | 14.3% |
| 3 | RC-V2: 1-Fire Hybrid Finisher | 21.2% | 29.4% | 26.2% | 17.7% | 11.4% |
| 4 | RC-V4: Focused Snorlax & Slaking Midrange (0 Energy) | 20.2% | 29.3% | 25.5% | 14.7% | 11.3% |
| 5 | RC-V1: Pure 0-Energy Slaking & Dunsparce Turbo | 16.8% | 24.2% | 21.1% | 11.7% | 10.1% |
| 6 | RC-V3: Full 1-5 Colorless Arsenal (0 Energy) | 13.3% | 20.9% | 17.3% | 10.1% | 5.0% |

## Attack Usage Insights

Key attacks executed during simulations across variants:
### Phase 1 Champion: V5 Hybrid Baseline (Pure Baby)
*Winning list from Phase 1: 3 Mew ex, 4 Igglybuff, 3 Budew, 2 Cleffa, 1 Mime Jr., 4 Poffin, 4 Nest, 4 Ultra, 4 Stretcher, 4 Cage, 3 Charm, 1 Belt, 4 Arven, 4 Iono, 2 Research, 3 Boss, 4 Hammer, 4 Switch, 2 CC.*

| Matchup | Win Rate | Top Attacks Executed |
| :--- | :---: | :--- |
| T60 | 45.6% | `event_prefix:Mew ex:`: 913 |
| HEDRICK | 42.3% | `event_prefix:Mew ex:`: 918 |
| C60 | 31.7% | `event_prefix:Mew ex:`: 971 |
| D60 | 24.1% | `event_prefix:Mew ex:`: 897 |

### RC-V5: 2-Fire Heavy Charizard Finisher
*Runs 2 Fire Energy for maximum reliability of drawing and attaching Fire Energy to Radiant Charizard, ensuring 250 Combustion Blast is always online.*

| Matchup | Win Rate | Top Attacks Executed |
| :--- | :---: | :--- |
| T60 | 32.6% | `event_prefix:Mew ex:`: 766, `event_prefix:Radiant Charizard:`: 54 |
| HEDRICK | 27.4% | `event_prefix:Mew ex:`: 722, `event_prefix:Radiant Charizard:`: 40 |
| C60 | 19.6% | `event_prefix:Mew ex:`: 768, `event_prefix:Radiant Charizard:`: 58 |
| D60 | 14.3% | `event_prefix:Mew ex:`: 726, `event_prefix:Radiant Charizard:`: 83 |

### RC-V2: 1-Fire Hybrid Finisher
*Adds 1 Basic Fire Energy so Radiant Charizard itself can promote and unleash 250 dmg Combustion Blast for 1 Fire at 3+ prizes taken, as an alternate late-game win condition.*

| Matchup | Win Rate | Top Attacks Executed |
| :--- | :---: | :--- |
| T60 | 29.4% | `event_prefix:Mew ex:`: 736, `event_prefix:Radiant Charizard:`: 21 |
| HEDRICK | 26.2% | `event_prefix:Mew ex:`: 655, `event_prefix:Radiant Charizard:`: 21 |
| C60 | 17.7% | `event_prefix:Mew ex:`: 703, `event_prefix:Radiant Charizard:`: 22 |
| D60 | 11.4% | `event_prefix:Mew ex:`: 698, `event_prefix:Radiant Charizard:`: 46 |
