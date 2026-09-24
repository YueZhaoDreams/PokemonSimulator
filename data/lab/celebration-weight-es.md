# Celebration weight self-play pilot

Date: 2026-09-23
Rule: s60 (60 cards, 4-of, 6 prizes)
Script: `data/lab/celebration_weight_es.py`
Raw: `data/lab/celebration-weight-es.json`
Elapsed: 848s on 15 processes

Question: while every `strat.name == "celebration"` branch in `game.py` still decides the play, how much win rate is left in the seven `StrategySpec` floats alone?

Row is G30 (Ambipom PAR Hand Fling, strategy `celebration`) as player A. Foes are the household 60s from `data/lab/gholdengo-30-array.py`: C60 `party`, T60 `phantom`, Hedrick `phantom`, UNL `phantom`, D60 `demolish`, S60 `slash`, Carpet Set G `carnival`. First player random. Objective is the unweighted mean win rate over the seven foes.

## Search

- (mu/mu_w, lambda) evolution strategy on [0, 1]^7: lambda 12, mu 4, step 0.2 decaying by 0.9 per generation to a floor of 0.03, 20 generations.
- 500 games per foe per candidate. Every candidate in a generation, and the defaults, play the same seeds (seed 20260923 + 1000 × generation + foe index).
- Validation: 3,000 games per foe on held-out seed 20260924 for the defaults, the final mean, and the best single candidate seen in training.

Parameters: `prefer_damage`, `prefer_status`, `bench_fill`, `evolve_asap`, `attach_pokemon_as_energy`, `item_spend`, `self_preserve`. The last two have no effect on this deck under s60: Pokémon are not Energy, and `self_preserve` is only read by the look-then-attach decision, which this list never takes.

## Validation (held-out seeds, 3,000 games per foe)

| Variant | C60 | T60 | Hedrick | UNL | D60 | S60 | G | Mean | Δ vs defaults (95% CI) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| **defaults** | 4.2% | 5.6% | 6.2% | 21.1% | 4.6% | 29.4% | 19.4% | **12.9%** | — |
| final mean | 4.1% | 5.7% | 7.2% | 19.7% | 3.9% | 26.5% | 19.3% | 12.3% | −0.6% [−1.2%, +0.0%] |
| best seen | 4.9% | 5.8% | 6.8% | 19.6% | 4.0% | 28.2% | 18.1% | 12.5% | −0.4% [−1.1%, +0.2%] |

Tuned values:

| Param | defaults | final mean | best seen |
| --- | ---: | ---: | ---: |
| prefer_damage | 0.20 | 0.48 | 0.34 |
| prefer_status | 0.00 | 0.11 | 0.29 |
| bench_fill | 0.00 | 0.18 | 0.25 |
| evolve_asap | 1.00 | 0.94 | 0.94 |
| attach_pokemon_as_energy | 0.00 | 0.44 | 0.29 |
| item_spend | 1.00 | 0.92 | 0.80 |
| self_preserve | 0.45 | 0.43 | 0.46 |

## Reading

Neither tuned vector beats the defaults on held-out seeds. Both intervals include zero or sit just below it.

In training, the best of 12 candidates beat the defaults by −0.2 to +2.1 points per generation (median +0.8), while the median candidate stayed near 0 (between −1.2 and +0.9 points). With 500 games per foe, the difference between one candidate's mean and the defaults has a standard error of about 0.8 points; the best of 12 such draws lands near +1.2 by selection alone. The search followed noise.

`attach_pokemon_as_energy` has no effect on this deck and drifted from 0 to 0.44. That is what a flat direction looks like.

The deck's choices live in the `celebration` name branches (bench caps, bench order, trainer order). The floats sit on generic fallbacks. This is the measured case for moving those choices into plan data before tuning (`docs/epics/deck-as-fate/combo-design.md`, section 5).

G here is 19.4% against 30.4% in the 2026-09-15 array. Carpet Set G's list has been relocked since (#123, #126), and the seed differs.

## Lock

No change. `celebration` keeps its defaults.
