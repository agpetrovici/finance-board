from pydantic import BaseModel
import datetime


class StockValue(BaseModel):
    date: datetime.datetime
    quantity: int
    price: float
    value: float
