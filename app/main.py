from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.ai.coach import ask_coach
from app.ai.llm import provider_status
from app.catalog import resolve_name, search_local
from app.config import SAMPLES_DIR, STATIC_DIR, UPLOADS_DIR
from app.db import (
    delete_deck,
    get_deck,
    get_rules,
    get_simulation,
    init_db,
    list_chats,
    list_decks,
    list_simulations,
    save_deck,
    save_rules,
    save_simulation,
)
from app.engine.models import Card, FamilyRules
from app.engine.montecarlo import run_simulation
from app.engine.probability import draw_probability
from app.engine.strategies import list_strategies, StrategySpec
from app.engine.trades import suggest_trades
from app.recognition.pipeline import recognize_image

app = FastAPI(title="Family Pokémon TCG Simulator", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
if SAMPLES_DIR.exists():
    app.mount("/samples", StaticFiles(directory=SAMPLES_DIR), name="samples")


@app.on_event("startup")
def _startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True, "ai": provider_status(), "rules": get_rules().to_dict()}


@app.get("/api/rules")
def api_rules() -> dict:
    return get_rules().to_dict()


@app.put("/api/rules")
def api_put_rules(payload: dict) -> dict:
    return save_rules(FamilyRules.from_dict(payload)).to_dict()


@app.get("/api/strategies")
def api_strategies() -> list:
    return list_strategies()


@app.get("/api/decks")
def api_decks() -> list:
    return list_decks()


@app.get("/api/decks/{deck_id}")
def api_deck(deck_id: str) -> dict:
    deck = get_deck(deck_id)
    if not deck:
        raise HTTPException(404, "Deck not found")
    return deck


@app.post("/api/decks")
def api_create_deck(payload: dict) -> dict:
    name = payload.get("name") or "Untitled set"
    cards = payload.get("cards") or []
    return save_deck(name, cards, source=payload.get("source"), deck_id=payload.get("id"))


@app.put("/api/decks/{deck_id}")
def api_update_deck(deck_id: str, payload: dict) -> dict:
    existing = get_deck(deck_id)
    if not existing:
        raise HTTPException(404, "Deck not found")
    return save_deck(
        payload.get("name") or existing["name"],
        payload.get("cards") or existing["cards"],
        source=payload.get("source", existing.get("source")),
        deck_id=deck_id,
    )


@app.delete("/api/decks/{deck_id}")
def api_delete_deck(deck_id: str) -> dict:
    delete_deck(deck_id)
    return {"ok": True}


@app.get("/api/cards/search")
def api_card_search(q: str) -> list:
    return search_local(q)


@app.post("/api/cards/resolve")
def api_resolve(payload: dict) -> dict:
    name = payload.get("name") or ""
    if not name:
        raise HTTPException(400, "name required")
    return resolve_name(name, payload.get("prefer")).to_dict()


@app.post("/api/recognize")
async def api_recognize(file: UploadFile = File(...), save_as: str | None = Form(None)) -> dict:
    raw = await file.read()
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    stored = UPLOADS_DIR / f"{uuid.uuid4()}{suffix}"
    stored.write_bytes(raw)
    result = recognize_image(raw, filename=file.filename or stored.name)
    if save_as and result.get("cards"):
        deck = save_deck(save_as, result["cards"], source=str(stored.name))
        result["saved_deck"] = deck
    return result


@app.post("/api/recognize/learn")
def api_learn_crop(payload: dict) -> dict:
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
def api_probability(payload: dict) -> dict:
    deck = get_deck(payload.get("deck_id") or "")
    if not deck:
        raise HTTPException(404, "Deck not found")
    names = [c["name"] for c in deck["cards"]]
    return draw_probability(payload.get("card_name") or "", names, int(payload.get("draw") or 7))


@app.post("/api/simulate")
def api_simulate(payload: dict) -> dict:
    deck_a = get_deck(payload.get("deck_a_id") or "")
    deck_b = get_deck(payload.get("deck_b_id") or "")
    if not deck_a or not deck_b:
        raise HTTPException(400, "Need two decks")
    rules = FamilyRules.from_dict(payload.get("rules")) if payload.get("rules") else get_rules()
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
def api_trades(payload: dict) -> dict:
    deck_a = get_deck(payload.get("deck_a_id") or "")
    deck_b = get_deck(payload.get("deck_b_id") or "")
    if not deck_a or not deck_b:
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
def api_sims() -> list:
    return list_simulations()


@app.get("/api/simulations/{sim_id}")
def api_sim(sim_id: str) -> dict:
    record = get_simulation(sim_id)
    if not record:
        raise HTTPException(404, "Not found")
    return record


@app.post("/api/chat")
def api_chat(payload: dict) -> dict:
    message = (payload.get("message") or "").strip()
    if not message:
        raise HTTPException(400, "message required")
    return ask_coach(message, chat_id=payload.get("chat_id"), history=payload.get("history"))


@app.get("/api/chats")
def api_chats() -> list:
    return list_chats()
