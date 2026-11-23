# Robinhood-trading

Python tools for working with a Robinhood account and testing strategies:

- **`portfolio`**: read-only view of your current holdings, cost basis and unrealized P/L.
- **`backtest`**: offline simple moving average (SMA) crossover backtest on a CSV of historical prices. It needs no account and no network access.

This project **does not place trades**.

> Robinhood has no official public API for stock trading. The `portfolio` command uses the
> unofficial [`robin_stocks`](https://github.com/jmfernandes/robin_stocks) library, which can
> break without notice and may conflict with Robinhood's terms of service. Use at your own risk.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in credentials; .env is git-ignored
```

## Usage

```bash
# Backtest on the bundled sample data (or any Yahoo Finance-style CSV with a Close column)
python -m robinhood_trading backtest data/sample.csv --fast 10 --slow 30 --fee 0.001

# Show holdings (loads credentials from the environment)
set -a; source .env; set +a
python -m robinhood_trading portfolio
```

## How the backtest works

- A position is long when the fast SMA is above the slow SMA, and flat otherwise.
- A signal computed on bar *i* is filled at bar *i+1*'s price, so the backtest never trades on future data.
- The report shows strategy return, buy-and-hold return, trade count and max drawdown.

## Tests

```bash
pytest
```
