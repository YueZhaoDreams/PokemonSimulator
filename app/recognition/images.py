from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener

    register_heif_opener()
except Exception:
    pass


def load_image(source: Path | bytes) -> Image.Image:
    if isinstance(source, (bytes, bytearray)):
        image = Image.open(io.BytesIO(source))
    else:
        image = Image.open(source)
    image = ImageOps.exif_transpose(image)
    if image.mode not in {"RGB", "L"}:
        image = image.convert("RGB")
    elif image.mode == "L":
        image = image.convert("RGB")
    return image


def resize_for_vision(image: Image.Image, max_side: int = 1600) -> Image.Image:
    w, h = image.size
    scale = max_side / max(w, h)
    if scale >= 1:
        return image
    return image.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)


def to_jpeg_bytes(image: Image.Image, quality: int = 85) -> bytes:
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def dhash(image: Image.Image, hash_size: int = 16) -> int:
    gray = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = list(getattr(gray, "get_flattened_data", gray.getdata)())
    bits = 0
    bit = 0
    for row in range(hash_size):
        row_start = row * (hash_size + 1)
        for col in range(hash_size):
            if pixels[row_start + col] > pixels[row_start + col + 1]:
                bits |= 1 << bit
            bit += 1
    return bits


def hamming(a: int, b: int) -> int:
    return (a ^ b).bit_count()


def illustration_box(image: Image.Image) -> Image.Image:
    """Center window that is mostly the TCG illustration, not the attack text."""
    w, h = image.size
    return image.crop((int(w * 0.08), int(h * 0.16), int(w * 0.92), int(h * 0.58)))


def frame_yellow_frac(image: Image.Image, frac: float = 0.04) -> float:
    """How much of the outer frame looks like a Sword & Shield yellow border.

    HSV illustration matching confuses two green forests (TWM Tangela vs Crown
    Zenith berries). A strong yellow English frame is the era signal hist missed.
    Only high values are trustworthy — tight crops of dark SWSH cards look silver.
    """
    try:
        import cv2
        import numpy as np
    except Exception:
        return 0.0
    if image is None:
        return 0.0
    arr = np.array(image.convert("RGB"))
    hsv = cv2.cvtColor(arr, cv2.COLOR_RGB2HSV)
    h, w = hsv.shape[:2]
    bw, bh = max(2, int(w * frac)), max(2, int(h * frac))
    mask = np.zeros((h, w), np.uint8)
    mask[:bh, :] = 1
    mask[-bh:, :] = 1
    mask[:, :bw] = 1
    mask[:, -bw:] = 1
    yellow = cv2.inRange(hsv, (14, 80, 80), (42, 255, 255))
    sampled = yellow[mask == 1]
    if sampled.size == 0:
        return 0.0
    return float((sampled > 0).mean())


def art_similarity(crop: Image.Image, catalog: Image.Image) -> float:
    """How well a photo crop matches a catalog card. 0..1, HSV histogram over 4 rotations.

    Attack OCR often misses on art-only crops; color of the illustration is the signal
    that separates Lost Origin Phantump (pink forest light) from Obsidian Flames, etc.
    """
    try:
        import cv2
        import numpy as np
    except Exception:
        return 0.0
    if crop is None or catalog is None:
        return 0.0
    target = _hsv_hist(illustration_box(catalog.convert("RGB")))
    arr = np.array(crop.convert("RGB"))
    best = 0.0
    for k in range(4):
        rotated = Image.fromarray(np.rot90(arr, k))
        for piece in (rotated, illustration_box(rotated)):
            corr = float(cv2.compareHist(_hsv_hist(piece), target, cv2.HISTCMP_CORREL))
            if corr > best:
                best = corr
    return max(0.0, min(1.0, best))


def _hsv_hist(image: Image.Image):
    import cv2
    import numpy as np

    hsv = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [18, 8], [0, 180, 0, 256])
    cv2.normalize(hist, hist)
    return hist
