from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlencode
import unicodedata

import httpx

from app.config import CACHE_DIR, TCGDEX_BASE
from app.engine.effects import parse_ability_effects, parse_attack
from app.engine.models import Ability, Card

CACHE_DIR.mkdir(parents=True, exist_ok=True)
_CLIENT = httpx.Client(timeout=20.0, headers={"User-Agent": "PokemonFamilySimulator/1.0"})
_SEARCH_CLIENT = httpx.Client(timeout=2.5, headers={"User-Agent": "PokemonFamilySimulator/1.0"})

ENERGY_NAME_TO_TYPE = {
    "grass energy": "Grass",
    "fire energy": "Fire",
    "water energy": "Water",
    "lightning energy": "Lightning",
    "psychic energy": "Psychic",
    "fighting energy": "Fighting",
    "darkness energy": "Darkness",
    "dark energy": "Darkness",
    "metal energy": "Metal",
    "fairy energy": "Fairy",
    "basic grass energy": "Grass",
    "basic fire energy": "Fire",
    "basic water energy": "Water",
    "basic lightning energy": "Lightning",
    "basic psychic energy": "Psychic",
    "basic fighting energy": "Fighting",
    "basic darkness energy": "Darkness",
    "basic dark energy": "Darkness",
    "basic metal energy": "Metal",
}

TRAINER_KIND_HINTS = {
    "rare candy": "item",
    "quick ball": "item",
    "great ball": "item",
    "nest ball": "item",
    "nesting ball": "item",
    "picnic basket": "item",
    "energy search": "item",
    "energy retrieval": "item",
    "energy switch": "item",
    "switch": "item",
    "nest ball": "item",
    "buddy-buddy poffin": "item",
    "maximum belt": "item",
    "bravery charm": "item",
    "beach court": "stadium",
    "arven": "supporter",
    "acerola": "supporter",
    "ultra ball": "item",
    "poké ball": "item",
    "poke ball": "item",
    "tool box": "item",
    "trekking shoes": "item",
    "lake acuity": "stadium",
    "hop": "supporter",
    "lillie": "supporter",
    "youngster": "supporter",
    "shauna": "supporter",
    "jacq": "supporter",
    "tulip": "supporter",
    "lillie's determination": "supporter",
    "boss's orders": "supporter",
    "crispin": "supporter",
    "surfer": "supporter",
    "iris's fighting spirit": "supporter",
    "iono": "supporter",
    "switch cart": "item",
    "irida": "supporter",
    "poké pad": "item",
    "poke pad": "item",
    "crushing hammer": "item",
    "night stretcher": "item",
    "unfair stamp": "item",
    "judge": "supporter",
}

