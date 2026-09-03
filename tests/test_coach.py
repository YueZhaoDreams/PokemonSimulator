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


def test_local_coach_greets_in_chinese_without_simulating():
    init_db()
    trace = []
    answer = _local_coach("你好！你会什么？", trace)
    assert "家庭杯" in answer
    assert "中文" in answer
    assert trace == []


def test_local_coach_nin_hao_greeting_without_simulating():
    init_db()
    trace = []
    answer = _local_coach("您好", trace)
    assert "家庭杯" in answer
    assert trace == []


def test_local_coach_greets_in_english_without_simulating():
    init_db()
    trace = []
    answer = _local_coach("Hi! What can you do?", trace)
    assert "Family Cup" in answer
    assert "中文" in answer
    assert trace == []


def test_local_coach_chinese_draw_odds():
    init_db()
    trace = []
    answer = _local_coach("暴噬龟出现在起手7张的概率是多少？", trace)
    assert "Dondozo" in answer
    assert "%" in answer
    assert "概率" in answer
    assert trace and trace[0]["tool"] == "draw_odds"


def test_local_coach_greeting_plus_odds_still_runs_tools():
    init_db()
    trace = []
    answer = _local_coach("你好，暴噬龟起手概率？", trace)
    assert "Dondozo" in answer
    assert trace and trace[0]["tool"] == "draw_odds"


def test_local_coach_paralyze_question_still_simulates():
    init_db()
    trace = []
    answer = _local_coach("If I use Pikachu to paralyze Dondozo, how often can I pull that off?", trace)
    assert "%" in answer
    assert trace and trace[0]["tool"] == "simulate_match"


def test_local_coach_win_chance_chinese_simulates():
    init_db()
    trace = []
    answer = _local_coach("B套有机会赢吗", trace)
    assert trace and trace[0]["tool"] == "simulate_match"
    assert "胜" in answer or "wins" in answer.lower() or "%" in answer


def test_local_coach_greeting_plus_match_still_simulates():
    init_db()
    trace = []
    answer = _local_coach("Hello, run 1000 games", trace)
    assert "%" in answer
    assert trace and trace[0]["tool"] == "simulate_match"
    trace_zh = []
    zh = _local_coach("嗨，帮我对打", trace_zh)
    assert "%" in zh or "胜" in zh
    assert trace_zh and trace_zh[0]["tool"] == "simulate_match"


def test_preset_from_chat_message_does_not_treat_160_as_standard_60():
    from app.ai.coach import preset_from_chat_message

    assert preset_from_chat_message("Run Standard 60") == "s60"
    assert preset_from_chat_message("60-card Standard please") == "s60"
    assert preset_from_chat_message("I have 160 cards in the box") is None
    assert preset_from_chat_message("Standard 30 cards") == "s30"
    assert preset_from_chat_message("Rule C, no Pokémon energy") == "c"
