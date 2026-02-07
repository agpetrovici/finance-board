from pydantic import BaseModel
from typing import Sequence
from .stock import Stock


class Portfolio(BaseModel):
    stocks: Sequence[Stock]