# Carpet-photo printings confirmed via attack OCR phrases / user correction.
PREFERRED_IDS = {
    "Dondozo": "sv04-055",  # Supplemental Swallow-Up / Hydro Splash 180 (Paradox Rift)
    "Orthworm": "sv04-138",  # Punch and Draw / Crunch-Time Rush
    "Flutter Mane": "sv05-078",  # Hex Hurl
    "Pikachu": "sm3-40",  # Set B original: Tail Whap / Thunder Shock. sm12-66 (Nuzzle) is B's second copy after the Tulip trade.
    "Baltoy": "swsh12.5-070",  # Fighting — Carbink Power Gem fuel under Family Cup
    "Tulip": "sv04-181",
    "Plusle": "sv04-060",
    "Crocalor": "sv04-024",
    "Salazzle": "swsh12.5-028",
    "Roselia": "swsh11-014",
    "Relicanth": "swsh11-101",
    "Carbink": "swsh11-108",
    "Hisuian Sliggoo": "swsh11-133",
    "Lickilicky": "swsh11-139",
    "Emolga": "sv10.5b-029",
    "Spheal": "sv08-043",  # Powder Snow 10 + Asleep (Surging Sparks)
    "Sealeo": "sv08-044",  # Lunge Out 30 / Ice Ball 60
    "Walrein": "sv08-045",  # Frigid Fangs 60 / Megaton Fall 170
    "Gimmighoul": "sv04-087",  # Call for Family / Corkscrew Punch
    "Litwick": "swsh11-024",  # Kindling Panic — mill opponent deck
    "Oddish": "swsh12.5-001",
    "Clefairy": "swsh11-062",
    "Clefable": "swsh2-75",
    "Clefable ex": "sv03-082",
    "Mega Clefable ex": "me03-031",
    "Mewtwo ex": "sv04-058",
    "Wo-Chien ex": "sv02-027",
    "Sprigatito": "sv01-013",  # Paldea Evolved Scratch / Leafage
    "Floragato": "sv01-014",  # Paldea Evolved art; engine keeps Slashing Claw 90
    "Jacq": "sv01-175",
    "Buddy-Buddy Poffin": "sv05-144",
    "Maximum Belt": "sv05-154",
    "Muscle Band": "xy1-121",
    "Energy Search": "sv01-172",
    "Energy Retrieval": "sv01-171",
    "Trekking Shoes": "swsh12.5-145",
    "Switch": "sv01-194",
    "Beach Court": "sv01-167",
    "Hop": "swsh1-165",
    "Lillie": "sm5-125",
    "Tool Box": "swsh11-168",
    "Arven": "sv01-166",
    "Super Rod": "sv02-188",
    "Earthen Vessel": "sv04-163",
    "Cornerstone Mask Ogerpon ex": "sv06-112",
    "Mr. Mime": "base2-6",
    "Nest Ball": "sv01-181",
    "Bravery Charm": "sv02-173",
    "Acerola": "sm3-112",
    "Double Colorless Energy": "sm1-136",
    "Dusclops": "swsh12.5-063",  # Fade to Black / Confused (Crown Zenith) — not Brilliant Stars
    "Spinarak": "swsh11-112",  # Darkness Poison Sting 10 (Lost Origin) — not Pokémon GO Grass
    "Bronzor": "swsh11-125",  # Spinning Attack 10, HP 70 (Lost Origin)
    "Metang": "swsh12.5-090",  # Bullet Punch 30+ flip 2 coins (Crown Zenith)
    "Seel": "swsh12.5-029",  # Headbutt 10 / Rain Splash 20 (Crown Zenith)
    "Corphish": "swsh12.5-033",  # Water Gun 10 / Crabhammer 50 (Crown Zenith)
    "Poliwhirl": "swsh11-031",  # Light Punch / Double Smash 50× (Lost Origin)
    "Phantump": "swsh11-016",  # Hook 10, pink/purple forest (Lost Origin) — not OF Branch Poke
    "Gloom": "swsh11-002",  # Absorb 30, Komiya circular flowers (Lost Origin) — not OF IR
    "Pumpkaboo": "sv04-077",  # Seed Bomb / Reckless Charge (Paradox Rift). Set A had this, not Flittle.
    "Flittle": "sv04-079",  # Keep for real Flittle photos; Carpet Set A uses Pumpkaboo.
    "Sudowoodo": "swsh11-094",  # Joust / Impound (Lost Origin)
    "Gible": "sv04-094",  # Bite 20, HP 70 Fighting (Paradox Rift) — not Forbidden Light / POP
    "Slugma": "swsh11-021",  # Draw In / Combustion 50 (Lost Origin)
    "Ferroseed": "sv04-127",  # Spike Sting 30 (Paradox Rift) — not White Flare
    "Electrike": "swsh11-054",  # Zap Kick / Thunder Fang (Lost Origin)
    "Wailmer": "swsh12.5-031",  # Nap / Water Gun 70 (Crown Zenith)
    "Aron": "swsh12.5-087",  # Ram / Slight Intrusion (Crown Zenith)
    "Starly": "sv01-148",  # Flap 20 (Paldea Evolved)
    "Staravia": "sv01-149",  # Wing Attack / Speed Dive
    "Staraptor": "sv01-150",  # Tailspin Away 60 / Power Blast 180
    "Gligar": "sv04-091",  # Toxic (Paradox Rift)
    "Surfer": "sv08-187",  # Regular Surging Sparks 187 — not 191 Enriching Energy
    "Iris's Fighting Spirit": "sv09-149",
    "Iono": "sv01-185",
    "Switch Cart": "sv02-178",
    "Hippopotas": "swsh7-084",  # Evolving Skies Hippopotas — not sv01-112 Riolu
    "Skwovet": "sv01-151",
    "Scream Tail": "sv04-086",
    "Gengar": "sv06-057",
    "Haunter": "sv06-056",
    "Gastly": "sv06-055",
    "Ultra Ball": "sv01-196",
    "Lake Acuity": "swsh11-160",  # Lost Origin 160/196 — not Astral Radiance 160 Beedrill V
    "Boomerang Energy": "sv06-166",
    "Dragapult ex": "sv06-130",
    "Dreepy": "sv06-128",
    "Drakloak": "sv06-129",
    "Fezandipiti ex": "sv06.5-038",
    "Budew": "sv08.5-004",
    "Lillie's Determination": "me01-119",
    "Lillie's Clefairy ex": "sv09-056",
    "Boss's Orders": "sv02-172",
    "Crispin": "sv07-133",
    "Poké Pad": "me02.5-198",
    "Crushing Hammer": "swsh12.5-125",
    "Night Stretcher": "sv06.5-061",
    "Unfair Stamp": "sv06-165",
    "Judge": "sv01-176",
    "Ultra Ball": "sv04.5-091",
    "Rare Candy": "sv04.5-089",
    "Ivysaur": "sv03.5-002",  # Leech Seed / Vine Whip (151)
    "Tangela": "swsh12.5-004",  # Beat 10 / Vine Whip 60, Razz berries (Crown Zenith) — not TWM meadow
    "Aipom": "swsh11-144",  # Mischievous Tail / Scratch 10 (Lost Origin) — not Pokémon GO
    "Galarian Meowth": "swsh12.5-084",  # Fasten Claws (Crown Zenith)
    # Rockruff is NOT pinned globally: Set A is Crown Zenith Invite Out, Set B is Lost Origin Double Draw.
}

# Extra household printings of the same name (search / scan / replace). PREFERRED_IDS is the default.
EXTRA_PRINT_IDS: dict[str, tuple[str, ...]] = {
    "Pikachu": ("sm3-40", "sm12-66"),
    "Rockruff": ("swsh12.5-073", "swsh11-109"),
    "Starly": ("sv01-148", "swsh9-117"),  # Flap 20 Paldea Evolved; Claw 30 Brilliant Stars 117/172
}


def allowed_print_ids(name: str) -> set[str] | None:
    extra = EXTRA_PRINT_IDS.get(name)
    if extra:
        return set(extra)
    pinned = PREFERRED_IDS.get(name)
    return {pinned} if pinned else None


def _names_match(got: str, wanted: str) -> bool:
    return (got or "").strip().lower() == (wanted or "").strip().lower()

