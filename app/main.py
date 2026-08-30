from __future__ import annotations

import json
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, Response, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from app.ai.coach import ask_coach, ask_coach_events
from app.ai.cursor_agent import start_cursor_runtime, stop_cursor_runtime
from app.ai.llm import provider_status
from app.ai.tools import reset_viewer, use_viewer
from app.auth import hash_password, normalize_email, valid_email, verify_password
from app.catalog import resolve_name, search_local
from app.config import SAMPLES_DIR, SESSION_COOKIE, SESSION_DAYS, SESSION_SECURE, STATIC_DIR, UPLOADS_DIR
from app.db import (
    create_session,
    create_user,
    delete_deck,
    delete_session,
    get_deck,
    get_rules,
    get_simulation,
    get_user_by_email,
    init_db,
    delete_chat,
    get_chat,
    list_chats,
    list_decks,
    list_simulations,
    list_users,
    save_deck,
    save_rules,
    save_simulation,
    user_from_session,
)
from app.engine.models import Card, FamilyRules, RULE_PRESETS, rules_from_preset
from app.engine.montecarlo import run_simulation
from app.engine.probability import draw_probability
from app.engine.strategies import list_strategies, StrategySpec
from app.engine.trades import suggest_trades
from app.recognition.pipeline import recognize_image


def _set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=SESSION_SECURE,
        max_age=SESSION_DAYS * 24 * 60 * 60,
        path="/",
    )


def require_user(request: Request) -> dict:
    user = user_from_session(request.cookies.get(SESSION_COOKIE))
    if not user:
        raise HTTPException(401, "Sign in required")
    return user


