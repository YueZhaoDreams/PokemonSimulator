from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
SAMPLES_DIR = DATA_DIR / "samples"
CACHE_DIR = DATA_DIR / "cache"
UPLOADS_DIR = DATA_DIR / "uploads"
CURSOR_STATE_DIR = DATA_DIR / "cursor-agents"
STATIC_DIR = Path(__file__).resolve().parent / "static"
DB_PATH = DATA_DIR / "app.db"

for folder in (DATA_DIR, SAMPLES_DIR, CACHE_DIR, UPLOADS_DIR, CURSOR_STATE_DIR):
    folder.mkdir(parents=True, exist_ok=True)

CURSOR_API_KEY = os.getenv("CURSOR_API_KEY", "").strip()
CURSOR_MODEL = os.getenv("CURSOR_MODEL", "grok-4.6").strip() or "grok-4.6"
CURSOR_MODEL_EFFORT = os.getenv("CURSOR_MODEL_EFFORT", "xhigh").strip()
CURSOR_SETTING_SOURCES = tuple(
    part.strip()
    for part in os.getenv("CURSOR_SETTING_SOURCES", "project").split(",")
    if part.strip()
)

XAI_API_KEY = os.getenv("XAI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()

XAI_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
XAI_MODEL = os.getenv("XAI_MODEL", "grok-4.6")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5")

TCGDEX_BASE = "https://api.tcgdex.net/v2/en"
POKEMONTCG_API_KEY = os.getenv("POKEMONTCG_API_KEY", "").strip()

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "dancedfire@gmail.com").strip() or "dancedfire@gmail.com"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "1013")
SESSION_COOKIE = os.getenv("SESSION_COOKIE", "combocub_session")
SESSION_SECURE = os.getenv("SESSION_SECURE", "").strip().lower() in ("1", "true", "yes")
SESSION_DAYS = int(os.getenv("SESSION_DAYS", "30"))


def llm_provider() -> str | None:
    if XAI_API_KEY:
        return "grok"
    if OPENAI_API_KEY:
        return "openai"
    if ANTHROPIC_API_KEY:
        return "anthropic"
    return None
