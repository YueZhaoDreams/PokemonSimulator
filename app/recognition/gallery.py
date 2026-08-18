from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from app.config import DATA_DIR
from app.recognition.images import dhash, hamming

GALLERY_DIR = DATA_DIR / "gallery"
INDEX_PATH = GALLERY_DIR / "index.json"
MAX_HAMMING = 28  # 16x16 dhash is 256 bits; this is a close crop of the same card.


def _load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        return []
    try:
        return json.loads(INDEX_PATH.read_text())
    except json.JSONDecodeError:
        return []


def _save_index(rows: list[dict]) -> None:
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(rows, indent=2))


def remember_crop(image: Image.Image, name: str, source: str = "", catalog_id: str | None = None) -> dict:
    GALLERY_DIR.mkdir(parents=True, exist_ok=True)
    digest = dhash(image)
    hex_id = f"{digest:064x}"[-16:]
    filename = f"{_slug(name)}__{hex_id}.jpg"
    path = GALLERY_DIR / filename
    image.convert("RGB").save(path, format="JPEG", quality=82)
    row = {"name": name, "hash": digest, "file": filename, "source": source}
    if catalog_id:
        row["catalog_id"] = catalog_id
    rows = [r for r in _load_index() if r.get("hash") != digest]
    rows.append(row)
    _save_index(rows)
    return row


def match_crop(image: Image.Image) -> tuple[str | None, float, int, str | None]:
    rows = _load_index()
    if not rows:
        return None, 0.0, 999, None
    best, best_dist = None, 999
    for rot in range(4):
        oriented = image if rot == 0 else image.rotate(90 * rot, expand=True)
        digest = dhash(oriented)
        for row in rows:
            dist = hamming(digest, int(row["hash"]))
            if dist < best_dist:
                best, best_dist = row, dist
        if best_dist == 0:
            break
    if best is None or best_dist > MAX_HAMMING:
        return None, 0.0, best_dist, None
    conf = 99.0 - (best_dist / max(1, MAX_HAMMING)) * 13.0
    return best["name"], round(conf, 1), best_dist, best.get("catalog_id")


def _slug(name: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")[:40]
