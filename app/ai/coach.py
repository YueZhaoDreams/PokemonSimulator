from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator
from typing import Any

from app.ai.cursor_agent import cursor_configured, runtime_ready, stream_cursor_turn
from app.ai.llm import provider_status
from app.ai.tools import _default_ids, fill_default_args, run_tool
from app.db import get_chat, get_rules, list_decks, save_chat


async def ask_coach_events(
    message: str,
    chat_id: str | None = None,
    history: list[dict] | None = None,
) -> AsyncIterator[dict[str, Any]]:
    stored = get_chat(chat_id) if chat_id else None
    thread = list(history or (stored["messages"] if stored else []))
    agent_id = (stored or {}).get("agent_id")
    tool_trace: list[dict[str, Any]] = []

    if cursor_configured() and runtime_ready():
        try:
            async for event in stream_cursor_turn(
                message,
                agent_id=agent_id,
                chat_id=chat_id,
                history=thread,
            ):
                if event.get("type") == "tool":
                    tool_trace.append(
                        {
                            "tool": event.get("tool"),
                            "args": event.get("args"),
                            "output_preview": event.get("output_preview"),
                            "status": event.get("status"),
                        }
                    )
                if event.get("type") == "result":
                    saved = _save_turn(
                        thread,
                        message,
                        event["answer"],
                        chat_id=chat_id,
                        agent_id=event.get("agent_id"),
                    )
                    yield {
                        "type": "done",
                        "chat_id": saved["id"],
                        "answer": event["answer"],
                        "messages": saved["messages"],
                        "tool_trace": event.get("tool_trace") or tool_trace,
                        "coach": "cursor",
                        "provider": provider_status(),
                        "agent_id": event.get("agent_id"),
                        "run_id": event.get("run_id"),
                    }
                    return
                yield event
        except Exception as exc:
            yield {"type": "status", "text": f"Cursor fallback: {exc}"}
            answer = _local_coach(message, tool_trace) + f"\n\n(Cursor fallback: {exc})"
            saved = _save_turn(thread, message, answer, chat_id=chat_id, agent_id=agent_id)
            yield _done(saved, answer, tool_trace, "cursor-fallback")
            return

    answer = _local_coach(message, tool_trace)
    used = "local"
    saved = _save_turn(thread, message, answer, chat_id=chat_id, agent_id=agent_id)
    yield _done(saved, answer, tool_trace, used)


async def ask_coach(message: str, chat_id: str | None = None, history: list[dict] | None = None) -> dict[str, Any]:
    done: dict[str, Any] | None = None
    async for event in ask_coach_events(message, chat_id=chat_id, history=history):
        if event.get("type") == "done":
            done = event
    if not done:
        raise RuntimeError("chat produced no reply")
    return {
        "chat_id": done["chat_id"],
        "answer": done["answer"],
        "messages": done["messages"],
        "tool_trace": done.get("tool_trace") or [],
        "coach": done.get("coach"),
        "provider": done.get("provider") or provider_status(),
        "agent_id": done.get("agent_id"),
        "run_id": done.get("run_id"),
    }


def _save_turn(
    thread: list[dict],
    message: str,
    answer: str,
    *,
    chat_id: str | None,
    agent_id: str | None,
) -> dict:
    thread.append({"role": "user", "content": message})
    thread.append({"role": "assistant", "content": answer})
    return save_chat(thread, chat_id=chat_id, agent_id=agent_id)


def _done(saved: dict, answer: str, tool_trace: list[dict], coach: str) -> dict[str, Any]:
    return {
        "type": "done",
        "chat_id": saved["id"],
        "answer": answer,
        "messages": saved["messages"],
        "tool_trace": tool_trace,
        "coach": coach,
        "provider": provider_status(),
        "agent_id": saved.get("agent_id"),
    }


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
        args = fill_default_args({"deck_id": deck_id, "card_name": card, "draw": draw})
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
        args = fill_default_args({"deck_a_id": a_id, "deck_b_id": b_id, "games": 200})
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
    args = fill_default_args(
        {
            "deck_a_id": a_id,
            "deck_b_id": b_id,
            "games": games,
            "strategy_a": "thrifty",
            "strategy_b": "shock",
            "question": message,
        }
    )
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


def _preview(output: Any) -> Any:
    text = json.dumps(output, default=str)
    if len(text) < 1500:
        return output
    if isinstance(output, dict):
        slim = {
            k: output[k]
            for k in output
            if k
            in {
                "results",
                "learning",
                "method",
                "recommendations",
                "p_at_least_one",
                "simulation_id",
                "needs_a",
                "needs_b",
            }
        }
        return slim or text[:1500]
    return text[:1500]