# When resolving by name, prefer candidates whose attacks/text match these phrases.
PRINT_PREFER = {
    "Dondozo": ["supplemental swallow", "hydro splash"],
    "Orthworm": ["crunch-time", "punch and draw"],
    "Flutter Mane": ["hex hurl"],
    "Pikachu": ["thunder shock", "tail whap", "paralyze"],
    "Roselia": ["soothing scent"],
    "Salazzle": ["tail trickery", "super singe"],
    "Carbink": ["lucky find", "power gem"],
    "Baltoy": ["smack"],
    "Clefairy": ["wonder storm", "moon-watching"],
    "Clefable": ["prankish"],
    "Clefable ex": ["lunar zone"],
    "Mega Clefable ex": ["luminous wing", "shooting moons"],
    "Mewtwo ex": ["photon kinesis", "transfer charge"],
    "Wo-Chien ex": ["forest blast", "covetous ivy"],
    "Floragato": ["slashing claw"],
    "Sprigatito": ["leafage", "scratch"],
    "Cornerstone Mask Ogerpon ex": ["demolish", "cornerstone stance"],
    "Mr. Mime": ["invisible wall", "meditate"],
    "Buddy-Buddy Poffin": ["70 hp"],
    "Maximum Belt": ["50 more damage"],
    "Muscle Band": ["20 more damage"],
    "Beach Court": ["retreat"],
    "Arven": ["item", "tool"],
    "Bravery Charm": ["+50 hp"],
    "Tool Box": ["top 7", "pokemon tool"],
    "Acerola": ["damage counters"],
    "Relicanth": ["into the deep"],
    "Plusle": ["plus damage"],
    "Emolga": ["static shock", "call for family"],
    "Spheal": ["powder snow"],
    "Sealeo": ["lunge out", "ice ball"],
    "Walrein": ["frigid fangs", "megaton fall"],
    "Gimmighoul": ["call for family", "corkscrew"],
    "Litwick": ["kindling panic", "discard the top"],
    "Hisuian Sliggoo": ["rigidify", "gentle slap"],
    "Dusclops": ["fade to black"],
    "Oddish": ["leaf boomerang"],
    "Lickilicky": ["tongue slap", "heavy impact"],
    "Spinarak": ["poison sting"],
    "Sudowoodo": ["joust", "impound"],
    "Gible": ["bite"],
    "Slugma": ["draw in", "combustion"],
    "Ferroseed": ["spike sting"],
    "Electrike": ["zap kick", "thunder fang"],
    "Wailmer": ["nap", "water gun"],
    "Aron": ["slight intrusion", "ram"],
    "Ivysaur": ["leech seed", "vine whip"],
    "Tangela": ["beat", "vine whip"],
    "Aipom": ["mischievous tail", "scratch"],
    "Starly": ["flap"],
    "Staravia": ["wing attack", "speed dive"],
    "Staraptor": ["tailspin away", "power blast"],
    "Gligar": ["toxic"],
    "Surfer": ["benched", "until you have 5"],
    "Lake Acuity": ["water", "fighting", "20 less"],
    "Hippopotas": ["mud shot", "tackle"],
    "Boomerang Energy": ["provides", "discarded by an effect"],
    "Galarian Meowth": ["fasten claws"],
    "Corphish": ["water gun", "crabhammer"],
    "Bronzor": ["spinning attack"],
    "Metang": ["bullet punch", "flip 2 coins"],
    "Seel": ["headbutt", "rain splash"],
    "Poliwhirl": ["light punch", "double smash"],
    "Phantump": ["hook"],
    "Gloom": ["absorb"],
    "Pumpkaboo": ["seed bomb", "reckless charge"],
    "Flittle": ["quick attack"],
    "Crocalor": ["rolling fireball"],
    "Tulip": ["psychic"],
    "Dragapult ex": ["phantom dive"],
    "Dreepy": ["petty grudge"],
    "Drakloak": ["recon directive"],
    "Fezandipiti ex": ["flip the script", "cruel arrow"],
    "Budew": ["itchy pollen"],
    "Lillie": ["until you have 6", "first turn"],
    "Lillie's Determination": ["exactly 6 prize"],
    "Lillie's Clefairy ex": ["fairy zone", "full moon rondo"],
    "Boss's Orders": ["switch in"],
    "Crispin": ["different types"],
    "Poké Pad": ["rule box"],
    "Crushing Hammer": ["flip a coin"],
    "Night Stretcher": ["discard pile"],
    "Unfair Stamp": ["knocked out during your opponent's last turn"],
    "Judge": ["draws 4"],
}


def _cache_path(kind: str, key: str) -> Path:
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", key)[:180]
    folder = CACHE_DIR / kind
    folder.mkdir(parents=True, exist_ok=True)
    return folder / f"{safe}.json"


def _get_json(url: str, cache_key: str) -> Any:
    path = _cache_path("http", cache_key)
    if path.exists():
        return json.loads(path.read_text())
    response = _CLIENT.get(url)
    response.raise_for_status()
    data = response.json()
    path.write_text(json.dumps(data))
    return data


def search_briefs(name: str) -> list[dict[str, Any]]:
    url = f"{TCGDEX_BASE}/cards?name={quote(name)}"
    data = _get_json(url, f"search-{name.lower()}")
    if isinstance(data, list):
        return data
    return data.get("data") or []


def fetch_full(card_id: str) -> dict[str, Any]:
    url = f"{TCGDEX_BASE}/cards/{quote(card_id)}"
    return _get_json(url, f"card-{card_id}")


def _image_url(raw: dict[str, Any]) -> str | None:
    image = raw.get("image")
    if not image:
        return None
    if image.endswith((".png", ".jpg", ".jpeg", ".webp")):
        return image
    return f"{image}/low.webp"


def _trainer_kind(name: str, stage: str, category: str, trainer_type: str | None = None) -> str | None:
    if category.lower() != "trainer":
        return None
    hinted = TRAINER_KIND_HINTS.get(name.lower())
    if hinted:
        return hinted
    for blob in (trainer_type or "", stage or ""):
        stage_l = blob.lower()
        if "support" in stage_l:
            return "supporter"
        if "stadium" in stage_l:
            return "stadium"
        if "item" in stage_l or "tool" in stage_l:
            return "item"
    return "item"


