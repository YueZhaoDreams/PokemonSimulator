from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from app.ai.tools import TOOL_SCHEMAS, fill_default_args, run_tool
from app.config import (
    CURSOR_API_KEY,
    CURSOR_MODEL,
    CURSOR_MODEL_EFFORT,
    CURSOR_SETTING_SOURCES,
    CURSOR_STATE_DIR,
    ROOT,
)

try:
    from cursor_sdk import (
        AgentOptions,
        AsyncAgent,
        AsyncClient,
        CursorAgentError,
        CustomTool,
        LocalAgentOptions,
        LocalSendOptions,
        ModelParameterValue,
        ModelSelection,
        SendOptions,
    )

    HAS_SDK = True
except ImportError:  # pragma: no cover
    HAS_SDK = False
    CursorAgentError = RuntimeError  # type: ignore[misc, assignment]

FAMILY_CUP_BRIEF = """You are Cursor, chatting through the Family Pokémon TCG Simulator web app.
Kids and parents talk to you here. Hold a real conversation: greet them, answer follow-ups, and stay on this thread.
This process is already serving the app (typically http://127.0.0.1:8000). Do not start another uvicorn on port 8000 unless the user asks you to restart it.

Language:
- Support Simplified Chinese and English in the same thread.
- Reply in the language of the latest user message. If they mix both, answer in the language they used most, and keep Pokémon names in English as printed on the cards (you may add the Chinese name in parentheses).
- For a child, use short, kind sentences. Skip lab jargon unless they ask for a simulation.
- Replies may be spoken aloud. Keep a spoken answer to a few short sentences unless they asked for a full simulation.

Family Cup:
- 30-card decks, opening hand of 7, 3 prize cards
- Any Pokémon can be attached as a Basic Energy of its type
- Otherwise follow standard Pokémon TCG
- Printed card text wins over lab notes or memory. Never invent a look size such as "top 6".

How to do work:
- Prefer the in-process tools (list_decks, get_deck, simulate_match, draw_odds, suggest_trades, list_lab, list_strategies, search_cards, get_rules) for engine numbers.
- Use the shell for pytest, lab scripts under data/lab/, and other repo commands. Activate with `.venv/bin/pytest -q` from the repo root.
- You may edit files when the user wants the simulator changed.
- Never invent a win rate or probability. Run the tool or script.
- Do not run a match simulation just because someone said hello.

Be concrete and short. Name cards. Mention Family Cup energy when it matters.
After a simulation, explain: how the sim was run, which strategies were used, the results, and what was learned.
"""

_client: Any = None
_owner_client: Any = None
_client_error: str | None = None
_locks: dict[str, asyncio.Lock] = {}
_locks_guard = asyncio.Lock()


def cursor_configured() -> bool:
    return HAS_SDK and bool(CURSOR_API_KEY)


def cursor_model_label() -> str:
    labels = {"xhigh": "extra high", "high": "high", "medium": "medium", "low": "low"}
    effort = labels.get(CURSOR_MODEL_EFFORT, CURSOR_MODEL_EFFORT)
    return f"{CURSOR_MODEL} · {effort}" if effort else CURSOR_MODEL


def cursor_model_selection() -> Any:
    if not HAS_SDK:
        return CURSOR_MODEL
    params = []
    if CURSOR_MODEL_EFFORT:
        params.append(ModelParameterValue(id="effort", value=CURSOR_MODEL_EFFORT))
    return ModelSelection(id=CURSOR_MODEL, params=params)


def cursor_status() -> dict[str, Any]:
    return {
        "provider": "cursor",
        "model": cursor_model_label(),
        "model_id": CURSOR_MODEL,
        "effort": CURSOR_MODEL_EFFORT or None,
        "configured": cursor_configured(),
        "ready": _client is not None,
        "error": _client_error,
    }


def opening_prompt(message: str, history: list[dict] | None = None, language: str | None = None) -> str:
    parts = [FAMILY_CUP_BRIEF.strip(), ""]
    if language == "zh":
        parts.append("Preferred UI language: Simplified Chinese. Still follow the latest user message.")
        parts.append("")
    elif language == "en":
        parts.append("Preferred UI language: English. Still follow the latest user message.")
        parts.append("")
    prior = [
        f"{item.get('role', 'user').upper()}: {item.get('content', '')}"
        for item in (history or [])[-8:]
        if item.get("content")
    ]
    if prior:
        parts.append("Recent chat in this browser session:")
        parts.extend(prior)
        parts.append("")
    parts.append("User:")
    parts.append(message)
    return "\n".join(parts)


def family_cup_tools() -> dict[str, Any]:
    if not HAS_SDK:
        return {}
    tools: dict[str, Any] = {}
    for schema in TOOL_SCHEMAS:
        name = schema["name"]

        def execute(args: dict[str, Any], _context: Any, tool_name: str = name) -> Any:
            return run_tool(tool_name, fill_default_args(args))

        tools[name] = CustomTool(
            execute=execute,
            description=schema.get("description") or "",
            input_schema=schema.get("parameters") or {"type": "object", "properties": {}},
        )
    return tools


