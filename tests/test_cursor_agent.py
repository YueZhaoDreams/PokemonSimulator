from app.ai.cursor_agent import FAMILY_CUP_BRIEF, cursor_model_label, cursor_model_selection, family_cup_tools, opening_prompt
from app.config import CURSOR_MODEL, CURSOR_MODEL_EFFORT
from app.ai.tools import TOOL_SCHEMAS
from app.db import init_db


def test_default_model_is_grok_extra_high():
    assert CURSOR_MODEL == "grok-4.6"
    assert CURSOR_MODEL_EFFORT == "xhigh"
    assert cursor_model_label() == "grok-4.6 · extra high"
    selection = cursor_model_selection()
    assert selection.id == "grok-4.6"
    assert any(param.id == "effort" and param.value == "xhigh" for param in selection.params)


def test_opening_prompt_includes_family_cup_and_user_text():
    text = opening_prompt("Run 1000 games of A vs B")
    assert "30-card" in FAMILY_CUP_BRIEF
    assert "30-card" in text
    assert "Do not start another uvicorn" in text
    assert "Run 1000 games of A vs B" in text


def test_opening_prompt_can_replay_recent_history():
    text = opening_prompt(
        "Now vs Set D",
        history=[
            {"role": "user", "content": "Who is favored?"},
            {"role": "assistant", "content": "Set A, because Hydro Splash is 180."},
        ],
    )
    assert "Who is favored?" in text
    assert "Hydro Splash" in text


def test_family_cup_tools_match_schemas_and_run():
    init_db()
    tools = family_cup_tools()
    assert set(tools) == {schema["name"] for schema in TOOL_SCHEMAS}
    rules = tools["get_rules"].execute({}, None)
    assert rules["deck_size"] == 30
    assert rules["prize_count"] == 3
    names = [item["name"] for item in tools["list_strategies"].execute({}, None)]
    assert "thrifty" in names
    assert "shock" in names