def normalize_card(raw: dict[str, Any]) -> Card:
    category = raw.get("category") or "Pokemon"
    name = raw.get("name") or "Unknown"
    types = list(raw.get("types") or [])
    energy_type = None
    if category.lower() == "energy":
        energy_type = ENERGY_NAME_TO_TYPE.get(name.lower())
        if not energy_type and types:
            energy_type = types[0]
        if not energy_type:
            for energy_name, etype in ENERGY_NAME_TO_TYPE.items():
                if etype.lower() in name.lower():
                    energy_type = etype
                    break
            energy_type = energy_type or "Colorless"
        types = types or [energy_type]
        category = "Energy"
        if (raw.get("energyType") or raw.get("energy_type") or "").lower() == "special":
            raw = {**raw, "stage": raw.get("stage") or "Special"}

    attacks = [parse_attack(a) for a in raw.get("attacks") or []]
    abilities = []
    for a in raw.get("abilities") or []:
        text = a.get("effect") or a.get("text") or ""
        abilities.append(
            Ability(
                name=a.get("name") or "Ability",
                text=text,
                effects=parse_ability_effects(text),
            )
        )
    set_info = raw.get("set") or {}
    trainer_type = raw.get("trainerType") or raw.get("trainer_type")
    stage = raw.get("stage") or ""
    trainer_kind = _trainer_kind(name, stage, category, trainer_type)
    if category.lower() == "trainer" and not stage:
        stage = (trainer_kind or "item").title()

    evolves = raw.get("evolveFrom") or raw.get("evolvesFrom") or raw.get("evolves_from")
    return Card(
        catalog_id=str(raw.get("id") or name),
        name=name,
        category=category,
        stage=stage,
        types=types,
        hp=int(raw.get("hp") or 0),
        attacks=attacks,
        abilities=abilities,
        weaknesses=list(raw.get("weaknesses") or []),
        resistances=list(raw.get("resistances") or []),
        retreat=int(raw.get("retreat") or 0),
        evolves_from=evolves,
        trainer_kind=trainer_kind,
        energy_type=energy_type,
        image=_image_url(raw),
        set_name=set_info.get("name") if isinstance(set_info, dict) else None,
        text=raw.get("effect") or raw.get("description") or "",
        dex_id=(raw.get("dexId") or [None])[0] if isinstance(raw.get("dexId"), list) else raw.get("dexId"),
    )


def _norm_alnum(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (text or "").lower()).strip()


def _score_candidate(brief: dict[str, Any], name: str, prefer: list[str]) -> float:
    score = 0.0
    cid = str(brief.get("id") or "")
    cname = brief.get("name") or ""
    if cname.lower() == name.lower():
        score += 50
    elif name.lower() in cname.lower():
        score += 10
    else:
        score -= 20
    if "tcgp" in cid or (cid[:1] in {"A", "B"} and "-" in cid):
        score -= 25
    if any(cid.startswith(prefix) for prefix in ("sv", "swsh")):
        score += 10
    elif any(cid.startswith(prefix) for prefix in ("sm", "xy")):
        score += 4
    if prefer:
        blob = json.dumps(brief).lower()
        score += 5 * sum(1 for p in prefer if p.lower() in blob)
    return score


def _score_print(
    card: Card,
    prefer: list[str],
    ocr_text: str,
    preferred_id: str | None,
    art: float = 0.0,
    best_art: float = 0.0,
    crop_yellow: float = 0.0,
    wanted_name: str = "",
) -> float:
    """Rank a fully fetched printing. Coverage beats first-match on a shared attack name."""
    if wanted_name and not _names_match(card.name, wanted_name):
        return -100.0
    blob = json.dumps(card.to_dict()).lower()
    attack_blob = " ".join(f"{a.name} {a.damage} {a.text}" for a in card.attacks).lower()
    ocr = _norm_alnum(ocr_text)
    ocr_compact = ocr.replace(" ", "")
    score = 0.0
    pin_ok = True
    if best_art >= 0.28 and art + 0.04 < best_art:
        pin_ok = False
    if preferred_id and card.catalog_id == preferred_id and pin_ok:
        score += 40
    cid = card.catalog_id
    if cid.startswith(("A", "B")) or "tcgp" in cid.lower():
        score -= 30
    elif cid.startswith(("sv", "swsh")):
        score += 4
    prefix = cid.split("-")[0].lower()
    if (art > 0 or best_art > 0) and prefix.startswith(
        ("pop", "ex", "ecard", "neo", "base", "dp", "col", "pl", "hgss", "bw", "lc")
    ):
        # Carpet photos are SWSH/SV-era paper; vintage color collisions (POP Gible) lose.
        score -= 28
    if crop_yellow >= 0.70:
        # Visible yellow English frame → SWSH/SM, not SV silver (TWM Tangela vs CZ).
        if prefix.startswith("sv"):
            score -= 18
        elif prefix.startswith(("swsh", "sm")):
            score += 10
    hits = 0
    for phrase in prefer:
        pl = phrase.lower().strip()
        if not pl:
            continue
        if pl in attack_blob:
            hits += 1
            score += 12
        elif pl in blob:
            hits += 1
            score += 5
    if prefer:
        score += 18 * (hits / len(prefer))
    if ocr:
        for attack in card.attacks:
            an = _norm_alnum(attack.name)
            if len(an) < 5:
                continue
            if an in ocr:
                score += 20
            elif an.replace(" ", "") in ocr_compact:
                score += 16
    if art > 0:
        score += 70 * art
    return score


def _load_catalog_image(url: str | None):
    if not url:
        return None
    try:
        from PIL import Image
    except Exception:
        return None
    folder = CACHE_DIR / "img"
    folder.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", url)[:180]
    path = folder / safe
    try:
        if path.exists() and path.stat().st_size > 200:
            return Image.open(path).convert("RGB")
        response = _CLIENT.get(url)
        response.raise_for_status()
        path.write_bytes(response.content)
        return Image.open(path).convert("RGB")
    except Exception:
        return None


