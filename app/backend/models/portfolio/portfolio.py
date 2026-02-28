from pydantic import BaseModel
from typing import Sequence
from .stock import Stock


class Portfolio(BaseModel):
    stocks: Sequence[Stock]
    total_invested: float = 0.0
    total_cash_returned: float = 0.0
    net_invested: float = 0.0
    total_market_value: float = 0.0
    total_unrealized_pnl: float = 0.0
    total_realized_pnl: float = 0.0
    total_return: float = 0.0
    total_return_pct: float = 0.0
