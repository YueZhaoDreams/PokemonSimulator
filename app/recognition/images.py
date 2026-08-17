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