def require_admin(user: dict = Depends(require_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(403, "Admin only")
    return user


def _can_use_deck(user: dict, deck: dict | None) -> bool:
    if not deck:
        return False
    if user.get("role") == "admin":
        return True
    return deck.get("owner_id") == user["id"]


def _can_use_chat(user: dict, chat: dict | None) -> bool:
    if not chat:
        return False
    if user.get("role") == "admin":
        return True
    return chat.get("owner_id") == user["id"]


def _visible_decks(user: dict) -> list[dict]:
    if user.get("role") == "admin":
        return list_decks()
    return list_decks(owner_id=user["id"])


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    await start_cursor_runtime()
    try:
        yield
    finally:
        await stop_cursor_runtime()


app = FastAPI(title="Family Pokémon TCG Simulator", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "ai": provider_status(), "rules": get_rules().to_dict()}


@app.post("/api/auth/register")
def api_register(payload: dict, response: Response) -> dict:
    from app.auth import MIN_PASSWORD_LEN

    email = normalize_email(payload.get("email") or "")
    password = payload.get("password") or ""
    if not valid_email(email):
        raise HTTPException(400, "A valid email is required")
    if len(password) < MIN_PASSWORD_LEN:
        raise HTTPException(400, f"Password must be at least {MIN_PASSWORD_LEN} characters")
    if get_user_by_email(email):
        raise HTTPException(409, "That email is already registered")
    try:
        user = create_user(email, hash_password(password), role="member")
    except Exception as exc:
        if "UNIQUE" in str(exc).upper():
            raise HTTPException(409, "That email is already registered") from exc
        raise
    token = create_session(user["id"])
    _set_session_cookie(response, token)
    return user


@app.post("/api/auth/login")
def api_login(payload: dict, response: Response) -> dict:
    email = normalize_email(payload.get("email") or "")
    password = payload.get("password") or ""
    stored = get_user_by_email(email)
    if not stored or not verify_password(password, stored["password_hash"]):
        raise HTTPException(401, "Wrong email or password")
    token = create_session(stored["id"])
    _set_session_cookie(response, token)
    return {"id": stored["id"], "email": stored["email"], "role": stored["role"], "created_at": stored["created_at"]}


@app.post("/api/auth/logout")
def api_logout(request: Request, response: Response) -> dict:
    delete_session(request.cookies.get(SESSION_COOKIE) or "")
    response.delete_cookie(SESSION_COOKIE, path="/")
    return {"ok": True}


@app.get("/api/auth/me")
def api_me(user: dict = Depends(require_user)) -> dict:
    return user


@app.get("/api/users")
def api_users(_admin: dict = Depends(require_admin)) -> list:
    return list_users()


@app.get("/api/rules")
def api_rules(_user: dict = Depends(require_user)) -> dict:
    return get_rules().to_dict()


@app.get("/api/rule-presets")
def api_rule_presets(_user: dict = Depends(require_user)) -> list:
    # Deduplicate aliases so the UI only shows Rule B and Open Stage.
    seen: set[str] = set()
    out = []
    for key in ("b", "c"):
        rules = RULE_PRESETS[key]
        blob = rules.to_dict()
        blob["preset"] = key
        blob["label"] = "Rule B (Pokémon = energy)" if key == "b" else "Open Stage (any Pokémon playable)"
        out.append(blob)
        seen.add(rules.name)
    return out


@app.put("/api/rules")
def api_put_rules(payload: dict, _admin: dict = Depends(require_admin)) -> dict:
    if payload.get("preset"):
        return save_rules(rules_from_preset(str(payload["preset"]))).to_dict()
    return save_rules(FamilyRules.from_dict(payload)).to_dict()


@app.get("/api/strategies")
def api_strategies(_user: dict = Depends(require_user)) -> list:
    return list_strategies()


@app.get("/api/decks")
def api_decks(user: dict = Depends(require_user)) -> list:
    return _visible_decks(user)


@app.get("/api/decks/{deck_id}")
def api_deck(deck_id: str, user: dict = Depends(require_user)) -> dict:
    deck = get_deck(deck_id)
    if not _can_use_deck(user, deck):
        raise HTTPException(404, "Deck not found")
    return deck


@app.post("/api/decks")
def api_create_deck(payload: dict, user: dict = Depends(require_user)) -> dict:
    name = payload.get("name") or "Untitled set"
    cards = payload.get("cards") or []
    requested_id = payload.get("id")
    if requested_id:
        existing = get_deck(requested_id)
        if existing:
            if not _can_use_deck(user, existing):
                raise HTTPException(409, "Deck id already exists")
            return save_deck(
                name,
                cards,
                source=payload.get("source", existing.get("source")),
                deck_id=requested_id,
            )
    return save_deck(name, cards, source=payload.get("source"), deck_id=requested_id, owner_id=user["id"])


@app.put("/api/decks/{deck_id}")
def api_update_deck(deck_id: str, payload: dict, user: dict = Depends(require_user)) -> dict:
    existing = get_deck(deck_id)
    if not _can_use_deck(user, existing):
        raise HTTPException(404, "Deck not found")
    return save_deck(
        payload.get("name") or existing["name"],
        payload.get("cards") or existing["cards"],
        source=payload.get("source", existing.get("source")),
        deck_id=deck_id,
        owner_id=existing.get("owner_id") or user["id"],
    )


@app.delete("/api/decks/{deck_id}")
def api_delete_deck(deck_id: str, user: dict = Depends(require_user)) -> dict:
    existing = get_deck(deck_id)
    if not _can_use_deck(user, existing):
        raise HTTPException(404, "Deck not found")
    delete_deck(deck_id)
    return {"ok": True}


@app.get("/api/cards/search")
def api_card_search(q: str, _user: dict = Depends(require_user)) -> list:
    return search_local(q)


@app.post("/api/cards/resolve")
def api_resolve(payload: dict, _user: dict = Depends(require_user)) -> dict:
    name = payload.get("name") or ""
    if not name:
        raise HTTPException(400, "name required")
    return resolve_name(name, payload.get("prefer")).to_dict()


@app.post("/api/recognize")
async def api_recognize(
    file: UploadFile = File(...),
    save_as: str | None = Form(None),
    user: dict = Depends(require_user),
) -> dict:
    raw = await file.read()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    stored = UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
    stored.write_bytes(raw)
    result = recognize_image(raw, filename=file.filename or stored.name)
    if save_as and result.get("cards"):
        deck = save_deck(save_as, result["cards"], source=str(stored.name), owner_id=user["id"])
        result["saved_deck"] = deck
    return result


@app.post("/api/recognize/learn")
def api_learn_crop(payload: dict, _user: dict = Depends(require_user)) -> dict:
    name = (payload.get("name") or "").strip()
    raw = payload.get("jpeg_b64") or ""
    if not name or not raw:
        raise HTTPException(400, "name and jpeg_b64 required")
    from app.recognition.pipeline import learn_crop
    from app.recognition.images import load_image
    import base64

    image = load_image(base64.b64decode(raw))
    return learn_crop(image, name, source="user")


@app.post("/api/probability")
def api_probability(payload: dict, user: dict = Depends(require_user)) -> dict:
    deck = get_deck(payload.get("deck_id") or "")
    if not _can_use_deck(user, deck):
        raise HTTPException(404, "Deck not found")
    names = [c["name"] for c in deck["cards"]]
    return draw_probability(payload.get("card_name") or "", names, int(payload.get("draw") or 7))


@app.post("/api/simulate")
def api_simulate(payload: dict, user: dict = Depends(require_user)) -> dict:
    deck_a = get_deck(payload.get("deck_a_id") or "")
    deck_b = get_deck(payload.get("deck_b_id") or "")
    if not _can_use_deck(user, deck_a) or not _can_use_deck(user, deck_b):
        raise HTTPException(400, "Need two decks")
    if payload.get("rules"):
        rules = FamilyRules.from_dict(payload.get("rules"))
    elif payload.get("rule_preset"):
        rules = rules_from_preset(str(payload.get("rule_preset")))
    else:
        rules = get_rules()
    record = run_simulation(
        [Card.from_dict(c) for c in deck_a["cards"]],
        [Card.from_dict(c) for c in deck_b["cards"]],
        rules,
        StrategySpec.from_dict(payload.get("strategy_a") or "thrifty"),
        StrategySpec.from_dict(payload.get("strategy_b") or "shock"),
        games=int(payload.get("games") or 2000),
        seed=payload.get("seed"),
        question=payload.get("question"),
        queries=payload.get("queries") or [
            {"type": "opening_hand_contains", "side": "a", "card": "Dondozo", "key": "dondozo_opening_a"},
            {"type": "event_prefix", "prefix": "saw_play:Dondozo", "key": "dondozo_saw_play"},
            {"type": "event_prefix", "prefix": "tutor:Dondozo", "key": "dondozo_tutored"},
            {"type": "event_prefix", "prefix": "saw_play:Pikachu", "key": "pikachu_saw_play"},
            {"type": "event_prefix", "prefix": "attack:Pikachu:Volt Tackle", "key": "volt_tackle"},
            {
                "type": "status",
                "attacker": "Pikachu",
                "defender": "Dondozo",
                "status": "paralyzed",
                "key": "pikachu_paralyze_dondozo",
            },
        ],
        deck_a_meta={"id": deck_a["id"], "name": deck_a["name"]},
        deck_b_meta={"id": deck_b["id"], "name": deck_b["name"]},
    )
    save_simulation(record)
    return record


@app.post("/api/trades")
def api_trades(payload: dict, user: dict = Depends(require_user)) -> dict:
    deck_a = get_deck(payload.get("deck_a_id") or "")
    deck_b = get_deck(payload.get("deck_b_id") or "")
    if not _can_use_deck(user, deck_a) or not _can_use_deck(user, deck_b):
        raise HTTPException(400, "Need two decks")
    return suggest_trades(
        [Card.from_dict(c) for c in deck_a["cards"]],
        [Card.from_dict(c) for c in deck_b["cards"]],
        get_rules(),
        StrategySpec.from_dict(payload.get("strategy_a") or "thrifty"),
        StrategySpec.from_dict(payload.get("strategy_b") or "shock"),
        games=int(payload.get("games") or 240),
    )


@app.get("/api/simulations")
def api_sims(_user: dict = Depends(require_user)) -> list:
    return list_simulations()


@app.get("/api/simulations/{sim_id}")
def api_sim(sim_id: str, _user: dict = Depends(require_user)) -> dict:
    record = get_simulation(sim_id)
    if not record:
        raise HTTPException(404, "Not found")
    return record


@app.post("/api/chat")
async def api_chat(payload: dict, user: dict = Depends(require_user)) -> dict:
    message = (payload.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "message required")
    token = use_viewer(user)
    try:
        return await ask_coach(
            message,
            chat_id=payload.get("chat_id"),
            history=payload.get("history"),
            language=payload.get("language"),
        )
    finally:
        reset_viewer(token)


@app.post("/api/chat/stream")
async def api_chat_stream(payload: dict, user: dict = Depends(require_user)) -> StreamingResponse:
    message = (payload.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "message required")

    async def events():
        token = use_viewer(user)
        try:
            async for event in ask_coach_events(
                message,
                chat_id=payload.get("chat_id"),
                history=payload.get("history"),
                language=payload.get("language"),
            ):
                yield f"data: {json.dumps(event, default=str)}\n\n"
        finally:
            reset_viewer(token)

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.get("/api/chats")
def api_chats(q: str = "", user: dict = Depends(require_user)) -> list:
    if user.get("role") == "admin":
        return list_chats(query=q)
    return list_chats(query=q, owner_id=user["id"])


@app.get("/api/chats/{chat_id}")
def api_get_chat(chat_id: str, user: dict = Depends(require_user)) -> dict:
    chat = get_chat(chat_id)
    if not _can_use_chat(user, chat):
        raise HTTPException(404, "Chat not found")
    return chat


@app.delete("/api/chats/{chat_id}")
def api_delete_chat(chat_id: str, user: dict = Depends(require_user)) -> dict:
    chat = get_chat(chat_id)
    if not _can_use_chat(user, chat):
        raise HTTPException(404, "Chat not found")
    delete_chat(chat_id)
    return {"ok": True}
