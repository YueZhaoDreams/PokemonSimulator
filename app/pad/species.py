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


def flavor_line(species: dict) -> str:
    hits = [
        row
        for row in species.get("flavor_text_entries") or []
        if str((row.get("language") or {}).get("name") or "").lower() == "zh-hans"
    ]
    if not hits:
        return ""
    return clean_text(str(hits[-1].get("flavor_text") or ""))


def speech_text(entry: dict) -> str:
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


def find_ids(query: str, names: dict[tuple[int, str], str]) -> list[int]:
    text = query.strip()
    if not text:
        return []
    if text.isdigit():
        number = int(text)
        known = {species_id for species_id, _lang in names}
        return [number] if number in known else []
    folded = text.casefold()
    exact: list[int] = []
    partial: list[int] = []
    for (species_id, _lang), name in names.items():
        label = name.casefold()
        if label == folded:
            exact.append(species_id)
        elif folded in label:
            partial.append(species_id)
    chosen = exact or partial
    seen: list[int] = []
    for species_id in chosen:
        if species_id not in seen:
            seen.append(species_id)
    return seen[:8]


def _named(transport: HttpxTransport, url: str) -> str:
    payload = transport.get_json(url)
    return _localized(payload.get("names") or [], "name")


def build_entry(species_id: int, transport: HttpxTransport, cache_dir: Path = CACHE) -> dict:
    cached = cache_dir / f"{species_id}.json"
    if cached.exists():
        return json.loads(cached.read_text(encoding="utf-8"))
    try:
        species = transport.get_json(f"{POKEAPI}/pokemon-species/{species_id}/")
        pokemon = transport.get_json(f"{POKEAPI}/pokemon/{species_id}/")
    except (httpx.HTTPError, KeyError) as exc:
        raise LookupError(str(species_id)) from exc
    sprites = (pokemon.get("sprites") or {}).get("other") or {}
    artwork = ((sprites.get("official-artwork") or {}).get("front_default")) or ""
    animation = ((sprites.get("showdown") or {}).get("front_default")) or ""
    types = []
    for row in pokemon.get("types") or []:
        label = _named(transport, row["type"]["url"])
        if label:
            types.append(label)
    abilities = []
    for row in pokemon.get("abilities") or []:
        label = _named(transport, row["ability"]["url"])
        if label:
            abilities.append(label)
    entry = {
        "id": species_id,
        "name": _localized(species.get("names") or [], "name") or str(species.get("name") or species_id),
        "types": types,
        "category": _localized(species.get("genera") or [], "genus"),
        "abilities": abilities,
        "height_m": round(int(pokemon.get("height") or 0) / 10, 1),
        "weight_kg": round(int(pokemon.get("weight") or 0) / 10, 1),
        "flavor": flavor_line(species),
        "artwork_url": artwork,
        "animation_url": animation,
        "cry_url": (pokemon.get("cries") or {}).get("latest") or "",
    }
    entry["speech_text"] = speech_text(entry)
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


def search_species(
    query: str,
    transport: HttpxTransport | None = None,
    names: dict[tuple[int, str], str] | None = None,
    cache_dir: Path = CACHE,
) -> dict:
    transport = transport or HttpxTransport()
    index = names if names is not None else load_name_index(transport, cache_dir)
    found = find_ids(query, index)
    if not found:
        return {"match": "none", "results": []}
    if len(found) > 1:
        return {
            "match": "many",
            "results": [{"id": species_id, "name": display_name(species_id, index)} for species_id in found],
        }
    return {"match": "one", "entry": build_entry(found[0], transport, cache_dir)}
