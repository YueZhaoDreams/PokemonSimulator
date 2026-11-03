"""Artwork hashes for Pad photo match. Files stay under data/cache/pad/."""

from __future__ import annotations

import json
from pathlib import Path

from app.recognition.images import dhash, hamming, load_image

HASH_FILE = "art-hashes.json"
# 256-bit artwork hash. The same picture stays within a few dozen bits.
# A second neighbor this close is a suggestion list, not a confident name.
CLOSE_BITS = 32
WIN_GAP = 8


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


def rank(query_hash: int, gallery: dict[int, int]) -> dict:
    scored = sorted(
        (hamming(query_hash, value), species_id) for species_id, value in gallery.items()
    )
    close = [(dist, species_id) for dist, species_id in scored if dist <= CLOSE_BITS]
    if not close:
        return {"match": "none"}
    best = close[0][0]
    if len(close) == 1 or close[1][0] - best >= WIN_GAP:
        return {"match": "one", "id": close[0][1]}
    return {"match": "many", "ids": [species_id for _dist, species_id in close[:8]]}
