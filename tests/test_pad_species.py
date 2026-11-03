import io
import re

import httpx
from PIL import Image

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, STATIC_DIR
from app.main import app
from app.pad.species import HttpxTransport, USER_AGENT, search_species, speech_text
from fastapi.testclient import TestClient

POKE = "https://pokeapi.co/api/v2"


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), (255, 220, 0)).save(buf, format="PNG")
    return buf.getvalue()


class MapTransport:
    def __init__(self, docs, blobs=None):
        self.docs = docs
        self.blobs = blobs or {}
        self.calls = 0

    def get_json(self, url):
        self.calls += 1
        return self.docs[url]

    def get_text(self, url):
        return self.docs[url]

    def get_bytes(self, url):
        return self.blobs[url]


def _names():
    return {
        (25, "zh-hans"): "皮卡丘",
        (25, "en"): "Pikachu",
        (152, "zh-hans"): "菊草叶",
        (152, "en"): "Chikorita",
        (1, "en"): "Bulbasaur",
        (1, "zh-hans"): "妙蛙种子",
    }


def _docs():
    art = "https://art.example/25.png"
    return {
        f"{POKE}/pokemon-species/25/": {
            "id": 25,
            "name": "pikachu",
            "names": [
                {"language": {"name": "en"}, "name": "Pikachu"},
                {"language": {"name": "zh-hans"}, "name": "皮卡丘"},
            ],
            "genera": [{"language": {"name": "zh-hans"}, "genus": "鼠宝可梦"}],
            "flavor_text_entries": [
                {"language": {"name": "en"}, "flavor_text": "English only line", "version": {"name": "red"}},
                {"language": {"name": "zh-hans"}, "flavor_text": "第一句", "version": {"name": "sun"}},
                {"language": {"name": "zh-hans"}, "flavor_text": "脸颊上的\n袋子", "version": {"name": "shield"}},
            ],
        },
        f"{POKE}/pokemon/25/": {
            "id": 25,
            "height": 4,
            "weight": 60,
            "types": [{"type": {"name": "electric", "url": f"{POKE}/type/13/"}}],
            "abilities": [{"ability": {"name": "static", "url": f"{POKE}/ability/9/"}}],
            "sprites": {
                "other": {
                    "official-artwork": {"front_default": art},
                    "showdown": {"front_default": "https://ani.example/25.gif"},
                }
            },
            "cries": {"latest": "https://cries.example/25.ogg"},
        },
        f"{POKE}/type/13/": {"names": [{"language": {"name": "zh-hans"}, "name": "电"}]},
        f"{POKE}/ability/9/": {"names": [{"language": {"name": "zh-hans"}, "name": "静电"}]},
        f"{POKE}/pokemon-species/152/": {
            "id": 152,
            "name": "chikorita",
            "names": [{"language": {"name": "zh-hans"}, "name": "菊草叶"}],
            "genera": [{"language": {"name": "zh-hans"}, "genus": "叶子宝可梦"}],
            "flavor_text_entries": [
                {"language": {"name": "en"}, "flavor_text": "A sweet aroma gently wafts from the leaf.", "version": {"name": "gold"}},
            ],
        },
        f"{POKE}/pokemon/152/": {
            "id": 152,
            "height": 9,
            "weight": 64,
            "types": [{"type": {"name": "grass", "url": f"{POKE}/type/12/"}}],
            "abilities": [{"ability": {"name": "overgrow", "url": f"{POKE}/ability/65/"}}],
            "sprites": {"other": {}},
            "cries": {},
        },
        f"{POKE}/type/12/": {"names": [{"language": {"name": "zh-hans"}, "name": "草"}]},
        f"{POKE}/ability/65/": {"names": [{"language": {"name": "zh-hans"}, "name": "茂盛"}]},
    }, art


def test_pikachu_entry_uses_chinese_fields(tmp_path):
    docs, art = _docs()
    transport = MapTransport(docs, {art: _png()})
    found = search_species("皮卡丘", transport=transport, names=_names(), cache_dir=tmp_path)
    entry = found["entry"]
    assert found["match"] == "one"
    assert entry["id"] == 25
    assert entry["name"] == "皮卡丘"
    assert entry["types"] == ["电"]
    assert entry["category"] == "鼠宝可梦"
    assert entry["abilities"] == ["静电"]
    assert entry["height_m"] == 0.4
    assert entry["weight_kg"] == 6.0
    assert entry["flavor"] == "脸颊上的 袋子"
    assert "English" not in entry["flavor"]
    assert entry["artwork_url"] == art
    assert entry["animation_url"] == "https://ani.example/25.gif"
    assert entry["cry_url"] == "https://cries.example/25.ogg"
    assert "皮卡丘" in entry["speech_text"]
    assert "鼠宝可梦" in entry["speech_text"]
    assert entry["flavor"] in entry["speech_text"]
    again = search_species("pikachu", transport=transport, names=_names(), cache_dir=tmp_path)
    number = search_species("25", transport=transport, names=_names(), cache_dir=tmp_path)
    assert again["entry"]["id"] == number["entry"]["id"] == 25


def test_missing_flavor_does_not_speak_english(tmp_path):
    docs, art = _docs()
    found = search_species("菊草叶", transport=MapTransport(docs, {art: _png()}), names=_names(), cache_dir=tmp_path)
    entry = found["entry"]
    assert entry["name"] == "菊草叶"
    assert entry["category"] == "叶子宝可梦"
    assert entry["flavor"] == ""
    assert "菊草叶" in entry["speech_text"]
    assert not re.search(r"[A-Za-z]", entry["speech_text"])


def test_unknown_query_is_a_miss(tmp_path):
    docs, art = _docs()
    found = search_species("not-a-pokemon", transport=MapTransport(docs, {art: _png()}), names=_names(), cache_dir=tmp_path)
    assert found == {"match": "none", "results": []}


def test_speech_text_keeps_a_flavor_line():
    spoken = speech_text({"name": "皮卡丘", "category": "鼠宝可梦", "flavor": "打招呼", "types": ["电"]})
    assert spoken == "皮卡丘，鼠宝可梦。打招呼"


def test_transport_sends_user_agent():
    seen = {}

    def handler(request: httpx.Request):
        seen["ua"] = request.headers.get("user-agent")
        return httpx.Response(200, json={"ok": True})

    client = httpx.Client(transport=httpx.MockTransport(handler), headers={"User-Agent": USER_AGENT})
    assert HttpxTransport(client).get_json("https://pokeapi.co/api/v2/pokemon/25/")["ok"] is True
    assert "ComboCubFamilyPad" in seen["ua"]


def test_pad_speech_uses_chinese_voice():
    js = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    assert "function togglePadSpeech" in js
    assert 'utter.lang = "zh-CN"' in js
    assert "speechSynthesis.cancel" in js
    assert "speechSynthesis.speak" in js
    assert 'cry.src = entry.cry_url' in js
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    assert 'id="padCry"' in html
    assert 'id="padSpeak"' in html


def test_pad_species_route(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    def fake(query):
        if query == "nope":
            return {"match": "none", "results": []}
        return {"match": "one", "entry": {"id": 25, "name": "皮卡丘", "speech_text": "皮卡丘，鼠宝可梦。"}}

    monkeypatch.setattr("app.main.search_species", fake)
    with TestClient(app) as client:
        client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        missing = client.get("/api/pad/species", params={"q": "nope"})
        assert missing.status_code == 404
        assert "皮卡丘" not in missing.text
        hit = client.get("/api/pad/species", params={"q": "皮卡丘"})
        assert hit.status_code == 200
        assert hit.json()["entry"]["id"] == 25
