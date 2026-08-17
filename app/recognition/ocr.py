from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rapidfuzz import fuzz, process

from app.config import DATA_DIR

try:
    import pytesseract

    tcmd = Path(str(pytesseract.pytesseract.tesseract_cmd or ""))
    if not tcmd.exists():
        brew = Path("/opt/homebrew/bin/tesseract")
        if brew.exists():
            pytesseract.pytesseract.tesseract_cmd = str(brew)
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False

ENERGY_WORDS = {
    "grass": "Grass Energy",
    "fire": "Fire Energy",
    "water": "Water Energy",
    "lightning": "Lightning Energy",
    "psychic": "Psychic Energy",
    "fighting": "Fighting Energy",
    "darkness": "Darkness Energy",
    "metal": "Metal Energy",
    "fairy": "Fairy Energy",
}

# Distinctive printed phrases that survive messy OCR better than the title.
PHRASE_HINTS = {
    "lucky find": "Carbink",
    "power gem": "Carbink",
    "nuzzle": "Pikachu",
    "volt tackle": "Pikachu",
    "moon watching": "Clefairy",
    "wonder storm": "Clefairy",
    "supplemental swallow": "Dondozo",
    "hydro splash": "Dondozo",
    "fade to black": "Dusclops",
    "leaf boomerang": "Oddish",
    "soothing scent": "Roselia",
    "midnight fluttering": "Flutter Mane",
    "hex hurl": "Flutter Mane",
    "gentle slap": "Hisuian Sliggoo",
    "rigidify": "Hisuian Sliggoo",
    "trekking shoes": "Trekking Shoes",
    "energy switch": "Energy Switch",
    "energy search": "Energy Search",
    "energy retrieval": "Energy Retrieval",
    "ultra ball": "Ultra Ball",
    "poke ball": "Poké Ball",
    "lake acuity": "Lake Acuity",
    "tool box": "Tool Box",
    "call for family": None,  # shared by several cards
    "plus damage": "Plusle",
    "static shock": "Emolga",
    "tail trickery": "Salazzle",
    "super singe": "Salazzle",
    "rolling fireball": "Combusken",
    "into the deep": "Relicanth",
    "poison sting": "Spinarak",
    "crabhammer": "Corphish",
    "kindling panic": "Litwick",
    "flickering flames": "Litwick",
    "tongue slap": "Lickilicky",
    "heavy impact": "Lickilicky",
    "spinning attack": "Bronzor",
    "bullet punch": "Metang",
    "crunch time": "Orthworm",
    "punch and draw": "Orthworm",
}


@lru_cache(maxsize=1)
def name_lexicon() -> list[str]:
    path = DATA_DIR / "card_names.json"
    names = json.loads(path.read_text()) if path.exists() else []
    extras = [
        "Poké Ball",
        "Poke Ball",
        "Ultra Ball",
        "Great Ball",
        "Nest Ball",
        "Energy Switch",
        "Energy Search",
        "Energy Retrieval",
        "Lake Acuity",
        "Trekking Shoes",
        "Tool Box",
        "Rare Candy",
        "Picnic Basket",
        "Flutter Mane",
        "Hisuian Sliggoo",
        "Galarian Meowth",
        "Basic Psychic Energy",
        "Psychic Energy",
        "Grass Energy",
        "Jacq",
        "Tulip",
        "Gimmighoul",
        "Flittle",
        "Crocalor",
    ]
    return sorted(set(list(names) + extras))


def _to_bgr(image: Image.Image) -> np.ndarray:
    return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)


