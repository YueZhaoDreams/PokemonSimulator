import io
import time
import threading

from PIL import Image
from fastapi.testclient import TestClient

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD
from app.main import app


def _jpeg_bytes() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (12, 12), (30, 80, 140)).save(buf, format="JPEG")
    return buf.getvalue()


def test_recognize_returns_before_ocr_finishes(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "app.db")

    async def _noop():
        return None

    monkeypatch.setattr("app.main.start_cursor_runtime", _noop)
    monkeypatch.setattr("app.main.stop_cursor_runtime", _noop)

    started = threading.Event()
    release = threading.Event()

    def _slow(*_a, **_k):
        started.set()
        assert release.wait(timeout=5)
        return {"cards": [{"name": "Pikachu", "category": "Pokemon"}], "notes": [], "crops": [], "preview_jpeg_b64": ""}

    monkeypatch.setattr("app.main.recognize_image", _slow)

    with TestClient(app) as client:
        login = client.post("/api/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert login.status_code == 200
        t0 = time.perf_counter()
        posted = client.post("/api/recognize", files={"file": ("carpet.jpg", _jpeg_bytes(), "image/jpeg")})
        elapsed = time.perf_counter() - t0
        assert posted.status_code == 200, posted.text
        body = posted.json()
        assert body["status"] == "pending"
        assert body["job_id"]
        assert elapsed < 1.0
        assert started.wait(timeout=2)
        release.set()
        job_id = body["job_id"]
        result = None
        for _ in range(40):
            job = client.get(f"/api/recognize/jobs/{job_id}")
            assert job.status_code == 200
            payload = job.json()
            if payload["status"] != "pending":
                result = payload
                break
            time.sleep(0.05)
        assert result is not None
        assert result["status"] == "done"
        assert result["cards"][0]["name"] == "Pikachu"


def test_cheap_bulk_resolve_skips_remote_catalog(monkeypatch):
    from app.recognition.pipeline import _resolve_identified

    def _boom(*_a, **_k):
        raise AssertionError("remote catalog must not run on bulk scans")

    monkeypatch.setattr("app.catalog.fetch_full", _boom)
    monkeypatch.setattr("app.catalog.resolve_name", _boom)
    monkeypatch.setattr("app.recognition.pipeline.resolve_name", _boom)
    card = _resolve_identified({"name": "Lightning Energy"}, cheap=True)
    assert card.name == "Lightning Energy"
    assert card.category == "Energy"
