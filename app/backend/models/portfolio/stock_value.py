from pydantic import BaseModel
import datetime


class StockValue(BaseModel):
    date: datetime.datetime
    quantity: int
    price: float
    value: float
    cost_basis: float = 0.0
    avg_cost_per_share: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_pct: float = 0.0
    realized_pnl: float = 0.0
    total_pnl: float = 0.0
