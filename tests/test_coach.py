import asyncio

from app.ai.coach import _local_coach, ask_coach
from app.db import init_db


def test_local_coach_draw_odds():
    init_db()
    trace = []
    answer = _local_coach("What is the probability Dondozo appears in the first 7 cards?", trace)
    assert "Dondozo" in answer
    assert "%" in answer
    assert trace and trace[0]["tool"] == "draw_odds"


def test_ask_coach_stays_local_without_runtime(monkeypatch):
    init_db()
    monkeypatch.setattr("app.ai.coach.cursor_configured", lambda: False)
    monkeypatch.setattr("app.ai.coach.runtime_ready", lambda: False)
    result = asyncio.run(ask_coach("What is the probability Dondozo appears in the first 7 cards?"))
    assert result["coach"] == "local"
    assert "Dondozo" in result["answer"]
    assert result["chat_id"]
