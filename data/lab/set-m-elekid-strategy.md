# Set M with Elekid: the play, written before the search

Elekid (Paradox Rift 59) is a Basic Lightning Pokémon with 30 HP and a Retreat Cost of 0. Its only attack,
Crackling Shot, costs no Energy:

> This attack does 30 damage to 1 of your opponent's Pokémon. (Don't apply Weakness and Resistance for Benched Pokémon.)

The list this search starts from is the locked Set M: 3 Mew ex, 2 Mime Jr., 4 Igglybuff, 4 Budew, 1 Manaphy,
4 Buddy-Buddy Poffin, 4 Nest Ball, 1 Junk Arm, 1 Night Stretcher, 2 Rescue Carrier, 4 Battle Cage, 3 Sky Field,
2 Bravery Charm, 1 Bursting Balloon, 1 Hero's Cape, 3 Max Potion, 4 Arven, 4 Iono, 2 Professor's Research,
4 Team Rocket's Petrel, 3 Crushing Hammer, 1 Counter Catcher, 2 Spiky Energy. No Ultra Ball, no Penny, no Boss's Orders.

Elekid does two jobs there, and the second one is rare.

1. **A 30 HP body.** Bouncy Circle is 30 damage for each of your Benched Pokémon with a maximum HP of 30.
   An Elekid on the Bench is +30 for the Active Igglybuff, and for Mew ex copying it. Buddy-Buddy Poffin, Nest Ball,
   Night Stretcher and Rescue Carrier can find it, next to Igglybuff, Mime Jr. and Budew.
2. **A finisher, and only an extreme one.** Crackling Shot is how this list takes a Knock Out it would otherwise miss.
   It is not a routine attack. A Benched Pokémon at 30 HP or less is not, by itself, a reason to use it.

## When Crackling Shot is used

The Knock Out has to be extreme, and it has to be better than the hit the Active attack already has:

- **It wins the game.** The prizes from that Knock Out are at least the prizes still needed.
  A 1-prize Knock Out counts here, because it is the last one.
- **Or it takes at least 2 prizes the Active attack cannot take this turn.** The usual case is a Benched ex
  with 30 HP or less left, while Bouncy Circle does not Knock Out the Active Pokémon for that many prizes.

A 1-prize Knock Out that leaves prizes still to take is not extreme. Crackling Shot is not chosen, and Elekid
does not go Active for it. Bouncy Circle, or whatever the Active attack already is, is used instead.
If Crackling Shot is the only attack and the Knock Out is not extreme, the Pokémon does not attack.

When the shot is used, it takes the Knock Out with the most prizes. On a tie it takes the Active Pokémon
(the opponent must promote), then the Pokémon with more Energy attached, then the one with less HP left.
Weakness and Resistance apply to the Active Pokémon only, as printed. A Benched Pokémon that a shield protects
(Wave Veil, Spherical Shield, Flower Curtain) is not a target.

## Who goes Active

All of these Pokémon retreat for 0, so the choice is free each turn.

- **Mew ex Active (default).** It keeps every option: Bouncy Circle, Mimed Games, and Crackling Shot copied from the Bench.
  Mew ex is also where Bravery Charm, Hero's Cape and Max Potion pay off. When the shot is the extreme Knock Out,
  Mew ex is the one that uses it. Elekid stays on the Bench.
- **Elekid Active, only when Mew ex cannot use the attack and the Knock Out is extreme.** Memory Helix is off under a
  Rule Box lock (Iron Thorns ex), and it is off when no Mew ex can hold the Active Spot this turn. Then Elekid
  goes Active and takes that Knock Out. If the Knock Out is not extreme, the usual Baby stays Active (Budew, then
  the Baby that out-damages Itchy Pollen).
- **When Bouncy Circle takes the same prizes or more, Mew ex stays and uses Bouncy Circle.** A Knock Out on the
  Active Pokémon also makes the opponent promote, so a tie goes to that hit.

## Boss's Orders and Counter Catcher

An extreme Knock Out that Crackling Shot takes counts as already taken when a gust is weighed. A gust is played only
when the pulled Pokémon's Knock Out gives strictly more prizes this turn, the same rule as `set-m-gust-search.md`.
A 1-prize Knock Out that is not extreme does not count, so Boss's Orders and Counter Catcher are still played for a
bigger Knock Out.

The locked list has Counter Catcher and no Boss's Orders. Team Rocket's Petrel can still search Boss's Orders and
hold it for the next turn. That play is unchanged.

## What the engine does (so the search measures the play above)

- Elekid is searched with the other Babies (Buddy-Buddy Poffin, Nest Ball) only when the 60 holds one,
  starts a game after Mew ex, Budew and Cleffa and before Igglybuff, and is returned by Night Stretcher and Rescue Carrier.
- `_crackling_is_extreme` is the rule above. `_choose_attack` gives Crackling Shot the prize bonus only then, and drops
  the attack otherwise. `_snipe_holder` moves Elekid forward only when Mew ex cannot make that same extreme Knock Out.
  `_mew_strike_prizes` counts an extreme Knock Out and ignores the rest, so `_mew_gust_plan` is unchanged by a
  1-prize snipe.
- `_damage_one_pokemon` uses the prize picker only for Crackling Shot. Cruel Arrow, including a Mimed Games copy, keeps
  the target it had before Elekid: the Active Pokémon when that hit Knock Out, otherwise the Benched Pokémon with
  the least HP left.
- A list with no Elekid takes none of the finisher paths. The "1 of your opponent's Pokémon" sentence is still one hit,
  not two. That parse was already in the previous Elekid report and is not measured again here.

## How the search computes it

Greedy, one card per step, from the locked Set M above. Each step adds one more Elekid and tries every other card
name as the cut, screened on 300 games per foe, the best six confirmed on 1000. Elekid is forced in up to four copies
(the 4-of-a-name limit), even past the first step that does not gain, so the report can say how many copies are best.
Weights are frozen from this locked list on the selection seed. Each list on the path is then run on two fresh seeds,
and the best list on the fresh seeds goes to the clean seed. Same six foes and the same seeds as the earlier Set M reports.
