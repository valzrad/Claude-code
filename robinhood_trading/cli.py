"""Command-line entry point: `python -m robinhood_trading <command>`."""

from __future__ import annotations

import argparse

from .backtest import load_closes, run_backtest
from .strategy import sma_crossover_signals


def cmd_portfolio(_: argparse.Namespace) -> None:
    from .portfolio import fetch_holdings

    holdings = fetch_holdings()
    total = sum(h.market_value for h in holdings)
    print(f"{'Symbol':<8}{'Qty':>12}{'Avg cost':>12}{'Price':>12}{'Value':>14}{'P/L':>14}")
    for h in holdings:
        print(
            f"{h.symbol:<8}{h.quantity:>12.4f}{h.average_cost:>12.2f}{h.price:>12.2f}"
            f"{h.market_value:>14.2f}{h.unrealized_pl:>14.2f}"
        )
    print(f"\nTotal market value: {total:,.2f}")


def cmd_backtest(args: argparse.Namespace) -> None:
    prices = load_closes(args.csv, args.column)
    positions = sma_crossover_signals(prices, args.fast, args.slow)
    result = run_backtest(prices, positions, args.cash, args.fee)
    buy_hold = prices[-1] / prices[0] - 1
    print(f"Bars:            {len(prices)}")
    print(f"Trades:          {len(result.trades)}")
    print(f"Final equity:    {result.final_equity:,.2f}")
    print(f"Strategy return: {result.total_return:+.2%}")
    print(f"Buy & hold:      {buy_hold:+.2%}")
    print(f"Max drawdown:    {result.max_drawdown:.2%}")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="robinhood_trading")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("portfolio", help="Show current Robinhood holdings (read-only)")
    p.set_defaults(func=cmd_portfolio)

    b = sub.add_parser("backtest", help="Backtest an SMA crossover on a CSV of prices")
    b.add_argument("csv")
    b.add_argument("--column", default="Close")
    b.add_argument("--fast", type=int, default=10)
    b.add_argument("--slow", type=int, default=30)
    b.add_argument("--cash", type=float, default=10_000.0)
    b.add_argument("--fee", type=float, default=0.0, help="Fee/slippage per trade, e.g. 0.001")
    b.set_defaults(func=cmd_backtest)

    args = parser.parse_args(argv)
    args.func(args)
