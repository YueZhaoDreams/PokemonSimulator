from app.recognition.ocr import HAS_TESSERACT, _match_lexicon
from app.recognition.images import load_image
from app.recognition.detector import detect_card_boxes
from app.recognition.gallery import match_crop, remember_crop, _load_index
from app.config import SAMPLES_DIR
from PIL import Image


def test_lexicon_reads_printed_name():
    name, score = _match_lexicon("SyMetang Bullet Punch 30")
    assert name == "Metang"
    assert score >= 97


def test_lexicon_reads_attack_phrase():
    name, score = _match_lexicon("Lucky Find Power Gem 80")
    assert name == "Carbink"


def test_lexicon_reads_energy_switch():
    name, score = _match_lexicon("Move a basic Energy Switch from 1 of your")
    assert name == "Energy Switch"


def test_detector_finds_many_cards_on_sample_a():
    image = load_image(SAMPLES_DIR / "set-a.jpg")
    boxes = detect_card_boxes(image)
    assert len(boxes) >= 18


def _phone_closeup_from_sample():
    """A single card filling a phone-sized frame — how Scan photo is used on iOS."""
    import cv2
    import numpy as np
    from app.recognition.detector import warp_card

    image = load_image(SAMPLES_DIR / "set-e-carpet.jpg")
    boxes = detect_card_boxes(image)
    assert boxes, "carpet sample produced no card boxes"
    bgr = cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    crop = warp_card(bgr, boxes[0], target_h=720)
    assert crop is not None, "could not warp the first carpet card"
    card = Image.fromarray(cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)).resize((900, 1260))
    phone = Image.new("RGB", (1200, 1600), (36, 48, 36))
    phone.paste(card, (150, 170))
    return phone


def test_detector_finds_phone_closeup_card():
    from app.recognition.detector import detect_card_crops

    phone = _phone_closeup_from_sample()
    boxes = detect_card_boxes(phone)
    crops = detect_card_crops(phone)
    assert len(boxes) >= 1
    assert len(crops) >= 1
    assert len(boxes) <= 4


def test_recognize_phone_closeup_names_a_card():
    from app.config import DATA_DIR
    from app.recognition.pipeline import recognize_image
    from app.recognition.images import to_jpeg_bytes

    gallery = DATA_DIR / "gallery"
    sample = next(gallery.glob("dondozo__*.jpg"))
    phone = Image.open(sample).convert("RGB").resize((1200, 1680))
    result = recognize_image(to_jpeg_bytes(phone), filename="iphone-closeup.jpg")
    names = [c.get("name") for c in result.get("cards") or [] if c.get("name") and c.get("name") != "Unknown"]
    assert "Dondozo" in names, result.get("notes")


def test_has_tesseract_requires_a_real_binary():
    import shutil
    from pathlib import Path

    import pytesseract

    # Path("") is the cwd; that must not count as a tesseract install.
    assert not Path("").is_file()
    cmd = str(pytesseract.pytesseract.tesseract_cmd or "").strip()
    if shutil.which("tesseract") or (cmd and Path(cmd).is_file()):
        assert HAS_TESSERACT is True
    else:
        assert HAS_TESSERACT is False


def test_gallery_contains_labeled_family_cards():
    names = {row["name"] for row in _load_index()}
    if not names:
        return
    assert "Dondozo" in names
    assert "Pikachu" in names
    assert "Metang" in names


def test_lexicon_reads_electric_energy_as_lightning():
    name, score = _match_lexicon("Basic Electric Energy")
    assert name == "Lightning Energy"
    assert score >= 90


def test_bulk_recognize_skips_vision_and_omits_previews(monkeypatch):
    from PIL import Image

    from app.recognition import pipeline as pipeline_mod

    dummy = Image.new("RGB", (120, 168), (40, 80, 200))
    vision_calls = []

    monkeypatch.setattr(pipeline_mod, "load_image", lambda *_a, **_k: dummy)
    monkeypatch.setattr(pipeline_mod, "detect_card_crops", lambda *_a, **_k: [dummy] * 8)
    monkeypatch.setattr(pipeline_mod, "match_crop", lambda *_a, **_k: ("Pikachu", 95.0, 0, "sv-pikachu"))
    monkeypatch.setattr(pipeline_mod, "llm_provider", lambda: "grok")
    monkeypatch.setattr(
        pipeline_mod,
        "identify_one_card_with_vision",
        lambda *_a, **_k: vision_calls.append(True) or "Raichu",
    )

    class _Card:
        def to_dict(self):
            return {"name": "Pikachu", "category": "Pokemon"}

    monkeypatch.setattr(pipeline_mod, "_resolve_identified", lambda item, crop=None: _Card())

    result = pipeline_mod.recognize_image(b"not-used", filename="carpet.jpg")
    assert vision_calls == []
    assert result["detected_regions"] == 8
    assert len(result["cards"]) == 8
    assert result["crops"] == []
    assert result["preview_jpeg_b64"] == ""
    assert any("no per-card vision" in note for note in result["notes"])


def test_gallery_roundtrip(tmp_path, monkeypatch):
    from app.recognition import gallery as gallery_mod

    monkeypatch.setattr(gallery_mod, "GALLERY_DIR", tmp_path)
    monkeypatch.setattr(gallery_mod, "INDEX_PATH", tmp_path / "index.json")
    image = Image.new("RGB", (200, 280), (40, 80, 160))
    gallery_mod.remember_crop(image, "Dondozo", source="test")
    name, conf, dist, _cid = gallery_mod.match_crop(image)
    assert name == "Dondozo"
    assert dist <= 2
    assert conf >= 90