def resolve_name(name: str, prefer: list[str] | None = None, ocr_text: str | None = None, crop_image=None) -> Card:
    name = name.strip()
    energy = ENERGY_NAME_TO_TYPE.get(name.lower())
    if energy and name.lower() not in {"boomerang energy", "double colorless energy"}:
        return energy_card(energy)

    prefer = list(prefer or []) or list(PRINT_PREFER.get(name) or [])
    preferred_id = PREFERRED_IDS.get(name)

    briefs = search_briefs(name)
    exact = [b for b in briefs if (b.get("name") or "").lower() == name.lower()]
    pool = exact or briefs
    ranked = sorted(pool, key=lambda b: _score_candidate(b, name, prefer), reverse=True)

    candidates: list[Card] = []
    seen: set[str] = set()

    def _add(card_id: str | None) -> None:
        if not card_id or card_id in seen:
            return
        seen.add(card_id)
        try:
            card = normalize_card(fetch_full(card_id))
        except Exception:
            return
        if not _names_match(card.name, name):
            return
        candidates.append(card)

    _add(preferred_id)
    for extra_id in EXTRA_PRINT_IDS.get(name) or ():
        _add(extra_id)
    for brief in ranked[:16]:
        _add(brief.get("id"))
    for brief in exact:
        cid = str(brief.get("id") or "")
        if cid.startswith(("sv", "swsh", "sm")):
            _add(cid)

    if not candidates:
        return fallback_card(name)

    art_scores: dict[str, float] = {}
    crop_yellow = 0.0
    if crop_image is not None:
        from app.recognition.images import art_similarity, frame_yellow_frac

        crop_yellow = frame_yellow_frac(crop_image)
        for card in candidates:
            img = _load_catalog_image(card.image)
            if img is not None:
                art_scores[card.catalog_id] = art_similarity(crop_image, img)
    best_art = max(art_scores.values(), default=0.0)

    def _key(card: Card) -> float:
        return _score_print(
            card,
            prefer,
            ocr_text or "",
            preferred_id,
            art_scores.get(card.catalog_id, 0.0),
            best_art,
            crop_yellow,
            wanted_name=name,
        )

    best = max(candidates, key=_key)
    if prefer and _key(best) <= 0:
        if preferred_id:
            _add(preferred_id)
            pinned = next((c for c in candidates if c.catalog_id == preferred_id), None)
            if pinned:
                return pinned
    return best


# Crown Zenith basic energy — one print per type, with TCGDex art.
ENERGY_PRINTS = {
    "Grass": "swsh12.5-152",
    "Fire": "swsh12.5-153",
    "Water": "swsh12.5-154",
    "Lightning": "swsh12.5-155",
    "Psychic": "swsh12.5-156",
    "Fighting": "swsh12.5-157",
    "Darkness": "swsh12.5-158",
    "Metal": "swsh12.5-159",
}

# Keep fallback attack text, overlay this catalog art (wrong print would break Set S OHKO).
ART_ONLY_IDS = {
    "Floragato": "sv01-014",
}


def _looks_like_tcgdex_id(card_id: str) -> bool:
    if not card_id or not isinstance(card_id, str) or card_id.startswith("fallback"):
        return False
    if "-" not in card_id:
        return False
    series = card_id.split("-", 1)[0].lower()
    return series.startswith(("sv", "swsh", "sm", "xy", "me", "base"))


def _tcgdex_low(card_id: str) -> str:
    series, number = card_id.split("-", 1)
    folder = "swsh" if series.startswith("swsh") else "sv" if series.startswith("sv") else "sm" if series.startswith("sm") else series
    return f"https://assets.tcgdex.net/en/{folder}/{series}/{number}/low.webp"


def energy_card(energy_type: str) -> Card:
    print_id = ENERGY_PRINTS.get(energy_type)
    return Card(
        catalog_id=print_id or f"energy-{energy_type.lower()}",
        name=f"{energy_type} Energy",
        category="Energy",
        stage="Basic",
        types=[energy_type],
        energy_type=energy_type,
        image=_tcgdex_low(print_id) if print_id else None,
        set_name="Crown Zenith" if print_id else None,
        retreat=0,
    )


def fallback_card(name: str) -> Card:
    lower = name.lower()
    if lower in TRAINER_KIND_HINTS:
        kind = TRAINER_KIND_HINTS[lower]
        return Card(
            catalog_id=f"fallback-{lower.replace(' ', '-')}",
            name=name,
            category="Trainer",
            stage=kind.title(),
            trainer_kind=kind,
            text=f"Family-rules approximation of {name}.",
        )
    if "energy" in lower:
        etype = ENERGY_NAME_TO_TYPE.get(lower, "Colorless")
        return energy_card(etype)
    return Card(
        catalog_id=f"fallback-{lower.replace(' ', '-')}",
        name=name,
        category="Pokemon",
        stage="Basic",
        types=["Colorless"],
        hp=70,
        attacks=[parse_attack({"name": "Tackle", "cost": ["Colorless"], "damage": 20})],
        retreat=1,
    )


def resolve_many(names: list[str], prefer_map: dict[str, list[str]] | None = None) -> list[Card]:
    prefer_map = prefer_map or {}
    return [resolve_name(n, prefer_map.get(n)) for n in names]


@lru_cache(maxsize=1)
def popular_names() -> list[str]:
    path = CACHE_DIR / "popular_names.json"
    if path.exists():
        return json.loads(path.read_text())
    return []


def _fold_name(text: str) -> str:
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode("ascii").lower().strip()


def _pretty_catalog_name(raw: str) -> str:
    if raw[:1].isupper():
        return raw
    return " ".join(part.capitalize() for part in raw.replace("_", " ").split())


