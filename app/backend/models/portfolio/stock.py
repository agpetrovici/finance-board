from pydantic import BaseModel
from typing import Sequence
from .stock_value import StockValue

class Stock(BaseModel):
    symbol: str
    values: Sequence[StockValue]