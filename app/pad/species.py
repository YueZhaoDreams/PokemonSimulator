"""PokéAPI species entries for the Pad. Cache lives in data/cache/pad/."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

import httpx

from app.config import CACHE_DIR
from app.pad.gallery import remember

POKEAPI = "https://pokeapi.co/api/v2"
NAMES_URL = (
    "https://raw.githubusercontent.com/PokeAPI/pokeapi/master/data/v2/csv/pokemon_species_names.csv"
)
USER_AGENT = "ComboCubFamilyPad/0.1 (household pokedex)"
CACHE = CACHE_DIR / "pad"
LANG_IDS = {"9": "en", "12": "zh-hans"}
_LATIN = re.compile(r"[A-Za-z]")


class HttpxTransport:
    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(
            headers={"User-Agent": USER_AGENT},
            timeout=20.0,
            follow_redirects=True,
        )

    def get_json(self, url: str) -> dict:
        response = self._client.get(url)
        response.raise_for_status()
        return response.json()

    def get_text(self, url: str) -> str:
        response = self._client.get(url)
        response.raise_for_status()
        return response.text

    def get_bytes(self, url: str) -> bytes:
        response = self._client.get(url)
        response.raise_for_status()
        return response.content

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "HttpxTransport":
        return self

    def __exit__(self, *_exc) -> None:
        self.close()


def clean_text(text: str) -> str:
    return " ".join(text.replace("\f", " ").replace("\n", " ").split())


def parse_names(csv_text: str) -> dict[tuple[int, str], str]:
    names: dict[tuple[int, str], str] = {}
    for row in csv.reader(io.StringIO(csv_text)):
        if not row or row[0] == "species_id" or len(row) < 3:
            continue
        lang = LANG_IDS.get(row[1])
        name = row[2].strip()
        if lang and name:
            names[(int(row[0]), lang)] = name
    return names


def load_name_index(transport: HttpxTransport, cache_dir: Path = CACHE) -> dict[tuple[int, str], str]:
    path = cache_dir / "species_names.csv"
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        text = transport.get_text(NAMES_URL)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return parse_names(text)


def _localized(rows: list[dict], key: str, language: str = "zh-hans") -> str:
    for row in rows or []:
        if str((row.get("language") or {}).get("name") or "").lower() == language:
            return clean_text(str(row.get(key) or ""))
    return ""


def flavor_line(species: dict, language: str = "zh-hans") -> str:
    hits = [
        row
        for row in species.get("flavor_text_entries") or []
        if str((row.get("language") or {}).get("name") or "").lower() == language
    ]
    if not hits:
        return ""
    return clean_text(str(hits[-1].get("flavor_text") or ""))


def speech_text(entry: dict, language: str = "zh-hans") -> str:
    if language == "en":
        name = entry.get("name_en") or ""
        category = entry.get("category_en") or ""
        flavor = entry.get("flavor_en") or ""
        if flavor:
            head = f"{name}, {category}. " if category else f"{name}. "
            return head + flavor
        parts = [part for part in (name, category) if part]
        sentence = ", ".join(parts) + "." if parts else ""
        extras = []
        types = ", ".join(entry.get("types_en") or [])
        if types:
            extras.append(f"Type {types}")
        if entry.get("height_m") is not None:
            extras.append(f"{entry['height_m']} m")
        if entry.get("weight_kg") is not None:
            extras.append(f"{entry['weight_kg']} kg")
        if extras:
            sentence += " " + ". ".join(extras) + "."
        return sentence
    name = entry.get("name") or ""
    category = entry.get("category") or ""
    flavor = entry.get("flavor") or ""
    if flavor:
        head = f"{name}，{category}。" if category else f"{name}。"
        return head + flavor
    parts = [part for part in (name, category) if part]
    sentence = "，".join(parts) + "。"
    extras = []
    types = "、".join(entry.get("types") or [])
    if types:
        extras.append(f"属性{types}")
    if entry.get("height_m") is not None:
        extras.append(f"身高{entry['height_m']}米")
    if entry.get("weight_kg") is not None:
        extras.append(f"体重{entry['weight_kg']}千克")
    if extras:
        sentence += "。".join(extras) + "。"
    if _LATIN.search(sentence):
        sentence = _LATIN.sub("", sentence)
    return sentence


def artwork_thumb(species_id: int) -> str:
    return (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/"
        f"{int(species_id)}.png"
    )


def sprite_thumb(species_id: int) -> str:
    """Small sprite for the numbered index. Official art stays on the opened entry."""
    return (
        "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/"
        f"{int(species_id)}.png"
    )


def _edit_distance(left: str, right: str, limit: int) -> int:
    if abs(len(left) - len(right)) > limit:
        return limit + 1
    previous = list(range(len(right) + 1))
    for i, char_left in enumerate(left, 1):
        current = [i]
        best = limit + 1
        for j, char_right in enumerate(right, 1):
            cost = 0 if char_left == char_right else 1
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + cost))
            best = min(best, current[-1])
        if best > limit:
            return limit + 1
        previous = current
    return previous[-1]


def _fuzzy_limit(text: str) -> int:
    length = len(text)
    if length < 2:
        return 0
    if length <= 4:
        return 1
    return 2


def find_ids(query: str, names: dict[tuple[int, str], str]) -> list[int]:
    text = query.strip()
    if not text:
        return []
    if text.isdigit():
        number = int(text)
        known = {species_id for species_id, _lang in names}
        return [number] if number in known else []
    folded = text.casefold()
    limit = _fuzzy_limit(folded)
    best: dict[int, int] = {}
    for (species_id, _lang), name in names.items():
        label = name.casefold()
        if label == folded:
            rank = 0
        elif folded in label or label in folded:
            rank = 1
        elif limit:
            distance = _edit_distance(folded, label, limit)
            if distance > limit:
                continue
            rank = 1 + distance
        else:
            continue
        previous = best.get(species_id)
        if previous is None or rank < previous:
            best[species_id] = rank
    if not best:
        return []
    if any(rank == 0 for rank in best.values()):
        chosen = [species_id for species_id, rank in best.items() if rank == 0]
    elif any(rank == 1 for rank in best.values()):
        chosen = [species_id for species_id, rank in best.items() if rank == 1]
    else:
        nearest = min(best.values())
        chosen = [species_id for species_id, rank in best.items() if rank == nearest]
    chosen.sort(key=lambda species_id: (best[species_id], species_id))
    return chosen[:8]


def _labels(transport: HttpxTransport, url: str) -> tuple[str, str]:
    payload = transport.get_json(url)
    rows = payload.get("names") or []
    return _localized(rows, "name", "zh-hans"), _localized(rows, "name", "en")


def build_entry(species_id: int, transport: HttpxTransport, cache_dir: Path = CACHE) -> dict:
    cached = cache_dir / f"{species_id}.json"
    if cached.exists():
        stored = json.loads(cached.read_text(encoding="utf-8"))
        if "name_en" in stored and "speech_en" in stored:
            return stored
    try:
        species = transport.get_json(f"{POKEAPI}/pokemon-species/{species_id}/")
        pokemon = transport.get_json(f"{POKEAPI}/pokemon/{species_id}/")
    except (httpx.HTTPError, KeyError) as exc:
        raise LookupError(str(species_id)) from exc
    sprites = (pokemon.get("sprites") or {}).get("other") or {}
    artwork = ((sprites.get("official-artwork") or {}).get("front_default")) or ""
    animation = ((sprites.get("showdown") or {}).get("front_default")) or ""
    types = []
    types_en = []
    for row in pokemon.get("types") or []:
        label, label_en = _labels(transport, row["type"]["url"])
        if label:
            types.append(label)
        if label_en:
            types_en.append(label_en)
    abilities = []
    abilities_en = []
    for row in pokemon.get("abilities") or []:
        label, label_en = _labels(transport, row["ability"]["url"])
        if label:
            abilities.append(label)
        if label_en:
            abilities_en.append(label_en)
    entry = {
        "id": species_id,
        "name": _localized(species.get("names") or [], "name") or str(species.get("name") or species_id),
        "name_en": _localized(species.get("names") or [], "name", "en"),
        "types": types,
        "types_en": types_en,
        "category": _localized(species.get("genera") or [], "genus"),
        "category_en": _localized(species.get("genera") or [], "genus", "en"),
        "abilities": abilities,
        "abilities_en": abilities_en,
        "height_m": round(int(pokemon.get("height") or 0) / 10, 1),
        "weight_kg": round(int(pokemon.get("weight") or 0) / 10, 1),
        "flavor": flavor_line(species),
        "flavor_en": flavor_line(species, "en"),
        "artwork_url": artwork,
        "animation_url": animation,
        "cry_url": (pokemon.get("cries") or {}).get("latest") or "",
    }
    entry["speech_text"] = speech_text(entry)
    entry["speech_en"] = speech_text(entry, "en")
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached.write_text(json.dumps(entry, ensure_ascii=False), encoding="utf-8")
    if artwork:
        try:
            remember(species_id, transport.get_bytes(artwork), cache_dir)
        except Exception:
            pass
    return entry


def display_name(species_id: int, names: dict[tuple[int, str], str]) -> str:
    return names.get((species_id, "zh-hans")) or names.get((species_id, "en")) or str(species_id)


def suggestion_row(species_id: int, names: dict[tuple[int, str], str]) -> dict:
    return {
        "id": species_id,
        "name": display_name(species_id, names),
        "name_en": names.get((species_id, "en")) or "",
        "thumb_url": artwork_thumb(species_id),
    }


def catalog_rows(names: dict[tuple[int, str], str]) -> list[dict]:
    rows = []
    for species_id in sorted({species_id for species_id, _lang in names}):
        row = suggestion_row(species_id, names)
        row["thumb_url"] = sprite_thumb(species_id)
        rows.append(row)
    return rows


def search_species(
    query: str,
    transport: HttpxTransport | None = None,
    names: dict[tuple[int, str], str] | None = None,
    cache_dir: Path = CACHE,
) -> dict:
    owns_transport = transport is None
    transport = transport or HttpxTransport()
    try:
        return _search_species(query, transport, names, cache_dir)
    finally:
        if owns_transport:
            transport.close()


def _search_species(query, transport, names, cache_dir: Path) -> dict:
    index = names if names is not None else load_name_index(transport, cache_dir)
    found = find_ids(query, index)
    if not found:
        return {"match": "none", "results": []}
    if len(found) > 1:
        return {
            "match": "many",
            "results": [suggestion_row(species_id, index) for species_id in found],
        }
    return {"match": "one", "entry": build_entry(found[0], transport, cache_dir)}
