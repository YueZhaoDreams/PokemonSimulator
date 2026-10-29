"""Mill's Sleepy Voice. The benefit rule is Doll's; the attacks are Mill's.

Printed text (Cosmic Eclipse 168): once during your turn, before your attack,
you may flip a coin. If heads, your opponent's Active Pokémon is now Asleep.
If you use this Ability, your turn ends. The sentence does not say the Active
Spot, so a Benched copy can use it.

Undersea Tunnel, Playground, Sleepy Lost, and Eeeeeeek stay ahead of the coin.
The coin replaces that attack only when the hit ignores effects on the Active,
as Demolish does. A turn that cannot attack still flips when their hit would
land. One copy is benched where Cleffa would be safe. Level Ball still takes
Wiglett or Wugtrio while that piece is only in the deck.
"""

from __future__ import annotations

from app.engine.doll import wants_sleepy_voice as benefit_rule
from app.engine.effects import parse_ability_effects

_LINE = ("wiglett", "wugtrio")


def is_sleepy_voice(card) -> bool:
    return any(
        eff.get("kind") == "sleepy_voice"
        for abi in (card.abilities or [])
        for eff in parse_ability_effects(abi.text or "")
    )


def list_has_sleepy(player) -> bool:
    return any(is_sleepy_voice(card) for card in player.cards if card.name.lower() == "igglybuff")


def _hand_sleepy(player) -> list:
    return [player.card(i) for i in player.hand if is_sleepy_voice(player.card(i))]


def wants_in_play(game, player, card) -> bool:
    """One body. The same matches that leave Cleffa in the deck leave this there too.

    A copy already in hand is that body. Poffin does not bench a second one.
    The hand copy itself still enters play.
    """
    if not is_sleepy_voice(card):
        return False
    if game._count_named_in_play(player, "Igglybuff") >= 1:
        return False
    if not game._mill_cleffa_safe(player):
        return False
    in_hand = _hand_sleepy(player)
    if in_hand and all(id(held) != id(card) for held in in_hand):
        return False
    return True


def wants_search(game, player) -> bool:
    """Level Ball and Playground look for a copy only while none is in hand or in play."""
    if game._count_named_in_play(player, "Igglybuff") >= 1:
        return False
    if _hand_sleepy(player):
        return False
    return game._mill_cleffa_safe(player)


def bench_rank(game, player, card) -> tuple[int, int] | None:
    """After Manaphy and before Playground when Demolish ignores the wall.

    Every other match benches it after the one Sweet Sleeping Face.
    """
    if not is_sleepy_voice(card):
        return None
    if game._foe_strat_name(player) == "demolish" and game._mill_cleffa_safe(player):
        return (0, 1)
    return (1, 3)


def starter_score(card) -> float | None:
    """The coin works from the Bench. Wiglett and the wall still lead."""
    if is_sleepy_voice(card):
        return 80.0
    return None


def place_in_search(prefer: list[str], game, me) -> list[str]:
    """Demolish searches the coin after the first line card and before the wall.

    Other matches take it after the pieces already listed. A list with no
    Sleepy Voice print is unchanged.
    """
    if not list_has_sleepy(me) or not wants_search(game, me):
        return prefer
    names = {me.card(mon.card_i).name.lower() for mon in me.in_play()}
    names |= {me.card(i).name.lower() for i in me.hand}
    if "igglybuff" in names:
        return prefer
    out = list(prefer)
    if game._foe_strat_name(me) == "demolish":
        at = 0
        for index, name in enumerate(out):
            if name.lower() in _LINE:
                at = index + 1
                break
        out.insert(at, "Igglybuff")
        return out
    out.append("Igglybuff")
    return out


def level_ball_skip(me) -> set[str]:
    """Poffin benches Manaphy and Cleffa. This search keeps the line.

    Sleepy Voice waits while Wiglett or Wugtrio is still only in the deck.
    """
    skip = {"manaphy", "cleffa"}
    if not list_has_sleepy(me):
        return skip
    have = {me.card(mon.card_i).name.lower() for mon in me.in_play()}
    have |= {me.card(i).name.lower() for i in me.hand}
    deck = {me.card(i).name.lower() for i in me.deck}
    if any(name not in have and name in deck for name in _LINE):
        skip.add("igglybuff")
    return skip


def bench_score(game, me, card) -> float | None:
    """Poffin order for the Sleepy Voice print.

    Demolish takes it ahead of Playground. The first Wiglett is scored above
    this. Other matches take it after the one face.
    """
    if not wants_in_play(game, me, card):
        return None
    if any(me.card(i).name.lower() == "igglybuff" for i in me.hand):
        return None
    if game._foe_strat_name(me) == "demolish":
        return 93
    return 55


def first_wiglett_score(game, me) -> float | None:
    """Against Demolish the first Wiglett stays ahead of the coin on Poffin."""
    if game._foe_strat_name(me) != "demolish" or not list_has_sleepy(me):
        return None
    if game._count_named_in_play(me, "Igglybuff") >= 1:
        return None
    if any(is_sleepy_voice(me.card(i)) for i in me.hand):
        return None
    return 97


def _usable_attack(game, me, foe):
    """The attack Mill would use. None when this turn cannot attack."""
    if not me.active or not foe.active or not game._mill_can_attack_turn(me):
        return None
    from app.engine.game import ST_ASLEEP, ST_PARALYZED

    if me.active.status & (ST_ASLEEP | ST_PARALYZED):
        return None
    who = "a" if me.name == "A" else "b"
    return game._choose_attack(me, foe, game.strats[who])


def wants_sleepy_voice(game, me, foe) -> bool:
    """Doll's benefit rule, with Mill's attack in place of Doll's chooser."""
    return benefit_rule(game, me, foe, attack=_usable_attack(game, me, foe))
