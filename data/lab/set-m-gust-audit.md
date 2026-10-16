# Set M gust audit: Boss's Orders and Counter Catcher plays

The locked Set M (`SET_M60_NAMES`: one Boss's Orders, two Counter Catcher) against the six foes, 300 games per foe on seed `20261007`. Every play is checked at the moment it is made and again at the end of the turn. `before` is the engine before the gust fix, `after` is the engine after it. Both columns come from `data/lab/set_m_gust_audit.py`.

| Card | Measure | Before | After |
| :--- | :--- | ---: | ---: |
| Boss's Orders | Plays per game | 0.268 | 0.126 |
| Boss's Orders | Plays with no prize that turn | 36% | 2% |
| Boss's Orders | Pulled Pokémon Knocked Out that turn | 63% | 98% |
| Boss's Orders | Active could already be Knocked Out | 37% | 6% |
| Boss's Orders | Active could be Knocked Out, pull cannot or takes fewer prizes | 15% | 0% |
| Boss's Orders | Prizes taken that turn, per play | 0.69 | 1.11 |
| Counter Catcher | Plays per game | 0.087 | 0.030 |
| Counter Catcher | Plays with no prize that turn | 29% | 0% |
| Counter Catcher | Pulled Pokémon Knocked Out that turn | 61% | 98% |
| Counter Catcher | Active could already be Knocked Out | 36% | 6% |
| Counter Catcher | Active could be Knocked Out, pull cannot or takes fewer prizes | 23% | 0% |
| Counter Catcher | Prizes taken that turn, per play | 0.83 | 1.30 |

## Boss's Orders by foe

| Foe | Plays per game (before) | (after) | No prize that turn (before) | (after) |
| :--- | ---: | ---: | ---: | ---: |
| t60 | 0.253 | 0.147 | 42% | 0% |
| hedrick | 0.317 | 0.163 | 18% | 4% |
| c60 | 0.397 | 0.190 | 29% | 2% |
| d60 | 0.000 | 0.000 | — | — |
| thorns | 0.220 | 0.010 | 92% | 0% |
| starmie | 0.423 | 0.247 | 25% | 1% |

## What was wrong

- Boss's Orders scored +8 whenever the opponent had a Bench, level with or above Professor's Research and above Arven, so it was played before the draw and used the Supporter for the turn even when the pull changed nothing.
- Counter Catcher scored +10 whenever Set M was behind on prizes, again with no check that the pull helped.
- The pull was the lowest remaining HP on the Bench, not the Knock Out that takes the most prizes.
- The only check, "this gust wins the game", looked at every Benched Pokémon, but the pull took only the lowest-HP one.
- That check used the Active Spot's own attack, so a Bench Pokémon the Active could retreat into never counted.

## The fix

Set M plays Boss's Orders or Counter Catcher only when the Pokémon it pulls can be Knocked Out this turn for more prizes than the Active Spot already gives, counting a Benched attacker the Active can retreat for. The pull is that Knock Out, most prizes first, then most attached Energy. Counter Catcher still needs more Prize cards remaining than the opponent, as printed, and goes ahead of Boss's Orders so the Supporter stays in hand (`tests/test_mew_gust.py`).
