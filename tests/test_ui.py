import re

from app.config import STATIC_DIR


REQUIRED_IDS = [
    "aiPill",
    "view-scan",
    "file",
    "preview",
    "scanNotes",
    "deckName",
    "editor",
    "addName",
    "addCard",
    "saveDeck",
    "view-decks",
    "deckList",
    "view-fight",
    "arenaStage",
    "deckA",
    "deckB",
    "stratA",
    "stratB",
    "games",
    "simQuestion",
    "runSim",
    "watchOne",
    "runTrades",
    "simOut",
    "view-chat",
    "chatSearch",
    "newChat",
    "chatLang",
    "chatLangZh",
    "chatLangEn",
    "chatSpeak",
    "chatThreads",
    "chatThread",
    "backToThreads",
    "chatTitle",
    "chips",
    "chatLog",
    "chatInput",
    "chatVoiceHint",
    "chatMic",
    "sendChat",
    "view-lab",
    "labList",
    "labDetail",
    "sfxToggle",
    "busyMask",
    "authGate",
    "authEmail",
    "authPassword",
    "authLogin",
    "authRegister",
    "logoutBtn",
    "userList",
]


def _read(name: str) -> str:
    return (STATIC_DIR / name).read_text(encoding="utf-8")


def classify_log(line: str) -> str:
    """Keep in lockstep with classifyLog() in app/static/app.js."""
    text = line or ""
    if re.search(r"used .+ for \d+", text, re.I):
        return "attack"
    if re.search(r"Knocked Out", text, re.I):
        return "ko"
    if re.search(r"attaches|as .+ energy", text, re.I):
        return "energy"
    if re.search(r"paralyz|asleep|burn|poison|confus", text, re.I):
        return "status"
    if re.search(r"evolves", text, re.I):
        return "evolve"
    if re.search(r"benches|plays |promotes|Switch|retreats", text, re.I):
        return "play"
    if re.search(r"First player", text, re.I):
        return "setup"
    return "note"


def test_index_keeps_family_cup_controls():
    html = _read("index.html")
    for ident in REQUIRED_IDS:
        assert f'id="{ident}"' in html, ident
    for view in ("scan", "decks", "fight", "chat", "lab"):
        assert f'data-view="{view}"' in html
    assert 'data-sample="a"' in html
    assert 'data-sample="b"' in html


def test_styles_keep_stadium_tokens_and_reduced_motion():
    css = _read("styles.css")
    assert "prefers-reduced-motion" in css
    assert "--type-lightning" in css
    assert "--type-psychic" in css
    assert ".arena" in css
    assert ".pokeball-spin" in css
    assert ".busy-mask" in css


def test_app_js_keeps_simulator_contracts():
    js = _read("app.js")
    assert "async function boot" in js
    assert "function loadApp" in js
    assert "function showAuthGate" in js
    assert "function clearClientSession" in js
    assert "/api/chat/stream" in js
    assert "Sign in required" in js
    assert "rememberChat(null)" in js
    assert "/api/auth/login" in js
    assert "/api/auth/register" in js
    assert "/api/auth/me" in js
    assert "/api/auth/logout" in js
    assert "/api/users" in js
    assert "/api/simulate" in js
    assert "/api/trades" in js
    assert "function classifyLog" in js
    assert "function paintArena" in js
    assert "function resultPanel" in js
    assert "function resetArenaResult" in js
    assert "function bindReplay" in js
    assert "p_at_least_one" in js
    assert "thrifty" in js
    assert "shock" in js
    assert "pokemon_as_energy ? \"Pokémon are energy\"" in js or "pokemon_as_energy ? 'Pokémon are energy'" in js or 'pokemon_as_energy ? "Pokémon are energy"' in js
    assert "ex = 2 prizes · Mega ex = 3" in js
    assert "max ${rules.max_copies_except_basic_energy} of a name" in js
    assert "standard energy" in js
    assert 'bindReplay($("#simOut"), "watchReplay")' in js
    assert "in opening ${hand}" in js
    assert "Looking for win-win trades" in js
    assert "function beginStadiumRun" in js
    assert "Simulation failed" in js
    assert "${aName} takes it" in js
    assert "function prizeCount" in js
    assert "function closeLightbox" in js
    assert 'classList.toggle("busy", !!(on && withMask))' in js
    assert "function stopReplay" in js
    assert "sendChat.busy" in js
    assert "language: state.chatLang" in js
    assert "webkitSpeechRecognition" in js
    assert "speechSynthesis" in js
    assert "function speakReply" in js
    assert "function startVoiceListen" in js
    assert "function speakableText" in js
    assert "function speechLang" in js
    assert "function speechLangFor" in js
    assert "sendChat.pending" in js
    assert "function chatViewOpen" in js
    assert "CHAT_WELCOME" in js
    assert "function setChatLang" in js
    assert "function startNewChat" in js
    assert "state.chatOpened" in js


def test_classify_log_labels_printed_engine_lines():
    js = _read("app.js")
    start = js.index("function classifyLog")
    chunk = js[start : start + 700]
    assert "Knocked Out" in chunk
    assert "attack" in chunk
    assert "energy" in chunk
    assert classify_log("Pikachu used Volt Tackle for 120 on Dondozo") == "attack"
    assert classify_log("Dondozo was Knocked Out") == "ko"
    assert classify_log("A attaches Sobble as Water energy to Dondozo") == "energy"
    assert classify_log("A evolves into Clefable") == "evolve"
    assert classify_log("First player: A") == "setup"
    assert classify_log("A benches Pikachu") == "play"
    assert classify_log("A used Thunder Shock and Dondozo is paralyzed") == "status"
