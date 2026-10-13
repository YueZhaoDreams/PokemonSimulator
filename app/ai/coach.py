from __future__ import annotations

import json
import logging
import re
from collections.abc import AsyncIterator
from typing import Any

from app.ai.chat_language import alias_card_in_text, reply_language
from app.ai.cursor_agent import cursor_configured, runtime_ready, stream_cursor_turn
from app.ai.llm import provider_status
from app.ai.tools import _default_ids, chat_visible, current_viewer, fill_default_args, run_tool, _visible_decks
from app.db import get_chat, get_rules, save_chat

log = logging.getLogger(__name__)


def preset_from_chat_message(message: str) -> str | None:
    if re.search(r"standard\s*60\b|(?<!\d)60[\s-]?cards?\b", message, re.I):
        return "s60"
    if re.search(
        r"standard\s*30\b|(?<!\d)30[\s-]?cards?\s*standard\b",
        message,
        re.I,
    ):
        return "s30"
    if re.search(
        r"rule\s*c|规则\s*c|no pok[eé]mon energy|不要.*能量|不当能量",
        message,
        re.I,
    ):
        return "c"
    return None


async def ask_coach_events(
    message: str,
    chat_id: str | None = None,
    history: list[dict] | None = None,
    language: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    stored = get_chat(chat_id) if chat_id else None
    if stored and not chat_visible(stored):
        stored = None
        chat_id = None
    thread = list(history or (stored["messages"] if stored else []))
    agent_id = (stored or {}).get("agent_id")
    tool_trace: list[dict[str, Any]] = []
    lang = reply_language(message, language)

    if cursor_configured() and runtime_ready():
        try:
            async for event in stream_cursor_turn(
                message,
                agent_id=agent_id,
                chat_id=chat_id,
                history=thread,
                language=lang,
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
        except Exception:
            log.exception("Cursor stream failed; using on-device helper")
            yield {
                "type": "status",
                "text": "改用本地助手" if lang == "zh" else "Using on-device helper",
            }
            prefix = "本地助手。" if lang == "zh" else "On-device helper."
            answer = _local_coach(message, tool_trace, language=lang) + f"\n\n({prefix})"
            saved = _save_turn(thread, message, answer, chat_id=chat_id, agent_id=agent_id)
            yield _done(saved, answer, tool_trace, "local")
            return

    answer = _local_coach(message, tool_trace, language=lang)
    used = "local"
    saved = _save_turn(thread, message, answer, chat_id=chat_id, agent_id=agent_id)
    yield _done(saved, answer, tool_trace, used)


async def ask_coach(
    message: str,
    chat_id: str | None = None,
    history: list[dict] | None = None,
    language: str | None = None,
) -> dict[str, Any]:
    done: dict[str, Any] | None = None
    async for event in ask_coach_events(message, chat_id=chat_id, history=history, language=language):
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
    viewer = current_viewer()
    return save_chat(
        thread,
        chat_id=chat_id,
        agent_id=agent_id,
        owner_id=viewer["id"] if viewer else None,
    )


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


def _local_coach(message: str, tool_trace: list[dict], language: str | None = None) -> str:
    lang = reply_language(message, language)
    intent = _intent(message)
    a_id, b_id = _default_ids()
    decks = _visible_decks()
    rules = get_rules()

    if intent == "talk":
        return _talk_reply(message, decks, lang)

    if intent == "fate_cut":
        return _fate_cut_reply(message, decks, tool_trace, lang)

    if intent == "fate_junk":
        return _fate_junk_reply(message, decks, tool_trace, lang)

    if intent == "probability":
        card = _card_in_text(message, decks) or "Dondozo"
        deck_id = a_id if _name_in_deck(card, a_id) else (b_id if _name_in_deck(card, b_id) else a_id)
        draw = 7
        m = re.search(r"first\s+(\d+)|opening\s+(\d+)|(\d+)\s+cards|起手\s*(\d+)|前\s*(\d+)\s*张", message.lower())
        if m:
            draw = int(next(g for g in m.groups() if g))
        args = fill_default_args({"deck_id": deck_id, "card_name": card, "draw": draw})
        result = run_tool("draw_odds", args)
        tool_trace.append({"tool": "draw_odds", "args": args, "output_preview": result})
        if result.get("error"):
            return (
                "还没有可用套牌。请先在扫描页保存一套牌，我再帮你算起手概率。"
                if lang == "zh"
                else "Save a card set first, then I can calculate opening-hand odds."
            )
        p = result.get("p_at_least_one", 0)
        copies = result.get("copies")
        if lang == "zh":
            return (
                f"**{card}** 在 {result.get('deck_size')} 张套牌里有 {copies} 张。"
                f"起手 {draw} 张抽到至少一张的概率是 **{p:.1%}**。\n\n"
                f"{result.get('method')}\n\n"
                "这是精确组合计算，不是猜的。"
                f"家庭杯先抽 {draw} 张手牌，再放 {rules.prize_count} 张奖赏卡。"
            )
        return (
            f"**{card} in the first {draw} cards** of {result.get('deck_size')}-card deck "
            f"({copies} cop{'y' if copies == 1 else 'ies'}): "
            f"**{p:.1%}**.\n\n{result.get('method')}\n\n"
            "This is exact combinatorics, not a guess. Opening hand is drawn before prize cards, "
            f"so with Family Cup's {rules.prize_count} prizes it is still a {draw}-card look at the top."
        )

    if intent == "trade":
        args = fill_default_args({"deck_a_id": a_id, "deck_b_id": b_id, "games": 200})
        result = run_tool("suggest_trades", args)
        tool_trace.append({"tool": "suggest_trades", "args": args, "output_preview": _preview(result)})
        if lang == "zh":
            lines = [
                "双赢换牌会找两边套牌缺的东西（能量、检索、状态、墙），并尽量让对战胜率接近 50%。",
                result.get("method", ""),
                f"A 套需要：{', '.join(result.get('needs_a') or ['暂时看不出'])}。",
                f"B 套需要：{', '.join(result.get('needs_b') or ['暂时看不出'])}。",
                "",
            ]
            for rec in (result.get("recommendations") or [])[:3]:
                lines.append(
                    f"- 用 **{rec['give_a']}**（A→B）换 **{rec['give_b']}**（B→A）。"
                    f"{rec['why_a']}。{rec['why_b']}。"
                    f"换完后 A 胜率 {rec['win_rate_a_after']:.0%}。"
                )
            if not result.get("recommendations"):
                lines.append("没有特别明显的一对一互换。两边都可以先加一张检索和一张能量。")
            return "\n".join(lines)
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
            lines.append(
                "No clearly mutually helpful one-for-one jumped out. Try adding a search card and one extra energy to both."
            )
        return "\n".join(lines)

    games = 2000
    if re.search(r"10,?000|一万", message):
        games = 10000
    elif re.search(r"1,?000|一千", message):
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
    preset = preset_from_chat_message(message)
    if preset:
        args["rule_preset"] = preset
    result = run_tool("simulate_match", args)
    tool_trace.append({"tool": "simulate_match", "args": args, "output_preview": _preview(result)})
    return _narrate_sim(result, lang)


def _narrate_sim(result: dict, lang: str = "en") -> str:
    if result.get("error"):
        return str(result["error"])
    res = result["results"]
    learn = result["learning"]
    method = result["method"]
    combo = learn.get("combo")
    if lang == "zh":
        lines = [
            f"用家庭杯规则跑了 **{method['games']:,}** 局，种子 {method['seed']}。",
            method["how"],
            f"策略：A = {result['strategies']['a']['name']}（{result['strategies']['a']['description']}）· "
            f"B = {result['strategies']['b']['name']}（{result['strategies']['b']['description']}）。",
            "",
            f"**结果：** A 胜 {res['win_rate_a']:.1%} · B 胜 {res['win_rate_b']:.1%} · 平 {res['tie_rate']:.1%}。",
        ]
        if res.get("queries"):
            lines.append("跟踪问题：" + "，".join(f"{k}={v:.1%}" for k, v in res["queries"].items()))
        if combo:
            lines.append(
                f"皮卡丘（Pikachu）麻痹暴噬龟（Dondozo）出现在 **{combo.get('p_games_with_success', combo['p_landed_per_game']):.1%}** 的对局里"
                f"（平均每局尝试 {combo['p_attempted_per_game']:.2f} 次；电击还要抛硬币）。"
            )
        lines.append("")
        lines.append("**这次学到了什么**")
        for insight in learn.get("insights") or []:
            lines.append(f"- {insight}")
        lines.append(f"\n完整记录在实验室 `{result['simulation_id']}`。")
        return "\n".join(lines)
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
    if _is_talk(t, message):
        return "talk"
    if _is_cut_ask(t, message):
        return "fate_cut"
    if _is_junk_ask(t, message):
        return "fate_junk"
    if any(w in t for w in ("trade", "swap", "win-win", "exchange", "which card")) or any(
        w in message for w in ("换牌", "交换", "互换", "双赢")
    ):
        return "trade"
    if (
        any(w in t for w in ("probab", "chance", "odds", "first 7", "opening hand", "how often is"))
        or any(w in message for w in ("概率", "几率", "起手", "抽到"))
    ) and "paraly" not in t and "麻痹" not in message:
        return "probability"
    return "simulate"


def _is_talk(lowered: str, original: str) -> bool:
    if _has_lab_ask(lowered, original):
        return False
    if re.search(r"\b(hi|hello|hey|thanks|thank you)\b", lowered) and len(lowered) < 80:
        return True
    if re.search(r"\b(who are you|what can you|how are you|good morning|good night)\b", lowered) and len(lowered) < 80:
        return True
    zh_talk = ("你好", "您好", "嗨", "在吗", "你是谁", "你会什么", "谢谢", "多谢", "早安", "晚安", "早上好", "晚上好", "聊天", "一起玩")
    if any(g in original for g in zh_talk) and len(original) < 80:
        return True
    return False


def _has_lab_ask(lowered: str, original: str) -> bool:
    if any(
        w in lowered
        for w in (
            "trade",
            "swap",
            "win-win",
            "probab",
            "odds",
            "opening hand",
            "simulat",
            "win rate",
            "paraly",
            "matchup",
            " vs ",
            "games",
            "run ",
            "who win",
        )
    ):
        return True
    if re.search(r"what (do|should) i cut|\bcut for\b|\b(?:junk|isolated)\b", lowered):
        return True
    if _cut_clause(original):
        return True
    if any(w in original for w in ("换牌", "交换", "概率", "几率", "起手", "抽到", "模拟", "对战", "对打", "胜率", "麻痹", "谁更强", "谁会赢", "一万", "垃圾", "孤立")):
        return True
    return False


def _talk_reply(message: str, decks: list[dict], lang: str) -> str:
    card = _card_in_text(message, decks)
    if card:
        if lang == "zh":
            return (
                f"我看到你在问 **{card}**。家庭杯里宝可梦还可以当同属性基础能量贴上去。\n\n"
                "想算它起手抽到的概率，或者说「帮我对打 A 和 B」，我都可以帮忙。"
                "用中文或英文继续说就行。"
            )
        return (
            f"I see you mentioning **{card}**. In Family Cup, a Pokémon can also attach as a Basic Energy of its type.\n\n"
            "Ask me the opening-hand odds, or say “run A vs B”, in English or 中文."
        )
    if lang == "zh":
        return (
            "你好！我是家庭杯小助手。你可以直接跟我聊天，中文和英文都可以。\n\n"
            "可以问：哪张牌容易起手抽到、皮卡丘能不能麻痹暴噬龟、或者帮两套牌对打。"
            "数字我会去实验室里算，不会瞎猜。"
        )
    return (
        "Hi! I’m the Family Cup helper. Talk to me in English or 中文.\n\n"
        "Ask which card shows up in the opening hand, whether Pikachu can paralyze Dondozo, or who wins a matchup. "
        "I will run the lab tools for numbers instead of guessing."
    )


def _trim_cut_clause(text: str) -> str:
    """Drop filler around the card: 为了加 Mega Clefable ex 该 → Mega Clefable ex."""
    previous = None
    while text and text != previous:
        previous = text
        text = re.sub(r"^(?:添加|加)\s*", "", text)
        text = re.sub(r"\s*该\s*$", "", text)
    return text.strip(" ?.!")


def _cut_clause(message: str) -> str:
    """The card to add: English 'cut for X', or Chinese '给 X 切'."""
    english = re.search(r"\bcut for\s+(.+?)\s*$", message.strip(), re.I)
    if english:
        return english.group(1).strip(" ?.!")
    # Bare 为 must not eat 为什么 / 为何 / 为啥.
    chinese = re.search(r"(?:给|为了加|为了|为(?!什|何|啥))\s*(.+?)\s*(?:切|腾|拿掉)", message)
    if chinese:
        return _trim_cut_clause(chinese.group(1).strip(" ?.!"))
    return ""


def _is_cut_ask(lowered: str, original: str) -> bool:
    if re.search(r"what (do|should) i cut|\bcut for\b|which card (do i|should i) cut", lowered):
        return True
    return bool(_cut_clause(original))


def _is_junk_ask(lowered: str, original: str) -> bool:
    if re.search(r"\b(?:junk|isolated)\b", lowered):
        return True
    return any(phrase in original for phrase in ("垃圾", "孤立"))


def _deck_named_in_text(message: str, decks: list[dict]) -> str | None:
    lowered = message.lower()
    named = sorted(decks, key=lambda deck: len(deck.get("name") or ""), reverse=True)
    for deck in named:
        name = deck.get("name") or ""
        if name and name.lower() in lowered:
            return deck["id"]
    return None


def _playable_deck_id(decks: list[dict]) -> str:
    for deck in decks:
        if deck.get("archived") or deck.get("kind") == "spare":
            continue
        return deck["id"]
    a_id, _b_id = _default_ids()
    return a_id


def _deck_for_cut(message: str, decks: list[dict]) -> str:
    """The set being edited. Naming it in the question wins over a list that already has the new card."""
    return _deck_named_in_text(message, decks) or _playable_deck_id(decks)


def _deck_for_junk(message: str, decks: list[dict], card: str) -> str:
    return _deck_named_in_text(message, decks) or _deck_for_card(card, decks)


def _deck_for_card(name: str | None, decks: list[dict]) -> str:
    if name:
        for deck in decks:
            if deck.get("archived") or deck.get("kind") == "spare":
                continue
            if any(card["name"] == name for card in deck.get("cards") or []):
                return deck["id"]
    return _playable_deck_id(decks)


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    head = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([head, sep, *body])


def _cut_target(message: str, decks: list[dict]) -> str:
    """The card to add, even when a shorter name already in the deck is part of it."""
    clause = _cut_clause(message)
    if clause:
        named = _card_in_text(clause, decks)
        if named and named.lower() == clause.lower():
            return named
        return clause
    return _card_in_text(message, decks) or ""


def _fate_cut_reply(message: str, decks: list[dict], tool_trace: list[dict], lang: str) -> str:
    add = _cut_target(message, decks)
    if not add:
        return "说出要加的牌，例如 what do I cut for Mega Clefable ex?" if lang == "zh" else "Name the card to add, for example: what do I cut for Mega Clefable ex?"
    deck_id = _deck_for_cut(message, decks)
    args = {"deck_id": deck_id, "add": add}
    result = run_tool("rank_fate_swaps", args)
    tool_trace.append({"tool": "rank_fate_swaps", "args": args, "output_preview": _preview(result)})
    if result.get("error"):
        return str(result["error"])
    ecos = list((result.get("rows") or [{}])[0].get("ecologies") or {})
    headers = ["rank", "cut", "copies", "delta_s", *ecos]
    table_rows = []
    for row in result.get("rows") or []:
        table_rows.append(
            [row.get("rank"), row.get("cut"), row.get("copies"), row.get("delta_s")]
            + [row.get("ecologies", {}).get(name) for name in ecos]
        )
    weights = (result.get("weights") or {}).get("ecologies") or {}
    weight_text = ", ".join(f"{name}={value}" for name, value in weights.items())
    label = result.get("label") or "fast estimate, not a win rate"
    intro = (
        f"给 **{add}** 腾位置。{label}。权重：{weight_text}。胜率只来自对战模拟。"
        if lang == "zh"
        else f"Cuts for **{add}**. {label}. Weights: {weight_text}. Win rate still comes only from a simulation."
    )
    return intro + "\n\n" + _markdown_table(headers, table_rows)


def _fate_junk_reply(message: str, decks: list[dict], tool_trace: list[dict], lang: str) -> str:
    card = _card_in_text(message, decks)
    if not card:
        return "说出牌名，例如 is Nest Ball junk?" if lang == "zh" else "Name the card, for example: is Nest Ball junk?"
    deck_id = _deck_for_junk(message, decks, card)
    args = {"deck_id": deck_id}
    result = run_tool("deck_metrics", args)
    tool_trace.append({"tool": "deck_metrics", "args": args, "output_preview": _preview(result)})
    if result.get("error"):
        return str(result["error"])
    node = next((row for row in result.get("nodes") or [] if row.get("name") == card), None)
    if not node:
        return f"这套牌里没有 **{card}**。" if lang == "zh" else f"**{card}** is not in that set."
    if node.get("isolated"):
        link = "没有连线，算孤立的。" if lang == "zh" else "It has no links, so it is isolated."
    else:
        linked = ", ".join(node.get("searchers") or []) or "another card"
        link = f"有连线：{linked}。" if lang == "zh" else f"It is linked: {linked}."
    dpe = node.get("dpe_lead")
    damage = f"每能量伤害 {dpe}。" if lang == "zh" and dpe is not None else (
        f"Damage per energy {dpe}." if dpe is not None else ""
    )
    return f"**{card}**. {link} {damage}".strip()


def _card_in_text(message: str, decks: list[dict]) -> str | None:
    aliased = alias_card_in_text(message)
    if aliased:
        return aliased
    names = []
    for deck in decks:
        names.extend(c["name"] for c in deck["cards"])
    t = message.lower()
    for name in sorted(set(names), key=len, reverse=True):
        if name.lower() in t:
            return name
    return None


def _name_in_deck(name: str, deck_id: str) -> bool:
    from app.ai.tools import _usable_deck

    deck = _usable_deck(deck_id)
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
