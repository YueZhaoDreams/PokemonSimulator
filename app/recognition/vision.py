from __future__ import annotations

import json
import re
from typing import Any

from app.ai.llm import chat_completion, vision_completion
from app.engine.models import Card


ONE_CARD_PROMPT = """This photo is ONE Pokémon TCG card. It may be rotated 90/180/270 degrees.
Read the printed English card title.
Return ONLY JSON: {"name": "Exact Card Name"}
Energy cards: "Psychic Energy", "Grass Energy", etc.
If it is not a card, return {"name": null}.
"""


def identify_one_card_with_vision(image_bytes: bytes, mime: str = "image/jpeg") -> str | None:
    raw = vision_completion(ONE_CARD_PROMPT, image_bytes, mime=mime)
    data = _extract_json(raw)
    if isinstance(data, dict):
        name = data.get("name")
        if isinstance(name, str) and name.strip() and name.strip().lower() != "null":
            return name.strip()
    return None


IDENTIFY_PROMPT = """You are identifying Pokémon Trading Card Game cards in a photo of cards laid on the floor.
Return ONLY JSON:
{
  "cards": [
    {"name": "Card Name", "count": 1, "notes": "optional"}
  ]
}

Rules:
- Use the English card title printed at the top.
- Basic Energy cards should be named like "Water Energy" or "Psychic Energy".
- Count duplicates.
- Include Trainer cards (Item/Supporter).
- Ignore feet, carpet, and anything that is not a card.
- If a name is hard to read, still give your best guess.
"""


def identify_cards_with_vision(image_bytes: bytes, mime: str = "image/jpeg") -> list[dict[str, Any]]:
    raw = vision_completion(IDENTIFY_PROMPT, image_bytes, mime=mime)
    data = _extract_json(raw)
    cards = data.get("cards") if isinstance(data, dict) else data
    if not isinstance(cards, list):
        return []
    flattened = []
    for item in cards:
        if not isinstance(item, dict):
            continue
        name = (item.get("name") or "").strip()
        if not name:
            continue
        count = int(item.get("count") or 1)
        for _ in range(max(1, min(count, 8))):
            flattened.append({"name": name, "notes": item.get("notes") or "", "source": "vision"})
    return flattened


def identify_from_names_blob(text: str) -> list[str]:
    data = _extract_json(text)
    if isinstance(data, dict) and "cards" in data:
        return [c.get("name") for c in data["cards"] if c.get("name")]
    names = []
    for line in text.splitlines():
        line = re.sub(r"^[\-\d\.\)\s]+", "", line).strip()
        if line:
            names.append(line)
    return names


def _extract_json(text: str) -> Any:
    if not text:
        return {}
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]+?)```", text)
    if fence:
        text = fence.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return {}
        start = text.find("[")
        end = text.rfind("]")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                return {}
    return {}


def enrich(names: list[dict[str, Any] | str]) -> list[Card]:
    from app.catalog import resolve_name

    cards = []
    for item in names:
        if isinstance(item, str):
            cards.append(resolve_name(item))
        else:
            prefer = []
            notes = (item.get("notes") or "").lower()
            if "paraly" in notes or "thunder shock" in notes:
                prefer = ["paralyze", "Thunder Shock"]
            cards.append(resolve_name(item["name"], prefer))
    return cards
