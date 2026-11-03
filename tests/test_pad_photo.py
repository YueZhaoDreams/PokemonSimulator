import io
import json
from contextlib import contextmanager

from PIL import Image
from fastapi.testclient import TestClient

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, STATIC_DIR
from app.db import list_decks
from app.main import app
from app.pad.gallery import CLOSE_BITS, remember
from app.recognition.images import dhash, load_image


def _png(color=(255, 220, 0)) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), color).save(buf, format="PNG")
    return buf.getvalue()


@contextmanager
def _client(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")
    monkeypatch.setattr("app.pad.species.CACHE", tmp_path / "pad")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        yield client


def test_same_hash_opens_species_25(tmp_path, monkeypatch):
    png = _png()
    remember(25, png, tmp_path / "pad")

    def entry(species_id, transport, cache_dir=None):
        return {"id": species_id, "name": "皮卡丘"}

    monkeypatch.setattr("app.main.build_entry", entry)
    with _client(tmp_path, monkeypatch) as client:
        before = list_decks()
        res = client.post("/api/pad/photo", files={"file": ("pika.png", png, "image/png")})
        assert res.status_code == 200
        body = res.json()
        assert body["match"] == "one"
        assert body["entry"]["id"] == 25
        assert body["entry"]["name"] == "皮卡丘"
        assert list_decks() == before


def test_two_close_hashes_are_a_list(tmp_path, monkeypatch):
    png = _png()
    folder = tmp_path / "pad"
    value = remember(25, png, folder)
    stored = json.loads((folder / "art-hashes.json").read_text(encoding="utf-8"))
    stored["26"] = value ^ 0b1111
    (folder / "art-hashes.json").write_text(json.dumps(stored), encoding="utf-8")

    def entry(*_args, **_kwargs):
        raise AssertionError("an ambiguous photo must not open one entry")

    monkeypatch.setattr("app.main.build_entry", entry)
    with _client(tmp_path, monkeypatch) as client:
        res = client.post("/api/pad/photo", files={"file": ("pika.png", png, "image/png")})
        assert res.status_code == 200
        body = res.json()
        assert body["match"] == "many"
        assert 25 in [row["id"] for row in body["results"]]
        assert "entry" not in body


def test_distant_hash_is_a_miss(tmp_path, monkeypatch):
    png = _png()
    folder = tmp_path / "pad"
    value = remember(25, png, folder)
    far = value ^ ((1 << (CLOSE_BITS + 8)) - 1)
    (folder / "art-hashes.json").write_text(json.dumps({"25": far}), encoding="utf-8")
    with _client(tmp_path, monkeypatch) as client:
        res = client.post("/api/pad/photo", files={"file": ("pika.png", png, "image/png")})
        assert res.status_code == 200
        body = res.json()
        assert body["match"] == "none"
        assert body["results"] == []
        assert "皮卡丘" not in res.text
        assert dhash(load_image(png)) != far


def test_photo_does_not_start_a_card_scan(tmp_path, monkeypatch):
    def boom(*_args, **_kwargs):
        raise AssertionError("pad photo must not start a card scan")

    monkeypatch.setattr("app.main.create_scan_job", boom)
    monkeypatch.setattr("app.main.save_deck", boom)
    monkeypatch.setattr("app.main.recognize_image", boom)
    png = _png((1, 2, 3))
    with _client(tmp_path, monkeypatch) as client:
        res = client.post("/api/pad/photo", files={"file": ("toy.png", png, "image/png")})
        assert res.status_code == 200
        assert res.json()["match"] == "none"


def test_pad_photo_control_is_not_card_scan():
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    cards = html[html.index('id="view-cards"') : html.index('id="view-fight"')]
    pokemon = cards[cards.index('id="padPokemon"') : cards.index('id="cardsHost"')]
    finder = cards[cards.index('id="findPanel"') : cards.index('id="ownedGrid"')]
    assert 'id="padPhoto"' in pokemon
    assert 'id="padPhoto"' not in finder
    assert 'id="findScan"' in finder
    js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    photo = js[js.index("async function searchPadPhoto") : js.index('$("#padPhoto"')]
    scan = js[js.index('$("#findScan"') : js.index("async function recognizePhoto")]
    assert "/api/pad/photo" in photo
    assert "/api/recognize" not in photo
    assert "recognizePhoto" in scan
    assert "/api/recognize" in js[js.index("async function recognizePhoto") : js.index("async function photoForScan")]
