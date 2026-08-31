from pathlib import Path
import sys

from app.ai.cursor_agent import (
    FAMILY_CUP_BRIEF,
    PRODUCT_CHAT_DISALLOWED_TOOLS,
    PRODUCT_CHAT_TOOLS,
    cursor_model_label,
    cursor_model_selection,
    family_cup_tools,
    opening_prompt,
    product_chat_agent_options,
    product_chat_workspace,
)
from app.config import COACH_SANDBOX_DIR, CURSOR_MODEL, CURSOR_MODEL_EFFORT, ROOT
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
    assert "Mega ex takes 3" in FAMILY_CUP_BRIEF
    assert "30-card" in text
    assert "Do not start another uvicorn" in text
    assert "Reply in the language of the latest user message" in FAMILY_CUP_BRIEF
    assert "Do not run a match simulation just because someone said hello" in FAMILY_CUP_BRIEF
    assert "Replies may be spoken aloud" in FAMILY_CUP_BRIEF
    assert "Run 1000 games of A vs B" in text


def test_opening_prompt_marks_chinese_ui_language():
    text = opening_prompt("你好", language="zh")
    assert "Simplified Chinese" in text
    assert "你好" in text


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


def test_product_chat_workspace_is_not_the_git_root():
    workspace = Path(product_chat_workspace()).resolve()
    assert workspace == COACH_SANDBOX_DIR.resolve()
    assert workspace != ROOT.resolve()
    assert workspace.is_dir()


def test_product_chat_agent_options_are_mcp_only_and_off_repo():
    opts = product_chat_agent_options(name="Family Cup chat")
    payload = opts.to_json()
    assert payload["tools"]["names"] == list(PRODUCT_CHAT_TOOLS)
    disallowed = set(payload["disallowedTools"])
    assert disallowed >= set(PRODUCT_CHAT_DISALLOWED_TOOLS)
    local = opts.local
    assert Path(str(local.cwd)).resolve() == COACH_SANDBOX_DIR.resolve()
    assert Path(str(local.cwd)).resolve() != ROOT.resolve()
    assert list(local.setting_sources or []) == []
    sandbox = getattr(local, "sandbox_options", None)
    if sys.platform == "win32":
        assert sandbox is None or sandbox.enabled is not True
    else:
        assert sandbox is not None
        assert sandbox.enabled is True


def test_family_cup_brief_does_not_invite_repo_edits():
    lowered = FAMILY_CUP_BRIEF.lower()
    assert "you may edit files" not in FAMILY_CUP_BRIEF
    assert "pytest" not in lowered
    assert "in-process tool" in lowered
    assert "cannot edit the git checkout" in lowered
