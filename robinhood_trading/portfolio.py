"""Read-only Robinhood portfolio access via the unofficial `robin_stocks` library.

Credentials come from environment variables (see .env.example) and are never
stored by this package. Nothing in this module places, changes or cancels orders.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class Holding:
    symbol: str
    quantity: float
    average_cost: float
    price: float

    @property
    def market_value(self) -> float:
        return self.quantity * self.price

    @property
    def unrealized_pl(self) -> float:
        return (self.price - self.average_cost) * self.quantity


def login():
    """Log in with ROBINHOOD_USERNAME / ROBINHOOD_PASSWORD (and optional ROBINHOOD_MFA_CODE)."""
    try:
        import robin_stocks.robinhood as rh
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("Install the optional dependency: pip install robin_stocks") from exc
    user = os.environ.get("ROBINHOOD_USERNAME")
    password = os.environ.get("ROBINHOOD_PASSWORD")
    if not user or not password:
        raise SystemExit("Set ROBINHOOD_USERNAME and ROBINHOOD_PASSWORD in your environment.")
    rh.login(user, password, mfa_code=os.environ.get("ROBINHOOD_MFA_CODE"), store_session=True)
    return rh


def parse_holdings(raw: dict) -> list[Holding]:
    """Convert robin_stocks `build_holdings()` output into Holding objects."""
    return sorted(
        (
            Holding(
                symbol=sym,
                quantity=float(d.get("quantity", 0)),
                average_cost=float(d.get("average_buy_price", 0)),
                price=float(d.get("price", 0)),
            )
            for sym, d in raw.items()
        ),
        key=lambda h: h.market_value,
        reverse=True,
    )


def fetch_holdings() -> list[Holding]:
    rh = login()
    return parse_holdings(rh.account.build_holdings())
