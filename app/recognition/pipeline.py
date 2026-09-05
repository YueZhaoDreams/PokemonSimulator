from __future__ import annotations

import base64
import io
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from PIL import Image

from app.catalog import resolve_name
from app.config import llm_provider
from app.engine.models import Card
from app.recognition.detector import CROP_HEIGHT, detect_card_boxes, detect_card_crops
from app.recognition.gallery import match_crop, remember_crop
from app.recognition.images import load_image, resize_for_vision, to_jpeg_bytes
from app.recognition.ocr import identify_crop

try:
    from app.recognition.vision import identify_one_card_with_vision
except Exception:  # pragma: no cover
    identify_one_card_with_vision = None  # type: ignore

# Per-card vision and catalog art matching are too slow for a carpet of cards;
# Safari then shows a long-running-script warning while the request sits open.
BULK_CROP_COUNT = 4
SCAN_MAX_SIDE = 2400
_OCR_POOL = ThreadPoolExecutor(max_workers=8)


def recognize_image(source, filename: str = "", include_previews: bool = False) -> dict:
    image = load_image(source)
    if max(image.size) > SCAN_MAX_SIDE:
        image = resize_for_vision(image, SCAN_MAX_SIDE)
    notes: list[str] = []
    boxes = detect_card_boxes(image, max_cards=40)
    maybe_bulk = len(boxes) >= BULK_CROP_COUNT
    crops = detect_card_crops(image, max_cards=40, target_h=480 if maybe_bulk else CROP_HEIGHT, boxes=boxes)
    if not crops:
        notes.append("No card grid found; reading the whole photo as one card.")
        crops = [image]
    notes.append(f"Cropped {len(crops)} card-shaped regions, then read each one.")
    bulk = len(crops) >= BULK_CROP_COUNT

    scan = partial(_scan_crop, bulk=bulk, filename=filename)
    if bulk and len(crops) > 1:
        parts = list(_OCR_POOL.map(scan, crops))
    else:
        parts = [scan(crop) for crop in crops]

    identified: list[dict] = []
    oriented_crops: list[Image.Image] = []
    for oriented, item, crop_notes in parts:
        oriented_crops.append(oriented)
        notes.extend(crop_notes)
        identified.append(item)

    cards = [
        _resolve_identified(item, None if bulk else crop)
        for item, crop in zip(identified, oriented_crops)
        if item["name"] != "Unknown"
    ]
    unknown_n = sum(1 for item in identified if item["name"] == "Unknown")
    if unknown_n:
        notes.append(f"{unknown_n} crops still need a name — search to add the rest.")
    if bulk:
        notes.append("Read the carpet quickly (no per-card vision) so the phone stays responsive.")
    if cards:
        notes.append(f"Named {len(cards)} cards from individual crops (not the whole photo).")
        source_tag = "crops"
    else:
        source_tag = "manual"
        notes.append("Could not read names automatically. Search by name instead.")

    previews = []
    preview_b64 = ""
    if include_previews:
        for crop, item in zip(oriented_crops, identified):
            thumb = crop.copy()
            thumb.thumbnail((160, 220))
            buf = io.BytesIO()
            thumb.save(buf, format="JPEG", quality=72)
            previews.append(
                {
                    "name": item["name"],
                    "confidence": item["confidence"],
                    "needs_review": item.get("needs_review", False),
                    "source": item.get("source"),
                    "jpeg_b64": base64.b64encode(buf.getvalue()).decode(),
                }
            )
        preview_b64 = base64.b64encode(to_jpeg_bytes(resize_for_vision(image, 900), 70)).decode()

    return {
        "source": source_tag,
        "notes": notes,
        "detected_regions": len(crops),
        "cards": [c.to_dict() for c in cards],
        "crops": previews,
        "preview_jpeg_b64": preview_b64,
        "filename": filename,
    }


def learn_crop(image: Image.Image, name: str, source: str = "") -> dict:
    clean = _normalize_name(name)
    card = resolve_name(clean, crop_image=image)
    remember_crop(image, clean, source=source, catalog_id=card.catalog_id)
    return card.to_dict()


