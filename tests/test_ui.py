import re

from app.config import STATIC_DIR


REQUIRED_IDS = [
    "aiPill",
    "view-decks",
    "findPanel",
    "addToSet",
    "newSetName",
    "addName",
    "addHits",
    "addCard",
    "findScan",
    "cancelReplace",
    "findHint",
    "viewSet",
    "openAddCard",
    "view-cards",
    "cardsHost",
    "cardSheet",
    "cardSheetTitle",
    "closeCardSheet",
    "cardSheetHost",
    "deckList",
    "rulePreset",
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
    "agentPanel",
    "agentFull",
    "agentShrink",
    "cubLauncher",
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
    for view in ("decks", "cards", "fight", "lab"):
        assert f'data-view="{view}"' in html
    assert 'data-view="chat"' not in html
    assert 'data-view="scan"' not in html
    nav = html[html.index("<nav") : html.index("</nav>")]
    assert nav.index('data-view="cards"') < nav.index('data-view="decks"')
    assert "Talk 语音" not in html
    assert 'id="cubLauncher"' in html
    assert 'src="/static/cub.svg"' in html
    assert "Chat language and spoken replies" in html
    assert "Sets for this rule only" in html
    assert "keep at least one" in html
    assert 'class="rule-banner"' in html
    assert 'class="grow search-wrap"' in html
    assert 'id="addHits"' in html
    assert 'id="deckRuleFilter"' not in html
    decks = html[html.index('id="view-decks"') : html.index('id="view-cards"')]
    assert "Find a card" not in decks
    assert "Add a card" in decks
    assert "Search or scan, then tap +" in html


def test_styles_keep_stadium_tokens_and_reduced_motion():
    css = _read("styles.css")
    assert "prefers-reduced-motion" in css
    assert "--type-lightning" in css
    assert "--type-psychic" in css
    assert ".arena" in css
    assert ".pokeball-spin" in css
    assert ".busy-mask" in css
    assert ".scan-btn input { display: none; }" not in css
    assert ".scan-btn input" in css
    assert "opacity: 0" in css
    assert "opacity: 0" in css
    assert ".card-sheet" in css
    assert ".hit-add" in css
    assert "body.card-sheet-open" in css
    assert "#cubLauncher:focus-visible" in css
    assert "body.agent-open" in css
    assert "body.agent-full" in css
    assert "body.agent-open .nav" in css
    nav_open = css[css.index("body.agent-open .nav") : css.index("body.agent-open .nav") + 220]
    assert "position: fixed" in nav_open
    assert ".chat-voice { display: none !important; }" not in css
    assert "grid-template-columns: minmax(0, 1fr) min(440px, 42vw)" in css
    assert "minmax(220px, 46vh)" in css


def test_app_js_keeps_simulator_contracts():
    js = _read("app.js")
    assert "async function boot" in js
    assert "function loadApp" in js
    gate = js[js.index("function showAuthGate") : js.index("function hideAuthGate")]
    assert "shrinkAgent" in gate
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
    assert "No Pokémon energy" in js
    assert "Pokémon = energy" in js
    assert "Rule B (Pokémon = energy)" not in js
    assert "function decksMatchingRule" in js
    assert "function currentRule" in js
    assert "function toggleDeckRule" in js
    assert "function deckRulePresets" in js
    assert "Keep at least one rule." in js
    assert "rule_presets" in js
    assert "deckRuleFilter" not in js
    assert "rule_preset" in js
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
    show_fn = js[js.index("function show(view)") : js.index("function md")]
    assert "agent-open" in show_fn
    assert "stopVoiceSession" in show_fn
    assert "function openAgent" in js
    assert 'agentShrink")?.focus()' in js
    assert "function shrinkAgent" in js
    assert "function toggleAgentFull" in js
    assert "function isBrowserDesktop" not in js
    assert "function voiceUiEnabled" not in js
    start_401 = js.index("if (res.status === 401)")
    chunk_401 = js[start_401 : start_401 + 220]
    assert "shrinkAgent" in chunk_401
    assert "state.chatOpened" in js
    assert "function searchHitHtml" in js
    assert 'alt="${esc(h.name || "")}"' in js
    assert "function replaceDeckCard" in js
    assert "function fillAddToSet" in js
    assert "function fillViewSet" in js
    assert "pickerTarget?.deckId" in js
    assert "function selectedSearchHit" in js
    assert "dataset.query" in js
    assert "function cardCount" in js
    assert "function runCardSearch" in js
    assert 'lookupCards(query, "local")' in js
    assert "data-replace-deck" in js
    assert "/api/cards/search" in js
    assert "findScan" in js
    assert "function deleteSelectedSet" in js
    assert "startsWith(\"seed-\")" in js
    assert "data-delete-set" in js
    assert "function selectedSet" in js
    start = js.index("function renderDecks")
    chunk = js[start : js.index("async function deleteSelectedSet")]
    assert "selectedSet()" in chunk
    assert "state.decks.map" not in chunk
    assert "function openCardPicker" in js
    assert "function closeCardSheet" in js
    assert "cardSheetOpener" in js
    assert "function startAddCard" in js
    replace_fn = js[js.index("function startReplace") : js.index("function startAddCard")]
    assert 'show("decks")' not in replace_fn
    assert "openCardPicker" in replace_fn


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
