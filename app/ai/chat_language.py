from __future__ import annotations

import re

_CJK = re.compile(r"[\u3400-\u9fff]")
_LATIN = re.compile(r"[A-Za-z]")

# Printed English names stay the engine key. These are the names a kid is likely to type.
CARD_ALIASES = {
    "皮卡丘": "Pikachu",
    "暴噬龟": "Dondozo",
    "帝牙海狮": "Walrein",
    "海狮王": "Walrein",
    "姆克鹰": "Staraptor",
    "皮皮": "Clefairy",
    "皮可西": "Clefable",
    "正电拍拍": "Plusle",
    "负电拍拍": "Minun",
    "诡角鹿": "Wyrdeer",
}


def prefers_chinese(text: str | None) -> bool:
    return bool(_CJK.search(text or ""))


def reply_language(message: str, preferred: str | None = None) -> str:
    if prefers_chinese(message):
        return "zh"
    if _LATIN.search(message or ""):
        return "en"
    if preferred in {"zh", "en"}:
        return preferred
    return "en"


def alias_card_in_text(text: str) -> str | None:
    for zh_name, en_name in sorted(CARD_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        if zh_name in (text or ""):
            return en_name
    return None
