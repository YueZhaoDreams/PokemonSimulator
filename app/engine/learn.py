from __future__ import annotations

from collections import Counter
from typing import Any

from app.engine.models import Card


def learn_from_games(games: list[Any], cards_a: list[Card], cards_b: list[Card]) -> dict[str, Any]:
    n = len(games) or 1
    wins_a = sum(1 for g in games if g.winner == "a")
    wins_b = sum(1 for g in games if g.winner == "b")
    ties = sum(1 for g in games if g.winner == "tie")
    reasons = Counter(g.reason for g in games)
    first_wins = Counter()
    for g in games:
        if g.winner in {"a", "b"}:
            first_wins["first" if g.winner == g.first_player else "second"] += 1

    events = Counter()
    for g in games:
        events.update(g.events)

    def card_lift(side: str) -> list[dict[str, Any]]:
        names = cards_a if side == "a" else cards_b
        unique = list(dict.fromkeys(c.name for c in names))
        rows = []
        for name in unique:
            with_card = [g for g in games if name in (g.opening_a if side == "a" else g.opening_b)]
            prized = [g for g in games if name in (g.prized_a if side == "a" else g.prized_b)]
            if not with_card:
                continue
            win_with = sum(1 for g in with_card if g.winner == side) / len(with_card)
            win_prized = (
                sum(1 for g in prized if g.winner == side) / len(prized) if prized else None
            )
            rows.append(
                {
                    "card": name,
                    "opening_rate": len(with_card) / n,
                    "win_rate_in_opening": win_with,
                    "win_rate_when_prized": win_prized,
                    "prized_rate": len(prized) / n,
                }
            )
        rows.sort(key=lambda r: r["win_rate_in_opening"], reverse=True)
        return rows[:12]

    paralyze = {k: v for k, v in events.items() if k.startswith("status:") and "paralyzed" in k}
    insights = []
    win_rate_a = wins_a / n
    if win_rate_a > 0.6:
        insights.append(f"Deck A won {win_rate_a:.0%} of games — it is currently the stronger set.")
    elif win_rate_a < 0.4:
        insights.append(f"Deck B won {wins_b / n:.0%} of games — Deck A needs more consistency or a better attacker.")
    else:
        insights.append(f"The matchup is close ({win_rate_a:.0%} for A). Family play should stay fun.")

    if events.get("saw_play:Dondozo") or events.get("tutor:Dondozo"):
        saw = sum(1 for g in games if any(k.startswith("saw_play:Dondozo") for k in g.events))
        tutored = sum(1 for g in games if any(k.startswith("tutor:Dondozo") for k in g.events))
        prized_open = sum(1 for g in games if "Dondozo" in g.prized_a)
        insights.append(
            f"Dondozo reached play in {saw / n:.0%} of games "
            f"(tutored from deck in {tutored / n:.0%}; started in prizes in {prized_open / n:.0%})."
        )

    if events.get("pokemon_as_energy"):
        insights.append(
            f"Family energy rule fired {events['pokemon_as_energy'] / n:.1f} times per game on average — "
            "Pokémon were regularly spent as Basic Energy."
        )

    if paralyze:
        total_para = events.get("status:paralyzed", 0)
        insights.append(
            f"Paralysis landed {total_para / n:.2f} times per game. "
            "Status is a real lever in this format because 3 prizes end the game quickly."
        )

    avg_turns = sum(g.turns for g in games) / n
    insights.append(f"Games lasted {avg_turns:.1f} turns on average with {sum(g.mulligans_a + g.mulligans_b for g in games) / n:.2f} mulligans per game.")

    top_kos = [(k.split(":", 1)[1], v) for k, v in events.items() if k.startswith("ko:")]
    top_kos.sort(key=lambda kv: kv[1], reverse=True)
    if top_kos:
        insights.append("Most common Knock Outs: " + ", ".join(f"{n} ({c})" for n, c in top_kos[:5]) + ".")

    pikachu_para = sum(v for k, v in events.items() if "Pikachu" in k and "Dondozo" in k and k.startswith("status:") and "paralyzed" in k)
    pikachu_fail = sum(
        v
        for k, v in events.items()
        if k.startswith("status_fail:Pikachu:Dondozo:paralyzed")
    )
    games_with_combo = sum(
        1
        for g in games
        if any("Pikachu" in k and "Dondozo" in k and "paralyzed" in k and k.startswith("status:") for k in g.events)
    )
    combo = None
    if pikachu_para or pikachu_fail:
        attempts = pikachu_para + pikachu_fail
        combo = {
            "attacker": "Pikachu",
            "defender": "Dondozo",
            "status": "paralyzed",
            "successes": pikachu_para,
            "failures": pikachu_fail,
            "games": n,
            "games_with_success": games_with_combo,
            "p_games_with_success": games_with_combo / n,
            "p_landed_per_game": pikachu_para / n,
            "p_attempted_per_game": attempts / n,
        }
        insights.append(
            f"Pikachu paralyzed Dondozo in {games_with_combo / n:.1%} of games "
            f"({pikachu_para / n:.2f} successful shocks per game; coin-flip misses {pikachu_fail})."
        )

    return {
        "win_rate_a": win_rate_a,
        "win_rate_b": wins_b / n,
        "tie_rate": ties / n,
        "avg_turns": avg_turns,
        "reasons": dict(reasons),
        "first_player_edge": {
            "wins_going_first": first_wins.get("first", 0) / n,
            "wins_going_second": first_wins.get("second", 0) / n,
        },
        "card_impact_a": card_lift("a"),
        "card_impact_b": card_lift("b"),
        "status": {
            "paralyzed": events.get("status:paralyzed", 0) / n,
            "poisoned": events.get("status:poisoned", 0) / n,
            "burned": events.get("status:burned", 0) / n,
            "pokemon_as_energy_per_game": events.get("pokemon_as_energy", 0) / n,
        },
        "combo": combo,
        "ace_access": {
            "dondozo_saw_play": sum(1 for g in games if any(k.startswith("saw_play:Dondozo") for k in g.events)) / n,
            "dondozo_tutored": sum(1 for g in games if any(k.startswith("tutor:Dondozo") for k in g.events)) / n,
            "dondozo_opening_prize": sum(1 for g in games if "Dondozo" in g.prized_a) / n,
            "tutor_poke_ball": events.get("tutor:Dondozo:poke ball", 0) / n,
            "tutor_ultra_ball": events.get("tutor:Dondozo:ultra ball", 0) / n,
            "tutor_energy_search": events.get("tutor:Dondozo:energy search", 0) / n,
        },
        "insights": insights,
        "top_knockouts": top_kos[:8],
        "event_totals": dict(events.most_common(40)),
    }
