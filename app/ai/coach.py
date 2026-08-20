from __future__ import annotations

import json
import re
from typing import Any

from app.ai.llm import LLMNotConfigured, chat_completion, provider_status
from app.ai.tools import TOOL_SCHEMAS, _default_ids, run_tool
from app.db import get_rules, list_decks, save_chat

SYSTEM = """You are the family Pokémon TCG simulator coach.
You help a household play a home-ruled format:
- 30-card decks
- 3 prize cards
- Any Pokémon can be attached as a Basic Energy of its type
- Otherwise follow standard Pokémon TCG

Always use tools for numbers. Never invent a win rate or probability.
After a simulation, explain: how the sim was run, which strategies were used, the results, and what was learned.
Be concrete and short. Name cards. Mention Family Cup energy when it matters.
"""


def ask_coach(message: str, chat_id: str | None = None, history: list[dict] | None = None) -> dict[str, Any]:
    history = list(history or [])
    history.append({"role": "user", "content": message})
    tool_trace: list[dict[str, Any]] = []
    try:
        answer = _llm_loop(history, tool_trace, message)
        used = "llm"
    except LLMNotConfigured:
        answer = _local_coach(message, tool_trace)
        used = "local"
    except Exception as exc:
        answer = _local_coach(message, tool_trace) + f"\n\n(Cloud AI fallback: {exc})"
        used = "local-fallback"

    history.append({"role": "assistant", "content": answer})
    saved = save_chat(history, chat_id=chat_id)
    return {
        "chat_id": saved["id"],
        "answer": answer,
        "messages": saved["messages"],
        "tool_trace": tool_trace,
        "coach": used,
        "provider": provider_status(),
    }


def _llm_loop(history: list[dict], tool_trace: list[dict], question: str) -> str:
    messages = [{"role": "system", "content": SYSTEM}] + history
    for _ in range(4):
        result = chat_completion(messages, TOOL_SCHEMAS)
        calls = result.get("tool_calls") or []
        if not calls:
            return result.get("content") or "I need a bit more context about the two decks."
        messages.append(result.get("raw") or {"role": "assistant", "content": result.get("content"), "tool_calls": calls})
        for call in calls:
            args = _parse_args(call.get("arguments"))
            if "question" not in args:
                args["question"] = question
            _fill_default_decks(args)
            output = run_tool(call["name"], args)
            tool_trace.append({"tool": call["name"], "args": args, "output_preview": _preview(output)})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id"),
                    "name": call["name"],
                    "content": json.dumps(output, default=str)[:12000],
                }
            )
    return "The tools ran, but I could not summarize in time. Check the Lab tab for the simulation record."


def _local_coach(message: str, tool_trace: list[dict]) -> str:
    intent = _intent(message)
    a_id, b_id = _default_ids()
    decks = list_decks()
    rules = get_rules()

    if intent == "probability":
        card = _card_in_text(message, decks) or "Dondozo"
        deck_id = a_id if _name_in_deck(card, a_id) else (b_id if _name_in_deck(card, b_id) else a_id)
        draw = 7
        m = re.search(r"first\s+(\d+)|opening\s+(\d+)|(\d+)\s+cards", message.lower())
        if m:
            draw = int(next(g for g in m.groups() if g))
        args = {"deck_id": deck_id, "card_name": card, "draw": draw}
        result = run_tool("draw_odds", args)
        tool_trace.append({"tool": "draw_odds", "args": args, "output_preview": result})
        p = result.get("p_at_least_one", 0)
        return (
            f"**{card} in the first {draw} cards** of {result.get('deck_size')}-card deck "
            f"({result.get('copies')} cop{'y' if result.get('copies')==1 else 'ies'}): "
            f"**{p:.1%}**.\n\n{result.get('method')}\n\n"
            "This is exact combinatorics, not a guess. Opening hand is drawn before prize cards, "
            f"so with Family Cup's {rules.prize_count} prizes it is still a {draw}-card look at the top."
        )

    if intent == "trade":
        args = {"deck_a_id": a_id, "deck_b_id": b_id, "games": 200}
        result = run_tool("suggest_trades", args)
        tool_trace.append({"tool": "suggest_trades", "args": args, "output_preview": _preview(result)})
        lines = [
            "Win-win trades look for holes in both sets (energy, search, status, a wall) and keep the matchup near 50/50.",
            result.get("method", ""),
            f"Deck A needs: {', '.join(result.get('needs_a') or ['nothing obvious'])}.",
            f"Deck B needs: {', '.join(result.get('needs_b') or ['nothing obvious'])}.",
            "",
        ]
        for rec in (result.get("recommendations") or [])[:3]:
            lines.append(
                f"- Trade **{rec['give_a']}** (A → B) for **{rec['give_b']}** (B → A). "
                f"{rec['why_a']}. {rec['why_b']}. "
                f"Matchup after: A wins {rec['win_rate_a_after']:.0%}."
            )
        if not result.get("recommendations"):
            lines.append("No clearly mutually helpful one-for-one jumped out. Try adding a search card and one extra energy to both.")
        return "\n".join(lines)

    games = 2000
    if re.search(r"10,?000", message):
        games = 10000
    elif re.search(r"1,?000", message):
        games = 1000
    args = {
        "deck_a_id": a_id,
        "deck_b_id": b_id,
        "games": games,
        "strategy_a": "thrifty",
        "strategy_b": "shock",
        "question": message,
    }
    result = run_tool("simulate_match", args)
    tool_trace.append({"tool": "simulate_match", "args": args, "output_preview": _preview(result)})
    return _narrate_sim(result, message)


