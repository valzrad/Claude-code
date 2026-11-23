"""Trading signal generators. Pure functions over lists of closing prices."""

from __future__ import annotations

from typing import Sequence


def sma(prices: Sequence[float], window: int) -> list[float | None]:
    """Simple moving average; None until enough data points exist."""
    if window <= 0:
        raise ValueError("window must be positive")
    out: list[float | None] = []
    running = 0.0
    for i, p in enumerate(prices):
        running += p
        if i >= window:
            running -= prices[i - window]
        out.append(running / window if i >= window - 1 else None)
    return out


def sma_crossover_signals(prices: Sequence[float], fast: int = 10, slow: int = 30) -> list[int]:
    """Return a target position per bar: 1 = long, 0 = flat.

    Long when the fast SMA is above the slow SMA, flat otherwise.
    """
    if fast >= slow:
        raise ValueError("fast window must be smaller than slow window")
    f, s = sma(prices, fast), sma(prices, slow)
    return [1 if (a is not None and b is not None and a > b) else 0 for a, b in zip(f, s)]
