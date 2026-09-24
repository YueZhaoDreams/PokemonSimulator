"""Deck-building (fate) layer.

Everything here scores or describes a frozen list. Nothing here is consulted by
``app.engine.game``; Choice and Decision stay in the match kernel.
"""

from app.engine.fate.ceilings import compute_ceilings, printed_draw_operators
from app.engine.fate.kg import build_catalog_kg, explain_edge, induce

__all__ = ["build_catalog_kg", "compute_ceilings", "explain_edge", "induce", "printed_draw_operators"]
