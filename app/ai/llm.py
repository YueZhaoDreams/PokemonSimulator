from __future__ import annotations

import json
from typing import Any

import httpx

from app.config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    XAI_API_KEY,
    XAI_BASE_URL,
    XAI_MODEL,
    llm_provider,
)


class LLMNotConfigured(RuntimeError):
    pass


def provider_status() -> dict[str, Any]:
    name = llm_provider()
    return {
        "provider": name,
        "model": {"grok": XAI_MODEL, "openai": OPENAI_MODEL, "anthropic": ANTHROPIC_MODEL}.get(name),
        "configured": name is not None,
    }


def chat_completion(messages: list[dict[str, Any]], tools: list[dict] | None = None) -> dict[str, Any]:
    provider = llm_provider()
    if provider is None:
        raise LLMNotConfigured("No AI key configured")
    if provider == "anthropic":
        return _anthropic(messages, tools)
    return _openai_compat(messages, tools, grok=provider == "grok")


def vision_completion(prompt: str, image_bytes: bytes, mime: str = "image/jpeg") -> str:
    import base64

    b64 = base64.b64encode(image_bytes).decode()
    data_url = f"data:{mime};base64,{b64}"
    provider = llm_provider()
    if provider is None:
        raise LLMNotConfigured("No AI key configured")
    if provider == "anthropic":
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": mime, "data": b64}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]
        result = _anthropic(messages, None)
        return result.get("content") or ""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": data_url}},
            ],
        }
    ]
    result = _openai_compat(messages, None, grok=provider == "grok")
    return result.get("content") or ""


def _openai_compat(messages: list[dict[str, Any]], tools: list[dict] | None, grok: bool) -> dict[str, Any]:
    if grok:
        key, base, model = XAI_API_KEY, XAI_BASE_URL, XAI_MODEL
    else:
        key, base, model = OPENAI_API_KEY, "https://api.openai.com/v1", OPENAI_MODEL
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload: dict[str, Any] = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = [{"type": "function", "function": t} for t in tools]
        payload["tool_choice"] = "auto"
    with httpx.Client(timeout=90.0) as client:
        response = client.post(f"{base}/chat/completions", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    choice = data["choices"][0]["message"]
    tool_calls = []
    for tc in choice.get("tool_calls") or []:
        fn = tc.get("function") or {}
        tool_calls.append(
            {
                "id": tc.get("id"),
                "name": fn.get("name"),
                "arguments": fn.get("arguments") or "{}",
            }
        )
    return {"content": choice.get("content") or "", "tool_calls": tool_calls, "raw": choice}


def _anthropic(messages: list[dict[str, Any]], tools: list[dict] | None) -> dict[str, Any]:
    system = ""
    converted = []
    for msg in messages:
        if msg["role"] == "system":
            system = msg.get("content") or ""
            continue
        converted.append({"role": msg["role"], "content": msg.get("content")})
    payload: dict[str, Any] = {
        "model": ANTHROPIC_MODEL,
        "max_tokens": 2000,
        "messages": converted,
    }
    if system:
        payload["system"] = system
    if tools:
        payload["tools"] = [
            {
                "name": t["name"],
                "description": t.get("description") or "",
                "input_schema": t.get("parameters") or {"type": "object"},
            }
            for t in tools
        ]
    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    with httpx.Client(timeout=90.0) as client:
        response = client.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
    text = ""
    tool_calls = []
    for block in data.get("content") or []:
        if block.get("type") == "text":
            text += block.get("text") or ""
        elif block.get("type") == "tool_use":
            tool_calls.append(
                {
                    "id": block.get("id"),
                    "name": block.get("name"),
                    "arguments": json.dumps(block.get("input") or {}),
                }
            )
    return {"content": text, "tool_calls": tool_calls, "raw": data}