def _narrate_sim(result: dict, question: str) -> str:
    if result.get("error"):
        return str(result["error"])
    res = result["results"]
    learn = result["learning"]
    method = result["method"]
    combo = learn.get("combo")
    lines = [
        f"Ran **{method['games']:,} games** with seed {method['seed']} in the family-rules engine.",
        method["how"],
        f"Strategies: A = {result['strategies']['a']['name']} ({result['strategies']['a']['description']}) · "
        f"B = {result['strategies']['b']['name']} ({result['strategies']['b']['description']}).",
        "",
        f"**Results:** A wins {res['win_rate_a']:.1%} · B wins {res['win_rate_b']:.1%} · ties {res['tie_rate']:.1%}.",
    ]
    if res.get("queries"):
        lines.append("Tracked questions: " + ", ".join(f"{k}={v:.1%}" for k, v in res["queries"].items()))
    if combo:
        lines.append(
            f"Pikachu paralyzed Dondozo in **{combo.get('p_games_with_success', combo['p_landed_per_game']):.1%}** of games "
            f"(attempted {combo['p_attempted_per_game']:.2f} times per game on average; coin flips still fail half the shocks)."
        )
    lines.append("")
    lines.append("**What the AI learned**")
    for insight in learn.get("insights") or []:
        lines.append(f"- {insight}")
    lines.append(f"\nFull record saved in the Lab as `{result['simulation_id']}`.")
    return "\n".join(lines)


def _intent(message: str) -> str:
    t = message.lower()
    if any(w in t for w in ("trade", "swap", "win-win", "exchange", "which card")):
        return "trade"
    if any(w in t for w in ("probab", "chance", "odds", "first 7", "opening hand", "how often is")) and "paraly" not in t:
        return "probability"
    if any(w in t for w in ("trade",)):
        return "trade"
    return "simulate"


def _card_in_text(message: str, decks: list[dict]) -> str | None:
    names = []
    for deck in decks:
        names.extend(c["name"] for c in deck["cards"])
    t = message.lower()
    for name in sorted(set(names), key=len, reverse=True):
        if name.lower() in t:
            return name
    return None


def _name_in_deck(name: str, deck_id: str) -> bool:
    from app.db import get_deck

    deck = get_deck(deck_id)
    if not deck:
        return False
    return any(c["name"].lower() == name.lower() for c in deck["cards"])


def _fill_default_decks(args: dict) -> None:
    a_id, b_id = _default_ids()
    args.setdefault("deck_a_id", a_id)
    args.setdefault("deck_b_id", b_id)
    if "deck_id" in args and not args["deck_id"]:
        args["deck_id"] = a_id


def _parse_args(raw: Any) -> dict:
    if isinstance(raw, dict):
        return raw
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def _preview(output: Any) -> Any:
    text = json.dumps(output, default=str)
    if len(text) < 1500:
        return output
    if isinstance(output, dict):
        slim = {k: output[k] for k in output if k in {"results", "learning", "method", "recommendations", "p_at_least_one", "simulation_id", "needs_a", "needs_b"}}
        return slim or text[:1500]
    return text[:1500]
