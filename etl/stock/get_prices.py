import datetime
from app.backend.utils.stock.stock_api import StockApi, IntervalTwelveData

from app.backend.models.db import SessionLocal
from app.backend.models.stock.e_stock_symbol import StockSymbol  # noqa: F401

# Insert prices in the database
with SessionLocal() as session:
    stock_api = StockApi()
    prices = stock_api.get_prices(
        "FTNT",
        IntervalTwelveData.DAILY,
        start_date=datetime.datetime.now() - datetime.timedelta(days=365),
        end_date=datetime.datetime.now(),
        timezone="UTC",
    )
    for price in prices:
        session.add(price)
    session.commit()