def _scan_crop(crop: Image.Image, *, bulk: bool, filename: str) -> tuple[Image.Image, dict, list[str]]:
    gallery_name, gallery_conf, _dist, gallery_id = match_crop(crop)
    result = {"name": None, "confidence": 0.0, "ocr": "", "oriented": crop}
    crop_notes: list[str] = []
    if gallery_name and gallery_conf >= 88:
        name, conf, source_tag = gallery_name, gallery_conf, "gallery"
        oriented = crop
    elif _dull_background(crop):
        name, conf, source_tag = None, 0.0, "unrecognized"
        oriented = crop
        gallery_id = None
    else:
        try:
            result = identify_crop(crop, quick=bulk)
        except Exception as exc:
            crop_notes.append(f"OCR skipped ({type(exc).__name__}).")
            result = {"name": None, "confidence": 0.0, "ocr": "", "oriented": crop}
        oriented = result["oriented"] if isinstance(result.get("oriented"), Image.Image) else crop
        if gallery_name is None:
            gallery_name, gallery_conf, _dist, gallery_id = match_crop(oriented)
        name = result["name"]
        conf = result["confidence"]
        source_tag = "ocr"
        if gallery_name and gallery_conf >= max(conf, 86):
            name = gallery_name
            conf = gallery_conf
            source_tag = "gallery"
    if (
        not bulk
        and (not name or conf < 84)
        and llm_provider()
        and identify_one_card_with_vision
    ):
        try:
            jpeg = to_jpeg_bytes(oriented, 82)
            vision_name = identify_one_card_with_vision(jpeg)
            if vision_name:
                name = vision_name
                conf = max(conf, 92)
                source_tag = "crop-vision"
        except Exception as exc:
            crop_notes.append(f"Per-card vision skipped ({type(exc).__name__}).")
    if not name:
        return (
            oriented,
            {
                "name": "Unknown",
                "confidence": conf,
                "source": "unrecognized",
                "needs_review": True,
                "ocr": result.get("ocr") or "",
            },
            crop_notes,
        )
    clean = _normalize_name(name)
    item = {
        "name": clean,
        "confidence": conf,
        "source": source_tag,
        "needs_review": conf < 90 or source_tag == "unrecognized",
        "ocr": result.get("ocr") or "",
        "catalog_id": gallery_id if source_tag == "gallery" else None,
    }
    if not bulk and source_tag == "ocr" and conf >= 99:
        try:
            remember_crop(oriented, clean, source=filename)
        except Exception:
            pass
    return oriented, item, crop_notes


def _dull_background(image: Image.Image) -> bool:
    import cv2
    import numpy as np

    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    sat = hsv[:, :, 1]
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    return float(np.mean(sat)) < 36 and float(yellow.mean()) / 255.0 < 0.03


def _normalize_name(name: str) -> str:
    aliases = {
        "Poke Ball": "Poké Ball",
        "Poke ball": "Poké Ball",
        "Basic Psychic Energy": "Psychic Energy",
        "Basic Grass Energy": "Grass Energy",
        "Basic Lightning Energy": "Lightning Energy",
        "Electric Energy": "Lightning Energy",
        "Basic Electric Energy": "Lightning Energy",
        "Sliggoo Hisui": "Hisuian Sliggoo",
    }
    return aliases.get(name, name)


def _resolve_identified(item: dict, crop=None) -> Card:
    from app.catalog import PRINT_PREFER, fetch_full, normalize_card, _names_match

    if item.get("catalog_id"):
        try:
            card = normalize_card(fetch_full(item["catalog_id"]))
            if _names_match(card.name, item.get("name") or ""):
                return card
        except Exception:
            pass
    name = item["name"]
    prefer = list(PRINT_PREFER.get(name) or [])
    if name.lower() == "pikachu":
        prefer = ["paralyze", "Nuzzle", "Thunder Shock", "Tail Whap", "Volt Tackle"]
    return resolve_name(name, prefer, ocr_text=item.get("ocr") or "", crop_image=crop)
