from app.recognition.ocr import _match_lexicon
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


def test_gallery_contains_labeled_family_cards():
    names = {row["name"] for row in _load_index()}
    if not names:
        return
    assert "Dondozo" in names
    assert "Pikachu" in names
    assert "Metang" in names


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
