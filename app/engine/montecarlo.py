from __future__ import annotations

import random
import time
import uuid
from datetime import datetime, timezone
from typing import Any

from app.engine.game import play_game
from app.engine.learn import learn_from_games
from app.engine.models import Card, FamilyRules
from app.engine.probability import draw_probability
from app.engine.strategies import StrategySpec


def run_simulation(
    cards_a: list[Card],
    cards_b: list[Card],
    rules: FamilyRules,
    strat_a: StrategySpec,
    strat_b: StrategySpec,
    games: int = 10000,
    seed: int | None = None,
    question: str | None = None,
    queries: list[dict[str, Any]] | None = None,
    deck_a_meta: dict[str, Any] | None = None,
    deck_b_meta: dict[str, Any] | None = None,
    first_player: str | None = None,
) -> dict[str, Any]:
    games = max(1, min(int(games), 25000))
    seed = int(seed if seed is not None else random.randrange(1, 10**9))
    rng = random.Random(seed)
    started = time.perf_counter()
    results = []
    query_hits: dict[str, int] = {}
    sample_traces = []
    if queries is None:
        queries = [
            {"type": "opening_hand_contains", "side": "a", "card": "Dondozo", "key": "dondozo_opening_a"},
            {"type": "event_prefix", "prefix": "saw_play:Dondozo", "key": "dondozo_saw_play"},
            {"type": "event_prefix", "prefix": "tutor:Dondozo", "key": "dondozo_tutored"},
            {"type": "event_prefix", "prefix": "saw_play:Pikachu", "key": "pikachu_saw_play"},
            {"type": "event_prefix", "prefix": "attack:Pikachu:Volt Tackle", "key": "volt_tackle"},
            {
                "type": "status",
                "attacker": "Pikachu",
                "defender": "Dondozo",
                "status": "paralyzed",
                "key": "pikachu_paralyze_dondozo",
            },
        ]

    for i in range(games):
        want_trace = i < 6
        result = play_game(cards_a, cards_b, rules, strat_a, strat_b, rng, trace=want_trace, first=first_player)
        results.append(result)
        _apply_queries(result, queries or [], query_hits)
        if want_trace:
            sample_traces.append(
                {
                    "winner": result.winner,
                    "reason": result.reason,
                    "turns": result.turns,
                    "first_player": result.first_player,
                    "log": result.trace[:80],
                }
            )

    elapsed = time.perf_counter() - started
    learning = learn_from_games(results, cards_a, cards_b)
    names_a = [c.name for c in cards_a]
    names_b = [c.name for c in cards_b]
    extra_probs = {}
    interesting = list(dict.fromkeys(["Dondozo", "Pikachu"] + _mentioned_cards(question or "", names_a + names_b)))
    for name in interesting:
        if name in names_a or name in names_b:
            extra_probs[name] = {
                "deck_a": draw_probability(name, names_a, rules.opening_hand),
                "deck_b": draw_probability(name, names_b, rules.opening_hand),
            }

    wins_a = sum(1 for g in results if g.winner == "a")
    wins_b = sum(1 for g in results if g.winner == "b")
    ties = sum(1 for g in results if g.winner == "tie")
    a_first = [g for g in results if g.first_player == "a"]
    a_second = [g for g in results if g.first_player == "b"]

    def _rate(games, winner):
        return (sum(1 for g in games if g.winner == winner) / len(games)) if games else 0.0

    record = {
        "id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "question": question,
        "elapsed_seconds": round(elapsed, 3),
        "method": {
            "engine": "family-tcg-monte-carlo",
            "games": games,
            "seed": seed,
            "rules": rules.to_dict(),
            "how": (
                f"Shuffled both decks, drew {rules.opening_hand}, mulliganed until a Basic Pokémon, "
                f"set {rules.prize_count} prize cards, drew one card per opponent mulligan, "
                "then played turns under Family Cup rules "
                f"({'Pokémon count as matching Basic Energy' if rules.pokemon_as_energy else 'standard energy only'}"
                f"{'; ex = 2 prizes, Mega ex = 3' if rules.extra_prize_for_ex else ''}). "
                f"Each side used a deterministic-weighted strategy. {games} independent games, seed {seed}."
            ),
        },
        "strategies": {"a": strat_a.to_dict(), "b": strat_b.to_dict()},
        "decks": {
            "a": {**(deck_a_meta or {}), "cards": names_a, "size": len(names_a)},
            "b": {**(deck_b_meta or {}), "cards": names_b, "size": len(names_b)},
        },
        "results": {
            "wins_a": wins_a,
            "wins_b": wins_b,
            "ties": ties,
            "win_rate_a": wins_a / games,
            "win_rate_b": wins_b / games,
            "tie_rate": ties / games,
            "win_rate_a_going_first": _rate(a_first, "a"),
            "win_rate_a_going_second": _rate(a_second, "a"),
            "games_a_first": len(a_first),
            "games_a_second": len(a_second),
            "queries": {k: v / games for k, v in query_hits.items()},
            "query_counts": query_hits,
            "opening_probabilities": extra_probs,
        },
        "sample_games": sample_traces,
        "learning": learning,
    }
    return record


def _apply_queries(result, queries: list[dict[str, Any]], hits: dict[str, int]) -> None:
    opening_a = set(result.opening_a)
    opening_b = set(result.opening_b)
    for q in queries:
        qtype = q.get("type")
        card = q.get("card") or q.get("name")
        key = q.get("key") or f"{qtype}:{card}"
        ok = False
        if qtype == "opening_hand_contains":
            side = q.get("side", "a")
            pool = opening_a if side == "a" else opening_b
            ok = card in pool or (card or "").lower() in {n.lower() for n in pool}
        elif qtype == "status":
            attacker = (q.get("attacker") or "").lower()
            defender = (q.get("defender") or "").lower()
            status = (q.get("status") or "").lower()
            ok = any(
                k.lower().startswith("status:")
                and attacker in k.lower()
                and defender in k.lower()
                and status in k.lower()
                and not k.lower().startswith("status_fail")
                for k in result.events
            )
        elif qtype == "event_prefix":
            prefix = q.get("prefix") or ""
            ok = any(k.startswith(prefix) for k in result.events)
        if ok:
            hits[key] = hits.get(key, 0) + 1


def _mentioned_cards(question: str, names: list[str]) -> list[str]:
    q = question.lower()
    found = []
    for name in dict.fromkeys(names):
        if name.lower() in q:
            found.append(name)
    return found
