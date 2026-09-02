# Strategy: condition → decision

Cards plugin into **Game**. A **Player** sits at that game and plays with a **Strategy**. Strategy is the only chooser. It answers **game-step** decisions and **card-declared** decisions through one interface: given a condition (observation + legal set), return a legal choice.

This is not a class hierarchy (`Thrifty`, `Party`, `AggroDondozo`). Those names in v1 mixed card parameters into the policy. v2 Strategy is `decide(ctx) → choice`.

Related: [engine v2](./engine-v2-design.md), [spec](./spec.md), [survey](./set-card-survey.md).

## 1. Four objects

```
Game (kernel)          legality, turn loop, hook dispatch
  plugins: Card[]      printed program, params, declared decision ids
  seats: Player[]
           strategy: Strategy    decide(ctx) → legal choice
```

| Object | Role | Does not |
| --- | --- | --- |
| Game | Ask for a decision; apply the returned legal action | Pick Swallow-Up counts, pick Boss target, decide whether to “go for it” |
| Card | Plug in effects; **declare** decision ids the print left open | Know if this household is aggro or mill |
| Player | Seat: deck, prizes, hand. Holds one Strategy | Contain `if name == Dondozo` |
| Strategy | Map condition → decision for **every** ask this turn | Own `look: 5` or any printed param |

**Player vs Combo Cub chat.** The in-game Player is the Monte Carlo agent. Product-chat Cursor is outside the match: it may overlay Strategy weights and named policies. It is not `Game.players[0]`.

## 2. One decide(), two sources

Every ask is the same record:

```
DecisionContext {
  id:     "game.attack" | "game.attach" | "swallow.attach" | "distribute_counters" | ...
  source: "game_step" | "card"
  legal:  Action[]          # kernel + card already filtered
  observe: Observation      # public facts, read-only
}

Strategy.decide(ctx) -> Action   # must be in ctx.legal
```

- **Game-step ids** (always exist): `game.setup_active`, `game.attach`, `game.play_trainer`, `game.evolve`, `game.attack_or_pass`, `game.retreat`, `game.boss` if Boss is being resolved as a trainer program, etc.
- **Card ids** (exist only when that printing’s program runs): hook-scoped, e.g. `look_then_attach.how_many`, `distribute_counters`, `move_energy`, `look.which`. A new Dondozo printing reuses `look_then_attach.how_many`; Strategy does not get a new method.

The kernel never special-cases “this decision came from a card.” Cards only add ids to the stream. Strategy does not care whether the hole was printed as “any number” or “which attack to use.”

If Strategy returns illegal or nothing, fail closed: kernel’s documented default (usually “do nothing / take 0 / pass”), never invent an extra look.

## 3. Condition is Observation, not the live Game

Do not hand Strategy a mutable `Game` to patch. Hand a typed snapshot. That is the access-control boundary for lab overlays too.

Minimum observation (household is enough to start; add fields as hooks need them):

| Field | Why it exists |
| --- | --- |
| `prizes_me`, `prizes_opp` | Prize race, Boss, Unfair Stamp |
| `deck_me`, `deck_opp` | Thin deck, Orthworm bonus, mill, Hop |
| `can_pay(attack)` | Swallow / attach / whether Hydro is live |
| `can_ko_active`, `can_take_last_prizes_this_turn` | “Go for it” |
| `exposed_if_attack` | Attack then die to the counter |
| `hand_attachable_energy` | Swallow one fewer |
| `in_play` roles from **card programs** (closer, mill, item-lock, wall) | Deck-specific without name tables |
| `decision payload` | Swallow candidates, bench HP list, looked cards |

Unknown fields in an overlay condition fail closed (ignore that clause). Strategy must not read `app/engine/game.py` or other players’ private RNG.

## 4. Do not subclass Aggro / Mill by deck

Aggro and mill are **objectives**, not Python classes. The same Strategy object plays Dondozo Hydro and Floragato slash. What changes is:

1. Which **legal actions** exist (cards plugged into this Game).
2. Which **observation fields** light up (a mill attack in play, a 180 damage closer, an Orthworm `deck_count_bonus`).
3. The **weights** on objectives.

Objectives (weights, sum not required to be 1):

| Objective | Reads as | Aggro leans | Grind / mill leans |
| --- | --- | --- | --- |
| `win_now` | Take last prize(s) this turn even if the board is ugly | high | low unless it also closes |
| `equity` | Still likely to win if the game continues | medium | high |
| `clock` | Opponent’s deck / prize clock, not yours | low unless mill cards | high if mill program is in play |
| `setup` | Evolve, attach, bench the closer | early-game | early-game |
| `self_preserve` | Don’t deck out, don’t Hop-mill a 7-card library, don’t strip Swallow when hand already has Energy | low–medium | high when thin |