def _local_options() -> Any:
    sources = CURSOR_SETTING_SOURCES or ("project",)
    return LocalAgentOptions(
        cwd=str(ROOT),
        setting_sources=list(sources),
        custom_tools=family_cup_tools(),
    )


def _agent_options(*, name: str | None = None) -> Any:
    return AgentOptions(
        model=cursor_model_selection(),
        api_key=CURSOR_API_KEY,
        name=name,
        local=_local_options(),
    )


async def start_cursor_runtime() -> None:
    global _client, _owner_client, _client_error
    _client_error = None
    if not cursor_configured():
        return
    try:
        owner = await AsyncClient.launch_bridge(
            workspace=str(ROOT),
            state_root=str(CURSOR_STATE_DIR),
            timeout=60,
        )
        _owner_client = owner
        _client = owner.with_options(stream_timeout=3600.0, unary_timeout=120.0)
    except Exception as exc:  # pragma: no cover - depends on local Cursor install
        _client = None
        _owner_client = None
        _client_error = str(exc)


async def stop_cursor_runtime() -> None:
    global _client, _owner_client
    _client = None
    owner = _owner_client
    _owner_client = None
    if owner is not None:
        await owner.aclose()


def runtime_ready() -> bool:
    return _client is not None


async def _lock_for(key: str) -> asyncio.Lock:
    async with _locks_guard:
        lock = _locks.get(key)
        if lock is None:
            lock = asyncio.Lock()
            _locks[key] = lock
        return lock


def _preview(value: Any) -> Any:
    text = json.dumps(value, default=str)
    if len(text) < 1500:
        return value
    if isinstance(value, dict):
        slim = {
            k: value[k]
            for k in value
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


def _assistant_text(message: Any) -> str:
    payload = getattr(message, "message", None)
    content = getattr(payload, "content", None)
    if content is None and isinstance(payload, dict):
        content = payload.get("content")
    if not content:
        return ""
    parts: list[str] = []
    for block in content:
        block_type = getattr(block, "type", None) or (block.get("type") if isinstance(block, dict) else None)
        if block_type != "text":
            continue
        text = getattr(block, "text", None)
        if text is None and isinstance(block, dict):
            text = block.get("text")
        if text:
            parts.append(text)
    return "".join(parts)


async def _open_agent(agent_id: str | None) -> tuple[Any, bool]:
    client = _client
    if client is None:
        raise RuntimeError(_client_error or "Cursor runtime is not running")
    if agent_id:
        try:
            return await AsyncAgent.resume(agent_id, _agent_options(), client=client), False
        except Exception:
            pass
    agent = await AsyncAgent.create(
        _agent_options(name="Family Cup chat"),
        client=client,
    )
    return agent, True


async def stream_cursor_turn(
    message: str,
    *,
    agent_id: str | None = None,
    chat_id: str | None = None,
    history: list[dict] | None = None,
    language: str | None = None,
) -> AsyncIterator[dict[str, Any]]:
    if not runtime_ready():
        raise RuntimeError(_client_error or "Cursor is not ready")
    lock = await _lock_for(chat_id or agent_id or "new")
    async with lock:
        agent = None
        created = False
        try:
            agent, created = await _open_agent(agent_id)
            yield {"type": "status", "text": "正在想… / Thinking…", "agent_id": agent.agent_id}
            prompt = (
                opening_prompt(message, history if created else None, language=language)
                if created
                else message
            )
            run = await agent.send(
                prompt,
                SendOptions(local=LocalSendOptions(force=True)),
            )
            yield {"type": "status", "text": f"Run {run.id}", "agent_id": agent.agent_id, "run_id": run.id}
            tool_trace: list[dict[str, Any]] = []
            answer_parts: list[str] = []
            async for event in run.messages():
                kind = getattr(event, "type", None)
                if kind == "assistant":
                    chunk = _assistant_text(event)
                    if chunk:
                        answer_parts.append(chunk)
                        yield {"type": "text", "text": chunk}
                elif kind == "tool_call":
                    item = {
                        "tool": getattr(event, "name", None),
                        "status": getattr(event, "status", None),
                        "args": getattr(event, "args", None),
                        "output_preview": _preview(getattr(event, "result", None)),
                    }
                    if item["status"] in {None, "completed", "success", "error"}:
                        tool_trace.append(item)
                    yield {"type": "tool", **item}
                elif kind == "status":
                    yield {"type": "status", "text": str(getattr(event, "status", ""))}
            result = await run.wait()
            if result.status == "error":
                raise RuntimeError(result.result or f"Cursor run failed ({result.id})")
            answer = (result.result or "").strip() or "".join(answer_parts).strip()
            yield {
                "type": "result",
                "answer": answer or "Cursor finished without a text reply.",
                "agent_id": agent.agent_id,
                "run_id": result.id,
                "tool_trace": tool_trace,
                "status": result.status,
            }
        except CursorAgentError as exc:
            retryable = getattr(exc, "is_retryable", False)
            raise RuntimeError(f"Cursor could not start: {exc} (retryable={retryable})") from exc
        finally:
            if agent is not None:
                await agent.close()
