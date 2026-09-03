"""Map lab cells to customer-facing attempts and a question conclusion."""

from __future__ import annotations

import json
from typing import Any

ATTEMPT_INPUT_KEYS = (
    "deck_a_id",
    "deck_b_id",
    "strategy_a",
    "strategy_b",
    "patch_a",
    "patch_b",
    "card_overlay",
    "card_overlay_a",
    "card_overlay_b",
)


def _strat_name(spec: object) -> str:
    if isinstance(spec, str):
        return spec
    if isinstance(spec, dict):
        return str(spec.get("name") or "")
    return ""


def human_title(cell: dict, index: int) -> str:
    if cell.get("title"):
        return str(cell["title"])
    parts: list[str] = []
    sa = _strat_name(cell.get("strategy_a"))
    sb = _strat_name(cell.get("strategy_b"))
    if sa and sb:
        parts.append(f"{sa} vs {sb}")
    elif sa or sb:
        parts.append(sa or sb)
    if cell.get("patch_a") or cell.get("patch_b"):
        parts.append("deck patch")
    if cell.get("card_overlay") or cell.get("card_overlay_a") or cell.get("card_overlay_b"):
        parts.append("card overlay")
    if parts:
        return " · ".join(parts)
    return str(cell.get("id") or f"This run {index + 1}")


def insights_list(value: object) -> list[str]:
    if isinstance(value, dict):
        raw = value.get("insights") or []
    elif isinstance(value, list):
        raw = value
    elif isinstance(value, str):
        raw = [value] if value else []
    else:
        raw = []
    if isinstance(raw, str):
        raw = [raw] if raw else []
    if not isinstance(raw, list):
        return []
    return [str(item) for item in raw if isinstance(item, str) and item]


def cells_from_attempts(attempts: object) -> list[dict]:
    if attempts is None:
        return []
    if not isinstance(attempts, list):
        raise ValueError("attempts must be a list")
    return [attempt_to_cell(item, index) for index, item in enumerate(attempts)]


def attempt_to_cell(attempt: object, index: int) -> dict:
    if not isinstance(attempt, dict):
        raise ValueError(f"run {index + 1} must be an object")
    src = attempt.get("input") if isinstance(attempt.get("input"), dict) else attempt
    cell: dict[str, Any] = {}
    for key in ATTEMPT_INPUT_KEYS:
        if key in src:
            cell[key] = src[key]
        elif key in attempt:
            cell[key] = attempt[key]
    cell_id = attempt.get("id") or src.get("id") or f"run-{index + 1}"
    cell["id"] = str(cell_id)
    title = attempt.get("title") or src.get("title")
    if title:
        cell["title"] = str(title)
    return cell


def payload_cells(payload: dict, existing: dict | None = None) -> list | dict | None:
    if "attempts" in payload:
        return cells_from_attempts(payload.get("attempts"))
    if "cells" in payload:
        cells = payload["cells"]
        if cells is None:
            return []
        if not isinstance(cells, list):
            raise ValueError("cells must be a list")
        return cells
    if existing is not None:
        return existing.get("cells")
    return []


def payload_conclusion(payload: dict, existing: dict | None = None) -> str | None:
    if "conclusion" in payload:
        value = payload.get("conclusion")
        if value is None:
            return None
        return str(value)
    if existing is not None:
        stored = existing.get("conclusion")
        return str(stored) if stored is not None else None
    return None


def input_fingerprint(cell: dict) -> dict:
    return {key: cell[key] for key in ATTEMPT_INPUT_KEYS if key in cell}


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def result_matches_cell(row: dict, cell: dict) -> bool:
    stored = row.get("input")
    if stored is None:
        return True
    return _canonical(stored) == _canonical(input_fingerprint(cell))


def cells_run_key(cells: object) -> list[dict]:
    out: list[dict] = []
    if not isinstance(cells, list):
        return out
    for index, cell in enumerate(cells):
        if not isinstance(cell, dict):
            continue
        item = input_fingerprint(cell)
        item["id"] = str(cell.get("id") or f"run-{index + 1}")
        out.append(item)
    out.sort(key=lambda item: item["id"])
    return out


def payload_results(payload: dict, existing: dict | None = None):
    if existing is not None and ("attempts" in payload or "cells" in payload):
        incoming = cells_run_key(payload_cells(payload, existing))
        stored = cells_run_key(existing.get("cells") or [])
        if _canonical(incoming) != _canonical(stored):
            return None
    if "results" in payload:
        return payload["results"]
    if existing is None:
        return None
    return existing.get("results")


def attach_report(exp: dict | None) -> dict | None:
    """Add attempts[] from cells + results.cells. conclusion stays stored text (may be null)."""
    if not exp:
        return exp
    cells = exp.get("cells") if isinstance(exp.get("cells"), list) else []
    results = exp.get("results") if isinstance(exp.get("results"), dict) else {}
    result_cells = results.get("cells") if isinstance(results.get("cells"), list) else []
    by_id = {
        str(row.get("id")): row
        for row in result_cells
        if isinstance(row, dict) and row.get("id") is not None
    }
    by_cell = {
        str(cell.get("id") or f"run-{index + 1}"): cell
        for index, cell in enumerate(cells)
        if isinstance(cell, dict)
    }
    attempts: list[dict[str, Any]] = []
    iterable = result_cells if result_cells else cells
    from_results = bool(result_cells)
    for index, item in enumerate(iterable):
        if not isinstance(item, dict):
            continue
        cell_id = str(item.get("id") or f"run-{index + 1}")
        cell = by_cell.get(cell_id) or ({} if from_results else item)
        row = item if from_results else (by_id.get(cell_id) or {})
        if cell and row and not result_matches_cell(row, cell):
            row = {}
        insights = row.get("insights")
        if not isinstance(insights, list):
            insights = insights_list(row.get("learning"))
        title_src = cell if cell else {"id": cell_id, "title": item.get("title")}
        attempts.append(
            {
                "id": cell_id,
                "title": human_title(title_src, index),
                "input": cell if cell else (row.get("input") if isinstance(row.get("input"), dict) else {}),
                "win_rate_a": row.get("win_rate_a"),
                "win_rate_b": row.get("win_rate_b"),
                "tie_rate": row.get("tie_rate"),
                "queries": row.get("queries") or {},
                "insights": insights if isinstance(insights, list) else [],
                "decks": row.get("decks"),
            }
        )
    out = dict(exp)
    out["attempts"] = attempts
    if "conclusion" not in out:
        out["conclusion"] = None
    return out
