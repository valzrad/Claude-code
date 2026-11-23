"""Minimal long/flat backtester. No brokerage connection; runs on historical prices."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence


@dataclass
class Trade:
    index: int
    side: str  # "BUY" or "SELL"
    price: float
    shares: float


@dataclass
class BacktestResult:
    starting_cash: float
    final_equity: float
    equity_curve: list[float]
    trades: list[Trade] = field(default_factory=list)

    @property
    def total_return(self) -> float:
        return self.final_equity / self.starting_cash - 1

    @property
    def max_drawdown(self) -> float:
        peak, worst = float("-inf"), 0.0
        for e in self.equity_curve:
            peak = max(peak, e)
            worst = min(worst, e / peak - 1)
        return worst


def run_backtest(
    prices: Sequence[float],
    positions: Sequence[int],
    starting_cash: float = 10_000.0,
    fee_rate: float = 0.0,
) -> BacktestResult:
    """Simulate trading.

    The position decided on bar i is executed at bar i+1's price, so the
    backtest never trades on information it could not have had yet.
    """
    if len(prices) != len(positions):
        raise ValueError("prices and positions must be the same length")
    cash, shares = starting_cash, 0.0
    trades: list[Trade] = []
    equity: list[float] = []
    for i, price in enumerate(prices):
        target = positions[i - 1] if i > 0 else 0
        if target == 1 and shares == 0:
            shares = cash * (1 - fee_rate) / price
            trades.append(Trade(i, "BUY", price, shares))
            cash = 0.0
        elif target == 0 and shares > 0:
            cash = shares * price * (1 - fee_rate)
            trades.append(Trade(i, "SELL", price, shares))
            shares = 0.0
        equity.append(cash + shares * price)
    return BacktestResult(starting_cash, equity[-1] if equity else starting_cash, equity, trades)


def load_closes(path: str | Path, column: str = "Close") -> list[float]:
    """Load closing prices from a CSV with a header row (e.g. a Yahoo Finance export)."""
    with open(path, newline="") as fh:
        return [float(row[column]) for row in csv.DictReader(fh) if row.get(column)]
