# Set M with Elekid: the play, written before the search

Elekid (Paradox Rift 59) is a Basic Lightning Pokémon with 30 HP and a Retreat Cost of 0. Its only attack,
Crackling Shot, costs no Energy:

> This attack does 30 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)

It does two jobs in the Set M list (Mew ex, 30 HP Babies, Bouncy Circle).

1. **A fifth kind of 30 HP body.** Bouncy Circle is 30 damage for each of your Benched Pokémon with a maximum HP of 30,
   so every Elekid on the Bench is +30 for the Active Igglybuff, and for Mew ex copying it. Elekid is one more card
   that Buddy-Buddy Poffin, Nest Ball, Night Stretcher and Rescue Carrier return, next to Igglybuff, Mime Jr. and Budew.
2. **A free hit on anything the opponent has in play.** When a Pokémon has 30 HP or less left, Crackling Shot takes it
   without a gust. A Pokémon on the opponent's Bench is out of reach for Bouncy Circle, which only hits the Active
   Pokémon, so this is the one hit in the list that reaches the Bench. Boss's Orders and Counter Catcher exist for the same
   reason, and each costs a card and a turn of Supporter or Item use.

Mew ex's Memory Helix lets it use the attacks of any Benched Pokémon, so Mew ex can use Crackling Shot as well.
That is why the Active Spot is a decision, not a rule.

## Who goes Active

All of these Pokémon retreat for 0, so the choice is free each turn.

- **Mew ex Active (default).** It keeps every option: Bouncy Circle, Mimed Games, Crackling Shot from the Bench.
  Mew ex is also where Bravery Charm, Hero's Cape and Max Potion pay off.
- **Elekid Active, only when Crackling Shot takes more prizes this turn than any other hit.** The case is a Benched
  ex (or a Benched Pokémon that gives more prizes than the Active one) with 30 HP or less left, while the opponent's
  Active Pokémon cannot be Knocked Out the same way. Mew ex has the same Crackling Shot, but a 30 HP Pokémon in front
  gives the opponent a 1-prize Knock Out in place of a 2-prize one. Mew ex waits on the Bench for the next turn.
- **When Bouncy Circle takes the same prizes or more, Mew ex stays.** A Knock Out on the Active Pokémon also makes the
  opponent promote a new attacker, so a tie goes to the Active Knock Out.
- **Under Iron Thorns ex (Rule Box Abilities off, Memory Helix off),** Mew ex cannot copy anything. A Baby stays Active as
  before, and Elekid is that Baby when its hit is the Knock Out.

## Which Pokémon Crackling Shot hits

A hit that Knocks Out takes the Knock Out with the most prizes. On a tie it takes the Active Pokémon (the opponent
must promote), then the Pokémon with more Energy attached, then the one with less HP left. Weakness and Resistance
apply to the Active Pokémon only, as printed. A Benched Pokémon that a shield protects (Wave Veil, Spherical Shield, Flower Curtain)
is not a target, so the hit goes to the Active Pokémon. With no Knock Out available it does what Cruel Arrow did:
the Active Pokémon if there is no Bench, and otherwise the Benched Pokémon with the least HP left.

## Boss's Orders and Counter Catcher

The Knock Out that Crackling Shot takes counts as already taken when a gust is weighed. A gust is played only when
the pulled Pokémon's Knock Out gives strictly more prizes this turn than the best hit already does, and that is the
rule from `set-m-gust-search.md`. With Elekid on the Bench, a Benched Pokémon at 30 HP or less no longer needs a gust.

## What the engine does (so the search measures the play above)

- Elekid is searched with the other Babies (Buddy-Buddy Poffin, Nest Ball, Ultra Ball) only when the 60 holds one,
  starts a game after Mew ex, Budew and Cleffa and before Igglybuff, and is returned by Night Stretcher and Rescue Carrier.
- `_snipe_pick` takes the Knock Out with the most prizes. `_mew_strike_prizes` counts it, `_mew_gust_plan` therefore skips a
  gust it covers, `_retreat_baby` moves Elekid forward by the rule above, and `_choose_attack` weighs every Knock Out by its
  prizes so a Benched 2-prize Knock Out beats a 1-prize Active one.
- A list with no Elekid takes none of these paths. The one change that touches every list is the single-target hit
  (Cruel Arrow, and Mew ex's Mimed Games copying it) now taking the Knock Out with the most prizes, and a
  "1 of your opponent's Pokémon" sentence no longer parsing as a second, spread hit. The report runs Set M and the start
  list on the clean seed of `set-m-gust-search.md` to show what those engine changes alone do.

## How the search computes it

Greedy, one card per step, from the best list of `set-m-gust-search.md` (four Sky Field, four Budew, one Counter Catcher).
Each step adds one more Elekid and tries every other card name as the cut, screened on 300 games per foe, the best six
confirmed on 1000. Elekid is forced in up to four copies (the 4-of-a-name limit), even past the first step that does not
gain, so the report can say how many copies are best. Each list on the path is then run on two fresh seeds, and the best
list on the fresh seeds goes to the clean seed. Same six foes, same frozen weights, same seeds as the earlier Set M reports.