def _prepare(gray: np.ndarray) -> list[np.ndarray]:
    if gray.size == 0:
        return []
    h, w = gray.shape[:2]
    if max(h, w) < 28:
        return []
    scale = 3.2 if min(h, w) < 160 else 2.4
    up = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    clahe = cv2.createCLAHE(clipLimit=2.6, tileGridSize=(8, 8)).apply(up)
    _, otsu = cv2.threshold(clahe, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return [clahe, 255 - otsu, otsu]


def _ocr_text(gray: np.ndarray, psm: int = 7) -> str:
    if not HAS_TESSERACT:
        return ""
    import pytesseract

    blobs = []
    config = f"--oem 3 --psm {psm} -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-"
    for img in _prepare(gray):
        text = pytesseract.image_to_string(img, config=config) or ""
        blobs.append(text)
    blob = " ".join(blobs)
    blob = re.sub(r"[^A-Za-z0-9éÉ' \-]", " ", blob)
    return " ".join(blob.split())


def _normalize_alnum(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _match_lexicon(text: str) -> tuple[str | None, float]:
    if not text or len(text) < 3:
        return None, 0.0
    blob = _normalize_alnum(text)
    padded = f" {blob} "
    phrase_hit, phrase_score = _match_phrases(blob)
    if "energy" in blob:
        for key, name in ENERGY_WORDS.items():
            if re.search(rf"\b{key}\b", blob):
                if "search" in blob:
                    return "Energy Search", 98.0
                if "retrieval" in blob:
                    return "Energy Retrieval", 98.0
                if "switch" in blob:
                    return "Energy Switch", 98.0
                return name, 96.0
        if re.search(r"\benergy\b", blob) and not any(w in blob for w in ("search", "retrieval", "switch")):
            # Colored energy with unreadable type word — still better than a random Pokémon.
            if "psychic" in blob or "eye" in blob:
                return "Psychic Energy", 90.0
    lexicon = sorted(name_lexicon(), key=lambda n: len(n), reverse=True)
    substring_hits = []
    for name in lexicon:
        needle = _normalize_alnum(name)
        if len(needle) < 4:
            continue
        if f" {needle} " in padded or padded.startswith(needle + " ") or padded.endswith(" " + needle):
            substring_hits.append(name)
    if substring_hits:
        return substring_hits[0], 99.0

    tokens = [t for t in blob.split() if len(t) >= 4]
    best_name, best_score = None, 0.0
    for token in tokens:
        hit = process.extractOne(token, lexicon, scorer=fuzz.ratio)
        if not hit:
            continue
        name, score = hit[0], float(hit[1])
        needle = _normalize_alnum(name).replace(" ", "")
        compact = token.replace(" ", "")
        if abs(len(compact) - len(needle)) > 2:
            continue
        # Tight: avoid mapping OCR junk onto random species.
        need = 90 if len(compact) >= 6 else 93
        if score >= need and score > best_score:
            best_name, best_score = name, score
    if phrase_hit and phrase_score >= best_score:
        return phrase_hit, phrase_score
    return best_name, best_score


def _match_phrases(blob: str) -> tuple[str | None, float]:
    for phrase, name in PHRASE_HINTS.items():
        if name and phrase in blob:
            return name, 97.0
    return None, 0.0


def identify_crop(image: Image.Image) -> dict:
    bgr = _to_bgr(image)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    best_name, best_score, best_rot, raw = None, 0.0, 0, ""
    for rot in range(4):
        rotated = np.rot90(gray, rot)
        h, w = rotated.shape
        band_h = max(28, int(h * 0.24))
        text = _ocr_text(rotated[:band_h, :], psm=7)
        name, score = _match_lexicon(text)
        if (not name or score < 90) and min(h, w) >= 60:
            full = _ocr_text(rotated, psm=6)
            n2, s2 = _match_lexicon(full)
            if s2 > score:
                name, score, text = n2, s2, full
        if text and (not raw or (name and score > best_score) or (not best_name and len(text) > len(raw))):
            raw = text
        if name and score > best_score:
            best_name, best_score, best_rot, raw = name, score, rot, text
        if best_score >= 99:
            break
    oriented = image
    if best_rot:
        oriented = Image.fromarray(np.rot90(np.array(image.convert("RGB")), best_rot))
    elif best_name is None:
        # Prefer the rotation whose top band looks most like a title (letters, not carpet).
        oriented = _guess_upright(image, gray)
    return {
        "name": best_name,
        "confidence": round(best_score, 1),
        "rotation": best_rot,
        "ocr": raw,
        "oriented": oriented,
    }


def _guess_upright(image: Image.Image, gray: np.ndarray) -> Image.Image:
    best_rot, best = 0, -1.0
    for rot in range(4):
        rotated = np.rot90(gray, rot)
        h, w = rotated.shape
        top = rotated[: max(20, int(h * 0.2)), :]
        text = _ocr_text(top, psm=7)
        letters = len(re.sub(r"[^A-Za-z]", "", text))
        if letters > best:
            best, best_rot = letters, rot
    if best_rot:
        return Image.fromarray(np.rot90(np.array(image.convert("RGB")), best_rot))
    return image
