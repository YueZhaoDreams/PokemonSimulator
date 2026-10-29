"""One-card greedy search.

Each step adds one copy of a card and removes one copy of one other card.
A cheap screen ranks every cut. The confirm replays the baseline and the cuts
that are still close to the best screen score. The step keeps the confirm with
the higher weighted win rate. The next copy starts from that list. The search
stops when the next copy does not raise the score, or at the copy cap.
"""

from __future__ import annotations


def confirm_cuts(screen_rows: list[dict], *, limit: int = 8) -> list[str]:
    """Baseline plus the cuts close to the best screen score.

    The best cut is always included, so a noisy screen still gets one confirm.
    `limit` counts the baseline.
    """
    if limit < 1:
        raise ValueError(limit)
    ordered = sorted(screen_rows, key=lambda row: (-row["weighted"], row["cut"] or ""))
    if not ordered:
        return []
    base = next(row for row in ordered if row["cut"] is None)
    band = max(base["se"], ordered[0]["se"]) * 2
    floor = ordered[0]["weighted"] - band
    labels = ["baseline"]
    for row in ordered:
        if row["cut"] is None:
            continue
        if row["weighted"] + 1e-12 >= floor or len(labels) == 1:
            labels.append(row["cut"])
        if len(labels) >= limit:
            break
    best_cut = ordered[0]["cut"]
    if best_cut and best_cut not in labels:
        labels.append(best_cut)
    return labels


def choose_swap(baseline: dict, swaps: list[dict]) -> tuple[dict, bool]:
    """Keep the higher weighted rate, then the better worst matchup.

    An exact tie takes the alphabetically earlier cut. A swap is kept when its
    weighted rate is higher than this step's own baseline.
    """
    if not swaps:
        raise ValueError("no cuts")
    best = max(swaps, key=lambda row: (row["weighted"], row["worst"], tuple(-ord(ch) for ch in row["cut"])))
    return best, best["weighted"] > baseline["weighted"]
