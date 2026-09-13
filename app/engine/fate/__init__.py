"""Deck-building (fate) layer.

Everything here scores or describes a frozen list. Nothing here is consulted by
``app.engine.game``; Choice and Decision stay in the match kernel.
"""

from app.engine.fate.ceilings import compute_ceilings, printed_draw_operators

__all__ = ["compute_ceilings", "printed_draw_operators"]
