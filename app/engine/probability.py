from __future__ import annotations

from math import comb


def hypergeometric_at_least_one(copies: int, deck_size: int, draw: int) -> float:
    if copies <= 0 or draw <= 0 or deck_size <= 0:
        return 0.0
    if copies >= deck_size:
        return 1.0
    if draw > deck_size:
        draw = deck_size
    miss = deck_size - copies
    if draw > miss:
        return 1.0
    return 1.0 - comb(miss, draw) / comb(deck_size, draw)


def hypergeometric_exact(copies: int, deck_size: int, draw: int, k: int) -> float:
    if k < 0 or k > copies or draw > deck_size:
        return 0.0
    return comb(copies, k) * comb(deck_size - copies, draw - k) / comb(deck_size, draw)


def draw_probability(card_name: str, names: list[str], draw: int = 7) -> dict:
    deck_size = len(names)
    copies = sum(1 for n in names if n.lower() == card_name.lower())
    p_least = hypergeometric_at_least_one(copies, deck_size, draw)
    exact = {str(k): hypergeometric_exact(copies, deck_size, draw, k) for k in range(0, copies + 1)}
    return {
        "card": card_name,
        "copies": copies,
        "deck_size": deck_size,
        "draw": draw,
        "p_at_least_one": p_least,
        "exact": exact,
        "method": (
            f"Hypergeometric draw: {draw} cards from a {deck_size}-card deck with "
            f"{copies} cop{'y' if copies == 1 else 'ies'} of {card_name}. "
            f"P(at least one) = 1 - C({deck_size - copies},{draw}) / C({deck_size},{draw})."
        ),
    }
