"""Artwork hashes for Pad photo match. Files stay under data/cache/pad/."""

from __future__ import annotations

import json
from pathlib import Path

from app.recognition.images import dhash, load_image

HASH_FILE = "art-hashes.json"


def remember(species_id: int, image_bytes: bytes, cache_dir: Path) -> int:
    value = dhash(load_image(image_bytes))
    path = cache_dir / HASH_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    data: dict[str, int] = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    data[str(species_id)] = value
    path.write_text(json.dumps(data), encoding="utf-8")
    return value


def load_hashes(cache_dir: Path) -> dict[int, int]:
    path = cache_dir / HASH_FILE
    if not path.exists():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {int(key): int(value) for key, value in raw.items()}