@lru_cache(maxsize=1)
def _local_name_catalog() -> tuple[tuple[str, str, str], ...]:
    rows: list[tuple[str, str, str]] = []
    seen: set[tuple[str, str]] = set()

    def add(name: str, cid: str = "") -> None:
        fold = _fold_name(name)
        key = (fold, cid or "")
        if not fold or key in seen:
            return
        if not cid and any(_fold_name(existing) == fold and existing_cid for existing_cid, existing, _img in rows):
            return
        seen.add(key)
        image = ""
        if _looks_like_tcgdex_id(cid):
            try:
                image = _tcgdex_low(cid)
            except Exception:
                image = ""
        rows.append((cid, name.strip(), image))

    for name, cid in PREFERRED_IDS.items():
        add(name, cid)
        for extra in EXTRA_PRINT_IDS.get(name) or ():
            add(name, extra)
    for name, extras in EXTRA_PRINT_IDS.items():
        for extra in extras:
            add(name, extra)
    for name in PRINT_PREFER:
        add(name, PREFERRED_IDS.get(name, ""))
    for raw in ENERGY_NAME_TO_TYPE:
        if raw.startswith("basic "):
            continue
        add(_pretty_catalog_name(raw))
    for raw in TRAINER_KIND_HINTS:
        add(_pretty_catalog_name(raw), PREFERRED_IDS.get(_pretty_catalog_name(raw), ""))
    for name in popular_names():
        add(name, PREFERRED_IDS.get(name, ""))
    try:
        from app.seed_data import (
            SET_A_NAMES,
            SET_B_NAMES,
            SET_C_NAMES,
            SET_D_NAMES,
            SET_E_NAMES,
            SET_F_NAMES,
            SET_S_NAMES,
            SET_T_NAMES,
            SET_SPARE_NAMES,
        )

        for group in (
            SET_A_NAMES,
            SET_B_NAMES,
            SET_C_NAMES,
            SET_D_NAMES,
            SET_E_NAMES,
            SET_F_NAMES,
            SET_S_NAMES,
            SET_T_NAMES,
            SET_SPARE_NAMES,
        ):
            for name in group:
                add(name, PREFERRED_IDS.get(name, ""))
    except Exception:
        pass
    return tuple(rows)


_COLLECTOR_RE = re.compile(r"\b(\d{1,3})\s*/\s*(\d{2,3})\b")
_HP_RE = re.compile(r"\b(\d{2,3})\s*hp\b", re.I)
_CATALOG_TOKEN_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9.]*-\d+[A-Za-z0-9]*)\b")
_PRINTING_HIT_CAP = 40
_REMOTE_HIT_CAP = 250
_NAME_STAGE_SUFFIXES = {"ex", "v", "vmax", "vstar", "gx", "tag team"}


def _local_id_from_catalog_id(cid: str) -> str:
    if not cid or "-" not in str(cid):
        return ""
    return str(cid).split("-", 1)[1]


def _norm_local_id(value: str) -> str:
    text = str(value or "").strip()
    if text.isdigit():
        return str(int(text))
    return text.lower()


def _local_ids_equal(left: str, right: str) -> bool:
    a, b = _norm_local_id(left), _norm_local_id(right)
    return bool(a) and a == b


def _hit_local_id(hit: dict[str, Any]) -> str:
    return str(hit.get("local_id") or hit.get("localId") or _local_id_from_catalog_id(str(hit.get("id") or "")))


def _set_size_from_brief(brief: dict[str, Any]) -> str:
    set_info = brief.get("set") if isinstance(brief, dict) else None
    if not isinstance(set_info, dict):
        return ""
    counts = set_info.get("cardCount") if isinstance(set_info.get("cardCount"), dict) else {}
    for key in ("official", "total", "printed"):
        raw = counts.get(key)
        if raw:
            return str(raw)
    return ""


def _hit_code(local_id: str, set_size: str = "") -> str:
    if local_id and set_size:
        return f"{local_id}/{set_size}"
    return local_id or ""


def _leftover_is_name_suffix(leftover: str) -> bool:
    fold = _fold_name(leftover)
    if not fold:
        return False
    first = fold.split()[0]
    return first in _NAME_STAGE_SUFFIXES or fold in _NAME_STAGE_SUFFIXES


_SET_OFFICIAL_COUNTS: dict[str, str] | None = None


def _set_official_counts() -> dict[str, str]:
    global _SET_OFFICIAL_COUNTS
    if _SET_OFFICIAL_COUNTS:
        return _SET_OFFICIAL_COUNTS
    path = _cache_path("http", "sets-en")
    data: Any = []
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except Exception:
            data = []
    if not data:
        try:
            response = _CLIENT.get(f"{TCGDEX_BASE}/sets")
            response.raise_for_status()
            data = response.json()
            path.write_text(json.dumps(data))
        except Exception:
            return {}
    if not isinstance(data, list):
        data = data.get("data") or []
    out: dict[str, str] = {}
    for row in data:
        sid = str(row.get("id") or "")
        counts = row.get("cardCount") if isinstance(row.get("cardCount"), dict) else {}
        official = counts.get("official") or counts.get("total")
        if sid and official:
            out[sid] = str(official)
    if out:
        _SET_OFFICIAL_COUNTS = out
    return out


def _hit_set_size(hit: dict[str, Any]) -> str:
    code = str(hit.get("code") or "")
    if "/" in code:
        return code.split("/", 1)[1]
    cid = str(hit.get("id") or "")
    set_id = cid.split("-", 1)[0] if "-" in cid else ""
    if not set_id:
        return ""
    counts = _SET_OFFICIAL_COUNTS
    if not counts:
        path = _cache_path("http", "sets-en")
        if not path.exists():
            return ""
        counts = _set_official_counts()
    return str(counts.get(set_id) or "")


def _hit_matches_set_size(hit: dict[str, Any], set_size: str) -> bool:
    if not set_size:
        return False
    got = _hit_set_size(hit)
    return bool(got) and str(got) == str(set_size)


