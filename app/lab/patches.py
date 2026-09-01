from __future__ import annotations

from typing import Any

from app.catalog import fallback_card
from app.engine.effects import is_basic_energy
from app.engine.models import Card

_PATCH_KEYS = {"swap_energy", "drop", "add"}


def apply_deck_patch(cards: list[dict], patch: dict | None) -> list[dict]:
    """Apply a small data patch: energy-type swap, drop/add named cards. Does not import data/lab."""
    out = [dict(card) for card in cards]
    if not patch:
        return out
    if not isinstance(patch, dict):
        raise ValueError("patch must be an object")
    unknown = set(patch) - _PATCH_KEYS
    if unknown:
        raise ValueError(f"unknown patch keys: {sorted(unknown)}")
    if "swap_energy" in patch:
        out = _swap_energy(out, patch["swap_energy"])
    for name in patch.get("drop") or []:
        out = _drop_named(out, str(name))
    for name in patch.get("add") or []:
        out.append(fallback_card(str(name)).to_dict())
    return out


def _as_card(blob: dict) -> Card:
    return Card.from_dict(blob)


def _energy_wanted(want: str) -> tuple[str, str]:
    raw = (want or "").strip()
    lower = raw.lower()
    if lower.endswith(" energy"):
        return raw, lower[: -len(" energy")].strip()
    return f"{raw} Energy" if raw else "", lower


def _is_named_basic_energy(card: Card, want: str) -> bool:
    if not is_basic_energy(card, pokemon_as_energy=False):
        return False
    full, typ = _energy_wanted(want)
    name = (card.name or "").lower()
    et = (getattr(card, "energy_type", None) or "").lower()
    return name == (full or "").lower() or name == f"{typ} energy" or et == typ


def _swap_energy(cards: list[dict], spec: Any) -> list[dict]:
    if not isinstance(spec, dict):
        raise ValueError("swap_energy must be an object")
    src = spec.get("from") or spec.get("from_name") or spec.get("from_type")
    dest = spec.get("to") or spec.get("to_name") or spec.get("to_type")
    if not src or not dest:
        raise ValueError("swap_energy needs from and to")
    limit = spec.get("count")
    remaining = int(limit) if limit is not None else None
    dest_name, _ = _energy_wanted(str(dest))
    replacement = fallback_card(dest_name or str(dest)).to_dict()
    out: list[dict] = []
    swapped = 0
    for blob in cards:
        card = _as_card(blob)
        if remaining != 0 and _is_named_basic_energy(card, str(src)):
            out.append(dict(replacement))
            swapped += 1
            if remaining is not None:
                remaining -= 1
        else:
            out.append(blob)
    if remaining is not None and remaining > 0:
        raise ValueError(f"swap_energy needed {limit} {src} cards, found {swapped}")
    if limit is None and swapped == 0:
        raise ValueError(f"swap_energy found no {src} cards")
    return out


def _drop_named(cards: list[dict], name: str) -> list[dict]:
    want = name.lower()
    out: list[dict] = []
    dropped = False
    for blob in cards:
        if not dropped and str(blob.get("name") or "").lower() == want:
            dropped = True
            continue
        out.append(blob)
    if not dropped:
        raise ValueError(f"drop did not find {name}")
    return out
