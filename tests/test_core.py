import pytest

from robinhood_trading.backtest import run_backtest
from robinhood_trading.portfolio import parse_holdings
from robinhood_trading.strategy import sma, sma_crossover_signals


def test_sma():
    assert sma([1, 2, 3, 4], 2) == [None, 1.5, 2.5, 3.5]


def test_crossover_requires_fast_lt_slow():
    with pytest.raises(ValueError):
        sma_crossover_signals([1, 2, 3], fast=3, slow=2)


def test_crossover_goes_long_in_uptrend():
    prices = [10] * 5 + list(range(11, 31))
    assert sma_crossover_signals(prices, 2, 4)[-1] == 1


def test_backtest_executes_next_bar_without_lookahead():
    prices = [10, 10, 20, 20]
    result = run_backtest(prices, [1, 1, 1, 1], starting_cash=100)
    assert result.trades[0].index == 1 and result.trades[0].price == 10
    assert result.final_equity == pytest.approx(200)


def test_backtest_round_trip_and_drawdown():
    prices = [10, 10, 5, 5]
    result = run_backtest(prices, [1, 0, 0, 0], starting_cash=100)
    assert [t.side for t in result.trades] == ["BUY", "SELL"]
    assert result.final_equity == pytest.approx(50)
    assert result.max_drawdown == pytest.approx(-0.5)


def test_parse_holdings_sorted_by_value():
    raw = {
        "AAA": {"quantity": "1", "average_buy_price": "10", "price": "12"},
        "BBB": {"quantity": "10", "average_buy_price": "5", "price": "4"},
    }
    h = parse_holdings(raw)
    assert [x.symbol for x in h] == ["BBB", "AAA"]
    assert h[1].unrealized_pl == pytest.approx(2)
    assert h[0].unrealized_pl == pytest.approx(-10)