def _parse_search_query(query: str) -> dict[str, str]:
    rest = (query or "").strip()
    catalog_id = ""
    local_id = ""
    set_size = ""
    hp = ""
    name = ""
    attack = ""

    cat = _CATALOG_TOKEN_RE.search(rest)
    if cat and _looks_like_tcgdex_id(cat.group(1)):
        catalog_id = cat.group(1)
        rest = f"{rest[: cat.start()]} {rest[cat.end() :]}".strip()

    col = _COLLECTOR_RE.search(rest)
    if col:
        local_id = col.group(1)
        set_size = col.group(2)
        rest = f"{rest[: col.start()]} {rest[col.end() :]}".strip()

    hp_m = _HP_RE.search(rest)
    if hp_m:
        hp = hp_m.group(1)
        rest = f"{rest[: hp_m.start()]} {rest[hp_m.end() :]}".strip()

    folded_rest = _fold_name(rest)
    best = ""
    for _cid, catalog_name, _image in _local_name_catalog():
        folded_name = _fold_name(catalog_name)
        if not folded_name:
            continue
        if folded_rest == folded_name or folded_rest.startswith(f"{folded_name} "):
            if len(folded_name) >= len(best):
                best = folded_name
                name = catalog_name
                leftover = folded_rest[len(folded_name) :].strip()
                if leftover.isdigit() and 1 <= len(leftover) <= 3 and not local_id:
                    local_id = leftover
                    attack = ""
                elif _leftover_is_name_suffix(leftover):
                    name = rest
                    attack = ""
                else:
                    attack = re.sub(r"\s+\d{1,3}$", "", leftover).strip()
    if not best:
        name = rest
        if not local_id and re.fullmatch(r"\d{1,3}", rest.strip() or ""):
            local_id = rest.strip()
            name = ""

    return {
        "raw": (query or "").strip(),
        "name": name.strip(),
        "local_id": local_id,
        "set_size": set_size,
        "catalog_id": catalog_id,
        "hp": hp,
        "attack": attack,
    }


def _name_match_rank(name: str, query: str) -> int:
    n = _fold_name(name)
    q = _fold_name(query)
    if not q:
        return 9
    if n == q:
        return 0
    if n.startswith(q):
        return 1
    if f" {q}" in f" {n}":
        return 2
    if q in n:
        return 3
    return 9


def _brief_as_hit(brief: dict[str, Any]) -> dict[str, str]:
    name = (brief.get("name") or "").strip()
    cid = str(brief.get("id") or "")
    local_id = str(brief.get("localId") or brief.get("local_id") or _local_id_from_catalog_id(cid))
    set_size = _set_size_from_brief(brief)
    return {
        "id": cid,
        "name": name,
        "image": _image_url(brief) or "",
        "local_id": local_id,
        "code": _hit_code(local_id, set_size),
    }


def _catalog_row_hit(cid: str, name: str, image: str) -> dict[str, str]:
    local_id = _local_id_from_catalog_id(cid)
    return {"id": cid, "name": name, "image": image, "local_id": local_id, "code": local_id}


def _hits_from_briefs(briefs: list[dict[str, Any]], limit: int) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for brief in briefs:
        name = (brief.get("name") or "").strip()
        cid = str(brief.get("id") or "")
        key = cid or f"name:{_fold_name(name)}"
        if not name or key in seen:
            continue
        seen.add(key)
        out.append(_brief_as_hit(brief))
        if len(out) >= limit:
            break
    return out


def _tcgdex_list_cards(params: list[tuple[str, str]]) -> list[dict[str, Any]]:
    exact_id = any(key == "localId" and str(value).startswith("eq:") for key, value in params)
    paginate = any(key == "localId" for key, _value in params) and not exact_id
    pages = 3 if paginate else 1
    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for page in range(1, pages + 1):
        page_params = list(params)
        if paginate:
            page_params.extend(
                [("pagination:itemsPerPage", "100"), ("pagination:page", str(page))]
            )
        cache_key = "search-" + "&".join(f"{key}={value}" for key, value in page_params)
        path = _cache_path("http", cache_key)
        if path.exists():
            try:
                data = json.loads(path.read_text())
            except Exception:
                data = []
        else:
            url = f"{TCGDEX_BASE}/cards?{urlencode(page_params)}"
            try:
                client = _CLIENT if any(key == "localId" for key, _value in page_params) else _SEARCH_CLIENT
                response = client.get(url)
                response.raise_for_status()
                data = response.json()
                path.write_text(json.dumps(data))
            except Exception:
                break
        if not isinstance(data, list):
            data = data.get("data") or []
        if not data:
            break
        for brief in data:
            cid = str(brief.get("id") or "")
            key = cid or f"name:{_fold_name(str(brief.get('name') or ''))}"
            if key in seen:
                continue
            seen.add(key)
            rows.append(brief)
        if len(data) < 100:
            break
    return rows