“拼一把可能立刻赢，不拼慢慢打输的概率更高但输得慢” is not a new kind of effect. It is:

```
if observe.can_take_last_prizes_this_turn:
    score(attack) += w.win_now * 1
if observe.exposed_if_attack:
    score(attack) -= w.self_preserve * danger
if not can_win_now:
    score(pass_or_setup) += w.equity * continue_value
```

Pick `argmax` among `ctx.legal`. Log the id, the chosen action, and the top features. Monte Carlo then tells you whether that policy’s win rate matches the story.

v1 `thrifty` / `party` / `phantom` are **preset weight bundles + a few when-clauses**, not extra engine code. Deck identity does not need `if strat.name == "slash"`. Floragato aggro is high `win_now` plus a closer attack of 90 sitting on the card. Dragapult mill-adjacent prize spread is `distribute_counters` answered by the same scorer (dump on the KO vs spread to strip belts — that is still `decide`).

## 5. Fingerprint the plugged-in cards, don’t name them

At match start, Strategy may scan each Card program (not English names) for tags the hooks already expose: `high_damage`, `mill_opponent`, `deck_count_bonus`, `item_lock`, `prevent_basic_damage`, `swallow_energy`. Those tags adjust default weights and which observation fields matter.

- Set A Dondozo: closer tag + swallow decision id → attach policy uses `deck_me` and `hand_attachable_energy`.
- Set T Dragapult: `distribute_counters` + prize closer → spreading vs concentrating is `win_now` vs `equity`.
- Hop as mill vs Hop as draw: same trainer program; Strategy sees `deck_me` and whether a mill tag or Orthworm bonus is in play.

If a new printing only uses existing AST kinds, tags are derived automatically. A new *kind* is a new hook on trunk. Strategy does not grow an `if "Litwick"`.

## 6. Overlay (what product chat may change)

Safe Strategy overlay (DB / simulate payload), not a `.py`:

- Objective weights (`win_now`, `equity`, `clock`, `setup`, `self_preserve`).
- When-clauses: `if <predicate on Observation> then prefer <action pattern>` (bounded list, fail closed).
- Per-decision-id hints bound to **hook-level** ids (`look_then_attach.how_many`), implemented by scoring **action features** (`attach_count`, `target_remaining_hp`), not a growing enum in git.

Forbidden: customer Python as Strategy (until a gated sandbox, and even then it may only pass JSON overlays into `run_simulation`). Forbidden: overlay that sets card params above print. Forbidden: new decision ids or hook names the trunk did not publish. Forbidden: mutating `Game` / `STRATEGY_LIBRARY`.

Shipped presets (`thrifty`, `carnival`) become named weight files in trunk. Lab cells overlay weights. Fight picks a preset or a saved overlay.

## 7. Worked lines

**Go for it (Set A vs a 1-prize wall).**  
`game.attack`: legal = {Hydro Splash, Swallow-Up, pass}. `can_take_last_prizes_this_turn` true, `exposed_if_attack` true. High `win_now` picks Hydro. High `self_preserve` may Swallow or pass. Same Strategy class, different weights.

**Swallow (card id).**  
`swallow.attach`: legal = subsets of looked Basic Energy. Observation includes `deck_me`, `hand_attachable_energy`, `can_pay(Hydro Splash)`. Policy: if deck thin → smaller subset; if hand already has Energy → one fewer. Print still looked 5.

**Mill / thin (Set T Unfair Stamp vs Set A Hop).**  
`game.play_trainer`: legal includes Hop or not. If `deck_me` is 6 and no mill tag, `self_preserve` skips Hop. If opponent deck is 2 and a mill attack is legal, `clock` plays the mill. Different decks, same decide().

## 8. Relation to v1 StrategySpec

Keep a thin preset layer for Fight dropdowns. Delete fields that were card params (`swallow_look`). Move `_pick_trainer` name scores into `decide(game.play_trainer)` using Observation. Move `_resolve_trainer` effects onto Card programs. Kernel only asks and applies.

## 9. Invariants

- Strategy never invents an action outside `ctx.legal`.
- Strategy never writes printed params.
- Game-step and card holes share `DecisionContext`.
- Aggro / mill / “go for it” are weights + observation, not subclasses per deck.
- Every `decide` is logged (id, legal size, choice, winning objective).