def _remote_search_briefs(query: str, parsed: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """TCGDex lookup by name, collector number, catalog id, HP, or attack."""
    parsed = parsed or _parse_search_query(query)
    params: list[tuple[str, str]] = []
    if parsed["name"]:
        params.append(("name", parsed["name"]))
    if parsed["local_id"]:
        params.append(("localId", f"eq:{parsed['local_id']}"))
    if parsed["hp"]:
        params.append(("hp", f"eq:{parsed['hp']}"))
    if parsed["attack"]:
        params.append(("attacks.name", parsed["attack"]))

    briefs: list[dict[str, Any]] = []
    seen: set[str] = set()

    def _absorb(rows: list[dict[str, Any]]) -> None:
        for brief in rows:
            cid = str(brief.get("id") or "")
            key = cid or f"name:{_fold_name(str(brief.get('name') or ''))}"
            if key in seen:
                continue
            seen.add(key)
            briefs.append(brief)

    if params:
        _absorb(_tcgdex_list_cards(params))
        if not briefs and parsed["name"] and parsed["local_id"]:
            _absorb(_tcgdex_list_cards([("name", parsed["name"])]))
            _absorb(_tcgdex_list_cards([("localId", f"eq:{parsed['local_id']}")]))
    elif not parsed["catalog_id"]:
        _absorb(_tcgdex_list_cards([("name", query.strip())]))

    if parsed["catalog_id"] and parsed["catalog_id"] not in seen:
        cid = parsed["catalog_id"]
        briefs.insert(
            0,
            {
                "id": cid,
                "name": parsed["name"] or cid,
                "localId": _local_id_from_catalog_id(cid),
                "image": _tcgdex_low(cid) if _looks_like_tcgdex_id(cid) else "",
            },
        )
    return briefs


def _merge_search_hits(
    local: list[dict[str, str]],
    remote: list[dict[str, str]],
    query: str,
    limit: int,
    parsed: dict[str, str] | None = None,
) -> list[dict[str, str]]:
    parsed = parsed or _parse_search_query(query)
    name_q = parsed["name"] or query
    merged: dict[str, dict[str, str]] = {}
    for hit in local + remote:
        name = hit.get("name") or ""
        cid = str(hit.get("id") or "").strip()
        key = f"id:{cid}" if cid else f"name:{_fold_name(name)}"
        if not _fold_name(name) and not cid:
            continue
        prev = merged.get(key)
        if not prev:
            merged[key] = hit
            continue
        richer_code = hit.get("code") or ""
        prev_code = prev.get("code") or ""
        code = richer_code if "/" in richer_code and "/" not in prev_code else prev_code or richer_code
        if not prev.get("id") and hit.get("id"):
            merged[key] = {**prev, **hit, "code": code}
        elif not prev.get("image") and hit.get("image"):
            merged[key] = {**prev, "image": hit["image"], "id": hit.get("id") or prev.get("id"), "code": code}
        else:
            merged[key] = {
                **hit,
                **prev,
                "local_id": prev.get("local_id") or hit.get("local_id") or "",
                "code": code,
            }
    ranked = sorted(
        merged.values(),
        key=lambda hit: (
            0 if parsed["catalog_id"] and (hit.get("id") or "") == parsed["catalog_id"] else 1,
            0 if parsed["set_size"] and _hit_matches_set_size(hit, parsed["set_size"]) else 1,
            0 if parsed["local_id"] and _local_ids_equal(_hit_local_id(hit), parsed["local_id"]) else 1,
            _name_match_rank(hit.get("name") or "", name_q) if name_q else 9,
            0 if (hit.get("id") or "") == (PREFERRED_IDS.get(hit.get("name") or "") or "") else 1,
            _fold_name(hit.get("name") or ""),
            hit.get("id") or "",
        ),
    )
    cap = _REMOTE_HIT_CAP if parsed["local_id"] else _PRINTING_HIT_CAP
    exact = [hit for hit in ranked if name_q and _name_match_rank(hit.get("name") or "", name_q) == 0]
    number_hits = [
        hit for hit in ranked if parsed["local_id"] and _local_ids_equal(_hit_local_id(hit), parsed["local_id"])
    ]
    if number_hits:
        others = [hit for hit in ranked if hit not in number_hits]
        return (number_hits[:cap] + others)[: max(limit, min(len(number_hits), cap))]
    if exact:
        others = [hit for hit in ranked if hit not in exact]
        return (exact[:_PRINTING_HIT_CAP] + others)[: max(limit, min(len(exact), _PRINTING_HIT_CAP))]
    return ranked[:limit]


def search_local(query: str, limit: int = 12, remote: bool = True) -> list[dict[str, str]]:
    q = query.strip()
    if len(q) < 2:
        return []
    parsed = _parse_search_query(q)
    name_q = parsed["name"] or (q if not parsed["local_id"] else "")
    local = []
    for cid, name, image in _local_name_catalog():
        name_hit = bool(name_q) and _name_match_rank(name, name_q) < 9
        number_hit = bool(parsed["local_id"]) and _local_ids_equal(_local_id_from_catalog_id(cid), parsed["local_id"])
        id_hit = bool(parsed["catalog_id"]) and cid == parsed["catalog_id"]
        if name_hit or number_hit or id_hit:
            local.append(_catalog_row_hit(cid, name, image))
    if parsed["catalog_id"] and not any(hit.get("id") == parsed["catalog_id"] for hit in local):
        cid = parsed["catalog_id"]
        image = _tcgdex_low(cid) if _looks_like_tcgdex_id(cid) else ""
        local.insert(0, _catalog_row_hit(cid, parsed["name"] or cid, image))
    local.sort(
        key=lambda hit: (
            0 if parsed["local_id"] and _local_ids_equal(_hit_local_id(hit), parsed["local_id"]) else 1,
            _name_match_rank(hit["name"], name_q) if name_q else 9,
            _fold_name(hit["name"]),
        )
    )
    local = local[: max(limit, 12, _PRINTING_HIT_CAP if parsed["local_id"] else 12)]
    extra: list[dict[str, str]] = []
    if remote:
        cap = _REMOTE_HIT_CAP if parsed["local_id"] else _PRINTING_HIT_CAP
        extra = _hits_from_briefs(_remote_search_briefs(q), cap)
    merged = _merge_search_hits(local, extra, q, limit, parsed)
    if merged:
        return merged
    return [{"id": "", "name": q, "image": "", "local_id": parsed["local_id"], "code": _hit_code(parsed["local_id"], parsed["set_size"])}]


def pick_search_hit(typed: str, hits: list[dict[str, str]] | None) -> dict[str, str] | None:
    """What Add to set should resolve: numbered print, exact typed name, else the top hit."""
    q = (typed or "").strip()
    rows = [h for h in (hits or []) if (h.get("name") or "").strip()]
    parsed = _parse_search_query(q)
    if parsed["catalog_id"]:
        for hit in rows:
            if (hit.get("id") or "") == parsed["catalog_id"]:
                return hit
    if parsed["local_id"]:
        numbered = [h for h in rows if _local_ids_equal(_hit_local_id(h), parsed["local_id"])]
        if parsed["set_size"]:
            sized = [h for h in numbered if _hit_matches_set_size(h, parsed["set_size"])]
            if sized:
                numbered = sized
        if parsed["name"]:
            named = [h for h in numbered if _name_match_rank(h.get("name") or "", parsed["name"]) <= 1]
            if named:
                return named[0]
        elif numbered:
            return numbered[0]
    folded = _fold_name(parsed["name"] or q)
    if folded:
        matches = [h for h in rows if _fold_name(h.get("name") or "") == folded]
        if matches:
            pin = PREFERRED_IDS.get(matches[0].get("name") or "")
            for hit in matches:
                if pin and (hit.get("id") or "") == pin:
                    return hit
            return matches[0]
        if parsed["name"] and parsed["local_id"]:
            return {"id": "", "name": parsed["name"], "image": ""}
    if rows:
        return rows[0]
    if q:
        return {"id": "", "name": q, "image": ""}
    return None
